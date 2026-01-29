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
    EpistemicLevel,
)

from farfan_pipeline.calibration.epistemic_core import (
    N0InfrastructureCalibration,
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    N3AuditCalibration,
    N4MetaCalibration,
    create_calibration,
    get_default_calibration_for_level,
)

from farfan_pipeline.calibration.type_defaults import get_type_defaults

# Alias for backward compatibility
CalibrationResult = CalibrationMetrics
PDPCalibrator = Phase1PDMCalibrator
CalibrationRegistry = EpistemicCalibrationRegistry

__all__ = [
    # Core results
    "CalibrationResult",
    "CalibrationMetrics",
    "PDPCalibrator",
    "Phase1PDMCalibrator",
    "CalibrationRegistry",
    "EpistemicCalibrationRegistry",
    # Errors
    "ValidationError",
    "CalibrationBoundsError",
    # Types
    "ClosedInterval",
    "EpistemicLevel",
    # Epistemic calibrations
    "N0InfrastructureCalibration",
    "N1EmpiricalCalibration",
    "N2InferentialCalibration",
    "N3AuditCalibration",
    "N4MetaCalibration",
    # Factory functions
    "create_registry",
    "create_calibration",
    "get_default_calibration_for_level",
    "get_type_defaults",
]
