from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final


CLASS_LEVELS: Final[set[str]] = {
    "N1-EMP",
    "N2-INF",
    "N3-AUD",
    "N4-SYN",
    "INFRASTRUCTURE",
    "PROTOCOL",
}

CLASS_EPISTEMOLOGIES: Final[set[str]] = {
    "POSITIVIST_EMPIRICAL",
    "BAYESIAN_PROBABILISTIC",
    "DETERMINISTIC_LOGICAL",
    "CAUSAL_MECHANISTIC",
    "POPPERIAN_FALSIFICATIONIST",
    "CRITICAL_REFLEXIVE",
    "NONE",
}

METHOD_LEVELS: Final[set[str]] = {
    "N1-EMP",
    "N2-INF",
    "N3-AUD",
    "N4-SYN",
    "INFRASTRUCTURE",
}

VETO_ACTIONS: Final[set[str]] = {
    # Minimal set (spec) + allowed set (audit_v4_rigorous.py)
    "block_branch",
    "reduce_confidence",
    "flag_caution",
    "suppress_fact",
    "invalidate_graph",
    "flag_and_reduce",
    "flag_insufficiency",
    "downgrade_confidence_to_zero",
    "flag_invalid_sequence",
    "suppress_contradicting_nodes",
}


@dataclass(frozen=True)
class MethodDecision:
    level: str
    epistemology: str
    decision_path: str
    skip_rest: bool = False
    precheck: bool = False


def _norm(s: object) -> str:
    return "" if s is None else str(s)


def _contains_any(haystack: str, needles: list[str]) -> bool:
    h = haystack.lower()
    return any(n.lower() in h for n in needles)


def _method_signature_blob(method_name: str, method: dict[str, Any]) -> str:
    return " ".join(
        [
            method_name,
            _norm(method.get("return_type")),
            _norm(method.get("docstring")),
            json.dumps(method.get("parameters", []), ensure_ascii=False, sort_keys=True),
        ]
    ).lower()


