#!/usr/bin/env python3
"""
Metadata Injector for GNEA Phase Modules.

Injects required metadata into all phase modules following GNEA standards.

Document: FPN-GNEA-010
Version: 1.0.0
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path


def extract_metadata_from_filename(filename: str) -> dict[str, str] | None:
    """Extract phase, stage, order from filename.

    Args:
        filename: The filename to parse

    Returns:
        Dictionary with phase, stage, order, name or None if not a valid phase module
    """
    pattern = r"^phase(?P<phase>[0-9])_(?P<stage>\d{2})_(?P<order>\d{2})_(?P<name>[a-z][a-z0-9_]+)\.py$"
    match = re.match(pattern, filename)
    if match:
        return match.groupdict()
    return None


def determine_criticality(stage: int, name: str) -> str:
    """Determine criticality based on stage and module name.

    Args:
        stage: Stage number
        name: Module name

    Returns:
        Criticality level: CRITICAL, HIGH, MEDIUM, or LOW
    """
    # Stage-based criticality
    if stage in (0, 90):
        return "LOW"
    elif stage in (10, 50):
        return "CRITICAL"
    elif stage == 40:
        return "HIGH"

    # Name-based criticality
    if any(x in name for x in ["validator", "enforcer", "contract"]):
        return "HIGH"
    elif any(x in name for x in ["main", "bootstrap", "orchestrator"]):
        return "CRITICAL"

    return "MEDIUM"


def determine_execution_pattern(name: str) -> str:
    """Determine execution pattern from module name.

    Args:
        name: Module name

    Returns:
        Execution pattern: Singleton, Per-Task, Continuous, On-Demand, or Parallel
    """
    if any(x in name for x in ["validator", "enforcer"]):
        return "Per-Task"
    elif any(x in name for x in ["orchestrator", "main", "factory"]):
        return "Singleton"
    elif any(x in name for x in ["monitor", "continuous", "watcher"]):
        return "Continuous"
    elif "parallel" in name:
        return "Parallel"
    else:
        return "On-Demand"


def inject_metadata(filepath: Path, dry_run: bool = False) -> bool:
    """Inject metadata into a Python file.

    Args:
        filepath: Path to the Python file
        dry_run: If True, don't actually write changes

    Returns:
        True if metadata was injected, False otherwise
    """
    # Parse filename
    metadata = extract_metadata_from_filename(filepath.name)
    if not metadata:
        return False

    content = filepath.read_text()

    # Check if metadata already exists
    if "__phase__" in content:
        return False

    # Find existing docstring if present
    docstring_match = re.search(r'^"""[\s\S]*?"""', content, re.MULTILINE)
    if docstring_match:
        docstring = docstring_match.group(0)
        insert_position = docstring_match.end()
    else:
        # Find first import or class/function definition
        import_match = re.search(r'^(from |import |class |def )', content, re.MULTILINE)
        if import_match:
            insert_position = import_match.start()
        else:
            insert_position = 0
        docstring = ''

    # Extract metadata values
    phase = int(metadata['phase'])
    stage = int(metadata['stage'])
    order = int(metadata['order'])

    # Determine criticality and execution pattern
    criticality = determine_criticality(stage, metadata['name'])
    execution_pattern = determine_execution_pattern(metadata['name'])

    # Get current date
    today = datetime.now().strftime('%Y-%m-%d')

    # Generate metadata block
    metadata_block = f"""
# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = {phase}
__stage__ = {stage}
__order__ = {order}
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "{today}"
__modified__ = "{today}"
__criticality__ = "{criticality}"
__execution_pattern__ = "{execution_pattern}"

"""

    # Insert metadata after docstring
    new_content = content[:insert_position] + "\n" + metadata_block + content[insert_position:]

    if not dry_run:
        filepath.write_text(new_content)

    return True


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GNEA Metadata Injector"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=range(10),
        help="Only process specific phase (0-9)"
    )

    args = parser.parse_args()

    repo_root = Path.cwd()
    phases_root = repo_root / "src" / "farfan_pipeline" / "phases"

    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")

    print("Injecting metadata into phase modules...")
    print(f"Repository root: {repo_root}")

    if args.phase is not None:
        print(f"Phase filter: {args.phase}")

    print()

    processed = 0
    skipped = 0
    updated = []

    for phase_dir in sorted(phases_root.glob("Phase_*")):
        # Extract phase number
        phase_match = re.match(r"Phase_(\d+)", phase_dir.name)
        if not phase_match:
            continue

        phase_num = int(phase_match.group(1))

        # Apply phase filter if specified
        if args.phase is not None and phase_num != args.phase:
            continue

        for py_file in sorted(phase_dir.glob("phase*.py")):
            if py_file.name == "__init__.py":
                continue

            result = inject_metadata(py_file, dry_run=args.dry_run)

            if result:
                processed += 1
                updated.append(str(py_file.relative_to(repo_root)))
                action = "Would update" if args.dry_run else "✓ Updated"
                print(f"{action}: {py_file.relative_to(repo_root)}")
            else:
                skipped += 1

    print()
    print(f"Processed: {processed} files")
    print(f"Skipped: {skipped} files (already have metadata or not phase modules)")

    if args.dry_run:
        print("\nThis was a dry run. Run without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
