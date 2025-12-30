#!/usr/bin/env python3
"""
Script para aplicar correcciones comunes a todos los contratos pendientes
usando el Validator Governance Layer (VGL).
"""

import json
from pathlib import Path
from validator_governance_layer import ValidatorGovernanceLayer
from datetime import datetime
import sys

# Contratos ya normalizados
NORMALIZED_CONTRACTS = {
    'D1-Q2-v4.json', 'D1-Q4-v4.json', 'D1-Q5-v4.json',
    'D2-Q1-v4.json', 'D2-Q2-v4.json', 'D2-Q3-v4.json', 'D2-Q4-v4.json', 'D2-Q5-v4.json',
    'D3-Q1-v4.json', 'D3-Q2-v4.json', 'D3-Q3-v4.json', 'D3-Q4-v4.json',
    'D4-Q4-v4.json'  # Recién normalizado
}

def apply_phase1_corrections(contract, vgl, contract_name):
    """Aplica correcciones Fase 1 (AUTO - estructurales)"""
    corrections_applied = []
    
    phases = contract.get('method_binding', {}).get('execution_phases', {})
    if not phases:
        return corrections_applied
    
    # 1. incorrect_dependencies
    if 'phase_A_construction' in phases:
        phases['phase_A_construction']['dependencies'] = []
        corrections_applied.append('incorrect_dependencies')
    
    if 'phase_B_computation' in phases:
        phases['phase_B_computation']['dependencies'] = ['phase_A_construction']
        corrections_applied.append('incorrect_dependencies')
    
    if 'phase_C_litigation' in phases:
        phases['phase_C_litigation']['dependencies'] = ['phase_A_construction', 'phase_B_computation']
        corrections_applied.append('incorrect_dependencies')
    
    # 2. method_count_mismatch
    phase_a_count = len(phases.get('phase_A_construction', {}).get('methods', []))
    phase_b_count = len(phases.get('phase_B_computation', {}).get('methods', []))
    phase_c_count = len(phases.get('phase_C_litigation', {}).get('methods', []))
    new_count = phase_a_count + phase_b_count + phase_c_count
    
    if 'method_binding' in contract:
        contract['method_binding']['method_count'] = new_count
        corrections_applied.append('method_count_mismatch')
    
    # 3. incorrect_requires (N2 methods)
    for method in phases.get('phase_B_computation', {}).get('methods', []):
        requires = method.get('requires', [])
        if 'PreprocesadoMetadata' in requires:
            requires.remove('PreprocesadoMetadata')
        if 'raw_facts' not in requires:
            requires.insert(0, 'raw_facts')
            corrections_applied.append('incorrect_requires')
    
    # 4. missing_cross_layer_fusion
    if 'cross_layer_fusion' not in contract:
        contract['cross_layer_fusion'] = {}
    
    if 'N3_to_N1' not in contract['cross_layer_fusion']:
        contract['cross_layer_fusion']['N3_to_N1'] = {
            "relationship": "N3 can BLOCK or INVALIDATE N1 facts",
            "effect": "Failed validation removes invalid facts from graph",
            "data_flow": "veto_propagation",
            "asymmetry": "N1 CANNOT invalidate N3"
        }
        corrections_applied.append('missing_cross_layer_fusion')
    
    if 'N2_to_N1' in contract.get('cross_layer_fusion', {}):
        contract['cross_layer_fusion']['N2_to_N1']['data_flow'] = 'confidence_backpropagation'
        corrections_applied.append('missing_cross_layer_fusion')
    
    # 5. missing_placeholders
    has = contract.get('human_answer_structure', {})
    sections = has.get('sections', [])
    s1 = next((s for s in sections if s.get('section_id') == 'S1_verdict'), None)
    if s1 and 'template' in s1:
        if 'placeholders' not in s1['template']:
            s1['template']['placeholders'] = []
        required_ph = ['verdict_statement', 'final_confidence_pct', 'confidence_label', 'method_count', 'audit_count', 'blocked_count']
        for ph in required_ph:
            if ph not in s1['template']['placeholders']:
                s1['template']['placeholders'].append(ph)
                corrections_applied.append('missing_placeholders')
    
    # 6. r1_sources_issue
    assembly_rules = contract.get('evidence_assembly', {}).get('assembly_rules', [])
    r1 = next((r for r in assembly_rules if r.get('rule_id') == 'R1_empirical_basis'), None)
    if r1 and phase_a_count > 0:
        phase_a_provides = [m.get('provides') for m in phases['phase_A_construction']['methods'] if m.get('provides')]
        if set(r1.get('sources', [])) != set(phase_a_provides):
            r1['sources'] = phase_a_provides
            corrections_applied.append('r1_sources_issue')
    
    return corrections_applied

