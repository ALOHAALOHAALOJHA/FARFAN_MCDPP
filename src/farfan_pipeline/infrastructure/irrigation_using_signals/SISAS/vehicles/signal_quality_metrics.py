# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_quality_metrics.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import os

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..core.contracts import PublicationContract, ContractType, ContractStatus, SignalTypeSpec
from ..signals.types.integrity import (
    DataIntegritySignal,
    EventCompletenessSignal,
    CompletenessLevel
)

@dataclass
class SignalQualityMetricsVehicle(BaseVehicle):
    """
    Vehículo: signal_quality_metrics

    Responsabilidad: Validar calidad e integridad de datos canónicos.

    Archivos que procesa:
    - Todos los archivos JSON canónicos que requieren validación de integridad
    - Verifica referencias, schemas y completitud de datos
    """
    vehicle_id: str = "signal_quality_metrics"
    vehicle_name: str = "Signal Quality Metrics Vehicle"

    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=True,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=False,
        can_validate=True,
        can_irrigate=False,
        signal_types_produced=["DataIntegritySignal", "EventCompletenessSignal"]
    ))

    def __post_init__(self):
        # Crear contrato de publicación
        self.publication_contract = PublicationContract(
            contract_id=f"pub_{self.vehicle_id}",
            publisher_vehicle=self.vehicle_id,
            status=ContractStatus.ACTIVE,
            allowed_signal_types=[
                SignalTypeSpec(signal_type="DataIntegritySignal"),
                SignalTypeSpec(signal_type="EventCompletenessSignal")
            ],
            allowed_buses=["integrity_bus", "quality_bus"],
            require_context=True,
            require_source=True
        )
        if self.contract_registry:
            self.contract_registry.register(self.publication_contract)

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa datos y genera señales de calidad e integridad.
        """
        signals = []

        # Crear evento
        event = self.create_event(
            event_type="quality_validation",
            payload={"file": context.node_id},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )

        source = self.create_signal_source(event)

        # 1. Señal de integridad de datos
        integrity_signal = self._validate_data_integrity(data, context, source)
        signals.append(integrity_signal)

        # 2. Señal de completitud de evento
        completeness_signal = self._validate_event_completeness(data, context, source)
        signals.append(completeness_signal)

        self.stats["signals_generated"] += len(signals)
        return signals

    def _validate_data_integrity(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> DataIntegritySignal:
        """Valida integridad referencial de los datos"""

        source_file = context.node_id
        referenced_files = []
        valid_references = []
        broken_references = []

        # Buscar referencias en los datos
        if isinstance(data, dict):
            # Referencias a otras dimensiones
            if "dimension_id" in data:
                dim_id = data["dimension_id"]
                referenced_files.append(f"dimensions/{dim_id}/metadata.json")

            # Referencias a policy areas
            if "policy_areas" in data:
                for pa in data["policy_areas"]:
                    referenced_files.append(f"policy_areas/{pa}/metadata.json")

            # Referencias a clusters
            if "cluster_id" in data:
                cluster_id = data["cluster_id"]
                referenced_files.append(f"clusters/{cluster_id}/metadata.json")

            # Referencias normativas
            if "normative_references" in data:
                for ref in data["normative_references"]:
                    referenced_files.append(ref.get("file_path", ""))

            # Validar referencias
            base_path = "canonic_questionnaire_central"
            for ref in referenced_files:
                if ref:
                    full_path = os.path.join(base_path, ref)
                    if os.path.exists(full_path):
                        valid_references.append(ref)
                    else:
                        broken_references.append(ref)

        # Calcular score de integridad
        total_refs = len(referenced_files) if referenced_files else 1
        integrity_score = len(valid_references) / total_refs if total_refs > 0 else 1.0

        return DataIntegritySignal(
            context=context,
            source=source,
            source_file=source_file,
            referenced_files=referenced_files,
            valid_references=valid_references,
            broken_references=broken_references,
            integrity_score=integrity_score,
            confidence=SignalConfidence.HIGH if integrity_score > 0.8 else SignalConfidence.MEDIUM,
            rationale=f"Validated {len(referenced_files)} references, {len(broken_references)} broken"
        )

    def _validate_event_completeness(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EventCompletenessSignal:
        """Valida completitud de los datos del evento"""

        # Campos esperados según tipo de archivo
        file_type = context.node_id.split("/")[-1] if "/" in context.node_id else context.node_id

        expected_fields_map = {
            "metadata.json": ["id", "name", "description", "version"],
            "questions.json": ["questions"],
            "keywords.json": ["keywords"],
            "aggregation_rules.json": ["rules", "weights"],
            "pdet_context.json": ["context", "municipalities"],
            "scoring_system.json": ["dimensions", "weights", "thresholds"],
            "governance.json": ["policies", "actors", "mechanisms"]
        }

        expected_fields = expected_fields_map.get(file_type, [])

        # Campos presentes
        if isinstance(data, dict):
            present_fields = list(data.keys())
        else:
            present_fields = []

        # Campos faltantes
        missing_fields = [f for f in expected_fields if f not in present_fields]

        # Determinar nivel de completitud
        total_expected = len(expected_fields) if expected_fields else 0
        if total_expected == 0:
            completeness_level = CompletenessLevel.COMPLETE
        elif len(missing_fields) == 0:
            completeness_level = CompletenessLevel.COMPLETE
        elif len(missing_fields) < total_expected / 2:
            completeness_level = CompletenessLevel.MOSTLY_COMPLETE
        elif len(missing_fields) < total_expected:
            completeness_level = CompletenessLevel.INCOMPLETE
        else:
            completeness_level = CompletenessLevel.EMPTY

        # Calcular score
        completeness_score = len(present_fields) / total_expected if total_expected > 0 else 1.0

        return EventCompletenessSignal(
            context=context,
            source=source,
            completeness_level=completeness_level,
            required_fields=expected_fields,
            present_fields=present_fields,
            missing_fields=missing_fields,
            completeness_score=completeness_score,
            confidence=SignalConfidence.HIGH,
            rationale=f"Completeness: {completeness_level.value}, {len(missing_fields)} missing"
        )