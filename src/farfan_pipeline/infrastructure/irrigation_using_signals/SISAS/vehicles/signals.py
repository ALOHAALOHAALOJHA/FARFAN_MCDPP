# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signals.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event


@dataclass
class SignalsAggregatorVehicle(BaseVehicle):
    """
    Vehículo: signals (agregador)
    
    Responsabilidad: Agregar y coordinar múltiples vehículos, actuando como
    punto de entrada unificado para procesamiento de datos canónicos.
    
    Este vehículo puede invocar otros vehículos según el tipo de datos.
    """
    
    vehicle_id: str = field(default="signals")
    vehicle_name: str = field(default="Signals Aggregator Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=True,
        can_scope=True,
        can_extract=True,
        can_transform=True,
        can_enrich=True,
        can_validate=True,
        can_irrigate=False,
        signal_types_produced=[
            "StructuralAlignmentSignal",
            "EventPresenceSignal",
            "DataIntegritySignal"
        ],
        signal_types_consumed=[]  # Puede consumir cualquier señal
    ))
    
    # Registro de vehículos delegados
    registered_vehicles: Dict[str, BaseVehicle] = field(default_factory=dict)
    delegation_stats: Dict[str, int] = field(default_factory=dict)

    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa datos agregando señales de múltiples fuentes.
        """
        signals = []
        
        # Crear evento de agregación
        event = self.create_event(
            event_type="signal_generated",
            payload={"aggregation": True, "context_type": context.node_type},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # Determinar qué vehículos deben procesar estos datos
        applicable_vehicles = self._determine_applicable_vehicles(data, context)
        
        # Delegar a vehículos apropiados
        for vehicle_id in applicable_vehicles:
            if vehicle_id in self.registered_vehicles:
                vehicle = self.registered_vehicles[vehicle_id]
                try:
                    delegated_signals = vehicle.process(data, context)
                    signals.extend(delegated_signals)
                    
                    # Actualizar estadísticas
                    self.delegation_stats[vehicle_id] = self.delegation_stats.get(vehicle_id, 0) + 1
                except Exception as e:
                    self.stats["errors"] += 1
                    # Continuar con otros vehículos
        
        # Si no hay vehículos registrados, generar señales básicas
        if not signals:
            # Importar señales necesarias
            from ..signals.types.structural import StructuralAlignmentSignal, AlignmentStatus
            from ..signals.types.integrity import EventPresenceSignal, PresenceStatus
            
            # Señal básica de alineación
            basic_alignment = StructuralAlignmentSignal(
                context=context,
                source=source,
                alignment_status=AlignmentStatus.ALIGNED,
                canonical_path=f"{context.node_type}/{context.node_id}",
                actual_path=source.source_path,
                missing_elements=[],
                extra_elements=[],
                confidence=SignalConfidence.MEDIUM,
                rationale="Basic aggregation signal - no vehicles registered"
            )
            signals.append(basic_alignment)
            
            # Señal básica de presencia
            has_data = bool(data)
            basic_presence = EventPresenceSignal(
                context=context,
                source=source,
                expected_event_type="canonical_data_loaded",
                presence_status=PresenceStatus.PRESENT if has_data else PresenceStatus.ABSENT,
                event_count=1 if has_data else 0,
                confidence=SignalConfidence.HIGH,
                rationale=f"Data presence: {has_data}"
            )
            signals.append(basic_presence)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _determine_applicable_vehicles(
        self,
        data: Dict[str, Any],
        context: SignalContext
    ) -> List[str]:
        """Determina qué vehículos deben procesar estos datos"""
        applicable = []
        
        node_id_lower = context.node_id.lower()
        node_type_lower = context.node_type.lower()
        
        # signal_registry: clusters, dimensions, policy_areas, cross_cutting, scoring, governance
        if any(term in node_id_lower or term in node_type_lower for term in [
            "cluster", "dimension", "policy_area", "cross_cutting", "scoring", "governance"
        ]):
            applicable.append("signal_registry")
        
        # signal_context_scoper: questions, patterns
        if any(term in node_id_lower for term in ["question", "pattern"]):
            applicable.append("signal_context_scoper")
        
        # signal_evidence_extractor: patterns
        if "pattern" in node_id_lower:
            applicable.append("signal_evidence_extractor")
        
        # signal_intelligence_layer: membership_criteria, entities, calibration
        if any(term in node_id_lower for term in ["membership", "entities", "calibration"]):
            applicable.append("signal_intelligence_layer")
        
        # signal_quality_metrics: keywords, questions in policy_areas
        if "policy_area" in node_type_lower and ("keyword" in node_id_lower or "question" in node_id_lower):
            applicable.append("signal_quality_metrics")
        
        # signal_enhancement_integrator: cross_cutting, scoring, semantic, validations
        if any(term in node_id_lower for term in ["cross_cutting", "scoring", "semantic", "validation"]):
            applicable.append("signal_enhancement_integrator")
        
        # signal_loader: config files y referencias
        if "config" in node_id_lower or context.node_type == "config":
            applicable.append("signal_loader")
        
        return applicable
    
    def register_vehicle(self, vehicle: BaseVehicle):
        """Registra un vehículo para delegación"""
        self.registered_vehicles[vehicle.vehicle_id] = vehicle
    
    def unregister_vehicle(self, vehicle_id: str):
        """Desregistra un vehículo"""
        if vehicle_id in self.registered_vehicles:
            del self.registered_vehicles[vehicle_id]
    
    def get_aggregation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de agregación"""
        return {
            "registered_vehicles": len(self.registered_vehicles),
            "vehicle_ids": list(self.registered_vehicles.keys()),
            "delegation_stats": self.delegation_stats,
            "total_delegations": sum(self.delegation_stats.values())
        }
