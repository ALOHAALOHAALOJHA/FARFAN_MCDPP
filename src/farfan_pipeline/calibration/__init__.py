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
]
