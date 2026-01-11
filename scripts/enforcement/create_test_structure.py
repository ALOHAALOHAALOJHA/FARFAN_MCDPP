#!/usr/bin/env python3
"""
Create Test Structure for GNEA Compliance.

Creates test manifests and organizes test directories for all phases.

Document: FPN-GNEA-011
Version: 1.0.0
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


def create_test_manifest(phase_num: int, phase_dir: Path) -> bool:
    """Create TEST_MANIFEST.json for a phase.

    Args:
        phase_num: Phase number (0-9)
        phase_dir: Path to the phase directory

    Returns:
        True if manifest was created
    """
    # Find all phase modules
    modules = []
    for py_file in phase_dir.glob("phase*.py"):
        if py_file.name == "__init__.py":
            continue

        # Extract module info from filename
        match = re.match(r"phase\d_(\d{2})_(\d{2})_(.+)\.py", py_file.name)
        if match:
            stage, order, name = match.groups()

            # Determine criticality based on stage
            stage_int = int(stage)
            if stage_int in (0, 90):
                criticality = "LOW"
            elif stage_int in (10, 50):
                criticality = "CRITICAL"
            elif stage_int == 40:
                criticality = "HIGH"
            else:
                criticality = "MEDIUM"

            modules.append({
                "module": py_file.stem,
                "stage": stage_int,
                "order": int(order),
                "test_file": f"tests/phases/phase{phase_num}/test_{py_file.stem}.py",
                "coverage_target": 0.80,
                "criticality": criticality
            })

    # Count stages
    stages = {}
    for module in modules:
        stage = module["stage"]
        stages[stage] = stages.get(stage, 0) + 1

    manifest = {
        "test_suite_version": "1.0.0",
        "phase": phase_num,
        "phase_name": f"Phase_{phase_num}",
        "generated_at": datetime.utcnow().isoformat(),
        "test_framework": "pytest",
        "modules": modules,
        "stages": {
            "total": len(stages),
            "stage_counts": stages
        },
        "integration_tests": [],
        "coverage_threshold": 80.0,
        "quality_gates": {
            "min_coverage": 80.0,
            "max_violations": 0,
            "require_docstrings": True
        }
    }

    # Write manifest
    manifest_path = phase_dir / "TEST_MANIFEST.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return True


def create_stage_directory_structure(phase_dir: Path, phase_num: int) -> int:
    """Create stage component directories for a phase.

    Args:
        phase_dir: Path to the phase directory
        phase_num: Phase number

    Returns:
        Number of stage directories created
    """
    stages = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    created = 0

    for stage in stages:
        stage_dir = phase_dir / f"stage_{stage:02d}_components"
        if not stage_dir.exists():
            stage_dir.mkdir(exist_ok=True)

            # Create __init__.py
            init_file = stage_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f'''"""
Stage {stage:02d} components for Phase {phase_num}.

This directory contains modules that execute in stage {stage:02d}
of the phase {phase_num} pipeline.
"""
from __future__ import annotations

__version__ = "1.0.0"
__phase__ = {phase_num}
__stage__ = {stage}
''')
            created += 1

    return created


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create GNEA Test Structure"
    )
    parser.add_argument(
        "--stage-dirs",
        action="store_true",
        help="Create stage component directories"
    )
    parser.add_argument(
        "--test-manifests",
        action="store_true",
        help="Create test manifests"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=range(10),
        help="Only process specific phase (0-9)"
    )

    args = parser.parse_args()

    # Default to both if neither specified
    if not args.stage_dirs and not args.test_manifests:
        args.stage_dirs = True
        args.test_manifests = True

    repo_root = Path.cwd()
    phases_root = repo_root / "src" / "farfan_pipeline" / "phases"

    print("Creating GNEA test structure...")
    print(f"Repository root: {repo_root}")

    if args.phase is not None:
        print(f"Phase filter: {args.phase}")

    print()

    stage_dirs_created = 0
    manifests_created = 0

    for phase_num in range(10):
        if args.phase is not None and phase_num != args.phase:
            continue

        phase_dir = phases_root / f"Phase_{phase_num}"
        if not phase_dir.exists():
            continue

        print(f"Phase {phase_num}:")

        if args.stage_dirs:
            created = create_stage_directory_structure(phase_dir, phase_num)
            stage_dirs_created += created
            if created:
                print(f"  ✓ Created {created} stage component directories")

        if args.test_manifests:
            if create_test_manifest(phase_num, phase_dir):
                manifests_created += 1
                print(f"  ✓ Created TEST_MANIFEST.json")

    print()
    print(f"Summary:")
    print(f"  Stage directories created: {stage_dirs_created}")
    print(f"  Test manifests created: {manifests_created}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
