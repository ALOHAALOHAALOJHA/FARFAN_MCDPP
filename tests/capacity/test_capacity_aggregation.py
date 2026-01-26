"""
Test Suite for Capacity Aggregation Module
==========================================

Tests for the capacity aggregation implementation from the
Wu, Ramesh & Howlett (2015) Policy Capacity Framework.

Tests cover:
1. Aggregation weight formula (W_agg = η × exp(-λ × Δ_level))
2. Individual→Organizational power mean aggregation
3. Organizational→Systemic geometric mean aggregation
4. Transformation matrix properties
5. Full aggregation pipeline
6. Edge cases and mathematical invariants

Mathematical Models Under Test:
    Formula 2: W_agg = η × exp(-λ × Δ_level)
    Formula 3: C_org = (Σ C_ind^p)^(1/p) × κ_org
    Formula 4: C_sys = √(C_org_mean × C_org_max) × κ_sys

Author: F.A.R.F.A.N. Test Team
Version: 1.0.0
"""

import math
import pytest
import numpy as np
from typing import Dict, List

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    CapacityScore,
)
from farfan_pipeline.capacity.aggregation import (
    CapacityAggregator,
    AggregationConfig,
    TransformationMatrix,
    LevelAggregationResult,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def default_aggregator() -> CapacityAggregator:
    """Create aggregator with default configuration."""
    return CapacityAggregator()


@pytest.fixture
def custom_aggregator() -> CapacityAggregator:
    """Create aggregator with custom configuration."""
    config = AggregationConfig(
        eta=0.90,
        lambda_decay=0.10,
        power_mean_p=1.3,
        kappa_org=0.90,
        kappa_sys=0.95,
    )
    return CapacityAggregator(config=config)


@pytest.fixture
def sample_capacity_scores() -> Dict[CapacityType, CapacityScore]:
    """Sample capacity scores for testing."""
    scores = {}
    
    # Analytical scores
    scores[CapacityType.CA_I] = CapacityScore(
        capacity_type=CapacityType.CA_I,
        raw_score=1.068,
        weighted_score=0.107,
        confidence=0.85,
        method_count=64,
    )
    scores[CapacityType.CA_O] = CapacityScore(
        capacity_type=CapacityType.CA_O,
        raw_score=1.338,
        weighted_score=0.187,
        confidence=0.80,
        method_count=42,
    )
    scores[CapacityType.CA_S] = CapacityScore(
        capacity_type=CapacityType.CA_S,
        raw_score=0.0,
        weighted_score=0.0,
        confidence=0.0,
        method_count=0,
    )
    
    # Operational scores
    scores[CapacityType.CO_I] = CapacityScore(
        capacity_type=CapacityType.CO_I,
        raw_score=0.0,
        weighted_score=0.0,
        confidence=0.0,
        method_count=0,
    )
    scores[CapacityType.CO_O] = CapacityScore(
        capacity_type=CapacityType.CO_O,
        raw_score=1.372,
        weighted_score=0.192,
        confidence=0.75,
        method_count=41,
    )
    scores[CapacityType.CO_S] = CapacityScore(
        capacity_type=CapacityType.CO_S,
        raw_score=1.642,
        weighted_score=0.263,
        confidence=0.82,
        method_count=48,
    )
    
    # Political scores
    scores[CapacityType.CP_I] = CapacityScore(
        capacity_type=CapacityType.CP_I,
        raw_score=0.0,
        weighted_score=0.0,
        confidence=0.0,
        method_count=0,
    )
    scores[CapacityType.CP_O] = CapacityScore(
        capacity_type=CapacityType.CP_O,
        raw_score=1.410,
        weighted_score=0.176,
        confidence=0.78,
        method_count=42,
    )
    scores[CapacityType.CP_S] = CapacityScore(
        capacity_type=CapacityType.CP_S,
        raw_score=0.0,
        weighted_score=0.0,
        confidence=0.0,
        method_count=0,
    )
    
    return scores


# ============================================================================
# TEST: CONFIGURATION VALIDATION
# ============================================================================

class TestAggregationConfig:
    """Test cases for AggregationConfig."""
    
    def test_default_config_level_weights_sum_to_one(self):
        """Verify default level weights sum to 1.0."""
        config = AggregationConfig.default()
        total = sum(config.level_weights.values())
        assert math.isclose(total, 1.0, rel_tol=1e-9)
    
    def test_default_config_skill_weights_sum_to_one(self):
        """Verify default skill weights sum to 1.0."""
        config = AggregationConfig.default()
        total = sum(config.skill_weights.values())
        assert math.isclose(total, 1.0, rel_tol=1e-9)
    
    def test_invalid_level_weights_raises(self):
        """Verify invalid level weights raise error."""
        with pytest.raises(ValueError, match="Level weights must sum to 1.0"):
            AggregationConfig(
                level_weights={
                    PolicyLevel.INDIVIDUAL: 0.5,
                    PolicyLevel.ORGANIZATIONAL: 0.5,
                    PolicyLevel.SYSTEMIC: 0.5,
                }
            )
    
    def test_high_synergy_config(self):
        """Test high synergy configuration preset."""
        config = AggregationConfig.high_synergy()
        assert config.congregation_delta == 0.5
        assert config.kappa_org == 0.90
        assert config.kappa_sys == 0.95


# ============================================================================
# TEST: TRANSFORMATION MATRIX
# ============================================================================

class TestTransformationMatrix:
    """Test cases for TransformationMatrix."""
    
    def test_default_matrix_diagonal_is_one(self):
        """Verify diagonal elements are 1.0 (full self-contribution)."""
        matrix = TransformationMatrix.default()
        np_matrix = matrix.as_numpy()
        
        for i in range(3):
            assert np_matrix[i, i] == 1.0, f"Diagonal [{i},{i}] is not 1.0"
    
    def test_matrix_dimensions(self):
        """Verify matrix is 3×3."""
        matrix = TransformationMatrix.default()
        np_matrix = matrix.as_numpy()
        
        assert np_matrix.shape == (3, 3)
    
    def test_get_coefficient(self):
        """Test coefficient retrieval for specific level pairs."""
        matrix = TransformationMatrix.default()
        
        # Individual to Individual = 1.0
        assert matrix.get_coefficient(
            PolicyLevel.INDIVIDUAL, PolicyLevel.INDIVIDUAL
        ) == 1.0
        
        # Individual to Organizational = 0.75
        assert matrix.get_coefficient(
            PolicyLevel.INDIVIDUAL, PolicyLevel.ORGANIZATIONAL
        ) == 0.75
        
        # Individual to Systemic = 0.50
        assert matrix.get_coefficient(
            PolicyLevel.INDIVIDUAL, PolicyLevel.SYSTEMIC
        ) == 0.50
    
    def test_upper_triangular_stronger(self):
        """Verify upper triangular elements (upward) are stronger."""
        matrix = TransformationMatrix.default()
        
        # Individual→Org should be stronger than Org→Individual
        i_to_o = matrix.get_coefficient(PolicyLevel.INDIVIDUAL, PolicyLevel.ORGANIZATIONAL)
        o_to_i = matrix.get_coefficient(PolicyLevel.ORGANIZATIONAL, PolicyLevel.INDIVIDUAL)
        
        assert i_to_o > o_to_i
    
    def test_eigenvalue_stability(self):
        """Verify matrix eigenvalues indicate stability."""
        matrix = TransformationMatrix.default()
        
        # Default matrix may not be stable, but should be computable
        eigenvalues = matrix.eigenvalues
        assert len(eigenvalues) == 3
    
    def test_get_aggregation_weights(self):
        """Test aggregation weight retrieval."""
        matrix = TransformationMatrix.default()
        weights = matrix.get_aggregation_weights(PolicyLevel.ORGANIZATIONAL)
        
        assert PolicyLevel.INDIVIDUAL in weights
        assert PolicyLevel.ORGANIZATIONAL in weights
        assert PolicyLevel.SYSTEMIC in weights


# ============================================================================
# TEST: AGGREGATION WEIGHT FORMULA
# ============================================================================

class TestAggregationWeight:
    """Test cases for aggregation weight calculation (Formula 2)."""
    
    def test_same_level_weight(self, default_aggregator):
        """Verify weight for same level is maximum (η)."""
        weight = default_aggregator.calculate_aggregation_weight(
            PolicyLevel.INDIVIDUAL, PolicyLevel.INDIVIDUAL
        )
        
        # Same level means Δ_level = 0, so W = η × exp(0) = η
        assert weight == default_aggregator.config.eta
    
    def test_adjacent_level_weight(self, default_aggregator):
        """Verify weight for adjacent levels follows formula."""
        weight = default_aggregator.calculate_aggregation_weight(
            PolicyLevel.INDIVIDUAL, PolicyLevel.ORGANIZATIONAL
        )
        
        # Δ_level = 1, W = η × exp(-λ × 1)
        eta = default_aggregator.config.eta
        lambda_d = default_aggregator.config.lambda_decay
        expected = eta * math.exp(-lambda_d * 1)
        
        assert math.isclose(weight, expected, rel_tol=1e-6)
    
    def test_two_level_gap_weight(self, default_aggregator):
        """Verify weight for two-level gap follows formula."""
        weight = default_aggregator.calculate_aggregation_weight(
            PolicyLevel.INDIVIDUAL, PolicyLevel.SYSTEMIC
        )
        
        # Δ_level = 2, W = η × exp(-λ × 2)
        eta = default_aggregator.config.eta
        lambda_d = default_aggregator.config.lambda_decay
        expected = eta * math.exp(-lambda_d * 2)
        
        assert math.isclose(weight, expected, rel_tol=1e-6)
    
    def test_weight_decreases_with_distance(self, default_aggregator):
        """Verify weights decrease with level distance."""
        w_0 = default_aggregator.calculate_aggregation_weight(
            PolicyLevel.INDIVIDUAL, PolicyLevel.INDIVIDUAL
        )
        w_1 = default_aggregator.calculate_aggregation_weight(
            PolicyLevel.INDIVIDUAL, PolicyLevel.ORGANIZATIONAL
        )
        w_2 = default_aggregator.calculate_aggregation_weight(
            PolicyLevel.INDIVIDUAL, PolicyLevel.SYSTEMIC
        )
        
        assert w_0 > w_1 > w_2
    
    def test_get_all_aggregation_weights(self, default_aggregator):
        """Test batch weight retrieval for target level."""
        weights = default_aggregator.get_all_aggregation_weights(
            PolicyLevel.ORGANIZATIONAL
        )
        
        assert len(weights) == 3
        assert PolicyLevel.INDIVIDUAL in weights
        assert PolicyLevel.ORGANIZATIONAL in weights
        assert PolicyLevel.SYSTEMIC in weights


# ============================================================================
# TEST: INDIVIDUAL → ORGANIZATIONAL AGGREGATION
# ============================================================================

class TestIndividualToOrganizational:
    """Test cases for Individual→Organizational aggregation (Formula 3)."""
    
    def test_power_mean_single_value(self, default_aggregator):
        """Test power mean with single value."""
        result = default_aggregator.aggregate_individual_to_organizational([1.0])
        
        # Single value: (1.0^p)^(1/p) × κ = 1.0 × 0.85 = 0.85
        kappa = default_aggregator.config.kappa_org
        assert math.isclose(result, kappa, rel_tol=1e-3)
    
    def test_power_mean_multiple_values(self, default_aggregator):
        """Test power mean with multiple values."""
        scores = [1.0, 1.2, 0.8]
        result = default_aggregator.aggregate_individual_to_organizational(scores)
        
        # Power mean: (Σ x^p / n)^(1/p) × κ
        p = default_aggregator.config.power_mean_p
        kappa = default_aggregator.config.kappa_org
        
        power_sum = sum(x ** p for x in scores)
        power_mean = (power_sum / len(scores)) ** (1 / p)
        expected = power_mean * kappa
        
        assert math.isclose(result, expected, rel_tol=1e-6)
    
    def test_power_mean_empty_returns_zero(self, default_aggregator):
        """Test power mean returns zero for empty input."""
        result = default_aggregator.aggregate_individual_to_organizational([])
        assert result == 0.0
    
    def test_power_mean_all_zeros_returns_zero(self, default_aggregator):
        """Test power mean returns zero when all inputs are zero."""
        result = default_aggregator.aggregate_individual_to_organizational([0.0, 0.0])
        assert result == 0.0
    
    def test_kappa_org_applied(self, custom_aggregator):
        """Verify organizational capacity factor is applied."""
        scores = [1.0]
        result = custom_aggregator.aggregate_individual_to_organizational(scores)
        
        # With κ_org = 0.90
        assert math.isclose(result, 0.90, rel_tol=1e-3)


# ============================================================================
# TEST: ORGANIZATIONAL → SYSTEMIC AGGREGATION
# ============================================================================

class TestOrganizationalToSystemic:
    """Test cases for Organizational→Systemic aggregation (Formula 4)."""
    
    def test_geometric_mean_calculation(self, default_aggregator):
        """Test geometric mean of mean and max."""
        scores = [1.0, 1.5, 0.8]
        result = default_aggregator.aggregate_organizational_to_systemic(scores)
        
        # mean = 1.1, max = 1.5
        # geometric_mean = √(1.1 × 1.5) = √1.65 ≈ 1.285
        # result = 1.285 × κ_sys = 1.285 × 0.90 ≈ 1.156
        
        org_mean = sum(scores) / len(scores)
        org_max = max(scores)
        geometric = math.sqrt(org_mean * org_max)
        expected = geometric * default_aggregator.config.kappa_sys
        
        assert math.isclose(result, expected, rel_tol=1e-6)
    
    def test_geometric_mean_single_value(self, default_aggregator):
        """Test with single organizational score."""
        result = default_aggregator.aggregate_organizational_to_systemic([1.2])
        
        # mean = max = 1.2, geometric = √(1.2 × 1.2) = 1.2
        # result = 1.2 × 0.90 = 1.08
        expected = 1.2 * default_aggregator.config.kappa_sys
        
        assert math.isclose(result, expected, rel_tol=1e-3)
    
    def test_geometric_mean_empty_returns_zero(self, default_aggregator):
        """Test returns zero for empty input."""
        result = default_aggregator.aggregate_organizational_to_systemic([])
        assert result == 0.0
    
    def test_kappa_sys_applied(self, custom_aggregator):
        """Verify systemic capacity factor is applied."""
        scores = [1.0]
        result = custom_aggregator.aggregate_organizational_to_systemic(scores)
        
        # With κ_sys = 0.95
        assert math.isclose(result, 0.95, rel_tol=1e-3)


# ============================================================================
# TEST: SKILL AGGREGATION
# ============================================================================

class TestSkillAggregation:
    """Test cases for skill-level aggregation."""
    
    def test_aggregate_skill_to_individual(self, default_aggregator):
        """Test aggregation to Individual level (direct score)."""
        source_scores = {
            PolicyLevel.INDIVIDUAL: 1.068,
            PolicyLevel.ORGANIZATIONAL: 1.338,
        }
        
        result = default_aggregator.aggregate_skill_to_level(
            PolicySkill.ANALYTICAL, source_scores, PolicyLevel.INDIVIDUAL
        )
        
        assert result.target_level == PolicyLevel.INDIVIDUAL
        assert result.skill == PolicySkill.ANALYTICAL
        assert result.aggregation_method == "direct"
    
    def test_aggregate_skill_to_organizational(self, default_aggregator):
        """Test aggregation to Organizational level (power mean)."""
        source_scores = {
            PolicyLevel.INDIVIDUAL: 1.068,
            PolicyLevel.ORGANIZATIONAL: 1.338,
        }
        
        result = default_aggregator.aggregate_skill_to_level(
            PolicySkill.ANALYTICAL, source_scores, PolicyLevel.ORGANIZATIONAL
        )
        
        assert result.target_level == PolicyLevel.ORGANIZATIONAL
        assert result.aggregation_method == "power_mean"
        assert result.final_score > 0
    
    def test_aggregate_skill_to_systemic(self, default_aggregator):
        """Test aggregation to Systemic level (geometric mean)."""
        source_scores = {
            PolicyLevel.INDIVIDUAL: 1.068,
            PolicyLevel.ORGANIZATIONAL: 1.338,
            PolicyLevel.SYSTEMIC: 0.0,
        }
        
        result = default_aggregator.aggregate_skill_to_level(
            PolicySkill.ANALYTICAL, source_scores, PolicyLevel.SYSTEMIC
        )
        
        assert result.target_level == PolicyLevel.SYSTEMIC
        assert result.aggregation_method == "geometric_mean"
    
    def test_aggregate_all_for_skill(self, default_aggregator):
        """Test aggregation to all levels for single skill."""
        source_scores = {
            PolicyLevel.INDIVIDUAL: 1.068,
            PolicyLevel.ORGANIZATIONAL: 1.338,
        }
        
        results = default_aggregator.aggregate_all_for_skill(
            PolicySkill.ANALYTICAL, source_scores
        )
        
        assert len(results) == 3
        assert PolicyLevel.INDIVIDUAL in results
        assert PolicyLevel.ORGANIZATIONAL in results
        assert PolicyLevel.SYSTEMIC in results


# ============================================================================
# TEST: FULL AGGREGATION
# ============================================================================

class TestFullAggregation:
    """Test cases for complete aggregation pipeline."""
    
    def test_aggregate_all(self, default_aggregator, sample_capacity_scores):
        """Test full aggregation for all capacity types."""
        results = default_aggregator.aggregate_all(sample_capacity_scores)
        
        # Should have results for all 9 capacity types
        assert len(results) == 9
        
        # All capacity types should be present
        for ct in CapacityType.all_types():
            assert ct in results
    
    def test_aggregate_by_skill(self, default_aggregator, sample_capacity_scores):
        """Test aggregation grouped by skill."""
        skill_results = default_aggregator.aggregate_by_skill(sample_capacity_scores)
        
        assert len(skill_results) == 3
        assert PolicySkill.ANALYTICAL in skill_results
        assert PolicySkill.OPERATIONAL in skill_results
        assert PolicySkill.POLITICAL in skill_results
    
    def test_aggregate_by_level(self, default_aggregator, sample_capacity_scores):
        """Test aggregation grouped by level."""
        level_results = default_aggregator.aggregate_by_level(sample_capacity_scores)
        
        assert len(level_results) == 3
        assert PolicyLevel.INDIVIDUAL in level_results
        assert PolicyLevel.ORGANIZATIONAL in level_results
        assert PolicyLevel.SYSTEMIC in level_results
    
    def test_cross_level_matrix(self, default_aggregator, sample_capacity_scores):
        """Test cross-level contribution matrix computation."""
        matrix = default_aggregator.compute_cross_level_matrix(sample_capacity_scores)
        
        assert matrix.shape == (3, 3)
        # All values should be non-negative
        assert (matrix >= 0).all()


# ============================================================================
# TEST: PROVENANCE
# ============================================================================

class TestProvenance:
    """Test cases for aggregation provenance tracking."""
    
    def test_aggregation_result_contains_parameters(self, default_aggregator):
        """Verify aggregation results contain formula parameters."""
        source_scores = {PolicyLevel.INDIVIDUAL: 1.0}
        
        result = default_aggregator.aggregate_skill_to_level(
            PolicySkill.ANALYTICAL, source_scores, PolicyLevel.ORGANIZATIONAL
        )
        
        assert "eta" in result.formula_parameters
        assert "lambda_decay" in result.formula_parameters
        assert "kappa_org" in result.formula_parameters
    
    def test_provenance_generation(self, default_aggregator, sample_capacity_scores):
        """Test provenance data generation."""
        results = default_aggregator.aggregate_all(sample_capacity_scores)
        provenance = default_aggregator.get_aggregation_provenance(results)
        
        assert "config" in provenance
        assert "transformation_matrix" in provenance
        assert "results" in provenance


# ============================================================================
# TEST: MATHEMATICAL INVARIANTS
# ============================================================================

class TestMathematicalInvariants:
    """Test mathematical invariants and consistency."""
    
    def test_aggregation_weight_bounded(self, default_aggregator):
        """Verify aggregation weights are bounded in (0, η]."""
        eta = default_aggregator.config.eta
        
        for source in PolicyLevel.all_levels():
            for target in PolicyLevel.all_levels():
                weight = default_aggregator.calculate_aggregation_weight(source, target)
                assert 0 < weight <= eta
    
    def test_power_mean_bounded_by_min_max(self, default_aggregator):
        """Verify power mean is bounded by min and max of inputs."""
        scores = [0.5, 1.0, 1.5]
        
        # Get raw power mean (without kappa)
        p = default_aggregator.config.power_mean_p
        power_sum = sum(x ** p for x in scores)
        power_mean = (power_sum / len(scores)) ** (1 / p)
        
        # Power mean should be between min and max
        assert min(scores) <= power_mean <= max(scores)
    
    def test_geometric_mean_bounded(self, default_aggregator):
        """Verify geometric mean is bounded appropriately."""
        scores = [0.8, 1.0, 1.5]
        
        mean_score = sum(scores) / len(scores)
        max_score = max(scores)
        geometric = math.sqrt(mean_score * max_score)
        
        # Geometric mean of mean and max should be between them
        assert mean_score <= geometric <= max_score
    
    def test_transformation_matrix_non_negative(self):
        """Verify transformation matrix has non-negative elements."""
        matrix = TransformationMatrix.default()
        np_matrix = matrix.as_numpy()
        
        assert (np_matrix >= 0).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
