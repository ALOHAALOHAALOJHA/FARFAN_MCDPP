"""
Phase 5 Input Contract

Defines and validates the input contract for Phase 5.

Input:
- 60 DimensionScore objects from Phase 4
- 6 dimensions × 10 policy areas
- Each dimension must be in [0.0, 3.0]

Module: src/farfan_pipeline/phases/Phase_5/contracts/phase5_input_contract.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"

import logging
from typing import Any

from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import DimensionScore
from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
    DIMENSIONS_PER_AREA,
    DIMENSION_IDS,
    EXPECTED_AREA_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    POLICY_AREAS,
)

logger = logging.getLogger(__name__)


class Phase5InputContract:
    """
    Input contract validator for Phase 5.
    
    Validates:
    - Total count: 60 DimensionScore objects
    - Hermeticity: Each policy area has exactly 6 dimensions
    - Bounds: All dimension scores in [0.0, 3.0]
    - Coverage: All 10 policy areas present
    """

    EXPECTED_INPUT_COUNT = DIMENSIONS_PER_AREA * EXPECTED_AREA_SCORE_COUNT  # 60

    @staticmethod
    def validate(dimension_scores: list[DimensionScore]) -> tuple[bool, dict[str, Any]]:
        """
        Validate Phase 5 input contract.
        
        Args:
            dimension_scores: List of DimensionScore objects from Phase 4
        
        Returns:
            Tuple of (is_valid, details_dict)
        """
        logger.info(f"Validating Phase 5 input: {len(dimension_scores)} dimension scores")
        
        details = {
            "count_valid": False,
            "hermeticity_valid": False,
            "bounds_valid": False,
            "coverage_valid": False,
            "violations": [],
        }
        
        # 1. Validate count
        if len(dimension_scores) != Phase5InputContract.EXPECTED_INPUT_COUNT:
            msg = (
                f"Expected {Phase5InputContract.EXPECTED_INPUT_COUNT} dimension scores, "
                f"got {len(dimension_scores)}"
            )
            logger.error(msg)
            details["violations"].append(msg)
        else:
            details["count_valid"] = True
        
        # 2. Group by area and validate hermeticity
        grouped = Phase5InputContract._group_by_area(dimension_scores)
        
        hermeticity_violations = []
        for area_id in POLICY_AREAS:
            if area_id not in grouped:
                hermeticity_violations.append(f"Missing policy area: {area_id}")
                continue
            
            area_dims = grouped[area_id]
            if len(area_dims) != DIMENSIONS_PER_AREA:
                msg = (
                    f"Area {area_id}: expected {DIMENSIONS_PER_AREA} dimensions, "
                    f"got {len(area_dims)}"
                )
                hermeticity_violations.append(msg)
            
            # Check dimension IDs
            dim_ids = {ds.dimension_id for ds in area_dims}
            if dim_ids != set(DIMENSION_IDS):
                missing = set(DIMENSION_IDS) - dim_ids
                extra = dim_ids - set(DIMENSION_IDS)
                hermeticity_violations.append(
                    f"Area {area_id}: missing {missing}, extra {extra}"
                )
        
        if hermeticity_violations:
            logger.error(f"Hermeticity violations: {len(hermeticity_violations)}")
            details["violations"].extend(hermeticity_violations)
        else:
            details["hermeticity_valid"] = True
        
        # 3. Validate bounds
        bounds_violations = []
        for ds in dimension_scores:
            if ds.score < MIN_SCORE or ds.score > MAX_SCORE:
                msg = (
                    f"DimensionScore {ds.dimension_id} in {ds.area_id}: "
                    f"score {ds.score} out of bounds [{MIN_SCORE}, {MAX_SCORE}]"
                )
                bounds_violations.append(msg)
        
        if bounds_violations:
            logger.error(f"Bounds violations: {len(bounds_violations)}")
            details["violations"].extend(bounds_violations)
        else:
            details["bounds_valid"] = True
        
        # 4. Validate coverage
        present_areas = set(grouped.keys())
        expected_areas = set(POLICY_AREAS)
        if present_areas != expected_areas:
            missing = expected_areas - present_areas
            extra = present_areas - expected_areas
            msg = f"Coverage violation: missing {missing}, extra {extra}"
            logger.error(msg)
            details["violations"].append(msg)
        else:
            details["coverage_valid"] = True
        
        # Overall validity
        is_valid = (
            details["count_valid"]
            and details["hermeticity_valid"]
            and details["bounds_valid"]
            and details["coverage_valid"]
        )
        
        if is_valid:
            logger.info("Phase 5 input contract: VALID")
        else:
            logger.error(f"Phase 5 input contract: INVALID ({len(details['violations'])} violations)")
        
        return is_valid, details

    @staticmethod
    def _group_by_area(
        dimension_scores: list[DimensionScore],
    ) -> dict[str, list[DimensionScore]]:
        """Group dimension scores by area."""
        grouped: dict[str, list[DimensionScore]] = {}
        for ds in dimension_scores:
            if ds.area_id not in grouped:
                grouped[ds.area_id] = []
            grouped[ds.area_id].append(ds)
        return grouped
