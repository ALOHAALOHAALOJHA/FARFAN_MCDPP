#!/usr/bin/env python3
"""Path Audit Script for F.A.R. F.A.N

This script audits the codebase for common path-related issues:
- Hardcoded absolute paths
- Deprecated import patterns
- Manual sys.path manipulation
- Inappropriate use of os.getcwd()
- String concatenation for paths
- os.path.join usage
- Fragile relative path navigation
- Unresolved __file__ usage

Usage:
    python scripts/audit/path_audit.py [--verbose] [--json] [--severity LEVEL]

Exit codes:
    0 - No issues found
    1 - Issues found (or error occurred)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


class PathAuditor:
    """Audits Python files for path-related issues."""

    def __init__(
        self, root: Path, verbose: bool = False, exclude_patterns: Optional[List[str]] = None
    ):
        self.root = root
        self.verbose = verbose
        self.exclude_patterns = exclude_patterns or []
        self.issues: List[Dict[str, str]] = []
        self.files_scanned = 0

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
                file_issues.append(
                    {
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "hardcoded_path",
                        "severity": "high",
                        "message": "Hardcoded absolute Unix path detected",
                        "code": line.strip(),
                    }
                )

            # Check 2: Hardcoded absolute paths (Windows-style)
            if re.search(r'["\'][A-Z]:\\\\', line) or re.search(r'Path\(["\'][A-Z]:', line):
                file_issues.append(
                    {
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "hardcoded_path",
                        "severity": "high",
                        "message": "Hardcoded absolute Windows path detected",
                        "code": line.strip(),
                    }
                )

            # Check 3: Deprecated import paths
            if "from canonic_phases" in line and "import" in line:
                file_issues.append(
                    {
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "deprecated_import",
                        "severity": "medium",
                        "message": "Deprecated import (use farfan_pipeline instead)",
                        "code": line.strip(),
                    }
                )

            # Check 4: Raw sys.path manipulation
            if (
                "sys.path.append" in line or "sys.path.insert" in line
            ) and "import sys" not in line:
                # Skip if line has noqa comment
                if "# noqa" in line or "# type: ignore" in line:
                    continue
                # Allow in conftest.py and setup files
                if not (py_file.name in ["conftest.py", "setup.py", "__init__.py"]):
                    file_issues.append(
                        {
                            "file": str(py_file.relative_to(self.root)),
                            "line": i,
                            "type": "sys_path_manipulation",
                            "severity": "medium",
                            "message": "Manual sys.path manipulation (prefer 'pip install -e .')",
                            "code": line.strip(),
                        }
                    )

            # Check 5: Using os.getcwd() for path construction
            if "os.getcwd()" in line and ("Path" in line or "/" in line or "\\" in line):
                file_issues.append(
                    {
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "os_getcwd_usage",
                        "severity": "low",
                        "message": "Using os.getcwd() for path construction (use PROJECT_ROOT)",
                        "code": line.strip(),
                    }
                )

            # Check 6: String concatenation for paths
            if re.search(r'["\'][^"\']*[/\\][^"\']*["\']\\s*\\+', line):
                file_issues.append(
                    {
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "string_concatenation",
                        "severity": "low",
                        "message": "String concatenation for paths (use Path / operator)",
                        "code": line.strip(),
                    }
                )

            # Check 7: Using os.path.join instead of Path / operator
            if "os.path.join" in line and "import" not in line:
                file_issues.append(
                    {
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "os_path_join",
                        "severity": "low",
                        "message": "Using os.path.join (prefer Path / operator)",
                        "code": line.strip(),
                    }
                )

            # Check 8: Relative path navigation (../../)
            if re.search(r'[\'"](\.\.[\\/]){2,}', line):
                file_issues.append(
                    {
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "relative_navigation",
                        "severity": "medium",
                        "message": "Fragile relative path navigation (use PROJECT_ROOT)",
                        "code": line.strip(),
                    }
                )

            # Check 9: Direct __file__ manipulation without proper resolution
            if "__file__" in line and "resolve()" not in line and "Path(" in line:
                file_issues.append(
                    {
                        "file": str(py_file.relative_to(self.root)),
                        "line": i,
                        "type": "unresolved_file",
                        "severity": "low",
                        "message": "Using __file__ without .resolve() (may fail with symlinks)",
                        "code": line.strip(),
                    }
                )

        return file_issues

    def audit_directory(self) -> None:
        """Audit all Python files in the directory tree."""
        for py_file in self.root.rglob("*.py"):
            # Skip virtual environments and cache directories
            if any(
                part in py_file.parts
                for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
            ):
                continue

            # Skip files matching exclude patterns
            if any(pattern in str(py_file) for pattern in self.exclude_patterns):
                continue

            self.files_scanned += 1

            if self.verbose:
                print(f"Auditing: {py_file.relative_to(self.root)}")

            file_issues = self.audit_file(py_file)
            self.issues.extend(file_issues)

    def print_report(self, format: str = "text", min_severity: str = None) -> None:
        """Print a formatted audit report.

        Args:
            format: Output format ('text' or 'json')
            min_severity: Minimum severity to report ('low', 'medium', 'high')
        """
        # Filter by severity if requested
        issues_to_report = self.issues
        if min_severity:
            severity_levels = {"low": 0, "medium": 1, "high": 2}
            min_level = severity_levels.get(min_severity, 0)
            issues_to_report = [
                issue
                for issue in self.issues
                if severity_levels.get(issue["severity"], 0) >= min_level
            ]

        if format == "json":
            self._print_json_report(issues_to_report)
            return

        if not issues_to_report:
            print("✅ Path audit passed - no issues found")
            return

        # Group by severity
        by_severity = {"high": [], "medium": [], "low": []}
        for issue in issues_to_report:
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
        print(f"\nTotal issues: {len(issues_to_report)}")
        print(f"  High: {len(by_severity['high'])}")
        print(f"  Medium: {len(by_severity['medium'])}")
        print(f"  Low: {len(by_severity['low'])}")
        print(f"\nFiles scanned: {self.files_scanned}")

    def _print_json_report(self, issues: List[Dict[str, str]]) -> None:
        """Print report in JSON format."""
        stats = self.get_statistics()
        report = {
            "summary": {
                "total_issues": len(issues),
                "files_scanned": self.files_scanned,
                "high_severity": stats["high"],
                "medium_severity": stats["medium"],
                "low_severity": stats["low"],
            },
            "issues": issues,
        }
        print(json.dumps(report, indent=2))

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
    parser = argparse.ArgumentParser(description="Audit Python files for path-related issues")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument(
        "--severity", choices=["low", "medium", "high"], help="Minimum severity level to report"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Patterns to exclude from scanning (can be used multiple times)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Root directory to audit (default: auto-detect project root)",
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

    if args.verbose and not args.json:
        print(f"Auditing directory: {root}\n")

    auditor = PathAuditor(root, verbose=args.verbose, exclude_patterns=args.exclude)
    auditor.audit_directory()

    output_format = "json" if args.json else "text"
    auditor.print_report(format=output_format, min_severity=args.severity)

    stats = auditor.get_statistics()

    # Exit with error code if high-severity issues found
    if stats["high"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
