"""
COHORT 2024 Usage Examples

Demonstrates how to use the calibration_parametrization_system to load
configurations with cohort metadata validation.
"""

from __future__ import annotations

from pathlib import Path


def example_basic_loading():
    """Basic configuration loading with automatic cohort validation."""
    print("=" * 60)
    print("Example 1: Basic Configuration Loading")
    print("=" * 60)

    from calibration_parametrization_system import (
        get_calibration_config,
        get_cohort_metadata,
        get_parametrization_config,
    )

    # Load calibration configs
    intrinsic_cal = get_calibration_config("intrinsic_calibration")
    print("✓ Loaded intrinsic_calibration")
    print(f"  Cohort: {intrinsic_cal['_cohort_metadata']['cohort_id']}")
    print(f"  Wave: {intrinsic_cal['_cohort_metadata']['wave_version']}")

    rubric = get_calibration_config("intrinsic_calibration_rubric")  # noqa: F841
    print("✓ Loaded intrinsic_calibration_rubric")

    method_compat = get_calibration_config("method_compatibility")  # noqa: F841
    print("✓ Loaded method_compatibility")

    # Load parametrization configs
    runtime_layers = get_parametrization_config("runtime_layers")  # noqa: F841
    print("✓ Loaded runtime_layers")

    # Verify cohort metadata
    metadata = get_cohort_metadata()
    print("\nCohort Metadata:")
    print(f"  ID: {metadata['cohort_id']}")
    print(f"  Wave: {metadata['wave_version']}")
    print(f"  Date: {metadata['migration_date']}")


def example_advanced_loading():
    """Advanced loading with explicit CohortLoader."""
    print("\n" + "=" * 60)
    print("Example 2: Advanced Loading with CohortLoader")
    print("=" * 60)

    from calibration_parametrization_system import CohortLoader

    loader = CohortLoader()

    # List available configs
    calibration_files = loader.list_calibration_files()
    parametrization_files = loader.list_parametrization_files()

    print(f"Available calibration configs: {len(calibration_files)}")
    for name in calibration_files:
        print(f"  - {name}")

    print(f"\nAvailable parametrization configs: {len(parametrization_files)}")
    for name in parametrization_files:
        print(f"  - {name}")

    # Load with validation
    config = loader.load_calibration("intrinsic_calibration")
    assert "_cohort_metadata" in config
    print("\n✓ Validation passed for intrinsic_calibration")

    # Get original path
    original_path = loader.get_original_path(
        "calibration", "COHORT_2024_intrinsic_calibration.json"
    )
    print(f"  Original path: {original_path}")


def example_backward_compatibility():
    """Backward compatibility with ConfigPathAdapter."""
    print("\n" + "=" * 60)
    print("Example 3: Backward Compatibility")
    print("=" * 60)

    from calibration_parametrization_system.import_adapters import ConfigPathAdapter

    # Load using old path (automatically redirects to COHORT_2024)
    old_paths = [
        "system/config/calibration/intrinsic_calibration.json",
        "system/config/calibration/runtime_layers.json",
        "config/json_files_ no_schemas/method_compatibility.json",
    ]

    for old_path in old_paths:
        try:
            config = ConfigPathAdapter.load_config(old_path)  # noqa: F841
            print(f"✓ Loaded {old_path}")
            print("  → COHORT_2024 version with metadata")

            cohort_path = ConfigPathAdapter.get_cohort_path(old_path)
            print(f"  New path: {cohort_path.relative_to(Path.cwd())}")
        except FileNotFoundError as e:
            print(f"✗ {old_path}: {e}")


def example_metadata_validation():
    """Demonstrate metadata validation."""
    print("\n" + "=" * 60)
    print("Example 4: Metadata Validation")
    print("=" * 60)

    from calibration_parametrization_system import get_calibration_config

    config = get_calibration_config("intrinsic_calibration")

    # Validate cohort metadata
    cohort_meta = config["_cohort_metadata"]
    required_fields = ["cohort_id", "creation_date", "wave_version"]

    print("Validating cohort metadata...")
    for field in required_fields:
        if field in cohort_meta:
            print(f"  ✓ {field}: {cohort_meta[field]}")
        else:
            print(f"  ✗ {field}: MISSING")

    # Check cohort ID
    if cohort_meta["cohort_id"] == "COHORT_2024":
        print("\n✓ Cohort ID validation passed")
    else:
        print(f"\n✗ Invalid cohort ID: {cohort_meta['cohort_id']}")


def example_manifest_inspection():
    """Inspect the COHORT_MANIFEST for audit trail."""
    print("\n" + "=" * 60)
    print("Example 5: Manifest Inspection (Audit Trail)")
    print("=" * 60)

    import json
    from pathlib import Path

    manifest_path = Path(__file__).parent / "COHORT_MANIFEST.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    print(f"Manifest Version: {manifest['manifest_version']}")
    print(f"Cohort ID: {manifest['cohort_id']}")
    print(f"Wave Version: {manifest['wave_version']}")
    print(f"Migration Date: {manifest['migration_date']}")

    stats = manifest["statistics"]
    print("\nStatistics:")
    print(f"  Total calibration files: {stats['total_calibration_files']}")
    print(f"  Total parametrization files: {stats['total_parametrization_files']}")
    print(f"  Total files migrated: {stats['total_files_migrated']}")
    print(f"  JSON files: {stats['json_files']}")
    print(f"  Python files: {stats['python_files']}")

    print("\nSample Migration Records:")
    for i, record in enumerate(manifest["calibration_files"][:3], 1):
        print(f"\n  {i}. {record['new_filename']}")
        print(f"     Original: {record['original_path']}")
        print(f"     Category: {record['category']}")
        print(f"     Purpose: {record['purpose']}")


if __name__ == "__main__":
    print("\nCOHORT 2024 CALIBRATION & PARAMETRIZATION SYSTEM")
    print("Usage Examples\n")

    try:
        example_basic_loading()
        example_advanced_loading()
        example_backward_compatibility()
        example_metadata_validation()
        example_manifest_inspection()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
