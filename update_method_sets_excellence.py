#!/usr/bin/env python3
"""
ACTUALIZACIÓN DE method_sets_by_question.json - VERSIÓN EXCELENCIA

Añade ~50 métodos verificados del dispensario existente para alcanzar
calidad epistémica de excelencia.
"""

import json
from pathlib import Path

# Paths
assets_path = Path("src/farfan_pipeline/phases/Phase_two/epistemological_assets")
method_sets_file = assets_path / "method_sets_by_question.json"
classified_file = assets_path / "classified_methods.json"

# Backup
backup_file = assets_path / f"method_sets_by_question_backup_{json.load(open(method_sets_file))['metadata']['version']}.json"

print("=" * 80)
print("ACTUALIZANDO method_sets_by_question.json - VERSIÓN EXCELENCIA")
print("=" * 80)
print()

# 1. Crear backup
print("1. Creando backup...")
with open(method_sets_file) as f:
    data = json.load(f)

with open(backup_file, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"   ✅ Backup creado: {backup_file}")
print()

# 2. Cargar classified_methods para obtener definiciones completas
print("2. Cargando definiciones de métodos clasificados...")
with open(classified_file) as f:
    classified_data = json.load(f)

# Crear mapa method_name -> definición completa
method_definitions = {}
for method in classified_data["all_methods"]:
    method_definitions[method["method_name"]] = method

print(f"   ✅ {len(method_definitions)} métodos cargados")
print()

# 3. Definir adiciones por contrato (solo method_names)
# Basado en el catálogo de excelencia creado previamente
additions = {
    # DIM01_INSUMOS (D1)
    "D1_Q1": {
        "phase_a_N1": [
            "_extract_numerical_values",
            "_extract_financial_amounts",
            "_check_official_sources",
            "_check_year_reference",
        ]
    },
    "D1_Q2": {
        "phase_b_N2": [
            "calculate_max_gap",
            "_detect_allocation_gaps",
        ]
    },
    "D1_Q3": {
        "phase_a_N1": [
            "extract_tables",
        ]
    },
    "D1_Q4": {
        "phase_a_N1": [
            "extract_entity_activity",
        ]
    },
    "D1_Q5": {
        "phase_c_N3": [
            "verify_temporal_consistency",
        ]
    },

    # DIM02_ACTIVIDADES (D2)
    "D2_Q1": {
        "phase_a_N1": [
            "extract_tables",
            "_extract_from_ppi_dict",
        ]
    },
    "D2_Q2": {
        "phase_c_N3": [
            "audit_causal_coherence_d6",
        ]
    },
    "D2_Q3": {
        "phase_c_N3": [
            "audit_causal_coherence_d6",
        ]
    },
    "D2_Q4": {
        "phase_c_N3": [
            "_perform_counterfactual_budget_check",
        ]
    },
    "D2_Q5": {
        "phase_c_N3": [
            "check_consistency",
            "detect_any_contradiction",
        ]
    },

    # DIM03_PRODUCTOS (D3)
    "D3_Q1": {
        "phase_b_N2": [
            "calculate_coverage",
            "extract_statistical_metadata",
        ]
    },
    "D3_Q2": {
        "phase_b_N2": [
            "compare_to_peers",
        ]
    },
    "D3_Q3": {
        "phase_b_N2": [
            "calculate_coverage",
        ]
    },
    "D3_Q4": {
        "phase_c_N3": [
            "verify_temporal_consistency",
            "check_consistency",
        ]
    },
    "D3_Q5": {
        "phase_c_N3": [
            "_assess_financial_sustainability",
        ]
    },

    # DIM04_RESULTADOS (D4)
    "D4_Q1": {
        "phase_c_N3": [
            "audit_causal_coherence_d6",
        ]
    },
    "D4_Q2": {
        "phase_b_N2": [
            "infer_mechanisms",
            "extract_statistical_metadata",
        ]
    },
    "D4_Q3": {
        "phase_c_N3": [
            "_perform_counterfactual_budget_check",
            "calculate_sufficiency",
        ]
    },
    "D4_Q4": {
        "phase_c_N3": [
            "detect_any_contradiction",
            "check_consistency",
        ]
    },
    "D4_Q5": {
        "phase_c_N3": [
            "bayesian_counterfactual_audit",
        ]
    },

    # DIM05_IMPACTOS (D5)
    "D5_Q1": {
        "phase_b_N2": [
            "analyze_financial_feasibility",
            "infer_mechanisms",
        ]
    },
    "D5_Q2": {
        "phase_b_N2": [
            "analyze_financial_feasibility",
            "_assess_financial_sustainability",
        ]
    },
    "D5_Q3": {
        "phase_c_N3": [
            "update_priors_from_feedback",
        ]
    },
    "D5_Q4": {
        "phase_b_N2": [
            "compare_to_peers",
        ]
    },
    "D5_Q5": {
        "phase_c_N3": [
            "audit_evidence_traceability",
            "_assess_financial_sustainability",
        ]
    },

    # DIM06_CAUSALIDAD (D6)
    "D6_Q1": {
        "phase_c_N3": [
            "audit_causal_coherence_d6",
            "infer_mechanisms",
        ]
    },
    "D6_Q2": {
        "phase_b_N2": [
            "infer_mechanisms",
            "extract_statistical_metadata",
        ]
    },
    "D6_Q3": {
        "phase_c_N3": [
            "detect_any_contradiction",
        ]
    },
    "D6_Q4": {
        "phase_c_N3": [
            "audit_evidence_traceability",
            "update_priors_from_feedback",
        ]
    },
    "D6_Q5": {
        "phase_b_N2": [
            "audit_causal_coherence_d6",
            "infer_mechanisms",
        ]
    },
}

