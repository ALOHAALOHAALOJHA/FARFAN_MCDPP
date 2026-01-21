#!/usr/bin/env python3
"""
F.A.R.F.A.N Import Validator
============================

Validates import patterns across the codebase to ensure compliance
with import governance standards.

Usage:
    python scripts/validate_imports.py [--fix] [--verbose]

Author: F.A.R.F.A.N Development Team
Date: 2026-01-21
"""

import ast
import os
import re
import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ImportValidator:
    """Validates Python imports against governance standards."""

    # Deprecated import patterns
    DEPRECATED_PATTERNS = {
        r"from farfan_pipeline\.analysis\.factory": "Use farfan_pipeline.infrastructure.dependencies instead",
        r"from farfan_pipeline\.analysis\.retry_handler": "Use farfan_pipeline.infrastructure.dependencies instead",
        r"import analysis\.factory": "Use farfan_pipeline.infrastructure.dependencies instead",
    }

    # Files that should use absolute imports
    ABSOLUTE_IMPORT_ZONES = [
        "src/farfan_pipeline/phases/Phase_",
        "src/farfan_pipeline/orchestration",
    ]

    def __init__(self, root: Path):
        self.root = root
        self.issues: List[Dict] = []
        self.stats = defaultdict(int)

    def validate_file(self, filepath: Path) -> List[Dict]:
        """Validate a single Python file."""
        issues = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
                tree = ast.parse(source, filename=str(filepath))

            # Check each import statement
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    issues.extend(self._check_import(node, filepath))
                elif isinstance(node, ast.ImportFrom):
                    issues.extend(self._check_import_from(node, filepath))

            # Check for deprecated patterns
            for line_num, line in enumerate(source.split("\n"), 1):
                for pattern, message in self.DEPRECATED_PATTERNS.items():
                    if re.search(pattern, line) and not line.strip().startswith("#"):
                        issues.append({
                            "file": str(filepath.relative_to(self.root)),
                            "line": line_num,
                            "type": "deprecated",
                            "pattern": pattern,
                            "message": message,
                            "code": line.strip(),
                        })

        except SyntaxError as e:
            issues.append({
                "file": str(filepath.relative_to(self.root)),
                "line": e.lineno or 0,
                "type": "syntax",
                "message": str(e),
            })

        return issues

    def _check_import(self, node: ast.Import, filepath: Path) -> List[Dict]:
        """Check an 'import X' statement."""
        issues = []
        for alias in node.names:
            for pattern, message in self.DEPRECATED_PATTERNS.items():
                if re.match(pattern, alias.name):
                    issues.append({
                        "file": str(filepath.relative_to(self.root)),
                        "line": node.lineno,
                        "type": "deprecated",
                        "pattern": pattern,
                        "message": message,
                        "code": f"import {alias.name}",
                    })
        return issues

    def _check_import_from(self, node: ast.ImportFrom, filepath: Path) -> List[Dict]:
        """Check a 'from X import Y' statement."""
        issues = []

        if node.module is None:
            return issues

        module = node.module

        # Check for deprecated patterns
        for pattern, message in self.DEPRECATED_PATTERNS.items():
            if re.match(pattern, module):
                issues.append({
                    "file": str(filepath.relative_to(self.root)),
                    "line": node.lineno,
                    "type": "deprecated",
                    "pattern": pattern,
                    "message": message,
                    "code": f"from {module} import ...",
                })

        # Check for bare relative imports in specific zones
        filepath_str = str(filepath)
        for zone in self.ABSOLUTE_IMPORT_ZONES:
            if zone in filepath_str:
                if node.level > 0 and not module:
                    issues.append({
                        "file": str(filepath.relative_to(self.root)),
                        "line": node.lineno,
                        "type": "style",
                        "message": "Use absolute imports instead of bare relative imports",
                        "code": f"from . import ...",
                    })

        return issues

    def validate_project(self) -> None:
        """Validate all Python files in the project."""
        python_files = list(self.root.rglob("*.py"))

        # Exclude common directories
        exclude_dirs = {".venv", "__pycache__", ".git", "node_modules", "build", "dist"}
        python_files = [
            f for f in python_files
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]

        for filepath in python_files:
            issues = self.validate_file(filepath)
            self.issues.extend(issues)

        # Calculate statistics
        for issue in self.issues:
            self.stats[issue["type"]] += 1
        self.stats["files_checked"] = len(python_files)

    def print_report(self, verbose: bool = False) -> None:
        """Print the validation report."""
        print("=" * 80)
        print("IMPORT VALIDATION REPORT")
        print("=" * 80)
        print(f"\nFiles checked: {self.stats['files_checked']}")
        print(f"Total issues: {len(self.issues)}")

        if not self.issues:
            print("\n✅ No import issues found!")
            return

        # Group issues by type
        by_type = defaultdict(list)
        for issue in self.issues:
            by_type[issue["type"]].append(issue)

        # Print issues by type
        for issue_type, issues in by_type.items():
            print(f"\n{issue_type.upper()} ({len(issues)} issues):")
            print("-" * 80)

            for issue in issues:
                print(f"  {issue['file']}:{issue['line']}")
                print(f"    {issue.get('message', 'Unknown issue')}")
                if verbose:
                    print(f"    Code: {issue.get('code', 'N/A')}")
                print()

        # Print summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        for issue_type, count in sorted(self.stats.items()):
            if issue_type != "files_checked":
                print(f"  {issue_type}: {count}")
        print()


def main():
    parser = ArgumentParser(description="Validate F.A.R.F.A.N imports")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues (not implemented yet)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    # Get project root
    root = Path(__file__).parent.parent
    if not (root / "pyproject.toml").exists():
        print("Error: Could not find project root (pyproject.toml not found)")
        sys.exit(1)

    # Run validation
    validator = ImportValidator(root)
    validator.validate_project()
    validator.print_report(verbose=args.verbose)

    # Exit with error code if issues found
    sys.exit(1 if validator.issues else 0)


if __name__ == "__main__":
    main()
