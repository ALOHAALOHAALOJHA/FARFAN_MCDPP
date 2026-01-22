"""
SubPhase Triggers - Phase-level event triggers.

Provides fine-grained triggers within phase execution with advanced features:
- Thread-safe registration and emission
- Bulk registration/deregistration
- Introspection and diagnostics
- Conditional trigger execution
- Metrics and timing
- Decorator-based registration
"""

from typing import Optional, Dict, Any, Callable, List, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from functools import wraps
from enum import Enum
import logging
import threading
import time
import uuid

from .trigger_registry import TriggerRegistry, TriggerEvent, TriggerContext, register_trigger

logger = logging.getLogger(__name__)


class TriggerState(str, Enum):
    """State of a registered trigger."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


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
class TriggerRegistration:
    """Extended registration info for a subphase trigger."""
    registration_id: str
    event: TriggerEvent
    phase_id: str
    name: str
    priority: int
    state: TriggerState = TriggerState.ACTIVE
    condition: Optional[Callable[[TriggerContext], bool]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: TriggerMetrics = field(default_factory=TriggerMetrics)
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: Set[str] = field(default_factory=set)


class SubPhaseTriggers:
    """
    Manager for sub-phase level triggers.

    These triggers emit at specific points within phase execution:
    - Phase initialization
    - Prerequisite validation
    - Phase execution start/end
    - Phase finalization

    Features:
    - Thread-safe operations
    - Conditional execution
    - Bulk operations
    - Metrics tracking
    - Introspection utilities
    - Context managers for scoped triggers
    """

    # Class-level event mapping for DRY registration
    _EVENT_MAP: Dict[str, TriggerEvent] = {
        "initializing": TriggerEvent.PHASE_INITIALIZING,
        "validating": TriggerEvent.PHASE_VALIDATING_PREREQUISITES,
        "executing": TriggerEvent.PHASE_EXECUTING,
        "finalizing": TriggerEvent.PHASE_FINALIZING,
    }

    def __init__(self, registry: Optional[TriggerRegistry] = None):
        """
        Initialize SubPhaseTriggers.

        Args:
            registry: Optional TriggerRegistry instance (uses singleton if None)
        """
        from .trigger_registry import TriggerRegistry
        self._registry = registry or TriggerRegistry()
        self._lock = threading.RLock()
        self._registrations: Dict[str, TriggerRegistration] = {}
        self._phase_registrations: Dict[str, Set[str]] = {}  # phase_id -> registration_ids
        self._event_registrations: Dict[TriggerEvent, Set[str]] = {}  # event -> registration_ids
        self._emission_history: List[Dict[str, Any]] = []
        self._max_history_size: int = 1000

    # ═══════════════════════════════════════════════════════════════════════════
    # CORE REGISTRATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _register_internal(
        self,
        event: TriggerEvent,
        phase_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Internal registration with full feature support.

        Args:
            event: The trigger event type
            phase_id: The phase ID to scope the trigger
            callback: Function to call when trigger fires
            priority: Execution priority (higher = first)
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        registration_id = str(uuid.uuid4())[:12]
        trigger_name = name or f"{event.name.lower()}_{phase_id}_{registration_id}"

        # Create registration record
        registration = TriggerRegistration(
            registration_id=registration_id,
            event=event,
            phase_id=phase_id,
            name=trigger_name,
            priority=priority,
            condition=condition,
            metadata=metadata or {},
            tags=tags or set(),
        )

        # Create wrapped callback with metrics and condition
        @wraps(callback)
        def instrumented_callback(ctx: TriggerContext) -> None:
            with self._lock:
                reg = self._registrations.get(registration_id)
                if not reg or reg.state != TriggerState.ACTIVE:
                    return

            # Apply phase_id to context
            ctx.phase_id = phase_id

            # Check condition
            if registration.condition is not None:
                try:
                    if not registration.condition(ctx):
                        logger.debug(f"Trigger '{trigger_name}' skipped: condition not met")
                        return
                except Exception as e:
                    logger.warning(f"Trigger '{trigger_name}' condition check failed: {e}")
                    return

            # Execute with timing
            start_time = time.perf_counter()
            try:
                callback(ctx)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                with self._lock:
                    if registration_id in self._registrations:
                        reg = self._registrations[registration_id]
                        reg.metrics.invocation_count += 1
                        reg.metrics.success_count += 1
                        reg.metrics.total_execution_time_ms += elapsed_ms
                        reg.metrics.last_invocation = datetime.utcnow()

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"Trigger '{trigger_name}' failed after {elapsed_ms:.2f}ms: {e}")

                with self._lock:
                    if registration_id in self._registrations:
                        reg = self._registrations[registration_id]
                        reg.metrics.invocation_count += 1
                        reg.metrics.failure_count += 1
                        reg.metrics.total_execution_time_ms += elapsed_ms
                        reg.metrics.last_invocation = datetime.utcnow()
                        reg.metrics.last_error = str(e)
                raise

        # Register with underlying registry
        with self._lock:
            self._registry.register(
                event,
                instrumented_callback,
                priority=priority,
                name=trigger_name,
            )

            # Track registration
            self._registrations[registration_id] = registration

            # Index by phase
            if phase_id not in self._phase_registrations:
                self._phase_registrations[phase_id] = set()
            self._phase_registrations[phase_id].add(registration_id)

            # Index by event
            if event not in self._event_registrations:
                self._event_registrations[event] = set()
            self._event_registrations[event].add(registration_id)

        logger.debug(f"Registered subphase trigger '{trigger_name}' for {event.value} on {phase_id}")
        return registration_id

    def on_phase_initializing(
        self,
        phase_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for phase initialization.

        Args:
            phase_id: The phase ID (e.g., "phase_1")
            callback: Function to call when phase initializes
            priority: Execution priority (higher executes first)
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.PHASE_INITIALIZING,
            phase_id,
            callback,
            priority,
            name or f"phase_init_{phase_id}",
            condition,
            metadata,
            tags,
        )

    def on_phase_validating_prerequisites(
        self,
        phase_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for prerequisite validation.

        Args:
            phase_id: The phase ID
            callback: Function to call when validating prerequisites
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.PHASE_VALIDATING_PREREQUISITES,
            phase_id,
            callback,
            priority,
            name or f"phase_validate_{phase_id}",
            condition,
            metadata,
            tags,
        )

    def on_phase_executing(
        self,
        phase_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for phase execution.

        Args:
            phase_id: The phase ID
            callback: Function to call when phase executes
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.PHASE_EXECUTING,
            phase_id,
            callback,
            priority,
            name or f"phase_execute_{phase_id}",
            condition,
            metadata,
            tags,
        )

    def on_phase_finalizing(
        self,
        phase_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for phase finalization.

        Args:
            phase_id: The phase ID
            callback: Function to call when phase finalizes
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.PHASE_FINALIZING,
            phase_id,
            callback,
            priority,
            name or f"phase_finalize_{phase_id}",
            condition,
            metadata,
            tags,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # BULK REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════════

    def register_phase_lifecycle(
        self,
        phase_id: str,
        on_init: Optional[Callable[[TriggerContext], None]] = None,
        on_validate: Optional[Callable[[TriggerContext], None]] = None,
        on_execute: Optional[Callable[[TriggerContext], None]] = None,
        on_finalize: Optional[Callable[[TriggerContext], None]] = None,
        priority: int = 0,
        tags: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Register callbacks for all lifecycle events of a phase.

        Args:
            phase_id: The phase ID
            on_init: Callback for initialization
            on_validate: Callback for prerequisite validation
            on_execute: Callback for execution
            on_finalize: Callback for finalization
            priority: Execution priority for all callbacks
            tags: Tags to apply to all registrations

        Returns:
            List of registration IDs
        """
        registration_ids = []
        lifecycle_tags = (tags or set()) | {f"lifecycle_{phase_id}"}

        if on_init:
            reg_id = self.on_phase_initializing(
                phase_id, on_init, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_validate:
            reg_id = self.on_phase_validating_prerequisites(
                phase_id, on_validate, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_execute:
            reg_id = self.on_phase_executing(
                phase_id, on_execute, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_finalize:
            reg_id = self.on_phase_finalizing(
                phase_id, on_finalize, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        logger.info(f"Registered {len(registration_ids)} lifecycle triggers for {phase_id}")
        return registration_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # EMISSION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _emit_internal(
        self,
        event: TriggerEvent,
        phase_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Internal emission with history tracking.

        Args:
            event: The event to emit
            phase_id: The phase ID
            payload: Optional payload data

        Returns:
            Number of triggers executed
        """
        context = TriggerContext(
            event=event,
            timestamp=datetime.utcnow(),
            phase_id=phase_id,
            payload=payload or {},
        )

        start_time = time.perf_counter()
        executed = self._registry.emit(event, context)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Record history
        history_entry = {
            "event": event.value,
            "phase_id": phase_id,
            "timestamp": context.timestamp.isoformat(),
            "triggers_executed": executed,
            "execution_time_ms": round(elapsed_ms, 2),
            "payload_keys": list((payload or {}).keys()),
        }

        with self._lock:
            self._emission_history.append(history_entry)
            if len(self._emission_history) > self._max_history_size:
                self._emission_history = self._emission_history[-self._max_history_size:]

        logger.debug(
            f"Emitted {event.value} for {phase_id}: "
            f"{executed} triggers in {elapsed_ms:.2f}ms"
        )
        return executed

    def emit_phase_initializing(
        self, phase_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit phase initializing event."""
        return self._emit_internal(TriggerEvent.PHASE_INITIALIZING, phase_id, payload)

    def emit_phase_validating_prerequisites(
        self, phase_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit prerequisite validation event."""
        return self._emit_internal(
            TriggerEvent.PHASE_VALIDATING_PREREQUISITES, phase_id, payload
        )

    def emit_phase_executing(
        self, phase_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit phase executing event."""
        return self._emit_internal(TriggerEvent.PHASE_EXECUTING, phase_id, payload)

    def emit_phase_finalizing(
        self, phase_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit phase finalizing event."""
        return self._emit_internal(TriggerEvent.PHASE_FINALIZING, phase_id, payload)

    def emit_phase_lifecycle(
        self,
        phase_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """
        Emit all lifecycle events for a phase in sequence.

        Args:
            phase_id: The phase ID
            payload: Payload to pass to all events

        Returns:
            Dict mapping event names to execution counts
        """
        results = {}
        results["initializing"] = self.emit_phase_initializing(phase_id, payload)
        results["validating"] = self.emit_phase_validating_prerequisites(phase_id, payload)
        results["executing"] = self.emit_phase_executing(phase_id, payload)
        results["finalizing"] = self.emit_phase_finalizing(phase_id, payload)
        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # DEREGISTRATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def unregister(self, registration_id: str) -> bool:
        """
        Unregister a trigger by its registration ID.

        Args:
            registration_id: The registration ID returned from registration

        Returns:
            True if successfully unregistered
        """
        with self._lock:
            if registration_id not in self._registrations:
                return False

            reg = self._registrations[registration_id]

            # Remove from registry
            self._registry.unregister(reg.event, reg.name)

            # Remove from indices
            if reg.phase_id in self._phase_registrations:
                self._phase_registrations[reg.phase_id].discard(registration_id)
            if reg.event in self._event_registrations:
                self._event_registrations[reg.event].discard(registration_id)

            # Remove registration
            del self._registrations[registration_id]

        logger.debug(f"Unregistered trigger '{reg.name}'")
        return True

    def unregister_phase(self, phase_id: str) -> int:
        """
        Unregister all triggers for a specific phase.

        Args:
            phase_id: The phase ID

        Returns:
            Number of triggers unregistered
        """
        with self._lock:
            reg_ids = list(self._phase_registrations.get(phase_id, set()))

        count = 0
        for reg_id in reg_ids:
            if self.unregister(reg_id):
                count += 1

        logger.info(f"Unregistered {count} triggers for phase {phase_id}")
        return count

    def unregister_by_tag(self, tag: str) -> int:
        """
        Unregister all triggers with a specific tag.

        Args:
            tag: The tag to match

        Returns:
            Number of triggers unregistered
        """
        with self._lock:
            matching_ids = [
                reg_id
                for reg_id, reg in self._registrations.items()
                if tag in reg.tags
            ]

        count = 0
        for reg_id in matching_ids:
            if self.unregister(reg_id):
                count += 1

        logger.info(f"Unregistered {count} triggers with tag '{tag}'")
        return count

    def clear_all(self) -> int:
        """
        Clear all registered subphase triggers.

        Returns:
            Number of triggers cleared
        """
        with self._lock:
            count = len(self._registrations)
            reg_ids = list(self._registrations.keys())

        for reg_id in reg_ids:
            self.unregister(reg_id)

        logger.info(f"Cleared {count} subphase triggers")
        return count

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    def pause(self, registration_id: str) -> bool:
        """Pause a trigger (prevents execution but keeps registration)."""
        with self._lock:
            if registration_id in self._registrations:
                self._registrations[registration_id].state = TriggerState.PAUSED
                return True
        return False

    def resume(self, registration_id: str) -> bool:
        """Resume a paused trigger."""
        with self._lock:
            if registration_id in self._registrations:
                self._registrations[registration_id].state = TriggerState.ACTIVE
                return True
        return False

    def disable(self, registration_id: str) -> bool:
        """Disable a trigger."""
        with self._lock:
            if registration_id in self._registrations:
                self._registrations[registration_id].state = TriggerState.DISABLED
                return True
        return False

    def pause_phase(self, phase_id: str) -> int:
        """Pause all triggers for a phase."""
        with self._lock:
            reg_ids = self._phase_registrations.get(phase_id, set())
            count = 0
            for reg_id in reg_ids:
                if reg_id in self._registrations:
                    self._registrations[reg_id].state = TriggerState.PAUSED
                    count += 1
        return count

    def resume_phase(self, phase_id: str) -> int:
        """Resume all triggers for a phase."""
        with self._lock:
            reg_ids = self._phase_registrations.get(phase_id, set())
            count = 0
            for reg_id in reg_ids:
                if reg_id in self._registrations:
                    self._registrations[reg_id].state = TriggerState.ACTIVE
                    count += 1
        return count

    # ═══════════════════════════════════════════════════════════════════════════
    # INTROSPECTION & DIAGNOSTICS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_registration(self, registration_id: str) -> Optional[TriggerRegistration]:
        """Get registration details by ID."""
        with self._lock:
            return self._registrations.get(registration_id)

    def list_registrations(
        self,
        phase_id: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
        tag: Optional[str] = None,
        state: Optional[TriggerState] = None,
    ) -> List[TriggerRegistration]:
        """
        List registrations with optional filters.

        Args:
            phase_id: Filter by phase ID
            event: Filter by event type
            tag: Filter by tag
            state: Filter by state

        Returns:
            List of matching registrations
        """
        with self._lock:
            results = list(self._registrations.values())

        if phase_id is not None:
            results = [r for r in results if r.phase_id == phase_id]
        if event is not None:
            results = [r for r in results if r.event == event]
        if tag is not None:
            results = [r for r in results if tag in r.tags]
        if state is not None:
            results = [r for r in results if r.state == state]

        return results

    def get_metrics(self, registration_id: str) -> Optional[TriggerMetrics]:
        """Get metrics for a specific registration."""
        with self._lock:
            reg = self._registrations.get(registration_id)
            return reg.metrics if reg else None

    def get_aggregated_metrics(
        self, phase_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics across registrations.

        Args:
            phase_id: Optional filter by phase ID

        Returns:
            Aggregated metrics dict
        """
        registrations = self.list_registrations(phase_id=phase_id)

        total_invocations = sum(r.metrics.invocation_count for r in registrations)
        total_successes = sum(r.metrics.success_count for r in registrations)
        total_failures = sum(r.metrics.failure_count for r in registrations)
        total_time = sum(r.metrics.total_execution_time_ms for r in registrations)

        return {
            "registration_count": len(registrations),
            "total_invocations": total_invocations,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "success_rate": (total_successes / total_invocations * 100) if total_invocations > 0 else 100.0,
            "total_execution_time_ms": round(total_time, 2),
            "avg_execution_time_ms": round(total_time / total_invocations, 2) if total_invocations > 0 else 0.0,
        }

    def get_emission_history(
        self,
        limit: int = 100,
        phase_id: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get emission history with optional filters.

        Args:
            limit: Maximum entries to return
            phase_id: Filter by phase ID
            event: Filter by event type

        Returns:
            List of history entries
        """
        with self._lock:
            history = list(self._emission_history)

        if phase_id is not None:
            history = [h for h in history if h.get("phase_id") == phase_id]
        if event is not None:
            history = [h for h in history if h.get("event") == event.value]

        return history[-limit:]

    def get_registered_phases(self) -> List[str]:
        """Get list of all phases with registered triggers."""
        with self._lock:
            return [
                phase_id
                for phase_id, reg_ids in self._phase_registrations.items()
                if reg_ids
            ]

    def get_registration_count(
        self,
        phase_id: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
    ) -> int:
        """Get count of registrations with optional filters."""
        return len(self.list_registrations(phase_id=phase_id, event=event))

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the trigger system.

        Returns:
            Health status dict
        """
        with self._lock:
            active_count = sum(
                1 for r in self._registrations.values()
                if r.state == TriggerState.ACTIVE
            )
            paused_count = sum(
                1 for r in self._registrations.values()
                if r.state == TriggerState.PAUSED
            )
            disabled_count = sum(
                1 for r in self._registrations.values()
                if r.state == TriggerState.DISABLED
            )

            # Check for failing triggers
            failing_triggers = [
                r.name
                for r in self._registrations.values()
                if r.metrics.failure_count > 0 and r.metrics.success_rate < 90
            ]

        return {
            "status": "healthy" if not failing_triggers else "degraded",
            "total_registrations": len(self._registrations),
            "active": active_count,
            "paused": paused_count,
            "disabled": disabled_count,
            "phases_tracked": len(self._phase_registrations),
            "failing_triggers": failing_triggers,
            "emission_history_size": len(self._emission_history),
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # CONTEXT MANAGERS
    # ═══════════════════════════════════════════════════════════════════════════

    @contextmanager
    def scoped_trigger(
        self,
        event: TriggerEvent,
        phase_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
    ):
        """
        Context manager for temporary trigger registration.

        Usage:
            with triggers.scoped_trigger(event, phase_id, callback):
                # trigger is active only within this block
                ...
        """
        method_map = {
            TriggerEvent.PHASE_INITIALIZING: self.on_phase_initializing,
            TriggerEvent.PHASE_VALIDATING_PREREQUISITES: self.on_phase_validating_prerequisites,
            TriggerEvent.PHASE_EXECUTING: self.on_phase_executing,
            TriggerEvent.PHASE_FINALIZING: self.on_phase_finalizing,
        }

        register_method = method_map.get(event)
        if not register_method:
            raise ValueError(f"Unsupported event for scoped trigger: {event}")

        reg_id = register_method(phase_id, callback, priority)
        try:
            yield reg_id
        finally:
            self.unregister(reg_id)

    @contextmanager
    def paused_phase(self, phase_id: str):
        """
        Context manager to temporarily pause all triggers for a phase.

        Usage:
            with triggers.paused_phase("phase_1"):
                # all phase_1 triggers are paused
                ...
        """
        self.pause_phase(phase_id)
        try:
            yield
        finally:
            self.resume_phase(phase_id)

    # ═══════════════════════════════════════════════════════════════════════════
    # DECORATOR-BASED REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════════

    def on_initializing(
        self,
        phase_id: str,
        priority: int = 0,
        name: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        """Decorator to register a function as phase initialization trigger."""
        def decorator(func: Callable[[TriggerContext], None]):
            self.on_phase_initializing(phase_id, func, priority, name, tags=tags)
            return func
        return decorator

    def on_validating(
        self,
        phase_id: str,
        priority: int = 0,
        name: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        """Decorator to register a function as prerequisite validation trigger."""
        def decorator(func: Callable[[TriggerContext], None]):
            self.on_phase_validating_prerequisites(phase_id, func, priority, name, tags=tags)
            return func
        return decorator

    def on_executing(
        self,
        phase_id: str,
        priority: int = 0,
        name: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        """Decorator to register a function as phase execution trigger."""
        def decorator(func: Callable[[TriggerContext], None]):
            self.on_phase_executing(phase_id, func, priority, name, tags=tags)
            return func
        return decorator

    def on_finalizing(
        self,
        phase_id: str,
        priority: int = 0,
        name: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        """Decorator to register a function as phase finalization trigger."""
        def decorator(func: Callable[[TriggerContext], None]):
            self.on_phase_finalizing(phase_id, func, priority, name, tags=tags)
            return func
        return decorator

    # ═══════════════════════════════════════════════════════════════════════════
    # STRING REPRESENTATION
    # ═══════════════════════════════════════════════════════════════════════════

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<SubPhaseTriggers registrations={len(self._registrations)} "
            f"phases={len(self._phase_registrations)}>"
        )

    def __len__(self) -> int:
        """Number of registrations."""
        return len(self._registrations)
