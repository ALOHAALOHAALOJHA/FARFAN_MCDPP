#!/usr/bin/env python3
"""
Phase 2 Infrastructure Validation Script

Verifies that all Phase 2 canonical freeze infrastructure is in place.
Run this before attempting migration to ensure everything is ready.

Usage:
    python scripts/validate_phase2_infrastructure.py
"""

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
PHASE2_ROOT = PROJECT_ROOT / "src" / "canonic_phases" / "phase_2"

# Define expected structure
EXPECTED_STRUCTURE = {
    "directories": [
        PHASE2_ROOT,
        PHASE2_ROOT / "executors",
        PHASE2_ROOT / "orchestration",
        PHASE2_ROOT / "contracts",
        PHASE2_ROOT / "contracts" / "certificates",
        PHASE2_ROOT / "sisas",
        PHASE2_ROOT / "schemas",
    ],
    "package_files": [
        PHASE2_ROOT / "__init__.py",
        PHASE2_ROOT / "executors" / "__init__.py",
        PHASE2_ROOT / "orchestration" / "__init__.py",
        PHASE2_ROOT / "contracts" / "__init__.py",
        PHASE2_ROOT / "sisas" / "__init__.py",
    ],
    "documentation": [
        PHASE2_ROOT / "README.md",
        PHASE2_ROOT / "PHASE2_FREEZE_IMPLEMENTATION_STATUS.md",
        PROJECT_ROOT / "PHASE2_CANONICAL_FREEZE_EXECUTIVE_SUMMARY.md",
        PROJECT_ROOT / "PHASE2_MIGRATION_GUIDE.md",
        PROJECT_ROOT / "PHASE2_FREEZE_QUICKSTART.md",
    ],
    "schemas": [
        PHASE2_ROOT / "schemas" / "executor_config.schema.json",
        PHASE2_ROOT / "schemas" / "executor_output.schema.json",
    ],
    "certificates": [
        PHASE2_ROOT / "contracts" / "certificates" / "CERTIFICATE_01_ROUTING_CONTRACT.md",
        PHASE2_ROOT / "contracts" / "certificates" / "CERTIFICATE_08_CARVER_300_DELIVERY.md",
    ],
    "test_files": [
        PROJECT_ROOT / "tests" / "test_phase2_router_contracts.py",
        PROJECT_ROOT / "tests" / "test_phase2_carver_300_delivery.py",
        PROJECT_ROOT / "tests" / "test_phase2_contracts_enforcement.py",
        PROJECT_ROOT / "tests" / "test_phase2_config_and_output_schemas.py",
        PROJECT_ROOT / "tests" / "test_phase2_sisas_synchronization.py",
        PROJECT_ROOT / "tests" / "test_phase2_orchestrator_alignment.py",
        PROJECT_ROOT / "tests" / "test_phase2_resource_and_precision.py",
    ],
    "tooling": [
        PROJECT_ROOT / "scripts" / "migrate_phase2_canonical.py",
    ],
}


def check_file_exists(path: Path, category: str) -> dict[str, Any]:
    """Check if a file exists and return status."""
    exists = path.exists()
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "category": category,
        "exists": exists,
        "is_file": path.is_file() if exists else False,
        "size": path.stat().st_size if exists and path.is_file() else 0,
    }


def check_directory_exists(path: Path) -> dict[str, Any]:
    """Check if a directory exists and return status."""
    exists = path.exists()
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "category": "directory",
        "exists": exists,
        "is_directory": path.is_dir() if exists else False,
    }


def validate_json_schema(schema_path: Path) -> dict[str, Any]:
    """Validate that a file is valid JSON."""
    result = {"valid": False, "error": None}
    try:
        with open(schema_path) as f:
            data = json.load(f)
            result["valid"] = True
            result["schema_version"] = data.get("$schema", "unknown")
            result["version"] = data.get("version", "unknown")
    except Exception as e:
        result["error"] = str(e)
    return result


