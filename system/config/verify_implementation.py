"""Verify configuration governance implementation completeness.

Checks all required components are in place:
- Directory structure
- Configuration files
- Utility scripts
- Pre-commit hook
- Documentation

IMPLEMENTATION_WAVE: GOVERNANCE_WAVE_2024_12_07
WAVE_LABEL: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION
"""

from pathlib import Path


def check_directories() -> tuple[list[str], list[str]]:
    """Check required directories exist."""
    required = [
        "system/config/calibration",
        "system/config/questionnaire",
        "system/config/environments",
        ".backup",
    ]

    present = []
    missing = []

    for dir_path in required:
        if Path(dir_path).is_dir():
            present.append(dir_path)
        else:
            missing.append(dir_path)

    return present, missing


def check_config_files() -> tuple[list[str], list[str]]:
    """Check required configuration files exist."""
    required = [
        "system/config/calibration/intrinsic_calibration.json",
        "system/config/calibration/intrinsic_calibration_rubric.json",
        "system/config/calibration/unit_transforms.json",
        "system/config/calibration/runtime_layers.json",
        "system/config/questionnaire/questionnaire_monolith.json",
        "system/config/questionnaire/pattern_registry.json",
        "system/config/environments/production.json",
        "system/config/environments/development.json",
        "system/config/environments/testing.json",
    ]

    present = []
    missing = []

    for file_path in required:
        if Path(file_path).is_file():
            present.append(file_path)
        else:
            missing.append(file_path)

    return present, missing


def check_utilities() -> tuple[list[str], list[str]]:
    """Check required utility scripts exist."""
    required = [
        "system/config/config_manager.py",
        "system/config/initialize_registry.py",
        "system/config/verify_config_integrity.py",
        "system/config/list_backups.py",
        "system/config/migrate_hardcoded_values.py",
        "system/config/test_governance_system.py",
        "system/config/setup_governance.sh",
    ]

    present = []
    missing = []

    for file_path in required:
        if Path(file_path).is_file():
            present.append(file_path)
        else:
            missing.append(file_path)

    return present, missing


def check_documentation() -> tuple[list[str], list[str]]:
    """Check required documentation exists."""
    required = [
        "system/config/GOVERNANCE.md",
        "system/config/QUICK_REFERENCE.md",
        ".backup/README.md",
        "CONFIGURATION_GOVERNANCE_IMPLEMENTATION.md",
    ]

    present = []
    missing = []

    for file_path in required:
        if Path(file_path).is_file():
            present.append(file_path)
        else:
            missing.append(file_path)

    return present, missing


def check_hook() -> bool:
    """Check pre-commit hook exists and is executable."""
    hook_path = Path(".git/hooks/pre-commit")
    if not hook_path.exists():
        return False

    import stat

    mode = hook_path.stat().st_mode
    return bool(mode & stat.S_IXUSR)


def main() -> None:
    """Main verification entry point."""
    print("=" * 80)
    print("Configuration Governance Implementation Verification")
    print("=" * 80)
    print()

    all_passed = True

    print("1. Directory Structure")
    print("-" * 80)
    present, missing = check_directories()
    for d in present:
        print(f"  ✓ {d}")
    for d in missing:
        print(f"  ✗ {d} [MISSING]")
        all_passed = False
    print()

    print("2. Configuration Files")
    print("-" * 80)
    present, missing = check_config_files()
    for f in present:
        size = Path(f).stat().st_size
        print(f"  ✓ {f} ({size} bytes)")
    for f in missing:
        print(f"  ✗ {f} [MISSING]")
        all_passed = False
    print()

    print("3. Utility Scripts")
    print("-" * 80)
    present, missing = check_utilities()
    for f in present:
        print(f"  ✓ {f}")
    for f in missing:
        print(f"  ✗ {f} [MISSING]")
        all_passed = False
    print()

    print("4. Documentation")
    print("-" * 80)
    present, missing = check_documentation()
    for f in present:
        print(f"  ✓ {f}")
    for f in missing:
        print(f"  ✗ {f} [MISSING]")
        all_passed = False
    print()

    print("5. Pre-Commit Hook")
    print("-" * 80)
    hook_ok = check_hook()
    if hook_ok:
        print("  ✓ .git/hooks/pre-commit (executable)")
    else:
        print("  ✗ .git/hooks/pre-commit [MISSING or NOT EXECUTABLE]")
        all_passed = False
    print()

    print("=" * 80)
    if all_passed:
        print("✓ VERIFICATION PASSED - All components present")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Run: bash system/config/setup_governance.sh")
        print("  2. Initialize: python system/config/initialize_registry.py")
        print("  3. Verify: python system/config/verify_config_integrity.py")
        print()
        exit(0)
    else:
        print("✗ VERIFICATION FAILED - Some components missing")
        print("=" * 80)
        exit(1)


if __name__ == "__main__":
    main()
