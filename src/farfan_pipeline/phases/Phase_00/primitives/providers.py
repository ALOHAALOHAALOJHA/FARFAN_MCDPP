"""
Providers and Factories for Phase 0 primitives.

This module contains the foundational resource providers and factories
used by the bootstrap process.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import structlog

from farfan_pipeline.phases.Phase_00.phase0_10_00_paths import DATA_DIR
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption import (
    AccessLevel,
    get_access_audit,
)

# Import CanonicalQuestionnaire from canonical source to avoid circular import
try:
    from canonic_questionnaire_central import CanonicalQuestionnaire
except ImportError:
    # Fallback: define minimal protocol for type hints
    class CanonicalQuestionnaire(Protocol):  # type: ignore[no-redef]
        data: dict
        dimensions: dict
        policy_areas: dict
        micro_questions: list
        sha256: str

logger = structlog.get_logger(__name__)


@dataclass
class QuestionnaireResourceProvider:
    """
    Proveedor de recursos del cuestionario con acceso scoped.

    NIVEL 2: Acceso Parcial Recurrente
    PROVEEDOR: AnalysisPipelineFactory (Nivel 1)
    CONSUMIDORES: Orchestrator, ReportAssembler, SISAS components

    Este provider NO hace I/O. Recibe CanonicalQuestionnaire ya cargado
    y expone métodos que retornan subconjuntos específicos.
    """

    questionnaire_path: Path | None = None
    data_dir: Path = field(default_factory=lambda: DATA_DIR)
    _canonical: CanonicalQuestionnaire | None = field(default=None, repr=False)

    # === MÉTODOS DE INICIALIZACIÓN ===

    def initialize(self, canonical: CanonicalQuestionnaire) -> None:
        """
        Inicializa el provider con el cuestionario canónico.
        DEBE ser llamado por Factory después de load_questionnaire().
        """
        object.__setattr__(self, "_canonical", canonical)

    @property
    def is_initialized(self) -> bool:
        """Verifica si el provider fue inicializado."""
        return self._canonical is not None

    def _require_initialized(self) -> CanonicalQuestionnaire:
        """Guarda que lanza error si no está inicializado."""
        if self._canonical is None:
            raise RuntimeError(
                "QuestionnaireResourceProvider not initialized. "
                "Call initialize() with CanonicalQuestionnaire first."
            )
        return self._canonical

    # === MÉTODOS DE ACCESO SCOPED (NIVEL 2) ===

    def get_data(self) -> dict[str, Any]:
        """
        Retorna el contenido completo del cuestionario.
        SCOPE: Total (pero solo lectura, no I/O)
        USO: ReportAssembler para metadatos
        """
        return dict(self._require_initialized().data)

    def get_dimensions(self) -> dict[str, Any]:
        """
        SCOPE: Solo canonical_notation.dimensions (6 items)
        """
        result = self._require_initialized().dimensions
        get_access_audit().record_access(
            level=AccessLevel.ORCHESTRATOR,
            accessor_module=__name__,
            accessor_class="QuestionnaireResourceProvider",
            accessor_method="get_dimensions",
            accessed_block="dimensions",
            accessed_keys=list(result.keys()),
        )
        return result

    def get_policy_areas(self) -> dict[str, Any]:
        """
        SCOPE: Solo canonical_notation.policy_areas (10 items)
        """
        result = self._require_initialized().policy_areas
        get_access_audit().record_access(
            level=AccessLevel.ORCHESTRATOR,
            accessor_module=__name__,
            accessor_class="QuestionnaireResourceProvider",
            accessor_method="get_policy_areas",
            accessed_block="policy_areas",
            accessed_keys=list(result.keys()),
        )
        return result

    def get_micro_questions_for_policy_area(self, pa_id: str) -> list[dict[str, Any]]:
        """
        SCOPE: Micro preguntas filtradas por policy_area_id
        Ejemplo: get_micro_questions_for_policy_area("PA01") → 30 preguntas
        """
        canonical = self._require_initialized()
        result = [q for q in canonical.micro_questions if q.get("policy_area_id") == pa_id]
        get_access_audit().record_access(
            level=AccessLevel.ORCHESTRATOR,
            accessor_module=__name__,
            accessor_class="QuestionnaireResourceProvider",
            accessor_method="get_micro_questions_for_policy_area",
            accessed_block="micro_questions",
            accessed_keys=[q.get("question_id", "") for q in result],
            scope_filter=f"policy_area_id={pa_id}",
        )
        return result

    def get_micro_questions_for_dimension(self, dim_id: str) -> list[dict[str, Any]]:
        """
        SCOPE: Micro preguntas filtradas por dimension_id
        Ejemplo: get_micro_questions_for_dimension("DIM01") → 50 preguntas
        """
        canonical = self._require_initialized()
        result = [q for q in canonical.micro_questions if q.get("dimension_id") == dim_id]
        get_access_audit().record_access(
            level=AccessLevel.ORCHESTRATOR,
            accessor_module=__name__,
            accessor_class="QuestionnaireResourceProvider",
            accessor_method="get_micro_questions_for_dimension",
            accessed_block="micro_questions",
            accessed_keys=[q.get("question_id", "") for q in result],
            scope_filter=f"dimension_id={dim_id}",
        )
        return result

    def get_patterns_by_question(self, question_id: str) -> list[dict[str, Any]]:
        """
        SCOPE: Patrones de una micro pregunta específica
        USO: ReportAssembler para enrichment de respuestas
        """
        canonical = self._require_initialized()
        result = []
        for q in canonical.micro_questions:
            if q.get("question_id") == question_id:
                result = list(q.get("patterns", []))
                break
        pattern_ids = [p.get("id", f"idx_{i}") for i, p in enumerate(result)]
        get_access_audit().record_access(
            level=AccessLevel.ORCHESTRATOR,
            accessor_module=__name__,
            accessor_class="QuestionnaireResourceProvider",
            accessor_method="get_patterns_by_question",
            accessed_block="patterns",
            accessed_keys=pattern_ids,
            scope_filter=f"question_id={question_id}",
        )
        return result

    def get_expected_elements_for_question(self, question_id: str) -> list[dict[str, Any]]:
        """
        SCOPE: Elementos esperados de una micro pregunta específica
        USO: EvidenceValidator para verificación
        """
        canonical = self._require_initialized()
        result = []
        for q in canonical.micro_questions:
            if q.get("question_id") == question_id:
                result = list(q.get("expected_elements", []))
                break
        element_types = [e.get("type", f"idx_{i}") for i, e in enumerate(result)]
        get_access_audit().record_access(
            level=AccessLevel.ORCHESTRATOR,
            accessor_module=__name__,
            accessor_class="QuestionnaireResourceProvider",
            accessor_method="get_expected_elements_for_question",
            accessed_block="expected_elements",
            accessed_keys=element_types,
            scope_filter=f"question_id={question_id}",
        )
        return result

    def get_failure_contract_for_question(self, question_id: str) -> dict[str, Any] | None:
        """
        SCOPE: Contrato de falla de una micro pregunta específica
        USO: EvidenceValidator para abort conditions
        """
        canonical = self._require_initialized()
        result = None
        for q in canonical.micro_questions:
            if q.get("question_id") == question_id:
                result = q.get("failure_contract")
                break
        get_access_audit().record_access(
            level=AccessLevel.ORCHESTRATOR,
            accessor_module=__name__,
            accessor_class="QuestionnaireResourceProvider",
            accessor_method="get_failure_contract_for_question",
            accessed_block="failure_contract",
            accessed_keys=[question_id] if result else [],
            scope_filter=f"question_id={question_id}",
        )
        return result

    @property
    def source_hash(self) -> str:
        """Hash SHA256 del cuestionario para trazabilidad."""
        if self._canonical is None:
            return ""
        return self._canonical.sha256


@dataclass
class CoreModuleFactory:
    """Stub factory for core module instantiation.
    
    Note: This is a minimal stub. The full implementation is in
    AnalysisPipelineFactory (phase2_10_00_factory.py).
    """
    data_dir: Path | None = None
