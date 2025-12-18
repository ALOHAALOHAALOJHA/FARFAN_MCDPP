"""
File Header Template Enforcement for F.A.R.F.A.N Phase 2

Validates that Python files follow the mandatory header structure specified
in Section 3.2 of the naming convention requirements.

Required Header Structure (Lines 1-25):
1. Module docstring with full path
2. Brief description
3. Compliance markers
4. Optional: Additional documentation

Enforced via CI: All new Python files must have proper headers.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class HeaderViolation(NamedTuple):
    """Represents a file header violation."""

    file_path: Path
    line_number: int
    issue: str
    expected: str | None = None


def extract_module_path(file_path: Path, repo_root: Path) -> str:
    """Extract the module path from a file path.

    Args:
        file_path: Full path to the Python file
        repo_root: Repository root directory

    Returns:
        Module path in dotted notation (e.g., 'src.canonic_phases.phase_2.module_name')
    """
    rel_path = file_path.relative_to(repo_root)
    # Remove .py extension and convert path separators to dots
    module_path = str(rel_path.with_suffix("")).replace("/", ".")
    return module_path


def validate_file_header(
    file_path: Path, repo_root: Path, is_phase2: bool = False
) -> list[HeaderViolation]:
    """Validate that a Python file has the required header structure.

    Args:
        file_path: Path to the Python file
        repo_root: Repository root directory
        is_phase2: Whether this is a Phase 2 file (stricter requirements)

    Returns:
        List of header violations found
    """
    violations: list[HeaderViolation] = []

    try:
        with open(file_path) as f:
            lines = f.readlines()
    except Exception as e:
        violations.append(
            HeaderViolation(
                file_path=file_path,
                line_number=0,
                issue=f"Cannot read file: {e}",
            )
        )
        return violations

    if not lines:
        violations.append(
            HeaderViolation(
                file_path=file_path,
                line_number=0,
                issue="File is empty",
            )
        )
        return violations

    # Check 1: File must start with a docstring
    first_line = lines[0].strip()
    if not (first_line.startswith('"""') or first_line.startswith("'''")):
        violations.append(
            HeaderViolation(
                file_path=file_path,
                line_number=1,
                issue="File must start with a module docstring",
                expected='"""',
            )
        )
        return violations

    # Find the end of the docstring
    docstring_end = None
    docstring_lines = []
    in_docstring = True
    quote_type = '"""' if lines[0].strip().startswith('"""') else "'''"

    # Handle single-line docstring
    if lines[0].strip().count(quote_type) >= 2:
        docstring_end = 0
        docstring_lines = [lines[0]]
    else:
        for i, line in enumerate(lines[1:], start=1):
            if in_docstring:
                docstring_lines.append(line)
                if quote_type in line:
                    docstring_end = i
                    break

    if docstring_end is None:
        violations.append(
            HeaderViolation(
                file_path=file_path,
                line_number=1,
                issue="Docstring not properly closed",
            )
        )
        return violations

    # Check 2: For Phase 2 files, docstring must include "Module:" line
    if is_phase2:
        docstring_text = "".join(docstring_lines)
        expected_module_path = extract_module_path(file_path, repo_root)

        if "Module:" not in docstring_text and "module:" not in docstring_text.lower():
            violations.append(
                HeaderViolation(
                    file_path=file_path,
                    line_number=2,
                    issue="Phase 2 files must include 'Module:' line in docstring",
                    expected=f"Module: {expected_module_path}",
                )
            )

    # Check 3: Docstring should have reasonable length (at least 2 lines for Phase 2)
    if is_phase2 and len(docstring_lines) < 3:
        violations.append(
            HeaderViolation(
                file_path=file_path,
                line_number=1,
                issue="Phase 2 file header should have substantial documentation",
                expected="Minimum 3 lines: opening quote, Module line, description",
            )
        )

    # Check 4: After docstring, should have imports with proper structure
    # This is lenient - just check that imports exist within first 50 lines
    has_imports = False
    for i in range(docstring_end + 1, min(len(lines), 50)):
        line = lines[i].strip()
        if line.startswith("from ") or line.startswith("import "):
            has_imports = True
            break

    if not has_imports and len(lines) > docstring_end + 10:
        # Only flag if file is substantial
        violations.append(
            HeaderViolation(
                file_path=file_path,
                line_number=docstring_end + 2,
                issue="No imports found after docstring (may be okay for small files)",
            )
        )

    return violations