def main() -> None:
    """Run infrastructure validation."""
    print("=" * 70)
    print("PHASE 2 CANONICAL FREEZE - INFRASTRUCTURE VALIDATION")
    print("=" * 70)
    print()

    results = {
        "directories": [],
        "package_files": [],
        "documentation": [],
        "schemas": [],
        "certificates": [],
        "test_files": [],
        "tooling": [],
    }

    # Check directories
    print("Checking directories...")
    for directory in EXPECTED_STRUCTURE["directories"]:
        result = check_directory_exists(directory)
        results["directories"].append(result)
        status = "✅" if result["exists"] and result["is_directory"] else "❌"
        print(f"  {status} {result['path']}")

    # Check package files
    print("\nChecking package files...")
    for file_path in EXPECTED_STRUCTURE["package_files"]:
        result = check_file_exists(file_path, "package")
        results["package_files"].append(result)
        status = "✅" if result["exists"] and result["is_file"] else "❌"
        size = f"({result['size']} bytes)" if result["exists"] else ""
        print(f"  {status} {result['path']} {size}")

    # Check documentation
    print("\nChecking documentation...")
    for file_path in EXPECTED_STRUCTURE["documentation"]:
        result = check_file_exists(file_path, "documentation")
        results["documentation"].append(result)
        status = "✅" if result["exists"] and result["is_file"] else "❌"
        size = f"({result['size']} bytes)" if result["exists"] else ""
        print(f"  {status} {result['path']} {size}")

    # Check schemas
    print("\nChecking JSON schemas...")
    for file_path in EXPECTED_STRUCTURE["schemas"]:
        result = check_file_exists(file_path, "schema")
        results["schemas"].append(result)
        status = "✅" if result["exists"] and result["is_file"] else "❌"
        
        if result["exists"]:
            schema_validation = validate_json_schema(file_path)
            result["schema_validation"] = schema_validation
            valid_marker = "✓" if schema_validation["valid"] else "✗"
            version_info = f"[{schema_validation.get('version', 'unknown')}]" if schema_validation["valid"] else ""
            print(f"  {status} {result['path']} {valid_marker} {version_info}")
        else:
            print(f"  {status} {result['path']}")

    # Check certificates
    print("\nChecking certificates...")
    for file_path in EXPECTED_STRUCTURE["certificates"]:
        result = check_file_exists(file_path, "certificate")
        results["certificates"].append(result)
        status = "✅" if result["exists"] and result["is_file"] else "❌"
        print(f"  {status} {result['path']}")

    # Check test files
    print("\nChecking test files...")
    for file_path in EXPECTED_STRUCTURE["test_files"]:
        result = check_file_exists(file_path, "test")
        results["test_files"].append(result)
        status = "✅" if result["exists"] and result["is_file"] else "❌"
        print(f"  {status} {result['path']}")

    # Check tooling
    print("\nChecking tooling...")
    for file_path in EXPECTED_STRUCTURE["tooling"]:
        result = check_file_exists(file_path, "tooling")
        results["tooling"].append(result)
        status = "✅" if result["exists"] and result["is_file"] else "❌"
        executable = "🔧" if result["exists"] and file_path.stat().st_mode & 0o111 else ""
        print(f"  {status} {result['path']} {executable}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_checks = sum(len(v) for v in results.values())
    passed_checks = sum(
        1
        for category in results.values()
        for item in category
        if item["exists"]
    )

    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print()

    if passed_checks == total_checks:
        print("✅ ALL INFRASTRUCTURE CHECKS PASSED")
        print()
        print("Next steps:")
        print("  1. Review PHASE2_FREEZE_QUICKSTART.md")
        print("  2. Run migration dry-run:")
        print("     python scripts/migrate_phase2_canonical.py --dry-run --all")
        print("  3. Follow PHASE2_MIGRATION_GUIDE.md for execution")
        sys.exit(0)
    else:
        print("❌ SOME INFRASTRUCTURE CHECKS FAILED")
        print()
        print("Fix the failed checks before proceeding with migration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
