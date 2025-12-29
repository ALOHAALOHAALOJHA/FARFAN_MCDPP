from __future__ import annotations

from typing import Any

from .constants import CLASS_EPISTEMOLOGIES, CLASS_LEVELS, METHOD_LEVELS, VETO_ACTIONS
from .infer import map_level_to_output
from .utils import norm


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
                errors.append(
                    {
                        "error": "MISSING_EPISTEMOLOGICAL_CLASSIFICATION",
                        "class": class_name,
                        "method": method_name,
                    }
                )
                continue

            mlevel = ec.get("level")
            if mlevel not in METHOD_LEVELS:
                errors.append(
                    {
                        "error": "INVALID_METHOD_LEVEL",
                        "class": class_name,
                        "method": method_name,
                        "value": mlevel,
                    }
                )

            if mlevel == "N3-AUD" and ec.get("veto_conditions") is None:
                errors.append({"error": "MISSING_VETO_FOR_N3", "class": class_name, "method": method_name})

            expected_output, expected_fusion, expected_phase = map_level_to_output(mlevel)
            if ec.get("output_type") != expected_output:
                errors.append({"error": "OUTPUT_TYPE_MISMATCH", "class": class_name, "method": method_name})
            if ec.get("fusion_behavior") != expected_fusion:
                errors.append({"error": "FUSION_BEHAVIOR_MISMATCH", "class": class_name, "method": method_name})
            if ec.get("phase_assignment") != expected_phase:
                errors.append({"error": "PHASE_ASSIGNMENT_MISMATCH", "class": class_name, "method": method_name})

            decision_path = norm(ec.get("classification_evidence", {}).get("decision_path"))
            if decision_path.strip() == "":
                errors.append({"error": "MISSING_DECISION_PATH", "class": class_name, "method": method_name})

            if mlevel != "INFRASTRUCTURE":
                compat = ec.get("contract_compatibility", {})
                if not any(bool(compat.get(k)) for k in ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E"]):
                    errors.append({"error": "NO_CONTRACT_COMPATIBILITY", "class": class_name, "method": method_name})

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

                if ec.get("epistemology") == "BAYESIAN_PROBABILISTIC" and not compat.get("TYPE_B"):
                    errors.append({"error": "BAYESIAN_NOT_TYPE_B", "class": class_name, "method": method_name})

            if mlevel == "N3-AUD":
                veto = ec.get("veto_conditions")
                if not isinstance(veto, dict) or not veto:
                    errors.append({"error": "EMPTY_VETO_CONDITIONS", "class": class_name, "method": method_name})
                else:
                    for k, v in veto.items():
                        if not all(x in v for x in ["trigger", "action", "scope", "confidence_multiplier"]):
                            errors.append(
                                {
                                    "error": "INCOMPLETE_VETO",
                                    "class": class_name,
                                    "method": method_name,
                                    "key": k,
                                }
                            )
                            continue
                        if v["action"] not in VETO_ACTIONS:
                            errors.append(
                                {
                                    "error": "INVALID_VETO_ACTION",
                                    "class": class_name,
                                    "method": method_name,
                                    "key": k,
                                }
                            )
                        try:
                            cm = float(v["confidence_multiplier"])
                        except Exception:
                            errors.append(
                                {
                                    "error": "INVALID_MULTIPLIER",
                                    "class": class_name,
                                    "method": method_name,
                                    "key": k,
                                }
                            )
                            continue
                        if not (0.0 <= cm <= 1.0):
                            errors.append(
                                {
                                    "error": "INVALID_MULTIPLIER",
                                    "class": class_name,
                                    "method": method_name,
                                    "key": k,
                                }
                            )

    return errors
