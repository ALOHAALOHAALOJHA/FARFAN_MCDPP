#!/usr/bin/env python3
"""
Script de migración de patterns para CQC v2.0.

Consolida 3 fuentes de patterns:
1. pattern_registry.json
2. patterns/pattern_registry_v3.json
3. Patterns embebidos en questionnaire_monolith.json

Genera:
- _registry/patterns/index.json (índice maestro)
- _registry/patterns/by_category/*.json (patterns por categoría)

Autor: CQC Migration System
Versión: 2.0.0
Fecha: 2026-01-06
"""

import json
import hashlib
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CQC_ROOT = Path(__file__).parent.parent
PATTERN_REGISTRY_V1 = CQC_ROOT / "pattern_registry.json"
PATTERN_REGISTRY_V3 = CQC_ROOT / "patterns" / "pattern_registry_v3.json"
QUESTIONNAIRE_MONOLITH = CQC_ROOT / "questionnaire_monolith.json"
OUTPUT_DIR = CQC_ROOT / "_registry" / "patterns"


@dataclass
class Pattern:
    """Representación unificada de un pattern."""
    canonical_id: str
    pattern_spec: Dict[str, Any]
    classification: Dict[str, Any]
    bindings: Dict[str, List[str]] = field(default_factory=lambda: {
        "applies_to_dimensions": [],
        "applies_to_questions": [],
        "applies_to_policy_areas": [],
        "applies_to_membership_criteria": []
    })
    scoring_impact: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    examples: Dict[str, List[str]] = field(default_factory=lambda: {"positive": [], "negative": []})
    legacy_ids: List[str] = field(default_factory=list)
    content_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.canonical_id,
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
    """Migrador de patterns con deduplicación."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.patterns: Dict[str, Pattern] = {}  # content_hash -> Pattern
        self.id_counter = 1
        self.duplicates_merged = 0
        self.patterns_by_source: Dict[str, int] = Counter()

    def compute_content_hash(self, pattern_str: str, category: str = "GENERAL") -> str:
        """Computa hash del contenido del pattern."""
        content = f"{pattern_str}:{category}".lower().strip()
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def normalize_pattern(self, raw_pattern: Dict[str, Any], source: str) -> Optional[Pattern]:
        """Normaliza un pattern raw al formato unificado."""
        try:
            # Extraer pattern string
            pattern_str = raw_pattern.get("pattern", raw_pattern.get("regex", ""))
            if not pattern_str:
                logger.warning(f"Skipping pattern without pattern string from {source}")
                return None

            # Categoría
            category = raw_pattern.get("category", raw_pattern.get("type", "GENERAL")).upper()

            # Content hash
            content_hash = self.compute_content_hash(pattern_str, category)

            # Verificar si ya existe
            if content_hash in self.patterns:
                existing = self.patterns[content_hash]
                # Merge legacy IDs
                raw_id = raw_pattern.get("id", raw_pattern.get("pattern_id"))
                if raw_id and raw_id not in existing.legacy_ids:
                    existing.legacy_ids.append(str(raw_id))

                # Merge bindings
                for key in ["applies_to_questions", "applies_to_dimensions", "applies_to_policy_areas"]:
                    if key in raw_pattern:
                        existing.bindings[key] = list(set(
                            existing.bindings.get(key, []) + raw_pattern[key]
                        ))

                self.duplicates_merged += 1
                return None  # Ya existe

            # Crear nuevo pattern
            canonical_id = f"PAT-{self.id_counter:04d}"
            self.id_counter += 1

            pattern = Pattern(
                canonical_id=canonical_id,
                pattern_spec={
                    "type": raw_pattern.get("match_type", "REGEX").upper(),
                    "pattern": pattern_str,
                    "flags": raw_pattern.get("flags", ["IGNORECASE", "MULTILINE"]),
                    "captures": raw_pattern.get("captures", {})
                },
                classification={
                    "category": category,
                    "subcategory": raw_pattern.get("subcategory", ""),
                    "specificity": raw_pattern.get("specificity", "MEDIUM"),
                    "confidence_weight": float(raw_pattern.get("confidence_weight", 0.85))
                },
                bindings={
                    "applies_to_dimensions": raw_pattern.get("applies_to_dimensions", []),
                    "applies_to_questions": raw_pattern.get("applies_to_questions", []),
                    "applies_to_policy_areas": raw_pattern.get("applies_to_policy_areas", []),
                    "applies_to_membership_criteria": []
                },
                scoring_impact={
                    "weight_in_scoring": float(raw_pattern.get("weight", 0.15)),
                    "boost_conditions": raw_pattern.get("boost_conditions", []),
                    "penalty_conditions": raw_pattern.get("penalty_conditions", [])
                },
                provenance={
                    "source_file": source,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "validated": raw_pattern.get("validated", False),
                    "validation_tests": raw_pattern.get("tests", [])
                },
                examples={
                    "positive": raw_pattern.get("examples", {}).get("positive", []),
                    "negative": raw_pattern.get("examples", {}).get("negative", [])
                },
                legacy_ids=[str(raw_pattern.get("id", raw_pattern.get("pattern_id", "")))],
                content_hash=content_hash
            )

            self.patterns[content_hash] = pattern
            self.patterns_by_source[source] += 1
            return pattern

        except Exception as e:
            logger.error(f"Error normalizing pattern from {source}: {e}")
            return None

    def load_pattern_registry_v1(self) -> None:
        """Carga pattern_registry.json."""
        logger.info(f"Loading {PATTERN_REGISTRY_V1}...")

        if not PATTERN_REGISTRY_V1.exists():
            logger.warning(f"{PATTERN_REGISTRY_V1} not found, skipping")
            return

        with open(PATTERN_REGISTRY_V1) as f:
            data = json.load(f)
            # Handle both list and dict with "patterns" key
            if isinstance(data, list):
                patterns = data
            elif isinstance(data, dict):
                patterns = data.get("patterns", [])
            else:
                patterns = []

            for raw in patterns:
                self.normalize_pattern(raw, "pattern_registry.json")

        logger.info(f"  Loaded {self.patterns_by_source['pattern_registry.json']} patterns from v1")

    def load_pattern_registry_v3(self) -> None:
        """Carga patterns/pattern_registry_v3.json."""
        logger.info(f"Loading {PATTERN_REGISTRY_V3}...")

        if not PATTERN_REGISTRY_V3.exists():
            logger.warning(f"{PATTERN_REGISTRY_V3} not found, skipping")
            return

        with open(PATTERN_REGISTRY_V3) as f:
            data = json.load(f)

            # V3 puede tener estructura diferente
            if "patterns" in data:
                patterns = data["patterns"]
                if isinstance(patterns, dict):
                    patterns = list(patterns.values())
            else:
                patterns = data if isinstance(data, list) else []

            for raw in patterns:
                self.normalize_pattern(raw, "pattern_registry_v3.json")

        logger.info(f"  Loaded {self.patterns_by_source['pattern_registry_v3.json']} patterns from v3")

    def load_embedded_patterns(self) -> None:
        """Carga patterns embebidos en questionnaire_monolith.json."""
        logger.info(f"Loading embedded patterns from {QUESTIONNAIRE_MONOLITH}...")

        if not QUESTIONNAIRE_MONOLITH.exists():
            logger.warning(f"{QUESTIONNAIRE_MONOLITH} not found, skipping")
            return

        with open(QUESTIONNAIRE_MONOLITH) as f:
            data = json.load(f)
            questions = data.get("blocks", {}).get("micro_questions", [])

            for q in questions:
                q_id = q.get("question_id", "UNKNOWN")
                embedded_patterns = q.get("patterns", [])

                for raw in embedded_patterns:
                    # Agregar binding a pregunta
                    raw["applies_to_questions"] = [q_id]
                    raw["applies_to_dimensions"] = [q.get("dimension_id", "")]
                    raw["applies_to_policy_areas"] = [q.get("policy_area_id", "")]

                    self.normalize_pattern(raw, "embedded_in_questions")

        logger.info(f"  Loaded {self.patterns_by_source['embedded_in_questions']} unique patterns from embedded")

    def categorize_patterns(self) -> Dict[str, List[Pattern]]:
        """Categoriza patterns por categoría."""
        by_category = defaultdict(list)

        for pattern in self.patterns.values():
            category = pattern.classification["category"]
            by_category[category].append(pattern)

        return dict(by_category)

    def generate_index(self) -> Dict[str, Any]:
        """Genera índice maestro."""
        patterns_dict = {
            p.canonical_id: p.to_dict()
            for p in sorted(self.patterns.values(), key=lambda x: x.canonical_id)
        }

        # Estadísticas
        by_category = self.categorize_patterns()
        category_dist = {
            cat: len(patterns)
            for cat, patterns in by_category.items()
        }

        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "pattern-index-v2.0.0",
            "_meta": {
                "schema_version": "2.0.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator": "migrate_patterns.py",
                "source_files": [
                    "pattern_registry.json",
                    "patterns/pattern_registry_v3.json",
                    "questionnaire_monolith.json (embedded)"
                ],
                "deduplication_strategy": "CONTENT_HASH_MERGE"
            },
            "statistics": {
                "total_patterns": len(self.patterns),
                "unique_patterns": len(self.patterns),
                "duplicates_merged": self.duplicates_merged,
                "category_distribution": category_dist,
                "patterns_by_source": dict(self.patterns_by_source)
            },
            "patterns": patterns_dict
        }

    def save_index(self, index: Dict[str, Any]) -> None:
        """Guarda índice maestro."""
        output_file = OUTPUT_DIR / "index.json"
        logger.info(f"Saving index to {output_file}...")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        logger.info(f"  ✓ Saved {len(index['patterns'])} patterns to index.json")

    def save_by_category(self) -> None:
        """Guarda patterns por categoría."""
        by_category = self.categorize_patterns()
        output_dir = OUTPUT_DIR / "by_category"

        logger.info(f"Saving patterns by category to {output_dir}...")

        for category, patterns in by_category.items():
            patterns_dict = {
                p.canonical_id: p.to_dict()
                for p in sorted(patterns, key=lambda x: x.canonical_id)
            }

            output_file = output_dir / f"{category}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "category": category,
                    "pattern_count": len(patterns),
                    "patterns": patterns_dict
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"  ✓ Saved {len(patterns)} patterns to {category}.json")

    def generate_schema(self) -> None:
        """Genera JSON schema para patterns."""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "pattern-schema-v2.0.0",
            "title": "CQC Pattern Schema",
            "description": "Schema para patterns en CQC v2.0",
            "type": "object",
            "required": ["canonical_id", "pattern_spec", "classification"],
            "properties": {
                "canonical_id": {"type": "string", "pattern": "^PAT-\\d{4}$"},
                "legacy_ids": {"type": "array", "items": {"type": "string"}},
                "pattern_spec": {
                    "type": "object",
                    "required": ["type", "pattern"],
                    "properties": {
                        "type": {"type": "string", "enum": ["REGEX", "KEYWORD", "SEMANTIC"]},
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
                        "subcategory": {"type": "string"},
                        "specificity": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        "confidence_weight": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "bindings": {"type": "object"},
                "scoring_impact": {"type": "object"},
                "provenance": {"type": "object"},
                "examples": {"type": "object"}
            }
        }

        output_file = OUTPUT_DIR / "schema.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)

        logger.info(f"  ✓ Generated schema.json")

    def migrate(self) -> bool:
        """Ejecuta migración completa."""
        logger.info("🔄 Starting pattern migration...")

        try:
            # Cargar fuentes
            self.load_pattern_registry_v1()
            self.load_pattern_registry_v3()
            self.load_embedded_patterns()

            # Generar outputs
            index = self.generate_index()
            self.save_index(index)
            self.save_by_category()
            self.generate_schema()

            # Resumen
            logger.info("\n" + "="*80)
            logger.info("✅ PATTERN MIGRATION COMPLETED")
            logger.info("="*80)
            logger.info(f"  Total unique patterns: {len(self.patterns)}")
            logger.info(f"  Duplicates merged: {self.duplicates_merged}")
            logger.info(f"  Patterns by source:")
            for source, count in self.patterns_by_source.items():
                logger.info(f"    - {source}: {count}")
            logger.info(f"  Output location: {OUTPUT_DIR}")
            logger.info("="*80)

            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(description="Migrate patterns to CQC v2.0")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without saving")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    migrator = PatternMigrator(verbose=args.verbose)
    success = migrator.migrate()

    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