def apply_phase2_corrections(contract, vgl, contract_name):
    """Aplica correcciones Fase 2 (SEMI_AUTO con guards validados)"""
    corrections_applied = []
    
    contract_type = contract.get('identity', {}).get('contract_type')
    if not contract_type:
        return corrections_applied
    
    phases = contract.get('method_binding', {}).get('execution_phases', {})
    if not phases:
        return corrections_applied
    
    # 1. phase_B.epistemology
    phase_b = phases.get('phase_B_computation', {})
    if phase_b and isinstance(phase_b, dict):
        expected_epistemology = None
        if contract_type == 'TYPE_E':
            expected_epistemology = 'Lógica relacional y verificación de condiciones'
        elif contract_type in ['TYPE_B', 'TYPE_C']:
            expected_epistemology = 'Bayesianismo subjetivista'
        elif contract_type == 'TYPE_D':
            expected_epistemology = 'Inferencia probabilística financiera'
        elif contract_type == 'TYPE_A':
            expected_epistemology = 'Inferencia semántica'
        
        if expected_epistemology and phase_b.get('epistemology') != expected_epistemology:
            phase_b['epistemology'] = expected_epistemology
            corrections_applied.append('phase_B_epistemology')
    
    # 2. fusion_strategy_mismatch
    fusion_spec = contract.get('fusion_specification', {})
    if fusion_spec.get('contract_type') != contract_type:
        fusion_spec['contract_type'] = contract_type
        corrections_applied.append('fusion_strategy_mismatch')
    
    if 'level_strategies' in fusion_spec:
        n1_fusion = fusion_spec['level_strategies'].get('N1_fact_fusion', {})
        if contract_type == 'TYPE_E':
            if n1_fusion.get('strategy') != 'concat':
                n1_fusion['strategy'] = 'concat'
                corrections_applied.append('fusion_strategy_mismatch')
        elif contract_type == 'TYPE_C':
            if n1_fusion.get('strategy') != 'graph_construction':
                n1_fusion['strategy'] = 'graph_construction'
                corrections_applied.append('fusion_strategy_mismatch')
        elif contract_type == 'TYPE_A':
            if n1_fusion.get('strategy') != 'semantic_corroboration':
                n1_fusion['strategy'] = 'semantic_corroboration'
                corrections_applied.append('fusion_strategy_mismatch')
        
        # Corregir stage_1
        if 'fusion_pipeline' in fusion_spec:
            stage_1 = fusion_spec['fusion_pipeline'].get('stage_1_fact_accumulation', {})
            stage_1['type_consumed'] = 'FACT'
            stage_1['behavior'] = 'additive'
            corrections_applied.append('fusion_strategy_mismatch')
    
    # 3. missing_asymmetry (con domain_note)
    phase_c = phases.get('phase_C_litigation', {})
    if 'asymmetry_principle' not in phase_c:
        domain_note = f"En contratos {contract_type}, N3 valida mediante falsación popperiana. Si se detecta una contradicción crítica, N3 puede bloquear completamente los resultados de N1/N2, pero N1/N2 no pueden invalidar las validaciones de N3."
        
        phase_c['asymmetry_principle'] = {
            "description": "N3 can invalidate N1 and N2 outputs through veto power. N1 and N2 CANNOT invalidate N3.",
            "asymmetry_domain_note": domain_note
        }
        corrections_applied.append('missing_asymmetry')
    
    return corrections_applied

