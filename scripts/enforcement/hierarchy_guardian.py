#!/usr/bin/env python3
"""
Hierarchy Guardian for GNEA
Validates directory structure and depth compliance.

Document: FPN-GNEA-001
Version: 2.0.0
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

__version__ = "2.0.0"


class HierarchyGuardian:
    """Guards directory hierarchy compliance."""

    MAX_DEPTH = 5
    FORBIDDEN_DIRS: set[str] = {"temp", "tmp", "backup", "old", "misc", "other", "stuff", "things"}

    REQUIRED_PHASE_STRUCTURE = {
        "files": [
            "PHASE_{N}_MANIFEST.json",
            "PHASE_{N}_CONSTANTS.py",
            "README.md",
            "__init__.py",
        ],
        "directories": ["tests", "contracts", "docs"],
    }

    SKIP_PATTERNS = [
        "__pycache__",
        ".git",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        "-env",
        ".egg-info",
        ".DS_Store",
    ]

    def __init__(self, root: Path):
        self.root = root
        self.violations: list[dict[str, Any]] = []

    def validate(self) -> dict[str, Any]:
        """Run all hierarchy validations."""
        self._check_depth()
        self._check_forbidden_dirs()
        self._check_phase_structure()
        self._check_orphan_directories()

        return {
            "valid": len(self.violations) == 0,
            "violation_count": len(self.violations),
            "violations": self.violations,
        }

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        return any(pattern in str(path) for pattern in self.SKIP_PATTERNS)

    def _check_depth(self) -> None:
        """Check hierarchy depth violations."""
        for path in self.root.rglob("*"):
            if self._should_skip(path):
                continue
            if path.is_file():
                try:
                    rel_path = path.relative_to(self.root)
                    depth = len(rel_path.parts)
                    if depth > self.MAX_DEPTH:
                        self.violations.append({
                            "rule": "HIERARCHY-DEPTH",
                            "severity": "WARNING",
                            "path": str(path),
                            "message": f"Depth {depth} exceeds max {self.MAX_DEPTH}",
                            "depth": depth,
                        })
                except ValueError:
                    # Defensive guard: paths come from self.root.rglob("*"), so relative_to(self.root)
                    # should not fail. If it does due to an unexpected filesystem edge case, skip
                    # this path rather than failing the entire validation run.
                    pass

    def _check_forbidden_dirs(self) -> None:
        """Check for forbidden directory names."""
        for path in self.root.rglob("*"):
            if self._should_skip(path):
                continue
            if path.is_dir() and path.name.lower() in self.FORBIDDEN_DIRS:
                self.violations.append({
                    "rule": "HIERARCHY-FORBIDDEN",
                    "severity": "ERROR",
                    "path": str(path),
                    "message": f"Forbidden directory name: {path.name}",
                })

    def _check_phase_structure(self) -> None:
        """Check phase directory structure compliance."""
        phases_dir = self.root / "src" / "farfan_pipeline" / "phases"
        if not phases_dir.exists():
            return

        phase_name_map = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        }

        for phase_dir in phases_dir.iterdir():
            if not phase_dir.is_dir() or not phase_dir.name.startswith("Phase_"):
                continue

            phase_name = phase_dir.name.replace("Phase_", "").lower()
            phase_num = phase_name_map.get(phase_name)

            if phase_num is None:
                continue

            for file_template in self.REQUIRED_PHASE_STRUCTURE["files"]:
                filename = file_template.replace("{N}", str(phase_num))
                if not (phase_dir / filename).exists():
                    self.violations.append({
                        "rule": "PHASE-STRUCTURE-FILE",
                        "severity": "ERROR",
                        "path": str(phase_dir / filename),
                        "message": f"Missing required file: {filename}",
                    })

            for dirname in self.REQUIRED_PHASE_STRUCTURE["directories"]:
                if not (phase_dir / dirname).exists():
                    self.violations.append({
                        "rule": "PHASE-STRUCTURE-DIR",
                        "severity": "WARNING",
                        "path": str(phase_dir / dirname),
                        "message": f"Missing recommended directory: {dirname}",
                    })

    def _check_orphan_directories(self) -> None:
        """Check for empty or orphan directories."""
        for path in self.root.rglob("*"):
            if self._should_skip(path):
                continue
            if path.is_dir():
                contents = list(path.iterdir())
                non_hidden = [c for c in contents if not c.name.startswith(".")]
                if len(non_hidden) == 0:
                    self.violations.append({
                        "rule": "HIERARCHY-ORPHAN",
                        "severity": "INFO",
                        "path": str(path),
                        "message": "Empty directory",
                    })


def main():
    parser = argparse.ArgumentParser(description="GNEA Hierarchy Guardian")
    parser.add_argument("--path", type=Path, default=Path.cwd(), help="Root path")
    parser.add_argument("--output", type=Path, help="Output report path")

    args = parser.parse_args()

    guardian = HierarchyGuardian(args.path)
    result = guardian.validate()

    print("=" * 70)
    print("GNEA HIERARCHY GUARDIAN REPORT")
    print("=" * 70)
    print(f"Violations: {result['violation_count']}")
    print("=" * 70)

    for v in result["violations"][:20]:
        icon = "❌" if v["severity"] == "ERROR" else "⚠️" if v["severity"] == "WARNING" else "ℹ️"
        print(f"{icon} [{v['rule']}] {v['path']}")
        print(f"   {v['message']}")

    if len(result["violations"]) > 20:
        print(f"\n... and {len(result['violations']) - 20} more violations")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