def validate_headers_in_directory(
    repo_root: Path, phase2_locations: list[str]
) -> list[HeaderViolation]:
    """Validate headers for all Python files in specified directories.

    Args:
        repo_root: Repository root directory
        phase2_locations: List of directory paths that are Phase 2 locations

    Returns:
        List of all header violations found
    """
    violations: list[HeaderViolation] = []

    # Find all Python files
    python_files = list(repo_root.glob("**/*.py"))

    # Filter out __pycache__, .venv, etc.
    python_files = [
        f
        for f in python_files
        if "__pycache__" not in str(f)
        and ".venv" not in str(f)
        and "/.git/" not in str(f)
    ]

    for file_path in python_files:
        # Skip __init__.py files (they can have minimal headers)
        if file_path.name == "__init__.py":
            continue

        # Check if this is a Phase 2 file
        rel_path = str(file_path.relative_to(repo_root))
        is_phase2 = any(rel_path.startswith(loc) for loc in phase2_locations)

        file_violations = validate_file_header(file_path, repo_root, is_phase2)
        violations.extend(file_violations)

    return violations


def load_legacy_header_exemptions(repo_root: Path) -> set[str]:
    """Load list of files exempt from header validation.

    Args:
        repo_root: Repository root directory

    Returns:
        Set of relative file paths that are exempt
    """
    exemption_file = repo_root / ".header_exemptions"
    if not exemption_file.exists():
        return set()

    with open(exemption_file) as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def print_violations(violations: list[HeaderViolation], repo_root: Path) -> None:
    """Print header violations in a readable format.

    Args:
        violations: List of violations to print
        repo_root: Repository root for relative paths
    """
    if not violations:
        print("✅ All file headers are properly formatted")
        return

    print(f"❌ Found {len(violations)} file header violation(s):\n")

    for violation in violations:
        rel_path = violation.file_path.relative_to(repo_root)
        print(f"❌ {rel_path}:{violation.line_number}")
        print(f"   Issue: {violation.issue}")
        if violation.expected:
            print(f"   Expected: {violation.expected}")
        print()


def main() -> int:
    """Main entry point for header validation.

    Returns:
        Exit code: 0 if all headers valid, 1 if violations found
    """
    parser = argparse.ArgumentParser(
        description="Validate F.A.R.F.A.N file headers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the repository",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with code 1 if violations found",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: ignore legacy exemptions",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Report violations but exit with code 0",
    )

    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if not repo_root.exists():
        print(f"❌ Repository root not found: {repo_root}", file=sys.stderr)
        return 1

    # Define Phase 2 locations
    phase2_locations = [
        "src/canonic_phases/phase_2",
        "src/farfan_pipeline/phases/Phase_two",
    ]

    print(f"Validating file headers in: {repo_root}\n")

    violations = validate_headers_in_directory(repo_root, phase2_locations)

    # Filter legacy exemptions unless in strict mode
    if not args.strict:
        exemptions = load_legacy_header_exemptions(repo_root)
        if exemptions:
            print(f"ℹ️  Loaded {len(exemptions)} legacy header exemptions\n")
            original_count = len(violations)
            violations = [
                v
                for v in violations
                if str(v.file_path.relative_to(repo_root)) not in exemptions
            ]
            exempted_count = original_count - len(violations)
            if exempted_count > 0:
                print(f"ℹ️  Exempted {exempted_count} legacy file(s)\n")

    print_violations(violations, repo_root)

    if violations:
        print(f"\n❌ {len(violations)} header violation(s) found")
        if args.ci and not args.report_only:
            print("\nCI MODE: Blocking PR due to header violations")
            return 1
        if args.report_only:
            print("\nREPORT MODE: Violations reported but not blocking")
            return 0
        return 1

    print("\n✅ All file headers validated successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
