"""
F.A.R.F.A.N Orchestration Module
================================

Public API for the orchestration layer.

EXPORTS:
    - Core Orchestrator: PipelineOrchestrator, ExecutionContext, PhaseResult
    - Configuration: OrchestratorConfig, validation functions, presets
    - Phase Management: PhaseID, PhaseStatus, ContractEnforcer
    - Calibration types: CalibrationResult, CalibrationSubject, etc.

Note: Orchestrator is imported from orchestrator.py directly to avoid
      circular import issues with complex dependencies.
"""

from farfan_pipeline.calibration.calibration_types import (
    ROLE_LAYER_REQUIREMENTS,
    VALID_ROLES,
    CalibrationEvidenceContext,
    CalibrationResult,
    CalibrationSubject,
    LayerId,
)

# Core Orchestrator Components
from farfan_pipeline.orchestration.core_orchestrator import (
    ContractEnforcer,
    ExecutionContext,
    PhaseID,
    PhaseResult,
    PhaseStatus,
    PipelineOrchestrator,
    PHASE_METADATA,
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
