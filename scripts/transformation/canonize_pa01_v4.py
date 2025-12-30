#!/usr/bin/env python3
"""
canonize_pa01_v4.py
===================
Creates the 30 canonical v4 epistemological contracts (Q001..Q030) under:
  contracts_v4/PA01/Q###.v4.json

Source of truth for structure: episte_refact.md (PARTE II–VI).
This script is deterministic (aside from file mtimes) and aborts on first error.

Strategy:
- Load the existing v4 templates from:
    src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/v4/contracts_v4/*.json
- Map by identity.representative_question_id (Q001..Q030)
- Canonize the minimal required fields per episte_refact.md:
  - evidence_assembly.type_system.*.description
  - Phase B (N2) methods: ensure modifies exists (non-empty list)
  - Ensure assembly_rules sources cover provides for N1/N2/N3 (R1/R2/R3)
  - Recompute method_count
- Validate with audit_v4_rigorous.validate_epistemological_structure
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TypeAlias, cast

from audit_v4_rigorous import JSONValue, JSONObject, validate_epistemological_structure


REPO_ROOT = Path(__file__).resolve().parent
SRC_TEMPLATES_DIR = (
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
OUTPUT_DIR = REPO_ROOT / "contracts_v4" / "PA01"

SLOTS: tuple[str, ...] = tuple(f"Q{i:03d}" for i in range(1, 31))


def _load_json(path: Path) -> JSONObject:
    data = cast(JSONValue, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(data, dict):
        raise ValueError(f"Template JSON must be an object: {path}")
    return data


def _save_json(path: Path, data: JSONObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _deepcopy_json(obj: JSONValue) -> JSONValue:
    return cast(JSONValue, json.loads(json.dumps(obj, ensure_ascii=False)))


def _string_list(v: JSONValue) -> list[str] | None:
    if not isinstance(v, list):
        return None
    out: list[str] = []
    for x in v:
        if not isinstance(x, str):
            return None
        out.append(x)
    return out


def _collect_phase_provides(contract: JSONObject, phase_key: str) -> list[str]:
    mb = contract.get("method_binding")
    if not isinstance(mb, dict):
        return []
    phases = mb.get("execution_phases")
    if not isinstance(phases, dict):
        return []
    phase = phases.get(phase_key)
    if not isinstance(phase, dict):
        return []
    methods = phase.get("methods")
    if not isinstance(methods, list):
        return []

    provides: list[str] = []
    for m in methods:
        if not isinstance(m, dict):
            continue
        pv = m.get("provides")
        if isinstance(pv, str) and pv.strip():
            provides.append(pv.strip())
    return provides


def _canonize_type_system(contract: JSONObject) -> None:
    ea = contract.get("evidence_assembly")
    if not isinstance(ea, dict):
        return
    ts = ea.get("type_system")
    if not isinstance(ts, dict):
        return

    descriptions: dict[str, str] = {
        "FACT": "Se SUMA al grafo como nodo",
        "PARAMETER": "MODIFICA pesos de aristas del grafo",
        "CONSTRAINT": "FILTRA/BLOQUEA ramas si validación falla",
        "NARRATIVE": "CONSUME grafo para texto final",
    }
    for k, desc in descriptions.items():
        node = ts.get(k)
        if isinstance(node, dict):
            if "description" not in node:
                node["description"] = desc


def _canonize_n2_methods(contract: JSONObject) -> None:
    mb = contract.get("method_binding")
    if not isinstance(mb, dict):
        return
    phases = mb.get("execution_phases")
    if not isinstance(phases, dict):
        return
    phase_b = phases.get("phase_B_computation")
    if not isinstance(phase_b, dict):
        return
    methods = phase_b.get("methods")
    if not isinstance(methods, list):
        return

    for m in methods:
        if not isinstance(m, dict):
            continue
        if m.get("level") != "N2-INF":
            continue
        if "modifies" in m:
            mods = _string_list(m.get("modifies"))
            if mods is None or not mods:
                m["modifies"] = ["edge_weights", "confidence_scores"]
            continue

        # Minimal required by PARTE II (can be specialized later)
        m["modifies"] = ["edge_weights", "confidence_scores"]


def _recompute_method_count(contract: JSONObject) -> None:
    mb = contract.get("method_binding")
    if not isinstance(mb, dict):
        return
    phases = mb.get("execution_phases")
    if not isinstance(phases, dict):
        return

    total = 0
    for phase_key in ["phase_A_construction", "phase_B_computation", "phase_C_litigation"]:
        phase = phases.get(phase_key)
        if not isinstance(phase, dict):
            continue
        methods = phase.get("methods")
        if isinstance(methods, list):
            total += len([m for m in methods if isinstance(m, dict)])
    mb["method_count"] = total


def _canonize_assembly_rule_sources(contract: JSONObject) -> None:
    ea = contract.get("evidence_assembly")
    if not isinstance(ea, dict):
        return
    rules = ea.get("assembly_rules")
    if not isinstance(rules, list):
        return

    n1 = _collect_phase_provides(contract, "phase_A_construction")
    n2 = _collect_phase_provides(contract, "phase_B_computation")
    n3 = _collect_phase_provides(contract, "phase_C_litigation")

    # R1/R2/R3 are positional; enforce sources reflect current method provides.
    if len(rules) >= 1 and isinstance(rules[0], dict):
        rules[0]["sources"] = n1
    if len(rules) >= 2 and isinstance(rules[1], dict):
        rules[1]["sources"] = n2
    if len(rules) >= 3 and isinstance(rules[2], dict):
        rules[2]["sources"] = n3


def canonize_one(slot_id: str) -> Path:
    if slot_id not in SLOTS:
        raise ValueError(f"slot_id must be one of Q001..Q030, got {slot_id}")

    templates = sorted(p for p in SRC_TEMPLATES_DIR.glob("*.json") if p.is_file())
    if len(templates) != 30:
        raise ValueError(f"Expected 30 source templates in {SRC_TEMPLATES_DIR}, got {len(templates)}")

    chosen: Path | None = None
    for p in templates:
        tpl = _load_json(p)
        identity = tpl.get("identity")
        if not isinstance(identity, dict):
            continue
        rq = identity.get("representative_question_id")
        if rq == slot_id:
            chosen = p
            break
    if not chosen:
        raise FileNotFoundError(f"Template for {slot_id} not found in {SRC_TEMPLATES_DIR}")

    contract = cast(JSONObject, _deepcopy_json(_load_json(chosen)))

    _canonize_type_system(contract)
    _canonize_n2_methods(contract)
    _canonize_assembly_rule_sources(contract)
    _recompute_method_count(contract)

    validation = validate_epistemological_structure(contract)
    if not validation.valid:
        raise ValueError(f"Canonicalization failed for {slot_id}: {validation.errors}")

    out_path = OUTPUT_DIR / f"{slot_id}.v4.json"
    if out_path.exists():
        raise FileExistsError(f"Output already exists: {out_path}")
    _save_json(out_path, contract)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", help="Generate only one slot (Q001..Q030). If omitted, generates all 30.")
    args = parser.parse_args()

    slot = cast(str | None, getattr(args, "slot", None))
    if slot:
        canonize_one(slot)
        return 0

    for slot_id in SLOTS:
        canonize_one(slot_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



