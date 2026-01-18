"""
SISAS-Aware Orchestration Core Module

This module provides the core orchestration infrastructure including:
- State Machine: Lifecycle state management with transition validation
- Dependency Graph: Phase dependency management with DAG structure
- Phase Scheduler: Scheduling logic for phase execution with multiple strategies

This consolidated module provides complete orchestration infrastructure
in a single, comprehensive file for production deployment.

Architecture:
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATION CORE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ State Machine   │  │ Dependency      │  │ Phase Scheduler │             │
│  │                 │  │ Graph           │  │                 │             │
│  │ - IDLE          │  │ - Nodes         │  │ - SEQUENTIAL    │             │
│  │ - INITIALIZING  │  │ - Edges         │  │ - PARALLEL      │             │
│  │ - RUNNING       │  │ - Validation    │  │ - HYBRID        │             │
│  │ - COMPLETED     │  │ - Propagation   │  │ - PRIORITY      │             │
│  │ - STOPPED       │  │ - Status mgmt   │  │ - Decision      │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple


logger = logging.getLogger("SISAS.Orchestration.Core")


# =============================================================================
# EXCEPTIONS
# =============================================================================

class OrchestrationError(Exception):
    """Base exception for all orchestration errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code or "ORCHESTRATION_ERROR"
        self.context = context or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }


