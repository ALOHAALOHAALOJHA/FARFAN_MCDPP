#!/usr/bin/env python3
"""
Script de corrección sistemática para contratos D5 (TYPE_B).
Aplica correcciones canónicas según episte_refact.md líneas 583-589.

TYPE_B requiere:
- N1_fact_fusion.strategy: "concat"
- N2_parameter_fusion.strategy: "bayesian_update"
- N3_constraint_fusion.strategy: "veto_gate"
"""

import json
import os
from datetime import datetime

CONTRACTS_DIR = "/Users/recovered/PycharmProjects/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/contracts_v4"

# Contratos TYPE_B en el lote D5
TYPE_B_CONTRACTS = ["D5-Q3-v4.json", "D5-Q4-v4.json", "D5-Q5-v4.json"]

# Estrategias canónicas para TYPE_B según episte_refact.md L586
CANONICAL_TYPE_B = {
    "N1_fact_fusion": {"strategy": "concat"},
    "N2_parameter_fusion": {"strategy": "bayesian_update"},
    "N3_constraint_fusion": {"strategy": "veto_gate"}
}

def load_contract(filepath):
    """Carga contrato JSON con validación."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_contract(filepath, data):
    """Guarda contrato JSON con formato consistente."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def apply_fusion_corrections(contract, contract_name):
    """Aplica correcciones de fusión según el tipo de contrato."""
    corrections = []
    
    # Verificar que es TYPE_B
    contract_type = contract.get("identity", {}).get("contract_type", "UNKNOWN")
    if contract_type != "TYPE_B":
        print(f"  ⚠️ {contract_name} no es TYPE_B (es {contract_type}), saltando...")
        return corrections
    
    fusion_spec = contract.get("fusion_specification", {})
    level_strategies = fusion_spec.get("level_strategies", {})
    
    for level_key, canonical_values in CANONICAL_TYPE_B.items():
        current = level_strategies.get(level_key, {})
        current_strategy = current.get("strategy", "MISSING")
        canonical_strategy = canonical_values["strategy"]
        
        if current_strategy != canonical_strategy:
            corrections.append({
                "field": f"fusion_specification.level_strategies.{level_key}.strategy",
                "from": current_strategy,
                "to": canonical_strategy
            })
            level_strategies[level_key]["strategy"] = canonical_strategy
    
    # Añadir prohibitions si no existe
    traceability = contract.get("traceability", {})
    generation = traceability.get("generation", {})
    if "prohibitions" not in generation:
        generation["prohibitions"] = {"v3_recovery": "FORBIDDEN"}
        corrections.append({
            "field": "traceability.generation.prohibitions",
            "from": "MISSING",
            "to": {"v3_recovery": "FORBIDDEN"}
        })
    
    return corrections

def main():
    print("=" * 60)
    print("CORRECCIÓN SISTEMÁTICA D5 BATCH (TYPE_B)")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    total_corrections = 0
    report = []
    
    for contract_name in TYPE_B_CONTRACTS:
        filepath = os.path.join(CONTRACTS_DIR, contract_name)
        print(f"\n📄 Procesando: {contract_name}")
        
        if not os.path.exists(filepath):
            print(f"  ❌ Archivo no encontrado: {filepath}")
            continue
        
        try:
            contract = load_contract(filepath)
            corrections = apply_fusion_corrections(contract, contract_name)
            
            if corrections:
                save_contract(filepath, contract)
                print(f"  ✅ {len(corrections)} correcciones aplicadas:")
                for c in corrections:
                    print(f"     - {c['field']}: {c['from']} → {c['to']}")
                total_corrections += len(corrections)
            else:
                print(f"  ✓ Sin correcciones necesarias")
            
            report.append({
                "contract": contract_name,
                "corrections": corrections,
                "status": "OK"
            })
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON inválido: {e}")
            report.append({
                "contract": contract_name,
                "corrections": [],
                "status": f"JSON_ERROR: {e}"
            })
    
    print("\n" + "=" * 60)
    print(f"RESUMEN: {total_corrections} correcciones totales aplicadas")
    print("=" * 60)
    
    return report

if __name__ == "__main__":
    main()
