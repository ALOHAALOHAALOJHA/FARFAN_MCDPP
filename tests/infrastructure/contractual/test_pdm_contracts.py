"""
Tests for PDM Contracts.

Validates contract enforcement for PDM structural recognition.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from farfan_pipeline.infrastructure.contractual.pdm_contracts import (
    PDMProfileContract,
    Phase1Phase2HandoffContract,
    PrerequisiteError,
    SP2Obligations,
    SP4Obligations,
    ValidationError,
    verify_all_pdm_contracts,
)
from farfan_pipeline.infrastructure.parametrization.pdm_structural_profile import (
    CanonicalSection,
    ContextualMarker,
    HierarchyLevel,
    PDMStructuralProfile,
    SemanticRule,
    StructuralTransition,
    get_default_profile,
)


class TestPDMProfileContract:
    """Test PDM profile contract enforcement."""

    def test_enforce_profile_presence_success(self):
        """Test profile presence enforcement succeeds with valid profile."""
        # Should succeed because default profile exists
        profile = PDMProfileContract.enforce_profile_presence()
        assert profile is not None
        assert isinstance(profile, PDMStructuralProfile)

    def test_enforce_profile_presence_invalid_path(self):
        """Test profile presence enforcement fails with invalid path."""
        with pytest.raises(PrerequisiteError, match="not found"):
            PDMProfileContract.enforce_profile_presence(
                profile_path=Path("/nonexistent/path/profile.py")
            )

    def test_validate_profile_version_success(self):
        """Test profile version validation succeeds."""
        profile = get_default_profile()
        assert PDMProfileContract.validate_profile_version(profile)

    def test_validate_profile_version_failure(self):
        """Test profile version validation fails with wrong version."""
        profile = PDMStructuralProfile(
            profile_version="WRONG-VERSION",
        )

        with pytest.raises(ValidationError, match="version mismatch"):
            PDMProfileContract.validate_profile_version(profile)


class TestSP2Obligations:
    """Test SP2 obligations contract."""

    def test_validate_sp2_execution_success(self):
        """Test SP2 validation succeeds with valid output."""
        profile = get_default_profile()

        # Mock valid SP2 output
        sp2_output = Mock()
        sp2_output.hierarchy = {"1": "H1", "2": "H2"}
        sp2_output.sections = [{"name": "Diagnóstico"}]
        sp2_output.tables = [{"name": "PPI"}]
        sp2_output._pdm_profile_used = "PDM-2025.1"

        is_valid, violations = SP2Obligations.validate_sp2_execution(profile, sp2_output)
        assert is_valid
        assert len(violations) == 0

    def test_validate_sp2_execution_missing_hierarchy(self):
        """Test SP2 validation fails without hierarchy."""
        profile = get_default_profile()

        # Mock SP2 output without hierarchy
        sp2_output = Mock()
        sp2_output.hierarchy = {}  # Empty
        sp2_output.sections = [{"name": "Diagnóstico"}]
        sp2_output.tables = [{"name": "PPI"}]
        sp2_output._pdm_profile_used = "PDM-2025.1"

        is_valid, violations = SP2Obligations.validate_sp2_execution(profile, sp2_output)
        assert not is_valid
        assert any("Hierarchy not detected" in v for v in violations)

    def test_validate_sp2_execution_missing_sections(self):
        """Test SP2 validation fails without sections."""
        profile = get_default_profile()

        sp2_output = Mock()
        sp2_output.hierarchy = {"1": "H1"}
        sp2_output.sections = []  # Empty
        sp2_output.tables = [{"name": "PPI"}]
        sp2_output._pdm_profile_used = "PDM-2025.1"

        is_valid, violations = SP2Obligations.validate_sp2_execution(profile, sp2_output)
        assert not is_valid
        assert any("No canonical sections" in v for v in violations)

    def test_enforce_sp2_preconditions_success(self):
        """Test SP2 precondition enforcement succeeds."""
        profile = get_default_profile()
        # Should not raise
        SP2Obligations.enforce_sp2_preconditions(profile)

    def test_enforce_sp2_preconditions_no_profile(self):
        """Test SP2 precondition enforcement fails without profile."""
        with pytest.raises(PrerequisiteError, match="mandatory"):
            SP2Obligations.enforce_sp2_preconditions(None)


class TestSP4Obligations:
    """Test SP4 obligations contract."""

    def test_validate_sp4_assignment_success(self):
        """Test SP4 validation succeeds with valid chunks."""
        profile = get_default_profile()

        sp2_output = Mock()
        sp2_output.hierarchy = {"1": "H1"}
        sp2_output.sections = [{"name": "Diagnóstico"}]

        # Create 60 valid chunks
        sp4_output = []
        for i in range(60):
            chunk = Mock()
            chunk.chunk_id = f"PA{(i % 10) + 1:02d}-DIM{(i % 6) + 1:02d}"
            chunk.text = "Test text"
            chunk.pdm_metadata = Mock()
            chunk.pdm_metadata.source_section = CanonicalSection.DIAGNOSTICO
            chunk.pdm_metadata.hierarchy_level = HierarchyLevel.H1
            sp4_output.append(chunk)

        is_valid, violations = SP4Obligations.validate_sp4_assignment(
            sp2_output, profile, sp4_output
        )
        assert is_valid
        assert len(violations) == 0

    def test_validate_sp4_assignment_wrong_count(self):
        """Test SP4 validation fails with wrong chunk count."""
        profile = get_default_profile()
        sp2_output = Mock()

        # Only 50 chunks instead of 60
        sp4_output = [Mock() for _ in range(50)]

        is_valid, violations = SP4Obligations.validate_sp4_assignment(
            sp2_output, profile, sp4_output
        )
        assert not is_valid
        assert any("60 chunks" in v for v in violations)

    def test_validate_sp4_assignment_missing_metadata(self):
        """Test SP4 validation fails with missing PDM metadata."""
        profile = get_default_profile()
        sp2_output = Mock()

        # 60 chunks but no PDM metadata
        sp4_output = []
        for i in range(60):
            chunk = Mock()
            chunk.chunk_id = f"PA{(i % 10) + 1:02d}-DIM{(i % 6) + 1:02d}"
            chunk.pdm_metadata = None  # Missing
            sp4_output.append(chunk)

        is_valid, violations = SP4Obligations.validate_sp4_assignment(
            sp2_output, profile, sp4_output
        )
        assert not is_valid
        assert any("missing PDM metadata" in v for v in violations)

    def test_enforce_sp4_preconditions_success(self):
        """Test SP4 precondition enforcement succeeds."""
        profile = get_default_profile()
        sp2_output = Mock()

        # Should not raise
        SP4Obligations.enforce_sp4_preconditions(sp2_output, profile)

    def test_enforce_sp4_preconditions_no_profile(self):
        """Test SP4 precondition enforcement fails without profile."""
        sp2_output = Mock()

        with pytest.raises(PrerequisiteError, match="PDMStructuralProfile required"):
            SP4Obligations.enforce_sp4_preconditions(sp2_output, None)


class TestPhase1Phase2HandoffContract:
    """Test Phase 1 → Phase 2 handoff contract."""

    def test_validate_cpp_for_phase2_success(self):
        """Test CPP validation succeeds."""
        # Mock valid CPP
        cpp = Mock()
        cpp.chunk_graph = Mock()
        cpp.chunk_graph.chunks = {}

        for i in range(60):
            chunk = Mock()
            chunk.pdm_metadata = Mock()
            chunk.pdm_metadata.hierarchy_level = HierarchyLevel.H1
            chunk.pdm_metadata.source_section = CanonicalSection.DIAGNOSTICO
            cpp.chunk_graph.chunks[f"chunk_{i}"] = chunk

        cpp.semantic_integrity_verified = True
        cpp.semantic_violations = ()
        cpp.calibration_applied = False
        cpp.pdm_profile_version = "PDM-2025.1"

        is_valid, violations = Phase1Phase2HandoffContract.validate_cpp_for_phase2(cpp)
        assert is_valid
        assert len(violations) == 0

    def test_validate_cpp_for_phase2_wrong_chunk_count(self):
        """Test CPP validation fails with wrong chunk count."""
        cpp = Mock()
        cpp.chunk_graph = Mock()
        cpp.chunk_graph.chunks = {f"chunk_{i}": Mock() for i in range(50)}  # Only 50

        is_valid, violations = Phase1Phase2HandoffContract.validate_cpp_for_phase2(cpp)
        assert not is_valid
        assert any("Expected 60 chunks" in v for v in violations)

    def test_validate_cpp_for_phase2_missing_pdm_version(self):
        """Test CPP validation fails without PDM version."""
        cpp = Mock()
        cpp.chunk_graph = Mock()
        cpp.chunk_graph.chunks = {}

        for i in range(60):
            chunk = Mock()
            chunk.pdm_metadata = Mock()
            cpp.chunk_graph.chunks[f"chunk_{i}"] = chunk

        cpp.pdm_profile_version = None  # Missing

        is_valid, violations = Phase1Phase2HandoffContract.validate_cpp_for_phase2(cpp)
        assert not is_valid
        assert any("PDM profile version not recorded" in v for v in violations)

    def test_enforce_phase2_preconditions_success(self):
        """Test Phase 2 precondition enforcement succeeds."""
        # Mock valid CPP
        cpp = Mock()
        cpp.chunk_graph = Mock()
        cpp.chunk_graph.chunks = {}

        for i in range(60):
            chunk = Mock()
            chunk.pdm_metadata = Mock()
            chunk.pdm_metadata.hierarchy_level = HierarchyLevel.H1
            chunk.pdm_metadata.source_section = CanonicalSection.DIAGNOSTICO
            cpp.chunk_graph.chunks[f"chunk_{i}"] = chunk

        cpp.semantic_integrity_verified = True
        cpp.semantic_violations = ()
        cpp.calibration_applied = False
        cpp.pdm_profile_version = "PDM-2025.1"

        # Should not raise
        Phase1Phase2HandoffContract.enforce_phase2_preconditions(cpp)

    def test_enforce_phase2_preconditions_failure(self):
        """Test Phase 2 precondition enforcement fails with invalid CPP."""
        cpp = Mock()
        cpp.chunk_graph = Mock()
        cpp.chunk_graph.chunks = {}  # Empty - violation

        with pytest.raises(PrerequisiteError, match="preconditions not met"):
            Phase1Phase2HandoffContract.enforce_phase2_preconditions(cpp)


class TestVerifyAllPDMContracts:
    """Test unified contract verification."""

    def test_verify_all_contracts(self):
        """Test verifying all contracts at once."""
        profile = get_default_profile()

        # Mock outputs
        sp2_output = Mock()
        sp2_output.hierarchy = {"1": "H1"}
        sp2_output.sections = [{"name": "Diagnóstico"}]
        sp2_output.tables = [{"name": "PPI"}]
        sp2_output._pdm_profile_used = "PDM-2025.1"

        sp4_output = []
        for i in range(60):
            chunk = Mock()
            chunk.chunk_id = f"PA{(i % 10) + 1:02d}-DIM{(i % 6) + 1:02d}"
            chunk.text = "Test"
            chunk.pdm_metadata = Mock()
            chunk.pdm_metadata.source_section = CanonicalSection.DIAGNOSTICO
            sp4_output.append(chunk)

        cpp = Mock()
        cpp.chunk_graph = Mock()
        cpp.chunk_graph.chunks = {f"chunk_{i}": sp4_output[i] for i in range(60)}
        cpp.semantic_integrity_verified = True
        cpp.semantic_violations = ()
        cpp.calibration_applied = False
        cpp.pdm_profile_version = "PDM-2025.1"

        results = verify_all_pdm_contracts(profile, sp2_output, sp4_output, cpp)

        assert "SP2Obligations" in results
        assert "SP4Obligations" in results
        assert "Phase1Phase2Handoff" in results

        # All should pass
        for contract_name, (is_valid, violations) in results.items():
            assert is_valid, f"{contract_name} failed: {violations}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
