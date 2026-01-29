"""
Test Suite for Base Capacity Scoring Module
===========================================

Tests for the base capacity scoring implementation from the
Wu, Ramesh & Howlett (2015) Policy Capacity Framework.

Tests cover:
1. Formula weight validation (α + β + γ = 1.0)
2. Base score calculation accuracy
3. Epistemology → Capacity type mapping
4. Method classification confidence
5. Batch scoring operations
6. Edge cases and error handling

Mathematical Model Under Test:
    C_base(e, l, o) = α × E(e) + β × L(l) + γ × O(o)
    
    Where:
    - α = 0.4, β = 0.35, γ = 0.25
    - E(e) = epistemology weight
    - L(l) = level weight
    - O(o) = output type weight

Author: F.A.R.F.A.N. Test Team
Version: 1.0.0
"""

import math
import pytest
from typing import Dict, List, Any

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    EpistemologicalLevel,
    CapacityScore,
    MethodCapacityMapping,
)
from farfan_pipeline.capacity.base_score import (
    BaseCapacityScorer,
    CapacityScoringConfig,
    EpistemologyWeights,
    LevelWeights,
    OutputTypeWeights,
    CapacityMappingRule,
    DEFAULT_MAPPING_RULES,
)


# ============================================================================
# FIXTURE DEFINITIONS
# ============================================================================

@pytest.fixture
def default_scorer() -> BaseCapacityScorer:
    """Create a scorer with default configuration."""
    return BaseCapacityScorer()


@pytest.fixture
def custom_scorer() -> BaseCapacityScorer:
    """Create a scorer with custom configuration."""
    config = CapacityScoringConfig(
        alpha=0.5,
        beta=0.3,
        gamma=0.2,
        normalize_scores=False,
    )
    return BaseCapacityScorer(config=config)


@pytest.fixture
def sample_method_data() -> List[Dict[str, Any]]:
    """Sample method data for batch testing."""
    return [
        {
            "method_id": "M001",
            "class_name": "TextMiningEngine",
            "method_name": "extract_evidence",
            "file_path": "embedding_policy.py",
            "epistemological_level": "N1-EMP",
            "output_type": "FACT",
            "classification_confidence": 0.9,
            "classification_evidence": ["Method name starts with 'extract_'"],
        },
        {
            "method_id": "M002",
            "class_name": "BayesianNumericalAnalyzer",
            "method_name": "calculate_posterior",
            "file_path": "bayesian_multilevel_system.py",
            "epistemological_level": "N2-INF",
            "output_type": "PARAMETER",
            "classification_confidence": 0.85,
            "classification_evidence": ["Class is in analytical N2 list"],
        },
        {
            "method_id": "M003",
            "class_name": "PolicyContradictionDetector",
            "method_name": "detect_conflicts",
            "file_path": "contradiction_deteccion.py",
            "epistemological_level": "N3-AUD",
            "output_type": "CONSTRAINT",
            "classification_confidence": 0.8,
            "classification_evidence": ["Method name contains 'detect'"],
        },
    ]


# ============================================================================
# TEST: CONFIGURATION VALIDATION
# ============================================================================

class TestCapacityScoringConfig:
    """Test cases for CapacityScoringConfig."""
    
    def test_default_config_weights_sum_to_one(self):
        """Verify default formula weights sum to 1.0."""
        config = CapacityScoringConfig.default()
        total = config.alpha + config.beta + config.gamma
        assert math.isclose(total, 1.0, rel_tol=1e-9), \
            f"Default weights sum to {total}, expected 1.0"
    
    def test_custom_config_validates_weights(self):
        """Verify weight validation raises on invalid sums."""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            CapacityScoringConfig(alpha=0.5, beta=0.5, gamma=0.5)
    
    def test_high_analytical_emphasis_config(self):
        """Test alternative configuration with analytical emphasis."""
        config = CapacityScoringConfig.high_analytical_emphasis()
        assert config.alpha == 0.5
        assert config.beta == 0.3
        assert config.gamma == 0.2
        assert math.isclose(config.alpha + config.beta + config.gamma, 1.0)
    
    def test_balanced_config(self):
        """Test balanced configuration."""
        config = CapacityScoringConfig.balanced()
        assert math.isclose(config.alpha + config.beta + config.gamma, 1.0)
        # Balanced should have roughly equal weights
        weights = [config.alpha, config.beta, config.gamma]
        assert max(weights) - min(weights) < 0.05


