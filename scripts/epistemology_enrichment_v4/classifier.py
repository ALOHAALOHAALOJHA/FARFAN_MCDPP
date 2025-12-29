"""Clasificador epistemológico de métodos.

Diseño v2:
- Todas las señales centralizadas en `rulebook.Rulebook`.
- Cada decisión registra las señales que dispararon (matched_signals).
- Invariantes tipados (frozen dataclass).
- Normalización Unicode via utils.norm_text_for_match.

Versión: 2.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .rulebook import DEFAULT_RULEBOOK, Rulebook
from .utils import contains_any, norm, norm_text_for_match


# ---------------------------------------------------------------------------
# Decisión de método (inmutable + auditable)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MethodDecision:
    level: str
    epistemology: str
    decision_path: str
    matched_signals: tuple[str, ...] = field(default_factory=tuple)
    skip_rest: bool = False
    precheck: bool = False


# ---------------------------------------------------------------------------
# Subtipos de infraestructura (centralizados)
# ---------------------------------------------------------------------------
INFRASTRUCTURE_SUBTYPES: dict[str, tuple[str, ...]] = {
    "LIFECYCLE": ("__init__", "__del__", "__enter__", "__exit__"),
    "REPRESENTATION": ("__repr__", "__str__", "__hash__", "__eq__"),
    "IO": ("load", "save", "read", "write", "cache"),
    "FORMATTING": ("format", "_format"),
    "UTILITY": ("_normalize", "normalize", "_clean", "clean", "_sanitize", "sanitize"),
}


def classify_infrastructure_subtype(method_name: str) -> str:
    nm = norm_text_for_match(method_name)
    for subtype, patterns in INFRASTRUCTURE_SUBTYPES.items():
        for p in patterns:
            pl = norm_text_for_match(p)
            if nm == pl or pl in nm:
                return f"INFRASTRUCTURE_{subtype}"
    return "INFRASTRUCTURE_GENERIC"


# ---------------------------------------------------------------------------
# Helpers con trazabilidad
# ---------------------------------------------------------------------------
def _match_signals(blob: str, signals: tuple[str, ...]) -> list[str]:
    """Retorna lista de señales que coinciden en blob (para trazabilidad)."""
    normalized = norm_text_for_match(blob)
    return [s for s in signals if norm_text_for_match(s) in normalized]


def output_is_derived(
    return_type: str,
    docstring: str,
    method_name: str,
    rulebook: Rulebook = DEFAULT_RULEBOOK,
) -> tuple[bool, list[str]]:
    """Heurística: derivado (N2) vs literal (N1).

    Retorna (is_derived, matched_signals).
    """

    blob = f"{return_type} {docstring} {method_name}"
    derived_matches = _match_signals(blob, rulebook.derived_signals)
    if derived_matches:
        return True, derived_matches

    literal_matches = _match_signals(docstring, rulebook.literal_signals)
    if literal_matches:
        return False, literal_matches

    rt = norm_text_for_match(return_type)
    if any(x in rt for x in ("float", "int", "ndarray")) and not any(x in rt for x in ("list", "dict", "mapping")):
        return True, ["numeric_return_type_heuristic"]

    return False, ["default_literal_assumption"]


def has_veto_capability(
    docstring: str,
    method_name: str,
    rulebook: Rulebook = DEFAULT_RULEBOOK,
) -> tuple[bool, list[str]]:
    """Detecta capacidad de veto. Retorna (has_veto, matched_signals)."""

    blob = f"{docstring} {method_name}"
    matches = _match_signals(blob, rulebook.veto_signals)
    return bool(matches), matches


# ---------------------------------------------------------------------------
# Clasificador principal
# ---------------------------------------------------------------------------
def classify_method(
    method_name: str,
    method: dict[str, Any],
    rulebook: Rulebook = DEFAULT_RULEBOOK,
) -> MethodDecision:
    """Clasifica un método según árbol de decisión epistemológico.

    Cada rama registra las señales que dispararon la decisión.
    """

    return_type = norm(method.get("return_type"))
    docstring = norm(method.get("docstring"))
    name = method_name

    # --- PASO 1: dunders triviales ---
    if name in {"__init__", "__repr__", "__str__", "__hash__", "__eq__"}:
        return MethodDecision(
            level="INFRASTRUCTURE",
            epistemology="NONE",
            decision_path="PASO 1 → dunder/trivial → INFRASTRUCTURE",
            matched_signals=(name,),
            skip_rest=True,
        )

    # --- PRECHECK: private + trivial signature ---
    is_private = name.startswith("_")
    is_trivialish = (
        is_private
        and (return_type.strip() in {"", "None", "NoReturn"} or docstring.strip() == "")
        and name not in {"__init__"}
    )
    if is_trivialish:
        return MethodDecision(
            level="INFRASTRUCTURE",
            epistemology="NONE",
            decision_path="PRECHECK → private+trivial signature → INFRASTRUCTURE",
            matched_signals=("private", "empty_signature"),
            skip_rest=True,
            precheck=True,
        )

    # --- PRECHECK: error/exception formatting ---
    if contains_any(name, ["format", "_format"]) and contains_any(docstring, ["error", "exception", "traceback"]):
        return MethodDecision(
            level="INFRASTRUCTURE",
            epistemology="NONE",
            decision_path="PRECHECK → formateo de error/exception → INFRASTRUCTURE",
            matched_signals=("format", "error_context"),
            skip_rest=True,
            precheck=True,
        )

    # --- PASO 2: auditoría booleana con veto observable ---
    rt_lower = norm_text_for_match(return_type)
    if "bool" in rt_lower and contains_any(name, ["validate", "check", "verify", "detect", "audit", "test"]):
        has_veto, veto_matches = has_veto_capability(docstring, name, rulebook)
        if has_veto:
            return MethodDecision(
                level="N3-AUD",
                epistemology="POPPERIAN_FALSIFICATIONIST",
                decision_path="PASO 2 → bool + validator + veto_observable → N3-AUD",
                matched_signals=tuple(veto_matches),
            )
        # Sin veto observable: degradar a N2-INF (principio de observabilidad)
        return MethodDecision(
            level="N2-INF",
            epistemology="DETERMINISTIC_LOGICAL",
            decision_path="PASO 2 → bool + validator pero SIN veto observable → N2-INF",
            matched_signals=("validator_without_veto",),
        )

    # --- PASO 3: numérico/score/distribution ---
    if contains_any(return_type, ["float", "ndarray", "distribution", "posterior", "score"]):
        bayes_matches = _match_signals(docstring, ("posterior", "bayesian", "prior", "credible"))
        if bayes_matches:
            return MethodDecision(
                level="N2-INF",
                epistemology="BAYESIAN_PROBABILISTIC",
                decision_path="PASO 3 → return_type numérico + docstring bayesian → N2-INF + BAYESIAN",
                matched_signals=tuple(bayes_matches),
            )
        return MethodDecision(
            level="N2-INF",
            epistemology="DETERMINISTIC_LOGICAL",
            decision_path="PASO 3 → return_type numérico → N2-INF",
            matched_signals=("numeric_return",),
        )

    # --- PASO 4: extracción / parseo ---
    if contains_any(name, ["extract", "parse", "chunk", "split", "normalize"]):
        derived, derive_matches = output_is_derived(return_type, docstring, name, rulebook)
        if not derived:
            return MethodDecision(
                level="N1-EMP",
                epistemology="POSITIVIST_EMPIRICAL",
                decision_path="PASO 4 → extracción/parseo con output literal → N1-EMP",
                matched_signals=tuple(derive_matches),
            )
        return MethodDecision(
            level="N2-INF",
            epistemology="DETERMINISTIC_LOGICAL",
            decision_path="PASO 4 → extracción/parseo con output derivado → N2-INF",
            matched_signals=tuple(derive_matches),
        )

    # --- PASO 5: inferencia ---
    if contains_any(name, ["infer", "compute", "calculate", "score", "evaluate", "classify", "compare", "analyze"]):
        bayes_matches = _match_signals(docstring, ("posterior", "bayesian", "prior", "credible", "bayes factor", "bayes_factor"))
        epi = "BAYESIAN_PROBABILISTIC" if bayes_matches else "DETERMINISTIC_LOGICAL"
        return MethodDecision(
            level="N2-INF",
            epistemology=epi,
            decision_path="PASO 5 → inference/compute → N2-INF",
            matched_signals=tuple(bayes_matches) if bayes_matches else ("inference_verb",),
        )

    # --- PASO N4: síntesis narrativa ---
    n4_name_matches = _match_signals(name, rulebook.n4_name_signals)
    n4_doc_matches = _match_signals(docstring, rulebook.n4_doc_signals)
    if (n4_name_matches or n4_doc_matches) and contains_any(return_type, ["str", "dict", "mapping", "list[str]", "path"]):
        return MethodDecision(
            level="N4-SYN",
            epistemology="CRITICAL_REFLEXIVE",
            decision_path="PASO N4 → señales de síntesis → N4-SYN",
            matched_signals=tuple(n4_name_matches + n4_doc_matches),
        )

    # --- PASO 6: side-effect only ---
    if return_type.strip() in {"", "None", "NoReturn"}:
        return MethodDecision(
            level="INFRASTRUCTURE",
            epistemology="NONE",
            decision_path="PASO 6 → return_type vacío/None → INFRASTRUCTURE",
            matched_signals=("void_return",),
        )

    # --- Default conservador ---
    bayes_matches = _match_signals(docstring, ("posterior", "bayesian", "prior", "credible", "bayes factor", "bayes_factor"))
    epi = "BAYESIAN_PROBABILISTIC" if bayes_matches else "DETERMINISTIC_LOGICAL"
    return MethodDecision(
        level="N2-INF",
        epistemology=epi,
        decision_path="PASO 6 → default conservador (retorno no vacío) → N2-INF",
        matched_signals=tuple(bayes_matches) if bayes_matches else ("default_n2",),
    )
