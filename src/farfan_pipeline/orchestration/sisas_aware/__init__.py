"""
SISAS-Aware Orchestration Module

This module provides signal-driven orchestration for the FARFAN pipeline.
All phase coordination is handled through signals, not direct invocation.

NOTE: The orchestrator files (main_orchestrator.py, orchestration_core.py) have been
consolidated into the unified orchestrator.py. This module now re-exports the
relevant components from the unified orchestrator.

Version: 2.0.0 (Unified)
"""

# Import from unified orchestrator
from farfan_pipeline.orchestration.orchestrator import (
    # Exceptions
    OrchestrationError,
    DependencyResolutionError,
    SchedulingError,
    StateTransitionError,
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
    # Configuration
    OrchestratorConfig,
)

# Signal Contracts - Imported from SISAS
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals.types import (
    # Phase Lifecycle
    PhaseCompletionStatus,
    PhaseStartSignal,
    PhaseCompleteSignal,
    PhaseProgressSignal,
    PhaseRetrySignal,
    create_phase_start_signal,
    create_phase_complete_signal,
    # Orchestration Decision
    OrchestrationInitializedSignal,
    OrchestrationCompleteSignal,
    OrchestrationDecisionSignal,
    ConstitutionalValidationSignal,
    DependencyGraphLoadedSignal,
    create_orchestration_initialized_signal,
    create_orchestration_decision_signal,
    create_orchestration_complete_signal,
    # Coordination
    PhaseReadyToStartSignal,
    DependencyGraphUpdatedSignal,
    PhaseBlockedSignal,
    ParallelExecutionLimitSignal,
    PhaseDependencySatisfiedSignal,
    create_phase_ready_to_start_signal,
    create_dependency_graph_updated_signal,
)

# Aliases for backward compatibility
MainOrchestrator = None  # TODO: Implement signal-driven orchestrator in unified module
OrchestratorConfiguration = OrchestratorConfig
OrchestratorMode = None  # Use SchedulingStrategy instead

__version__ = "2.0.0"
__all__ = [
    # Unified Orchestrator imports
    "OrchestrationError",
    "DependencyResolutionError",
    "SchedulingError",
    "StateTransitionError",
    "OrchestrationState",
    "StateTransition",
    "OrchestrationStateMachine",
    "DependencyStatus",
    "DependencyNode",
    "DependencyEdge",
    "GraphValidationResult",
    "DependencyGraph",
    "SchedulingStrategy",
    "SchedulingDecision",
    "PhaseScheduler",
    "OrchestratorConfig",

    # Backward compatibility aliases
    "MainOrchestrator",
    "OrchestratorConfiguration",
    "OrchestratorMode",

    # Signals
    "PhaseCompletionStatus",
    "PhaseStartSignal",
    "PhaseCompleteSignal",
    "PhaseProgressSignal",
    "PhaseRetrySignal",
    "create_phase_start_signal",
    "create_phase_complete_signal",
    "OrchestrationInitializedSignal",
    "OrchestrationCompleteSignal",
    "OrchestrationDecisionSignal",
    "ConstitutionalValidationSignal",
    "DependencyGraphLoadedSignal",
    "create_orchestration_initialized_signal",
    "create_orchestration_decision_signal",
    "create_orchestration_complete_signal",
    "PhaseReadyToStartSignal",
    "DependencyGraphUpdatedSignal",
    "PhaseBlockedSignal",
    "ParallelExecutionLimitSignal",
    "PhaseDependencySatisfiedSignal",
    "create_phase_ready_to_start_signal",
    "create_dependency_graph_updated_signal",
]
