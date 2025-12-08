"""Verify configuration file integrity against hash registry.

This script checks if configuration files have been modified by comparing
their current SHA256 hashes against the registry.

IMPLEMENTATION_WAVE: GOVERNANCE_WAVE_2024_12_07
WAVE_LABEL: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION
"""

from pathlib import Path

from config_manager import ConfigManager


def verify_all_configs() -> tuple[list[str], list[str], list[str]]:
    """Verify all configuration files.

    Returns:
        Tuple of (verified_files, modified_files, missing_files)
    """
    config_root = Path(__file__).parent
    manager = ConfigManager(config_root)

    registry = manager.get_registry()

    verified = []
    modified = []
    missing = []

    for relative_path in registry.keys():
        file_path = config_root / relative_path

        if not file_path.exists():
            missing.append(relative_path)
            continue

        if manager.verify_hash(relative_path):
            verified.append(relative_path)
        else:
            modified.append(relative_path)

    return verified, modified, missing


def main() -> None:
    """Main verification entry point."""
    print("=" * 80)
    print("Configuration Integrity Verification")
    print("=" * 80)
    print()

    verified, modified, missing = verify_all_configs()

    print(f"Total files in registry: {len(verified) + len(modified) + len(missing)}")
    print()

    if verified:
        print(f"✓ Verified ({len(verified)} files):")
        for path in sorted(verified):
            print(f"  ✓ {path}")
        print()

    if modified:
        print(f"⚠ Modified ({len(modified)} files):")
        for path in sorted(modified):
            print(f"  ⚠ {path}")
        print()
        print("  → Run initialize_registry.py to update hashes")
        print()

    if missing:
        print(f"✗ Missing ({len(missing)} files):")
        for path in sorted(missing):
            print(f"  ✗ {path}")
        print()
        print("  → Files exist in registry but not on disk")
        print()

    print("=" * 80)

    if modified or missing:
        print("Status: FAILED - Integrity issues detected")
        exit(1)
    else:
        print("Status: PASSED - All files verified")
        exit(0)


if __name__ == "__main__":
    main()
