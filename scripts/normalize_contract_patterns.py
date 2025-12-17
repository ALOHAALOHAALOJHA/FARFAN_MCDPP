#!/usr/bin/env python3
"""Normalize v3 executor contract patterns.

What this does (batch-safe, deterministic):
- For every Q###.v3.json in Phase_two executor_contracts/specialized/
  - Ensure each question_context.patterns[] has a usable "pattern" string.
    - If a pattern has pattern_ref but no pattern, resolve it from canonic_questionnaire_central/pattern_registry.json
  - Fill missing match_type from registry when possible
  - Preserve all existing fields (no lossy transform)
  - Recompute identity.contract_hash using canonical sha256 rule used by ContractUpdateValidator
  - Update identity.updated_at

This fixes the core issue where contracts carried pattern_ref without the actual regex, which makes
"patterns" effectively non-executable at runtime.

Run:
  python3 scripts/normalize_contract_patterns.py

Optional:
  DRY_RUN=1 python3 scripts/normalize_contract_patterns.py
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
PATTERN_REGISTRY_PATH = REPO_ROOT / "canonic_questionnaire_central" / "pattern_registry.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_pattern_registry(path: Path) -> dict[str, dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise TypeError(f"pattern_registry.json must be a list, got {type(raw).__name__}")
    idx: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        pid = item.get("pattern_id") or item.get("id")
        if isinstance(pid, str) and pid:
            idx[pid] = item
    return idx


def _compute_contract_hash(contract: dict[str, Any]) -> str:
    # Mirror ContractUpdateValidator behavior to avoid hash drift.
    temp = json.loads(json.dumps(contract))
    try:
        del temp["identity"]["contract_hash"]
    except Exception:
        pass
    contract_str = json.dumps(temp, sort_keys=True)
    return hashlib.sha256(contract_str.encode()).hexdigest()


def _normalize_patterns_in_contract(
    contract: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []

    qc = contract.get("question_context")
    if not isinstance(qc, dict):
        return contract, ["missing_or_invalid_question_context"]

    pats = qc.get("patterns")
    if not isinstance(pats, list):
        return contract, ["missing_or_invalid_question_context.patterns"]

    for idx, pat in enumerate(pats):
        if not isinstance(pat, dict):
            warnings.append(f"patterns[{idx}] not an object")
            continue

        pattern_ref = pat.get("pattern_ref")
        pattern_str = pat.get("pattern")

        # Resolve missing pattern from global registry when pattern_ref points to PAT-xxxx
        if (not isinstance(pattern_str, str) or not pattern_str.strip()) and isinstance(pattern_ref, str) and pattern_ref:
            src = registry.get(pattern_ref)
            if src and isinstance(src.get("pattern"), str):
                pat["pattern"] = src["pattern"]
                # Only fill match_type if missing/null
                if not isinstance(pat.get("match_type"), str) or not pat.get("match_type"):
                    if isinstance(src.get("match_type"), str):
                        pat["match_type"] = src["match_type"]
            else:
                warnings.append(f"patterns[{idx}] unresolved pattern_ref={pattern_ref}")

        # If match_type still missing, default to REGEX (schema-friendly)
        if not isinstance(pat.get("match_type"), str) or not pat.get("match_type"):
            pat["match_type"] = "REGEX"

    qc["patterns"] = pats
    contract["question_context"] = qc

    ident = contract.get("identity")
    if isinstance(ident, dict):
        ident["updated_at"] = _utc_now_iso()
        contract["identity"] = ident

    # Recompute hash after normalization.
    if isinstance(contract.get("identity"), dict):
        contract["identity"]["contract_hash"] = _compute_contract_hash(contract)

    return contract, warnings


def main() -> int:
    if not CONTRACTS_DIR.exists():
        raise FileNotFoundError(str(CONTRACTS_DIR))
    if not PATTERN_REGISTRY_PATH.exists():
        raise FileNotFoundError(str(PATTERN_REGISTRY_PATH))

    dry_run = os.getenv("DRY_RUN", "0").strip() in {"1", "true", "TRUE", "yes", "YES"}

    registry = _load_pattern_registry(PATTERN_REGISTRY_PATH)

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

        normalized, warnings = _normalize_patterns_in_contract(contract, registry)
        total_warnings.extend(f"{path.name}: {w}" for w in warnings)

        new_text = json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=False) + "\n"

        if new_text != original_text:
            changed += 1
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")

    print(f"contracts_total={total} changed={changed} dry_run={dry_run}")
    if total_warnings:
        # Print only the first chunk to keep output readable
        print(f"warnings_count={len(total_warnings)}")
        for w in total_warnings[:50]:
            print(f"WARN: {w}")
        if len(total_warnings) > 50:
            print("... (more warnings truncated)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
