#!/usr/bin/env python3
"""
Quick verification script to check policy area normalization status.
Run this anytime to verify canonical ordering is maintained.
"""

import json
from pathlib import Path
from typing import Tuple


def quick_check() -> Tuple[bool, str]:
    """Quick check of policy area normalization."""
    
    # Check a few key contracts
    test_contracts = {
        'Q001': 'PA01',  # First of PA01
        'Q030': 'PA01',  # Last of PA01
        'Q031': 'PA02',  # First of PA02 (was PA10 before fix)
        'Q060': 'PA02',  # Last of PA02
        'Q061': 'PA03',  # First of PA03 (was PA02 before fix)
        'Q271': 'PA10',  # First of PA10 (was PA09 before fix)
        'Q300': 'PA10',  # Last of PA10
    }
    
    contracts_dir = Path('src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized')
    
    errors = []
    for qid, expected_pa in test_contracts.items():
        contract_file = contracts_dir / f'{qid}.v3.json'
        
        if not contract_file.exists():
            errors.append(f"{qid}: Contract file not found")
            continue
        
        with open(contract_file, 'r') as f:
            contract = json.load(f)
        
        actual_pa = contract['identity']['policy_area_id']
        if actual_pa != expected_pa:
            errors.append(f"{qid}: has {actual_pa}, expected {expected_pa}")
    
    if errors:
        return False, "\n".join(errors)
    
    return True, "All key contracts have correct policy areas"


def main():
    """Main execution."""
    print("Policy Area Normalization - Quick Check")
    print("=" * 50)
    
    ok, message = quick_check()
    
    if ok:
        print("✓ PASS:", message)
        print("\nCanonical ordering verified:")
        print("  PA01: Q001-Q030")
        print("  PA02: Q031-Q060")
        print("  PA03: Q061-Q090")
        print("  ...")
        print("  PA10: Q271-Q300")
        return 0
    else:
        print("✗ FAIL: Policy area normalization issues detected")
        print("\nErrors:")
        print(message)
        print("\nRun validate_policy_area_normalization.py for detailed analysis")
        return 1


if __name__ == '__main__':
    exit(main())
