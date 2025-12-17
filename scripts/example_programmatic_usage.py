#!/usr/bin/env python3
"""
Example: Programmatic Usage of Contract Remediator
Demonstrates how to use the remediator in custom scripts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.contract_remediator import (
    ContractRemediator,
    RemediationStrategy,
)


def main():
    """Example workflow for remediating contracts."""
    
    # Initialize remediator
    remediator = ContractRemediator(
        contracts_dir=Path(
            "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
        ),
        monolith_path=Path("canonic_questionnaire_central/questionnaire_monolith.json"),
        backup_dir=Path("backups/contracts"),
        dry_run=False,  # Set to True for testing
    )
    
    print("=" * 80)
    print("CONTRACT REMEDIATION WORKFLOW")
    print("=" * 80)
    
    # Example 1: Remediate single contract
    print("\n1. Remediating single contract (Q011)...")
    contract_path = Path(
        "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q011.v3.json"
    )
    
    result = remediator.remediate_contract(contract_path, RemediationStrategy.AUTO)
    
    if result.success:
        improvement = result.new_score - result.original_score
        print(f"   ✅ Success: {result.original_score:.1f} → {result.new_score:.1f} (+{improvement:.1f})")
        print(f"   Fixes applied: {', '.join(result.fixes_applied)}")
    else:
        print(f"   ⚠️  No improvement or error: {result.error_message}")
    
    # Example 2: Batch remediation
    print("\n2. Batch remediating contracts Q012-Q014...")
    question_ids = ["Q012", "Q013", "Q014"]
    results = remediator.remediate_batch(question_ids, RemediationStrategy.AUTO)
    
    successful = [r for r in results if r.success]
    print(f"   Processed: {len(results)}, Successful: {len(successful)}")
    
    # Example 3: Remediate all failing contracts
    print("\n3. Remediating all contracts below threshold 70...")
    results = remediator.remediate_failing(70.0, RemediationStrategy.AUTO)
    
    if results:
        total_improvement = sum(r.new_score - r.original_score for r in results if r.success)
        avg_improvement = total_improvement / len([r for r in results if r.success])
        print(f"   Average improvement: +{avg_improvement:.1f} points")
    
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE")
    print("=" * 80)
    
    # Summary statistics
    all_results = results
    production_ready = [r for r in all_results if r.success and r.new_score >= 80]
    
    print(f"\nProduction-ready contracts (≥80): {len(production_ready)}")
    for result in production_ready[:5]:  # Show first 5
        print(f"  - {result.contract_path.name}: {result.new_score:.1f}")


if __name__ == "__main__":
    main()
