#!/usr/bin/env python3
"""
F.A.R.F.A.N Validation Normalizer

Addresses the critical validation imbalance issue:
- Current Validation CV: 78.44% (TARGET: <40%)
- DIM01: 4.0 validations/question
- DIM02: 1.08 validations/question (98% weak validation)
- DIM03: 4.0 validations/question
- DIM04: 1.0 validations/question (100% weak validation)
- DIM05: 1.0 validations/question (100% weak validation)
- DIM06: 1.0 validations/question (100% weak validation)

Creates validation templates and applies them to under-validated dimensions.

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


class ValidationNormalizer:
    """Normalizes validation contracts across all dimensions."""

    # Validation templates for each dimension based on their analytical focus
    VALIDATION_TEMPLATES = {
        "DIM02_ACTIVIDADES": [
            {
                "type": "completeness",
                "threshold": 0.8,
                "description": "Ensures minimum text completeness",
                "priority": 1,
            },
            {
                "type": "causal_link_verification",
                "min_links": 2,
                "description": "Verifies explicit causal connections between activity and problem",
                "priority": 2,
                "colombian_context": "Activities in Colombian PDMs must explicitly link to diagnosed problems",
            },
            {
                "type": "resource_consistency",
                "check": "budget_match",
                "description": "Validates that activities have corresponding budget allocation",
                "priority": 3,
                "colombian_context": "BPIN/SIGOP numbering required for Colombian investment projects",
            },
            {
                "type": "responsibility_assignment",
                "required": True,
                "description": "Ensures responsible entity is identified",
                "priority": 4,
                "colombian_context": "Secretaría, entidad, or dependencia must be named",
            },
            {
                "type": "temporal_coherence",
                "check": "plausible_timeline",
                "description": "Validates activity duration is realistic",
                "priority": 5,
                "colombian_context": "Activities must fit within 4-year mayoral term",
            },
        ],
        "DIM04_RESULTADOS": [
            {
                "type": "completeness",
                "threshold": 0.8,
                "description": "Ensures minimum text completeness",
                "priority": 1,
            },
            {
                "type": "outcome_traceability",
                "check": "result_to_product",
                "description": "Verifies outcomes are traceable to products",
                "priority": 2,
                "colombian_context": "Results must derive from products (Ley 152 de 1994)",
            },
            {
                "type": "indicator_validity",
                "requires": ["linea_base", "meta", "unidad_medida"],
                "description": "Validates outcome indicators have baseline, target, and unit",
                "priority": 3,
                "colombian_context": "INDICADOR-PDM format following DNP standards",
            },
            {
                "type": "temporal_coherence",
                "horizon": "medium_term",
                "description": "Validates outcome temporal consistency",
                "priority": 4,
                "colombian_context": "Outcomes typically 2-4 year horizon",
            },
            {
                "type": "measurability",
                "check": "quantifiable",
                "description": "Ensures outcome can be measured",
                "priority": 5,
                "colombian_context": "DNP requires measurable outcomes for follow-up",
            },
        ],
        "DIM05_IMPACTOS": [
            {
                "type": "completeness",
                "threshold": 0.8,
                "description": "Ensures minimum text completeness",
                "priority": 1,
            },
            {
                "type": "impact_chain_completeness",
                "requires": ["outcome_to_impact_link"],
                "description": "Verifies impact chain from outcomes to long-term impacts",
                "priority": 2,
                "colombian_context": "Impacts are long-term (10+ years) structural changes",
            },
            {
                "type": "theoretical_coherence",
                "check": "change_theory_aligned",
                "description": "Validates impact aligns with theory of change",
                "priority": 3,
                "colombian_context": "Must align with Teoría de Cambio del PDM",
            },
            {
                "type": "strategic_alignment",
                "frameworks": ["PND", "ODS", "plan_sectorial"],
                "description": "Validates alignment with national/global frameworks",
                "priority": 4,
                "colombian_context": "PND, ODS, CONPES alignment required",
            },
            {
                "type": "ambition_realism_balance",
                "check": "ambitious_but_achievable",
                "description": "Balances ambitious goals with feasibility",
                "priority": 5,
                "colombian_context": "Impact targets must be ambitious yet municipality-feasible",
            },
        ],
        "DIM06_CAUSALIDAD": [
            {
                "type": "completeness",
                "threshold": 0.8,
                "description": "Ensures minimum text completeness",
                "priority": 1,
            },
            {
                "type": "causal_chain_integrity",
                "min_links": 3,
                "description": "Verifies complete causal chain from activities to impacts",
                "priority": 2,
                "colombian_context": "Cadena de resultados must be complete",
            },
            {
                "type": "assumption_explicitness",
                "requires": ["supuestos_clave"],
                "description": "Validates key assumptions are explicitly stated",
                "priority": 3,
                "colombian_context": "Supuestos y riesgos must be documented",
            },
            {
                "type": "logical_consistency",
                "check": "no_circular_reasoning",
                "description": "Detects circular reasoning or logical fallacies",
                "priority": 4,
                "colombian_context": "Common fallacy: 'we will achieve X by achieving X'",
            },
            {
                "type": "contextual_adaptation",
                "check": "territorial_specificity",
                "description": "Validates causal logic is adapted to municipal context",
                "priority": 5,
                "colombian_context": "Causal mechanisms must reflect municipal realities",
            },
        ],
    }

    def __init__(self):
        self.current_stats = {}
        self.target_stats = {}
        self.questions_by_dimension = {}

    def load_dimension_files(self) -> None:
        """Load all dimension question files."""
        print("\n=== Loading dimension files ===")

        for dim_id, dir_name in DIMENSION_DIRS.items():
            file_path = BASE_PATH / "dimensions" / dir_name / "questions.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    questions = data.get("questions", [])

                # Calculate current validation stats
                validation_counts = []
                for q in questions:
                    validations = q.get("validations", {})
                    count = len(validations) if validations else 0
                    validation_counts.append(count)

                avg_validations = (
                    sum(validation_counts) / len(validation_counts) if validation_counts else 0
                )
                weak_count = sum(1 for c in validation_counts if c <= 1)
                weak_pct = (weak_count / len(validation_counts) * 100) if validation_counts else 0

                self.current_stats[dim_id] = {
                    "question_count": len(questions),
                    "avg_validations": round(avg_validations, 2),
                    "weak_validation_count": weak_count,
                    "weak_validation_pct": round(weak_pct, 2),
                    "validation_counts": validation_counts,
                }
                self.questions_by_dimension[dim_id] = questions

                print(
                    f"  {dim_id}: {len(questions)} questions, avg {avg_validations:.2f} validations, {weak_pct:.1f}% weak"
                )

    def calculate_cv(self) -> float:
        """Calculate coefficient of variation for validation distribution."""
        averages = [self.current_stats[dim]["avg_validations"] for dim in DIMENSION_DIRS.keys()]
        if not averages:
            return 0.0

        mean = sum(averages) / len(averages)
        variance = sum((x - mean) ** 2 for x in averages) / len(averages)
        std_dev = variance**0.5

        cv = (std_dev / mean * 100) if mean > 0 else 0
        return round(cv, 2)

    def apply_validation_templates(self) -> None:
        """Apply validation templates to under-validated dimensions."""
        print("\n=== Applying validation templates ===")

        # Dimensions that need normalization (avg < 2.0 validations)
        under_validated = ["DIM04", "DIM05", "DIM06"]  # DIM02 will be handled separately

        for dim_id in under_validated:
            dir_name = DIMENSION_DIRS[dim_id]
            templates = self.VALIDATION_TEMPLATES.get(dir_name, [])

            if not templates:
                print(f"  WARNING: No templates found for {dim_id}")
                continue

            print(f"\n  Applying {len(templates)} templates to {dim_id}...")

            questions = self.questions_by_dimension.get(dim_id, [])
            updated_questions = []

            for q in questions:
                qid = q.get("question_id")
                current_validations = q.get("validations", {})

                # Apply templates
                new_validations = dict(current_validations) if current_validations else {}
                applied_count = 0

                for template in templates:
                    vtype = template["type"]
                    if vtype not in new_validations:
                        new_validations[vtype] = {
                            "type": vtype,
                            **{k: v for k, v in template.items() if k != "type"},
                            "applied_by": "validation_normalization_v3.0.0",
                            "applied_at": datetime.now().isoformat() + "Z",
                        }
                        applied_count += 1

                # Update question
                q["validations"] = new_validations
                updated_questions.append(q)

                if applied_count > 0 and qid in ["Q001", "Q016", "Q086", "Q151", "Q186", "Q221"]:
                    print(
                        f"    {qid}: Added {applied_count} new validations (total: {len(new_validations)})"
                    )

            self.questions_by_dimension[dim_id] = updated_questions

        # Special handling for DIM02 (1.08 avg - slightly above 1)
        self._normalize_dim02()

    def _normalize_dim02(self) -> None:
        """Special handling for DIM02 which has 1.08 avg validations."""
        print("\n  Applying validation templates to DIM02 (special handling)...")

        dim_id = "DIM02"
        dir_name = DIMENSION_DIRS[dim_id]
        templates = self.VALIDATION_TEMPLATES.get(dir_name, [])

        questions = self.questions_by_dimension.get(dim_id, [])
        updated_questions = []

        for q in questions:
            qid = q.get("question_id")
            current_validations = q.get("validations", {})
            current_count = len(current_validations) if current_validations else 0

            # Only add validations if currently has only 1
            if current_count <= 1:
                new_validations = dict(current_validations) if current_validations else {}
                applied_count = 0

                for template in templates:
                    vtype = template["type"]
                    if vtype not in new_validations:
                        new_validations[vtype] = {
                            "type": vtype,
                            **{k: v for k, v in template.items() if k != "type"},
                            "applied_by": "validation_normalization_v3.0.0",
                            "applied_at": datetime.now().isoformat() + "Z",
                        }
                        applied_count += 1

                q["validations"] = new_validations

                if applied_count > 0 and qid in ["Q006", "Q036", "Q066", "Q096", "Q126"]:
                    print(
                        f"    {qid}: Added {applied_count} new validations (total: {len(new_validations)})"
                    )

            updated_questions.append(q)

        self.questions_by_dimension[dim_id] = updated_questions

    def save_updated_files(self) -> None:
        """Save the updated dimension files with normalized validations."""
        print("\n=== Saving updated dimension files ===")

        for dim_id, dir_name in DIMENSION_DIRS.items():
            if dim_id not in self.questions_by_dimension:
                continue

            file_path = BASE_PATH / "dimensions" / dir_name / "questions.json"
            metadata_path = BASE_PATH / "dimensions" / dir_name / "metadata.json"

            # Load original metadata
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Save updated questions
            questions = self.questions_by_dimension[dim_id]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "dimension_id": dim_id,
                        "dimension_metadata": metadata,
                        "question_count": len(questions),
                        "questions": sorted(
                            questions, key=lambda x: int(x.get("question_id", "Q0")[1:])
                        ),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"  Saved {dir_name}/questions.json")

    def calculate_target_stats(self) -> None:
        """Calculate statistics after normalization."""
        print("\n=== Calculating target statistics ===")

        for dim_id, questions in self.questions_by_dimension.items():
            validation_counts = []
            for q in questions:
                validations = q.get("validations", {})
                count = len(validations) if validations else 0
                validation_counts.append(count)

            avg_validations = (
                sum(validation_counts) / len(validation_counts) if validation_counts else 0
            )
            weak_count = sum(1 for c in validation_counts if c <= 1)
            weak_pct = (weak_count / len(validation_counts) * 100) if validation_counts else 0

            self.target_stats[dim_id] = {
                "question_count": len(questions),
                "avg_validations": round(avg_validations, 2),
                "weak_validation_count": weak_count,
                "weak_validation_pct": round(weak_pct, 2),
            }

            print(f"  {dim_id}: avg {avg_validations:.2f} validations, {weak_pct:.1f}% weak")

    def create_validation_report(self) -> Dict[str, Any]:
        """Create a detailed validation normalization report."""
        cv_before = self.calculate_cv()

        # Calculate CV after
        averages_after = [
            self.target_stats[dim]["avg_validations"] for dim in DIMENSION_DIRS.keys()
        ]
        mean_after = sum(averages_after) / len(averages_after)
        variance_after = sum((x - mean_after) ** 2 for x in averages_after) / len(averages_after)
        cv_after = round((variance_after**0.5 / mean_after * 100) if mean_after > 0 else 0, 2)

        report = {
            "generated_at": datetime.now().isoformat() + "Z",
            "version": "3.0.0",
            "summary": {
                "cv_before": cv_before,
                "cv_after": cv_after,
                "cv_reduction_percent": (
                    round((cv_before - cv_after) / cv_before * 100, 2) if cv_before > 0 else 0
                ),
                "target_cv": 40.0,
                "target_met": cv_after < 40.0,
            },
            "before_normalization": self.current_stats,
            "after_normalization": self.target_stats,
            "improvements": {},
        }

        # Calculate improvements
        for dim_id in DIMENSION_DIRS.keys():
            before_avg = self.current_stats[dim_id]["avg_validations"]
            after_avg = self.target_stats[dim_id]["avg_validations"]
            before_weak = self.current_stats[dim_id]["weak_validation_pct"]
            after_weak = self.target_stats[dim_id]["weak_validation_pct"]

            report["improvements"][dim_id] = {
                "avg_validations_change": round(after_avg - before_avg, 2),
                "weak_validation_pct_reduction": round(before_weak - after_weak, 2),
            }

        return report

    def save_validation_templates(self) -> None:
        """Save validation templates for future reference."""
        templates_file = BASE_PATH / "validations" / "validation_templates.json"

        templates_export = {
            "version": "3.0.0",
            "generated_at": datetime.now().isoformat() + "Z",
            "description": "Validation templates for normalizing validation contracts across dimensions",
            "templates": self.VALIDATION_TEMPLATES,
        }

        with open(templates_file, "w", encoding="utf-8") as f:
            json.dump(templates_export, f, indent=2, ensure_ascii=False)

        print(f"\n=== Saved validation templates to {templates_file} ===")

    def run(self) -> Dict[str, Any]:
        """Execute the full validation normalization process."""
        print("=" * 60)
        print("F.A.R.F.A.N Validation Normalizer v3.0.0")
        print("CRITICAL FIX: Reducing Validation CV from 78.44% to <40%")
        print("=" * 60)

        self.load_dimension_files()

        cv_before = self.calculate_cv()
        print(f"\n  Current Validation CV: {cv_before}%")
        print(f"  Target CV: <40%")
        print(f"  Gap: {cv_before - 40:.2f} percentage points")

        self.apply_validation_templates()
        self.save_updated_files()
        self.calculate_target_stats()
        self.save_validation_templates()

        report = self.create_validation_report()

        # Save report
        report_file = BASE_PATH / "validations" / "normalization_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 60)
        print("Validation Normalization Complete!")
        print(f"  CV Before: {cv_before}%")
        print(f"  CV After: {report['summary']['cv_after']}%")
        print(f"  Reduction: {report['summary']['cv_reduction_percent']}%")
        print(f"  Target Met: {'YES ✓' if report['summary']['target_met'] else 'NO ✗'}")
        print(f"  Report saved to: {report_file}")
        print("=" * 60)

        return report


def main():
    normalizer = ValidationNormalizer()
    normalizer.run()


if __name__ == "__main__":
    main()
