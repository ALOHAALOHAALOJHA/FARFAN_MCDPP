#!/usr/bin/env python3
"""
Script: verify_phase2_labels.py
Purpose: Verify that all Phase 2 files have correct PHASE_LABEL metadata

This script checks that:
- All .py files in Phase_2 contain "PHASE_LABEL: Phase 2"
- Phase labels are consistent
- No mismatched phase labels exist

Usage:
    python scripts/verify_phase2_labels.py
    python scripts/verify_phase2_labels.py --fix
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


def check_phase_label(file_path: Path, expected_phase: int = 2) -> tuple[bool, str | None]:
    """
    Check if a file has the correct PHASE_LABEL.
    
    Args:
        file_path: Path to the Python file
        expected_phase: Expected phase number
        
    Returns:
        Tuple of (has_correct_label, current_label)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Search for PHASE_LABEL in docstrings and comments
        pattern = r'PHASE_LABEL:\s*Phase\s+(\d+)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        if not matches:
            return False, None
        
        # Check if all matches are correct
        for match in matches:
            if int(match) != expected_phase:
                return False, f"Phase {match}"
        
        return True, f"Phase {expected_phase}"
        
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return False, None


def add_phase_label(file_path: Path, phase: int = 2) -> bool:
    """
    Add PHASE_LABEL to a file if it's missing.
    
    Args:
        file_path: Path to the Python file
        phase: Phase number to add
        
    Returns:
        True if label was added successfully
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check if there's already a docstring
        if '"""' in content[:500]:
            # Find the end of the first docstring
            first_quote = content.find('"""')
            if first_quote != -1:
                # Find closing quotes
                closing_quote = content.find('"""', first_quote + 3)
                if closing_quote != -1:
                    # Insert PHASE_LABEL before closing quotes
                    label = f"\nPHASE_LABEL: Phase {phase}\n"
                    new_content = (
                        content[:closing_quote] +
                        label +
                        content[closing_quote:]
                    )
                    file_path.write_text(new_content, encoding='utf-8')
                    return True
        
        # If no docstring, add one at the top
        lines = content.split('\n')
        
        # Find first line after shebang and encoding
        insert_line = 0
        for i, line in enumerate(lines):
            if line.startswith('#!') or 'coding' in line or 'encoding' in line:
                insert_line = i + 1
            else:
                break
        
        docstring = f'"""\nPHASE_LABEL: Phase {phase}\n"""\n'
        lines.insert(insert_line, docstring)
        
        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"Error: Could not update {file_path}: {e}", file=sys.stderr)
        return False


def verify_phase2_labels(fix: bool = False) -> int:
    """
    Verify Phase 2 labels.
    
    Args:
        fix: If True, add missing labels
        
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    phase_dir = REPO_ROOT / "src" / "farfan_pipeline" / "phases" / "Phase_2"
    
    if not phase_dir.exists():
        print(f"Error: Phase directory not found: {phase_dir}", file=sys.stderr)
        return 1
    
    print("Verifying Phase 2 labels...")
    print(f"Phase directory: {phase_dir}")
    print("=" * 60)
    
    # Get all Python files
    py_files = list(phase_dir.rglob("*.py"))
    py_files = [
        f for f in py_files
        if "__pycache__" not in str(f) and not f.name.endswith(".bak")
    ]
    
    print(f"\nFound {len(py_files)} Python files")
    
    # Check each file
    missing_labels = []
    incorrect_labels = []
    correct_labels = []
    
    for py_file in py_files:
        has_correct, current_label = check_phase_label(py_file, expected_phase=2)
        
        rel_path = py_file.relative_to(phase_dir)
        
        if has_correct:
            correct_labels.append(str(rel_path))
        elif current_label is None:
            missing_labels.append(str(rel_path))
            if fix:
                if add_phase_label(py_file, phase=2):
                    print(f"  ✓ Added label to: {rel_path}")
                    correct_labels.append(str(rel_path))
                    missing_labels.remove(str(rel_path))
                else:
                    print(f"  ✗ Failed to add label to: {rel_path}")
        else:
            incorrect_labels.append((str(rel_path), current_label))
    
    # Print results
    print(f"\n✓ Correct labels: {len(correct_labels)}")
    
    if missing_labels:
        print(f"\n⚠ Missing labels: {len(missing_labels)}")
        for path in missing_labels[:10]:  # Show first 10
            print(f"  - {path}")
        if len(missing_labels) > 10:
            print(f"  ... and {len(missing_labels) - 10} more")
    
    if incorrect_labels:
        print(f"\n✗ Incorrect labels: {len(incorrect_labels)}")
        for path, label in incorrect_labels:
            print(f"  - {path}: {label}")
    
    print("\n" + "=" * 60)
    
    if missing_labels or incorrect_labels:
        if fix:
            print("VERIFICATION COMPLETED WITH FIXES")
        else:
            print("VERIFICATION FAILED")
            print("\nRun with --fix to automatically add missing labels")
        return 1 if (missing_labels or incorrect_labels) and not fix else 0
    else:
        print("VERIFICATION PASSED")
        return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify Phase 2 PHASE_LABEL metadata"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically add missing PHASE_LABEL entries"
    )
    
    args = parser.parse_args()
    return verify_phase2_labels(args.fix)


if __name__ == "__main__":
    sys.exit(main())
