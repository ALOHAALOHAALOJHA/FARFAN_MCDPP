"""
Phase 4-7 Aggregation Pipeline Compatibility Package
=====================================================

Backward compatibility layer that re-exports Phase 4-7 aggregation
functionality from their actual implementation locations.
"""

from .aggregation import (
    DimensionAggregator,
    AggregationSettings,
    SignalEnrichedAggregator,
    ScoredResult,
)

from .aggregation_enhancements import (
    AdaptiveMesoScoring,
)

from .adaptive_meso_scoring import (
    AdaptiveScoringConfig,
    ScoringMetrics,
    create_adaptive_scorer,
)

__all__ = [
    "DimensionAggregator",
    "AggregationSettings",
    "SignalEnrichedAggregator",
    "ScoredResult",
    "AdaptiveMesoScoring",
    "AdaptiveScoringConfig",
    "ScoringMetrics",
    "create_adaptive_scorer",
]