def classify_method(method_name: str, method: dict[str, Any]) -> MethodDecision:
    return_type = _norm(method.get("return_type"))
    docstring = _norm(method.get("docstring"))
    name = method_name

    # §2.1: __init__ or trivial private method
    if name in {"__init__", "__repr__", "__str__", "__hash__", "__eq__"}:
        return MethodDecision(
            level="INFRASTRUCTURE",
            epistemology="NONE",
            decision_path="PASO 1 → dunder/trivial → INFRASTRUCTURE",
            skip_rest=True,
        )

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
            skip_rest=True,
            precheck=True,
        )

    # §2.3 PASO 2
    if (
        "bool" in return_type.lower()
        and _contains_any(name, ["validate", "check", "verify", "detect", "audit", "test"])
    ):
        epistemology = "POPPERIAN_FALSIFICATIONIST"
        return MethodDecision(
            level="N3-AUD",
            epistemology=epistemology,
            decision_path="PASO 2 → bool + validate/check/verify/detect/audit/test → N3-AUD",
        )

    # §2.3 PASO 3
    if _contains_any(return_type, ["float", "ndarray", "distribution", "posterior", "score"]):
        if _contains_any(docstring, ["posterior", "bayesian", "prior", "credible"]):
            return MethodDecision(
                level="N2-INF",
                epistemology="BAYESIAN_PROBABILISTIC",
                decision_path=(
                    "PASO 3 → return_type numérico + docstring bayesian (posterior/prior/credible) "
                    "→ N2-INF + BAYESIAN_PROBABILISTIC"
                ),
            )
        return MethodDecision(
            level="N2-INF",
            epistemology="DETERMINISTIC_LOGICAL",
            decision_path="PASO 3 → return_type numérico (float/NDArray/Distribution/Posterior/Score) → N2-INF",
        )

    # §2.3 PASO 4
    if _contains_any(name, ["extract", "parse", "chunk", "split", "normalize"]):
        if _contains_any(return_type, ["str", "list[str]", "list[str]", "list", "dict", "mapping"]):
            return MethodDecision(
                level="N1-EMP",
                epistemology="POSITIVIST_EMPIRICAL",
                decision_path="PASO 4 → extract/parse/chunk/split/normalize + retorno textual → N1-EMP",
            )
        return MethodDecision(
            level="N2-INF",
            epistemology="DETERMINISTIC_LOGICAL",
            decision_path="PASO 4 → extract/parse/chunk/split/normalize pero no retorno textual → N2-INF",
        )

    # §2.3 PASO 5
    if _contains_any(name, ["infer", "compute", "calculate", "score", "evaluate", "classify"]):
        epistemology = "BAYESIAN_PROBABILISTIC" if _contains_any(docstring, ["posterior", "bayesian", "prior", "credible"]) else "DETERMINISTIC_LOGICAL"
        return MethodDecision(
            level="N2-INF",
            epistemology=epistemology,
            decision_path="PASO 5 → infer/compute/calculate/score/evaluate/classify → N2-INF",
        )

    # episte_refact.md: N4-SYN (síntesis narrativa) cuando el método genera reporte/respuesta/narrativa
    # Nota: esto opera SOLO con señales de firma (name/return_type/docstring).
    if _contains_any(name, ["format", "_format"]) and _contains_any(docstring, ["error", "exception", "traceback"]):
        return MethodDecision(
            level="INFRASTRUCTURE",
            epistemology="NONE",
            decision_path="PRECHECK → formateo de error/exception → INFRASTRUCTURE",
            skip_rest=True,
            precheck=True,
        )

    n4_name_signals = [
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
        "format",
        "write",
        "produce",
    ]
    n4_doc_signals = [
        "executive report",
        "reporte ejecutivo",
        "report",
        "summary",
        "summarize",
        "narrative",
        "síntesis",
        "synthesis",
        "human_answer",
        "veredicto",
        "respuesta",
        "markdown",
    ]
    if _contains_any(name, n4_name_signals) or _contains_any(docstring, n4_doc_signals):
        if _contains_any(return_type, ["str", "dict", "mapping", "list[str]", "path"]):
            return MethodDecision(
                level="N4-SYN",
                epistemology="CRITICAL_REFLEXIVE",
                decision_path="PASO N4 → señales de síntesis (reporte/narrativa/respuesta) → N4-SYN",
            )

    # §2.3 PASO 6
    if return_type.strip() in {"", "None", "NoReturn"}:
        return MethodDecision(
            level="INFRASTRUCTURE",
            epistemology="NONE",
            decision_path="PASO 6 → return_type vacío/None → INFRASTRUCTURE",
        )

    # Default conservador
    epistemology = (
        "BAYESIAN_PROBABILISTIC"
        if _contains_any(docstring, ["posterior", "bayesian", "prior", "credible", "bayes factor", "bayes_factor"])
        else "DETERMINISTIC_LOGICAL"
    )
    return MethodDecision(
        level="N2-INF",
        epistemology=epistemology,
        decision_path="PASO 6 → default conservador (retorno no vacío) → N2-INF",
    )


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


def infer_requires(parameters: list[dict[str, Any]]) -> list[str]:
    requires: set[str] = set()
    for p in parameters:
        blob = f"{_norm(p.get('name'))} {_norm(p.get('type'))}".lower()
        if _contains_any(blob, ["text", "raw_text"]):
            requires.add("raw_text")
        if _contains_any(blob, ["observations", "facts", "extracted"]):
            requires.add("raw_facts")
        if _contains_any(blob, ["scores", "parameters", "inferences"]):
            requires.add("inferences")
        if _contains_any(blob, ["preprocesadometadata", "metadata"]):
            requires.add("PreprocesadoMetadata")
        if _contains_any(blob, ["constraints", "validations", "audit_results"]):
            requires.add("validated_constraints")
    return sorted(requires)


def infer_produces(return_type: str, docstring: str) -> list[str]:
    rt = return_type.lower().strip()
    ds = docstring.lower()
    produces: set[str] = set()

    if rt == "":
        return []

    if _contains_any(rt, ["bool", "validationresult", "constraint"]):
        produces.add("validated_constraints")

    if _contains_any(rt, ["float", "ndarray", "score", "evaluation", "distribution", "posterior"]):
        produces.add("inferences")

    if _contains_any(rt, ["str", "list[str]", "dict", "mapping", "list"]):
        # textual containers default to raw_facts unless narrative/synthesis is explicit
        if _contains_any(ds, ["narrative", "synthesis", "summary", "report"]):
            produces.add("narrative")
        else:
            produces.add("raw_facts")

    return sorted(produces)


