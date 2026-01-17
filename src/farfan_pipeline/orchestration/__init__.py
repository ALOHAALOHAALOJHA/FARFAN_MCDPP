"""
F.A.R.F.A.N Orchestration Module
================================

Public API for the orchestration layer.

EXPORTS:
    - Core Orchestrator: PipelineOrchestrator, ExecutionContext, PhaseResult
    - Factory-Aligned Orchestrator: Orchestrator, MethodExecutor
    - Phase 0 Validation: Phase0ValidationResult, GateResult
    - Configuration: OrchestratorConfig, validation functions, presets
    - Phase Management: PhaseID, PhaseStatus, ContractEnforcer
    - Calibration types: CalibrationResult, CalibrationSubject, etc.

Note: Calibration types imports are optional. If calibration_types module
      is not available, only core orchestration classes are exported.
"""

# Try to import calibration types if available
try:
    from farfan_pipeline.calibration.pdm_calibrator import CalibrationResult
    _has_calibration_types = True
except ImportError:
    _has_calibration_types = False

# Import all orchestration classes from core_orchestrator
from farfan_pipeline.orchestration.core_orchestrator import (
    ContractEnforcer,
    ExecutionContext,
    PhaseID,
    PhaseResult,
    PhaseStatus,
    PipelineOrchestrator,
    PHASE_METADATA,
    Orchestrator,
    MethodExecutor,
    Phase0ValidationResult,
    GateResult,
)

# Configuration Management
from farfan_pipeline.orchestration.orchestrator_config import (
    OrchestratorConfig,
    ConfigValidationError,
    validate_config,
    get_development_config,
    get_production_config,
    get_testing_config,
)

__all__ = [
    # Core Orchestrator
    "PipelineOrchestrator",
    "ExecutionContext",
    "PhaseResult",
    "PhaseStatus",
    "PhaseID",
    "ContractEnforcer",
    "PHASE_METADATA",

    # Factory-Aligned Orchestrator
    "Orchestrator",
    "MethodExecutor",

    # Phase 0 Validation
    "GateResult",
    "Phase0ValidationResult",

    # Configuration
    "OrchestratorConfig",
    "ConfigValidationError",
    "validate_config",
    "get_development_config",
    "get_production_config",
    "get_testing_config",

    # Calibration types (legacy)
    "LayerId",
    "ROLE_LAYER_REQUIREMENTS",
    "VALID_ROLES",
    "CalibrationSubject",
    "CalibrationEvidenceContext",
    "CalibrationResult",
]

# Add calibration types if available
if _has_calibration_types:
    __all__.append("CalibrationResult")
