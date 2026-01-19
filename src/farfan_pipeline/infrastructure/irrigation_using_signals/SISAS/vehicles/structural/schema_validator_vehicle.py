# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/structural/schema_validator_vehicle.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import json

from ..base_vehicle import BaseVehicle, VehicleCapabilities
from ...core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ...core.event import Event
from ...core.contracts import PublicationContract, ContractType, ContractStatus, SignalTypeSpec
from ....signals.types.structural import SchemaConflictSignal


@dataclass
class SchemaValidatorVehicle(BaseVehicle):
    """
    Vehículo: schema_validator_vehicle

    Responsabilidad: Validar esquemas y detectar conflictos de versión.

    Archivos que procesa:
    - Archivos JSON que requieren validación de esquema
    - Metadatos de archivos con versiones de esquema
    - Configuraciones que especifican esquemas esperados

    Señales que produce:
    - SchemaConflictSignal: Conflictos de esquema detectados
    """
    vehicle_id: str = "schema_validator_vehicle"
    vehicle_name: str = "Schema Validator Vehicle"

    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=False,
        can_validate=True,
        can_irrigate=False,
        signal_types_produced=["SchemaConflictSignal"]
    ))

    # Esquemas esperados por tipo de archivo
    expected_schemas: Dict[str, str] = field(default_factory=lambda: {
        "metadata.json": "1.0.0",
        "questions.json": "2.1.0",
        "keywords.json": "1.0.0",
        "scoring_system.json": "1.0.0",
        "governance.json": "1.0.0"
    })

    # Campos obligatorios por tipo de archivo
    required_fields: Dict[str, Set[str]] = field(default_factory=lambda: {
        "metadata.json": {"id", "name", "description", "version"},
        "questions.json": {"questions"},
        "keywords.json": {"keywords"},
        "scoring_system.json": {"dimensions", "weights"},
        "governance.json": {"policies"}
    })

    def __post_init__(self):
        # Crear contrato de publicación
        self.publication_contract = PublicationContract(
            contract_id=f"pub_{self.vehicle_id}",
            publisher_vehicle=self.vehicle_id,
            status=ContractStatus.ACTIVE,
            allowed_signal_types=[
                SignalTypeSpec(signal_type="SchemaConflictSignal")
            ],
            allowed_buses=["structural_bus", "integrity_bus"],
            require_context=True,
            require_source=True
        )
        if self.contract_registry:
            self.contract_registry.register(self.publication_contract)

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa datos y valida esquemas.

        Analiza:
        - Versiones de esquema
        - Campos obligatorios
        - Tipos de datos
        - Conflictos con esquemas esperados
        """
        signals = []

        # Crear evento
        event = self.create_event(
            event_type="schema_validation",
            payload={"file": context.node_id},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )

        source = self.create_signal_source(event)

        # Determinar tipo de archivo
        file_type = self._get_file_type(context.node_id)

        # Validar esquema
        conflict_signal = self._validate_schema(data, file_type, context, source)
        signals.append(conflict_signal)

        self.stats["signals_generated"] += len(signals)
        return signals

    def _get_file_type(self, node_id: str) -> str:
        """Determina el tipo de archivo desde el node_id"""
        if "metadata" in node_id.lower():
            return "metadata.json"
        elif "questions" in node_id.lower():
            return "questions.json"
        elif "keywords" in node_id.lower():
            return "keywords.json"
        elif "scoring" in node_id.lower():
            return "scoring_system.json"
        elif "governance" in node_id.lower():
            return "governance.json"
        else:
            # Default: intentar extraer del nombre del archivo
            parts = node_id.split("/")
            if parts:
                filename = parts[-1]
                if filename.endswith(".json"):
                    return filename
            return "unknown.json"

    def _validate_schema(
        self,
        data: Any,
        file_type: str,
        context: SignalContext,
        source: SignalSource
    ) -> SchemaConflictSignal:
        """Valida esquema y detecta conflictos"""

        # Versión esperada
        expected_version = self.expected_schemas.get(file_type, "1.0.0")

        # Versión actual
        if isinstance(data, dict):
            actual_version = data.get("schema_version", data.get("version", "1.0.0"))
        else:
            actual_version = "1.0.0"

        # Detectar conflicto de versión
        version_conflict = self._detect_version_conflict(expected_version, actual_version)

        # Detectar campos faltantes
        missing_fields = self._detect_missing_fields(data, file_type)

        # Detectar tipos incorrectos
        type_conflicts = self._detect_type_conflicts(data, file_type)

        # Detectar campos extra (no conflictivos pero informativos)
        extra_fields = self._detect_extra_fields(data, file_type)

        # Determinar tipo de conflicto
        conflicting_fields = list(set(missing_fields + type_conflicts))
        is_breaking = len(missing_fields) > 0 or any(t.get("is_breaking", False) for t in type_conflicts)

        if conflicting_fields or is_breaking:
            conflict_type = "BREAKING" if is_breaking else "NON_BREAKING"
        elif version_conflict:
            conflict_type = "VERSION_MISMATCH"
        else:
            conflict_type = "NONE"

        return SchemaConflictSignal(
            context=context,
            source=source,
            expected_schema_version=expected_version,
            actual_schema_version=actual_version,
            conflict_type=conflict_type,
            conflicting_fields=conflicting_fields,
            is_breaking=is_breaking,
            missing_fields=missing_fields,
            type_conflicts=type_conflicts,
            extra_fields=extra_fields,
            confidence=SignalConfidence.HIGH if conflict_type != "NONE" else SignalConfidence.LOW,
            rationale=f"Schema validation: {conflict_type} ({len(conflicting_fields)} conflicts, {len(missing_fields)} missing)"
        )

    def _detect_version_conflict(self, expected: str, actual: str) -> bool:
        """Detecta conflicto de versión"""
        try:
            expected_parts = expected.split(".")
            actual_parts = actual.split(".")

            # Comparar major version
            if expected_parts[0] != actual_parts[0]:
                return True  # Breaking change
            elif len(expected_parts) > 1 and len(actual_parts) > 1:
                if expected_parts[1] != actual_parts[1]:
                    return True  # Minor version mismatch
        except Exception:
            return False

        return False

    def _detect_missing_fields(self, data: Any, file_type: str) -> List[str]:
        """Detecta campos obligatorios faltantes"""
        if file_type not in self.required_fields:
            return []

        if not isinstance(data, dict):
            return list(self.required_fields[file_type])

        required = self.required_fields[file_type]
        missing = [field for field in required if field not in data]

        return missing

    def _detect_type_conflicts(self, data: Any, file_type: str) -> List[Dict[str, Any]]:
        """Detecta conflictos de tipos de datos"""
        conflicts = []

        if not isinstance(data, dict):
            return conflicts

        # Definiciones de tipos esperados
        type_expectations = {
            "metadata.json": {
                "id": str,
                "name": str,
                "description": str,
                "version": str
            },
            "questions.json": {
                "questions": list
            }
        }

        if file_type in type_expectations:
            expectations = type_expectations[file_type]

            for field, expected_type in expectations.items():
                if field in data:
                    actual_value = data[field]
                    if not isinstance(actual_value, expected_type):
                        conflicts.append({
                            "field": field,
                            "expected_type": expected_type.__name__,
                            "actual_type": type(actual_value).__name__,
                            "is_breaking": True
                        })

        return conflicts

    def _detect_extra_fields(self, data: Any, file_type: str) -> List[str]:
        """Detecta campos extra no especificados"""
        if file_type not in self.required_fields:
            return []

        if not isinstance(data, dict):
            return []

        required = self.required_fields[file_type]
        extra = [field for field in data.keys() if field not in required and not field.startswith("_")]

        return extra