class TestWeightConfigurations:
    """Test cases for individual weight configurations."""
    
    def test_epistemology_weights_coverage(self):
        """Verify all epistemologies have weights defined."""
        weights = EpistemologyWeights()
        
        expected_epistemologies = [
            "Empirismo positivista",
            "Bayesianismo subjetivista",
            "Falsacionismo popperiano",
            "Instrumentalismo",
            "Reflexividad crítica",
        ]
        
        for ep in expected_epistemologies:
            weight = weights.get_weight(ep)
            assert 0 < weight <= 1.0, f"Invalid weight {weight} for {ep}"
    
    def test_level_weights_coverage(self):
        """Verify all levels have weights defined."""
        weights = LevelWeights()
        
        expected_levels = ["N0-INFRA", "N1-EMP", "N2-INF", "N3-AUD", "N4-META"]
        
        for level in expected_levels:
            weight = weights.get_weight(level)
            assert 0 < weight <= 3.0, f"Invalid weight {weight} for {level}"
    
    def test_level_weights_ordering(self):
        """Verify level weights follow expected ordering N0 < N1 < N2 < N3 < N4."""
        weights = LevelWeights()
        
        assert weights.n0_infra < weights.n1_emp
        assert weights.n1_emp < weights.n2_inf
        assert weights.n2_inf < weights.n3_aud
        assert weights.n3_aud < weights.n4_meta
    
    def test_output_type_weights_coverage(self):
        """Verify all output types have weights defined."""
        weights = OutputTypeWeights()
        
        expected_outputs = ["FACT", "PARAMETER", "CONSTRAINT"]
        
        for output in expected_outputs:
            weight = weights.get_weight(output)
            assert 0 < weight <= 2.0, f"Invalid weight {weight} for {output}"
    
    def test_constraint_highest_output_weight(self):
        """Verify CONSTRAINT has highest output weight (audit importance)."""
        weights = OutputTypeWeights()
        
        assert weights.constraint > weights.parameter
        assert weights.parameter > weights.fact


# ============================================================================
# TEST: BASE SCORE CALCULATION
# ============================================================================

class TestBaseScoreCalculation:
    """Test cases for base capacity score calculation."""
    
    def test_calculate_base_score_n1_emp(self, default_scorer):
        """Test score calculation for N1-EMP empirical level."""
        score = default_scorer.calculate_base_score(
            epistemology="Empirismo positivista",
            method_level="N1-EMP",
            output_type="FACT",
        )
        
        # Manual calculation:
        # E = 0.85, L = 1.0, O = 0.8
        # C_base = 0.4 * 0.85 + 0.35 * 1.0 + 0.25 * 0.8 = 0.34 + 0.35 + 0.2 = 0.89
        # With normalization (1.2): 0.89 * 1.2 = 1.068
        
        assert 1.0 < score < 1.2, f"N1-EMP score {score} outside expected range"
    
    def test_calculate_base_score_n2_inf(self, default_scorer):
        """Test score calculation for N2-INF inferential level."""
        score = default_scorer.calculate_base_score(
            epistemology="Bayesianismo subjetivista",
            method_level="N2-INF",
            output_type="PARAMETER",
        )
        
        # E = 1.0, L = 1.5, O = 1.0
        # C_base = 0.4 * 1.0 + 0.35 * 1.5 + 0.25 * 1.0 = 0.4 + 0.525 + 0.25 = 1.175
        # With normalization: 1.175 * 1.2 = 1.41
        
        assert 1.3 < score < 1.5, f"N2-INF score {score} outside expected range"
    
    def test_calculate_base_score_n3_aud(self, default_scorer):
        """Test score calculation for N3-AUD audit level."""
        score = default_scorer.calculate_base_score(
            epistemology="Falsacionismo popperiano",
            method_level="N3-AUD",
            output_type="CONSTRAINT",
        )
        
        # E = 0.92, L = 2.0, O = 1.2
        # C_base = 0.4 * 0.92 + 0.35 * 2.0 + 0.25 * 1.2 = 0.368 + 0.7 + 0.3 = 1.368
        # With normalization: 1.368 * 1.2 = 1.6416
        
        assert 1.5 < score < 1.8, f"N3-AUD score {score} outside expected range"
    
    def test_calculate_base_score_without_normalization(self, custom_scorer):
        """Test score calculation without normalization factor."""
        score = custom_scorer.calculate_base_score(
            epistemology="Empirismo positivista",
            method_level="N1-EMP",
            output_type="FACT",
        )
        
        # Custom config: α=0.5, β=0.3, γ=0.2, no normalization
        # E = 0.85, L = 1.0, O = 0.8
        # C_base = 0.5 * 0.85 + 0.3 * 1.0 + 0.2 * 0.8 = 0.425 + 0.3 + 0.16 = 0.885
        
        assert 0.8 < score < 0.95, f"Non-normalized score {score} outside expected range"
    
    def test_score_ordering_by_level(self, default_scorer):
        """Verify scores increase with epistemological level sophistication."""
        n1_score = default_scorer.calculate_base_score(
            "Empirismo positivista", "N1-EMP", "FACT"
        )
        n2_score = default_scorer.calculate_base_score(
            "Bayesianismo subjetivista", "N2-INF", "PARAMETER"
        )
        n3_score = default_scorer.calculate_base_score(
            "Falsacionismo popperiano", "N3-AUD", "CONSTRAINT"
        )
        
        assert n1_score < n2_score < n3_score, \
            f"Score ordering violated: N1={n1_score}, N2={n2_score}, N3={n3_score}"


