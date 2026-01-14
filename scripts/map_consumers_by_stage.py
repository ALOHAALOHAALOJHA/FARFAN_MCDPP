#!/usr/bin/env python3
"""Map current vs potential SISAS consumers by stage (phase_0..phase_9).

Inputs:
- canonic_questionnaire_central/_registry/CQC_AUDIT_MATRIX.csv
- canonic_questionnaire_central/_registry/capabilities/consumer_capability_declarations.json
- canonic_questionnaire_central/_registry/irrigation_validation_rules.json
- canonic_questionnaire_central/resolver.py (SDO consumer registrations)

Output:
- artifacts/consumers_by_stage.json

Rationale
---------
The audit matrix expresses intended consumption (consumer + consumer_scope).
The capability declarations express equipped consumers (declared_capabilities + allowed_signal_types).
The irrigation rules express what signal types exist per phase.
This script joins them to surface:
- Current consumers by phase (declared + registered)
- Potential consumers by phase (from matrix, not clearly mapped to equipped consumers)
- Expected signal types per phase and their capability requirements
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
CQC_ROOT = REPO_ROOT / "canonic_questionnaire_central"


@dataclass(frozen=True)
class DeclaredConsumer:
    consumer_id: str
    phase: int
    declared_capabilities: List[str]
    allowed_signal_types: List[str]
    min_confidence: float | None
    max_signals_per_query: int | None


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _phase_key(n: int) -> str:
    return f"phase_{n}"


def _extract_registered_consumers_from_resolver(resolver_path: Path) -> List[str]:
    text = resolver_path.read_text(encoding="utf-8")
    # Matches consumer_id="..." inside register_consumer calls
    # Keep it simple & robust: capture all consumer_id="..." occurrences.
    ids = re.findall(r"consumer_id\s*=\s*[\"']([^\"']+)[\"']", text)
    # Deduplicate preserving order
    seen: Set[str] = set()
    out: List[str] = []
    for cid in ids:
        if cid not in seen:
            out.append(cid)
            seen.add(cid)
    return out


def _infer_phase_from_registered_consumer_id(consumer_id: str) -> str | None:
    # Examples: phase_0_assembly, phase_1_extraction, phase_9_report, phase_4_scoring
    m = re.match(r"^phase_(\d+)_", consumer_id)
    if not m:
        return None
    return _phase_key(int(m.group(1)))


def _declared_consumers_by_phase(declarations: Dict[str, Any]) -> Dict[str, List[DeclaredConsumer]]:
    out: Dict[str, List[DeclaredConsumer]] = defaultdict(list)
    for cid, payload in (declarations.get("consumers") or {}).items():
        phase = int(payload.get("phase"))
        scope = payload.get("scope") or {}
        out[_phase_key(phase)].append(
            DeclaredConsumer(
                consumer_id=cid,
                phase=phase,
                declared_capabilities=list(payload.get("declared_capabilities") or []),
                allowed_signal_types=list(scope.get("allowed_signal_types") or []),
                min_confidence=scope.get("min_confidence"),
                max_signals_per_query=scope.get("max_signals_per_query"),
            )
        )
    # Stable ordering
    for k in out:
        out[k].sort(key=lambda c: c.consumer_id)
    return dict(out)


def _matrix_consumers_by_scope(matrix_rows: List[Dict[str, str]]) -> Dict[str, List[str]]:
    by_scope: Dict[str, Set[str]] = defaultdict(set)
    for row in matrix_rows:
        scope = row.get("consumer_scope", "") or ""
        consumer = row.get("consumer", "") or ""
        if not scope:
            continue
        if consumer:
            by_scope[scope].add(consumer)
    return {k: sorted(v) for k, v in by_scope.items()}


def _expected_signals_by_phase(rules: Dict[str, Any]) -> Dict[str, List[str]]:
    routing = rules.get("routing") or {}
    return {k: list(v) for k, v in routing.items() if k.startswith("phase_")}


def _capabilities_required_by_signal(rules: Dict[str, Any]) -> Dict[str, List[str]]:
    return {k: list(v) for k, v in (rules.get("capabilities_required") or {}).items()}


def _aggregate_required_capabilities(signal_types: Iterable[str], cap_required: Dict[str, List[str]]) -> List[str]:
    agg: Set[str] = set()
    for st in signal_types:
        for cap in cap_required.get(st, []):
            agg.add(cap)
    return sorted(agg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--matrix",
        default="canonic_questionnaire_central/_registry/CQC_AUDIT_MATRIX.csv",
    )
    ap.add_argument(
        "--declarations",
        default="canonic_questionnaire_central/_registry/capabilities/consumer_capability_declarations.json",
    )
    ap.add_argument(
        "--rules",
        default="canonic_questionnaire_central/_registry/irrigation_validation_rules.json",
    )
    ap.add_argument(
        "--resolver",
        default="canonic_questionnaire_central/resolver.py",
    )
    ap.add_argument(
        "--out",
        default="artifacts/consumers_by_stage.json",
    )
    args = ap.parse_args()

    matrix_rows = _read_csv(REPO_ROOT / args.matrix)
    declarations = _load_json(REPO_ROOT / args.declarations)
    rules = _load_json(REPO_ROOT / args.rules)

    declared_by_phase = _declared_consumers_by_phase(declarations)
    matrix_by_scope = _matrix_consumers_by_scope(matrix_rows)
    expected_signals = _expected_signals_by_phase(rules)
    cap_required_by_signal = _capabilities_required_by_signal(rules)

    registered_ids = _extract_registered_consumers_from_resolver(REPO_ROOT / args.resolver)
    registered_by_phase: Dict[str, List[str]] = defaultdict(list)
    for cid in registered_ids:
        pk = _infer_phase_from_registered_consumer_id(cid)
        if pk:
            registered_by_phase[pk].append(cid)
    for k in registered_by_phase:
        registered_by_phase[k] = sorted(set(registered_by_phase[k]))

    stages: Dict[str, Any] = {}

    # Normalize matrix consumer scopes: they are "Phase_3" style (capital P)
    # while rules use "phase_3".
    def norm_scope(scope: str) -> str:
        scope = scope.strip()
        m = re.match(r"^Phase_(\d+)$", scope)
        if m:
            return _phase_key(int(m.group(1)))
        return scope

    # Build stage list from union of phases observed in any source
    stage_keys: Set[str] = set()
    stage_keys |= set(expected_signals.keys())
    stage_keys |= set(declared_by_phase.keys())
    stage_keys |= set(registered_by_phase.keys())
    stage_keys |= {norm_scope(s) for s in matrix_by_scope.keys()}

    for stage in sorted(stage_keys, key=lambda s: (0, int(s.split("_")[1])) if s.startswith("phase_") and s.split("_")[1].isdigit() else (1, s)):
        exp = expected_signals.get(stage, [])
        req_caps = _aggregate_required_capabilities(exp, cap_required_by_signal)

        declared = declared_by_phase.get(stage, [])
        declared_ids = [c.consumer_id for c in declared]

        registered = registered_by_phase.get(stage, [])

        # Matrix consumers: find original key mapping back
        matrix_consumers: List[str] = []
        for raw_scope, consumers in matrix_by_scope.items():
            if norm_scope(raw_scope) == stage:
                matrix_consumers.extend(consumers)
        matrix_consumers = sorted(set(matrix_consumers))

        # Heuristic gaps: matrix consumers are function/class refs, so they won't match consumer_id.
        # Still, we can flag stages where matrix expects consumption but there is no equipped consumer.
        equipped_count = len(declared_ids)
        matrix_count = len(matrix_consumers)

        stages[stage] = {
            "expected_signal_types": exp,
            "required_capabilities_from_rules": req_caps,
            "current_consumers_declared": [asdict(c) for c in declared],
            "current_consumers_registered": registered,
            "matrix_consumers": matrix_consumers,
            "summary": {
                "matrix_consumers_count": matrix_count,
                "declared_consumers_count": equipped_count,
                "registered_consumers_count": len(registered),
                "expected_signal_types_count": len(exp),
            },
        }

    report = {
        "inputs": {
            "matrix": args.matrix,
            "declarations": args.declarations,
            "rules": args.rules,
            "resolver": args.resolver,
        },
        "notes": {
            "scope_normalization": "Matrix uses Phase_N while rules use phase_N; normalized for join.",
            "consumer_id_mismatch": "Matrix consumer strings are code refs; capability declarations use consumer_id. This report lists both and highlights per-stage coverage.",
        },
        "stages": stages,
    }

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Minimal stdout for quick scan: per stage counts
    quick = {
        stage: v["summary"]
        for stage, v in stages.items()
        if stage.startswith("phase_")
    }
    print(json.dumps(quick, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
