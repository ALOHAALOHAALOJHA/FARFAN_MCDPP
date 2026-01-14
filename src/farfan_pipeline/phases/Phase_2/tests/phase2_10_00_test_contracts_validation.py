"""
Test Phase 2 Contracts
======================

PHASE_LABEL: Phase 2
Module: tests/test_phase2_contracts.py
Purpose: Unit tests for Phase 2 input, mission, and output contracts

Tests verify:
- Input contract validation works correctly
- Mission contract DAG is acyclic
- Output contract validation works correctly
- Compatibility certificates are generated

Version: 1.0.0
"""
from __future__ import annotations

import pytest
from dataclasses import dataclass

# Import contracts

from farfan_pipeline.phases.Phase_2.contracts.phase2_input_contract import (
    Phase2InputPreconditions,
    Phase2InputValidator,
)
from farfan_pipeline.phases.Phase_2.contracts.phase2_mission_contract import (
    verify_dag_acyclicity,
    get_topological_sort,
    Phase2ExecutionFlow,
)
from farfan_pipeline.phases.Phase_2.contracts.phase2_output_contract import (
    Phase2Result,
    Phase2Output,
    Phase2OutputValidator,
    generate_phase3_compatibility_certificate,
)


# =============================================================================
# Input Contract Tests
# =============================================================================

class TestPhase2InputContract:
    """Tests for Phase 2 input contract validation."""
    
    def test_preconditions_immutable(self):
        """Test that preconditions are immutable."""
        preconditions = Phase2InputPreconditions()
        assert preconditions.EXPECTED_CHUNK_COUNT == 60
        assert preconditions.EXPECTED_QUESTION_COUNT == 300
        assert preconditions.EXPECTED_METHOD_COUNT == 240
    
    def test_validate_cpp_valid(self):
        """Test CPP validation with valid input."""
        @dataclass
        class MockCPP:
            chunks: list = None
            schema_version: str = "CPP-2025.1"
            
            def __post_init__(self):
                self.chunks = list(range(60))
        
        validator = Phase2InputValidator()
        cpp = MockCPP()
        is_valid, errors = validator.validate_cpp(cpp)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_cpp_wrong_chunk_count(self):
        """Test CPP validation with wrong chunk count."""
        @dataclass
        class MockCPP:
            chunks: list = None
            schema_version: str = "CPP-2025.1"
            
            def __post_init__(self):
                self.chunks = list(range(50))  # Wrong count
        
        validator = Phase2InputValidator()
        cpp = MockCPP()
        is_valid, errors = validator.validate_cpp(cpp)
        
        assert not is_valid
        assert any("PRE-002" in error for error in errors)
    
    def test_validate_cpp_missing_schema(self):
        """Test CPP validation with missing schema version."""
        @dataclass
        class MockCPP:
            chunks: list = None
            
            def __post_init__(self):
                self.chunks = list(range(60))
        
        validator = Phase2InputValidator()
        cpp = MockCPP()
        is_valid, errors = validator.validate_cpp(cpp)
        
        assert not is_valid
        assert any("PRE-003" in error for error in errors)
    
    def test_validate_certificate_valid(self):
        """Test certificate validation with valid certificate."""
        validator = Phase2InputValidator()
        certificate = {"status": "VALID"}
        
        is_valid, errors = validator.validate_phase1_certificate(certificate)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_certificate_invalid_status(self):
        """Test certificate validation with invalid status."""
        validator = Phase2InputValidator()
        certificate = {"status": "INVALID"}
        
        is_valid, errors = validator.validate_phase1_certificate(certificate)
        
        assert not is_valid
        assert any("PRE-004" in error for error in errors)


# =============================================================================
# Mission Contract Tests
# =============================================================================

class TestPhase2MissionContract:
    """Tests for Phase 2 mission contract and DAG structure."""
    
    def test_dag_is_acyclic(self):
        """Test that the dependency graph is acyclic."""
        is_acyclic = verify_dag_acyclicity()
        assert is_acyclic, "Phase 2 dependency graph contains cycles"
    
    def test_topological_sort_length(self):
        """Test that topological sort includes all modules."""
        topo_sort = get_topological_sort()
        assert len(topo_sort) > 0
        # Should have at least 40 modules based on the issue description
        assert len(topo_sort) >= 40
    
    def test_execution_flow_constants(self):
        """Test execution flow constants."""
        flow = Phase2ExecutionFlow()
        
        assert flow.TOTAL_CONTRACTS == 300
        assert flow.TOTAL_METHODS == 240
        assert "CanonPolicyPackage" in flow.FLOW_DESCRIPTION
        assert "v4 JSON contracts" in flow.ARCHITECTURE_NOTE
    
    def test_contract_pattern(self):
        """Test that contract pattern is documented."""
        flow = Phase2ExecutionFlow()
        assert "Q{001-030}_PA{01-10}" in flow.CONTRACT_PATTERN


# =============================================================================
# Output Contract Tests
# =============================================================================

