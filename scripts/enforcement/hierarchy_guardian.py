#!/usr/bin/env python3
"""
Hierarchy Guardian for GNEA

Validates directory structure compliance, ensuring proper hierarchy depth,
forbidden directory detection, and structural integrity.

Document: FPN-GNEA-003
Version: 1.0.0
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class HierarchyViolation(Enum):
    """Types of hierarchy violations."""

    MAX_DEPTH_EXCEEDED = "MAX_DEPTH_EXCEEDED"
    FORBIDDEN_DIRECTORY = "FORBIDDEN_DIRECTORY"
    EMPTY_DIRECTORY = "EMPTY_DIRECTORY"
    ORPHANED_FILE = "ORPHANED_FILE"
    MISSING_REQUIRED_STRUCTURE = "MISSING_REQUIRED_STRUCTURE"
    INCONSISTENT_STRUCTURE = "INCONSISTENT_STRUCTURE"


@dataclass
class HierarchyIssue:
    """Represents a hierarchy structure violation."""

    path: Path
    violation_type: HierarchyViolation
    message: str
    severity: str = "ERROR"
    suggestion: Optional[str] = None
    actual_depth: Optional[int] = None
    expected_depth: Optional[int] = None


@dataclass
class DirectoryStats:
    """Statistics for a directory."""

    path: Path
    total_files: int = 0
    total_dirs: int = 0
    max_depth: int = 0
    file_types: Dict[str, int] = field(default_factory=dict)
    has_init: bool = False
    has_readme: bool = False
    has_manifest: bool = False


class HierarchyGuardian:
    """
    Guardian of directory structure compliance.

    Validates:
    - Maximum hierarchy depth
    - Forbidden directory names
    - Required structure for phases
    - Consistent organization
    """

    # Forbidden directory names
    FORBIDDEN_DIRS = {
        "temp",
        "tmp",
        "backup",
        "old",
        "misc",
        "legacy",
        "deprecated",
        "archive",
        "staging",
        "dev",
        "test",
    }

    # Maximum hierarchy depth from src/
    MAX_DEPTH = 5

    # Required subdirectories for each phase
    PHASE_REQUIRED_SUBDIRS = ["tests", "contracts", "transitions", "docs", "validation"]

    # Optional but recommended subdirectories (legacy: stage_*_components removed)
    PHASE_OPTIONAL_SUBDIRS: List[str] = []

    def __init__(self, repo_root: Optional[Path] = None, max_depth: int = MAX_DEPTH):
        self.repo_root = repo_root or Path.cwd()
        self.max_depth = max_depth
        self.issues: List[HierarchyIssue] = []
        self.stats: Dict[Path, DirectoryStats] = {}

    def validate_repository(self) -> List[HierarchyIssue]:
        """Validate entire repository structure."""
        phases_dir = self.repo_root / "src/farfan_pipeline/phases"

        if not phases_dir.exists():
            return []

        # Validate each phase directory
        for phase_dir in phases_dir.iterdir():
            if not phase_dir.is_dir() or phase_dir.name.startswith("."):
                continue

            self.issues.extend(self._validate_phase_directory(phase_dir))

        # Validate hierarchy depth
        self.issues.extend(self._validate_hierarchy_depth())

        # Check for forbidden directories
        self.issues.extend(self._validate_forbidden_directories())

        return self.issues

    def _validate_phase_directory(self, phase_dir: Path) -> List[HierarchyIssue]:
        """Validate a single phase directory structure."""
        issues = []

        # Check for required files
        required_files = {
            "PHASE_{N}_MANIFEST.json": self._get_manifest_name(phase_dir),
            "PHASE_{N}_CONSTANTS.py": self._get_constants_name(phase_dir),
            "README.md": "README.md",
            "__init__.py": "__init__.py",
        }

        for file_type, filename in required_files.items():
            if not (phase_dir / filename).exists():
                issues.append(
                    HierarchyIssue(
                        path=phase_dir,
                        violation_type=HierarchyViolation.MISSING_REQUIRED_STRUCTURE,
                        message=f"Missing required file: {filename}",
                        severity="ERROR",
                        suggestion=f"Create {filename} in {phase_dir.name}",
                    )
                )

        # Check for required subdirectories
        for subdir in self.PHASE_REQUIRED_SUBDIRS:
            subdir_path = phase_dir / subdir
            if not subdir_path.exists():
                issues.append(
                    HierarchyIssue(
                        path=phase_dir,
                        violation_type=HierarchyViolation.MISSING_REQUIRED_STRUCTURE,
                        message=f"Missing required subdirectory: {subdir}/",
                        severity="WARNING",
                        suggestion=f"Create {subdir}/ directory in {phase_dir.name}",
                    )
                )

        # Check for empty directories
        if self._is_directory_empty(phase_dir, ignore_dunder=True):
            issues.append(
                HierarchyIssue(
                    path=phase_dir,
                    violation_type=HierarchyViolation.EMPTY_DIRECTORY,
                    message=f"Phase directory is empty or contains only dunder files",
                    severity="WARNING",
                )
            )

        return issues

    def _validate_hierarchy_depth(self) -> List[HierarchyIssue]:
        """Validate maximum hierarchy depth."""
        issues = []
        src_dir = self.repo_root / "src"

        if not src_dir.exists():
            return issues

        for file_path in src_dir.rglob("*"):
            if not file_path.is_file():
                continue

            # Calculate depth from src/
            try:
                rel_path = file_path.relative_to(src_dir)
                depth = len(rel_path.parts)

                if depth > self.max_depth:
                    issues.append(
                        HierarchyIssue(
                            path=file_path,
                            violation_type=HierarchyViolation.MAX_DEPTH_EXCEEDED,
                            message=f"File at depth {depth} exceeds maximum depth of {self.max_depth}",
                            severity="WARNING",
                            actual_depth=depth,
                            expected_depth=self.max_depth,
                            suggestion=f"Consider reorganizing: {rel_path}",
                        )
                    )
            except ValueError:
                # File not under src/ - skip
                continue

        return issues

    def _validate_forbidden_directories(self) -> List[HierarchyIssue]:
        """Check for forbidden directory names."""
        issues = []
        phases_dir = self.repo_root / "src/farfan_pipeline/phases"

        if not phases_dir.exists():
            return issues

        for root, dirs, _ in self._walk(phases_dir):
            for dir_name in dirs:
                if dir_name.lower() in self.FORBIDDEN_DIRS:
                    issues.append(
                        HierarchyIssue(
                            path=Path(root) / dir_name,
                            violation_type=HierarchyViolation.FORBIDDEN_DIRECTORY,
                            message=f"Forbidden directory name: {dir_name}",
                            severity="ERROR",
                            suggestion="Rename to a compliant name",
                        )
                    )

        return issues

    def _get_manifest_name(self, phase_dir: Path) -> str:
        """Get the expected manifest filename for a phase."""
        # Extract phase number from directory name
        name = phase_dir.name

        # Handle Phase_N pattern
        if name.startswith("Phase_"):
            phase_num = name[6:]  # After 'Phase_'
            return f"PHASE_{phase_num}_MANIFEST.json"

        # Handle old-style names (Phase_zero, etc.)
        phase_map = {
            "Phase_zero": "PHASE_0_MANIFEST.json",
            "Phase_one": "PHASE_1_MANIFEST.json",
            "Phase_two": "PHASE_2_MANIFEST.json",
            "Phase_three": "PHASE_3_MANIFEST.json",
            "Phase_eight": "PHASE_8_MANIFEST.json",
            "Phase_nine": "PHASE_9_MANIFEST.json",
        }

        return phase_map.get(name, "PHASE_N_MANIFEST.json")

    def _get_constants_name(self, phase_dir: Path) -> str:
        """Get the expected constants filename for a phase."""
        name = phase_dir.name

        # Handle Phase_N pattern
        if name.startswith("Phase_"):
            phase_num = name[6:]
            return f"PHASE_{phase_num}_CONSTANTS.py"

        # Handle old-style names
        phase_map = {
            "Phase_zero": "PHASE_0_CONSTANTS.py",
            "Phase_one": "PHASE_1_CONSTANTS.py",
            "Phase_two": "PHASE_2_CONSTANTS.py",
            "Phase_three": "PHASE_3_CONSTANTS.py",
            "Phase_eight": "PHASE_8_CONSTANTS.py",
            "Phase_nine": "PHASE_9_CONSTANTS.py",
        }

        return phase_map.get(name, "PHASE_N_CONSTANTS.py")

    def _is_directory_empty(self, dir_path: Path, ignore_dunder: bool = True) -> bool:
        """Check if directory is empty (optionally ignoring dunder files)."""
        if not dir_path.is_dir():
            return False

        items = list(dir_path.iterdir())
        if ignore_dunder:
            items = [i for i in items if not i.name.startswith("__")]

        return len(items) == 0

    def _walk(self, path: Path):
        """Walk directory tree."""
        for root, dirs, files in os.walk(path):
            yield root, dirs, files

    def generate_structure_report(self) -> Dict:
        """Generate a comprehensive structure report."""
        phases_dir = self.repo_root / "src/farfan_pipeline/phases"

        report = {
            "repository_root": str(self.repo_root),
            "validation_timestamp": Path(__file__).stat().st_mtime,
            "max_depth_allowed": self.max_depth,
            "phases": {},
            "summary": {"total_issues": len(self.issues), "by_severity": {}, "by_type": {}},
        }

        if not phases_dir.exists():
            return report

        # Collect phase statistics
        for phase_dir in phases_dir.iterdir():
            if not phase_dir.is_dir() or phase_dir.name.startswith("."):
                continue

            phase_stats = self._collect_directory_stats(phase_dir)
            report["phases"][phase_dir.name] = {
                "file_count": phase_stats.total_files,
                "directory_count": phase_stats.total_dirs,
                "max_depth": phase_stats.max_depth,
                "has_init": phase_stats.has_init,
                "has_readme": phase_stats.has_readme,
                "has_manifest": phase_stats.has_manifest,
                "file_types": phase_stats.file_types,
            }

        # Summarize issues
        for issue in self.issues:
            report["summary"]["by_severity"][issue.severity] = (
                report["summary"]["by_severity"].get(issue.severity, 0) + 1
            )
            report["summary"]["by_type"][issue.violation_type.value] = (
                report["summary"]["by_type"].get(issue.violation_type.value, 0) + 1
            )

        return report

    def _collect_directory_stats(self, dir_path: Path) -> DirectoryStats:
        """Collect statistics for a directory."""
        stats = DirectoryStats(path=dir_path)

        try:
            for item in dir_path.rglob("*"):
                if item.is_file():
                    stats.total_files += 1
                    # Track file types
                    ext = item.suffix or "no_extension"
                    stats.file_types[ext] = stats.file_types.get(ext, 0) + 1
                elif item.is_dir():
                    stats.total_dirs += 1

            # Check for required files
            stats.has_init = (dir_path / "__init__.py").exists()
            stats.has_readme = (dir_path / "README.md").exists()

            # Check for manifest (handle different naming patterns)
            for manifest_file in dir_path.glob("*MANIFEST.json"):
                stats.has_manifest = True
                break

            # Calculate max depth
            for item in dir_path.rglob("*"):
                try:
                    depth = len(item.relative_to(dir_path).parts)
                    stats.max_depth = max(stats.max_depth, depth)
                except ValueError:
                    pass

        except PermissionError:
            pass

        return stats

    def print_report(self) -> None:
        """Print hierarchy validation report."""
        print("\n" + "=" * 70)
        print("HIERARCHY GUARDIAN REPORT")
        print("=" * 70)
        print(f"Repository: {self.repo_root}")
        print(f"Max Depth Allowed: {self.max_depth}")
        print("-" * 70)
        print(f"Total Issues Found: {len(self.issues)}")

        if not self.issues:
            print("✓ No hierarchy violations found")
            print("=" * 70)
            return

        # Group by severity
        by_severity = {"ERROR": [], "WARNING": []}
        for issue in self.issues:
            by_severity[issue.severity].append(issue)

        for severity, issues in by_severity.items():
            if not issues:
                continue

            print(f"\n{severity}: {len(issues)} issues")
            print("-" * 70)

            for issue in issues[:10]:  # Show first 10
                rel_path = issue.path.relative_to(self.repo_root)
                print(f"  [{issue.violation_type.value}]")
                print(f"    Path: {rel_path}")
                print(f"    Message: {issue.message}")
                if issue.suggestion:
                    print(f"    💡 {issue.suggestion}")
                if issue.actual_depth is not None:
                    print(f"    Depth: {issue.actual_depth} (max: {issue.expected_depth})")

            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more")

        print("=" * 70)

    def save_report(self, output_path: Path) -> None:
        """Save structure report to JSON file."""
        report = self.generate_structure_report()
        output_path.write_text(json.dumps(report, indent=2))
        print(f"\nStructure report saved to: {output_path}")


def main():
    """CLI entry point."""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="Hierarchy Guardian - Validate directory structure compliance"
    )

    parser.add_argument("--path", type=Path, default=None, help="Path to repository root")

    parser.add_argument("--max-depth", type=int, default=5, help="Maximum allowed hierarchy depth")

    parser.add_argument("--output", type=Path, default=None, help="Output JSON report file")

    args = parser.parse_args()

    guardian = HierarchyGuardian(repo_root=args.path, max_depth=args.max_depth)

    guardian.validate_repository()
    guardian.print_report()

    if args.output:
        guardian.save_report(args.output)

    # Exit with error code if issues found
    import sys

    error_count = sum(1 for i in guardian.issues if i.severity == "ERROR")
    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    import os

    main()
