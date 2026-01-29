# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signals.py

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext

@dataclass
class SignalsAggregatorVehicle(BaseVehicle):
    """
    Vehículo: signals
    Responsabilidad: Vehículo agregador.
    """
    vehicle_id: str = "signals"
    vehicle_name: str = "Signals Aggregator Vehicle"
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=True,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=[]
    ))

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        # Logic to be implemented
        return []