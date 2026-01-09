#!/usr/bin/env python3
"""Path Audit Script for F.A.R. F.A.N

This script audits the codebase for common path-related issues:
- Hardcoded absolute paths
- Deprecated import patterns
- Manual sys.path manipulation
- Inappropriate use of os.getcwd()

Usage:
    python scripts/audit/path_audit.py [--fix] [--verbose]

Exit codes:
    0 - No issues found
    1 - Issues found (or error occurred)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class PathAuditor:
    """Audits Python files for path-related issues."""

    def __init__(self, root: Path, verbose: bool = False):
        self.root = root
        self.verbose = verbose
        self.issues: List[Dict[str, str]] = []

    def audit_file(self, py_file: Path) -> List[Dict[str, str]]:
        """Audit a single Python file for path issues."""
        file_issues = []

        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not read {py_file}: {e}")
            return file_issues

        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check 1: Hardcoded absolute paths (Unix-style)
            if re.search(r'Path\(["\']/(Users|home|var|tmp|opt|usr)', line):
                file_issues.append({
                    "file": str(py_file.relative_to(self.root)),
                    "line": i,
                    "type": "hardcoded_path",
                    "severity": "high",
                    "message": "Hardcoded absolute Unix path detected",
                    "code": line.strip()
                })

            # Check 2: Hardcoded absolute paths (Windows-style)
            if re.search(r'["\'][A-Z]:\\\\', line) or re.search(r'Path\(["\'][A-Z]:', line):
                file_issues.append({
                    "file": str(py_file.relative_to(self.root)),
                    "line": i,
                    "type": "hardcoded_path",
                    "severity": "high",
                    "message": "Hardcoded absolute Windows path detected",
                    "code": line.strip()
                })

            # Check 3: Deprecated import paths
            if "from canonic_phases" in line and "import" in line:
                file_issues.append({
                    "file": str(py_file.relative_to(self.root)),
                    "line": i,
                    "type": "deprecated_import",
                    "severity": "medium",
                    "message": "Deprecated import (use farfan_pipeline instead)",
                    "code": line.strip()
                })

            # Check 4: Raw sys.path manipulation
            if ("sys.path.append" in line or "sys.path.insert" in line) and "import sys" not in line:
                # Allow in conftest.py and setup files
                if not (py_file.name in ["conftest.py", "setup.py", "__init__.py"]):
                    file_issues.append({
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "sys_path_manipulation",
                        "severity": "medium",
                        "message": "Manual sys.path manipulation (prefer 'pip install -e .')",
                        "code": line.strip()
                    })

            # Check 5: Using os.getcwd() for path construction
            if "os.getcwd()" in line and ("Path" in line or "/" in line or "\\" in line):
                file_issues.append({
                    "file": str(py_file.relative_to(self.root)),
                    "line": i,
                    "type": "os_getcwd_usage",
                    "severity": "low",
                    "message": "Using os.getcwd() for path construction (use PROJECT_ROOT)",
                    "code": line.strip()
                })

            # Check 6: String concatenation for paths
            if re.search(r'["\'][^"\']*[/\\][^"\']*["\']\\s*\\+', line):
                file_issues.append({
                    "file": str(py_file.relative_to(self.root)),
                    "line": i,
                    "type": "string_concatenation",
                    "severity": "low",
                    "message": "String concatenation for paths (use Path / operator)",
                    "code": line.strip()
                })

        return file_issues

    def audit_directory(self) -> None:
        """Audit all Python files in the directory tree."""
        for py_file in self.root.rglob("*.py"):
            # Skip virtual environments and cache directories
            if any(part in py_file.parts for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]):
                continue

            if self.verbose:
                print(f"Auditing: {py_file.relative_to(self.root)}")

            file_issues = self.audit_file(py_file)
            self.issues.extend(file_issues)

    def print_report(self) -> None:
        """Print a formatted audit report."""
        if not self.issues:
            print("✅ Path audit passed - no issues found")
            return

        # Group by severity
        by_severity = {"high": [], "medium": [], "low": []}
        for issue in self.issues:
            by_severity[issue["severity"]].append(issue)

        print("❌ PATH AUDIT ISSUES FOUND\n")
        print("=" * 80)

        for severity in ["high", "medium", "low"]:
            issues = by_severity[severity]
            if not issues:
                continue

            icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🔵"
            print(f"\n{icon} {severity.upper()} SEVERITY ({len(issues)} issues)\n")

            for issue in issues:
                print(f"  {issue['file']}:{issue['line']}")
                print(f"    Type: {issue['type']}")
                print(f"    Message: {issue['message']}")
                print(f"    Code: {issue['code']}")
                print()

        print("=" * 80)
        print(f"\nTotal issues: {len(self.issues)}")
        print(f"  High: {len(by_severity['high'])}")
        print(f"  Medium: {len(by_severity['medium'])}")
        print(f"  Low: {len(by_severity['low'])}")

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about issues found."""
        stats = {
            "total": len(self.issues),
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for issue in self.issues:
            stats[issue["severity"]] += 1

        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit Python files for path-related issues"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Root directory to audit (default: auto-detect project root)"
    )

    args = parser.parse_args()

    # Detect project root
    if args.root:
        root = args.root.resolve()
    else:
        # Auto-detect: go up from script location to find pyproject.toml
        script_dir = Path(__file__).resolve().parent
        root = script_dir.parent.parent

        # Verify we found the right root
        if not (root / "pyproject.toml").exists():
            print("Error: Could not find project root (no pyproject.toml)")
            sys.exit(1)

    if args.verbose:
        print(f"Auditing directory: {root}\n")

    auditor = PathAuditor(root, verbose=args.verbose)
    auditor.audit_directory()
    auditor.print_report()

    stats = auditor.get_statistics()

    # Exit with error code if high-severity issues found
    if stats["high"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
