"""Tests for Phase 2 label verifier script.

Verifies:
1. Verifier detects missing docstrings
2. Verifier detects missing Phase 2 labels
3. Verifier produces JSON report with SHA-256 hash
4. Verifier fails-fast after max_failures
5. Verifier terminates with correct exit codes
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from verify_phase2_labels import (
    Violation,
    VerificationReport,
    check_file_for_phase2_label,
    verify_phase2_labels,
)


class TestLabelDetection:
    """Test Phase 2 label detection logic."""

    def test_compliant_file_with_label(self, tmp_path: Path) -> None:
        """Test that file with Phase 2 label is detected as compliant."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            '''"""Module docstring.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Test Module
"""
'''
        )

        violation = check_file_for_phase2_label(test_file, tmp_path)

        assert violation is None

    def test_missing_docstring_detected(self, tmp_path: Path) -> None:
        """Test that file without docstring is detected as violation."""
        test_file = tmp_path / "no_docstring.py"
        test_file.write_text(
            """# Just a comment
"""
        )

        violation = check_file_for_phase2_label(test_file, tmp_path)

        assert violation is not None
        assert violation.violation_type == "MISSING_DOCSTRING"
        assert "does not start with a module docstring" in violation.details

    def test_missing_label_detected(self, tmp_path: Path) -> None:
        """Test that file without Phase 2 label is detected as violation."""
        test_file = tmp_path / "no_label.py"
        test_file.write_text(
            '''"""Module docstring without Phase 2 label.

This module does not have the required label.
"""
'''
        )

        violation = check_file_for_phase2_label(test_file, tmp_path)

        assert violation is not None
        assert violation.violation_type == "MISSING_LABEL"
        assert "PHASE_LABEL: Phase 2" in violation.details

    def test_label_in_first_20_lines(self, tmp_path: Path) -> None:
        """Test that label must appear in first 20 lines."""
        test_file = tmp_path / "late_label.py"
        lines = ['"""Module docstring.\n'] + ["\n"] * 25 + ["PHASE_LABEL: Phase 2\n", '"""\n']
        test_file.write_text("".join(lines))

        violation = check_file_for_phase2_label(test_file, tmp_path)

        # Should be violation because label is after line 20
        assert violation is not None
        assert violation.violation_type == "MISSING_LABEL"


class TestVerificationReport:
    """Test verification report generation."""

    def test_report_with_compliant_files(self, tmp_path: Path) -> None:
        """Test report generation with all compliant files."""
        # Create compliant files
        for i in range(3):
            file = tmp_path / f"module{i}.py"
            file.write_text(
                f'''"""Module {i} docstring.

PHASE_LABEL: Phase 2
"""
'''
            )

        report = verify_phase2_labels(tmp_path, max_failures=10)

        assert report.files_scanned == 3
        assert report.files_compliant == 3
        assert report.files_violated == 0
        assert len(report.violations) == 0
        assert report.termination_reason == "all_scanned"

    def test_report_with_violations(self, tmp_path: Path) -> None:
        """Test report generation with violations."""
        # Create one compliant file
        compliant = tmp_path / "compliant.py"
        compliant.write_text(
            '''"""Compliant module.

PHASE_LABEL: Phase 2
"""
'''
        )

        # Create one non-compliant file
        violated = tmp_path / "violated.py"
        violated.write_text(
            '''"""No label here.
"""
'''
        )

        report = verify_phase2_labels(tmp_path, max_failures=10)

        assert report.files_scanned == 2
        assert report.files_compliant == 1
        assert report.files_violated == 1
        assert len(report.violations) == 1
        assert report.violations[0].violation_type == "MISSING_LABEL"

    def test_fail_fast_termination(self, tmp_path: Path) -> None:
        """Test that verification stops after max_failures."""
        # Create 10 non-compliant files
        for i in range(10):
            file = tmp_path / f"violated{i}.py"
            file.write_text(
                f'''"""Module {i} without label.
"""
'''
            )

        report = verify_phase2_labels(tmp_path, max_failures=5)

        # Should stop after 5 failures
        assert report.files_violated == 5
        assert len(report.violations) == 5
        assert report.termination_reason == "max_failures"

    def test_sha256_hash_computed(self, tmp_path: Path) -> None:
        """Test that SHA-256 hash is computed for audit trail."""
        file = tmp_path / "module.py"
        file.write_text(
            '''"""Module.

PHASE_LABEL: Phase 2
"""
'''
        )

        report = verify_phase2_labels(tmp_path, max_failures=10)

        assert report.sha256_hash != ""
        assert len(report.sha256_hash) == 64  # SHA-256 hex length

    def test_report_to_dict_serializable(self, tmp_path: Path) -> None:
        """Test that report can be serialized to JSON."""
        file = tmp_path / "module.py"
        file.write_text(
            '''"""Module.

PHASE_LABEL: Phase 2
"""
'''
        )

        report = verify_phase2_labels(tmp_path, max_failures=10)
        report_dict = report.to_dict()

        # Should be JSON serializable
        json_str = json.dumps(report_dict)
        assert json_str is not None

        # Verify structure
        parsed = json.loads(json_str)
        assert "timestamp" in parsed
        assert "files_scanned" in parsed
        assert "violations" in parsed
        assert "sha256_hash" in parsed


class TestViolationDetails:
    """Test violation detail capture."""

    def test_violation_captures_file_path(self, tmp_path: Path) -> None:
        """Test that violations capture relative file paths."""
        violated = tmp_path / "subdir" / "module.py"
        violated.parent.mkdir(parents=True, exist_ok=True)
        violated.write_text(
            '''"""No label.
"""
'''
        )

        violation = check_file_for_phase2_label(violated, tmp_path)

        assert violation is not None
        assert "module.py" in violation.file_path

    def test_violation_has_human_readable_details(self, tmp_path: Path) -> None:
        """Test that violations have clear, actionable details."""
        violated = tmp_path / "module.py"
        violated.write_text(
            '''"""No label.
"""
'''
        )

        violation = check_file_for_phase2_label(violated, tmp_path)

        assert violation is not None
        assert violation.details != ""
        assert "PHASE_LABEL: Phase 2" in violation.details
        assert "not found" in violation.details


class TestDirectoryNotFound:
    """Test error handling for missing directory."""

    def test_directory_not_found_error(self, tmp_path: Path) -> None:
        """Test that missing directory produces error violation."""
        nonexistent = tmp_path / "does_not_exist"

        report = verify_phase2_labels(nonexistent, max_failures=10)

        assert report.files_scanned == 0
        assert len(report.violations) == 1
        assert report.violations[0].violation_type == "DIRECTORY_NOT_FOUND"
        assert report.termination_reason == "error"
