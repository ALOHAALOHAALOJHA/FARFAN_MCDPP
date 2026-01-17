"""
Phase 5 Area Integration Module

This module provides integration functions for Phase 5 (Area Aggregation).
Bridges Phase 4 outputs to Phase 5 processing.

Module: src/farfan_pipeline/phases/Phase_05/phase5_30_00_area_integration.py
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.1.0"
__phase__ = 5
__stage__ = 30
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"
__modified__ = "2026-01-17"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import logging
from typing import Any

from farfan_pipeline.phases.Phase_04.phase4_30_00_aggregation import DimensionScore
from farfan_pipeline.phases.Phase_05.phase5_10_00_area_aggregation import (
    AreaScore,
    aggregate_policy_areas_async,
)
from farfan_pipeline.phases.Phase_05.phase5_20_00_area_validation import (
    validate_phase5_output,
)

logger = logging.getLogger(__name__)


# =============================================================================
# INTEGRATION FUNCTIONS
# =============================================================================


async def run_phase5_aggregation(
    dimension_scores: list[DimensionScore],
    questionnaire: dict[str, Any] | None = None,
    instrumentation: Any | None = None,
    signal_registry: Any | None = None,
    validate: bool = True,
) -> list[AreaScore]:
    """
    Run complete Phase 5 aggregation pipeline.
    
    Args:
        dimension_scores: List of 60 DimensionScore objects from Phase 4
        questionnaire: Questionnaire monolith (optional)
        instrumentation: Phase instrumentation for tracking
        signal_registry: Optional SISAS signal registry
        validate: Whether to validate output (default: True)
    
    Returns:
        List of 10 AreaScore objects
    
    Raises:
        ValueError: If validation fails
    """
    logger.info("Starting Phase 5 aggregation pipeline")
    
    # Run aggregation
    area_scores = await aggregate_policy_areas_async(
        dimension_scores=dimension_scores,
        questionnaire=questionnaire,
        instrumentation=instrumentation,
        signal_registry=signal_registry,
    )
    
    # Validate output
    if validate:
        is_valid, details = validate_phase5_output(area_scores, strict=True)
        if not is_valid:
            logger.error(f"Phase 5 validation failed: {details}")
            raise ValueError(f"Phase 5 validation failed: {details['violations']}")
    
    logger.info(f"Phase 5 aggregation complete: {len(area_scores)} area scores")
    return area_scores


def group_dimension_scores_by_area(
    dimension_scores: list[DimensionScore],
) -> dict[str, list[DimensionScore]]:
    """
    Group dimension scores by policy area.
    
    Utility function for external callers.
    
    Args:
        dimension_scores: List of DimensionScore objects
    
    Returns:
        Dict mapping area_id to list of DimensionScore
    """
    grouped: dict[str, list[DimensionScore]] = {}
    for ds in dimension_scores:
        if ds.area_id not in grouped:
            grouped[ds.area_id] = []
        grouped[ds.area_id].append(ds)
    return grouped
