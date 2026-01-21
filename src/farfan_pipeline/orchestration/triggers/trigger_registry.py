"""
Trigger Registry - Central registry for all event triggers.

SOTA Pattern: Observer Pattern with Type-Safe Callbacks
"""

from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional
from enum import Enum, auto
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TriggerEvent(str, Enum):
    """All possible trigger events in the system."""

    # Phase lifecycle (granular)
    PHASE_INITIALIZING = "PHASE_INITIALIZING"
    PHASE_VALIDATING_PREREQUISITES = "PHASE_VALIDATING_PREREQUISITES"
    PHASE_EXECUTING = "PHASE_EXECUTING"
    PHASE_FINALIZING = "PHASE_FINALIZING"

    # Contract lifecycle
    CONTRACT_LOADING = "CONTRACT_LOADING"
    CONTRACT_METHOD_INJECTING = "CONTRACT_METHOD_INJECTING"
    CONTRACT_EXECUTING = "CONTRACT_EXECUTING"
    CONTRACT_VETO_CHECK = "CONTRACT_VETO_CHECK"
    CONTRACT_FUSION = "CONTRACT_FUSION"

    # Extraction lifecycle (MC01-MC10)
    EXTRACTION_STARTING = "EXTRACTION_STARTING"
    EXTRACTION_PATTERN_MATCHED = "EXTRACTION_PATTERN_MATCHED"
    EXTRACTION_SIGNAL_CREATED = "EXTRACTION_SIGNAL_CREATED"
    EXTRACTION_COMPLETED = "EXTRACTION_COMPLETED"

    # Validation lifecycle
    VALIDATION_GATE_1_START = "VALIDATION_GATE_1_START"
    VALIDATION_GATE_1_COMPLETE = "VALIDATION_GATE_1_COMPLETE"
    VALIDATION_GATE_2_START = "VALIDATION_GATE_2_START"
    VALIDATION_GATE_2_COMPLETE = "VALIDATION_GATE_2_COMPLETE"
    VALIDATION_GATE_3_START = "VALIDATION_GATE_3_START"
    VALIDATION_GATE_3_COMPLETE = "VALIDATION_GATE_3_COMPLETE"
    VALIDATION_GATE_4_START = "VALIDATION_GATE_4_START"
    VALIDATION_GATE_4_COMPLETE = "VALIDATION_GATE_4_COMPLETE"

    # Aggregation lifecycle
    AGGREGATION_MICRO_TO_MESO = "AGGREGATION_MICRO_TO_MESO"
    AGGREGATION_MESO_TO_MACRO = "AGGREGATION_MESO_TO_MACRO"
    AGGREGATION_CLUSTER = "AGGREGATION_CLUSTER"
    AGGREGATION_HOLISTIC = "AGGREGATION_HOLISTIC"


@dataclass
class TriggerContext:
    """Context passed to trigger callbacks."""
    event: TriggerEvent
    timestamp: datetime
    phase_id: Optional[str] = None
    signal_type: Optional[str] = None
    consumer_id: Optional[str] = None
    contract_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)


TriggerCallback = Callable[[TriggerContext], None]


@dataclass
class RegisteredTrigger:
    """A registered trigger callback."""
    callback: TriggerCallback
    event: TriggerEvent
    priority: int = 0  # Higher priority executes first
    name: str = "unnamed"
    enabled: bool = True


class TriggerRegistry:
    """
    Central registry for event triggers.

    Usage:
        registry = TriggerRegistry()
        registry.register(TriggerEvent.PHASE_EXECUTING, my_callback)
        registry.emit(TriggerEvent.PHASE_EXECUTING, context)
    """

    _instance: Optional["TriggerRegistry"] = None

    def __new__(cls):
        """Singleton pattern for global trigger registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._triggers = {}
            cls._instance._execution_log = []
        return cls._instance

    def register(
        self,
        event: TriggerEvent,
        callback: TriggerCallback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """
        Register a trigger callback for an event.

        Args:
            event: The event to listen for
            callback: Function to call when event fires
            priority: Execution priority (higher = first)
            name: Optional name for debugging

        Returns:
            Registration ID for later unregistration
        """
        if event not in self._triggers:
            self._triggers[event] = []

        trigger = RegisteredTrigger(
            callback=callback,
            event=event,
            priority=priority,
            name=name or f"trigger_{len(self._triggers[event])}",
        )

        self._triggers[event].append(trigger)
        # Sort by priority (descending)
        self._triggers[event].sort(key=lambda t: t.priority, reverse=True)

        logger.debug(f"Registered trigger '{trigger.name}' for event {event.value}")
        return trigger.name

    def unregister(self, event: TriggerEvent, name: str) -> bool:
        """Unregister a trigger by name."""
        if event not in self._triggers:
            return False

        original_len = len(self._triggers[event])
        self._triggers[event] = [t for t in self._triggers[event] if t.name != name]
        return len(self._triggers[event]) < original_len

    def emit(self, event: TriggerEvent, context: TriggerContext) -> int:
        """
        Emit an event to all registered triggers.

        Args:
            event: The event to emit
            context: Context to pass to callbacks

        Returns:
            Number of triggers executed
        """
        if event not in self._triggers:
            return 0

        executed = 0
        for trigger in self._triggers[event]:
            if not trigger.enabled:
                continue

            try:
                trigger.callback(context)
                executed += 1
                self._execution_log.append({
                    "event": event.value,
                    "trigger": trigger.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "success",
                })
            except Exception as e:
                logger.error(f"Trigger '{trigger.name}' failed: {e}")
                self._execution_log.append({
                    "event": event.value,
                    "trigger": trigger.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "error",
                    "error": str(e),
                })

        return executed

    def get_registered_count(self, event: TriggerEvent = None) -> int:
        """Get count of registered triggers."""
        if event is not None:
            return len(self._triggers.get(event, []))
        return sum(len(triggers) for triggers in self._triggers.values())

    def get_execution_log(self, limit: int = 100) -> List[Dict]:
        """Get recent execution log entries."""
        return self._execution_log[-limit:]

    def clear(self) -> None:
        """Clear all registered triggers."""
        self._triggers.clear()
        self._execution_log.clear()


# Module-level convenience functions
_registry = TriggerRegistry()


def register_trigger(
    event: TriggerEvent,
    callback: TriggerCallback,
    priority: int = 0,
    name: str = None,
) -> str:
    """Register a trigger callback."""
    return _registry.register(event, callback, priority, name)


def emit_trigger(event: TriggerEvent, **kwargs) -> int:
    """Emit a trigger event."""
    context = TriggerContext(
        event=event,
        timestamp=datetime.utcnow(),
        **kwargs
    )
    return _registry.emit(event, context)
