"""
Extraction Triggers - Extraction-level event triggers.

Provides triggers for MC (Membership Criteria) extraction events with advanced features:
- Thread-safe registration and emission
- Bulk registration/deregistration
- Introspection and diagnostics
- Conditional trigger execution
- Metrics and timing
- Decorator-based registration
- Pattern-based filtering
"""

from typing import Optional, Dict, Any, Callable, List, Set, Pattern
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
from enum import Enum
import logging
import threading
import time
import uuid
import re

from .trigger_registry import TriggerRegistry, TriggerEvent, TriggerContext

logger = logging.getLogger(__name__)


class TriggerState(str, Enum):
    """State of a registered trigger."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class ExtractionStage(str, Enum):
    """Extraction pipeline stages."""
    STARTING = "starting"
    PATTERN_MATCHED = "pattern_matched"
    SIGNAL_CREATED = "signal_created"
    COMPLETED = "completed"


@dataclass
class ExtractionMetrics:
    """Metrics for extraction trigger performance."""
    invocation_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_execution_time_ms: float = 0.0
    patterns_matched: int = 0
    signals_created: int = 0
    last_invocation: Optional[datetime] = None
    last_error: Optional[str] = None
    last_signal_type: Optional[str] = None

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

    @property
    def pattern_match_rate(self) -> float:
        """Calculate pattern match rate."""
        if self.invocation_count == 0:
            return 0.0
        return (self.patterns_matched / self.invocation_count) * 100


@dataclass
class ExtractionRegistration:
    """Extended registration info for an extraction trigger."""
    registration_id: str
    event: TriggerEvent
    signal_type: str
    name: str
    priority: int
    state: TriggerState = TriggerState.ACTIVE
    condition: Optional[Callable[[TriggerContext], bool]] = None
    signal_pattern: Optional[str] = None  # Regex pattern for signal_type matching
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: ExtractionMetrics = field(default_factory=ExtractionMetrics)
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: Set[str] = field(default_factory=set)

    def matches_signal(self, signal_type: str) -> bool:
        """Check if signal_type matches this registration."""
        if self.signal_type == "*":
            return True
        if self.signal_pattern:
            return bool(re.match(self.signal_pattern, signal_type))
        return self.signal_type == signal_type


class ExtractionTriggers:
    """
    Manager for extraction-level triggers.

    These triggers emit during MC extraction:
    - Extraction starting
    - Pattern matched
    - Signal created
    - Extraction completed

    Features:
    - Thread-safe operations
    - Conditional execution
    - Bulk operations
    - Metrics tracking
    - Signal pattern matching (regex support)
    - Introspection utilities
    - Context managers for scoped triggers
    """

    # Class-level event mapping for DRY registration
    _EVENT_MAP: Dict[str, TriggerEvent] = {
        "starting": TriggerEvent.EXTRACTION_STARTING,
        "pattern_matched": TriggerEvent.EXTRACTION_PATTERN_MATCHED,
        "signal_created": TriggerEvent.EXTRACTION_SIGNAL_CREATED,
        "completed": TriggerEvent.EXTRACTION_COMPLETED,
    }

    _STAGE_TO_EVENT: Dict[ExtractionStage, TriggerEvent] = {
        ExtractionStage.STARTING: TriggerEvent.EXTRACTION_STARTING,
        ExtractionStage.PATTERN_MATCHED: TriggerEvent.EXTRACTION_PATTERN_MATCHED,
        ExtractionStage.SIGNAL_CREATED: TriggerEvent.EXTRACTION_SIGNAL_CREATED,
        ExtractionStage.COMPLETED: TriggerEvent.EXTRACTION_COMPLETED,
    }

    def __init__(self, registry: Optional[TriggerRegistry] = None):
        """
        Initialize ExtractionTriggers.

        Args:
            registry: Optional TriggerRegistry instance (uses singleton if None)
        """
        from .trigger_registry import TriggerRegistry
        self._registry = registry or TriggerRegistry()
        self._lock = threading.RLock()
        self._registrations: Dict[str, ExtractionRegistration] = {}
        self._signal_registrations: Dict[str, Set[str]] = {}  # signal_type -> registration_ids
        self._event_registrations: Dict[TriggerEvent, Set[str]] = {}  # event -> registration_ids
        self._emission_history: List[Dict[str, Any]] = []
        self._max_history_size: int = 1000
        self._global_metrics = ExtractionMetrics()

    # ═══════════════════════════════════════════════════════════════════════════
    # CORE REGISTRATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _register_internal(
        self,
        event: TriggerEvent,
        signal_type: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        signal_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Internal registration with full feature support.

        Args:
            event: The trigger event type
            signal_type: The signal type to scope the trigger (or "*" for all)
            callback: Function to call when trigger fires
            priority: Execution priority (higher = first)
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            signal_pattern: Optional regex pattern for signal_type matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        
        Technical Debt: Registered in TECHNICAL_DEBT_REGISTER.md
        Complexity: 25 - Refactoring scheduled Q2-Q3 2026
        """
        registration_id = str(uuid.uuid4())[:12]
        trigger_name = name or f"{event.name.lower()}_{signal_type}_{registration_id}"

        # Compile pattern if provided
        compiled_pattern = None
        if signal_pattern:
            try:
                compiled_pattern = re.compile(signal_pattern)
            except re.error as e:
                logger.warning(f"Invalid signal pattern '{signal_pattern}': {e}")
                signal_pattern = None

        # Create registration record
        registration = ExtractionRegistration(
            registration_id=registration_id,
            event=event,
            signal_type=signal_type,
            name=trigger_name,
            priority=priority,
            condition=condition,
            signal_pattern=signal_pattern,
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

            # Check signal_type match
            ctx_signal = getattr(ctx, 'signal_type', None) or ''
            if not registration.matches_signal(ctx_signal):
                return

            # Apply signal_type to context
            if signal_type != "*":
                ctx.signal_type = signal_type

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
                        reg.metrics.last_signal_type = ctx_signal

                        # Track specific event metrics
                        if event == TriggerEvent.EXTRACTION_PATTERN_MATCHED:
                            reg.metrics.patterns_matched += 1
                        elif event == TriggerEvent.EXTRACTION_SIGNAL_CREATED:
                            reg.metrics.signals_created += 1

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

            # Index by signal_type
            if signal_type not in self._signal_registrations:
                self._signal_registrations[signal_type] = set()
            self._signal_registrations[signal_type].add(registration_id)

            # Index by event
            if event not in self._event_registrations:
                self._event_registrations[event] = set()
            self._event_registrations[event].add(registration_id)

        logger.debug(f"Registered extraction trigger '{trigger_name}' for {event.value} on {signal_type}")
        return registration_id

    def on_extraction_starting(
        self,
        signal_type: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        signal_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for extraction starting.

        Args:
            signal_type: The signal type (e.g., "MC01") or "*" for all
            callback: Function to call when extraction starts
            priority: Execution priority (higher executes first)
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            signal_pattern: Optional regex pattern for signal matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.EXTRACTION_STARTING,
            signal_type,
            callback,
            priority,
            name or f"extraction_start_{signal_type}",
            condition,
            signal_pattern,
            metadata,
            tags,
        )

    def on_extraction_pattern_matched(
        self,
        signal_type: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        signal_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for pattern matched.

        Args:
            signal_type: The signal type or "*" for all
            callback: Function to call when pattern is matched
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            signal_pattern: Optional regex pattern for signal matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.EXTRACTION_PATTERN_MATCHED,
            signal_type,
            callback,
            priority,
            name or f"extraction_pattern_{signal_type}",
            condition,
            signal_pattern,
            metadata,
            tags,
        )

    def on_extraction_signal_created(
        self,
        signal_type: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        signal_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for signal created.

        Args:
            signal_type: The signal type or "*" for all
            callback: Function to call when signal is created
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            signal_pattern: Optional regex pattern for signal matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.EXTRACTION_SIGNAL_CREATED,
            signal_type,
            callback,
            priority,
            name or f"extraction_signal_{signal_type}",
            condition,
            signal_pattern,
            metadata,
            tags,
        )

    def on_extraction_completed(
        self,
        signal_type: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        signal_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for extraction completed.

        Args:
            signal_type: The signal type or "*" for all
            callback: Function to call when extraction completes
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            signal_pattern: Optional regex pattern for signal matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.EXTRACTION_COMPLETED,
            signal_type,
            callback,
            priority,
            name or f"extraction_complete_{signal_type}",
            condition,
            signal_pattern,
            metadata,
            tags,
        )

    def on_any_extraction_event(
        self,
        signal_type: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        tags: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Register callback for ALL extraction events for a signal type.

        Args:
            signal_type: The signal type or "*" for all
            callback: Function to call on any extraction event
            priority: Execution priority
            tags: Optional tags for categorization

        Returns:
            List of registration IDs
        """
        reg_ids = []
        all_tags = (tags or set()) | {f"all_events_{signal_type}"}

        for event in self._EVENT_MAP.values():
            reg_id = self._register_internal(
                event, signal_type, callback, priority, tags=all_tags
            )
            reg_ids.append(reg_id)

        return reg_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # BULK REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════════

    def register_extraction_lifecycle(
        self,
        signal_type: str,
        on_starting: Optional[Callable[[TriggerContext], None]] = None,
        on_pattern_matched: Optional[Callable[[TriggerContext], None]] = None,
        on_signal_created: Optional[Callable[[TriggerContext], None]] = None,
        on_completed: Optional[Callable[[TriggerContext], None]] = None,
        priority: int = 0,
        tags: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Register callbacks for all lifecycle events of an extraction.

        Args:
            signal_type: The signal type (e.g., "MC01")
            on_starting: Callback for extraction starting
            on_pattern_matched: Callback for pattern matched
            on_signal_created: Callback for signal created
            on_completed: Callback for extraction completed
            priority: Execution priority for all callbacks
            tags: Tags to apply to all registrations

        Returns:
            List of registration IDs
        """
        registration_ids = []
        lifecycle_tags = (tags or set()) | {f"lifecycle_{signal_type}"}

        if on_starting:
            reg_id = self.on_extraction_starting(
                signal_type, on_starting, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_pattern_matched:
            reg_id = self.on_extraction_pattern_matched(
                signal_type, on_pattern_matched, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_signal_created:
            reg_id = self.on_extraction_signal_created(
                signal_type, on_signal_created, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_completed:
            reg_id = self.on_extraction_completed(
                signal_type, on_completed, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        logger.info(f"Registered {len(registration_ids)} lifecycle triggers for {signal_type}")
        return registration_ids

    def register_mc_range(
        self,
        mc_start: int,
        mc_end: int,
        event: TriggerEvent,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        tags: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Register callback for a range of MC signal types.

        Args:
            mc_start: Start of MC range (e.g., 1 for MC01)
            mc_end: End of MC range inclusive (e.g., 10 for MC10)
            event: The event to register for
            callback: Function to call
            priority: Execution priority
            tags: Optional tags

        Returns:
            List of registration IDs
        """
        reg_ids = []
        range_tags = (tags or set()) | {f"mc_range_{mc_start:02d}_{mc_end:02d}"}

        for mc_num in range(mc_start, mc_end + 1):
            signal_type = f"MC{mc_num:02d}"
            reg_id = self._register_internal(
                event, signal_type, callback, priority, tags=range_tags
            )
            reg_ids.append(reg_id)

        logger.info(f"Registered {len(reg_ids)} triggers for MC{mc_start:02d}-MC{mc_end:02d}")
        return reg_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # EMISSION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _emit_internal(
        self,
        event: TriggerEvent,
        signal_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Internal emission with history tracking.

        Args:
            event: The event to emit
            signal_type: The signal type
            payload: Optional payload data

        Returns:
            Number of triggers executed
        """
        context = TriggerContext(
            event=event,
            timestamp=datetime.utcnow(),
            signal_type=signal_type,
            payload=payload or {},
        )

        start_time = time.perf_counter()
        executed = self._registry.emit(event, context)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Update global metrics
        with self._lock:
            self._global_metrics.invocation_count += 1
            self._global_metrics.total_execution_time_ms += elapsed_ms
            self._global_metrics.last_invocation = datetime.utcnow()
            self._global_metrics.last_signal_type = signal_type

            if event == TriggerEvent.EXTRACTION_PATTERN_MATCHED:
                self._global_metrics.patterns_matched += 1
            elif event == TriggerEvent.EXTRACTION_SIGNAL_CREATED:
                self._global_metrics.signals_created += 1

        # Record history
        history_entry = {
            "event": event.value,
            "signal_type": signal_type,
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
            f"Emitted {event.value} for {signal_type}: "
            f"{executed} triggers in {elapsed_ms:.2f}ms"
        )
        return executed

    def emit_extraction_starting(
        self, signal_type: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit extraction starting event."""
        return self._emit_internal(TriggerEvent.EXTRACTION_STARTING, signal_type, payload)

    def emit_extraction_pattern_matched(
        self, signal_type: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit pattern matched event."""
        return self._emit_internal(
            TriggerEvent.EXTRACTION_PATTERN_MATCHED, signal_type, payload
        )

    def emit_extraction_signal_created(
        self, signal_type: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit signal created event."""
        return self._emit_internal(
            TriggerEvent.EXTRACTION_SIGNAL_CREATED, signal_type, payload
        )

    def emit_extraction_completed(
        self, signal_type: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit extraction completed event."""
        return self._emit_internal(TriggerEvent.EXTRACTION_COMPLETED, signal_type, payload)

    def emit_extraction_lifecycle(
        self,
        signal_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """
        Emit all lifecycle events for an extraction in sequence.

        Args:
            signal_type: The signal type
            payload: Payload to pass to all events

        Returns:
            Dict mapping event names to execution counts
        """
        results = {}
        results["starting"] = self.emit_extraction_starting(signal_type, payload)
        results["pattern_matched"] = self.emit_extraction_pattern_matched(signal_type, payload)
        results["signal_created"] = self.emit_extraction_signal_created(signal_type, payload)
        results["completed"] = self.emit_extraction_completed(signal_type, payload)
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
            if reg.signal_type in self._signal_registrations:
                self._signal_registrations[reg.signal_type].discard(registration_id)
            if reg.event in self._event_registrations:
                self._event_registrations[reg.event].discard(registration_id)

            # Remove registration
            del self._registrations[registration_id]

        logger.debug(f"Unregistered trigger '{reg.name}'")
        return True

    def unregister_signal(self, signal_type: str) -> int:
        """
        Unregister all triggers for a specific signal type.

        Args:
            signal_type: The signal type

        Returns:
            Number of triggers unregistered
        """
        with self._lock:
            reg_ids = list(self._signal_registrations.get(signal_type, set()))

        count = 0
        for reg_id in reg_ids:
            if self.unregister(reg_id):
                count += 1

        logger.info(f"Unregistered {count} triggers for signal {signal_type}")
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

    def unregister_by_event(self, event: TriggerEvent) -> int:
        """
        Unregister all triggers for a specific event type.

        Args:
            event: The event type

        Returns:
            Number of triggers unregistered
        """
        with self._lock:
            reg_ids = list(self._event_registrations.get(event, set()))

        count = 0
        for reg_id in reg_ids:
            if self.unregister(reg_id):
                count += 1

        logger.info(f"Unregistered {count} triggers for event {event.value}")
        return count

    def clear_all(self) -> int:
        """
        Clear all registered extraction triggers.

        Returns:
            Number of triggers cleared
        """
        with self._lock:
            count = len(self._registrations)
            reg_ids = list(self._registrations.keys())

        for reg_id in reg_ids:
            self.unregister(reg_id)

        logger.info(f"Cleared {count} extraction triggers")
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

    def pause_signal(self, signal_type: str) -> int:
        """Pause all triggers for a signal type."""
        with self._lock:
            reg_ids = self._signal_registrations.get(signal_type, set())
            count = 0
            for reg_id in reg_ids:
                if reg_id in self._registrations:
                    self._registrations[reg_id].state = TriggerState.PAUSED
                    count += 1
        return count

    def resume_signal(self, signal_type: str) -> int:
        """Resume all triggers for a signal type."""
        with self._lock:
            reg_ids = self._signal_registrations.get(signal_type, set())
            count = 0
            for reg_id in reg_ids:
                if reg_id in self._registrations:
                    self._registrations[reg_id].state = TriggerState.ACTIVE
                    count += 1
        return count

    # ═══════════════════════════════════════════════════════════════════════════
    # INTROSPECTION & DIAGNOSTICS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_registration(self, registration_id: str) -> Optional[ExtractionRegistration]:
        """Get registration details by ID."""
        with self._lock:
            return self._registrations.get(registration_id)

    def list_registrations(
        self,
        signal_type: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
        tag: Optional[str] = None,
        state: Optional[TriggerState] = None,
    ) -> List[ExtractionRegistration]:
        """
        List registrations with optional filters.

        Args:
            signal_type: Filter by signal type
            event: Filter by event type
            tag: Filter by tag
            state: Filter by state

        Returns:
            List of matching registrations
        """
        with self._lock:
            results = list(self._registrations.values())

        if signal_type is not None:
            results = [r for r in results if r.signal_type == signal_type]
        if event is not None:
            results = [r for r in results if r.event == event]
        if tag is not None:
            results = [r for r in results if tag in r.tags]
        if state is not None:
            results = [r for r in results if r.state == state]

        return results

    def get_metrics(self, registration_id: str) -> Optional[ExtractionMetrics]:
        """Get metrics for a specific registration."""
        with self._lock:
            reg = self._registrations.get(registration_id)
            return reg.metrics if reg else None

    def get_global_metrics(self) -> ExtractionMetrics:
        """Get global extraction metrics."""
        with self._lock:
            return self._global_metrics

    def get_aggregated_metrics(
        self, signal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics across registrations.

        Args:
            signal_type: Optional filter by signal type

        Returns:
            Aggregated metrics dict
        """
        registrations = self.list_registrations(signal_type=signal_type)

        total_invocations = sum(r.metrics.invocation_count for r in registrations)
        total_successes = sum(r.metrics.success_count for r in registrations)
        total_failures = sum(r.metrics.failure_count for r in registrations)
        total_time = sum(r.metrics.total_execution_time_ms for r in registrations)
        total_patterns = sum(r.metrics.patterns_matched for r in registrations)
        total_signals = sum(r.metrics.signals_created for r in registrations)

        return {
            "registration_count": len(registrations),
            "total_invocations": total_invocations,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "success_rate": (total_successes / total_invocations * 100) if total_invocations > 0 else 100.0,
            "total_execution_time_ms": round(total_time, 2),
            "avg_execution_time_ms": round(total_time / total_invocations, 2) if total_invocations > 0 else 0.0,
            "total_patterns_matched": total_patterns,
            "total_signals_created": total_signals,
        }

    def get_emission_history(
        self,
        limit: int = 100,
        signal_type: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get emission history with optional filters.

        Args:
            limit: Maximum entries to return
            signal_type: Filter by signal type
            event: Filter by event type

        Returns:
            List of history entries
        """
        with self._lock:
            history = list(self._emission_history)

        if signal_type is not None:
            history = [h for h in history if h.get("signal_type") == signal_type]
        if event is not None:
            history = [h for h in history if h.get("event") == event.value]

        return history[-limit:]

    def get_registered_signals(self) -> List[str]:
        """Get list of all signal types with registered triggers."""
        with self._lock:
            return [
                signal_type
                for signal_type, reg_ids in self._signal_registrations.items()
                if reg_ids
            ]

    def get_registration_count(
        self,
        signal_type: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
    ) -> int:
        """Get count of registrations with optional filters."""
        return len(self.list_registrations(signal_type=signal_type, event=event))

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the extraction trigger system.

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

            # Check signal coverage
            mc_signals = [f"MC{i:02d}" for i in range(1, 11)]
            covered_signals = set(self._signal_registrations.keys())
            missing_coverage = [s for s in mc_signals if s not in covered_signals]

        return {
            "status": "healthy" if not failing_triggers else "degraded",
            "total_registrations": len(self._registrations),
            "active": active_count,
            "paused": paused_count,
            "disabled": disabled_count,
            "signals_tracked": len(self._signal_registrations),
            "failing_triggers": failing_triggers,
            "missing_mc_coverage": missing_coverage,
            "emission_history_size": len(self._emission_history),
            "global_success_rate": self._global_metrics.success_rate,
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # CONTEXT MANAGERS
    # ═══════════════════════════════════════════════════════════════════════════

    @contextmanager
    def scoped_trigger(
        self,
        event: TriggerEvent,
        signal_type: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
    ):
        """
        Context manager for temporary trigger registration.

        Usage:
            with triggers.scoped_trigger(event, signal_type, callback):
                # trigger is active only within this block
                ...
        """
        method_map = {
            TriggerEvent.EXTRACTION_STARTING: self.on_extraction_starting,
            TriggerEvent.EXTRACTION_PATTERN_MATCHED: self.on_extraction_pattern_matched,
            TriggerEvent.EXTRACTION_SIGNAL_CREATED: self.on_extraction_signal_created,
            TriggerEvent.EXTRACTION_COMPLETED: self.on_extraction_completed,
        }

        register_method = method_map.get(event)
        if not register_method:
            raise ValueError(f"Unsupported event for scoped trigger: {event}")

        reg_id = register_method(signal_type, callback, priority)
        try:
            yield reg_id
        finally:
            self.unregister(reg_id)

    @contextmanager
    def paused_signal(self, signal_type: str):
        """
        Context manager to temporarily pause all triggers for a signal.

        Usage:
            with triggers.paused_signal("MC01"):
                # all MC01 triggers are paused
                ...
        """
        self.pause_signal(signal_type)
        try:
            yield
        finally:
            self.resume_signal(signal_type)

    @contextmanager
    def extraction_span(
        self,
        signal_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ):
        """
        Context manager that emits starting/completed events automatically.

        Usage:
            with triggers.extraction_span("MC01", {"doc_id": "123"}):
                # extraction logic here
                ...
        """
        self.emit_extraction_starting(signal_type, payload)
        try:
            yield
            self.emit_extraction_completed(signal_type, payload)
        except Exception as e:
            error_payload = {**(payload or {}), "error": str(e)}
            self.emit_extraction_completed(signal_type, error_payload)
            raise

    # ═══════════════════════════════════════════════════════════════════════════
    # DECORATOR-BASED REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════════

    def on_starting(
        self,
        signal_type: str,
        priority: int = 0,
        name: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        """Decorator to register a function as extraction starting trigger."""
        def decorator(func: Callable[[TriggerContext], None]):
            self.on_extraction_starting(signal_type, func, priority, name, tags=tags)
            return func
        return decorator

    def on_pattern(
        self,
        signal_type: str,
        priority: int = 0,
        name: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        """Decorator to register a function as pattern matched trigger."""
        def decorator(func: Callable[[TriggerContext], None]):
            self.on_extraction_pattern_matched(signal_type, func, priority, name, tags=tags)
            return func
        return decorator

    def on_signal(
        self,
        signal_type: str,
        priority: int = 0,
        name: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        """Decorator to register a function as signal created trigger."""
        def decorator(func: Callable[[TriggerContext], None]):
            self.on_extraction_signal_created(signal_type, func, priority, name, tags=tags)
            return func
        return decorator

    def on_completed(
        self,
        signal_type: str,
        priority: int = 0,
        name: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        """Decorator to register a function as extraction completed trigger."""
        def decorator(func: Callable[[TriggerContext], None]):
            self.on_extraction_completed(signal_type, func, priority, name, tags=tags)
            return func
        return decorator

    # ═══════════════════════════════════════════════════════════════════════════
    # STRING REPRESENTATION
    # ═══════════════════════════════════════════════════════════════════════════

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ExtractionTriggers registrations={len(self._registrations)} "
            f"signals={len(self._signal_registrations)}>"
        )

    def __len__(self) -> int:
        """Number of registrations."""
        return len(self._registrations)
