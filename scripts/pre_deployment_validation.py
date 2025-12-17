#!/usr/bin/env python3
"""
Pre-deployment validation script.
Validates system readiness before production deployment.
"""
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def validate_quality_gates() -> dict[str, Any]:
    """Validate CQVR quality gates."""
    print("Checking CQVR quality gates...")
    
    evaluation_file = Path(__file__).parent.parent / "artifacts/cqvr_evaluation_full.json"
    
    if not evaluation_file.exists():
        return {
            "passed": False,
            "reason": "CQVR evaluation not found. Run: python scripts/evaluate_all_contracts.py",
        }
    
    with open(evaluation_file) as f:
        data = json.load(f)
    
    avg_score = data["statistics"]["average_score"]
    failed_40 = data["statistics"]["failed_40"]
    total = data["evaluated"]
    
    checks = {
        "average_score_80": avg_score >= 80,
        "no_contracts_below_40": failed_40 == 0,
        "all_contracts_evaluated": total >= 299,
    }
    
    passed = all(checks.values())
    
    reason = None
    if not passed:
        failed_checks = [k for k, v in checks.items() if not v]
        reason = f"Failed checks: {', '.join(failed_checks)}"
    
    return {
        "passed": passed,
        "reason": reason,
        "checks": checks,
        "metrics": {
            "average_score": avg_score,
            "failed_40": failed_40,
            "total": total,
        },
    }


def validate_backup_exists() -> dict[str, Any]:
    """Validate backup directory exists and has recent backups."""
    print("Checking backup infrastructure...")
    
    backup_dir = Path(__file__).parent.parent / "backups"
    
    if not backup_dir.exists():
        return {
            "passed": False,
            "reason": "Backup directory does not exist",
        }
    
    backups = list(backup_dir.glob("contracts_*"))
    
    if not backups:
        return {
            "passed": False,
            "reason": "No backups found. Create backup before deployment.",
        }
    
    return {
        "passed": True,
        "backup_count": len(backups),
    }


def validate_scripts_executable() -> dict[str, Any]:
    """Validate deployment scripts are executable."""
    import os
    
    print("Checking deployment scripts...")
    
    base_path = Path(__file__).parent
    
    required_scripts = [
        "rollback.sh",
        "restore_contracts.sh",
        "evaluate_all_contracts.py",
        "remediate_contracts.py",
    ]
    
    missing = []
    not_executable = []
    
    for script in required_scripts:
        script_path = base_path / script
        if not script_path.exists():
            missing.append(script)
        elif not os.access(script_path, os.X_OK):
            not_executable.append(script)
    
    if missing:
        return {
            "passed": False,
            "reason": f"Missing scripts: {', '.join(missing)}",
        }
    
    if not_executable:
        return {
            "passed": False,
            "reason": f"Scripts not executable: {', '.join(not_executable)}",
        }
    
    return {"passed": True}


def validate_workflows_exist() -> dict[str, Any]:
    """Validate GitHub Actions workflows exist."""
    print("Checking CI/CD workflows...")
    
    workflows_dir = Path(__file__).parent.parent / ".github/workflows"
    
    if not workflows_dir.exists():
        return {
            "passed": False,
            "reason": "Workflows directory does not exist",
        }
    
    required_workflows = [
        "cqvr-quality-gate.yml",
        "deploy-staging.yml",
        "deploy-production.yml",
    ]
    
    missing = []
    
    for workflow in required_workflows:
        if not (workflows_dir / workflow).exists():
            missing.append(workflow)
    
    if missing:
        return {
            "passed": False,
            "reason": f"Missing workflows: {', '.join(missing)}",
        }
    
    return {"passed": True}


def validate_documentation() -> dict[str, Any]:
    """Validate deployment documentation exists."""
    print("Checking documentation...")
    
    docs_dir = Path(__file__).parent.parent / "docs"
    
    required_docs = [
        "DEPLOYMENT_RUNBOOK.md",
        "MONITORING_CONFIG.md",
    ]
    
    missing = []
    
    for doc in required_docs:
        if not (docs_dir / doc).exists():
            missing.append(doc)
    
    if missing:
        return {
            "passed": False,
            "reason": f"Missing documentation: {', '.join(missing)}",
        }
    
    return {"passed": True}


def validate_dashboard() -> dict[str, Any]:
    """Validate monitoring dashboard exists."""
    print("Checking monitoring dashboard...")
    
    dashboard_file = Path(__file__).parent.parent / "dashboard/cqvr_dashboard.html"
    
    if not dashboard_file.exists():
        return {
            "passed": False,
            "reason": "Dashboard not found at dashboard/cqvr_dashboard.html",
        }
    
    return {"passed": True}


def main() -> None:
    """Execute pre-deployment validation."""
    print("="*60)
    print("PRE-DEPLOYMENT VALIDATION")
    print("="*60)
    print()
    
    validations = [
        ("Quality Gates", validate_quality_gates),
        ("Backup Infrastructure", validate_backup_exists),
        ("Deployment Scripts", validate_scripts_executable),
        ("CI/CD Workflows", validate_workflows_exist),
        ("Documentation", validate_documentation),
        ("Monitoring Dashboard", validate_dashboard),
    ]
    
    results = []
    all_passed = True
    
    for name, validator in validations:
        result = validator()
        results.append((name, result))
        
        if result["passed"]:
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED")
            print(f"   Reason: {result.get('reason', 'Unknown')}")
            all_passed = False
        
        print()
    
    print("="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print()
    
    passed_count = sum(1 for _, r in results if r["passed"])
    total_count = len(results)
    
    print(f"Passed: {passed_count}/{total_count}")
    print()
    
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print()
        print("System is ready for deployment.")
        print()
        print("Next steps:")
        print("1. Review deployment runbook: docs/DEPLOYMENT_RUNBOOK.md")
        print("2. Notify team of deployment window")
        print("3. Execute staging deployment: git push origin develop")
        print("4. Monitor staging for 1 hour")
        print("5. Execute production deployment when ready")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED")
        print()
        print("System is NOT ready for deployment.")
        print()
        print("Please resolve the issues above before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
