"""
Tests for Adaptive Meso-Level Scoring

Validates that the adaptive scoring mechanism:
1. Is mathematically correct
2. Provides improved sensitivity vs fixed penalty approach
3. Handles dispersion and convergence scenarios appropriately
4. Maintains numerical stability
"""

import pytest
from farfan_pipeline.phases.Phase_04_five_six_seven.adaptive_meso_scoring import (
    AdaptiveMesoScoring,
    AdaptiveScoringConfig,
    ScoringMetrics,
    create_adaptive_scorer,
)


class TestAdaptiveMesoScoring:
    """Test suite for adaptive meso-level scoring."""

    @pytest.fixture
    def scorer(self) -> AdaptiveMesoScoring:
        """Create default scorer instance."""
        return AdaptiveMesoScoring()

    def test_perfect_convergence(self, scorer: AdaptiveMesoScoring) -> None:
        """Test perfect convergence scenario (all scores equal)."""
        scores = [2.5, 2.5, 2.5, 2.5]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Should have no penalty
        assert details["metrics"]["cv"] == pytest.approx(0.0)
        assert details["metrics"]["dispersion_index"] == pytest.approx(0.0)
        assert details["metrics"]["scenario_type"] == "convergence"
        assert details["penalty_computation"]["penalty_factor"] == pytest.approx(1.0)
        assert adjusted_score == pytest.approx(details["weighted_score"])
        assert adjusted_score == pytest.approx(2.5)

    def test_mild_convergence(self, scorer: AdaptiveMesoScoring) -> None:
        """Test mild convergence with small variance."""
        scores = [2.3, 2.4, 2.5, 2.6]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Should have minimal penalty
        assert details["metrics"]["cv"] < 0.1
        assert details["metrics"]["scenario_type"] == "convergence"
        assert details["penalty_computation"]["penalty_factor"] > 0.95

        # Should be more lenient than fixed approach for convergence
        improvement = details["improvement_over_fixed"]
        assert improvement["is_more_lenient"] or abs(improvement["score_difference"]) < 0.01

    def test_high_dispersion(self, scorer: AdaptiveMesoScoring) -> None:
        """Test high dispersion scenario."""
        scores = [0.5, 1.5, 2.5, 3.0]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Should have significant penalty
        assert details["metrics"]["cv"] > 0.4
        assert details["metrics"]["scenario_type"] == "high_dispersion"
        penalty_factor = details["penalty_computation"]["penalty_factor"]
        assert penalty_factor < 0.85

        # Should be stricter than fixed approach for high dispersion
        improvement = details["improvement_over_fixed"]
        assert improvement["is_stricter"]

    def test_extreme_dispersion(self, scorer: AdaptiveMesoScoring) -> None:
        """Test extreme dispersion (full range)."""
        scores = [0.0, 1.0, 2.0, 3.0]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Should have maximum penalty
        assert details["metrics"]["cv"] > 0.6
        assert details["metrics"]["scenario_type"] == "extreme_dispersion"
        assert details["metrics"]["dispersion_index"] == 1.0
        penalty_factor = details["penalty_computation"]["penalty_factor"]
        assert penalty_factor < 0.75

        # Should apply non-linear scaling
        shape_factor = details["penalty_computation"]["shape_factor"]
        assert shape_factor > 1.0

    def test_bimodal_distribution(self, scorer: AdaptiveMesoScoring) -> None:
        """Test bimodal distribution pattern."""
        scores = [0.5, 0.8, 2.8, 3.0]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Should detect bimodal pattern and apply boost
        shape_class = details["metrics"]["shape_classification"]
        if shape_class == "bimodal":
            shape_factor = details["penalty_computation"]["shape_factor"]
            assert shape_factor > 1.0

        # Should have strong penalty
        penalty_factor = details["penalty_computation"]["penalty_factor"]
        assert penalty_factor < 0.85

    def test_weighted_scoring(self, scorer: AdaptiveMesoScoring) -> None:
        """Test that weights are properly applied."""
        scores = [1.0, 2.0, 2.0, 3.0]
        weights = [0.1, 0.3, 0.3, 0.3]

        adjusted_score, details = scorer.compute_adjusted_score(scores, weights)

        # Verify weighted average
        expected_weighted = sum(s * w for s, w in zip(scores, weights, strict=True))
        assert abs(details["weighted_score"] - expected_weighted) < 1e-6

        # Verify penalty applied to weighted score
        penalty_factor = details["penalty_computation"]["penalty_factor"]
        expected_adjusted = expected_weighted * penalty_factor
        assert abs(adjusted_score - expected_adjusted) < 1e-6

    def test_mathematical_correctness(self, scorer: AdaptiveMesoScoring) -> None:
        """Test mathematical properties are preserved."""
        scores = [1.5, 2.0, 2.5]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Verify variance calculation
        mean = details["metrics"]["mean"]
        variance = details["metrics"]["variance"]
        expected_variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        assert abs(variance - expected_variance) < 1e-9

        # Verify std_dev = sqrt(variance)
        std_dev = details["metrics"]["std_dev"]
        assert abs(std_dev - variance**0.5) < 1e-9

        # Verify coefficient of variation
        cv = details["metrics"]["cv"]
        expected_cv = std_dev / mean if mean > 0 else 0
        assert abs(cv - expected_cv) < 1e-9

        # Verify bounds
        assert 0 <= adjusted_score <= 3.0
        assert 0 <= details["penalty_computation"]["penalty_factor"] <= 1.0
        assert 0 <= details["coherence"] <= 1.0

    def test_single_score_edge_case(self, scorer: AdaptiveMesoScoring) -> None:
        """Test edge case with single score."""
        scores = [2.5]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Should have perfect coherence and no penalty
        assert details["metrics"]["variance"] == 0.0
        assert details["penalty_computation"]["penalty_factor"] == 1.0
        assert details["coherence"] == 1.0
        assert adjusted_score == 2.5

    def test_two_identical_scores(self, scorer: AdaptiveMesoScoring) -> None:
        """Test edge case with two identical scores."""
        scores = [2.0, 2.0]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Should have no penalty
        assert details["metrics"]["variance"] == 0.0
        assert details["penalty_computation"]["penalty_factor"] == 1.0
        assert adjusted_score == 2.0

    def test_two_opposite_scores(self, scorer: AdaptiveMesoScoring) -> None:
        """Test edge case with maximum opposition."""
        scores = [0.0, 3.0]
        adjusted_score, details = scorer.compute_adjusted_score(scores)

        # Should have maximum dispersion and strong penalty
        assert details["metrics"]["dispersion_index"] == 1.0
        penalty_factor = details["penalty_computation"]["penalty_factor"]
        assert penalty_factor < 0.85

    def test_sensitivity_multipliers(self, scorer: AdaptiveMesoScoring) -> None:
        """Test that sensitivity multipliers are applied correctly."""
        # Convergence scenario
        convergence_scores = [2.0, 2.1, 2.2]
        _, conv_details = scorer.compute_adjusted_score(convergence_scores)
        assert conv_details["penalty_computation"]["sensitivity_multiplier"] == 0.5

        # High dispersion scenario
        dispersion_scores = [0.5, 1.5, 2.5, 3.0]
        _, disp_details = scorer.compute_adjusted_score(dispersion_scores)
        assert disp_details["penalty_computation"]["sensitivity_multiplier"] >= 1.5

    def test_improvement_over_fixed_approach(self, scorer: AdaptiveMesoScoring) -> None:
        """Test that adaptive approach improves over fixed penalty."""
        test_cases = [
            # (scores, expected_improvement_type)
            ([2.4, 2.5, 2.6], "more_lenient"),  # Convergence: should be more lenient
            ([0.5, 1.5, 2.5, 3.0], "stricter"),  # High dispersion: should be stricter
            ([2.0, 2.1, 2.2, 2.3], "more_lenient"),  # Good convergence: more lenient
        ]

        for scores, expected_type in test_cases:
            _, details = scorer.compute_adjusted_score(scores)
            improvement = details["improvement_over_fixed"]

            if expected_type == "more_lenient":
                assert improvement["is_more_lenient"] or abs(improvement["score_difference"]) < 0.01
            else:
                assert improvement["is_stricter"]

    def test_invalid_inputs(self, scorer: AdaptiveMesoScoring) -> None:
        """Test error handling for invalid inputs."""
        # Empty scores
        with pytest.raises(ValueError, match="Empty scores"):
            scorer.compute_adjusted_score([])

        # Mismatched weights
        with pytest.raises(ValueError, match="Weight length mismatch"):
            scorer.compute_adjusted_score([1.0, 2.0], weights=[0.5])

        # Weights don't sum to 1
        with pytest.raises(ValueError, match="sum to 1.0"):
            scorer.compute_adjusted_score([1.0, 2.0], weights=[0.3, 0.5])

    def test_custom_config(self) -> None:
        """Test scorer with custom configuration."""
        config = AdaptiveScoringConfig(
            base_penalty_weight=0.4, convergence_multiplier=0.3, extreme_dispersion_multiplier=2.5
        )
        scorer = AdaptiveMesoScoring(config)

        # Test that config is applied
        assert scorer.config.base_penalty_weight == 0.4

        # Test extreme case with custom config
        scores = [0.0, 1.0, 2.0, 3.0]
        _, details = scorer.compute_adjusted_score(scores)

        # Should use custom multiplier
        assert details["penalty_computation"]["sensitivity_multiplier"] == 2.5

    def test_create_adaptive_scorer_factory(self) -> None:
        """Test factory function."""
        scorer = create_adaptive_scorer(base_penalty_weight=0.4, extreme_shape_factor=2.0)

        assert isinstance(scorer, AdaptiveMesoScoring)
        assert scorer.config.base_penalty_weight == 0.4
        assert scorer.config.extreme_shape_factor == 2.0

    def test_sensitivity_analysis(self, scorer: AdaptiveMesoScoring) -> None:
        """Test sensitivity analysis functionality."""
        scores = [1.5, 2.0, 2.5, 3.0]
        analysis = scorer.get_sensitivity_analysis(scores)

        # Should have all required sections
        assert "base_analysis" in analysis
        assert "sensitivity_to_perturbations" in analysis
        assert "robustness_metrics" in analysis

        # Should compute perturbation impacts
        perturbations = analysis["sensitivity_to_perturbations"]
        assert "max_positive_impact" in perturbations
        assert "max_negative_impact" in perturbations
        assert "avg_abs_impact" in perturbations

    def test_metrics_computation(self, scorer: AdaptiveMesoScoring) -> None:
        """Test metrics computation in isolation."""
        scores = [1.0, 2.0, 2.5, 3.0]
        metrics = scorer.compute_metrics(scores)

        assert isinstance(metrics, ScoringMetrics)
        assert metrics.mean > 0
        assert metrics.variance >= 0
        assert metrics.std_dev >= 0
        assert metrics.coefficient_variation >= 0
        assert 0 <= metrics.dispersion_index <= 1
        assert metrics.scenario_type in [
            "convergence",
            "moderate",
            "high_dispersion",
            "extreme_dispersion",
        ]

    def test_penalty_factor_bounds(self, scorer: AdaptiveMesoScoring) -> None:
        """Test that penalty factor is always bounded properly."""
        # Test various score patterns
        test_patterns = [
            [3.0, 3.0, 3.0, 3.0],  # All max
            [0.0, 0.0, 0.0, 0.0],  # All min
            [0.0, 1.5, 3.0],  # Wide spread
            [1.0, 1.1, 1.2],  # Tight convergence
            [0.0, 0.5, 2.5, 3.0],  # Mixed
        ]

        for scores in test_patterns:
            # Handle all-zero case specially
            if all(s == 0.0 for s in scores):
                continue

            _, details = scorer.compute_adjusted_score(scores)
            penalty_factor = details["penalty_computation"]["penalty_factor"]

            # Should always be in [0.5, 1.0]
            assert (
                0.5 <= penalty_factor <= 1.0
            ), f"Penalty factor {penalty_factor} out of bounds for {scores}"

            # Should never apply more than 50% penalty
            assert penalty_factor >= 0.5


