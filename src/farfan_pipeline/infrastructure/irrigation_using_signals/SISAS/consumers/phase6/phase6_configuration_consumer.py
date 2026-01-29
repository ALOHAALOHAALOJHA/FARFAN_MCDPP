# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase6/phase6_configuration_consumer.py

from dataclasses import dataclass
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase6ConfigurationConsumer(BaseConsumer):
    """
    Consumidor para configuration validation en Phase 6.

    Responsabilidad: Procesa señales para validación de configuración,
    integrando outputs de Phase 5 (uncertainty) para asegurar que
    la configuración del sistema es correcta y coherente.

    Señales que consume:
    - StructuralAlignmentSignal: Para validación de estructura
    - DataIntegritySignal: Para validación de integridad
    - SchemaConflictSignal: Para detección de conflictos de esquema

    Señales que produce (indirectamente via vehicles):
    - ConfigurationValidatedSignal: Validación de configuración
    - SchemaValidatedSignal: Validación de esquemas
    """

    consumer_id: str = "phase6_configuration_consumer"
    consumer_phase: str = "phase_06"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE6_CONFIGURATION",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "StructuralAlignmentSignal",
                "CanonicalMappingSignal",
                "DataIntegritySignal",
                "SchemaConflictSignal"
            ],
            subscribed_buses=["structural_bus", "integrity_bus"],
            context_filters={
                "phase": ["phase_05", "phase_06"],
                "consumer_scope": ["Phase_06", "Cross-Phase"]
            },
            required_capabilities=["can_validate", "can_scope"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales para validación de configuración.

        Enfoque: Validar que la configuración del sistema es correcta
        y que no hay conflictos estructurales o de esquema.
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "validation_results": {},
            "configuration_status": "UNKNOWN",
            "phase": "phase_06"
        }

        if signal.signal_type == "StructuralAlignmentSignal":
            result["validation_results"] = self._validate_structure(signal)

        elif signal.signal_type == "CanonicalMappingSignal":
            result["validation_results"] = self._validate_mapping(signal)

        elif signal.signal_type == "DataIntegritySignal":
            result["validation_results"] = self._validate_integrity(signal)

        elif signal.signal_type == "SchemaConflictSignal":
            result["validation_results"] = self._validate_schema(signal)

        # Determine overall configuration status
        result["configuration_status"] = self._determine_status(result["validation_results"])

        return result

    def _validate_structure(self, signal: Signal) -> Dict[str, Any]:
        """Valida estructura de datos"""
        alignment_status = str(getattr(signal, 'alignment_status', 'UNKNOWN'))
        missing_elements = getattr(signal, 'missing_elements', [])
        extra_elements = getattr(signal, 'extra_elements', [])

        is_valid = alignment_status == "AlignmentStatus.ALIGNED"
        has_issues = len(missing_elements) > 0 or len(extra_elements) > 0

        return {
            "structure_valid": is_valid,
            "alignment_status": alignment_status,
            "has_issues": has_issues,
            "missing_count": len(missing_elements),
            "extra_count": len(extra_elements),
            "issues": missing_elements + extra_elements
        }

    def _validate_mapping(self, signal: Signal) -> Dict[str, Any]:
        """Valida mapeo canónico"""
        mapping_completeness = getattr(signal, 'mapping_completeness', 0.0)
        mapped_entities = getattr(signal, 'mapped_entities', {})
        unmapped_aspects = getattr(signal, 'unmapped_aspects', [])

        is_valid = mapping_completeness >= 0.8
        has_issues = len(unmapped_aspects) > 0

        return {
            "mapping_valid": is_valid,
            "completeness": mapping_completeness,
            "has_issues": has_issues,
            "mapped_count": len(mapped_entities),
            "unmapped_count": len(unmapped_aspects),
            "unmapped_aspects": unmapped_aspects
        }

    def _validate_integrity(self, signal: Signal) -> Dict[str, Any]:
        """Valida integridad de datos"""
        integrity_score = getattr(signal, 'integrity_score', 1.0)
        broken_references = getattr(signal, 'broken_references', [])

        is_valid = integrity_score >= 0.8
        has_issues = len(broken_references) > 0

        return {
            "integrity_valid": is_valid,
            "integrity_score": integrity_score,
            "has_issues": has_issues,
            "broken_count": len(broken_references),
            "broken_references": broken_references
        }

    def _validate_schema(self, signal: Signal) -> Dict[str, Any]:
        """Valida conflictos de esquema"""
        conflict_type = getattr(signal, 'conflict_type', 'NONE')
        is_breaking = getattr(signal, 'is_breaking', False)
        conflicting_fields = getattr(signal, 'conflicting_fields', [])

        is_valid = conflict_type == 'NONE' or not is_breaking
        has_issues = len(conflicting_fields) > 0

        return {
            "schema_valid": is_valid,
            "conflict_type": conflict_type,
            "is_breaking": is_breaking,
            "has_issues": has_issues,
            "conflicting_count": len(conflicting_fields),
            "conflicting_fields": conflicting_fields
        }

    def _determine_status(self, validation_results: Dict[str, Any]) -> str:
        """Determina estado general de configuración"""
        if not validation_results:
            return "UNKNOWN"

        # Revisar si hay alguna validación fallida
        has_valid = validation_results.get("structure_valid", True) or \
                   validation_results.get("mapping_valid", True) or \
                   validation_results.get("integrity_valid", True) or \
                   validation_results.get("schema_valid", True)

        # Revisar si hay issues críticos
        has_critical_issues = validation_results.get("is_breaking", False) or \
                             validation_results.get("broken_count", 0) > 5

        if has_valid and not has_critical_issues:
            return "VALID"
        elif has_valid and has_critical_issues:
            return "WARNING"
        else:
            return "INVALID"
