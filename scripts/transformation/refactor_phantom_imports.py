#!/usr/bin/env python3
"""
PHANTOM IMPORTS REFACTOR SCRIPT
===============================
Transforms phantom namespace imports to real namespace imports.

SPEC REFERENCE: SPEC_SIGNAL_NORMALIZATION_COMPREHENSIVE.md
- Section 5.1: SISAS-NAMESPACE-001 — Resolver imports no resolubles

PHANTOM NAMESPACES (to be eliminated):
- cross_cutting_infrastructure → farfan_pipeline.infrastructure
- canonic_phases → farfan_pipeline.phases

CRITICAL RULES:
1. Preserve all functionality - only change import paths
2. Create backup before any modification
3. Verify importability after transformation
4. Log all changes for audit trail

Author: F.A.R.F.A.N Pipeline
Date: 2026-01-04
Version: 1.0.0
"""

from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
BACKUP_DIR = (
    PROJECT_ROOT / "backups" / f"phantom_refactor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)


class Transformation(NamedTuple):
    """A single import transformation."""

    pattern: str
    replacement: str
    description: str


# ============================================================================
# TRANSFORMATION MAPPINGS
# Based on empirical evidence from grep analysis
# ============================================================================

TRANSFORMATIONS: list[Transformation] = [
    # SISAS Infrastructure
    Transformation(
        pattern=r"from cross_cutting_infrastructure\.irrigation_using_signals\.SISAS",
        replacement="from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS",
        description="SISAS signal infrastructure",
    ),
    Transformation(
        pattern=r"from cross_cutting_infrastructure\.irrigation_using_signals\.ports",
        replacement="from farfan_pipeline.infrastructure.irrigation_using_signals.ports",
        description="Signal ports",
    ),
    # Capaz Calibration
    Transformation(
        pattern=r"from cross_cutting_infrastructure\.capaz_calibration_parmetrization",
        replacement="from farfan_pipeline.infrastructure.capaz_calibration_parmetrization",
        description="Capaz calibration infrastructure",
    ),
    # Contractual/Dura Lex
    Transformation(
        pattern=r"from cross_cutting_infrastructure\.contractual\.dura_lex",
        replacement="from farfan_pipeline.infrastructure.contractual.dura_lex",
        description="Dura lex contracts",
    ),
    Transformation(
        pattern=r"from cross_cutting_infrastructure\.contractual",
        replacement="from farfan_pipeline.infrastructure.contractual",
        description="Contractual infrastructure",
    ),
    # Generic cross_cutting fallback
    Transformation(
        pattern=r"from cross_cutting_infrastructure\.",
        replacement="from farfan_pipeline.infrastructure.",
        description="Generic cross_cutting to infrastructure",
    ),
    Transformation(
        pattern=r"import cross_cutting_infrastructure\.",
        replacement="import farfan_pipeline.infrastructure.",
        description="Generic cross_cutting import",
    ),
    # Phase Zero
    Transformation(
        pattern=r"from canonic_phases\.Phase_zero",
        replacement="from farfan_pipeline.phases.Phase_zero",
        description="Phase Zero imports",
    ),
    Transformation(
        pattern=r"from canonic_phases\.phase_0_bootstrap",
        replacement="from farfan_pipeline.phases.Phase_zero",
        description="Phase Zero bootstrap alias",
    ),
    # Phase One
    Transformation(
        pattern=r"from canonic_phases\.Phase_one",
        replacement="from farfan_pipeline.phases.Phase_one",
        description="Phase One imports",
    ),
    Transformation(
        pattern=r"from canonic_phases\.phase_1_cpp_ingestion",
        replacement="from farfan_pipeline.phases.Phase_one",
        description="Phase One CPP alias",
    ),
    # Phase Two
    Transformation(
        pattern=r"from canonic_phases\.Phase_two",
        replacement="from farfan_pipeline.phases.Phase_two",
        description="Phase Two imports",
    ),
    Transformation(
        pattern=r"from canonic_phases\.phase_2_execution",
        replacement="from farfan_pipeline.phases.Phase_two",
        description="Phase Two execution alias",
    ),
    # Phase Three
    Transformation(
        pattern=r"from canonic_phases\.Phase_three",
        replacement="from farfan_pipeline.phases.Phase_three",
        description="Phase Three imports",
    ),
    # Phase Four-Seven (Aggregation)
    Transformation(
        pattern=r"from canonic_phases\.Phase_four_five_six_seven",
        replacement="from farfan_pipeline.phases.Phase_four_five_six_seven",
        description="Phase 4-7 aggregation imports",
    ),
    Transformation(
        pattern=r"from canonic_phases\.phase_4_7_aggregation_pipeline",
        replacement="from farfan_pipeline.phases.Phase_four_five_six_seven",
        description="Phase 4-7 aggregation pipeline alias",
    ),
    # Phase Eight
    Transformation(
        pattern=r"from canonic_phases\.Phase_eight",
        replacement="from farfan_pipeline.phases.Phase_eight",
        description="Phase Eight imports",
    ),
    # Phase Nine
    Transformation(
        pattern=r"from canonic_phases\.Phase_nine",
        replacement="from farfan_pipeline.phases.Phase_nine",
        description="Phase Nine imports",
    ),
    # Generic canonic_phases fallback
    Transformation(
        pattern=r"from canonic_phases\.",
        replacement="from farfan_pipeline.phases.",
        description="Generic canonic_phases to phases",
    ),
    Transformation(
        pattern=r"import canonic_phases\.",
        replacement="import farfan_pipeline.phases.",
        description="Generic canonic_phases import",
    ),
]


class RefactorResult(NamedTuple):
    """Result of refactoring a single file."""

    filepath: Path
    original_lines: int
    modified_lines: int
    transformations_applied: list[str]
    success: bool
    error: str | None = None


def create_backup(src_dir: Path, backup_dir: Path) -> bool:
    """Create backup of source directory."""
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_dir, backup_dir / "src", dirs_exist_ok=True)
        print(f"✓ Backup created at: {backup_dir}")
        return True
    except Exception as e:
        print(f"✗ Backup failed: {e}")
        return False


