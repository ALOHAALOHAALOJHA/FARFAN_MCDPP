#!/usr/bin/env python3
"""
Comprehensive CQVR evaluation for all 300 executor contracts.
Generates detailed reports and identifies contracts requiring remediation.
"""
import json
import sys
from pathlib import Path
from typing import Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from farfan_pipeline.phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import (
    CQVRValidator,
    ContractRemediation,
)


def evaluate_all_contracts() -> dict[str, Any]:
    """Evaluate all contracts and generate comprehensive report."""
    base_path = Path(__file__).parent.parent
    contracts_dir = (
        base_path
        / "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
    )

    validator = CQVRValidator()
    contracts = sorted(contracts_dir.glob("Q*.v3.json"))

    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_contracts": 0,
        "evaluated": 0,
        "skipped": 0,
        "errors": 0,
        "statistics": {
            "average_score": 0.0,
            "min_score": 100.0,
            "max_score": 0.0,
            "passed_80": 0,
            "passed_70": 0,
            "passed_60": 0,
            "failed_40": 0,
        },
        "contracts": [],
        "remediation_needed": [],
        "errors_list": [],
    }

    scores = []

    for contract_path in contracts:
        results["total_contracts"] += 1
        contract_id = contract_path.stem

        try:
            with open(contract_path) as f:
                contract = json.load(f)

            if isinstance(contract, str):
                results["skipped"] += 1
                continue

            report = validator.validate_contract(contract)
            results["evaluated"] += 1

            score = report["percentage"]
            scores.append(score)

            contract_result = {
                "contract_id": contract_id,
                "score": score,
                "tier1": report["tier1_score"],
                "tier2": report["tier2_score"],
                "tier3": report["tier3_score"],
                "passed": report["passed"],
                "triage": report["triage_decision"],
                "breakdown": report["breakdown"],
            }

            results["contracts"].append(contract_result)

            if score >= 80:
                results["statistics"]["passed_80"] += 1
            elif score >= 70:
                results["statistics"]["passed_70"] += 1
            elif score >= 60:
                results["statistics"]["passed_60"] += 1
            
            if score < 40:
                results["statistics"]["failed_40"] += 1
                results["remediation_needed"].append(
                    {"contract_id": contract_id, "score": score, "action": "REGENERATE"}
                )
            elif score < 80:
                action = "PATCH_MAJOR" if score < 70 else "PATCH_MINOR"
                results["remediation_needed"].append(
                    {"contract_id": contract_id, "score": score, "action": action}
                )

        except Exception as e:
            results["errors"] += 1
            results["errors_list"].append({"contract_id": contract_id, "error": str(e)})

    if scores:
        results["statistics"]["average_score"] = sum(scores) / len(scores)
        results["statistics"]["min_score"] = min(scores)
        results["statistics"]["max_score"] = max(scores)

    return results


def generate_report(results: dict[str, Any], output_path: Path) -> None:
    """Generate human-readable report."""
    report_lines = [
        "# CQVR Contract Evaluation Report",
        f"\n**Generated**: {results['timestamp']}",
        f"\n## Summary\n",
        f"- Total contracts: {results['total_contracts']}",
        f"- Evaluated: {results['evaluated']}",
        f"- Skipped: {results['skipped']}",
        f"- Errors: {results['errors']}",
        f"\n## Quality Statistics\n",
        f"- Average score: {results['statistics']['average_score']:.1f}/100",
        f"- Min score: {results['statistics']['min_score']:.1f}/100",
        f"- Max score: {results['statistics']['max_score']:.1f}/100",
        f"- Contracts ≥ 80: {results['statistics']['passed_80']} ({results['statistics']['passed_80']*100/results['evaluated']:.1f}%)",
        f"- Contracts 70-79: {results['statistics']['passed_70']} ({results['statistics']['passed_70']*100/results['evaluated']:.1f}%)",
        f"- Contracts 60-69: {results['statistics']['passed_60']} ({results['statistics']['passed_60']*100/results['evaluated']:.1f}%)",
        f"- Contracts < 40: {results['statistics']['failed_40']} ({results['statistics']['failed_40']*100/results['evaluated']:.1f}%)",
        f"\n## Remediation Required\n",
        f"\nTotal contracts requiring action: {len(results['remediation_needed'])}",
    ]

    if results["remediation_needed"]:
        report_lines.append("\n### Priority Actions\n")
        
        regenerate = [r for r in results["remediation_needed"] if r["action"] == "REGENERATE"]
        if regenerate:
            report_lines.append(f"\n**REGENERATE (< 40)**: {len(regenerate)} contracts")
            for r in regenerate[:10]:
                report_lines.append(f"- {r['contract_id']}: {r['score']:.1f}/100")
        
        patch_major = [r for r in results["remediation_needed"] if r["action"] == "PATCH_MAJOR"]
        if patch_major:
            report_lines.append(f"\n**PATCH_MAJOR (60-69)**: {len(patch_major)} contracts")
        
        patch_minor = [r for r in results["remediation_needed"] if r["action"] == "PATCH_MINOR"]
        if patch_minor:
            report_lines.append(f"\n**PATCH_MINOR (70-79)**: {len(patch_minor)} contracts")

    if results["errors_list"]:
        report_lines.append(f"\n## Errors\n")
        for err in results["errors_list"][:10]:
            report_lines.append(f"- {err['contract_id']}: {err['error']}")

    report_lines.append(f"\n## Deployment Readiness\n")
    
    if results['statistics']['failed_40'] > 0:
        report_lines.append("❌ **NOT READY**: Contracts scoring < 40 detected")
    elif results['statistics']['average_score'] < 80:
        report_lines.append("⚠️ **NEEDS IMPROVEMENT**: Average score below 80")
    else:
        report_lines.append("✅ **READY**: All quality gates passed")

    output_path.write_text("\n".join(report_lines))
    print(f"Report saved to: {output_path}")


def main() -> None:
    """Execute comprehensive contract evaluation."""
    print("Starting CQVR contract evaluation...")
    results = evaluate_all_contracts()

    output_dir = Path(__file__).parent.parent / "artifacts"
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / "cqvr_evaluation_full.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"JSON results saved to: {json_path}")

    report_path = output_dir / "CQVR_EVALUATION_REPORT.md"
    generate_report(results, report_path)

    print(f"\n{'='*60}")
    print(f"EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total: {results['evaluated']}/{results['total_contracts']} contracts")
    print(f"Average: {results['statistics']['average_score']:.1f}/100")
    print(f"Ready (≥80): {results['statistics']['passed_80']}")
    print(f"Need work: {len(results['remediation_needed'])}")

    if results["statistics"]["average_score"] >= 80 and results["statistics"]["failed_40"] == 0:
        print("\n✅ READY FOR DEPLOYMENT")
        sys.exit(0)
    else:
        print("\n⚠️ REMEDIATION REQUIRED")
        sys.exit(1)


if __name__ == "__main__":
    main()
