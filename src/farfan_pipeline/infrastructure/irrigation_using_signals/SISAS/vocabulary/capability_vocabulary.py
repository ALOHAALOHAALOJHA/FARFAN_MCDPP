# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vocabulary/capability_vocabulary.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CapabilityDefinition:
    """Definición de una capacidad"""
    capability_id: str
    name: str
    description: str
    category: str  # "loading", "scoping", "extraction", "transformation", "enrichment", "validation", "irrigation"
    required_signals: List[str] = field(default_factory=list)
    produced_signals: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    version: str = "1.0.0"


@dataclass
class CapabilityVocabulary:
    """
    Vocabulario canónico de capacidades.
    Define todas las capacidades válidas del sistema.
    """

    definitions: Dict[str, CapabilityDefinition] = field(default_factory=dict)

    def __post_init__(self):
        self._register_core_capabilities()

    def _register_core_capabilities(self):
        """Registra capacidades core del sistema"""

        # Capacidades de carga
        self.register(CapabilityDefinition(
            capability_id="can_load_canonical",
            name="Load Canonical Data",
            description="Capacidad de cargar archivos canónicos JSON",
            category="loading",
            produced_signals=["EventPresenceSignal", "StructuralAlignmentSignal"]
        ))

        # Capacidades de scoping
        self.register(CapabilityDefinition(
            capability_id="can_scope_context",
            name="Apply Context Scope",
            description="Capacidad de aplicar contexto y scope a datos",
            category="scoping",
            required_signals=["StructuralAlignmentSignal"],
            produced_signals=["CanonicalMappingSignal"]
        ))

        # Capacidades de extracción
        self.register(CapabilityDefinition(
            capability_id="can_extract_evidence",
            name="Extract Evidence",
            description="Capacidad de extraer evidencia empírica de respuestas",
            category="extraction",
            required_signals=["CanonicalMappingSignal"],
            produced_signals=["EmpiricalSupportSignal", "MethodApplicationSignal"]
        ))

        self.register(CapabilityDefinition(
            capability_id="can_extract_determinacy",
            name="Extract Determinacy",
            description="Capacidad de evaluar determinismo de respuestas",
            category="extraction",
            produced_signals=["AnswerDeterminacySignal"]
        ))

        self.register(CapabilityDefinition(
            capability_id="can_extract_specificity",
            name="Extract Specificity",
            description="Capacidad de evaluar especificidad de respuestas",
            category="extraction",
            produced_signals=["AnswerSpecificitySignal"]
        ))

        # Capacidades de transformación
        self.register(CapabilityDefinition(
            capability_id="can_transform_to_signals",
            name="Transform to Signals",
            description="Capacidad de transformar eventos en señales tipadas",
            category="transformation",
            required_signals=["EventPresenceSignal"],
            produced_signals=["*"]  # Puede producir cualquier señal
        ))

        # Capacidades de enriquecimiento
        self.register(CapabilityDefinition(
            capability_id="can_enrich_with_context",
            name="Enrich with Context",
            description="Capacidad de enriquecer datos con contexto PDET, territorial, etc.",
            category="enrichment",
            dependencies=["can_scope_context"]
        ))

        self.register(CapabilityDefinition(
            capability_id="can_enrich_with_signals",
            name="Enrich with Signals",
            description="Capacidad de enriquecer datos con señales previas",
            category="enrichment",
            required_signals=["*"]  # Requiere señales existentes
        ))

        # Capacidades de validación
        self.register(CapabilityDefinition(
            capability_id="can_validate_contracts",
            name="Validate Contracts",
            description="Capacidad de validar contratos de irrigación",
            category="validation",
            produced_signals=["DataIntegritySignal"]
        ))

        self.register(CapabilityDefinition(
            capability_id="can_validate_schema",
            name="Validate Schema",
            description="Capacidad de validar esquemas de datos",
            category="validation",
            produced_signals=["SchemaConflictSignal"]
        ))

        # Capacidades de irrigación
        self.register(CapabilityDefinition(
            capability_id="can_irrigate",
            name="Execute Irrigation",
            description="Capacidad de ejecutar irrigación completa",
            category="irrigation",
            dependencies=["can_load_canonical", "can_transform_to_signals"],
            produced_signals=["ExecutionAttemptSignal"]
        ))

        # Capacidades de contraste
        self.register(CapabilityDefinition(
            capability_id="can_contrast_legacy",
            name="Contrast with Legacy",
            description="Capacidad de contrastar resultados con sistema legacy",
            category="contrast",
            produced_signals=["DecisionDivergenceSignal", "ConfidenceDropSignal"]
        ))

        # Capacidades de auditoría
        self.register(CapabilityDefinition(
            capability_id="can_audit_signals",
            name="Audit Signals",
            description="Capacidad de auditar señales generadas",
            category="audit",
            required_signals=["*"]
        ))

        self.register(CapabilityDefinition(
            capability_id="can_audit_consumers",
            name="Audit Consumers",
            description="Capacidad de auditar consumidores",
            category="audit",
            produced_signals=["ConsumerHealthSignal"]
        ))

    def register(self, definition: CapabilityDefinition):
        """Registra una definición de capacidad"""
        self.definitions[definition.capability_id] = definition

    def get(self, capability_id:  str) -> Optional[CapabilityDefinition]:
        """Obtiene definición de una capacidad"""
        return self.definitions.get(capability_id)

    def is_valid(self, capability_id: str) -> bool:
        """Verifica si una capacidad es válida"""
        return capability_id in self.definitions

    def get_by_category(self, category: str) -> List[CapabilityDefinition]:
        """Obtiene capacidades por categoría"""
        return [d for d in self.definitions.values() if d.category == category]

    def get_producers_of(self, signal_type: str) -> List[CapabilityDefinition]:
        """Obtiene capacidades que producen un tipo de señal"""
        result = []
        for d in self.definitions.values():
            if signal_type in d.produced_signals or "*" in d.produced_signals:
                result.append(d)
        return result

    def get_consumers_of(self, signal_type: str) -> List[CapabilityDefinition]:
        """Obtiene capacidades que requieren un tipo de señal"""
        result = []
        for d in self.definitions.values():
            if signal_type in d.required_signals or "*" in d.required_signals:
                result.append(d)
        return result
