"""
Tests for Aggregation Contracts - Dura Lex Enforcement

Tests contract validation for all aggregation levels:
- Weight normalization (AGG-001)
- Score bounds (AGG-002)
- Coherence bounds (AGG-003)
- Hermeticity (AGG-004)
- Convexity (AGG-006)
"""

import pytest
from cross_cutting_infrastructure.contractual.dura_lex.aggregation_contract import (
    DimensionAggregationContract,
    AreaAggregationContract,
    ClusterAggregationContract,
    MacroAggregationContract,
    create_aggregation_contract,
    AggregationContractViolation,
)


class TestBaseAggregationContract:
    """Test base contract functionality."""
    
    def test_weight_normalization_valid(self):
        """Test valid weight normalization."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        weights = [0.2, 0.2, 0.2, 0.2, 0.2]
        
        assert contract.validate_weight_normalization(weights)
        assert len(contract.get_violations()) == 0
    
    def test_weight_normalization_invalid(self):
        """Test invalid weight normalization."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        weights = [0.3, 0.3, 0.3, 0.3, 0.3]  # Sum = 1.5
        
        assert not contract.validate_weight_normalization(weights)
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].invariant_id == "AGG-001"
        assert violations[0].severity == "CRITICAL"
    
    def test_weight_normalization_abort(self):
        """Test abort on weight normalization violation."""
        contract = DimensionAggregationContract(abort_on_violation=True)
        weights = [0.5, 0.5, 0.5]  # Sum = 1.5
        
        with pytest.raises(ValueError, match="Weights do not sum to 1.0"):
            contract.validate_weight_normalization(weights)
    
    def test_score_bounds_valid(self):
        """Test valid score bounds."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        
        assert contract.validate_score_bounds(0.0)
        assert contract.validate_score_bounds(1.5)
        assert contract.validate_score_bounds(3.0)
        assert len(contract.get_violations()) == 0
    
    def test_score_bounds_invalid(self):
        """Test invalid score bounds."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        
        # Test below minimum
        assert not contract.validate_score_bounds(-0.5)
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].invariant_id == "AGG-002"
        
        contract.clear_violations()
        
        # Test above maximum
        assert not contract.validate_score_bounds(3.5)
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].invariant_id == "AGG-002"
    
    def test_coherence_bounds_valid(self):
        """Test valid coherence bounds."""
        contract = ClusterAggregationContract(abort_on_violation=False)
        
        assert contract.validate_coherence_bounds(0.0)
        assert contract.validate_coherence_bounds(0.5)
        assert contract.validate_coherence_bounds(1.0)
        assert len(contract.get_violations()) == 0
    
    def test_coherence_bounds_invalid(self):
        """Test invalid coherence bounds."""
        contract = ClusterAggregationContract(abort_on_violation=False)
        
        assert not contract.validate_coherence_bounds(-0.1)
        assert not contract.validate_coherence_bounds(1.5)
        
        violations = contract.get_violations()
        assert len(violations) == 2
        assert all(v.invariant_id == "AGG-003" for v in violations)
    
    def test_convexity_valid(self):
        """Test valid convexity."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        inputs = [1.0, 2.0, 3.0]
        
        # Aggregated should be within [1.0, 3.0]
        assert contract.validate_convexity(2.0, inputs)
        assert contract.validate_convexity(1.5, inputs)
        assert contract.validate_convexity(2.8, inputs)
        assert len(contract.get_violations()) == 0
    
    def test_convexity_invalid(self):
        """Test invalid convexity."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        inputs = [1.0, 2.0, 3.0]
        
        # Aggregated outside [1.0, 3.0]
        assert not contract.validate_convexity(0.5, inputs)
        assert not contract.validate_convexity(3.5, inputs)
        
        violations = contract.get_violations()
        assert len(violations) == 2
        assert all(v.invariant_id == "AGG-006" for v in violations)


