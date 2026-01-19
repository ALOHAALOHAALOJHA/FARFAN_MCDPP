# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/orchestration.py

"""
SISAS Orchestration Signal Types

This module provides all signal types for orchestration-level communication.

Signal Categories:
- Phase Lifecycle: PhaseStartSignal, PhaseCompleteSignal, PhaseProgressSignal, PhaseRetrySignal
- Orchestration Decision: OrchestrationInitializedSignal, OrchestrationCompleteSignal,
  OrchestrationDecisionSignal, ConstitutionalValidationSignal
- Coordination: PhaseReadyToStartSignal, DependencyGraphUpdatedSignal, PhaseBlockedSignal,
  ParallelExecutionLimitSignal, PhaseDependencySatisfiedSignal

AXIOMS:
- Signal-First: All orchestration communication happens via signals
- Contextual: Every signal carries rich context (phase_id, run_id, execution context)
- Observable: Complete audit trail via signal audit entries
- Contractual: All signals follow SISAS Signal base class contracts

Architecture:
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION SIGNAL TYPES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌─────────────────┐  │
│  │ Phase Lifecycle      │  │ Orchestration        │  │ Coordination    │  │
│  │ Signals              │  │ Decision Signals     │  │ Signals         │  │
│  │                      │  │                      │  │                 │  │
│  │ - PhaseStartSignal   │  │ - OrchestrationInit  │  │ - PhaseReady    │  │
│  │ - PhaseCompleteSignal│  │ - OrchestrationComp  │  │ - GraphUpdated  │  │
│  │ - PhaseProgressSignal│  │ - OrchestrationDec   │  │ - PhaseBlocked  │  │
│  │ - PhaseRetrySignal   │  │ - ConstitutionalVal  │  │ - ParallelLimit │  │
│  └──────────────────────┘  └──────────────────────┘  └─────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ...core.signal import Signal, SignalCategory, SignalConfidence, SignalContext, SignalSource


logger = logging.getLogger("SISAS.Orchestration.SignalTypes")


# =============================================================================
# ENUMS
# =============================================================================


class PhaseCompletionStatus(Enum):
    """Status of phase completion."""

    SUCCESS = auto()
    FAILURE = auto()
    PARTIAL = auto()
    TIMEOUT = auto()


class OrchestrationDecisionType(Enum):
    """Types of orchestration decisions."""

    PHASE_SCHEDULING = "PHASE_SCHEDULING"
    PHASE_COMPLETION_HANDLING = "PHASE_COMPLETION_HANDLING"
    RETRY_DECISION = "RETRY_DECISION"
    FAILURE_HANDLING = "FAILURE_HANDLING"
    DEPENDENCY_UPDATE = "DEPENDENCY_UPDATE"
    PARALLEL_EXECUTION_CONTROL = "PARALLEL_EXECUTION_CONTROL"


class OrchestrationFinalStatus(Enum):
    """Final orchestration status."""

    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class BlockingStatus(Enum):
    """Blocking status types."""

    TEMPORARY = "TEMPORARY"
    PERMANENT = "PERMANENT"


# =============================================================================
# PHASE LIFECYCLE SIGNALS
# =============================================================================


@dataclass
class PhaseStartSignal(Signal):
    """
    Signal emitted when a phase is ready to start.

    This signal does NOT invoke the phase directly. Instead, it is consumed
    by the PhaseConsumer which then executes the phase.

    AXIOMS:
    - Signal-First: Phase start is communicated via signal, not direct invocation
    - Contextual: Annotated with phase_id, run_id, execution context
    - Observable: Audit trail captures when and why phase started

    Attributes:
        run_id: Unique identifier for this orchestration run
        phase_id: Phase to start (e.g., "PHASE_2")
        execution_context: Context for phase execution
        upstream_dependencies: Phases that this phase depends on
        expected_signals: Signals this phase should emit
        timeout_seconds: Maximum time for phase execution
    """

    signal_type: str = "PhaseStartSignal"

    # Phase-specific fields
    run_id: str = ""
    phase_id: str = ""
    execution_context: Dict[str, Any] = None
    upstream_dependencies: List[str] = None
    expected_signals: List[str] = None
    timeout_seconds: int = 3600

    def __post_init__(self):
        """Validate phase start signal."""
        if self.execution_context is None:
            object.__setattr__(self, 'execution_context', {})
        if self.upstream_dependencies is None:
            object.__setattr__(self, 'upstream_dependencies', [])
        if self.expected_signals is None:
            object.__setattr__(self, 'expected_signals', [])

        super().__post_init__()

        # Add validation audit entry
        self.add_audit_entry(
            "PHASE_START_VALIDATED",
            details={
                "phase_id": self.phase_id,
                "run_id": self.run_id,
                "upstream_count": len(self.upstream_dependencies),
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class PhaseCompleteSignal(Signal):
    """
    Signal emitted when a phase completes execution.

    This is the ONLY way the orchestrator knows a phase has finished.
    The orchestrator subscribes to this signal and updates dependency graph.

    AXIOMS:
    - Signal-Only Completion: No direct callbacks, only signal emission
    - Status-Rich: Captures success/failure/partial/timeout
    - Result-Carrying: Contains completion metadata and outputs

    Attributes:
        run_id: Unique identifier for this orchestration run
        phase_id: Phase that completed
        status: Completion status (SUCCESS/FAILURE/PARTIAL/TIMEOUT)
        completion_metadata: Results and outputs from phase
        error_message: Error details if status is FAILURE
        execution_duration_seconds: How long the phase took
    """

    signal_type: str = "PhaseCompleteSignal"

    # Completion-specific fields
    run_id: str = ""
    phase_id: str = ""
    status: PhaseCompletionStatus = PhaseCompletionStatus.SUCCESS
    completion_metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    execution_duration_seconds: float = 0.0
    attempt_number: int = 1

    def __post_init__(self):
        """Validate phase complete signal."""
        if self.completion_metadata is None:
            object.__setattr__(self, 'completion_metadata', {})

        super().__post_init__()

        # Add completion audit entry
        self.add_audit_entry(
            "PHASE_COMPLETE_VALIDATED",
            details={
                "phase_id": self.phase_id,
                "run_id": self.run_id,
                "status": self.status.name,
                "duration": self.execution_duration_seconds,
                "attempt": self.attempt_number,
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL

    def is_success(self) -> bool:
        """Check if phase completed successfully."""
        return self.status == PhaseCompletionStatus.SUCCESS

    def is_failure(self) -> bool:
        """Check if phase failed."""
        return self.status == PhaseCompletionStatus.FAILURE

    def is_partial(self) -> bool:
        """Check if phase completed partially."""
        return self.status == PhaseCompletionStatus.PARTIAL

    def is_timeout(self) -> bool:
        """Check if phase timed out."""
        return self.status == PhaseCompletionStatus.TIMEOUT


@dataclass
class PhaseProgressSignal(Signal):
    """
    Signal emitted when a phase reports progress.

    This optional signal provides real-time progress updates during
    long-running phase execution.

    Attributes:
        run_id: Unique identifier for this orchestration run
        phase_id: Phase reporting progress
        progress_percent: Progress percentage (0-100)
        current_step: Current step description
        estimated_remaining_seconds: Estimated time to completion
        metadata: Additional progress metadata
    """

    signal_type: str = "PhaseProgressSignal"

    # Progress-specific fields
    run_id: str = ""
    phase_id: str = ""
    progress_percent: float = 0.0
    current_step: str = ""
    estimated_remaining_seconds: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate phase progress signal."""
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})

        # Clamp progress to 0-100
        object.__setattr__(self, 'progress_percent', max(0.0, min(100.0, self.progress_percent)))

        super().__post_init__()

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class PhaseRetrySignal(Signal):
    """
    Signal emitted when a phase is being retried.

    Attributes:
        run_id: Unique identifier for this orchestration run
        phase_id: Phase being retried
        attempt_number: Which retry attempt this is
        max_attempts: Maximum retry attempts allowed
        previous_error: Error from previous attempt
    """

    signal_type: str = "PhaseRetrySignal"

    # Retry-specific fields
    run_id: str = ""
    phase_id: str = ""
    attempt_number: int = 1
    max_attempts: int = 3
    previous_error: Optional[str] = None

    def __post_init__(self):
        """Validate phase retry signal."""
        super().__post_init__()

        self.add_audit_entry(
            "PHASE_RETRY_VALIDATED",
            details={
                "phase_id": self.phase_id,
                "run_id": self.run_id,
                "attempt": f"{self.attempt_number}/{self.max_attempts}",
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


# =============================================================================
# ORCHESTRATION DECISION SIGNALS
# =============================================================================


@dataclass
class OrchestrationInitializedSignal(Signal):
    """
    Signal emitted when orchestration is initialized.

    This signals that the orchestrator is ready to begin phase execution.
    It includes configuration, dependency graph summary, and validation status.

    Attributes:
        run_id: Unique identifier for this orchestration run
        configuration: Orchestrator configuration
        dependency_graph_summary: Summary of the dependency graph
        validation_passed: Whether initial validation passed
    """

    signal_type: str = "OrchestrationInitializedSignal"

    # Initialization-specific fields
    run_id: str = ""
    configuration: Dict[str, Any] = None
    dependency_graph_summary: Dict[str, Any] = None
    validation_passed: bool = True

    def __post_init__(self):
        """Validate orchestration initialized signal."""
        if self.configuration is None:
            object.__setattr__(self, 'configuration', {})
        if self.dependency_graph_summary is None:
            object.__setattr__(self, 'dependency_graph_summary', {})

        super().__post_init__()

        self.add_audit_entry(
            "ORCHESTRATION_INITIALIZED",
            details={
                "run_id": self.run_id,
                "validation_passed": self.validation_passed,
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class OrchestrationCompleteSignal(Signal):
    """
    Signal emitted when orchestration completes.

    This signals the end of the orchestration lifecycle, whether successful,
    with errors, or stopped. It includes a complete execution summary.

    Attributes:
        run_id: Unique identifier for this orchestration run
        final_status: Final orchestration status
        total_phases: Total number of phases
        completed_successfully: Number of phases that completed successfully
        completed_partially: Number of phases that completed partially
        failed: Number of phases that failed
        execution_summary: Complete execution summary
    """

    signal_type: str = "OrchestrationCompleteSignal"

    # Completion-specific fields
    run_id: str = ""
    final_status: str = "COMPLETED"
    total_phases: int = 0
    completed_successfully: int = 0
    completed_partially: int = 0
    failed: int = 0
    execution_summary: Dict[str, Any] = None

    def __post_init__(self):
        """Validate orchestration complete signal."""
        if self.execution_summary is None:
            object.__setattr__(self, 'execution_summary', {})

        super().__post_init__()

        self.add_audit_entry(
            "ORCHESTRATION_COMPLETE",
            details={
                "run_id": self.run_id,
                "final_status": self.final_status,
                "success_rate": f"{self.completed_successfully}/{self.total_phases}",
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class OrchestrationDecisionSignal(Signal):
    """
    Signal emitted for every orchestration decision.

    This is the PRIMARY audit signal for orchestration. It is emitted for:
    - Phase scheduling decisions
    - Phase completion handling
    - Retry decisions
    - Failure handling
    - Dependency updates

    AXIOM: Complete Observability - Every decision is auditable via this signal.

    Attributes:
        run_id: Unique identifier for this orchestration run
        decision_type: Type of decision (PHASE_SCHEDULING, PHASE_COMPLETION_HANDLING, etc.)
        decision_rationale: Explanation of why this decision was made
        phases_selected: Phases selected for execution (if applicable)
        phases_waiting: Phases ready but waiting (if applicable)
        phases_blocked: Phases blocked by dependencies (if applicable)
        dependency_state: Snapshot of dependency graph at decision time
    """

    signal_type: str = "OrchestrationDecisionSignal"

    # Decision-specific fields
    run_id: str = ""
    decision_type: str = ""
    decision_rationale: str = ""
    phases_selected: List[str] = None
    phases_waiting: List[str] = None
    phases_blocked: List[str] = None
    dependency_state: Dict[str, str] = None
    partial_results: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate orchestration decision signal."""
        if self.phases_selected is None:
            object.__setattr__(self, 'phases_selected', [])
        if self.phases_waiting is None:
            object.__setattr__(self, 'phases_waiting', [])
        if self.phases_blocked is None:
            object.__setattr__(self, 'phases_blocked', [])
        if self.dependency_state is None:
            object.__setattr__(self, 'dependency_state', {})

        super().__post_init__()

        self.add_audit_entry(
            "ORCHESTRATION_DECISION",
            details={
                "run_id": self.run_id,
                "decision_type": self.decision_type,
                "phases_affected": len(self.phases_selected) + len(self.phases_blocked),
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class ConstitutionalValidationSignal(Signal):
    """
    Signal emitted when constitutional/contract validation occurs.

    This signal reports on the health of the orchestration system,
    validating that all contracts are in place and all buses are available.

    Attributes:
        run_id: Unique identifier for this orchestration run
        validation_passed: Whether validation passed
        validation_errors: List of validation errors
        contracts_validated: Number of contracts validated
        timestamp: When validation occurred
    """

    signal_type: str = "ConstitutionalValidationSignal"

    # Validation-specific fields
    run_id: str = ""
    validation_passed: bool = True
    validation_errors: List[str] = None
    contracts_validated: int = 0
    timestamp: datetime = None

    def __post_init__(self):
        """Validate constitutional validation signal."""
        if self.validation_errors is None:
            object.__setattr__(self, 'validation_errors', [])
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow())

        super().__post_init__()

        confidence = (
            SignalConfidence.HIGH
            if self.validation_passed
            else SignalConfidence.LOW
        )

        self.add_audit_entry(
            "CONSTITUTIONAL_VALIDATION",
            details={
                "run_id": self.run_id,
                "passed": self.validation_passed,
                "error_count": len(self.validation_errors),
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.INTEGRITY


@dataclass
class DependencyGraphLoadedSignal(Signal):
    """
    Signal emitted when dependency graph is loaded/initialized.

    Attributes:
        run_id: Unique identifier for this orchestration run
        total_nodes: Number of nodes in the graph
        total_edges: Number of edges in the graph
        graph_structure: Summary of graph structure
    """

    signal_type: str = "DependencyGraphLoadedSignal"

    # Graph loading-specific fields
    run_id: str = ""
    total_nodes: int = 0
    total_edges: int = 0
    graph_structure: Dict[str, Any] = None

    def __post_init__(self):
        """Validate dependency graph loaded signal."""
        if self.graph_structure is None:
            object.__setattr__(self, 'graph_structure', {})

        super().__post_init__()

        self.add_audit_entry(
            "DEPENDENCY_GRAPH_LOADED",
            details={
                "run_id": self.run_id,
                "nodes": self.total_nodes,
                "edges": self.total_edges,
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL


# =============================================================================
# COORDINATION SIGNALS
# =============================================================================


@dataclass
class PhaseReadyToStartSignal(Signal):
    """
    Signal emitted when a phase is ready to start.

    This coordination signal indicates that:
    - All dependencies are satisfied
    - The phase has been scheduled
    - PhaseStartSignal will be emitted

    AXIOM: Separation of Concerns - "Ready" is separate from "Start"
    - PhaseReadyToStartSignal: Coordinator notification
    - PhaseStartSignal: Actual execution trigger

    Attributes:
        run_id: Unique identifier for this orchestration run
        phase_id: Phase that is ready
        dependencies_satisfied: Whether all dependencies are satisfied
        unsatisfied_dependencies: List of any unsatisfied dependencies (if any)
    """

    signal_type: str = "PhaseReadyToStartSignal"

    # Ready-specific fields
    run_id: str = ""
    phase_id: str = ""
    dependencies_satisfied: bool = True
    unsatisfied_dependencies: List[str] = None

    def __post_init__(self):
        """Validate phase ready signal."""
        if self.unsatisfied_dependencies is None:
            object.__setattr__(self, 'unsatisfied_dependencies', [])

        super().__post_init__()

        self.add_audit_entry(
            "PHASE_READY_TO_START",
            details={
                "run_id": self.run_id,
                "phase_id": self.phase_id,
                "dependencies_satisfied": self.dependencies_satisfied,
                "unsatisfied_count": len(self.unsatisfied_dependencies),
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class DependencyGraphUpdatedSignal(Signal):
    """
    Signal emitted when the dependency graph is updated.

    This signal notifies consumers that:
    - A phase status has changed
    - New phases may be unblocked
    - Downstream impact should be evaluated

    Attributes:
        run_id: Unique identifier for this orchestration run
        updated_node: Node that was updated
        new_status: New status of the node
        newly_unblocked_phases: Phases that became unblocked by this update
        impact_summary: Summary of downstream impact
    """

    signal_type: str = "DependencyGraphUpdatedSignal"

    # Graph update-specific fields
    run_id: str = ""
    updated_node: str = ""
    new_status: str = ""
    newly_unblocked_phases: List[str] = None
    impact_summary: Dict[str, Any] = None

    def __post_init__(self):
        """Validate dependency graph updated signal."""
        if self.newly_unblocked_phases is None:
            object.__setattr__(self, 'newly_unblocked_phases', [])
        if self.impact_summary is None:
            object.__setattr__(self, 'impact_summary', {})

        super().__post_init__()

        self.add_audit_entry(
            "DEPENDENCY_GRAPH_UPDATED",
            details={
                "run_id": self.run_id,
                "updated_node": self.updated_node,
                "new_status": self.new_status,
                "unblocked_count": len(self.newly_unblocked_phases),
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL


@dataclass
class PhaseBlockedSignal(Signal):
    """
    Signal emitted when a phase is blocked.

    This notification signal indicates that a phase cannot proceed
    due to unsatisfied dependencies.

    Attributes:
        run_id: Unique identifier for this orchestration run
        phase_id: Phase that is blocked
        blocking_dependencies: Dependencies that are blocking this phase
        blocking_status: Whether this is temporary or permanent block
    """

    signal_type: str = "PhaseBlockedSignal"

    # Blocked-specific fields
    run_id: str = ""
    phase_id: str = ""
    blocking_dependencies: List[str] = None
    blocking_status: str = "TEMPORARY"  # TEMPORARY or PERMANENT

    def __post_init__(self):
        """Validate phase blocked signal."""
        if self.blocking_dependencies is None:
            object.__setattr__(self, 'blocking_dependencies', [])

        super().__post_init__()

        self.add_audit_entry(
            "PHASE_BLOCKED",
            details={
                "run_id": self.run_id,
                "phase_id": self.phase_id,
                "blocking_count": len(self.blocking_dependencies),
                "blocking_status": self.blocking_status,
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class ParallelExecutionLimitSignal(Signal):
    """
    Signal emitted when parallel execution limit is reached.

    This coordination signal indicates that:
    - Maximum parallel phases are running
    - Additional ready phases must wait
    - Scheduler should queue phases for later

    Attributes:
        run_id: Unique identifier for this orchestration run
        current_parallel_count: Number of phases currently running
        max_parallel: Maximum parallel phases allowed
        waiting_phases: Phases waiting for execution slot
    """

    signal_type: str = "ParallelExecutionLimitSignal"

    # Parallel limit-specific fields
    run_id: str = ""
    current_parallel_count: int = 0
    max_parallel: int = 4
    waiting_phases: List[str] = None

    def __post_init__(self):
        """Validate parallel execution limit signal."""
        if self.waiting_phases is None:
            object.__setattr__(self, 'waiting_phases', [])

        super().__post_init__()

        self.add_audit_entry(
            "PARALLEL_LIMIT_REACHED",
            details={
                "run_id": self.run_id,
                "current": self.current_parallel_count,
                "max": self.max_parallel,
                "waiting": len(self.waiting_phases),
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class PhaseDependencySatisfiedSignal(Signal):
    """
    Signal emitted when a dependency is satisfied.

    This fine-grained coordination signal indicates that a specific
    dependency has been satisfied, potentially unblocking downstream phases.

    Attributes:
        run_id: Unique identifier for this orchestration run
        dependency_phase_id: Phase that completed (the dependency)
        downstream_phases_affected: Phases that depend on this one
        newly_ready_phases: Subset of downstream that are now fully ready
    """

    signal_type: str = "PhaseDependencySatisfiedSignal"

    # Dependency satisfied-specific fields
    run_id: str = ""
    dependency_phase_id: str = ""
    downstream_phases_affected: List[str] = None
    newly_ready_phases: List[str] = None

    def __post_init__(self):
        """Validate phase dependency satisfied signal."""
        if self.downstream_phases_affected is None:
            object.__setattr__(self, 'downstream_phases_affected', [])
        if self.newly_ready_phases is None:
            object.__setattr__(self, 'newly_ready_phases', [])

        super().__post_init__()

        self.add_audit_entry(
            "DEPENDENCY_SATISFIED",
            details={
                "run_id": self.run_id,
                "dependency": self.dependency_phase_id,
                "downstream_count": len(self.downstream_phases_affected),
                "newly_ready_count": len(self.newly_ready_phases),
            },
        )

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL


# =============================================================================
# SIGNAL CREATOR HELPER FUNCTIONS
# =============================================================================


def create_phase_start_signal(
    phase_id: str,
    run_id: str,
    upstream_dependencies: List[str],
    execution_context: Dict[str, Any],
    timeout_seconds: int = 3600,
    generator_vehicle: str = "main_orchestrator",
) -> PhaseStartSignal:
    """
    Create a PhaseStartSignal with proper SISAS context and source.

    Args:
        phase_id: Phase to start
        run_id: Orchestration run ID
        upstream_dependencies: Phases this phase depends on
        execution_context: Execution context for the phase
        timeout_seconds: Maximum execution time
        generator_vehicle: Vehicle generating this signal

    Returns:
        PhaseStartSignal: Properly configured signal
    """
    return PhaseStartSignal(
        context=SignalContext(
            node_type="phase",
            node_id=phase_id,
            phase=phase_id,
            consumer_scope=phase_id,
        ),
        source=SignalSource(
            event_id=str(uuid4()),
            source_file="orchestration.py",
            source_path="src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/orchestration.py",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=generator_vehicle,
        ),
        run_id=run_id,
        phase_id=phase_id,
        execution_context=execution_context,
        upstream_dependencies=upstream_dependencies,
        expected_signals=[],
        timeout_seconds=timeout_seconds,
        confidence=SignalConfidence.HIGH,
        rationale=f"Phase {phase_id} is ready to start (dependencies satisfied)",
    )


def create_phase_complete_signal(
    phase_id: str,
    run_id: str,
    status: PhaseCompletionStatus,
    completion_metadata: Dict[str, Any],
    execution_duration_seconds: float = 0.0,
    error_message: Optional[str] = None,
    attempt_number: int = 1,
    generator_vehicle: str = "phase_consumer",
) -> PhaseCompleteSignal:
    """
    Create a PhaseCompleteSignal with proper SISAS context and source.

    Args:
        phase_id: Phase that completed
        run_id: Orchestration run ID
        status: Completion status
        completion_metadata: Results and outputs
        execution_duration_seconds: Execution time
        error_message: Error details if failed
        attempt_number: Which attempt this was
        generator_vehicle: Vehicle generating this signal

    Returns:
        PhaseCompleteSignal: Properly configured signal
    """
    return PhaseCompleteSignal(
        context=SignalContext(
            node_type="phase",
            node_id=phase_id,
            phase=phase_id,
            consumer_scope=phase_id,
        ),
        source=SignalSource(
            event_id=str(uuid4()),
            source_file="orchestration.py",
            source_path="src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/orchestration.py",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=generator_vehicle,
        ),
        run_id=run_id,
        phase_id=phase_id,
        status=status,
        completion_metadata=completion_metadata,
        error_message=error_message,
        execution_duration_seconds=execution_duration_seconds,
        attempt_number=attempt_number,
        confidence=SignalConfidence.HIGH,
        rationale=f"Phase {phase_id} completed with status: {status.name}",
    )


def create_orchestration_initialized_signal(
    run_id: str,
    configuration: Dict[str, Any],
    dependency_graph_summary: Dict[str, Any],
    validation_passed: bool = True,
    generator_vehicle: str = "main_orchestrator",
) -> OrchestrationInitializedSignal:
    """Create an OrchestrationInitializedSignal with proper SISAS context."""
    return OrchestrationInitializedSignal(
        context=SignalContext(
            node_type="orchestration",
            node_id="main_orchestrator",
            phase="orchestration",
            consumer_scope="global",
        ),
        source=SignalSource(
            event_id=str(uuid4()),
            source_file="orchestration.py",
            source_path="src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/orchestration.py",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=generator_vehicle,
        ),
        run_id=run_id,
        configuration=configuration,
        dependency_graph_summary=dependency_graph_summary,
        validation_passed=validation_passed,
        confidence=SignalConfidence.HIGH,
        rationale="Orchestration initialized and ready to begin phase execution",
    )


def create_orchestration_decision_signal(
    run_id: str,
    decision_type: str,
    decision_rationale: str,
    phases_selected: List[str] = None,
    phases_waiting: List[str] = None,
    phases_blocked: List[str] = None,
    dependency_state: Dict[str, str] = None,
    generator_vehicle: str = "main_orchestrator",
) -> OrchestrationDecisionSignal:
    """Create an OrchestrationDecisionSignal with proper SISAS context."""
    return OrchestrationDecisionSignal(
        context=SignalContext(
            node_type="orchestration",
            node_id="main_orchestrator",
            phase="orchestration",
            consumer_scope="global",
        ),
        source=SignalSource(
            event_id=str(uuid4()),
            source_file="orchestration.py",
            source_path="src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/orchestration.py",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=generator_vehicle,
        ),
        run_id=run_id,
        decision_type=decision_type,
        decision_rationale=decision_rationale,
        phases_selected=phases_selected or [],
        phases_waiting=phases_waiting or [],
        phases_blocked=phases_blocked or [],
        dependency_state=dependency_state or {},
        confidence=SignalConfidence.HIGH,
        rationale=f"Orchestration decision: {decision_type}",
    )


def create_orchestration_complete_signal(
    run_id: str,
    final_status: str,
    total_phases: int,
    completed_successfully: int,
    completed_partially: int,
    failed: int,
    execution_summary: Dict[str, Any],
    generator_vehicle: str = "main_orchestrator",
) -> OrchestrationCompleteSignal:
    """Create an OrchestrationCompleteSignal with proper SISAS context."""
    return OrchestrationCompleteSignal(
        context=SignalContext(
            node_type="orchestration",
            node_id="main_orchestrator",
            phase="orchestration",
            consumer_scope="global",
        ),
        source=SignalSource(
            event_id=str(uuid4()),
            source_file="orchestration.py",
            source_path="src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/orchestration.py",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=generator_vehicle,
        ),
        run_id=run_id,
        final_status=final_status,
        total_phases=total_phases,
        completed_successfully=completed_successfully,
        completed_partially=completed_partially,
        failed=failed,
        execution_summary=execution_summary,
        confidence=SignalConfidence.HIGH,
        rationale=f"Orchestration completed with status: {final_status}",
    )


def create_phase_ready_to_start_signal(
    run_id: str,
    phase_id: str,
    dependencies_satisfied: bool,
    unsatisfied_dependencies: List[str] = None,
    generator_vehicle: str = "main_orchestrator",
) -> PhaseReadyToStartSignal:
    """Create a PhaseReadyToStartSignal with proper SISAS context."""
    return PhaseReadyToStartSignal(
        context=SignalContext(
            node_type="phase",
            node_id=phase_id,
            phase=phase_id,
            consumer_scope=phase_id,
        ),
        source=SignalSource(
            event_id=str(uuid4()),
            source_file="orchestration.py",
            source_path="src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/orchestration.py",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=generator_vehicle,
        ),
        run_id=run_id,
        phase_id=phase_id,
        dependencies_satisfied=dependencies_satisfied,
        unsatisfied_dependencies=unsatisfied_dependencies or [],
        confidence=SignalConfidence.HIGH,
        rationale=f"Phase {phase_id} is ready to start",
    )


def create_dependency_graph_updated_signal(
    run_id: str,
    updated_node: str,
    new_status: str,
    newly_unblocked_phases: List[str],
    impact_summary: Dict[str, Any] = None,
    generator_vehicle: str = "main_orchestrator",
) -> DependencyGraphUpdatedSignal:
    """Create a DependencyGraphUpdatedSignal with proper SISAS context."""
    return DependencyGraphUpdatedSignal(
        context=SignalContext(
            node_type="orchestration",
            node_id="main_orchestrator",
            phase="orchestration",
            consumer_scope="global",
        ),
        source=SignalSource(
            event_id=str(uuid4()),
            source_file="orchestration.py",
            source_path="src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/orchestration.py",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=generator_vehicle,
        ),
        run_id=run_id,
        updated_node=updated_node,
        new_status=new_status,
        newly_unblocked_phases=newly_unblocked_phases,
        impact_summary=impact_summary or {},
        confidence=SignalConfidence.HIGH,
        rationale=f"Dependency graph updated: {updated_node} -> {new_status}",
    )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Enums
    "PhaseCompletionStatus",
    "OrchestrationDecisionType",
    "OrchestrationFinalStatus",
    "BlockingStatus",
    # Phase Lifecycle
    "PhaseStartSignal",
    "PhaseCompleteSignal",
    "PhaseProgressSignal",
    "PhaseRetrySignal",
    "create_phase_start_signal",
    "create_phase_complete_signal",
    # Orchestration Decision
    "OrchestrationInitializedSignal",
    "OrchestrationCompleteSignal",
    "OrchestrationDecisionSignal",
    "ConstitutionalValidationSignal",
    "DependencyGraphLoadedSignal",
    "create_orchestration_initialized_signal",
    "create_orchestration_decision_signal",
    "create_orchestration_complete_signal",
    # Coordination
    "PhaseReadyToStartSignal",
    "DependencyGraphUpdatedSignal",
    "PhaseBlockedSignal",
    "ParallelExecutionLimitSignal",
    "PhaseDependencySatisfiedSignal",
    "create_phase_ready_to_start_signal",
    "create_dependency_graph_updated_signal",
]
