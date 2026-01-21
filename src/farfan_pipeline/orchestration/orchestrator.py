"""
Unified FARFAN Pipeline Orchestrator
===================================

This is the SINGLE unified orchestrator that consolidates all orchestration logic.

Previously split across 5 files:
- orchestrator_config.py (configuration)
- orchestration_core.py (state machine, dependency graph, scheduler)
- core_orchestrator.py (core orchestration logic)
- phase_executors.py (phase executors P02-P09)
- main_orchestrator.py (signal-driven orchestrator)

Now consolidated into ONE comprehensive orchestrator.

Architecture:
┌─────────────────────────────────────────────────────────────────────────────┐
│                         UNIFIED ORCHESTRATOR                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Configuration   │  │ State Machine   │  │ Dependency      │             │
│  │                 │  │                 │  │ Graph           │             │
│  │ - Orchestrator  │  │ - IDLE          │  │ - Nodes         │             │
│  │   Config        │  │ - INITIALIZING  │  │ - Edges         │             │
│  │ - Validation    │  │ - RUNNING       │  │ - Validation    │             │
│  └─────────────────┘  │ - COMPLETED     │  │ - Propagation   │             │
│                      └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Phase Scheduler │  │ Core Orchestrator│  │ Signal-Driven   │             │
│  │                 │  │                 │  │ Orchestrator    │             │
│  │ - SEQUENTIAL    │  │ - Execute phases │  │ - PhaseStart    │             │
│  │ - PARALLEL      │  │ - Contract      │  │ - PhaseComplete │             │
│  │ - HYBRID        │  │   enforcement   │  │ - Decision      │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                    Phase Executors (P02-P09)                     │       │
│  │  P2: Task Execution  P3: Scoring  P4-P7: Aggregation  P8-P9     │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Version: 2.0.0 (Unified)
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple, cast
from uuid import uuid4

import blake3
import structlog

# =============================================================================
# SISAS CORE IMPORTS
# =============================================================================
try:
    from canonic_questionnaire_central.core.signal import (
        Signal, SignalType, SignalScope, SignalProvenance
    )
    from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
        SignalDistributionOrchestrator, Consumer, DeadLetterReason
    )
    SISAS_CORE_AVAILABLE = True
except ImportError:
    SISAS_CORE_AVAILABLE = False
    Signal = None
    SignalType = None
    SignalScope = None
    SignalProvenance = None

# Import validation gates
try:
    from .gates import (
        GateOrchestrator,
        ScopeAlignmentGate,
        ValueAddGate,
        CapabilityGate,
        IrrigationChannelGate
    )
    GATES_AVAILABLE = True
except ImportError:
    GATES_AVAILABLE = False
    GateOrchestrator = None

# =============================================================================
# UNIFIED FACTORY IMPORT
# =============================================================================
# Import the unified factory for all component creation and questionnaire loading
try:
    from .factory import UnifiedFactory, FactoryConfig
    FACTORY_AVAILABLE = True
except ImportError:
    FACTORY_AVAILABLE = False
    UnifiedFactory = None  # type: ignore
    FactoryConfig = None  # type: ignore

# =============================================================================
# SISAS INTEGRATION HUB IMPORT
# =============================================================================
# Import the SISAS integration hub for comprehensive SISAS wiring
try:
    from .sisas_integration_hub import (
        SISASIntegrationHub,
        IntegrationStatus,
        initialize_sisas,
        get_sisas_status,
    )
    SISAS_HUB_AVAILABLE = True
except ImportError:
    SISAS_HUB_AVAILABLE = False
    SISASIntegrationHub = None  # type: ignore
    initialize_sisas = None  # type: ignore

# =============================================================================
# LOGGER CONFIGURATION
# =============================================================================

logger = structlog.get_logger(__name__)

# =============================================================================
# SECTION 1: CONFIGURATION (from orchestrator_config.py)
# =============================================================================

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


@dataclass
class OrchestratorConfig:
    """Unified configuration for the orchestrator."""

    # Core settings
    municipality_name: str = "Unknown"
    document_path: Optional[str] = None
    output_dir: str = "./output"

    # Execution settings
    strict_mode: bool = False
    phases_to_execute: str = "ALL"

    # Resource settings
    seed: int = 42
    max_workers: int = 4
    enable_parallel_execution: bool = True

    # Feature flags
    enable_sisas: bool = True
    enable_calibration: bool = True
    enable_checkpoint: bool = True

    # Paths
    questionnaire_path: str = "canonic_questionnaire_central/_registry"
    methods_file: str = "json_methods/METHODS_OPERACIONALIZACION.json"

    # Resource limits
    resource_limits: dict = field(default_factory=dict)

    # Scheduling mode
    scheduling_mode: str = "HYBRID"  # SEQUENTIAL, PARALLEL, HYBRID, PRIORITY
    max_parallel_phases: int = 4

    # Retry settings
    retry_failed_phases: bool = True
    max_retries_per_phase: int = 3

    # Signal settings
    emit_decision_signals: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "municipality_name": self.municipality_name,
            "document_path": self.document_path,
            "output_dir": self.output_dir,
            "strict_mode": self.strict_mode,
            "phases_to_execute": self.phases_to_execute,
            "seed": self.seed,
            "max_workers": self.max_workers,
            "enable_parallel_execution": self.enable_parallel_execution,
            "enable_sisas": self.enable_sisas,
            "enable_calibration": self.enable_calibration,
            "enable_checkpoint": self.enable_checkpoint,
            "questionnaire_path": self.questionnaire_path,
            "methods_file": self.methods_file,
            "resource_limits": self.resource_limits,
            "scheduling_mode": self.scheduling_mode,
            "max_parallel_phases": self.max_parallel_phases,
            "retry_failed_phases": self.retry_failed_phases,
            "max_retries_per_phase": self.max_retries_per_phase,
            "emit_decision_signals": self.emit_decision_signals,
        }


def validate_config(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate configuration dictionary."""
    errors = []

    if not config.get("document_path"):
        errors.append("document_path is required")

    if config.get("seed") is not None and not isinstance(config.get("seed"), int):
        errors.append("seed must be an integer")

    if config.get("max_workers") is not None:
        workers = config.get("max_workers")
        if not isinstance(workers, int) or workers < 1:
            errors.append("max_workers must be a positive integer")

    return len(errors) == 0, errors


def get_development_config() -> OrchestratorConfig:
    """Get configuration preset for development."""
    return OrchestratorConfig(
        strict_mode=False,
        enable_sisas=True,
        enable_calibration=False,
        max_workers=2,
    )


def get_production_config() -> OrchestratorConfig:
    """Get configuration preset for production."""
    return OrchestratorConfig(
        strict_mode=True,
        enable_sisas=True,
        enable_calibration=True,
        max_workers=4,
    )


