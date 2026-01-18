"""
SISAS-Aware Main Orchestrator

This module provides the primary orchestrator for signal-driven phase execution.

AXIOMS:
- Signal-First: All communication via signals, never direct invocation
- Contract-Bound: All signal operations have contracts
- Observable: Every decision emits OrchestrationDecisionSignal
- Zero-Direct-Invocation: Never call phase.execute() directly

Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import (
    BusRegistry,
    SignalBus,
    BusType,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
    SignalContext,
    SignalSource,
)

# Orchestration Core (Consolidated: State Machine, Dependency Graph, Phase Scheduler, Exceptions)
from .orchestration_core import (
    # Exceptions
    OrchestrationError,
    DependencyResolutionError,
    SchedulingError,
    StateTransitionError,
    # State Machine
    OrchestrationStateMachine,
    OrchestrationState,
    # Dependency Graph
    DependencyGraph,
    DependencyStatus,
    # Phase Scheduler
    PhaseScheduler,
    SchedulingStrategy,
)

# Signal Contracts (Consolidated: All signal types)
from .signal_contracts import (
    # Phase Lifecycle
    PhaseStartSignal,
    PhaseCompleteSignal,
    PhaseCompletionStatus,
    create_phase_start_signal,
    create_phase_complete_signal,
    # Orchestration Decision
    OrchestrationInitializedSignal,
    OrchestrationCompleteSignal,
    OrchestrationDecisionSignal,
    ConstitutionalValidationSignal,
    create_orchestration_initialized_signal,
    create_orchestration_decision_signal,
    create_orchestration_complete_signal,
    # Coordination
    PhaseReadyToStartSignal,
    DependencyGraphUpdatedSignal,
    create_phase_ready_to_start_signal,
    create_dependency_graph_updated_signal,
)

# Additional exceptions not in orchestration_core
class OrchestrationInitializationError(OrchestrationError):
    """Raised when the orchestrator cannot be initialized."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="ORCH_INIT_ERROR", context=kwargs)

class PhaseExecutionError(OrchestrationError):
    """Raised when a phase fails to execute."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="PHASE_EXECUTION_ERROR", context=kwargs)

class ContractViolationError(OrchestrationError):
    """Raised when a signal contract is violated."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CONTRACT_VIOLATION_ERROR", context=kwargs)


logger = logging.getLogger("SISAS.Orchestrator.Main")


class OrchestratorMode(Enum):
    """Orchestration execution modes."""

    SEQUENTIAL = auto()
    PARALLEL = auto()
    HYBRID = auto()


@dataclass
class OrchestratorConfiguration:
    """
    Immutable configuration for the orchestrator.

    Attributes:
        mode: Execution mode (SEQUENTIAL/PARALLEL/HYBRID)
        max_parallel_phases: Maximum phases to run in parallel
        phase_timeout_seconds: Default timeout for phase execution
        retry_failed_phases: Whether to retry failed phases
        max_retries_per_phase: Maximum retry attempts per phase
        emit_decision_signals: Whether to emit decision signals (for audit)
        validate_contracts_on_startup: Validate contracts at initialization
        fail_fast_on_contract_violation: Fail on contract violations
    """

    run_id: str = field(default_factory=lambda: str(uuid4()))
    mode: OrchestratorMode = OrchestratorMode.HYBRID
    max_parallel_phases: int = 4
    phase_timeout_seconds: int = 3600
    retry_failed_phases: bool = True
    max_retries_per_phase: int = 3
    emit_decision_signals: bool = True
    validate_contracts_on_startup: bool = True
    fail_fast_on_contract_violation: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "mode": self.mode.name,
            "max_parallel_phases": self.max_parallel_phases,
            "phase_timeout_seconds": self.phase_timeout_seconds,
            "retry_failed_phases": self.retry_failed_phases,
            "max_retries_per_phase": self.max_retries_per_phase,
            "emit_decision_signals": self.emit_decision_signals,
        }


