from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields


@dataclass(frozen=True)
class Rulebook:
    """Reglas centralizadas (versionables) para clasificación.

    Esto reduce hardcoding disperso y hace auditable el conjunto de señales.
    """

    # Signals (shared)
    veto_signals: tuple[str, ...] = (
        "invalid",
        "reject",
        "block",
        "veto",
        "fail",
        "suppress",
        "nullify",
        "discard",
        "exclude",
        "confidence_multiplier",
        "reduce_confidence",
        "downgrade",
        "invalidate",
        "filters out",
        "contradiction",
        "inconsistent",
    )

    derived_signals: tuple[str, ...] = (
        "score",
        "probability",
        "confidence",
        "likelihood",
        "embedding",
        "vector",
        "similarity",
        "coherence",
        "aggregate",
        "summary",
        "computed",
        "calculated",
        "inferred",
        "predicted",
        "estimated",
        "normalized",
        "bayesian",
        "posterior",
        "prior",
        "credible",
        "distribution",
        "ranking",
        "rank",
        "cluster",
        "classification",
    )

    literal_signals: tuple[str, ...] = (
        "extracted from",
        "parsed from",
        "found in document",
        "verbatim",
        "raw text",
        "original",
        "literal",
    )

    n4_name_signals: tuple[str, ...] = (
        "generate_report",
        "generate_executive_report",
        "export_summary_report",
        "generate_summary",
        "generate_pdq_report",
        "generate_recommendations",
        "_generate_scenario_narrative",
        "_generate_narrative",
        "render",
        "compose",
        "finalize",
        "write",
        "produce",
    )

    n4_doc_signals: tuple[str, ...] = (
        "executive report",
        "reporte ejecutivo",
        "human_answer",
        "veredicto",
        "respuesta",
        "narrative",
        "synthesis",
        "síntesis",
        "markdown",
        "summary",
        "summarize",
        "recommendations",
        "recomendaciones",
    )


DEFAULT_RULEBOOK = Rulebook()


def compute_rulebook_hash(rulebook: Rulebook = DEFAULT_RULEBOOK) -> str:
    """Hash SHA-256 del rulebook para detectar cambios en reglas."""
    payload = {f.name: getattr(rulebook, f.name) for f in fields(rulebook)}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
