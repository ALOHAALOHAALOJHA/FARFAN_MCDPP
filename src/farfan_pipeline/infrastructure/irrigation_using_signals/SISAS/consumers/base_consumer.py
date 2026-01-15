# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/base_consumer.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from ..core.signal import Signal
from ..core.contracts import ConsumptionContract
from ..core.bus import BusRegistry


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
        """Punto de entrada para señales desde el bus"""
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
            if self.consumption_contract and self.consumption_contract.on_process_error:
                self.consumption_contract.on_process_error(signal, self.consumer_id, e)
            raise e

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