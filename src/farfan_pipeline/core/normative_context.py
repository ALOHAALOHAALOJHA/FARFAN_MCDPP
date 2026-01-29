"""
Normative Context Manager - SOTA Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Advanced normative compliance validation system using empirical corpus.
Single source of truth: corpus_empirico_normatividad.json

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
Date: 2026-01-21
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONSTANTS AND ENUMS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class NormativeLevel(Enum):
    """Normative hierarchy levels"""
    CONSTITUTIONAL = "constitutional"
    ORGANIC_LAW = "organic_law"
    ORDINARY_LAW = "ordinary_law"
    DECREE = "decree"
    CONPES = "conpes"
    RESOLUTION = "resolution"
    AGREEMENT = "agreement"
    
class ComplianceScore(Enum):
    """Compliance scoring categories"""
    EXCELENTE = (0.90, 1.00, "All mandatory norms cited")
    BUENO = (0.75, 0.89, "Minor gaps")
    ACEPTABLE = (0.60, 0.74, "Significant gaps")
    DEFICIENTE = (0.00, 0.59, "Critical gaps")
    
    def __init__(self, min_score: float, max_score: float, description: str):
        self.min_score = min_score
        self.max_score = max_score
        self.description = description
    
    @classmethod
    def from_score(cls, score: float) -> ComplianceScore:
        """Get category from numeric score"""
        for category in cls:
            if category.min_score <= score <= category.max_score:
                return category
        return cls.DEFICIENTE

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class NormativeReference:
    """Immutable normative reference with metadata"""
    norm_id: str
    name: str
    level: NormativeLevel
    year: int
    articles: List[str] = field(default_factory=list)
    reason: str = ""
    penalty_if_missing: float = 0.0
    empirical_frequency: int = 0
    
    def __hash__(self) -> int:
        return hash(self.norm_id)

@dataclass
class ExtractedNorm:
    """Norm extracted from PDT document"""
    id: str
    content: str
    policy_areas: List[str] = field(default_factory=list)
    norm_type: Optional[str] = None
    source: Optional[str] = None
    confidence: float = 0.85
    metadata: Dict[str, Any] = field(default_factory=dict)
    _normalized_id: Optional[str] = field(default=None, init=False, repr=False)
    
    @property
    def normalized_id(self) -> str:
        """Lazy normalization of ID"""
        if self._normalized_id is None:
            self._normalized_id = NormativeContextManager.normalize_norm_id(self.id)
        return self._normalized_id

@dataclass
class IrrigationEvent:
    """Event for downstream processing and validation"""
    event_type: str
    policy_area: str
    timestamp: str
    score: float
    cited_norms: List[str]
    missing_norms: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationContext:
    """Context for municipal validation"""
    municipality: str
    is_pdet: bool = False
    ethnic_population_percentage: float = 0.0
    has_coastal_zone: bool = False
    population: int = 0
    category: Optional[str] = None
    department: Optional[str] = None
    
    def get_applicable_rules(self) -> Set[str]:
        """Determine which contextual rules apply"""
        rules = set()
        if self.is_pdet:
            rules.add("pdet_municipalities")
        if self.ethnic_population_percentage >= 10.0:
            rules.add("ethnic_territories")
        if self.has_coastal_zone:
            rules.add("coastal_municipalities")
        return rules

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN MANAGER CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class NormativeContextManager:
    """
    State-of-the-art Normative Context Manager
    
    Features:
    - Single source of truth (corpus_empirico_normatividad.json)
    - Advanced norm matching with fuzzy logic
    - Policy area-based grouping
    - Context-aware validation
    - Event irrigation for downstream processing
    """
    
    def __init__(
        self,
        municipality: str,
        enable_validation: bool = True,
        corpus_path: Optional[Path] = None,
        cache_size: int = 128
    ):
        """
        Initialize manager with municipality context
        
        Args:
            municipality: Municipality name for context
            enable_validation: Enable strict validation
            corpus_path: Optional custom corpus path
            cache_size: LRU cache size for norm lookups
        """
        self.municipality = municipality
        self.enable_validation = enable_validation
        self._corpus_path = self._resolve_corpus_path(corpus_path)
        self._corpus_cache: Optional[Dict[str, Any]] = None
        self._norm_index: Optional[Dict[str, Dict[str, Any]]] = None
        
        # Configure LRU cache
        self.normalize_norm_id = lru_cache(maxsize=cache_size)(
            self._normalize_norm_id_impl
        )
    
    # ─────────────────────────────────────────────────────────────
    # Corpus Management
    # ─────────────────────────────────────────────────────────────
    
    def _resolve_corpus_path(self, corpus_path: Optional[Path]) -> Path:
        """Resolve corpus path with intelligent fallback"""
        if corpus_path:
            return Path(corpus_path)
        
        # Smart path resolution
        current = Path(__file__).resolve()
        search_patterns = [
            ("canonic_questionnaire_central", "_registry", "entities"),
            ("data", "corpus"),
            ("resources", "normative")
        ]
        
        for depth in range(3, 6):
            try:
                root = current.parents[depth]
                for pattern in search_patterns:
                    candidate = root.joinpath(*pattern, "corpus_empirico_normatividad.json")
                    if candidate.exists():
                        return candidate
            except IndexError:
                continue
        
        # Default fallback
        return Path("canonic_questionnaire_central/_registry/entities/corpus_empirico_normatividad.json")
    
    @lru_cache(maxsize=1)
    def _load_corpus(self) -> Dict[str, Any]:
        """Load and validate corpus with caching"""
        if not self._corpus_path.exists():
            raise FileNotFoundError(
                f"Corpus empírico not found at {self._corpus_path}. "
                "Please ensure corpus_empirico_normatividad.json is available."
            )
        
        with open(self._corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Schema validation
        required_keys = {
            "mandatory_norms_by_policy_area",
            "universal_mandatory_norms",
            "contextual_validation_rules"
        }
        
        missing = required_keys - set(data.keys())
        if missing:
            raise ValueError(f"Invalid corpus schema. Missing keys: {missing}")
        
        return data
    
    # ─────────────────────────────────────────────────────────────
    # Normalization and Indexing
    # ─────────────────────────────────────────────────────────────
    
    @staticmethod
    def _normalize_norm_id_impl(text: str) -> str:
        """Normalize norm ID for matching"""
        if not text:
            return ""
        
        # Convert to lowercase and strip
        normalized = text.lower().strip()
        
        # Normalize whitespace
        normalized = re.sub(r"\s+", " ", normalized)
        
        # Remove special characters but keep Spanish chars
        normalized = re.sub(r"[^\w\sáéíóúñü]", "", normalized)
        
        # Normalize common variations
        replacements = {
            "ley ": "ley ",
            "decreto ": "decreto ",
            "conpes ": "conpes ",
            "resolucion ": "resolucion ",
            "acuerdo ": "acuerdo ",
            " de ": " ",
            " del ": " ",
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized.strip()
    
    @staticmethod
    def normalize_norm_id(text: str) -> str:
        """Public interface for norm ID normalization"""
        return NormativeContextManager._normalize_norm_id_impl(text)
    
    def _build_norm_index(self) -> Dict[str, Dict[str, Any]]:
        """Build searchable index from corpus"""
        if self._norm_index is not None:
            return self._norm_index
        
        corpus = self._load_corpus()
        index: Dict[str, Dict[str, Any]] = {}
        
        # Index universal norms
        for norm in corpus.get("universal_mandatory_norms", []):
            self._index_norm(index, norm, ["__UNIVERSAL__"], "universal")
        
        # Index policy area norms
        pa_map = corpus.get("mandatory_norms_by_policy_area", {})
        for pa_id, pa_data in pa_map.items():
            for category in ("mandatory", "recommended"):
                for norm in pa_data.get(category, []):
                    self._index_norm(index, norm, [pa_id], category)
        
        self._norm_index = index
        return index
    
    def _index_norm(
        self,
        index: Dict[str, Dict[str, Any]],
        norm: Dict[str, Any],
        policy_areas: List[str],
        kind: str
    ) -> None:
        """Add norm to index with deduplication"""
        norm_id = norm.get("norm_id", "")
        if not norm_id:
            return
        
        key = self.normalize_norm_id(norm_id)
        if key in index:
            # Merge policy areas
            existing_pas = set(index[key].get("policy_areas", []))
            existing_pas.update(policy_areas)
            index[key]["policy_areas"] = sorted(existing_pas)
        else:
            index[key] = {
                **norm,
                "policy_areas": policy_areas,
                "kind": kind
            }
    
    # ─────────────────────────────────────────────────────────────
    # Norm Loading and Processing
    # ─────────────────────────────────────────────────────────────
    
    def load_norms(self, source: Path | str | List[Dict] | Dict) -> List[ExtractedNorm]:
        """
        Load norms from various sources
        
        Args:
            source: Path to file, JSON string, list of dicts, or dict
            
        Returns:
            List of extracted norms
        """
        if isinstance(source, (Path, str)):
            path = Path(source) if isinstance(source, str) else source
            if not path.exists():
                raise FileNotFoundError(f"Norm file not found: {path}")
            
            if path.suffix.lower() == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                # Plain text, one norm per line
                with open(path, "r", encoding="utf-8") as f:
                    data = [
                        {"norm_id": line.strip(), "content": line.strip()}
                        for line in f if line.strip()
                    ]
        else:
            data = source
        
        return self._parse_norm_data(data)
    
    def _parse_norm_data(self, data: Any) -> List[ExtractedNorm]:
        """Parse various data formats into ExtractedNorm objects"""
        items: List[Dict[str, Any]] = []
        
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Handle various dict formats
            for key in ("references", "norms", "extracted_norms", "normative_references"):
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            else:
                items = [data]
        else:
            return []
        
        norms = []
        for item in items:
            if not isinstance(item, dict):
                continue
            
            # Extract norm ID from various fields
            norm_id = (
                item.get("norm_id") or
                item.get("id") or
                item.get("reference") or
                item.get("text") or
                item.get("content", "")
            )
            
            content = (
                item.get("content") or
                item.get("text") or
                item.get("description") or
                norm_id
            )
            
            if norm_id and content:
                norms.append(
                    ExtractedNorm(
                        id=str(norm_id),
                        content=str(content),
                        norm_type=item.get("norm_type") or item.get("type"),
                        source=item.get("source") or item.get("file"),
                        confidence=float(item.get("confidence", 0.85)),
                        metadata=item
                    )
                )
        
        return norms
    
    # ─────────────────────────────────────────────────────────────
    # Grouping and Analysis
    # ─────────────────────────────────────────────────────────────
    
    def group_by_policy_area(
        self,
        norms: List[ExtractedNorm]
    ) -> Dict[str, List[ExtractedNorm]]:
        """
        Group norms by policy area using corpus mapping
        
        Returns:
            Dict with policy areas as keys and norm lists as values
        """
        index = self._build_norm_index()
        grouped: Dict[str, List[ExtractedNorm]] = {}
        unmatched: List[ExtractedNorm] = []
        
        for norm in norms:
            record = index.get(norm.normalized_id)
            
            if not record:
                # Try fuzzy matching
                record = self._fuzzy_match_norm(norm.normalized_id, index)
            
            if record:
                policy_areas = record.get("policy_areas", [])
                norm.policy_areas = policy_areas
                
                for pa in policy_areas:
                    grouped.setdefault(pa, []).append(norm)
            else:
                unmatched.append(norm)
        
        if unmatched:
            grouped["__UNMATCHED__"] = unmatched
        
        return grouped
    
    def _fuzzy_match_norm(
        self,
        normalized_id: str,
        index: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Fuzzy matching for norm IDs"""
        # Extract numeric parts for laws/decrees
        numeric_match = re.search(r"\d+", normalized_id)
        if not numeric_match:
            return None
        
        number = numeric_match.group()
        
        # Try common patterns
        patterns = [
            f"ley {number}",
            f"decreto {number}",
            f"conpes {number}",
            f"resolucion {number}"
        ]
        
        for pattern in patterns:
            if pattern in index:
                return index[pattern]
        
        return None
    
    # ─────────────────────────────────────────────────────────────
    # Contextual Validation
    # ─────────────────────────────────────────────────────────────
    
    def resolve_contextual_norms(
        self,
        context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """
        Get additional norms based on municipal context
        
        Args:
            context: Validation context with municipal characteristics
            
        Returns:
            List of additional mandatory norms
        """
        corpus = self._load_corpus()
        rules = corpus.get("contextual_validation_rules", {})
        additional_norms: List[Dict[str, Any]] = []
        
        for rule_name in context.get_applicable_rules():
            rule_data = rules.get(rule_name, {})
            additional_norms.extend(
                rule_data.get("additional_mandatory", [])
            )
        
        return additional_norms
    
    # ─────────────────────────────────────────────────────────────
    # Event Irrigation System
    # ─────────────────────────────────────────────────────────────
    
    def generate_irrigation_events(
        self,
        norms: List[ExtractedNorm],
        policy_area: str,
        context: Optional[ValidationContext] = None
    ) -> Iterator[IrrigationEvent]:
        """
        Generate irrigation events for downstream processing
        
        Yields:
            IrrigationEvent objects for each validation
        """
        from datetime import datetime
        
        corpus = self._load_corpus()
        pa_map = corpus.get("mandatory_norms_by_policy_area", {})
        pa_data = pa_map.get(policy_area, {})
        
        # Collect all expected norms
        mandatory = pa_data.get("mandatory", [])
        universal = corpus.get("universal_mandatory_norms", [])
        contextual = self.resolve_contextual_norms(context) if context else []
        
        all_expected = mandatory + universal + contextual
        
        # Check compliance
        extracted_ids = {norm.normalized_id for norm in norms}
        cited = []
        missing = []
        total_penalty = 0.0
        
        for expected_norm in all_expected:
            norm_id = expected_norm.get("norm_id", "")
            normalized = self.normalize_norm_id(norm_id)
            
            if normalized in extracted_ids:
                cited.append(norm_id)
            else:
                penalty = float(expected_norm.get("penalty_if_missing", 0.0))
                total_penalty += penalty
                missing.append({
                    "norm_id": norm_id,
                    "name": expected_norm.get("name", ""),
                    "penalty": penalty,
                    "reason": expected_norm.get("reason", "")
                })
        
        score = max(0.0, 1.0 - total_penalty)
        category = ComplianceScore.from_score(score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(missing, category)
        
        # Create event
        yield IrrigationEvent(
            event_type="NORMATIVE_COMPLIANCE_CHECK",
            policy_area=policy_area,
            timestamp=datetime.now().isoformat(),
            score=score,
            cited_norms=cited,
            missing_norms=missing,
            recommendations=recommendations,
            metadata={
                "municipality": self.municipality,
                "category": category.name,
                "total_expected": len(all_expected),
                "total_cited": len(cited),
                "total_missing": len(missing)
            }
        )
    
    def _generate_recommendations(
        self,
        missing: List[Dict[str, Any]],
        category: ComplianceScore
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if category == ComplianceScore.EXCELENTE:
            recommendations.append(
                "Excelente trabajo. El PDT cumple con todas las normas obligatorias."
            )
        elif category == ComplianceScore.BUENO:
            recommendations.append(
                "Buen cumplimiento normativo. Revisar las siguientes normas menores:"
            )
            for norm in missing[:3]:  # Top 3
                recommendations.append(
                    f"  • Incluir {norm['norm_id']}: {norm.get('reason', 'Requerido')}"
                )
        else:
            recommendations.append(
                "ATENCIÓN: Gaps normativos críticos detectados. Acción urgente requerida:"
            )
            critical = [m for m in missing if m["penalty"] >= 0.3]
            for norm in critical:
                recommendations.append(
                    f"  ⚠️ {norm['norm_id']} (penalidad: {norm['penalty']:.1%})"
                )
        
        return recommendations
    
    # ─────────────────────────────────────────────────────────────
    # Analysis and Reporting
    # ─────────────────────────────────────────────────────────────
    
    def generate_compliance_report(
        self,
        norms: List[ExtractedNorm],
        context: Optional[ValidationContext] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report
        
        Returns:
            Full compliance analysis with scores and recommendations
        """
        grouped = self.group_by_policy_area(norms)
        report = {
            "municipality": self.municipality,
            "total_norms_extracted": len(norms),
            "policy_areas": {},
            "overall_score": 0.0,
            "overall_category": "",
            "summary": {}
        }
        
        scores = []
        for pa, pa_norms in grouped.items():
            if pa == "__UNMATCHED__":
                continue
            
            events = list(self.generate_irrigation_events(pa_norms, pa, context))
            if events:
                event = events[0]
                report["policy_areas"][pa] = {
                    "score": event.score,
                    "cited": len(event.cited_norms),
                    "missing": len(event.missing_norms),
                    "recommendations": event.recommendations
                }
                scores.append(event.score)
        
        if scores:
            report["overall_score"] = sum(scores) / len(scores)
            report["overall_category"] = ComplianceScore.from_score(
                report["overall_score"]
            ).name
        
        return report
    
    def find_norm_details(self, norm_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific norm"""
        index = self._build_norm_index()
        normalized = self.normalize_norm_id(norm_id)
        return index.get(normalized)
    
    def list_all_mandatory_norms(self) -> List[Tuple[str, List[str]]]:
        """List all mandatory norms with their policy areas"""
        index = self._build_norm_index()
        mandatory = [
            (data["norm_id"], data["policy_areas"])
            for data in index.values()
            if data.get("kind") in ("mandatory", "universal")
        ]
        return sorted(mandatory, key=lambda x: x[0])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUBLIC API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

__all__ = [
    "NormativeContextManager",
    "ExtractedNorm",
    "IrrigationEvent",
    "ValidationContext",
    "NormativeLevel",
    "ComplianceScore",
    "NormativeReference"
]
