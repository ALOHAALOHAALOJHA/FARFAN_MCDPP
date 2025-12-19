"""Canonical Pattern Registry for SISAS-IrrigationSynchronizer-Contract Harmony.

This module provides the canonical registry for patterns, integrating:
1. Global patterns from canonic_questionnaire_central/pattern_registry.json
2. Contract-specific patterns from Q001-Q300.v3.json
3. Signal bindings for SISAS integration

Architecture Integration:
- Consumed by: IrrigationSynchronizer._filter_patterns_from_registry()
- Bound to: SISAS.SignalRegistry via pattern_key→signal_type mapping
- Validated by: ValidationEngine.PatternMatchRule

Design Invariants:
[INV-001] Each pattern_key is globally unique
[INV-002] Global patterns (PAT-0xxx) take precedence over contract patterns
[INV-003] Pattern→Signal bindings are immutable after registration
[INV-004] Contract patterns extend global patterns, not replace
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CanonicalPattern:
    """Immutable pattern with full provenance."""
    
    pattern_key: str
    contract_key: str | None
    policy_area_id: str | None
    dimension_id: str | None
    category: str
    match_type: str
    pattern: str
    confidence_weight: float
    specificity: str = "MEDIUM"
    produces_signals: tuple[str, ...] = field(default_factory=tuple)
    context_scope: str = "PARAGRAPH"
    flags: str = "i"
    is_global: bool = False
    usage_count: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_key": self.pattern_key,
            "contract_key": self.contract_key,
            "policy_area_id": self.policy_area_id,
            "dimension_id": self.dimension_id,
            "category": self.category,
            "match_type": self.match_type,
            "pattern": self.pattern,
            "confidence_weight": self.confidence_weight,
            "specificity": self.specificity,
            "produces_signals": list(self.produces_signals),
            "context_scope": self.context_scope,
            "flags": self.flags,
            "is_global": self.is_global,
            "usage_count": self.usage_count,
        }
    
    def compile_regex(self) -> re.Pattern[str]:
        """Compile pattern to regex with appropriate flags."""
        if self.match_type == "LITERAL":
            return re.compile(re.escape(self.pattern), re.IGNORECASE if "i" in self.flags else 0)
        flags = re.IGNORECASE if "i" in self.flags else 0
        return re.compile(self.pattern, flags)


@dataclass
class PatternSignalBinding:
    """Binding between pattern and signal types it produces."""
    
    pattern_key: str
    signal_types: list[str]
    binding_confidence: float = 1.0
    binding_source: str = "inferred"


class PatternRegistry:
    """Canonical registry for patterns with signal binding support.
    
    This registry serves as the single source of truth for patterns,
    integrating global patterns from pattern_registry.json and
    contract-specific patterns from Q001-Q300.v3.json.
    """
    
    CATEGORY_SIGNAL_MAP: dict[str, list[str]] = {
        "FUENTE_OFICIAL": ["data_sources", "source_validation"],
        "INDICADOR": ["baseline_completeness", "gender_indicators", "migration_indicators", "violence_indicators"],
        "TEMPORAL": ["temporal_coverage"],
        "TERRITORIAL": ["geographic_scope", "policy_coverage"],
        "GENERAL": ["baseline_completeness"],
        "CAUSAL": ["causal_coherence"],
        "CAUSAL_OUTCOME": ["causal_coherence"],
        "CAUSAL_CONNECTOR": ["causal_coherence"],
        "UNIDAD_MEDIDA": ["baseline_completeness"],
        "POBLACION": ["population_targeting"],
        "INSTRUMENTO": ["instrument_specification"],
        "MECANISMO_COMPLETO": ["causal_coherence"],
    }
    
    def __init__(self) -> None:
        self._patterns: dict[str, CanonicalPattern] = {}
        self._by_contract: dict[str, list[str]] = {}
        self._by_policy_area: dict[str, list[str]] = {}
        self._by_category: dict[str, list[str]] = {}
        self._global_patterns: dict[str, str] = {}
        self._signal_bindings: dict[str, PatternSignalBinding] = {}
        self._registry_hash: str = ""
        self._frozen: bool = False
    
    def register_global_patterns(self, registry_path: Path) -> int:
        """Register patterns from canonic_questionnaire_central/pattern_registry.json.
        
        Args:
            registry_path: Path to pattern_registry.json
            
        Returns:
            Number of patterns registered
        """
        if self._frozen:
            raise ValueError("PatternRegistry is frozen; cannot register new patterns")
        
        if not registry_path.exists():
            logger.warning(f"Global pattern registry not found: {registry_path}")
            return 0
        
        with open(registry_path, encoding="utf-8") as f:
            global_patterns = json.load(f)
        
        registered = 0
        for pattern_dict in global_patterns:
            pattern_key = pattern_dict.get("pattern_id", "")
            if not pattern_key:
                continue
            
            if pattern_key in self._patterns:
                logger.debug(f"Global pattern {pattern_key} already registered")
                continue
            
            match_type = pattern_dict.get("match_type", "REGEX")
            category = self._infer_category_from_pattern(pattern_dict.get("pattern", ""))
            produces_signals = tuple(self.CATEGORY_SIGNAL_MAP.get(category, ["baseline_completeness"]))
            
            canonical = CanonicalPattern(
                pattern_key=pattern_key,
                contract_key=None,
                policy_area_id=None,
                dimension_id=None,
                category=category,
                match_type=match_type,
                pattern=pattern_dict.get("pattern", ""),
                confidence_weight=0.85,
                specificity="MEDIUM",
                produces_signals=produces_signals,
                context_scope="PARAGRAPH",
                flags="i",
                is_global=True,
                usage_count=pattern_dict.get("usage_count", 0),
            )
            
            self._patterns[pattern_key] = canonical
            self._global_patterns[pattern_key] = pattern_key
            self._by_category.setdefault(category, []).append(pattern_key)
            
            self._signal_bindings[pattern_key] = PatternSignalBinding(
                pattern_key=pattern_key,
                signal_types=list(produces_signals),
                binding_confidence=0.85,
                binding_source="global_registry",
            )
            
            registered += 1
        
        logger.info(f"Registered {registered} global patterns from {registry_path}")
        return registered
    
    def register_from_contract(self, contract: dict[str, Any]) -> int:
        """Register all patterns from a single contract."""
        if self._frozen:
            raise ValueError("PatternRegistry is frozen")
        
        identity = contract.get("identity", {})
        contract_key = identity.get("question_id")
        policy_area_id = identity.get("policy_area_id")
        dimension_id = identity.get("dimension_id")
        
        if not contract_key:
            return 0
        
        question_context = contract.get("question_context", {})
        patterns = question_context.get("patterns", [])
        
        registered = 0
        for idx, pattern_dict in enumerate(patterns):
            pattern_key = pattern_dict.get("id", f"PAT-{contract_key}-{idx:03d}")
            
            pattern_ref = pattern_dict.get("pattern_ref")
            if pattern_ref and pattern_ref in self._global_patterns:
                self._by_contract.setdefault(contract_key, []).append(pattern_ref)
                continue
            
            if pattern_key in self._patterns:
                self._by_contract.setdefault(contract_key, []).append(pattern_key)
                continue
            
            category = pattern_dict.get("category", "GENERAL")
            produces_signals = tuple(self.CATEGORY_SIGNAL_MAP.get(category, ["baseline_completeness"]))
            
            canonical = CanonicalPattern(
                pattern_key=pattern_key,
                contract_key=contract_key,
                policy_area_id=policy_area_id or pattern_dict.get("policy_area"),
                dimension_id=dimension_id,
                category=category,
                match_type=pattern_dict.get("match_type", "REGEX"),
                pattern=pattern_dict.get("pattern", ""),
                confidence_weight=pattern_dict.get("confidence_weight", 0.85),
                specificity=pattern_dict.get("specificity", "MEDIUM"),
                produces_signals=produces_signals,
                context_scope=pattern_dict.get("context_scope", "PARAGRAPH"),
                flags=pattern_dict.get("flags", "i"),
                is_global=False,
                usage_count=0,
            )
            
            self._patterns[pattern_key] = canonical
            self._by_contract.setdefault(contract_key, []).append(pattern_key)
            
            if policy_area_id:
                self._by_policy_area.setdefault(policy_area_id, []).append(pattern_key)
            
            self._by_category.setdefault(category, []).append(pattern_key)
            
            self._signal_bindings[pattern_key] = PatternSignalBinding(
                pattern_key=pattern_key,
                signal_types=list(produces_signals),
                binding_confidence=canonical.confidence_weight,
                binding_source="contract",
            )
            
            registered += 1
        
        return registered
    
    def register_from_contracts_dir(self, contracts_dir: Path) -> int:
        """Register patterns from all contracts in a directory."""
        total_registered = 0
        contract_files = sorted(contracts_dir.glob("Q*.v3.json"))
        
        for contract_file in contract_files:
            try:
                with open(contract_file, encoding="utf-8") as f:
                    contract = json.load(f)
                registered = self.register_from_contract(contract)
                total_registered += registered
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to register patterns from {contract_file}: {e}")
        
        logger.info(f"Registered {total_registered} contract patterns from {len(contract_files)} contracts")
        return total_registered
    
    def freeze(self) -> str:
        """Freeze registry and compute integrity hash."""
        if self._frozen:
            return self._registry_hash
        
        sorted_patterns = sorted(self._patterns.items(), key=lambda x: x[0])
        serialization = [p.to_dict() for _, p in sorted_patterns]
        json_bytes = json.dumps(serialization, sort_keys=True, separators=(",", ":")).encode("utf-8")
        
        self._registry_hash = hashlib.sha256(json_bytes).hexdigest()
        self._frozen = True
        
        logger.info(f"Pattern registry frozen: {len(self._patterns)} patterns, hash={self._registry_hash[:16]}...")
        return self._registry_hash
    
    def get_pattern(self, pattern_key: str) -> CanonicalPattern | None:
        return self._patterns.get(pattern_key)
    
    def get_patterns_for_contract(self, contract_key: str) -> list[CanonicalPattern]:
        pattern_keys = self._by_contract.get(contract_key, [])
        return [self._patterns[pk] for pk in pattern_keys if pk in self._patterns]
    
    def get_patterns_for_policy_area(self, policy_area_id: str) -> list[CanonicalPattern]:
        pattern_keys = self._by_policy_area.get(policy_area_id, [])
        return [self._patterns[pk] for pk in pattern_keys if pk in self._patterns]
    
    def get_patterns_for_category(self, category: str) -> list[CanonicalPattern]:
        pattern_keys = self._by_category.get(category, [])
        return [self._patterns[pk] for pk in pattern_keys if pk in self._patterns]
    
    def get_global_patterns(self) -> list[CanonicalPattern]:
        return [self._patterns[pk] for pk in self._global_patterns.keys() if pk in self._patterns]
    
    def get_signal_binding(self, pattern_key: str) -> PatternSignalBinding | None:
        return self._signal_bindings.get(pattern_key)
    
    def get_patterns_producing_signal(self, signal_type: str) -> list[CanonicalPattern]:
        result = []
        for pattern in self._patterns.values():
            if signal_type in pattern.produces_signals:
                result.append(pattern)
        return result
    
    def resolve_pattern_ref(self, pattern_ref: str) -> CanonicalPattern | None:
        """Resolve a pattern reference (PAT-0xxx) to its canonical pattern."""
        return self._patterns.get(pattern_ref)
    
    def iter_patterns(self) -> Iterator[CanonicalPattern]:
        yield from self._patterns.values()
    
    def __len__(self) -> int:
        return len(self._patterns)
    
    def __contains__(self, pattern_key: str) -> bool:
        return pattern_key in self._patterns
    
    @property
    def is_frozen(self) -> bool:
        return self._frozen
    
    @property
    def registry_hash(self) -> str:
        return self._registry_hash
    
    def get_stats(self) -> dict[str, Any]:
        return {
            "total_patterns": len(self._patterns),
            "global_patterns": len(self._global_patterns),
            "contract_patterns": len(self._patterns) - len(self._global_patterns),
            "total_contracts": len(self._by_contract),
            "total_policy_areas": len(self._by_policy_area),
            "total_categories": len(self._by_category),
            "patterns_by_category": {cat: len(pks) for cat, pks in self._by_category.items()},
            "is_frozen": self._frozen,
            "registry_hash": self._registry_hash,
        }
    
    def _infer_category_from_pattern(self, pattern: str) -> str:
        """Infer category from pattern content."""
        pattern_lower = pattern.lower()
        
        if any(kw in pattern_lower for kw in ["dane", "ministerio", "sivigila", "sispro", "fiscalía"]):
            return "FUENTE_OFICIAL"
        if any(kw in pattern_lower for kw in ["\\d+", "tasa", "porcentaje", "indicador"]):
            return "INDICADOR"
        if any(kw in pattern_lower for kw in ["20\\d{2}", "año", "periodo", "vigencia"]):
            return "TEMPORAL"
        if any(kw in pattern_lower for kw in ["municipal", "departamental", "territorial"]):
            return "TERRITORIAL"
        if any(kw in pattern_lower for kw in ["causa", "efecto", "mecanismo", "cadena"]):
            return "CAUSAL"
        
        return "GENERAL"


_global_registry: PatternRegistry | None = None


def get_pattern_registry() -> PatternRegistry:
    """Get global pattern registry singleton."""
    global _global_registry
    if _global_registry is None:
        _global_registry = PatternRegistry()
    return _global_registry


def initialize_pattern_registry(
    global_registry_path: Path | None = None,
    contracts_dir: Path | None = None,
) -> PatternRegistry:
    """Initialize and freeze global pattern registry.
    
    Args:
        global_registry_path: Path to pattern_registry.json
        contracts_dir: Path to executor contracts directory
        
    Returns:
        Initialized and frozen PatternRegistry
    """
    global _global_registry
    _global_registry = PatternRegistry()
    
    if global_registry_path and global_registry_path.exists():
        _global_registry.register_global_patterns(global_registry_path)
    
    if contracts_dir and contracts_dir.exists():
        _global_registry.register_from_contracts_dir(contracts_dir)
    
    _global_registry.freeze()
    return _global_registry


__all__ = [
    "PatternRegistry",
    "CanonicalPattern",
    "PatternSignalBinding",
    "get_pattern_registry",
    "initialize_pattern_registry",
]
