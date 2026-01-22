"""
F.A.R.F.A.N Calibration Module
==============================

Bayesian calibration, validation, and parameter estimation.

Key Exports:
------------
- CalibrationResult: Result of calibration process
- PDPCalibrator: PDP calibration system
"""

from farfan_pipeline.calibration.pdm_calibrator import (
    CalibrationResult,
    PDPCalibrator,
)

from farfan_pipeline.calibration.registry import (
    CalibrationRegistry,
)

__all__ = [
    "CalibrationResult",
    "PDPCalibrator",
    "CalibrationRegistry",
]
