# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_loader.py

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext

@dataclass
class SignalLoaderVehicle(BaseVehicle):
    """
    Vehículo: signal_loader
    Responsabilidad: Carga de archivos.
    """
    vehicle_id: str = "signal_loader"
    vehicle_name: str = "Signal Loader Vehicle"
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=True,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=False,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=[]
    ))

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        # Logic to be implemented
        return []