def infer_contract_compatibility(method_blob: str, level: str, epistemology: str) -> dict[str, bool]:
    compat = {"TYPE_A": False, "TYPE_B": False, "TYPE_C": False, "TYPE_D": False, "TYPE_E": False}

    if _contains_any(method_blob, ["semantic", "chunk", "embed", "embedding", "text", "coherence"]):
        compat["TYPE_A"] = True
    if _contains_any(method_blob, ["bayesian", "posterior", "prior", "credible", "distribution"]):
        compat["TYPE_B"] = True
    if _contains_any(method_blob, ["causal", "dag", "mechanism", "counterfactual", "path"]):
        compat["TYPE_C"] = True
    if _contains_any(method_blob, ["financial", "budget", "allocation", "sufficiency", "cost", "amount", "monto", "presupuesto"]):
        compat["TYPE_D"] = True
    if _contains_any(method_blob, ["contradiction", "consistency", "logical", "sequence", "valid", "validate", "verify", "check"]):
        compat["TYPE_E"] = True

    # Enforcements
    if epistemology == "BAYESIAN_PROBABILISTIC":
        compat["TYPE_B"] = True

    # Orphan prevention (V4.1/V2.5)
    if level != "INFRASTRUCTURE" and not any(compat.values()):
        if level == "N4-SYN":
            compat["TYPE_A"] = True
        elif level == "N1-EMP":
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

    if _contains_any(ds, ["invalid", "fail", "reject"]):
        veto["validation_failed"] = {
            "trigger": "validation_failed",
            "action": "block_branch",
            "scope": "global",
            "confidence_multiplier": 0.0,
        }
    if _contains_any(ds, ["weak", "insufficient", "low"]):
        veto["below_threshold"] = {
            "trigger": "below_threshold",
            "action": "reduce_confidence",
            "scope": "global",
            "confidence_multiplier": 0.3,
        }
    if _contains_any(ds, ["inconsistent", "contradiction"]):
        veto["logical_inconsistency"] = {
            "trigger": "logical_inconsistency",
            "action": "flag_caution",
            "scope": "global",
            "confidence_multiplier": 0.5,
        }

    if not veto:
        veto = {
            "generic_validation_failure": {
                "trigger": "return_value indicates failure",
                "action": "reduce_confidence",
                "scope": "global",
                "confidence_multiplier": 0.5,
            }
        }

    return veto


def infer_class_level(method_levels: list[str], method_names: list[str]) -> str:
    # §1.2
    meaningful = [lvl for lvl in method_levels if lvl in {"N1-EMP", "N2-INF", "N3-AUD", "N4-SYN"}]

    if not meaningful:
        # If class only has __init__ or no methods
        if method_names and all(n == "__init__" for n in method_names):
            return "INFRASTRUCTURE"
        return "INFRASTRUCTURE"

    c1 = meaningful.count("N1-EMP")
    c2 = meaningful.count("N2-INF")
    c3 = meaningful.count("N3-AUD")
    c4 = meaningful.count("N4-SYN")

    maxc = max(c1, c2, c3, c4)
    winners = [
        lvl
        for lvl, c in [("N1-EMP", c1), ("N2-INF", c2), ("N3-AUD", c3), ("N4-SYN", c4)]
        if c == maxc
    ]

    if len(winners) == 1:
        return winners[0]

    if "N4-SYN" in winners:
        return "N4-SYN"

    if set(winners) == {"N1-EMP", "N2-INF"}:
        return "N2-INF"

    if set(winners) == {"N2-INF", "N3-AUD"}:
        return "N3-AUD"

    # Three-way tie: conservative towards N3 (validation overrides)
    return "N3-AUD"


