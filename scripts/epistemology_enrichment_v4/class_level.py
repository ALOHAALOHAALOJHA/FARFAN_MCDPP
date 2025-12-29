"""Inferencia de nivel y epistemología a nivel de clase.

Diseño:
- Cada decisión deja evidencia explícita (ClassDecisionRecord).
- Ponderación por criticidad (N3 > N2 > N1 para conflictos de dominio).
- Overrides contextuales por nombre de clase y ruta de archivo.
- Desempates justificados y documentados.
- Fail-loud ante ambigüedad no resuelta.

Versión: 2.0.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .utils import contains_any, norm_text_for_match


# ---------------------------------------------------------------------------
# Pesos de criticidad por nivel (más alto = más crítico en conflicto)
# ---------------------------------------------------------------------------
LEVEL_CRITICALITY: dict[str, int] = {
    "N4-SYN": 40,  # síntesis terminal prevalece
    "N3-AUD": 30,  # auditoría/veto es crítico
    "N2-INF": 20,  # inferencia
    "N1-EMP": 10,  # empírico base
    "INFRASTRUCTURE": 0,
}


# ---------------------------------------------------------------------------
# Overrides contextuales por patrón en nombre de clase o ruta
# ---------------------------------------------------------------------------
CLASS_NAME_OVERRIDES: tuple[tuple[str, str], ...] = (
    (r"(?i)validator", "N3-AUD"),
    (r"(?i)auditor", "N3-AUD"),
    (r"(?i)checker", "N3-AUD"),
    (r"(?i)verifier", "N3-AUD"),
    (r"(?i)synthesizer", "N4-SYN"),
    (r"(?i)composer", "N4-SYN"),
    (r"(?i)reporter", "N4-SYN"),
    (r"(?i)extractor", "N1-EMP"),
    (r"(?i)parser", "N1-EMP"),
    (r"(?i)loader", "INFRASTRUCTURE"),
    (r"(?i)config", "INFRASTRUCTURE"),
    (r"(?i)registry", "INFRASTRUCTURE"),
    (r"(?i)factory", "INFRASTRUCTURE"),
    (r"(?i)helper", "INFRASTRUCTURE"),
    (r"(?i)util", "INFRASTRUCTURE"),
)

FILE_PATH_OVERRIDES: tuple[tuple[str, str], ...] = (
    (r"(?i)/validators?/", "N3-AUD"),
    (r"(?i)/auditors?/", "N3-AUD"),
    (r"(?i)/synthesis/", "N4-SYN"),
    (r"(?i)/reports?/", "N4-SYN"),
    (r"(?i)/extractors?/", "N1-EMP"),
    (r"(?i)/parsers?/", "N1-EMP"),
    (r"(?i)/infrastructure/", "INFRASTRUCTURE"),
    (r"(?i)/utils?/", "INFRASTRUCTURE"),
    (r"(?i)/helpers?/", "INFRASTRUCTURE"),
)

PROTOCOL_PATTERNS: tuple[str, ...] = (
    r"\bprotocol\b",
    r"\bcontract\b",
    r"\binterface\b",
    r"Protocol$",
    r"Contract$",
    r"Interface$",
)


# ---------------------------------------------------------------------------
# Registro de decisión (auditable)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ClassDecisionRecord:
    """Registro completo de la decisión de nivel/epistemología de clase."""

    class_name: str
    file_path: str
    inferred_level: str
    inferred_epistemology: str
    method_level_counts: dict[str, int]
    method_epistemology_counts: dict[str, int]
    override_applied: str | None
    override_source: str | None  # "class_name" | "file_path" | None
    tie_resolution: str | None
    decision_rationale: str
    weighted_score: float


# ---------------------------------------------------------------------------
# Inferencia de nivel de clase
# ---------------------------------------------------------------------------
def infer_class_level(
    method_levels: list[str],
    method_names: list[str],
    class_name: str = "",
    file_path: str = "",
) -> tuple[str, ClassDecisionRecord]:
    """Infiere el nivel epistemológico de una clase.

    Reglas (en orden de precedencia):
    1. Override por nombre de clase (patrones en CLASS_NAME_OVERRIDES).
    2. Override por ruta de archivo (patrones en FILE_PATH_OVERRIDES).
    3. Ponderación por criticidad si hay métodos significativos.
    4. Desempate por criticidad máxima (no arbitrario).
    5. Default a INFRASTRUCTURE si no hay métodos significativos.
    """

    meaningful = [lvl for lvl in method_levels if lvl in LEVEL_CRITICALITY and lvl != "INFRASTRUCTURE"]
    counts = {lvl: method_levels.count(lvl) for lvl in LEVEL_CRITICALITY}

    # --- Override por nombre de clase ---
    for pattern, forced_level in CLASS_NAME_OVERRIDES:
        if re.search(pattern, class_name):
            return forced_level, ClassDecisionRecord(
                class_name=class_name,
                file_path=file_path,
                inferred_level=forced_level,
                inferred_epistemology="",  # se resuelve después
                method_level_counts=counts,
                method_epistemology_counts={},
                override_applied=forced_level,
                override_source="class_name",
                tie_resolution=None,
                decision_rationale=f"Override por patrón en nombre de clase: {pattern!r} → {forced_level}",
                weighted_score=0.0,
            )

    # --- Override por ruta de archivo ---
    for pattern, forced_level in FILE_PATH_OVERRIDES:
        if re.search(pattern, file_path):
            return forced_level, ClassDecisionRecord(
                class_name=class_name,
                file_path=file_path,
                inferred_level=forced_level,
                inferred_epistemology="",
                method_level_counts=counts,
                method_epistemology_counts={},
                override_applied=forced_level,
                override_source="file_path",
                tie_resolution=None,
                decision_rationale=f"Override por patrón en ruta: {pattern!r} → {forced_level}",
                weighted_score=0.0,
            )

    # --- Sin métodos significativos ---
    if not meaningful:
        rationale = (
            "Sin métodos significativos (solo INFRASTRUCTURE o vacío). "
            f"Nombres de métodos: {method_names!r}"
        )
        return "INFRASTRUCTURE", ClassDecisionRecord(
            class_name=class_name,
            file_path=file_path,
            inferred_level="INFRASTRUCTURE",
            inferred_epistemology="NONE",
            method_level_counts=counts,
            method_epistemology_counts={},
            override_applied=None,
            override_source=None,
            tie_resolution=None,
            decision_rationale=rationale,
            weighted_score=0.0,
        )

    # --- Ponderación por criticidad ---
    weighted_scores: dict[str, float] = {}
    total_meaningful = len(meaningful)
    for lvl in ["N1-EMP", "N2-INF", "N3-AUD", "N4-SYN"]:
        count = counts.get(lvl, 0)
        if count > 0:
            proportion = count / total_meaningful
            criticality = LEVEL_CRITICALITY[lvl]
            weighted_scores[lvl] = proportion * criticality

    if not weighted_scores:
        return "INFRASTRUCTURE", ClassDecisionRecord(
            class_name=class_name,
            file_path=file_path,
            inferred_level="INFRASTRUCTURE",
            inferred_epistemology="NONE",
            method_level_counts=counts,
            method_epistemology_counts={},
            override_applied=None,
            override_source=None,
            tie_resolution=None,
            decision_rationale="weighted_scores vacío tras filtrado",
            weighted_score=0.0,
        )

    max_score = max(weighted_scores.values())
    winners = [lvl for lvl, sc in weighted_scores.items() if sc == max_score]

    # --- Desempate por criticidad máxima ---
    if len(winners) == 1:
        winner = winners[0]
        tie_resolution = None
        rationale = (
            f"Ganador único por ponderación: {winner} "
            f"(score={max_score:.3f}, counts={counts})"
        )
    else:
        # Desempate: nivel de mayor criticidad intrínseca
        winner = max(winners, key=lambda x: LEVEL_CRITICALITY[x])
        tie_resolution = f"Empate entre {winners} resuelto por criticidad máxima → {winner}"
        rationale = (
            f"Empate resuelto: {winners} → {winner} "
            f"(criticality={LEVEL_CRITICALITY[winner]}, counts={counts})"
        )

    return winner, ClassDecisionRecord(
        class_name=class_name,
        file_path=file_path,
        inferred_level=winner,
        inferred_epistemology="",
        method_level_counts=counts,
        method_epistemology_counts={},
        override_applied=None,
        override_source=None,
        tie_resolution=tie_resolution,
        decision_rationale=rationale,
        weighted_score=max_score,
    )


# ---------------------------------------------------------------------------
# Inferencia de epistemología de clase
# ---------------------------------------------------------------------------
EPISTEMOLOGY_PRIORITY: dict[str, int] = {
    "CRITICAL_REFLEXIVE": 50,
    "POPPERIAN_FALSIFICATIONIST": 40,
    "BAYESIAN_PROBABILISTIC": 30,
    "CAUSAL_MECHANISTIC": 20,
    "DETERMINISTIC_LOGICAL": 10,
    "POSITIVIST_EMPIRICAL": 5,
    "NONE": 0,
}


def infer_class_epistemology(
    class_level: str,
    class_name: str,
    file_path: str,
    method_epistemologies: list[str],
    method_blobs: list[str],
) -> tuple[str, str]:
    """Infiere la epistemología de clase.

    Reglas:
    1. INFRASTRUCTURE/PROTOCOL → NONE.
    2. N1-EMP → POSITIVIST_EMPIRICAL.
    3. N4-SYN → CRITICAL_REFLEXIVE.
    4. N3-AUD → POPPERIAN_FALSIFICATIONIST (o CRITICAL_REFLEXIVE si presente).
    5. Para N2-INF: mayoría ponderada por prioridad.
    6. Fallback a DETERMINISTIC_LOGICAL.

    Retorna (epistemology, rationale).
    """

    if class_level in {"INFRASTRUCTURE", "PROTOCOL"}:
        return "NONE", f"class_level={class_level} → epistemología forzada a NONE"

    if class_level == "N1-EMP":
        return "POSITIVIST_EMPIRICAL", "N1-EMP → POSITIVIST_EMPIRICAL por definición"

    if class_level == "N4-SYN":
        return "CRITICAL_REFLEXIVE", "N4-SYN → CRITICAL_REFLEXIVE por definición"

    if class_level == "N3-AUD":
        if "CRITICAL_REFLEXIVE" in method_epistemologies:
            return "CRITICAL_REFLEXIVE", "N3-AUD con método CRITICAL_REFLEXIVE → hereda CRITICAL_REFLEXIVE"
        return "POPPERIAN_FALSIFICATIONIST", "N3-AUD → POPPERIAN_FALSIFICATIONIST por definición"

    # --- Para N2-INF: ponderación por prioridad ---
    epi_counts: dict[str, int] = {}
    for e in method_epistemologies:
        if e in EPISTEMOLOGY_PRIORITY:
            epi_counts[e] = epi_counts.get(e, 0) + 1

    if not epi_counts:
        blob = f"{class_name} {file_path} " + " ".join(method_blobs)
        if contains_any(blob, ["causal", "dag", "mechanism", "counterfactual"]):
            return "CAUSAL_MECHANISTIC", "Sin epistemologías de método pero señales causales en blob → CAUSAL_MECHANISTIC"
        return "DETERMINISTIC_LOGICAL", "Sin epistemologías de método, fallback → DETERMINISTIC_LOGICAL"

    # Mayoría ponderada
    total = sum(epi_counts.values())
    weighted: dict[str, float] = {}
    for e, c in epi_counts.items():
        weighted[e] = (c / total) * EPISTEMOLOGY_PRIORITY[e]

    winner = max(weighted, key=lambda x: weighted[x])
    rationale = (
        f"Epistemología por ponderación: {winner} "
        f"(score={weighted[winner]:.2f}, counts={epi_counts})"
    )
    return winner, rationale


# ---------------------------------------------------------------------------
# Detección de clase Protocol
# ---------------------------------------------------------------------------
def is_protocol_class(class_name: str, file_path: str) -> bool:
    """Detecta si una clase es un Protocol/Contract/Interface.

    Usa patrones en PROTOCOL_PATTERNS (word-boundary para evitar falsos positivos).
    """

    blob = norm_text_for_match(f"{class_name} {file_path}")
    for pattern in PROTOCOL_PATTERNS:
        if re.search(pattern, blob, re.IGNORECASE):
            return True
    return False
