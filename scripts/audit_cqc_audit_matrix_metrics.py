#!/usr/bin/env python3
"""Audit CQC_AUDIT_MATRIX.csv metrics and deltas against a git baseline.

Goal
----
Given the current working tree and a baseline commit, compute:
- Intrinsic matrix metrics (counts by key columns)
- File-existence metrics (paths referenced by the matrix) at baseline vs now
- Contradictions (e.g., consumer_ready=YES but file missing)

Outputs
-------
Writes a JSON report to artifacts/audit_matrix_metrics_delta.json

Usage
-----
  python scripts/audit_cqc_audit_matrix_metrics.py \
    --baseline 6bd69bf6 \
    --matrix canonic_questionnaire_central/_registry/CQC_AUDIT_MATRIX.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple


CANONIC_ROOT = Path("canonic_questionnaire_central")


@dataclass(frozen=True)
class MatrixRow:
    json_file_path: str
    consumer: str
    consumer_scope: str
    scope_alignment: str
    signalt_irrigation_source: str
    consumer_ready: str
    redundant_with: str
    added_value: str
    quality_risk: str
    notes: str


def _run_git(repo_root: Path, args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _git_show_file(repo_root: Path, commit: str, path: str) -> str:
    proc = _run_git(repo_root, ["show", f"{commit}:{path}"])
    if proc.returncode != 0:
        raise RuntimeError(f"git show failed for {commit}:{path}: {proc.stderr.strip()}")
    return proc.stdout


def _git_path_exists_at_commit(repo_root: Path, commit: str, path: str) -> bool:
    # git cat-file -e exits 0 if object exists
    proc = _run_git(repo_root, ["cat-file", "-e", f"{commit}:{path}"])
    return proc.returncode == 0


def _read_matrix_csv_text(csv_text: str) -> List[MatrixRow]:
    reader = csv.DictReader(csv_text.splitlines())
    rows: List[MatrixRow] = []
    for raw in reader:
        rows.append(
            MatrixRow(
                json_file_path=(raw.get("json_file_path") or "").strip(),
                consumer=(raw.get("consumer") or "").strip(),
                consumer_scope=(raw.get("consumer_scope") or "").strip(),
                scope_alignment=(raw.get("scope_alignment") or "").strip(),
                signalt_irrigation_source=(raw.get("signalt_irrigation_source") or "").strip(),
                consumer_ready=(raw.get("consumer_ready") or "").strip(),
                redundant_with=(raw.get("redundant_with") or "").strip(),
                added_value=(raw.get("added_value") or "").strip(),
                quality_risk=(raw.get("quality_risk") or "").strip(),
                notes=(raw.get("notes") or "").strip(),
            )
        )
    return rows


def _read_matrix_csv_file(path: Path) -> List[MatrixRow]:
    return _read_matrix_csv_text(path.read_text(encoding="utf-8"))


def _metrics(rows: Iterable[MatrixRow]) -> Dict[str, Any]:
    rows_list = list(rows)
    def _counter(getter) -> Dict[str, int]:
        return dict(Counter(getter(r) for r in rows_list))

    redundant_nonempty = sum(1 for r in rows_list if r.redundant_with and r.redundant_with != "None")
    notes_nonempty = sum(1 for r in rows_list if r.notes)

    return {
        "rows_total": len(rows_list),
        "distinct_consumers": len(set(r.consumer for r in rows_list if r.consumer)),
        "by_consumer_scope": _counter(lambda r: r.consumer_scope or "<EMPTY>"),
        "by_scope_alignment": _counter(lambda r: r.scope_alignment or "<EMPTY>"),
        "by_signalt_irrigation_source": _counter(lambda r: r.signalt_irrigation_source or "<EMPTY>"),
        "by_consumer_ready": _counter(lambda r: r.consumer_ready or "<EMPTY>"),
        "by_added_value": _counter(lambda r: r.added_value or "<EMPTY>"),
        "by_quality_risk": _counter(lambda r: r.quality_risk or "<EMPTY>"),
        "redundant_with_nonempty": redundant_nonempty,
        "notes_nonempty": notes_nonempty,
    }


def _existence_metrics(
    repo_root: Path,
    rows: List[MatrixRow],
    commit: str,
) -> Dict[str, Any]:
    total = len(rows)

    # CSV paths are relative to canonic_questionnaire_central/
    def repo_rel(p: str) -> str:
        return str(CANONIC_ROOT / p)

    exists_at_commit = 0
    exists_now = 0
    missing_now: List[str] = []
    missing_at_commit: List[str] = []
    ready_but_missing_now: List[str] = []

    for r in rows:
        rel = repo_rel(r.json_file_path)
        if _git_path_exists_at_commit(repo_root, commit, rel):
            exists_at_commit += 1
        else:
            missing_at_commit.append(r.json_file_path)

        if (repo_root / rel).exists():
            exists_now += 1
        else:
            missing_now.append(r.json_file_path)
            if r.consumer_ready.upper() == "YES":
                ready_but_missing_now.append(r.json_file_path)

    return {
        "total_paths": total,
        "exists_at_baseline_commit": exists_at_commit,
        "missing_at_baseline_commit": len(missing_at_commit),
        "exists_now": exists_now,
        "missing_now": len(missing_now),
        "missing_now_examples": missing_now[:25],
        "missing_at_baseline_examples": missing_at_commit[:25],
        "ready_but_missing_now": len(ready_but_missing_now),
        "ready_but_missing_now_examples": ready_but_missing_now[:25],
    }


def _diff_metrics(current: Mapping[str, Any], baseline: Mapping[str, Any]) -> Dict[str, Any]:
    # Only diff numeric leafs and dict-of-int counters
    out: Dict[str, Any] = {}

    for k in sorted(set(current.keys()) | set(baseline.keys())):
        a = baseline.get(k)
        b = current.get(k)

        if isinstance(a, int) and isinstance(b, int):
            if a != b:
                out[k] = {"baseline": a, "current": b, "delta": b - a}
            continue

        if isinstance(a, dict) and isinstance(b, dict):
            # assume dict[str,int]
            sub: Dict[str, Any] = {}
            keys = set(a.keys()) | set(b.keys())
            for sk in sorted(keys):
                av = a.get(sk, 0)
                bv = b.get(sk, 0)
                if isinstance(av, int) and isinstance(bv, int) and av != bv:
                    sub[sk] = {"baseline": av, "current": bv, "delta": bv - av}
            if sub:
                out[k] = sub
            continue

        # ignore non-diffable types

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, help="Baseline git commit SHA")
    ap.add_argument(
        "--matrix",
        default="canonic_questionnaire_central/_registry/CQC_AUDIT_MATRIX.csv",
        help="Path to current matrix CSV",
    )
    ap.add_argument(
        "--out",
        default="artifacts/audit_matrix_metrics_delta.json",
        help="Output JSON report path",
    )

    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    matrix_path = repo_root / args.matrix

    baseline_matrix_text = _git_show_file(repo_root, args.baseline, args.matrix)

    baseline_rows = _read_matrix_csv_text(baseline_matrix_text)
    current_rows = _read_matrix_csv_file(matrix_path)

    baseline_metrics = _metrics(baseline_rows)
    current_metrics = _metrics(current_rows)

    baseline_exist = _existence_metrics(repo_root, baseline_rows, args.baseline)
    current_exist = _existence_metrics(repo_root, current_rows, args.baseline)

    # Note: existence metrics for "current" are still evaluated against the same baseline commit,
    # but on the working tree; that makes the delta attributable to refactors/moves/deletes.

    diff_intrinsic = _diff_metrics(current_metrics, baseline_metrics)
    diff_existence = _diff_metrics(current_exist, baseline_exist)

    report: Dict[str, Any] = {
        "baseline_commit": args.baseline,
        "matrix_path": args.matrix,
        "intrinsic_metrics": {
            "baseline": baseline_metrics,
            "current": current_metrics,
            "delta": diff_intrinsic,
        },
        "existence_metrics": {
            "baseline": baseline_exist,
            "current": current_exist,
            "delta": diff_existence,
        },
    }

    out_path = repo_root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Also print a minimal human summary to stdout
    print(json.dumps({"intrinsic_delta": diff_intrinsic, "existence_delta": diff_existence}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
