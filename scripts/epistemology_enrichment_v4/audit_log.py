"""Sistema de logging estructurado para auditoría forense.

Cada decisión registra:
- Reglas evaluadas (matched + anti-matched)
- Degradaciones con justificación
- Warnings de inconsistencia
- Fingerprint de entrada/salida

Versión: 2.1.0 - Integración con enricher.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RuleEvaluation:
    """Evaluación de una regla individual."""

    rule_id: str
    rule_description: str
    matched: bool
    signals_checked: tuple[str, ...]
    signals_found: tuple[str, ...]
    contribution: str  # "triggered_level", "contributed_epistemology", "no_effect"


@dataclass
class DegradationWarning:
    """Registro de degradación de nivel."""

    original_level: str
    degraded_to: str
    reason: str
    method_id: str
    class_name: str


@dataclass
class MethodDecisionLog:
    """Log completo de decisión de método."""

    method_id: str
    class_name: str
    original_level: str
    final_level: str
    was_degraded: bool
    degradation_reason: str | None
    epistemology: str
    matched_signals: tuple[str, ...]
    decision_path: str
    invariant_violations: list[dict[str, Any]]
    input_hash: str  # SHA256 del blob de entrada


@dataclass
class ClassDecisionLog:
    """Log completo de decisión de clase."""

    class_name: str
    file_path: str
    final_level: str
    final_epistemology: str
    method_count: int
    decision_record: Any  # ClassDecisionRecord o None
    level_rationale: str
    epistemology_rationale: str


@dataclass
class EnrichmentSession:
    """Sesión completa de enriquecimiento con trazabilidad forense."""

    session_id: str
    started_at: str
    completed_at: str | None = None
    input_file_hash: str = ""
    output_file_hash: str = ""
    rulebook_hash: str = ""
    pipeline_version: str = ""
    method_logs: list[MethodDecisionLog] = field(default_factory=list)
    class_logs: list[ClassDecisionLog] = field(default_factory=list)
    degradations: list[DegradationWarning] = field(default_factory=list)
    invariant_violations: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_degradation(self, degradation: DegradationWarning) -> None:
        self.degradations.append(degradation)
        self.warnings.append(
            f"DEGRADATION: {degradation.class_name}.{degradation.method_id} "
            f"{degradation.original_level} → {degradation.degraded_to}: {degradation.reason}"
        )

    def add_invariant_violation(self, violation: dict[str, Any]) -> None:
        self.invariant_violations.append(violation)
        self.warnings.append(f"INVARIANT_VIOLATION: {json.dumps(violation)}")

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    @staticmethod
    def hash_blob(blob: str) -> str:
        """SHA256 de un blob de texto (primeros 16 chars)."""
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

    def to_manifest(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "input_file_hash": self.input_file_hash,
            "output_file_hash": self.output_file_hash,
            "rulebook_hash": self.rulebook_hash,
            "pipeline_version": self.pipeline_version,
            "total_methods_processed": len(self.method_logs),
            "total_classes_processed": len(self.class_logs),
            "total_degradations": len(self.degradations),
            "total_invariant_violations": len(self.invariant_violations),
            "degradations": [
                {
                    "method_id": d.method_id,
                    "class_name": d.class_name,
                    "original_level": d.original_level,
                    "degraded_to": d.degraded_to,
                    "reason": d.reason,
                }
                for d in self.degradations
            ],
            "invariant_violations": self.invariant_violations,
            "warnings": self.warnings,
        }


def generate_session_id() -> str:
    """Genera ID único de sesión basado en timestamp."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    return f"enrich_session_{ts}"


def hash_blob(blob: str) -> str:
    """SHA256 de un blob de texto."""
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def hash_data(data: dict[str, Any]) -> str:
    """SHA256 de datos estructurados (canonicalizados)."""
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# Singleton de sesión activa (para logging durante enriquecimiento)
_active_session: EnrichmentSession | None = None


def start_session(
    input_data: dict[str, Any] | None = None,
    input_file_hash: str = "",
    rulebook_hash: str = "",
    pipeline_version: str = "",
) -> EnrichmentSession:
    """Inicia una nueva sesión de enriquecimiento.

    Args:
        input_data: Datos de entrada (se calcula hash si se proporciona).
        input_file_hash: Hash del archivo de entrada (si ya se calculó).
        rulebook_hash: Hash del rulebook.
        pipeline_version: Versión del pipeline.

    Returns:
        Nueva sesión de enriquecimiento.
    """
    global _active_session

    if input_data and not input_file_hash:
        input_file_hash = hash_data(input_data)

    _active_session = EnrichmentSession(
        session_id=generate_session_id(),
        started_at=datetime.now(timezone.utc).isoformat(),
        input_file_hash=input_file_hash,
        rulebook_hash=rulebook_hash,
        pipeline_version=pipeline_version,
    )
    return _active_session


def get_session() -> EnrichmentSession | None:
    return _active_session


def end_session(output_file_hash: str) -> EnrichmentSession:
    global _active_session
    if _active_session is None:
        raise RuntimeError("No active enrichment session")
    _active_session.completed_at = datetime.now(timezone.utc).isoformat()
    _active_session.output_file_hash = output_file_hash
    session = _active_session
    _active_session = None
    return session