# ============================================================================
# TEST: CAPACITY TYPE MAPPING
# ============================================================================

class TestCapacityTypeMapping:
    """Test cases for method → capacity type mapping."""
    
    def test_n1_emp_maps_to_ca_i(self, default_scorer):
        """Verify N1-EMP maps to CA-I (Individual Analytical)."""
        capacity = default_scorer.map_to_capacity_type("N1-EMP")
        assert capacity == CapacityType.CA_I
    
    def test_n2_inf_primary_maps_to_ca_o(self, default_scorer):
        """Verify N2-INF primary mapping is CA-O."""
        capacity = default_scorer.map_to_capacity_type(
            "N2-INF",
            class_name="BayesianNumericalAnalyzer",
            method_name="calculate_posterior",
        )
        assert capacity == CapacityType.CA_O
    
    def test_n2_inf_secondary_maps_to_co_o(self, default_scorer):
        """Verify N2-INF secondary mapping (operational classes) is CO-O."""
        capacity = default_scorer.map_to_capacity_type(
            "N2-INF",
            class_name="TeoriaCambio",
            method_name="compute_change",
        )
        assert capacity == CapacityType.CO_O
    
    def test_n3_aud_primary_maps_to_co_s(self, default_scorer):
        """Verify N3-AUD primary mapping is CO-S."""
        capacity = default_scorer.map_to_capacity_type(
            "N3-AUD",
            class_name="FinancialAuditor",
            method_name="validate_allocation",
        )
        assert capacity == CapacityType.CO_S
    
    def test_n3_aud_secondary_maps_to_cp_o(self, default_scorer):
        """Verify N3-AUD secondary mapping (political keywords) is CP-O."""
        capacity = default_scorer.map_to_capacity_type(
            "N3-AUD",
            class_name="SomeValidator",
            method_name="detect_contradictions",
        )
        assert capacity == CapacityType.CP_O
    
    def test_unknown_level_defaults_to_ca_o(self, default_scorer):
        """Verify unknown levels default to organizational analytical."""
        capacity = default_scorer.map_to_capacity_type("UNKNOWN-LEVEL")
        assert capacity == CapacityType.CA_O


# ============================================================================
# TEST: METHOD SCORING
# ============================================================================

class TestMethodScoring:
    """Test cases for complete method scoring."""
    
    def test_score_method_creates_valid_mapping(self, default_scorer):
        """Verify score_method returns valid MethodCapacityMapping."""
        mapping = default_scorer.score_method(
            method_id="M001",
            class_name="TextMiningEngine",
            method_name="extract_evidence",
            file_path="embedding_policy.py",
            epistemological_level="N1-EMP",
            output_type="FACT",
            classification_confidence=0.9,
            classification_evidence=["Test evidence"],
        )
        
        assert isinstance(mapping, MethodCapacityMapping)
        assert mapping.method_id == "M001"
        assert mapping.capacity_type == "CA-I"
        assert mapping.base_score > 0
        assert mapping.classification_confidence == 0.9
    
    def test_score_methods_batch(self, default_scorer, sample_method_data):
        """Test batch scoring of multiple methods."""
        mappings = default_scorer.score_methods_batch(sample_method_data)
        
        assert len(mappings) == 3
        
        # Verify first mapping (N1-EMP → CA-I)
        assert mappings[0].capacity_type == "CA-I"
        
        # Verify second mapping (N2-INF → CA-O)
        assert mappings[1].capacity_type == "CA-O"
        
        # Verify third mapping (N3-AUD → CP-O, detect keyword)
        assert mappings[2].capacity_type == "CP-O"
    
    def test_calculate_capacity_score(self, default_scorer, sample_method_data):
        """Test capacity score aggregation for a type."""
        mappings = default_scorer.score_methods_batch(sample_method_data)
        
        # Get CA-I capacity score (should have 1 method)
        ca_i_score = default_scorer.calculate_capacity_score(
            CapacityType.CA_I, mappings
        )
        
        assert ca_i_score.capacity_type == CapacityType.CA_I
        assert ca_i_score.method_count == 1
        assert ca_i_score.raw_score > 0
    
    def test_calculate_all_capacity_scores(self, default_scorer, sample_method_data):
        """Test calculation of all 9 capacity type scores."""
        mappings = default_scorer.score_methods_batch(sample_method_data)
        scores = default_scorer.calculate_all_capacity_scores(mappings)
        
        # Should have entry for all 9 capacity types
        assert len(scores) == 9
        
        # All types should be present
        for ct in CapacityType.all_types():
            assert ct in scores


