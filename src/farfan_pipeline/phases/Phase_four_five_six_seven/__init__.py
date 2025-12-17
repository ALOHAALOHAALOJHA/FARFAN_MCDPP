"""
Phase Four Through Seven: Advanced Processing
==============================================

Combined phases 4-7 of the F.A.R.F.A.N pipeline responsible for advanced
processing and analysis of policy documents.

Phase 4-7: Aggregation Pipeline
--------------------------------

This module implements the complete aggregation pipeline for the policy analysis system:
- FASE 4: Dimension aggregation (60 dimensions: 6 × 10 policy areas)
- FASE 5: Policy area aggregation (10 areas)
- FASE 6: Cluster aggregation (4 MESO questions)
- FASE 7: Macro evaluation (1 holistic question)

New additions:
- Choquet aggregator for multi-layer calibration with interaction terms
"""

from .aggregation import (
    DimensionAggregator,
    AreaPolicyAggregator,
    ClusterAggregator,
    AggregationSettings,
    DimensionScore,
    AreaScore,
    ClusterScore,
    MacroScore,
)

from .choquet_aggregator import (
    ChoquetAggregator,
    ChoquetConfig,
    CalibrationResult,
    CalibrationBreakdown,
    CalibrationConfigError,
)

from .aggregation_enhancements import (
    EnhancedDimensionAggregator,
    EnhancedAreaAggregator,
    EnhancedClusterAggregator,
    EnhancedMacroAggregator,
    ConfidenceInterval,
    DispersionMetrics,
    HermeticityDiagnosis,
    StrategicAlignmentMetrics,
    enhance_aggregator,
)

from .aggregation_validation import (
    validate_phase4_output,
    validate_phase5_output,
    validate_phase6_output,
    validate_phase7_output,
    validate_full_aggregation_pipeline,
    enforce_validation_or_fail,
    ValidationResult,
    AggregationValidationError,
)

__all__ = [
    # Existing aggregation
    "DimensionAggregator",
    "AreaPolicyAggregator",
    "ClusterAggregator",
    "AggregationSettings",
    "DimensionScore",
    "AreaScore",
    "ClusterScore",
    "MacroScore",
    # Choquet aggregator
    "ChoquetAggregator",
    "ChoquetConfig",
    "CalibrationResult",
    "CalibrationBreakdown",
    "CalibrationConfigError",
    # Enhancements and contracts
    "EnhancedDimensionAggregator",
    "EnhancedAreaAggregator",
    "EnhancedClusterAggregator",
    "EnhancedMacroAggregator",
    "ConfidenceInterval",
    "DispersionMetrics",
    "HermeticityDiagnosis",
    "StrategicAlignmentMetrics",
    "enhance_aggregator",
    # Validation
    "validate_phase4_output",
    "validate_phase5_output",
    "validate_phase6_output",
    "validate_phase7_output",
    "validate_full_aggregation_pipeline",
    "enforce_validation_or_fail",
    "ValidationResult",
    "AggregationValidationError",
]
