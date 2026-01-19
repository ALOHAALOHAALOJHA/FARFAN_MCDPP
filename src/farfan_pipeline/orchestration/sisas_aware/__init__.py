"""
SISAS-Aware Orchestration Module

This module provides signal-driven orchestration for the FARFAN pipeline.
All phase coordination is handled through signals, not direct invocation.

Architecture:
- MainOrchestrator: Core signal-driven orchestrator
- Orchestration Core: Consolidated state machine, dependency graph, and scheduler
- Signal Contracts: All orchestration signals (lifecycle, decision, coordination)

Version: 1.0.0
"""

# Core Orchestrator
from .main_orchestrator import (
    MainOrchestrator,
    OrchestratorConfiguration,
    OrchestratorMode,
)

# Orchestration Core (Consolidated: State Machine, Dependency Graph, Phase Scheduler)
from .orchestration_core import (
    # Exceptions
    OrchestrationError,
    DependencyResolutionError,
    SchedulingError,
    StateTransitionError,
    # State Machine
    OrchestrationState,
    StateTransition,
    VALID_TRANSITIONS,
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
)

# Signal Contracts - Now imported from SISAS
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

__version__ = "1.0.0"
__all__ = [
    # Core Orchestrator
    "MainOrchestrator",
    "OrchestratorConfiguration",
    "OrchestratorMode",
    # Orchestration Core (State Machine, Dependency Graph, Phase Scheduler)
    "OrchestrationError",
    "DependencyResolutionError",
    "SchedulingError",
    "StateTransitionError",
    "OrchestrationState",
    "StateTransition",
    "VALID_TRANSITIONS",
    "OrchestrationStateMachine",
    "DependencyStatus",
    "DependencyNode",
    "DependencyEdge",
    "GraphValidationResult",
    "DependencyGraph",
    "SchedulingStrategy",
    "SchedulingDecision",
    "PhaseScheduler",
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
