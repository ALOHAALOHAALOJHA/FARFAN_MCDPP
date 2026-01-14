"""
Phase 4 Output Contract

Defines and validates the output contract for Phase 4.

Output:
- 60 DimensionScore objects for Phase 5
- 6 dimensions × 10 policy areas
- Each dimension score in [0.0, 3.0]
- Complete provenance and uncertainty metrics

Module: src/farfan_pipeline/phases/Phase_4/contracts/phase4_output_contract.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Phase4OutputContract:
    """
    Output contract validator for Phase 4.
    
    Validates:
    - Total count: 60 DimensionScore objects
    - Coverage: All 6 dimensions × 10 policy areas represented
    - Bounds: All dimension scores in [0.0, 3.0]
    - Downstream compatibility: Format matches Phase 5 input contract
    """

    EXPECTED_OUTPUT_COUNT = 60  # 6 dimensions × 10 policy areas
    EXPECTED_DIMENSIONS = 6
    EXPECTED_POLICY_AREAS = 10
    MIN_SCORE = 0.0
    MAX_SCORE = 3.0

    @staticmethod
    def validate(dimension_scores: list[Any]) -> tuple[bool, dict[str, Any]]:
        """
        Validate Phase 4 output contract.
        
        Args:
            dimension_scores: List of DimensionScore objects
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            "contract": "Phase4OutputContract",
            "version": __version__,
            "total_count": len(dimension_scores),
            "expected_count": Phase4OutputContract.EXPECTED_OUTPUT_COUNT,
            "errors": [],
            "warnings": [],
            "is_valid": True,
        }

        # Postcondition 1: Count validation
        if len(dimension_scores) != Phase4OutputContract.EXPECTED_OUTPUT_COUNT:
            report["errors"].append(
                f"Expected {Phase4OutputContract.EXPECTED_OUTPUT_COUNT} "
                f"DimensionScore objects, got {len(dimension_scores)}"
            )
            report["is_valid"] = False

        # Postcondition 2: Structure validation
        if not dimension_scores:
            report["errors"].append("Empty output: no dimension scores produced")
            report["is_valid"] = False
            return report["is_valid"], report

        # Check for required attributes
        required_attrs = ["dimension", "policy_area", "score"]
        sample = dimension_scores[0]
        for attr in required_attrs:
            if not hasattr(sample, attr):
                report["errors"].append(f"Missing required attribute: {attr}")
                report["is_valid"] = False

        # Postcondition 3: Coverage validation
        # Each (dimension, policy_area) pair should appear exactly once
        coverage = set()
        duplicates = []
        
        for ds in dimension_scores:
            try:
                key = (ds.dimension, ds.policy_area)
                if key in coverage:
                    duplicates.append(key)
                coverage.add(key)
            except AttributeError as e:
                report["errors"].append(f"Missing attribute in dimension score: {e}")
                report["is_valid"] = False
                break

        if duplicates:
            report["errors"].append(
                f"Found {len(duplicates)} duplicate (dimension, policy_area) pairs: {duplicates[:5]}"
            )
            report["is_valid"] = False

        expected_cells = Phase4OutputContract.EXPECTED_DIMENSIONS * Phase4OutputContract.EXPECTED_POLICY_AREAS
        if len(coverage) != expected_cells:
            report["errors"].append(
                f"Expected {expected_cells} unique (dimension, policy_area) pairs, got {len(coverage)}"
            )
            report["is_valid"] = False

        # Postcondition 4: Bounds validation
        out_of_bounds = []
        for ds in dimension_scores:
            try:
                score = ds.score
                if score < Phase4OutputContract.MIN_SCORE or score > Phase4OutputContract.MAX_SCORE:
                    out_of_bounds.append((ds.dimension, ds.policy_area, score))
            except AttributeError:
                pass  # Already reported above

        if out_of_bounds:
            report["errors"].append(
                f"Found {len(out_of_bounds)} scores outside [{Phase4OutputContract.MIN_SCORE}, "
                f"{Phase4OutputContract.MAX_SCORE}] range: {out_of_bounds[:5]}"
            )
            report["is_valid"] = False

        # Postcondition 5: Provenance validation (optional but recommended)
        has_provenance = hasattr(sample, "provenance") or hasattr(sample, "source_questions")
        if not has_provenance:
            report["warnings"].append(
                "No provenance information found. Consider adding provenance tracking."
            )

        # Postcondition 6: Uncertainty quantification (optional but recommended)
        has_uncertainty = any(
            hasattr(sample, attr) 
            for attr in ["uncertainty", "confidence_interval", "std_dev"]
        )
        if not has_uncertainty:
            report["warnings"].append(
                "No uncertainty metrics found. Consider adding uncertainty quantification."
            )

        report["coverage_stats"] = {
            "total_cells": len(coverage),
            "expected_cells": expected_cells,
            "duplicate_cells": len(duplicates),
        }

        report["score_stats"] = {
            "total_scores": len(dimension_scores),
            "out_of_bounds": len(out_of_bounds),
            "in_bounds": len(dimension_scores) - len(out_of_bounds),
        }

        return report["is_valid"], report

    @staticmethod
    def validate_downstream_compatibility() -> tuple[bool, dict[str, Any]]:
        """
        Validate compatibility with Phase 5 input contract.
        
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            "contract": "Phase4OutputContract.downstream_compatibility",
            "version": __version__,
            "downstream_phase": "Phase 5 (Area Aggregation)",
            "checks": [],
            "is_valid": True,
        }

        # Check 1: Phase 5 module is importable
        try:
            import farfan_pipeline.phases.Phase_5
            report["checks"].append({
                "name": "Phase 5 module importable",
                "status": "PASS",
            })
        except ImportError as e:
            report["checks"].append({
                "name": "Phase 5 module importable",
                "status": "FAIL",
                "error": str(e),
            })
            report["is_valid"] = False
            return report["is_valid"], report

        # Check 2: Phase 5 input contract is compatible
        try:
            from farfan_pipeline.phases.Phase_5.contracts.phase5_input_contract import (
                Phase5InputContract,
            )
            
            # Verify expected counts match
            phase5_expected = Phase5InputContract.EXPECTED_INPUT_COUNT
            if phase5_expected != Phase4OutputContract.EXPECTED_OUTPUT_COUNT:
                report["checks"].append({
                    "name": "Count compatibility",
                    "status": "FAIL",
                    "error": f"Phase 5 expects {phase5_expected}, Phase 4 outputs {Phase4OutputContract.EXPECTED_OUTPUT_COUNT}",
                })
                report["is_valid"] = False
            else:
                report["checks"].append({
                    "name": "Count compatibility",
                    "status": "PASS",
                    "detail": f"Both expect {phase5_expected} objects",
                })

            # Verify bounds match
            phase5_min = Phase5InputContract.MIN_SCORE if hasattr(Phase5InputContract, "MIN_SCORE") else 0.0
            phase5_max = Phase5InputContract.MAX_SCORE if hasattr(Phase5InputContract, "MAX_SCORE") else 3.0
            
            if phase5_min != Phase4OutputContract.MIN_SCORE or phase5_max != Phase4OutputContract.MAX_SCORE:
                report["checks"].append({
                    "name": "Bounds compatibility",
                    "status": "FAIL",
                    "error": f"Phase 5 expects [{phase5_min}, {phase5_max}], Phase 4 outputs [{Phase4OutputContract.MIN_SCORE}, {Phase4OutputContract.MAX_SCORE}]",
                })
                report["is_valid"] = False
            else:
                report["checks"].append({
                    "name": "Bounds compatibility",
                    "status": "PASS",
                    "detail": f"Both use [{phase5_min}, {phase5_max}] range",
                })

        except Exception as e:
            report["checks"].append({
                "name": "Phase 5 contract compatibility",
                "status": "ERROR",
                "error": str(e),
            })
            report["is_valid"] = False

        return report["is_valid"], report


def run_validation_checks() -> int:
    """
    Run all Phase 4 output contract validation checks.
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("=" * 60)
    print("Phase 4 Output Contract Validation")
    print("=" * 60)

    # Downstream compatibility checks
    is_valid, report = Phase4OutputContract.validate_downstream_compatibility()
    print("\nDownstream Compatibility (Phase 5):")
    for check in report["checks"]:
        status_symbol = "✓" if check["status"] == "PASS" else "✗"
        print(f"  {status_symbol} {check['name']}")
        if "error" in check:
            print(f"    Error: {check['error']}")
        elif "detail" in check:
            print(f"    {check['detail']}")

    print("\n" + "=" * 60)
    if is_valid:
        print("OUTPUT CONTRACT: VALID")
        print("✓ Phase 4 output is compatible with Phase 5 input")
        return 0
    else:
        print("OUTPUT CONTRACT: INVALID")
        print("✗ Phase 4 output is NOT compatible with Phase 5 input")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_validation_checks())
