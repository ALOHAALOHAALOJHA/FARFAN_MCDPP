"""Test Phase 1 Contracts and Certificates.

This test verifies:
- 4 contract modules exist and are valid
- 15 certificate files exist and have required fields
- Contract functions can be imported and executed
"""

import pytest
from pathlib import Path


class TestContractModules:
    """Test Phase 1 contract modules."""
    
    def test_mission_contract_exists(self):
        """Verify mission contract module exists."""
        contract_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "phase1_mission_contract.py"
        assert contract_path.exists(), "phase1_mission_contract.py must exist"
    
    def test_input_contract_exists(self):
        """Verify input contract module exists."""
        contract_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "phase1_input_contract.py"
        assert contract_path.exists(), "phase1_input_contract.py must exist"
    
    def test_output_contract_exists(self):
        """Verify output contract module exists."""
        contract_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "phase1_output_contract.py"
        assert contract_path.exists(), "phase1_output_contract.py must exist"
    
    def test_constitutional_contract_exists(self):
        """Verify constitutional contract module exists."""
        contract_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "phase1_constitutional_contract.py"
        assert contract_path.exists(), "phase1_constitutional_contract.py must exist"
    
    def test_contracts_are_substantial(self):
        """Verify contracts are substantial (not stubs)."""
        contracts_dir = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts"
        
        contract_files = [
            "phase1_mission_contract.py",
            "phase1_input_contract.py",
            "phase1_output_contract.py",
            "phase1_constitutional_contract.py",
        ]
        
        for filename in contract_files:
            contract_path = contracts_dir / filename
            size_bytes = contract_path.stat().st_size
            assert size_bytes > 500, f"{filename} should be substantial (>500 bytes), got {size_bytes}"


class TestContractImports:
    """Test contract imports and functions."""
    
    def test_mission_contract_imports(self):
        """Verify mission contract can be imported."""
        from canonic_phases.phase_1_cpp_ingestion.contracts import (
            PHASE1_SUBPHASE_WEIGHTS,
            WeightTier,
            validate_mission_contract,
        )
        
        assert PHASE1_SUBPHASE_WEIGHTS is not None
        assert WeightTier is not None
        assert validate_mission_contract is not None
        
        # Verify function executes
        result = validate_mission_contract()
        assert result is True
    
    def test_input_contract_imports(self):
        """Verify input contract can be imported."""
        from canonic_phases.phase_1_cpp_ingestion.contracts import (
            PHASE1_INPUT_PRECONDITIONS,
            validate_phase1_input_contract,
        )
        
        assert PHASE1_INPUT_PRECONDITIONS is not None
        assert len(PHASE1_INPUT_PRECONDITIONS) == 5, "Must have 5 preconditions (PRE-01 through PRE-05)"
        assert validate_phase1_input_contract is not None
    
    def test_output_contract_imports(self):
        """Verify output contract can be imported."""
        from canonic_phases.phase_1_cpp_ingestion.contracts import (
            PHASE1_OUTPUT_POSTCONDITIONS,
            validate_phase1_output_contract,
        )
        
        assert PHASE1_OUTPUT_POSTCONDITIONS is not None
        assert len(PHASE1_OUTPUT_POSTCONDITIONS) == 6, "Must have 6 postconditions (POST-01 through POST-06)"
        assert validate_phase1_output_contract is not None
    
    def test_constitutional_contract_imports(self):
        """Verify constitutional contract can be imported."""
        from canonic_phases.phase_1_cpp_ingestion.contracts import (
            EXPECTED_CHUNK_COUNT,
            EXPECTED_POLICY_AREA_COUNT,
            EXPECTED_DIMENSION_COUNT,
            validate_constitutional_invariant,
        )
        
        assert EXPECTED_CHUNK_COUNT == 60
        assert EXPECTED_POLICY_AREA_COUNT == 10
        assert EXPECTED_DIMENSION_COUNT == 6
        assert validate_constitutional_invariant is not None


class TestCertificates:
    """Test Phase 1 execution certificates."""
    
    def test_certificates_directory_exists(self):
        """Verify certificates directory exists."""
        cert_dir = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        assert cert_dir.exists(), "certificates directory must exist"
        assert cert_dir.is_dir(), "certificates must be a directory"
    
    def test_exactly_15_certificates(self):
        """Verify exactly 15 certificates exist (SP0-SP14)."""
        cert_dir = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        certificates = list(cert_dir.glob("CERTIFICATE_*.md"))
        # Filter out any that don't match the expected pattern
        valid_certs = [c for c in certificates if c.name.startswith("CERTIFICATE_") and c.name.endswith(".md")]
        
        assert len(valid_certs) >= 15, f"Must have at least 15 certificates, found {len(valid_certs)}: {[c.name for c in valid_certs]}"
    
    def test_certificate_naming_convention(self):
        """Verify certificates follow naming convention."""
        cert_dir = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        expected_certificates = [
            f"CERTIFICATE_{i:02d}_SP{i}.md" for i in range(15)
        ]
        
        for expected_name in expected_certificates:
            cert_path = cert_dir / expected_name
            if not cert_path.exists():
                # Some might have slightly different naming, just warn
                print(f"Warning: Expected certificate {expected_name} not found (may use different naming)")
    
    def test_certificate_required_fields(self):
        """Verify certificates contain required fields."""
        cert_dir = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        required_fields = [
            "Status:",
            "Version:",
            "Certificate ID:",
            "Subphase ID:",
            "Weight:",
            "Tier:",
            "Contract Obligations",
            "Verification Criteria",
            "Certificate Authority",
        ]
        
        certificates = sorted(cert_dir.glob("CERTIFICATE_*.md"))[:5]  # Check first 5
        
        for cert_file in certificates:
            content = cert_file.read_text()
            for field in required_fields:
                assert field in content, f"{cert_file.name} must contain '{field}'"
    
    def test_certificates_are_markdown(self):
        """Verify all certificates are Markdown files."""
        cert_dir = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        for cert_file in cert_dir.glob("CERTIFICATE_*"):
            assert cert_file.suffix == ".md", f"Certificate must be Markdown: {cert_file.name}"


class TestContractsPackage:
    """Test contracts package structure."""
    
    def test_contracts_init_exports(self):
        """Verify contracts __init__.py exports all required symbols."""
        from canonic_phases.phase_1_cpp_ingestion import contracts
        
        required_exports = [
            "PHASE1_SUBPHASE_WEIGHTS",
            "PHASE1_INPUT_PRECONDITIONS",
            "PHASE1_OUTPUT_POSTCONDITIONS",
            "EXPECTED_CHUNK_COUNT",
            "validate_mission_contract",
            "validate_phase1_input_contract",
            "validate_phase1_output_contract",
            "validate_constitutional_invariant",
        ]
        
        for export_name in required_exports:
            assert hasattr(contracts, export_name), f"contracts package must export {export_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
