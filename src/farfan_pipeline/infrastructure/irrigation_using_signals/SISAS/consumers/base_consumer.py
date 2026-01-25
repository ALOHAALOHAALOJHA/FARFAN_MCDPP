# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/base_consumer.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime
import logging

from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.contracts import ConsumptionContract
from ..core.bus import BusRegistry

if TYPE_CHECKING:
    from ..signal_types.types.operational import FailureModeSignal, FailureMode
    from ..signal_types.types.consumption import ConsumerHealthSignal


@dataclass
class ConsumerHealth:
    """Estado de salud de un consumidor"""
    consumer_id: str
    is_active: bool = False
    signals_received: int = 0
    signals_processed: int = 0
    signals_failed: int = 0
    last_signal_at: Optional[datetime] = None
    error_rate: float = 0.0
    uptime_seconds: float = 0.0


@dataclass
class BaseConsumer(ABC):
    """
    Clase base abstracta para todos los consumidores SISAS.
    
    Un consumidor:
    1. Se suscribe a buses mediante un contrato.
    2. Recibe y filtra señales.
    3. Analiza las señales (NO ejecuta decisiones).
    4. Reporta su salud.
    """
    
    consumer_id: str
    consumer_phase: str
    
    # Contrato de consumo
    consumption_contract: Optional[ConsumptionContract] = None
    
    # Registro de buses
    bus_registry: Optional[BusRegistry] = None
    
    # Estado
    is_active: bool = False
    start_time: datetime = field(default_factory=datetime.utcnow)
    
    # Estadísticas
    stats: Dict[str, int] = field(default_factory=lambda: {
        "received": 0,
        "processed": 0,
        "failed": 0
    })
    
    # Logger
    _logger: logging.Logger = field(default=None)

    def __post_init__(self):
        if self._logger is None:
            self._logger = logging.getLogger(f"SISAS.Consumer.{self.consumer_id}")

    def subscribe(self, bus_registry: BusRegistry):
        """Se suscribe a los buses permitidos por su contrato"""
        self.bus_registry = bus_registry
        
        if not self.consumption_contract:
            self._logger.error("No consumption contract defined")
            return
            
        # Configurar el callback de recepción
        self.consumption_contract.on_receive = self.receive_signal
        
        for bus_name in self.consumption_contract.subscribed_buses:
            bus = self.bus_registry.get_bus(bus_name)
            if bus:
                success = bus.subscribe(self.consumption_contract)
                if success:
                    self._logger.info(f"Subscribed to {bus_name}")
                else:
                    self._logger.warning(f"Failed to subscribe to {bus_name}")
        
        self.is_active = True

    def receive_signal(self, signal: Signal, consumer_id: str):
        """
        Punto de entrada para señales desde el bus.
        
        Enhanced with automatic failure signal generation for feedback loop.
        """
        self.stats["received"] += 1
        
        try:
            self._logger.debug(f"Received signal {signal.signal_id} ({signal.signal_type})")
            
            # Procesar analíticamente
            result = self.process_signal(signal)
            
            self.stats["processed"] += 1
            return result
            
        except Exception as e:
            self.stats["failed"] += 1
            self._logger.error(f"Error processing signal: {str(e)}")
            
            # ENHANCED: Generate FailureModeSignal for feedback loop
            if self.bus_registry:
                try:
                    failure_signal = self._create_failure_signal(signal, e)
                    self._publish_failure_signal(failure_signal)
                except Exception as publish_error:
                    self._logger.error(f"Failed to publish failure signal: {publish_error}")
            
            # Call error callback if defined
            if self.consumption_contract and self.consumption_contract.on_process_error:
                self.consumption_contract.on_process_error(signal, self.consumer_id, e)
            raise e

    def _create_failure_signal(self, original_signal: Signal, error: Exception) -> 'FailureModeSignal':
        """
        FEEDBACK LOOP: Create FailureModeSignal when consumption fails.
        
        This implements the missing feedback mechanism identified in the architecture analysis.
        When a consumer fails to process a signal, it generates a new signal that:
        1. Alerts downstream consumers about the failure
        2. Provides operational observability
        3. Enables automated recovery mechanisms
        
        Args:
            original_signal: The signal that failed to process
            error: The exception that occurred
            
        Returns:
            FailureModeSignal describing the failure
        """
        from ..signal_types.types.operational import FailureModeSignal, FailureMode
        
        # Determine failure mode based on error type
        failure_mode_mapping = {
            ValueError: FailureMode.VALIDATION_ERROR,
            KeyError: FailureMode.VALIDATION_ERROR,  # Map to existing enum value
            TypeError: FailureMode.TRANSFORMATION_ERROR,
            RuntimeError: FailureMode.UNKNOWN,  # Map to existing enum value
        }
        failure_mode = failure_mode_mapping.get(type(error), FailureMode.UNKNOWN)
        
        # Create context for failure signal
        context = SignalContext(
            node_type="consumer",
            node_id=self.consumer_id,
            phase=self.consumer_phase,
            consumer_scope=original_signal.context.consumer_scope if hasattr(original_signal, 'context') else "UNKNOWN"
        )
        
        # Create source
        source = SignalSource(
            event_id=f"failure_{datetime.utcnow().timestamp()}",
            source_file=self.consumer_id,
            source_path=f"consumers/{self.consumer_phase}/{self.consumer_id}",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=f"consumer_{self.consumer_id}"
        )
        
        return FailureModeSignal(
            context=context,
            source=source,
            execution_id=f"{self.consumer_id}_{original_signal.signal_id if hasattr(original_signal, 'signal_id') else 'unknown'}",
            failure_mode=failure_mode,
            error_message=str(error)[:500],  # Truncate to 500 chars
            recoverable=failure_mode != FailureMode.SYSTEM_ERROR,
            retry_count=0,
            confidence=SignalConfidence.VERY_HIGH,  # High confidence in failure detection
            rationale=f"Consumer {self.consumer_id} failed to process {original_signal.signal_type if hasattr(original_signal, 'signal_type') else 'signal'}: {type(error).__name__}"
        )
    
    def _publish_failure_signal(self, failure_signal: 'FailureModeSignal'):
        """
        Publish failure signal to operational_bus for monitoring.
        
        This completes the feedback loop by ensuring failure information
        propagates back through the SISAS system.
        """
        operational_bus = self.bus_registry.get_bus("operational_bus")
        if operational_bus:
            # Create minimal publication contract for failure signals
            from ..core.contracts import PublicationContract, ContractStatus, SignalTypeSpec
            
            failure_contract = PublicationContract(
                contract_id=f"failure_{self.consumer_id}",
                publisher_vehicle=f"consumer_{self.consumer_id}",
                status=ContractStatus.ACTIVE,
                allowed_signal_types=[SignalTypeSpec(signal_type="FailureModeSignal")],
                allowed_buses=["operational_bus"],
                require_context=True,
                require_source=True
            )
            
            success, msg = operational_bus.publish(
                signal=failure_signal,
                publisher_vehicle=f"consumer_{self.consumer_id}",
                publication_contract=failure_contract
            )
            
            if success:
                self._logger.info(f"Published failure signal: {msg}")
            else:
                self._logger.warning(f"Failed to publish failure signal: {msg}")

    def generate_health_signal(self) -> 'ConsumerHealthSignal':
        """
        OBSERVABILITY: Generate ConsumerHealthSignal for monitoring.
        
        This provides rich operational metrics about consumer performance.
        Should be called periodically or on-demand for health checks.
        
        Returns:
            ConsumerHealthSignal with current health metrics
        """
        from ..signal_types.types.consumption import ConsumerHealthSignal
        
        health = self.get_health()
        
        context = SignalContext(
            node_type="consumer",
            node_id=self.consumer_id,
            phase=self.consumer_phase,
            consumer_scope="MONITORING"
        )
        
        source = SignalSource(
            event_id=f"health_{datetime.utcnow().timestamp()}",
            source_file=self.consumer_id,
            source_path=f"consumers/{self.consumer_phase}/{self.consumer_id}",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=f"consumer_{self.consumer_id}"
        )
        
        # Determine health status
        if health.error_rate > 0.5:
            status = "CRITICAL"
        elif health.error_rate > 0.2:
            status = "DEGRADED"
        elif not health.is_active:
            status = "INACTIVE"
        else:
            status = "HEALTHY"
        
        return ConsumerHealthSignal(
            context=context,
            source=source,
            consumer_id=self.consumer_id,
            status=status,
            signals_processed=health.signals_processed,
            signals_failed=health.signals_failed,
            error_rate=health.error_rate,
            uptime_seconds=health.uptime_seconds,
            confidence=SignalConfidence.VERY_HIGH,
            rationale=f"Consumer health metrics: {health.signals_processed} processed, {health.signals_failed} failed, {health.error_rate:.1%} error rate"
        )

    @abstractmethod
    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Lógica analítica específica del consumidor.
        Debe retornar un diccionario con los hallazgos.
        """
        pass

    def get_health(self) -> ConsumerHealth:
        """Obtiene reporte de salud"""
        total = self.stats["processed"] + self.stats["failed"]
        error_rate = (self.stats["failed"] / total) if total > 0 else 0.0
        
        return ConsumerHealth(
            consumer_id=self.consumer_id,
            is_active=self.is_active,
            signals_received=self.stats["received"],
            signals_processed=self.stats["processed"],
            signals_failed=self.stats["failed"],
            error_rate=error_rate,
            uptime_seconds=(datetime.utcnow() - self.start_time).total_seconds()
        )