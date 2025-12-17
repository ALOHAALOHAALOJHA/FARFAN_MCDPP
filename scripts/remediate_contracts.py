#!/usr/bin/env python3
"""
Automated contract remediation applying structural corrections.
Applies ContractRemediation fixes to improve CQVR scores.
"""
import json
import sys
import shutil
from pathlib import Path
from typing import Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from farfan_pipeline.phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import (
    CQVRValidator,
    ContractRemediation,
)


def backup_contract(contract_path: Path, backup_dir: Path) -> None:
    """Create backup of contract before remediation."""
    backup_path = backup_dir / contract_path.name
    shutil.copy2(contract_path, backup_path)


def remediate_contract(contract_path: Path, backup_dir: Path) -> dict[str, Any]:
    """Apply remediation to a single contract."""
    contract_id = contract_path.stem
    
    try:
        with open(contract_path) as f:
            contract = json.load(f)
        
        if isinstance(contract, str):
            return {
                "contract_id": contract_id,
                "status": "skipped",
                "reason": "String content",
            }
        
        validator = CQVRValidator()
        remediation = ContractRemediation()
        
        before_report = validator.validate_contract(contract)
        before_score = before_report["percentage"]
        
        backup_contract(contract_path, backup_dir)
        
        remediated_contract = remediation.apply_structural_corrections(contract)
        
        after_report = validator.validate_contract(remediated_contract)
        after_score = after_report["percentage"]
        
        if after_score > before_score:
            with open(contract_path, "w") as f:
                json.dump(remediated_contract, f, indent=2)
            
            return {
                "contract_id": contract_id,
                "status": "improved",
                "before_score": before_score,
                "after_score": after_score,
                "improvement": after_score - before_score,
            }
        else:
            return {
                "contract_id": contract_id,
                "status": "no_improvement",
                "score": before_score,
            }
    
    except Exception as e:
        return {
            "contract_id": contract_id,
            "status": "error",
            "error": str(e),
        }


def main() -> None:
    """Execute automated remediation for all contracts."""
    base_path = Path(__file__).parent.parent
    contracts_dir = (
        base_path
        / "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
    )
    
    backup_dir = base_path / "backups" / f"contracts_{datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating backups in: {backup_dir}")
    
    contracts = sorted(contracts_dir.glob("Q*.v3.json"))
    
    results = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "backup_dir": str(backup_dir),
        "total": len(contracts),
        "improved": 0,
        "no_improvement": 0,
        "skipped": 0,
        "errors": 0,
        "details": [],
    }
    
    for contract_path in contracts:
        print(f"Processing {contract_path.name}...", end=" ")
        result = remediate_contract(contract_path, backup_dir)
        results["details"].append(result)
        
        status = result["status"]
        if status == "improved":
            results["improved"] += 1
            improvement = result["improvement"]
            print(f"✓ Improved {result['before_score']:.1f} → {result['after_score']:.1f} (+{improvement:.1f})")
        elif status == "no_improvement":
            results["no_improvement"] += 1
            print(f"- No improvement ({result['score']:.1f})")
        elif status == "skipped":
            results["skipped"] += 1
            print(f"⊘ Skipped")
        elif status == "error":
            results["errors"] += 1
            print(f"✗ Error: {result['error']}")
    
    output_path = base_path / "artifacts" / "remediation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"REMEDIATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total: {results['total']}")
    print(f"Improved: {results['improved']}")
    print(f"No improvement: {results['no_improvement']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Errors: {results['errors']}")
    print(f"\nBackups saved to: {backup_dir}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
