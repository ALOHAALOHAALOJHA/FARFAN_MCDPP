# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vocabulary/signal_vocabulary.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from functools import lru_cache, wraps
import time
import hashlib
import json


@dataclass
class SignalTypeDefinition:
    """Definición canónica de un tipo de señal con metadatos enriquecidos"""
    signal_type: str
    category: str
    description: str
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    value_type: str = "any"  # "enum", "float", "string", "dict"
    value_constraints: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    # Enhancement: Metadata adicional
    examples: List[Dict[str, Any]] = field(default_factory=list)
    deprecation_info: Optional[Dict[str, str]] = None
    performance_hints: Dict[str, str] = field(default_factory=dict)
    related_signals: List[str] = field(default_factory=list)
    
    def compute_hash(self) -> str:
        """Computa hash determinístico de la definición"""
        content = {
            "signal_type": self.signal_type,
            "category": self.category,
            "required_fields": sorted(self.required_fields),
            "version": self.version
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]


@dataclass
class SignalVocabulary:
    """
    Vocabulario canónico de señales con enhancements avanzados.
    Define todos los tipos de señales válidos en el sistema.
    
    Enhancements:
    - Caching de validaciones para performance
    - Métricas de uso y validación
    - Índices para búsqueda rápida
    - Versionado y compatibilidad
    """

    definitions: Dict[str, SignalTypeDefinition] = field(default_factory=dict)
    
    # Enhancement: Índices para búsqueda rápida
    _category_index: Dict[str, Set[str]] = field(default_factory=dict)
    _field_index: Dict[str, Set[str]] = field(default_factory=dict)
    
    # Enhancement: Cache de validaciones
    _validation_cache: Dict[str, Tuple[bool, List[str]]] = field(default_factory=dict)
    _cache_hits: int = 0
    _cache_misses: int = 0
    
    # Enhancement: Métricas de uso
    _usage_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)
    _validation_times: Dict[str, List[float]] = field(default_factory=dict)

    def __post_init__(self):
        # Registrar tipos de señales del sistema
        self._register_structural_signals()
        self._register_integrity_signals()
        self._register_epistemic_signals()
        self._register_contrast_signals()
        self._register_orchestration_signals()
        self._register_operational_signals()
        self._register_consumption_signals()

        # Construir índices
        self._build_indices()

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

    def _register_orchestration_signals(self):
        """Registra señales de orquestación SISAS"""
        # Phase Lifecycle Signals
        self.register(SignalTypeDefinition(
            signal_type="PhaseStartSignal",
            category="orchestration",
            description="Signal emitted when a phase is ready to start",
            required_fields=["run_id", "phase_id"],
            optional_fields=["execution_context", "upstream_dependencies", "expected_signals", "timeout_seconds"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="PhaseCompleteSignal",
            category="orchestration",
            description="Signal emitted when a phase completes execution",
            required_fields=["run_id", "phase_id", "status"],
            optional_fields=["completion_metadata", "error_message", "execution_duration_seconds", "attempt_number"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="PhaseProgressSignal",
            category="orchestration",
            description="Signal emitted when a phase reports progress",
            required_fields=["run_id", "phase_id", "progress_percent"],
            optional_fields=["current_step", "estimated_remaining_seconds", "metadata"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="PhaseRetrySignal",
            category="orchestration",
            description="Signal emitted when a phase is being retried",
            required_fields=["run_id", "phase_id", "attempt_number"],
            optional_fields=["max_attempts", "previous_error"]
        ))

        # Orchestration Decision Signals
        self.register(SignalTypeDefinition(
            signal_type="OrchestrationInitializedSignal",
            category="orchestration",
            description="Signal emitted when orchestration is initialized",
            required_fields=["run_id"],
            optional_fields=["configuration", "dependency_graph_summary", "validation_passed"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="OrchestrationCompleteSignal",
            category="orchestration",
            description="Signal emitted when orchestration completes",
            required_fields=["run_id", "final_status"],
            optional_fields=["total_phases", "completed_successfully", "completed_partially", "failed", "execution_summary"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="OrchestrationDecisionSignal",
            category="orchestration",
            description="Signal emitted for every orchestration decision",
            required_fields=["run_id", "decision_type", "decision_rationale"],
            optional_fields=["phases_selected", "phases_waiting", "phases_blocked", "dependency_state"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="ConstitutionalValidationSignal",
            category="orchestration",
            description="Signal emitted when constitutional/contract validation occurs",
            required_fields=["run_id", "validation_passed"],
            optional_fields=["validation_errors", "contracts_validated", "timestamp"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="DependencyGraphLoadedSignal",
            category="orchestration",
            description="Signal emitted when dependency graph is loaded/initialized",
            required_fields=["run_id"],
            optional_fields=["total_nodes", "total_edges", "graph_structure"]
        ))

        # Coordination Signals
        self.register(SignalTypeDefinition(
            signal_type="PhaseReadyToStartSignal",
            category="orchestration",
            description="Signal emitted when a phase is ready to start",
            required_fields=["run_id", "phase_id", "dependencies_satisfied"],
            optional_fields=["unsatisfied_dependencies"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="DependencyGraphUpdatedSignal",
            category="orchestration",
            description="Signal emitted when the dependency graph is updated",
            required_fields=["run_id", "updated_node", "new_status"],
            optional_fields=["newly_unblocked_phases", "impact_summary"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="PhaseBlockedSignal",
            category="orchestration",
            description="Signal emitted when a phase is blocked",
            required_fields=["run_id", "phase_id"],
            optional_fields=["blocking_dependencies", "blocking_status"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="ParallelExecutionLimitSignal",
            category="orchestration",
            description="Signal emitted when parallel execution limit is reached",
            required_fields=["run_id", "current_parallel_count"],
            optional_fields=["max_parallel", "waiting_phases"]
        ))

        self.register(SignalTypeDefinition(
            signal_type="PhaseDependencySatisfiedSignal",
            category="orchestration",
            description="Signal emitted when a dependency is satisfied",
            required_fields=["run_id", "dependency_phase_id"],
            optional_fields=["downstream_phases_affected", "newly_ready_phases"]
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
        """Registra una definición de tipo de señal y actualiza índices"""
        self.definitions[definition.signal_type] = definition
        
        # Actualizar índices
        if definition.category not in self._category_index:
            self._category_index[definition.category] = set()
        self._category_index[definition.category].add(definition.signal_type)
        
        # Indexar por campos
        for field_name in definition.required_fields + definition.optional_fields:
            if field_name not in self._field_index:
                self._field_index[field_name] = set()
            self._field_index[field_name].add(definition.signal_type)
        
        # Inicializar stats
        if definition.signal_type not in self._usage_stats:
            self._usage_stats[definition.signal_type] = {
                "validations": 0,
                "successes": 0,
                "failures": 0
            }
    
    def _build_indices(self):
        """Construye índices de búsqueda"""
        self._category_index.clear()
        self._field_index.clear()
        
        for signal_type, definition in self.definitions.items():
            # Índice por categoría
            if definition.category not in self._category_index:
                self._category_index[definition.category] = set()
            self._category_index[definition.category].add(signal_type)
            
            # Índice por campos
            for field_name in definition.required_fields + definition.optional_fields:
                if field_name not in self._field_index:
                    self._field_index[field_name] = set()
                self._field_index[field_name].add(signal_type)
    
    def _compute_signal_hash(self, signal: Any) -> str:
        """Computa hash de señal para caching"""
        signal_type = getattr(signal, 'signal_type', '')
        signal_id = getattr(signal, 'signal_id', '')
        return f"{signal_type}:{signal_id}"

    def get(self, signal_type: str) -> Optional[SignalTypeDefinition]:
        """Obtiene definición de un tipo de señal"""
        return self.definitions.get(signal_type)

    def is_valid_type(self, signal_type: str) -> bool:
        """Verifica si un tipo de señal es válido"""
        return signal_type in self.definitions

    def get_by_category(self, category: str) -> List[SignalTypeDefinition]:
        """Obtiene tipos de señal por categoría"""
        return [d for d in self.definitions.values() if d.category == category]

    def validate_signal(self, signal: Any, use_cache: bool = True) -> tuple[bool, List[str]]:
        """
        Valida una señal contra el vocabulario con caching opcional.
        Retorna (es_válido, lista_de_errores)
        """
        start_time = time.time()
        
        signal_type = getattr(signal, 'signal_type', None)
        if not signal_type:
            return (False, ["Signal has no signal_type"])
        
        # Intentar usar cache
        if use_cache:
            cache_key = self._compute_signal_hash(signal)
            if cache_key in self._validation_cache:
                self._cache_hits += 1
                return self._validation_cache[cache_key]
            self._cache_misses += 1
        
        errors = []

        definition = self.get(signal_type)
        if not definition:
            errors.append(f"Unknown signal type: {signal_type}")
            result = (False, errors)
            if use_cache:
                self._validation_cache[self._compute_signal_hash(signal)] = result
            return result

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
                    errors.append(f"Invalid value '{value_str}'. Allowed: {allowed}")

        result = (len(errors) == 0, errors)
        
        # Actualizar estadísticas
        validation_time = (time.time() - start_time) * 1000  # ms
        if signal_type not in self._usage_stats:
            self._usage_stats[signal_type] = {
                "validations": 0,
                "successes": 0,
                "failures": 0
            }
        
        self._usage_stats[signal_type]["validations"] += 1
        if result[0]:
            self._usage_stats[signal_type]["successes"] += 1
        else:
            self._usage_stats[signal_type]["failures"] += 1
        
        if signal_type not in self._validation_times:
            self._validation_times[signal_type] = []
        self._validation_times[signal_type].append(validation_time)
        
        # Guardar en cache
        if use_cache:
            self._validation_cache[self._compute_signal_hash(signal)] = result
        
        return result

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
    
    def search_by_field(self, field_name: str) -> List[str]:
        """Búsqueda rápida de tipos de señal que usan un campo"""
        return list(self._field_index.get(field_name, set()))
    
    def search_by_description(self, keyword: str) -> List[SignalTypeDefinition]:
        """Búsqueda de tipos de señal por palabra clave en descripción"""
        keyword_lower = keyword.lower()
        return [
            d for d in self.definitions.values()
            if keyword_lower in d.description.lower()
        ]
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso del vocabulario"""
        total_validations = sum(s["validations"] for s in self._usage_stats.values())
        total_successes = sum(s["successes"] for s in self._usage_stats.values())
        total_failures = sum(s["failures"] for s in self._usage_stats.values())
        
        # Calcular tiempos promedio de validación
        avg_times = {}
        for signal_type, times in self._validation_times.items():
            if times:
                avg_times[signal_type] = sum(times) / len(times)
        
        # Top señales más usadas
        top_used = sorted(
            self._usage_stats.items(),
            key=lambda x: x[1]["validations"],
            reverse=True
        )[:10]
        
        return {
            "total_definitions": len(self.definitions),
            "total_validations": total_validations,
            "success_rate": (total_successes / total_validations * 100) if total_validations > 0 else 0,
            "cache_hit_rate": (self._cache_hits / (self._cache_hits + self._cache_misses) * 100) 
                             if (self._cache_hits + self._cache_misses) > 0 else 0,
            "top_used_signals": [{"signal_type": st, "count": stats["validations"]} 
                                for st, stats in top_used],
            "average_validation_times_ms": avg_times,
            "by_category": {
                cat: len(signals) for cat, signals in self._category_index.items()
            }
        }
    
    def clear_cache(self):
        """Limpia el cache de validaciones"""
        self._validation_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_related_signals(self, signal_type: str) -> List[str]:
        """Obtiene señales relacionadas a un tipo dado"""
        definition = self.get(signal_type)
        if definition and definition.related_signals:
            return definition.related_signals
        
        # Si no hay relaciones explícitas, buscar por categoría
        if definition:
            return [
                st for st in self._category_index.get(definition.category, set())
                if st != signal_type
            ]
        return []
    
    def validate_compatibility(self, old_version: str, new_version: str) -> List[str]:
        """Valida compatibilidad entre versiones del vocabulario"""
        warnings = []
        # Implementación simplificada - en producción compararía definiciones reales
        if old_version != new_version:
            warnings.append(f"Version mismatch: {old_version} vs {new_version}")
        return warnings
