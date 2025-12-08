#!/usr/bin/env python3
"""
COHORT 2024 Verification Script

Verifies the integrity and completeness of the COHORT_2024 migration:
- Directory structure
- File counts
- Metadata presence
- Manifest completeness
- Import functionality
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def verify_structure() -> bool:
    """Verify directory structure exists."""
    print("=" * 60)
    print("1. Verifying Directory Structure")
    print("=" * 60)

    root = Path(__file__).parent
    required_dirs = ["calibration", "parametrization"]

    all_ok = True
    for dir_name in required_dirs:
        dir_path = root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ MISSING")
            all_ok = False

    return all_ok


def verify_files() -> bool:
    """Verify expected files exist."""
    print("\n" + "=" * 60)
    print("2. Verifying Core Files")
    print("=" * 60)

    root = Path(__file__).parent
    required_files = [
        "COHORT_MANIFEST.json",
        "cohort_loader.py",
        "import_adapters.py",
        "__init__.py",
        "README.md",
        "QUICK_REFERENCE.md",
        "INDEX.md",
    ]

    all_ok = True
    for file_name in required_files:
        file_path = root / file_name
        if file_path.exists():
            print(f"✓ {file_name}")
        else:
            print(f"✗ {file_name} MISSING")
            all_ok = False

    return all_ok


def verify_cohort_files() -> bool:
    """Verify COHORT_2024 files in calibration and parametrization."""
    print("\n" + "=" * 60)
    print("3. Verifying COHORT_2024 Files")
    print("=" * 60)

    root = Path(__file__).parent

    calibration_files = list((root / "calibration").glob("COHORT_2024_*"))
    parametrization_files = list((root / "parametrization").glob("COHORT_2024_*"))

    print(f"Calibration files: {len(calibration_files)}")
    for f in sorted(calibration_files):
        print(f"  - {f.name}")

    print(f"\nParametrization files: {len(parametrization_files)}")
    for f in sorted(parametrization_files):
        print(f"  - {f.name}")

    expected_cal = 16
    expected_param = 4

    if (
        len(calibration_files) >= expected_cal
        and len(parametrization_files) >= expected_param
    ):
        print(
            f"\n✓ File counts OK (cal={len(calibration_files)}, param={len(parametrization_files)})"
        )
        return True
    else:
        print("\n✗ File counts MISMATCH")
        print(f"  Expected: cal>={expected_cal}, param>={expected_param}")
        print(
            f"  Got: cal={len(calibration_files)}, param={len(parametrization_files)}"
        )
        return False


def verify_metadata() -> bool:
    """Verify cohort metadata in JSON files."""
    print("\n" + "=" * 60)
    print("4. Verifying Cohort Metadata")
    print("=" * 60)

    root = Path(__file__).parent
    json_files = list((root / "calibration").glob("COHORT_2024_*.json")) + list(
        (root / "parametrization").glob("COHORT_2024_*.json")
    )

    all_ok = True
    for json_file in sorted(json_files):
        try:
            with open(json_file) as f:
                data = json.load(f)

            if "_cohort_metadata" not in data:
                print(f"✗ {json_file.name}: Missing _cohort_metadata")
                all_ok = False
                continue

            meta = data["_cohort_metadata"]
            required = ["cohort_id", "creation_date", "wave_version"]
            missing = [k for k in required if k not in meta]

            if missing:
                print(f"✗ {json_file.name}: Missing fields {missing}")
                all_ok = False
            elif meta["cohort_id"] != "COHORT_2024":
                print(f"✗ {json_file.name}: Invalid cohort_id {meta['cohort_id']}")
                all_ok = False
            else:
                print(f"✓ {json_file.name}")
        except Exception as e:
            print(f"✗ {json_file.name}: ERROR {e}")
            all_ok = False

    return all_ok


def verify_manifest() -> bool:
    """Verify COHORT_MANIFEST.json completeness."""
    print("\n" + "=" * 60)
    print("5. Verifying Manifest")
    print("=" * 60)

    root = Path(__file__).parent
    manifest_path = root / "COHORT_MANIFEST.json"

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)

        print(f"Manifest Version: {manifest['manifest_version']}")
        print(f"Cohort ID: {manifest['cohort_id']}")
        print(f"Wave Version: {manifest['wave_version']}")

        cal_count = len(manifest.get("calibration_files", []))
        param_count = len(manifest.get("parametrization_files", []))

        print("\nManifest Statistics:")
        print(f"  Calibration files: {cal_count}")
        print(f"  Parametrization files: {param_count}")
        print(f"  Total: {cal_count + param_count}")

        if manifest["cohort_id"] == "COHORT_2024":
            print("\n✓ Manifest valid")
            return True
        else:
            print("\n✗ Invalid cohort_id in manifest")
            return False

    except Exception as e:
        print(f"✗ Manifest error: {e}")
        return False


def verify_imports() -> bool:
    """Verify import functionality."""
    print("\n" + "=" * 60)
    print("6. Verifying Import Functionality")
    print("=" * 60)

    try:
        # Test basic imports
        from calibration_parametrization_system import (
            get_calibration_config,
            get_cohort_metadata,
            get_parametrization_config,
        )

        print("✓ Basic imports work")

        # Test metadata retrieval
        metadata = get_cohort_metadata()
        assert metadata["cohort_id"] == "COHORT_2024"
        print("✓ Metadata retrieval works")

        # Test config loading
        intrinsic = get_calibration_config("intrinsic_calibration")
        assert "_cohort_metadata" in intrinsic
        print("✓ Configuration loading works")

        runtime = get_parametrization_config("runtime_layers")
        assert "_cohort_metadata" in runtime
        print("✓ Parametrization loading works")

        return True

    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all verifications."""
    print("\n" + "=" * 60)
    print("COHORT 2024 VERIFICATION")
    print("=" * 60 + "\n")

    results = [
        ("Structure", verify_structure()),
        ("Core Files", verify_files()),
        ("COHORT Files", verify_cohort_files()),
        ("Metadata", verify_metadata()),
        ("Manifest", verify_manifest()),
        ("Imports", verify_imports()),
    ]

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} - {name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n" + "=" * 60)
        print("✓ ALL VERIFICATIONS PASSED")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ SOME VERIFICATIONS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
