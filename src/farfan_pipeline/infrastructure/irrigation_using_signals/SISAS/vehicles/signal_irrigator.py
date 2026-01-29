# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_irrigator.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import os
import json
from pathlib import Path

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event, EventStore, EventType, EventPayload
from ..core.bus import BusType, SignalBus
from ..core.contracts import ContractRegistry, IrrigationContract, ContractStatus

@dataclass
class IrrigationResult:
    """Resultado de una operación de irrigación"""
    success: bool
    file_path: str
    vehicles_executed: List[str]
    signals_generated: int
    consumers_notified: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SignalIrrigatorVehicle(BaseVehicle):
    """
    Vehículo: signal_irrigator

    Responsabilidad: Ejecución de irrigación end-to-end.

    Flujo de irrigación:
    1. Identificar archivo canónico
    2. Determinar vehículos asignados (via IrrigationContract)
    3. Ejecutar cada vehículo en orden
    4. Publicar señales a los buses correspondientes
    5. Notificar consumidores suscritos
    6. Reportar resultado

    Este vehículo NO genera señales - ORQUESTRA la irrigación.
    """
    vehicle_id: str = "signal_irrigator"
    vehicle_name: str = "Signal Irrigator Vehicle"

    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=False,
        can_validate=False,
        can_irrigate=True,
        signal_types_produced=[]
    ))

    # Dependencias inyectadas
    contract_registry: Optional[ContractRegistry] = None
    event_store: Optional[EventStore] = None
    vehicle_registry: Optional[Dict[str, 'BaseVehicle']] = None
    bus_registry: Optional[Dict[BusType, SignalBus]] = None

    # Estadísticas de irrigación
    irrigation_stats: Dict[str, Any] = field(default_factory=lambda: {
        "files_irrigated": 0,
        "signals_generated": 0,
        "consumers_notified": 0,
        "errors": 0,
        "last_irrigation_time": None
    })

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa solicitud de irrigación.

        Nota: Este vehículo no genera señales directamente.
        Retorna lista vacía para cumplir la interfaz.
        La irrigación real se ejecuta vía irrigate_file().
        """
        # Este vehículo es un orchestrator, no un productor de señales
        # Las solicitudes de irrigación vienen vía método irrigate_file()
        return []

    def irrigate_file(
        self,
        file_path: str,
        phase: str,
        consumer_scope: str = "default"
    ) -> IrrigationResult:
        """
        Ejecuta irrigación completa de un archivo canónico.

        Flujo:
        1. Cargar archivo (delega a signal_loader si está disponible)
        2. Buscar contrato de irrigación
        3. Ejecutar vehículos en orden
        4. Publicar señales
        5. Notificar consumidores
        """
        result = IrrigationResult(
            success=False,
            file_path=file_path,
            vehicles_executed=[],
            signals_generated=0,
            consumers_notified=0
        )

        try:
            # 1. Cargar archivo canónico
            file_data = self._load_canonical_file(file_path)
            if file_data is None:
                result.errors.append(f"Failed to load file: {file_path}")
                return result

            # 2. Buscar contrato de irrigación
            if self.contract_registry is None:
                result.warnings.append("No contract registry - using default irrigation")
                vehicles_to_use = self._get_default_vehicles_for_file(file_path)
            else:
                contract = self.contract_registry.get_irrigation_for_file(file_path)
                if contract is None:
                    result.warnings.append(f"No irrigation contract for {file_path} - using defaults")
                    vehicles_to_use = self._get_default_vehicles_for_file(file_path)
                else:
                    vehicles_to_use = contract.vehicles
                    # Verificar que el contrato es irrigable
                    if not contract.is_irrigable():
                        blocking = contract.get_blocking_gaps()
                        result.errors.append(f"Contract has blocking gaps: {blocking}")
                        return result

            # 3. Ejecutar cada vehículo
            all_signals = []
            for vehicle_id in vehicles_to_use:
                if self.vehicle_registry and vehicle_id in self.vehicle_registry:
                    vehicle = self.vehicle_registry[vehicle_id]

                    # Crear contexto para el vehículo
                    vehicle_context = SignalContext(
                        node_id=os.path.basename(file_path),
                        node_type=self._infer_node_type(file_path),
                        phase=phase,
                        consumer_scope=consumer_scope
                    )

                    # Ejecutar vehículo
                    try:
                        vehicle_signals = vehicle.process(file_data, vehicle_context)
                        all_signals.extend(vehicle_signals)
                        result.vehicles_executed.append(vehicle_id)
                    except Exception as e:
                        result.errors.append(f"Vehicle {vehicle_id} failed: {str(e)}")
                else:
                    result.warnings.append(f"Vehicle {vehicle_id} not found in registry")

            result.signals_generated = len(all_signals)

            # 4. Publicar señales a buses
            if self.bus_registry:
                consumers_count = self._publish_signals_to_buses(all_signals)
                result.consumers_notified = consumers_count
            else:
                result.warnings.append("No bus registry - signals not published")

            # 5. Registrar evento de irrigación completada
            if self.event_store:
                event = Event(
                    event_type=EventType.IRRIGATION_COMPLETED,
                    source_file=os.path.basename(file_path),
                    source_path=file_path,
                    payload=EventPayload(data={"signals_count": len(all_signals), "vehicles": result.vehicles_executed}),
                    phase=phase,
                    consumer_scope=consumer_scope
                )
                self.event_store.append(event)

            result.success = True

            # Actualizar estadísticas
            self.irrigation_stats["files_irrigated"] += 1
            self.irrigation_stats["signals_generated"] += len(all_signals)
            self.irrigation_stats["consumers_notified"] += result.consumers_notified

        except Exception as e:
            result.errors.append(f"Irrigation failed: {str(e)}")
            self.irrigation_stats["errors"] += 1

        return result

    def irrigate_batch(
        self,
        file_paths: List[str],
        phase: str,
        consumer_scope: str = "default"
    ) -> List[IrrigationResult]:
        """Ejecuta irrigación en lote para múltiples archivos"""
        results = []
        for file_path in file_paths:
            result = self.irrigate_file(file_path, phase, consumer_scope)
            results.append(result)
        return results

    def get_irrigation_summary(self) -> Dict[str, Any]:
        """Retorna resumen de estadísticas de irrigación"""
        return {
            **self.irrigation_stats,
            "success_rate": self._calculate_success_rate(),
            "avg_signals_per_file": self._calculate_avg_signals()
        }

    def _load_canonical_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Carga un archivo canónico JSON"""
        try:
            full_path = os.path.join("canonic_questionnaire_central", file_path)
            if not os.path.exists(full_path):
                # Intentar sin prefijo
                if os.path.exists(file_path):
                    full_path = file_path
                else:
                    return None

            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return None

    def _get_default_vehicles_for_file(self, file_path: str) -> List[str]:
        """Determina vehículos predeterminados según tipo de archivo"""
        # Basado en el tipo de archivo, asignar vehículos apropiados
        filename = os.path.basename(file_path)

        if "metadata" in filename:
            return ["signal_quality_metrics", "signal_enhancement_integrator"]
        elif filename.startswith("Q"):
            return [
                "signal_context_scoper",
                "signal_evidence_extractor",
                "signal_intelligence_layer",
            ]
        elif "dimension" in file_path or "policy_area" in file_path:
            return ["signal_registry", "signal_enhancement_integrator"]
        else:
            return ["signal_context_scoper", "signal_quality_metrics"]

    def _infer_node_type(self, file_path: str) -> str:
        """Infiere el tipo de nodo desde el path"""
        if "dimensions" in file_path:
            return "dimension"
        elif "policy_areas" in file_path:
            return "policy_area"
        elif "clusters" in file_path:
            return "cluster"
        elif "questions" in file_path:
            return "question"
        else:
            return "unknown"

    def _publish_signals_to_buses(self, signals: List[Signal]) -> int:
        """Publica señales a los buses correspondientes y retorna count de consumidores notificados"""
        consumers_notified = 0

        for signal in signals:
            # Determinar bus apropiado según tipo de señal
            bus_type = self._get_bus_for_signal(signal)

            if bus_type and self.bus_registry and bus_type in self.bus_registry:
                bus = self.bus_registry[bus_type]
                # Publicar al bus
                bus.publish(signal)
                # Contar consumidores que podrían recibir esto
                consumers_notified += len(getattr(bus, '_subscribers', []))

        return consumers_notified

    def _get_bus_for_signal(self, signal: Signal) -> Optional[BusType]:
        """Determina el bus apropiado para una señal según su categoría"""
        from ..signal_types.types.structural import StructuralAlignmentSignal, CanonicalMappingSignal
        from ..signal_types.types.integrity import DataIntegritySignal, EventCompletenessSignal
        from ..signal_types.types.epistemic import EmpiricalSupportSignal, MethodApplicationSignal

        signal_type = type(signal).__name__

        # Mapeo señal → bus
        signal_to_bus = {
            # Structural → STRUCTURAL_BUS
            "StructuralAlignmentSignal": BusType.STRUCTURAL,
            "CanonicalMappingSignal": BusType.STRUCTURAL,
            "SchemaConflictSignal": BusType.STRUCTURAL,
            # Integrity → INTEGRITY_BUS
            "DataIntegritySignal": BusType.INTEGRITY,
            "EventCompletenessSignal": BusType.INTEGRITY,
            # Epistemic → EPISTEMIC_BUS
            "EmpiricalSupportSignal": BusType.EPISTEMIC,
            "MethodApplicationSignal": BusType.EPISTEMIC,
            "AnswerDeterminacySignal": BusType.EPISTEMIC,
            "AnswerSpecificitySignal": BusType.EPISTEMIC,
            # Event presence → OPERATIONAL_BUS
            "EventPresenceSignal": BusType.OPERATIONAL,
        }

        return signal_to_bus.get(signal_type)

    def _calculate_success_rate(self) -> float:
        """Calcula tasa de éxito de irrigación"""
        total = self.irrigation_stats["files_irrigated"] + self.irrigation_stats["errors"]
        if total == 0:
            return 1.0
        return self.irrigation_stats["files_irrigated"] / total

    def _calculate_avg_signals(self) -> float:
        """Calcula promedio de señales por archivo"""
        files = self.irrigation_stats["files_irrigated"]
        if files == 0:
            return 0.0
        return self.irrigation_stats["signals_generated"] / files
