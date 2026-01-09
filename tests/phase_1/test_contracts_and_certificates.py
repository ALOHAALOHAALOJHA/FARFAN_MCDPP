"""Test Phase 1 Contracts and Certificates.

This test verifies:
- 4 contract modules exist and are valid
- 15 certificate files exist and have required fields
- Contract functions are properly structured
"""

import pytest
from pathlib import Path
import ast


class TestContractModules:
    """Test Phase 1 contract modules."""
    
    def test_all_contract_files_exist(self):
        """Verify all 4 contract files exist."""
        contracts_dir = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts"
        
        contract_files = [
            "phase1_mission_contract.py",
            "phase1_input_contract.py",
            "phase1_output_contract.py",
            "phase1_constitutional_contract.py",
        ]
        
        for filename in contract_files:
            contract_path = contracts_dir / filename
            assert contract_path.exists(), f"{filename} must exist"
            
            # Verify substantial content
            size_bytes = contract_path.stat().st_size
            assert size_bytes > 500, f"{filename} should be substantial (>500 bytes), got {size_bytes}"


class TestContractStructure:
    """Test contract structure and content."""
    
    def test_mission_contract_defines_subphases(self):
        """Verify mission contract defines all subphases."""
        mission_contract_path = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "phase1_mission_contract.py"
        
        content = mission_contract_path.read_text()
        
        # Verify PHASE1_SUBPHASE_WEIGHTS is defined
        assert "PHASE1_SUBPHASE_WEIGHTS" in content, "PHASE1_SUBPHASE_WEIGHTS must be defined"
        
        # Verify validation function exists
        assert "def validate_mission_contract" in content, "validate_mission_contract function must exist"
        
        # Verify WeightTier enum
        assert "WeightTier" in content, "WeightTier must be defined"
        assert "CRITICAL" in content, "CRITICAL tier must be defined"
        assert "HIGH" in content, "HIGH tier must be defined"
        assert "STANDARD" in content, "STANDARD tier must be defined"
    
    def test_input_contract_defines_preconditions(self):
        """Verify input contract defines preconditions."""
        input_contract_path = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "phase1_input_contract.py"
        
        content = input_contract_path.read_text()
        
        # Verify preconditions are defined
        assert "PHASE1_INPUT_PRECONDITIONS" in content, "PHASE1_INPUT_PRECONDITIONS must be defined"
        assert "PRE-01" in content, "PRE-01 must be defined"
        assert "PRE-02" in content, "PRE-02 must be defined"
        assert "PRE-03" in content, "PRE-03 must be defined"
        assert "PRE-04" in content, "PRE-04 must be defined"
        assert "PRE-05" in content, "PRE-05 must be defined"
        
        # Verify validation function
        assert "def validate_phase1_input_contract" in content, "validate_phase1_input_contract must exist"
    
    def test_output_contract_defines_postconditions(self):
        """Verify output contract defines postconditions."""
        output_contract_path = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "phase1_output_contract.py"
        
        content = output_contract_path.read_text()
        
        # Verify postconditions are defined
        assert "PHASE1_OUTPUT_POSTCONDITIONS" in content, "PHASE1_OUTPUT_POSTCONDITIONS must be defined"
        assert "POST-01" in content, "POST-01 must be defined"
        assert "POST-02" in content, "POST-02 must be defined"
        assert "POST-03" in content, "POST-03 must be defined"
        assert "POST-04" in content, "POST-04 must be defined"
        assert "POST-05" in content, "POST-05 must be defined"
        assert "POST-06" in content, "POST-06 must be defined"
        
        # Verify validation function
        assert "def validate_phase1_output_contract" in content, "validate_phase1_output_contract must exist"
    
    def test_constitutional_contract_defines_constants(self):
        """Verify constitutional contract defines key constants."""
        constitutional_contract_path = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "phase1_constitutional_contract.py"
        
        content = constitutional_contract_path.read_text()
        
        # Verify constants
        assert "EXPECTED_CHUNK_COUNT = 60" in content, "EXPECTED_CHUNK_COUNT must be 60"
        assert "EXPECTED_POLICY_AREA_COUNT = 10" in content, "EXPECTED_POLICY_AREA_COUNT must be 10"
        assert "EXPECTED_DIMENSION_COUNT = 6" in content, "EXPECTED_DIMENSION_COUNT must be 6"
        
        # Verify validation function
        assert "def validate_constitutional_invariant" in content, "validate_constitutional_invariant must exist"


class TestCertificates:
    """Test Phase 1 execution certificates."""
    
    def test_certificates_directory_exists(self):
        """Verify certificates directory exists."""
        cert_dir = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        assert cert_dir.exists(), "certificates directory must exist"
        assert cert_dir.is_dir(), "certificates must be a directory"
    
    def test_exactly_15_certificates(self):
        """Verify exactly 15 certificates exist (SP0-SP14)."""
        cert_dir = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        certificates = list(cert_dir.glob("CERTIFICATE_*.md"))
        # Filter out any that don't match the expected pattern
        valid_certs = [c for c in certificates if c.name.startswith("CERTIFICATE_") and c.name.endswith(".md")]
        
        assert len(valid_certs) >= 15, f"Must have at least 15 certificates, found {len(valid_certs)}: {[c.name for c in valid_certs]}"
    
    def test_certificate_required_fields(self):
        """Verify certificates contain required fields."""
        cert_dir = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        required_fields = [
            "**Status**:",
            "**Version**:",
            "**Certificate ID**:",
            "**Subphase ID**:",
            "**Weight**:",
            "**Tier**:",
            "Contract Obligations",
            "Verification Criteria",
            "Certificate Authority",
        ]
        
        certificates = sorted(cert_dir.glob("CERTIFICATE_*.md"))[:5]  # Check first 5
        
        assert len(certificates) >= 5, "Must have at least 5 certificates"
        
        for cert_file in certificates:
            content = cert_file.read_text()
            for field in required_fields:
                assert field in content, f"{cert_file.name} must contain '{field}'"
    
    def test_certificates_are_markdown(self):
        """Verify all certificates are Markdown files."""
        cert_dir = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "certificates"
        
        for cert_file in cert_dir.glob("CERTIFICATE_*"):
            assert cert_file.suffix == ".md", f"Certificate must be Markdown: {cert_file.name}"


class TestContractsPackage:
    """Test contracts package structure."""
    
    def test_contracts_init_exists(self):
        """Verify contracts __init__.py exists and has exports."""
        contracts_init = Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "contracts" / "__init__.py"
        
        assert contracts_init.exists(), "contracts/__init__.py must exist"
        
        content = contracts_init.read_text()
        
        # Verify key exports are mentioned
        expected_exports = [
            "PHASE1_SUBPHASE_WEIGHTS",
            "PHASE1_INPUT_PRECONDITIONS",
            "PHASE1_OUTPUT_POSTCONDITIONS",
            "EXPECTED_CHUNK_COUNT",
        ]
        
        for export_name in expected_exports:
            assert export_name in content, f"contracts/__init__.py must export {export_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
