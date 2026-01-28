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

# Alias for backward compatibility
CalibrationResult = CalibrationMetrics
PDPCalibrator = Phase1PDMCalibrator
CalibrationRegistry = EpistemicCalibrationRegistry

__all__ = [
    "CalibrationResult",
    "CalibrationMetrics",
    "PDPCalibrator",
    "Phase1PDMCalibrator",
    "CalibrationRegistry",
    "EpistemicCalibrationRegistry",
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
]
