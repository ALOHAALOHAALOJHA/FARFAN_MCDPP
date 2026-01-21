# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_enhancement_integrator.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import os
import re

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..core.contracts import PublicationContract, ContractType, ContractStatus, SignalTypeSpec
from ..signal_types.types.structural import (
    StructuralAlignmentSignal,
    CanonicalMappingSignal,
    AlignmentStatus
)

@dataclass
class SignalEnhancementIntegratorVehicle(BaseVehicle):
    """
    Vehículo: signal_enhancement_integrator

    Responsabilidad: Integración de enriquecimiento estructural.

    Archivos que procesa:
    - Todos los archivos canónicos que requieren validación estructural
    - Verifica alineación con la estructura canónica esperada
    - Mapea entidades canónicas (policy_areas, dimensions, clusters)
    """
    vehicle_id: str = "signal_enhancement_integrator"
    vehicle_name: str = "Signal Enhancement Integrator Vehicle"

    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=True,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=["StructuralAlignmentSignal", "CanonicalMappingSignal"]
    ))

    def __post_init__(self):
        # Crear contrato de publicación
        self.publication_contract = PublicationContract(
            contract_id=f"pub_{self.vehicle_id}",
            publisher_vehicle=self.vehicle_id,
            status=ContractStatus.ACTIVE,
            allowed_signal_types=[
                SignalTypeSpec(signal_type="StructuralAlignmentSignal"),
                SignalTypeSpec(signal_type="CanonicalMappingSignal")
            ],
            allowed_buses=["structural_bus", "enhancement_bus"],
            require_context=True,
            require_source=True
        )
        if self.contract_registry:
            self.contract_registry.register(self.publication_contract)

    # Patrones de estructura canónica
    canonical_structure: Dict[str, List[str]] = field(default_factory=lambda: {
        "dimensions": ["id", "name", "description", "policy_areas"],
        "policy_areas": ["id", "name", "description", "dimensions"],
        "clusters": ["id", "name", "description", "policy_area_id"],
        "questions": ["id", "text", "type", "policy_area", "dimension"],
        "metadata": ["id", "name", "description", "version", "created_at"]
    })

    # Mapeo de patrones de archivos a entidades canónicas
    file_pattern_mapping: Dict[str, str] = field(default_factory=lambda: {
        r"dimensions/[^/]+/metadata\.json$": "dimension",
        r"policy_areas/[^/]+/metadata\.json$": "policy_area",
        r"clusters/[^/]+/metadata\.json$": "cluster",
        r"questions/[^/]+\.json$": "question",
        r"micro_questions/[^/]+\.json$": "micro_question",
        r"atomized_questions/[^/]+\.json$": "atomized_question",
    })

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa datos y genera señales de enriquecimiento estructural.
        """
        signals = []

        # Crear evento
        event = self.create_event(
            event_type="enhancement_integration",
            payload={"file": context.node_id},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )

        source = self.create_signal_source(event)

        # 1. Señal de alineación estructural
        alignment_signal = self._validate_structural_alignment(data, context, source)
        signals.append(alignment_signal)

        # 2. Señal de mapeo canónico
        mapping_signal = self._create_canonical_mapping(data, context, source)
        signals.append(mapping_signal)

        self.stats["signals_generated"] += len(signals)
        return signals

    def _validate_structural_alignment(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> StructuralAlignmentSignal:
        """Valida alineación estructural con la canónica"""

        node_id = context.node_id
        node_type = context.node_type

        # Determinar la estructura esperada según el tipo
        expected_structure = self._get_expected_structure(node_id, node_type)

        # Obtener estructura actual
        actual_structure = list(data.keys()) if isinstance(data, dict) else []

        # Detectar elementos faltantes y extra
        missing_elements = [e for e in expected_structure if e not in actual_structure]
        extra_elements = [e for e in actual_structure if e not in expected_structure and not e.startswith("_")]

        # Determinar path canónico esperado
        canonical_path = self._get_canonical_path(node_id, node_type)
        actual_path = f"{node_type}/{node_id}"

        # Determinar estado de alineación
        if not missing_elements and not extra_elements:
            alignment_status = AlignmentStatus.ALIGNED
        elif missing_elements and not extra_elements:
            alignment_status = AlignmentStatus.PARTIAL
        elif not missing_elements and extra_elements:
            alignment_status = AlignmentStatus.PARTIAL
        else:
            alignment_status = AlignmentStatus.MISALIGNED

        return StructuralAlignmentSignal(
            context=context,
            source=source,
            alignment_status=alignment_status,
            canonical_path=canonical_path,
            actual_path=actual_path,
            missing_elements=missing_elements,
            extra_elements=extra_elements,
            confidence=SignalConfidence.HIGH if alignment_status == AlignmentStatus.ALIGNED else SignalConfidence.MEDIUM,
            rationale=f"Alignment: {alignment_status.value} ({len(missing_elements)} missing, {len(extra_elements)} extra)"
        )

    def _create_canonical_mapping(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> CanonicalMappingSignal:
        """Crea mapeo a entidades canónicas"""

        source_item_id = context.node_id
        mapped_entities = {}
        unmapped_aspects = []

        # Mapear policy_area si existe
        if "policy_area" in data or "policy_area_id" in data:
            pa_id = data.get("policy_area") or data.get("policy_area_id")
            if pa_id:
                mapped_entities["policy_area"] = pa_id
            else:
                unmapped_aspects.append("policy_area")

        # Mapear dimension si existe
        if "dimension" in data or "dimension_id" in data:
            dim_id = data.get("dimension") or data.get("dimension_id")
            if dim_id:
                mapped_entities["dimension"] = dim_id
            else:
                unmapped_aspects.append("dimension")

        # Mapear cluster si existe
        if "cluster" in data or "cluster_id" in data:
            cl_id = data.get("cluster") or data.get("cluster_id")
            if cl_id:
                mapped_entities["cluster"] = cl_id
            else:
                unmapped_aspects.append("cluster")

        # Mapear entidad padre si existe
        if "parent" in data or "parent_id" in data:
            parent_id = data.get("parent") or data.get("parent_id")
            if parent_id:
                mapped_entities["parent"] = parent_id

        # Calcular completitud del mapeo
        expected_mappings = 0
        for key in ["policy_area", "dimension", "cluster"]:
            if key in data or f"{key}_id" in data:
                expected_mappings += 1

        mapping_completeness = len(mapped_entities) / expected_mappings if expected_mappings > 0 else 1.0

        return CanonicalMappingSignal(
            context=context,
            source=source,
            source_item_id=source_item_id,
            mapped_entities=mapped_entities,
            unmapped_aspects=unmapped_aspects,
            mapping_completeness=mapping_completeness,
            confidence=SignalConfidence.HIGH,
            rationale=f"Mapping: {len(mapped_entities)} entities, {len(unmapped_aspects)} unmapped, {mapping_completeness:.0%} complete"
        )

    def _get_expected_structure(self, node_id: str, node_type: str) -> List[str]:
        """Determina la estructura esperada para un nodo"""
        # Inferir tipo desde node_id
        for pattern, entity_type in self.file_pattern_mapping.items():
            if re.search(pattern, f"{node_type}/{node_id}"):
                return self.canonical_structure.get(entity_type, [])

        # Por defecto, buscar en estructuras conocidas
        if "dimension" in node_type.lower():
            return self.canonical_structure.get("dimensions", [])
        elif "policy_area" in node_type.lower() or "policy" in node_type.lower():
            return self.canonical_structure.get("policy_areas", [])
        elif "cluster" in node_type.lower():
            return self.canonical_structure.get("clusters", [])
        elif "question" in node_type.lower() or node_id.startswith("Q"):
            return self.canonical_structure.get("questions", [])

        return []

    def _get_canonical_path(self, node_id: str, node_type: str) -> str:
        """Construye el path canónico esperado"""
        # Intentar inferir la ubicación canónica
        if node_id.startswith("Q"):
            # Es una pregunta
            if node_id.startswith("QM"):
                return f"micro_questions/{node_id}.json"
            elif node_id.startswith("QA"):
                return f"atomized_questions/{node_id}.json"
            else:
                return f"questions/{node_id}.json"

        # Buscar en file_pattern_mapping
        for pattern, entity_type in self.file_pattern_mapping.items():
            if re.search(pattern, f"{node_type}/{node_id}"):
                # Ya está en formato canónico
                return f"{node_type}/{node_id}"

        # Por defecto, retornar path actual
        return f"{node_type}/{node_id}"
