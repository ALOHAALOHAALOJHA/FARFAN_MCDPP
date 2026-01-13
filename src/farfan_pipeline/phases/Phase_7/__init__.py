"""
Phase 7: Macro Evaluation

This module provides the Phase 7 macro evaluation components for the FARFAN pipeline.
Phase 7 evaluates 4 ClusterScore inputs and produces a holistic MacroScore.

Module: src/farfan_pipeline/phases/Phase_7/__init__.py
Purpose: Package façade for Phase 7
Owner: phase7_00
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-01-09
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 7
__stage__ = 0
__order__ = 0
__author__ = "GNEA-Enforcement"
__created__ = "2025-01-09T00:00:00Z"
__modified__ = "2026-01-13T00:00:00Z"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Per-Task"

from .phase7_10_00_phase_7_constants import (
    ALIGNMENT_THRESHOLD_HIGH,
    ALIGNMENT_THRESHOLD_LOW,
    ALIGNMENT_THRESHOLD_MEDIUM,
    CLUSTER_WEIGHTS,
    COHERENCE_THRESHOLD_ACCEPTABLE,
    COHERENCE_THRESHOLD_EXCELLENT,
    COHERENCE_THRESHOLD_GOOD,
    COHERENCE_WEIGHT_INSTITUTIONAL,
    COHERENCE_WEIGHT_OPERATIONAL,
    COHERENCE_WEIGHT_STRATEGIC,
    EXPECTED_MACRO_SCORE_COUNT,
    INPUT_CLUSTERS,
    MAX_SCORE,
    MIN_SCORE,
    QUALITY_THRESHOLDS,
    SYSTEMIC_GAP_THRESHOLD,
    MacroInvariants,
    QualityLevel,
)

from .phase7_10_00_macro_score import MacroScore
from .phase7_20_00_macro_aggregator import MacroAggregator
from .phase7_10_00_systemic_gap_detector import SystemicGapDetector, SystemicGap

__all__ = [
    # Constants
    "ALIGNMENT_THRESHOLD_HIGH",
    "ALIGNMENT_THRESHOLD_LOW",
    "ALIGNMENT_THRESHOLD_MEDIUM",
    "CLUSTER_WEIGHTS",
    "COHERENCE_THRESHOLD_ACCEPTABLE",
    "COHERENCE_THRESHOLD_EXCELLENT",
    "COHERENCE_THRESHOLD_GOOD",
    "COHERENCE_WEIGHT_INSTITUTIONAL",
    "COHERENCE_WEIGHT_OPERATIONAL",
    "COHERENCE_WEIGHT_STRATEGIC",
    "EXPECTED_MACRO_SCORE_COUNT",
    "INPUT_CLUSTERS",
    "MAX_SCORE",
    "MIN_SCORE",
    "QUALITY_THRESHOLDS",
    "SYSTEMIC_GAP_THRESHOLD",
    "MacroInvariants",
    "QualityLevel",
    # Classes
    "MacroScore",
    "MacroAggregator",
    "SystemicGapDetector",
    "SystemicGap",
]
