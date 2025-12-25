#!/usr/bin/env python3
"""
contract_factory_v4.2.py
========================
Deterministic batch instantiation of v4 epistemological contracts.

Generates 270 contracts for:
  PA02..PA10 × Q001..Q030

Outputs:
  contracts_v4/expansion/{policy_area_id}/{Q###}.v4.json
  contracts_v4/expansion/manifest_{YYYY-MM-DD_HHMMSS}.json

Hard constraints:
- Abort on first error (strict)
- Do NOT modify canonical templates
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_v4_rigorous import compute_file_hash, compute_invariant_hashes, validate_epistemological_structure


REPO_ROOT = Path(__file__).resolve().parent

TEMPLATE_DIR = (
    REPO_ROOT
    / "src"
    / "farfan_pipeline"
    / "phases"
    / "Phase_two"
    / "json_files_phase_two"
    / "executor_contracts"
    / "v4"
    / "contracts_v4"
)
CHECKLIST_PATH = TEMPLATE_DIR / "CHECKLIST"

POLICY_AREA_MAPPING_PATH = REPO_ROOT / "policy_area_mapping.json"
QUESTIONNAIRE_MONOLITH_PATH = REPO_ROOT / "canonic_questionnaire_central" / "questionnaire_monolith.json"
EPISTE_GUIDE_PATH = REPO_ROOT / "episte_refact.md"

OUTPUT_ROOT = REPO_ROOT / "contracts_v4" / "expansion"

TARGET_POLICY_AREAS: tuple[str, ...] = ("PA02", "PA03", "PA04", "PA05", "PA06", "PA07", "PA08", "PA09", "PA10")
SLOTS: tuple[str, ...] = tuple(f"Q{i:03d}" for i in range(1, 31))


@dataclass
class AuditLog:
    generated_files: list[str] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    schema_valid_count: int = 0
    epistemological_valid_count: int = 0
    invariants_preserved_count: int = 0
    type_consistent_count: int = 0

    total_n1_methods: int = 0
    total_n2_methods: int = 0
    total_n3_methods: int = 0

    contracts_with_veto_gates: int = 0
    contracts_with_asymmetry: int = 0
    contracts_with_four_levels: int = 0
    contracts_with_veto_display: int = 0

    per_file: dict[str, dict[str, Any]] = field(default_factory=dict)

    def record_success(self, path: str, invariant_hashes: dict[str, str], inferred_type: dict[str, Any]) -> None:
        self.generated_files.append(path)
        self.per_file[path] = {
            "invariant_hashes": invariant_hashes,
            "inferred_type": inferred_type,
        }

    def record_failure(self, policy_area_id: str, slot_id: str, error: str) -> None:
        self.failures.append({"policy_area_id": policy_area_id, "slot_id": slot_id, "error": error})

    def record_warning(self, path: str, warning: str) -> None:
        self.warnings.append({"path": path, "warning": warning})

    def get_pass_rate(self) -> float:
        total = len(self.generated_files) + len(self.failures)
        return (len(self.generated_files) / total) if total else 0.0

    def get_overall_score(self) -> float:
        # Strict mode: any failure means 0.0; otherwise 1.0.
        return 1.0 if not self.failures else 0.0


def _utc_now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _load_policy_area_mapping() -> dict[str, str]:
    raw = _load_json(POLICY_AREA_MAPPING_PATH)
    if not isinstance(raw, list):
        raise ValueError("policy_area_mapping.json must be a list")

    mapping: dict[str, str] = {}
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        cid = str(entry.get("canonical_id", "")).strip()
        cname = str(entry.get("canonical_name", "")).strip()
        if cid and cname:
            mapping[cid] = cname

    return mapping


def _count_methods_by_level(contract: dict[str, Any], level: str) -> int:
    phases = contract.get("method_binding", {}).get("execution_phases", {})
    if not isinstance(phases, dict):
        return 0
    count = 0
    for phase in phases.values():
        if not isinstance(phase, dict):
            continue
        methods = phase.get("methods", [])
        if not isinstance(methods, list):
            continue
        for m in methods:
            if isinstance(m, dict) and m.get("level") == level:
                count += 1
    return count


def _check_veto_gate_exists(contract: dict[str, Any]) -> bool:
    rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
    if not isinstance(rules, list) or len(rules) < 3:
        return False
    r3 = rules[2]
    return isinstance(r3, dict) and r3.get("merge_strategy") == "veto_gate"


def _check_n3_asymmetry(contract: dict[str, Any]) -> bool:
    clf = contract.get("cross_layer_fusion", {})
    if not isinstance(clf, dict):
        return False
    n3_to_n1 = clf.get("N3_to_N1", {})
    n3_to_n2 = clf.get("N3_to_N2", {})
    if not isinstance(n3_to_n1, dict) or not isinstance(n3_to_n2, dict):
        return False
    a1 = str(n3_to_n1.get("asymmetry", ""))
    a2 = str(n3_to_n2.get("asymmetry", ""))
    return ("N1 CANNOT invalidate N3" in a1) and ("N2 CANNOT invalidate N3" in a2) and ("N1_to_N3" not in clf) and (
        "N2_to_N3" not in clf
    )


def _check_four_levels_present(contract: dict[str, Any]) -> bool:
    ts = contract.get("evidence_assembly", {}).get("type_system", {})
    if not isinstance(ts, dict):
        return False
    required_types = {"FACT", "PARAMETER", "CONSTRAINT", "NARRATIVE"}
    return required_types.issubset(set(ts.keys()))


def _check_veto_display_present(contract: dict[str, Any]) -> bool:
    sections = contract.get("human_answer_structure", {}).get("sections", [])
    if not isinstance(sections, list):
        return False
    for s in sections:
        if isinstance(s, dict) and s.get("section_id") == "S3_robustness_audit":
            vd = s.get("veto_display", {})
            return isinstance(vd, dict) and ("if_veto_triggered" in vd) and ("if_no_veto" in vd)
    return False


def _preflight_check() -> None:
    required = [
        ("policy_area_mapping.json", POLICY_AREA_MAPPING_PATH),
        ("questionnaire_monolith.json", QUESTIONNAIRE_MONOLITH_PATH),
        ("episte_refact.md", EPISTE_GUIDE_PATH),
        ("templates_dir", TEMPLATE_DIR),
        ("validation_checklist", CHECKLIST_PATH),
    ]
    missing = [(name, str(path)) for name, path in required if not path.exists()]
    if missing:
        # Mirror the spec's abort policy via a hard failure.
        detail = "\n".join([f"- {n}: {p}" for n, p in missing])
        raise FileNotFoundError(f"Missing required inputs:\n{detail}")


def _load_templates() -> dict[str, dict[str, Any]]:
    templates: dict[str, dict[str, Any]] = {}
    json_files = sorted([p for p in TEMPLATE_DIR.glob("*.json") if p.name != "CHECKLIST"])
    if len(json_files) != 30:
        raise ValueError(f"Expected 30 canonical templates in {TEMPLATE_DIR}, got {len(json_files)}")

    for p in json_files:
        contract = _load_json(p)
        slot = contract.get("identity", {}).get("representative_question_id")
        if not isinstance(slot, str) or not slot.startswith("Q") or len(slot) != 4:
            raise ValueError(f"Template {p} missing/invalid identity.representative_question_id: {slot}")

        if slot in templates:
            raise ValueError(f"Duplicate representative_question_id {slot} across templates")

        validation = validate_epistemological_structure(contract)
        if not validation.valid:
            raise ValueError(f"Template {p.name} fails epistemological validation: {validation.errors}")

        templates[slot] = contract

    missing_slots = [s for s in SLOTS if s not in templates]
    if missing_slots:
        raise ValueError(f"Templates missing required slots: {missing_slots}")

    return templates


def _instantiate_contract(
    template: dict[str, Any],
    policy_area_id: str,
    policy_area_name: str,
    template_hashes: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    instance: dict[str, Any] = json.loads(json.dumps(template))

    identity = instance.setdefault("identity", {})
    if not isinstance(identity, dict):
        raise ValueError("identity must be an object")

    # Allowed delta: bind contract to a single policy area
    identity["policy_area_id"] = policy_area_id
    identity["policy_area_name"] = policy_area_name
    if "policy_area_ids_served" in identity and isinstance(identity.get("policy_area_ids_served"), list):
        identity["policy_area_ids_served"] = [policy_area_id]

    # Traceability generation metadata
    trace = instance.setdefault("traceability", {})
    if not isinstance(trace, dict):
        raise ValueError("traceability must be an object")
    gen = trace.setdefault("generation", {})
    if not isinstance(gen, dict):
        raise ValueError("traceability.generation must be an object")
    gen["timestamp"] = _utc_now_iso_z()
    gen["generator_version"] = "BatchFactory-V4.2-Epistemological"

    # Invariant hash check (must not drift)
    instance_hashes = compute_invariant_hashes(instance)
    for path, expected_hash in template_hashes.items():
        if instance_hashes.get(path) != expected_hash:
            raise ValueError(f"Invariant violation at {path}: hash mismatch")

    # Epistemological validation (strict)
    validation = validate_epistemological_structure(instance)
    if not validation.valid:
        raise ValueError(f"Epistemological validation failed: {validation.errors}")

    # PA01 residue detection (strict)
    if "PA01" in json.dumps(instance, ensure_ascii=False):
        raise ValueError("PA01 residue detected in instance")

    return instance, validation.inferred_type


def _final_validation(generated_paths: list[Path], audit_log: AuditLog) -> None:
    if len(generated_paths) != 270:
        raise ValueError(f"Expected 270 contracts, got {len(generated_paths)}")

    for p in generated_paths:
        contract = _load_json(p)
        validation = validate_epistemological_structure(contract)
        if not validation.valid:
            raise ValueError(f"Contract {p} failed validation: {validation.errors}")

        pa = contract.get("identity", {}).get("policy_area_id")
        if pa == "PA01":
            raise ValueError(f"PA01 found as identity.policy_area_id in {p}")

        n1 = _count_methods_by_level(contract, "N1-EMP")
        n2 = _count_methods_by_level(contract, "N2-INF")
        n3 = _count_methods_by_level(contract, "N3-AUD")
        audit_log.total_n1_methods += n1
        audit_log.total_n2_methods += n2
        audit_log.total_n3_methods += n3

        if _check_veto_gate_exists(contract):
            audit_log.contracts_with_veto_gates += 1
        if _check_n3_asymmetry(contract):
            audit_log.contracts_with_asymmetry += 1
        if _check_four_levels_present(contract):
            audit_log.contracts_with_four_levels += 1
        if _check_veto_display_present(contract):
            audit_log.contracts_with_veto_display += 1


def _generate_manifest(audit_log: AuditLog) -> Path:
    manifest = {
        "manifest_version": "4.2-epistemological",
        "generation_date": _utc_now_iso_z(),
        "generator": "BatchFactory-V4.2-Epistemological",
        "statistics": {
            "total_contracts": 270,
            "validation_pass_rate": audit_log.get_pass_rate(),
            "methods_by_level": {
                "N1-EMP": audit_log.total_n1_methods,
                "N2-INF": audit_log.total_n2_methods,
                "N3-AUD": audit_log.total_n3_methods,
            },
            "epistemological_metrics": {
                "veto_gates_configured": audit_log.contracts_with_veto_gates,
                "n3_asymmetry_verified": audit_log.contracts_with_asymmetry,
                "four_levels_present": audit_log.contracts_with_four_levels,
                "veto_display_present": audit_log.contracts_with_veto_display,
            },
        },
        "validation_results": {
            "audit_score": audit_log.get_overall_score(),
        },
        "files": [
            {
                "path": f,
                "sha256": compute_file_hash(Path(f)),
                "invariant_hashes": audit_log.per_file.get(f, {}).get("invariant_hashes", {}),
                "inferred_type": audit_log.per_file.get(f, {}).get("inferred_type", {}),
            }
            for f in audit_log.generated_files
        ],
        "failures": audit_log.failures,
        "warnings": audit_log.warnings,
    }

    manifest_name = f"manifest_{datetime.now():%Y-%m-%d_%H%M%S}.json"
    manifest_path = OUTPUT_ROOT / manifest_name
    _save_json(manifest, manifest_path)
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="strict", choices=["strict"], help="Only strict mode is supported.")
    parser.add_argument("--abort-on-error", action="store_true", default=False)
    parser.add_argument("--validate-all", action="store_true", default=False)
    args = parser.parse_args()

    # Default behavior is strict+abort; flags are accepted to match the spec's command signature.
    abort_on_error = True if args.mode == "strict" else bool(args.abort_on_error)

    _preflight_check()

    # Destination directory must be empty (or non-existent)
    if OUTPUT_ROOT.exists():
        existing = [p for p in OUTPUT_ROOT.rglob("*") if p.is_file()]
        if existing:
            raise FileExistsError(f"Destination not empty: {OUTPUT_ROOT} has {len(existing)} file(s)")

    templates = _load_templates()
    template_hashes_by_slot = {slot: compute_invariant_hashes(tpl) for slot, tpl in templates.items()}

    policy_area_mapping = _load_policy_area_mapping()
    for pa in TARGET_POLICY_AREAS:
        if pa not in policy_area_mapping:
            raise ValueError(f"Policy area {pa} not in policy_area_mapping.json")

    audit_log = AuditLog()
    generated_paths: list[Path] = []

    for slot_id in SLOTS:
        template = templates[slot_id]
        template_hashes = template_hashes_by_slot[slot_id]

        for policy_area_id in TARGET_POLICY_AREAS:
            try:
                policy_area_name = policy_area_mapping[policy_area_id]
                instance, inferred_type = _instantiate_contract(
                    template=template,
                    policy_area_id=policy_area_id,
                    policy_area_name=policy_area_name,
                    template_hashes=template_hashes,
                )

                out_path = OUTPUT_ROOT / policy_area_id / f"{slot_id}.v4.json"
                if out_path.exists():
                    raise FileExistsError(f"File already exists: {out_path}")

                _save_json(instance, out_path)
                inv = compute_invariant_hashes(instance)
                audit_log.record_success(str(out_path), inv, inferred_type)
                generated_paths.append(out_path)

            except Exception as e:
                audit_log.record_failure(policy_area_id, slot_id, f"{type(e).__name__}: {e}")
                if abort_on_error:
                    raise

    _final_validation(generated_paths, audit_log)
    manifest_path = _generate_manifest(audit_log)

    print(f"✅ Manifest generated: {manifest_path}")
    print(f"✅ Total contracts: {len(audit_log.generated_files)}")
    print(f"✅ Validation score: {audit_log.get_overall_score():.2%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())






