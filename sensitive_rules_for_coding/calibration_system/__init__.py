"""
⚠️  SENSITIVE - Production Calibration System ⚠️

COHORT_2024 intrinsic calibration loader with role-based scoring.

This module contains SENSITIVE production calibration data and logic.
See README_SENSITIVE.md for security requirements and usage guidelines.
"""

from .COHORT_2024_intrinsic_calibration_loader_SENSITIVE import (
    CalibrationScore,
    IntrinsicCalibrationLoader,
    get_calibration_statistics,
    get_detailed_score,
    get_role_default,
    get_score,
    is_excluded,
    is_pending,
    list_calibrated_methods,
    load_intrinsic_calibration,
)

__all__ = [
    "CalibrationScore",
    "IntrinsicCalibrationLoader",
    "load_intrinsic_calibration",
    "get_score",
    "get_detailed_score",
    "is_excluded",
    "is_pending",
    "list_calibrated_methods",
    "get_role_default",
    "get_calibration_statistics",
]
