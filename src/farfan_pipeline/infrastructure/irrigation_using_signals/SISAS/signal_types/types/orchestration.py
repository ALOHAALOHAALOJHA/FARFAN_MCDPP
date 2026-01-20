"""
SISAS Orchestration Signal Types

Signal types for phase execution and orchestration events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
import uuid


class PhaseCompletionStatus(Enum):
    """Status of phase completion."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class OrchestrationDecisionType(Enum):
    """Types of orchestration decisions."""
    PROCEED = "proceed"
    ABORT = "abort"
    RETRY = "retry"
    SKIP = "skip"
    WAIT = "wait"


class OrchestrationFinalStatus(Enum):
    """Final status of orchestration."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ABORTED = "aborted"


class BlockingStatus(Enum):
    """Blocking status for phases."""
    BLOCKED = "blocked"
    UNBLOCKED = "unblocked"
    DEPENDENCIES_MET = "dependencies_met"


@dataclass
class PhaseStartSignal:
    """Signal emitted when a phase starts."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "PHASE_START"
    phase_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseCompleteSignal:
    """Signal emitted when a phase completes."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "PHASE_COMPLETE"
    phase_id: str = ""
    status: PhaseCompletionStatus = PhaseCompletionStatus.COMPLETED
    execution_time_s: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseProgressSignal:
    """Signal emitted during phase execution with progress updates."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "PHASE_PROGRESS"
    phase_id: str = ""
    progress_pct: float = 0.0
    current_step: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseRetrySignal:
    """Signal emitted when a phase retry is triggered."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "PHASE_RETRY"
    phase_id: str = ""
    retry_count: int = 0
    max_retries: int = 3
    reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationInitializedSignal:
    """Signal emitted when orchestration is initialized."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "ORCHESTRATION_INITIALIZED"
    execution_id: str = ""
    config_hash: str = ""
    phases_to_execute: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationCompleteSignal:
    """Signal emitted when orchestration completes."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "ORCHESTRATION_COMPLETE"
    execution_id: str = ""
    final_status: OrchestrationFinalStatus = OrchestrationFinalStatus.SUCCESS
    phases_completed: List[str] = field(default_factory=list)
    phases_failed: List[str] = field(default_factory=list)
    total_execution_time_s: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationDecisionSignal:
    """Signal emitted when an orchestration decision is made."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "ORCHESTRATION_DECISION"
    decision_type: OrchestrationDecisionType = OrchestrationDecisionType.PROCEED
    phase_id: str = ""
    reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstitutionalValidationSignal:
    """Signal emitted for constitutional validation results."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "CONSTITUTIONAL_VALIDATION"
    valid: bool = True
    violations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyGraphLoadedSignal:
    """Signal emitted when dependency graph is loaded."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "DEPENDENCY_GRAPH_LOADED"
    node_count: int = 0
    edge_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseReadyToStartSignal:
    """Signal emitted when a phase is ready to start."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "PHASE_READY_TO_START"
    phase_id: str = ""
    dependencies_satisfied: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyGraphUpdatedSignal:
    """Signal emitted when dependency graph is updated."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "DEPENDENCY_GRAPH_UPDATED"
    updated_node: str = ""
    new_status: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseBlockedSignal:
    """Signal emitted when a phase is blocked."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "PHASE_BLOCKED"
    phase_id: str = ""
    blocking_status: BlockingStatus = BlockingStatus.BLOCKED
    blocked_by: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelExecutionLimitSignal:
    """Signal emitted when parallel execution limit is reached."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "PARALLEL_EXECUTION_LIMIT"
    current_parallel: int = 0
    max_parallel: int = 0
    queued_phases: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseDependencySatisfiedSignal:
    """Signal emitted when a phase dependency is satisfied."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "PHASE_DEPENDENCY_SATISFIED"
    phase_id: str = ""
    dependency_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)


# Factory functions for creating signals
def create_phase_start_signal(phase_id: str, **kwargs) -> PhaseStartSignal:
    """Create a phase start signal."""
    return PhaseStartSignal(phase_id=phase_id, payload=kwargs)


def create_phase_complete_signal(
    phase_id: str,
    status: PhaseCompletionStatus = PhaseCompletionStatus.COMPLETED,
    execution_time_s: float = 0.0,
    **kwargs
) -> PhaseCompleteSignal:
    """Create a phase complete signal."""
    return PhaseCompleteSignal(
        phase_id=phase_id,
        status=status,
        execution_time_s=execution_time_s,
        payload=kwargs
    )


def create_orchestration_initialized_signal(
    execution_id: str,
    phases_to_execute: List[str],
    **kwargs
) -> OrchestrationInitializedSignal:
    """Create an orchestration initialized signal."""
    return OrchestrationInitializedSignal(
        execution_id=execution_id,
        phases_to_execute=phases_to_execute,
        payload=kwargs
    )


def create_orchestration_decision_signal(
    decision_type: OrchestrationDecisionType,
    phase_id: str = "",
    reason: str = "",
    **kwargs
) -> OrchestrationDecisionSignal:
    """Create an orchestration decision signal."""
    return OrchestrationDecisionSignal(
        decision_type=decision_type,
        phase_id=phase_id,
        reason=reason,
        payload=kwargs
    )


def create_orchestration_complete_signal(
    execution_id: str,
    final_status: OrchestrationFinalStatus,
    phases_completed: List[str],
    phases_failed: List[str],
    total_execution_time_s: float = 0.0,
    **kwargs
) -> OrchestrationCompleteSignal:
    """Create an orchestration complete signal."""
    return OrchestrationCompleteSignal(
        execution_id=execution_id,
        final_status=final_status,
        phases_completed=phases_completed,
        phases_failed=phases_failed,
        total_execution_time_s=total_execution_time_s,
        payload=kwargs
    )


def create_phase_ready_to_start_signal(
    phase_id: str,
    dependencies_satisfied: List[str],
    **kwargs
) -> PhaseReadyToStartSignal:
    """Create a phase ready to start signal."""
    return PhaseReadyToStartSignal(
        phase_id=phase_id,
        dependencies_satisfied=dependencies_satisfied,
        payload=kwargs
    )


def create_dependency_graph_updated_signal(
    updated_node: str,
    new_status: str,
    **kwargs
) -> DependencyGraphUpdatedSignal:
    """Create a dependency graph updated signal."""
    return DependencyGraphUpdatedSignal(
        updated_node=updated_node,
        new_status=new_status,
        payload=kwargs
    )
