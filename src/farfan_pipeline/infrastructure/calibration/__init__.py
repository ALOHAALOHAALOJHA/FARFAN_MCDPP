"""
Calibration Infrastructure
==========================
Public API for calibration layer.

DESIGN PATTERN: Facade Pattern
- Single entry point for all calibration operations
- Hides internal complexity from consumers

Schema Version: 2.0.0
"""
from .calibration_core import (
    CalibrationError,
    CalibrationLayer,
    CalibrationParameter,
    CalibrationPhase,
    ClosedInterval,
    EvidenceReference,
    ExpirationError,
    IntegrityError,
    ValidationError,
    ValidityStatus,
)
from .type_defaults import (
    PROHIBITED_OPERATIONS,
    get_type_defaults,
    is_operation_prohibited,
)

__all__ = [
    # Core types
    "CalibrationLayer",
    "CalibrationParameter",
    "CalibrationPhase",
    "ClosedInterval",
    "EvidenceReference",
    "ValidityStatus",
    # Exceptions
    "CalibrationError",
    "ValidationError",
    "IntegrityError",
    "ExpirationError",
    # Type defaults
    "get_type_defaults",
    "is_operation_prohibited",
    "PROHIBITED_OPERATIONS",
]
