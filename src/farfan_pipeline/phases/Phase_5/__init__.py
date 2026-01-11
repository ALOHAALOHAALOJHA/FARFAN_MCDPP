"""
Phase 5: Policy Area Aggregation

This module provides the Phase 5 aggregation components for the FARFAN pipeline.
Phase 5 aggregates 60 DimensionScore outputs into 10 AreaScore values.

Module: src/farfan_pipeline/phases/Phase_5/__init__.py
Purpose: Package façade for Phase 5
Owner: phase5_00
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-01-09
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 5
__stage__ = 0
__order__ = 0
__author__ = "GNEA-Enforcement"
__created__ = "2025-01-09T00:00:00Z"
__modified__ = "2025-01-09T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

from .phase5_10_00_phase_5_constants import (
    CLUSTER_ASSIGNMENTS,
    DIMENSION_IDS,
    DIMENSIONS_PER_AREA,
    EXPECTED_AREA_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    POLICY_AREAS,
    QUALITY_THRESHOLDS,
    Phase5Invariants,
    QualityLevel,
)

__all__ = [
    "CLUSTER_ASSIGNMENTS",
    "DIMENSIONS_PER_AREA",
    "DIMENSION_IDS",
    "EXPECTED_AREA_SCORE_COUNT",
    "MAX_SCORE",
    "MIN_SCORE",
    "POLICY_AREAS",
    "QUALITY_THRESHOLDS",
    "Phase5Invariants",
    "QualityLevel",
]
