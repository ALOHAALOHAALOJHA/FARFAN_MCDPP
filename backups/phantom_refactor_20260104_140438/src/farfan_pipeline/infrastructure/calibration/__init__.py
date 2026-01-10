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
from .unit_of_analysis import (
    FiscalContext,
    MunicipalityCategory,
    UnitOfAnalysis,
)
from .ingestion_calibrator import (
    CalibrationStrategy,
    IngestionCalibrator,
    StandardCalibrationStrategy,
    AggressiveCalibrationStrategy,
    ConservativeCalibrationStrategy,
)
from .method_binding_validator import (
    EpistemicViolation,
    MethodBinding,
    MethodBindingSet,
    MethodBindingValidator,
    ValidationResult,
    ValidationSeverity,
)
from .phase2_calibrator import (
    Phase2CalibrationResult,
    Phase2Calibrator,
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
    # Unit of Analysis
    "FiscalContext",
    "MunicipalityCategory",
    "UnitOfAnalysis",
    # Ingestion Calibrator
    "CalibrationStrategy",
    "IngestionCalibrator",
    "StandardCalibrationStrategy",
    "AggressiveCalibrationStrategy",
    "ConservativeCalibrationStrategy",
    # Method Binding Validator
    "EpistemicViolation",
    "MethodBinding",
    "MethodBindingSet",
    "MethodBindingValidator",
    "ValidationResult",
    "ValidationSeverity",
    # Phase-2 Calibrator
    "Phase2CalibrationResult",
    "Phase2Calibrator",
]
