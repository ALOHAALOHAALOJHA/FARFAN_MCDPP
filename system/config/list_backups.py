"""List and manage configuration backups.

Utilities for viewing, filtering, and restoring configuration backups.

IMPLEMENTATION_WAVE: GOVERNANCE_WAVE_2024_12_07
WAVE_LABEL: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION
"""

from datetime import datetime
from pathlib import Path

from config_manager import ConfigManager


def parse_backup_timestamp(backup_name: str) -> datetime | None:
    """Parse timestamp from backup filename.

    Backup format: YYYYMMDD_HHMMSS_microseconds_filename
    """
    try:
        parts = backup_name.split("_")
        if len(parts) >= 3:
            date_str = parts[0]
            time_str = parts[1]
            timestamp_str = f"{date_str}{time_str}"
            return datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
    except (ValueError, IndexError):
        pass
    return None


def list_all_backups(manager: ConfigManager, config_file: str | None = None) -> None:
    """List all backups, optionally filtered by config file."""
    backups = manager.list_backups(config_file)

    if not backups:
        print("No backups found.")
        return

    print(f"Found {len(backups)} backup(s):")
    print("-" * 80)

    for backup_path in backups:
        timestamp = parse_backup_timestamp(backup_path.name)
        size_kb = backup_path.stat().st_size / 1024

        print(f"  {backup_path.name}")
        if timestamp:
            print(f"    Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Size: {size_kb:.2f} KB")
        print()


def show_backup_summary(manager: ConfigManager) -> None:
    """Show summary of backups by configuration file."""
    config_root = Path(__file__).parent
    registry = manager.get_registry()

    print("=" * 80)
    print("Backup Summary")
    print("=" * 80)
    print()

    for relative_path in sorted(registry.keys()):
        backups = manager.list_backups(relative_path)
        if backups:
            latest = backups[0]
            timestamp = parse_backup_timestamp(latest.name)

            print(f"{relative_path}")
            print(f"  Backups: {len(backups)}")
            if timestamp:
                print(f"  Latest: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print()


def main() -> None:
    """Main entry point for backup listing."""
    import argparse

    parser = argparse.ArgumentParser(description="List configuration backups")
    parser.add_argument(
        "--file",
        "-f",
        help="Filter by configuration file (relative path)",
        default=None,
    )
    parser.add_argument(
        "--summary", "-s", action="store_true", help="Show summary of backups by file"
    )

    args = parser.parse_args()

    config_root = Path(__file__).parent
    manager = ConfigManager(config_root)

    print("=" * 80)
    print("Configuration Backups")
    print("=" * 80)
    print(f"Backup directory: {manager.backup_dir}")
    print()

    if args.summary:
        show_backup_summary(manager)
    else:
        list_all_backups(manager, args.file)


if __name__ == "__main__":
    main()
