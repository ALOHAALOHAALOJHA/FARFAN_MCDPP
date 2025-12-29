from __future__ import annotations

from typing import Any

from .utils import contains_any, norm


def map_level_to_output(level: str) -> tuple[str, str, str]:
    if level == "N1-EMP":
        return "FACT", "additive", "phase_A_construction"
    if level == "N2-INF":
        return "PARAMETER", "multiplicative", "phase_B_computation"
    if level == "N3-AUD":
        return "CONSTRAINT", "gate", "phase_C_litigation"
    if level == "N4-SYN":
        return "NARRATIVE", "terminal", "phase_D_synthesis"
    return "NONE", "none", "none"


def infer_requires(parameters: list[dict[str, Any]], level: str, docstring: str = "") -> list[str]:
    requires: set[str] = set()
    for p in parameters:
        blob = f"{norm(p.get('name'))} {norm(p.get('type'))}".lower()
        if contains_any(blob, ["text", "raw_text"]):
            requires.add("raw_text")
        if contains_any(blob, ["observations", "facts", "extracted"]):
            requires.add("raw_facts")
        if contains_any(blob, ["scores", "parameters", "inferences"]):
            requires.add("inferences")
        if contains_any(blob, ["preprocesadometadata", "metadata"]):
            requires.add("PreprocesadoMetadata")
        if contains_any(blob, ["constraints", "validations", "audit_results"]):
            requires.add("validated_constraints")

    # Invariantes jerárquicas por nivel (Guía v1.0.0)
    if level == "N1-EMP":
        return []

    if level == "N2-INF":
        if not (requires & {"raw_facts", "PreprocesadoMetadata"}):
            requires.add("raw_facts")

    if level == "N3-AUD":
        requires |= {"raw_facts", "inferences"}

    if level == "N4-SYN":
        requires |= {"raw_facts", "inferences", "validated_constraints"}

    return sorted(requires)


def infer_produces(return_type: str, docstring: str) -> list[str]:
    rt = return_type.lower().strip()
    ds = docstring.lower()
    produces: set[str] = set()

    if rt == "":
        return []

    if contains_any(rt, ["bool", "validationresult", "constraint"]):
        produces.add("validated_constraints")

    if contains_any(rt, ["float", "ndarray", "score", "evaluation", "distribution", "posterior"]):
        produces.add("inferences")

    if contains_any(rt, ["str", "list[str]", "dict", "mapping", "list"]):
        if contains_any(ds, ["narrative", "synthesis", "summary", "report"]):
            produces.add("narrative")
        else:
            produces.add("raw_facts")

    return sorted(produces)


def infer_contract_compatibility(
    method_blob: str,
    level: str,
    epistemology: str,
    return_type: str,
    class_context: str = "",
) -> dict[str, bool]:
    compat = {"TYPE_A": False, "TYPE_B": False, "TYPE_C": False, "TYPE_D": False, "TYPE_E": False}

    # Prioridad 1: señales específicas de dominio (early return)
    domain_specific: dict[str, list[str]] = {
        "TYPE_D": [
            "budget",
            "monto",
            "presupuesto",
            "allocation",
            "financial",
            "cop",
            "pesos",
            "suficiencia",
            "rubro",
            "rubr",
            "cost",
        ],
        "TYPE_C": ["dag", "causal_graph", "causal", "counterfactual", "mechanism", "scm"],
        "TYPE_B": ["posterior", "prior", "credible_interval", "credible", "bayes_factor", "bayesian"],
    }
    blob_full = f"{method_blob} {class_context} {return_type}".lower()
    for type_key, signals in domain_specific.items():
        if contains_any(blob_full, signals):
            compat[type_key] = True
            # NO early return: continúa para aplicar epistemología y otros flags

    if contains_any(method_blob, ["semantic", "chunk", "embed", "embedding", "text", "coherence"]):
        compat["TYPE_A"] = True
    if contains_any(method_blob, ["bayesian", "posterior", "prior", "credible", "distribution"]):
        compat["TYPE_B"] = True
    if contains_any(method_blob, ["causal", "dag", "mechanism", "counterfactual", "path"]):
        compat["TYPE_C"] = True
    if contains_any(method_blob, ["financial", "budget", "allocation", "sufficiency", "cost", "amount", "monto", "presupuesto"]):
        compat["TYPE_D"] = True
    if contains_any(method_blob, ["contradiction", "consistency", "logical", "sequence", "valid", "validate", "verify", "check"]):
        compat["TYPE_E"] = True

    if epistemology == "BAYESIAN_PROBABILISTIC":
        compat["TYPE_B"] = True

    # Orphan prevention
    if level != "INFRASTRUCTURE" and not any(compat.values()):
        if level in {"N4-SYN", "N1-EMP"}:
            compat["TYPE_A"] = True
        elif level == "N3-AUD":
            compat["TYPE_E"] = True
        else:
            compat["TYPE_E"] = True

    return compat


def infer_veto_conditions(level: str, docstring: str) -> dict[str, Any] | None:
    if level != "N3-AUD":
        return None

    ds = docstring.lower()
    veto: dict[str, Any] = {}

    if contains_any(ds, ["invalid", "fail", "reject"]):
        veto["validation_failed"] = {
            "trigger": "validation_failed",
            "action": "block_branch",
            "scope": "global",
            "confidence_multiplier": 0.0,
        }
    if contains_any(ds, ["weak", "insufficient", "low"]):
        veto["below_threshold"] = {
            "trigger": "below_threshold",
            "action": "reduce_confidence",
            "scope": "global",
            "confidence_multiplier": 0.3,
        }
    if contains_any(ds, ["inconsistent", "contradiction"]):
        veto["logical_inconsistency"] = {
            "trigger": "logical_inconsistency",
            "action": "flag_caution",
            "scope": "global",
            "confidence_multiplier": 0.5,
        }

    # Principio de observabilidad: si no hay condiciones observables, no inventar vetos.
    return veto or None
