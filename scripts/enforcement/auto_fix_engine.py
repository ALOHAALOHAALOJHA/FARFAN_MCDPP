#!/usr/bin/env python3
"""
Auto-Fix Engine for GNEA

Automatically fixes common GNEA violations where safe to do so.
Performs atomic operations with backup and rollback capabilities.

Document: FPN-GNEA-004
Version: 1.0.0
"""

from __future__ import annotations

import ast
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple


class FixType(Enum):
    """Types of auto-fixable operations."""

    RENAME_FILE = "RENAME_FILE"
    ADD_METADATA = "ADD_METADATA"
    UPDATE_IMPORTS = "UPDATE_IMPORTS"
    CREATE_DIRECTORY = "CREATE_DIRECTORY"
    MOVE_FILE = "MOVE_FILE"
    DANGEROUS = "DANGEROUS"


@dataclass
class FixOperation:
    """Represents a fix operation."""

    fix_type: FixType
    target: Path
    description: str
    operation: Callable[[], bool]
    rollback: Callable[[], bool]
    requires_confirmation: bool = True
    backup_path: Optional[Path] = None


class AutoFixEngine:
    """
    Automated fix engine for GNEA violations.

    Performs safe, atomic operations with:
    - Backup before changes
    - Rollback capability
    - Confirmation prompts for dangerous operations
    - Dry-run mode for preview
    """

    # Phase module naming pattern
    PHASE_MODULE_PATTERN = re.compile(
        r"^phase(?P<phase>[0-9])_"
        r"(?P<stage>\d{2})_"
        r"(?P<order>\d{2})_"
        r"(?P<name>[a-z][a-z0-9_]*)\.py$"
    )

    # Metadata template for phase modules
    METADATA_TEMPLATE = """
# METADATA
__version__ = "1.0.0"
__phase__ = {phase}
__stage__ = {stage}
__order__ = {order}
__author__ = "{author}"
__created__ = "{created}"
__modified__ = "{modified}"
__criticality__ = "{criticality}"
__execution_pattern__ = "{execution_pattern}"
"""

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        dry_run: bool = False,
        require_confirmation: bool = True,
    ):
        self.repo_root = repo_root or Path.cwd()
        self.dry_run = dry_run
        self.require_confirmation = require_confirmation
        self.operations: List[FixOperation] = []
        self.completed: List[FixOperation] = []
        self.failed: List[Tuple[FixOperation, str]] = []
        self.backup_dir = self.repo_root / ".gnea_backup"

    def fix_phase_directory_naming(self, old_name: str, new_name: str) -> bool:
        """Fix phase directory naming (e.g., Phase_zero → Phase_0)."""
        phases_dir = self.repo_root / "src/farfan_pipeline/phases"
        old_path = phases_dir / old_name
        new_path = phases_dir / new_name

        if not old_path.exists():
            print(f"✗ Source directory not found: {old_path}")
            return False

        if new_path.exists():
            print(f"✗ Target directory already exists: {new_path}")
            return False

        def operation() -> bool:
            try:
                if self.dry_run:
                    print(f"[DRY RUN] Would rename: {old_name} → {new_name}")
                    return True

                # Create backup
                backup_path = self._backup_directory(old_path)

                # Perform rename
                old_path.rename(new_path)

                # Update imports in all Python files
                self._update_phase_imports(old_name, new_name)

                return True
            except Exception as e:
                print(f"✗ Error renaming directory: {e}")
                return False

        def rollback() -> bool:
            try:
                # Restore from backup if it exists
                if (self.backup_dir / old_name).exists():
                    shutil.move(str(self.backup_dir / old_name), str(old_path))
                # Rename back if new_path exists
                if new_path.exists():
                    new_path.rename(old_path)
                # Revert imports
                self._update_phase_imports(new_name, old_name)
                return True
            except Exception:
                return False

        op = FixOperation(
            fix_type=FixType.RENAME_FILE,
            target=old_path,
            description=f"Rename phase directory: {old_name} → {new_name}",
            operation=operation,
            rollback=rollback,
            requires_confirmation=True,
        )

        return self._execute_operation(op)

    def fix_module_naming(self, old_path: Path, new_name: str) -> bool:
        """Fix module file naming to follow phase{N}_{SS}_{OO}_{name}.py pattern."""
        if not old_path.exists():
            print(f"✗ File not found: {old_path}")
            return False

        new_path = old_path.parent / new_name

        if new_path.exists():
            print(f"✗ Target file already exists: {new_path}")
            return False

        def operation() -> bool:
            try:
                if self.dry_run:
                    print(f"[DRY RUN] Would rename: {old_path.name} → {new_name}")
                    return True

                # Create backup
                backup_path = self._backup_file(old_path)

                # Perform rename
                old_path.rename(new_path)

                # Update imports
                self._update_imports(old_path.name, new_name)

                return True
            except Exception as e:
                print(f"✗ Error renaming file: {e}")
                return False

        def rollback() -> bool:
            try:
                if new_path.exists():
                    new_path.rename(old_path)
                self._update_imports(new_name, old_path.name)
                return True
            except Exception:
                return False

        op = FixOperation(
            fix_type=FixType.RENAME_FILE,
            target=old_path,
            description=f"Rename module: {old_path.name} → {new_name}",
            operation=operation,
            rollback=rollback,
            requires_confirmation=False,
        )

        return self._execute_operation(op)

    def add_metadata_to_module(
        self, filepath: Path, phase: int, stage: int, order: int, author: str = "GNEA-AutoFix"
    ) -> bool:
        """Add required metadata to a phase module."""
        if not filepath.exists():
            print(f"✗ File not found: {filepath}")
            return False

        def operation() -> bool:
            try:
                content = filepath.read_text()

                # Check if metadata already exists
                if "__phase__" in content:
                    print(f"✓ Metadata already exists in {filepath.name}")
                    return True

                if self.dry_run:
                    print(f"[DRY RUN] Would add metadata to: {filepath.name}")
                    return True

                # Backup first
                self._backup_file(filepath)

                # Parse to find insertion point (after docstring)
                tree = ast.parse(content)

                # Prepare metadata
                now = datetime.utcnow().isoformat()
                metadata = self.METADATA_TEMPLATE.format(
                    phase=phase,
                    stage=stage,
                    order=order,
                    author=author,
                    created=now,
                    modified=now,
                    criticality="MEDIUM",
                    execution_pattern="Per-Task",
                )

                # Find first non-docstring statement
                insert_pos = 0
                found_docstring = False
                for node in tree.body:
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                        found_docstring = True
                        insert_pos = node.end_lineno
                        break
                    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                        if isinstance(node.value.value, str):
                            found_docstring = True
                            insert_pos = node.end_lineno
                            break

                # Insert metadata
                lines = content.split("\n")

                if found_docstring:
                    # Insert after docstring
                    insert_index = insert_pos
                    lines.insert(insert_index, metadata)
                else:
                    # Insert at beginning
                    lines.insert(0, metadata)

                # Write back
                filepath.write_text("\n".join(lines))
                return True

            except Exception as e:
                print(f"✗ Error adding metadata: {e}")
                return False

        def rollback() -> bool:
            # Restore from backup
            backup_path = self.backup_dir / filepath.name
            if backup_path.exists():
                shutil.copy(str(backup_path), str(filepath))
                return True
            return False

        op = FixOperation(
            fix_type=FixType.ADD_METADATA,
            target=filepath,
            description=f"Add metadata to: {filepath.name}",
            operation=operation,
            rollback=rollback,
            requires_confirmation=False,
        )

        return self._execute_operation(op)

    def create_stage_directories(self, phase_dir: Path) -> bool:
        """Create required stage component directories for a phase."""
        stage_dirs = [
            "stage_10_components",
            "stage_20_components",
            "stage_30_components",
            "stage_40_components",
            "stage_50_components",
            "stage_60_components",
            "stage_80_components",
            "stage_90_components",
        ]

        success = True
        for stage_dir in stage_dirs:
            stage_path = phase_dir / stage_dir
            if not stage_path.exists():
                if not self._create_directory(stage_path):
                    success = False

        return success

    def _create_directory(self, dir_path: Path) -> bool:
        """Create a directory."""

        def operation() -> bool:
            try:
                if self.dry_run:
                    print(f"[DRY RUN] Would create directory: {dir_path.name}")
                    return True

                dir_path.mkdir(parents=True, exist_ok=True)

                # Create __init__.py
                (dir_path / "__init__.py").write_text('"""Stage components."""\n')

                return True
            except Exception as e:
                print(f"✗ Error creating directory: {e}")
                return False

        def rollback() -> bool:
            try:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                return True
            except Exception:
                return False

        op = FixOperation(
            fix_type=FixType.CREATE_DIRECTORY,
            target=dir_path,
            description=f"Create directory: {dir_path.name}",
            operation=operation,
            rollback=rollback,
            requires_confirmation=False,
        )

        return self._execute_operation(op)

    def _execute_operation(self, op: FixOperation) -> bool:
        """Execute a fix operation with confirmation and rollback support."""
        self.operations.append(op)

        # Check if confirmation is required
        if self.require_confirmation and op.requires_confirmation:
            response = input(f"\nExecute: {op.description}? [y/N] ")
            if response.lower() != "y":
                print("⊘ Skipped")
                return False

        # Execute operation
        print(f"⏳ {op.description}...")
        success = op.operation()

        if success:
            self.completed.append(op)
            print(f"✓ Done")
        else:
            self.failed.append((op, "Operation failed"))
            # Attempt rollback
            print("⎋ Attempting rollback...")
            if op.rollback():
                print("✓ Rollback successful")
            else:
                print("✗ Rollback failed")

        return success

    def _backup_file(self, filepath: Path) -> Path:
        """Create a backup of a file."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(str(filepath), str(backup_path))
        return backup_path

    def _backup_directory(self, dirpath: Path) -> Path:
        """Create a backup of a directory."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{dirpath.name}_{timestamp}"
        backup_path = self.backup_dir / backup_name

        shutil.copytree(str(dirpath), str(backup_path))
        return backup_path

    def _update_imports(self, old_name: str, new_name: str) -> None:
        """Update import statements across the codebase."""
        src_dir = self.repo_root / "src"

        # Find import patterns to update
        old_module = old_name.replace(".py", "")
        new_module = new_name.replace(".py", "")

        for py_file in src_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                original = content

                # Update direct imports
                content = content.replace(f"from {old_module}", f"from {new_module}")
                content = content.replace(f"import {old_module}", f"import {new_module}")

                # Update if changed
                if content != original:
                    if not self.dry_run:
                        py_file.write_text(content)
                    else:
                        print(f"[DRY RUN] Would update imports in: {py_file}")

            except (UnicodeDecodeError, PermissionError):
                pass

    def _update_phase_imports(self, old_phase: str, new_phase: str) -> None:
        """Update imports related to a phase rename."""
        # Map old phase names to module prefixes
        phase_map = {
            "Phase_zero": "phase0",
            "Phase_one": "phase1",
            "Phase_two": "phase2",
            "Phase_three": "phase3",
            "Phase_0": "phase0",
            "Phase_1": "phase1",
            "Phase_2": "phase2",
            "Phase_3": "phase3",
        }

        old_prefix = phase_map.get(old_phase)
        new_prefix = phase_map.get(new_phase)

        if not old_prefix or not new_prefix:
            return

        # Update imports
        self._update_imports(old_prefix, new_prefix)

    def print_summary(self) -> None:
        """Print summary of operations."""
        print("\n" + "=" * 70)
        print("AUTO-FIX SUMMARY")
        print("=" * 70)
        print(f"Total Operations: {len(self.operations)}")
        print(f"Completed: {len(self.completed)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Dry Run: {self.dry_run}")
        print("=" * 70)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-Fix Engine - Automatically fix GNEA violations"
    )

    parser.add_argument("--path", type=Path, default=None, help="Path to repository root")

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying them"
    )

    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm all operations")

    parser.add_argument(
        "--rename-phase",
        nargs=2,
        metavar=("OLD", "NEW"),
        help="Rename a phase directory (e.g., Phase_zero Phase_0)",
    )

    parser.add_argument(
        "--rename-file",
        nargs=2,
        metavar=("PATH", "NEW_NAME"),
        help="Rename a file (e.g., path/to/file.py new_name.py)",
    )

    args = parser.parse_args()

    engine = AutoFixEngine(
        repo_root=args.path, dry_run=args.dry_run, require_confirmation=not args.yes
    )

    # Execute requested operation
    if args.rename_phase:
        old_name, new_name = args.rename_phase
        engine.fix_phase_directory_naming(old_name, new_name)

    if args.rename_file:
        old_path, new_name = args.rename_file
        engine.fix_module_naming(Path(old_path), new_name)

    engine.print_summary()

    # Exit with appropriate code
    import sys

    sys.exit(0 if not engine.failed else 1)


if __name__ == "__main__":
    main()
