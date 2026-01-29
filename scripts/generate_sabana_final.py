#!/usr/bin/env python3
"""Sábana Final: Assets CQC × Vehículos × Consumidores × Estado Actual × Estado Ideal.

Cruza:
- Assets de canonic_questionnaire_central (de matrix_sabana.json)
- Vehículos: módulos SISAS que los transmiten
- Consumidores: módulos de fase que reciben la data
- Estado actual: si ya hay wiring
- Estado ideal: qué falta para irrigación completa

Outputs:
- artifacts/sabana_final_decisiones.json
- artifacts/sabana_final_decisiones.csv
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


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


# Mapeo explícito: vehículo SISAS → qué tipos de assets de CQC carga
VEHICLE_ASSET_PATTERNS = {
    "signal_registry": [
        r"policy_areas/",
        r"clusters/",
        r"dimensions/",
        r"cross_cutting/",
        r"questions/",
        r"patterns/",
        r"scoring/",
        r"semantic/",
        r"governance/",
        r"validations/",
    ],
    "signal_irrigator": [
        r"_registry/questions/integration_map\.json",
    ],
    "signal_loader": [
        r"patterns/",
        r"questionnaire_monolith",
    ],
    "signal_enhancement_integrator": [
        r"cross_cutting/",
        r"validations/",
        r"scoring/",
        r"semantic/",
        r"method",
    ],
    "signal_intelligence_layer": [
        r"patterns/",
        r"semantic/",
        r"validations/",
        r"scoring/",
    ],
    "signal_context_scoper": [
        r"patterns/",
        r"questions/",
    ],
    "signal_evidence_extractor": [
        r"expected_elements",
        r"patterns/",
    ],
    "signal_consumption": [
        r"questionnaire_monolith",
    ],
    "signal_quality_metrics": [
        r"patterns/",
        r"policy_areas/",
    ],
    "signals": [
        r"patterns/",
        r"policy_areas/",
    ],
}

# Mapeo: fase → consumidores principales (módulos de fase que usan Signals)
PHASE_CONSUMERS = {
    "Phase_00": [
        "phase0_90_02_bootstrap.py",
        "providers.py",
        "wiring_types.py",
    ],
    "Phase_01": [
        "phase1_11_00_signal_enrichment.py",
        "phase1_13_00_cpp_ingestion.py",
    ],
    "Phase_02": [
        "phase2_10_00_factory.py",
        "phase2_30_03_resource_aware_executor.py",
        "phase2_40_03_irrigation_synchronizer.py",
        "phase2_60_00_base_executor_with_contract.py",
        "phase2_80_00_evidence_nexus.py",
        "phase2_95_00_contract_hydrator.py",
        "phase2_95_02_precision_tracking.py",
    ],
    "Phase_03": [
        "phase3_10_00_phase3_signal_enriched_scoring.py",
    ],
    "Phase_04": [
        "phase4_10_00_aggregation.py",
        "phase4_10_00_signal_enriched_aggregation.py",
        "phase4_10_00_signal_enriched_primitives.py",
    ],
    "Phase_05": [],  # Sin consumidores Signals detectados
    "Phase_06": [],  # Sin consumidores Signals detectados
    "Phase_07": [],  # Sin consumidores Signals detectados
    "Phase_08": [
        "phase8_30_00_signal_enriched_recommendations.py",
    ],
    "Phase_09": [
        "phase9_10_00_signal_enriched_reporting.py",
    ],
}

# Mapeo: stage (de la matriz) → fase
def _stage_to_phase(stage: str) -> str | None:
    m = re.match(r"phase_(\d+)", stage, re.IGNORECASE)
    if m:
        return f"Phase_{m.group(1)}"
    return None


def _match_vehicles(asset_path: str) -> list[str]:
    """Determinar qué vehículos SISAS cargan este asset."""
    vehicles = []
    for vehicle, patterns in VEHICLE_ASSET_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, asset_path, re.IGNORECASE):
                vehicles.append(vehicle)
                break
    return sorted(set(vehicles))


def generate(sabana_path: Path) -> dict[str, Any]:
    sabana = _load_json(sabana_path)
    rows = sabana.get("rows", [])
    
    enriched_rows = []
    
    for row in rows:
        asset_path = row.get("json_file_path", "")
        stage = row.get("stage", "")
        phase = _stage_to_phase(stage)
        
        # Vehículos que cargan este asset
        vehicles = _match_vehicles(asset_path)
        
        # Consumidores de la fase
        consumers = PHASE_CONSUMERS.get(phase, []) if phase else []
        
        # Estado actual
        has_vehicle = len(vehicles) > 0
        has_consumer = len(consumers) > 0
        irrigability = row.get("irrigability_bucket", "")
        value_blocked = row.get("flag_value_blocked", irrigability == "definitely_not")
        
        # Estado ideal: qué falta
        gaps = []
        if not has_vehicle:
            gaps.append("NECESITA_VEHICULO")
        if not has_consumer:
            gaps.append("NECESITA_CONSUMIDOR")
        if value_blocked:
            gaps.append("BLOQUEADO_POR_VALOR_MARGINAL")
        if row.get("stage_signal_vocab_mismatch"):
            gaps.append("VOCAB_SEÑALES_NO_ALINEADO")
        if row.get("stage_capability_vocab_mismatch"):
            gaps.append("VOCAB_CAPACIDADES_NO_ALINEADO")
        
        # Acción recomendada
        if not gaps:
            action = "IRRIGABLE_AHORA"
        elif "BLOQUEADO_POR_VALOR_MARGINAL" in gaps and len(gaps) == 1:
            action = "RECLASIFICAR_VALOR"
        elif "NECESITA_VEHICULO" in gaps and "NECESITA_CONSUMIDOR" in gaps:
            action = "WIRING_COMPLETO_REQUERIDO"
        elif "NECESITA_VEHICULO" in gaps:
            action = "AGREGAR_CARGA_EN_VEHICULO"
        elif "NECESITA_CONSUMIDOR" in gaps:
            action = "DECLARAR_CONSUMIDOR_EN_FASE"
        else:
            action = "ALINEAR_VOCABULARIOS"
        
        enriched_rows.append({
            "json_file_path": asset_path,
            "stage": stage,
            "phase": phase or "N/A",
            # Vehículos
            "vehiculos": vehicles,
            "vehiculo_count": len(vehicles),
            "vehiculos_str": ", ".join(vehicles) if vehicles else "NINGUNO",
            # Consumidores
            "consumidores": consumers,
            "consumidor_count": len(consumers),
            "consumidores_str": ", ".join(consumers) if consumers else "NINGUNO",
            # Estado
            "irrigability_bucket": irrigability,
            "tiene_vehiculo": has_vehicle,
            "tiene_consumidor": has_consumer,
            "bloqueado_por_valor": value_blocked,
            # Ideal
            "gaps": gaps,
            "gaps_str": ", ".join(gaps) if gaps else "NINGUNO",
            "accion_recomendada": action,
            # Campos originales útiles
            "added_value": row.get("added_value", ""),
            "notes": row.get("notes", ""),
            "consumer_scope": row.get("consumer_scope", ""),
            "file_exists": row.get("file_exists"),
            "file_bytes": row.get("file_bytes"),
        })
    
    # Resumen
    summary = {
        "total_assets": len(enriched_rows),
        "irrigables_ahora": sum(1 for r in enriched_rows if r["accion_recomendada"] == "IRRIGABLE_AHORA"),
        "necesitan_vehiculo": sum(1 for r in enriched_rows if "NECESITA_VEHICULO" in r["gaps"]),
        "necesitan_consumidor": sum(1 for r in enriched_rows if "NECESITA_CONSUMIDOR" in r["gaps"]),
        "bloqueados_por_valor": sum(1 for r in enriched_rows if r["bloqueado_por_valor"]),
        "por_fase": {},
    }
    
    for phase in ["Phase_00", "Phase_01", "Phase_02", "Phase_03", "Phase_04", "Phase_05", "Phase_06", "Phase_07", "Phase_08", "Phase_09", "N/A"]:
        phase_rows = [r for r in enriched_rows if r["phase"] == phase]
        if phase_rows:
            summary["por_fase"][phase] = {
                "total": len(phase_rows),
                "irrigables": sum(1 for r in phase_rows if r["accion_recomendada"] == "IRRIGABLE_AHORA"),
                "sin_vehiculo": sum(1 for r in phase_rows if not r["tiene_vehiculo"]),
                "sin_consumidor": sum(1 for r in phase_rows if not r["tiene_consumidor"]),
                "bloqueados_valor": sum(1 for r in phase_rows if r["bloqueado_por_valor"]),
            }
    
    return {
        "summary": summary,
        "rows": enriched_rows,
    }


def write_outputs(report: dict[str, Any], out_json: Path, out_csv: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # CSV
    fieldnames = [
        "json_file_path",
        "stage",
        "phase",
        "vehiculos_str",
        "vehiculo_count",
        "consumidores_str",
        "consumidor_count",
        "irrigability_bucket",
        "tiene_vehiculo",
        "tiene_consumidor",
        "bloqueado_por_valor",
        "gaps_str",
        "accion_recomendada",
        "added_value",
        "notes",
        "consumer_scope",
        "file_exists",
        "file_bytes",
    ]
    
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["rows"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabana", default="artifacts/matrix_sabana.json")
    ap.add_argument("--out-json", default="artifacts/sabana_final_decisiones.json")
    ap.add_argument("--out-csv", default="artifacts/sabana_final_decisiones.csv")
    args = ap.parse_args()
    
    report = generate(REPO_ROOT / args.sabana)
    write_outputs(report, REPO_ROOT / args.out_json, REPO_ROOT / args.out_csv)
    
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
