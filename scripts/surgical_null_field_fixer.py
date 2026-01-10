"""
Surgical NULL Field Fixer - Operation 1

Systematically populates null validation_rule, context_requirement, and semantic_expansion
fields across all 300 questions in 20 questions.json files.

Author: Python Detective
Date: 2026-01-06
Status: SURGICAL OPERATION 1
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


class NullFieldPopulator:
    """
    Intelligently populates null fields based on pattern characteristics.

    Uses template-based generation from pattern category, match_type, and content.
    """

    def __init__(self):
        self.stats = {
            "files_processed": 0,
            "patterns_fixed": 0,
            "validation_rules_added": 0,
            "context_requirements_added": 0,
            "semantic_expansions_added": 0,
        }

    def generate_validation_rule(self, pattern: Dict[str, Any]) -> Optional[str]:
        """
        Generate validation_rule based on pattern characteristics.

        Templates:
        - FUENTE_OFICIAL: must_be_capitalized
        - INDICADOR with numbers: must_have_numeric_value
        - TEMPORAL with years: must_match_year_format
        - NER patterns: must_be_proper_noun
        - REGEX patterns: must_match_full_pattern
        """
        category = pattern.get("category", "GENERAL")
        match_type = pattern.get("match_type", "REGEX")
        pattern_str = pattern.get("pattern", "")

        # Already has value
        if pattern.get("validation_rule"):
            return pattern["validation_rule"]

        # Category-based rules
        if category == "FUENTE_OFICIAL":
            return "must_be_capitalized"
        elif category == "INDICADOR":
            if "\\d" in pattern_str or "%" in pattern_str:
                return "must_have_numeric_value"
            else:
                return "must_match_full_pattern"
        elif category == "TEMPORAL":
            if "20\\d{2}" in pattern_str or "19\\d{2}" in pattern_str:
                return "must_match_year_format"
            else:
                return "must_indicate_time_reference"
        elif category == "UNIDAD_MEDIDA":
            return "must_have_numeric_prefix"
        elif category == "FINANCIAL" or category == "PRESUPUESTO":
            return "must_have_currency_or_numeric_value"

        # Match type based rules
        if match_type == "NER_OR_REGEX":
            return "must_be_proper_noun"
        elif match_type == "LITERAL":
            return "must_match_exact"

        # Default
        return "must_match_full_pattern"

    def generate_context_requirement(self, pattern: Dict[str, Any]) -> Optional[str]:
        """
        Generate context_requirement based on pattern category and context_scope.

        Templates:
        - FUENTE_OFICIAL: within_diagnostic_section
        - INDICADOR: near_quantitative_claim
        - TEMPORAL: within_temporal_context
        - FINANCIAL: within_budget_section
        - CAUSAL: near_action_verb
        """
        category = pattern.get("category", "GENERAL")
        context_scope = pattern.get("context_scope", "PARAGRAPH")

        # Already has value
        if pattern.get("context_requirement"):
            return pattern["context_requirement"]

        # Category-based context
        if category == "FUENTE_OFICIAL":
            return "within_diagnostic_section"
        elif category == "INDICADOR":
            return "near_quantitative_claim"
        elif category == "TEMPORAL":
            return "within_temporal_context"
        elif category == "UNIDAD_MEDIDA":
            return "adjacent_to_numeric_value"
        elif category == "FINANCIAL" or category == "PRESUPUESTO":
            return "within_budget_section"
        elif category == "CAUSAL":
            return "near_action_verb"
        elif category == "PROGRAMMATIC":
            return "within_program_description"
        elif category == "INSTITUTIONAL":
            return "within_institutional_mention"

        # Scope-based default
        if context_scope == "SENTENCE":
            return "within_same_sentence"
        elif context_scope == "PARAGRAPH":
            return "within_same_paragraph"

        # Default
        return "within_relevant_section"

    def generate_semantic_expansion(
        self, pattern: Dict[str, Any]
    ) -> Optional[Dict[str, List[str]]]:
        """
        Generate semantic_expansion for patterns with known entities or terms.

        Only generates for patterns with identifiable entities (NER, FUENTE_OFICIAL, etc.)
        Returns None for general patterns.
        """
        category = pattern.get("category", "GENERAL")
        match_type = pattern.get("match_type", "REGEX")
        pattern_str = pattern.get("pattern", "")

        # Already has value
        existing = pattern.get("semantic_expansion")
        if existing and existing is not None:
            return existing

        # Only generate for specific categories
        if category not in ["FUENTE_OFICIAL", "INSTITUTIONAL", "PROGRAMMATIC"]:
            return None

        if match_type not in ["NER_OR_REGEX", "NER"]:
            return None

        # Extract entities from pattern (pipe-separated terms)
        if "|" in pattern_str:
            entities = [e.strip() for e in pattern_str.split("|")]

            # Build semantic expansion dict
            expansion = {}
            for entity in entities[:5]:  # Limit to first 5 entities
                # Clean entity (remove regex chars)
                clean_entity = re.sub(r"[\\()?.*+\[\]]", "", entity).strip()

                if len(clean_entity) > 3:  # Only for meaningful entities
                    expansion[clean_entity] = [
                        f"referencia a {clean_entity}",
                        f"mención de {clean_entity}",
                    ]

            return expansion if expansion else None

        return None

    def fix_pattern(self, pattern: Dict[str, Any]) -> bool:
        """
        Fix null fields in a single pattern.

        Returns True if any field was fixed.
        """
        fixed = False

        # Fix validation_rule
        if pattern.get("validation_rule") is None:
            rule = self.generate_validation_rule(pattern)
            if rule:
                pattern["validation_rule"] = rule
                self.stats["validation_rules_added"] += 1
                fixed = True

        # Fix context_requirement
        if pattern.get("context_requirement") is None:
            ctx = self.generate_context_requirement(pattern)
            if ctx:
                pattern["context_requirement"] = ctx
                self.stats["context_requirements_added"] += 1
                fixed = True

        # Fix semantic_expansion
        if pattern.get("semantic_expansion") is None:
            sem = self.generate_semantic_expansion(pattern)
            if sem:
                pattern["semantic_expansion"] = sem
                self.stats["semantic_expansions_added"] += 1
                fixed = True

        if fixed:
            self.stats["patterns_fixed"] += 1

        return fixed

    def process_questions_file(self, file_path: Path) -> Dict[str, int]:
        """Process a single questions.json file."""
        print(f"📄 Processing: {file_path.relative_to(file_path.parents[3])}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        patterns_fixed = 0

        # Process all questions
        for question in data.get("questions", []):
            # Process all patterns in question
            for pattern in question.get("patterns", []):
                if self.fix_pattern(pattern):
                    patterns_fixed += 1

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.stats["files_processed"] += 1

        return {"patterns_fixed": patterns_fixed}

    def process_all_files(self, root_path: Path) -> None:
        """Process all questions.json files in the repository."""

        # Find all questions.json files
        questions_files = list(root_path.glob("**/questions.json"))

        print(f"🔍 Found {len(questions_files)} questions.json files\n")

        for file_path in sorted(questions_files):
            result = self.process_questions_file(file_path)
            print(f"   ✓ Fixed {result['patterns_fixed']} patterns\n")

        # Print summary
        print("=" * 70)
        print("📊 SURGICAL OPERATION 1: COMPLETE")
        print("=" * 70)
        print(f"Files processed:              {self.stats['files_processed']}")
        print(f"Total patterns fixed:         {self.stats['patterns_fixed']}")
        print(f"Validation rules added:       {self.stats['validation_rules_added']}")
        print(f"Context requirements added:   {self.stats['context_requirements_added']}")
        print(f"Semantic expansions added:    {self.stats['semantic_expansions_added']}")
        print("=" * 70)


def main():
    """Execute surgical operation 1."""

    root_path = Path(__file__).resolve().parent.parent / "canonic_questionnaire_central"

    populator = NullFieldPopulator()
    populator.process_all_files(root_path)

    print("\n✨ NULL FIELD EPIDEMIC: ERADICATED")


if __name__ == "__main__":
    main()
