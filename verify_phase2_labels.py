#!/usr/bin/env python3
"""Phase 2 Label Verifier - Deterministic File Placement Rule Enforcement.

This script verifies that all Python files in src/farfan_pipeline/phases/Phase_two/
declare a Phase 2 label in their module header docstring metadata block.

RULES:
1. Every .py file in Phase_two/ must have a module docstring
2. The docstring must contain "PHASE_LABEL: Phase 2" on its own line
3. The label must appear within the first 20 lines of the file
4. Violation detection is fail-fast: stop after N failures (configurable)
5. Output is a JSON report with SHA-256 hash for audit trail

RATIONALE:
Files in Phase_two/ directory may describe logic for later "phase numbers"
(e.g., phase6_validation.py describes Phase 6 validation logic but lives in Phase 2
because it's part of Phase 2's task construction orchestration). The PHASE_LABEL
metadata makes this explicit and machine-checkable.

USAGE:
    python verify_phase2_labels.py
    python verify_phase2_labels.py --max-failures 5
    python verify_phase2_labels.py --output-report phase2_verification.json

EXIT CODES:
    0: All files compliant
    1: Violations detected
    2: Execution error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE_TWO_DIR = Path(__file__).parent / "src" / "farfan_pipeline" / "phases" / "Phase_two"
REQUIRED_LABEL = "PHASE_LABEL: Phase 2"
MAX_LINES_TO_SCAN = 20
DEFAULT_MAX_FAILURES = 10


@dataclass
class Violation:
    """Represents a Phase 2 label violation.
    
    Attributes:
        file_path: Relative path to the violating file
        violation_type: Type of violation (MISSING_DOCSTRING, MISSING_LABEL, etc.)
        line_number: Line number where violation detected (0 if N/A)
        details: Human-readable explanation
    """
    file_path: str
    violation_type: str
    line_number: int
    details: str
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "violation_type": self.violation_type,
            "line_number": self.line_number,
            "details": self.details,
        }


@dataclass
class VerificationReport:
    """Verification report with violations and metadata.
    
    Attributes:
        timestamp: ISO 8601 timestamp of verification
        phase_two_dir: Absolute path to Phase_two directory
        files_scanned: Total number of .py files scanned
        files_compliant: Number of compliant files
        files_violated: Number of files with violations
        violations: List of detected violations
        sha256_hash: SHA-256 hash of report for audit trail
        termination_reason: Reason for termination (all_scanned, max_failures, error)
    """
    timestamp: str
    phase_two_dir: str
    files_scanned: int
    files_compliant: int
    files_violated: int
    violations: list[Violation] = field(default_factory=list)
    sha256_hash: str = ""
    termination_reason: str = "all_scanned"
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash of report (excluding hash field itself)."""
        report_dict = self.to_dict()
        report_dict.pop("sha256_hash", None)
        report_json = json.dumps(report_dict, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(report_json.encode("utf-8")).hexdigest()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "phase_two_dir": self.phase_two_dir,
            "files_scanned": self.files_scanned,
            "files_compliant": self.files_compliant,
            "files_violated": self.files_violated,
            "violations": [v.to_dict() for v in self.violations],
            "sha256_hash": self.sha256_hash,
            "termination_reason": self.termination_reason,
        }


def check_file_for_phase2_label(file_path: Path, phase_two_dir: Path, max_lines: int = MAX_LINES_TO_SCAN) -> Violation | None:
    """Check if a Python file has the required Phase 2 label in its docstring.
    
    Args:
        file_path: Path to the Python file to check
        phase_two_dir: Base Phase_two directory for relative path calculation
        max_lines: Maximum number of lines to scan for the label
    
    Returns:
        Violation object if label is missing/invalid, None if compliant
        
    Detection Strategy:
        1. Check if file has a module docstring (starts with triple quotes)
        2. Scan first max_lines for "PHASE_LABEL: Phase 2"
        3. Return violation if docstring missing or label not found
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [f.readline() for _ in range(max_lines)]
    except Exception as e:
        return Violation(
            file_path=str(file_path.relative_to(phase_two_dir.parent.parent.parent)),
            violation_type="READ_ERROR",
            line_number=0,
            details=f"Failed to read file: {e}",
        )
    
    # Check if file starts with docstring
    first_line = lines[0].strip() if lines else ""
    if not first_line.startswith('"""') and not first_line.startswith("'''"):
        return Violation(
            file_path=str(file_path.relative_to(phase_two_dir.parent.parent.parent)),
            violation_type="MISSING_DOCSTRING",
            line_number=1,
            details="File does not start with a module docstring (triple quotes)",
        )
    
    # Scan for PHASE_LABEL
    for idx, line in enumerate(lines, start=1):
        if REQUIRED_LABEL in line:
            return None  # Compliant
    
    # Label not found
    return Violation(
        file_path=str(file_path.relative_to(phase_two_dir.parent.parent.parent)),
        violation_type="MISSING_LABEL",
        line_number=0,
        details=f"'{REQUIRED_LABEL}' not found in first {max_lines} lines of docstring",
    )


