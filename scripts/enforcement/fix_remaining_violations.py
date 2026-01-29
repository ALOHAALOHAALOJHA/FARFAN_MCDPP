#!/usr/bin/env python3
"""Fix remaining GNEA violations by renaming non-compliant files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def find_non_compliant_files(phases_root: Path) -> list[Path]:
    """Find all Python files that don't follow the canonical naming pattern.

    Args:
        phases_root: Path to the phases directory

    Returns:
        List of non-compliant file paths
    """
    non_compliant = []
    compliant_pattern = re.compile(r"^phase[0-9]_\d{2}_\d{2}_[a-z][a-z0-9_]*\.py$")

    for py_file in phases_root.rglob("*.py"):
        # Skip stage directories, __pycache__, and __init__.py
        if "/stage_" in str(py_file) or "__pycache__" in str(py_file):
            continue
        if py_file.name == "__init__.py":
            continue

        # Check if filename matches the compliant pattern
        if not compliant_pattern.match(py_file.name):
            non_compliant.append(py_file)

    return non_compliant


def generate_compliant_name(filepath: Path) -> str:
    """Generate a compliant name for a non-compliant file.

    Args:
        filepath: Path to the non-compliant file

    Returns:
        New compliant filename
    """
    # Extract phase number from directory
    phase_match = re.search(r"Phase_(\d+)", str(filepath))
    if not phase_match:
        return None

    phase_num = phase_match.group(1)

    # Get current filename without extension
    name_stem = filepath.stem

    # If it already starts with "phase" but doesn't match the full pattern,
    # it might be a file like "phase1_protocols.py"
    if name_stem.startswith("phase"):
        # Extract the actual name part
        parts = name_stem.split("_", 1)
        if len(parts) > 1:
            name = parts[1]
        else:
            name = name_stem
    else:
        name = name_stem

    # Default to stage 10, order 00 for interface/contract files
    # These will be placed in appropriate stages based on their purpose
    stage = "10"
    order = "00"

    # Determine stage based on directory context
    path_parts = filepath.parts
    if "interface" in path_parts or "interfaces" in path_parts:
        stage = "10"  # Initialization
    elif "primitives" in path_parts:
        stage = "00"  # Infrastructure
    elif "validation" in path_parts:
        stage = "40"  # Validation
    elif "enhancements" in path_parts:
        stage = "95"  # Telemetry/enhancements

    # Format: phase{N}_{SS}_{OO}_{name}.py
    return f"phase{phase_num}_{stage}_{order}_{name}.py"


def main():
    """Main entry point."""
    repo_root = Path.cwd()
    phases_root = repo_root / "src" / "farfan_pipeline" / "phases"

    print("Finding non-compliant files...")
    non_compliant = find_non_compliant_files(phases_root)

    print(f"\nFound {len(non_compliant)} non-compliant files:\n")

    # Group by parent directory
    by_dir = {}
    for filepath in non_compliant:
        parent = filepath.parent
        if parent not in by_dir:
            by_dir[parent] = []
        by_dir[parent].append(filepath)

    for parent, files in sorted(by_dir.items()):
        print(f"\n{parent.relative_to(repo_root)}:")
        for filepath in files:
            new_name = generate_compliant_name(filepath)
            if new_name:
                print(f"  {filepath.name} -> {new_name}")
            else:
                print(f"  {filepath.name} -> [SKIPPED - cannot parse]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
