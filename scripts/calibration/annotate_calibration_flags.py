"""
annotate_calibration_flags.py - Epistemological Flag Annotation

This script copies `requiere_calibracion` and `requiere_parametrizacion` flags
from methods_inventory_raw.json to canonical_method_catalogue_v2.json.

[Constraint 1] Flags are SOURCE OF TRUTH from inventory, not generated.
[Constraint 4] Parametrization flags guide config externalization.

Architecture:
- Reads flags from methods_inventory_raw.json (2093 methods, 227 calibration, 198 param)
- Copies to canonical_method_catalogue_v2.json (2163 methods)
- Applies mandatory overrides for 30 executors
- Validates coverage before writing

Usage:
    python scripts/calibration/annotate_calibration_flags.py --dry-run
    python scripts/calibration/annotate_calibration_flags.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# File paths
REPO_ROOT = Path(__file__).parent.parent.parent
CATALOG_PATH = REPO_ROOT / "config" / "canonical_method_catalogue_v2.json"
INVENTORY_PATH = REPO_ROOT / "methods_inventory_raw.json"

# Expected counts from inventory
EXPECTED_MIN_CALIBRATION = 200  # Should be >= 227 from inventory
EXPECTED_MIN_PARAMETRIZATION = 180  # Should be ~198 from inventory


def load_json(path: Path) -> Dict | List:
    """Load JSON file."""
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data: Dict | List) -> None:
    """Save JSON file with pretty formatting."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def build_inventory_index(inventory: Dict) -> Dict[str, Dict]:
    """
    Build index from methods_inventory_raw.json.
    
    Args:
        inventory: Loaded inventory dict with 'methods' key
        
    Returns:
        Dict mapping canonical_id to method data
    """
    if 'methods' not in inventory:
        print("ERROR: methods_inventory_raw.json missing 'methods' key", file=sys.stderr)
        sys.exit(1)
    
    methods = inventory['methods']
    index = {}
    
    missing_flags_count = 0
    for method in methods:
        canonical_id = method.get('canonical_identifier')
        if not canonical_id:
            continue
        
        # Check for required flags
        if 'requiere_calibracion' not in method:
            missing_flags_count += 1
            continue
        if 'requiere_parametrizacion' not in method:
            missing_flags_count += 1
            continue
        
        index[canonical_id] = {
            'requiere_calibracion': method['requiere_calibracion'],
            'requiere_parametrizacion': method['requiere_parametrizacion'],
            'role': method.get('role', 'unknown'),
            'epistemology_tags': method.get('epistemology_tags', []),
        }
    
    if missing_flags_count > 0:
        print(f"ERROR: {missing_flags_count} methods missing flags in inventory", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ Loaded {len(index)} methods from inventory")
    return index


def normalize_unique_id_to_canonical(unique_id: str) -> str:
    """
    Convert unique_id from catalog to canonical_identifier format.
    
    Catalog format: module.path.ClassName.method_name.line_number
    Inventory format: module_path.ClassName.method_name OR ClassName.method_name
    
    Args:
        unique_id: From catalog
        
    Returns:
        Normalized ID for matching
    """
    # Remove file extension and line number
    parts = unique_id.split('.')
    
    # Try to extract ClassNa.method pattern
    # Find where class names start (capitalized)
    for i in range(len(parts)):
        if parts[i] and parts[i][0].isupper():
            # Found class, take class.method
            if i + 1 < len(parts):
                return f"{parts[i]}.{parts[i+1]}"
    
    # Fallback: last two parts before line number
    if len(parts) >= 2:
        # Check if last part is a number (line number)
        if parts[-1].isdigit() and len(parts) >= 3:
            return f"{parts[-3]}.{parts[-2]}"
        return f"{parts[-2]}.{parts[-1]}"
    
    return unique_id


def is_executor_execute_method(method: Dict) -> bool:
    """
    Check if method is an executor .execute() method (D{n}_Q{m}_*).
    
    Args:
        method: Catalog entry
        
    Returns:
        True if executor method
    """
    file_path = method.get('file_path', '')
    canonical_name = method.get('canonical_name', '')
    
    # Must be in executors.py
    if 'executors.py' not in file_path:
        return False
    
    # Must end with .execute
    if not canonical_name.endswith('.execute'):
        return False
    
    # Must match D[1-6]_Q[1-5] pattern
    if re.search(r'D[1-6]_Q[1-5]_\w+\.execute', canonical_name):
        return True
    
    return False


def annotate_catalog(inventory_index: Dict[str, Dict], dry_run: bool = True) -> Tuple[int, int, int]:
    """
    Annotate catalog with flags from inventory.
    
    Args:
        inventory_index: Index built from inventory
        dry_run: If True, don't modify file
        
    Returns:
        Tuple of (calibration_count, parametrization_count, executor_count)
    """
    catalog = load_json(CATALOG_PATH)
    assert isinstance(catalog, list), "Catalog must be a list"
    
    calibration_count = 0
    parametrization_count = 0
    executor_count = 0
    executors_list = []
    
    for method in catalog:
        unique_id = method.get('unique_id', '')
        
        # Try to match with inventory
        canonical_id = normalize_unique_id_to_canonical(unique_id)
        
        # Default: no calibration/parametrization
        req_cal = False
        req_param = False
        
        # Look up in inventory
        if canonical_id in inventory_index:
            inv_data = inventory_index[canonical_id]
            req_cal = inv_data['requiere_calibracion']
            req_param = inv_data['requiere_parametrizacion']
        
        # MANDATORY OVERRIDE: ALL executors require calibration
        if is_executor_execute_method(method):
            req_cal = True  # Force
            executor_count += 1
            executors_list.append(method.get('canonical_name', unique_id))
        
        # Write flags to catalog
        method['requiere_calibracion'] = req_cal
        method['requiere_parametrizacion'] = req_param
        
        if req_cal:
            calibration_count += 1
        if req_param:
            parametrization_count += 1
    
    # Validate coverage
    errors = []
    
    if calibration_count < EXPECTED_MIN_CALIBRATION:
        errors.append(
            f"Calibration count {calibration_count} < expected {EXPECTED_MIN_CALIBRATION}"
        )
    
    if parametrization_count < EXPECTED_MIN_PARAMETRIZATION:
        errors.append(
            f"Parametrization count {parametrization_count} < expected {EXPECTED_MIN_PARAMETRIZATION}"
        )
    
    if executor_count != 30:
        errors.append(
            f"Executor count {executor_count} != 30 expected"
        )
    
    if errors:
        print("\n❌ VALIDATION ERRORS:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(f"\nExecutors found ({executor_count}):", file=sys.stderr)
        for ex in executors_list[:10]:
            print(f"  - {ex}", file=sys.stderr)
        if len(executors_list) > 10:
            print(f"  ... and {len(executors_list) - 10} more", file=sys.stderr)
        sys.exit(1)
    
    if not dry_run:
        save_json(CATALOG_PATH, catalog)
        print(f"✓ Written: {CATALOG_PATH}")
    else:
        print(f"[DRY RUN] Would write to: {CATALOG_PATH}")
    
    return calibration_count, parametrization_count, executor_count


def main():
    parser = argparse.ArgumentParser(
        description="Annotate catalog with calibration/parametrization flags"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Report changes without modifying files"
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help="Apply changes to catalog"
    )
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        print("ERROR: Must specify --dry-run or --apply", file=sys.stderr)
        sys.exit(1)
    
    print("="*80)
    print("CALIBRATION FLAG ANNOTATION")
    print("="*80)
    
    # Load inventory and build index
    inventory = load_json(INVENTORY_PATH)
    inventory_index = build_inventory_index(inventory)
    
    # Annotate catalog
    cal_count, param_count, exec_count = annotate_catalog(
        inventory_index, dry_run=args.dry_run
    )
    
    print(f"\n📊 Results:")
    print(f"  - Methods requiring calibration: {cal_count}")
    print(f"  - Methods requiring parametrization: {param_count}")
    print(f"  - Executor methods (forced calibration): {exec_count}/30")
    
    if args.dry_run:
        print("\n✅ Validation passed! Run with --apply to modify catalog")
    else:
        print("\n✅ Catalog annotated successfully!")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
