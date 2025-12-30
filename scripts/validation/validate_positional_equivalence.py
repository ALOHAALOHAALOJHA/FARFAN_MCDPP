#!/usr/bin/env python3
"""
Positional Equivalence Validation Report

Validates that the policy area normalization preserved the structural invariants
required by the concept of "relative equivalence of positionality".

This ensures that questions at the same position across different policy areas
maintain their epistemological role, causal logic, method composition, and
analytical structure - while allowing only the policy area to vary.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple


def validate_positional_equivalence() -> Dict:
    """
    Validate positional equivalence across all 300 questions.
    
    Returns comprehensive report on invariants and variants.
    """
    contracts_dir = Path('src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized')
    
    report = {
        'summary': {},
        'invariants_validated': [],
        'variants_validated': [],
        'detailed_checks': [],
        'violations': []
    }
    
    # Check all 30 positional sets
    for position in range(1, 31):
        # Questions at this position across all PAs
        questions = [f'Q{((pa-1)*30 + position):03d}' for pa in range(1, 11)]
        
        # Collect contract data
        contracts = {}
        for qid in questions:
            contract_file = contracts_dir / f'{qid}.v3.json'
            with open(contract_file, 'r') as f:
                contract = json.load(f)
            contracts[qid] = contract
        
        # Extract invariant elements
        base_slots = [c['identity']['base_slot'] for c in contracts.values()]
        dimensions = [c['identity']['dimension_id'] for c in contracts.values()]
        clusters = [c['identity']['cluster_id'] for c in contracts.values()]
        
        # Extract method compositions
        method_bindings = []
        for contract in contracts.values():
            methods = contract['method_binding']['methods']
            # Create signature: (class_name, method_name, priority, role)
            signature = tuple([
                (m['class_name'], m['method_name'], m['priority'], m['role'])
                for m in methods
            ])
            method_bindings.append(signature)
        
        # Extract output structures
        output_schemas = []
        for contract in contracts.values():
            if 'output_contract' in contract and 'schema' in contract['output_contract']:
                schema = contract['output_contract']['schema']
                # Extract required properties
                required = tuple(sorted(schema.get('required', [])))
                output_schemas.append(required)
        
        # Extract scoring definitions
        scoring_refs = [c.get('scoring_definition_ref') for c in contracts.values()]
        
        # Extract variant element (policy area)
        policy_areas = [c['identity']['policy_area_id'] for c in contracts.values()]
        
        # Validate invariants
        position_check = {
            'position': position,
            'questions': questions,
            'checks': {}
        }
        
        # Check base_slot invariance
        if len(set(base_slots)) == 1:
            position_check['checks']['base_slot'] = {
                'status': 'PASS',
                'value': base_slots[0],
                'message': 'Base slot invariant across all policy areas'
            }
        else:
            position_check['checks']['base_slot'] = {
                'status': 'FAIL',
                'values': list(set(base_slots)),
                'message': f'Base slot varies: {set(base_slots)}'
            }
            report['violations'].append(f"Position {position}: Base slot varies")
        
        # Check dimension invariance
        if len(set(dimensions)) == 1:
            position_check['checks']['dimension'] = {
                'status': 'PASS',
                'value': dimensions[0],
                'message': 'Dimension invariant across all policy areas'
            }
        else:
            position_check['checks']['dimension'] = {
                'status': 'FAIL',
                'values': list(set(dimensions)),
                'message': f'Dimension varies: {set(dimensions)}'
            }
            report['violations'].append(f"Position {position}: Dimension varies")
        
        # Check method composition invariance
        if len(set(method_bindings)) == 1:
            position_check['checks']['method_composition'] = {
                'status': 'PASS',
                'method_count': len(method_bindings[0]),
                'message': 'Method composition invariant across all policy areas'
            }
        else:
            position_check['checks']['method_composition'] = {
                'status': 'FAIL',
                'message': 'Method composition varies across policy areas'
            }
            report['violations'].append(f"Position {position}: Method composition varies")
        
        # Check output structure invariance
        if output_schemas and len(set(output_schemas)) == 1:
            position_check['checks']['output_structure'] = {
                'status': 'PASS',
                'message': 'Output structure invariant across all policy areas'
            }
        else:
            position_check['checks']['output_structure'] = {
                'status': 'FAIL',
                'message': 'Output structure varies across policy areas'
            }
            report['violations'].append(f"Position {position}: Output structure varies")
        
        # Check scoring logic invariance
        if len(set(scoring_refs)) == 1:
            position_check['checks']['scoring_logic'] = {
                'status': 'PASS',
                'message': 'Scoring logic invariant across all policy areas'
            }
        else:
            position_check['checks']['scoring_logic'] = {
                'status': 'FAIL',
                'message': 'Scoring logic varies across policy areas'
            }
            report['violations'].append(f"Position {position}: Scoring logic varies")
        
        # Check policy area variance (should vary correctly)
        expected_pas = [f'PA{i:02d}' for i in range(1, 11)]
        if policy_areas == expected_pas:
            position_check['checks']['policy_area_variance'] = {
                'status': 'PASS',
                'values': policy_areas,
                'message': 'Policy areas vary correctly (PA01-PA10)'
            }
        else:
            position_check['checks']['policy_area_variance'] = {
                'status': 'FAIL',
                'expected': expected_pas,
                'actual': policy_areas,
                'message': 'Policy areas do not follow expected sequence'
            }
            report['violations'].append(f"Position {position}: Policy areas incorrect")
        
        report['detailed_checks'].append(position_check)
    
    # Generate summary
    total_positions = 30
    total_questions = 300
    violations = len(report['violations'])
    
    report['summary'] = {
        'total_positions_checked': total_positions,
        'total_questions_validated': total_questions,
        'total_violations': violations,
        'status': 'PASS' if violations == 0 else 'FAIL'
    }
    
    # List validated invariants
    if violations == 0:
        report['invariants_validated'] = [
            'Base slot (analytical position) remains constant within each positional set',
            'Dimension (analytical axis) remains constant within each positional set',
            'Method composition (class, method, priority, role) remains identical',
            'Output structure (required fields) remains consistent',
            'Scoring logic (scoring_definition_ref) remains constant',
            'Epistemological role (implied by base_slot + dimension) remains constant',
            'Causal logic (implied by method composition) remains constant'
        ]
        
        report['variants_validated'] = [
            'Policy area ID varies correctly from PA01 to PA10 for each position',
            'Semantic surface (question wording) varies by policy area (not validated in contracts)',
            'Sectoral language varies by policy area (not validated in contracts)'
        ]
    
    return report


def main():
    """Main execution."""
    print("=" * 80)
    print("POSITIONAL EQUIVALENCE VALIDATION REPORT")
    print("Validating structural invariants after policy area normalization")
    print("=" * 80)
    print()
    
    report = validate_positional_equivalence()
    
    # Print summary
    print("SUMMARY")
    print("-" * 80)
    print(f"Total positions checked: {report['summary']['total_positions_checked']}")
    print(f"Total questions validated: {report['summary']['total_questions_validated']}")
    print(f"Total violations found: {report['summary']['total_violations']}")
    print(f"Overall status: {report['summary']['status']}")
    print()
    
    if report['summary']['status'] == 'PASS':
        print("✓ ALL POSITIONAL EQUIVALENCE CHECKS PASSED")
        print()
        
        print("INVARIANTS VALIDATED:")
        for invariant in report['invariants_validated']:
            print(f"  ✓ {invariant}")
        print()
        
        print("VARIANTS VALIDATED:")
        for variant in report['variants_validated']:
            print(f"  ✓ {variant}")
        print()
        
        print("DETAILED VALIDATION:")
        print("  Sampled positions 1, 15, 30:")
        for pos in [1, 15, 30]:
            check = report['detailed_checks'][pos - 1]
            base_slot = check['checks']['base_slot']['value']
            dimension = check['checks']['dimension']['value']
            methods = check['checks']['method_composition']['method_count']
            print(f"    Position {pos:2d}: {base_slot} / {dimension} / {methods} methods / PA01-PA10")
    else:
        print("✗ VIOLATIONS FOUND:")
        for violation in report['violations']:
            print(f"  • {violation}")
    
    print()
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    if report['summary']['status'] == 'PASS':
        print("""
The policy area normalization has been validated successfully. All structural
invariants required by the concept of "relative equivalence of positionality"
have been preserved:

1. Questions at the same position across different policy areas maintain
   identical epistemological roles, causal logic, method compositions,
   output structures, and scoring logic.

2. Only the policy area ID varies across positionally equivalent questions,
   as expected and required.

3. No methodological inconsistencies were introduced by the normalization.

The system's analytical architecture remains intact and structurally sound.
""")
    else:
        print("""
CRITICAL: The validation has detected violations of positional equivalence.
These violations must be addressed before the normalization can be considered
complete.
""")
    
    # Save detailed report
    report_file = Path('POSITIONAL_EQUIVALENCE_VALIDATION_REPORT.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    print(f"Detailed report saved: {report_file}")
    
    return 0 if report['summary']['status'] == 'PASS' else 1


if __name__ == '__main__':
    exit(main())