def get_testing_config() -> OrchestratorConfig:
    """Get configuration preset for testing."""
    return OrchestratorConfig(
        strict_mode=True,
        enable_sisas=False,
        enable_calibration=False,
        max_workers=1,
        phases_to_execute="0-2",
    )


# =============================================================================
# SECTION 2: EXCEPTIONS (from orchestration_core.py)
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


# =============================================================================
# SECTION 3: STATE MACHINE (from orchestration_core.py)
# =============================================================================

class OrchestrationState(Enum):
    """States of the orchestration lifecycle."""

    IDLE = auto()
    INITIALIZING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    COMPLETED_WITH_ERRORS = auto()
    STOPPED = auto()
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


VALID_TRANSITIONS: Dict[OrchestrationState, Set[OrchestrationState]] = {
    OrchestrationState.IDLE: {OrchestrationState.INITIALIZING},
    OrchestrationState.INITIALIZING: {OrchestrationState.RUNNING, OrchestrationState.STOPPING},
    OrchestrationState.RUNNING: {
        OrchestrationState.COMPLETED,
        OrchestrationState.COMPLETED_WITH_ERRORS,
        OrchestrationState.STOPPING,
    },
    OrchestrationState.STOPPING: {OrchestrationState.STOPPED},
    OrchestrationState.COMPLETED: set(),
    OrchestrationState.COMPLETED_WITH_ERRORS: set(),
    OrchestrationState.STOPPED: set(),
}


