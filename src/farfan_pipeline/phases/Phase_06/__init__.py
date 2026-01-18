"""
Phase 6: Cluster Aggregation (MESO)

This module provides the Phase 6 aggregation components for the FARFAN pipeline.
Phase 6 aggregates 10 AreaScore outputs into 4 ClusterScore values.

All files participate in the default flow by canonical imports in deterministic order.

Module: src/farfan_pipeline/phases/Phase_6/__init__.py
Purpose: Package façade for Phase 6
Owner: phase6_00
Lifecycle: ACTIVE
Version: 2.0.0
Effective-Date: 2026-01-18
"""

# METADATA
__version__ = "2.0.0"
__phase__ = 6
__stage__ = 0
__order__ = 0
__author__ = "GNEA-Enforcement"
__created__ = "2025-01-09T00:00:00Z"
__modified__ = "2026-01-18T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

# ============================================================================
# STAGE 10: Configuration and Data Models (Deterministic Import Order)
# ============================================================================
# Import configuration first (no internal dependencies)
from .phase6_10_01_scoring_config import (
    PHASE6_CONFIG,
    CoherenceQuality,
    DispersionScenario,
    Phase6ScoringConfig,
)

# Import constants (depends on scoring_config)
from .phase6_10_00_phase_6_constants import (
    CLUSTER_COMPOSITION,
    CLUSTERS,
    COHERENCE_THRESHOLD_HIGH,
    COHERENCE_THRESHOLD_LOW,
    DISPERSION_THRESHOLDS,
    EXPECTED_CLUSTER_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    PENALTY_WEIGHT,
    Phase6Invariants,
)

# Import data model (no internal dependencies)
from .phase6_10_00_cluster_score import ClusterScore

# ============================================================================
# STAGE 20: Enforcement and Adaptive Logic
# ============================================================================
# Import adaptive scoring (depends on scoring_config)
from .phase6_20_00_adaptive_meso_scoring import (
    AdaptiveMesoScoring,
    AdaptiveScoringConfig,
    ScoringMetrics,
)

# ============================================================================
# STAGE 30: Aggregation Orchestration
# ============================================================================
# Import aggregator (depends on constants, cluster_score, adaptive_meso_scoring, contracts)
from .phase6_30_00_cluster_aggregator import ClusterAggregator

# ============================================================================
# STAGE 40: Contracts (Design by Contract)
# ============================================================================
# Import contracts (depends on scoring_config)
from .contracts.phase6_input_contract import Phase6InputContract
from .contracts.phase6_mission_contract import (
    MISSION_STATEMENT,
    Phase6Stage,
)
from .contracts.phase6_output_contract import (
    Phase6OutputContract,
    validate_phase6_output,
)

# ============================================================================
# PUBLIC API
# ============================================================================
__all__ = [
    # Constants
    "CLUSTERS",
    "CLUSTER_COMPOSITION",
    "COHERENCE_THRESHOLD_HIGH",
    "COHERENCE_THRESHOLD_LOW",
    "DISPERSION_THRESHOLDS",
    "EXPECTED_CLUSTER_SCORE_COUNT",
    "MAX_SCORE",
    "MIN_SCORE",
    "PENALTY_WEIGHT",
    # Enums and Types
    "DispersionScenario",
    "CoherenceQuality",
    "Phase6Invariants",
    "Phase6Stage",
    # Configuration
    "PHASE6_CONFIG",
    "Phase6ScoringConfig",
    "AdaptiveScoringConfig",
    # Data Models
    "ClusterScore",
    "ScoringMetrics",
    # Core Components
    "AdaptiveMesoScoring",
    "ClusterAggregator",
    # Contracts
    "Phase6InputContract",
    "Phase6OutputContract",
    "MISSION_STATEMENT",
    "validate_phase6_output",
]
