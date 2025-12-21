"""
Extrae los métodos y clases de los primeros 30 contratos (Q001-Q030, PA01)
desde EXECUTOR_METHODS_BY_FILE.json
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
EXECUTOR_METHODS_FILE = PROJECT_ROOT / "EXECUTOR_METHODS_BY_FILE.json"
QUESTIONNAIRE_FILE = PROJECT_ROOT / "canonic_questionnaire_central" / "questionnaire_monolith.json"
OUTPUT_FILE = PROJECT_ROOT / "FIRST_30_EXECUTOR_CONTRACTS.json"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_methods_with_usage(executor_data: dict) -> list[dict]:
    """Extrae todos los métodos con usage_count > 0"""
    methods_with_usage = []
    
    for file_info in executor_data.get("files", []):
        file_name = file_info.get("file_name", "")
        file_path = file_info.get("file_path", "")
        
        for class_info in file_info.get("classes", []):
            class_name = class_info.get("class_name", "")
            
            for method in class_info.get("methods", []):
                usage_count = method.get("usage_count", 0)
                if usage_count > 0:
                    methods_with_usage.append({
                        "class": class_name,
                        "method": method.get("name", ""),
                        "file": file_name,
                        "file_path": file_path,
                        "usage_count": usage_count,
                        "mapped_questions": method.get("mapped_questions", []),
                        "return_type": method.get("return_type"),
                        "parameters": method.get("parameters", []),
                        "line_start": method.get("line_start"),
                        "line_end": method.get("line_end"),
                        "is_private": method.get("is_private", False),
                        "docstring": method.get("docstring")
                    })
    
    return methods_with_usage


def extract_q001_q030_from_questionnaire(questionnaire_data: dict) -> list[dict]:
    """Extrae las preguntas Q001-Q030 del questionnaire"""
    questions = []
    micro_questions = questionnaire_data.get("blocks", {}).get("micro_questions", [])
    
    for q in micro_questions:
        q_id = q.get("question_id", "")
        q_global = q.get("question_global", 0)
        
        if 1 <= q_global <= 30:
            questions.append({
                "question_id": q_id,
                "question_global": q_global,
                "dimension_id": q.get("dimension_id"),
                "base_slot": q.get("base_slot"),
                "policy_area_id": q.get("policy_area_id"),
                "scoring_modality": q.get("scoring_modality"),
                "text": q.get("text", "")[:200] + "..." if len(q.get("text", "")) > 200 else q.get("text", ""),
                "method_sets": q.get("method_sets", []),
                "expected_elements": q.get("expected_elements", []),
                "patterns_count": len(q.get("patterns", []))
            })
    
    return sorted(questions, key=lambda x: x["question_global"])


def build_contracts(questions: list[dict], all_methods: list[dict]) -> list[dict]:
    """Construye los contratos con sus métodos asociados"""
    contracts = []
    
    methods_by_class_method = {}
    for m in all_methods:
        key = f"{m['class']}.{m['method']}"
        methods_by_class_method[key] = m
    
    for q in questions:
        contract = {
            "contract_id": q["question_id"],
            "question_global": q["question_global"],
            "dimension": q["dimension_id"],
            "base_slot": q["base_slot"],
            "policy_area": q["policy_area_id"],
            "scoring_modality": q["scoring_modality"],
            "text": q["text"],
            "patterns_count": q["patterns_count"],
            "expected_elements": q["expected_elements"],
            "methods": []
        }
        
        for ms in q.get("method_sets", []):
            class_name = ms.get("class", "")
            func_name = ms.get("function", "")
            key = f"{class_name}.{func_name}"
            
            if key in methods_by_class_method:
                method_info = methods_by_class_method[key]
                contract["methods"].append({
                    "class": class_name,
                    "method": func_name,
                    "file": method_info["file"],
                    "method_type": ms.get("method_type", ""),
                    "priority": ms.get("priority", 0),
                    "usage_count": method_info["usage_count"],
                    "return_type": method_info["return_type"],
                    "is_private": method_info["is_private"],
                    "line_range": f"{method_info['line_start']}-{method_info['line_end']}"
                })
            else:
                contract["methods"].append({
                    "class": class_name,
                    "method": func_name,
                    "file": "NOT_FOUND_IN_EXECUTOR",
                    "method_type": ms.get("method_type", ""),
                    "priority": ms.get("priority", 0),
                    "usage_count": 0,
                    "status": "METHOD_NOT_MAPPED"
                })
        
        contract["total_methods"] = len(contract["methods"])
        contract["methods_with_usage"] = sum(1 for m in contract["methods"] if m.get("usage_count", 0) > 0)
        contracts.append(contract)
    
    return contracts


def compute_statistics(contracts: list[dict], all_methods: list[dict]) -> dict:
    """Calcula estadísticas del resultado"""
    all_classes = set()
    all_method_names = set()
    total_usage = 0
    
    for c in contracts:
        for m in c["methods"]:
            all_classes.add(m["class"])
            all_method_names.add(f"{m['class']}.{m['method']}")
            total_usage += m.get("usage_count", 0)
    
    methods_by_file = defaultdict(int)
    for m in all_methods:
        methods_by_file[m["file"]] += 1
    
    return {
        "total_contracts": len(contracts),
        "total_unique_classes": len(all_classes),
        "total_unique_methods": len(all_method_names),
        "total_usage_count": total_usage,
        "methods_by_file": dict(methods_by_file),
        "source_methods_with_usage": len(all_methods)
    }


def main():
    print(f"[INFO] Cargando {EXECUTOR_METHODS_FILE}...")
    executor_data = load_json(EXECUTOR_METHODS_FILE)
    
    print(f"[INFO] Cargando {QUESTIONNAIRE_FILE}...")
    questionnaire_data = load_json(QUESTIONNAIRE_FILE)
    
    print("[INFO] Extrayendo métodos con usage_count > 0...")
    all_methods = extract_methods_with_usage(executor_data)
    print(f"       → {len(all_methods)} métodos encontrados")
    
    print("[INFO] Extrayendo Q001-Q030 del questionnaire...")
    questions = extract_q001_q030_from_questionnaire(questionnaire_data)
    print(f"       → {len(questions)} preguntas encontradas")
    
    print("[INFO] Construyendo contratos...")
    contracts = build_contracts(questions, all_methods)
    
    print("[INFO] Calculando estadísticas...")
    stats = compute_statistics(contracts, all_methods)
    
    policy_areas = questionnaire_data.get("canonical_notation", {}).get("policy_areas", {})
    pa01_info = policy_areas.get("PA01", {})
    
    result = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "Métodos y clases de los primeros 30 contratos de executors (Q001-Q030 para PA01)",
            "contract_range": "Q001-Q030",
            "policy_area": {
                "id": "PA01",
                "name": pa01_info.get("name", "Derechos de las mujeres e igualdad de género"),
                "legacy_id": pa01_info.get("legacy_id", "P1")
            },
            "source_files": [
                str(EXECUTOR_METHODS_FILE.name),
                str(QUESTIONNAIRE_FILE.name)
            ],
            "statistics": stats
        },
        "contracts": contracts,
        "all_methods_with_usage": sorted(all_methods, key=lambda x: (-x["usage_count"], x["class"], x["method"]))
    }
    
    print(f"[INFO] Guardando resultado en {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("RESUMEN DE EXTRACCIÓN")
    print("="*60)
    print(f"Contratos extraídos:     {stats['total_contracts']}")
    print(f"Clases únicas:           {stats['total_unique_classes']}")
    print(f"Métodos únicos:          {stats['total_unique_methods']}")
    print(f"Total usage_count:       {stats['total_usage_count']}")
    print(f"Métodos fuente (>0):     {stats['source_methods_with_usage']}")
    print("-"*60)
    print("Métodos por archivo:")
    for file, count in sorted(stats["methods_by_file"].items()):
        print(f"  {file}: {count}")
    print("="*60)
    print(f"\n✓ Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
