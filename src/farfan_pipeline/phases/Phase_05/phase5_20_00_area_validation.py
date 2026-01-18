"""
Phase 5 Area Validation Module

This module provides validation functions for Phase 5 (Area Aggregation).

Validates:
- Output count (exactly 10 AreaScore objects)
- Hermeticity (exactly 6 dimensions per area)
- Score bounds ([0.0, 3.0])
- Quality level consistency
- Cluster assignments (for Phase 6 transition)

Module: src/farfan_pipeline/phases/Phase_05/phase5_20_00_area_validation.py
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.1.0"
__phase__ = 5
__stage__ = 20
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"
__modified__ = "2026-01-17"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import logging
from typing import Any

from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore
from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
    DIMENSIONS_PER_AREA,
    DIMENSION_IDS,
    EXPECTED_AREA_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    POLICY_AREAS,
    QUALITY_THRESHOLDS,
)

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_phase5_output(
    area_scores: list[AreaScore],
    strict: bool = True,
) -> tuple[bool, dict[str, Any]]:
    """
    Validate Phase 5 output (10 AreaScore objects).
    
    Checks:
    1. Count: Exactly 10 area scores
    2. Hermeticity: Each area has exactly 6 dimensions
    3. Bounds: All scores in [0.0, 3.0]
    4. Coverage: All policy areas present (PA01-PA10)
    5. Quality levels: Consistent with score thresholds
    
    Args:
        area_scores: List of AreaScore objects to validate
        strict: Whether to fail on any violation (default: True)
    
    Returns:
        Tuple of (is_valid, details_dict)
        - is_valid: True if all checks pass
        - details_dict: Dict with validation results
    """
    logger.info(f"Validating Phase 5 output: {len(area_scores)} area scores")
    
    details = {
        "count_valid": False,
        "hermeticity_valid": False,
        "bounds_valid": False,
        "coverage_valid": False,
        "quality_valid": False,
        "violations": [],
    }
    
    # 1. Validate count
    if len(area_scores) != EXPECTED_AREA_SCORE_COUNT:
        msg = f"Expected {EXPECTED_AREA_SCORE_COUNT} area scores, got {len(area_scores)}"
        logger.error(msg)
        details["violations"].append(msg)
    else:
        details["count_valid"] = True
    
    # 2. Validate hermeticity
    hermeticity_violations = []
    for area_score in area_scores:
        if len(area_score.dimension_scores) != DIMENSIONS_PER_AREA:
            msg = (
                f"Area {area_score.area_id}: expected {DIMENSIONS_PER_AREA} dimensions, "
                f"got {len(area_score.dimension_scores)}"
            )
            hermeticity_violations.append(msg)
        else:
            # Check exact dimension set
            dim_ids = {ds.dimension_id for ds in area_score.dimension_scores}
            if dim_ids != set(DIMENSION_IDS):
                missing = set(DIMENSION_IDS) - dim_ids
                extra = dim_ids - set(DIMENSION_IDS)
                msg = f"Area {area_score.area_id}: missing {missing}, extra {extra}"
                hermeticity_violations.append(msg)
    
    if hermeticity_violations:
        logger.error(f"Hermeticity violations: {len(hermeticity_violations)}")
        details["violations"].extend(hermeticity_violations)
    else:
        details["hermeticity_valid"] = True
    
    # 3. Validate bounds
    bounds_violations = []
    for area_score in area_scores:
        if area_score.score < MIN_SCORE or area_score.score > MAX_SCORE:
            msg = (
                f"Area {area_score.area_id}: score {area_score.score} "
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
    
    # 5. Validate quality levels
    quality_violations = []
    for area_score in area_scores:
        expected_quality = _get_expected_quality(area_score.score)
        if area_score.quality_level != expected_quality:
            msg = (
                f"Area {area_score.area_id}: quality level '{area_score.quality_level}' "
                f"inconsistent with score {area_score.score} (expected '{expected_quality}')"
            )
            quality_violations.append(msg)
    
    if quality_violations:
        logger.warning(f"Quality level inconsistencies: {len(quality_violations)}")
        details["violations"].extend(quality_violations)
    else:
        details["quality_valid"] = True
    
    # Overall validity
    is_valid = (
        details["count_valid"]
        and details["hermeticity_valid"]
        and details["bounds_valid"]
        and details["coverage_valid"]
        and details["quality_valid"]
    )
    
    if is_valid:
        logger.info("Phase 5 output validation: PASSED")
    else:
        logger.error(f"Phase 5 output validation: FAILED ({len(details['violations'])} violations)")
    
    return is_valid, details


def _get_expected_quality(score: float) -> str:
    """
    Get expected quality level for a score.
    
    Args:
        score: Score in [0.0, 3.0]
    
    Returns:
        Expected quality level string
    """
    normalized = score / MAX_SCORE
    if normalized >= QUALITY_THRESHOLDS["EXCELENTE"]:
        return "EXCELENTE"
    elif normalized >= QUALITY_THRESHOLDS["BUENO"]:
        return "BUENO"
    elif normalized >= QUALITY_THRESHOLDS["ACEPTABLE"]:
        return "ACEPTABLE"
    else:
        return "INSUFICIENTE"


def validate_area_score_hermeticity(area_score: AreaScore) -> tuple[bool, str]:
    """
    Validate hermeticity for a single AreaScore.
    
    Args:
        area_score: AreaScore to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    dim_count = len(area_score.dimension_scores)
    if dim_count != DIMENSIONS_PER_AREA:
        return False, f"Expected {DIMENSIONS_PER_AREA} dimensions, got {dim_count}"
    
    dim_ids = {ds.dimension_id for ds in area_score.dimension_scores}
    expected_dims = set(DIMENSION_IDS)
    if dim_ids != expected_dims:
        missing = expected_dims - dim_ids
        extra = dim_ids - expected_dims
        return False, f"Missing: {missing}, Extra: {extra}"
    
    return True, "Hermeticity OK"


def validate_area_score_bounds(area_score: AreaScore) -> tuple[bool, str]:
    """
    Validate score bounds for a single AreaScore.
    
    Args:
        area_score: AreaScore to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if area_score.score < MIN_SCORE:
        return False, f"Score {area_score.score} below minimum {MIN_SCORE}"
    if area_score.score > MAX_SCORE:
        return False, f"Score {area_score.score} above maximum {MAX_SCORE}"
    return True, "Bounds OK"