def verify_phase2_labels(
    phase_two_dir: Path,
    max_failures: int = DEFAULT_MAX_FAILURES,
) -> VerificationReport:
    """Verify Phase 2 labels for all Python files in Phase_two directory.
    
    Args:
        phase_two_dir: Path to Phase_two directory
        max_failures: Maximum number of failures before terminating
    
    Returns:
        VerificationReport with violations and metadata
        
    Termination:
        - Stops after max_failures violations detected (fail-fast)
        - Returns report with all violations found up to that point
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    
    if not phase_two_dir.exists():
        return VerificationReport(
            timestamp=timestamp,
            phase_two_dir=str(phase_two_dir),
            files_scanned=0,
            files_compliant=0,
            files_violated=0,
            violations=[
                Violation(
                    file_path=str(phase_two_dir),
                    violation_type="DIRECTORY_NOT_FOUND",
                    line_number=0,
                    details=f"Phase_two directory not found: {phase_two_dir}",
                )
            ],
            termination_reason="error",
        )
    
    violations: list[Violation] = []
    files_scanned = 0
    files_compliant = 0
    files_violated = 0
    termination_reason = "all_scanned"
    
    # Find all .py files in Phase_two directory (non-recursive, excluding __pycache__)
    py_files = sorted(
        f for f in phase_two_dir.glob("*.py")
        if f.is_file() and not f.name.startswith(".")
    )
    
    for py_file in py_files:
        files_scanned += 1
        violation = check_file_for_phase2_label(py_file, phase_two_dir)
        
        if violation:
            violations.append(violation)
            files_violated += 1
            
            # Fail-fast termination
            if len(violations) >= max_failures:
                termination_reason = "max_failures"
                break
        else:
            files_compliant += 1
    
    report = VerificationReport(
        timestamp=timestamp,
        phase_two_dir=str(phase_two_dir.absolute()),
        files_scanned=files_scanned,
        files_compliant=files_compliant,
        files_violated=files_violated,
        violations=violations,
        termination_reason=termination_reason,
    )
    
    # Compute SHA-256 hash for audit trail
    report.sha256_hash = report.compute_hash()
    
    return report


def main() -> int:
    """Main entry point for Phase 2 label verifier.
    
    Returns:
        Exit code (0=compliant, 1=violations, 2=error)
    """
    parser = argparse.ArgumentParser(
        description="Verify Phase 2 labels in Phase_two directory files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--phase-two-dir",
        type=Path,
        default=PHASE_TWO_DIR,
        help=f"Path to Phase_two directory (default: {PHASE_TWO_DIR})",
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=DEFAULT_MAX_FAILURES,
        help=f"Maximum failures before terminating (default: {DEFAULT_MAX_FAILURES})",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        help="Path to output JSON report (default: stdout)",
    )
    
    args = parser.parse_args()
    
    try:
        report = verify_phase2_labels(
            phase_two_dir=args.phase_two_dir,
            max_failures=args.max_failures,
        )
        
        # Output report
        report_json = json.dumps(report.to_dict(), indent=2, sort_keys=False)
        
        if args.output_report:
            args.output_report.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output_report, "w", encoding="utf-8") as f:
                f.write(report_json)
            print(f"Report written to: {args.output_report}")
        else:
            print(report_json)
        
        # Print SHA-256 to stderr for audit
        print(f"\nSHA-256: {report.sha256_hash}", file=sys.stderr)
        
        # Print summary
        print(f"\nVerification Summary:", file=sys.stderr)
        print(f"  Files scanned: {report.files_scanned}", file=sys.stderr)
        print(f"  Compliant: {report.files_compliant}", file=sys.stderr)
        print(f"  Violated: {report.files_violated}", file=sys.stderr)
        print(f"  Termination: {report.termination_reason}", file=sys.stderr)
        
        # Exit with appropriate code
        if report.files_violated > 0:
            print("\n❌ VIOLATIONS DETECTED", file=sys.stderr)
            return 1
        else:
            print("\n✅ ALL FILES COMPLIANT", file=sys.stderr)
            return 0
            
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
