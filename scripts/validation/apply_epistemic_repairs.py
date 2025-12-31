#!/usr/bin/env python3
"""
Apply epistemic repairs to EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030.json
Based on audit findings in EPISTEMIC_AUDIT_SUMMARY_AND_REPAIRS.md
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Define fusion behaviors by TYPE and level
FUSION_BEHAVIORS = {
    'TYPE_A': {
        'N1-EMP': 'concat',
        'N2-INF': ['dempster_shafer', 'semantic_triangulation'],
        'N3-AUD': 'veto_gate'
    },
    'TYPE_B': {
        'N1-EMP': 'concat',
        'N2-INF': 'bayesian_update',
        'N3-AUD': 'statistical_threshold_gate'
    },
    'TYPE_C': {
        'N1-EMP': 'concat',
        'N2-INF': 'topological_overlay',
        'N3-AUD': 'cycle_detection_veto'
    },
    'TYPE_D': {
        'N1-EMP': 'concat',
        'N2-INF': 'weighted_mean',
        'N3-AUD': 'veto_gate'
    },
    'TYPE_E': {
        'N1-EMP': 'concat',
        'N2-INF': 'weighted_mean',
        'N3-AUD': 'veto_gate'
    }
}

# Mandatory N2 method template for TYPE_D
MANDATORY_TYPE_D_METHOD = {
    "method_id": "FinancialAggregator.normalize_to_budget_base",
    "file": "financiero_viabilidad_tablas.py",
    "justification": "N2: MANDATORY for TYPE_D per episte_refact.md Section 2.2. Normalizes financial allocations to % of budget for cross-municipality comparability. Formula: (amount/total_budget)*100.",
    "output_type": "PARAMETER",
    "fusion_behavior": "weighted_mean",
    "epistemic_necessity": "forced_inclusion"
}

# Overall justification templates by TYPE
JUSTIFICATION_TEMPLATES = {
    'TYPE_A': lambda q: f"{q} requires semantic coherence assessment. TYPE_A strategy: N1 extracts semantic chunks and keywords via bundling, N2 combines via Dempster-Shafer to handle conflict, N3 applies contradiction veto (Popperian falsification). This ensures semantic validity.",
    
    'TYPE_B': lambda q: f"{q} requires Bayesian inference from priors and evidence. TYPE_B strategy: N1 extracts prior beliefs and likelihood evidence, N2 computes posterior via Bayesian update, N3 validates statistical significance via gate. This ensures quantitative rigor.",
    
    'TYPE_C': lambda q: f"{q} requires causal structure validation. TYPE_C strategy: N1 extracts causal links and builds DAG, N2 validates acyclicity via topological overlay, N3 applies cycle veto (confidence=0.0 if cycle detected). This ensures causal logic is valid.",
    
    'TYPE_D': lambda q: f"{q} is financial - TYPE_D requires N2 dominance. N1 extracts raw budget data, N2 normalizes to % of budget and aggregates via weighted mean, N3 applies sufficiency veto. This ensures financial allocations are evaluated proportionally, not nominally.",
    
    'TYPE_E': lambda q: f"{q} requires logical consistency check. TYPE_E strategy: N1 collates statements, N2 computes MIN-based consistency (one contradiction → confidence=0), N3 applies ContradictionDominator veto. This ensures no logical contradictions exist."
}


def add_fusion_behavior(data: Dict[str, Any]) -> int:
    """Add fusion_behavior to all methods based on TYPE"""
    repairs = 0
    
    for q_id, q_data in data['assignments'].items():
        q_type = q_data.get('type')
        if not q_type:
            continue
            
        behaviors = FUSION_BEHAVIORS.get(q_type, {})
        
        for level in ['N1-EMP', 'N2-INF', 'N3-AUD']:
            if level not in q_data.get('selected_methods', {}):
                continue
                
            expected_behavior = behaviors.get(level)
            if not expected_behavior:
                continue
                
            for method in q_data['selected_methods'][level]:
                if 'fusion_behavior' not in method:
                    # Determine correct behavior
                    if isinstance(expected_behavior, list):
                        # Multiple valid behaviors - choose based on method_id
                        if 'DempsterShafer' in method.get('method_id', ''):
                            method['fusion_behavior'] = 'dempster_shafer'
                        elif 'Semantic' in method.get('method_id', ''):
                            method['fusion_behavior'] = 'semantic_triangulation'
                        else:
                            method['fusion_behavior'] = expected_behavior[0]
                    else:
                        method['fusion_behavior'] = expected_behavior
                    repairs += 1
                    
    return repairs


def add_mandatory_type_d_method(data: Dict[str, Any]) -> int:
    """Add mandatory FinancialAggregator.normalize_to_budget_base to TYPE_D questions"""
    repairs = 0
    
    type_d_questions = [
        q_id for q_id, q_data in data['assignments'].items()
        if q_data.get('type') == 'TYPE_D'
    ]
    
    for q_id in type_d_questions:
        q_data = data['assignments'][q_id]
        n2_methods = q_data.get('selected_methods', {}).get('N2-INF', [])
        
        # Check if mandatory method exists
        has_mandatory = any(
            'normalize_to_budget_base' in m.get('method_id', '')
            for m in n2_methods
        )
        
        if not has_mandatory:
            # Insert at beginning (highest priority)
            n2_methods.insert(0, MANDATORY_TYPE_D_METHOD.copy())
            repairs += 1
            
    return repairs


def add_overall_justifications(data: Dict[str, Any]) -> int:
    """Add overall_justification to Q004-Q030"""
    repairs = 0
    
    for q_id, q_data in data['assignments'].items():
        # Q001-Q003 already have justifications
        if q_id in ['Q001', 'Q002', 'Q003']:
            continue
            
        if 'overall_justification' not in q_data:
            q_type = q_data.get('type')
            question = q_data.get('question', q_id)
            
            template = JUSTIFICATION_TEMPLATES.get(q_type)
            if template:
                q_data['overall_justification'] = template(question)
                repairs += 1
                
    return repairs


def fix_type_d_fusion_strategy(data: Dict[str, Any]) -> int:
    """Fix R1 fusion strategy for TYPE_D questions"""
    repairs = 0
    
    for q_id, q_data in data['assignments'].items():
        if q_data.get('type') != 'TYPE_D':
            continue
            
        fusion_strategy = q_data.get('fusion_strategy', {})
        if fusion_strategy.get('R1') == 'concat':
            fusion_strategy['R1'] = 'financial_aggregation'
            repairs += 1
            
    return repairs


def main():
    # File paths
    repo_root = Path(__file__).parent.parent.parent
    input_file = repo_root / 'artifacts/data/reports/EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030.json'
    output_file = repo_root / 'artifacts/data/reports/EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030_REPAIRED.json'
    
    print("=" * 80)
    print("EPISTEMIC METHOD REPAIR APPLICATION")
    print("=" * 80)
    
    # Load original file
    print(f"\n1. Loading original file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_repairs = 0
    
    # Task 1: Add mandatory TYPE_D method
    print("\n2. Task 1: Adding mandatory FinancialAggregator.normalize_to_budget_base to TYPE_D")
    repairs = add_mandatory_type_d_method(data)
    print(f"   ✓ Added mandatory method to {repairs} questions")
    total_repairs += repairs
    
    # Task 2.1: Add fusion_behavior to all methods
    print("\n3. Task 2.1: Adding fusion_behavior to all methods")
    repairs = add_fusion_behavior(data)
    print(f"   ✓ Added fusion_behavior to {repairs} methods")
    total_repairs += repairs
    
    # Task 2.2: Fix TYPE_D fusion strategy R1
    print("\n4. Task 2.2: Fixing R1 fusion strategy for TYPE_D")
    repairs = fix_type_d_fusion_strategy(data)
    print(f"   ✓ Fixed R1 strategy in {repairs} questions")
    total_repairs += repairs
    
    # Task 3: Add overall_justification
    print("\n5. Task 3: Adding overall_justification to Q004-Q030")
    repairs = add_overall_justifications(data)
    print(f"   ✓ Added overall_justification to {repairs} questions")
    total_repairs += repairs
    
    # Save repaired file
    print(f"\n6. Saving repaired file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved successfully")
    
    print("\n" + "=" * 80)
    print(f"REPAIR SUMMARY: {total_repairs} total repairs applied")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
