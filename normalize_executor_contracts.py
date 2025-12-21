#!/usr/bin/env python3
"""
Script to normalize policy_area_id in all 300 executor contracts.

Fixes the collateral damage from the questionnaire ordering error where contracts
were generated under the erroneous PA order: PA01→PA10→PA02→PA03→PA04→PA05→PA06→PA07→PA08→PA09

Corrects to canonical order: PA01→PA02→PA03→PA04→PA05→PA06→PA07→PA08→PA09→PA10
"""

import json
import os
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


CONTRACTS_DIR = Path('src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized')


def compute_contract_hash(contract: Dict) -> str:
    """Compute deterministic hash for contract (excluding hash and timestamps)."""
    contract_copy = contract.copy()
    if 'identity' in contract_copy:
        identity = contract_copy['identity'].copy()
        identity.pop('contract_hash', None)
        identity.pop('created_at', None)
        identity.pop('updated_at', None)
        contract_copy['identity'] = identity
    
    contract_str = json.dumps(contract_copy, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(contract_str.encode('utf-8')).hexdigest()


def get_correct_policy_area(question_id: str) -> str:
    """Get correct policy area for a question ID based on canonical ordering."""
    q_num = int(question_id[1:])
    pa_num = ((q_num - 1) // 30) + 1
    return f'PA{pa_num:02d}'


def update_policy_area_in_contract(contract: Dict, new_policy_area: str) -> Dict:
    """Update all policy_area references in a contract."""
    # Update identity.policy_area_id
    if 'identity' in contract:
        contract['identity']['policy_area_id'] = new_policy_area
    
    # Update question_context.patterns[*].policy_area
    if 'question_context' in contract and 'patterns' in contract['question_context']:
        for pattern in contract['question_context']['patterns']:
            if 'policy_area' in pattern:
                pattern['policy_area'] = new_policy_area
    
    # Update output_contract.schema.properties.policy_area_id.const
    if 'output_contract' in contract:
        if 'schema' in contract['output_contract']:
            if 'properties' in contract['output_contract']['schema']:
                if 'policy_area_id' in contract['output_contract']['schema']['properties']:
                    contract['output_contract']['schema']['properties']['policy_area_id']['const'] = new_policy_area
    
    return contract


def normalize_contracts(dry_run: bool = False) -> Dict[str, any]:
    """Normalize all 300 executor contracts to correct policy areas."""
    results = {
        'total_contracts': 0,
        'updated_contracts': 0,
        'unchanged_contracts': 0,
        'updates': []
    }
    
    if not CONTRACTS_DIR.exists():
        raise FileNotFoundError(f"Contracts directory not found: {CONTRACTS_DIR}")
    
    # Create backup if not dry run
    if not dry_run:
        backup_dir = CONTRACTS_DIR.parent / 'specialized_backup_pre_normalization'
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(CONTRACTS_DIR, backup_dir)
        print(f"✓ Backup created: {backup_dir}")
    
    # Process all contracts
    for i in range(1, 301):
        qid = f'Q{i:03d}'
        contract_file = CONTRACTS_DIR / f'{qid}.v3.json'
        
        if not contract_file.exists():
            print(f"✗ Contract not found: {contract_file}")
            continue
        
        results['total_contracts'] += 1
        
        # Read contract
        with open(contract_file, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        # Determine correct policy area
        expected_pa = get_correct_policy_area(qid)
        current_pa = contract['identity']['policy_area_id']
        
        if current_pa == expected_pa:
            results['unchanged_contracts'] += 1
            continue
        
        # Update policy area
        old_pa = current_pa
        contract = update_policy_area_in_contract(contract, expected_pa)
        
        # Update timestamp
        contract['identity']['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Recompute hash
        new_hash = compute_contract_hash(contract)
        contract['identity']['contract_hash'] = new_hash
        
        # Write back
        if not dry_run:
            with open(contract_file, 'w', encoding='utf-8') as f:
                json.dump(contract, f, indent=2, ensure_ascii=False)
                f.write('\n')
        
        results['updated_contracts'] += 1
        results['updates'].append({
            'question_id': qid,
            'old_policy_area': old_pa,
            'new_policy_area': expected_pa
        })
    
    return results


def main():
    """Main execution."""
    print("=" * 80)
    print("EXECUTOR CONTRACTS NORMALIZATION")
    print("=" * 80)
    print()
    print("This script will update policy_area_id in 270 contracts to match the")
    print("canonical questionnaire ordering (PA01→PA02→...→PA10)")
    print()
    
    # Dry run first
    print("Running pre-flight check...")
    dry_results = normalize_contracts(dry_run=True)
    
    print(f"\nPre-flight results:")
    print(f"  Total contracts: {dry_results['total_contracts']}")
    print(f"  Contracts to update: {dry_results['updated_contracts']}")
    print(f"  Contracts unchanged: {dry_results['unchanged_contracts']}")
    
    if dry_results['updated_contracts'] > 0:
        print(f"\nFirst 5 updates:")
        for update in dry_results['updates'][:5]:
            print(f"  {update['question_id']}: {update['old_policy_area']} → {update['new_policy_area']}")
        
        print(f"\nLast 5 updates:")
        for update in dry_results['updates'][-5:]:
            print(f"  {update['question_id']}: {update['old_policy_area']} → {update['new_policy_area']}")
    
    # Execute normalization
    print("\n" + "=" * 80)
    print("Executing normalization...")
    print("=" * 80)
    
    results = normalize_contracts(dry_run=False)
    
    print(f"\n✓ Normalization complete!")
    print(f"  Total contracts processed: {results['total_contracts']}")
    print(f"  Contracts updated: {results['updated_contracts']}")
    print(f"  Contracts unchanged: {results['unchanged_contracts']}")
    
    # Save audit report
    report_file = Path('EXECUTOR_CONTRACTS_NORMALIZATION_REPORT.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    print(f"\n✓ Audit report saved: {report_file}")
    
    # Verify all contracts now have correct policy areas
    print("\nVerifying normalization...")
    errors = []
    for i in range(1, 301):
        qid = f'Q{i:03d}'
        contract_file = CONTRACTS_DIR / f'{qid}.v3.json'
        
        with open(contract_file, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        expected_pa = get_correct_policy_area(qid)
        actual_pa = contract['identity']['policy_area_id']
        
        if actual_pa != expected_pa:
            errors.append(f"{qid}: has {actual_pa}, expected {expected_pa}")
    
    if errors:
        print(f"\n✗ Verification found {len(errors)} errors:")
        for error in errors[:10]:
            print(f"  {error}")
    else:
        print("✓ All 300 contracts verified: policy areas are correct!")
    
    print("\n" + "=" * 80)
    print("NORMALIZATION COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
