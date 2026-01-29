"""
Phase 5 Output Contract

Defines and validates the output contract for Phase 5.

Output:
- 10 AreaScore objects (one per policy area)
- Each AreaScore contains 6 DimensionScores
- All scores in [0.0, 3.0]

Module: src/farfan_pipeline/phases/Phase_05/contracts/phase5_output_contract.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"

import logging
from typing import Any

from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore
from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
    DIMENSIONS_PER_AREA,
    EXPECTED_AREA_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    POLICY_AREAS,
)

logger = logging.getLogger(__name__)


class Phase5OutputContract:
    """
    Output contract validator for Phase 5.
    
    Validates:
    - Total count: 10 AreaScore objects
    - Hermeticity: Each area has exactly 6 dimensions
    - Bounds: All area scores in [0.0, 3.0]
    - Coverage: All 10 policy areas present
    """

    EXPECTED_OUTPUT_COUNT = EXPECTED_AREA_SCORE_COUNT  # 10

    @staticmethod
    def validate(area_scores: list[AreaScore]) -> tuple[bool, dict[str, Any]]:
        """
        Validate Phase 5 output contract.
        
        Args:
            area_scores: List of AreaScore objects
        
        Returns:
            Tuple of (is_valid, details_dict)
        """
        logger.info(f"Validating Phase 5 output: {len(area_scores)} area scores")
        
        details = {
            "count_valid": False,
            "hermeticity_valid": False,
            "bounds_valid": False,
            "coverage_valid": False,
            "violations": [],
        }
        
        # 1. Validate count
        if len(area_scores) != Phase5OutputContract.EXPECTED_OUTPUT_COUNT:
            msg = (
                f"Expected {Phase5OutputContract.EXPECTED_OUTPUT_COUNT} area scores, "
                f"got {len(area_scores)}"
            )
            logger.error(msg)
            details["violations"].append(msg)
        else:
            details["count_valid"] = True
        
        # 2. Validate hermeticity
        hermeticity_violations = []
        for area in area_scores:
            if len(area.dimension_scores) != DIMENSIONS_PER_AREA:
                msg = (
                    f"Area {area.area_id}: expected {DIMENSIONS_PER_AREA} dimensions, "
                    f"got {len(area.dimension_scores)}"
                )
                hermeticity_violations.append(msg)
        
        if hermeticity_violations:
            logger.error(f"Hermeticity violations: {len(hermeticity_violations)}")
            details["violations"].extend(hermeticity_violations)
        else:
            details["hermeticity_valid"] = True
        
        # 3. Validate bounds
        bounds_violations = []
        for area in area_scores:
            if area.score < MIN_SCORE or area.score > MAX_SCORE:
                msg = (
                    f"Area {area.area_id}: score {area.score} "
                    f"out of bounds [{MIN_SCORE}, {MAX_SCORE}]"
                )
                bounds_violations.append(msg)
        
        if bounds_violations:
            logger.error(f"Bounds violations: {len(bounds_violations)}")
            details["violations"].extend(bounds_violations)
        else:
            details["bounds_valid"] = True
        
        # 4. Validate coverage
        present_areas = {area.area_id for area in area_scores}
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
            logger.info("Phase 5 output contract: VALID")
        else:
            logger.error(f"Phase 5 output contract: INVALID ({len(details['violations'])} violations)")
        
        return is_valid, details
