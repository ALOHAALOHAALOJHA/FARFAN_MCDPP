"""
Módulo:  method_expander.py
Propósito: Expandir cada método asignado en una unidad semántica completa

Ubicación: src/farfan_pipeline/phases/Phase_two/contract_generator/method_expander.py

RESPONSABILIDADES:
1. Transformar MethodAssignment en ExpandedMethodUnit
2. Derivar campos semánticos desde la clasificación (NO inventar)
3. Enriquecer con metadata de contexto
4. Generar veto_conditions para métodos N3
5. Preservar trazabilidad completa

PRINCIPIOS: 
- El expander NUNCA inventa información epistémica
- Toda derivación se basa en reglas documentadas en la guía
- Los campos expandidos son derivaciones lógicas, no inferencias

Versión: 4.0.0-granular
Fecha: 2026-01-03
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . input_registry import MethodAssignment

logger = logging. getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES DE DERIVACIÓN
# ══════════════════════════════════════════════════════════════════════════════

EXPANDER_VERSION = "4.0.0-granular"

# Mapeo de nivel a evidence requirements típicos (PARTE II, Sec 2.2)
LEVEL_EVIDENCE_REQUIREMENTS:  dict[str, tuple[str, ...]] = {
    "N1-EMP": (
        "raw_document_text",
        "preprocesado_metadata",
    ),
    "N2-INF": (
        "raw_facts_from_N1",
        "confidence_scores",
    ),
    "N3-AUD": (
        "raw_facts_from_N1",
        "inferences_from_N2",
        "audit_criteria",
    ),
}

# Mapeo de output_type a claims típicos (PARTE I, Sec 1.3)
OUTPUT_TYPE_CLAIMS: dict[str, tuple[str, ...]] = {
    "FACT": (
        "observable_datum",
        "literal_extraction",
    ),
    "PARAMETER": (
        "derived_score",
        "probability_estimate",
        "relational_inference",
    ),
    "CONSTRAINT": (
        "validation_flag",
        "confidence_modulator",
        "veto_signal",
    ),
}

# Mapeo de nivel a failure modes típicos (PARTE II, Sec 2.2)
LEVEL_FAILURE_MODES: dict[str, tuple[str, ...]] = {
    "N1-EMP":  (
        "empty_extraction",
        "pattern_not_found",
        "malformed_input",
    ),
    "N2-INF": (
        "insufficient_evidence",
        "prior_undefined",
        "computation_error",
    ),
    "N3-AUD": (
        "validation_inconclusive",
        "criteria_not_met",
        "veto_triggered",
    ),
}

# Mapeo de nivel a constraints base (PARTE II, Sec 2.2)
LEVEL_BASE_CONSTRAINTS: dict[str, tuple[str, ...]] = {
    "N1-EMP": (
        "output_must_be_literal",
        "no_transformation_allowed",
    ),
    "N2-INF": (
        "requires_N1_input",
        "output_is_derived",
    ),
    "N3-AUD": (
        "requires_N1_and_N2_input",
        "can_veto_lower_levels",
        "asymmetric_authority",
    ),
}

# Mapeo de nivel a descripción de fase (PARTE II)
LEVEL_PHASE_DESCRIPTIONS: dict[str, str] = {
    "N1-EMP": (
        "Extrae y procesa observaciones empíricas directas del texto.  "
        "Produce hechos observables sin interpretación."
    ),
    "N2-INF": (
        "Calcula parámetros inferenciales basados en evidencia de N1. "
        "Transforma hechos en parámetros cuantitativos."
    ),
    "N3-AUD":  (
        "Valida y puede vetar hallazgos basándose en criterios de robustez. "
        "Genera restricciones que pueden bloquear resultados."
    ),
}

# Mapeo de nivel a dependencies (para method_binding)
LEVEL_DEPENDENCIES:  dict[str, tuple[str, ...]] = {
    "N1-EMP":  (),
    "N2-INF": ("raw_facts",),
    "N3-AUD": ("raw_facts", "inferences"),
}

# Mapeo de nivel a modulates (para N3)
LEVEL_MODULATES:  dict[str, tuple[str, ...]] = {
    "N1-EMP": (),
    "N2-INF": ("edge_weights", "confidence_scores"),
    "N3-AUD": ("raw_facts. confidence", "inferences.confidence"),
}

# Veto conditions por defecto para N3 según tipo de contrato (PARTE V)
DEFAULT_VETO_CONDITIONS: dict[str, dict[str, dict[str, Any]]] = {
    "TYPE_A": {
        "semantic_contradiction": {
            "trigger": "semantic_contradiction_detected == True",
            "action": "block_branch",
            "scope": "contradicting_nodes",
            "confidence_multiplier": 0.0,
            "rationale": "Semantic contradiction invalidates affected nodes",
        },
        "low_coherence": {
            "trigger":  "coherence_score < 0.5",
            "action": "reduce_confidence",
            "scope": "source_facts",
            "confidence_multiplier": 0.5,
            "rationale": "Low coherence reduces reliability",
        },
    },
    "TYPE_B":  {
        "statistical_significance_failed": {
            "trigger": "p_value > 0.05",
            "action": "reduce_confidence",
            "scope":  "source_facts",
            "confidence_multiplier": 0.5,
            "rationale":  "Statistical insignificance degrades confidence",
        },
        "sample_size_insufficient": {
            "trigger": "sample_size < 30",
            "action":  "flag_caution",
            "scope": "affected_inferences",
            "confidence_multiplier": 0.7,
            "rationale": "Small sample size warrants caution",
        },
    },
    "TYPE_C": {
        "cycle_detected": {
            "trigger": "has_cycle(DAG) == True",
            "action":  "invalidate_graph",
            "scope": "entire_causal_graph",
            "confidence_multiplier": 0.0,
            "rationale": "Cyclic DAG is epistemically invalid",
        },
        "topological_violation": {
            "trigger": "topological_order_violated == True",
            "action":  "block_branch",
            "scope":  "affected_subgraph",
            "confidence_multiplier": 0.0,
            "rationale": "Topological violation invalidates causal chain",
        },
    },
    "TYPE_D": {
        "budget_gap_critical": {
            "trigger": "budget_gap > 0.5",
            "action": "block_branch",
            "scope":  "affected_goals",
            "confidence_multiplier": 0.0,
            "rationale": "Critical budget gap blocks feasibility",
        },
        "budget_gap_significant": {
            "trigger": "budget_gap > 0.3",
            "action": "reduce_confidence",
            "scope":  "affected_goals",
            "confidence_multiplier": 0.3,
            "rationale": "Significant budget gap reduces confidence",
        },
    },
    "TYPE_E": {
        "logical_contradiction": {
            "trigger": "logical_contradiction_detected == True",
            "action": "block_branch",
            "scope": "contradicting_nodes",
            "confidence_multiplier": 0.0,
            "rationale": "Logical contradiction invalidates affected nodes (Popper)",
        },
        "sequence_violation": {
            "trigger": "sequence_logic_violated == True",
            "action": "flag_caution",
            "scope": "affected_sequence",
            "confidence_multiplier": 0.2,
            "rationale": "Sequence violation degrades logical coherence",
        },
    },
}

# Veto conditions genéricas para cualquier N3
GENERIC_N3_VETO_CONDITIONS:  dict[str, dict[str, Any]] = {
    "critical_failure_veto": {
        "trigger":  "critical_validation_failed == True",
        "action":  "invalidate_graph",
        "scope": "entire_output",
        "confidence_multiplier":  0.0,
        "rationale": "Critical validation failure invalidates entire output",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# DATACLASS PRINCIPAL - UNIDAD EXPANDIDA
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ExpandedMethodUnit: 
    """
    Unidad de método completamente expandida. 

    Representa un método con toda su información semántica explícita,
    lista para ser incluida en un contrato. 

    INMUTABLE después de creación. 

    Esta estructura captura: 
    - Identidad del método (class, name, file, provides)
    - Clasificación epistémica (level, epistemology, output_type)
    - Comportamiento de fusión (fusion_behavior, fusion_symbol)
    - Justificación (rationale, confidence, affinities)
    - Firma técnica (parameters, return_type, is_private)
    - Campos expandidos derivados (evidence, claims, constraints, failures)
    - Veto conditions (solo para N3)
    - Metadata de trazabilidad
    """
    # ══════════════════════════════════════════════════════════════════════
    # IDENTIDAD
    # ══════════════════════════════════════════════════════════════════════
    method_id: str  # ClassName. method_name
    class_name:  str
    method_name: str
    mother_file: str
    provides: str

    # ══════════════════════════════════════════════════════════════════════
    # CLASIFICACIÓN EPISTÉMICA
    # ══════════════════════════════════════════════════════════════════════
    level: str  # N1-EMP, N2-INF, N3-AUD
    level_name: str  # Base Empírica, Procesamiento Inferencial, etc.
    epistemology: str  # Empirismo positivista, Bayesianismo, Falsacionismo
    output_type:  str  # FACT, PARAMETER, CONSTRAINT

    # ══════════════════════════════════════════════════════════════════════
    # COMPORTAMIENTO DE FUSIÓN
    # ══════════════════════════════════════════════════════════════════════
    fusion_behavior: str  # additive, multiplicative, gate
    fusion_symbol: str  # ⊕, ⊗, ⊘

    # ══════════════════════════════════════════════════════════════════════
    # JUSTIFICACIÓN
    # ══════════════════════════════════════════════════════════════════════
    classification_rationale: str
    confidence_score: float
    contract_affinities: dict[str, float]

    # ══════════════════════════════════════════════════════════════════════
    # FIRMA TÉCNICA
    # ══════════════════════════════════════════════════════════════════════
    parameters: tuple[str, ...]
    return_type: str
    is_private: bool

    # ══════════════════════════════════════════════════════════════════════
    # CAMPOS EXPANDIDOS (derivados, no inventados)
    # ══════════════════════════════════════════════════════════════════════
    evidence_requirements: tuple[str, ...]
    output_claims: tuple[str, ...]
    constraints_and_limits: tuple[str, ...]
    failure_modes: tuple[str, ...]
    interaction_notes: str
    description: str

    # ══════════════════════════════════════════════════════════════════════
    # DEPENDENCIAS Y MODIFICACIONES
    # ══════════════════════════════════════════════════════════════════════
    requires:  tuple[str, ...]  # Dependencias de entrada
    modifies: tuple[str, ...]  # Lo que modifica (para N2) o modulates (para N3)

    # ══════════════════════════════════════════════════════════════════════
    # VETO CONDITIONS (solo para N3)
    # ══════════════════════════════════════════════════════════════════════
    veto_conditions: dict[str, dict[str, Any]] = field(default_factory=dict)

    # ══════════════════════════════════════════════════════════════════════
    # METADATA DE TRAZABILIDAD
    # ══════════════════════════════════════════════════════════════════════
    expansion_source: str
    expansion_timestamp: str

    @property
    def level_prefix(self) -> str:
        """Prefijo del nivel (N1, N2, N3)"""
        return self.level.split("-")[0] if "-" in self.level else self.level

    @property
    def is_n3_auditor(self) -> bool:
        """Indica si es un método de auditoría (N3)"""
        return self.level. startswith("N3")

    @property
    def is_low_confidence(self) -> bool:
        """Indica si tiene baja confianza (< 0.7)"""
        return self.confidence_score < 0.7

    @property
    def has_veto_power(self) -> bool:
        """Indica si tiene poder de veto"""
        return self.is_n3_auditor and len(self.veto_conditions) > 0

    def to_contract_dict(self) -> dict[str, Any]:
        """
        Convierte a diccionario para inclusión en contrato JSON. 

        Returns:
            Diccionario con todos los campos para el contrato
        """
        base_dict = {
            "class_name": self.class_name,
            "method_name":  self.method_name,
            "mother_file": self.mother_file,
            "provides":  self.provides,
            "method_id": self.method_id,
            "level": self. level,
            "level_name": self.level_name,
            "epistemology": self. epistemology,
            "output_type": self.output_type,
            "fusion_behavior":  self.fusion_behavior,
            "fusion_symbol": self.fusion_symbol,
            "classification_rationale": self.classification_rationale,
            "confidence_score": self.confidence_score,
            "contract_affinities":  self.contract_affinities,
            "parameters": list(self.parameters),
            "return_type": self.return_type,
            "is_private": self.is_private,
            "evidence_requirements": list(self.evidence_requirements),
            "output_claims": list(self.output_claims),
            "constraints_and_limits": list(self.constraints_and_limits),
            "failure_modes": list(self.failure_modes),
            "interaction_notes": self. interaction_notes,
            "expansion_source": self.expansion_source,
            "expansion_timestamp":  self.expansion_timestamp,
            "description": self.description,
            "requires": list(self.requires),
        }

        # Añadir modifies/modulates según nivel
        if self.level.startswith("N2"):
            base_dict["modifies"] = list(self.modifies)
        elif self.level.startswith("N3"):
            base_dict["veto_conditions"] = self.veto_conditions
            base_dict["modulates"] = list(self.modifies)

        return base_dict


# ══════════════════════════════════════════════════════════════════════════════
# CLASE EXPANDIDORA
# ══════════════════════════════════════════════════════════════════════════════


class MethodExpander:
    """
    Expande métodos asignados en unidades semánticas completas.

    RESPONSABILIDADES:
    1. Transformar MethodAssignment → ExpandedMethodUnit
    2. Derivar campos semánticos de la clasificación existente
    3. Generar veto_conditions para métodos N3
    4. Preservar trazabilidad completa

    PRINCIPIOS:
    - NUNCA inventa información epistémica
    - Toda derivación se basa en reglas documentadas
    - Los campos expandidos son derivaciones lógicas

    USO:
        expander = MethodExpander()
        expanded = expander.expand_method(assignment, context)
    """

    def __init__(self, timestamp: str | None = None):
        """
        Inicializa el expander. 

        Args:
            timestamp:  ISO timestamp para trazabilidad.  Si None, se genera automáticamente. 
        """
        self.expansion_timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self._expansion_count = 0

        logger.info(f"MethodExpander initialized, version {EXPANDER_VERSION}")

    def expand_method(
        self,
        assignment: "MethodAssignment",
        context: dict[str, Any],
    ) -> ExpandedMethodUnit:
        """
        Expande un método asignado en unidad semántica completa.

        SECUENCIA: 
        1. Derivar evidence_requirements del nivel
        2. Derivar output_claims del output_type
        3. Derivar constraints del nivel y contexto
        4. Derivar failure_modes del nivel
        5. Generar interaction_notes del contexto
        6. Generar description del nivel
        7. Derivar dependencies del nivel
        8. Generar veto_conditions si es N3
        9. Ensamblar ExpandedMethodUnit

        Args: 
            assignment: MethodAssignment del method_sets_by_question. json
            context: Contexto de la pregunta con: 
                - type_code: Código del tipo de contrato (TYPE_A, etc.)
                - type_name: Nombre del tipo
                - fusion_strategy: Estrategia de fusión
                - question_id: ID de la pregunta
                - phase_id: ID de la fase (opcional)

        Returns:
            ExpandedMethodUnit con todos los campos poblados
        """
        # ══════════════════════════════════════════════════════════════════
        # DERIVACIONES BASADAS EN CLASIFICACIÓN (NO INVENTA)
        # ══════════════════════════════════════════════════════════════════

        # 1. Evidence requirements del nivel
        evidence_reqs = self._derive_evidence_requirements(assignment. level)

        # 2. Output claims del output_type
        output_claims = self._derive_output_claims(assignment.output_type)

        # 3. Constraints del nivel y contexto
        constraints = self._derive_constraints(assignment, context)

        # 4. Failure modes del nivel
        failure_modes = self._derive_failure_modes(assignment.level)

        # 5. Interaction notes del contexto
        interaction = self._derive_interaction_notes(assignment, context)

        # 6. Description del nivel
        description = self._derive_description(assignment. level)

        # 7. Dependencies del nivel
        requires = self._derive_requires(assignment.level)
        modifies = self._derive_modifies(assignment.level)

        # 8. Veto conditions si es N3
        veto_conditions = self._derive_veto_conditions(assignment, context)

        # 9. Enriquecer classification_rationale con referencia a la guía
        enhanced_rationale = (
            f"{assignment.classification_rationale} (PARTE II, Sección 2.2)"
        )

        # ══════════════════════════════════════════════════════════════════
        # ENSAMBLAJE
        # ══════════════════════════════════════════════════════════════════

        expanded = ExpandedMethodUnit(
            # Identidad
            method_id=assignment.full_id,
            class_name=assignment.class_name,
            method_name=assignment.method_name,
            mother_file=assignment.mother_file,
            provides=assignment.provides,
            # Clasificación epistémica
            level=assignment.level,
            level_name=assignment.level_name,
            epistemology=assignment.epistemology,
            output_type=assignment.output_type,
            # Comportamiento de fusión
            fusion_behavior=assignment.fusion_behavior,
            fusion_symbol=assignment.fusion_symbol,
            # Justificación
            classification_rationale=enhanced_rationale,
            confidence_score=assignment.confidence_score,
            contract_affinities=dict(assignment.contract_affinities),
            # Firma técnica
            parameters=assignment.parameters,
            return_type=assignment. return_type,
            is_private=assignment.is_private,
            # Campos expandidos
            evidence_requirements=evidence_reqs,
            output_claims=output_claims,
            constraints_and_limits=constraints,
            failure_modes=failure_modes,
            interaction_notes=interaction,
            description=description,
            # Dependencias
            requires=requires,
            modifies=modifies,
            # Veto conditions
            veto_conditions=veto_conditions,
            # Trazabilidad
            expansion_source="method_sets_by_question.json",
            expansion_timestamp=self.expansion_timestamp,
        )

        self._expansion_count += 1
        logger.debug(f"  Expanded {assignment.full_id} ({assignment.level})")

        return expanded

    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS - DERIVACIONES
    # ══════════════════════════════════════════════════════════════════════════

    def _derive_evidence_requirements(self, level: str) -> tuple[str, ...]:
        """
        Deriva evidence requirements del nivel.

        Basado en PARTE II, Sección 2.2 de la guía. 

        Args:
            level: Nivel epistémico (N1-EMP, N2-INF, N3-AUD)

        Returns:
            Tupla de requirements
        """
        return LEVEL_EVIDENCE_REQUIREMENTS. get(level, ())

    def _derive_output_claims(self, output_type: str) -> tuple[str, ...]:
        """
        Deriva output claims del output_type. 

        Basado en PARTE I, Sección 1.3 de la guía.

        Args:
            output_type:  Tipo de output (FACT, PARAMETER, CONSTRAINT)

        Returns:
            Tupla de claims
        """
        return OUTPUT_TYPE_CLAIMS.get(output_type, ())

    def _derive_constraints(
        self,
        assignment: "MethodAssignment",
        context: dict[str, Any],
    ) -> tuple[str, ...]:
        """
        Deriva constraints de la clasificación y contexto.

        Basado en PARTE II, Sección 2.2 de la guía.

        Args:
            assignment: MethodAssignment con clasificación
            context: Contexto de la pregunta

        Returns:
            Tupla de constraints
        """
        constraints:  list[str] = []

        # Constraints base del nivel
        base_constraints = LEVEL_BASE_CONSTRAINTS.get(assignment. level, ())
        constraints. extend(base_constraints)

        # Constraint de confianza baja
        if assignment.confidence_score < 0.7:
            constraints.append("low_confidence_method")

        return tuple(constraints)

    def _derive_failure_modes(self, level: str) -> tuple[str, ...]:
        """
        Deriva failure modes del nivel. 

        Basado en PARTE II, Sección 2.2 de la guía.

        Args:
            level: Nivel epistémico

        Returns:
            Tupla de failure modes
        """
        return LEVEL_FAILURE_MODES.get(level, ())

    def _derive_interaction_notes(
        self,
        assignment: "MethodAssignment",
        context: dict[str, Any],
    ) -> str:
        """
        Deriva notas de interacción del contexto.

        Args:
            assignment: MethodAssignment
            context: Contexto de la pregunta

        Returns:
            String con notas de interacción
        """
        type_code = context.get("type_code", "UNKNOWN")
        strategy = context.get("fusion_strategy", "UNKNOWN")

        return (
            f"Method operates within {type_code} contract.  "
            f"Fusion strategy: {strategy}. "
            f"Level {assignment.level} provides {assignment.output_type} output."
        )

    def _derive_description(self, level:  str) -> str:
        """
        Deriva descripción del nivel.

        Basado en PARTE II de la guía.

        Args:
            level: Nivel epistémico

        Returns:
            String con descripción
        """
        return LEVEL_PHASE_DESCRIPTIONS.get(level, "")

    def _derive_requires(self, level: str) -> tuple[str, ...]: 
        """
        Deriva dependencias de entrada del nivel.

        Args:
            level: Nivel epistémico

        Returns:
            Tupla de dependencias
        """
        return LEVEL_DEPENDENCIES.get(level, ())

    def _derive_modifies(self, level: str) -> tuple[str, ...]:
        """
        Deriva lo que el método modifica o modula.

        Para N2: modifies (edge_weights, confidence_scores)
        Para N3: modulates (raw_facts. confidence, inferences.confidence)

        Args:
            level: Nivel epistémico

        Returns:
            Tupla de targets modificados
        """
        return LEVEL_MODULATES.get(level, ())

    def _derive_veto_conditions(
        self,
        assignment: "MethodAssignment",
        context: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """
        Deriva veto conditions para métodos N3.

        Basado en PARTE V de la guía (blocking_propagation_rules).

        Solo aplica a métodos N3-AUD.  Retorna dict vacío para otros niveles.

        Args:
            assignment: MethodAssignment
            context: Contexto con type_code

        Returns:
            Diccionario de veto conditions
        """
        # Solo N3 tiene veto conditions
        if not assignment.level.startswith("N3"):
            return {}

        type_code = context.get("type_code", "TYPE_A")
        veto_conditions:  dict[str, dict[str, Any]] = {}

        # Obtener veto conditions específicas del tipo
        type_specific = DEFAULT_VETO_CONDITIONS.get(type_code, {})

        # Seleccionar veto conditions relevantes basado en el nombre del método
        method_name_lower = assignment.method_name.lower()

        # Heurísticas para seleccionar veto conditions
        if "coherence" in method_name_lower or "semantic" in method_name_lower: 
            if "low_coherence" in type_specific:
                veto_conditions["low_coherence"] = type_specific["low_coherence"]
            if "semantic_contradiction" in type_specific:
                veto_conditions["semantic_contradiction"] = type_specific["semantic_contradiction"]

        if "statistical" in method_name_lower or "significance" in method_name_lower: 
            if "statistical_significance_failed" in type_specific:
                veto_conditions["statistical_significance_failed"] = type_specific["statistical_significance_failed"]

        if "cycle" in method_name_lower or "acyclic" in method_name_lower:
            if "cycle_detected" in type_specific: 
                veto_conditions["cycle_detected"] = type_specific["cycle_detected"]

        if "budget" in method_name_lower or "sufficiency" in method_name_lower: 
            if "budget_gap_critical" in type_specific:
                veto_conditions["budget_gap_critical"] = type_specific["budget_gap_critical"]
            if "budget_gap_significant" in type_specific:
                veto_conditions["budget_gap_significant"] = type_specific["budget_gap_significant"]

        if "logical" in method_name_lower or "contradiction" in method_name_lower: 
            if "logical_contradiction" in type_specific:
                veto_conditions["logical_contradiction"] = type_specific["logical_contradiction"]

        if "sequence" in method_name_lower: 
            if "sequence_violation" in type_specific:
                veto_conditions["sequence_violation"] = type_specific["sequence_violation"]

        # Si no se encontraron veto conditions específicas, añadir la genérica
        if not veto_conditions:
            veto_conditions["critical_failure_veto"] = GENERIC_N3_VETO_CONDITIONS["critical_failure_veto"]

        return veto_conditions

    # ══════════════════════════════════════════════════════════════════════════
    # PROPIEDADES PÚBLICAS
    # ══════════════════════════════════════════════════════════════════════════

    @property
    def expansion_count(self) -> int:
        """Número de métodos expandidos por esta instancia."""
        return self._expansion_count

    @property
    def version(self) -> str:
        """Versión del expander."""
        return EXPANDER_VERSION