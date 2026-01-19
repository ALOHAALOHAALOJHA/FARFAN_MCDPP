#!/usr/bin/env python3
"""Full Signals Ecosystem Map - Vehículos × Consumidores × Assets.

Maps:
- Vehículo: módulo SISAS en infrastructure/irrigation_using_signals/SISAS/
- Consumidor: módulo de fase (Phase_00..Phase_09) que importa ese vehículo
- Assets: archivos de canonic_questionnaire_central que el vehículo carga/transmite

Outputs:
- artifacts/signals_full_map.json
- artifacts/signals_full_map.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SISAS_ROOT = REPO_ROOT / "src" / "farfan_pipeline" / "infrastructure" / "irrigation_using_signals" / "SISAS"
PHASES_ROOT = REPO_ROOT / "src" / "farfan_pipeline" / "phases"
CQC_ROOT = REPO_ROOT / "canonic_questionnaire_central"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_py_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if p.is_file() and "__pycache__" not in str(p))


def _extract_sisas_imports(py_file: Path) -> list[str]:
    """Extract SISAS module names imported by a .py file."""
    text = py_file.read_text(encoding="utf-8", errors="ignore")
    # Match: from ...SISAS.signal_xxx import | from ...SISAS import signal_xxx
    pattern = r"from\s+[\w.]*SISAS\.(\w+)\s+import|from\s+[\w.]*SISAS\s+import\s+(\w+)"
    matches = re.findall(pattern, text)
    modules = set()
    for m1, m2 in matches:
        if m1:
            modules.add(m1)
        if m2:
            modules.add(m2)
    return sorted(modules)


def _extract_cqc_references(py_file: Path) -> list[str]:
    """Extract canonic_questionnaire_central paths referenced in a .py file."""
    text = py_file.read_text(encoding="utf-8", errors="ignore")
    refs: set[str] = set()
    # Match string literals containing canonic paths or _registry paths
    patterns = [
        r'canonic_questionnaire_central[^"\']*',
        r'_registry/[^"\']*\.json',
        r'policy_areas/[^"\']*\.json',
        r'clusters/[^"\']*\.json',
        r'dimensions/[^"\']*\.json',
        r'cross_cutting/[^"\']*\.json',
        r'questions/[^"\']*\.json',
        r'patterns/[^"\']*\.json',
        r'capabilities/[^"\']*\.json',
        r'validations/[^"\']*\.json',
        r'semantic/[^"\']*\.json',
        r'scoring/[^"\']*\.json',
        r'governance/[^"\']*\.json',
    ]
    for pat in patterns:
        for m in re.findall(pat, text):
            refs.add(m.strip())
    return sorted(refs)


def _infer_phase(py_file: Path) -> str | None:
    """Infer phase from path like .../Phase_02/..."""
    parts = py_file.parts
    for p in parts:
        if p.startswith("Phase_"):
            return p
    return None


def build_vehicle_consumer_map() -> list[dict[str, Any]]:
    """Build mapping: vehículo (SISAS module) → consumidores (phase modules)."""
    vehicle_consumers: dict[str, list[dict[str, str]]] = {}
    
    # Scan phase modules for SISAS imports
    for py_file in _iter_py_files(PHASES_ROOT):
        sisas_modules = _extract_sisas_imports(py_file)
        phase = _infer_phase(py_file)
        consumer_path = str(py_file.relative_to(REPO_ROOT))
        consumer_name = py_file.stem
        
        for sisas_mod in sisas_modules:
            if sisas_mod not in vehicle_consumers:
                vehicle_consumers[sisas_mod] = []
            vehicle_consumers[sisas_mod].append({
                "consumer_module": consumer_name,
                "consumer_path": consumer_path,
                "phase": phase or "unknown",
            })
    
    return [
        {"vehicle": v, "consumers": sorted(c, key=lambda x: (x["phase"], x["consumer_module"]))}
        for v, c in sorted(vehicle_consumers.items())
    ]


def build_vehicle_assets_map() -> dict[str, list[str]]:
    """Build mapping: vehículo (SISAS module) → assets de CQC que referencia."""
    vehicle_assets: dict[str, set[str]] = {}
    
    for py_file in _iter_py_files(SISAS_ROOT):
        mod_name = py_file.stem
        refs = _extract_cqc_references(py_file)
        if refs:
            vehicle_assets[mod_name] = set(refs)
    
    return {k: sorted(v) for k, v in sorted(vehicle_assets.items())}


def build_full_map() -> dict[str, Any]:
    """Build complete ecosystem map."""
    # Vehicle → Consumers (by phase)
    vehicle_consumer_list = build_vehicle_consumer_map()
    
    # Vehicle → Assets
    vehicle_assets = build_vehicle_assets_map()
    
    # Enrich vehicle_consumer_list with assets
    for entry in vehicle_consumer_list:
        vehicle = entry["vehicle"]
        entry["assets_loaded"] = vehicle_assets.get(vehicle, [])
    
    # Summary by phase
    phase_summary: dict[str, dict[str, Any]] = {}
    for entry in vehicle_consumer_list:
        for consumer in entry["consumers"]:
            phase = consumer["phase"]
            if phase not in phase_summary:
                phase_summary[phase] = {
                    "vehicles": set(),
                    "consumer_modules": set(),
                    "assets": set(),
                }
            phase_summary[phase]["vehicles"].add(entry["vehicle"])
            phase_summary[phase]["consumer_modules"].add(consumer["consumer_module"])
            phase_summary[phase]["assets"].update(entry["assets_loaded"])
    
    # Convert sets to sorted lists
    phase_summary_out = {
        p: {
            "vehicles": sorted(v["vehicles"]),
            "consumer_modules": sorted(v["consumer_modules"]),
            "assets": sorted(v["assets"]),
            "vehicle_count": len(v["vehicles"]),
            "consumer_count": len(v["consumer_modules"]),
            "asset_count": len(v["assets"]),
        }
        for p, v in sorted(phase_summary.items(), key=lambda x: (0, int(x[0].split("_")[1])) if x[0].startswith("Phase_") else (1, x[0]))
    }
    
    return {
        "vehicle_consumer_map": vehicle_consumer_list,
        "vehicle_assets_map": vehicle_assets,
        "phase_summary": phase_summary_out,
        "totals": {
            "vehicles": len(vehicle_consumer_list),
            "phases_with_signals": len(phase_summary_out),
        },
    }


def write_outputs(report: dict[str, Any], out_json: Path, out_csv: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # CSV: phase summary
    rows = []
    for phase, data in report["phase_summary"].items():
        rows.append({
            "phase": phase,
            "vehicle_count": data["vehicle_count"],
            "consumer_count": data["consumer_count"],
            "asset_count": data["asset_count"],
            "vehicles": json.dumps(data["vehicles"]),
            "consumer_modules": json.dumps(data["consumer_modules"]),
            "assets": json.dumps(data["assets"]),
        })
    
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["phase", "vehicle_count", "consumer_count", "asset_count", "vehicles", "consumer_modules", "assets"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", default="artifacts/signals_full_map.json")
    ap.add_argument("--out-csv", default="artifacts/signals_full_map.csv")
    args = ap.parse_args()
    
    report = build_full_map()
    write_outputs(report, REPO_ROOT / args.out_json, REPO_ROOT / args.out_csv)
    
    # Summary
    print(json.dumps({
        "totals": report["totals"],
        "phases": list(report["phase_summary"].keys()),
        "out_json": args.out_json,
        "out_csv": args.out_csv,
    }, indent=2))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
