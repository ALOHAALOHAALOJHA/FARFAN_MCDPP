"""
Módulo:  method_expander.py
Propósito: Expandir cada método asignado en una unidad semántica completa
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExpandedMethodUnit:
    """
    Unidad epistémica expandida de un método.

    Esta es la GRANULARIDAD ATÓMICA del sistema.
    Cada campo existe porque tiene significado epistémico.
    NADA se omite.
    """
    # Identidad
    method_id: str  # class_name.method_name
    class_name: str
    method_name: str
    mother_file: str
    provides: str

    # Clasificación epistémica
    level: str
    level_name: str
    epistemology: str
    output_type: str

    # Comportamiento de fusión
    fusion_behavior: str
    fusion_symbol: str

    # Justificación
    classification_rationale: str
    confidence_score: float
    contract_affinities: dict[str, float]

    # Firma técnica
    parameters: tuple[str, ...]
    return_type: str
    is_private: bool

    # Campos expandidos (derivados de la clasificación)
    evidence_requirements: tuple[str, ...]
    output_claims: tuple[str, ...]
    constraints_and_limits: tuple[str, ...]
    failure_modes: tuple[str, ...]
    interaction_notes: str

    # Campos para auditoría
    expansion_source: str  # Referencia al archivo de origen
    expansion_timestamp: str  # ISO timestamp de expansión


class MethodExpander:
    """
    Expande métodos asignados en unidades semánticas completas.

    PROPIEDADES:
    1. NO infiere campos - los deriva de la clasificación
    2. NO reordena - preserva orden de input
    3. NO colapsa - cada método es una unidad discreta
    4. Determinista - misma entrada → misma salida
    """

    # Mapeo de nivel a requirements típicos
    LEVEL_EVIDENCE_REQUIREMENTS = {
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

    # Mapeo de output_type a claims típicos
    OUTPUT_TYPE_CLAIMS = {
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

    # Mapeo de nivel a failure modes típicos
    LEVEL_FAILURE_MODES = {
        "N1-EMP": (
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

    def __init__(self, expansion_timestamp: str):
        """
        Args:
            expansion_timestamp: ISO timestamp para trazabilidad
        """
        self.expansion_timestamp = expansion_timestamp

    def expand_method(
        self,
        assignment: "MethodAssignment",
        question_context: dict[str, Any],
    ) -> ExpandedMethodUnit:
        """
        Expande un método asignado en unidad semántica completa.

        Args:
            assignment: MethodAssignment del method_sets_by_question.json
            question_context: Contexto de la pregunta (TYPE, estrategias, etc.)

        Returns:
            ExpandedMethodUnit con todos los campos poblados
        """
        # Derivar campos de la clasificación (NO inventar)
        evidence_reqs = self._derive_evidence_requirements(assignment.level)
        output_claims = self._derive_output_claims(assignment.output_type)
        constraints = self._derive_constraints(assignment, question_context)
        failure_modes = self._derive_failure_modes(assignment.level)
        interaction = self._derive_interaction_notes(assignment, question_context)

        # Enriquecer classification_rationale con referencia a la guía
        enhanced_rationale = f"{assignment.classification_rationale} (PARTE II, Sección 2.2)"

        return ExpandedMethodUnit(
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
            contract_affinities=assignment.contract_affinities,

            # Firma técnica
            parameters=assignment.parameters,
            return_type=assignment.return_type,
            is_private=assignment.is_private,

            # Campos expandidos
            evidence_requirements=evidence_reqs,
            output_claims=output_claims,
            constraints_and_limits=constraints,
            failure_modes=failure_modes,
            interaction_notes=interaction,

            # Auditoría
            expansion_source="method_sets_by_question.json",
            expansion_timestamp=self.expansion_timestamp,
        )

    def _derive_evidence_requirements(self, level: str) -> tuple[str, ...]:
        """Deriva requirements del nivel (no inventa)"""
        return self.LEVEL_EVIDENCE_REQUIREMENTS.get(level, ())

    def _derive_output_claims(self, output_type: str) -> tuple[str, ...]:
        """Deriva claims del output_type (no inventa)"""
        return self.OUTPUT_TYPE_CLAIMS.get(output_type, ())

    def _derive_constraints(
        self,
        assignment: "MethodAssignment",
        context: dict[str, Any],
    ) -> tuple[str, ...]:
        """Deriva constraints de la clasificación y contexto"""
        constraints = []

        # Constraint de nivel
        if assignment.level == "N1-EMP":
            constraints.append("output_must_be_literal")
            constraints.append("no_transformation_allowed")
        elif assignment.level == "N2-INF":
            constraints.append("requires_N1_input")
            constraints.append("output_is_derived")
        elif assignment.level == "N3-AUD":
            constraints.append("requires_N1_and_N2_input")
            constraints.append("can_veto_lower_levels")
            constraints.append("asymmetric_authority")

        # Constraint de confianza
        if assignment.confidence_score < 0.7:
            constraints.append("low_confidence_method")

        return tuple(constraints)

    def _derive_failure_modes(self, level: str) -> tuple[str, ...]:
        """Deriva failure modes del nivel (no inventa)"""
        return self.LEVEL_FAILURE_MODES.get(level, ())

    def _derive_interaction_notes(
        self,
        assignment: "MethodAssignment",
        context: dict[str, Any],
    ) -> str:
        """Deriva notas de interacción del contexto"""
        type_code = context.get("type_code", "UNKNOWN")
        strategy = context.get("fusion_strategy", "UNKNOWN")

        return (
            f"Method operates within {type_code} contract. "
            f"Fusion strategy: {strategy}. "
            f"Level {assignment.level} provides {assignment.output_type} output."
        )
