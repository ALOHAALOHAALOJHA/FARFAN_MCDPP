#!/usr/bin/env python3
"""Classify each CQC_AUDIT_MATRIX row as irrigable vs not, based on current/potential consumers.

This answers: "qué data actual de Canonical Questionnaire se puede irrigar y cuál definitivamente no",
considering:
- consumer scope alignment
- added value
- whether the row declares a Signalt irrigation source
- whether the target stage has *equipped* consumers (declared capabilities) and/or is registered in resolver

Outputs:
- artifacts/matrix_irrigability_report.json

Notes
-----
- The matrix "consumer" strings are code refs; equipped consumers are in consumer_capability_declarations.json.
  We therefore classify at *stage* granularity for equipamiento.
- "Definitivamente no" is interpreted as: fails one of the hard requirements the user stated
  (scope coherence, value-add, and via signals), given the current artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm_scope(scope: str) -> str:
    scope = (scope or "").strip()
    m = re.match(r"^Phase_(\d+)$", scope)
    if m:
        return f"phase_{int(m.group(1))}"
    return scope


def _is_yes(v: str) -> bool:
    return (v or "").strip().upper() == "YES"


def _is_marginal(v: str) -> bool:
    return (v or "").strip().upper() == "MARGINAL"


def _has_signalt_source(v: str) -> bool:
    v = (v or "").strip()
    if not v or v.upper() == "NONE":
        return False
    # Accept any Signalt.* token
    return v.startswith("Signalt.")


def _classify_row(
    row: Dict[str, str],
    stage_summary: Dict[str, Dict[str, int]],
) -> Tuple[str, List[str]]:
    """Return (bucket, reasons).

    Buckets:
    - irrigable_now
    - not_irrigable_yet
    - definitely_not
    """
    reasons: List[str] = []

    scope = row.get("consumer_scope", "")
    stage = _norm_scope(scope)

    scope_alignment = (row.get("scope_alignment") or "").strip().upper()
    added_value = (row.get("added_value") or "").strip().upper()
    consumer_ready = (row.get("consumer_ready") or "").strip().upper()
    signalt_src = row.get("signalt_irrigation_source") or ""
    notes = row.get("notes") or ""

    # Hard requirement checks
    if stage == "External":
        reasons.append("consumer_scope=External")
    if scope_alignment != "YES":
        reasons.append(f"scope_alignment={scope_alignment or '<EMPTY>'}")
    if added_value != "YES":
        reasons.append(f"added_value={added_value or '<EMPTY>'}")
    if not _has_signalt_source(signalt_src):
        reasons.append("signalt_irrigation_source=None")
    if consumer_ready != "YES":
        reasons.append(f"consumer_ready={consumer_ready or '<EMPTY>'}")

    # Value gating: notes indicate regenerable/atomic => fails the user's "agrega valor" constraint.
    if _is_marginal(row.get("added_value", "")) and "regenerated" in notes.lower():
        reasons.append("regenerable_or_atomic_unit")

    # Equipamiento by stage
    stage_info = stage_summary.get(stage)
    declared_count = (stage_info or {}).get("declared_consumers_count", 0)
    registered_count = (stage_info or {}).get("registered_consumers_count", 0)

    # phase_00 is special: it is resolver assembly; we allow registered consumer to count as operational.
    has_operational_consumer = declared_count > 0 or (stage == "phase_00" and registered_count > 0)

    if stage.startswith("phase_") and not has_operational_consumer:
        reasons.append("no_equipped_consumer_for_stage")

    # Decide bucket
    hard_fail = (
        stage == "External"
        or scope_alignment != "YES"
        or added_value != "YES"
        or not _has_signalt_source(signalt_src)
        or consumer_ready != "YES"
    )

    if hard_fail:
        return "definitely_not", reasons

    if stage.startswith("phase_") and not has_operational_consumer:
        return "not_irrigable_yet", reasons

    return "irrigable_now", reasons


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--matrix",
        default="canonic_questionnaire_central/_registry/CQC_AUDIT_MATRIX.csv",
    )
    ap.add_argument(
        "--consumers_by_stage",
        default="artifacts/consumers_by_stage.json",
    )
    ap.add_argument(
        "--out",
        default="artifacts/matrix_irrigability_report.json",
    )
    args = ap.parse_args()

    matrix_rows = _read_csv(REPO_ROOT / args.matrix)
    consumers_map = _load_json(REPO_ROOT / args.consumers_by_stage)

    stage_summary: Dict[str, Dict[str, int]] = {}
    for stage, payload in (consumers_map.get("stages") or {}).items():
        stage_summary[stage] = payload.get("summary") or {}

    classified: List[Dict[str, Any]] = []
    buckets: Dict[str, int] = {"irrigable_now": 0, "not_irrigable_yet": 0, "definitely_not": 0}

    by_stage_bucket: Dict[str, Dict[str, int]] = {}

    for row in matrix_rows:
        stage = _norm_scope(row.get("consumer_scope", ""))
        bucket, reasons = _classify_row(row, stage_summary)

        buckets[bucket] += 1
        by_stage_bucket.setdefault(stage, {"irrigable_now": 0, "not_irrigable_yet": 0, "definitely_not": 0})
        by_stage_bucket[stage][bucket] += 1

        classified.append(
            {
                "json_file_path": row.get("json_file_path"),
                "consumer": row.get("consumer"),
                "consumer_scope": row.get("consumer_scope"),
                "stage": stage,
                "scope_alignment": row.get("scope_alignment"),
                "signalt_irrigation_source": row.get("signalt_irrigation_source"),
                "consumer_ready": row.get("consumer_ready"),
                "added_value": row.get("added_value"),
                "quality_risk": row.get("quality_risk"),
                "notes": row.get("notes"),
                "bucket": bucket,
                "reasons": reasons,
            }
        )

    report = {
        "inputs": {
            "matrix": args.matrix,
            "consumers_by_stage": args.consumers_by_stage,
        },
        "bucket_counts": buckets,
        "bucket_counts_by_stage": dict(sorted(by_stage_bucket.items())),
        "rows": classified,
        "interpretation": {
            "irrigable_now": "Meets scope_alignment=YES, added_value=YES, consumer_ready=YES, and has Signalt source; plus stage has equipped/operational consumers.",
            "not_irrigable_yet": "Row meets hard requirements but stage lacks equipped consumer coverage (based on declarations/registrations).",
            "definitely_not": "Fails at least one hard requirement (scope coherence, value-add, via signals, or consumer readiness) under current artifacts.",
        },
    }

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"bucket_counts": buckets, "bucket_counts_by_stage": by_stage_bucket}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
