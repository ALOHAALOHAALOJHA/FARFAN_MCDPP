#!/usr/bin/env python3
"""Generate CQVR evaluation data for all contracts and create interactive dashboard."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "src" / "farfan_pipeline" / "phases" / "Phase_two"))

from contract_validator_cqvr import CQVRValidator


def load_contract(contract_path: Path) -> dict[str, Any]:
    """Load a contract JSON file."""
    with open(contract_path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_all_contracts() -> list[dict[str, Any]]:
    """Evaluate all 300 contracts and return results."""
    validator = CQVRValidator()
    contracts_dir = Path(
        "/home/runner/work/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/"
        "F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/src/farfan_pipeline/phases/"
        "Phase_two/json_files_phase_two/executor_contracts/specialized"
    )
    
    contract_files = sorted(contracts_dir.glob("*.v3.json"))
    print(f"Found {len(contract_files)} contract files")
    
    results = []
    for i, contract_file in enumerate(contract_files, 1):
        print(f"Evaluating {i}/{len(contract_files)}: {contract_file.name}")
        
        try:
            contract = load_contract(contract_file)
            decision = validator.validate_contract(contract)
            
            identity = contract.get("identity", {})
            
            result = {
                "contract_id": contract_file.stem,
                "question_id": identity.get("question_id", "UNKNOWN"),
                "policy_area_id": identity.get("policy_area_id", "UNKNOWN"),
                "dimension_id": identity.get("dimension_id", "UNKNOWN"),
                "base_slot": identity.get("base_slot", "UNKNOWN"),
                "tier1_score": decision.score.tier1_score,
                "tier2_score": decision.score.tier2_score,
                "tier3_score": decision.score.tier3_score,
                "total_score": decision.score.total_score,
                "tier1_percentage": decision.score.tier1_percentage,
                "tier2_percentage": decision.score.tier2_percentage,
                "tier3_percentage": decision.score.tier3_percentage,
                "total_percentage": decision.score.total_percentage,
                "decision": decision.decision.value,
                "is_production_ready": decision.is_production_ready(),
                "blockers_count": len(decision.blockers),
                "warnings_count": len(decision.warnings),
                "blockers": decision.blockers,
                "warnings": decision.warnings,
                "recommendations": decision.recommendations,
                "rationale": decision.rationale,
                "evaluated_at": datetime.now().isoformat(),
            }
            results.append(result)
            
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "contract_id": contract_file.stem,
                "question_id": "ERROR",
                "policy_area_id": "ERROR",
                "dimension_id": "ERROR",
                "base_slot": "ERROR",
                "tier1_score": 0.0,
                "tier2_score": 0.0,
                "tier3_score": 0.0,
                "total_score": 0.0,
                "tier1_percentage": 0.0,
                "tier2_percentage": 0.0,
                "tier3_percentage": 0.0,
                "total_percentage": 0.0,
                "decision": "ERROR",
                "is_production_ready": False,
                "blockers_count": 1,
                "warnings_count": 0,
                "blockers": [f"Evaluation failed: {str(e)}"],
                "warnings": [],
                "recommendations": [],
                "rationale": f"Contract evaluation failed: {str(e)}",
                "evaluated_at": datetime.now().isoformat(),
            })
    
    return results


def save_evaluation_data(results: list[dict[str, Any]], output_path: Path) -> None:
    """Save evaluation results to JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved evaluation data to {output_path}")


def main() -> None:
    """Main execution function."""
    print("=" * 80)
    print("CQVR Contract Evaluation - Dashboard Data Generation")
    print("=" * 80)
    print()
    
    results = evaluate_all_contracts()
    
    output_path = Path("cqvr_evaluation_results.json")
    save_evaluation_data(results, output_path)
    
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    
    total_contracts = len(results)
    production_ready = sum(1 for r in results if r["is_production_ready"])
    patchable = sum(1 for r in results if r["decision"] == "PARCHEAR")
    reformulation = sum(1 for r in results if r["decision"] == "REFORMULAR")
    errors = sum(1 for r in results if r["decision"] == "ERROR")
    
    print(f"Total contracts evaluated: {total_contracts}")

    if total_contracts > 0:
        avg_total = sum(r["total_score"] for r in results) / total_contracts
        avg_tier1 = sum(r["tier1_score"] for r in results) / total_contracts
        avg_tier2 = sum(r["tier2_score"] for r in results) / total_contracts
        avg_tier3 = sum(r["tier3_score"] for r in results) / total_contracts
        
        print(f"  Production ready: {production_ready} ({production_ready/total_contracts*100:.1f}%)")
        print(f"  Patchable: {patchable} ({patchable/total_contracts*100:.1f}%)")
        print(f"  Needs reformulation: {reformulation} ({reformulation/total_contracts*100:.1f}%)")
        print(f"  Errors: {errors} ({errors/total_contracts*100:.1f}%)")
        print()
        print(f"Average scores:")
        print(f"  Total: {avg_total:.2f}/100 ({avg_total:.1f}%)")
        print(f"  Tier 1: {avg_tier1:.2f}/55 ({avg_tier1/55*100:.1f}%)")
        print(f"  Tier 2: {avg_tier2:.2f}/30 ({avg_tier2/30*100:.1f}%)")
        print(f"  Tier 3: {avg_tier3:.2f}/15 ({avg_tier3/15*100:.1f}%)")
    else:
        print("  Production ready: 0 (0.0%)")
        print("  Patchable: 0 (0.0%)")
        print("  Needs reformulation: 0 (0.0%)")
        print("  Errors: 0 (0.0%)")
        print()
        print("Average scores are not available because no contracts were evaluated.")
    print()
    print("Dashboard data generation complete!")


if __name__ == "__main__":
    main()
