from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = (
    REPO_ROOT
    / "src"
    / "farfan_pipeline"
    / "phases"
    / "Phase_two"
    / "json_files_phase_two"
    / "executor_contracts"
    / "specialized"
)
VALIDATOR_PATH = (
    REPO_ROOT
    / "src"
    / "farfan_pipeline"
    / "phases"
    / "Phase_two"
    / "json_files_phase_two"
    / "executor_contracts"
    / "cqvr_validator.py"
)

CONTRACT_RE = re.compile(r"^Q\d{3}\.v3\.json$")
SLOT_RE = re.compile(r"D\d-Q\d")
GENERIC_PHRASES = ("Execute", "Process results", "Return structured output")


def _load_cqvr_validator() -> Any:
    spec = importlib.util.spec_from_file_location("cqvr_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load CQVR validator from {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CQVRValidator()


def _iter_contract_paths() -> list[Path]:
    paths = sorted(p for p in CONTRACTS_DIR.iterdir() if CONTRACT_RE.match(p.name))
    assert len(paths) == 300, f"Expected 300 contracts, found {len(paths)}"
    return paths


def test_phase2_executor_contracts_cqvr_ge_96() -> None:
    validator = _load_cqvr_validator()
    failures: list[str] = []

    for path in _iter_contract_paths():
        contract_id = path.stem.replace(".v3", "")
        contract = json.loads(path.read_text(encoding="utf-8"))
        report = validator.validate_contract(contract)
        percentage = float(report["percentage"])
        if percentage < 96.0:
            failures.append(f"{contract_id}: {percentage:.1f} {report.get('breakdown')}")

    assert not failures, f"Contracts below CQVR threshold: {failures[:25]}"


def test_phase2_executor_contracts_structural_invariants() -> None:
    errors: list[str] = []

    for path in _iter_contract_paths():
        contract_id = path.stem.replace(".v3", "")
        contract = json.loads(path.read_text(encoding="utf-8"))

        identity = contract.get("identity", {})
        if not isinstance(identity, dict):
            errors.append(f"{contract_id}: missing identity")
            continue

        if identity.get("question_id") != contract_id:
            errors.append(f"{contract_id}: identity.question_id mismatch")

        base_slot = str(identity.get("base_slot") or "")

        signal_reqs = contract.get("signal_requirements", {})
        mandatory = (
            signal_reqs.get("mandatory_signals", []) if isinstance(signal_reqs, dict) else []
        )
        threshold = signal_reqs.get("minimum_signal_threshold", 0.0) if isinstance(signal_reqs, dict) else 0.0
        if isinstance(mandatory, list) and mandatory and float(threshold) <= 0.0:
            errors.append(f"{contract_id}: minimum_signal_threshold must be >0 for mandatory_signals")
        if isinstance(mandatory, list) and "transparency" in mandatory:
            errors.append(f"{contract_id}: raw 'transparency' mandatory signal must be normalized")
        if isinstance(mandatory, list) and not all(isinstance(s, str) and "_" in s for s in mandatory):
            errors.append(f"{contract_id}: mandatory_signals must be snake_case")

        method_binding = contract.get("method_binding", {})
        methods = method_binding.get("methods", []) if isinstance(method_binding, dict) else []
        if isinstance(methods, list):
            if method_binding.get("method_count") != len(methods):
                errors.append(f"{contract_id}: method_binding.method_count mismatch")
            provides_set = {
                m.get("provides")
                for m in methods
                if isinstance(m, dict) and isinstance(m.get("provides"), str) and m.get("provides")
            }
        else:
            provides_set = set()

        assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
        if not assembly_rules:
            errors.append(f"{contract_id}: missing evidence_assembly.assembly_rules")
        else:
            sources0 = assembly_rules[0].get("sources", [])
            sources0_set = {s for s in sources0 if isinstance(s, str) and "*" not in s}
            if provides_set and sources0_set != provides_set:
                errors.append(f"{contract_id}: assembly_rules[0].sources must equal provides")

        template = (
            contract.get("output_contract", {})
            .get("human_readable_output", {})
            .get("template", {})
        )
        title = str(template.get("title") or "") if isinstance(template, dict) else ""
        if contract_id not in title:
            errors.append(f"{contract_id}: template.title must contain question_id")
        if base_slot and base_slot not in title and SLOT_RE.search(title):
            errors.append(f"{contract_id}: template.title base_slot mismatch")

        md = (
            contract.get("output_contract", {})
            .get("human_readable_output", {})
            .get("methodological_depth", {})
        )
        md_methods = md.get("methods", []) if isinstance(md, dict) else []
        if not md_methods:
            errors.append(f"{contract_id}: missing methodological_depth.methods")
        else:
            for method in md_methods[:5]:
                if not isinstance(method, dict):
                    continue
                steps = method.get("technical_approach", {}).get("steps", [])
                if not isinstance(steps, list) or not steps:
                    errors.append(f"{contract_id}: missing methodological steps")
                    continue
                for step in steps:
                    desc = step.get("description", "") if isinstance(step, dict) else str(step)
                    if any(p in desc for p in GENERIC_PHRASES):
                        errors.append(f"{contract_id}: boilerplate methodological step detected")
                        break

    assert not errors, f"Contract invariant violations: {errors[:25]}"

