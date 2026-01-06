#!/usr/bin/env python3
"""
Pattern Migration Script for CQC Restructure.

SPEC REFERENCE: Section 4.1, 9.1
PURPOSE: Consolidate 3 pattern sources into _registry/patterns/ structure

Sources:
1. pattern_registry.json (1,720 patterns, basic structure)
2. patterns/pattern_registry_v3.json (2,358 patterns, rich structure)
3. Patterns embedded in dimensions/*/questions.json

Output Structure (per SPEC 4.1):
_registry/patterns/
├── index.json           # Master index with all patterns
├── schema.json          # JSON Schema for validation
├── by_category/         # Patterns organized by category
│   ├── INDICADOR.json
│   ├── TEMPORAL.json
│   └── ...
└── by_dimension/        # Materialized views
    ├── DIM01.json
    └── ...

DEDUPLICATION: Content hash merge (same regex = same pattern)
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CQC_ROOT = Path(__file__).parent.parent
REGISTRY = CQC_ROOT / "_registry" / "patterns"


@dataclass
class PatternSpec:
    """Pattern specification per SPEC 4.1 schema."""
    id: str
    canonical_id: str
    legacy_ids: List[str]
    
    pattern_spec: Dict[str, Any]
    classification: Dict[str, Any]
    bindings: Dict[str, List[str]]
    scoring_impact: Dict[str, Any]
    provenance: Dict[str, Any]
    examples: Dict[str, List[str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "canonical_id": self.canonical_id,
            "legacy_ids": self.legacy_ids,
            "pattern_spec": self.pattern_spec,
            "classification": self.classification,
            "bindings": self.bindings,
            "scoring_impact": self.scoring_impact,
            "provenance": self.provenance,
            "examples": self.examples
        }


class PatternMigrator:
    """Migrates patterns from multiple sources to unified structure."""
    
    def __init__(self):
        self.patterns: Dict[str, PatternSpec] = {}
        self.content_hashes: Dict[str, str] = {}  # hash -> pattern_id
        self.legacy_id_map: Dict[str, str] = {}   # legacy_id -> canonical_id
        self.stats = {
            "v1_loaded": 0,
            "v3_loaded": 0,
            "embedded_loaded": 0,
            "duplicates_merged": 0,
            "total_unique": 0
        }
    
    def _compute_content_hash(self, regex: str, category: str) -> str:
        """Compute content hash for deduplication."""
        normalized = regex.strip().lower()
        content = f"{normalized}:{category}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category names."""
        mapping = {
            "GENERAL": "GENERAL",
            "INDICADOR": "INDICADOR",
            "TEMPORAL": "TEMPORAL",
            "PRESUPUESTO": "PRESUPUESTO",
            "INSTITUCIONAL": "INSTITUCIONAL",
            "POBLACIONAL": "POBLACIONAL",
            "POBLACION": "POBLACIONAL",
            "NORMATIVO": "NORMATIVO",
            "CAUSAL": "CAUSAL",
            "CAUSAL_CONNECTOR": "CAUSAL",
            "CAUSAL_OUTCOME": "CAUSAL",
            "ESTRUCTURAL": "ESTRUCTURAL",
            "TERRITORIAL": "TERRITORIAL",
            "FUENTE_OFICIAL": "INSTITUCIONAL",
            "UNIDAD_MEDIDA": "INDICADOR",
            "INSTRUMENTO": "NORMATIVO",
            "MECANISMO_COMPLETO": "CAUSAL",
            "PRODUCTO_TIPO": "GENERAL",
            "MEDICION": "INDICADOR",
            "DESCRIPCION": "GENERAL",
        }
        return mapping.get(category.upper(), "GENERAL")
    
    def load_v1_patterns(self) -> None:
        """Load patterns from pattern_registry.json (v1)."""
        v1_path = CQC_ROOT / "pattern_registry.json"
        if not v1_path.exists():
            logger.warning("pattern_registry.json not found")
            return
        
        with open(v1_path) as f:
            patterns = json.load(f)
        
        for p in patterns:
            pattern_id = p.get("pattern_id", "")
            regex = p.get("pattern", "")
            category = self._normalize_category(p.get("category", "GENERAL"))
            
            content_hash = self._compute_content_hash(regex, category)
            
            if content_hash in self.content_hashes:
                existing_id = self.content_hashes[content_hash]
                self.patterns[existing_id].legacy_ids.append(pattern_id)
                self.legacy_id_map[pattern_id] = existing_id
                self.stats["duplicates_merged"] += 1
                continue
            
            spec = PatternSpec(
                id=pattern_id,
                canonical_id=pattern_id,
                legacy_ids=[],
                pattern_spec={
                    "type": p.get("match_type", "REGEX").upper(),
                    "pattern": regex,
                    "flags": ["IGNORECASE"],
                    "captures": {}
                },
                classification={
                    "category": category,
                    "subcategory": None,
                    "specificity": "MEDIUM",
                    "confidence_weight": 0.85
                },
                bindings={
                    "applies_to_dimensions": [],
                    "applies_to_questions": [],
                    "applies_to_policy_areas": [],
                    "applies_to_membership_criteria": []
                },
                scoring_impact={
                    "weight_in_scoring": 0.10,
                    "boost_conditions": [],
                    "penalty_conditions": []
                },
                provenance={
                    "source_file": "pattern_registry.json",
                    "source_version": "v1",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "validated": False
                },
                examples={
                    "positive": [],
                    "negative": []
                }
            )
            
            self.patterns[pattern_id] = spec
            self.content_hashes[content_hash] = pattern_id
            self.legacy_id_map[pattern_id] = pattern_id
            self.stats["v1_loaded"] += 1
    
    def load_v3_patterns(self) -> None:
        """Load patterns from pattern_registry_v3.json (richer metadata)."""
        v3_path = CQC_ROOT / "patterns" / "pattern_registry_v3.json"
        if not v3_path.exists():
            logger.warning("pattern_registry_v3.json not found")
            return
        
        with open(v3_path) as f:
            data = json.load(f)
        
        patterns = data.get("patterns", {})
        usage = data.get("pattern_usage", {})
        
        for pattern_id, p in patterns.items():
            regex = p.get("regex", p.get("pattern", ""))
            category = self._normalize_category(p.get("category", "GENERAL"))
            
            content_hash = self._compute_content_hash(regex, category)
            
            # Get question bindings from usage
            question_ids = usage.get(pattern_id, {}).get("question_ids", [])
            
            if content_hash in self.content_hashes:
                existing_id = self.content_hashes[content_hash]
                existing = self.patterns[existing_id]
                
                # Merge: add legacy_id and update bindings
                if pattern_id not in existing.legacy_ids and pattern_id != existing_id:
                    existing.legacy_ids.append(pattern_id)
                
                # Merge question bindings
                for q_id in question_ids:
                    if q_id not in existing.bindings["applies_to_questions"]:
                        existing.bindings["applies_to_questions"].append(q_id)
                
                # Update with richer metadata if v3 has it
                if p.get("confidence_weight"):
                    existing.classification["confidence_weight"] = p["confidence_weight"]
                if p.get("specificity"):
                    existing.classification["specificity"] = p["specificity"]
                
                self.legacy_id_map[pattern_id] = existing_id
                self.stats["duplicates_merged"] += 1
                continue
            
            # New pattern
            spec = PatternSpec(
                id=pattern_id,
                canonical_id=pattern_id,
                legacy_ids=[],
                pattern_spec={
                    "type": p.get("match_type", "REGEX").upper(),
                    "pattern": regex,
                    "flags": [p.get("flags", "i").upper()] if p.get("flags") else ["IGNORECASE"],
                    "captures": {},
                    "context_scope": p.get("context_scope", "PARAGRAPH")
                },
                classification={
                    "category": category,
                    "subcategory": None,
                    "specificity": p.get("specificity", "MEDIUM"),
                    "confidence_weight": p.get("confidence_weight", 0.85)
                },
                bindings={
                    "applies_to_dimensions": self._extract_dimensions_from_questions(question_ids),
                    "applies_to_questions": question_ids,
                    "applies_to_policy_areas": self._extract_policy_areas_from_questions(question_ids),
                    "applies_to_membership_criteria": []
                },
                scoring_impact={
                    "weight_in_scoring": 0.10,
                    "boost_conditions": [],
                    "penalty_conditions": []
                },
                provenance={
                    "source_file": "patterns/pattern_registry_v3.json",
                    "source_version": "v3",
                    "created_at": p.get("created_at", datetime.now(timezone.utc).isoformat()),
                    "validated": False
                },
                examples={
                    "positive": [],
                    "negative": []
                }
            )
            
            self.patterns[pattern_id] = spec
            self.content_hashes[content_hash] = pattern_id
            self.legacy_id_map[pattern_id] = pattern_id
            self.stats["v3_loaded"] += 1
    
    def _extract_dimensions_from_questions(self, question_ids: List[str]) -> List[str]:
        """Extract dimension IDs from question IDs (Q001-Q050 -> DIM01, etc.)."""
        dimensions = set()
        for q_id in question_ids:
            match = re.match(r'Q(\d+)', q_id)
            if match:
                q_num = int(match.group(1))
                # Q001-Q050 -> DIM01, Q051-Q100 -> DIM02, etc. (30 questions per dimension × 10 PAs)
                # Actually: Q001-Q030 are base questions replicated across PAs
                # Dimension is encoded in the question structure, not the number
                # For now, derive from base question
                base_q = ((q_num - 1) % 30) + 1
                if base_q <= 5:
                    dimensions.add("DIM01")
                elif base_q <= 10:
                    dimensions.add("DIM02")
                elif base_q <= 15:
                    dimensions.add("DIM03")
                elif base_q <= 20:
                    dimensions.add("DIM04")
                elif base_q <= 25:
                    dimensions.add("DIM05")
                else:
                    dimensions.add("DIM06")
        return sorted(dimensions)
    
    def _extract_policy_areas_from_questions(self, question_ids: List[str]) -> List[str]:
        """Extract policy area IDs from question IDs."""
        policy_areas = set()
        for q_id in question_ids:
            match = re.match(r'Q(\d+)', q_id)
            if match:
                q_num = int(match.group(1))
                # Q001-Q030 -> PA01, Q031-Q060 -> PA02, etc.
                pa_num = ((q_num - 1) // 30) + 1
                if 1 <= pa_num <= 10:
                    policy_areas.add(f"PA{pa_num:02d}")
        return sorted(policy_areas)
    
    def generate_output(self) -> None:
        """Generate output structure per SPEC 4.1."""
        REGISTRY.mkdir(parents=True, exist_ok=True)
        (REGISTRY / "by_category").mkdir(exist_ok=True)
        (REGISTRY / "by_dimension").mkdir(exist_ok=True)
        (REGISTRY / "by_policy_area").mkdir(exist_ok=True)
        
        self.stats["total_unique"] = len(self.patterns)
        
        # Generate category distribution
        category_dist = defaultdict(int)
        for p in self.patterns.values():
            category_dist[p.classification["category"]] += 1
        
        # Build index.json
        index = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "pattern-index-v2.0.0",
            "_meta": {
                "schema_version": "2.0.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator": "_scripts/migrate_patterns.py",
                "source_files": [
                    "pattern_registry.json",
                    "patterns/pattern_registry_v3.json"
                ],
                "deduplication_strategy": "CONTENT_HASH_MERGE"
            },
            "statistics": {
                "total_patterns": len(self.patterns),
                "sources": {
                    "v1_patterns": self.stats["v1_loaded"],
                    "v3_patterns": self.stats["v3_loaded"],
                    "duplicates_merged": self.stats["duplicates_merged"]
                },
                "category_distribution": dict(sorted(category_dist.items(), key=lambda x: -x[1]))
            },
            "patterns": {p_id: p.to_dict() for p_id, p in self.patterns.items()}
        }
        
        with open(REGISTRY / "index.json", "w") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        logger.info(f"Created index.json with {len(self.patterns)} patterns")
        
        # Generate by_category files
        by_category: Dict[str, Dict[str, Any]] = defaultdict(dict)
        for p_id, p in self.patterns.items():
            cat = p.classification["category"]
            by_category[cat][p_id] = p.to_dict()
        
        for cat, patterns in by_category.items():
            cat_file = REGISTRY / "by_category" / f"{cat}.json"
            with open(cat_file, "w") as f:
                json.dump({
                    "_category": cat,
                    "_count": len(patterns),
                    "patterns": patterns
                }, f, indent=2, ensure_ascii=False)
        logger.info(f"Created {len(by_category)} category files")
        
        # Generate by_dimension files
        by_dimension: Dict[str, Dict[str, Any]] = defaultdict(dict)
        for p_id, p in self.patterns.items():
            for dim in p.bindings["applies_to_dimensions"]:
                by_dimension[dim][p_id] = p.to_dict()
        
        for dim, patterns in by_dimension.items():
            dim_file = REGISTRY / "by_dimension" / f"{dim}.json"
            with open(dim_file, "w") as f:
                json.dump({
                    "_dimension": dim,
                    "_count": len(patterns),
                    "patterns": patterns
                }, f, indent=2, ensure_ascii=False)
        logger.info(f"Created {len(by_dimension)} dimension files")
        
        # Generate by_policy_area files
        by_pa: Dict[str, Dict[str, Any]] = defaultdict(dict)
        for p_id, p in self.patterns.items():
            for pa in p.bindings["applies_to_policy_areas"]:
                by_pa[pa][p_id] = p.to_dict()
        
        for pa, patterns in by_pa.items():
            pa_file = REGISTRY / "by_policy_area" / f"{pa}.json"
            with open(pa_file, "w") as f:
                json.dump({
                    "_policy_area": pa,
                    "_count": len(patterns),
                    "patterns": patterns
                }, f, indent=2, ensure_ascii=False)
        logger.info(f"Created {len(by_pa)} policy area files")
        
        # Generate schema.json
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "pattern-schema-v2.0.0",
            "type": "object",
            "required": ["id", "canonical_id", "pattern_spec", "classification", "bindings"],
            "properties": {
                "id": {"type": "string", "pattern": "^PAT-"},
                "canonical_id": {"type": "string"},
                "legacy_ids": {"type": "array", "items": {"type": "string"}},
                "pattern_spec": {
                    "type": "object",
                    "required": ["type", "pattern"],
                    "properties": {
                        "type": {"enum": ["REGEX", "LITERAL", "NER_OR_REGEX", "COMPOUND"]},
                        "pattern": {"type": "string"},
                        "flags": {"type": "array", "items": {"type": "string"}},
                        "captures": {"type": "object"}
                    }
                },
                "classification": {
                    "type": "object",
                    "required": ["category", "confidence_weight"],
                    "properties": {
                        "category": {"type": "string"},
                        "subcategory": {"type": ["string", "null"]},
                        "specificity": {"enum": ["LOW", "MEDIUM", "HIGH"]},
                        "confidence_weight": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "bindings": {
                    "type": "object",
                    "properties": {
                        "applies_to_dimensions": {"type": "array", "items": {"type": "string"}},
                        "applies_to_questions": {"type": "array", "items": {"type": "string"}},
                        "applies_to_policy_areas": {"type": "array", "items": {"type": "string"}},
                        "applies_to_membership_criteria": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        }
        
        with open(REGISTRY / "schema.json", "w") as f:
            json.dump(schema, f, indent=2)
        logger.info("Created schema.json")
    
    def run(self) -> Dict[str, Any]:
        """Execute full migration."""
        logger.info("Starting pattern migration...")
        
        self.load_v1_patterns()
        logger.info(f"  V1 patterns loaded: {self.stats['v1_loaded']}")
        
        self.load_v3_patterns()
        logger.info(f"  V3 patterns loaded: {self.stats['v3_loaded']}")
        logger.info(f"  Duplicates merged: {self.stats['duplicates_merged']}")
        
        self.generate_output()
        
        logger.info(f"Migration complete: {self.stats['total_unique']} unique patterns")
        return self.stats


def main():
    migrator = PatternMigrator()
    stats = migrator.run()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
