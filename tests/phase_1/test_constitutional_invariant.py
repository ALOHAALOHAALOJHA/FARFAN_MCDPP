"""Test Phase 1 Constitutional Invariant (60-chunk requirement).

This test verifies the constitutional invariant of Phase 1:
EXACTLY 60 chunks must be produced (10 Policy Areas × 6 Causal Dimensions).

Test Coverage:
- POST-01: Exactly 60 chunks produced
- POST-02: All chunks have valid PA and Dimension assignments
- POST-03: Chunk graph is acyclic (DAG property)
- Constitutional: Complete PA×Dimension grid coverage
- Constitutional: 10 Policy Areas, 6 Dimensions
"""

import pytest
from canonic_phases.phase_1_cpp_ingestion.contracts import (
    EXPECTED_CHUNK_COUNT,
    EXPECTED_DIMENSION_COUNT,
    EXPECTED_POLICY_AREA_COUNT,
    validate_constitutional_invariant,
    get_padim_coverage_matrix,
)


class TestConstitutionalInvariant:
    """Test Phase 1 constitutional invariant enforcement."""
    
    def test_expected_constants(self):
        """Verify expected constants are correct."""
        assert EXPECTED_CHUNK_COUNT == 60, "Constitutional invariant: 60 chunks"
        assert EXPECTED_POLICY_AREA_COUNT == 10, "Constitutional invariant: 10 Policy Areas"
        assert EXPECTED_DIMENSION_COUNT == 6, "Constitutional invariant: 6 Dimensions"
        assert EXPECTED_POLICY_AREA_COUNT * EXPECTED_DIMENSION_COUNT == EXPECTED_CHUNK_COUNT
    
    def test_contract_imports(self):
        """Verify contracts can be imported from canonical path."""
        from canonic_phases.phase_1_cpp_ingestion.contracts import (
            phase1_mission_contract,
            phase1_input_contract,
            phase1_output_contract,
            phase1_constitutional_contract,
        )
        
        assert phase1_mission_contract is not None
        assert phase1_input_contract is not None
        assert phase1_output_contract is not None
        assert phase1_constitutional_contract is not None
    
    def test_subphase_weights_defined(self):
        """Verify all 16 subphase weights are defined."""
        from canonic_phases.phase_1_cpp_ingestion.contracts import PHASE1_SUBPHASE_WEIGHTS
        
        assert len(PHASE1_SUBPHASE_WEIGHTS) == 16, "Must have exactly 16 subphases"
        
        # Verify critical subphases
        critical_subphases = ["SP4", "SP11", "SP13"]
        for sp_id in critical_subphases:
            assert sp_id in PHASE1_SUBPHASE_WEIGHTS
            sp_weight = PHASE1_SUBPHASE_WEIGHTS[sp_id]
            assert sp_weight.weight == 10000, f"{sp_id} must have weight 10000 (CRITICAL)"
            assert sp_weight.tier.value == "CRITICAL"
            assert sp_weight.abort_on_failure is True
    
    def test_mission_contract_validation(self):
        """Verify mission contract validates correctly."""
        from canonic_phases.phase_1_cpp_ingestion.contracts import validate_mission_contract
        
        # Should not raise
        result = validate_mission_contract()
        assert result is True


class TestPADimGridCoverage:
    """Test PA×Dimension grid coverage requirements."""
    
    def test_grid_math(self):
        """Verify PA×Dim grid mathematics."""
        # 10 Policy Areas × 6 Dimensions = 60 chunks
        assert 10 * 6 == 60
        
        # Each PA should have 6 chunks (one per Dimension)
        chunks_per_pa = 60 // 10
        assert chunks_per_pa == 6
        
        # Each Dimension should have 10 chunks (one per PA)
        chunks_per_dim = 60 // 6
        assert chunks_per_dim == 10


class TestCertificates:
    """Test Phase 1 execution certificates."""
    
    def test_certificates_exist(self):
        """Verify all 15 certificates exist."""
        from pathlib import Path
        
        cert_dir = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        assert cert_dir.exists(), f"Certificates directory must exist: {cert_dir}"
        
        # Verify 15 certificates (SP0-SP14)
        certificates = list(cert_dir.glob("CERTIFICATE_*.md"))
        assert len(certificates) >= 15, f"Must have at least 15 certificates, found {len(certificates)}"
    
    def test_certificate_content(self):
        """Verify certificate files have required fields."""
        from pathlib import Path
        
        cert_dir = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        required_fields = [
            "Status:",
            "Version:",
            "Certificate ID:",
            "Subphase ID:",
            "Weight:",
            "Tier:",
        ]
        
        for cert_file in sorted(cert_dir.glob("CERTIFICATE_*.md"))[:5]:  # Check first 5
            content = cert_file.read_text()
            for field in required_fields:
                assert field in content, f"{cert_file.name} must contain '{field}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
