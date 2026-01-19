#!/usr/bin/env python3
"""
Script para generar la matriz final de auditoría SISAS.

Esta matriz contiene:
- Todos los archivos del questionnaire canónico
- Condiciones de irrigación para cada archivo
- Estado de implementación SISAS
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict


# Mapeo de vehículos según tipo de archivo
VEHICLE_ASSIGNMENTS = {
    "metadata": ["signal_quality_metrics", "signal_enhancement_integrator"],
    "questions": ["signal_context_scoper", "signal_evidence_extractor", "signal_intelligence_layer"],
    "keywords": ["signal_registry", "signal_context_scoper"],
    "aggregation_rules": ["signal_quality_metrics", "signal_intelligence_layer"],
    "contextual_enrichment": ["signal_enhancement_integrator", "signal_evidence_extractor"],
    "scoring_system": ["signal_intelligence_layer", "signal_quality_metrics"],
    "governance": ["signal_enhancement_integrator", "signal_registry"],
    "semantic": ["signal_context_scoper", "signal_evidence_extractor"],
    "default": ["signal_context_scoper", "signal_quality_metrics"]
}

# Mapeo de consumidores según fase y tipo de archivo
CONSUMER_ASSIGNMENTS = {
    "phase_0": ["phase0_bootstrap", "phase0_providers", "phase0_wiring_types"],
    "phase_1": ["phase1_signal_enrichment", "phase1_cpp_ingestion"],
    "phase_2": ["phase2_factory_consumer", "phase2_evidence_consumer", "phase2_contract_consumer"],
    "phase_3": ["phase3_scoring"],
    "phase_7": ["phase7_meso_consumer"],
    "phase_8": ["phase8_recommendations"],
}

# Fases asignadas por tipo de archivo
PHASE_ASSIGNMENTS = {
    "policy_areas": "phase_1",
    "dimensions": "phase_1",
    "clusters": "phase_2",
    "questions": "phase_2",
    "micro_questions": "phase_2",
    "atomized_questions": "phase_2",
    "CORE_DATA": "phase_0",
    "REGISTRY_DATA": "phase_0",
    "DOMAIN_DATA": "phase_1",
    "OPERATIONAL_DATA": "phase_2",
    "config": "phase_0",
    "validations": "phase_0",
}


def get_file_category(file_path: str) -> str:
    """Determina la categoría de un archivo"""
    path_parts = file_path.split("/")

    if "policy_areas" in path_parts:
        return "DOMAIN_DATA/policy_areas"
    elif "dimensions" in path_parts:
        return "DOMAIN_DATA/dimensions"
    elif "clusters" in path_parts:
        return "DOMAIN_DATA/clusters"
    elif "questions" in path_parts:
        return "QUESTION_FILES/questions"
    elif "micro_questions" in path_parts:
        return "QUESTION_FILES/micro_questions"
    elif "atomized_questions" in path_parts:
        return "QUESTION_FILES/atomized_questions"
    elif "config" in path_parts:
        return "OPERATIONAL_DATA/config"
    elif "validations" in path_parts:
        return "OPERATIONAL_DATA/validations"
    elif "semantic" in path_parts:
        return "OPERATIONAL_DATA/semantic"
    elif "scoring" in path_parts:
        return "OPERATIONAL_DATA/scoring_system"
    elif "governance" in path_parts:
        return "OPERATIONAL_DATA/governance"
    elif "patterns" in path_parts:
        return "REGISTRY_DATA/patterns"
    elif "entities" in path_parts:
        return "REGISTRY_DATA/entities"
    elif "membership_criteria" in path_parts:
        return "REGISTRY_DATA/membership_criteria"
    elif "keywords" in path_parts:
        return "REGISTRY_DATA/keywords"
    elif "capabilities" in path_parts:
        return "REGISTRY_DATA/capabilities"
    elif "colombia_context" in path_parts:
        return "OPERATIONAL_DATA/colombia_context"
    elif "pdet_context" in path_parts:
        return "OPERATIONAL_DATA/pdet_context"
    elif "cross_cutting" in path_parts:
        return "OPERATIONAL_DATA/cross_cutting"
    else:
        return "UNKNOWN"


def get_assigned_vehicles(file_path: str) -> List[str]:
    """Determina vehículos asignados para un archivo"""
    filename = os.path.basename(file_path)

    if "metadata" in filename:
        return VEHICLE_ASSIGNMENTS["metadata"]
    elif "questions" in filename:
        return VEHICLE_ASSIGNMENTS["questions"]
    elif "keywords" in filename:
        return VEHICLE_ASSIGNMENTS["keywords"]
    elif "aggregation" in filename:
        return VEHICLE_ASSIGNMENTS["aggregation_rules"]
    elif "contextual" in filename:
        return VEHICLE_ASSIGNMENTS["contextual_enrichment"]
    elif "scoring" in filename:
        return VEHICLE_ASSIGNMENTS["scoring_system"]
    elif "governance" in filename:
        return VEHICLE_ASSIGNMENTS["governance"]
    elif "semantic" in filename:
        return VEHICLE_ASSIGNMENTS["semantic"]
    else:
        return VEHICLE_ASSIGNMENTS["default"]


def get_assigned_consumers(file_path: str) -> List[str]:
    """Determina consumidores asignados para un archivo"""
    category = get_file_category(file_path)

    # Extraer fase base
    if "/" in category:
        base_category = category.split("/")[0]
    else:
        base_category = category

    phase = PHASE_ASSIGNMENTS.get(base_category, "phase_1")
    return CONSUMER_ASSIGNMENTS.get(phase, [])


def check_irrigation_conditions(file_path: str) -> Dict[str, Any]:
    """Verifica condiciones de irrigación para un archivo"""
    vehicles = get_assigned_vehicles(file_path)
    consumers = get_assigned_consumers(file_path)

    # Verificar condiciones
    vehicle_assigned = len(vehicles) > 0
    consumer_assigned = len(consumers) > 0
    # Contract: No existen contratos de irrigación creados aún
    contract_created = False
    # Signals: Los vehículos existen pero no hay contratos
    signals_generated = vehicle_assigned
    # Connected: No conectado al flujo SISAS (usa CanonicalQuestionnaireResolver)
    connected_to_sisas = False

    # Determinar estado general
    if vehicle_assigned and consumer_assigned and contract_created and connected_to_sisas:
        status = "READY"
    elif vehicle_assigned and consumer_assigned:
        status = "INTEGRATION_NEEDED"
    elif vehicle_assigned:
        status = "PARTIAL"
    else:
        status = "BLOCKED"

    return {
        "vehicle_assigned": vehicle_assigned,
        "consumer_assigned": consumer_assigned,
        "contract_created": contract_created,
        "signals_generated": signals_generated,
        "connected_to_sisas": connected_to_sisas,
        "status": status
    }


def generate_sisas_audit_matrix(base_path: str = "canonic_questionnaire_central") -> Dict[str, Any]:
    """Genera la matriz completa de auditoría SISAS"""

    # Descubrir todos los archivos JSON
    all_files = []
    for root, dirs, files in os.walk(base_path):
        for filename in files:
            if filename.endswith(".json"):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, base_path)
                all_files.append(rel_path)

    all_files.sort()

    # Agrupar por categoría
    files_by_category = defaultdict(list)
    for file_path in all_files:
        category = get_file_category(file_path)
        files_by_category[category].append(file_path)

    # Generar matriz detallada
    detailed_matrix = {}
    for file_path in all_files:
        conditions = check_irrigation_conditions(file_path)
        vehicles = get_assigned_vehicles(file_path)
        consumers = get_assigned_consumers(file_path)
        category = get_file_category(file_path)

        # Obtener tamaño de archivo
        full_path = os.path.join(base_path, file_path)
        file_size = os.path.getsize(full_path) if os.path.exists(full_path) else 0

        detailed_matrix[file_path] = {
            "category": category,
            "vehicles_assigned": vehicles,
            "consumers_assigned": consumers,
            "irrigation_conditions": {
                "vehicle_assigned": conditions["vehicle_assigned"],
                "consumer_assigned": conditions["consumer_assigned"],
                "contract_created": conditions["contract_created"],
                "signals_generated": conditions["signals_generated"],
                "connected_to_sisas": conditions["connected_to_sisas"]
            },
            "status": conditions["status"],
            "file_size_bytes": file_size
        }

    # Calcular estadísticas
    status_counts = defaultdict(int)
    for file_data in detailed_matrix.values():
        status_counts[file_data["status"]] += 1

    total_files = len(all_files)
    ready_pct = (status_counts.get("READY", 0) / total_files * 100) if total_files > 0 else 0
    integration_pct = (status_counts.get("INTEGRATION_NEEDED", 0) / total_files * 100) if total_files > 0 else 0
    partial_pct = (status_counts.get("PARTIAL", 0) / total_files * 100) if total_files > 0 else 0
    blocked_pct = (status_counts.get("BLOCKED", 0) / total_files * 100) if total_files > 0 else 0

    # Crear resumen ejecutivo
    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "specification": "SISAS 5.0 AUDIT MATRIX - FINAL DELIVERABLE",
        "total_files": total_files,
        "status_distribution": {
            "READY": status_counts.get("READY", 0),
            "INTEGRATION_NEEDED": status_counts.get("INTEGRATION_NEEDED", 0),
            "PARTIAL": status_counts.get("PARTIAL", 0),
            "BLOCKED": status_counts.get("BLOCKED", 0)
        },
        "percentages": {
            "ready": f"{ready_pct:.1f}%",
            "integration_needed": f"{integration_pct:.1f}%",
            "partial": f"{partial_pct:.1f}%",
            "blocked": f"{blocked_pct:.1f}%"
        },
        "categories": dict(sorted(
            [(cat, len(files)) for cat, files in files_by_category.items()],
            key=lambda x: x[1],
            reverse=True
        ))
    }

    # Matriz por categorías
    category_matrix = {}
    for category, files in files_by_category.items():
        category_files = {}
        for file_path in files:
            category_files[file_path] = detailed_matrix[file_path]

        # Calcular stats por categoría
        cat_status_counts = defaultdict(int)
        for file_data in category_files.values():
            cat_status_counts[file_data["status"]] += 1

        category_matrix[category] = {
            "file_count": len(files),
            "status_distribution": dict(cat_status_counts),
            "files": category_files
        }

    return {
        "summary": summary,
        "detailed_matrix": detailed_matrix,
        "category_matrix": category_matrix,
        "vehicle_assignments": VEHICLE_ASSIGNMENTS,
        "consumer_assignments": CONSUMER_ASSIGNMENTS,
        "phase_assignments": PHASE_ASSIGNMENTS
    }


def main():
    """Función principal"""
    print("Generating SISAS 5.0 Audit Matrix...")

    matrix = generate_sisas_audit_matrix()

    # Guardar matriz completa
    output_path = "artifacts/audit_reports/SISAS_5.0_FINAL_AUDIT_MATRIX.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(matrix, f, indent=2, ensure_ascii=False)

    print(f"\nMatrix saved to: {output_path}")
    print(f"\nSUMMARY:")
    print(f"  Total files: {matrix['summary']['total_files']}")
    print(f"  Status distribution:")
    for status, count in matrix['summary']['status_distribution'].items():
        pct = matrix['summary']['percentages'].get(status.lower(), "0%")
        print(f"    {status}: {count} ({pct})")

    # Guardar versión resumida (solo checklist)
    checklist_path = "artifacts/audit_reports/SISAS_5.0_IRRIGATION_CHECKLIST.json"
    checklist = {
        "specification": "SISAS 5.0 IRRIGATION CHECKLIST",
        "timestamp": matrix["summary"]["timestamp"],
        "total_files": matrix["summary"]["total_files"],
        "checklist": {}
    }

    for file_path, data in matrix["detailed_matrix"].items():
        checklist["checklist"][file_path] = {
            "status": data["status"],
            "vehicle_assigned": data["irrigation_conditions"]["vehicle_assigned"],
            "consumer_assigned": data["irrigation_conditions"]["consumer_assigned"],
            "contract_created": data["irrigation_conditions"]["contract_created"],
            "signals_generated": data["irrigation_conditions"]["signals_generated"],
            "connected_to_sisas": data["irrigation_conditions"]["connected_to_sisas"]
        }

    with open(checklist_path, 'w', encoding='utf-8') as f:
        json.dump(checklist, f, indent=2, ensure_ascii=False)

    print(f"\nChecklist saved to: {checklist_path}")

    return matrix


if __name__ == "__main__":
    main()
