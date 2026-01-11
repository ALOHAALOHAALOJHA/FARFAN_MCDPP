"""
Calibration Subpackage - Decorators and Instrumentation
========================================================

Provides:
- calibrated_method: Decorator for method-level calibration
- Telemetry collection
- Validation hooks
"""

from __future__ import annotations

from .decorators import (
    calibrated_method,
    MethodInvocationContext,
    MethodCalibrationSpec,
    ValidationResult,
    InstrumentationMode,
    is_calibrated_method,
    get_calibration_spec,
    flush_telemetry,
    calibration_context,
)

__version__ = "1.0.0"

__all__ = [
    "calibrated_method",
    "MethodInvocationContext",
    "MethodCalibrationSpec",
    "ValidationResult",
    "InstrumentationMode",
    "is_calibrated_method",
    "get_calibration_spec",
    "flush_telemetry",
    "calibration_context",
]
