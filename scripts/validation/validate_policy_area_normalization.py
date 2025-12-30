#!/usr/bin/env python3
"""
Validation script to verify policy area normalization across all system components.

Validates:
1. Questionnaire monolith has correct PA ordering
2. All 300 executor contracts have correct policy_area_id
3. Internal consistency within each contract
4. Alignment between monolith and contracts
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


def get_expected_policy_area(question_num: int) -> str:
    """Get expected policy area for a question number (1-300)."""
    pa_num = ((question_num - 1) // 30) + 1
    return f'PA{pa_num:02d}'


def validate_questionnaire_monolith() -> Tuple[bool, List[str]]:
    """Validate questionnaire monolith has correct PA ordering."""
    errors = []
    monolith_path = Path('canonic_questionnaire_central/questionnaire_monolith.json')
    
    if not monolith_path.exists():
        errors.append(f"Questionnaire monolith not found: {monolith_path}")
        return False, errors
    
    with open(monolith_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    micro_qs = data.get('blocks', {}).get('micro_questions', [])
    
    if len(micro_qs) != 300:
        errors.append(f"Expected 300 micro questions, found {len(micro_qs)}")
        return False, errors
    
    # Verify each question has correct policy area
    for i, question in enumerate(micro_qs, 1):
        qid = question.get('question_id', f'Q{i:03d}')
        pa_id = question.get('policy_area_id', 'MISSING')
        expected_pa = get_expected_policy_area(i)
        
        if pa_id != expected_pa:
            errors.append(f"Monolith {qid}: has {pa_id}, expected {expected_pa}")
    
    return len(errors) == 0, errors


def validate_contract_internal_consistency(contract: Dict, qid: str) -> List[str]:
    """Validate internal consistency of policy_area references within a contract."""
    errors = []
    
    # Get primary policy area from identity
    identity_pa = contract.get('identity', {}).get('policy_area_id')
    if not identity_pa:
        errors.append(f"{qid}: Missing identity.policy_area_id")
        return errors
    
    # Check all pattern policy areas
    patterns = contract.get('question_context', {}).get('patterns', [])
    for idx, pattern in enumerate(patterns):
        pattern_pa = pattern.get('policy_area')
        if pattern_pa and pattern_pa != identity_pa:
            errors.append(
                f"{qid}: Pattern[{idx}] has {pattern_pa}, but identity has {identity_pa}"
            )
    
    # Check output_contract schema const
    output_pa_const = (
        contract.get('output_contract', {})
        .get('schema', {})
        .get('properties', {})
        .get('policy_area_id', {})
        .get('const')
    )
    if output_pa_const and output_pa_const != identity_pa:
        errors.append(
            f"{qid}: output_contract.schema const has {output_pa_const}, but identity has {identity_pa}"
        )
    
    return errors


def validate_executor_contracts() -> Tuple[bool, List[str]]:
    """Validate all 300 executor contracts have correct policy areas."""
    errors = []
    contracts_dir = Path('src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized')
    
    if not contracts_dir.exists():
        errors.append(f"Contracts directory not found: {contracts_dir}")
        return False, errors
    
    for i in range(1, 301):
        qid = f'Q{i:03d}'
        contract_file = contracts_dir / f'{qid}.v3.json'
        
        if not contract_file.exists():
            errors.append(f"{qid}: Contract file not found")
            continue
        
        with open(contract_file, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        # Check expected policy area
        expected_pa = get_expected_policy_area(i)
        actual_pa = contract.get('identity', {}).get('policy_area_id')
        
        if actual_pa != expected_pa:
            errors.append(f"{qid}: has {actual_pa}, expected {expected_pa}")
        
        # Check internal consistency
        consistency_errors = validate_contract_internal_consistency(contract, qid)
        errors.extend(consistency_errors)
    
    return len(errors) == 0, errors


def validate_monolith_contract_alignment() -> Tuple[bool, List[str]]:
    """Validate alignment between questionnaire monolith and executor contracts."""
    errors = []
    
    monolith_path = Path('canonic_questionnaire_central/questionnaire_monolith.json')
    contracts_dir = Path('src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized')
    
    with open(monolith_path, 'r', encoding='utf-8') as f:
        monolith_data = json.load(f)
    
    micro_qs = monolith_data.get('blocks', {}).get('micro_questions', [])
    
    for i, question in enumerate(micro_qs, 1):
        qid = question.get('question_id', f'Q{i:03d}')
        monolith_pa = question.get('policy_area_id')
        
        contract_file = contracts_dir / f'{qid}.v3.json'
        if not contract_file.exists():
            continue
        
        with open(contract_file, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        contract_pa = contract.get('identity', {}).get('policy_area_id')
        
        if monolith_pa != contract_pa:
            errors.append(
                f"{qid}: Monolith has {monolith_pa}, Contract has {contract_pa}"
            )
    
    return len(errors) == 0, errors


def main():
    """Main validation execution."""
    print("=" * 80)
    print("POLICY AREA NORMALIZATION VALIDATION")
    print("=" * 80)
    print()
    
    all_passed = True
    
    # 1. Validate questionnaire monolith
    print("1. Validating questionnaire monolith...")
    monolith_ok, monolith_errors = validate_questionnaire_monolith()
    if monolith_ok:
        print("   ✓ Questionnaire monolith: PASS (300 questions with correct PA ordering)")
    else:
        print(f"   ✗ Questionnaire monolith: FAIL ({len(monolith_errors)} errors)")
        for error in monolith_errors[:5]:
            print(f"     - {error}")
        if len(monolith_errors) > 5:
            print(f"     ... and {len(monolith_errors) - 5} more errors")
        all_passed = False
    
    print()
    
    # 2. Validate executor contracts
    print("2. Validating executor contracts...")
    contracts_ok, contracts_errors = validate_executor_contracts()
    if contracts_ok:
        print("   ✓ Executor contracts: PASS (300 contracts with correct PA and internal consistency)")
    else:
        print(f"   ✗ Executor contracts: FAIL ({len(contracts_errors)} errors)")
        for error in contracts_errors[:10]:
            print(f"     - {error}")
        if len(contracts_errors) > 10:
            print(f"     ... and {len(contracts_errors) - 10} more errors")
        all_passed = False
    
    print()
    
    # 3. Validate alignment
    print("3. Validating monolith-contract alignment...")
    alignment_ok, alignment_errors = validate_monolith_contract_alignment()
    if alignment_ok:
        print("   ✓ Alignment: PASS (all questions match between monolith and contracts)")
    else:
        print(f"   ✗ Alignment: FAIL ({len(alignment_errors)} errors)")
        for error in alignment_errors[:10]:
            print(f"     - {error}")
        if len(alignment_errors) > 10:
            print(f"     ... and {len(alignment_errors) - 10} more errors")
        all_passed = False
    
    print()
    print("=" * 80)
    
    if all_passed:
        print("✓ ALL VALIDATION CHECKS PASSED")
        print("  - Questionnaire monolith is normalized")
        print("  - All 300 contracts have correct policy areas")
        print("  - Internal consistency verified")
        print("  - Monolith and contracts are aligned")
        print()
        print("Canonical ordering: PA01→PA02→PA03→PA04→PA05→PA06→PA07→PA08→PA09→PA10")
        print("Questions per PA: 30 (Q001-Q030, Q031-Q060, ..., Q271-Q300)")
        return 0
    else:
        print("✗ VALIDATION FAILED")
        print("  See errors above")
        return 1


if __name__ == '__main__':
    exit(main())
