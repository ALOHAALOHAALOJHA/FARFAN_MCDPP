"""Questionnaire Access Audit - Canonical Location

Migrated from _deprecated/signal_consumption.py per Phase 5 remediation.

CANONICAL MODULE for questionnaire access tracking and auditing.

Key Features:
- Three-tier access level tracking (Factory, Orchestrator, Consumer)
- Immutable access records
- Utilization metrics
- Architectural violation detection
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, ClassVar

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Nivel de acceso al cuestionario según arquitectura de 3 niveles."""

    FACTORY = 1  # I/O total - Solo AnalysisPipelineFactory
    ORCHESTRATOR = 2  # Parcial recurrente - SISAS, ResourceProvider
    CONSUMER = 3  # Granular scoped - Ejecutores, Evidence*


@dataclass(frozen=True)
class AccessRecord:
    """Registro inmutable de un acceso al cuestionario."""

    timestamp: str
    level: AccessLevel
    accessor_module: str  # __name__ del módulo
    accessor_class: str  # Nombre de clase
    accessor_method: str  # Nombre de método
    accessed_block: str  # "dimensions", "micro_questions", "patterns", etc.
    accessed_keys: tuple[str, ...]  # IDs específicos (inmutable)
    scope_filter: str | None = None  # Filtro aplicado

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level.name,
            "accessor": f"{self.accessor_module}.{self.accessor_class}.{self.accessor_method}",
            "block": self.accessed_block,
            "keys": list(self.accessed_keys),
            "scope_filter": self.scope_filter,
        }


@dataclass
class QuestionnaireAccessAudit:
    """
    Auditor de acceso al cuestionario con métricas de utilización.

    PROPÓSITO:
    1. Medir qué porción del cuestionario se consume
    2. Detectar violaciones de nivel arquitectónico
    3. Identificar patrones/preguntas no utilizados
    4. Generar reporte de trazabilidad

    INVARIANTES DEL MONOLITO:
    - 300 micro preguntas (6 dims × 5 preguntas × 10 PAs)
    - 4 meso preguntas
    - 1 macro pregunta
    - 6 dimensiones (DIM01-DIM06)
    - 10 policy areas (PA01-PA10)
    """

    # Constantes del monolito
    TOTAL_MICRO_QUESTIONS: ClassVar[int] = 300
    TOTAL_MESO_QUESTIONS: ClassVar[int] = 4
    TOTAL_MACRO_QUESTIONS: ClassVar[int] = 1
    TOTAL_DIMENSIONS: ClassVar[int] = 6
    TOTAL_POLICY_AREAS: ClassVar[int] = 10

    # Estado mutable (privado)
    _access_log: list[AccessRecord] = field(default_factory=list)
    _accessed_questions: set[str] = field(default_factory=set)
    _accessed_patterns: set[str] = field(default_factory=set)
    _accessed_elements: set[str] = field(default_factory=set)
    _accessed_policy_areas: set[str] = field(default_factory=set)
    _accessed_dimensions: set[str] = field(default_factory=set)
    _violations: list[dict[str, Any]] = field(default_factory=list)

    def record_access(
        self,
        level: AccessLevel,
        accessor_module: str,
        accessor_class: str,
        accessor_method: str,
        accessed_block: str,
        accessed_keys: Sequence[str],
        scope_filter: str | None = None,
    ) -> None:
        """Registra un acceso al cuestionario."""
        record = AccessRecord(
            timestamp=datetime.now(UTC).isoformat(),
            level=level,
            accessor_module=accessor_module,
            accessor_class=accessor_class,
            accessor_method=accessor_method,
            accessed_block=accessed_block,
            accessed_keys=tuple(accessed_keys),
            scope_filter=scope_filter,
        )
        self._access_log.append(record)

        # Actualizar conjuntos de tracking
        if accessed_block == "micro_questions":
            self._accessed_questions.update(accessed_keys)
        elif accessed_block == "patterns":
            self._accessed_patterns.update(accessed_keys)
        elif accessed_block == "expected_elements":
            self._accessed_elements.update(accessed_keys)
        elif accessed_block == "policy_areas":
            self._accessed_policy_areas.update(accessed_keys)
        elif accessed_block == "dimensions":
            self._accessed_dimensions.update(accessed_keys)

    def record_violation(
        self,
        violation_type: str,
        accessor: str,
        expected_level: AccessLevel,
        actual_level: AccessLevel,
        details: str,
    ) -> None:
        """Registra una violación de nivel arquitectónico."""
        self._violations.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "type": violation_type,
                "accessor": accessor,
                "expected_level": expected_level.name,
                "actual_level": actual_level.name,
                "details": details,
            }
        )

    def get_utilization_report(self) -> dict[str, Any]:
        """Genera reporte de utilización del cuestionario."""
        return {
            "micro_questions": {
                "accessed": len(self._accessed_questions),
                "total": self.TOTAL_MICRO_QUESTIONS,
                "percentage": round(
                    len(self._accessed_questions) / self.TOTAL_MICRO_QUESTIONS * 100, 2
                ),
                "ids": sorted(self._accessed_questions),
            },
            "policy_areas": {
                "accessed": len(self._accessed_policy_areas),
                "total": self.TOTAL_POLICY_AREAS,
                "percentage": round(
                    len(self._accessed_policy_areas) / self.TOTAL_POLICY_AREAS * 100, 2
                ),
                "ids": sorted(self._accessed_policy_areas),
            },
            "dimensions": {
                "accessed": len(self._accessed_dimensions),
                "total": self.TOTAL_DIMENSIONS,
                "percentage": round(
                    len(self._accessed_dimensions) / self.TOTAL_DIMENSIONS * 100, 2
                ),
                "ids": sorted(self._accessed_dimensions),
            },
            "patterns_accessed": len(self._accessed_patterns),
            "elements_accessed": len(self._accessed_elements),
            "total_access_events": len(self._access_log),
            "access_by_level": self._count_by_level(),
            "violations_count": len(self._violations),
            "violations": self._violations,
        }

    def _count_by_level(self) -> dict[str, int]:
        """Cuenta accesos por nivel arquitectónico."""
        counts = {level.name: 0 for level in AccessLevel}
        for record in self._access_log:
            counts[record.level.name] += 1
        return counts

    def export_audit_log(self) -> list[dict[str, Any]]:
        """Exporta log de auditoría completo."""
        return [record.to_dict() for record in self._access_log]

    def reset(self) -> None:
        """Resetea el auditor (solo para testing)."""
        self._access_log.clear()
        self._accessed_questions.clear()
        self._accessed_patterns.clear()
        self._accessed_elements.clear()
        self._accessed_policy_areas.clear()
        self._accessed_dimensions.clear()
        self._violations.clear()


# Singleton global para auditoría (inicializado por Factory)
_global_access_audit: QuestionnaireAccessAudit | None = None


def get_access_audit() -> QuestionnaireAccessAudit:
    """Obtiene el auditor global de acceso al cuestionario."""
    global _global_access_audit
    if _global_access_audit is None:
        _global_access_audit = QuestionnaireAccessAudit()
    return _global_access_audit


def reset_access_audit() -> None:
    """Resetea el auditor global (solo para testing)."""
    global _global_access_audit
    if _global_access_audit is not None:
        _global_access_audit.reset()
    _global_access_audit = None
