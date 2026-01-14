#!/usr/bin/env python3
"""Cross canonic-central assets with SISAS vehicles (modules) and consumer readiness.

Outputs
-------
- artifacts/signals_vehicle_map.json
- artifacts/signals_vehicle_map.csv

Logic
-----
- Uses `artifacts/matrix_sabana.json` as authoritative list of assets + stage + irrigability.
- Scans SISAS modules for explicit string references to asset paths and filenames.
- Flags gaps: no vehicle found, no equipped consumer, value gating (MARGINAL), vocab mismatch.

This report separates "vehículo" (módulo Signals) de "consumidor" (nodo de fase).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set


REPO_ROOT = Path(__file__).resolve().parent.parent
SISAS_ROOT = REPO_ROOT / "src" / "farfan_pipeline" / "infrastructure" / "irrigation_using_signals" / "SISAS"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_sisas_py_files() -> List[Path]:
    return sorted(p for p in SISAS_ROOT.rglob("*.py") if p.is_file())


def _build_asset_index(sabana: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in sabana.get("rows") or []:
        path = row.get("json_file_path", "")
        if not path:
            continue
        out[path] = row
    return out


def _prepare_match_strings(asset_paths: Set[str]) -> Dict[str, Set[str]]:
    # Map from path -> set of candidate substrings (full path + filename) to match.
    out: Dict[str, Set[str]] = {}
    for p in asset_paths:
        substrs: Set[str] = set()
        substrs.add(p)
        filename = Path(p).name
        if filename:
            substrs.add(filename)
        out[p] = substrs
    return out


def _scan_modules_for_assets(py_files: List[Path], match_map: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    # Returns: asset_path -> list of module paths that mention it.
    hits: Dict[str, List[str]] = {k: [] for k in match_map}
    for pyf in py_files:
        text = pyf.read_text(encoding="utf-8", errors="ignore")
        for asset, substrs in match_map.items():
            if any(s in text for s in substrs):
                hits[asset].append(str(pyf.relative_to(REPO_ROOT)))
    return hits


def _bool(val: Any) -> bool:
    return bool(val)


def _recommended_action(row: Dict[str, Any]) -> str:
    bucket = row.get("irrigability_bucket")
    reasons = row.get("irrigability_reasons") or []
    needs_consumer = _bool(row.get("flag_needs_equipped_consumer"))
    vocab_gap = _bool(row.get("flag_signal_vocab_gap") or row.get("flag_capability_vocab_gap"))
    vehicle_missing = _bool(row.get("flag_no_vehicle_found"))

    if bucket == "definitely_not":
        return "reclassify_value_gate"  # blocked by value/regen policy
    if needs_consumer:
        return "declare_and_register_consumer"
    if vocab_gap:
        return "align_vocab_signal_or_capability"
    if vehicle_missing:
        return "wire_vehicle"
    if bucket == "not_irrigable_yet":
        return "fix_consumer_equipment"
    return "ok"


def generate(args: argparse.Namespace) -> Dict[str, Any]:
    sabana = _load_json(REPO_ROOT / args.sabana)
    asset_index = _build_asset_index(sabana)
    match_map = _prepare_match_strings(set(asset_index.keys()))

    py_files = _iter_sisas_py_files()
    asset_hits = _scan_modules_for_assets(py_files, match_map)

    rows_out: List[Dict[str, Any]] = []
    for asset_path, base in asset_index.items():
        vehicles = sorted(asset_hits.get(asset_path) or [])

        # Flags
        bucket = base.get("irrigability_bucket")
        reasons = base.get("irrigability_reasons") or []
        needs_consumer = (base.get("stage_declared_consumer_count", 0) == 0) or (
            base.get("stage_registered_consumer_count", 0) == 0
        )
        value_blocked = bucket == "definitely_not"
        signal_gap = _bool(base.get("stage_signal_vocab_mismatch"))
        cap_gap = _bool(base.get("stage_capability_vocab_mismatch"))

        row = {
            "json_file_path": asset_path,
            "stage": base.get("stage"),
            "consumer_scope": base.get("consumer_scope"),
            "irrigability_bucket": bucket,
            "irrigability_reasons": reasons,
            "vehicle_modules": vehicles,
            "vehicle_count": len(vehicles),
            "stage_declared_consumer_ids": base.get("stage_declared_consumer_ids") or [],
            "stage_registered_consumer_ids": base.get("stage_registered_consumer_ids") or [],
            "stage_expected_signal_types": base.get("stage_expected_signal_types") or [],
            "stage_required_capabilities": base.get("stage_required_capabilities") or [],
            "flag_no_vehicle_found": len(vehicles) == 0,
            "flag_needs_equipped_consumer": needs_consumer,
            "flag_value_blocked": value_blocked,
            "flag_signal_vocab_gap": signal_gap,
            "flag_capability_vocab_gap": cap_gap,
            "file_exists": base.get("file_exists"),
            "file_bytes": base.get("file_bytes"),
        }

        row["recommended_action"] = _recommended_action(row)
        rows_out.append(row)

    return {
        "inputs": {
            "sabana": args.sabana,
            "sisas_root": str(SISAS_ROOT.relative_to(REPO_ROOT)),
        },
        "row_count": len(rows_out),
        "rows": rows_out,
    }


def write_outputs(report: Dict[str, Any], out_json: Path, out_csv: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Flatten to CSV
    fieldnames = [
        "json_file_path",
        "stage",
        "consumer_scope",
        "irrigability_bucket",
        "irrigability_reasons",
        "vehicle_count",
        "vehicle_modules",
        "stage_declared_consumer_ids",
        "stage_registered_consumer_ids",
        "stage_expected_signal_types",
        "stage_required_capabilities",
        "flag_no_vehicle_found",
        "flag_needs_equipped_consumer",
        "flag_value_blocked",
        "flag_signal_vocab_gap",
        "flag_capability_vocab_gap",
        "file_exists",
        "file_bytes",
        "recommended_action",
    ]

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in report["rows"]:
            flat = {k: json.dumps(r.get(k), ensure_ascii=False) if isinstance(r.get(k), list) else r.get(k) for k in fieldnames}
            writer.writerow(flat)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabana", default="artifacts/matrix_sabana.json", help="Path to sabana JSON (matrix_sabana.json)")
    ap.add_argument("--out-json", default="artifacts/signals_vehicle_map.json", help="Output JSON path")
    ap.add_argument("--out-csv", default="artifacts/signals_vehicle_map.csv", help="Output CSV path")
    args = ap.parse_args()

    report = generate(args)
    write_outputs(report, REPO_ROOT / args.out_json, REPO_ROOT / args.out_csv)

    print(json.dumps({"row_count": report["row_count"], "out_json": str(args.out_json), "out_csv": str(args.out_csv)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())