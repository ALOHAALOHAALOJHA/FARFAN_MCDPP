# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vocabulary/signal_vocabulary.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum


@dataclass
class SignalTypeDefinition:
    """Definición canónica de un tipo de señal"""
    signal_type: str
    category: str
    description: str
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    value_type: str = "any"  # "enum", "float", "string", "dict"
    value_constraints: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"


@dataclass
class SignalVocabulary:
    """
    Vocabulario canónico de señales.
    Define todos los tipos de señales válidos en el sistema.
    """

    definitions: Dict[str, SignalTypeDefinition] = field(default_factory=dict)

    def __post_init__(self):
        # Registrar tipos de señales del sistema
        self._register_structural_signals()
        self._register_integrity_signals()
        self._register_epistemic_signals()
        self._register_contrast_signals()
        self._register_operational_signals()
        self._register_consumption_signals()

    def _register_structural_signals(self):
        """Registra señales estructurales"""
        self.register(SignalTypeDefinition(
            signal_type="StructuralAlignmentSignal",
            category="structural",
            description="Indica si un dato mapea correctamente a la estructura canónica",
            required_fields=["alignment_status", "canonical_path"],
            optional_fields=["missing_elements", "extra_elements"],
            value_type="enum",
            value_constraints={"values": ["ALIGNED", "PARTIAL", "MISALIGNED", "UNKNOWN"]}
        ))

        self.register(SignalTypeDefinition(
            signal_type="SchemaConflictSignal",
            category="structural",
            description="Indica conflicto de esquemas entre datos",
            required_fields=["expected_schema_version", "actual_schema_version", "conflict_type"],
            optional_fields=["conflicting_fields", "is_breaking"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="CanonicalMappingSignal",
            category="structural",
            description="Resultado de mapear un ítem a entidades canónicas",
            required_fields=["source_item_id", "mapped_entities"],
            optional_fields=["unmapped_aspects", "mapping_completeness"]
        ))

    def _register_integrity_signals(self):
        """Registra señales de integridad"""
        self.register(SignalTypeDefinition(
            signal_type="EventPresenceSignal",
            category="integrity",
            description="Indica si un evento esperado existe",
            required_fields=["expected_event_type", "presence_status"],
            optional_fields=["event_count", "first_occurrence", "last_occurrence"],
            value_type="enum",
            value_constraints={"values": ["PRESENT", "ABSENT", "PARTIAL"]}
        ))

        self.register(SignalTypeDefinition(
            signal_type="EventCompletenessSignal",
            category="integrity",
            description="Indica qué tan completo es un evento",
            required_fields=["completeness_level", "required_fields", "present_fields"],
            optional_fields=["missing_fields", "completeness_score"],
            value_type="enum",
            value_constraints={"values": ["COMPLETE", "MOSTLY_COMPLETE", "INCOMPLETE", "EMPTY"]}
        ))

        self.register(SignalTypeDefinition(
            signal_type="DataIntegritySignal",
            category="integrity",
            description="Indica la integridad referencial de los datos",
            required_fields=["source_file", "referenced_files"],
            optional_fields=["valid_references", "broken_references", "integrity_score"]
        ))

    def _register_epistemic_signals(self):
        """Registra señales epistémicas"""
        self.register(SignalTypeDefinition(
            signal_type="AnswerDeterminacySignal",
            category="epistemic",
            description="Evalúa qué tan determinante es una respuesta",
            required_fields=["question_id", "determinacy_level"],
            optional_fields=["affirmative_markers", "ambiguity_markers", "negation_markers"],
            value_type="enum",
            value_constraints={"values": ["HIGH", "MEDIUM", "LOW", "INDETERMINATE"]}
        ))

        self.register(SignalTypeDefinition(
            signal_type="AnswerSpecificitySignal",
            category="epistemic",
            description="Evalúa qué tan específica es una respuesta",
            required_fields=["question_id", "specificity_level"],
            optional_fields=["expected_elements", "found_elements", "missing_elements"],
            value_type="enum",
            value_constraints={"values": ["HIGH", "MEDIUM", "LOW", "NONE"]}
        ))

        self.register(SignalTypeDefinition(
            signal_type="EmpiricalSupportSignal",
            category="epistemic",
            description="Evalúa el soporte empírico/documental de una respuesta",
            required_fields=["question_id", "support_level"],
            optional_fields=["normative_references", "document_references", "institutional_references"],
            value_type="enum",
            value_constraints={"values": ["STRONG", "MODERATE", "WEAK", "NONE"]}
        ))

        self.register(SignalTypeDefinition(
            signal_type="MethodApplicationSignal",
            category="epistemic",
            description="Resultado de aplicar un método de evaluación",
            required_fields=["question_id", "method_id", "method_result"],
            optional_fields=["extraction_successful", "extracted_values", "processing_time_ms"]
        ))

    def _register_contrast_signals(self):
        """Registra señales de contraste"""
        self.register(SignalTypeDefinition(
            signal_type="DecisionDivergenceSignal",
            category="contrast",
            description="Indica divergencia entre sistema legacy y nuevo",
            required_fields=["item_id", "legacy_value", "signal_based_value"],
            optional_fields=["divergence_type", "divergence_severity", "divergence_explanation"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="ConfidenceDropSignal",
            category="contrast",
            description="Indica caída de confianza en una evaluación",
            required_fields=["item_id", "previous_confidence", "current_confidence"],
            optional_fields=["drop_percentage", "contributing_factors", "trend"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="TemporalContrastSignal",
            category="contrast",
            description="Indica cambios entre evaluaciones en diferentes momentos",
            required_fields=["item_id", "baseline_timestamp", "current_timestamp"],
            optional_fields=["baseline_state", "current_state", "changes_detected"]
        ))

    def _register_operational_signals(self):
        """Registra señales operacionales"""
        self.register(SignalTypeDefinition(
            signal_type="ExecutionAttemptSignal",
            category="operational",
            description="Registra un intento de ejecución",
            required_fields=["execution_id", "component", "operation", "status"],
            optional_fields=["started_at", "completed_at", "duration_ms"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="FailureModeSignal",
            category="operational",
            description="Describe cómo falló una operación",
            required_fields=["execution_id", "failure_mode", "error_message"],
            optional_fields=["error_code", "stack_trace", "recoverable"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="LegacyActivitySignal",
            category="operational",
            description="Registra actividad del sistema legacy",
            required_fields=["legacy_component", "activity_type"],
            optional_fields=["input_captured", "output_captured", "raw_payload"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="LegacyDependencySignal",
            category="operational",
            description="Mapea dependencias del sistema legacy",
            required_fields=["legacy_component"],
            optional_fields=["upstream_dependencies", "downstream_dependents", "criticality"]
        ))

    def _register_consumption_signals(self):
        """Registra señales de consumo"""
        self.register(SignalTypeDefinition(
            signal_type="FrequencySignal",
            category="consumption",
            description="Indica frecuencia de uso/acceso",
            required_fields=["resource_id", "resource_type", "access_count"],
            optional_fields=["period_start", "period_end", "access_pattern"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="TemporalCouplingSignal",
            category="consumption",
            description="Indica acoplamiento temporal entre componentes",
            required_fields=["component_a", "component_b", "correlation_coefficient"],
            optional_fields=["coupling_strength", "co_occurrence_count"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="ConsumerHealthSignal",
            category="consumption",
            description="Indica salud de un consumidor",
            required_fields=["consumer_id", "health_status"],
            optional_fields=["signals_received", "signals_processed", "error_rate"]
        ))

    def register(self, definition: SignalTypeDefinition):
        """Registra una definición de tipo de señal"""
        self.definitions[definition.signal_type] = definition

    def get(self, signal_type: str) -> Optional[SignalTypeDefinition]:
        """Obtiene definición de un tipo de señal"""
        return self.definitions.get(signal_type)

    def is_valid_type(self, signal_type: str) -> bool:
        """Verifica si un tipo de señal es válido"""
        return signal_type in self.definitions

    def get_by_category(self, category: str) -> List[SignalTypeDefinition]:
        """Obtiene tipos de señal por categoría"""
        return [d for d in self.definitions.values() if d.category == category]

    def validate_signal(self, signal:  Any) -> tuple[bool, List[str]]:
        """
        Valida una señal contra el vocabulario.
        Retorna (es_válido, lista_de_errores)
        """
        errors = []

        signal_type = getattr(signal, 'signal_type', None)
        if not signal_type:
            errors.append("Signal has no signal_type")
            return (False, errors)

        definition = self.get(signal_type)
        if not definition:
            errors.append(f"Unknown signal type: {signal_type}")
            return (False, errors)

        # Verificar campos requeridos
        for field_name in definition.required_fields:
            if not hasattr(signal, field_name):
                errors.append(f"Missing required field: {field_name}")
            elif getattr(signal, field_name) is None:
                errors.append(f"Required field is None: {field_name}")

        # Verificar constraints de valor si aplica
        if definition.value_type == "enum" and "values" in definition.value_constraints:
            value = getattr(signal, 'value', None)
            if value is not None:
                allowed = definition.value_constraints["values"]
                # El valor podría ser un Enum, extraer su valor
                value_str = value.value if hasattr(value, 'value') else str(value)
                if value_str not in allowed:
                    errors.append(f"Invalid value '{value_str}'.  Allowed:  {allowed}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Exporta vocabulario a diccionario"""
        return {
            signal_type: {
                "category": d.category,
                "description":  d.description,
                "required_fields": d.required_fields,
                "optional_fields":  d.optional_fields,
                "value_type": d.value_type,
                "value_constraints": d.value_constraints,
                "version": d.version
            }
            for signal_type, d in self.definitions.items()
        }
