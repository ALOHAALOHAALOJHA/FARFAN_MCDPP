#!/usr/bin/env python3
"""
Compute and update SHA-256 hashes for all V3 executor contracts.

This script:
1. Finds all Q{nnn}.v3.json files
2. Computes SHA-256 hash of file content (excluding contract_hash field)
3. Updates contract_hash field in-place
4. Validates hash after update

Usage:
    python scripts/compute_contract_hashes.py [--dry-run] [--verify-only]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def compute_contract_hash(contract_data: dict[str, Any]) -> str:
    """Compute SHA-256 hash of contract, excluding contract_hash field.
    
    Args:
        contract_data: Contract dictionary
        
    Returns:
        64-character lowercase hex SHA-256 hash
    """
    # Create copy and remove contract_hash to avoid circular dependency
    contract_copy = contract_data.copy()
    if "identity" in contract_copy and "contract_hash" in contract_copy["identity"]:
        contract_copy["identity"] = contract_copy["identity"].copy()
        contract_copy["identity"]["contract_hash"] = ""
    
    # Serialize deterministically
    json_bytes = json.dumps(
        contract_copy,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")
    
    # Compute SHA-256
    return hashlib.sha256(json_bytes).hexdigest()


def update_contract_hash(contract_path: Path, dry_run: bool = False) -> dict[str, Any]:
    """Update contract_hash field in contract file.
    
    Args:
        contract_path: Path to contract JSON file
        dry_run: If True, don't write changes
        
    Returns:
        dict with keys: success, old_hash, new_hash, message
    """
    try:
        # Load contract
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        
        # Validate structure
        if "identity" not in contract:
            return {
                "success": False,
                "message": "Missing 'identity' field",
                "old_hash": None,
                "new_hash": None
            }
        
        # Get old hash
        old_hash = contract["identity"].get("contract_hash", "")
        
        # Compute new hash
        new_hash = compute_contract_hash(contract)
        
        # Check if update needed
        if old_hash == new_hash:
            return {
                "success": True,
                "message": "Hash already correct",
                "old_hash": old_hash,
                "new_hash": new_hash,
                "updated": False
            }
        
        # Update hash
        contract["identity"]["contract_hash"] = new_hash
        
        if not dry_run:
            # Write back to file
            with open(contract_path, "w", encoding="utf-8") as f:
                json.dump(contract, f, indent=2, ensure_ascii=False)
                f.write("\n")  # Add trailing newline
        
        return {
            "success": True,
            "message": "Hash updated successfully" if not dry_run else "Would update hash",
            "old_hash": old_hash,
            "new_hash": new_hash,
            "updated": True
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "message": f"JSON decode error: {e}",
            "old_hash": None,
            "new_hash": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {e}",
            "old_hash": None,
            "new_hash": None
        }


def verify_contract_hash(contract_path: Path) -> dict[str, Any]:
    """Verify contract hash is correct.
    
    Args:
        contract_path: Path to contract JSON file
        
    Returns:
        dict with keys: valid, stored_hash, computed_hash, message
    """
    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        
        if "identity" not in contract or "contract_hash" not in contract["identity"]:
            return {
                "valid": False,
                "message": "Missing contract_hash field",
                "stored_hash": None,
                "computed_hash": None
            }
        
        stored_hash = contract["identity"]["contract_hash"]
        computed_hash = compute_contract_hash(contract)
        
        valid = stored_hash == computed_hash
        
        return {
            "valid": valid,
            "message": "Hash valid" if valid else "Hash mismatch",
            "stored_hash": stored_hash,
            "computed_hash": computed_hash
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error: {e}",
            "stored_hash": None,
            "computed_hash": None
        }


def main():
    parser = argparse.ArgumentParser(
        description="Compute and update SHA-256 hashes for V3 executor contracts"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify hashes, don't update"
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        help="Path to contracts directory (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    # Find contracts directory
    if args.contracts_dir:
        contracts_dir = args.contracts_dir
    else:
        # Auto-detect from script location
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent
        contracts_dir = project_root / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "json_files_phase_two" / "executor_contracts" / "specialized"
    
    if not contracts_dir.exists():
        print(f"❌ Contracts directory not found: {contracts_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find all V3 contracts
    contract_files = sorted(contracts_dir.glob("Q*.v3.json"))
    
    if not contract_files:
        print(f"❌ No V3 contracts found in {contracts_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(contract_files)} V3 contracts")
    print()
    
    # Process contracts
    updated = 0
    already_correct = 0
    errors = 0
    invalid_hashes = []
    
    for contract_path in contract_files:
        contract_id = contract_path.stem.replace(".v3", "")
        
        if args.verify_only:
            # Verify mode
            result = verify_contract_hash(contract_path)
            if result["valid"]:
                already_correct += 1
                print(f"✅ {contract_id}: {result['message']}")
            else:
                invalid_hashes.append(contract_id)
                errors += 1
                print(f"❌ {contract_id}: {result['message']}")
                if result["stored_hash"] and result["computed_hash"]:
                    print(f"   Stored:   {result['stored_hash'][:16]}...")
                    print(f"   Computed: {result['computed_hash'][:16]}...")
        else:
            # Update mode
            result = update_contract_hash(contract_path, dry_run=args.dry_run)
            if result["success"]:
                if result.get("updated", False):
                    updated += 1
                    print(f"✅ {contract_id}: {result['message']}")
                    if result["old_hash"] and result["old_hash"] != "":
                        print(f"   Old: {result['old_hash'][:16]}...")
                    print(f"   New: {result['new_hash'][:16]}...")
                else:
                    already_correct += 1
                    print(f"✅ {contract_id}: {result['message']}")
            else:
                errors += 1
                print(f"❌ {contract_id}: {result['message']}")
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Total contracts: {len(contract_files)}")
    
    if args.verify_only:
        print(f"  Valid hashes: {already_correct}")
        print(f"  Invalid hashes: {errors}")
        if invalid_hashes:
            print(f"  Invalid: {', '.join(invalid_hashes[:10])}")
            if len(invalid_hashes) > 10:
                print(f"           ... and {len(invalid_hashes) - 10} more")
    else:
        print(f"  Updated: {updated}")
        print(f"  Already correct: {already_correct}")
        print(f"  Errors: {errors}")
        
        if args.dry_run:
            print()
            print("DRY RUN - No files were modified")
    
    print("=" * 60)
    
    # Exit code
    if errors > 0 and args.verify_only:
        sys.exit(1)
    elif errors > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
