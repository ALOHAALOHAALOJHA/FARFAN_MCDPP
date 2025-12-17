#!/usr/bin/env python3
"""
Contract Rollback Utility
Rollback contracts to previous backup versions.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.contract_remediator import ContractBackupManager, ContractDiffGenerator


def list_backups(backup_dir: Path, contract_name: str | None = None) -> None:
    """List available backups."""
    manager = ContractBackupManager(backup_dir)

    if contract_name:
        backups = manager.list_backups(contract_name)
        if not backups:
            print(f"No backups found for {contract_name}")
            return

        print(f"\nBackups for {contract_name}:")
        for i, backup in enumerate(backups):
            size = backup.stat().st_size
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"  [{i}] {backup.name}")
            print(f"      Size: {size:,} bytes")
            print(f"      Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        all_backups = sorted(backup_dir.glob("*_backup_*.json"))
        if not all_backups:
            print("No backups found")
            return

        print("\nAll backups:")
        contracts = {}
        for backup in all_backups:
            contract = backup.name.split("_backup_")[0]
            contracts.setdefault(contract, []).append(backup)

        for contract, backups in sorted(contracts.items()):
            print(f"\n{contract}: {len(backups)} backup(s)")
            for backup in backups[-3:]:
                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                print(f"  - {backup.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")


def show_backup_diff(backup_path: Path, current_path: Path) -> None:
    """Show diff between backup and current contract."""
    try:
        with open(backup_path) as f:
            backup_contract = json.load(f)

        with open(current_path) as f:
            current_contract = json.load(f)

        diff_gen = ContractDiffGenerator()
        diff = diff_gen.generate_diff(backup_contract, current_contract, current_path.stem)

        if diff:
            print(f"\nDiff between backup and current version:")
            print(diff)
        else:
            print("\nNo differences found")

        changes = diff_gen.summarize_changes(backup_contract, current_contract)
        if any(changes.values()):
            print("\nSummary of changes:")
            if changes["fields_modified"]:
                print(f"  Modified: {', '.join(changes['fields_modified'][:5])}")
            if changes["fields_added"]:
                print(f"  Added: {', '.join(changes['fields_added'][:5])}")
            if changes["fields_removed"]:
                print(f"  Removed: {', '.join(changes['fields_removed'][:5])}")

    except Exception as e:
        print(f"Error generating diff: {e}")


def rollback_contract(
    backup_path: Path,
    target_path: Path,
    backup_dir: Path,
    dry_run: bool = False,
) -> None:
    """Rollback contract to backup version."""
    manager = ContractBackupManager(backup_dir)

    if not backup_path.exists():
        print(f"Error: Backup not found: {backup_path}")
        return

    if not target_path.exists():
        print(f"Warning: Target contract does not exist: {target_path}")

    if dry_run:
        print("\n🔍 DRY RUN MODE - No files will be modified")
        show_backup_diff(backup_path, target_path)
        return

    print(f"\nCreating backup of current version...")
    current_backup = manager.backup_contract(target_path)
    print(f"  Backed up to: {current_backup.name}")

    print(f"\nRestoring from: {backup_path.name}")
    manager.restore_backup(backup_path, target_path)
    print(f"  ✅ Restored to: {target_path}")

    with open(target_path) as f:
        contract = json.load(f)
        identity = contract.get("identity", {})
        version = identity.get("contract_version", "unknown")
        question_id = identity.get("question_id", "unknown")

    print(f"\nRestored contract: {question_id} (version {version})")


def main():
    parser = argparse.ArgumentParser(
        description="Contract Rollback Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all backups
  python scripts/rollback_contract.py --list

  # List backups for specific contract
  python scripts/rollback_contract.py --list --contract Q002.v3

  # Show diff between backup and current
  python scripts/rollback_contract.py --diff --backup Q002_backup_20250101_120000.json --contract Q002.v3.json

  # Rollback contract (with backup of current)
  python scripts/rollback_contract.py --rollback --backup Q002_backup_20250101_120000.json --contract Q002.v3.json

  # Dry run rollback
  python scripts/rollback_contract.py --rollback --backup Q002_backup_20250101_120000.json --contract Q002.v3.json --dry-run
        """,
    )

    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument(
        "--diff", action="store_true", help="Show diff between backup and current"
    )
    parser.add_argument("--rollback", action="store_true", help="Rollback to backup")
    parser.add_argument(
        "--contract", type=str, help="Contract file name (e.g., Q002.v3.json or Q002.v3)"
    )
    parser.add_argument("--backup", type=str, help="Backup file name")
    parser.add_argument("--dry-run", action="store_true", help="Preview rollback")
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("backups/contracts"),
        help="Directory for contract backups",
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=Path(
            "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
        ),
        help="Directory containing contracts",
    )

    args = parser.parse_args()

    if not any([args.list, args.diff, args.rollback]):
        parser.error("Must specify --list, --diff, or --rollback")

    if args.list:
        contract_name = None
        if args.contract:
            contract_name = args.contract.replace(".json", "").replace(".v3", "")
        list_backups(args.backup_dir, contract_name)

    elif args.diff:
        if not args.backup or not args.contract:
            parser.error("--diff requires --backup and --contract")

        backup_path = args.backup_dir / args.backup
        contract_path = args.contracts_dir / args.contract
        if not contract_path.name.endswith(".json"):
            contract_path = args.contracts_dir / f"{args.contract}.json"

        show_backup_diff(backup_path, contract_path)

    elif args.rollback:
        if not args.backup or not args.contract:
            parser.error("--rollback requires --backup and --contract")

        backup_path = args.backup_dir / args.backup
        contract_path = args.contracts_dir / args.contract
        if not contract_path.name.endswith(".json"):
            contract_path = args.contracts_dir / f"{args.contract}.json"

        rollback_contract(backup_path, contract_path, args.backup_dir, args.dry_run)


if __name__ == "__main__":
    main()
