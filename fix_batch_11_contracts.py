#!/usr/bin/env python3
"""
Batch 11 Contract Remediation Script
Fixes critical signal_threshold issue in Q251-Q275 contracts
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any

def fix_signal_threshold(contract: Dict[str, Any]) -> tuple[bool, str]:
    """
    Fix minimum_signal_threshold if it's 0.0 and mandatory_signals exist.
    
    Returns: (was_fixed, message)
    """
    signal_reqs = contract.get('signal_requirements', {})
    mandatory_signals = signal_reqs.get('mandatory_signals', [])
    current_threshold = signal_reqs.get('minimum_signal_threshold', 0.0)
    
    # Check if fix is needed
    if mandatory_signals and current_threshold == 0.0:
        contract['signal_requirements']['minimum_signal_threshold'] = 0.5
        return True, f"Fixed: threshold 0.0 → 0.5 (has {len(mandatory_signals)} mandatory signals)"
    elif not mandatory_signals and current_threshold == 0.0:
        return False, "No fix needed: no mandatory signals, threshold 0.0 is acceptable"
    elif current_threshold > 0.0:
        return False, f"Already correct: threshold = {current_threshold}"
    else:
        return False, "No change needed"

def process_contract(contract_path: Path) -> tuple[bool, str, Dict[str, Any]]:
    """
    Process a single contract file.
    
    Returns: (was_modified, message, contract_data)
    """
    try:
        with open(contract_path, 'r') as f:
            contract = json.load(f)
        
        contract_id = contract.get('identity', {}).get('question_id', 'UNKNOWN')
        was_fixed, message = fix_signal_threshold(contract)
        
        if was_fixed:
            # Write back the fixed contract
            with open(contract_path, 'w') as f:
                json.dump(contract, f, indent=2, ensure_ascii=False)
            
        return was_fixed, f"{contract_id}: {message}", contract
        
    except Exception as e:
        return False, f"ERROR: {e}", {}

def main():
    """Main remediation routine"""
    print("=" * 80)
    print("BATCH 11 CONTRACT REMEDIATION")
    print("Fixing signal_threshold issues in Q251-Q275")
    print("=" * 80)
    print()
    
    # Setup paths
    base_path = Path(__file__).parent
    contracts_dir = base_path / "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
    
    if not contracts_dir.exists():
        print(f"❌ ERROR: Contracts directory not found: {contracts_dir}")
        return 1
    
    # Process contracts Q251-Q275
    contract_range = range(251, 276)
    
    results = {
        'fixed': [],
        'already_correct': [],
        'errors': []
    }
    
    print(f"Processing {len(list(contract_range))} contracts...")
    print()
    
    for i in contract_range:
        contract_id = f"Q{i:03d}"
        contract_path = contracts_dir / f"{contract_id}.v3.json"
        
        if not contract_path.exists():
            msg = f"⚠️  {contract_id}: File not found"
            print(msg)
            results['errors'].append(msg)
            continue
        
        was_modified, message, _ = process_contract(contract_path)
        
        if "ERROR" in message:
            print(f"❌ {message}")
            results['errors'].append(message)
        elif was_modified:
            print(f"✅ {message}")
            results['fixed'].append(contract_id)
        else:
            print(f"ℹ️  {message}")
            results['already_correct'].append(contract_id)
    
    print()
    print("=" * 80)
    print("REMEDIATION COMPLETE")
    print("=" * 80)
    print()
    
    # Summary
    print("Summary:")
    print(f"  Contracts Fixed:        {len(results['fixed'])}")
    print(f"  Already Correct:        {len(results['already_correct'])}")
    print(f"  Errors:                 {len(results['errors'])}")
    print(f"  Total Processed:        {len(results['fixed']) + len(results['already_correct'])}")
    print()
    
    if results['fixed']:
        print("Fixed Contracts:")
        for contract_id in results['fixed']:
            print(f"  - {contract_id}")
        print()
    
    if results['errors']:
        print("⚠️ Errors Encountered:")
        for error in results['errors']:
            print(f"  - {error}")
        print()
    
    # Expected impact
    if results['fixed']:
        fixed_count = len(results['fixed'])
        print("Expected Impact:")
        print(f"  Score Improvement:      +10 pts per contract")
        print(f"  Contracts Now Passing:  ~{fixed_count}/25 (assuming no other critical issues)")
        print(f"  New Batch Average:      ~80.7/100 (from 70.7/100)")
        print()
        print("⚠️ IMPORTANT: Re-run evaluation script to verify improvements:")
        print("   python3 evaluate_batch_11_cqvr.py")
        print()
    
    return 0 if not results['errors'] else 1

if __name__ == "__main__":
    sys.exit(main())
