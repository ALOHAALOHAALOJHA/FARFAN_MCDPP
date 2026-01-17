"""Phase 4 Aggregation Pipeline Enhancements.

This package contains enhanced aggregators with additional features:
- Confidence interval tracking
- Dispersion analysis
- Hermeticity diagnosis
- Adaptive penalty computation

NOTE: Only Phase 4 (Dimension) aggregation enhancements are included here.
Area, Cluster, and Macro aggregation enhancements belong to Phases 5, 6, and 7.
"""

from __future__ import annotations

from .phase4_40_00_adaptive_meso_scoring import (
    AdaptiveMesoScoring,
    AdaptiveScoringConfig,
    ScoringMetrics,
    create_adaptive_scorer,
)
from .phase4_40_00_enhanced_aggregators import (
    ConfidenceInterval,
    DispersionMetrics,
    EnhancedAreaAggregator,
    EnhancedClusterAggregator,
    EnhancedDimensionAggregator,
    EnhancedMacroAggregator,
    HermeticityDiagnosis,
    enhance_aggregator,
)
from .phase4_40_00_signal_enriched_aggregation import (
    SignalEnrichedAggregator,
    adjust_weights,
    interpret_dispersion,
)

__all__ = [
    "AdaptiveMesoScoring",
    "AdaptiveScoringConfig",
    "ConfidenceInterval",
    "DispersionMetrics",
    "EnhancedAreaAggregator",
    "EnhancedClusterAggregator",
    "EnhancedDimensionAggregator",
    "EnhancedMacroAggregator",
    "HermeticityDiagnosis",
    "ScoringMetrics",
    "SignalEnrichedAggregator",
    "adjust_weights",
    "create_adaptive_scorer",
    "enhance_aggregator",
    "interpret_dispersion",
]
