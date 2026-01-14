#!/usr/bin/env python3
"""Generate a wide, decision-ready "sábana" by crossing CQC audit matrix rows
with SISAS consumers, signals, capabilities, and irrigability.

Outputs:
- artifacts/matrix_sabana.csv (flat table)
- artifacts/matrix_sabana.json (same rows as structured JSON)

Design goals
------------
- Deterministic and auditable: all derived fields are computed from explicit inputs.
- No assumptions about consumer name matching: matrix `consumer` strings are code refs;
  capability declarations use `consumer_id`. We cross them at the stage level.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
CQC_ROOT = REPO_ROOT / "canonic_questionnaire_central"


MATRIX_COLUMNS: Tuple[str, ...] = (
    "json_file_path",
    "consumer",
    "consumer_scope",
    "scope_alignment",
    "signalt_irrigation_source",
    "consumer_ready",
    "redundant_with",
    "added_value",
    "quality_risk",
    "notes",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        out: List[Dict[str, str]] = []
        for row in reader:
            normalized = {k: (v or "").strip() for k, v in row.items()}
            out.append(normalized)
        return out


def _norm_scope_to_stage(scope: str) -> str:
    scope = (scope or "").strip()
    m = re.match(r"^Phase_(\d+)$", scope)
    if m:
        return f"phase_{int(m.group(1))}"
    return scope or "<missing>"


def _stable_row_key(json_file_path: str, consumer: str, consumer_scope: str) -> str:
    raw = f"{json_file_path}|{consumer}|{consumer_scope}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


def _as_json_str(value: Any) -> str:
    # For CSV cells.
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class StageInfo:
    stage: str
    expected_signal_types: List[str]
    required_capabilities_from_rules: List[str]
    registered_consumer_ids: List[str]
    declared_consumers: List[Dict[str, Any]]


def _index_stages(consumers_by_stage: Dict[str, Any]) -> Dict[str, StageInfo]:
    stages = consumers_by_stage.get("stages") or {}
    out: Dict[str, StageInfo] = {}
    for stage, payload in stages.items():
        out[stage] = StageInfo(
            stage=stage,
            expected_signal_types=list(payload.get("expected_signal_types") or []),
            required_capabilities_from_rules=list(payload.get("required_capabilities_from_rules") or []),
            registered_consumer_ids=list(payload.get("current_consumers_registered") or []),
            declared_consumers=list(payload.get("current_consumers_declared") or []),
        )
    return out


def _union(values: Iterable[Iterable[str]]) -> List[str]:
    agg = set()
    for seq in values:
        for x in seq:
            if x:
                agg.add(x)
    return sorted(agg)


def _min_opt(nums: Iterable[Optional[float]]) -> Optional[float]:
    cleaned = [n for n in nums if n is not None]
    return min(cleaned) if cleaned else None


def _max_opt(nums: Iterable[Optional[int]]) -> Optional[int]:
    cleaned = [n for n in nums if n is not None]
    return max(cleaned) if cleaned else None


def _index_irrigability(irrigability: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    # Join on same triple used by `matrix_irrigability_report.json` rows.
    out: Dict[str, Dict[str, Any]] = {}
    for r in irrigability.get("rows") or []:
        key = _stable_row_key(
            r.get("json_file_path", ""),
            r.get("consumer", ""),
            r.get("consumer_scope", ""),
        )
        out[key] = r
    return out


def _file_stats(cqc_root: Path, json_file_path: str) -> Tuple[bool, Optional[int]]:
    p = cqc_root / json_file_path
    if not p.exists():
        return False, None
    try:
        return True, p.stat().st_size
    except OSError:
        return True, None


def _stage_metrics(stage_info: StageInfo) -> Dict[str, Any]:
    declared_ids = [c.get("consumer_id", "") for c in stage_info.declared_consumers if c.get("consumer_id")]

    declared_caps_union = _union((c.get("declared_capabilities") or []) for c in stage_info.declared_consumers)
    declared_allowed_union = _union((c.get("allowed_signal_types") or []) for c in stage_info.declared_consumers)

    min_conf = _min_opt((c.get("min_confidence") for c in stage_info.declared_consumers))
    max_signals = _max_opt((c.get("max_signals_per_query") for c in stage_info.declared_consumers))

    expected = list(stage_info.expected_signal_types)
    required = list(stage_info.required_capabilities_from_rules)

    expected_covered = sorted(set(expected) & set(declared_allowed_union))
    expected_uncovered = [x for x in expected if x not in set(expected_covered)]

    required_covered = sorted(set(required) & set(declared_caps_union))
    required_missing = [x for x in required if x not in set(required_covered)]

    return {
        "stage_expected_signal_types": expected,
        "stage_required_capabilities": required,
        "stage_registered_consumer_ids": stage_info.registered_consumer_ids,
        "stage_declared_consumer_ids": sorted(set(declared_ids)),
        "stage_declared_consumer_count": len(set(declared_ids)),
        "stage_registered_consumer_count": len(stage_info.registered_consumer_ids),
        "stage_declared_capabilities_union": declared_caps_union,
        "stage_declared_allowed_signal_types_union": declared_allowed_union,
        "stage_declared_min_confidence_min": min_conf,
        "stage_declared_max_signals_per_query_max": max_signals,
        "stage_expected_signal_types_covered_by_declared": expected_covered,
        "stage_expected_signal_types_uncovered_by_declared": expected_uncovered,
        "stage_required_capabilities_covered_by_declared": required_covered,
        "stage_required_capabilities_missing_in_declared": required_missing,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--matrix",
        default="canonic_questionnaire_central/_registry/CQC_AUDIT_MATRIX.csv",
        help="Path to CQC_AUDIT_MATRIX.csv (repo-relative)",
    )
    ap.add_argument(
        "--consumers-by-stage",
        default="artifacts/consumers_by_stage.json",
        help="Path to consumers_by_stage.json (repo-relative)",
    )
    ap.add_argument(
        "--irrigability",
        default="artifacts/matrix_irrigability_report.json",
        help="Path to matrix_irrigability_report.json (repo-relative)",
    )
    ap.add_argument(
        "--out-csv",
        default="artifacts/matrix_sabana.csv",
        help="Output CSV path (repo-relative)",
    )
    ap.add_argument(
        "--out-json",
        default="artifacts/matrix_sabana.json",
        help="Output JSON path (repo-relative)",
    )
    args = ap.parse_args()

    matrix_rows = _read_csv_dicts(REPO_ROOT / args.matrix)
    consumers_by_stage = _load_json(REPO_ROOT / args.consumers_by_stage)
    irrigability = _load_json(REPO_ROOT / args.irrigability)

    stage_index = _index_stages(consumers_by_stage)
    irrig_index = _index_irrigability(irrigability)

    enriched_rows: List[Dict[str, Any]] = []

    for row in matrix_rows:
        base: Dict[str, Any] = {k: row.get(k, "") for k in MATRIX_COLUMNS}

        json_file_path = base.get("json_file_path", "")
        consumer = base.get("consumer", "")
        consumer_scope = base.get("consumer_scope", "")

        stage = _norm_scope_to_stage(consumer_scope)
        base["stage"] = stage

        row_key = _stable_row_key(json_file_path, consumer, consumer_scope)
        base["row_key"] = row_key

        exists, size_bytes = _file_stats(CQC_ROOT, json_file_path)
        base["file_exists"] = exists
        base["file_bytes"] = size_bytes

        irr = irrig_index.get(row_key) or {}
        base["irrigability_bucket"] = irr.get("bucket") or ""
        base["irrigability_reasons"] = irr.get("reasons") or []

        st = stage_index.get(stage)
        if st is None:
            base["stage_known"] = False
            base["stage_expected_signal_types"] = []
            base["stage_required_capabilities"] = []
            base["stage_registered_consumer_ids"] = []
            base["stage_declared_consumer_ids"] = []
            base["stage_declared_consumer_count"] = 0
            base["stage_registered_consumer_count"] = 0
            base["stage_declared_capabilities_union"] = []
            base["stage_declared_allowed_signal_types_union"] = []
            base["stage_declared_min_confidence_min"] = None
            base["stage_declared_max_signals_per_query_max"] = None
            base["stage_expected_signal_types_covered_by_declared"] = []
            base["stage_expected_signal_types_uncovered_by_declared"] = []
            base["stage_required_capabilities_covered_by_declared"] = []
            base["stage_required_capabilities_missing_in_declared"] = []
        else:
            base["stage_known"] = True
            base.update(_stage_metrics(st))

        # Convenience flags for decision-making
        base["stage_has_registered_consumer"] = bool(base.get("stage_registered_consumer_ids"))
        base["stage_has_declared_equipped_consumer"] = bool(base.get("stage_declared_consumer_ids"))
        base["stage_signal_vocab_mismatch"] = bool(
            base.get("stage_expected_signal_types")
            and not base.get("stage_expected_signal_types_covered_by_declared")
            and base.get("stage_declared_allowed_signal_types_union")
        )
        base["stage_capability_vocab_mismatch"] = bool(
            base.get("stage_required_capabilities")
            and not base.get("stage_required_capabilities_covered_by_declared")
            and base.get("stage_declared_capabilities_union")
        )

        enriched_rows.append(base)

    # Define CSV columns deterministically
    csv_columns: List[str] = list(MATRIX_COLUMNS) + [
        "row_key",
        "stage",
        "stage_known",
        "file_exists",
        "file_bytes",
        "irrigability_bucket",
        "irrigability_reasons",
        "stage_expected_signal_types",
        "stage_required_capabilities",
        "stage_registered_consumer_ids",
        "stage_declared_consumer_ids",
        "stage_declared_consumer_count",
        "stage_registered_consumer_count",
        "stage_declared_capabilities_union",
        "stage_declared_allowed_signal_types_union",
        "stage_declared_min_confidence_min",
        "stage_declared_max_signals_per_query_max",
        "stage_expected_signal_types_covered_by_declared",
        "stage_expected_signal_types_uncovered_by_declared",
        "stage_required_capabilities_covered_by_declared",
        "stage_required_capabilities_missing_in_declared",
        "stage_has_registered_consumer",
        "stage_has_declared_equipped_consumer",
        "stage_signal_vocab_mismatch",
        "stage_capability_vocab_mismatch",
    ]

    out_json = {
        "inputs": {
            "matrix": args.matrix,
            "consumers_by_stage": args.consumers_by_stage,
            "irrigability": args.irrigability,
        },
        "row_count": len(enriched_rows),
        "columns": csv_columns,
        "rows": enriched_rows,
    }

    out_csv_path = REPO_ROOT / args.out_csv
    out_json_path = REPO_ROOT / args.out_json
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)

    with out_csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for r in enriched_rows:
            flat = {k: _as_json_str(r.get(k)) for k in csv_columns}
            writer.writerow(flat)

    out_json_path.write_text(json.dumps(out_json, ensure_ascii=False, indent=2), encoding="utf-8")

    # Minimal stdout summary
    print(
        json.dumps(
            {
                "row_count": len(enriched_rows),
                "out_csv": str(Path(args.out_csv)),
                "out_json": str(Path(args.out_json)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
