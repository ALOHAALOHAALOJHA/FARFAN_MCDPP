"""Test Phase 1 Naming Conventions and Purge Verification.

This test verifies:
- NR-01 through NR-08: Naming rule compliance
- Purge verification: No phase1 files outside canonical path
- Import path correctness
"""

import pytest
from pathlib import Path
import subprocess


class TestNamingConventions:
    """Test Phase 1 naming convention enforcement."""

    def test_canonical_path_exists(self):
        """Verify canonical path exists."""
        canonical_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
        )
        assert canonical_path.exists(), f"Canonical path must exist: {canonical_path}"
        assert canonical_path.is_dir(), f"Canonical path must be a directory"

    def test_no_spaces_in_filenames(self):
        """NR-04: No spaces in filenames."""
        canonical_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
        )

        for file_path in canonical_path.rglob("*"):
            if file_path.is_file():
                assert " " not in file_path.name, f"NR-04 violation: File has spaces: {file_path}"

    def test_explicit_extensions(self):
        """NR-05: All files must have explicit extensions."""
        canonical_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
        )

        for file_path in canonical_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                assert (
                    "." in file_path.name
                ), f"NR-05 violation: File missing extension: {file_path}"

    def test_phase1_prefix_compliance(self):
        """NR-03: Phase-specific files must have phase1_ prefix."""
        canonical_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
        )

        phase_specific_files = [
            "phase1_20_00_cpp_ingestion.py",
            "phase1_40_00_circuit_breaker.py",
            "phase1_50_00_dependency_validator.py",
            "phase1_10_00_models.py",
        ]

        for filename in phase_specific_files:
            file_path = canonical_path / filename
            assert file_path.exists(), f"NR-03: Phase-specific file must exist: {filename}"
            assert filename.startswith(
                "phase1_"
            ), f"NR-03 violation: File must have phase1_ prefix: {filename}"

    def test_snake_case_compliance(self):
        """NR-02: Python files must use snake_case."""
        canonical_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
        )

        for file_path in canonical_path.rglob("*.py"):
            filename = file_path.name
            # Check for snake_case (no uppercase, only alphanumeric and underscores)
            if filename != "__init__.py":
                assert (
                    filename.islower() or "_" in filename
                ), f"NR-02 violation: Not snake_case: {filename}"
                assert not any(
                    c.isupper() for c in filename
                ), f"NR-02 violation: Contains uppercase: {filename}"


class TestPurgeVerification:
    """Test Phase 1 purge: no files outside canonical path."""

    def test_no_legacy_phase_one_folder(self):
        """Verify legacy Phase_one folder deleted."""
        legacy_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_one"
        )
        assert not legacy_path.exists(), f"Legacy Phase_one folder must be deleted: {legacy_path}"

    def test_no_phase1_in_root(self):
        """Verify no Phase 1 scripts/files in repository root (except error manifests)."""
        root_path = Path(__file__).resolve().parent.parent.parent

        forbidden_root_files = [
            "implement_phase1_subgroup_a.py",
            # "phase1_error_manifest.json",  # May exist during error handling
            "requirements-phase1.txt",
            "PHASE_1_COMPREHENSIVE_AUDIT.md",
            "PHASE1_WIRING_DOCUMENTATION.md",
            "CANONICAL_REFACTORING_PHASE1_COMPLETE.md",
        ]

        for filename in forbidden_root_files:
            file_path = root_path / filename
            assert not file_path.exists(), f"Forbidden root file must be deleted: {filename}"

    def test_purge_command_verification(self):
        """Run purge verification command."""
        root_path = Path(__file__).resolve().parent.parent.parent

        # Find all phase1-related files outside canonical path
        result = subprocess.run(
            [
                "find",
                ".",
                "(",
                "-name",
                "*phase1*",
                "-o",
                "-name",
                "*Phase_one*",
                "-o",
                "-name",
                "*phase_one*",
                ")",
                "!",
                "-path",
                "*/Phase_1/*",
                "!",
                "-path",
                "*/__pycache__/*",
                "!",
                "-path",
                "*/.git/*",
                "!",
                "-path",
                "*/tests/*",  # Tests are allowed
                "!",
                "-path",
                "*/backups/*",  # Backups are allowed
                "!",
                "-path",
                "*/scripts/*",  # Scripts are allowed
                "!",
                "-path",
                "*/validators/*",  # Validators are allowed
                "!",
                "-name",
                "generate_phase1_ria.py",  # This script is allowed
                "!",
                "-name",
                "phase1_error_manifest.json",  # Error manifests are allowed
            ],
            cwd=root_path,
            capture_output=True,
            text=True,
        )

        # Filter out test files and legitimate scripts
        lines = [l for l in result.stdout.strip().split("\n") if l and not l.startswith("./tests/")]
        # Also filter backups, scripts and validators
        lines = [l for l in lines if l and not l.startswith("./backups/")]
        lines = [l for l in lines if l and not l.startswith("./scripts/")]
        lines = [l for l in lines if l and "validators" not in l]
        forbidden_files = [l for l in lines if l and "generate_phase1_ria.py" not in l and "phase1_error_manifest.json" not in l]

        assert (
            len(forbidden_files) == 0
        ), f"Found phase1 files outside canonical path: {forbidden_files}"


class TestImportPaths:
    """Test correct import paths."""

    def test_canonical_path_exists(self):
        """Verify canonical path exists and is importable."""
        canonical_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
        )
        assert canonical_path.exists(), f"Canonical path must exist: {canonical_path}"

        # Check __init__.py exists
        init_file = canonical_path / "__init__.py"
        assert init_file.exists(), "__init__.py must exist for package"

        # Verify it exports the main function
        content = init_file.read_text()
        assert (
            "Phase1Executor" in content
        ), "Must export Phase1Executor"

    def test_legacy_path_deleted(self):
        """Verify legacy Phase_one path is deleted."""
        legacy_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_one"
        )
        assert not legacy_path.exists(), f"Legacy Phase_one folder must be deleted: {legacy_path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
