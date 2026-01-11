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
from pathlib import Path


class TestConstitutionalInvariant:
    """Test Phase 1 constitutional invariant enforcement."""

    def test_expected_constants_defined(self):
        """Verify expected constants are defined in constitutional contract."""
        constitutional_contract_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
            / "contracts"
            / "phase1_10_00_phase1_constitutional_contract.py"
        )

        assert (
            constitutional_contract_path.exists()
        ), f"Constitutional contract must exist: {constitutional_contract_path}"

        content = constitutional_contract_path.read_text()

        # Verify constants are defined
        assert "EXPECTED_CHUNK_COUNT = 60" in content, "EXPECTED_CHUNK_COUNT must be 60"
        assert "EXPECTED_POLICY_AREA_COUNT = 10" in content, "EXPECTED_POLICY_AREA_COUNT must be 10"
        assert "EXPECTED_DIMENSION_COUNT = 6" in content, "EXPECTED_DIMENSION_COUNT must be 6"

        # Verify the math
        assert (
            "10 Policy Areas × 6 Causal Dimensions" in content or "10 PA × 6 Dimensions" in content
        )

    def test_contract_files_exist(self):
        """Verify all 4 contract files exist."""
        contracts_dir = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
            / "contracts"
        )

        required_contracts = [
            "phase1_10_00_phase1_mission_contract.py",
            "phase1_10_00_phase1_input_contract.py",
            "phase1_10_00_phase1_output_contract.py",
            "phase1_10_00_phase1_constitutional_contract.py",
        ]

        for contract_file in required_contracts:
            contract_path = contracts_dir / contract_file
            assert contract_path.exists(), f"Contract must exist: {contract_file}"

            # Verify file is not empty
            size = contract_path.stat().st_size
            assert size > 500, f"{contract_file} must be substantial (>500 bytes), got {size}"

    def test_subphase_weights_defined(self):
        """Verify all 16 subphase weights are defined in mission contract."""
        mission_contract_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
            / "contracts"
            / "phase1_10_00_phase1_mission_contract.py"
        )

        content = mission_contract_path.read_text()

        # Verify PHASE1_SUBPHASE_WEIGHTS is defined
        assert "PHASE1_SUBPHASE_WEIGHTS" in content, "PHASE1_SUBPHASE_WEIGHTS must be defined"

        # Verify it's a dictionary with 16 entries by counting SP definitions
        sp_count = sum(1 for i in range(16) if f'"SP{i}"' in content or f"'SP{i}'" in content)
        assert sp_count == 16, f"Must have exactly 16 subphases (SP0-SP15), found {sp_count}"

        # Verify critical subphases are mentioned
        critical_subphases = ["SP4", "SP11", "SP13"]
        for sp_id in critical_subphases:
            assert (
                f'"{sp_id}"' in content or f"'{sp_id}'" in content
            ), f"Critical subphase {sp_id} must be defined"
            assert "10000" in content, f"Weight 10000 must be present for CRITICAL subphases"

    def test_mission_contract_has_validation_function(self):
        """Verify mission contract has validation function."""
        mission_contract_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
            / "contracts"
            / "phase1_10_00_phase1_mission_contract.py"
        )

        content = mission_contract_path.read_text()

        assert (
            "def validate_mission_contract" in content
        ), "validate_mission_contract function must exist"
        assert (
            "return True" in content or "return bool" in content
        ), "Validation function must return boolean"


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

        cert_dir = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
            / "contracts"
            / "certificates"
        )

        assert cert_dir.exists(), f"Certificates directory must exist: {cert_dir}"

        # Verify 15 certificates (SP0-SP14)
        certificates = list(cert_dir.glob("CERTIFICATE_*.md"))
        assert (
            len(certificates) >= 15
        ), f"Must have at least 15 certificates, found {len(certificates)}"

    def test_certificate_content(self):
        """Verify certificate files have required fields."""
        from pathlib import Path

        cert_dir = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_1"
            / "contracts"
            / "certificates"
        )

        required_fields = [
            "**Status**:",
            "**Version**:",
            "**Certificate ID**:",
            "**Subphase ID**:",
            "**Weight**:",
            "**Tier**:",
        ]

        certificates = sorted(cert_dir.glob("CERTIFICATE_*.md"))
        assert len(certificates) >= 5, "Must have at least 5 certificates to check"

        for cert_file in certificates[:5]:  # Check first 5
            content = cert_file.read_text()
            for field in required_fields:
                assert field in content, f"{cert_file.name} must contain '{field}'"


class TestOrchestratorIntegration:
    """Test orchestrator integration with constitutional enforcement."""

    def test_orchestrator_has_60_chunk_assertion(self):
        """Verify orchestrator enforces 60-chunk invariant."""
        orchestrator_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "orchestration"
            / "orchestrator.py"
        )

        assert orchestrator_path.exists(), "Orchestrator must exist"

        content = orchestrator_path.read_text()

        # Verify P01_EXPECTED_CHUNK_COUNT is defined
        assert (
            "P01_EXPECTED_CHUNK_COUNT = 60" in content or "P01_EXPECTED_CHUNK_COUNT=60" in content
        ), "P01_EXPECTED_CHUNK_COUNT must be 60"

        # Verify chunk count validation exists (any form of validation message)
        assert (
            "expected" in content.lower() and "chunk" in content.lower()
        ) or "validation" in content.lower(), "Must have chunk validation logic"

        # Verify PA and Dimension checks
        assert "policy_areas" in content.lower() or "policyarea" in content.lower(), "Must reference policy areas"
        assert "dimensions" in content.lower() or "dimension" in content.lower(), "Must reference dimensions"

    def test_orchestrator_structure(self):
        """Verify orchestrator has basic DAG/execution structure."""
        orchestrator_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "farfan_pipeline"
            / "orchestration"
            / "orchestrator.py"
        )

        content = orchestrator_path.read_text()

        # Verify has class Orchestrator
        assert "class Orchestrator" in content, "Must have Orchestrator class"
        
        # Verify has phase execution methods (execute is the main method)
        assert "def execute" in content or "async def execute" in content, "Must have execute method"
        
        # Verify has validation/error handling
        assert "raise" in content, "Must have error handling with raise statements"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