class TestAdaptiveScoringComparison:
    """Compare adaptive vs fixed penalty approaches."""

    @pytest.fixture
    def scorer(self) -> AdaptiveMesoScoring:
        """Create scorer."""
        return AdaptiveMesoScoring()

    def test_convergence_scenarios_more_lenient(self, scorer: AdaptiveMesoScoring) -> None:
        """Verify adaptive approach is more lenient for convergence."""
        convergence_patterns = [
            [2.4, 2.5, 2.6],
            [2.0, 2.1, 2.2, 2.3],
            [1.8, 1.9, 2.0, 2.1],
        ]

        for scores in convergence_patterns:
            _, details = scorer.compute_adjusted_score(scores)
            improvement = details["improvement_over_fixed"]

            # Should be more lenient (higher score) or equivalent
            assert improvement["score_difference"] >= -0.01

    def test_dispersion_scenarios_stricter(self, scorer: AdaptiveMesoScoring) -> None:
        """Verify adaptive approach is stricter for dispersion."""
        dispersion_patterns = [
            [0.5, 1.5, 2.5, 3.0],
            [0.0, 1.0, 2.0, 3.0],
            [0.5, 0.8, 2.8, 3.0],
        ]

        for scores in dispersion_patterns:
            _, details = scorer.compute_adjusted_score(scores)
            improvement = details["improvement_over_fixed"]

            # Should be stricter (lower score)
            assert improvement["score_difference"] < 0.01


