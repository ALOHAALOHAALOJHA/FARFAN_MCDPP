"""
Phase 5: Policy Area Aggregation

This module provides the Phase 5 aggregation components for the FARFAN pipeline.
Phase 5 aggregates 60 DimensionScore outputs into 10 AreaScore values.

Phase 5 Contract:
- Input: 60 DimensionScore (6 dimensions × 10 policy areas) from Phase 4
- Output: 10 AreaScore (one per policy area)
- Process: Weighted average of 6 dimensions per policy area

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
__modified__ = "2026-01-13T21:40:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

# Constants
from .PHASE_5_CONSTANTS import (
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

# Data Model (stage 0 - MODEL)
from .phase5_00_00_area_score import AreaScore

# Core classes (stage 10 - CORE)
from .phase5_10_00_area_aggregation import (
    AreaPolicyAggregator,
    aggregate_policy_areas_async,
)

# Performance Boost (stage 15 - PERFORMANCE)
from .phase5_15_00_performance_boost import (
    HighPerformanceAreaAggregator,
    PerformanceMetrics,
    aggregate_with_performance_boost,
    AdaptiveCache,
)

# Validation
from .phase5_20_00_area_validation import (
    validate_phase5_output,
    validate_area_score_hermeticity,
    validate_area_score_bounds,
)

# Integration
from .phase5_30_00_area_integration import (
    run_phase5_aggregation,
    group_dimension_scores_by_area,
)

# Contracts
from .contracts.phase5_input_contract import Phase5InputContract
from .contracts.phase5_output_contract import Phase5OutputContract
from .contracts.phase5_mission_contract import Phase5MissionContract

__all__ = [
    # Constants
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
    # Core
    "AreaScore",
    "AreaPolicyAggregator",
    "aggregate_policy_areas_async",
    # Performance Boost
    "HighPerformanceAreaAggregator",
    "PerformanceMetrics",
    "aggregate_with_performance_boost",
    "AdaptiveCache",
    # Validation
    "validate_phase5_output",
    "validate_area_score_hermeticity",
    "validate_area_score_bounds",
    # Integration
    "run_phase5_aggregation",
    "group_dimension_scores_by_area",
    # Contracts
    "Phase5InputContract",
    "Phase5OutputContract",
    "Phase5MissionContract",
]
