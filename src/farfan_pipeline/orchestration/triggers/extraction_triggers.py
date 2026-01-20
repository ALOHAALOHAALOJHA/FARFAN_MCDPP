"""
Extraction Triggers - Extraction-level event triggers.

Provides triggers for MC (Membership Criteria) extraction events.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

from .trigger_registry import TriggerRegistry, TriggerEvent, TriggerContext

logger = logging.getLogger(__name__)


class ExtractionTriggers:
    """
    Manager for extraction-level triggers.

    These triggers emit during MC extraction:
    - Extraction starting
    - Pattern matched
    - Signal created
    - Extraction completed
    """

    def __init__(self, registry: Optional[TriggerRegistry] = None):
        """
        Initialize ExtractionTriggers.

        Args:
            registry: Optional TriggerRegistry instance (uses singleton if None)
        """
        from .trigger_registry import TriggerRegistry
        self._registry = registry or TriggerRegistry()

    def on_extraction_starting(
        self,
        signal_type: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for extraction starting."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.signal_type = signal_type
            callback(ctx)

        return self._registry.register(
            TriggerEvent.EXTRACTION_STARTING,
            wrapped_callback,
            priority=priority,
            name=name or f"extraction_start_{signal_type}",
        )

    def on_extraction_pattern_matched(
        self,
        signal_type: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for pattern matched."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.signal_type = signal_type
            callback(ctx)

        return self._registry.register(
            TriggerEvent.EXTRACTION_PATTERN_MATCHED,
            wrapped_callback,
            priority=priority,
            name=name or f"extraction_pattern_{signal_type}",
        )

    def on_extraction_signal_created(
        self,
        signal_type: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for signal created."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.signal_type = signal_type
            callback(ctx)

        return self._registry.register(
            TriggerEvent.EXTRACTION_SIGNAL_CREATED,
            wrapped_callback,
            priority=priority,
            name=name or f"extraction_signal_{signal_type}",
        )

    def on_extraction_completed(
        self,
        signal_type: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for extraction completed."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.signal_type = signal_type
            callback(ctx)

        return self._registry.register(
            TriggerEvent.EXTRACTION_COMPLETED,
            wrapped_callback,
            priority=priority,
            name=name or f"extraction_complete_{signal_type}",
        )

    def emit_extraction_starting(self, signal_type: str, payload: Dict[str, Any] = None) -> int:
        """Emit extraction starting event."""
        context = TriggerContext(
            event=TriggerEvent.EXTRACTION_STARTING,
            timestamp=datetime.utcnow(),
            signal_type=signal_type,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.EXTRACTION_STARTING, context)

    def emit_extraction_pattern_matched(self, signal_type: str, payload: Dict[str, Any] = None) -> int:
        """Emit pattern matched event."""
        context = TriggerContext(
            event=TriggerEvent.EXTRACTION_PATTERN_MATCHED,
            timestamp=datetime.utcnow(),
            signal_type=signal_type,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.EXTRACTION_PATTERN_MATCHED, context)

    def emit_extraction_signal_created(self, signal_type: str, payload: Dict[str, Any] = None) -> int:
        """Emit signal created event."""
        context = TriggerContext(
            event=TriggerEvent.EXTRACTION_SIGNAL_CREATED,
            timestamp=datetime.utcnow(),
            signal_type=signal_type,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.EXTRACTION_SIGNAL_CREATED, context)

    def emit_extraction_completed(self, signal_type: str, payload: Dict[str, Any] = None) -> int:
        """Emit extraction completed event."""
        context = TriggerContext(
            event=TriggerEvent.EXTRACTION_COMPLETED,
            timestamp=datetime.utcnow(),
            signal_type=signal_type,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.EXTRACTION_COMPLETED, context)
