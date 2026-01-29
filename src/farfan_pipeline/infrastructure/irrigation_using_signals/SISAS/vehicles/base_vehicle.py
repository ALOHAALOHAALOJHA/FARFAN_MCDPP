# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/base_vehicle.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from datetime import datetime

from .. core.signal import Signal, SignalContext, SignalSource
from ..core.event import Event, EventStore, EventType, EventPayload
from ..core.contracts import PublicationContract, ContractRegistry
from ..core.bus import BusRegistry, SignalBus


@dataclass
class VehicleCapabilities: 
    """Declaración de capacidades de un vehículo"""
    can_load:  bool = False          # Puede cargar datos canónicos
    can_scope: bool = False         # Puede aplicar scope/contexto
    can_extract: bool = False       # Puede extraer evidencia
    can_transform: bool = False     # Puede transformar datos
    can_enrich: bool = False        # Puede enriquecer con señales
    can_validate: bool = False      # Puede validar contratos
    can_irrigate: bool = False      # Puede ejecutar irrigación
    
    signal_types_produced: List[str] = field(default_factory=list)
    signal_types_consumed: List[str] = field(default_factory=list)


@dataclass
class BaseVehicle(ABC):
    """
    Clase base abstracta para todos los vehículos SISAS.
    
    Un vehículo es un componente que: 
    1. Carga datos canónicos
    2. Los transforma en eventos
    3. Genera señales a partir de eventos
    4. Publica señales en buses
    """
    
    vehicle_id: str
    vehicle_name: str
    
    # Capacidades
    capabilities: VehicleCapabilities = field(default_factory=VehicleCapabilities)
    
    # Contrato de publicación
    publication_contract: Optional[PublicationContract] = None
    
    # Registros
    event_store: EventStore = field(default_factory=EventStore)
    bus_registry: Optional[BusRegistry] = None
    contract_registry: Optional[ContractRegistry] = None
    
    # Estado
    is_active: bool = False
    last_activity: Optional[datetime] = None
    
    # Estadísticas
    stats: Dict[str, int] = field(default_factory=lambda: {
        "events_created": 0,
        "signals_generated": 0,
        "signals_published": 0,
        "errors":  0
    })
    
    @abstractmethod
    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa datos y genera señales.
        Cada vehículo implementa su lógica específica.
        """
        pass
    
    def create_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source_file: str,
        source_path: str,
        phase: str,
        consumer_scope: str
    ) -> Event:
        """Crea un evento y lo registra"""
        
        # Determine EventType safely
        try:
            e_type = EventType(event_type)
        except ValueError:
            # Fallback or mapping logic if string doesn't match enum value exactly
            # For now, defaulting to CANONICAL_DATA_LOADED if unknown or mapped
            e_type = EventType.CANONICAL_DATA_LOADED

        event = Event(
            event_type=e_type,
            source_file=source_file,
            source_path=source_path,
            payload=EventPayload(data=payload),
            phase=phase,
            consumer_scope=consumer_scope,
            source_component=self.vehicle_id
        )
        
        self.event_store.append(event)
        self.stats["events_created"] += 1
        self.last_activity = datetime.utcnow()
        
        return event
    
    def create_signal_source(self, event: Event) -> SignalSource:
        """Crea SignalSource a partir de un evento"""
        return SignalSource(
            event_id=event.event_id,
            source_file=event.source_file,
            source_path=event.source_path,
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=self.vehicle_id
        )
    
    def publish_signal(self, signal: Signal) -> tuple[bool, str]:
        """Publica una señal en el bus apropiado"""
        if not self.bus_registry:
            return (False, "No bus registry configured")
        
        if not self.publication_contract:
            return (False, "No publication contract configured")
        
        success, result = self.bus_registry.publish_to_appropriate_bus(
            signal=signal,
            publisher_vehicle=self.vehicle_id,
            publication_contract=self. publication_contract
        )
        
        if success:
            self.stats["signals_published"] += 1
        else:
            self.stats["errors"] += 1
        
        return (success, result)
    
    def activate(self):
        """Activa el vehículo"""
        self. is_active = True
        self.last_activity = datetime.utcnow()
    
    def deactivate(self):
        """Desactiva el vehículo"""
        self. is_active = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del vehículo"""
        return {
            "vehicle_id": self.vehicle_id,
            "vehicle_name":  self.vehicle_name,
            "is_active": self.is_active,
            "last_activity":  self.last_activity. isoformat() if self.last_activity else None,
            "capabilities": {
                "can_load": self. capabilities.can_load,
                "can_scope": self.capabilities.can_scope,
                "can_extract": self.capabilities. can_extract,
                "signal_types_produced": self.capabilities.signal_types_produced
            },
            "stats": self.stats
        }