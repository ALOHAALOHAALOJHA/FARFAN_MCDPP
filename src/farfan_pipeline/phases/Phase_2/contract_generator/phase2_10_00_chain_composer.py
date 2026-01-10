"""
Módulo:  chain_composer.py
Propósito: Componer cadena epistémica ordenada a partir de unidades expandidas

Ubicación: src/farfan_pipeline/phases/Phase_2/contract_generator/chain_composer.py

RESPONSABILIDADES:
1. Validar coherencia nivel-fase antes de composición (E-001)
2. Expandir métodos preservando orden EXACTO del input
3. Ensamblar cadena inmutable con metadata completa
4. Generar reportes de composición para auditoría

INVARIANTES:
- El orden de métodos es EXACTAMENTE el del input (Principio I-8)
- No hay fusión implícita (Principio I-9)
- Cada método mantiene su identidad discreta
- Falla duro ante cualquier violación de coherencia nivel-fase (E-001)

Versión: 4.0.0-granular
Fecha: 2026-01-03
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . method_expander import ExpandedMethodUnit, MethodExpander
    from .input_registry import QuestionMethodSet, ContractClassification, MethodAssignment

logger = logging. getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

COMPOSER_VERSION = "4.0.0-granular"

PHASE_DEFINITIONS:  dict[str, dict[str, Any]] = {
    "phase_A_construction": {
        "phase_id": "phase_A_construction",
        "phase_name": "Construction",
        "level_prefix":  "N1",
        "level_name": "Base Empírica",
        "epistemology": "Empirismo positivista",
        "output_type": "FACT",
        "fusion_behavior":  "additive",
        "dependencies": (),
        "output_target":  "raw_facts",
        "description": "Empirical observation layer - direct extraction without interpretation",
    },
    "phase_B_computation": {
        "phase_id": "phase_B_computation",
        "phase_name": "Computation",
        "level_prefix": "N2",
        "level_name": "Procesamiento Inferencial",
        "epistemology": "Bayesianismo subjetivista",
        "output_type": "PARAMETER",
        "fusion_behavior":  "multiplicative",
        "dependencies": ("phase_A_construction",),
        "output_target": "inferences",
        "description": "Inferential analysis layer - transformation into analytical constructs",
    },
    "phase_C_litigation": {
        "phase_id": "phase_C_litigation",
        "phase_name": "Litigation",
        "level_prefix":  "N3",
        "level_name": "Auditoría y Robustez",
        "epistemology": "Falsacionismo popperiano",
        "output_type": "CONSTRAINT",
        "fusion_behavior":  "gate",
        "dependencies": ("phase_A_construction", "phase_B_computation"),
        "output_target": "audit_results",
        "description":  "Audit layer - attempt to 'break' results.  Acts as VETO GATE.",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# DATACLASSES INMUTABLES
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class PhaseMetadata:
    """
    Metadata de una fase de ejecución.
    
    Captura información estructural sobre una fase específica
    de la cadena epistémica. 
    """
    phase_id:  str
    phase_name: str
    level_prefix: str
    level_name: str
    epistemology: str
    output_type: str
    fusion_behavior: str
    method_count: int
    dependencies: tuple[str, ...]
    output_target: str

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return {
            "phase_id": self.phase_id,
            "phase_name":  self.phase_name,
            "level_prefix": self.level_prefix,
            "level_name": self.level_name,
            "epistemology": self.epistemology,
            "output_type": self.output_type,
            "fusion_behavior": self.fusion_behavior,
            "method_count": self. method_count,
            "dependencies": list(self.dependencies),
            "output_target": self.output_target,
        }


@dataclass(frozen=True)
class EpistemicChain:
    """
    Cadena epistémica ordenada e inmutable.
    
    Representa la secuencia completa de métodos expandidos para una pregunta,
    organizados por fase epistémica (N1 → N2 → N3).
    
    INVARIANTES:
    - El orden de métodos es EXACTAMENTE el del input
    - No hay fusión implícita entre métodos
    - Cada método mantiene su identidad discreta
    - Las fases están estrictamente ordenadas:  A (N1) → B (N2) → C (N3)
    - Inmutable después de construcción (frozen=True)
    """
    # Identificación
    question_id: str
    contract_type_code: str
    contract_type_name: str
    contract_type_focus: str
    
    # Cadenas por fase (orden preservado, inmutables)
    phase_a_chain: tuple  # tuple[ExpandedMethodUnit, ...]
    phase_b_chain: tuple  # tuple[ExpandedMethodUnit, ...]
    phase_c_chain: tuple  # tuple[ExpandedMethodUnit, ...]
    
    # Metadata de fases
    phase_a_metadata: PhaseMetadata
    phase_b_metadata: PhaseMetadata
    phase_c_metadata: PhaseMetadata
    
    # Metadata de composición
    total_methods: int
    composition_timestamp: str
    composer_version: str
    
    # Evidencia matemática preservada del input
    efficiency_score: float
    mathematical_evidence: dict = field(default_factory=dict)
    doctoral_justification: str = ""
    
    @property
    def full_chain_ordered(self) -> tuple: 
        """
        Retorna cadena completa en orden epistémico:  N1 → N2 → N3.
        
        El orden es semánticamente significativo y NO debe alterarse.
        """
        return self.phase_a_chain + self.phase_b_chain + self.phase_c_chain
    
    @property
    def n1_count(self) -> int:
        """Número de métodos N1-EMP en la cadena."""
        return len(self.phase_a_chain)
    
    @property
    def n2_count(self) -> int:
        """Número de métodos N2-INF en la cadena."""
        return len(self.phase_b_chain)
    
    @property
    def n3_count(self) -> int:
        """Número de métodos N3-AUD en la cadena."""
        return len(self.phase_c_chain)
    
    @property
    def all_method_ids(self) -> tuple[str, ...]:
        """Lista ordenada de todos los method_id para trazabilidad."""
        return tuple(m.method_id for m in self.full_chain_ordered)
    
    @property
    def phase_distribution(self) -> dict[str, int]:
        """Distribución de métodos por fase."""
        return {
            "N1": self.n1_count,
            "N2": self.n2_count,
            "N3": self.n3_count,
        }
    
    @property
    def contract_type(self) -> dict[str, str]:
        """Diccionario con información del tipo de contrato."""
        return {
            "code": self.contract_type_code,
            "name": self. contract_type_name,
            "focus": self.contract_type_focus,
        }
    
    def get_methods_by_class(self, class_name: str) -> tuple:
        """Retorna todos los métodos de una clase específica."""
        return tuple(
            m for m in self.full_chain_ordered 
            if m.class_name == class_name
        )
    
    def has_method(self, method_id: str) -> bool:
        """Verifica si un método específico está en la cadena."""
        return method_id in self.all_method_ids


@dataclass(frozen=True)
class CompositionReport:
    """
    Reporte de composición de cadena epistémica.
    
    Captura información sobre el proceso de composición para auditoría. 
    """
    question_id: str
    composition_timestamp: str
    input_method_count: dict
    output_method_count: dict
    validation_passed: bool
    validation_details: tuple[str, ...]
    composition_duration_ms: float

    def to_dict(self) -> dict[str, Any]: 
        """Serializa a diccionario."""
        return {
            "question_id": self.question_id,
            "composition_timestamp": self.composition_timestamp,
            "input_method_count": self.input_method_count,
            "output_method_count": self.output_method_count,
            "validation_passed": self.validation_passed,
            "validation_details": list(self.validation_details),
            "composition_duration_ms":  round(self.composition_duration_ms, 3),
        }


# ══════════════════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════


class ChainComposer:
    """
    Compone cadena epistémica desde unidades expandidas.
    
    RESPONSABILIDADES:
    1. Validar coherencia nivel-fase antes de composición
    2. Expandir métodos preservando orden EXACTO del input
    3. Ensamblar cadena inmutable con metadata completa
    4. Generar reportes de composición para auditoría
    
    PROPIEDADES GARANTIZADAS:
    - Preservación de orden:  NUNCA reordena métodos
    - Sin agrupación:  NUNCA agrupa por criterio no-dado
    - Fronteras explícitas:  Transiciones entre fases son declaradas
    - Determinista: Misma entrada → misma salida
    - Fail-fast: Falla inmediatamente ante violaciones
    
    INVARIANTES:
    - Un método N1 SOLO puede estar en phase_A
    - Un método N2 SOLO puede estar en phase_B
    - Un método N3 SOLO puede estar en phase_C
    - El orden dentro de cada fase es el orden del input
    
    USO: 
        composer = ChainComposer(expander)
        chain = composer.compose_chain(method_set, classification)
    """
    
    def __init__(self, expander: "MethodExpander"):
        """
        Inicializa el composer con un expander de métodos.
        
        Args:
            expander: MethodExpander configurado para expandir métodos
        
        Raises:
            ValueError: Si expander es None
        """
        if expander is None:
            raise ValueError("MethodExpander cannot be None")
        
        self.expander = expander
        self._composition_count = 0
        
        logger.info(f"ChainComposer initialized, version {COMPOSER_VERSION}")
    
    def compose_chain(
        self,
        method_set: "QuestionMethodSet",
        contract_classification: "ContractClassification",
    ) -> EpistemicChain:
        """
        Compone cadena epistémica para una pregunta.
        
        SECUENCIA DE OPERACIONES:
        1. Validar coherencia nivel-fase (prevención de E-001)
        2. Construir contexto de expansión desde classification
        3. Expandir métodos N1 (preservando orden exacto)
        4. Expandir métodos N2 (preservando orden exacto)
        5. Expandir métodos N3 (preservando orden exacto)
        6. Construir metadata de fases
        7. Ensamblar cadena inmutable
        8. Validar cadena post-composición
        
        Args:
            method_set: QuestionMethodSet con métodos asignados por fase
            contract_classification: ContractClassification con tipo y metadata
        
        Returns:
            EpistemicChain inmutable con cadena completa
        
        Raises: 
            ValueError: Si hay violación de coherencia nivel-fase
            RuntimeError: Si la expansión de algún método falla
        """
        start_time = time.perf_counter()
        
        question_id = method_set.question_id
        logger.info(f"Composing chain for {question_id}")
        
        # ══════════════════════════════════════════════════════════════════
        # PASO 1: Validación pre-composición (E-001)
        # ══════════════════════════════════════════════════════════════════
        self._validate_phase_level_coherence(method_set)
        logger.debug(f"  Phase-level coherence validated for {question_id}")
        
        # ══════════════════════════════════════════════════════════════════
        # PASO 2: Construir contexto de expansión
        # ══════════════════════════════════════════════════════════════════
        expansion_context = self._build_expansion_context(
            method_set, 
            contract_classification
        )
        logger.debug(f"  Expansion context built:  TYPE={expansion_context['type_code']}")
        
        # ══════════════════════════════════════════════════════════════════
        # PASO 3-5: Expandir cada fase PRESERVANDO ORDEN EXACTO
        # ══════════════════════════════════════════════════════════════════
        phase_a = self._expand_phase(
            methods=method_set.phase_a_N1,
            phase_id="phase_A_construction",
            context=expansion_context,
        )
        logger.debug(f"  Phase A expanded: {len(phase_a)} methods")
        
        phase_b = self._expand_phase(
            methods=method_set.phase_b_N2,
            phase_id="phase_B_computation",
            context=expansion_context,
        )
        logger.debug(f"  Phase B expanded:  {len(phase_b)} methods")
        
        phase_c = self._expand_phase(
            methods=method_set.phase_c_N3,
            phase_id="phase_C_litigation",
            context=expansion_context,
        )
        logger.debug(f"  Phase C expanded: {len(phase_c)} methods")
        
        # ══════════════════════════════════════════════════════════════════
        # PASO 6: Construir metadata de fases
        # ══════════════════════════════════════════════════════════════════
        phase_a_meta = self._build_phase_metadata("phase_A_construction", len(phase_a))
        phase_b_meta = self._build_phase_metadata("phase_B_computation", len(phase_b))
        phase_c_meta = self._build_phase_metadata("phase_C_litigation", len(phase_c))
        
        # ══════════════════════════════════════════════════════════════════
        # PASO 7: Ensamblar cadena inmutable
        # ══════════════════════════════════════════════════════════════════
        chain = EpistemicChain(
            question_id=question_id,
            contract_type_code=contract_classification.tipo_contrato["codigo"],
            contract_type_name=contract_classification.tipo_contrato["nombre"],
            contract_type_focus=contract_classification.tipo_contrato["foco"],
            phase_a_chain=phase_a,
            phase_b_chain=phase_b,
            phase_c_chain=phase_c,
            phase_a_metadata=phase_a_meta,
            phase_b_metadata=phase_b_meta,
            phase_c_metadata=phase_c_meta,
            total_methods=len(phase_a) + len(phase_b) + len(phase_c),
            composition_timestamp=self._get_timestamp(),
            composer_version=COMPOSER_VERSION,
            efficiency_score=method_set.efficiency_score,
            mathematical_evidence=dict(method_set.mathematical_evidence),
            doctoral_justification=method_set.doctoral_justification,
        )
        
        # ══════════════════════════════════════════════════════════════════
        # PASO 8: Validación post-composición
        # ══════════════════════════════════════════════════════════════════
        self._validate_composed_chain(chain, method_set)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self._composition_count += 1
        
        logger.info(
            f"Chain composed for {question_id}:  "
            f"{chain.total_methods} methods "
            f"(N1={chain.n1_count}, N2={chain.n2_count}, N3={chain.n3_count}) "
            f"in {elapsed_ms:.2f}ms"
        )
        
        return chain
    
    def compose_chain_with_report(
        self,
        method_set: "QuestionMethodSet",
        contract_classification: "ContractClassification",
    ) -> tuple[EpistemicChain, CompositionReport]:
        """
        Compone cadena y genera reporte de composición.
        
        Útil para auditoría y debugging. 
        
        Args:
            method_set: QuestionMethodSet con métodos asignados
            contract_classification: ContractClassification para contexto
        
        Returns: 
            Tupla de (EpistemicChain, CompositionReport)
        """
        start_time = time.perf_counter()
        
        # Capturar conteos de entrada
        input_counts = {
            "N1": len(method_set.phase_a_N1),
            "N2": len(method_set. phase_b_N2),
            "N3": len(method_set.phase_c_N3),
        }
        
        validation_details:  list[str] = []
        validation_passed = True
        
        try:
            self._validate_phase_level_coherence(method_set)
            validation_details.append("Phase-level coherence:  PASSED")
        except ValueError as e:
            validation_details.append(f"Phase-level coherence: FAILED - {e}")
            validation_passed = False
            raise
        
        # Composición
        chain = self.compose_chain(method_set, contract_classification)
        
        # Capturar conteos de salida
        output_counts = chain.phase_distribution
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Validaciones adicionales
        if input_counts == output_counts:
            validation_details.append("Method count preservation: PASSED")
        else:
            validation_details.append(
                f"Method count preservation:  MISMATCH "
                f"(input={input_counts}, output={output_counts})"
            )
            validation_passed = False
        
        report = CompositionReport(
            question_id=method_set. question_id,
            composition_timestamp=chain.composition_timestamp,
            input_method_count=input_counts,
            output_method_count=output_counts,
            validation_passed=validation_passed,
            validation_details=tuple(validation_details),
            composition_duration_ms=elapsed_ms,
        )
        
        return chain, report
    
    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS - VALIDACIÓN
    # ══════════════════════════════════════════════════════════════════════════
    
    def _validate_phase_level_coherence(
        self, 
        method_set: "QuestionMethodSet"
    ) -> None:
        """
        Valida que los métodos asignados a cada fase tengan el nivel correcto.
        
        REGLAS ESTRICTAS (sin excepciones):
        - phase_a_N1 → SOLO métodos con level que empiece con "N1"
        - phase_b_N2 → SOLO métodos con level que empiece con "N2"
        - phase_c_N3 → SOLO métodos con level que empiece con "N3"
        
        Esta validación previene el error E-001.
        
        Args:
            method_set: QuestionMethodSet a validar
        
        Raises:
            ValueError:  Si cualquier método viola la regla de coherencia
        """
        phase_checks = [
            ("phase_a_N1", "N1", method_set.phase_a_N1),
            ("phase_b_N2", "N2", method_set.phase_b_N2),
            ("phase_c_N3", "N3", method_set.phase_c_N3),
        ]
        
        violations:  list[str] = []
        
        for phase_name, expected_prefix, methods in phase_checks:
            for method in methods:
                if not method.level.startswith(expected_prefix):
                    violations.append(
                        f"  - {phase_name}: {method.full_id} has level '{method.level}' "
                        f"(expected {expected_prefix}-*)"
                    )
        
        if violations:
            error_report = "\n".join(violations)
            raise ValueError(
                f"HARD FAILURE (E-001): Phase-Level Coherence Violation\n"
                f"  Question: {method_set.question_id}\n"
                f"  Violations found:  {len(violations)}\n"
                f"\n"
                f"Details:\n"
                f"{error_report}\n"
                f"\n"
                f"ROOT CAUSE: method_sets_by_question. json contains methods "
                f"assigned to phases that don't match their epistemological level.\n"
                f"\n"
                f"CORRECTIVE ACTION:\n"
                f"  1. Open method_sets_by_question. json\n"
                f"  2. Find entry for '{method_set.question_id}'\n"
                f"  3. Move misplaced methods to correct phase arrays\n"
                f"  4. Re-run generator"
            )
    
    def _validate_composed_chain(
        self, 
        chain: EpistemicChain, 
        method_set: "QuestionMethodSet"
    ) -> None:
        """
        Validación post-composición de la cadena.
        
        Args:
            chain:  Cadena compuesta a validar
            method_set: QuestionMethodSet original para comparación
        
        Raises: 
            RuntimeError: Si la cadena no cumple invariantes
        """
        # Verificar conteo total
        expected_total = (
            len(method_set.phase_a_N1) + 
            len(method_set. phase_b_N2) + 
            len(method_set.phase_c_N3)
        )
        
        if chain.total_methods != expected_total:
            raise RuntimeError(
                f"Method count mismatch after composition:  "
                f"expected {expected_total}, got {chain.total_methods}"
            )
        
        # Verificar que efficiency_score se preservó
        if chain.efficiency_score != method_set.efficiency_score:
            raise RuntimeError(
                f"Efficiency score not preserved:  "
                f"expected {method_set.efficiency_score}, got {chain.efficiency_score}"
            )
        
        # Verificar que todos los métodos tienen method_id
        for i, method in enumerate(chain.full_chain_ordered):
            if not method.method_id:
                raise RuntimeError(
                    f"Method at index {i} has empty method_id"
                )
    
    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS - CONSTRUCCIÓN
    # ══════════════════════════════════════════════════════════════════════════
    
    def _build_expansion_context(
        self,
        method_set: "QuestionMethodSet",
        contract_classification: "ContractClassification",
    ) -> dict[str, Any]:
        """
        Construye contexto para expansión de métodos.
        
        Args:
            method_set: QuestionMethodSet con metadata
            contract_classification: ContractClassification con tipo
        
        Returns:
            Dict con contexto de expansión
        """
        return {
            "question_id": method_set.question_id,
            "type_code": contract_classification.tipo_contrato["codigo"],
            "type_name": contract_classification.tipo_contrato["nombre"],
            "type_focus": contract_classification.tipo_contrato["foco"],
            "fusion_strategy": method_set.contract_type. get("fusion_strategy", ""),
            "efficiency_score": method_set.efficiency_score,
        }
    
    def _expand_phase(
        self,
        methods: tuple,  # tuple[MethodAssignment, ...]
        phase_id: str,
        context: dict[str, Any],
    ) -> tuple:   # tuple[ExpandedMethodUnit, ...]
        """
        Expande todos los métodos de una fase. 
        
        CRÍTICO: Preserva el orden EXACTO de la tupla de entrada. 
        
        Args:
            methods: Tupla de métodos a expandir (orden preservado)
            phase_id:  ID de la fase para contexto
            context: Contexto de expansión
        
        Returns:
            Tupla de ExpandedMethodUnit (mismo orden que entrada)
        
        Raises:
            RuntimeError: Si la expansión de algún método falla
        """
        phase_context = {**context, "phase_id": phase_id}
        
        expanded:  list = []
        
        for idx, method in enumerate(methods):
            try:
                expanded_method = self.expander.expand_method(method, phase_context)
                expanded. append(expanded_method)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to expand method at index {idx} in {phase_id}: "
                    f"{method.full_id}\n"
                    f"Error: {e}"
                ) from e
        
        return tuple(expanded)
    
    def _build_phase_metadata(
        self, 
        phase_id: str, 
        method_count: int
    ) -> PhaseMetadata:
        """
        Construye metadata para una fase específica.
        
        Args:
            phase_id: ID de la fase
            method_count:  Número de métodos en la fase
        
        Returns:
            PhaseMetadata inmutable
        """
        phase_def = PHASE_DEFINITIONS[phase_id]
        
        return PhaseMetadata(
            phase_id=phase_def["phase_id"],
            phase_name=phase_def["phase_name"],
            level_prefix=phase_def["level_prefix"],
            level_name=phase_def["level_name"],
            epistemology=phase_def["epistemology"],
            output_type=phase_def["output_type"],
            fusion_behavior=phase_def["fusion_behavior"],
            method_count=method_count,
            dependencies=phase_def["dependencies"],
            output_target=phase_def["output_target"],
        )
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp ISO 8601 con timezone UTC."""
        return datetime.now(timezone.utc).isoformat()
    
    # ══════════════════════════════════════════════════════════════════════════
    # PROPIEDADES PÚBLICAS
    # ══════════════════════════════════════════════════════════════════════════
    
    @property
    def composition_count(self) -> int:
        """Número de cadenas compuestas por esta instancia."""
        return self._composition_count
    
    @property
    def version(self) -> str:
        """Versión del composer."""
        return COMPOSER_VERSION