#!/usr/bin/env python3
"""
Audit all 30 contracts and generate summary report
"""

import subprocess
import json
from pathlib import Path

contracts_dir = Path("src/farfan_pipeline/phases/Phase_two/generated_contracts")
audit_script = Path(
    "src/farfan_pipeline/phases/Phase_two/epistemological_assets/audit_v4_rigorous.py"
)

contract_files = sorted(contracts_dir.glob("D*_Q*_contract_v4.json"))

print("=" * 80)
print(f"AUDIT V4 RIGUROUS - {len(contract_files)} CONTRATOS")
print("=" * 80)
print()

results = {"total_audited": 0, "passed": 0, "failed": 0, "errors": [], "summary_by_contract": {}}

for contract_file in contract_files:
    contract_name = contract_file.name

    # Run audit
    result = subprocess.run(
        ["python3", str(audit_script), str(contract_file)], capture_output=True, text=True
    )

    # Parse output
    output = result.stdout + result.stderr

    # Count failures
    failure_count = output.count("❌")
    pass_count = output.count("✅")

    results["total_audited"] += 1

    if result.returncode != 0 or "HARD FAILURE" in output:
        results["failed"] += 1
        results["errors"].append(contract_name)
        results["summary_by_contract"][contract_name] = {
            "status": "FAILED",
            "failures": failure_count,
        }
    elif failure_count == 0:
        results["passed"] += 1
        results["summary_by_contract"][contract_name] = {"status": "PASSED", "checks": pass_count}
    else:
        results["failed"] += 1
        results["summary_by_contract"][contract_name] = {
            "status": "WARNINGS",
            "failures": failure_count,
            "checks": pass_count,
        }

    # Show progress
    status = "✅ PASS" if failure_count == 0 else f"⚠️  {failure_count} issues"
    print(f"{contract_name}: {status}")

# Summary
print()
print("=" * 80)
print("RESUMEN DE AUDITORÍA")
print("=" * 80)
print(f"Total auditados: {results['total_audited']}")
print(f"✅ Pasaron: {results['passed']}")
print(f"❌ Fallaron: {results['failed']}")
print()

if results["failed"] > 0:
    print("CONTRATOS CON ERRORES:")
    for contract, data in results["summary_by_contract"].items():
        if data["status"] in ["FAILED", "WARNINGS"]:
            print(f"  {contract}: {data}")
else:
    print("🎉 TODOS LOS CONTRATOS PASARON LA AUDITORÍA")

print()
print("=" * 80)
