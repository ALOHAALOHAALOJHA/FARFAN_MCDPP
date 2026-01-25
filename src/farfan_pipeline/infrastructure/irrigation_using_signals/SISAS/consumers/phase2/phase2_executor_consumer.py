# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase2/phase2_executor_consumer.py

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract

# EventStore integration
try:
    from ...core.event import Event, EventStore, EventType
    EVENTSTORE_AVAILABLE = True
except ImportError:
    EVENTSTORE_AVAILABLE = False
    Event = None  # type: ignore
    EventStore = None  # type: ignore
    EventType = None  # type: ignore


@dataclass
class Phase2ExecutorConsumer(BaseConsumer):
    """
    Consumidor para executors en Phase 2 - Enhanced with EventStore integration.

    Consolidates functionality from:
    - phase2_60_00_base_executor_with_contract.py

    Responsabilidad: Validar que los executores respetan contratos
    y ejecutan correctamente, con acceso al contexto de eventos completo.
    
    SISAS Event System Enhancement:
    - Queries EventStore for originating events
    - Builds event causation chains
    - Enriches signal processing with event context
    """

    consumer_id: str = "phase2_executor_consumer.py"
    consumer_phase: str = "phase_02"
    event_store: Optional[Any] = None  # EventStore instance

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE2_EXECUTOR",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "ExecutionAttemptSignal",
                "FailureModeSignal"
            ],
            subscribed_buses=["operational_bus"],
            context_filters={
                "phase": ["phase_02"],
                "consumer_scope": ["Phase_02"]
            },
            required_capabilities=["can_validate"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """Procesa señales de executors con contexto de eventos completo"""
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "executor_analysis": {},
            "event_context": {}  # Enhanced with event data
        }

        if signal.signal_type == "ExecutionAttemptSignal":
            result["executor_analysis"] = self._analyze_execution(signal)
        elif signal.signal_type == "FailureModeSignal":
            result["executor_analysis"] = self._analyze_failure(signal)
        
        # Enrich with event context if EventStore available
        if self.event_store and EVENTSTORE_AVAILABLE:
            result["event_context"] = self._get_event_context(signal)

        return result

    def _analyze_execution(self, signal: Signal) -> Dict[str, Any]:
        """Analiza ejecución"""
        return {
            "status": str(getattr(signal, 'status', 'UNKNOWN')),
            "duration_ms": getattr(signal, 'duration_ms', 0.0),
            "component": getattr(signal, 'component', ''),
            "operation": getattr(signal, 'operation', '')
        }

    def _analyze_failure(self, signal: Signal) -> Dict[str, Any]:
        """Analiza fallas"""
        return {
            "failure_mode": str(getattr(signal, 'failure_mode', 'UNKNOWN')),
            "error_message": getattr(signal, 'error_message', ''),
            "recoverable": getattr(signal, 'recoverable', False)
        }
    
    def _get_event_context(self, signal: Signal) -> Dict[str, Any]:
        """
        Get event context for a signal (SISAS Event System Enhancement).
        
        Queries EventStore to:
        1. Find originating event for this signal
        2. Build causation chain (parent events)
        3. Find related events (same correlation_id)
        
        Args:
            signal: Signal to get event context for
            
        Returns:
            Dict with event context data
        """
        if not self.event_store or not EVENTSTORE_AVAILABLE:
            return {"available": False}
        
        try:
            # Get event_id from signal source if available
            event_id = getattr(getattr(signal, 'source', None), 'event_id', None)
            
            if not event_id:
                return {"available": False, "reason": "no_event_id_in_signal"}
            
            # Query originating event
            originating_event = self.event_store.get_by_id(event_id)
            
            if not originating_event:
                return {"available": False, "reason": "event_not_found"}
            
            # Build causation chain
            causation_chain = self._build_causation_chain(originating_event)
            
            # Get related events (same correlation)
            related_events = []
            if originating_event.correlation_id:
                related_events = self._get_related_events(originating_event.correlation_id)
            
            return {
                "available": True,
                "originating_event": {
                    "event_id": originating_event.event_id,
                    "event_type": originating_event.event_type.value if hasattr(originating_event.event_type, 'value') else str(originating_event.event_type),
                    "timestamp": originating_event.timestamp.isoformat() if hasattr(originating_event.timestamp, 'isoformat') else str(originating_event.timestamp),
                    "source_component": originating_event.source_component,
                    "phase": originating_event.phase,
                    "correlation_id": originating_event.correlation_id,
                },
                "causation_chain_length": len(causation_chain),
                "related_events_count": len(related_events),
                "event_lineage": [
                    {
                        "event_id": e.event_id,
                        "event_type": e.event_type.value if hasattr(e.event_type, 'value') else str(e.event_type),
                        "source_component": e.source_component,
                    }
                    for e in causation_chain
                ]
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def _build_causation_chain(self, event: Any) -> List[Any]:
        """
        Build causation chain by following causation_id links.
        
        Args:
            event: Starting event
            
        Returns:
            List of events in causation chain (oldest first)
        """
        chain = []
        current = event
        max_depth = 50  # Prevent infinite loops
        
        while current and len(chain) < max_depth:
            chain.append(current)
            if not current.causation_id:
                break
            parent = self.event_store.get_by_id(current.causation_id)
            if not parent or parent.event_id == current.event_id:
                break
            current = parent
        
        return list(reversed(chain))  # Oldest first
    
    def _get_related_events(self, correlation_id: str) -> List[Any]:
        """
        Get all events with the same correlation_id.
        
        Args:
            correlation_id: Correlation ID to query
            
        Returns:
            List of related events
        """
        # Query all phase_02 events
        phase_events = self.event_store.get_by_phase("phase_02")
        
        # Filter by correlation_id
        related = [e for e in phase_events if e.correlation_id == correlation_id]
        
        return related
