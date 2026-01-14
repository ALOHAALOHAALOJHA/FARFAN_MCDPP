# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/base_consumer.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.signal import Signal
from ..core.contracts import ConsumptionContract
from ..core.bus import BusRegistry

@dataclass
class BaseConsumer(ABC):
    """
    Clase base para todos los consumidores SISAS.

    Responsabilidades:
    1. Suscribirse a buses
    2. Recibir señales
    3. Filtrar por contrato (ya lo hace el bus, pero el consumidor valida)
    4. Procesar analíticamente (generar insights, no acciones)
    5. Reportar salud
    """

    consumer_id: str
    consumer_phase: str

    # Contrato de consumo
    consumption_contract: Optional[ConsumptionContract] = None

    # Estado
    is_active: bool = False
    last_activity: Optional[datetime] = None

    # Estadísticas
    stats: Dict[str, int] = field(default_factory=lambda: {
        "signals_received": 0,
        "signals_processed": 0,
        "signals_failed": 0,
        "errors": 0
    })

    bus_registry: Optional[BusRegistry] = None

    def __post_init__(self):
        if not self.consumption_contract:
            # Should be set by subclass or dependency injection
            pass

    def subscribe(self, bus_registry: BusRegistry) -> bool:
        """Suscribe el consumidor a los buses definidos en su contrato"""
        self.bus_registry = bus_registry
        if not self.consumption_contract:
            return False

        success = True
        for bus_name in self.consumption_contract.subscribed_buses:
            bus = bus_registry.get_bus(bus_name)
            if bus:
                # El bus usa el contrato para filtrar
                # Modificamos el contrato para setear los callbacks a self
                self.consumption_contract.on_receive = self.on_receive
                self.consumption_contract.on_process_error = self.on_process_error

                if not bus.subscribe(self.consumption_contract):
                    success = False
            else:
                success = False

        if success:
            self.is_active = True

        return success

    def on_receive(self, signal: Signal, consumer_id: str):
        """Callback cuando se recibe una señal"""
        self.stats["signals_received"] += 1
        self.last_activity = datetime.utcnow()

        try:
            result = self.process_signal(signal)
            self.stats["signals_processed"] += 1
        except Exception as e:
            self.stats["signals_failed"] += 1
            self.on_process_error(signal, consumer_id, e)

    def on_process_error(self, signal: Signal, consumer_id: str, error: Exception):
        """Callback de error"""
        self.stats["errors"] += 1
        # Log error

    @abstractmethod
    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa una señal. Debe ser implementado por subclases.
        Retorna un dict con resultados del análisis.
        """
        pass

    def get_health(self) -> Dict[str, Any]:
        """Retorna estado de salud"""
        return {
            "consumer_id": self.consumer_id,
            "is_active": self.is_active,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "stats": self.stats
        }
