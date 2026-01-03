"""
Módulo: chain_composer.py
Propósito: Componer cadena epistémica ordenada a partir de unidades expandidas
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PhaseMetadata:
    """Metadata for a specific execution phase."""
    level_prefix: str
    level_name: str
    epistemology: str
    dependencies: tuple[str, ...]
    output_target: str


@dataclass(frozen=True)
class EpistemicChain:
    """
    Cadena epistémica ordenada.

    INVARIANTES:
    - El orden de métodos es EXACTAMENTE el del input
    - No hay fusión implícita
    - Cada método mantiene su identidad discreta
    """
    question_id: str
    contract_type: dict[str, str]

    # Cadenas por fase (orden preservado)
    phase_a_chain: tuple["ExpandedMethodUnit", ...]
    phase_b_chain: tuple["ExpandedMethodUnit", ...]
    phase_c_chain: tuple["ExpandedMethodUnit", ...]

    # Metadata de composición
    total_methods: int
    composition_timestamp: str

    # Evidencia matemática preservada del input
    efficiency_score: float
    mathematical_evidence: dict[str, Any]
    doctoral_justification: str

    @property
    def full_chain_ordered(self) -> tuple["ExpandedMethodUnit", ...]:
        """Retorna cadena completa en orden: N1 → N2 → N3"""
        return self.phase_a_chain + self.phase_b_chain + self.phase_c_chain

    @property
    def contract_type_code(self) -> str:
        """Código del tipo de contrato (e.g., TYPE_A)."""
        return self.contract_type.get("codigo") or self.contract_type.get("code") or "UNKNOWN"

    @property
    def n1_count(self) -> int:
        return len(self.phase_a_chain)

    @property
    def n2_count(self) -> int:
        return len(self.phase_b_chain)

    @property
    def n3_count(self) -> int:
        return len(self.phase_c_chain)

    @property
    def phase_a_metadata(self) -> PhaseMetadata:
        return PhaseMetadata(
            level_prefix="N1",
            level_name="Empirical Foundation",
            epistemology="Positivist",
            dependencies=(),
            output_target="raw_facts"
        )

    @property
    def phase_b_metadata(self) -> PhaseMetadata:
        return PhaseMetadata(
            level_prefix="N2",
            level_name="Inferential Processing",
            epistemology="Bayesian/Constructivist",
            dependencies=("raw_facts",),
            output_target="inferences"
        )

    @property
    def phase_c_metadata(self) -> PhaseMetadata:
        return PhaseMetadata(
            level_prefix="N3",
            level_name="Epistemic Audit",
            epistemology="Popperian Falsificationism",
            dependencies=("raw_facts", "inferences"),
            output_target="validated_output"
        )


class ChainComposer:
    """
    Compone cadena epistémica desde unidades expandidas.

    PROPIEDADES:
    1. Preservación de orden - NUNCA reordena
    2. Sin agrupación - NUNCA agrupa por criterio no-dado
    3. Fronteras explícitas - transiciones entre fases son declaradas
    4. Determinista - misma entrada → misma salida
    """

    def __init__(self, expander: "MethodExpander"):
        self.expander = expander

    def compose_chain(
        self,
        method_set: "QuestionMethodSet",
        contract_classification: "ContractClassification",
    ) -> EpistemicChain:
        """
        Compone cadena epistémica para una pregunta.

        SECUENCIA:
        1. Validar coherencia nivel-fase (E-001)
        2. Expandir métodos N1 (preservando orden)
        3. Expandir métodos N2 (preservando orden)
        4. Expandir métodos N3 (preservando orden)
        5. Ensamblar cadena con metadata

        Args:
            method_set: QuestionMethodSet con métodos asignados
            contract_classification: ContractClassification para contexto

        Returns:
            EpistemicChain inmutable
        """
        # ══════════════════════════════════════════════════════════════════
        # VALIDACIÓN PRE-COMPOSICIÓN: Coherencia Nivel-Fase (E-001)
        # ══════════════════════════════════════════════════════════════════
        self._validate_phase_level_coherence(method_set)

        # Construir contexto para expansión
        context = {
            "type_code": contract_classification.tipo_contrato["codigo"],
            "type_name": contract_classification.tipo_contrato["nombre"],
            "fusion_strategy": method_set.contract_type.get("fusion_strategy", ""),
            "question_id": method_set.question_id,
        }

        # Expandir cada fase PRESERVANDO ORDEN EXACTO
        phase_a = tuple(
            self.expander.expand_method(m, context)
            for m in method_set.phase_a_N1
        )

        phase_b = tuple(
            self.expander.expand_method(m, context)
            for m in method_set.phase_b_N2
        )

        phase_c = tuple(
            self.expander.expand_method(m, context)
            for m in method_set.phase_c_N3
        )

        # Ensamblar cadena
        return EpistemicChain(
            question_id=method_set.question_id,
            contract_type=method_set.contract_type,
            phase_a_chain=phase_a,
            phase_b_chain=phase_b,
            phase_c_chain=phase_c,
            total_methods=len(phase_a) + len(phase_b) + len(phase_c),
            composition_timestamp=self.expander.expansion_timestamp,
            efficiency_score=method_set.efficiency_score,
            mathematical_evidence=method_set.mathematical_evidence,
            doctoral_justification=method_set.doctoral_justification,
        )

    def _validate_phase_level_coherence(self, method_set: "QuestionMethodSet") -> None:
        """
        Valida que los métodos asignados a cada fase tengan el nivel correcto.

        REGLAS ESTRICTAS:
        - phase_a_N1 → SOLO métodos con level que empiece con "N1"
        - phase_b_N2 → SOLO métodos con level que empiece con "N2"
        - phase_c_N3 → SOLO métodos con level que empiece con "N3"

        FALLA DURO si cualquier método viola esta regla.
        """
        violations = []

        # Validar phase_a_N1
        for method in method_set.phase_a_N1:
            if not method.level.startswith("N1"):
                violations.append(
                    f"  - phase_a_N1 contains {method.full_id} with level '{method.level}' "
                    f"(expected N1-*)"
                )

        # Validar phase_b_N2
        for method in method_set.phase_b_N2:
            if not method.level.startswith("N2"):
                violations.append(
                    f"  - phase_b_N2 contains {method.full_id} with level '{method.level}' "
                    f"(expected N2-*)"
                )

        # Validar phase_c_N3
        for method in method_set.phase_c_N3:
            if not method.level.startswith("N3"):
                violations.append(
                    f"  - phase_c_N3 contains {method.full_id} with level '{method.level}' "
                    f"(expected N3-*)"
                )

        if violations:
            error_report = "\n".join(violations)
            raise ValueError(
                f"HARD FAILURE (E-001): Phase-Level Coherence Violation\n"
                f"  Question: {method_set.question_id}\n"
                f"  Violations: {len(violations)}\n"
                f"Details:\n{error_report}\n\n"
                f"This error should have been caught by InputLoader. "
                f"Check method_sets_by_question.json for inconsistencies."
            )
