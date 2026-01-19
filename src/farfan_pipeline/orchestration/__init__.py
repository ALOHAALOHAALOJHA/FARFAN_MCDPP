"""
F.A.R.F.A.N Orchestration Module
================================

Public API for the orchestration layer.

EXPORTS:
    - Unified Orchestrator: Single consolidated orchestrator
    - Configuration: OrchestratorConfig, validation functions, presets
    - Phase Management: PhaseID, PhaseStatus, PhaseResult, ExecutionContext
    - State Machine: OrchestrationStateMachine, OrchestrationState
    - Dependency Graph: DependencyGraph, DependencyStatus, DependencyNode
    - Phase Scheduler: PhaseScheduler, SchedulingStrategy

Note: This module now exports the unified orchestrator which consolidates
all orchestration logic from previously separate modules.
"""

# Try to import calibration types if available
try:
    from farfan_pipeline.calibration.pdm_calibrator import CalibrationResult
    _has_calibration_types = True
except ImportError:
    _has_calibration_types = False

# Import from unified orchestrator
from farfan_pipeline.orchestration.orchestrator import (
    # Configuration
    OrchestratorConfig,
    ConfigValidationError,
    validate_config,
    get_development_config,
    get_production_config,
    get_testing_config,

    # Exceptions
    OrchestrationError,
    DependencyResolutionError,
    SchedulingError,
    StateTransitionError,
    OrchestrationInitializationError,
    PhaseExecutionError,
    ContractViolationError,

    # State Machine
    OrchestrationState,
    StateTransition,
    OrchestrationStateMachine,

    # Dependency Graph
    DependencyStatus,
    DependencyNode,
    DependencyEdge,
    GraphValidationResult,
    DependencyGraph,

    # Phase Scheduler
    SchedulingStrategy,
    SchedulingDecision,
    PhaseScheduler,

    # Core Orchestrator
    PhaseStatus,
    PhaseID,
    PHASE_METADATA,
    PhaseResult,
    ExecutionContext,
    PipelineResult,
    UnifiedOrchestrator,
)

# Aliases for backward compatibility
PipelineOrchestrator = UnifiedOrchestrator
ContractEnforcer = None  # TODO: Implement in unified orchestrator
Orchestrator = UnifiedOrchestrator
MethodExecutor = None  # TODO: Implement in unified orchestrator
Phase0ValidationResult = None  # TODO: Implement in unified orchestrator
GateResult = None  # TODO: Implement in unified orchestrator

__all__ = [
    # Unified Orchestrator
    "UnifiedOrchestrator",
    "PipelineOrchestrator",  # Alias

    # Configuration
    "OrchestratorConfig",
    "ConfigValidationError",
    "validate_config",
    "get_development_config",
    "get_production_config",
    "get_testing_config",

    # Phase Management
    "PhaseID",
    "PhaseStatus",
    "PhaseResult",
    "ExecutionContext",
    "PHASE_METADATA",
    "PipelineResult",

    # State Machine
    "OrchestrationState",
    "OrchestrationStateMachine",
    "StateTransition",

    # Dependency Graph
    "DependencyGraph",
    "DependencyStatus",
    "DependencyNode",
    "DependencyEdge",
    "GraphValidationResult",

    # Phase Scheduler
    "PhaseScheduler",
    "SchedulingStrategy",
    "SchedulingDecision",

    # Exceptions
    "OrchestrationError",
    "DependencyResolutionError",
    "SchedulingError",
    "StateTransitionError",
    "OrchestrationInitializationError",
    "PhaseExecutionError",
    "ContractViolationError",

    # Backward compatibility aliases
    "ContractEnforcer",
    "Orchestrator",
    "MethodExecutor",
    "Phase0ValidationResult",
    "GateResult",
]

# Add calibration types if available
if _has_calibration_types:
    __all__.extend([
        "CalibrationResult",
    ])
