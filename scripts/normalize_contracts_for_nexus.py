#!/usr/bin/env python3
"""Normalize v3 executor contracts for EvidenceNexus (definitive alignment).

Goals (batch-safe, deterministic):
- Remove/neutralize legacy EvidenceAssembler/EvidenceValidator references in contracts.
- Update wiring metadata to refer to EvidenceNexus + ValidationEngine.
- Enrich contract patterns with explicit policy_area for scope coherence.
- Make expected_elements usable as validation gates by ensuring minimum defaults.
- Copy failure_contract into question_context when only present in error_handling.
- Recompute identity.contract_hash (sha256 over canonical JSON, excluding old hash) and update identity.updated_at.

Run:
  python3 scripts/normalize_contracts_for_nexus.py

Optional:
  DRY_RUN=1 python3 scripts/normalize_contracts_for_nexus.py
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = (
    REPO_ROOT
    / "src"
    / "canonic_phases"
    / "Phase_two"
    / "json_files_phase_two"
    / "executor_contracts"
    / "specialized"
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compute_contract_hash(contract: dict[str, Any]) -> str:
    # Mirror ContractUpdateValidator behavior to avoid hash drift.
    temp = json.loads(json.dumps(contract))
    try:
        del temp["identity"]["contract_hash"]
    except Exception:
        pass
    contract_str = json.dumps(temp, sort_keys=True)
    return hashlib.sha256(contract_str.encode()).hexdigest()


_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("farfan_core.core.orchestrator.evidence_assembler", "canonic_phases.Phase_two.evidence_nexus"),
    ("farfan_core.core.orchestrator.evidence_validator", "canonic_phases.Phase_two.evidence_nexus"),
    ("farfan_core.core.orchestrator.evidence_registry", "canonic_phases.Phase_two.evidence_nexus"),
    ("EvidenceAssembler", "EvidenceNexus"),
    ("EvidenceValidator", "ValidationEngine"),
)


def _rewrite_strings(obj: Any) -> Any:
    """Recursively rewrite legacy strings inside an arbitrary JSON structure."""
    if isinstance(obj, str):
        out = obj
        for old, new in _REPLACEMENTS:
            out = out.replace(old, new)
        return out
    if isinstance(obj, list):
        return [_rewrite_strings(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _rewrite_strings(v) for k, v in obj.items()}
    return obj


def _normalize_contract(contract: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []

    identity = contract.get("identity")
    if not isinstance(identity, dict):
        return contract, ["missing_or_invalid_identity"]

    policy_area_id = identity.get("policy_area_id")
    if not isinstance(policy_area_id, str) or not policy_area_id:
        warnings.append("missing_identity.policy_area_id")
        policy_area_id = ""

    # 1) Rewrite legacy strings everywhere (docs, traceability, human_answer_structure, etc.)
    contract = _rewrite_strings(contract)

    # 2) Normalize evidence_assembly wiring metadata to Nexus (non-breaking: Nexus reads assembly_rules)
    evidence_assembly = contract.get("evidence_assembly")
    if isinstance(evidence_assembly, dict):
        evidence_assembly.setdefault("engine", "EVIDENCE_NEXUS")
        evidence_assembly["module"] = "canonic_phases.Phase_two.evidence_nexus"
        evidence_assembly["class_name"] = "EvidenceNexus"
        # There is no direct EvidenceNexus.assemble; process/process_evidence is the canonical entry point.
        evidence_assembly["method_name"] = evidence_assembly.get("method_name") or "process"
        contract["evidence_assembly"] = evidence_assembly

    # 3) Normalize validation_rules wiring metadata to ValidationEngine (non-breaking)
    validation_rules = contract.get("validation_rules")
    if isinstance(validation_rules, dict):
        validation_rules.setdefault("engine", "VALIDATION_ENGINE")
        validation_rules["module"] = "canonic_phases.Phase_two.evidence_nexus"
        validation_rules["class_name"] = "ValidationEngine"
        validation_rules["method_name"] = validation_rules.get("method_name") or "validate"
        contract["validation_rules"] = validation_rules

    # 4) Ensure question_context has policy-scoped patterns and minimums for expected_elements
    qc = contract.get("question_context")
    if not isinstance(qc, dict):
        warnings.append("missing_or_invalid_question_context")
        qc = {}

    pats = qc.get("patterns")
    if isinstance(pats, list):
        for p in pats:
            if isinstance(p, dict):
                # Scope coherence: question-level patterns belong to the contract's policy area.
                p.setdefault("policy_area", policy_area_id)
                # Ensure match_type exists (schema-friendly)
                if not isinstance(p.get("match_type"), str) or not p.get("match_type"):
                    p["match_type"] = "REGEX"
        qc["patterns"] = pats
    else:
        warnings.append("missing_or_invalid_question_context.patterns")

    elems = qc.get("expected_elements")
    if isinstance(elems, list):
        for e in elems:
            if not isinstance(e, dict):
                continue
            required = bool(e.get("required", False))
            # Make "required" measurable in a deterministic way.
            if required and "minimum" not in e:
                e["minimum"] = 1
            # Some monolith entries omit required; keep as-is
        qc["expected_elements"] = elems
    else:
        warnings.append("missing_or_invalid_question_context.expected_elements")

    # Ensure validations exists (monolith compatible)
    if "validations" not in qc or not isinstance(qc.get("validations"), dict):
        qc["validations"] = {}

    # 5) Copy failure_contract into question_context if only present in error_handling
    error_handling = contract.get("error_handling")
    if isinstance(error_handling, dict):
        fc = error_handling.get("failure_contract")
        if isinstance(fc, dict) and "failure_contract" not in qc:
            qc["failure_contract"] = fc

    contract["question_context"] = qc

    # 6) Update timestamps and contract hash
    identity["updated_at"] = _utc_now_iso()
    contract["identity"] = identity
    contract["identity"]["contract_hash"] = _compute_contract_hash(contract)

    return contract, warnings


def main() -> int:
    if not CONTRACTS_DIR.exists():
        raise FileNotFoundError(str(CONTRACTS_DIR))

    dry_run = os.getenv("DRY_RUN", "0").strip() in {"1", "true", "TRUE", "yes", "YES"}

    contract_files = sorted(CONTRACTS_DIR.glob("Q*.v3.json"))
    if not contract_files:
        raise RuntimeError(f"No v3 contracts found in {CONTRACTS_DIR}")

    total = 0
    changed = 0
    total_warnings: list[str] = []

    for path in contract_files:
        total += 1
        original_text = path.read_text(encoding="utf-8")
        contract = json.loads(original_text)
        if not isinstance(contract, dict):
            total_warnings.append(f"{path.name}: not a JSON object")
            continue

        normalized, warnings = _normalize_contract(contract)
        total_warnings.extend(f"{path.name}: {w}" for w in warnings)

        new_text = json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
        if new_text != original_text:
            changed += 1
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")

    print(f"contracts_total={total} changed={changed} dry_run={dry_run}")
    if total_warnings:
        print(f"warnings_count={len(total_warnings)}")
        for w in total_warnings[:50]:
            print(f"WARN: {w}")
        if len(total_warnings) > 50:
            print("... (more warnings truncated)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
