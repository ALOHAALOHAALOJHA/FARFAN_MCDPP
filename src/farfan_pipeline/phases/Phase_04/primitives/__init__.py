"""Phase 4 Aggregation Pipeline Primitives.

This package contains the foundational primitives for Phase 4 aggregation:
- Aggregation settings and configuration
- Choquet integral primitives for non-linear aggregation
- Quality levels and thresholds
- Signal-enriched aggregation
- Type definitions
- Uncertainty metrics
- Adaptive MESO scoring
- Aggregation enhancements

NOTE: This package exports ONLY what is actually defined in each module.
Imports are verified to match each module's __all__ exports.

Module: src/farfan_pipeline/phases/Phase_04/primitives/__init__.py
Version: 2.0.0 (Fixed import mismatches)
"""

from __future__ import annotations

# Aggregation settings
from .phase4_00_00_aggregation_settings import (
    AggregationSettings,
    validate_aggregation_settings,
)

# Choquet integral primitives
from .phase4_00_00_choquet_primitives import (
    CalibrationResult,
    CapacityIdentificationError,
    ChoquetAggregator,
    ChoquetConfig,
    FuzzyMeasureGenerator,
    FuzzyMeasureViolationError,
    InteractionStructure,
)

# Quality levels
from .phase4_00_00_quality_levels import (
    DEFAULT_THRESHOLDS,
    QualityLevel,
    QualityLevelThresholds,
    determine_quality_level,
    determine_quality_level_str,
    format_quality_report,
    get_quality_improvement_needed,
    get_quality_score_delta,
)

# Signal-enriched primitives
from .phase4_00_00_signal_enriched_primitives import (
    SignalEnrichedAggregator,
    adjust_weights,
    get_representative_question_for_dimension,
    interpret_dispersion,
)

# Type definitions
from .phase4_00_00_types import (
    PolicyAreaID,
    DimensionID,
    QuestionID,
    ClusterID,
    Score,
    Weight,
    AggregationMethod,
)

# Uncertainty metrics
from .phase4_00_00_uncertainty_metrics import (
    BootstrapAggregator,
    BootstrapConvergenceAnalyzer,
    ConvergenceDiagnostics,
    ConvergenceError,
    DistributionError,
    UncertaintyMetrics,
    aggregate_with_convergence,
    aggregate_with_uncertainty,
)

# Adaptive MESO scoring
from .phase4_40_00_adaptive_meso_scoring import (
    AdaptiveMesoScoring,
    AdaptiveScoringConfig,
    ScoringMetrics,
    create_adaptive_scorer,
)

# Aggregation enhancements
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
    "validate_aggregation_settings",
    # Choquet primitives
    "CalibrationResult",
    "CapacityIdentificationError",
    "ChoquetAggregator",
    "ChoquetConfig",
    "FuzzyMeasureGenerator",
    "FuzzyMeasureViolationError",
    "InteractionStructure",
    # Quality levels
    "DEFAULT_THRESHOLDS",
    "QualityLevel",
    "QualityLevelThresholds",
    "determine_quality_level",
    "determine_quality_level_str",
    "format_quality_report",
    "get_quality_improvement_needed",
    "get_quality_score_delta",
    # Signal enriched primitives
    "SignalEnrichedAggregator",
    "adjust_weights",
    "get_representative_question_for_dimension",
    "interpret_dispersion",
    # Types
    "PolicyAreaID",
    "DimensionID",
    "QuestionID",
    "ClusterID",
    "Score",
    "Weight",
    "AggregationMethod",
    # Uncertainty metrics
    "BootstrapAggregator",
    "BootstrapConvergenceAnalyzer",
    "ConvergenceDiagnostics",
    "ConvergenceError",
    "DistributionError",
    "UncertaintyMetrics",
    "aggregate_with_convergence",
    "aggregate_with_uncertainty",
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