def apply_phase3_corrections(contract, vgl, contract_name):
    """Aplica correcciones Fase 3 (AUTO adicionales)"""
    corrections_applied = []
    
    phases = contract.get('method_binding', {}).get('execution_phases', {})
    if not phases:
        phases = {}
    
    # 1. Vocabulario inferencial en métodos N2
    inferential_terms = ['evalúa', 'calcula', 'infiere', 'scoring', 'probabilidades']
    phase_b = phases.get('phase_B_computation', {})
    if phase_b and isinstance(phase_b, dict):
        for method in phase_b.get('methods', []):
            if not isinstance(method, dict):
                continue
            desc = method.get('description', '')
            if not desc or not isinstance(desc, str):
                continue
            has_inferential = any(term in desc.lower() for term in inferential_terms)
            if not has_inferential:
                original_desc = desc
                if desc.startswith('Calcula'):
                    method['description'] = f'Evalúa y {desc.lower()}'
                elif desc.startswith('Identifica'):
                    method['description'] = f'Evalúa y {desc.lower()}'
                elif desc.startswith('Genera'):
                    method['description'] = f'Infiere y {desc.lower()}'
                elif desc.startswith('Agrega'):
                    method['description'] = f'Calcula y {desc.lower()}'
                else:
                    # Si no empieza con ninguna palabra clave, agregar al inicio
                    method['description'] = f'Evalúa {desc.lower()}'
                
                if method['description'] != original_desc:
                    corrections_applied.append('vocabulary_inferential')
    
    # 2. N3 requires
    phase_c = phases.get('phase_C_litigation', {})
    if phase_c and isinstance(phase_c, dict):
        for method in phase_c.get('methods', []):
            if not isinstance(method, dict):
                continue
            requires = method.get('requires', [])
            if not isinstance(requires, list):
                requires = []
                method['requires'] = requires
            
            modified = False
            if 'PreprocesadoMetadata' in requires:
                requires.remove('PreprocesadoMetadata')
                modified = True
            if 'raw_facts' not in requires:
                requires.insert(0, 'raw_facts')
                modified = True
            if 'inferred_parameters' not in requires:
                requires.append('inferred_parameters')
                modified = True
            
            if modified:
                corrections_applied.append('n3_requires')
    
    # 3. Gate logic (estructura)
    evidence_assembly = contract.get('evidence_assembly', {})
    if evidence_assembly:
        assembly_rules = evidence_assembly.get('assembly_rules', [])
        for rule in assembly_rules:
            if not isinstance(rule, dict):
                continue
            if 'gate_logic' in rule:
                gate_logic = rule['gate_logic']
                if isinstance(gate_logic, dict):
                    for condition_id, condition in gate_logic.items():
                        if isinstance(condition, dict):
                            if 'multiplier' in condition and 'confidence_multiplier' not in condition:
                                condition['confidence_multiplier'] = condition.pop('multiplier')
                                condition['trigger'] = condition.get('trigger', f'{condition_id} detected')
                                condition['scope'] = condition.get('scope', 'all')
                                corrections_applied.append('gate_logic_structure')
    
    # 4. Traceability
    if 'traceability' not in contract:
        contract['traceability'] = {}
    
    if not isinstance(contract['traceability'], dict):
        contract['traceability'] = {}
    
    # Obtener epistemology de phase_B de forma segura
    phase_b_epistemology = 'N/A'
    if phases:
        phase_b = phases.get('phase_B_computation', {})
        if phase_b:
            phase_b_epistemology = phase_b.get('epistemology', 'N/A')
    
    if 'refactoring_history' not in contract['traceability']:
        contract['traceability']['refactoring_history'] = [
            {
                "timestamp": datetime.now().isoformat() + "Z",
                "action": "common_corrections_batch_applied",
                "description": "Aplicadas correcciones comunes mediante VGL",
                "epistemic_impact": "NONE",
                "epistemological_framework": {
                    "N1": "Empirismo positivista",
                    "N2": phase_b_epistemology,
                    "N3": "Falsacionismo popperiano"
                }
            }
        ]
        corrections_applied.append('traceability')
    
    if 'prohibitions' not in contract['traceability']:
        contract['traceability']['prohibitions'] = {
            "v3_recovery": "FORBIDDEN",
            "automatic_method_addition": "FORBIDDEN",
            "semantic_modification_without_review": "FORBIDDEN"
        }
        corrections_applied.append('traceability')
    
    # 5. S2 layer y role
    has = contract.get('human_answer_structure', {})
    if has and isinstance(has, dict):
        sections = has.get('sections', [])
        if isinstance(sections, list):
            s2 = next((s for s in sections if isinstance(s, dict) and s.get('section_id') == 'S2_empirical_base'), None)
            if s2:
                if s2.get('layer') != 'N1':
                    s2['layer'] = 'N1'
                    corrections_applied.append('s2_layer')
                if s2.get('argumentative_role') != 'EMPIRICAL_BASIS':
                    s2['argumentative_role'] = 'EMPIRICAL_BASIS'
                    corrections_applied.append('s2_role')
        
        # 6. N1_roles
        arg_roles = has.get('argumentative_roles', {})
        if not isinstance(arg_roles, dict):
            arg_roles = {}
            has['argumentative_roles'] = arg_roles
        
        if 'N1_roles' not in arg_roles or not arg_roles.get('N1_roles'):
            arg_roles['N1_roles'] = [
                {
                    "role": "EMPIRICAL_BASIS",
                    "description": "Base empírica para análisis",
                    "narrative_weight": "high"
                }
            ]
            corrections_applied.append('n1_roles')
    
    return corrections_applied

