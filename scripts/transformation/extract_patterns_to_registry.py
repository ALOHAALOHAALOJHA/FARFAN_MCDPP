#!/usr/bin/env python3
"""
F.A.R.F.A.N Pattern Registry Extractor

Extracts all patterns from the modular questionnaire files and creates
a centralized pattern registry with versioning and test fixtures.

Version: 3.0.0
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Set
from datetime import datetime

BASE_PATH = Path("canonic_questionnaire_central")
PATTERNS_OUTPUT = BASE_PATH / "patterns"
DIMENSION_DIRS = [
    ("DIM01", "DIM01_INSUMOS"),
    ("DIM02", "DIM02_ACTIVIDADES"),
    ("DIM03", "DIM03_PRODUCTOS"),
    ("DIM04", "DIM04_RESULTADOS"),
    ("DIM05", "DIM05_IMPACTOS"),
    ("DIM06", "DIM06_CAUSALIDAD"),
]


class PatternRegistryExtractor:
    """Extracts and organizes all patterns from the questionnaire."""

    def __init__(self):
        self.patterns = {}  # pattern_id -> pattern_data
        self.pattern_to_questions = defaultdict(list)  # pattern_id -> [question_ids]
        self.pattern_categories = defaultdict(list)  # category -> [pattern_ids]
        self.pattern_stats = {
            "total_patterns": 0,
            "by_category": {},
            "by_specificity": {},
            "by_match_type": {},
            "unique_regex_patterns": set(),
        }

    def extract_patterns_from_file(self, file_path: Path, source_label: str) -> None:
        """Extract patterns from a questions file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        questions = data.get("questions", [])
        print(f"  Processing {len(questions)} questions from {source_label}...")

        for q in questions:
            qid = q.get("question_id")
            patterns = q.get("patterns", [])

            for p in patterns:
                # Get pattern ID
                pid = p.get("id")
                if not pid:
                    continue

                # Track which questions use this pattern
                self.pattern_to_questions[pid].append(qid)

                # Store pattern data if not already stored
                if pid not in self.patterns:
                    # Check if it's a reference
                    if "pattern_ref" in p:
                        self.patterns[pid] = {
                            "pattern_id": pid,
                            "pattern_ref": p.get("pattern_ref"),
                            "is_reference": True,
                            "match_type": p.get("match_type"),
                            "category": p.get("category"),
                            "specificity": p.get("specificity"),
                            "context_scope": p.get("context_scope"),
                        }
                    else:
                        regex = p.get("pattern", "")
                        self.patterns[pid] = {
                            "pattern_id": pid,
                            "regex": regex,
                            "is_reference": False,
                            "match_type": p.get("match_type"),
                            "category": p.get("category"),
                            "specificity": p.get("specificity"),
                            "confidence_weight": p.get("confidence_weight"),
                            "flags": p.get("flags"),
                            "context_scope": p.get("context_scope"),
                            "context_requirement": p.get("context_requirement"),
                            "semantic_expansion": p.get("semantic_expansion"),
                            "validation_rule": p.get("validation_rule"),
                            "entity_type": p.get("entity_type"),
                            "glossary_metadata": p.get("glossary_metadata"),
                            "synonym_clusters": p.get("synonym_clusters"),
                            "disambiguation_rules": p.get("disambiguation_rules"),
                            "dynamic_update": p.get("dynamic_update"),
                            "element_tags": p.get("element_tags"),
                            "evidence_modality": p.get("evidence_modality"),
                            "negative_filter": p.get("negative_filter"),
                            "numeric_parsing": p.get("numeric_parsing"),
                            "semantic_analysis": p.get("semantic_analysis"),
                            "table_structure_parsing": p.get("table_structure_parsing"),
                            "variants": p.get("variants"),
                            "version": "1.0.0",
                            "created_at": datetime.now().isoformat() + "Z",
                            "colombian_context": None,
                            "test_fixtures": [],
                        }

                        # Track unique regex patterns
                        if regex:
                            self.pattern_stats["unique_regex_patterns"].add(regex)

                    # Track category
                    category = p.get("category")
                    if category:
                        self.pattern_categories[category].append(pid)

                    # Track statistics
                    self.pattern_stats["total_patterns"] += 1
                    self.pattern_stats["by_category"][category] = (
                        self.pattern_stats["by_category"].get(category, 0) + 1
                    )
                    self.pattern_stats["by_specificity"][p.get("specificity")] = (
                        self.pattern_stats["by_specificity"].get(p.get("specificity"), 0) + 1
                    )
                    self.pattern_stats["by_match_type"][p.get("match_type")] = (
                        self.pattern_stats["by_match_type"].get(p.get("match_type"), 0) + 1
                    )

    def extract_all_patterns(self) -> None:
        """Extract patterns from all dimension files."""
        print("\n=== Extracting patterns from all dimensions ===")

        for dim_id, dir_name in DIMENSION_DIRS:
            file_path = BASE_PATH / "dimensions" / dir_name / "questions.json"
            if file_path.exists():
                self.extract_patterns_from_file(file_path, f"{dim_id} ({dir_name})")

        print(f"\n  Total unique patterns: {len(self.patterns)}")
        print(
            f"  Total pattern-question associations: {sum(len(v) for v in self.pattern_to_questions.values())}"
        )

    def analyze_pattern_usage(self) -> Dict[str, Any]:
        """Analyze which patterns are most frequently used."""
        print("\n=== Analyzing pattern usage ===")

        usage_analysis = {}
        for pid, qids in self.pattern_to_questions.items():
            usage_analysis[pid] = {
                "question_count": len(qids),
                "questions": qids,
                "pattern_data": self.patterns.get(pid, {}),
            }

        # Sort by usage
        sorted_usage = sorted(
            usage_analysis.items(), key=lambda x: x[1]["question_count"], reverse=True
        )

        print("\n  Top 20 most used patterns:")
        for pid, data in sorted_usage[:20]:
            print(f"    {pid}: {data['question_count']} questions")

        return usage_analysis

    def create_pattern_registry(self) -> Dict[str, Any]:
        """Create the centralized pattern registry."""
        print("\n=== Creating pattern registry ===")

        registry = {
            "version": "3.0.0",
            "generated_at": datetime.now().isoformat() + "Z",
            "statistics": {
                **{k: v for k, v in self.pattern_stats.items() if k != "unique_regex_patterns"},
                "unique_regex_patterns_count": len(self.pattern_stats["unique_regex_patterns"]),
                "unique_regex_patterns_sample": list(self.pattern_stats["unique_regex_patterns"])[
                    :100
                ],
            },
            "patterns": {},
            "pattern_usage": {},
            "categories": dict(self.pattern_categories),
        }

        # Add all patterns with usage info
        for pid, pattern_data in self.patterns.items():
            registry["patterns"][pid] = {
                **pattern_data,
                "usage": {
                    "question_count": len(self.pattern_to_questions[pid]),
                    "question_ids": sorted(
                        self.pattern_to_questions[pid], key=lambda x: int(x[1:])
                    ),
                },
            }

        # Add detailed usage analysis
        sorted_usage = sorted(
            self.pattern_to_questions.items(), key=lambda x: len(x[1]), reverse=True
        )
        registry["pattern_usage"] = {
            pid: {
                "question_count": len(qids),
                "question_ids": sorted(qids, key=lambda x: int(x[1:])),
            }
            for pid, qids in sorted_usage
        }

        return registry

    def save_registry(self, registry: Dict[str, Any]) -> None:
        """Save the pattern registry to files."""
        # Save main registry
        registry_file = PATTERNS_OUTPUT / "pattern_registry_v3.json"
        with open(registry_file, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print(f"\n=== Saved pattern registry to {registry_file} ===")

        # Save pattern summary
        summary = {
            "total_patterns": registry["statistics"]["total_patterns"],
            "categories": registry["statistics"]["by_category"],
            "specificity_distribution": registry["statistics"]["by_specificity"],
            "match_type_distribution": registry["statistics"]["by_match_type"],
            "top_20_patterns": dict(list(registry["pattern_usage"].items())[:20]),
        }
        summary_file = PATTERNS_OUTPUT / "pattern_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"=== Saved pattern summary to {summary_file} ===")

    def create_pattern_templates(self) -> None:
        """Create template files for pattern test fixtures and documentation."""
        # Test fixtures template
        fixtures_template = {
            "description": "Test fixtures for patterns to verify matching behavior",
            "template": {
                "pattern_id": "PAT-XXXX",
                "regex": "example|pattern",
                "test_fixtures": [
                    {
                        "text": "Example text that should match",
                        "should_match": True,
                        "expected_matches": ["example"],
                    },
                    {
                        "text": "Example text that should not match",
                        "should_match": False,
                        "expected_matches": [],
                    },
                ],
                "colombian_context": "Description of Colombian municipal planning context",
                "legal_references": ["Ley XXX de YYYY"],
            },
        }

        fixtures_file = PATTERNS_OUTPUT / "pattern_tests" / "test_fixtures_template.json"
        fixtures_file.parent.mkdir(parents=True, exist_ok=True)
        with open(fixtures_file, "w", encoding="utf-8") as f:
            json.dump(fixtures_template, f, indent=2, ensure_ascii=False)
        print(f"=== Created test fixtures template at {fixtures_file} ===")

        # Pattern documentation template
        doc_template = {
            "pattern_id": "PAT-XXXX",
            "purpose": "What this pattern detects in municipal development plans",
            "regex_explanation": "Explanation of how the regex works",
            "examples_from_pdm": [
                {
                    "municipality": "Example Municipality",
                    "excerpt": "Text excerpt from PDM",
                    "year": 2024,
                }
            ],
            "false_positives": ["Known cases where pattern matches incorrectly"],
            "false_negatives": ["Known cases where pattern should match but doesn't"],
            "related_patterns": ["PAT-YYYY", "PAT-ZZZZ"],
        }

        doc_file = PATTERNS_OUTPUT / "pattern_tests" / "documentation_template.json"
        with open(doc_file, "w", encoding="utf-8") as f:
            json.dump(doc_template, f, indent=2, ensure_ascii=False)
        print(f"=== Created documentation template at {doc_file} ===")

    def run(self) -> None:
        """Execute the full pattern extraction process."""
        print("=" * 60)
        print("F.A.R.F.A.N Pattern Registry Extractor v3.0.0")
        print("=" * 60)

        self.extract_all_patterns()
        self.analyze_pattern_usage()
        registry = self.create_pattern_registry()
        self.save_registry(registry)
        self.create_pattern_templates()

        print("\n" + "=" * 60)
        print("Pattern registry extraction complete!")
        print("=" * 60)


def main():
    extractor = PatternRegistryExtractor()
    extractor.run()


if __name__ == "__main__":
    main()