def transform_file(filepath: Path, dry_run: bool = False) -> RefactorResult:
    """Apply transformations to a single file."""
    try:
        original_content = filepath.read_text(encoding="utf-8")
        modified_content = original_content
        transformations_applied: list[str] = []

        for transform in TRANSFORMATIONS:
            if re.search(transform.pattern, modified_content):
                modified_content = re.sub(
                    transform.pattern, transform.replacement, modified_content
                )
                transformations_applied.append(transform.description)

        if transformations_applied:
            original_lines = len(
                [
                    l
                    for l in original_content.split("\n")
                    if "cross_cutting" in l or "canonic_phases" in l
                ]
            )
            modified_lines = len(
                [
                    l
                    for l in modified_content.split("\n")
                    if "cross_cutting" in l or "canonic_phases" in l
                ]
            )

            if not dry_run:
                filepath.write_text(modified_content, encoding="utf-8")

            return RefactorResult(
                filepath=filepath,
                original_lines=original_lines,
                modified_lines=modified_lines,
                transformations_applied=transformations_applied,
                success=True,
            )

        return RefactorResult(
            filepath=filepath,
            original_lines=0,
            modified_lines=0,
            transformations_applied=[],
            success=True,
        )

    except Exception as e:
        return RefactorResult(
            filepath=filepath,
            original_lines=0,
            modified_lines=0,
            transformations_applied=[],
            success=False,
            error=str(e),
        )


def refactor_all(src_dir: Path, dry_run: bool = False) -> list[RefactorResult]:
    """Refactor all Python files in source directory."""
    results: list[RefactorResult] = []

    py_files = list(src_dir.rglob("*.py"))
    print(f"Found {len(py_files)} Python files to process")

    for py_file in py_files:
        result = transform_file(py_file, dry_run=dry_run)
        if result.transformations_applied:
            results.append(result)
            rel_path = py_file.relative_to(src_dir.parent)
            status = "[DRY-RUN]" if dry_run else "[MODIFIED]"
            print(f"  {status} {rel_path}")
            for t in result.transformations_applied:
                print(f"           └── {t}")

    return results


def verify_no_phantoms(src_dir: Path) -> tuple[int, list[str]]:
    """Verify no phantom imports remain."""
    phantom_pattern = re.compile(r"(cross_cutting_infrastructure|canonic_phases)")
    remaining: list[str] = []
    count = 0

    for py_file in src_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.split("\n"), 1):
                if phantom_pattern.search(line) and ("import" in line or "from" in line):
                    # Skip comments and strings (heuristic)
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if '"""' in line or "'''" in line:
                        continue
                    remaining.append(f"{py_file.relative_to(src_dir.parent)}:{i}")
                    count += 1
        except Exception:
            continue

    return count, remaining


def main(dry_run: bool = False) -> int:
    """Main entry point."""
    print("=" * 70)
    print("PHANTOM IMPORTS REFACTOR")
    print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'LIVE (will modify files)'}")
    print("=" * 70)

    # Pre-check
    print("\n[1/4] Pre-refactor phantom count...")
    pre_count, pre_files = verify_no_phantoms(SRC_DIR)
    print(
        f"      Found {pre_count} phantom imports in {len(set(f.split(':')[0] for f in pre_files))} files"
    )

    if pre_count == 0:
        print("\n✓ No phantom imports found. Nothing to do.")
        return 0

    # Backup
    if not dry_run:
        print("\n[2/4] Creating backup...")
        if not create_backup(SRC_DIR, BACKUP_DIR):
            print("✗ Aborting due to backup failure")
            return 1
    else:
        print("\n[2/4] Skipping backup (dry-run mode)")

    # Refactor
    print("\n[3/4] Applying transformations...")
    results = refactor_all(SRC_DIR, dry_run=dry_run)

    modified_count = len(results)
    total_transforms = sum(len(r.transformations_applied) for r in results)
    print(f"\n      Modified {modified_count} files with {total_transforms} transformations")

    # Verify
    print("\n[4/4] Post-refactor verification...")
    post_count, post_files = verify_no_phantoms(SRC_DIR)

    if post_count == 0:
        print("      ✓ All phantom imports eliminated!")
    else:
        print(f"      ⚠ {post_count} phantom imports remain:")
        for f in post_files[:10]:
            print(f"        - {f}")
        if len(post_files) > 10:
            print(f"        ... and {len(post_files) - 10} more")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Before: {pre_count} phantom imports")
    print(f"  After:  {post_count} phantom imports")
    print(f"  Eliminated: {pre_count - post_count}")
    print(f"  Files modified: {modified_count}")

    if not dry_run and post_count > 0:
        print(f"\n  Backup location: {BACKUP_DIR}")
        print("  To rollback: cp -r {backup}/src/* src/")

    print("=" * 70)

    return 0 if post_count == 0 else 1


if __name__ == "__main__":
    # Parse args
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    sys.exit(main(dry_run=dry_run))
