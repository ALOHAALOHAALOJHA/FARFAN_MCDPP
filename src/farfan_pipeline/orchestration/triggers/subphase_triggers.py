"""
SubPhase Triggers - Phase-level event triggers.

Provides fine-grained triggers within phase execution.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

from .trigger_registry import TriggerRegistry, TriggerEvent, TriggerContext, register_trigger

logger = logging.getLogger(__name__)


class SubPhaseTriggers:
    """
    Manager for sub-phase level triggers.

    These triggers emit at specific points within phase execution:
    - Phase initialization
    - Prerequisite validation
    - Phase execution start/end
    - Phase finalization
    """

    def __init__(self, registry: Optional[TriggerRegistry] = None):
        """
        Initialize SubPhaseTriggers.

        Args:
            registry: Optional TriggerRegistry instance (uses singleton if None)
        """
        from .trigger_registry import TriggerRegistry
        self._registry = registry or TriggerRegistry()

    def on_phase_initializing(
        self,
        phase_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """
        Register callback for phase initialization.

        Args:
            phase_id: The phase ID (e.g., "phase_1")
            callback: Function to call when phase initializes
            priority: Execution priority
            name: Optional trigger name

        Returns:
            Registration ID
        """
        def wrapped_callback(ctx: TriggerContext):
            ctx.phase_id = phase_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.PHASE_INITIALIZING,
            wrapped_callback,
            priority=priority,
            name=name or f"phase_init_{phase_id}",
        )

    def on_phase_validating_prerequisites(
        self,
        phase_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """
        Register callback for prerequisite validation.

        Args:
            phase_id: The phase ID
            callback: Function to call when validating prerequisites
            priority: Execution priority
            name: Optional trigger name

        Returns:
            Registration ID
        """
        def wrapped_callback(ctx: TriggerContext):
            ctx.phase_id = phase_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.PHASE_VALIDATING_PREREQUISITES,
            wrapped_callback,
            priority=priority,
            name=name or f"phase_validate_{phase_id}",
        )

    def on_phase_executing(
        self,
        phase_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """
        Register callback for phase execution.

        Args:
            phase_id: The phase ID
            callback: Function to call when phase executes
            priority: Execution priority
            name: Optional trigger name

        Returns:
            Registration ID
        """
        def wrapped_callback(ctx: TriggerContext):
            ctx.phase_id = phase_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.PHASE_EXECUTING,
            wrapped_callback,
            priority=priority,
            name=name or f"phase_execute_{phase_id}",
        )

    def on_phase_finalizing(
        self,
        phase_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """
        Register callback for phase finalization.

        Args:
            phase_id: The phase ID
            callback: Function to call when phase finalizes
            priority: Execution priority
            name: Optional trigger name

        Returns:
            Registration ID
        """
        def wrapped_callback(ctx: TriggerContext):
            ctx.phase_id = phase_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.PHASE_FINALIZING,
            wrapped_callback,
            priority=priority,
            name=name or f"phase_finalize_{phase_id}",
        )

    def emit_phase_initializing(self, phase_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit phase initializing event."""
        context = TriggerContext(
            event=TriggerEvent.PHASE_INITIALIZING,
            timestamp=datetime.utcnow(),
            phase_id=phase_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.PHASE_INITIALIZING, context)

    def emit_phase_validating_prerequisites(self, phase_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit prerequisite validation event."""
        context = TriggerContext(
            event=TriggerEvent.PHASE_VALIDATING_PREREQUISITES,
            timestamp=datetime.utcnow(),
            phase_id=phase_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.PHASE_VALIDATING_PREREQUISITES, context)

    def emit_phase_executing(self, phase_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit phase executing event."""
        context = TriggerContext(
            event=TriggerEvent.PHASE_EXECUTING,
            timestamp=datetime.utcnow(),
            phase_id=phase_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.PHASE_EXECUTING, context)

    def emit_phase_finalizing(self, phase_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit phase finalizing event."""
        context = TriggerContext(
            event=TriggerEvent.PHASE_FINALIZING,
            timestamp=datetime.utcnow(),
            phase_id=phase_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.PHASE_FINALIZING, context)