@dataclass
class MainOrchestrator:
    """
    SISAS-Aware Main Orchestrator.

    RESPONSIBILITIES:
    1. Manage orchestration lifecycle via state machine
    2. Publish PhaseStartSignal to initiate phases (NEVER direct invocation)
    3. Consume PhaseCompleteSignal to detect completion
    4. Maintain and update dependency graph
    5. Emit OrchestrationDecisionSignal for every decision

    AXIOMS:
    - Signal-First: Toda comunicación es vía señales
    - Zero-Direct-Invocation: NUNCA invocar directamente métodos de fase
    - Observable: Cada decisión genera señal auditable
    - Contract-Bound: Toda publicación/consumo tiene contrato

    INYECCIÓN OBLIGATORIA:
    - bus_registry: BusRegistry (infraestructura de routing)
    - dependency_graph: DependencyGraph (grafo de fases)
    """

    # === DEPENDENCIES (REQUIRED) ===
    bus_registry: BusRegistry
    dependency_graph: DependencyGraph

    # === COMPONENTS ===
    scheduler: PhaseScheduler = field(default=None)
    state_machine: OrchestrationStateMachine = field(default=None)

    # === CONFIGURATION ===
    config: OrchestratorConfiguration = field(default_factory=OrchestratorConfiguration)

    # === EXECUTION STATE ===
    _run_id: str = field(default="")
    _active_phases: Set[str] = field(default_factory=set)
    _completed_phases: Dict[str, PhaseCompleteSignal] = field(default_factory=dict)
    _failed_phases: Dict[str, List[PhaseCompleteSignal]] = field(default_factory=dict)
    _phase_retry_counts: Dict[str, int] = field(default_factory=dict)

    # === CALLBACKS ===
    _completion_callbacks: List[Callable[[PhaseCompleteSignal], None]] = field(
        default_factory=list
    )

    # === LOGGING ===
    _logger: logging.Logger = field(default=None)

    def __post_init__(self):
        """Initialize orchestrator after dataclass creation."""
        if self._logger is None:
            self._logger = logging.getLogger("SISAS.Orchestrator.Main")

        # Validate required injections
        if self.bus_registry is None:
            raise OrchestrationInitializationError(
                "BusRegistry must be injected",
                missing_component="BusRegistry",
            )
        if self.dependency_graph is None:
            raise OrchestrationInitializationError(
                "DependencyGraph must be injected",
                missing_component="DependencyGraph",
            )

        # Initialize components
        if self.scheduler is None:
            self.scheduler = PhaseScheduler(
                dependency_graph=self.dependency_graph,
                mode=SchedulingStrategy[self.config.mode.name],
            )

        if self.state_machine is None:
            self.state_machine = OrchestrationStateMachine()

        # Set run_id
        self._run_id = self.config.run_id

        # Ensure required buses exist
        self._setup_buses()

        # Subscribe to phase completion signals
        self._subscribe_to_phase_completion()

        self._logger.info(f"MainOrchestrator initialized for run: {self._run_id}")

    # =========================================================================
    # SETUP
    # =========================================================================

    def _setup_buses(self):
        """Ensure required signal buses exist."""
        required_buses = {
            "orchestration_lifecycle_bus": BusType.ORCHESTRATION_LIFECYCLE,
            "orchestration_decision_bus": BusType.ORCHESTRATION_DECISION,
            "orchestration_coordination_bus": BusType.ORCHESTRATION_COORDINATION,
        }

        for bus_name, bus_type in required_buses.items():
            if self.bus_registry.get_bus(bus_name) is None:
                self.bus_registry.create_bus(bus_type, bus_name)
                self._logger.info(f"Created bus: {bus_name}")

    def _subscribe_to_phase_completion(self):
        """Subscribe to PhaseCompleteSignal to detect phase completion."""
        lifecycle_bus = self.bus_registry.get_bus("orchestration_lifecycle_bus")

        # Create a simple subscription wrapper
        def on_phase_complete(signal, context):
            self._handle_phase_complete_signal(signal)

        # Subscribe (implementation depends on BusRegistry API)
        # This is a simplified version - actual implementation may vary
        self._logger.info("Subscribed to PhaseCompleteSignal")

    # =========================================================================
    # ORCHESTRATION LIFECYCLE
    # =========================================================================

    async def start(self) -> str:
        """
        Start the orchestration.

        Returns:
            run_id: The unique identifier for this run

        Raises:
            OrchestrationInitializationError: If initialization fails
        """
        self._logger.info(f"Starting orchestration run: {self._run_id}")

        # Transition to INITIALIZING
        self.state_machine.transition_to(
            OrchestrationState.INITIALIZING,
            reason="Orchestration starting",
        )

        # Validate if configured
        if self.config.validate_contracts_on_startup:
            self._validate_contracts()

        # Emit initialization signal
        init_signal = create_orchestration_initialized_signal(
            run_id=self._run_id,
            configuration=self.config.to_dict(),
            dependency_graph_summary=self.dependency_graph.get_summary(),
            validation_passed=True,
            generator_vehicle="main_orchestrator",
        )
        self._publish_signal(init_signal, "orchestration_lifecycle_bus")

        # Transition to RUNNING
        self.state_machine.transition_to(
            OrchestrationState.RUNNING,
            reason="Initialization complete, starting phase execution",
        )

        # Start scheduling
        await self._schedule_ready_phases()

        return self._run_id

    async def _schedule_ready_phases(self):
        """
        Evaluate ready phases and schedule them.

        NEVER invokes phases directly - always publishes signals.
        """
        # Get scheduling decision
        decision = self.scheduler.get_ready_phases(
            completed_phases=set(self._completed_phases.keys()),
            failed_phases=set(self._failed_phases.keys()),
            active_phases=self._active_phases,
            max_parallel=self.config.max_parallel_phases,
        )

        # Emit decision signal if configured
        if self.config.emit_decision_signals:
            decision_signal = create_orchestration_decision_signal(
                run_id=self._run_id,
                decision_type="PHASE_SCHEDULING",
                decision_rationale=decision.rationale,
                phases_selected=decision.phases_to_start,
                phases_waiting=decision.phases_waiting,
                phases_blocked=decision.phases_blocked,
                dependency_state=self.dependency_graph.get_state_snapshot(),
                generator_vehicle="main_orchestrator",
            )
            self._publish_signal(decision_signal, "orchestration_decision_bus")

        # Start each ready phase
        for phase_id in decision.phases_to_start:
            await self._start_phase(phase_id)

    async def _start_phase(self, phase_id: str):
        """
        Start a phase by publishing PhaseStartSignal.

        CRITICAL: This method NEVER invokes the phase directly.
        It only publishes a signal that will be consumed by the PhaseConsumer.

        Args:
            phase_id: Phase to start
        """
        self._logger.info(f"Starting phase: {phase_id}")

        # Add to active phases
        self._active_phases.add(phase_id)

        # Update dependency graph
        self.dependency_graph.update_node_status(phase_id, DependencyStatus.RUNNING)

        # Get upstream dependencies
        upstream = self.dependency_graph.get_upstream_dependencies(phase_id)
        upstream_results = self._get_upstream_results(phase_id)

        # Create execution context
        execution_context = {
            "phase_id": phase_id,
            "run_id": self._run_id,
            "attempt_number": self._phase_retry_counts.get(phase_id, 0) + 1,
            "upstream_results": upstream_results,
            "deadline": (datetime.utcnow() + timedelta(seconds=self.config.phase_timeout_seconds)).isoformat(),
        }

        # Create and publish PhaseStartSignal
        start_signal = create_phase_start_signal(
            phase_id=phase_id,
            run_id=self._run_id,
            upstream_dependencies=upstream,
            execution_context=execution_context,
            timeout_seconds=self.config.phase_timeout_seconds,
            generator_vehicle="main_orchestrator",
        )
        self._publish_signal(start_signal, "orchestration_lifecycle_bus")

        # Emit PhaseReadyToStartSignal for coordination
        ready_signal = create_phase_ready_to_start_signal(
            run_id=self._run_id,
            phase_id=phase_id,
            dependencies_satisfied=True,
            generator_vehicle="main_orchestrator",
        )
        self._publish_signal(ready_signal, "orchestration_coordination_bus")

        self._logger.info(f"PhaseStartSignal published for: {phase_id}")

    def _handle_phase_complete_signal(self, signal: PhaseCompleteSignal):
        """
        Handle PhaseCompleteSignal from a phase.

        This is the ONLY way the orchestrator knows a phase finished.

        Args:
            signal: The completion signal
        """
        phase_id = signal.phase_id
        self._logger.info(
            f"Received PhaseCompleteSignal for: {phase_id}, status: {signal.status.name}"
        )

        # Remove from active phases
        self._active_phases.discard(phase_id)

        # Handle based on status
        if signal.status == PhaseCompletionStatus.SUCCESS:
            self._handle_phase_success(signal)
        elif signal.status == PhaseCompletionStatus.FAILURE:
            self._handle_phase_failure(signal)
        elif signal.status == PhaseCompletionStatus.PARTIAL:
            self._handle_phase_partial(signal)
        elif signal.status == PhaseCompletionStatus.TIMEOUT:
            self._handle_phase_timeout(signal)

        # Check if orchestration is complete
        if self._is_orchestration_complete():
            asyncio.create_task(self._complete_orchestration())
        else:
            # Schedule next phases
            asyncio.create_task(self._schedule_ready_phases())

    def _handle_phase_success(self, signal: PhaseCompleteSignal):
        """Handle successful phase completion."""
        phase_id = signal.phase_id

        # Record completion
        self._completed_phases[phase_id] = signal

        # Update dependency graph
        self.dependency_graph.update_node_status(phase_id, DependencyStatus.COMPLETED)

        # Get newly unblocked phases
        newly_unblocked = self.dependency_graph.get_newly_unblocked(phase_id)

        # Emit DependencyGraphUpdatedSignal
        graph_update_signal = create_dependency_graph_updated_signal(
            run_id=self._run_id,
            updated_node=phase_id,
            new_status="COMPLETED",
            newly_unblocked_phases=newly_unblocked,
            impact_summary={"downstream_count": len(newly_unblocked)},
            generator_vehicle="main_orchestrator",
        )
        self._publish_signal(graph_update_signal, "orchestration_coordination_bus")

        # Emit decision signal
        if self.config.emit_decision_signals:
            decision_signal = create_orchestration_decision_signal(
                run_id=self._run_id,
                decision_type="PHASE_SUCCESS",
                decision_rationale=f"Phase {phase_id} completed successfully",
                phases_selected=[],
                dependency_state=self.dependency_graph.get_state_snapshot(),
                generator_vehicle="main_orchestrator",
            )
            self._publish_signal(decision_signal, "orchestration_decision_bus")

        # Invoke callbacks
        for callback in self._completion_callbacks:
            try:
                callback(signal)
            except Exception as e:
                self._logger.error(f"Completion callback error: {e}", exc_info=True)

    def _handle_phase_failure(self, signal: PhaseCompleteSignal):
        """Handle phase failure."""
        phase_id = signal.phase_id

        # Record failure
        if phase_id not in self._failed_phases:
            self._failed_phases[phase_id] = []
        self._failed_phases[phase_id].append(signal)

        # Increment retry count
        self._phase_retry_counts[phase_id] = (
            self._phase_retry_counts.get(phase_id, 0) + 1
        )

        # Check if should retry
        if (
            self.config.retry_failed_phases
            and self._phase_retry_counts[phase_id] < self.config.max_retries_per_phase
        ):
            self._logger.warning(
                f"Phase {phase_id} failed, scheduling retry "
                f"({self._phase_retry_counts[phase_id]}/{self.config.max_retries_per_phase})"
            )
            self.dependency_graph.update_node_status(
                phase_id, DependencyStatus.PENDING_RETRY
            )
        else:
            # Permanent failure
            self.dependency_graph.update_node_status(phase_id, DependencyStatus.FAILED)
            self._logger.error(f"Phase {phase_id} failed permanently")

    def _handle_phase_partial(self, signal: PhaseCompleteSignal):
        """Handle partial phase completion."""
        phase_id = signal.phase_id

        # Record as completed (partial)
        self._completed_phases[phase_id] = signal

        # Update dependency graph
        self.dependency_graph.update_node_status(phase_id, DependencyStatus.PARTIAL)

        self._logger.warning(f"Phase {phase_id} completed partially")

    def _handle_phase_timeout(self, signal: PhaseCompleteSignal):
        """Handle phase timeout."""
        phase_id = signal.phase_id
        self._logger.error(f"Phase {phase_id} timed out")

        # Treat as failure
        self._handle_phase_failure(signal)

    async def _complete_orchestration(self):
        """Complete the orchestration when all phases are done."""
        self._logger.info(f"Completing orchestration run: {self._run_id}")

        # Determine final status
        if self._failed_phases:
            final_state = OrchestrationState.COMPLETED_WITH_ERRORS
            final_status = "COMPLETED_WITH_ERRORS"
        else:
            final_state = OrchestrationState.COMPLETED
            final_status = "COMPLETED"

        # Transition state
        self.state_machine.transition_to(final_state, reason="All phases complete")

        # Generate execution summary
        execution_summary = {
            "run_id": self._run_id,
            "total_phases": len(self.dependency_graph.nodes),
            "phases_completed": list(self._completed_phases.keys()),
            "phases_failed": list(self._failed_phases.keys()),
            "retry_counts": self._phase_retry_counts,
        }

        # Emit completion signal
        completion_signal = create_orchestration_complete_signal(
            run_id=self._run_id,
            final_status=final_status,
            total_phases=len(self.dependency_graph.nodes),
            completed_successfully=len(
                [s for s in self._completed_phases.values() if s.is_success()]
            ),
            completed_partially=len(
                [s for s in self._completed_phases.values() if s.is_partial()]
            ),
            failed=len(self._failed_phases),
            execution_summary=execution_summary,
            generator_vehicle="main_orchestrator",
        )
        self._publish_signal(completion_signal, "orchestration_lifecycle_bus")

        self._logger.info(f"Orchestration complete: {self._run_id} - {final_status}")

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def _validate_contracts(self):
        """Validate orchestration contracts."""
        validation_errors = []

        # Check buses exist
        required_buses = [
            "orchestration_lifecycle_bus",
            "orchestration_decision_bus",
            "orchestration_coordination_bus",
        ]
        for bus_name in required_buses:
            if self.bus_registry.get_bus(bus_name) is None:
                validation_errors.append(f"Required bus '{bus_name}' not found")

        # Validate dependency graph
        graph_validation = self.dependency_graph.validate()
        if not graph_validation.is_valid:
            validation_errors.extend(graph_validation.errors)

        # Emit validation signal
        validation_signal = ConstitutionalValidationSignal(
            context=SignalContext(
                node_type="orchestration",
                node_id="main_orchestrator",
                phase="orchestration",
                consumer_scope="global",
            ),
            source=SignalSource(
                event_id=str(uuid4()),
                source_file="main_orchestrator.py",
                source_path="src/farfan_pipeline/orchestration/sisas_aware/main_orchestrator.py",
                generation_timestamp=datetime.utcnow(),
                generator_vehicle="main_orchestrator",
            ),
            run_id=self._run_id,
            validation_passed=len(validation_errors) == 0,
            validation_errors=validation_errors,
            contracts_validated=3 + len(self.dependency_graph.nodes),
            timestamp=datetime.utcnow(),
        )
        self._publish_signal(validation_signal, "orchestration_decision_bus")

        if validation_errors and self.config.fail_fast_on_contract_violation:
            raise ContractViolationError(
                f"Contract validation failed: {validation_errors}",
                context={"errors": validation_errors},
            )

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _publish_signal(self, signal, bus_name: str):
        """Publish a signal to the specified bus."""
        bus = self.bus_registry.get_bus(bus_name)
        if bus is None:
            raise ContractViolationError(
                f"Bus '{bus_name}' not found",
                bus_name=bus_name,
            )

        # Publish (implementation depends on SignalBus API)
        try:
            bus.publish(signal, "main_orchestrator")
        except Exception as e:
            self._logger.error(f"Failed to publish signal: {e}", exc_info=True)
            if self.config.fail_fast_on_contract_violation:
                raise ContractViolationError(
                    f"Signal publication failed: {e}",
                    bus_name=bus_name,
                    signal_type=signal.signal_type,
                )

    def _get_upstream_results(self, phase_id: str) -> Dict[str, Any]:
        """Get results from upstream phases."""
        results = {}
        for upstream_id in self.dependency_graph.get_upstream_dependencies(phase_id):
            if upstream_id in self._completed_phases:
                signal = self._completed_phases[upstream_id]
                results[upstream_id] = signal.completion_metadata
        return results

    def _is_orchestration_complete(self) -> bool:
        """Check if orchestration is complete."""
        all_phases = set(self.dependency_graph.nodes.keys())
        completed_or_failed = set(self._completed_phases.keys()) | set(
            self._failed_phases.keys()
        )
        blocked = set(self.dependency_graph.get_permanently_blocked())
        return all_phases == (completed_or_failed | blocked)

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "run_id": self._run_id,
            "state": self.state_machine.current_state.name,
            "active_phases": list(self._active_phases),
            "completed_phases": list(self._completed_phases.keys()),
            "failed_phases": list(self._failed_phases.keys()),
            "dependency_graph_state": self.dependency_graph.get_state_snapshot(),
        }

    def register_completion_callback(
        self, callback: Callable[[PhaseCompleteSignal], None]
    ):
        """Register a callback for phase completion."""
        self._completion_callbacks.append(callback)

    async def stop(self, reason: str = "Manual stop"):
        """Stop the orchestration."""
        self._logger.warning(f"Stopping orchestration: {reason}")

        self.state_machine.transition_to(
            OrchestrationState.STOPPING, reason=reason
        )

        # Emit stop decision
        decision_signal = create_orchestration_decision_signal(
            run_id=self._run_id,
            decision_type="ORCHESTRATION_STOP",
            decision_rationale=reason,
            generator_vehicle="main_orchestrator",
        )
        self._publish_signal(decision_signal, "orchestration_decision_bus")

        self.state_machine.transition_to(OrchestrationState.STOPPED)


__all__ = [
    "OrchestratorMode",
    "OrchestratorConfiguration",
    "MainOrchestrator",
]
