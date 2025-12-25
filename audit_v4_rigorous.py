#!/usr/bin/env python3
"""
audit_v4_rigorous.py
====================
Local, strict auditor for FARFAN v4 epistemological executor contracts.

This script is intentionally self-contained and deterministic:
- Loads each contract JSON
- Runs the existing V4 auditor (src/farfan_pipeline/scripts/audit_validator.py)
- Applies additional strict checks needed by the V4 checklist invariants

Exit codes:
- 0: all contracts pass
- 1: at least one contract fails
- 2: invalid usage / missing file(s)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, TypeAlias, cast


REPO_ROOT = Path(__file__).resolve().parent


JSONPrimitive: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONPrimitive | dict[str, "JSONValue"] | list["JSONValue"]
JSONObject: TypeAlias = dict[str, JSONValue]


INVARIANT_PATHS: tuple[str, ...] = (
    "method_binding.execution_phases",
    "evidence_assembly",
    "fusion_specification",
    "cross_layer_fusion",
    "human_answer_structure",
    "validation_rules",
    "error_handling",
)


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    inferred_type: dict[str, JSONValue]


def _extract_json_path(contract: JSONObject, path: str) -> JSONValue:
    cur: JSONValue = contract
    for part in path.split("."):
        if not isinstance(cur, dict):
            raise KeyError(f"Path '{path}' breaks at '{part}': not a dict")
        if part not in cur:
            raise KeyError(f"Missing path '{path}': '{part}' not found")
        cur = cur[part]
    return cur


def compute_invariant_hashes(contract: JSONObject) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in INVARIANT_PATHS:
        subtree = _extract_json_path(contract, path)
        canonical_json = json.dumps(subtree, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        hashes[path] = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return hashes


def infer_contract_type(contract: JSONObject) -> dict[str, JSONValue]:
    # Matches the spec inference mapping; non-matching classes simply contribute 0.
    mb_val = contract.get("method_binding")
    if not isinstance(mb_val, dict):
        return {"type": "UNKNOWN", "confidence": 0.0, "distribution": {}, "total_methods": 0}
    phases_val = mb_val.get("execution_phases")
    if not isinstance(phases_val, dict):
        return {"type": "UNKNOWN", "confidence": 0.0, "distribution": {}, "total_methods": 0}

    all_methods: list[JSONObject] = []
    for phase_v in phases_val.values():
        if not isinstance(phase_v, dict):
            continue
        methods_v = phase_v.get("methods")
        if not isinstance(methods_v, list):
            continue
        for m in methods_v:
            if isinstance(m, dict):
                all_methods.append(m)

    class_counts: dict[str, int] = {}
    for m in all_methods:
        class_name_v = m.get("class_name")
        class_name = class_name_v if isinstance(class_name_v, str) else ""
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    type_scores: dict[str, int] = {
        "TYPE_A": sum(class_counts.get(c, 0) for c in ["SemanticAnalyzer", "SemanticProcessor", "TextMiningEngine"]),
        "TYPE_B": sum(
            class_counts.get(c, 0)
            for c in [
                "BayesianNumericalAnalyzer",
                "AdaptivePriorCalculator",
                "HierarchicalGenerativeModel",
                "BayesianMechanismInference",
            ]
        ),
        "TYPE_C": sum(class_counts.get(c, 0) for c in ["CausalExtractor", "TeoriaCambio", "AdvancedDAGValidator"]),
        "TYPE_D": sum(class_counts.get(c, 0) for c in ["FinancialAuditor", "PDETMunicipalPlanAnalyzer"]),
        "TYPE_E": sum(
            class_counts.get(c, 0)
            for c in ["PolicyContradictionDetector", "IndustrialGradeValidator", "OperationalizationAuditor"]
        ),
    }
    dist: dict[str, JSONValue] = {k: v for k, v in type_scores.items()}
    total = sum(type_scores.values())
    if total == 0:
        return {"type": "UNKNOWN", "confidence": 0.0, "distribution": dist, "total_methods": len(all_methods)}

    best_type = max(type_scores, key=type_scores.__getitem__)
    confidence = (type_scores[best_type] / total) if total else 0.0
    return {
        "type": best_type,
        "confidence": confidence,
        "distribution": dist,
        "total_methods": len(all_methods),
    }


def _get_section_by_id(sections: list[JSONObject], section_id: str) -> JSONObject | None:
    for s in sections:
        if s.get("section_id") == section_id:
            return s
    return None


def validate_epistemological_structure(contract: JSONObject) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    identity_v = contract.get("identity")
    identity: JSONObject = identity_v if isinstance(identity_v, dict) else {}
    mb_v = contract.get("method_binding")
    mb: JSONObject = mb_v if isinstance(mb_v, dict) else {}
    phases_v = mb.get("execution_phases")
    phases: JSONObject = phases_v if isinstance(phases_v, dict) else {}
    ea_v = contract.get("evidence_assembly")
    ea: JSONObject = ea_v if isinstance(ea_v, dict) else {}
    clf_v = contract.get("cross_layer_fusion")
    clf: JSONObject = clf_v if isinstance(clf_v, dict) else {}
    fs_v = contract.get("fusion_specification")
    fs: JSONObject = fs_v if isinstance(fs_v, dict) else {}
    ha_v = contract.get("human_answer_structure")
    ha: JSONObject = ha_v if isinstance(ha_v, dict) else {}

    # --- Structural must-haves (subset of checklist Section 0) ---
    required_paths = [
        ("identity.contract_type", ("identity", "contract_type")),
        ("identity.base_slot", ("identity", "base_slot")),
        ("method_binding.orchestration_mode", ("method_binding", "orchestration_mode")),
        ("method_binding.contract_type", ("method_binding", "contract_type")),
        ("method_binding.execution_phases", ("method_binding", "execution_phases")),
        ("evidence_assembly.type_system", ("evidence_assembly", "type_system")),
        ("evidence_assembly.assembly_rules", ("evidence_assembly", "assembly_rules")),
        ("fusion_specification.contract_type", ("fusion_specification", "contract_type")),
        ("fusion_specification.level_strategies", ("fusion_specification", "level_strategies")),
        ("cross_layer_fusion", ("cross_layer_fusion",)),
        ("human_answer_structure.sections", ("human_answer_structure", "sections")),
    ]
    for label, p in required_paths:
        cur: JSONValue = contract
        ok = True
        for k in p:
            if not isinstance(cur, dict) or k not in cur:
                ok = False
                break
            cur = cur[k]
        if not ok:
            errors.append(f"Missing required field: {label}")

    # --- Version must be epistemological v4 ---
    contract_version_v = identity.get("contract_version")
    version = contract_version_v if isinstance(contract_version_v, str) else ""
    if "epistemological" not in version:
        errors.append(f"identity.contract_version must contain 'epistemological', got {version!r}")

    # --- Orchestration mode strict ---
    orch = mb.get("orchestration_mode")
    if orch != "epistemological_pipeline":
        errors.append(f"method_binding.orchestration_mode must be 'epistemological_pipeline', got {orch!r}")

    # --- Phases exist and are only A/B/C ---
    if "phase_A_construction" not in phases:
        errors.append("Missing phase_A_construction (N1)")
    if "phase_B_computation" not in phases:
        errors.append("Missing phase_B_computation (N2)")
    if "phase_C_litigation" not in phases:
        errors.append("Missing phase_C_litigation (N3)")
    extra_phases = set(phases.keys()) - {"phase_A_construction", "phase_B_computation", "phase_C_litigation"}
    if extra_phases:
        errors.append(f"INVALID: extra phases present: {sorted(extra_phases)}")

    # --- Methods have correct epistemological levels & required fields (PARTE II) ---
    expected_level_by_phase = {
        "phase_A_construction": ("N1-EMP", "FACT", "additive"),
        "phase_B_computation": ("N2-INF", "PARAMETER", "multiplicative"),
        "phase_C_litigation": ("N3-AUD", "CONSTRAINT", "gate"),
    }
    for phase_name, (lvl, out_t, fusion_b) in expected_level_by_phase.items():
        phase_v = phases.get(phase_name)
        phase = phase_v if isinstance(phase_v, dict) else {}
        methods_v = phase.get("methods")
        methods = methods_v if isinstance(methods_v, list) else None
        if methods is None:
            errors.append(f"{phase_name}.methods must be an array")
            continue
        for m in methods:
            if not isinstance(m, dict):
                errors.append(f"{phase_name} contains non-object method entry")
                continue
            # Required common fields (PARTE II 2.2)
            for k in ["class_name", "method_name", "mother_file", "provides", "description"]:
                if not isinstance(m.get(k), str) or not str(m.get(k)).strip():
                    errors.append(f"{phase_name} method missing/invalid field: {k}")
            if m.get("level") != lvl:
                errors.append(f"Method {m.get('method_name')} has wrong level in {phase_name}: {m.get('level')}")
            if m.get("output_type") != out_t:
                errors.append(
                    f"Method {m.get('method_name')} has wrong output_type in {phase_name}: {m.get('output_type')}"
                )
            if m.get("fusion_behavior") != fusion_b:
                errors.append(
                    f"Method {m.get('method_name')} has wrong fusion_behavior in {phase_name}: {m.get('fusion_behavior')}"
                )
            # Phase-specific required fields (PARTE II)
            if lvl == "N1-EMP":
                if m.get("requires") != []:
                    errors.append(f"N1 method {m.get('method_name')} requires must be []")
            if lvl == "N2-INF":
                reqs = m.get("requires")
                if not isinstance(reqs, list) or not reqs:
                    errors.append(f"N2 method {m.get('method_name')} requires must be a non-empty array")
                else:
                    # PARTE II: typically requires raw_facts; allow PreprocesadoMetadata as direct input
                    req_set = {x for x in reqs if isinstance(x, str)}
                    if not ({"raw_facts", "PreprocesadoMetadata"} & req_set):
                        errors.append(
                            f"N2 method {m.get('method_name')} requires must include raw_facts or PreprocesadoMetadata"
                        )
                mods = m.get("modifies")
                if not isinstance(mods, list) or not mods:
                    errors.append(f"N2 method {m.get('method_name')} missing modifies (non-empty array)")
            if lvl == "N3-AUD":
                reqs = m.get("requires")
                if not isinstance(reqs, list) or not reqs:
                    errors.append(f"N3 method {m.get('method_name')} requires must be a non-empty array")
                else:
                    req_set = {x for x in reqs if isinstance(x, str)}
                    if not {"raw_facts", "inferences"}.issubset(req_set):
                        errors.append(f"N3 method {m.get('method_name')} requires must include raw_facts and inferences")
                modulates = m.get("modulates")
                if not isinstance(modulates, list) or not modulates:
                    errors.append(f"N3 method {m.get('method_name')} missing modulates (non-empty array)")
                veto = m.get("veto_conditions")
                if not isinstance(veto, dict) or not veto:
                    errors.append(f"N3 method {m.get('method_name')} missing veto_conditions (non-empty object)")
                else:
                    allowed_actions = {
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
                    for cond_name, cond in veto.items():
                        if not cond_name.strip():
                            errors.append(f"N3 veto condition has invalid name: {cond_name!r}")
                        if not isinstance(cond, dict):
                            errors.append(f"N3 veto condition {cond_name} must be an object")
                            continue
                        for k in ["trigger", "action", "scope", "confidence_multiplier"]:
                            if k not in cond:
                                errors.append(f"N3 veto condition {cond_name} missing field: {k}")
                        action = cond.get("action")
                        if isinstance(action, str) and action not in allowed_actions:
                            errors.append(f"N3 veto condition {cond_name} action invalid: {action!r}")
                        try:
                            cm_v = cond.get("confidence_multiplier")
                            cm = float(cm_v)  # type: ignore[arg-type]
                            if not (0.0 <= cm <= 1.0):
                                errors.append(f"N3 veto condition {cond_name} confidence_multiplier out of [0,1]: {cm}")
                        except Exception:
                            errors.append(f"N3 veto condition {cond_name} confidence_multiplier must be a number")

    # --- Assembly rules (exactly 4, R3 veto_gate) ---
    assembly_rules_v = ea.get("assembly_rules")
    assembly_rules = assembly_rules_v if isinstance(assembly_rules_v, list) else None
    if assembly_rules is None:
        errors.append("evidence_assembly.assembly_rules must be an array")
    else:
        if len(assembly_rules) != 4:
            errors.append(f"Expected 4 assembly rules, got {len(assembly_rules)}")
        # Rule id prefixes and positional invariants (checklist 3.6)
        expected_prefixes = ["R1_", "R2_", "R3_", "R4_"]
        for idx, prefix in enumerate(expected_prefixes):
            if len(assembly_rules) <= idx:
                errors.append(f"Missing assembly_rules[{idx}] ({prefix}...)")
                continue
            rule_v = assembly_rules[idx]
            if not isinstance(rule_v, dict):
                errors.append(f"Missing assembly_rules[{idx}] ({prefix}...)")
                continue
            rid = rule_v.get("rule_id")
            if not isinstance(rid, str) or not rid.startswith(prefix):
                errors.append(f"assembly_rules[{idx}].rule_id must start with {prefix!r}, got {rid!r}")
        # R3 must be veto gate
        if len(assembly_rules) >= 3 and isinstance(assembly_rules[2], dict):
            r3 = assembly_rules[2]
            if r3.get("merge_strategy") != "veto_gate":
                errors.append(f"R3 merge_strategy must be veto_gate, got {r3.get('merge_strategy')}")
            gate_logic = r3.get("gate_logic")
            if not isinstance(gate_logic, dict) or not gate_logic:
                errors.append("R3.gate_logic must be a non-empty object")

    # --- N3 asymmetry relationships (PARTE V) ---
    # episte_refact.md provides canonical strings, but contracts may specialize the wording
    # (e.g. "N2 reads N1 budget facts"). We enforce "mentions" semantics (contains) +
    # exact data_flow invariants.
    required_relations: dict[str, dict[str, str]] = {
        "N1_to_N2": {
            "relationship_contains": "N2 reads N1",
            "data_flow": "forward_propagation",
        },
        "N2_to_N1": {
            "relationship_contains": "N2 modifies N1",
            "data_flow": "confidence_backpropagation",
        },
        "N3_to_N1": {
            "relationship_contains": "N3 can BLOCK N1",
            "data_flow": "veto_propagation",
        },
        "N3_to_N2": {
            "relationship_contains": "N3 can INVALIDATE N2",
            "data_flow": "inference_modulation",
        },
        "all_to_N4": {
            "relationship_contains": "N4 consumes",
            "data_flow": "terminal_aggregation",
        },
    }
    for rel, expected in required_relations.items():
        node = clf.get(rel)
        if not isinstance(node, dict):
            errors.append(f"Missing cross_layer_fusion.{rel}")
            continue
        rel_text_v = node.get("relationship")
        rel_text = rel_text_v if isinstance(rel_text_v, str) else ""
        needle = expected["relationship_contains"]
        if needle not in rel_text:
            errors.append(f"cross_layer_fusion.{rel}.relationship must mention {needle!r}, got {rel_text!r}")
        if node.get("data_flow") != expected["data_flow"]:
            errors.append(
                f"cross_layer_fusion.{rel}.data_flow must be {expected['data_flow']!r}, got {node.get('data_flow')!r}"
            )

    n3_to_n1 = clf.get("N3_to_N1")
    n3_to_n2 = clf.get("N3_to_N2")
    if not isinstance(n3_to_n1, dict):
        errors.append("Missing or invalid N3_to_N1 relationship")
    else:
        asym = n3_to_n1.get("asymmetry", "")
        if "N1 CANNOT invalidate N3" not in str(asym):
            errors.append("N3_to_N1 asymmetry incorrectly declared")
    if not isinstance(n3_to_n2, dict):
        errors.append("Missing or invalid N3_to_N2 relationship")
    else:
        asym = n3_to_n2.get("asymmetry", "")
        if "N2 CANNOT invalidate N3" not in str(asym):
            errors.append("N3_to_N2 asymmetry incorrectly declared")
    if "N1_to_N3" in clf:
        errors.append("INVALID: N1_to_N3 exists (breaks asymmetry)")
    if "N2_to_N3" in clf:
        errors.append("INVALID: N2_to_N3 exists (breaks asymmetry)")
    bpr = clf.get("blocking_propagation_rules")
    if not isinstance(bpr, dict) or len(bpr) < 2:
        errors.append("cross_layer_fusion.blocking_propagation_rules must be an object with at least 2 rules")

    # --- Human answer S3 veto display ---
    sections_v = ha.get("sections")
    sections = sections_v if isinstance(sections_v, list) else None
    if sections is None:
        errors.append("human_answer_structure.sections must be an array")
    else:
        sections_dicts = [s for s in sections if isinstance(s, dict)]
        s3 = _get_section_by_id(sections_dicts, "S3_robustness_audit")
        if not s3:
            errors.append("Missing S3_robustness_audit section")
        else:
            veto_display = s3.get("veto_display")
            if not isinstance(veto_display, dict):
                errors.append("Missing veto_display in S3_robustness_audit")
            else:
                if "if_veto_triggered" not in veto_display:
                    errors.append("Missing if_veto_triggered in veto_display")
                if "if_no_veto" not in veto_display:
                    errors.append("Missing if_no_veto in veto_display")
                # PARTE VI example uses "⚠️ ALERTA" and "INVÁLIDO"
                iv = str(veto_display.get("if_veto_triggered", ""))
                if "ALERTA" not in iv or "INVÁLIDO" not in iv:
                    warnings.append("S3.veto_display.if_veto_triggered should contain 'ALERTA' and 'INVÁLIDO'")

    # --- Type consistency (identity/method_binding/fusion_specification/human_answer_structure) ---
    identity_ct_v = identity.get("contract_type")
    mb_ct_v = mb.get("contract_type")
    fs_ct_v = fs.get("contract_type")
    ha_ct_v = ha.get("contract_type")
    declared_types = {
        "identity": identity_ct_v if isinstance(identity_ct_v, str) else None,
        "method_binding": mb_ct_v if isinstance(mb_ct_v, str) else None,
        "fusion_specification": fs_ct_v if isinstance(fs_ct_v, str) else None,
        "human_answer": ha_ct_v if isinstance(ha_ct_v, str) else None,
    }
    unique_types: set[str] = {t for t in declared_types.values() if isinstance(t, str)}
    if len(unique_types) > 1:
        errors.append(f"Inconsistent contract_type declarations: {declared_types}")

    inferred = infer_contract_type(contract)

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings, inferred_type=inferred)


def compute_file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> JSONObject:
    with path.open("r", encoding="utf-8") as f:
        data = cast(JSONValue, json.load(f))
    if not isinstance(data, dict):
        raise ValueError(f"Contract JSON must be an object at top-level: {path}")
    return data


def audit_paths(paths: Iterable[Path]) -> tuple[bool, dict[str, JSONValue]]:
    failures: list[dict[str, JSONValue]] = []
    warnings: list[dict[str, JSONValue]] = []
    passed_count = 0
    total = 0

    for p in paths:
        total += 1
        try:
            contract = _load_json(p)
        except Exception as e:
            failures.append({"path": str(p), "error": f"JSON load failed: {type(e).__name__}: {e}"})
            continue

        validation = validate_epistemological_structure(contract)
        if not validation.valid:
            errs_json: list[JSONValue] = [e for e in validation.errors]
            failures.append({"path": str(p), "errors": errs_json})
        else:
            passed_count += 1
        for w in validation.warnings:
            warnings.append({"path": str(p), "warning": w})

    failures_json: list[JSONValue] = [f for f in failures]
    warnings_json: list[JSONValue] = [w for w in warnings]
    summary: dict[str, JSONValue] = {
        "audit_version": "v4_rigorous_local",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "passed": passed_count,
        "failed": len(failures),
        "failures": failures_json,
        "warnings": warnings_json,
    }
    return (len(failures) == 0), summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contracts", nargs="*", help="Paths to v4 contract JSON files")
    args = parser.parse_args()

    contracts = cast(list[str], getattr(args, "contracts", []))
    if not contracts:
        print("No contract paths provided.", file=sys.stderr)
        return 2

    paths: list[Path] = [Path(p).expanduser().resolve() for p in contracts]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print("Missing contract file(s):", file=sys.stderr)
        for m in missing:
            print(f"- {m}", file=sys.stderr)
        return 2

    ok, summary = audit_paths(paths)
    if not ok:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


