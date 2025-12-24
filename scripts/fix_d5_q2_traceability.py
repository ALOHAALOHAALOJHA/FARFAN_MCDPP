#!/usr/bin/env python3
"""
Script de corrección rigurosa para D5-Q2-v4.json.
Inserta el campo 'prohibitions' en traceability.generation de forma segura.
"""

import json
import os

FILEPATH = "/Users/recovered/PycharmProjects/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/contracts_v4/D5-Q2-v4.json"

def fix_d5_q2():
    print(f"🔧 Procesando {FILEPATH}...")
    
    if not os.path.exists(FILEPATH):
        print(f"❌ Archivo no encontrado: {FILEPATH}")
        return

    try:
        with open(FILEPATH, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        # Navegar a traceability.generation
        if "traceability" not in contract:
            contract["traceability"] = {}
        
        if "generation" not in contract["traceability"]:
            contract["traceability"]["generation"] = {}
            
        generation = contract["traceability"]["generation"]
        
        # Verificar si ya existe
        if "prohibitions" in generation:
            print("ℹ️ 'prohibitions' ya existe. Verificando valor...")
            if generation["prohibitions"] == {"v3_recovery": "FORBIDDEN"}:
                print("✅ Valor correcto ya presente.")
                return
            else:
                print("⚠️ Valor incorrecto, actualizando...")
        
        # Insertar/Actualizar
        generation["prohibitions"] = {"v3_recovery": "FORBIDDEN"}
        
        # Guardar con formato consistente
        with open(FILEPATH, 'w', encoding='utf-8') as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)
            
        print("✅ Corrección aplicada exitosamente en D5-Q2.")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error JSON: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    fix_d5_q2()
