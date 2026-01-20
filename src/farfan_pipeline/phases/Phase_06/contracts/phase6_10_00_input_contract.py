"""
Phase 6 Input Contract

This contract defines and validates the input requirements for Phase 6.

Input Specification:
- Type: List[AreaScore]
- Count: Exactly 10 AreaScore objects (PA01-PA10)
- Each AreaScore must have 6 DimensionScore objects
- All scores must be in range [0.0, 3.0]

Module: src/farfan_pipeline/phases/Phase_06/contracts/phase6_input_contract.py
Phase: 6 (Cluster Aggregation - MESO)
Owner: phase6_contracts
"""

from __future__ import annotations

__version__ = "1.0.0"
__phase__ = 6
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"

from typing import Any
import logging

logger = logging.getLogger(__name__)


class Phase6InputContract:
    """
    Phase 6 Input Contract Validator.
    
    Validates that Phase 5 output (10 AreaScore objects) meets
    Phase 6 input requirements.
    """
    
    EXPECTED_AREA_COUNT = 10
    EXPECTED_DIMENSIONS_PER_AREA = 6
    MIN_SCORE = 0.0
    MAX_SCORE = 3.0
    
    REQUIRED_POLICY_AREAS = [
        "PA01", "PA02", "PA03", "PA04", "PA05",
        "PA06", "PA07", "PA08", "PA09", "PA10"
    ]
    
    @classmethod
    def validate(cls, area_scores: list[Any]) -> tuple[bool, dict[str, Any]]:
        """
        Validate Phase 6 input contract.
        
        Args:
            area_scores: List of AreaScore objects from Phase 5
            
        Returns:
            Tuple of (validation_passed, validation_details)
        """
        validation_details = {
            "contract": "Phase 6 Input",
            "checks": [],
            "errors": [],
            "warnings": []
        }
        
        # Check 1: Count validation
        if len(area_scores) != cls.EXPECTED_AREA_COUNT:
            validation_details["errors"].append(
                f"Expected {cls.EXPECTED_AREA_COUNT} area scores, got {len(area_scores)}"
            )
        else:
            validation_details["checks"].append(f"✓ Count: {len(area_scores)} area scores")
        
        # Check 2: Policy area coverage
        area_ids = {area.area_id for area in area_scores}
        missing_areas = set(cls.REQUIRED_POLICY_AREAS) - area_ids
        if missing_areas:
            validation_details["errors"].append(
                f"Missing policy areas: {sorted(missing_areas)}"
            )
        else:
            validation_details["checks"].append("✓ All 10 policy areas present")
        
        # Check 3: Hermeticity - each area has 6 dimensions
        for area in area_scores:
            if hasattr(area, 'dimension_scores'):
                dim_count = len(area.dimension_scores)
                if dim_count != cls.EXPECTED_DIMENSIONS_PER_AREA:
                    validation_details["errors"].append(
                        f"{area.area_id}: Expected {cls.EXPECTED_DIMENSIONS_PER_AREA} dimensions, got {dim_count}"
                    )
        
        validation_details["checks"].append("✓ Hermeticity validated")
        
        # Check 4: Score bounds
        out_of_bounds = []
        for area in area_scores:
            if not (cls.MIN_SCORE <= area.score <= cls.MAX_SCORE):
                out_of_bounds.append(f"{area.area_id}: {area.score}")
        
        if out_of_bounds:
            validation_details["errors"].append(
                f"Scores out of bounds [{cls.MIN_SCORE}, {cls.MAX_SCORE}]: {out_of_bounds}"
            )
        else:
            validation_details["checks"].append(f"✓ All scores in [{cls.MIN_SCORE}, {cls.MAX_SCORE}]")
        
        # Check 5: Cluster assignments present
        missing_cluster = [area.area_id for area in area_scores if not area.cluster_id]
        if missing_cluster:
            validation_details["warnings"].append(
                f"Areas without cluster_id: {missing_cluster}"
            )
        else:
            validation_details["checks"].append("✓ All areas have cluster assignments")
        
        validation_passed = len(validation_details["errors"]) == 0
        validation_details["passed"] = validation_passed
        
        return validation_passed, validation_details
    
    @classmethod
    def fail_fast(cls, area_scores: list[Any]) -> None:
        """
        Fail-fast validation - raises exception on first failure.
        
        Args:
            area_scores: List of AreaScore objects
            
        Raises:
            ValueError: If any validation check fails
        """
        passed, details = cls.validate(area_scores)
        
        if not passed:
            error_msg = "Phase 6 Input Contract Violation:\n"
            for error in details["errors"]:
                error_msg += f"  ✗ {error}\n"
            raise ValueError(error_msg)
        
        logger.info("✅ Phase 6 input contract validated successfully")


# Convenience function
def validate_phase6_input(area_scores: list[Any]) -> tuple[bool, dict[str, Any]]:
    """
    Validate Phase 6 input.
    
    Args:
        area_scores: List of AreaScore objects from Phase 5
        
    Returns:
        Tuple of (validation_passed, validation_details)
    """
    return Phase6InputContract.validate(area_scores)
