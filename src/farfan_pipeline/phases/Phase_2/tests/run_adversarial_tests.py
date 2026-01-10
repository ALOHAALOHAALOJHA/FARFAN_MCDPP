#!/usr/bin/env python3
"""
Phase 2 Adversarial Test Runner

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: Execute full adversarial test suite

Usage:
    python run_adversarial_tests.py                    # Run all tests
    python run_adversarial_tests.py --severe          # Run only severe tests
    python run_adversarial_tests.py --contracts       # Run contract tests only
    python run_adversarial_tests.py --quick           # Run quick smoke tests
    python run_adversarial_tests.py --report          # Generate HTML report

Exit Codes:
    0: All tests passed
    1: Some tests failed
    2: No tests collected
    3: Configuration error
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PHASE_TWO_DIR = TESTS_DIR.parent


def run_tests(
    test_files: list[str] | None = None,
    markers: list[str] | None = None,
    verbose: bool = True,
    html_report: bool = False,
    stop_on_first: bool = False,
    quick: bool = False,
) -> int:
    """Run pytest with specified options.

    Args:
        test_files: Specific test files to run
        markers: Pytest markers to filter by
        verbose: Enable verbose output
        html_report: Generate HTML report
        stop_on_first: Stop on first failure
        quick: Run quick subset of tests

    Returns:
        Exit code (0=success, 1=failure)
    """
    cmd = ["python", "-m", "pytest"]

    # Add test directory or specific files
    if test_files:
        cmd.extend(test_files)
    else:
        cmd.append(str(TESTS_DIR))

    # Add markers
    if markers:
        marker_expr = " or ".join(markers)
        cmd.extend(["-m", marker_expr])

    # Verbose output
    if verbose:
        cmd.append("-v")

    # Long tracebacks for debugging
    cmd.extend(["--tb", "long"])

    # Stop on first failure
    if stop_on_first:
        cmd.append("-x")

    # Quick mode: run first 50 tests only
    if quick:
        cmd.extend(["--maxfail", "5"])

    # HTML report
    if html_report:
        report_path = TESTS_DIR / "reports" / "adversarial_test_report.html"
        report_path.parent.mkdir(exist_ok=True)
        cmd.extend(["--html", str(report_path), "--self-contained-html"])

    # Run pytest
    print(f"\n{'='*70}")
    print("PHASE 2 ADVERSARIAL TEST SUITE")
    print(f"{'='*70}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*70}\n")

    try:
        result = subprocess.run(cmd, cwd=PHASE_TWO_DIR)
        return result.returncode
    except FileNotFoundError:
        print("ERROR: pytest not found. Install with: pip install pytest")
        return 3


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Phase 2 Adversarial Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--severe",
        "-s",
        action="store_true",
        help="Run only SEVERE tests (architecture-critical)",
    )

    parser.add_argument(
        "--contracts",
        "-c",
        action="store_true",
        help="Run contract integrity tests only",
    )

    parser.add_argument(
        "--architecture",
        "-a",
        action="store_true",
        help="Run architecture compliance tests only",
    )

    parser.add_argument(
        "--execution",
        "-e",
        action="store_true",
        help="Run execution flow tests only",
    )

    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security boundary tests only",
    )

    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick smoke test (stop after 5 failures)",
    )

    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Generate HTML test report",
    )

    parser.add_argument(
        "--stop-on-first",
        "-x",
        action="store_true",
        help="Stop on first test failure",
    )

    parser.add_argument(
        "--file",
        "-f",
        type=str,
        action="append",
        help="Run specific test file(s)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=True,
        help="Verbose output (default: True)",
    )

    args = parser.parse_args()

    # Determine markers
    markers = []
    if args.severe:
        markers.append("severe")
    if args.security:
        markers.append("security")

    # Determine test files
    test_files = None
    if args.file:
        test_files = args.file
    elif args.contracts:
        test_files = [str(TESTS_DIR / "test_contract_integrity.py")]
    elif args.architecture:
        test_files = [str(TESTS_DIR / "test_architecture_compliance.py")]
    elif args.execution:
        test_files = [str(TESTS_DIR / "test_execution_flow.py")]

    return run_tests(
        test_files=test_files,
        markers=markers if markers else None,
        verbose=args.verbose,
        html_report=args.report,
        stop_on_first=args.stop_on_first,
        quick=args.quick,
    )


if __name__ == "__main__":
    sys.exit(main())
