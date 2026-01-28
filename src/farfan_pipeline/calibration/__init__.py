"""
F.A.R.F.A.N Calibration Module
==============================

Bayesian calibration, validation, and parameter estimation.

Key Exports:
------------
- CalibrationMetrics: Result of calibration process
- Phase1PDMCalibrator: PDM calibration system
"""

from farfan_pipeline.calibration.pdm_calibrator import (
    CalibrationMetrics,
    Phase1PDMCalibrator,
)

from farfan_pipeline.calibration.registry import (
    EpistemicCalibrationRegistry,
    create_registry,
)

from farfan_pipeline.calibration.calibration_core import (
    ValidationError,
    CalibrationBoundsError,
    ClosedInterval,
    validate_epistemic_level,
    validate_output_type_for_level,
    validate_fusion_behavior_for_level,
)

from farfan_pipeline.calibration.epistemic_core import (
    EpistemicLevel,
    N0InfrastructureCalibration,
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    N3AuditCalibration,
    N4MetaCalibration,
    create_calibration,
    get_default_calibration_for_level,
)

from farfan_pipeline.calibration.type_defaults import (
    get_type_defaults,
    get_all_type_defaults,
    is_operation_prohibited,
    is_operation_permitted,
    get_fusion_strategy,
    validate_fusion_strategy_for_type,
    get_contract_type_for_question,
)

# Mathematical calibration optimizers (v5.0.0)
try:
    from farfan_pipeline.calibration.mathematical_calibration import (
        N1EmpiricalOptimizer,
        N2InferentialOptimizer,
        N3AuditOptimizer,
        N4MetaOptimizer,
    )
    MATHEMATICAL_CALIBRATION_AVAILABLE = True
except ImportError:
    # scipy/sklearn not available - mathematical optimization disabled
    N1EmpiricalOptimizer = None
    N2InferentialOptimizer = None
    N3AuditOptimizer = None
    N4MetaOptimizer = None
    MATHEMATICAL_CALIBRATION_AVAILABLE = False

# Alias for backward compatibility
CalibrationResult = CalibrationMetrics
PDPCalibrator = Phase1PDMCalibrator
CalibrationRegistry = EpistemicCalibrationRegistry
EpistemicRegistry = EpistemicCalibrationRegistry  # Additional alias

__all__ = [
    "CalibrationResult",
    "CalibrationMetrics",
    "PDPCalibrator",
    "Phase1PDMCalibrator",
    "CalibrationRegistry",
    "EpistemicCalibrationRegistry",
    "EpistemicRegistry",
    "ValidationError",
    "CalibrationBoundsError",
    "ClosedInterval",
    "EpistemicLevel",
    "N0InfrastructureCalibration",
    "N1EmpiricalCalibration",
    "N2InferentialCalibration",
    "N3AuditCalibration",
    "N4MetaCalibration",
    "create_calibration",
    "get_default_calibration_for_level",
    "validate_epistemic_level",
    "validate_output_type_for_level",
    "validate_fusion_behavior_for_level",
    "create_registry",
    "get_type_defaults",
    "get_all_type_defaults",
    "is_operation_prohibited",
    "is_operation_permitted",
    "get_fusion_strategy",
    "validate_fusion_strategy_for_type",
    "get_contract_type_for_question",
    # Mathematical calibration optimizers (v5.0.0)
    "N1EmpiricalOptimizer",
    "N2InferentialOptimizer",
    "N3AuditOptimizer",
    "N4MetaOptimizer",
    "MATHEMATICAL_CALIBRATION_AVAILABLE",
]
