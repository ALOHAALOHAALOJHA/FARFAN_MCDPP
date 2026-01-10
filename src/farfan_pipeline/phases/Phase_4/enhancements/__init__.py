"""Phase 4-7 Aggregation Pipeline Enhancements.

This package contains enhanced aggregators with additional features:
- Confidence interval tracking
- Dispersion analysis
- Hermeticity diagnosis
- Strategic alignment metrics
- Adaptive penalty computation
"""

from __future__ import annotations

from .adaptive_meso_scoring import (
    AdaptiveMesoScoring,
    AdaptiveScoringConfig,
    ScoringMetrics,
    create_adaptive_scorer,
)
from .enhanced_aggregators import (
    ConfidenceInterval,
    DispersionMetrics,
    EnhancedAreaAggregator,
    EnhancedClusterAggregator,
    EnhancedDimensionAggregator,
    EnhancedMacroAggregator,
    HermeticityDiagnosis,
    enhance_aggregator,
)
from .signal_enriched_aggregation import (
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
