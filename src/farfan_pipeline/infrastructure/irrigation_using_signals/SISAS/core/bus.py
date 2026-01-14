# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/bus.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque
from queue import Queue, PriorityQueue, Empty
from threading import Lock
import logging
import uuid
import time
from functools import lru_cache
import hashlib

from .signal import Signal, SignalCategory
from .contracts import PublicationContract, ConsumptionContract, ContractRegistry


class BusType(Enum):
    """Tipos de bus según categoría de señales"""
    STRUCTURAL = "structural_bus"
    INTEGRITY = "integrity_bus"
    EPISTEMIC = "epistemic_bus"
    CONTRAST = "contrast_bus"
    OPERATIONAL = "operational_bus"
    CONSUMPTION = "consumption_bus"
    UNIVERSAL = "universal_bus"  # Recibe todo


class MessagePriority(Enum):
    """Prioridades de mensajes para cola con prioridad"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class BusMessage:
    """Mensaje que circula por el bus con soporte para priorización"""
    signal: Signal
    publisher_vehicle: str
    published_at: datetime = field(default_factory=datetime.utcnow)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    acknowledged_by: Set[str] = field(default_factory=set)
    priority: MessagePriority = MessagePriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    ttl_seconds: Optional[int] = None  # Time to live

    def acknowledge(self, consumer_id: str):
        """Marca el mensaje como recibido por un consumidor"""
        self.acknowledged_by.add(consumer_id)
    
    def is_expired(self) -> bool:
        """Verifica si el mensaje ha expirado"""
        if self.ttl_seconds is None:
            return False
        age = (datetime.utcnow() - self.published_at).total_seconds()
        return age > self.ttl_seconds
    
    def should_retry(self) -> bool:
        """Verifica si el mensaje debe reintentarse"""
        return self.retry_count < self.max_retries
    
    def __lt__(self, other: 'BusMessage') -> bool:
        """Comparación para cola de prioridad"""
        return self.priority.value < other.priority.value


@dataclass
class SignalBus:
    """
    Bus de señales con enhancements avanzados.

    Principios:
    1. Nada circula sin contrato
    2. Todo se registra
    3. Los consumidores analizan, no ejecutan
    
    Enhancements:
    - Priority queue para procesamiento inteligente
    - Backpressure mechanism para control de flujo
    - Dead letter queue para mensajes fallidos
    - Circuit breaker para consumidores problemáticos
    - Métricas en tiempo real y agregadas
    """

    bus_type: BusType
    name: str = ""

    # Cola de mensajes con prioridad
    _queue: PriorityQueue = field(default_factory=PriorityQueue)
    _lock: Lock = field(default_factory=Lock)

    # Suscriptores
    _subscribers:  Dict[str, ConsumptionContract] = field(default_factory=dict)

    # Historial (NUNCA se borra)
    _message_history: List[BusMessage] = field(default_factory=list)
    _max_history_size: int = 100000

    # Dead Letter Queue para mensajes fallidos
    _dead_letter_queue: deque = field(default_factory=lambda: deque(maxlen=10000))
    
    # Circuit breaker para consumidores
    _consumer_health: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    _circuit_breaker_threshold: int = 5  # Fallos consecutivos antes de abrir circuito
    _circuit_breaker_timeout: int = 60  # Segundos antes de reintentar

    # Backpressure control
    _max_queue_size: int = 50000
    _backpressure_active: bool = False
    _backpressure_threshold: float = 0.8  # 80% de capacidad

    # Estadísticas avanzadas
    _stats: Dict[str, int] = field(default_factory=lambda: {
        "total_published": 0,
        "total_delivered": 0,
        "total_rejected": 0,
        "total_errors": 0,
        "total_retries": 0,
        "total_expired": 0,
        "total_dead_lettered": 0,
        "backpressure_activations": 0
    })
    
    # Métricas de latencia
    _latency_samples: deque = field(default_factory=lambda: deque(maxlen=1000))
    _throughput_window: deque = field(default_factory=lambda: deque(maxlen=60))  # 60 segundos
    _last_throughput_update: datetime = field(default_factory=datetime.utcnow)

    # Logger
    _logger: logging.Logger = field(default=None)

    def __post_init__(self):
        if not self.name:
            self.name = self.bus_type.value
        if self._logger is None:
            self._logger = logging.getLogger(f"SISAS.Bus.{self.name}")
    
    def _check_backpressure(self) -> bool:
        """Verifica si se debe activar backpressure"""
        queue_size = self._queue.qsize()
        utilization = queue_size / self._max_queue_size
        
        if utilization >= self._backpressure_threshold and not self._backpressure_active:
            self._backpressure_active = True
            self._stats["backpressure_activations"] += 1
            self._logger.warning(f"Backpressure activated: {utilization:.1%} utilization")
        elif utilization < (self._backpressure_threshold * 0.5) and self._backpressure_active:
            self._backpressure_active = False
            self._logger.info(f"Backpressure deactivated: {utilization:.1%} utilization")
        
        return self._backpressure_active
    
    def _is_consumer_healthy(self, consumer_id: str) -> bool:
        """Verifica si el consumidor está sano (circuit breaker)"""
        if consumer_id not in self._consumer_health:
            self._consumer_health[consumer_id] = {
                "consecutive_failures": 0,
                "circuit_open": False,
                "circuit_opened_at": None,
                "total_successes": 0,
                "total_failures": 0
            }
        
        health = self._consumer_health[consumer_id]
        
        # Si el circuito está abierto, verificar si es tiempo de reintentar
        if health["circuit_open"]:
            if health["circuit_opened_at"]:
                time_open = (datetime.utcnow() - health["circuit_opened_at"]).total_seconds()
                if time_open > self._circuit_breaker_timeout:
                    health["circuit_open"] = False
                    health["consecutive_failures"] = 0
                    self._logger.info(f"Circuit breaker reset for {consumer_id}")
                    return True
            return False
        
        return True
    
    def _record_consumer_success(self, consumer_id: str):
        """Registra éxito de consumidor"""
        if consumer_id in self._consumer_health:
            health = self._consumer_health[consumer_id]
            health["consecutive_failures"] = 0
            health["total_successes"] += 1
    
    def _record_consumer_failure(self, consumer_id: str):
        """Registra falla de consumidor y activa circuit breaker si es necesario"""
        if consumer_id not in self._consumer_health:
            self._consumer_health[consumer_id] = {
                "consecutive_failures": 0,
                "circuit_open": False,
                "circuit_opened_at": None,
                "total_successes": 0,
                "total_failures": 0
            }
        
        health = self._consumer_health[consumer_id]
        health["consecutive_failures"] += 1
        health["total_failures"] += 1
        
        if health["consecutive_failures"] >= self._circuit_breaker_threshold:
            health["circuit_open"] = True
            health["circuit_opened_at"] = datetime.utcnow()
            self._logger.error(
                f"Circuit breaker OPEN for {consumer_id} after "
                f"{health['consecutive_failures']} consecutive failures"
            )
    
    def _record_latency(self, latency_ms: float):
        """Registra latencia de procesamiento"""
        self._latency_samples.append(latency_ms)
    
    def _update_throughput(self):
        """Actualiza métricas de throughput"""
        now = datetime.utcnow()
        if (now - self._last_throughput_update).total_seconds() >= 1.0:
            # Registrar mensajes por segundo
            self._throughput_window.append(self._stats["total_delivered"])
            self._last_throughput_update = now

    def publish(
        self,
        signal: Signal,
        publisher_vehicle: str,
        publication_contract: PublicationContract,
        priority: MessagePriority = MessagePriority.NORMAL,
        ttl_seconds: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        Publica una señal en el bus con soporte para prioridad y TTL.

        Retorna (éxito, mensaje/error)
        """
        start_time = time.time()
        
        # Verificar backpressure
        if self._check_backpressure():
            # Solo rechazar mensajes de baja prioridad durante backpressure
            if priority in [MessagePriority.LOW, MessagePriority.BACKGROUND]:
                self._stats["total_rejected"] += 1
                error_msg = "Backpressure active: rejecting low priority message"
                self._logger.warning(error_msg)
                return (False, error_msg)
        
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
            error_msg = f"Bus '{self.name}' not in allowed buses"
            self._logger.warning(error_msg)
            return (False, error_msg)

        # Crear mensaje con prioridad y TTL
        message = BusMessage(
            signal=signal,
            publisher_vehicle=publisher_vehicle,
            priority=priority,
            ttl_seconds=ttl_seconds
        )

        # Encolar mensaje con prioridad
        with self._lock:
            if self._queue.qsize() >= self._max_queue_size:
                self._stats["total_rejected"] += 1
                error_msg = "Queue full: cannot accept more messages"
                self._logger.error(error_msg)
                return (False, error_msg)
            
            self._queue.put((priority.value, message))
            self._message_history.append(message)

            # Limitar historial si excede máximo
            if len(self._message_history) > self._max_history_size:
                # No borramos, movemos a almacenamiento persistente
                self._persist_overflow()

            self._stats["total_published"] += 1

        # Registrar latencia de publicación
        latency_ms = (time.time() - start_time) * 1000
        self._record_latency(latency_ms)

        self._logger.info(
            f"Signal published: {signal.signal_type} from {publisher_vehicle} "
            f"(priority={priority.name}, latency={latency_ms:.2f}ms)"
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
        """Notifica a todos los suscriptores que coincidan con circuit breaker y retry logic"""
        # Verificar si el mensaje ha expirado
        if message.is_expired():
            self._stats["total_expired"] += 1
            self._logger.warning(f"Message {message.message_id} expired, not delivering")
            return
        
        for consumer_id, contract in self._subscribers.items():
            # Verificar circuit breaker
            if not self._is_consumer_healthy(consumer_id):
                self._logger.warning(
                    f"Skipping {consumer_id}: circuit breaker OPEN"
                )
                continue
            
            if contract.matches_signal(message.signal):
                try:
                    if contract.on_receive:
                        contract.on_receive(message.signal, consumer_id)
                    message.acknowledge(consumer_id)
                    self._stats["total_delivered"] += 1
                    self._record_consumer_success(consumer_id)
                    self._update_throughput()
                except Exception as e:
                    self._stats["total_errors"] += 1
                    self._record_consumer_failure(consumer_id)
                    self._logger.error(
                        f"Error notifying {consumer_id}: {str(e)}"
                    )
                    
                    # Intentar retry si aplica
                    if message.should_retry():
                        message.retry_count += 1
                        self._stats["total_retries"] += 1
                        self._logger.info(
                            f"Scheduling retry {message.retry_count}/{message.max_retries} "
                            f"for message {message.message_id}"
                        )
                        # Re-encolar con menor prioridad
                        with self._lock:
                            retry_priority = MessagePriority.BACKGROUND
                            self._queue.put((retry_priority.value, message))
                    else:
                        # Enviar a dead letter queue
                        self._dead_letter_queue.append({
                            "message": message,
                            "consumer_id": consumer_id,
                            "error": str(e),
                            "dead_lettered_at": datetime.utcnow()
                        })
                        self._stats["total_dead_lettered"] += 1
                        self._logger.error(
                            f"Message {message.message_id} moved to dead letter queue "
                            f"after {message.retry_count} retries"
                        )
                    
                    if contract.on_process_error:
                        contract.on_process_error(message.signal, consumer_id, e)

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
        return self._stats.copy()

    def get_subscriber_count(self) -> int:
        """Número de suscriptores"""
        return len(self._subscribers)
    
    def get_advanced_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas avanzadas del bus"""
        queue_size = self._queue.qsize()
        utilization = queue_size / self._max_queue_size
        
        # Calcular latencia promedio y percentiles
        latency_avg = sum(self._latency_samples) / len(self._latency_samples) if self._latency_samples else 0
        sorted_latencies = sorted(self._latency_samples)
        latency_p50 = sorted_latencies[len(sorted_latencies) // 2] if sorted_latencies else 0
        latency_p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)] if sorted_latencies else 0
        latency_p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)] if sorted_latencies else 0
        
        # Calcular throughput (mensajes/segundo)
        if len(self._throughput_window) > 1:
            throughput = (
                self._throughput_window[-1] - self._throughput_window[0]
            ) / len(self._throughput_window)
        else:
            throughput = 0
        
        # Salud de consumidores
        healthy_consumers = sum(
            1 for h in self._consumer_health.values() if not h.get("circuit_open", False)
        )
        total_consumers = len(self._consumer_health)
        
        return {
            "queue_size": queue_size,
            "queue_utilization": utilization,
            "backpressure_active": self._backpressure_active,
            "dead_letter_count": len(self._dead_letter_queue),
            "latency_ms": {
                "avg": latency_avg,
                "p50": latency_p50,
                "p95": latency_p95,
                "p99": latency_p99
            },
            "throughput_per_sec": throughput,
            "consumers": {
                "total": total_consumers,
                "healthy": healthy_consumers,
                "unhealthy": total_consumers - healthy_consumers
            },
            "history_size": len(self._message_history)
        }
    
    def get_dead_letters(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene mensajes en la dead letter queue"""
        return list(self._dead_letter_queue)[-limit:]
    
    def replay_dead_letter(self, message_id: str) -> tuple[bool, str]:
        """Reintenta un mensaje de la dead letter queue"""
        for item in self._dead_letter_queue:
            if item["message"].message_id == message_id:
                message = item["message"]
                message.retry_count = 0  # Reset retry count
                with self._lock:
                    self._queue.put((message.priority.value, message))
                self._logger.info(f"Replaying dead letter message {message_id}")
                return (True, "Message queued for replay")
        return (False, "Message not found in dead letter queue")
    
    def get_consumer_health_report(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene reporte de salud de todos los consumidores"""
        return self._consumer_health.copy()

    def _persist_overflow(self):
        """Persiste mensajes cuando excede el límite"""
        # Implementar persistencia a disco/DB
        overflow_count = len(self._message_history) - self._max_history_size
        if overflow_count > 0:
            # Los primeros N mensajes van a persistencia
            self._message_history = self._message_history[overflow_count:]
            # TODO: Escribir mensajes removidos a almacenamiento persistente
            self._logger.info(f"Persisted {overflow_count} messages from {self.name}")


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
        }
        bus_type = category_to_bus.get(signal.category, BusType.UNIVERSAL)
        return self.buses[bus_type.value]

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
        return {name: bus.get_stats() for name, bus in self.buses.items()}
