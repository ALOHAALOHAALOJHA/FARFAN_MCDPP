"""
Phase 4 Input Contract

Defines and validates the input contract for Phase 4.

Input:
- 300 ScoredMicroQuestion objects from Phase 3
- 5 questions × 6 dimensions × 10 policy areas
- Each question must have quality scores in appropriate ranges

Module: src/farfan_pipeline/phases/Phase_04/contracts/phase4_input_contract.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Phase4InputContract:
    """
    Input contract validator for Phase 4.
    
    Validates:
    - Total count: 300 ScoredMicroQuestion objects
    - Coverage: All 6 dimensions × 10 policy areas × 5 questions represented
    - Bounds: All scores within valid ranges
    - Structure: Each scored result has required fields
    """

    EXPECTED_INPUT_COUNT = 300  # 5 questions × 6 dimensions × 10 policy areas
    EXPECTED_DIMENSIONS = 6
    EXPECTED_POLICY_AREAS = 10
    EXPECTED_QUESTIONS_PER_CELL = 5

    @staticmethod
    def validate(scored_results: list[Any]) -> tuple[bool, dict[str, Any]]:
        """
        Validate Phase 4 input contract.
        
        Args:
            scored_results: List of ScoredMicroQuestion objects from Phase 3
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            "contract": "Phase4InputContract",
            "version": __version__,
            "total_count": len(scored_results),
            "expected_count": Phase4InputContract.EXPECTED_INPUT_COUNT,
            "errors": [],
            "warnings": [],
            "is_valid": True,
        }

        # Precondition 1: Count validation
        if len(scored_results) != Phase4InputContract.EXPECTED_INPUT_COUNT:
            report["errors"].append(
                f"Expected {Phase4InputContract.EXPECTED_INPUT_COUNT} "
                f"ScoredMicroQuestion objects, got {len(scored_results)}"
            )
            report["is_valid"] = False

        # Precondition 2: Structure validation
        if not scored_results:
            report["errors"].append("Empty input: no scored results provided")
            report["is_valid"] = False
            return report["is_valid"], report

        # Check for required attributes
        required_attrs = ["question_id", "policy_area", "dimension"]
        sample = scored_results[0]
        for attr in required_attrs:
            if not hasattr(sample, attr):
                report["errors"].append(f"Missing required attribute: {attr}")
                report["is_valid"] = False

        # Precondition 3: Coverage validation
        # Group by (policy_area, dimension)
        coverage = {}
        for result in scored_results:
            try:
                key = (result.policy_area, result.dimension)
                if key not in coverage:
                    coverage[key] = []
                coverage[key].append(result.question_id)
            except AttributeError as e:
                report["errors"].append(f"Missing attribute in scored result: {e}")
                report["is_valid"] = False
                break

        expected_cells = Phase4InputContract.EXPECTED_DIMENSIONS * Phase4InputContract.EXPECTED_POLICY_AREAS
        if len(coverage) != expected_cells:
            report["errors"].append(
                f"Expected {expected_cells} dimension-policy cells, got {len(coverage)}"
            )
            report["is_valid"] = False

        # Check that each cell has expected number of questions
        for cell, questions in coverage.items():
            if len(questions) != Phase4InputContract.EXPECTED_QUESTIONS_PER_CELL:
                report["warnings"].append(
                    f"Cell {cell} has {len(questions)} questions, "
                    f"expected {Phase4InputContract.EXPECTED_QUESTIONS_PER_CELL}"
                )

        # Precondition 4: Bounds validation
        # Check if score attribute exists and is valid
        score_attr = None
        for attr in ["score", "final_score", "calibrated_score"]:
            if hasattr(sample, attr):
                score_attr = attr
                break

        if score_attr:
            invalid_scores = []
            for result in scored_results:
                score = getattr(result, score_attr, None)
                if score is not None and (score < 0.0 or score > 3.0):
                    invalid_scores.append((result.question_id, score))
            
            if invalid_scores:
                report["warnings"].append(
                    f"Found {len(invalid_scores)} scores outside [0.0, 3.0] range"
                )

        report["coverage_stats"] = {
            "total_cells": len(coverage),
            "expected_cells": expected_cells,
            "cells_with_full_coverage": sum(
                1 for q in coverage.values() 
                if len(q) == Phase4InputContract.EXPECTED_QUESTIONS_PER_CELL
            ),
        }

        return report["is_valid"], report

    @staticmethod
    def validate_file_preconditions() -> tuple[bool, dict[str, Any]]:
        """
        Validate file-level preconditions (that Phase 3 output exists).
        
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            "contract": "Phase4InputContract.file_preconditions",
            "version": __version__,
            "checks": [],
            "is_valid": True,
        }

        # Check that Phase 3 module is importable
        try:
            # Attempt to import Phase 3
            import farfan_pipeline.phases.Phase_3
            report["checks"].append({
                "name": "Phase 3 module importable",
                "status": "PASS",
            })
        except ImportError as e:
            report["checks"].append({
                "name": "Phase 3 module importable",
                "status": "FAIL",
                "error": str(e),
            })
            report["is_valid"] = False

        return report["is_valid"], report


def run_validation_checks() -> int:
    """
    Run all Phase 4 input contract validation checks.
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("=" * 60)
    print("Phase 4 Input Contract Validation")
    print("=" * 60)

    # File-level checks
    is_valid, report = Phase4InputContract.validate_file_preconditions()
    print("\nFile Precondition Checks:")
    for check in report["checks"]:
        status_symbol = "✓" if check["status"] == "PASS" else "✗"
        print(f"  {status_symbol} {check['name']}")
        if "error" in check:
            print(f"    Error: {check['error']}")

    print("\n" + "=" * 60)
    if is_valid:
        print("INPUT CONTRACT: VALID")
        return 0
    else:
        print("INPUT CONTRACT: INVALID")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_validation_checks())
