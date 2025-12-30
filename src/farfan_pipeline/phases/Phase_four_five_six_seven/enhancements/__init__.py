"""Phase 4-7 Aggregation Pipeline Enhancements.

This package contains enhanced aggregators with additional features:
- Confidence interval tracking
- Dispersion analysis
- Hermeticity diagnosis
- Strategic alignment metrics
- Adaptive penalty computation
"""

from __future__ import annotations

from .enhanced_aggregators import (
    ConfidenceInterval,
    DispersionMetrics,
    HermeticityDiagnosis,
    EnhancedDimensionAggregator,
    EnhancedAreaAggregator,
    EnhancedClusterAggregator,
    EnhancedMacroAggregator,
    enhance_aggregator,
)
from .adaptive_meso_scoring import (
    AdaptivePenaltyConfig,
    DispersionScenario,
    compute_adaptive_penalty,
    classify_dispersion_scenario,
)
from .signal_enriched_aggregation import (
    SignalEnrichedAggregator,
    SignalWeightAdjustment,
)

__all__ = [
    "ConfidenceInterval",
    "DispersionMetrics",
    "HermeticityDiagnosis",
    "EnhancedDimensionAggregator",
    "EnhancedAreaAggregator",
    "EnhancedClusterAggregator",
    "EnhancedMacroAggregator",
    "enhance_aggregator",
    "AdaptivePenaltyConfig",
    "DispersionScenario",
    "compute_adaptive_penalty",
    "classify_dispersion_scenario",
    "SignalEnrichedAggregator",
    "SignalWeightAdjustment",
]
