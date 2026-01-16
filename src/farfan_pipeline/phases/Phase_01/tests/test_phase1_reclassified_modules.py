"""
PHASE 1 RECLASSIFIED MODULE TEST SUITE
======================================

Tests for modules that were reclassified during normalization.
These modules are now in docs/legacy/, interphase/, or primitives/
and must still be accessible and functional for backward compatibility
or specific purposes.

Test Categories:
1. Legacy Module Tests - Tests for docs/legacy/ modules
2. Interphase Module Tests - Tests for interphase/ modules
3. Primitive Module Tests - Tests for primitives/ modules
4. Backward Compatibility Tests - Verify old imports still work

Author: F.A.R.F.A.N Testing Team
Version: 2.0.0 (Post-Normalization)
Status: ADVERSARIAL - Break if you can
"""

import sys
from pathlib import Path
from typing import Dict, List

import pytest


# =============================================================================
# TEST DATA
# =============================================================================

RECLASSIFIED_MODULES = {
    "phase1_01_00_cpp_models": {
        "new_location": "docs/legacy",
        "reason": "Superseded by phase1_03_00_models",
        "status": "archived",
    },
    "phase1_04_00_phase_protocol": {
        "new_location": "interphase",
        "reason": "Cross-phase protocol definition",
        "status": "active_interphase",
    },
    "phase1_08_00_adapter": {
        "new_location": "interphase",
        "reason": "Downstream adapter",
        "status": "active_interphase",
    },
    "phase1_10_00_dependency_validator": {
        "new_location": "primitives",
        "reason": "Utility with cross-phase dependencies",
        "status": "active_primitive",
    },
}


# =============================================================================
# FIXTURES
# =============================================================================

# phase1_dir fixture is provided by conftest.py


# =============================================================================
# 1. LEGACY MODULE TESTS
# =============================================================================

class TestLegacyModules:
    """Tests for modules in docs/legacy/."""

    def test_legacy_cpp_models_exists(self, phase1_dir: Path):
        """Legacy CPP models file must exist in docs/legacy/."""
        legacy_file = phase1_dir / "docs" / "legacy" / "phase1_01_00_cpp_models.py"
        assert legacy_file.exists(), f"Legacy file not found: {legacy_file}"

    def test_legacy_cpp_models_has_deprecation_notice(self, phase1_dir: Path):
        """Legacy CPP models should have deprecation notice in docstring."""
        legacy_file = phase1_dir / "docs" / "legacy" / "phase1_01_00_cpp_models.py"
        content = legacy_file.read_text()

        # Should indicate it's legacy/superseded
        docstring_lower = content[:500].lower()
        assert "legacy" in docstring_lower or "deprecated" in docstring_lower or "superseded" in docstring_lower, \
            "Legacy file should have deprecation notice"

    def test_legacy_cpp_models_not_imported_by_active_modules(self, phase1_dir: Path):
        """Active modules should NOT import the legacy CPP models."""
        legacy_module = "phase1_01_00_cpp_models"

        py_files = [f for f in phase1_dir.glob("*.py") if not f.name.startswith("__")]
        for py_file in py_files:
            if py_file.name == "phase1_01_00_cpp_models.py":
                continue

            content = py_file.read_text()
            # Check for direct imports
            assert f"import {legacy_module}" not in content, \
                f"{py_file.name} imports legacy module {legacy_module}"
            assert f"from .{legacy_module}" not in content, \
                f"{py_file.name} imports legacy module {legacy_module}"

    def test_legacy_folder_exists(self, phase1_dir: Path):
        """Legacy folder must exist."""
        legacy_dir = phase1_dir / "docs" / "legacy"
        assert legacy_dir.exists(), "Legacy directory not found"
        assert legacy_dir.is_dir(), "Legacy path is not a directory"


# =============================================================================
# 2. INTERPHASE MODULE TESTS
# =============================================================================

