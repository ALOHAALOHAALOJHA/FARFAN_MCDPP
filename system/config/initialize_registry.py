"""Initialize configuration hash registry and create initial backups.

This script:
1. Scans all configuration files in system/config/
2. Computes SHA256 hashes for each file
3. Creates the config_hash_registry.json
4. Generates timestamped backups in .backup/ directory

IMPLEMENTATION_WAVE: GOVERNANCE_WAVE_2024_12_07
WAVE_LABEL: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION
"""

from pathlib import Path

from config_manager import ConfigManager


def initialize_registry() -> None:
    """Initialize config hash registry and create backups."""
    config_root = Path(__file__).parent
    manager = ConfigManager(config_root)

    print("=" * 80)
    print("Configuration Registry Initialization")
    print("=" * 80)
    print(f"Config root: {config_root}")
    print(f"Backup directory: {manager.backup_dir}")
    print()

    print("Step 1: Creating backups of existing configuration files...")
    config_files = []
    for pattern in ["**/*.json", "**/*.yaml", "**/*.yml", "**/*.toml"]:
        for file_path in config_root.glob(pattern):
            if file_path.is_file() and ".backup" not in file_path.parts:
                relative_path = str(file_path.relative_to(config_root))
                if relative_path != "config_hash_registry.json":
                    config_files.append((file_path, relative_path))

    print(f"Found {len(config_files)} configuration files")

    for file_path, relative_path in config_files:
        backup_path = manager._create_backup(file_path)
        if backup_path:
            print(f"  ✓ Backed up: {relative_path}")
            print(f"    → {backup_path.name}")

    print()
    print("Step 2: Building hash registry...")
    registry = manager.rebuild_registry()

    print(f"  ✓ Registry created with {len(registry)} entries")
    print()

    print("Step 3: Registry contents:")
    print("-" * 80)
    for path, info in sorted(registry.items()):
        print(f"  {path}")
        print(f"    Hash: {info['hash'][:16]}...")
        print(f"    Size: {info['size_bytes']} bytes")
        print(f"    Modified: {info['last_modified']}")

    print()
    print("=" * 80)
    print("✓ Initialization complete")
    print("=" * 80)
    print()
    print("Registry file: system/config/config_hash_registry.json")
    print(f"Backup directory: {manager.backup_dir.relative_to(config_root.parent)}")
    print()


if __name__ == "__main__":
    initialize_registry()