class TestDimensionAggregationContract:
    """Test dimension-level contract."""
    
    def test_hermeticity_valid(self):
        """Test valid dimension hermeticity."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        
        actual = {"Q1", "Q2", "Q3", "Q4", "Q5"}
        expected = {"Q1", "Q2", "Q3", "Q4", "Q5"}
        
        assert contract.validate_hermeticity(actual, expected)
        assert len(contract.get_violations()) == 0
    
    def test_hermeticity_missing_questions(self):
        """Test hermeticity with missing questions."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        
        actual = {"Q1", "Q2", "Q3"}
        expected = {"Q1", "Q2", "Q3", "Q4", "Q5"}
        
        assert not contract.validate_hermeticity(actual, expected)
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].invariant_id == "AGG-004"
        assert violations[0].severity == "HIGH"
    
    def test_hermeticity_extra_questions(self):
        """Test hermeticity with extra questions."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        
        actual = {"Q1", "Q2", "Q3", "Q4", "Q5", "Q6"}
        expected = {"Q1", "Q2", "Q3", "Q4", "Q5"}
        
        assert not contract.validate_hermeticity(actual, expected)
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].invariant_id == "AGG-004"


class TestAreaAggregationContract:
    """Test area-level contract."""
    
    def test_hermeticity_valid(self):
        """Test valid area hermeticity."""
        contract = AreaAggregationContract(abort_on_violation=False)
        
        actual = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}
        expected = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}
        
        assert contract.validate_hermeticity(actual, expected)
        assert len(contract.get_violations()) == 0
    
    def test_hermeticity_missing_dimensions(self):
        """Test hermeticity with missing dimensions."""
        contract = AreaAggregationContract(abort_on_violation=False)
        
        actual = {"DIM01", "DIM02", "DIM03", "DIM04"}
        expected = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}
        
        assert not contract.validate_hermeticity(actual, expected)
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].severity == "CRITICAL"  # Area hermeticity is critical


class TestClusterAggregationContract:
    """Test cluster-level contract."""
    
    def test_hermeticity_valid(self):
        """Test valid cluster hermeticity."""
        contract = ClusterAggregationContract(abort_on_violation=False)
        
        actual = {"PA01", "PA02", "PA03"}
        expected = {"PA01", "PA02", "PA03"}
        
        assert contract.validate_hermeticity(actual, expected)
        assert len(contract.get_violations()) == 0
    
    def test_hermeticity_invalid(self):
        """Test invalid cluster hermeticity."""
        contract = ClusterAggregationContract(abort_on_violation=False)
        
        actual = {"PA01", "PA02"}
        expected = {"PA01", "PA02", "PA03"}
        
        assert not contract.validate_hermeticity(actual, expected)
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].invariant_id == "AGG-004"


class TestMacroAggregationContract:
    """Test macro-level contract."""
    
    def test_hermeticity_valid(self):
        """Test valid macro hermeticity (4 clusters)."""
        contract = MacroAggregationContract(abort_on_violation=False)
        
        actual = {"CL01", "CL02", "CL03", "CL04"}
        expected = {"CL01", "CL02", "CL03", "CL04"}
        
        assert contract.validate_hermeticity(actual, expected)
        assert len(contract.get_violations()) == 0
    
    def test_hermeticity_wrong_count(self):
        """Test hermeticity with wrong cluster count."""
        contract = MacroAggregationContract(abort_on_violation=False)
        
        actual = {"CL01", "CL02", "CL03"}  # Only 3 clusters
        expected = {"CL01", "CL02", "CL03", "CL04"}
        
        assert not contract.validate_hermeticity(actual, expected)
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].severity == "CRITICAL"
        assert "expected 4 clusters" in violations[0].message


class TestContractFactory:
    """Test contract factory function."""
    
    def test_create_dimension_contract(self):
        """Test creating dimension contract."""
        contract = create_aggregation_contract("dimension")
        assert isinstance(contract, DimensionAggregationContract)
        assert contract.contract_id == "DIM_AGG"
    
    def test_create_area_contract(self):
        """Test creating area contract."""
        contract = create_aggregation_contract("area")
        assert isinstance(contract, AreaAggregationContract)
        assert contract.contract_id == "AREA_AGG"
    
    def test_create_cluster_contract(self):
        """Test creating cluster contract."""
        contract = create_aggregation_contract("cluster")
        assert isinstance(contract, ClusterAggregationContract)
        assert contract.contract_id == "CLUSTER_AGG"
    
    def test_create_macro_contract(self):
        """Test creating macro contract."""
        contract = create_aggregation_contract("macro")
        assert isinstance(contract, MacroAggregationContract)
        assert contract.contract_id == "MACRO_AGG"
    
    def test_create_invalid_contract(self):
        """Test creating invalid contract."""
        with pytest.raises(ValueError, match="Invalid aggregation level"):
            create_aggregation_contract("invalid_level")


class TestContractViolationTracking:
    """Test violation tracking functionality."""
    
    def test_violation_accumulation(self):
        """Test that violations accumulate."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        
        # Generate multiple violations
        contract.validate_weight_normalization([0.5, 0.5, 0.5])
        contract.validate_score_bounds(-1.0)
        contract.validate_score_bounds(4.0)
        
        violations = contract.get_violations()
        assert len(violations) == 3
    
    def test_violation_clearing(self):
        """Test clearing violations."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        
        contract.validate_weight_normalization([0.5, 0.5, 0.5])
        assert len(contract.get_violations()) == 1
        
        contract.clear_violations()
        assert len(contract.get_violations()) == 0
    
    def test_violation_context(self):
        """Test that violations capture context."""
        contract = DimensionAggregationContract(abort_on_violation=False)
        
        context = {"dimension_id": "DIM01", "policy_area": "PA01"}
        contract.validate_weight_normalization([0.5, 0.5, 0.5], context=context)
        
        violations = contract.get_violations()
        assert len(violations) == 1
        assert violations[0].context == context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