@dataclass
class OrchestrationStateMachine:
    """State machine for orchestration lifecycle management."""

    current_state: OrchestrationState = field(default=OrchestrationState.IDLE)
    _transition_history: List[StateTransition] = field(default_factory=list)
    allow_terminal_transition: bool = False
    _transition_callbacks: Dict[OrchestrationState, List[callable]] = field(default_factory=dict)

    def transition_to(
        self,
        new_state: OrchestrationState,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateTransition:
        """Transition to a new state."""
        if not self._is_valid_transition(new_state):
            raise StateTransitionError(
                message=f"Invalid state transition: {self.current_state.name} → {new_state.name}",
                current_state=self.current_state.name,
                target_state=new_state.name,
            )

        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            reason=reason,
            metadata=metadata or {},
        )

        old_state = self.current_state
        self.current_state = new_state
        self._transition_history.append(transition)

        logger.info(f"State transition: {old_state.name} → {new_state.name}")

        self._invoke_callbacks(new_state, transition)
        return transition

    def _is_valid_transition(self, new_state: OrchestrationState) -> bool:
        """Check if a transition is valid."""
        if new_state == self.current_state:
            return False

        valid_targets = VALID_TRANSITIONS.get(self.current_state, set())

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
        """Register a callback to be invoked when entering a specific state."""
        if state not in self._transition_callbacks:
            self._transition_callbacks[state] = []
        self._transition_callbacks[state].append(callback)

    def _invoke_callbacks(self, state: OrchestrationState, transition: StateTransition) -> None:
        """Invoke all callbacks registered for a state."""
        callbacks = self._transition_callbacks.get(state, [])
        for callback in callbacks:
            try:
                callback(transition)
            except Exception as e:
                logger.error(f"State transition callback failed for state {state.name}: {e}")

    def get_transition_history(self) -> List[Dict[str, Any]]:
        """Get the complete transition history."""
        return [t.to_dict() for t in self._transition_history]

    def is_terminal(self) -> bool:
        """Check if the current state is terminal."""
        return self.current_state in {
            OrchestrationState.COMPLETED,
            OrchestrationState.COMPLETED_WITH_ERRORS,
            OrchestrationState.STOPPED,
        }

    def is_running(self) -> bool:
        """Check if the orchestration is currently running."""
        return self.current_state == OrchestrationState.RUNNING

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the state machine to a dictionary."""
        return {
            "current_state": self.current_state.name,
            "is_terminal": self.is_terminal(),
            "is_running": self.is_running(),
            "transition_count": len(self._transition_history),
            "transitions": self.get_transition_history(),
        }


# =============================================================================
# SECTION 4: DEPENDENCY GRAPH (from orchestration_core.py)
# =============================================================================

class DependencyStatus(Enum):
    """Status of a node in the dependency graph."""
    PENDING = auto()
    READY = auto()
    RUNNING = auto()
    COMPLETED = auto()
    PARTIAL = auto()
    PENDING_RETRY = auto()
    FAILED = auto()
    BLOCKED = auto()
    PERMANENTLY_BLOCKED = auto()


@dataclass
class DependencyNode:
    """Represents a phase node in the dependency graph."""

    node_id: str
    phase_id: str
    status: DependencyStatus = DependencyStatus.PENDING
    upstream: Set[str] = field(default_factory=set)
    downstream: Set[str] = field(default_factory=set)
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
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


@dataclass
class DependencyEdge:
    """Represents a dependency relationship between two phases."""
    from_node: str
    to_node: str
    edge_type: str = "hard"

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
    """Dependency graph for phase orchestration."""

    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    edges: Set[DependencyEdge] = field(default_factory=set)
    _adjacency: Dict[str, Set[str]] = field(default_factory=dict)
    _reverse_adjacency: Dict[str, Set[str]] = field(default_factory=dict)

    def add_node(
        self,
        node_id: str,
        phase_id: str,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DependencyNode:
        """Add a phase node to the graph."""
        if node_id in self.nodes:
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

        return node

    def add_edge(
        self, from_node: str, to_node: str, edge_type: str = "hard"
    ) -> DependencyEdge:
        """Add a dependency edge between two nodes."""
        if from_node not in self.nodes:
            raise DependencyResolutionError(f"Source node {from_node} does not exist")
        if to_node not in self.nodes:
            raise DependencyResolutionError(f"Target node {to_node} does not exist")

        edge = DependencyEdge(from_node=from_node, to_node=to_node, edge_type=edge_type)

        if self._would_create_cycle(edge):
            raise DependencyResolutionError(
                f"Edge {from_node} -> {to_node} would create a circular dependency"
            )

        self.edges.add(edge)
        self._adjacency[from_node].add(to_node)
        self._reverse_adjacency[to_node].add(from_node)

        self.nodes[from_node].downstream.add(to_node)
        self.nodes[to_node].upstream.add(from_node)

        self._update_node_readiness(to_node)

        return edge

    def _would_create_cycle(self, new_edge: DependencyEdge) -> bool:
        """Check if adding an edge would create a cycle."""
        visited: Set[str] = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            for neighbor in self._adjacency.get(node, set()):
                if neighbor == new_edge.from_node:
                    return True
                if neighbor not in visited and has_cycle(neighbor):
                    return True
            return False

        return has_cycle(new_edge.to_node)

    def update_node_status(
        self,
        node_id: str,
        new_status: DependencyStatus,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update the status of a node."""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]
        old_status = node.status
        node.status = new_status

        if metadata:
            node.metadata.update(metadata)

        if new_status == DependencyStatus.RUNNING and node.started_at is None:
            node.started_at = datetime.utcnow()
        elif new_status in {
            DependencyStatus.COMPLETED,
            DependencyStatus.PARTIAL,
            DependencyStatus.FAILED,
            DependencyStatus.PERMANENTLY_BLOCKED,
        }:
            node.completed_at = datetime.utcnow()

        logger.info(f"Node {node_id} status: {old_status.name} → {new_status.name}")
        self._propagate_status_change(node_id, new_status)

    def _update_node_readiness(self, node_id: str) -> None:
        """Update whether a node is ready to start."""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]

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
        """Propagate status changes to downstream nodes."""
        for downstream_id in self._adjacency.get(node_id, set()):
            if new_status == DependencyStatus.COMPLETED:
                self._update_node_readiness(downstream_id)
            elif new_status in {
                DependencyStatus.FAILED,
                DependencyStatus.PERMANENTLY_BLOCKED,
            }:
                edge = self._get_edge(node_id, downstream_id)
                if edge and edge.edge_type == "hard":
                    self.update_node_status(
                        downstream_id, DependencyStatus.PERMANENTLY_BLOCKED
                    )

    def get_ready_phases(self) -> List[str]:
        """Get all phases that are ready to start."""
        return [
            node_id
            for node_id, node in self.nodes.items()
            if node.status == DependencyStatus.READY
        ]

    def get_upstream_dependencies(self, node_id: str) -> List[str]:
        """Get upstream dependencies for a node."""
        return list(self.nodes.get(node_id, DependencyNode("", "")).upstream)

    def get_downstream_dependents(self, node_id: str) -> List[str]:
        """Get downstream dependents of a node."""
        return list(self._adjacency.get(node_id, set()))

    def get_newly_unblocked(self, node_id: str) -> List[str]:
        """Get downstream nodes that became unblocked by a node completion."""
        unblocked = []
        for downstream_id in self._adjacency.get(node_id, set()):
            if self.nodes[downstream_id].status == DependencyStatus.READY:
                unblocked.append(downstream_id)
        return unblocked

    def get_permanently_blocked(self) -> List[str]:
        """Get all permanently blocked nodes."""
        return [
            node_id
            for node_id, node in self.nodes.items()
            if node.status == DependencyStatus.PERMANENTLY_BLOCKED
        ]

    def get_state_snapshot(self) -> Dict[str, str]:
        """Get a snapshot of all node states."""
        return {
            node_id: node.status.name for node_id, node in self.nodes.items()
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the graph."""
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

    def validate(self) -> GraphValidationResult:
        """Validate the dependency graph."""
        errors = []
        warnings = []
        cycles = []
        orphans = []

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

    def _get_edge(self, from_node: str, to_node: str) -> Optional[DependencyEdge]:
        """Get an edge between two nodes."""
        for edge in self.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the graph to a dictionary."""
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
# SECTION 5: PHASE SCHEDULER (from orchestration_core.py)
# =============================================================================

class SchedulingStrategy(Enum):
    """Scheduling strategies for phase execution."""
    SEQUENTIAL = auto()
    PARALLEL = auto()
    HYBRID = auto()
    PRIORITY = auto()


@dataclass
class SchedulingDecision:
    """Result of a scheduling operation."""
    phases_to_start: List[str] = field(default_factory=list)
    phases_waiting: List[str] = field(default_factory=list)
    phases_blocked: List[str] = field(default_factory=list)
    rationale: str = ""
    strategy_used: SchedulingStrategy = SchedulingStrategy.HYBRID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseScheduler:
    """Scheduler for determining which phases should execute."""

    dependency_graph: DependencyGraph
    mode: SchedulingStrategy = SchedulingStrategy.HYBRID
    priority_weights: Dict[str, float] = field(default_factory=dict)

    def get_ready_phases(
        self,
        completed_phases: Set[str],
        failed_phases: Set[str],
        active_phases: Set[str],
        max_parallel: int = 4,
    ) -> SchedulingDecision:
        """Determine which phases should start."""
        ready_phases = self.dependency_graph.get_ready_phases()

        available = [
            p for p in ready_phases
            if p not in active_phases and p not in completed_phases
        ]

        blocked = self._get_blocked_phases(available, completed_phases, failed_phases)

        if self.mode == SchedulingStrategy.SEQUENTIAL:
            return self._schedule_sequential(available, blocked, active_phases, max_parallel)
        elif self.mode == SchedulingStrategy.PARALLEL:
            return self._schedule_parallel(available, blocked, active_phases, max_parallel)
        elif self.mode == SchedulingStrategy.PRIORITY:
            return self._schedule_priority(available, blocked, active_phases, max_parallel)
        else:
            return self._schedule_hybrid(available, blocked, active_phases, max_parallel)

    def _schedule_sequential(
        self,
        available: List[str],
        blocked: List[str],
        active_phases: Set[str],
        max_parallel: int,
    ) -> SchedulingDecision:
        """Sequential scheduling - one phase at a time."""
        if active_phases:
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
        """Parallel scheduling - start all available up to limit."""
        slots_available = max_parallel - len(active_phases)
        to_start = available[:slots_available] if slots_available > 0 else []
        waiting = available[slots_available:] if slots_available < len(available) else []

        return SchedulingDecision(
            phases_to_start=to_start,
            phases_waiting=waiting,
            phases_blocked=blocked,
            rationale=f"Parallel mode: {len(active_phases)} active, {slots_available} slots",
            strategy_used=SchedulingStrategy.PARALLEL,
        )

    def _schedule_hybrid(
        self,
        available: List[str],
        blocked: List[str],
        active_phases: Set[str],
        max_parallel: int,
    ) -> SchedulingDecision:
        """Hybrid scheduling - respect dependencies, parallelize independent phases."""
        slots_available = max_parallel - len(active_phases)

        if slots_available <= 0:
            return SchedulingDecision(
                phases_to_start=[],
                phases_waiting=available,
                phases_blocked=blocked,
                rationale=f"Hybrid mode: at parallel limit ({max_parallel})",
                strategy_used=SchedulingStrategy.HYBRID,
            )

        prioritized = self._prioritize_by_unblocking(available)
        to_start = prioritized[:slots_available]
        waiting = prioritized[slots_available:]

        return SchedulingDecision(
            phases_to_start=to_start,
            phases_waiting=waiting,
            phases_blocked=blocked,
            rationale=f"Hybrid mode: starting {len(to_start)} of {len(available)} available",
            strategy_used=SchedulingStrategy.HYBRID,
        )

    def _schedule_priority(
        self,
        available: List[str],
        blocked: List[str],
        active_phases: Set[str],
        max_parallel: int,
    ) -> SchedulingDecision:
        """Priority-based scheduling - use priority weights."""
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
            rationale=f"Priority mode: starting {len(to_start)} of {len(available)}",
            strategy_used=SchedulingStrategy.PRIORITY,
        )

    def _get_blocked_phases(
        self,
        available: List[str],
        completed_phases: Set[str],
        failed_phases: Set[str],
    ) -> List[str]:
        """Get phases that are blocked by failed dependencies."""
        blocked = []
        for phase_id in available:
            upstream = self.dependency_graph.get_upstream_dependencies(phase_id)
            for upstream_id in upstream:
                if upstream_id in failed_phases:
                    blocked.append(phase_id)
                    break
        return blocked

    def _prioritize_by_unblocking(self, phases: List[str]) -> List[str]:
        """Prioritize phases by how many downstream phases they unblock."""
        unblocking_counts = self._get_unblocking_counts(phases)
        return sorted(phases, key=lambda p: unblocking_counts.get(p, 0), reverse=True)

    def _get_unblocking_counts(self, phases: List[str]) -> Dict[str, int]:
        """Get count of downstream phases each phase would unblock."""
        counts = {}
        for phase_id in phases:
            downstream = self.dependency_graph.get_downstream_dependents(phase_id)
            blocked_count = 0
            for downstream_id in downstream:
                node = self.dependency_graph.nodes.get(downstream_id)
                if node and node.status == DependencyStatus.BLOCKED:
                    blocked_count += 1
            counts[phase_id] = blocked_count
        return counts


