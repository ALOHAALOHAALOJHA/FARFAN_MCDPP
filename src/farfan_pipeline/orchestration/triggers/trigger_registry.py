"""
Trigger Registry - Core trigger system with priority enforcement and circuit breakers.

This module provides the foundational trigger infrastructure:
- TriggerPriority: Enum for priority-based execution ordering
- TriggerEvent: Immutable event data structure
- TriggerRegistry: Central registry with priority-ordered emission
- CircuitBreaker: Fault tolerance for trigger callbacks

Features:
- Thread-safe registration and emission
- Priority-based execution ordering (CRITICAL > HIGH > MEDIUM > LOW > BACKGROUND)
- Circuit breakers for fault tolerance
- Comprehensive metrics and diagnostics

Author: FARFAN Pipeline Team
Version: 3.0.0
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

__all__ = [
    # Priority
    "TriggerPriority",
    # Core classes
    "TriggerRegistry",
    "TriggerEvent",
    "TriggerContext",
    "TriggerCallback",
    "TriggerCondition",
    "TriggerState",
    "TriggerMetrics",
    "RegisteredTrigger",
    "TriggerResult",
    # Circuit Breaker
    "CircuitBreakerConfig",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    # Enums
    "EventCategory",
    "EVENT_CATEGORIES",
    # Module-level functions
    "get_registry",
    "register_trigger",
    "emit_trigger",
    "on_event",
]


# =============================================================================
# PRIORITY SYSTEM
# =============================================================================


class TriggerPriority(IntEnum):
    """Trigger priority levels (higher = more important, executed first)."""

    CRITICAL = 100  # System-level triggers (errors, aborts)
    HIGH = 75  # Phase transitions, veto gates
    MEDIUM = 50  # Sub-phase completion, validation
    LOW = 25  # Metrics, logging, diagnostics
    BACKGROUND = 1  # Telemetry, analytics


# =============================================================================
# EVENT CATEGORIES
# =============================================================================


class EventCategory(str, Enum):
    """Categories of trigger events."""

    PHASE = "phase"
    SUBPHASE = "subphase"
    CONTRACT = "contract"
    EXTRACTION = "extraction"
    VALIDATION = "validation"
    SYSTEM = "system"


# Pre-defined event category mappings
EVENT_CATEGORIES: Dict[str, EventCategory] = {
    # Phase events
    "PHASE_INITIALIZING": EventCategory.PHASE,
    "PHASE_VALIDATING_PREREQUISITES": EventCategory.PHASE,
    "PHASE_EXECUTING": EventCategory.PHASE,
    "PHASE_FINALIZING": EventCategory.PHASE,
    "PHASE_COMPLETED": EventCategory.PHASE,
    "PHASE_FAILED": EventCategory.PHASE,
    # Subphase events
    "SUBPHASE_START": EventCategory.SUBPHASE,
    "SUBPHASE_END": EventCategory.SUBPHASE,
    # Contract events
    "CONTRACT_LOADING": EventCategory.CONTRACT,
    "CONTRACT_EXECUTING": EventCategory.CONTRACT,
    "CONTRACT_VETO": EventCategory.CONTRACT,
    "CONTRACT_COMPLETED": EventCategory.CONTRACT,
    # Extraction events
    "EXTRACTION_START": EventCategory.EXTRACTION,
    "EXTRACTION_COMPLETE": EventCategory.EXTRACTION,
    # Validation events
    "VALIDATION_START": EventCategory.VALIDATION,
    "VALIDATION_PASSED": EventCategory.VALIDATION,
    "VALIDATION_FAILED": EventCategory.VALIDATION,
    # System events
    "SYSTEM_ERROR": EventCategory.SYSTEM,
    "SYSTEM_WARNING": EventCategory.SYSTEM,
}


# =============================================================================
# TRIGGER STATE
# =============================================================================


class TriggerState(str, Enum):
    """State of a registered trigger."""

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass(frozen=True)
class TriggerEvent:
    """
    Immutable trigger event with priority.

    Attributes:
        event_id: Unique identifier for this event instance
        event_type: Type of event (e.g., "PHASE_COMPLETED")
        category: Event category for routing
        priority: Priority level for execution ordering
        payload: Additional event data
        timestamp: When the event was created
        source: Source component that emitted the event
        correlation_id: ID for tracing related events
    """

    event_id: str
    event_type: str
    category: EventCategory = EventCategory.SYSTEM
    priority: TriggerPriority = TriggerPriority.MEDIUM
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source: str = "unknown"
    correlation_id: Optional[str] = None

    # Predefined event types as class attributes for compatibility
    PHASE_INITIALIZING = "PHASE_INITIALIZING"
    PHASE_VALIDATING_PREREQUISITES = "PHASE_VALIDATING_PREREQUISITES"
    PHASE_EXECUTING = "PHASE_EXECUTING"
    PHASE_FINALIZING = "PHASE_FINALIZING"
    PHASE_COMPLETED = "PHASE_COMPLETED"
    PHASE_FAILED = "PHASE_FAILED"
    SUBPHASE_START = "SUBPHASE_START"
    SUBPHASE_END = "SUBPHASE_END"
    CONTRACT_LOADING = "CONTRACT_LOADING"
    CONTRACT_EXECUTING = "CONTRACT_EXECUTING"
    CONTRACT_VETO = "CONTRACT_VETO"
    CONTRACT_COMPLETED = "CONTRACT_COMPLETED"
    EXTRACTION_START = "EXTRACTION_START"
    EXTRACTION_COMPLETE = "EXTRACTION_COMPLETE"


@dataclass
class TriggerContext:
    """
    Mutable context passed to trigger callbacks.

    Attributes:
        event: The triggering event
        phase_id: Current phase ID
        metadata: Additional context data
        results: Results from prior callbacks in chain
    """

    event: TriggerEvent
    phase_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    results: List[Any] = field(default_factory=list)


@dataclass
class TriggerMetrics:
    """Metrics for a registered trigger."""

    invocation_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_execution_time_ms: float = 0.0
    last_invocation: Optional[datetime] = None
    last_error: Optional[str] = None

    @property
    def avg_execution_time_ms(self) -> float:
        """Calculate average execution time."""
        if self.invocation_count == 0:
            return 0.0
        return self.total_execution_time_ms / self.invocation_count

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.invocation_count == 0:
            return 100.0
        return (self.success_count / self.invocation_count) * 100


@dataclass
class TriggerResult:
    """Result from a trigger callback execution."""

    trigger_id: str
    success: bool
    priority: TriggerPriority
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


# Type aliases
TriggerCallback = Callable[[TriggerContext], Any]
TriggerCondition = Callable[[TriggerContext], bool]


@dataclass
class RegisteredTrigger:
    """A registered trigger with its callback and metadata."""

    trigger_id: str
    callback: TriggerCallback
    event_types: List[str]
    priority: TriggerPriority = TriggerPriority.MEDIUM
    state: TriggerState = TriggerState.ACTIVE
    condition: Optional[TriggerCondition] = None
    metrics: TriggerMetrics = field(default_factory=TriggerMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================


@dataclass(frozen=True)
class CircuitBreakerConfig:
    """Immutable circuit breaker configuration."""

    failure_threshold: int = 5  # Failures before opening
    timeout_seconds: float = 60.0  # How long to stay open
    half_open_attempts: int = 3  # Attempts in half-open state


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Circuit breaker for trigger callbacks."""

    def __init__(self, config: CircuitBreakerConfig = None):
        """Initialize circuit breaker with configuration."""
        self._config = config or CircuitBreakerConfig()
        self._state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_attempts = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        """Current circuit breaker state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Current failure count."""
        return self._failure_count

    def execute(self, callback: Callable, event: TriggerEvent) -> Any:
        """Execute callback with circuit breaker protection."""
        with self._lock:
            # Check if we should attempt execution
            if self._state == "OPEN":
                if self._last_failure_time is not None:
                    elapsed = time.time() - self._last_failure_time
                    if elapsed > self._config.timeout_seconds:
                        self._state = "HALF_OPEN"
                        self._half_open_attempts = 0
                        logger.info("Circuit breaker transitioning to HALF_OPEN")
                    else:
                        raise CircuitBreakerOpenError(
                            f"Circuit breaker is OPEN (retry in {self._config.timeout_seconds - elapsed:.1f}s)"
                        )

        # Execute callback (outside lock to avoid deadlock)
        try:
            result = callback(event)

            # Success handling
            with self._lock:
                if self._state == "HALF_OPEN":
                    self._half_open_attempts += 1
                    if self._half_open_attempts >= self._config.half_open_attempts:
                        self._state = "CLOSED"
                        self._failure_count = 0
                        logger.info("Circuit breaker CLOSED after recovery")
                elif self._state == "CLOSED":
                    self._failure_count = 0

            return result

        except Exception as e:
            # Failure handling
            with self._lock:
                self._failure_count += 1
                self._last_failure_time = time.time()

                if self._failure_count >= self._config.failure_threshold:
                    self._state = "OPEN"
                    logger.warning(
                        f"Circuit breaker OPEN after {self._failure_count} failures"
                    )

            raise e

    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED state."""
        with self._lock:
            self._state = "CLOSED"
            self._failure_count = 0
            self._last_failure_time = None
            self._half_open_attempts = 0
            logger.info("Circuit breaker manually reset to CLOSED")


# =============================================================================
# TRIGGER REGISTRY
# =============================================================================


class TriggerRegistry:
    """
    Registry with priority-based execution.

    Features:
    - Thread-safe registration and emission
    - Priority-ordered callback execution (CRITICAL first)
    - Circuit breaker integration for fault tolerance
    - Metrics tracking for each trigger
    - Bulk registration/deregistration
    """

    def __init__(
        self,
        enable_circuit_breaker: bool = True,
        circuit_breaker_config: CircuitBreakerConfig = None,
    ):
        """
        Initialize trigger registry.

        Args:
            enable_circuit_breaker: Whether to use circuit breakers
            circuit_breaker_config: Configuration for circuit breakers
        """
        self._triggers_by_id: Dict[str, RegisteredTrigger] = {}
        self._triggers_by_priority: Dict[TriggerPriority, List[str]] = {
            priority: [] for priority in TriggerPriority
        }
        self._triggers_by_event: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
        self._enable_circuit_breaker = enable_circuit_breaker
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._cb_config = circuit_breaker_config or CircuitBreakerConfig()
        self._emission_count = 0
        self._total_callbacks_executed = 0

    def __len__(self) -> int:
        """Return number of registered triggers."""
        return len(self._triggers_by_id)

    def register(
        self,
        trigger_id: str,
        callback: TriggerCallback,
        event_types: List[str],
        priority: TriggerPriority = TriggerPriority.MEDIUM,
        condition: Optional[TriggerCondition] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RegisteredTrigger:
        """
        Register trigger with priority.

        Args:
            trigger_id: Unique identifier for the trigger
            callback: Function to call when trigger fires
            event_types: List of event types this trigger handles
            priority: Execution priority (higher = executed first)
            condition: Optional predicate for conditional execution
            metadata: Optional metadata dict

        Returns:
            The registered trigger object
        """
        with self._lock:
            # Create trigger
            trigger = RegisteredTrigger(
                trigger_id=trigger_id,
                callback=callback,
                event_types=event_types,
                priority=priority,
                condition=condition,
                metadata=metadata or {},
            )

            # Store by ID
            self._triggers_by_id[trigger_id] = trigger

            # Index by priority
            if trigger_id not in self._triggers_by_priority[priority]:
                self._triggers_by_priority[priority].append(trigger_id)

            # Index by event type
            for event_type in event_types:
                if event_type not in self._triggers_by_event:
                    self._triggers_by_event[event_type] = []
                if trigger_id not in self._triggers_by_event[event_type]:
                    self._triggers_by_event[event_type].append(trigger_id)

            # Create circuit breaker if enabled
            if self._enable_circuit_breaker:
                self._circuit_breakers[trigger_id] = CircuitBreaker(self._cb_config)

            logger.debug(
                f"Registered trigger '{trigger_id}' with priority {priority.name} "
                f"for events: {event_types}"
            )

            return trigger

    def unregister(self, trigger_id: str) -> bool:
        """
        Unregister a trigger.

        Args:
            trigger_id: ID of trigger to remove

        Returns:
            True if trigger was removed, False if not found
        """
        with self._lock:
            if trigger_id not in self._triggers_by_id:
                return False

            trigger = self._triggers_by_id.pop(trigger_id)

            # Remove from priority index
            priority_list = self._triggers_by_priority.get(trigger.priority, [])
            if trigger_id in priority_list:
                priority_list.remove(trigger_id)

            # Remove from event type index
            for event_type in trigger.event_types:
                event_list = self._triggers_by_event.get(event_type, [])
                if trigger_id in event_list:
                    event_list.remove(trigger_id)

            # Remove circuit breaker
            self._circuit_breakers.pop(trigger_id, None)

            logger.debug(f"Unregistered trigger '{trigger_id}'")
            return True

    def emit(self, event: TriggerEvent) -> List[TriggerResult]:
        """
        Emit event with priority-ordered callback execution.

        Callbacks are executed in priority order (CRITICAL first, BACKGROUND last).
        Within the same priority level, order is deterministic (registration order).

        Args:
            event: The event to emit

        Returns:
            List of TriggerResult from each callback
        """
        self._emission_count += 1

        # Collect callbacks by priority (sorted descending)
        callbacks_to_execute: List[tuple] = []

        with self._lock:
            # Iterate priorities from highest to lowest
            for priority in sorted(TriggerPriority, reverse=True):
                for trigger_id in self._triggers_by_priority[priority]:
                    trigger = self._triggers_by_id.get(trigger_id)
                    if trigger is None:
                        continue

                    # Check if this trigger handles this event type
                    if event.event_type not in trigger.event_types:
                        continue

                    # Check if trigger is active
                    if trigger.state != TriggerState.ACTIVE:
                        continue

                    callbacks_to_execute.append((priority, trigger_id, trigger))

        # Execute in priority order (deterministic!)
        results: List[TriggerResult] = []
        context = TriggerContext(event=event)

        for priority, trigger_id, trigger in callbacks_to_execute:
            start_time = time.perf_counter()

            try:
                # Check condition if present
                if trigger.condition is not None:
                    try:
                        if not trigger.condition(context):
                            logger.debug(
                                f"Trigger '{trigger_id}' skipped: condition not met"
                            )
                            continue
                    except Exception as cond_error:
                        logger.warning(
                            f"Trigger '{trigger_id}' condition check failed: {cond_error}"
                        )
                        continue

                # Execute with circuit breaker if enabled
                if self._enable_circuit_breaker and trigger_id in self._circuit_breakers:
                    cb = self._circuit_breakers[trigger_id]
                    try:
                        result = cb.execute(trigger.callback, context)
                    except CircuitBreakerOpenError as cbo:
                        logger.warning(f"Trigger '{trigger_id}' blocked: {cbo}")
                        results.append(
                            TriggerResult(
                                trigger_id=trigger_id,
                                success=False,
                                error=str(cbo),
                                priority=priority,
                            )
                        )
                        continue
                else:
                    result = trigger.callback(context)

                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # Update metrics
                with self._lock:
                    if trigger_id in self._triggers_by_id:
                        trigger.metrics.invocation_count += 1
                        trigger.metrics.success_count += 1
                        trigger.metrics.total_execution_time_ms += elapsed_ms
                        trigger.metrics.last_invocation = datetime.utcnow()

                self._total_callbacks_executed += 1

                results.append(
                    TriggerResult(
                        trigger_id=trigger_id,
                        success=True,
                        result=result,
                        priority=priority,
                        execution_time_ms=elapsed_ms,
                    )
                )

                # Add result to context for chaining
                context.results.append(result)

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # Update metrics
                with self._lock:
                    if trigger_id in self._triggers_by_id:
                        trigger.metrics.invocation_count += 1
                        trigger.metrics.failure_count += 1
                        trigger.metrics.last_error = str(e)
                        trigger.metrics.last_invocation = datetime.utcnow()

                logger.error(f"Trigger '{trigger_id}' failed: {e}")

                results.append(
                    TriggerResult(
                        trigger_id=trigger_id,
                        success=False,
                        error=str(e),
                        priority=priority,
                        execution_time_ms=elapsed_ms,
                    )
                )

        return results

    def get_trigger(self, trigger_id: str) -> Optional[RegisteredTrigger]:
        """Get a registered trigger by ID."""
        return self._triggers_by_id.get(trigger_id)

    def get_triggers_by_event(self, event_type: str) -> List[RegisteredTrigger]:
        """Get all triggers for an event type."""
        with self._lock:
            trigger_ids = self._triggers_by_event.get(event_type, [])
            return [
                self._triggers_by_id[tid]
                for tid in trigger_ids
                if tid in self._triggers_by_id
            ]

    def clear(self) -> int:
        """Clear all triggers. Returns count of removed triggers."""
        with self._lock:
            count = len(self._triggers_by_id)
            self._triggers_by_id.clear()
            for priority in TriggerPriority:
                self._triggers_by_priority[priority].clear()
            self._triggers_by_event.clear()
            self._circuit_breakers.clear()
            return count

    def health_check(self) -> Dict[str, Any]:
        """Get health check information."""
        with self._lock:
            triggers_by_state = {state.value: 0 for state in TriggerState}
            for trigger in self._triggers_by_id.values():
                triggers_by_state[trigger.state.value] += 1

            circuit_breaker_states = {}
            if self._enable_circuit_breaker:
                for tid, cb in self._circuit_breakers.items():
                    circuit_breaker_states[tid] = cb.state

            return {
                "total_triggers": len(self._triggers_by_id),
                "triggers_by_state": triggers_by_state,
                "triggers_by_priority": {
                    p.name: len(ids) for p, ids in self._triggers_by_priority.items()
                },
                "emission_count": self._emission_count,
                "total_callbacks_executed": self._total_callbacks_executed,
                "circuit_breakers_enabled": self._enable_circuit_breaker,
                "circuit_breaker_states": circuit_breaker_states,
            }


# =============================================================================
# MODULE-LEVEL SINGLETON AND CONVENIENCE FUNCTIONS
# =============================================================================

_registry_singleton: Optional[TriggerRegistry] = None
_singleton_lock = threading.Lock()


def get_registry() -> TriggerRegistry:
    """Get the singleton TriggerRegistry instance."""
    global _registry_singleton
    with _singleton_lock:
        if _registry_singleton is None:
            _registry_singleton = TriggerRegistry()
        return _registry_singleton


def register_trigger(
    trigger_id: str,
    callback: TriggerCallback,
    event_types: List[str],
    priority: TriggerPriority = TriggerPriority.MEDIUM,
    **kwargs,
) -> RegisteredTrigger:
    """Convenience function to register a trigger on the singleton registry."""
    return get_registry().register(
        trigger_id=trigger_id,
        callback=callback,
        event_types=event_types,
        priority=priority,
        **kwargs,
    )


def emit_trigger(event: TriggerEvent) -> List[TriggerResult]:
    """Convenience function to emit an event on the singleton registry."""
    return get_registry().emit(event)


def on_event(
    event_types: Union[str, List[str]],
    priority: TriggerPriority = TriggerPriority.MEDIUM,
    trigger_id: Optional[str] = None,
):
    """
    Decorator for registering a function as a trigger callback.

    Usage:
        @on_event("PHASE_COMPLETED", priority=TriggerPriority.HIGH)
        def handle_phase_complete(ctx: TriggerContext):
            print(f"Phase completed: {ctx.event.payload}")

    Args:
        event_types: Event type(s) to handle
        priority: Execution priority
        trigger_id: Optional custom trigger ID (auto-generated if not provided)

    Returns:
        Decorator function
    """
    if isinstance(event_types, str):
        event_types = [event_types]

    def decorator(func: TriggerCallback) -> TriggerCallback:
        tid = trigger_id or f"{func.__module__}.{func.__name__}_{uuid.uuid4().hex[:8]}"
        register_trigger(
            trigger_id=tid,
            callback=func,
            event_types=event_types,
            priority=priority,
        )
        return func

    return decorator