# ============================================================================
# TEST: STATISTICS AND DISTRIBUTION
# ============================================================================

class TestStatisticsAndDistribution:
    """Test cases for statistical analysis functions."""
    
    def test_get_distribution(self, default_scorer, sample_method_data):
        """Test method distribution across capacity types."""
        mappings = default_scorer.score_methods_batch(sample_method_data)
        distribution = default_scorer.get_distribution(mappings)
        
        # Should have all capacity type codes
        assert "CA-I" in distribution
        assert "CA-O" in distribution
        assert "CP-O" in distribution
        
        # Check counts
        assert distribution["CA-I"] == 1
        assert distribution["CA-O"] == 1
        assert distribution["CP-O"] == 1
    
    def test_get_statistics(self, default_scorer, sample_method_data):
        """Test comprehensive statistics generation."""
        mappings = default_scorer.score_methods_batch(sample_method_data)
        stats = default_scorer.get_statistics(mappings)
        
        assert stats["total_methods"] == 3
        assert "by_capacity_type" in stats
        assert "by_skill" in stats
        assert "by_level" in stats
        assert "by_epistemology" in stats
        assert "confidence_distribution" in stats
        assert "score_statistics" in stats


# ============================================================================
# TEST: EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_method_list(self, default_scorer):
        """Test handling of empty method list."""
        mappings = default_scorer.score_methods_batch([])
        assert mappings == []
    
    def test_unknown_epistemology_handled(self, default_scorer):
        """Test handling of unknown epistemology."""
        score = default_scorer.calculate_base_score(
            epistemology="Unknown Epistemology",
            method_level="N2-INF",
            output_type="PARAMETER",
        )
        # Should use default weight (0.75)
        assert score > 0
    
    def test_unknown_output_type_handled(self, default_scorer):
        """Test handling of unknown output type."""
        score = default_scorer.calculate_base_score(
            epistemology="Empirismo positivista",
            method_level="N1-EMP",
            output_type="UNKNOWN_OUTPUT",
        )
        # Should use default weight (0.9)
        assert score > 0
    
    def test_capacity_score_for_empty_type(self, default_scorer):
        """Test capacity score calculation when type has no methods."""
        mappings = []  # Empty
        score = default_scorer.calculate_capacity_score(
            CapacityType.CA_S, mappings  # CA-S typically has zero methods
        )
        
        assert score.method_count == 0
        assert score.raw_score == 0.0
        assert score.confidence == 0.0


# ============================================================================
# TEST: MATHEMATICAL INVARIANTS
# ============================================================================

class TestMathematicalInvariants:
    """Test mathematical invariants and consistency."""
    
    def test_score_non_negative(self, default_scorer):
        """Verify all scores are non-negative."""
        test_cases = [
            ("Empirismo positivista", "N1-EMP", "FACT"),
            ("Bayesianismo subjetivista", "N2-INF", "PARAMETER"),
            ("Falsacionismo popperiano", "N3-AUD", "CONSTRAINT"),
        ]
        
        for ep, level, output in test_cases:
            score = default_scorer.calculate_base_score(ep, level, output)
            assert score >= 0, f"Negative score {score} for {ep}, {level}, {output}"
    
    def test_weight_sum_invariant_preserved(self, default_scorer):
        """Verify weight sum invariant is preserved in scorer."""
        config = default_scorer.config
        total = config.alpha + config.beta + config.gamma
        assert math.isclose(total, 1.0, rel_tol=1e-9)
    
    def test_capacity_types_exhaustive(self):
        """Verify all skill×level combinations are covered."""
        all_combinations = set()
        for skill in PolicySkill.all_skills():
            for level in PolicyLevel.all_levels():
                all_combinations.add((skill, level))
        
        covered_combinations = {
            (ct.skill, ct.level) for ct in CapacityType.all_types()
        }
        
        assert all_combinations == covered_combinations, \
            f"Missing combinations: {all_combinations - covered_combinations}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