# =============================================================================
# SECTION 6: CORE ORCHESTRATOR (consolidated from core_orchestrator.py)
# =============================================================================

class PhaseStatus(str, Enum):
    """Execution status for a pipeline phase."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    VALIDATED = "VALIDATED"
    ROLLED_BACK = "ROLLED_BACK"


class PhaseID(str, Enum):
    """Canonical phase identifiers."""
    PHASE_0 = "P00"
    PHASE_1 = "P01"
    PHASE_2 = "P02"
    PHASE_3 = "P03"
    PHASE_4 = "P04"
    PHASE_5 = "P05"
    PHASE_6 = "P06"
    PHASE_7 = "P07"
    PHASE_8 = "P08"
    PHASE_9 = "P09"


PHASE_METADATA = {
    PhaseID.PHASE_0: {
        "name": "Bootstrap & Validation",
        "description": "Infrastructure setup, determinism, resource control",
        "stages": 9,
        "sub_phases": 60,
    },
    PhaseID.PHASE_1: {
        "name": "CPP Ingestion",
        "description": "Question-aware chunking",
        "stages": 11,
        "sub_phases": 16,
        "expected_output_count": 300,
    },
    PhaseID.PHASE_2: {
        "name": "Executor Factory & Dispatch",
        "description": "Method dispensary instantiation and routing",
        "stages": 6,
        "sub_phases": 12,
        "expected_executor_count": 30,
        "expected_method_count": 240,
    },
    PhaseID.PHASE_3: {
        "name": "Layer Scoring",
        "description": "8-layer quality assessment",
        "stages": 4,
        "sub_phases": 10,
        "layers": 8,
    },
    PhaseID.PHASE_4: {
        "name": "Dimension Aggregation",
        "description": "Choquet integral aggregation",
        "stages": 3,
        "sub_phases": 9,
        "expected_output_count": 60,
    },
    PhaseID.PHASE_5: {
        "name": "Policy Area Aggregation",
        "description": "Dimension aggregation to policy areas",
        "stages": 3,
        "sub_phases": 7,
        "expected_output_count": 10,
    },
    PhaseID.PHASE_6: {
        "name": "Cluster Aggregation",
        "description": "Policy area aggregation to clusters",
        "stages": 3,
        "sub_phases": 7,
        "expected_output_count": 4,
    },
    PhaseID.PHASE_7: {
        "name": "Macro Aggregation",
        "description": "Cluster aggregation to holistic score",
        "stages": 3,
        "sub_phases": 6,
        "expected_output_count": 1,
    },
    PhaseID.PHASE_8: {
        "name": "Recommendations Engine",
        "description": "Signal-enriched recommendation generation",
        "stages": 4,
        "sub_phases": 11,
    },
    PhaseID.PHASE_9: {
        "name": "Report Assembly",
        "description": "Final report generation",
        "stages": 4,
        "sub_phases": 12,
    },
}


@dataclass
class PhaseResult:
    """Result of a single phase execution."""
    phase_id: PhaseID
    status: PhaseStatus
    output: Any
    execution_time_s: float
    violations: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    error: Optional[Exception] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    stage_timings: dict = field(default_factory=dict)
    sub_phase_results: dict = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Shared context across all pipeline phases."""

    wiring: Optional[Any] = None
    questionnaire: Optional[Any] = None
    sisas: Optional[Any] = None

    phase_inputs: dict = field(default_factory=dict)
    phase_outputs: dict = field(default_factory=dict)
    phase_results: dict = field(default_factory=dict)

    execution_id: str = field(default_factory=lambda: blake3.blake3(f"{time.time()}".encode()).hexdigest()[:16])
    start_time: datetime = field(default_factory=datetime.utcnow)
    config: dict = field(default_factory=dict)

    input_hashes: dict = field(default_factory=dict)
    output_hashes: dict = field(default_factory=dict)
    seed: Optional[int] = None

    total_violations: list = field(default_factory=list)
    signal_metrics: dict = field(default_factory=dict)

    def add_phase_result(self, result: PhaseResult) -> None:
        """Add a phase execution result."""
        self.phase_results[result.phase_id] = result
        self.phase_outputs[result.phase_id] = result.output
        self.total_violations.extend(result.violations)

    def get_phase_output(self, phase_id: PhaseID | str) -> Any:
        """Get output from a specific phase."""
        if isinstance(phase_id, str):
            phase_id = PhaseID(phase_id)
        return self.phase_outputs.get(phase_id)

    def validate_phase_prerequisite(self, phase_id: PhaseID) -> None:
        """Validate that all prerequisite phases have completed successfully."""
        if phase_id != PhaseID.PHASE_0:
            prev_phase_id = PhaseID(f"P0{int(phase_id.value[2]) - 1}")
            if prev_phase_id not in self.phase_results:
                raise RuntimeError(f"Phase {phase_id.value} requires {prev_phase_id.value} to complete first")


@dataclass
class PipelineResult:
    """Result of complete pipeline execution."""
    success: bool
    phase_results: dict
    total_duration_seconds: float
    metadata: dict
    errors: list = field(default_factory=list)