class DependencyResolutionError(OrchestrationError):
    """Raised when dependency graph resolution fails."""

    def __init__(
        self,
        message: str,
        phase_id: Optional[str] = None,
        dependency_chain: Optional[List[str]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        self.phase_id = phase_id
        self.dependency_chain = dependency_chain or []
        ctx = context or {}
        if phase_id:
            ctx["phase_id"] = phase_id
        if dependency_chain:
            ctx["dependency_chain"] = dependency_chain
        super().__init__(
            message,
            error_code="DEPENDENCY_RESOLUTION_ERROR",
            context=ctx,
        )


class SchedulingError(OrchestrationError):
    """Raised when phase scheduling fails."""

    def __init__(
        self,
        message: str,
        scheduling_strategy: Optional[str] = None,
        phases_in_conflict: Optional[List[str]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        self.scheduling_strategy = scheduling_strategy
        self.phases_in_conflict = phases_in_conflict or []
        ctx = context or {}
        if scheduling_strategy:
            ctx["scheduling_strategy"] = scheduling_strategy
        if phases_in_conflict:
            ctx["phases_in_conflict"] = phases_in_conflict
        super().__init__(
            message,
            error_code="SCHEDULING_ERROR",
            context=ctx,
        )


class StateTransitionError(OrchestrationError):
    """Raised when an invalid state transition is attempted."""

    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        target_state: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        self.current_state = current_state
        self.target_state = target_state
        ctx = context or {}
        if current_state:
            ctx["current_state"] = current_state
        if target_state:
            ctx["target_state"] = target_state
        super().__init__(
            message,
            error_code="STATE_TRANSITION_ERROR",
            context=ctx,
        )


# =============================================================================
# STATE MACHINE
# =============================================================================

class OrchestrationState(Enum):
    """
    States of the orchestration lifecycle.

    State Transition Diagram:
    ┌─────────────────────────────────────────────────────────────────┐
    │                                                                 │
    │   ┌──────┐     ┌─────────────┐     ┌──────┐                   │
    │   │ IDLE │ ──► │INITIALIZING │ ──► │RUNNING│                   │
    │   └──────┘     └─────────────┘     └──┬───┘                   │
    │                                       │                        │
    │          ┌────────────────────────────┼──────────────────┐    │
    │          ▼                            ▼                  ▼    │
    │    ┌─────────┐              ┌──────────────┐    ┌───────┐  │
    │    │STOPPED  │              │COMPLETED_WITH│    │COMPLETED│  │
    │    └─────────┘              │   _ERRORS    │    └───────┘  │
    │                             └──────────────┘               │
    └─────────────────────────────────────────────────────────────────┘
    """

    # Initial state - orchestrator created but not started
    IDLE = auto()

    # Initializing - setting up contracts, validating dependencies
    INITIALIZING = auto()

    # Running - actively orchestrating phases
    RUNNING = auto()

    # Completed successfully - all phases finished without errors
    COMPLETED = auto()

    # Completed with errors - some phases failed but orchestration finished
    COMPLETED_WITH_ERRORS = auto()

    # Stopped - manually stopped or error stopped orchestration
    STOPPED = auto()

    # Stopping - in the process of stopping (intermediate state)
    STOPPING = auto()


@dataclass
class StateTransition:
    """Represents a single state transition in the orchestration lifecycle."""

    from_state: OrchestrationState
    to_state: OrchestrationState
    timestamp: datetime = field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_state": self.from_state.name,
            "to_state": self.to_state.name,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "metadata": self.metadata,
        }


# Valid state transitions
VALID_TRANSITIONS: Dict[OrchestrationState, Set[OrchestrationState]] = {
    OrchestrationState.IDLE: {OrchestrationState.INITIALIZING},
    OrchestrationState.INITIALIZING: {OrchestrationState.RUNNING, OrchestrationState.STOPPING},
    OrchestrationState.RUNNING: {
        OrchestrationState.COMPLETED,
        OrchestrationState.COMPLETED_WITH_ERRORS,
        OrchestrationState.STOPPING,
    },
    OrchestrationState.STOPPING: {OrchestrationState.STOPPED},
    OrchestrationState.COMPLETED: set(),  # Terminal state
    OrchestrationState.COMPLETED_WITH_ERRORS: set(),  # Terminal state
    OrchestrationState.STOPPED: set(),  # Terminal state
}


@dataclass
class OrchestrationStateMachine:
    """
    State machine for orchestration lifecycle management.

    Responsibilities:
    - Enforce valid state transitions
    - Track state transition history
    - Provide current state queries
    - Emit state change events

    Usage:
        machine = OrchestrationStateMachine()
        machine.transition_to(OrchestrationState.INITIALIZING, reason="Starting initialization")
        assert machine.current_state == OrchestrationState.INITIALIZING
    """

    # Current state
    current_state: OrchestrationState = field(default=OrchestrationState.IDLE)

    # Transition history
    _transition_history: List[StateTransition] = field(default_factory=list)

    # Whether to allow transitions from terminal states (for testing/debugging)
    allow_terminal_transition: bool = False

    # Callbacks for state transitions
    _transition_callbacks: Dict[OrchestrationState, List[callable]] = field(
        default_factory=dict
    )

    # Logging
    _logger: logging.Logger = field(default=None)

    def __post_init__(self):
        if self._logger is None:
            self._logger = logging.getLogger("SISAS.Orchestration.StateMachine")

    def transition_to(
        self,
        new_state: OrchestrationState,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateTransition:
        """
        Transition to a new state.

        Args:
            new_state: The target state
            reason: Optional reason for the transition
            metadata: Optional metadata to attach to the transition

        Returns:
            StateTransition: The recorded transition

        Raises:
            StateTransitionError: If the transition is invalid
        """
        # Validate transition
        if not self._is_valid_transition(new_state):
            raise StateTransitionError(
                message=f"Invalid state transition: {self.current_state.name} → {new_state.name}",
                current_state=self.current_state.name,
                target_state=new_state.name,
                context={
                    "valid_transitions": [
                        s.name for s in VALID_TRANSITIONS.get(self.current_state, set())
                    ]
                },
            )

        # Record transition
        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            reason=reason,
            metadata=metadata or {},
        )

        # Update state
        old_state = self.current_state
        self.current_state = new_state
        self._transition_history.append(transition)

        # Log transition
        self._logger.info(
            f"State transition: {old_state.name} → {new_state.name}",
            extra={
                "reason": reason,
                "transition_number": len(self._transition_history),
            },
        )

        # Invoke callbacks for new state
        self._invoke_callbacks(new_state, transition)

        return transition

    def _is_valid_transition(self, new_state: OrchestrationState) -> bool:
        """
        Check if a transition is valid.

        Args:
            new_state: The target state

        Returns:
            bool: True if the transition is valid
        """
        # Same state is never valid (must use transition_to)
        if new_state == self.current_state:
            return False

        valid_targets = VALID_TRANSITIONS.get(self.current_state, set())

        # Terminal states normally can't transition out
        if self.current_state in {
            OrchestrationState.COMPLETED,
            OrchestrationState.COMPLETED_WITH_ERRORS,
            OrchestrationState.STOPPED,
        }:
            return self.allow_terminal_transition and new_state in valid_targets

        return new_state in valid_targets

    def register_callback(
        self, state: OrchestrationState, callback: callable[[StateTransition], None]
    ) -> None:
        """
        Register a callback to be invoked when entering a specific state.

        Args:
            state: The state to watch
            callback: Function to call with the StateTransition
        """
        if state not in self._transition_callbacks:
            self._transition_callbacks[state] = []
        self._transition_callbacks[state].append(callback)

    def _invoke_callbacks(self, state: OrchestrationState, transition: StateTransition) -> None:
        """
        Invoke all callbacks registered for a state.

        Args:
            state: The state that was entered
            transition: The transition that occurred
        """
        callbacks = self._transition_callbacks.get(state, [])
        for callback in callbacks:
            try:
                callback(transition)
            except Exception as e:
                self._logger.error(
                    f"State transition callback failed for state {state.name}: {e}",
                    exc_info=True,
                )

    def get_transition_history(self) -> List[Dict[str, Any]]:
        """
        Get the complete transition history.

        Returns:
            List[Dict[str, Any]]: All transitions in chronological order
        """
        return [t.to_dict() for t in self._transition_history]

    def get_current_state(self) -> OrchestrationState:
        """
        Get the current state.

        Returns:
            OrchestrationState: The current state
        """
        return self.current_state

    def is_terminal(self) -> bool:
        """
        Check if the current state is terminal.

        Returns:
            bool: True if in a terminal state
        """
        return self.current_state in {
            OrchestrationState.COMPLETED,
            OrchestrationState.COMPLETED_WITH_ERRORS,
            OrchestrationState.STOPPED,
        }

    def is_running(self) -> bool:
        """
        Check if the orchestration is currently running.

        Returns:
            bool: True if in RUNNING state
        """
        return self.current_state == OrchestrationState.RUNNING

    def can_start_phases(self) -> bool:
        """
        Check if phases can be started in the current state.

        Returns:
            bool: True if in RUNNING state
        """
        return self.current_state == OrchestrationState.RUNNING

    def get_valid_next_states(self) -> List[OrchestrationState]:
        """
        Get list of valid next states from current state.

        Returns:
            List[OrchestrationState]: Valid target states
        """
        return list(VALID_TRANSITIONS.get(self.current_state, set()))

    def reset(self) -> None:
        """
        Reset the state machine to IDLE.

        WARNING: This is primarily for testing. Production code should
        normally not reset state machines.
        """
        self.current_state = OrchestrationState.IDLE
        self._transition_history.clear()
        self._logger.warning("State machine reset to IDLE")

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the state machine to a dictionary.

        Returns:
            Dict[str, Any]: State machine representation
        """
        return {
            "current_state": self.current_state.name,
            "is_terminal": self.is_terminal(),
            "is_running": self.is_running(),
            "can_start_phases": self.can_start_phases(),
            "valid_next_states": [s.name for s in self.get_valid_next_states()],
            "transition_count": len(self._transition_history),
            "transitions": self.get_transition_history(),
        }


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================

class DependencyStatus(Enum):
    """Status of a node in the dependency graph."""

    # Phase is pending execution
    PENDING = auto()

    # Phase is ready to start (dependencies satisfied)
    READY = auto()

    # Phase is currently running
    RUNNING = auto()

    # Phase completed successfully
    COMPLETED = auto()

    # Phase completed partially (some tasks failed but can continue)
    PARTIAL = auto()

    # Phase failed, pending retry
    PENDING_RETRY = auto()

    # Phase failed permanently
    FAILED = auto()

    # Phase is blocked (dependencies not satisfied)
    BLOCKED = auto()

    # Phase is permanently blocked (upstream failure)
    PERMANENTLY_BLOCKED = auto()


@dataclass
class DependencyNode:
    """
    Represents a phase node in the dependency graph.

    Attributes:
        node_id: Unique identifier for the phase
        phase_id: Phase identifier (e.g., "PHASE_2")
        status: Current status of the phase
        upstream: Set of phase IDs that this phase depends on
        downstream: Set of phase IDs that depend on this phase
        config: Optional configuration for the phase
        metadata: Additional metadata about the phase
    """

    node_id: str
    phase_id: str
    status: DependencyStatus = DependencyStatus.PENDING
    upstream: Set[str] = field(default_factory=set)
    downstream: Set[str] = field(default_factory=set)
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0

    def __hash__(self) -> int:
        return hash(self.node_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DependencyNode):
            return False
        return self.node_id == other.node_id

    def is_terminal(self) -> bool:
        """Check if this node is in a terminal state."""
        return self.status in {
            DependencyStatus.COMPLETED,
            DependencyStatus.PARTIAL,
            DependencyStatus.FAILED,
            DependencyStatus.PERMANENTLY_BLOCKED,
        }

    def can_start(self) -> bool:
        """Check if this node can start execution."""
        return self.status == DependencyStatus.READY

    def is_blocking_downstream(self) -> bool:
        """Check if this node is blocking downstream phases."""
        return self.status in {
            DependencyStatus.PENDING,
            DependencyStatus.RUNNING,
            DependencyStatus.BLOCKED,
        }


@dataclass
class DependencyEdge:
    """
    Represents a dependency relationship between two phases.

    Attributes:
        from_node: Source phase ID
        to_node: Target phase ID (depends on from_node)
        edge_type: Type of dependency relationship
    """

    from_node: str
    to_node: str
    edge_type: str = "hard"  # "hard" or "soft" dependency

    def __hash__(self) -> int:
        return hash((self.from_node, self.to_node))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DependencyEdge):
            return False
        return self.from_node == other.from_node and self.to_node == other.to_node


@dataclass
class GraphValidationResult:
    """Result of validating the dependency graph."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)
    orphan_nodes: List[str] = field(default_factory=list)


@dataclass
class DependencyGraph:
    """
    Dependency graph for phase orchestration.

    Responsibilities:
    - Maintain phase nodes and their dependencies
    - Track status of each phase
    - Determine which phases are ready to execute
    - Detect circular dependencies
    - Calculate downstream impact of phase failures

    Usage:
        graph = DependencyGraph()
        graph.add_node("PHASE_1", phase_id="PHASE_1")
        graph.add_node("PHASE_2", phase_id="PHASE_2")
        graph.add_edge("PHASE_1", "PHASE_2")
        graph.update_node_status("PHASE_1", DependencyStatus.COMPLETED)
        ready = graph.get_ready_phases()
    """

    # Graph structure
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    edges: Set[DependencyEdge] = field(default_factory=set)

    # Adjacency lists for quick lookup
    _adjacency: Dict[str, Set[str]] = field(default_factory=dict)
    _reverse_adjacency: Dict[str, Set[str]] = field(default_factory=dict)

    # Logging
    _logger: logging.Logger = field(default=None)

    def __post_init__(self):
        if self._logger is None:
            self._logger = logging.getLogger("SISAS.Orchestration.DependencyGraph")

    # =========================================================================
    # GRAPH MODIFICATION
    # =========================================================================

    def add_node(
        self,
        node_id: str,
        phase_id: str,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DependencyNode:
        """
        Add a phase node to the graph.

        Args:
            node_id: Unique identifier for the node
            phase_id: Phase identifier
            config: Optional configuration
            metadata: Optional metadata

        Returns:
            DependencyNode: The created node
        """
        if node_id in self.nodes:
            self._logger.warning(f"Node {node_id} already exists, updating")
            node = self.nodes[node_id]
            if config:
                node.config.update(config)
            if metadata:
                node.metadata.update(metadata)
            return node

        node = DependencyNode(
            node_id=node_id,
            phase_id=phase_id,
            config=config or {},
            metadata=metadata or {},
        )

        self.nodes[node_id] = node
        self._adjacency[node_id] = set()
        self._reverse_adjacency[node_id] = set()

        self._logger.debug(f"Added node: {node_id} (phase: {phase_id})")
        return node

    def add_edge(
        self, from_node: str, to_node: str, edge_type: str = "hard"
    ) -> DependencyEdge:
        """
        Add a dependency edge between two nodes.

        Args:
            from_node: Source node (must complete first)
            to_node: Target node (depends on from_node)
            edge_type: Type of dependency ("hard" or "soft")

        Returns:
            DependencyEdge: The created edge

        Raises:
            DependencyResolutionError: If nodes don't exist or edge creates a cycle
        """
        if from_node not in self.nodes:
            raise DependencyResolutionError(
                f"Source node {from_node} does not exist",
                phase_id=from_node,
            )
        if to_node not in self.nodes:
            raise DependencyResolutionError(
                f"Target node {to_node} does not exist",
                phase_id=to_node,
            )

        edge = DependencyEdge(from_node=from_node, to_node=to_node, edge_type=edge_type)

        # Check for cycles
        if self._would_create_cycle(edge):
            raise DependencyResolutionError(
                f"Edge {from_node} -> {to_node} would create a circular dependency",
                phase_id=to_node,
                dependency_chain=self._get_cycle_path(edge),
            )

        # Add edge
        self.edges.add(edge)
        self._adjacency[from_node].add(to_node)
        self._reverse_adjacency[to_node].add(from_node)

        # Update nodes
        self.nodes[from_node].downstream.add(to_node)
        self.nodes[to_node].upstream.add(from_node)

        # Update target node status
        self._update_node_readiness(to_node)

        self._logger.debug(f"Added edge: {from_node} -> {to_node}")
        return edge

    def _would_create_cycle(self, new_edge: DependencyEdge) -> bool:
        """Check if adding an edge would create a cycle."""
        visited: Set[str] = set()
        path: List[str] = []

        def has_cycle(node: str) -> bool:
            visited.add(node)
            path.append(node)

            for neighbor in self._adjacency.get(node, set()):
                if neighbor == new_edge.from_node:
                    return True  # Found cycle back to start
                if neighbor not in visited and has_cycle(neighbor):
                    return True

            path.pop()
            return False

        return has_cycle(new_edge.to_node)

    def _get_cycle_path(self, edge: DependencyEdge) -> List[str]:
        """Get the cycle path that would be created."""
        path = [edge.from_node]
        current = edge.to_node

        while current != edge.from_node and current in self.nodes:
            path.append(current)
            # Get first upstream
            upstream = list(self._reverse_adjacency.get(current, set()))
            if not upstream:
                break
            current = upstream[0]

        return path

    # =========================================================================
    # STATUS MANAGEMENT
    # =========================================================================

    def update_node_status(
        self,
        node_id: str,
        new_status: DependencyStatus,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update the status of a node.

        Args:
            node_id: Node to update
            new_status: New status
            metadata: Optional metadata to attach
        """
        if node_id not in self.nodes:
            self._logger.warning(f"Node {node_id} not found, cannot update status")
            return

        node = self.nodes[node_id]
        old_status = node.status
        node.status = new_status

        if metadata:
            node.metadata.update(metadata)

        # Track timing
        if new_status == DependencyStatus.RUNNING and node.started_at is None:
            node.started_at = datetime.utcnow()
        elif new_status in {
            DependencyStatus.COMPLETED,
            DependencyStatus.PARTIAL,
            DependencyStatus.FAILED,
            DependencyStatus.PERMANENTLY_BLOCKED,
        }:
            node.completed_at = datetime.utcnow()

        self._logger.info(
            f"Node {node_id} status: {old_status.name} → {new_status.name}"
        )

        # Update downstream nodes
        self._propagate_status_change(node_id, new_status)

    def _update_node_readiness(self, node_id: str) -> None:
        """
        Update whether a node is ready to start based on upstream status.

        Args:
            node_id: Node to check
        """
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]

        # Check if all upstream are completed
        all_upstream_complete = all(
            self.nodes[upstream].status == DependencyStatus.COMPLETED
            for upstream in node.upstream
            if upstream in self.nodes
        )

        if all_upstream_complete and node.status == DependencyStatus.PENDING:
            node.status = DependencyStatus.READY
        elif not all_upstream_complete and node.status == DependencyStatus.READY:
            node.status = DependencyStatus.BLOCKED

    def _propagate_status_change(self, node_id: str, new_status: DependencyStatus) -> None:
        """
        Propagate status changes to downstream nodes.

        Args:
            node_id: Node that changed
            new_status: New status
        """
        for downstream_id in self._adjacency.get(node_id, set()):
            if new_status == DependencyStatus.COMPLETED:
                self._update_node_readiness(downstream_id)
            elif new_status in {
                DependencyStatus.FAILED,
                DependencyStatus.PERMANENTLY_BLOCKED,
            }:
                # Check if this is a hard dependency
                edge = self._get_edge(node_id, downstream_id)
                if edge and edge.edge_type == "hard":
                    self.update_node_status(
                        downstream_id, DependencyStatus.PERMANENTLY_BLOCKED
                    )

    # =========================================================================
    # QUERIES
    # =========================================================================

    def get_ready_phases(self) -> List[str]:
        """
        Get all phases that are ready to start.

        Returns:
            List[str]: Node IDs of ready phases
        """
        return [
            node_id
            for node_id, node in self.nodes.items()
            if node.status == DependencyStatus.READY
        ]

    def get_upstream_dependencies(self, node_id: str) -> List[str]:
        """
        Get upstream dependencies for a node.

        Args:
            node_id: Node to query

        Returns:
            List[str]: Upstream node IDs
        """
        return list(self.nodes.get(node_id, DependencyNode("", "")).upstream)

    def get_downstream_dependents(self, node_id: str) -> List[str]:
        """
        Get downstream dependents of a node.

        Args:
            node_id: Node to query

        Returns:
            List[str]: Downstream node IDs
        """
        return list(self._adjacency.get(node_id, set()))

    def get_newly_unblocked(self, node_id: str) -> List[str]:
        """
        Get downstream nodes that became unblocked by a node completion.

        Args:
            node_id: The node that completed

        Returns:
            List[str]: Newly unblocked node IDs
        """
        unblocked = []
        for downstream_id in self._adjacency.get(node_id, set()):
            if self.nodes[downstream_id].status == DependencyStatus.READY:
                unblocked.append(downstream_id)
        return unblocked

    def get_permanently_blocked(self) -> List[str]:
        """
        Get all permanently blocked nodes.

        Returns:
            List[str]: Permanently blocked node IDs
        """
        return [
            node_id
            for node_id, node in self.nodes.items()
            if node.status == DependencyStatus.PERMANENTLY_BLOCKED
        ]

    def get_node_config(self, node_id: str) -> Dict[str, Any]:
        """
        Get configuration for a node.

        Args:
            node_id: Node to query

        Returns:
            Dict[str, Any]: Node configuration
        """
        return self.nodes.get(node_id, DependencyNode("", "")).config

    def get_state_snapshot(self) -> Dict[str, str]:
        """
        Get a snapshot of all node states.

        Returns:
            Dict[str, str]: Mapping of node_id to status name
        """
        return {
            node_id: node.status.name for node_id, node in self.nodes.items()
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the graph.

        Returns:
            Dict[str, Any]: Graph summary
        """
        status_counts = {}
        for node in self.nodes.values():
            status = node.status.name
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "status_counts": status_counts,
            "ready_phases": len(self.get_ready_phases()),
            "blocked_phases": len(
                [n for n in self.nodes.values() if n.status == DependencyStatus.BLOCKED]
            ),
        }

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def validate(self) -> GraphValidationResult:
        """
        Validate the dependency graph.

        Returns:
            GraphValidationResult: Validation result
        """
        errors = []
        warnings = []
        cycles = []
        orphans = []

        # Check for cycles
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self._adjacency.get(node, set()):
                if neighbor not in visited:
                    if dfs_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                dfs_cycle(node_id)

        if cycles:
            errors.append(f"Found {len(cycles)} circular dependencies")

        # Check for orphans (nodes with no upstream and no downstream)
        for node_id, node in self.nodes.items():
            if not node.upstream and not node.downstream:
                orphans.append(node_id)

        if orphans:
            warnings.append(f"Found {len(orphans)} orphan nodes: {orphans}")

        return GraphValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cycles=cycles,
            orphan_nodes=orphans,
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_edge(self, from_node: str, to_node: str) -> Optional[DependencyEdge]:
        """Get an edge between two nodes."""
        for edge in self.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the graph to a dictionary.

        Returns:
            Dict[str, Any]: Graph representation
        """
        return {
            "nodes": {
                node_id: {
                    "phase_id": node.phase_id,
                    "status": node.status.name,
                    "upstream": list(node.upstream),
                    "downstream": list(node.downstream),
                    "config": node.config,
                }
                for node_id, node in self.nodes.items()
            },
            "edges": [
                {"from": edge.from_node, "to": edge.to_node, "type": edge.edge_type}
                for edge in self.edges
            ],
            "summary": self.get_summary(),
        }


# =============================================================================
# PHASE SCHEDULER
# =============================================================================

class SchedulingStrategy(Enum):
    """Scheduling strategies for phase execution."""

    # Execute phases sequentially (one at a time)
    SEQUENTIAL = auto()

    # Execute independent phases in parallel
    PARALLEL = auto()

    # Hybrid: parallelize independent phases, respect dependencies
    HYBRID = auto()

    # Priority-based: execute high-priority phases first
    PRIORITY = auto()


@dataclass
class SchedulingDecision:
    """
    Result of a scheduling operation.

    Attributes:
        phases_to_start: Phases that should start now
        phases_waiting: Phases that are ready but waiting (due to parallel limit)
        phases_blocked: Phases blocked by unsatisfied dependencies
        rationale: Explanation of the decision
        strategy_used: The scheduling strategy applied
    """

    phases_to_start: List[str] = field(default_factory=list)
    phases_waiting: List[str] = field(default_factory=list)
    phases_blocked: List[str] = field(default_factory=list)
    rationale: str = ""
    strategy_used: SchedulingStrategy = SchedulingStrategy.HYBRID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phases_to_start": self.phases_to_start,
            "phases_waiting": self.phases_waiting,
            "phases_blocked": self.phases_blocked,
            "rationale": self.rationale,
            "strategy_used": self.strategy_used.name,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class PhaseScheduler:
    """
    Scheduler for determining which phases should execute.

    Responsibilities:
    - Query dependency graph for ready phases
    - Apply scheduling strategy
    - Respect parallel execution limits
    - Provide scheduling rationale for audit

    Usage:
        scheduler = PhaseScheduler(
            dependency_graph=graph,
            mode=SchedulingStrategy.HYBRID
        )
        decision = scheduler.get_ready_phases(
            completed_phases={"PHASE_1"},
            active_phases=set(),
            max_parallel=4
        )
    """

    # Dependency graph to query
    dependency_graph: DependencyGraph

    # Scheduling mode
    mode: SchedulingStrategy = SchedulingStrategy.HYBRID

    # Priority weights for PRIORITY strategy
    priority_weights: Dict[str, float] = field(default_factory=dict)

    # Logging
    _logger: logging.Logger = field(default=None)

    def __post_init__(self):
        if self._logger is None:
            self._logger = logging.getLogger("SISAS.Orchestration.PhaseScheduler")

    # =========================================================================
    # SCHEDULING METHODS
    # =========================================================================

    def get_ready_phases(
        self,
        completed_phases: Set[str],
        failed_phases: Set[str],
        active_phases: Set[str],
        max_parallel: int = 4,
    ) -> SchedulingDecision:
        """
        Determine which phases should start.

        Args:
            completed_phases: Phases that have completed
            failed_phases: Phases that have failed
            active_phases: Phases currently running
            max_parallel: Maximum parallel phases allowed

        Returns:
            SchedulingDecision: The scheduling decision
        """
        # Get all ready phases from graph
        ready_phases = self.dependency_graph.get_ready_phases()

        # Filter out already active or completed
        available = [
            p for p in ready_phases
            if p not in active_phases and p not in completed_phases
        ]

        # Determine blocked phases
        blocked = self._get_blocked_phases(
            available, completed_phases, failed_phases
        )

        # Apply scheduling strategy
        if self.mode == SchedulingStrategy.SEQUENTIAL:
            return self._schedule_sequential(
                available, blocked, active_phases, max_parallel
            )
        elif self.mode == SchedulingStrategy.PARALLEL:
            return self._schedule_parallel(
                available, blocked, active_phases, max_parallel
            )
        elif self.mode == SchedulingStrategy.PRIORITY:
            return self._schedule_priority(
                available, blocked, active_phases, max_parallel
            )
        else:  # HYBRID (default)
            return self._schedule_hybrid(
                available, blocked, active_phases, max_parallel
            )

    def _schedule_sequential(
        self,
        available: List[str],
        blocked: List[str],
        active_phases: Set[str],
        max_parallel: int,
    ) -> SchedulingDecision:
        """
        Sequential scheduling - one phase at a time.

        Args:
            available: Available phases
            blocked: Blocked phases
            active_phases: Currently active phases
            max_parallel: Parallel limit (ignored in sequential mode)

        Returns:
            SchedulingDecision: Decision with single phase or none
        """
        if active_phases:
            # Something is already running, wait
            return SchedulingDecision(
                phases_to_start=[],
                phases_waiting=available[:1] if available else [],
                phases_blocked=blocked,
                rationale="Sequential mode: waiting for active phase to complete",
                strategy_used=SchedulingStrategy.SEQUENTIAL,
            )

        to_start = available[:1] if available else []
        waiting = available[1:] if len(available) > 1 else []

        return SchedulingDecision(
            phases_to_start=to_start,
            phases_waiting=waiting,
            phases_blocked=blocked,
            rationale=f"Sequential mode: starting {to_start[0] if to_start else 'none'}",
            strategy_used=SchedulingStrategy.SEQUENTIAL,
        )

    def _schedule_parallel(
        self,
        available: List[str],
        blocked: List[str],
        active_phases: Set[str],
        max_parallel: int,
    ) -> SchedulingDecision:
        """
        Parallel scheduling - start all available up to limit.

        Args:
            available: Available phases
            blocked: Blocked phases
            active_phases: Currently active phases
            max_parallel: Maximum parallel phases

        Returns:
            SchedulingDecision: Decision with as many phases as possible
        """
        slots_available = max_parallel - len(active_phases)
        to_start = available[:slots_available] if slots_available > 0 else []
        waiting = available[slots_available:] if slots_available < len(available) else []

        return SchedulingDecision(
            phases_to_start=to_start,
            phases_waiting=waiting,
            phases_blocked=blocked,
            rationale=(
                f"Parallel mode: {len(active_phases)} active, "
                f"{slots_available} slots available, starting {len(to_start)}"
            ),
            strategy_used=SchedulingStrategy.PARALLEL,
            metadata={
                "active_count": len(active_phases),
                "slots_available": slots_available,
                "max_parallel": max_parallel,
            },
        )

    def _schedule_hybrid(
        self,
        available: List[str],
        blocked: List[str],
        active_phases: Set[str],
        max_parallel: int,
    ) -> SchedulingDecision:
        """
        Hybrid scheduling - respect dependencies, parallelize independent phases.

        This is the default strategy. It:
        1. Respects all dependency constraints
        2. Parallelizes independent phases up to limit
        3. Prioritizes phases that unblock others

        Args:
            available: Available phases
            blocked: Blocked phases
            active_phases: Currently active phases
            max_parallel: Maximum parallel phases

        Returns:
            SchedulingDecision: Optimized scheduling decision
        """
        # Calculate slots available
        slots_available = max_parallel - len(active_phases)

        if slots_available <= 0:
            return SchedulingDecision(
                phases_to_start=[],
                phases_waiting=available,
                phases_blocked=blocked,
                rationale=f"Hybrid mode: at parallel limit ({max_parallel})",
                strategy_used=SchedulingStrategy.HYBRID,
            )

        # Prioritize phases that unblock the most downstream phases
        prioritized = self._prioritize_by_unblocking(available)

        # Select phases to start
        to_start = prioritized[:slots_available]
        waiting = prioritized[slots_available:]

        return SchedulingDecision(
            phases_to_start=to_start,
            phases_waiting=waiting,
            phases_blocked=blocked,
            rationale=(
                f"Hybrid mode: prioritized by downstream unblocking. "
                f"Starting {len(to_start)} of {len(available)} available."
            ),
            strategy_used=SchedulingStrategy.HYBRID,
            metadata={
                "prioritized_order": prioritized,
                "unblocking_counts": self._get_unblocking_counts(available),
            },
        )

    def _schedule_priority(
        self,
        available: List[str],
        blocked: List[str],
        active_phases: Set[str],
        max_parallel: int,
    ) -> SchedulingDecision:
        """
        Priority-based scheduling - use priority weights.

        Args:
            available: Available phases
            blocked: Blocked phases
            active_phases: Currently active phases
            max_parallel: Maximum parallel phases

        Returns:
            SchedulingDecision: Decision based on priority weights
        """
        # Sort by priority weight
        prioritized = sorted(
            available,
            key=lambda p: self.priority_weights.get(p, 0.0),
            reverse=True,
        )

        slots_available = max_parallel - len(active_phases)
        to_start = prioritized[:slots_available] if slots_available > 0 else []
        waiting = prioritized[slots_available:] if slots_available < len(prioritized) else []

        return SchedulingDecision(
            phases_to_start=to_start,
            phases_waiting=waiting,
            phases_blocked=blocked,
            rationale=(
                f"Priority mode: sorted by weight, "
                f"starting {len(to_start)} of {len(available)}"
            ),
            strategy_used=SchedulingStrategy.PRIORITY,
            metadata={
                "priority_weights": {
                    p: self.priority_weights.get(p, 0.0) for p in available
                },
            },
        )

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_blocked_phases(
        self,
        available: List[str],
        completed_phases: Set[str],
        failed_phases: Set[str],
    ) -> List[str]:
        """
        Get phases that are blocked by failed dependencies.

        Args:
            available: Available phases
            completed_phases: Completed phases
            failed_phases: Failed phases

        Returns:
            List[str]: Blocked phase IDs
        """
        blocked = []
        for phase_id in available:
            # Check upstream dependencies
            upstream = self.dependency_graph.get_upstream_dependencies(phase_id)
            for upstream_id in upstream:
                if upstream_id in failed_phases:
                    blocked.append(phase_id)
                    break

        return blocked

    def _prioritize_by_unblocking(self, phases: List[str]) -> List[str]:
        """
        Prioritize phases by how many downstream phases they unblock.

        Args:
            phases: Phases to prioritize

        Returns:
            List[str]: Prioritized phase IDs
        """
        unblocking_counts = self._get_unblocking_counts(phases)

        return sorted(
            phases,
            key=lambda p: unblocking_counts.get(p, 0),
            reverse=True,
        )

    def _get_unblocking_counts(self, phases: List[str]) -> Dict[str, int]:
        """
        Get count of downstream phases each phase would unblock.

        Args:
            phases: Phases to check

        Returns:
            Dict[str, int]: Mapping of phase_id to unblock count
        """
        counts = {}
        for phase_id in phases:
            # Count downstream phases that are currently blocked
            downstream = self.dependency_graph.get_downstream_dependents(phase_id)
            blocked_count = 0
            for downstream_id in downstream:
                node = self.dependency_graph.nodes.get(downstream_id)
                if node and node.status == DependencyStatus.BLOCKED:
                    blocked_count += 1
            counts[phase_id] = blocked_count

        return counts

    def set_priority(self, phase_id: str, weight: float) -> None:
        """
        Set priority weight for a phase (for PRIORITY strategy).

        Args:
            phase_id: Phase to set priority for
            weight: Priority weight (higher = more important)
        """
        self.priority_weights[phase_id] = weight
        self._logger.debug(f"Set priority for {phase_id}: {weight}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize scheduler to dictionary.

        Returns:
            Dict[str, Any]: Scheduler representation
        """
        return {
            "mode": self.mode.name,
            "priority_weights": self.priority_weights.copy(),
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Exceptions
    "OrchestrationError",
    "DependencyResolutionError",
    "SchedulingError",
    "StateTransitionError",
    # State Machine
    "OrchestrationState",
    "StateTransition",
    "VALID_TRANSITIONS",
    "OrchestrationStateMachine",
    # Dependency Graph
    "DependencyStatus",
    "DependencyNode",
    "DependencyEdge",
    "GraphValidationResult",
    "DependencyGraph",
    # Phase Scheduler
    "SchedulingStrategy",
    "SchedulingDecision",
    "PhaseScheduler",
]
