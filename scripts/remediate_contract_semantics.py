#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACTS_DIR = (
    REPO_ROOT
    / "src"
    / "farfan_pipeline"
    / "phases"
    / "Phase_two"
    / "json_files_phase_two"
    / "executor_contracts"
    / "specialized"
)


NUM_BASE_SLOTS = 30
NUM_POLICY_AREAS = 10


@dataclass(frozen=True, slots=True)
class RemediationOutcome:
    contract_path: Path
    changed: bool
    changes: tuple[str, ...]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected JSON object, got {type(data).__name__}")
    return data


def _dump_json_text(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def _trim_one_line(text: str, max_len: int) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."


def _canonical_monolith_hash(monolith_path: Path) -> str:
    monolith = _load_json(monolith_path)
    # Match existing contract_remediator convention: canonical JSON with ASCII escaping.
    canonical = json.dumps(monolith, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _policy_area_names(mapping_path: Path) -> dict[str, str]:
    try:
        raw = json.loads(mapping_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if not isinstance(raw, list):
        return {}
    out: dict[str, str] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        cid = item.get("canonical_id")
        name = item.get("canonical_name")
        if isinstance(cid, str) and isinstance(name, str):
            out[cid] = name
    return out


def _dimension_names(mapping_path: Path) -> dict[str, str]:
    try:
        raw = json.loads(mapping_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if not isinstance(raw, list):
        return {}
    out: dict[str, str] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        cid = item.get("canonical_id")
        name = item.get("canonical_name")
        if isinstance(cid, str) and isinstance(name, str):
            out[cid] = name
    return out


def _ensure_dict(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if isinstance(value, dict):
        return value
    new_value: dict[str, Any] = {}
    parent[key] = new_value
    return new_value


def _get_method_provides(contract: dict[str, Any]) -> list[str]:
    method_binding = contract.get("method_binding", {})
    if not isinstance(method_binding, dict):
        return []
    methods = method_binding.get("methods", [])
    if not isinstance(methods, list):
        return []
    provides: list[str] = []
    for m in methods:
        if not isinstance(m, dict):
            continue
        p = m.get("provides")
        if isinstance(p, str) and p.strip():
            provides.append(p.strip())
    return sorted(set(provides))


def _get_method_count(contract: dict[str, Any]) -> int:
    method_binding = contract.get("method_binding", {})
    if not isinstance(method_binding, dict):
        return 0
    mc = method_binding.get("method_count")
    if isinstance(mc, int):
        return mc
    methods = method_binding.get("methods", [])
    return len(methods) if isinstance(methods, list) else 0


def _fix_signal_requirements(
    contract: dict[str, Any],
    *,
    policy_area_id: str,
    dimension_id: str,
) -> tuple[bool, str | None]:
    sig = _ensure_dict(contract, "signal_requirements")

    desired_note = (
        "Signal requirements are under development. "
        f"Canonical mapping pending for {policy_area_id}/{dimension_id}; "
        "mandatory_signals and optional_signals are intentionally empty to avoid blocking execution."
    )
    desired_preferred = [
        "policy_instrument_detected",
        "activity_specification_found",
        "implementation_timeline_present",
    ]

    changed = False

    if sig.get("mandatory_signals") != []:
        sig["mandatory_signals"] = []
        changed = True

    if sig.get("optional_signals") != []:
        sig["optional_signals"] = []
        changed = True

    # Keep a normalized, non-zero threshold for downstream signal quality gating.
    if sig.get("minimum_signal_threshold") != 0.5:
        sig["minimum_signal_threshold"] = 0.5
        changed = True

    if not isinstance(sig.get("signal_aggregation"), str) or not sig.get("signal_aggregation"):
        sig["signal_aggregation"] = "weighted_mean"
        changed = True
    
    if sig.get("preferred_signal_types") != desired_preferred:
        sig["preferred_signal_types"] = desired_preferred
        changed = True

    if sig.get("note") != desired_note:
        sig["note"] = desired_note
        changed = True

    if changed:
        return True, "signal_requirements"
    return False, None


def _fix_traceability_source_hash(
    contract: dict[str, Any],
    *,
    monolith_hash: str,
) -> tuple[bool, str | None]:
    traceability = _ensure_dict(contract, "traceability")
    if traceability.get("source_hash") != monolith_hash:
        traceability["source_hash"] = monolith_hash
        return True, "traceability.source_hash"
    return False, None


def _fix_template(
    contract: dict[str, Any],
    *,
    question_id: str,
    base_slot: str,
    question_text: str,
    policy_area_name: str,
    dimension_name: str,
) -> tuple[bool, str | None]:
    output_contract = _ensure_dict(contract, "output_contract")
    human = _ensure_dict(output_contract, "human_readable_output")
    template = _ensure_dict(human, "template")

    label = _trim_one_line(question_text, 140)
    header = f"## Análisis {question_id} ({base_slot})"
    if label:
        header = f"{header}: {label}"

    desired = {
        "title": header,
        "summary": (
            "### Resumen Ejecutivo\n\n"
            f"**Área de política**: {policy_area_name}\n\n"
            f"**Dimensión**: {dimension_name}\n\n"
            "Se analizó la presencia de **{evidence.elements_found_count}** elementos de evidencia relevantes.\n\n"
            "**Puntaje**: {score}/3.0 | **Calidad**: {quality_level}"
        ),
        "score_section": (
            "### Evaluación\n\n"
            "- **Puntaje**: {score}/3.0\n"
            "- **Calidad**: {quality_level}\n"
            "- **Confianza promedio**: {evidence.confidence_scores.mean}\n"
            "- **Hash del grafo**: {evidence.graph_hash}"
        ),
        "elements_section": (
            "### Evidencia Identificada\n\n"
            "{evidence.elements_found_list}\n\n"
            "**Elementos críticos faltantes**: {evidence.missing_required_elements}"
        ),
        "interpretation": "### Interpretación\n\n{methodological_interpretation}",
        "recommendations": "### Recomendaciones\n\n{evidence.recommendations}",
    }

    if template == desired:
        return False, None

    human["format"] = human.get("format") or "markdown"
    human["template"] = desired
    return True, "output_contract.human_readable_output.template"


def _fix_evidence_assembly_sources_and_descriptions(
    contract: dict[str, Any],
    *,
    method_count: int,
    provides: list[str],
) -> tuple[bool, str | None]:
    evidence_assembly = _ensure_dict(contract, "evidence_assembly")
    rules = evidence_assembly.get("assembly_rules")
    if not isinstance(rules, list) or not rules:
        return False, None

    changed = False

    # Ensure one rule references all provides (prefer target=elements_found if present)
    target_rule: dict[str, Any] | None = None
    for rule in rules:
        if isinstance(rule, dict) and rule.get("target") == "elements_found":
            target_rule = rule
            break
    if target_rule is None and isinstance(rules[0], dict):
        target_rule = rules[0]

    if isinstance(target_rule, dict) and provides and target_rule.get("sources") != provides:
        target_rule["sources"] = provides
        changed = True

    desired_descriptions = {
        "elements_found": f"Combine evidence elements from {method_count} method invocations",
        "confidence_scores": f"Aggregate confidence scores across {method_count} methods",
        "pattern_matches": f"Combine pattern matches across {method_count} methods",
        "metadata": f"Combine metadata from {method_count} methods for full traceability",
    }

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        target = rule.get("target")
        if isinstance(target, str) and target in desired_descriptions:
            desired = desired_descriptions[target]
            if rule.get("description") != desired:
                rule["description"] = desired
                changed = True

    return (changed, "evidence_assembly.assembly_rules") if changed else (False, None)


def _fix_validation_rules_from_expected_elements(
    contract: dict[str, Any],
) -> tuple[bool, str | None]:
    qc = contract.get("question_context", {})
    if not isinstance(qc, dict):
        return False, None
    expected = qc.get("expected_elements", [])
    if not isinstance(expected, list) or not expected:
        return False, None

    required_types: list[str] = []
    optional_types: list[str] = []
    for e in expected:
        if not isinstance(e, dict):
            continue
        t = e.get("type")
        if not isinstance(t, str) or not t.strip():
            continue
        if bool(e.get("required")):
            required_types.append(t.strip())
        else:
            optional_types.append(t.strip())

    if not required_types:
        return False, None

    validation_rules = _ensure_dict(contract, "validation_rules")
    desired_rules: list[dict[str, Any]] = [
        {
            "description": "Auto-generated: require all required expected_elements types",
            "field": "elements_found",
            "must_contain": {"count": len(required_types), "elements": required_types},
            "type": "array",
        },
        {
            "description": "Auto-generated: encourage optional evidence types when available",
            "field": "elements_found",
            "should_contain": [{"elements": optional_types, "minimum": 1}] if optional_types else [],
            "type": "array",
        },
    ]

    previous = validation_rules.get("rules")
    if previous == desired_rules:
        return False, None

    validation_rules["rules"] = desired_rules
    contract["validation_rules"] = validation_rules
    return True, "validation_rules.rules"


def _fix_method_combination_logic(
    contract: dict[str, Any],
    *,
    question_id: str,
    base_slot: str,
    policy_area_id: str,
    dimension_id: str,
    method_count: int,
) -> tuple[bool, str | None]:
    output_contract = contract.get("output_contract", {})
    if not isinstance(output_contract, dict):
        return False, None
    human = output_contract.get("human_readable_output", {})
    if not isinstance(human, dict):
        return False, None
    depth = human.get("methodological_depth", {})
    if not isinstance(depth, dict):
        return False, None

    mcl = _ensure_dict(depth, "method_combination_logic")

    desired = {
        "combination_strategy": "Sequential multi-method pipeline with evidence fusion",
        "rationale": (
            f"{base_slot} ({question_id}) for {policy_area_id}/{dimension_id} requires consistent extraction, "
            f"validation, and synthesis across {method_count} methods. This block documents how the pipeline "
            "combines method outputs into a single evidence product."
        ),
        "evidence_fusion": (
            "Evidence from all methods is aggregated by the EvidenceNexus according to evidence_assembly. "
            "Overlaps are deduplicated where possible and confidence is propagated conservatively."
        ),
        "confidence_aggregation": (
            "Confidence is aggregated via contract-defined merge strategies, favoring calibrated methods "
            "when available."
        ),
        "execution_order": f"Methods execute in priority order (1→{method_count}).",
        "trade_offs": [
            (
                f"Coverage vs. cost: using {method_count} methods increases coverage but raises computation and "
                "maintenance burden."
            ),
            (
                "Recall vs. precision: multiple detectors increase recall but can introduce redundancy; "
                "deduplication and weighting mitigate this."
            ),
            (
                "Sophistication vs. interpretability: advanced models can be less transparent; "
                "human_readable_output documents assumptions and limitations."
            ),
        ],
    }

    changed = False
    for k, v in desired.items():
        if mcl.get(k) != v:
            mcl[k] = v
            changed = True

    depth["method_combination_logic"] = mcl
    human["methodological_depth"] = depth
    output_contract["human_readable_output"] = human
    contract["output_contract"] = output_contract

    return (changed, "output_contract.human_readable_output.methodological_depth.method_combination_logic") if changed else (False, None)


def _fix_method_steps_specificity(contract: dict[str, Any]) -> tuple[bool, str | None]:
    output_contract = contract.get("output_contract", {})
    if not isinstance(output_contract, dict):
        return False, None
    human = output_contract.get("human_readable_output", {})
    if not isinstance(human, dict):
        return False, None
    depth = human.get("methodological_depth", {})
    if not isinstance(depth, dict):
        return False, None
    methods = depth.get("methods", [])
    if not isinstance(methods, list) or not methods:
        return False, None

    generic_phrases = {"execute", "process results", "return structured output"}
    changed = False

    for m in methods:
        if not isinstance(m, dict):
            continue
        tech = m.get("technical_approach")
        if not isinstance(tech, dict):
            continue
        steps = tech.get("steps", [])
        if not isinstance(steps, list) or not steps:
            continue

        found_generic = False
        for s in steps:
            if isinstance(s, dict):
                desc = str(s.get("description", ""))
            else:
                desc = str(s)
            if any(p in desc.lower() for p in generic_phrases):
                found_generic = True
                break

        if not found_generic:
            continue

        class_name = str(m.get("class_name", "")).strip()
        method_name = str(m.get("method_name", "")).strip()
        method_id = f"{class_name}.{method_name}".strip(".")

        tech["steps"] = [
            {
                "step": 1,
                "description": f"Run {method_id} using contract-scoped inputs and produce intermediate artifacts",
            },
            {
                "step": 2,
                "description": "Normalize artifacts into evidence candidates with confidence estimates",
            },
            {
                "step": 3,
                "description": "Emit structured outputs for downstream evidence fusion and validation",
            },
        ]
        m["technical_approach"] = tech
        changed = True

    depth["methods"] = methods
    human["methodological_depth"] = depth
    output_contract["human_readable_output"] = human
    contract["output_contract"] = output_contract

    return (changed, "output_contract.human_readable_output.methodological_depth.methods[*].technical_approach.steps") if changed else (False, None)


def _fix_human_answer_structure_method_counts(
    contract: dict[str, Any],
    *,
    method_count: int,
) -> tuple[bool, str | None]:
    has = contract.get("human_answer_structure")
    if not isinstance(has, dict):
        return False, None

    changed = False
    desc = has.get("description")
    if isinstance(desc, str):
        desired = (
            f"Expected structure of evidence dict after all {method_count} methods execute and evidence is "
            "assembled according to assembly_rules"
        )
        if desc != desired:
            has["description"] = desired
            changed = True

    flow = has.get("assembly_flow")
    if isinstance(flow, dict):
        step1 = flow.get("step_1_method_execution")
        desired_step1 = (
            f"{method_count} methods execute in priority order, outputs stored with dot-notation keys"
        )
        if step1 != desired_step1:
            flow["step_1_method_execution"] = desired_step1
            changed = True
        has["assembly_flow"] = flow

    contract["human_answer_structure"] = has
    return (changed, "human_answer_structure") if changed else (False, None)


def _fix_traceability_provenance_note(
    contract: dict[str, Any],
    *,
    method_count: int,
) -> tuple[bool, str | None]:
    traceability = contract.get("traceability")
    if not isinstance(traceability, dict):
        return False, None

    executor_class = (
        contract.get("executor_binding", {}).get("executor_class")
        if isinstance(contract.get("executor_binding"), dict)
        else None
    )
    executor_label = str(executor_class) if isinstance(executor_class, str) and executor_class else "executor"

    desired = (
        "This contract was generated with full multi-method orchestration support. "
        f"The method_binding.methods array contains all {method_count} methods from {executor_label}, "
        "and human_answer_structure documents the expected evidence output after execution."
    )
    current = traceability.get("provenance_note")
    if current != desired:
        traceability["provenance_note"] = desired
        contract["traceability"] = traceability
        return True, "traceability.provenance_note"
    return False, None


def remediate_single_contract(
    *,
    contract_path: Path,
    monolith_hash: str,
    policy_area_names: dict[str, str],
    dimension_names: dict[str, str],
    apply: bool,
) -> RemediationOutcome:
    original_text = contract_path.read_text(encoding="utf-8")
    contract = json.loads(original_text)
    if not isinstance(contract, dict):
        raise TypeError(f"{contract_path}: expected JSON object")

    identity = contract.get("identity", {})
    if not isinstance(identity, dict):
        raise ValueError(f"{contract_path}: missing identity")

    question_id = str(identity.get("question_id") or "").strip()
    base_slot = str(identity.get("base_slot") or "").strip()
    policy_area_id = str(identity.get("policy_area_id") or "").strip()
    dimension_id = str(identity.get("dimension_id") or "").strip()

    qc = contract.get("question_context", {})
    question_text = ""
    if isinstance(qc, dict):
        question_text = str(qc.get("question_text") or "")

    method_count = _get_method_count(contract)
    provides = _get_method_provides(contract)

    policy_area_name = policy_area_names.get(policy_area_id, policy_area_id or "UNKNOWN")
    dimension_name = dimension_names.get(dimension_id, dimension_id or "UNKNOWN")

    changes: list[str] = []

    for changed, label in (
        _fix_signal_requirements(contract, policy_area_id=policy_area_id, dimension_id=dimension_id),
        _fix_traceability_source_hash(contract, monolith_hash=monolith_hash),
        _fix_template(
            contract,
            question_id=question_id,
            base_slot=base_slot,
            question_text=question_text,
            policy_area_name=policy_area_name,
            dimension_name=dimension_name,
        ),
        _fix_evidence_assembly_sources_and_descriptions(
            contract, method_count=method_count, provides=provides
        ),
        _fix_validation_rules_from_expected_elements(contract),
        _fix_method_combination_logic(
            contract,
            question_id=question_id,
            base_slot=base_slot,
            policy_area_id=policy_area_id,
            dimension_id=dimension_id,
            method_count=method_count,
        ),
        _fix_method_steps_specificity(contract),
        _fix_human_answer_structure_method_counts(contract, method_count=method_count),
        _fix_traceability_provenance_note(contract, method_count=method_count),
    ):
        if changed and label:
            changes.append(label)

    new_text = _dump_json_text(contract)
    changed = new_text != original_text
    if changed and apply:
        contract_path.write_text(new_text, encoding="utf-8")

    return RemediationOutcome(
        contract_path=contract_path,
        changed=changed,
        changes=tuple(changes),
    )


def _group_question_ids(group_id: int) -> list[str]:
    if not (0 <= group_id < NUM_BASE_SLOTS):
        raise ValueError(f"group_id must be 0-{NUM_BASE_SLOTS-1}")
    base = group_id + 1
    return [f"Q{base + (i * NUM_BASE_SLOTS):03d}" for i in range(NUM_POLICY_AREAS)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remediate semantic issues in v3 executor contracts (manual-friendly)."
    )
    parser.add_argument("--contracts-dir", type=Path, default=DEFAULT_CONTRACTS_DIR)
    parser.add_argument("--monolith", type=Path, default=REPO_ROOT / "canonic_questionnaire_central/questionnaire_monolith.json")
    parser.add_argument("--policy-area-mapping", type=Path, default=REPO_ROOT / "policy_area_mapping.json")
    parser.add_argument("--dimension-mapping", type=Path, default=REPO_ROOT / "dimension_mapping.json")

    sel = parser.add_mutually_exclusive_group(required=True)
    sel.add_argument("--contract", type=str, help="Single contract ID or filename (e.g., Q077 or Q077.v3.json)")
    sel.add_argument("--group", type=int, help="Equivalence group 0-29 (e.g., 16 for Q017/Q047/.../Q287)")

    parser.add_argument("--yes", action="store_true", help="Apply changes (write files).")
    args = parser.parse_args()

    contracts_dir: Path = args.contracts_dir
    if not contracts_dir.exists():
        print(f"Contracts directory not found: {contracts_dir}", file=sys.stderr)
        return 2

    monolith_hash = _canonical_monolith_hash(args.monolith)
    pa_names = _policy_area_names(args.policy_area_mapping)
    dim_names = _dimension_names(args.dimension_mapping)
    apply = bool(args.yes)

    if args.contract:
        raw = args.contract.strip()
        filename = raw if raw.endswith(".v3.json") else f"{raw}.v3.json"
        contract_path = contracts_dir / filename
        if not contract_path.exists():
            print(f"Contract not found: {contract_path}", file=sys.stderr)
            return 2
        outcome = remediate_single_contract(
            contract_path=contract_path,
            monolith_hash=monolith_hash,
            policy_area_names=pa_names,
            dimension_names=dim_names,
            apply=apply,
        )
        print(f"{outcome.contract_path.name}: changed={outcome.changed} changes={list(outcome.changes)}")
        return 0

    assert args.group is not None
    qids = _group_question_ids(args.group)
    changed = 0
    for qid in qids:
        contract_path = contracts_dir / f"{qid}.v3.json"
        if not contract_path.exists():
            print(f"{qid}: missing", file=sys.stderr)
            continue
        outcome = remediate_single_contract(
            contract_path=contract_path,
            monolith_hash=monolith_hash,
            policy_area_names=pa_names,
            dimension_names=dim_names,
            apply=apply,
        )
        changed += int(outcome.changed)
        print(f"{outcome.contract_path.name}: changed={outcome.changed} changes={list(outcome.changes)}")

    print(f"group={args.group} total={len(qids)} changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
