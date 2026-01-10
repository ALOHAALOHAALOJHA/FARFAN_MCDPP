#!/usr/bin/env python3
"""
F.A.R.F.A.N Scoring Modality Diversifier

Addresses the scoring modality concentration issue:
- Current TYPE_A concentration: 86.7% (260/300 questions)
- Target: <70% TYPE_A
- Action: Reassign appropriate modalities based on question characteristics

Version: 3.0.0
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

BASE_PATH = Path("canonic_questionnaire_central")
DIMENSION_DIRS = {
    "DIM01": "DIM01_INSUMOS",
    "DIM02": "DIM02_ACTIVIDADES",
    "DIM03": "DIM03_PRODUCTOS",
    "DIM04": "DIM04_RESULTADOS",
    "DIM05": "DIM05_IMPACTOS",
    "DIM06": "DIM06_CAUSALIDAD",
}


class ScoringModalityDiversifier:
    """Diversifies scoring modalities to reduce TYPE_A concentration."""

    # Scoring modality decision criteria
    MODALITY_CRITERIA = {
        "TYPE_B": {
            "description": "Binary count - up to 3 elements, each worth 1 point",
            "criteria": [
                "expected_elements count ≤ 3",
                "all elements are binary (present/absent)",
                "no proportional scaling needed",
                "elements have equal weight",
            ],
            "max_score": 3,
            "examples": [
                "Has baseline, target, unit (3 binary checks)",
                "Identifies responsible entity, budget, timeline (3 binary checks)",
            ],
        },
        "TYPE_C": {
            "description": "2-element threshold - count 2 elements and scale to 0-3",
            "criteria": [
                "exactly 2 expected_elements",
                "both elements are required",
                "proportional scoring desired",
                "threshold-based scoring",
            ],
            "max_score": 3,
            "examples": [
                "Has both official sources AND quantitative indicators",
                "Has both risk identification AND mitigation proposal",
            ],
        },
        "TYPE_D": {
            "description": "Weighted sum - 3 elements with different weights",
            "criteria": [
                "exactly 3 expected_elements",
                "elements have different importance",
                "weighted scoring appropriate",
                "prioritization needed",
            ],
            "max_score": 3,
            "weights": [0.5, 0.3, 0.2],
            "examples": [
                "Source (50%), indicators (30%), temporal coverage (20%)",
                "Technical definition (50%), unit measure (30%), dosing (20%)",
            ],
        },
        "TYPE_E": {
            "description": "Boolean presence - if-then-else logic",
            "criteria": [
                "single critical element",
                "pass/fail nature",
                "no partial credit appropriate",
                "binary outcome",
            ],
            "max_score": 3,
            "examples": [
                "Has valid causal chain (yes/no)",
                "Meets minimum completeness threshold (yes/no)",
            ],
        },
        "TYPE_F": {
            "description": "Semantic similarity - cosine matching",
            "criteria": [
                "requires semantic understanding",
                "no exact pattern matching possible",
                "qualitative assessment needed",
                "NLP-based evaluation",
            ],
            "max_score": 3,
            "examples": [
                "Alignment with stated theory of change",
                "Coherence of narrative explanation",
                "Quality of justification provided",
            ],
        },
    }

    def __init__(self):
        self.current_distribution = {}
        self.reassignments = []
        self.questions_by_dimension = {}

    def load_all_questions(self) -> List[Dict]:
        """Load all questions from all dimensions."""
        print("\n=== Loading all questions ===")
        all_questions = []

        for dim_id, dir_name in DIMENSION_DIRS.items():
            file_path = BASE_PATH / "dimensions" / dir_name / "questions.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    questions = data.get("questions", [])
                    all_questions.extend(questions)
                    self.questions_by_dimension[dim_id] = questions

        print(f"  Loaded {len(all_questions)} questions")
        return all_questions

    def analyze_current_distribution(self, questions: List[Dict]) -> None:
        """Analyze current scoring modality distribution."""
        print("\n=== Analyzing current distribution ===")

        distribution = defaultdict(int)
        by_dimension = defaultdict(lambda: defaultdict(int))

        for q in questions:
            modality = q.get("scoring_modality", "UNKNOWN")
            dimension = q.get("dimension_id", "UNKNOWN")
            distribution[modality] += 1
            by_dimension[dimension][modality] += 1

        total = sum(distribution.values())
        self.current_distribution = {
            modality: {"count": count, "percentage": round(count / total * 100, 2)}
            for modality, count in distribution.items()
        }

        for modality, data in sorted(self.current_distribution.items()):
            print(f"  {modality}: {data['count']} questions ({data['percentage']}%)")

        print(
            f"\n  TYPE_A concentration: {self.current_distribution.get('TYPE_A', {}).get('percentage', 0)}%"
        )
        print(f"  Target: <70%")
        print(
            f"  Status: {'EXCEEDS TARGET ✗' if self.current_distribution.get('TYPE_A', {}).get('percentage', 0) >= 70 else 'WITHIN TARGET ✓'}"
        )

    def determine_optimal_modality(self, q: Dict) -> str:
        """Determine the optimal scoring modality for a question."""
        current_modality = q.get("scoring_modality", "TYPE_A")
        expected_elements = q.get("expected_elements", [])
        question_text = q.get("text", "").lower()

        # Skip already non-TYPE_A questions
        if current_modality != "TYPE_A":
            return current_modality

        elem_count = len(expected_elements)

        # TYPE_E: Boolean check for single critical element
        if elem_count == 1:
            return "TYPE_E"

        # TYPE_C: Exactly 2 elements with threshold
        if elem_count == 2:
            # Check if both are required
            required_count = sum(1 for e in expected_elements if e.get("required", False))
            if required_count == 2:
                return "TYPE_C"

        # TYPE_B: Binary count for ≤3 elements
        if elem_count <= 3:
            # Check if all are simple presence checks
            all_simple = all(
                not e.get("minimum") and not e.get("maximum") and not e.get("threshold")
                for e in expected_elements
            )
            if all_simple:
                return "TYPE_B"

        # TYPE_D: 3 elements with different weights
        if elem_count == 3:
            # Check if elements have explicit priority/weight indicators
            has_priority = any(
                e.get("required") == True
                or e.get("priority") == 1
                or "required" in str(e.get("type", "")).lower()
                for e in expected_elements
            )
            if has_priority:
                return "TYPE_D"

        # TYPE_F: Semantic similarity (qualitative assessment)
        semantic_keywords = [
            "coherencia",
            "alineación",
            "consistencia",
            "articula",
            "coherence",
            "alignment",
            "consistency",
            "articulates",
            "calidad",
            "quality",
            "adecuación",
            "appropriateness",
        ]
        if any(kw in question_text for kw in semantic_keywords):
            return "TYPE_F"

        # Default: Keep TYPE_A
        return "TYPE_A"

    def identify_reassignments(self, questions: List[Dict]) -> List[Dict]:
        """Identify questions that should be reassigned."""
        print("\n=== Identifying reassignments ===")

        reassignments = []
        type_a_questions = [q for q in questions if q.get("scoring_modality") == "TYPE_A"]
        print(f"  Found {len(type_a_questions)} TYPE_A questions to evaluate")

        for q in type_a_questions:
            qid = q.get("question_id")
            optimal = self.determine_optimal_modality(q)
            current = q.get("scoring_modality")

            if optimal != current:
                reassignments.append(
                    {
                        "question_id": qid,
                        "dimension_id": q.get("dimension_id"),
                        "policy_area_id": q.get("policy_area_id"),
                        "from_modality": current,
                        "to_modality": optimal,
                        "reason": self._get_reason(q, optimal),
                        "expected_elements_count": len(q.get("expected_elements", [])),
                    }
                )

        # Sort by dimension and question_id
        reassignments.sort(key=lambda x: (x["dimension_id"], x["question_id"]))

        print(f"  Identified {len(reassignments)} reassignments")

        # Show sample
        print("\n  Sample reassignments:")
        for r in reassignments[:10]:
            print(
                f"    {r['question_id']}: {r['from_modality']} → {r['to_modality']} ({r['reason']})"
            )

        return reassignments

    def _get_reason(self, q: Dict, optimal_modality: str) -> str:
        """Get the reason for modality reassignment."""
        elem_count = len(q.get("expected_elements", []))

        reasons = {
            "TYPE_B": f"Binary count appropriate for {elem_count} elements",
            "TYPE_C": f"2-element threshold scoring",
            "TYPE_D": f"3 elements with differential weighting",
            "TYPE_E": "Single critical element - boolean check",
            "TYPE_F": "Qualitative assessment requires semantic similarity",
        }

        return reasons.get(optimal_modality, "Optimal fit for question structure")

    def apply_reassignments(self) -> None:
        """Apply the reassignments to dimension files."""
        print("\n=== Applying reassignments ===")

        # Build lookup
        reassign_lookup = {r["question_id"]: r for r in self.reassignments}

        # Track changes by dimension
        changes_by_dimension = defaultdict(int)

        for dim_id, questions in self.questions_by_dimension.items():
            updated_questions = []

            for q in questions:
                qid = q.get("question_id")
                if qid in reassign_lookup:
                    reassign = reassign_lookup[qid]
                    old_modality = q.get("scoring_modality")
                    q["scoring_modality"] = reassign["to_modality"]
                    q["scoring_definition_ref"] = f"scoring_modalities.{reassign['to_modality']}"
                    q["modality_reassigned"] = {
                        "from": old_modality,
                        "to": reassign["to_modality"],
                        "reason": reassign["reason"],
                        "reassigned_at": datetime.now().isoformat() + "Z",
                        "reassigned_by": "scoring_diversification_v3.0.0",
                    }
                    changes_by_dimension[dim_id] += 1

                updated_questions.append(q)

            # Save updated questions
            dir_name = DIMENSION_DIRS[dim_id]
            metadata_path = BASE_PATH / "dimensions" / dir_name / "metadata.json"
            questions_path = BASE_PATH / "dimensions" / dir_name / "questions.json"

            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            with open(questions_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "dimension_id": dim_id,
                        "dimension_metadata": metadata,
                        "question_count": len(updated_questions),
                        "questions": sorted(
                            updated_questions, key=lambda x: int(x.get("question_id", "Q0")[1:])
                        ),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            if changes_by_dimension[dim_id] > 0:
                print(f"  {dim_id}: {changes_by_dimension[dim_id]} reassignments")

    def calculate_new_distribution(self) -> Dict[str, Any]:
        """Calculate the new scoring modality distribution."""
        print("\n=== Calculating new distribution ===")

        # Recalculate from updated files
        new_distribution = defaultdict(int)

        for dim_id, questions in self.questions_by_dimension.items():
            for q in questions:
                modality = q.get("scoring_modality", "UNKNOWN")
                new_distribution[modality] += 1

        total = sum(new_distribution.values())

        result = {
            modality: {"count": count, "percentage": round(count / total * 100, 2)}
            for modality, count in new_distribution.items()
        }

        for modality, data in sorted(result.items()):
            print(f"  {modality}: {data['count']} questions ({data['percentage']}%)")

        type_a_pct = result.get("TYPE_A", {}).get("percentage", 0)
        print(f"\n  TYPE_A concentration: {type_a_pct}%")
        print(f"  Target: <70%")
        print(f"  Status: {'WITHIN TARGET ✓' if type_a_pct < 70 else 'EXCEEDS TARGET ✗'}")

        return result

    def create_report(self, new_distribution: Dict) -> Dict[str, Any]:
        """Create the diversification report."""
        type_a_before = self.current_distribution.get("TYPE_A", {}).get("percentage", 0)
        type_a_after = new_distribution.get("TYPE_A", {}).get("percentage", 0)

        report = {
            "generated_at": datetime.now().isoformat() + "Z",
            "version": "3.0.0",
            "summary": {
                "type_a_before_pct": type_a_before,
                "type_a_after_pct": type_a_after,
                "type_a_reduction_pct": round(type_a_before - type_a_after, 2),
                "total_reassignments": len(self.reassignments),
                "target_met": type_a_after < 70,
            },
            "before_distribution": self.current_distribution,
            "after_distribution": new_distribution,
            "reassignments_by_modality": {},
            "reassignments_by_dimension": {},
        }

        # Group reassignments
        for r in self.reassignments:
            to_mod = r["to_modality"]
            dim = r["dimension_id"]

            report["reassignments_by_modality"][to_mod] = (
                report["reassignments_by_modality"].get(to_mod, 0) + 1
            )
            report["reassignments_by_dimension"][dim] = (
                report["reassignments_by_dimension"].get(dim, 0) + 1
            )

        return report

    def save_report(self, report: Dict) -> None:
        """Save the diversification report."""
        report_file = BASE_PATH / "scoring" / "diversification_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n=== Saved report to {report_file} ===")

    def save_modality_guide(self) -> None:
        """Save the modality selection guide."""
        guide_file = BASE_PATH / "scoring" / "modality_selection_guide.json"

        guide = {
            "version": "3.0.0",
            "generated_at": datetime.now().isoformat() + "Z",
            "description": "Guide for selecting appropriate scoring modalities",
            "modalities": self.MODALITY_CRITERIA,
        }

        with open(guide_file, "w", encoding="utf-8") as f:
            json.dump(guide, f, indent=2, ensure_ascii=False)

        print(f"=== Saved modality guide to {guide_file} ===")

    def run(self) -> Dict[str, Any]:
        """Execute the full diversification process."""
        print("=" * 60)
        print("F.A.R.F.A.N Scoring Modality Diversifier v3.0.0")
        print("REDUCING TYPE_A CONCENTRATION FROM 86.7% TO <70%")
        print("=" * 60)

        questions = self.load_all_questions()
        self.analyze_current_distribution(questions)
        self.reassignments = self.identify_reassignments(questions)
        self.apply_reassignments()
        new_distribution = self.calculate_new_distribution()
        report = self.create_report(new_distribution)
        self.save_report(report)
        self.save_modality_guide()

        print("\n" + "=" * 60)
        print("Scoring Modality Diversification Complete!")
        print(f"  TYPE_A Before: {report['summary']['type_a_before_pct']}%")
        print(f"  TYPE_A After: {report['summary']['type_a_after_pct']}%")
        print(f"  Reduction: {report['summary']['type_a_reduction_pct']} percentage points")
        print(f"  Reassignments: {report['summary']['total_reassignments']} questions")
        print(f"  Target Met: {'YES ✓' if report['summary']['target_met'] else 'NO ✗'}")
        print("=" * 60)

        return report


def main():
    diversifier = ScoringModalityDiversifier()
    diversifier.run()


if __name__ == "__main__":
    main()