# 4. Aplicar adiciones
print("3. Aplicando adiciones de métodos...")
print()

total_added = 0
missing_methods = []

for q_id, phases_to_add in additions.items():
    if q_id not in data["method_sets"]:
        print(f"   ⚠️  {q_id}: NO ENCONTRADO")
        continue

    for phase_key, method_names_to_add in phases_to_add.items():
        if phase_key not in data["method_sets"][q_id]:
            print(f"   ⚠️  {q_id}.{phase_key}: NO ENCONTRADO")
            continue

        current_methods = data["method_sets"][q_id][phase_key]
        current_names = {m["method_name"] for m in current_methods}

        for method_name in method_names_to_add:
            if method_name in current_names:
                continue  # Ya existe, no duplicar

            if method_name not in method_definitions:
                missing_methods.append(f"{q_id}.{phase_key}: {method_name}")
                continue

            # Añadir método con su definición completa
            method_def = method_definitions[method_name].copy()
            current_methods.append(method_def)
            total_added += 1

        # Actualizar el array
        data["method_sets"][q_id][phase_key] = current_methods

if missing_methods:
    print("   ⚠️  Métodos faltantes en classified_methods.json:")
    for m in missing_methods:
        print(f"      - {m}")
    print()

print(f"   ✅ {total_added} métodos añadidos")
print()

# 5. Actualizar metadata
print("4. Actualizando metadata...")
data["metadata"]["version"] = "1.1.0-excellence"
data["metadata"]["total_questions"] = 30
data["metadata"]["generation_date"] = "2026-01-02"
data["metadata"]["update_notes"] = "Excellence version: Added ~50 verified methods from dispensary for enhanced epistemic quality"
print(f"   ✅ Versión actualizada: {data['metadata']['version']}")
print()

# 6. Calcular nuevas estadísticas
print("5. Calculando nuevas estadísticas...")
stats_before = {"N1": 5, "N2": 5, "N3": 3, "total": 13}
stats_after = {"N1": [], "N2": [], "N3": [], "total": []}

for q_id, q_data in data["method_sets"].items():
    n1 = len(q_data.get("phase_a_N1", []))
    n2 = len(q_data.get("phase_b_N2", []))
    n3 = len(q_data.get("phase_c_N3", []))
    total = n1 + n2 + n3
    stats_after["N1"].append(n1)
    stats_after["N2"].append(n2)
    stats_after["N3"].append(n3)
    stats_after["total"].append(total)

print("   Distribución después de actualización:")
for key in ["N1", "N2", "N3", "total"]:
    values = stats_after[key]
    print(f"      {key}: min={min(values)}, max={max(values)}, promedio={sum(values)/len(values):.1f}")
print()

# 7. Guardar archivo actualizado
print("6. Guardando archivo actualizado...")
output_file = method_sets_file
with open(output_file, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"   ✅ Archivo actualizado: {output_file}")
print()

# 8. Resumen
print("=" * 80)
print("RESUMEN DE ACTUALIZACIÓN")
print("=" * 80)
print()
print(f"✅ Backup creado: {backup_file.name}")
print(f"✅ Métodos añadidos: {total_added}")
print(f"✅ Nueva versión: {data['metadata']['version']}")
print(f"✅ Archivo actualizado: {method_sets_file}")
print()
print("CONTRATOS MODIFICADOS:")
for q_id in sorted(additions.keys()):
    q_data = data["method_sets"][q_id]
    n1 = len(q_data.get("phase_a_N1", []))
    n2 = len(q_data.get("phase_b_N2", []))
    n3 = len(q_data.get("phase_c_N3", []))
    print(f"   {q_id}: {n1+n2+n3} métodos (N1:{n1}, N2:{n2}, N3:{n3})")
print()
print("✅ ACTUALIZACIÓN COMPLETADA - Listo para regenerar contratos")
