"""
Calibration Infrastructure
==========================
Public API for calibration layer.

DESIGN PATTERN: Facade Pattern
- Single entry point for all calibration operations
- Hides internal complexity from consumers
"""
from .calibration_core import (
    CalibrationBounds,
    CalibrationLayer,
    CalibrationParameter,
    CalibrationPhase,
)
from .type_defaults import (
    PROHIBITED_OPERATIONS,
    get_type_defaults,
    is_operation_prohibited,
)

__all__ = [
    "CalibrationBounds",
    "CalibrationLayer",
    "CalibrationParameter",
    "CalibrationPhase",
    "get_type_defaults",
    "is_operation_prohibited",
    "PROHIBITED_OPERATIONS",
]
