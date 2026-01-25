#!/usr/bin/env python3
"""
Test Script for Unified Technical Runbook Commands

This script validates that key commands from the unified Technical Runbook (v3.0.0)
are accurate and executable. It tests commands from various sections to ensure
completeness and correctness.

Usage:
    python scripts/test_runbook_commands.py
    python scripts/test_runbook_commands.py --section 24  # Test specific section
    python scripts/test_runbook_commands.py --verbose     # Verbose output
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Test cases: (section, command, expected_exit_code, description)
RUNBOOK_COMMANDS = [
    # Section 24.1 - System Requirements
    ("24.1", ["python3", "--version"], 0, "Python version check"),
    ("24.1", ["python3", "-m", "pip", "--version"], 0, "Pip availability"),
    ("24.1", ["git", "--version"], 0, "Git availability"),
    
    # Section 24.3 - Configuration Verification
    ("24.3", ["python3", "-c", "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"], 0, "Python import test"),
    
    # Section F - Testing Commands
    ("F", ["python3", "-m", "pytest", "--version"], 0, "Pytest availability"),
    
    # Section 24.2 - Installation verification
    ("24.2", ["python3", "-c", "import json; print('JSON module OK')"], 0, "JSON module availability"),
    ("24.2", ["python3", "-c", "import pathlib; print('Pathlib module OK')"], 0, "Pathlib module availability"),
    
    # Section 21 - Troubleshooting (diagnostic commands)
    ("21", ["python3", "-c", "import os; print(f'CWD: {os.getcwd()}')"], 0, "Working directory check"),
]


def run_command(cmd: List[str], timeout: int = 10) -> Tuple[int, str, str]:
    """
    Run a command and return exit code, stdout, stderr.
    
    Args:
        cmd: Command to run as list of strings
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent.parent
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return -2, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -3, "", f"Error running command: {str(e)}"


def test_commands(section_filter: str = None, verbose: bool = False) -> Dict[str, int]:
    """
    Test runbook commands and return statistics.
    
    Args:
        section_filter: Only test commands from this section (e.g., "24", "21")
        verbose: Print detailed output
        
    Returns:
        Dictionary with test statistics
    """
    stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    failed_tests = []
    
    print("=" * 80)
    print("Testing Unified Technical Runbook Commands (v3.0.0)")
    print("=" * 80)
    print()
    
    for section, cmd, expected_code, description in RUNBOOK_COMMANDS:
        # Skip if section filter doesn't match
        if section_filter and not section.startswith(section_filter):
            stats["skipped"] += 1
            continue
            
        stats["total"] += 1
        
        # Run command
        if verbose:
            print(f"Testing [{section}] {description}")
            print(f"  Command: {' '.join(cmd)}")
        else:
            print(f"[{section}] {description}...", end=" ")
            
        exit_code, stdout, stderr = run_command(cmd)
        
        # Check result
        if exit_code == expected_code:
            stats["passed"] += 1
            if verbose:
                print(f"  ✅ PASSED (exit code: {exit_code})")
                if stdout.strip():
                    print(f"  Output: {stdout.strip()}")
            else:
                print("✅ PASSED")
        else:
            stats["failed"] += 1
            failed_tests.append((section, description, cmd, exit_code, expected_code, stderr))
            if verbose:
                print(f"  ❌ FAILED (exit code: {exit_code}, expected: {expected_code})")
                if stderr.strip():
                    print(f"  Error: {stderr.strip()}")
            else:
                print(f"❌ FAILED (exit code: {exit_code})")
        
        if verbose:
            print()
    
    # Print summary
    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Total:   {stats['total']}")
    print(f"Passed:  {stats['passed']} ✅")
    print(f"Failed:  {stats['failed']} ❌")
    print(f"Skipped: {stats['skipped']}")
    print()
    
    # Print failed tests
    if failed_tests:
        print("Failed Tests:")
        print("-" * 80)
        for section, desc, cmd, exit_code, expected, stderr in failed_tests:
            print(f"[{section}] {desc}")
            print(f"  Command: {' '.join(cmd)}")
            print(f"  Exit code: {exit_code} (expected: {expected})")
            if stderr.strip():
                print(f"  Error: {stderr.strip()}")
            print()
    
    return stats


def main():
    """Main entry point."""
    # Parse simple command line arguments
    section_filter = None
    verbose = False
    
    for arg in sys.argv[1:]:
        if arg == "--verbose" or arg == "-v":
            verbose = True
        elif arg == "--help" or arg == "-h":
            print(__doc__)
            return 0
        elif arg.startswith("--section="):
            section_filter = arg.split("=")[1]
        elif not arg.startswith("-"):
            section_filter = arg
    
    # Run tests
    stats = test_commands(section_filter=section_filter, verbose=verbose)
    
    # Exit with appropriate code
    if stats["failed"] > 0:
        print(f"❌ Tests failed: {stats['failed']}/{stats['total']}")
        return 1
    elif stats["total"] == 0:
        print("⚠️  No tests were run")
        return 2
    else:
        print(f"✅ All tests passed: {stats['passed']}/{stats['total']}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