def infer_class_epistemology(
    class_level: str,
    class_name: str,
    file_path: str,
    method_epistemologies: list[str],
    method_blobs: list[str],
) -> str:
    if class_level in {"INFRASTRUCTURE", "PROTOCOL"}:
        return "NONE"

    if class_level == "N1-EMP":
        return "POSITIVIST_EMPIRICAL"

    if class_level == "N4-SYN":
        return "CRITICAL_REFLEXIVE"

    if class_level == "N3-AUD":
        if any(e == "CRITICAL_REFLEXIVE" for e in method_epistemologies):
            return "CRITICAL_REFLEXIVE"
        return "POPPERIAN_FALSIFICATIONIST"

    # N2 (default) and any other
    if any(e == "BAYESIAN_PROBABILISTIC" for e in method_epistemologies):
        return "BAYESIAN_PROBABILISTIC"

    blob = f"{class_name} {file_path} " + " ".join(method_blobs)
    if _contains_any(blob, ["causal", "dag", "mechanism", "counterfactual", "path"]):
        return "CAUSAL_MECHANISTIC"

    return "DETERMINISTIC_LOGICAL"


def is_protocol_class(class_name: str, file_path: str) -> bool:
    blob = f"{class_name} {file_path}".lower()
    return bool(re.search(r"\bprotocol\b", blob)) or class_name.endswith("Protocol")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_enriched(enriched: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    for class_name, cls in enriched.items():
        if class_name == "quality_metrics":
            continue
        level = cls.get("class_level")
        epi = cls.get("class_epistemology")
        if level not in CLASS_LEVELS:
            errors.append({"error": "INVALID_CLASS_LEVEL", "class": class_name, "value": level})
        if epi not in CLASS_EPISTEMOLOGIES:
            errors.append({"error": "INVALID_CLASS_EPISTEMOLOGY", "class": class_name, "value": epi})
        if level == "INFRASTRUCTURE" and epi != "NONE":
            errors.append({"error": "INFRASTRUCTURE_MISMATCH", "class": class_name, "value": epi})

        methods = cls.get("methods", {})
        for method_name, m in methods.items():
            ec = m.get("epistemological_classification")
            if ec is None:
                errors.append({"error": "MISSING_EPISTEMOLOGICAL_CLASSIFICATION", "class": class_name, "method": method_name})
                continue

            mlevel = ec.get("level")
            if mlevel not in METHOD_LEVELS:
                errors.append({"error": "INVALID_METHOD_LEVEL", "class": class_name, "method": method_name, "value": mlevel})

            if mlevel == "N3-AUD" and ec.get("veto_conditions") is None:
                errors.append({"error": "MISSING_VETO_FOR_N3", "class": class_name, "method": method_name})

            expected_output, expected_fusion, expected_phase = map_level_to_output(mlevel)
            if ec.get("output_type") != expected_output:
                errors.append({"error": "OUTPUT_TYPE_MISMATCH", "class": class_name, "method": method_name})
            if ec.get("fusion_behavior") != expected_fusion:
                errors.append({"error": "FUSION_BEHAVIOR_MISMATCH", "class": class_name, "method": method_name})
            if ec.get("phase_assignment") != expected_phase:
                errors.append({"error": "PHASE_ASSIGNMENT_MISMATCH", "class": class_name, "method": method_name})

            decision_path = _norm(ec.get("classification_evidence", {}).get("decision_path"))
            if decision_path.strip() == "":
                errors.append({"error": "MISSING_DECISION_PATH", "class": class_name, "method": method_name})

            if mlevel != "INFRASTRUCTURE":
                compat = ec.get("contract_compatibility", {})
                if not any(bool(compat.get(k)) for k in ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E"]):
                    errors.append({"error": "NO_CONTRACT_COMPATIBILITY", "class": class_name, "method": method_name})

                # Dependency validations
                deps = ec.get("dependencies", {})
                req = deps.get("requires") or []
                prod = deps.get("produces") or []

                if mlevel == "N2-INF" and len(req) == 0:
                    errors.append({"error": "N2_WITHOUT_INPUT", "class": class_name, "method": method_name})
                if mlevel == "N2-INF":
                    req_set = {x for x in req if isinstance(x, str)}
                    if not ({"raw_facts", "PreprocesadoMetadata"} & req_set):
                        errors.append(
                            {
                                "error": "N2_REQUIRES_MISSING_RAW_FACTS_OR_METADATA",
                                "class": class_name,
                                "method": method_name,
                            }
                        )
                if mlevel == "N3-AUD":
                    req_set = {x for x in req if isinstance(x, str)}
                    if not ({"raw_facts", "inferences"}.issubset(req_set)):
                        errors.append({"error": "N3_WITHOUT_UPSTREAM", "class": class_name, "method": method_name})
                if len(prod) == 0:
                    errors.append({"error": "NO_OUTPUT_DECLARED", "class": class_name, "method": method_name})

                if mlevel == "N4-SYN" and "narrative" not in prod:
                    errors.append({"error": "N4_WITHOUT_NARRATIVE", "class": class_name, "method": method_name})

                # Compatibility validation
                if ec.get("epistemology") == "BAYESIAN_PROBABILISTIC" and not ec.get("contract_compatibility", {}).get("TYPE_B"):
                    errors.append({"error": "BAYESIAN_NOT_TYPE_B", "class": class_name, "method": method_name})

            if mlevel == "N3-AUD":
                veto = ec.get("veto_conditions")
                if not isinstance(veto, dict) or not veto:
                    errors.append({"error": "EMPTY_VETO_CONDITIONS", "class": class_name, "method": method_name})
                else:
                    for k, v in veto.items():
                        if not all(x in v for x in ["trigger", "action", "scope", "confidence_multiplier"]):
                            errors.append({"error": "INCOMPLETE_VETO", "class": class_name, "method": method_name, "key": k})
                            continue
                        if v["action"] not in VETO_ACTIONS:
                            errors.append({"error": "INVALID_VETO_ACTION", "class": class_name, "method": method_name, "key": k})
                        try:
                            cm = float(v["confidence_multiplier"])
                        except Exception:
                            errors.append({"error": "INVALID_MULTIPLIER", "class": class_name, "method": method_name, "key": k})
                            continue
                        if not (0.0 <= cm <= 1.0):
                            errors.append({"error": "INVALID_MULTIPLIER", "class": class_name, "method": method_name, "key": k})

    return errors


def enrich_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    enriched: dict[str, Any] = {}

    total_methods = 0
    infrastructure_methods = 0
    n1 = n2 = n3 = n4 = 0
    methods_with_veto = 0

    for class_name, cls in inventory.items():
        file_path = _norm(cls.get("file_path"))
        line_number = cls.get("line_number")
        methods = cls.get("methods", {}) or {}

        per_method_levels: list[str] = []
        per_method_epistemologies: list[str] = []
        per_method_blobs: list[str] = []
        method_names: list[str] = list(methods.keys())

        enriched_methods: dict[str, Any] = {}
        for method_name, method in methods.items():
            total_methods += 1
            decision = classify_method(method_name, method)
            level = decision.level
            epistemology = decision.epistemology

            output_type, fusion_behavior, phase_assignment = map_level_to_output(level)

            parameters = method.get("parameters", []) or []
            requires = infer_requires(parameters)

            produces = infer_produces(_norm(method.get("return_type")), _norm(method.get("docstring")))

            if level != "INFRASTRUCTURE":
                if level == "N1-EMP":
                    # Align with audit_v4_rigorous contract expectations: N1.requires must be []
                    requires = []
                if level == "N2-INF" and len(requires) == 0:
                    requires = ["raw_facts"]

                if level == "N2-INF":
                    req_set = set(requires)
                    if not ({"raw_facts", "PreprocesadoMetadata"} & req_set):
                        requires = sorted(req_set | {"raw_facts"})

                if level == "N3-AUD":
                    # Align with audit_v4_rigorous contract expectations: N3 requires raw_facts + inferences
                    requires = sorted(set(requires) | {"raw_facts", "inferences"})

                if level == "N4-SYN" and len(requires) == 0:
                    # N4 consumes validated outputs from all layers (episte_refact)
                    requires = ["raw_facts", "inferences", "validated_constraints"]

                if level == "N4-SYN":
                    # Por definición (episte_refact), N4 produce salida narrativa terminal
                    produces = ["narrative"]

                if len(produces) == 0:
                    # default consistent with level
                    produces = {
                        "N1-EMP": ["raw_facts"],
                        "N2-INF": ["inferences"],
                        "N3-AUD": ["validated_constraints"],
                        "N4-SYN": ["narrative"],
                    }.get(level, ["inferences"])  # type: ignore[assignment]

            method_blob = _method_signature_blob(method_name, method)
            per_method_blobs.append(method_blob)
            contract_compatibility = infer_contract_compatibility(method_blob, level, epistemology)

            veto_conditions = infer_veto_conditions(level, _norm(method.get("docstring")))
            if level == "N3-AUD" and veto_conditions is not None:
                methods_with_veto += 1

            dependencies: dict[str, Any] = {
                "requires": requires if level != "INFRASTRUCTURE" else [],
                "produces": produces if level != "INFRASTRUCTURE" else [],
                # Modeled after audit_v4_rigorous: N2 should declare modifies, N3 should declare modulates
                "modifies": ["inferences"] if level == "N2-INF" else [],
                "modulates": ["confidence_scores"] if level == "N3-AUD" else None,
            }

            enriched_methods[method_name] = {
                **method,
                "epistemological_classification": {
                    "level": level,
                    "output_type": output_type,
                    "fusion_behavior": fusion_behavior,
                    "epistemology": epistemology,
                    "phase_assignment": phase_assignment,
                    "dependencies": dependencies,
                    "contract_compatibility": contract_compatibility,
                    "veto_conditions": veto_conditions,
                    "classification_evidence": {
                        "return_type_signal": f"return_type='{_norm(method.get('return_type'))}'",
                        "name_pattern_signal": f"method_name='{method_name}'",
                        "docstring_signal": f"docstring_contains_bayes={_contains_any(_norm(method.get('docstring')), ['posterior','bayesian','prior','credible'])}",
                        "decision_path": decision.decision_path,
                    },
                },
            }

            per_method_levels.append(level)
            per_method_epistemologies.append(epistemology)

            if level == "INFRASTRUCTURE":
                infrastructure_methods += 1
            elif level == "N1-EMP":
                n1 += 1
            elif level == "N2-INF":
                n2 += 1
            elif level == "N3-AUD":
                n3 += 1
            elif level == "N4-SYN":
                n4 += 1

        if is_protocol_class(class_name, file_path):
            class_level = "PROTOCOL"
            class_epistemology = "NONE"
        else:
            class_level = infer_class_level(per_method_levels, method_names)
            class_epistemology = infer_class_epistemology(
                class_level,
                class_name,
                file_path,
                per_method_epistemologies,
                per_method_blobs,
            )

        enriched[class_name] = {
            "file_path": file_path,
            "line_number": line_number,
            "class_level": class_level,
            "class_epistemology": class_epistemology,
            "methods": enriched_methods,
        }

    enriched["quality_metrics"] = {
        "total_classes": len([k for k in enriched.keys() if k != 'quality_metrics']),
        "total_methods": total_methods,
        "infrastructure_methods": infrastructure_methods,
        "n1_methods": n1,
        "n2_methods": n2,
        "n3_methods": n3,
        "n4_methods": n4,
        "methods_with_veto": methods_with_veto,
        "n3_without_veto": 0,
        "orphan_methods": 0,
        "validation_errors": [],
    }

    return enriched


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    input_path = repo_root / "METHODS_DISPENSARY_SIGNATURES.json"
    output_path = repo_root / "METHODS_DISPENSARY_SIGNATURES_ENRICHED_EPISTEMOLOGY.json"

    inventory = json.loads(input_path.read_text(encoding="utf-8"))
    enriched = enrich_inventory(inventory)

    errors = validate_enriched(enriched)
    enriched["quality_metrics"]["validation_errors"] = errors

    # Derived metrics (must be 0)
    n3_without_veto = 0
    orphan_methods = 0
    for class_name, cls in enriched.items():
        if class_name == "quality_metrics":
            continue
        for method_name, m in (cls.get("methods", {}) or {}).items():
            ec = m.get("epistemological_classification")
            if not ec:
                continue
            if ec.get("level") == "N3-AUD" and ec.get("veto_conditions") is None:
                n3_without_veto += 1
            if ec.get("level") != "INFRASTRUCTURE":
                compat = ec.get("contract_compatibility", {})
                if not any(bool(compat.get(k)) for k in ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E"]):
                    orphan_methods += 1

    enriched["quality_metrics"]["n3_without_veto"] = n3_without_veto
    enriched["quality_metrics"]["orphan_methods"] = orphan_methods

    output_path.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "output_file": str(output_path),
        "output_sha256": sha256_file(output_path),
        "bytes": output_path.stat().st_size,
        "quality_metrics": enriched["quality_metrics"],
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
