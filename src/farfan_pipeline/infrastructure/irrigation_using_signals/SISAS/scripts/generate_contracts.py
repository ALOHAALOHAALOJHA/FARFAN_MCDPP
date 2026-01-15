# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/scripts/generate_contracts.py

import csv
import json
import os
from typing import Dict, List, Any
from dataclasses import asdict

from .. core.contracts import IrrigationContract, ContractStatus, ContractRegistry
from ..irrigation. irrigation_map import IrrigationSource, IrrigabilityStatus


def generate_contracts_from_csv(csv_path: str) -> ContractRegistry:
    """
    Genera contratos de irrigación desde sabana_final_decisiones.csv
    """
    registry = ContractRegistry()
    
    if not os.path.exists(csv_path):
        return registry

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Filtrar items no canónicos
            if row. get("added_value") == "MARGINAL":
                continue
            if row.get("stage") == "External":
                continue
            
            # Parsear datos
            file_path = row. get("json_file_path", "")
            stage = row.get("stage", "")
            phase = row.get("phase", "")
            vehicles = parse_list(row.get("vehiculos_str", ""))
            consumers = parse_list(row.get("consumidores_str", ""))
            gaps = parse_list(row.get("gaps_str", ""))
            irrigability = row.get("irrigability_bucket", "")
            
            # Determinar estado del contrato
            if irrigability == "irrigable_now" and not gaps:
                status = ContractStatus.ACTIVE
            elif irrigability == "not_irrigable_yet": 
                status = ContractStatus. DRAFT
            else:
                status = ContractStatus.SUSPENDED
            
            # Crear contrato
            contract = IrrigationContract(
                contract_id=f"IC_{file_path. replace('/', '_').replace('.json', '')}",
                source_file=file_path. split('/')[-1] if '/' in file_path else file_path,
                source_path=file_path,
                source_phase=phase,
                vehicles=vehicles,
                consumers=consumers,
                vocabulary_aligned=("VOCAB_SEÑALES_NO_ALINEADO" not in gaps and 
                                   "VOCAB_CAPACIDADES_NO_ALINEADO" not in gaps),
                gaps=gaps,
                status=status
            )
            
            registry.register_irrigation(contract)
    
    return registry


def parse_list(value: str) -> List[str]:
    """Parsea lista separada por comas"""
    if not value or value == "NINGUNO":
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def export_contracts_to_json(registry: ContractRegistry, output_path: str):
    """Exporta contratos a JSON"""
    contracts = {
        cid: contract.to_dict() 
        for cid, contract in registry.irrigation_contracts.items()
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(contracts, f, indent=2, ensure_ascii=False)


def generate_gap_resolution_tasks(registry: ContractRegistry) -> List[Dict[str, Any]]:
    """
    Genera tareas de resolución de gaps
    """
    tasks = []
    
    blocked = registry.get_blocked_contracts()
    
    # Agrupar por tipo de gap
    by_gap:  Dict[str, List[str]] = {}
    for contract, gaps in blocked: 
        for gap in gaps:
            if gap not in by_gap:
                by_gap[gap] = []
            by_gap[gap]. append(contract. source_path)
    
    # Generar tareas
    priority = 1
    
    if "NECESITA_VEHICULO" in by_gap: 
        tasks.append({
            "priority": priority,
            "gap_type": "NECESITA_VEHICULO",
            "action": "AGREGAR_CARGA_EN_VEHICULO",
            "description": "Asignar vehículos a archivos que no tienen",
            "files_affected": len(by_gap["NECESITA_VEHICULO"]),
            "files":  by_gap["NECESITA_VEHICULO"],
            "suggested_vehicles": {
                "_registry/entities/":  "signal_intelligence_layer",
                "_registry/membership_criteria/": "signal_intelligence_layer",
                "colombia_context/": "signal_enhancement_integrator",
                "config/": "signal_loader"
            }
        })
        priority += 1
    
    if "NECESITA_CONSUMIDOR" in by_gap: 
        tasks.append({
            "priority": priority,
            "gap_type": "NECESITA_CONSUMIDOR",
            "action": "DECLARAR_CONSUMIDOR_EN_FASE",
            "description": "Declarar consumidores para archivos sin destino",
            "files_affected": len(by_gap["NECESITA_CONSUMIDOR"]),
            "files": by_gap["NECESITA_CONSUMIDOR"],
            "suggested_consumers":  {
                "_registry/patterns/MASTER_INDEX.json": "phase2_pattern_consumer. py",
                "_registry/questions/integration_map.json": "phase_integration_consumer.py",
                "_registry/questions/meso_questions.json": "phase7_meso_consumer.py",
                "validations/": "validation_consumer. py"
            }
        })
        priority += 1
    
    if "VOCAB_SEÑALES_NO_ALINEADO" in by_gap:
        tasks.append({
            "priority": priority,
            "gap_type": "VOCAB_SEÑALES_NO_ALINEADO",
            "action": "ALINEAR_VOCABULARIOS",
            "description": "Mapear archivos a tipos de señales específicos",
            "files_affected":  len(by_gap["VOCAB_SEÑALES_NO_ALINEADO"]),
            "files": by_gap["VOCAB_SEÑALES_NO_ALINEADO"],
            "mapping_required": True
        })
        priority += 1
    
    if "VOCAB_CAPACIDADES_NO_ALINEADO" in by_gap:
        tasks. append({
            "priority": priority,
            "gap_type":  "VOCAB_CAPACIDADES_NO_ALINEADO",
            "action": "ALINEAR_CAPACIDADES",
            "description": "Declarar capacidades requeridas por consumidores",
            "files_affected": len(by_gap["VOCAB_CAPACIDADES_NO_ALINEADO"]),
            "files":  by_gap["VOCAB_CAPACIDADES_NO_ALINEADO"]
        })
    
    return tasks


if __name__ == "__main__": 
    # Generar contratos
    csv_path = "artifacts/sabana_final_decisiones.csv" # Adjusted path based on file tree
    if not os.path.exists(csv_path):
        csv_path = "sabana_final_decisiones.csv"

    registry = generate_contracts_from_csv(csv_path)
    
    # Exportar a JSON
    os.makedirs("_registry", exist_ok=True)
    export_contracts_to_json(registry, "_registry/irrigation_contracts.json")
    
    # Generar tareas de resolución
    tasks = generate_gap_resolution_tasks(registry)
    
    with open("_registry/gap_resolution_tasks.json", 'w', encoding='utf-8') as f:
        json. dump(tasks, f, indent=2, ensure_ascii=False)
    
    # Estadísticas
    stats = {
        "total_contracts": len(registry.irrigation_contracts),
        "active":  len([c for c in registry.irrigation_contracts.values() 
                      if c.status == ContractStatus.ACTIVE]),
        "pending": len([c for c in registry.irrigation_contracts.values() 
                       if c.status == ContractStatus.DRAFT]),
        "suspended": len([c for c in registry.irrigation_contracts.values() 
                         if c.status == ContractStatus.SUSPENDED]),
        "resolution_tasks": len(tasks)
    }
    
    print(json.dumps(stats, indent=2))