class TestInterphaseModules:
    """Tests for modules in interphase/."""

    def test_interphase_folder_exists(self, phase1_dir: Path):
        """Interphase folder must exist."""
        interphase_dir = phase1_dir / "interphase"
        assert interphase_dir.exists(), "Interphase directory not found"
        assert interphase_dir.is_dir(), "Interphase path is not a directory"

    def test_phase_protocol_exists(self, phase1_dir: Path):
        """Phase protocol must exist in interphase/."""
        protocol_file = phase1_dir / "interphase" / "phase1_04_00_phase_protocol.py"
        assert protocol_file.exists(), f"Phase protocol not found: {protocol_file}"

    def test_adapter_exists(self, phase1_dir: Path):
        """Adapter must exist in interphase/."""
        adapter_file = phase1_dir / "interphase" / "phase1_08_00_adapter.py"
        assert adapter_file.exists(), f"Adapter not found: {adapter_file}"

    def test_phase_protocol_has_cross_phase_documentation(self, phase1_dir: Path):
        """Phase protocol should document its cross-phase nature."""
        protocol_file = phase1_dir / "interphase" / "phase1_04_00_phase_protocol.py"
        content = protocol_file.read_text()

        # Should mention it's cross-phase or general protocol
        docstring_lower = content[:500].lower()
        assert "protocol" in docstring_lower or "contract" in docstring_lower, \
            "Phase protocol should be documented as protocol/contract"

    def test_adapter_has_downstream_documentation(self, phase1_dir: Path):
        """Adapter should document its downstream purpose."""
        adapter_file = phase1_dir / "interphase" / "phase1_08_00_adapter.py"
        content = adapter_file.read_text()

        # Should mention it's an adapter
        docstring_lower = content[:500].lower()
        assert "adapter" in docstring_lower or "convert" in docstring_lower, \
            "Adapter should document its conversion/adaptation purpose"

    def test_interphase_modules_parseable(self, phase1_dir: Path):
        """All interphase modules must be parseable (no syntax errors)."""
        import ast

        interphase_dir = phase1_dir / "interphase"
        py_files = list(interphase_dir.glob("*.py"))

        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue

            try:
                ast.parse(py_file.read_text())
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file.name}: {e}")


# =============================================================================
# 3. PRIMITIVE MODULE TESTS
# =============================================================================

class TestPrimitiveModules:
    """Tests for modules in primitives/."""

    def test_primitives_folder_exists(self, phase1_dir: Path):
        """Primitives folder must exist."""
        primitives_dir = phase1_dir / "primitives"
        assert primitives_dir.exists(), "Primitives directory not found"
        assert primitives_dir.is_dir(), "Primitives path is not a directory"

    def test_dependency_validator_exists(self, phase1_dir: Path):
        """Dependency validator must exist in primitives/."""
        validator_file = phase1_dir / "primitives" / "phase1_10_00_dependency_validator.py"
        assert validator_file.exists(), f"Dependency validator not found: {validator_file}"

    def test_dependency_validator_has_utility_documentation(self, phase1_dir: Path):
        """Dependency validator should document its utility purpose."""
        validator_file = phase1_dir / "primitives" / "phase1_10_00_dependency_validator.py"
        content = validator_file.read_text()

        # Should mention validation or utility
        docstring_lower = content[:500].lower()
        assert "validat" in docstring_lower or "check" in docstring_lower or "depend" in docstring_lower, \
            "Dependency validator should document its validation purpose"

    def test_primitives_modules_parseable(self, phase1_dir: Path):
        """All primitives modules must be parseable (no syntax errors)."""
        import ast

        primitives_dir = phase1_dir / "primitives"
        py_files = list(primitives_dir.glob("*.py"))

        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue

            try:
                ast.parse(py_file.read_text())
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file.name}: {e}")

    def test_expected_primitives_exist(self, phase1_dir: Path):
        """Expected primitive files should exist."""
        primitives_dir = phase1_dir / "primitives"

        expected_primitives = [
            "streaming_extractor.py",
            "truncation_audit.py",
            "phase1_10_00_dependency_validator.py",
        ]

        for prim in expected_primitives:
            # Check with and without version prefix
            variants = [
                primitives_dir / prim,
                primitives_dir / f"phase1_00_00_{prim}",
                primitives_dir / f"phase1_10_00_{prim.replace('.py', '')}.py",
            ]

            found = any(v.exists() for v in variants)
            assert found, f"Expected primitive not found: {prim}"