@pytest.mark.updated
class TestMathematicalCorrectness:
    """Comprehensive mathematical correctness tests."""

    def test_variance_formula(self) -> None:
        """Test variance calculation is mathematically correct."""
        scorer = AdaptiveMesoScoring()
        scores = [1.0, 2.0, 3.0, 4.0, 5.0]

        metrics = scorer.compute_metrics(scores)

        # Manual calculation
        mean = sum(scores) / len(scores)
        expected_variance = sum((s - mean) ** 2 for s in scores) / len(scores)

        assert abs(metrics.variance - expected_variance) < 1e-9

    def test_std_dev_formula(self) -> None:
        """Test standard deviation is sqrt of variance."""
        scorer = AdaptiveMesoScoring()
        scores = [0.5, 1.5, 2.5]

        metrics = scorer.compute_metrics(scores)

        assert abs(metrics.std_dev - (metrics.variance**0.5)) < 1e-9

    def test_coefficient_of_variation(self) -> None:
        """Test CV calculation."""
        scorer = AdaptiveMesoScoring()
        scores = [2.0, 2.5, 3.0]

        metrics = scorer.compute_metrics(scores)
        expected_cv = metrics.std_dev / metrics.mean

        assert abs(metrics.coefficient_variation - expected_cv) < 1e-9

    def test_dispersion_index(self) -> None:
        """Test dispersion index is normalized range."""
        scorer = AdaptiveMesoScoring()
        scores = [1.0, 2.0, 3.0]

        metrics = scorer.compute_metrics(scores)
        score_range = max(scores) - min(scores)
        expected_di = score_range / 3.0  # MAX_SCORE = 3.0

        assert abs(metrics.dispersion_index - expected_di) < 1e-9
