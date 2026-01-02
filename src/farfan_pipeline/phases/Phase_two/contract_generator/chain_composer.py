"""
Módulo: chain_composer.py
Propósito: Componer cadena epistémica ordenada a partir de unidades expandidas
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


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
        1. Expandir métodos N1 (preservando orden)
        2. Expandir métodos N2 (preservando orden)
        3. Expandir métodos N3 (preservando orden)
        4. Ensamblar cadena con metadata

        Args:
            method_set: QuestionMethodSet con métodos asignados
            contract_classification: ContractClassification para contexto

        Returns:
            EpistemicChain inmutable
        """
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