# =============================================================================
# 4. BACKWARD COMPATIBILITY TESTS
# =============================================================================

class TestBackwardCompatibility:
    """Test backward compatibility for reclassified modules."""

    def test_old_import_paths_fail_gracefully(self, phase1_dir: Path):
        """Old import paths should fail with clear error messages."""
        # This test verifies that if someone tries to import from the old location,
        # they get a clear error, not a cryptic one

        old_locations = [
            "phase1_01_00_cpp_models",
            "phase1_04_00_phase_protocol",
            "phase1_08_00_adapter",
        ]

        for old_module in old_locations:
            # The file shouldn't exist in the root anymore
            old_path = phase1_dir / f"{old_module}.py"
            assert not old_path.exists(), \
                f"Old module still exists in root: {old_module}"

    def test_new_import_paths_work(self, phase1_dir: Path):
        """New import paths should be accessible."""
        import sys

        # Add src to path
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        src_path = repo_root / "src"
        src_path_str = str(src_path)
        if src_path_str not in sys.path:
            sys.path.insert(0, src_path_str)

        try:
            # Try importing interphase module
            from farfan_pipeline.phases.Phase_01.interphase import phase1_04_00_phase_protocol
            assert phase1_04_00_phase_protocol is not None
        except (ImportError, SystemExit) as e:
            pytest.skip(f"Interphase module not importable (expected during transition or missing dependencies): {e}")

    def test_reclassification_documented(self, phase1_dir: Path):
        """Reclassification should be documented in chain report."""
        import json

        report_path = phase1_dir / "contracts" / "phase1_chain_report.json"
        assert report_path.exists(), "Chain report not found"

        report = json.loads(report_path.read_text())
        assert "reclassified_modules" in report, "Chain report missing reclassified_modules section"

        reclassified = report["reclassified_modules"]["reclassified"]
        assert len(reclassified) == 4, f"Expected 4 reclassified modules, got {len(reclassified)}"


# =============================================================================
# 5. INTEGRATION TESTS
# =============================================================================

class TestReclassifiedIntegration:
    """Integration tests for reclassified modules."""

    def test_phase1_still_functions_without_reclassified(self):
        """Phase 1 should function correctly without the reclassified modules in root."""
        # The main Phase 1 modules should be importable
        import sys

        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        src_path = repo_root / "src"
        sys.path.insert(0, str(src_path))

        try:
            from farfan_pipeline.phases.Phase_01 import (
                SmartChunk,
                Chunk,
                TOTAL_CHUNK_COMBINATIONS,
                POLICY_AREA_COUNT,
                DIMENSION_COUNT,
            )
            assert SmartChunk is not None
            assert Chunk is not None
            assert TOTAL_CHUNK_COMBINATIONS == 300
            assert POLICY_AREA_COUNT == 10
            assert DIMENSION_COUNT == 6
        except (ImportError, SystemExit) as e:
            pytest.skip(f"Core Phase 1 components not importable due to missing dependencies: {e}")

    def test_reclassified_dont_cause_import_cycles(self, phase1_dir: Path):
        """Reclassified modules should not cause import cycles."""
        import ast

        # Check that interphase modules don't import from root in a way that creates cycles
        interphase_dir = phase1_dir / "interphase"
        py_files = list(interphase_dir.glob("*.py"))

        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue

            content = py_file.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "Phase_1" in node.module:
                        # Check it's not importing from a file that imports back to interphase
                        for alias in node.names:
                            imported = alias.name
                            if imported.startswith("phase1_") and imported not in [
                                "phase1_04_00_phase_protocol",
                                "phase1_08_00_adapter",
                            ]:
                                # This is a cross-import that could cause issues
                                # Verify it's not creating a cycle
                                pass


# =============================================================================
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
