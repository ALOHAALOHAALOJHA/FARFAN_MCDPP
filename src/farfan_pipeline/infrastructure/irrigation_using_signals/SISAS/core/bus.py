# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/bus.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Protocol
from collections import defaultdict
from queue import Queue, Empty
from threading import Lock
from pathlib import Path
import logging
import json

from . signal import Signal, SignalCategory
from .contracts import PublicationContract, ConsumptionContract, ContractRegistry


class BusType(Enum):
    """Tipos de bus según categoría de señales"""
    STRUCTURAL = "structural_bus"
    INTEGRITY = "integrity_bus"
    EPISTEMIC = "epistemic_bus"
    CONTRAST = "contrast_bus"
    OPERATIONAL = "operational_bus"
    CONSUMPTION = "consumption_bus"
    ORCHESTRATION = "orchestration_bus"  # Orchestration signals
    UNIVERSAL = "universal_bus"  # Recibe todo


@dataclass
class BusMessage:
    """Mensaje que circula por el bus"""
    signal: Signal
    publisher_vehicle: str
    published_at: datetime = field(default_factory=datetime. utcnow)
    message_id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    acknowledged_by: Set[str] = field(default_factory=set)
    
    def acknowledge(self, consumer_id: str):
        """Marca el mensaje como recibido por un consumidor"""
        self.acknowledged_by.add(consumer_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert bus message to dictionary for serialization."""
        return {
            "signal": self.signal.to_dict() if hasattr(self.signal, 'to_dict') else str(self.signal),
            "publisher_vehicle": self.publisher_vehicle,
            "published_at": self.published_at.isoformat(),
            "message_id": self.message_id,
            "acknowledged_by": list(self.acknowledged_by),
        }


# =============================================================================
# MESSAGE PERSISTENCE BACKEND
# =============================================================================

class MessagePersistenceBackend(Protocol):
    """Protocol for message persistence backends."""

    def persist_messages(self, bus_name: str, messages: List[BusMessage]) -> None:
        """Persist messages to storage."""
        ...

    def retrieve_messages(self, bus_name: str, limit: int = 100) -> List[BusMessage]:
        """Retrieve messages from storage."""
        ...


class FileSystemMessagePersistence:
    """File-based persistence for bus messages."""

    def __init__(self, storage_dir: str = "artifacts/sisas/message_history"):
        """Initialize persistence with directory path.

        Args:
            storage_dir: Directory to store message history
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger(__name__)

    def persist_messages(self, bus_name: str, messages: List[BusMessage]) -> None:
        """Persist messages to file system."""
        if not messages:
            return

        bus_dir = self.storage_dir / bus_name
        bus_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        message_file = bus_dir / f"messages_{timestamp}.jsonl"

        with open(message_file, 'w', encoding='utf-8') as f:
            for msg in messages:
                f.write(json.dumps(msg.to_dict()) + '\n')

        self._logger.info(f"Persisted {len(messages)} messages from {bus_name} to {message_file}")

    def retrieve_messages(self, bus_name: str, limit: int = 100) -> List[BusMessage]:
        """Retrieve messages from file system."""
        bus_dir = self.storage_dir / bus_name
        if not bus_dir.exists():
            return []

        messages = []
        message_files = sorted(bus_dir.glob("messages_*.jsonl"), reverse=True)

        for message_file in message_files:
            if len(messages) >= limit:
                break

            with open(message_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(messages) >= limit:
                        break
                    if not line.strip():
                        continue
                    # Note: Full reconstruction would require Signal deserialization
                    # For now, we just store the messages for historical purposes
                    messages.append(json.loads(line))

        return messages


# Global message persistence backend
_message_persistence_backend: Optional[MessagePersistenceBackend] = None


def configure_message_persistence(backend: MessagePersistenceBackend) -> None:
    """Configure the global message persistence backend."""
    global _message_persistence_backend
    _message_persistence_backend = backend


def get_message_persistence_backend() -> Optional[MessagePersistenceBackend]:
    """Get the configured message persistence backend, or create default."""
    global _message_persistence_backend
    if _message_persistence_backend is None:
        _message_persistence_backend = FileSystemMessagePersistence()
    return _message_persistence_backend


@dataclass
class SignalBus:
    """
    Bus de señales.
    
    Principios:
    1. Nada circula sin contrato
    2. Todo se registra
    3. Los consumidores analizan, no ejecutan
    """
    
    bus_type: BusType
    name: str = ""
    
    # Cola de mensajes
    _queue: Queue = field(default_factory=Queue)
    _lock: Lock = field(default_factory=Lock)
    
    # Suscriptores
    _subscribers:  Dict[str, ConsumptionContract] = field(default_factory=dict)
    
    # Historial (NUNCA se borra)
    _message_history: List[BusMessage] = field(default_factory=list)
    _max_history_size: int = 100000
    
    # Estadísticas
    _stats: Dict[str, int] = field(default_factory=lambda: {
        "total_published": 0,
        "total_delivered": 0,
        "total_rejected": 0,
        "total_errors": 0
    })
    
    # Logger
    _logger: logging.Logger = field(default=None)
    
    def __post_init__(self):
        if not self.name:
            self. name = self. bus_type.value
        if self._logger is None:
            self._logger = logging.getLogger(f"SISAS.Bus.{self.name}")
    
    def publish(
        self,
        signal: Signal,
        publisher_vehicle: str,
        publication_contract: PublicationContract
    ) -> tuple[bool, str]:
        """
        Publica una señal en el bus.
        
        Retorna (éxito, mensaje/error)
        """
        # Validar contrato
        is_valid, errors = publication_contract.validate_signal(signal)
        
        if not is_valid: 
            self._stats["total_rejected"] += 1
            error_msg = f"Contract validation failed: {errors}"
            self._logger.warning(error_msg)
            return (False, error_msg)
        
        # Verificar que el bus está permitido
        if self.name not in publication_contract.allowed_buses:
            self._stats["total_rejected"] += 1
            error_msg = f"Bus '{self. name}' not in allowed buses"
            self._logger.warning(error_msg)
            return (False, error_msg)
        
        # Crear mensaje
        message = BusMessage(
            signal=signal,
            publisher_vehicle=publisher_vehicle
        )
        
        # Encolar mensaje
        with self._lock:
            self._queue.put(message)
            self._message_history.append(message)
            
            # Limitar historial si excede máximo
            if len(self._message_history) > self._max_history_size:
                # No borramos, movemos a almacenamiento persistente
                self._persist_overflow()
            
            self._stats["total_published"] += 1
        
        self._logger.info(
            f"Signal published: {signal.signal_type} from {publisher_vehicle}"
        )
        
        # Notificar a suscriptores
        self._notify_subscribers(message)
        
        return (True, message.message_id)
    
    def subscribe(self, contract: ConsumptionContract) -> bool:
        """
        Suscribe un consumidor al bus.
        """
        if self.name not in contract.subscribed_buses:
            self._logger.warning(
                f"Consumer {contract.consumer_id} tried to subscribe to "
                f"non-allowed bus {self.name}"
            )
            return False
        
        with self._lock:
            self._subscribers[contract.consumer_id] = contract
        
        self._logger.info(f"Consumer {contract.consumer_id} subscribed to {self.name}")
        return True
    
    def unsubscribe(self, consumer_id: str) -> bool:
        """Desuscribe un consumidor"""
        with self._lock:
            if consumer_id in self._subscribers:
                del self._subscribers[consumer_id]
                self._logger.info(f"Consumer {consumer_id} unsubscribed from {self.name}")
                return True
        return False
    
    def _notify_subscribers(self, message: BusMessage):
        """Notifica a todos los suscriptores que coincidan"""
        for consumer_id, contract in self._subscribers.items():
            if contract.matches_signal(message.signal):
                try:
                    if contract.on_receive: 
                        contract.on_receive(message. signal, consumer_id)
                    message.acknowledge(consumer_id)
                    self._stats["total_delivered"] += 1
                except Exception as e: 
                    self._stats["total_errors"] += 1
                    self._logger.error(
                        f"Error notifying {consumer_id}: {str(e)}"
                    )
                    if contract.on_process_error:
                        contract. on_process_error(message. signal, consumer_id, e)
    
    def get_pending_messages(self) -> List[BusMessage]:
        """Obtiene mensajes pendientes sin vaciar la cola"""
        with self._lock:
            return list(self._queue.queue)
    
    def consume_next(self, timeout: float = 1.0) -> Optional[BusMessage]:
        """Consume el siguiente mensaje de la cola"""
        try:
            return self._queue.get(timeout=timeout)
        except Empty: 
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas del bus"""
        return self._stats. copy()
    
    def check_consumer_backpressure(self, consumer_id: str, threshold: int = 100) -> Dict[str, Any]:
        """
        ENHANCEMENT: Check if a consumer is experiencing backpressure.
        
        Backpressure occurs when a consumer cannot keep up with the rate of
        incoming signals. This can cause the bus queue to grow unbounded.
        
        Args:
            consumer_id: Consumer to check
            threshold: Number of unacknowledged messages that indicates backpressure
            
        Returns:
            Dict with backpressure status and metrics
        """
        backpressure_status = {
            "consumer_id": consumer_id,
            "has_backpressure": False,
            "unacknowledged_count": 0,
            "oldest_unacknowledged_age_seconds": 0,
            "recommendation": "normal_operation"
        }
        
        # Count unacknowledged messages for this consumer
        unacknowledged = []
        for msg in self._message_history:
            if consumer_id not in msg.acknowledged_by:
                unacknowledged.append(msg)
        
        backpressure_status["unacknowledged_count"] = len(unacknowledged)
        
        if len(unacknowledged) > threshold:
            backpressure_status["has_backpressure"] = True
            backpressure_status["recommendation"] = "slow_down_publishing"
            
            # Calculate age of oldest unacknowledged message
            if unacknowledged:
                oldest = min(unacknowledged, key=lambda m: m.published_at)
                age = (datetime.utcnow() - oldest.published_at).total_seconds()
                backpressure_status["oldest_unacknowledged_age_seconds"] = age
                
                self._logger.warning(
                    f"[BACKPRESSURE DETECTED] Consumer {consumer_id} has {len(unacknowledged)} "
                    f"unacknowledged messages (threshold: {threshold}), oldest: {age:.0f}s"
                )
        
        return backpressure_status
    
    def adaptive_publish_rate(self, target_consumer: Optional[str] = None) -> float:
        """
        ENHANCEMENT: Calculate adaptive publishing rate based on consumer health.
        
        Returns a multiplier (0.0-1.0) to apply to publishing rate:
        - 1.0 = full speed (no backpressure)
        - 0.5 = slow down by 50%
        - 0.1 = slow down by 90% (severe backpressure)
        
        Args:
            target_consumer: Optional specific consumer to check (checks all if None)
            
        Returns:
            Rate multiplier between 0.1 and 1.0
        """
        consumers_to_check = [target_consumer] if target_consumer else list(self._subscribers.keys())
        
        max_backpressure = 0.0
        for consumer_id in consumers_to_check:
            bp_status = self.check_consumer_backpressure(consumer_id)
            if bp_status["has_backpressure"]:
                # Calculate backpressure severity (0.0-1.0)
                unack_count = bp_status["unacknowledged_count"]
                severity = min(1.0, unack_count / 500)  # 500 messages = full backpressure
                max_backpressure = max(max_backpressure, severity)
        
        # Convert severity to rate multiplier (inverse relationship)
        rate_multiplier = max(0.1, 1.0 - max_backpressure)
        
        return rate_multiplier
    
    def get_subscriber_count(self) -> int:
        """Número de suscriptores"""
        return len(self._subscribers)
    
    def _persist_overflow(self):
        """Persiste mensajes cuando excede el límite"""
        overflow_count = len(self._message_history) - self._max_history_size
        if overflow_count > 0:
            # Los primeros N mensajes van a persistencia
            to_persist = self._message_history[:overflow_count]
            self._message_history = self._message_history[overflow_count:]

            # IMPLEMENTED: Persist messages to storage backend
            persistence_backend = get_message_persistence_backend()
            if persistence_backend:
                try:
                    persistence_backend.persist_messages(self.name, to_persist)
                    self._logger.info(f"Persisted {overflow_count} messages from {self.name} to storage")
                except Exception as e:
                    self._logger.error(f"Failed to persist messages from {self.name}: {e}")
                    # Keep messages in memory if persistence fails
                    self._message_history = to_persist + self._message_history
            else:
                self._logger.warning(f"No persistence backend configured, messages from {self.name} will be lost")


@dataclass
class BusRegistry:
    """
    Registro central de todos los buses.
    """
    
    buses: Dict[str, SignalBus] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)
    
    def __post_init__(self):
        # Crear buses por defecto para cada categoría
        for bus_type in BusType:
            self.create_bus(bus_type)
    
    def create_bus(self, bus_type: BusType, name: str = None) -> SignalBus:
        """Crea un nuevo bus"""
        bus_name = name or bus_type.value
        with self._lock:
            if bus_name not in self.buses:
                self.buses[bus_name] = SignalBus(
                    bus_type=bus_type,
                    name=bus_name
                )
        return self.buses[bus_name]
    
    def get_bus(self, name: str) -> Optional[SignalBus]:
        """Obtiene un bus por nombre"""
        return self.buses.get(name)
    
    def get_bus_for_signal(self, signal: Signal) -> SignalBus:
        """Obtiene el bus apropiado para una señal según su categoría"""
        category_to_bus = {
            SignalCategory.STRUCTURAL: BusType.STRUCTURAL,
            SignalCategory.INTEGRITY: BusType.INTEGRITY,
            SignalCategory.EPISTEMIC: BusType.EPISTEMIC,
            SignalCategory.CONTRAST:  BusType.CONTRAST,
            SignalCategory.OPERATIONAL:  BusType.OPERATIONAL,
            SignalCategory.CONSUMPTION:  BusType.CONSUMPTION,
            SignalCategory.ORCHESTRATION: BusType.ORCHESTRATION,
        }
        bus_type = category_to_bus.get(signal.category, BusType.UNIVERSAL)
        return self.buses[bus_type. value]
    
    def publish_to_appropriate_bus(
        self,
        signal: Signal,
        publisher_vehicle: str,
        publication_contract: PublicationContract
    ) -> tuple[bool, str]:
        """Publica una señal en el bus apropiado según su categoría"""
        bus = self.get_bus_for_signal(signal)
        return bus.publish(signal, publisher_vehicle, publication_contract)
    
    def get_all_stats(self) -> Dict[str, Dict[str, int]]:
        """Estadísticas de todos los buses"""
        return {name: bus.get_stats() for name, bus in self.buses. items()}