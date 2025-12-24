#!/usr/bin/env python3
"""
Repara D5-Q3-v4.json: la línea 142 tiene escapes incorrectos.
Reconstruye phase_C_litigation con JSON válido.
"""

import json

FILEPATH = "/Users/recovered/PycharmProjects/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/contracts_v4/D5-Q3-v4.json"

# phase_C_litigation canónico para TYPE_B
PHASE_C_CANONICAL = {
    "description": "Audit layer - validation gates that can VETO findings",
    "level": "N3",
    "level_name": "Auditoría y Robustez",
    "epistemology": "Falsacionismo popperiano",
    "asymmetry_principle": "N3 can invalidate N1/N2 findings, but N1/N2 CANNOT invalidate N3",
    "methods": [
        {
            "class_name": "BayesianCounterfactualAuditor",
            "method_name": "validate_posterior_consistency",
            "mother_file": "derek_beach.py",
            "provides": "bayesiancounterfactualauditor.validate_posterior_consistency",
            "level": "N3-AUD",
            "output_type": "CONSTRAINT",
            "fusion_behavior": "gate",
            "description": "Valida consistencia bayesiana de posteriors",
            "requires": ["raw_facts", "inferences"],
            "modulates": ["raw_facts.confidence", "inferences.confidence"],
            "classification_rationale": "Auditoría de coherencia probabilística → N3-AUD",
            "veto_conditions": {
                "posterior_inconsistency": {
                    "trigger": "inconsistency_detected",
                    "action": "block_branch",
                    "scope": "affected_claims",
                    "confidence_multiplier": 0.0
                },
                "prior_mismatch": {
                    "trigger": "deviation > 2_sigma",
                    "action": "reduce_confidence",
                    "scope": "source_facts",
                    "confidence_multiplier": 0.5
                }
            }
        }
    ],
    "dependencies": ["phase_A_construction", "phase_B_computation"],
    "output_target": "audit_results",
    "fusion_mode": "modulation"
}

def main():
    print("Reparando D5-Q3-v4.json...")
    
    # Leer archivo como texto
    with open(FILEPATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar líneas problemáticas (141-143)
    # Reconstruir el archivo línea por línea
    new_lines = []
    skip_until_question_context = False
    
    for i, line in enumerate(lines, 1):
        if i == 142:
            # Reemplazar línea corrupta con phase_C_litigation válido
            phase_c_json = json.dumps(PHASE_C_CANONICAL, indent=8, ensure_ascii=False)
            # Indentar correctamente
            new_lines.append('      "phase_C_litigation": ' + phase_c_json.replace('\n', '\n      ') + '\n')
            skip_until_question_context = True
        elif skip_until_question_context:
            if '"question_context"' in line:
                skip_until_question_context = False
                new_lines.append('    }\n')  # Cerrar execution_phases
                new_lines.append('  },\n')  # Cerrar method_binding
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Escribir archivo reparado
    with open(FILEPATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    # Validar JSON resultante
    try:
        with open(FILEPATH, 'r', encoding='utf-8') as f:
            json.load(f)
        print("✅ JSON reparado y validado correctamente")
    except json.JSONDecodeError as e:
        print(f"❌ Error de validación: {e}")

if __name__ == "__main__":
    main()