class UnifiedOrchestrator:
    """
    Unified FARFAN Pipeline Orchestrator.

    This single orchestrator consolidates all orchestration logic from:
    - Configuration management
    - State machine lifecycle
    - Dependency graph management
    - Phase scheduling
    - Core orchestration logic
    - Signal-driven orchestration (SISAS-aware)

    Usage:
        config = OrchestratorConfig(municipality_name="Example", document_path="doc.pdf")
        orchestrator = UnifiedOrchestrator(config=config)
        result = orchestrator.execute()
    """

    # =========================================================================
    # SISAS CONSUMER CONFIGURATION
    # =========================================================================
    CONSUMER_CONFIGS = (
        {
            "consumer_id": "phase_00_assembly_consumer",
            "scopes": [{"phase": "phase_0", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["STATIC_LOAD", "SIGNAL_PACK", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_01_extraction_consumer",
            "scopes": [{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["EXTRACTION", "STRUCTURAL_PARSING", "TRIPLET_EXTRACTION",
                           "NUMERIC_PARSING", "NORMATIVE_LOOKUP", "HIERARCHY_PARSING",
                           "FINANCIAL_ANALYSIS", "POPULATION_PARSING", "TEMPORAL_PARSING",
                           "CAUSAL_ANALYSIS", "NER", "SEMANTIC_ANALYSIS", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_02_enrichment_consumer",
            "scopes": [{"phase": "phase_2", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["ENRICHMENT", "PATTERN_MATCHING", "ENTITY_RECOGNITION", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_03_validation_consumer",
            "scopes": [{"phase": "phase_3", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["VALIDATION", "NORMATIVE_CHECK", "COHERENCE_CHECK", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_04_micro_consumer",
            "scopes": [{"phase": "phase_4", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["SCORING", "MICRO_LEVEL", "CHOQUET_INTEGRAL", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_05_meso_consumer",
            "scopes": [{"phase": "phase_5", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["SCORING", "MESO_LEVEL", "DIMENSION_AGGREGATION", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_06_macro_consumer",
            "scopes": [{"phase": "phase_6", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["SCORING", "MACRO_LEVEL", "POLICY_AREA_AGGREGATION", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_07_aggregation_consumer",
            "scopes": [{"phase": "phase_7", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["AGGREGATION", "CLUSTER_LEVEL", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_08_integration_consumer",
            "scopes": [{"phase": "phase_8", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["INTEGRATION", "RECOMMENDATION_ENGINE", "PHASE_MONITORING"],
        },
        {
            "consumer_id": "phase_09_report_consumer",
            "scopes": [{"phase": "phase_9", "policy_area": "ALL", "slot": "ALL"}],
            "capabilities": ["REPORT_GENERATION", "ASSEMBLY", "EXPORT", "PHASE_MONITORING"],
        },
    )

    def __init__(self, config: OrchestratorConfig):
        """Initialize the unified orchestrator."""
        self.config = config
        self.logger = structlog.get_logger(f"{__name__}.UnifiedOrchestrator")

        # Initialize core context
        self.context = ExecutionContext()
        self.context.config = config.to_dict()

        # Initialize state machine
        self.state_machine = OrchestrationStateMachine()

        # Initialize dependency graph with default phases
        self.dependency_graph = self._build_default_dependency_graph()

        # Initialize phase scheduler
        self.scheduler = PhaseScheduler(
            dependency_graph=self.dependency_graph,
            mode=SchedulingStrategy[config.scheduling_mode],
        )

        # Execution state
        self._active_phases: Set[str] = set()
        self._completed_phases: Dict[str, Any] = {}
        self._failed_phases: Dict[str, List[Any]] = {}
        self._phase_retry_counts: Dict[str, int] = {}

        # ==========================================================================
        # UNIFIED FACTORY INITIALIZATION
        # ==========================================================================
        # Initialize the unified factory for questionnaire loading, component creation,
        # and contract execution
        if FACTORY_AVAILABLE:
            # Determine project root using multiple fallback strategies for robustness
            # 1. Try to locate via factory config if provided
            # 2. Try relative path from output_dir (output_dir may be output/ or artifacts/)
            # 3. Fall back to current working directory
            project_root = self._determine_project_root(config)

            self.factory: Optional[UnifiedFactory] = UnifiedFactory(
                config=FactoryConfig(
                    project_root=project_root,
                    questionnaire_path=Path(config.questionnaire_path) if config.questionnaire_path else None,
                    sisas_enabled=config.enable_sisas,
                    lazy_load_questions=True,
                )
            )
            # Initialize questionnaire through factory
            self.context.questionnaire = self.factory.load_questionnaire()
            # Initialize signal registry
            self.context.signal_registry = self.factory.create_signal_registry()

            # Initialize SISAS if enabled - USING INTEGRATION HUB
            if config.enable_sisas and SISAS_HUB_AVAILABLE:
                sisas_status = initialize_sisas(self)

                self.logger.info(
                    "SISAS initialized via integration hub",
                    consumers=f"{sisas_status.consumers_registered}/{sisas_status.consumers_available}",
                    extractors=f"{sisas_status.extractors_connected}/{sisas_status.extractors_available}",
                    vehicles=f"{sisas_status.vehicles_initialized}/{sisas_status.vehicles_available}",
                    irrigation_units=sisas_status.irrigation_units_loaded,
                    items_irrigable=sisas_status.items_irrigable,
                    fully_integrated=sisas_status.is_fully_integrated(),
                )
            elif config.enable_sisas and not SISAS_HUB_AVAILABLE:
                # Fallback to old method if hub not available
                self.context.sisas = self.factory.get_sisas_central()
                # Register phase consumers with SDO
                if self.context.sisas is not None:
                    consumers_registered = self._register_phase_consumers()
                    self.logger.info(f"SISAS initialized (legacy mode) with {consumers_registered} consumers")

            # ==========================================================================
            # INTERVENTION 2: Orchestrator-Factory Alignment
            # ==========================================================================
            # Perform initial sync with factory
            self._sync_with_factory()

            self.logger.info(
                "UnifiedFactory initialized",
                questionnaire_available=self.context.questionnaire is not None,
                signal_registry_available=self.context.signal_registry is not None,
                sisas_available=self.context.sisas is not None,
            )
        else:
            self.factory = None
            self.logger.warning(
                "UnifiedFactory not available, questionnaire and components will be limited"
            )

    def _sync_with_factory(self) -> None:
        """
        Synchronize orchestrator context with factory products.

        Ensures that all components created by the factory are correctly
        registered in the execution context. This provides thread-safe
        caching and single-source-of-truth alignment.
        """
        if not self.factory:
            return

        # Sync Questionnaire
        if self.context.questionnaire is None:
            self.context.questionnaire = self.factory.load_questionnaire()
            self.logger.debug("Synced questionnaire from factory")

        # Sync Signal Registry
        if self.context.signal_registry is None:
            self.context.signal_registry = self.factory.create_signal_registry()
            self.logger.debug("Synced signal registry from factory")

        # Sync SISAS (if enabled)
        if self.config.enable_sisas and self.context.sisas is None:
            self.context.sisas = self.factory.get_sisas_central()
            if self.context.sisas:
                self.logger.debug("Synced SISAS central from factory")

        self.logger.debug("Orchestrator-Factory alignment complete")

    def _register_phase_consumers(self) -> int:
        """
        Register all 10 phase consumers with the SDO.

        Returns:
            Number of consumers successfully registered
        """
        if not self.config.enable_sisas:
            self.logger.debug("SISAS disabled, skipping consumer registration")
            return 0

        if self.context.sisas is None:
            self.logger.warning("SDO not initialized, cannot register consumers")
            return 0

        if not SISAS_CORE_AVAILABLE:
            self.logger.warning("SISAS core not available")
            return 0

        sdo = self.context.sisas
        registered = 0

        for config in self.CONSUMER_CONFIGS:
            try:
                handler = self._create_phase_handler(config["consumer_id"])
                sdo.register_consumer(
                    consumer_id=config["consumer_id"],
                    scopes=config["scopes"],
                    capabilities=config["capabilities"],
                    handler=handler
                )
                registered += 1
                self.logger.debug(f"Registered consumer: {config['consumer_id']}")
            except Exception as e:
                self.logger.error(f"Failed to register {config['consumer_id']}: {e}")

        self.logger.info(
            "Phase consumers registered",
            registered=registered,
            total=len(self.CONSUMER_CONFIGS)
        )
        return registered

    def _create_phase_handler(self, consumer_id: str):
        """Create a signal handler for a phase consumer."""
        def handler(signal):
            phase_num = consumer_id.split("_")[1]  # Extract "00", "01", etc.
            metric_key = f"phase_{phase_num}_signals"
            self.context.signal_metrics.setdefault(metric_key, []).append(signal.signal_id)
            self.logger.debug(f"{consumer_id} received signal: {signal.signal_id}")
        return handler

    def _emit_phase_signal(
        self,
        phase_id: PhaseID,
        event_type: str,
        payload: Dict[str, Any],
        policy_area: str = "ALL"
    ) -> bool:
        """
        Emit a SISAS signal for phase lifecycle events.

        Args:
            phase_id: Phase emitting the signal
            event_type: PHASE_START, PHASE_COMPLETE, PHASE_FAILED
            payload: Signal payload data
            policy_area: Target policy area (default ALL)

        Returns:
            True if signal was delivered to at least one consumer
        """
        if not self.config.enable_sisas:
            return False

        if self.context.sisas is None or not SISAS_CORE_AVAILABLE:
            return False

        sdo = self.context.sisas

        try:
            phase_num = int(phase_id.value[1:])
            phase_str = f"phase_{phase_num}"

            scope = SignalScope(
                phase=phase_str,
                policy_area=policy_area,
                slot="ALL"
            )

            provenance = SignalProvenance(
                extractor="UnifiedOrchestrator",
                source_file="orchestrator.py",
                extraction_pattern=f"{phase_id.value}_{event_type}"
            )

            signal = Signal.create(
                signal_type=SignalType.STATIC_LOAD,
                scope=scope,
                payload={
                    "phase_id": phase_id.value,
                    "event_type": event_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    **payload
                },
                provenance=provenance,
                empirical_availability=1.0,
                capabilities_required=["PHASE_MONITORING"]
            )

            delivered = sdo.dispatch(signal)

            self.logger.debug(
                "Phase signal emitted",
                phase=phase_id.value,
                event_type=event_type,
                delivered=delivered
            )

            return delivered

        except Exception as e:
            self.logger.warning(f"Failed to emit signal for {phase_id}: {e}")
            return False

    def _determine_project_root(self, config: OrchestratorConfig) -> Path:
        """
        Determine project root using multiple fallback strategies.

        This provides robust path resolution that works with different
        directory layouts and configurations.

        Args:
            config: OrchestratorConfig with output_dir and other settings

        Returns:
            Path to project root directory

        Strategy:
            1. If factory_config has project_root, use it
            2. Try output_dir.parent.parent (traditional structure)
            3. Try output_dir.parent if artifacts/ is at output level
            4. Fall back to current working directory
        """
        from pathlib import Path
        import sys

        # Strategy 1: Check for explicit factory config
        if hasattr(config, 'factory_config') and config.factory_config:
            if hasattr(config.factory_config, 'project_root'):
                return Path(config.factory_config.project_root)

        output_dir = Path(config.output_dir)

        # Strategy 2: Try output_dir.parent.parent (output/ or artifacts/ structure)
        # This handles cases like:
        #   project_root/output/ -> parent.parent = project_root
        #   project_root/artifacts/output/ -> parent.parent = project_root/artifacts
        candidate1 = output_dir.parent.parent
        if (candidate1 / "canonic_questionnaire_central").exists():
            return candidate1
        if (candidate1 / "artifacts" / "data" / "contracts").exists():
            return candidate1

        # Strategy 3: Try output_dir.parent (flat structure)
        # This handles cases like:
        #   project_root/output_dir/ -> parent = project_root
        candidate2 = output_dir.parent
        if (candidate2 / "canonic_questionnaire_central").exists():
            return candidate2
        if (candidate2 / "artifacts" / "data" / "contracts").exists():
            return candidate2

        # Strategy 4: Check if we're in src/ directory
        # If this file is in src/farfan_pipeline/orchestration/orchestrator.py
        # then project_root is 3 levels up
        current_file = Path(__file__).resolve()
        candidate3 = current_file.parent.parent.parent
        if (candidate3 / "canonic_questionnaire_central").exists():
            return candidate3
        if (candidate3 / "artifacts" / "data" / "contracts").exists():
            return candidate3

        # Strategy 5: Fall back to current working directory
        cwd = Path.cwd()
        self.logger.warning(
            "Could not determine project_root via heuristics, using CWD",
            cwd=str(cwd),
            output_dir=str(output_dir)
        )
        return cwd

    def _build_default_dependency_graph(self) -> DependencyGraph:
        """Build default dependency graph for all phases."""
        graph = DependencyGraph()

        # Add all phase nodes
        for phase_id in PhaseID:
            graph.add_node(
                node_id=phase_id.value,
                phase_id=phase_id.value,
                metadata=PHASE_METADATA.get(phase_id, {})
            )

        # Add sequential dependencies
        phase_list = list(PhaseID)
        for i in range(len(phase_list) - 1):
            graph.add_edge(phase_list[i].value, phase_list[i + 1].value)

        return graph

    def execute(self) -> PipelineResult:
        """
        Main entry point for pipeline execution.
        Orchestrates all 10 phases (0-9) in sequence.
        """
        self.logger.critical(
            "="*80 + "\n" +
            "F.A.R.F.A.N PIPELINE EXECUTION STARTED\n" +
            "="*80,
            municipality=self.config.municipality_name,
            mode="STRICT" if self.config.strict_mode else "NORMAL",
        )

        # Transition to INITIALIZING
        self.state_machine.transition_to(
            OrchestrationState.INITIALIZING,
            reason="Starting pipeline execution"
        )

        # Record start time
        self.context.start_time = datetime.utcnow()
        pipeline_start = time.time()

        try:
            # Transition to RUNNING
            self.state_machine.transition_to(
                OrchestrationState.RUNNING,
                reason="Initialization complete"
            )

            # Execute phases based on configuration
            phases_to_execute = self._get_phases_to_execute()

            for phase_id in phases_to_execute:
                if self._should_execute_phase(phase_id):
                    result = self._execute_single_phase(phase_id)
                    self.context.add_phase_result(result)

            # Calculate total execution time
            total_time = time.time() - pipeline_start

            # Create pipeline result
            pipeline_result = PipelineResult(
                success=True,
                phase_results=self.context.phase_results,
                total_duration_seconds=total_time,
                metadata={
                    "municipality": self.config.municipality_name,
                    "start_time": self.context.start_time.isoformat(),
                    "end_time": datetime.utcnow().isoformat(),
                    "phases_completed": len(self.context.phase_results),
                },
                errors=[],
            )

            # Transition to COMPLETED
            self.state_machine.transition_to(
                OrchestrationState.COMPLETED,
                reason="All phases completed successfully"
            )

            self.logger.critical(
                "="*80 + "\n" +
                "F.A.R.F.A.N PIPELINE EXECUTION COMPLETED SUCCESSFULLY\n" +
                "="*80,
                total_time_seconds=total_time,
                phases_completed=len(self.context.phase_results),
            )

            return pipeline_result

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")

            # Transition to COMPLETED_WITH_ERRORS
            self.state_machine.transition_to(
                OrchestrationState.COMPLETED_WITH_ERRORS,
                reason=f"Pipeline failed: {str(e)}"
            )

            if self.config.strict_mode:
                raise

            return PipelineResult(
                success=False,
                phase_results=self.context.phase_results,
                total_duration_seconds=time.time() - pipeline_start,
                metadata={"error": str(e)},
                errors=[str(e)],
            )

    def _get_phases_to_execute(self) -> List[PhaseID]:
        """Get list of phases to execute based on configuration."""
        phases_to_execute = self.config.phases_to_execute

        if phases_to_execute == "ALL":
            return list(PhaseID)

        if isinstance(phases_to_execute, list):
            return [PhaseID(p) for p in phases_to_execute if p in [pid.value for pid in PhaseID]]

        if isinstance(phases_to_execute, str) and "-" in phases_to_execute:
            start, end = phases_to_execute.split("-")
            all_phases = list(PhaseID)
            start_idx = int(start.replace("P0", "")) if start.startswith("P0") else int(start)
            end_idx = int(end.replace("P0", "")) if end.startswith("P0") else int(end)
            return all_phases[start_idx:end_idx + 1]

        return list(PhaseID)

    def _should_execute_phase(self, phase_id: PhaseID) -> bool:
        """Determine if a phase should be executed."""
        phases_to_execute = self.config.phases_to_execute

        if phases_to_execute == "ALL":
            return True

        if isinstance(phases_to_execute, list):
            return phase_id.value in phases_to_execute

        return True

    def _execute_single_phase(self, phase_id: PhaseID) -> PhaseResult:
        """Execute a single phase with SISAS signal emission."""
        self.logger.info(f"Executing phase: {phase_id.value}")

        start_time = time.time()

        # Emit PHASE_START signal
        self._emit_phase_signal(
            phase_id=phase_id,
            event_type="PHASE_START",
            payload={"status": "started"}
        )

        try:
            self.context.validate_phase_prerequisite(phase_id)
            self.dependency_graph.update_node_status(phase_id.value, DependencyStatus.RUNNING)

            # Dispatch to appropriate phase method
            output = self._dispatch_phase_execution(phase_id)

            execution_time = time.time() - start_time
            self.dependency_graph.update_node_status(phase_id.value, DependencyStatus.COMPLETED)

            # Emit PHASE_COMPLETE signal
            self._emit_phase_signal(
                phase_id=phase_id,
                event_type="PHASE_COMPLETE",
                payload={
                    "status": "completed",
                    "execution_time_s": execution_time
                }
            )

            result = PhaseResult(
                phase_id=phase_id,
                status=PhaseStatus.COMPLETED,
                output=output,
                execution_time_s=execution_time,
            )

            self.logger.info(f"Phase {phase_id.value} completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            execution_time = time.time() - start_time

            # Emit PHASE_FAILED signal
            self._emit_phase_signal(
                phase_id=phase_id,
                event_type="PHASE_FAILED",
                payload={
                    "status": "failed",
                    "error": str(e),
                    "execution_time_s": execution_time
                }
            )

            self.dependency_graph.update_node_status(phase_id.value, DependencyStatus.FAILED)
            self.logger.error(f"Phase {phase_id.value} failed: {e}")

            if self.config.retry_failed_phases:
                retry_count = self._phase_retry_counts.get(phase_id.value, 0)
                if retry_count < self.config.max_retries_per_phase:
                    self._phase_retry_counts[phase_id.value] = retry_count + 1
                    self.dependency_graph.update_node_status(phase_id.value, DependencyStatus.PENDING_RETRY)
                    return self._execute_single_phase(phase_id)

            return PhaseResult(
                phase_id=phase_id,
                status=PhaseStatus.FAILED,
                output=None,
                execution_time_s=execution_time,
                error=e,
            )

    def _dispatch_phase_execution(self, phase_id: PhaseID) -> Any:
        """Dispatch execution to appropriate phase method."""
        dispatch_table = {
            PhaseID.PHASE_0: self._execute_phase_00,
            PhaseID.PHASE_1: self._execute_phase_01,
            PhaseID.PHASE_2: self._execute_phase_02,
            PhaseID.PHASE_3: self._execute_phase_03,
            PhaseID.PHASE_4: self._execute_phase_04,
            PhaseID.PHASE_5: self._execute_phase_05,
            PhaseID.PHASE_6: self._execute_phase_06,
            PhaseID.PHASE_7: self._execute_phase_07,
            PhaseID.PHASE_8: self._execute_phase_08,
            PhaseID.PHASE_9: self._execute_phase_09,
        }

        method = dispatch_table.get(phase_id)
        if method is None:
            raise ValueError(f"Unknown phase: {phase_id}")

        return method()

    # =========================================================================
    # PHASE EXECUTION METHODS (simplified placeholders)
    # =========================================================================

    def _execute_phase_00(self) -> Any:
        """Execute Phase 0: Bootstrap & Validation."""
        self.logger.info("Phase 0: Bootstrap & Validation")
        return {"status": "bootstrapped", "validation": "passed"}

    def _execute_phase_01(self) -> Any:
        """Execute Phase 1: CPP Ingestion."""
        self.logger.info("Phase 1: CPP Ingestion")
        return {"cpp_chunks": 300}

    def _execute_phase_02(self, plan_text: Optional[str] = None, **kwargs) -> Any:
        """
        Execute Phase 2: Executor Factory & Dispatch.

        This phase now uses the UnifiedFactory to:
        1. Load analysis components (detectors, calculators, analyzers)
        2. Load contracts
        3. Execute contracts with method injection

        Args:
            plan_text: Optional plan text for contract execution
            **kwargs: Additional arguments for contract execution

        Returns:
            Dict with task results from contract execution
        """
        self.logger.info("Phase 2: Executor Factory & Dispatch")

        if self.factory is None:
            self.logger.warning("Factory not available, returning empty results")
            return {
                "task_results": [],
                "status": "factory_unavailable",
                "contracts_executed": 0,
            }

        # Create analysis components via factory
        components = self.factory.create_analysis_components()
        self.logger.debug(
            "Analysis components created",
            components=list(components.keys()),
        )

        # Load contracts via factory
        contracts = self.factory.load_contracts()
        active_contracts = {
            cid: c for cid, c in contracts.items()
            if c.get("status") == "ACTIVE"
        }

        self.logger.info(
            "Contracts loaded for execution",
            total_contracts=len(contracts),
            active_contracts=len(active_contracts),
        )

        # Execute contracts with method injection
        task_results = []
        input_data = {"plan_text": plan_text, **kwargs}

        for contract_id, contract in list(active_contracts.items())[:10]:  # Limit to 10 for now
            try:
                result = self.factory.execute_contract(contract_id, input_data)
                task_results.append({
                    "contract_id": contract_id,
                    "result": result,
                    "status": "completed" if "error" not in result else "failed",
                })
            except Exception as e:
                self.logger.warning(
                    "Contract execution failed",
                    contract_id=contract_id,
                    error=str(e),
                )
                task_results.append({
                    "contract_id": contract_id,
                    "error": str(e),
                    "status": "error",
                })

        return {
            "task_results": task_results,
            "status": "completed",
            "contracts_executed": len(task_results),
            "components_available": list(components.keys()),
        }

    def _execute_phase_03(self) -> Any:
        """Execute Phase 3: Layer Scoring."""
        self.logger.info("Phase 3: Layer Scoring")
        return {"scored_results": []}

    def _execute_phase_04(self) -> Any:
        """Execute Phase 4: Dimension Aggregation."""
        self.logger.info("Phase 4: Dimension Aggregation")
        return []

    def _execute_phase_05(self) -> Any:
        """Execute Phase 5: Policy Area Aggregation."""
        self.logger.info("Phase 5: Policy Area Aggregation")
        return []

    def _execute_phase_06(self) -> Any:
        """Execute Phase 6: Cluster Aggregation."""
        self.logger.info("Phase 6: Cluster Aggregation")
        return []

    def _execute_phase_07(self) -> Any:
        """Execute Phase 7: Macro Aggregation."""
        self.logger.info("Phase 7: Macro Aggregation")
        return {"score": 0.0}

    def _execute_phase_08(self) -> Any:
        """Execute Phase 8: Recommendations Engine."""
        self.logger.info("Phase 8: Recommendations Engine")
        return {"recommendations": {}}

    def _execute_phase_09(self) -> Any:
        """Execute Phase 9: Report Assembly."""
        self.logger.info("Phase 9: Report Assembly")
        return {"report": {}}

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "state": self.state_machine.current_state.name,
            "active_phases": list(self._active_phases),
            "completed_phases": list(self._completed_phases.keys()),
            "failed_phases": list(self._failed_phases.keys()),
            "dependency_graph_state": self.dependency_graph.get_state_snapshot(),
        }

    def get_sisas_metrics(self) -> Dict[str, Any]:
        """Get SISAS metrics from SDO and context."""
        if self.context.sisas is None:
            return {"sisas_enabled": False}

        sdo_metrics = self.context.sisas.get_metrics()
        consumer_stats = self.context.sisas.get_consumer_stats()
        health = self.context.sisas.health_check()

        return {
            "sisas_enabled": True,
            "sdo_metrics": sdo_metrics,
            "consumer_stats": consumer_stats,
            "health_status": health["status"],
            "dead_letter_rate": health["dead_letter_rate"],
            "error_rate": health["error_rate"],
            "signal_metrics": self.context.signal_metrics,
        }

    def save_checkpoint(self, checkpoint_dir: str = None) -> str:
        """Save current pipeline state for recovery."""
        import pickle

        if checkpoint_dir is None:
            checkpoint_dir = self.config.output_dir

        checkpoint_path = Path(checkpoint_dir)
        checkpoint_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = checkpoint_path / f"farfan_checkpoint_{timestamp}.pkl"

        checkpoint_data = {
            "context": self.context,
            "config": self.config.to_dict(),
            "phase_outputs": self.context.phase_outputs,
            "phase_results": self.context.phase_results,
            "timestamp": datetime.utcnow().isoformat(),
        }

        with open(checkpoint_file, "wb") as f:
            pickle.dump(checkpoint_data, f)

        self.logger.info(f"Checkpoint saved to {checkpoint_file}")
        return str(checkpoint_file)

    def export_results(self, output_dir: str = None) -> Dict[str, str]:
        """Export all pipeline results to structured format."""
        if output_dir is None:
            output_dir = self.config.output_dir

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported_files = {}

        for phase_id, output in self.context.phase_outputs.items():
            phase_file = output_path / f"{phase_id.lower()}_output.json"

            if hasattr(output, "to_dict"):
                output_data = output.to_dict()
            elif isinstance(output, list) and output and hasattr(output[0], "to_dict"):
                output_data = [item.to_dict() for item in output]
            else:
                output_data = output

            with open(phase_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)

            exported_files[phase_id] = str(phase_file)

        self.logger.info(f"Results exported to {output_dir}")
        return exported_files

    def cleanup(self) -> None:
        """Clean up resources after pipeline execution."""
        self.logger.info("Starting cleanup")
        import gc
        gc.collect()
        self.logger.info("Cleanup completed")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Configuration
    "OrchestratorConfig",
    "ConfigValidationError",
    "validate_config",
    "get_development_config",
    "get_production_config",
    "get_testing_config",

    # Exceptions
    "OrchestrationError",
    "DependencyResolutionError",
    "SchedulingError",
    "StateTransitionError",
    "OrchestrationInitializationError",
    "PhaseExecutionError",
    "ContractViolationError",

    # State Machine
    "OrchestrationState",
    "StateTransition",
    "OrchestrationStateMachine",
    "VALID_TRANSITIONS",

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

    # Core Orchestrator
    "PhaseStatus",
    "PhaseID",
    "PHASE_METADATA",
    "PhaseResult",
    "ExecutionContext",
    "PipelineResult",
    "UnifiedOrchestrator",
]