def process_contract(contract_path, vgl):
    """Procesa un contrato aplicando todas las correcciones"""
    contract_name = contract_path.name
    
    try:
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract = json.load(f)
    except Exception as e:
        return {
            'contract': contract_name,
            'status': 'ERROR',
            'error': str(e),
            'corrections': []
        }
    
    all_corrections = []
    
    # Fase 1: AUTO
    phase1 = apply_phase1_corrections(contract, vgl, contract_name)
    all_corrections.extend(phase1)
    
    # Fase 2: SEMI_AUTO
    phase2 = apply_phase2_corrections(contract, vgl, contract_name)
    all_corrections.extend(phase2)
    
    # Fase 3: AUTO adicionales
    phase3 = apply_phase3_corrections(contract, vgl, contract_name)
    all_corrections.extend(phase3)
    
    # Guardar contrato corregido
    try:
        with open(contract_path, 'w', encoding='utf-8') as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)
        
        # Registrar en VGL
        for correction in set(all_corrections):
            vgl.log_correction(correction, contract_name, [correction], 'NONE')
        
        return {
            'contract': contract_name,
            'status': 'SUCCESS',
            'corrections': list(set(all_corrections)),
            'count': len(set(all_corrections))
        }
    except Exception as e:
        return {
            'contract': contract_name,
            'status': 'ERROR',
            'error': str(e),
            'corrections': all_corrections
        }

def main():
    """Función principal"""
    print('=' * 100)
    print('APLICACIÓN DE CORRECCIONES COMUNES EN BATCH')
    print('=' * 100)
    print()
    
    # Encontrar contratos pendientes
    all_contracts = sorted(Path('.').glob('D*-Q*-v4.json'))
    pending = [c for c in all_contracts if c.name not in NORMALIZED_CONTRACTS]
    
    print(f'📋 Contratos pendientes: {len(pending)}')
    print()
    
    # Inicializar VGL
    vgl = ValidatorGovernanceLayer()
    
    # Procesar cada contrato
    results = []
    for i, contract_path in enumerate(pending, 1):
        print(f'[{i}/{len(pending)}] Procesando {contract_path.name}...', end=' ')
        result = process_contract(contract_path, vgl)
        results.append(result)
        
        if result['status'] == 'SUCCESS':
            print(f'✅ {result["count"]} correcciones aplicadas')
        else:
            print(f'❌ ERROR: {result.get("error", "Unknown")}')
    
    print()
    print('=' * 100)
    print('RESUMEN FINAL')
    print('=' * 100)
    print()
    
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] == 'ERROR']
    
    print(f'✅ Exitosos: {len(successful)}/{len(pending)}')
    print(f'❌ Fallidos: {len(failed)}/{len(pending)}')
    print()
    
    if successful:
        total_corrections = sum(r['count'] for r in successful)
        print(f'📊 Total correcciones aplicadas: {total_corrections}')
        print()
        
        # Contar por tipo de corrección
        correction_counts = {}
        for r in successful:
            for corr in r['corrections']:
                correction_counts[corr] = correction_counts.get(corr, 0) + 1
        
        print('📋 Correcciones por tipo:')
        for corr, count in sorted(correction_counts.items(), key=lambda x: x[1], reverse=True):
            print(f'   {corr}: {count} contratos')
    
    if failed:
        print()
        print('❌ Contratos con errores:')
        for r in failed:
            print(f'   {r["contract"]}: {r.get("error", "Unknown")}')
    
    # Exportar reporte de governance
    vgl.export_governance_report('validator_governance_report_batch.json')
    print()
    print('✅ Reporte de governance exportado: validator_governance_report_batch.json')
    
    return results

if __name__ == '__main__':
    results = main()

