"""Phase 4 Aggregation Pipeline Enhancements.

This package contains enhanced aggregators with additional features:
- Confidence interval tracking
- Dispersion analysis
- Hermeticity diagnosis
- Adaptive penalty computation
- Choquet integral primitives
- Quality levels and uncertainty metrics

NOTE: Only Phase 4 (Dimension) aggregation enhancements are included here.
Area, Cluster, and Macro aggregation enhancements belong to Phases 5, 6, and 7.
"""

from __future__ import annotations

from .phase4_00_00_aggregation_settings import (
    AggregationSettings,
    DEFAULT_SETTINGS,
)
from .phase4_00_00_choquet_primitives import (
    ChoquetCapacity,
    ChoquetIntegral,
    ChoquetMeasure,
    MobiusTransform,
)
from .phase4_00_00_quality_levels import (
    QualityLevel,
    QualityMetrics,
    assign_quality_level,
)
from .phase4_00_00_signal_enriched_primitives import (
    SignalEnrichedPrimitive,
    SignalEnrichedPrimitivesCollection,
)
from .phase4_00_00_types import (
    AggregationInput,
    AggregationOutput,
    AggregationResult,
)
from .phase4_00_00_uncertainty_metrics import (
    UncertaintyMetric,
    UncertaintyMetrics,
)
from .phase4_40_00_adaptive_meso_scoring import (
    AdaptiveMesoScoring,
    AdaptiveScoringConfig,
    ScoringMetrics,
    create_adaptive_scorer,
)
from .phase4_40_00_aggregation_enhancements import (
    ConfidenceInterval,
    DispersionMetrics,
    HermeticityDiagnosis,
    StrategicAlignmentMetrics,
    enhance_aggregator,
)

__all__ = [
    # Aggregation settings
    "AggregationSettings",
    "DEFAULT_SETTINGS",
    # Choquet primitives
    "ChoquetCapacity",
    "ChoquetIntegral",
    "ChoquetMeasure",
    "MobiusTransform",
    # Quality levels
    "QualityLevel",
    "QualityMetrics",
    "assign_quality_level",
    # Signal enriched primitives
    "SignalEnrichedPrimitive",
    "SignalEnrichedPrimitivesCollection",
    # Types
    "AggregationInput",
    "AggregationOutput",
    "AggregationResult",
    # Uncertainty metrics
    "UncertaintyMetric",
    "UncertaintyMetrics",
    # Adaptive meso scoring
    "AdaptiveMesoScoring",
    "AdaptiveScoringConfig",
    "ScoringMetrics",
    "create_adaptive_scorer",
    # Aggregation enhancements
    "ConfidenceInterval",
    "DispersionMetrics",
    "HermeticityDiagnosis",
    "StrategicAlignmentMetrics",
    "enhance_aggregator",
]