class TestPhase2OutputContract:
    """Tests for Phase 2 output contract validation."""
    
    def test_result_validation_valid(self):
        """Test result validation with valid data."""
        result = Phase2Result(
            question_id="Q001",
            policy_area="PA01",
            narrative="A" * 150,  # Long enough
            evidence={"key": "value"},
            confidence_score=0.85,
            provenance={"sha256": "abc123"},
        )
        
        is_valid, errors = result.validate()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_result_validation_short_narrative(self):
        """Test result validation with short narrative."""
        result = Phase2Result(
            question_id="Q001",
            policy_area="PA01",
            narrative="Short",  # Too short
            evidence={"key": "value"},
            confidence_score=0.85,
            provenance={"sha256": "abc123"},
        )
        
        is_valid, errors = result.validate()
        
        assert not is_valid
        assert any("Narrative too short" in error for error in errors)
    
    def test_result_validation_missing_evidence(self):
        """Test result validation with missing evidence."""
        result = Phase2Result(
            question_id="Q001",
            policy_area="PA01",
            narrative="A" * 150,
            evidence={},  # Empty
            confidence_score=0.85,
            provenance={"sha256": "abc123"},
        )
        
        is_valid, errors = result.validate()
        
        assert not is_valid
        assert any("Evidence is empty" in error for error in errors)
    
    def test_result_validation_confidence_out_of_range(self):
        """Test result validation with confidence out of range."""
        result = Phase2Result(
            question_id="Q001",
            policy_area="PA01",
            narrative="A" * 150,
            evidence={"key": "value"},
            confidence_score=1.5,  # Out of range
            provenance={"sha256": "abc123"},
        )
        
        is_valid, errors = result.validate()
        
        assert not is_valid
        assert any("out of range" in error for error in errors)
    
    def test_output_completeness(self):
        """Test output completeness validation."""
        # Create 300 valid results
        results = [
            Phase2Result(
                question_id=f"Q{i:03d}",
                policy_area=f"PA{(i % 10) + 1:02d}",
                narrative="A" * 150,
                evidence={"key": "value"},
                confidence_score=0.85,
                provenance={"sha256": "abc123"},
            )
            for i in range(1, 301)
        ]
        
        output = Phase2Output(
            results=results,
            execution_metadata={},
        )
        
        validator = Phase2OutputValidator()
        is_valid, errors = validator.validate_completeness(output)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_output_incomplete(self):
        """Test output completeness with incomplete results."""
        # Create only 100 results
        results = [
            Phase2Result(
                question_id=f"Q{i:03d}",
                policy_area=f"PA{(i % 10) + 1:02d}",
                narrative="A" * 150,
                evidence={"key": "value"},
                confidence_score=0.85,
                provenance={"sha256": "abc123"},
            )
            for i in range(1, 101)
        ]
        
        output = Phase2Output(
            results=results,
            execution_metadata={},
        )
        
        validator = Phase2OutputValidator()
        is_valid, errors = validator.validate_completeness(output)
        
        assert not is_valid
        assert any("POST-001" in error for error in errors)
    
    def test_compatibility_certificate_generation(self):
        """Test Phase 3 compatibility certificate generation."""
        # Create valid output
        results = [
            Phase2Result(
                question_id=f"Q{i:03d}",
                policy_area=f"PA{(i % 10) + 1:02d}",
                narrative="A" * 150,
                evidence={"key": "value"},
                confidence_score=0.85,
                provenance={"sha256": "abc123"},
                metadata={"chunk_ids": [f"chunk_{i}"]}
            )
            for i in range(1, 301)
        ]
        
        output = Phase2Output(
            results=results,
            execution_metadata={},
        )
        
        certificate = generate_phase3_compatibility_certificate(output)
        
        assert certificate.status == "VALID"
        assert certificate.total_results == 300
        assert certificate.valid_results == 300
        assert len(certificate.output_hash) == 64  # SHA-256
    
    def test_compatibility_certificate_with_errors(self):
        """Test certificate generation with validation errors."""
        # Create output with some invalid results
        results = [
            Phase2Result(
                question_id=f"Q{i:03d}",
                policy_area=f"PA{(i % 10) + 1:02d}",
                narrative="Short",  # Too short
                evidence={"key": "value"},
                confidence_score=0.85,
                provenance={"sha256": "abc123"},
            )
            for i in range(1, 101)  # Only 100 results
        ]
        
        output = Phase2Output(
            results=results,
            execution_metadata={},
        )
        
        certificate = generate_phase3_compatibility_certificate(output, strict=True)
        
        assert certificate.status == "INVALID"
        assert certificate.total_results == 100
        assert certificate.valid_results == 0  # All have short narratives
        assert len(certificate.errors) > 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestPhase2ContractIntegration:
    """Integration tests for Phase 2 contracts."""
    
    def test_contracts_imported_correctly(self):
        """Test that all contract modules can be imported."""
        from farfan_pipeline.phases.Phase_2.contracts import (
            Phase2InputValidator,
            Phase2OutputValidator,
            verify_dag_acyclicity,
        )
        
        assert Phase2InputValidator is not None
        assert Phase2OutputValidator is not None
        assert verify_dag_acyclicity is not None
    
    def test_execution_flow_documented(self):
        """Test that execution flow is properly documented."""
        flow = Phase2ExecutionFlow()
        
        # Check that all key components are mentioned
        assert "CanonPolicyPackage" in flow.FLOW_DESCRIPTION
        assert "Carver" in flow.FLOW_DESCRIPTION
        assert "Evidence Nexus" in flow.FLOW_DESCRIPTION
        assert "Narrative Synthesis" in flow.FLOW_DESCRIPTION
        assert "Scoring" in flow.FLOW_DESCRIPTION


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
