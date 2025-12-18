"""
Tests for naming convention validation.

These tests validate the naming convention enforcement system
for Phase 2 stabilization.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from scripts.validate_naming_conventions import (
    NAMING_RULES,
    validate_file_name,
    validate_naming_conventions,
    NamingViolation,
)


class TestNamingRules:
    """Test naming rule pattern matching."""

    def test_phase2_root_files_valid(self):
        """Test valid Phase 2 root file names."""
        rule = NAMING_RULES["phase2_root_files"]
        
        valid_names = [
            "phase2_a_arg_router.py",
            "phase2_b_carver.py",
            "phase2_c_evidence_nexus.py",
            "phase2_z_test_module.py",
        ]
        
        for name in valid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is None, f"{name} should be valid"

    def test_phase2_root_files_invalid(self):
        """Test invalid Phase 2 root file names."""
        rule = NAMING_RULES["phase2_root_files"]
        
        invalid_names = [
            "arg_router.py",  # Missing phase2_ prefix
            "Phase2Router.py",  # Wrong case
            "phase2-router.py",  # Hyphen instead of underscore
            "phase2_Router.py",  # Capital letter after phase2_
            "phase2_a.py",  # Too short
            "phase2_a_.py",  # Trailing underscore
            "phase2_1_router.py",  # Digit as letter identifier
        ]
        
        for name in invalid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is not None, f"{name} should be invalid"

    def test_package_internal_files_valid(self):
        """Test valid package-internal file names."""
        rule = NAMING_RULES["package_internal_files"]
        
        valid_names = [
            "base_executor.py",
            "executor_config.py",
            "phase2_routing.py",
            "a.py",
            "abc123.py",
        ]
        
        for name in valid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is None, f"{name} should be valid"

    def test_package_internal_files_invalid(self):
        """Test invalid package-internal file names."""
        rule = NAMING_RULES["package_internal_files"]
        
        invalid_names = [
            "BaseExecutor.py",  # Capital letter
            "executor-config.py",  # Hyphen
            "1executor.py",  # Starts with digit
            "_private.py",  # Starts with underscore
        ]
        
        for name in invalid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is not None, f"{name} should be invalid"

    def test_schema_files_valid(self):
        """Test valid schema file names."""
        rule = NAMING_RULES["schema_files"]
        
        valid_names = [
            "executor_config.schema.json",
            "validation.schema.json",
            "a.schema.json",
        ]
        
        for name in valid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is None, f"{name} should be valid"

    def test_schema_files_invalid(self):
        """Test invalid schema file names."""
        rule = NAMING_RULES["schema_files"]
        
        invalid_names = [
            "executor_config.json",  # Missing .schema
            "ExecutorConfig.schema.json",  # Capital letter
            "executor-config.schema.json",  # Hyphen
            "log_schema.json",  # Missing .schema. in middle
        ]
        
        for name in invalid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is not None, f"{name} should be invalid"

    def test_certificate_files_valid(self):
        """Test valid certificate file names."""
        rule = NAMING_RULES["certificate_files"]
        
        valid_names = [
            "CERTIFICATE_01_ROUTING.md",
            "CERTIFICATE_99_ORCHESTRATOR_TRANSCRIPT.md",
            "CERTIFICATE_15_TEST_123.md",
        ]
        
        for name in valid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is None, f"{name} should be valid"

    def test_certificate_files_invalid(self):
        """Test invalid certificate file names."""
        rule = NAMING_RULES["certificate_files"]
        
        invalid_names = [
            "certificate_01.md",  # Wrong case
            "CERT_01.md",  # Wrong prefix
            "CERTIFICATE_P3_01.md",  # Letters in number field
            "CERTIFICATE_1_TEST.md",  # Single digit
            "CERTIFICATE_001_TEST.md",  # Three digits
            "CERTIFICATE_01_test.md",  # Lowercase in name
        ]
        
        for name in invalid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is not None, f"{name} should be invalid"

    def test_test_files_valid(self):
        """Test valid test file names."""
        rule = NAMING_RULES["test_files"]
        
        valid_names = [
            "test_phase2_carver.py",
            "test_phase2_execution_logic.py",
            "test_phase2_a_b_c.py",
            "test_phase2_123.py",
        ]
        
        for name in valid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is None, f"{name} should be valid"

    def test_test_files_invalid(self):
        """Test invalid test file names."""
        rule = NAMING_RULES["test_files"]
        
        invalid_names = [
            "test_carver.py",  # Missing phase2_
            "phase2_test_carver.py",  # Wrong prefix order
            "test_Phase2_carver.py",  # Capital P
            "test_phase2.py",  # Too short
        ]
        
        for name in invalid_names:
            path = Path(name)
            violation = validate_file_name(path, rule)
            assert violation is not None, f"{name} should be invalid"


class TestNamingConventionValidation:
    """Test full validation workflow."""

    def test_empty_directory(self):
        """Test validation with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            violations = validate_naming_conventions(repo_root)
            assert len(violations) == 0

    def test_valid_phase2_structure(self):
        """Test validation with valid Phase 2 structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            phase2_dir = repo_root / "src" / "farfan_pipeline" / "phases" / "Phase_two"
            phase2_dir.mkdir(parents=True)
            
            # Create valid files
            (phase2_dir / "__init__.py").touch()
            (phase2_dir / "phase2_a_router.py").touch()
            (phase2_dir / "phase2_b_carver.py").touch()
            
            violations = validate_naming_conventions(repo_root)
            assert len(violations) == 0

    def test_invalid_phase2_files(self):
        """Test validation detects invalid Phase 2 files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            phase2_dir = repo_root / "src" / "farfan_pipeline" / "phases" / "Phase_two"
            phase2_dir.mkdir(parents=True)
            
            # Create invalid files
            (phase2_dir / "arg_router.py").touch()  # Missing phase2_ prefix
            (phase2_dir / "BaseExecutor.py").touch()  # Wrong case
            
            violations = validate_naming_conventions(repo_root)
            assert len(violations) == 2

    def test_exemption_system(self):
        """Test that exemption system filters violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            phase2_dir = repo_root / "src" / "farfan_pipeline" / "phases" / "Phase_two"
            phase2_dir.mkdir(parents=True)
            
            # Create invalid file
            invalid_file = phase2_dir / "arg_router.py"
            invalid_file.touch()
            
            # Create exemption file
            exemption_file = repo_root / ".naming_exemptions"
            exemption_file.write_text(
                "src/farfan_pipeline/phases/Phase_two/arg_router.py\n"
            )
            
            # Load exemptions
            from scripts.validate_naming_conventions import (
                load_legacy_exemptions,
                filter_legacy_violations,
            )
            
            violations = validate_naming_conventions(repo_root)
            exemptions = load_legacy_exemptions(repo_root)
            filtered = filter_legacy_violations(violations, exemptions, repo_root)
            
            assert len(violations) == 1  # Original violation
            assert len(filtered) == 0  # Filtered out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
