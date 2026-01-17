"""
Tests for Mathematical Foundation
=================================

Tests verify the academic theorems and mathematical properties
underlying the scoring system.

Test Categories:
1. Wilson Score Interval Tests (Wilson 1927, JASA)
2. Weighted Aggregation Tests (Convexity Theorem)
3. Dempster-Shafer Combination Tests
4. Confidence Calibration Tests
5. Invariant Verification Tests

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
Date: 2025-12-11
"""

import math
import pytest
from typing import Any

# DELETED_MODULE: from farfan_pipeline.analysis.scoring.mathematical_foundation import (
    wilson_score_interval,
    weighted_aggregation,
    dempster_combination,
    calibrate_confidence,
    compute_score_variance,
    validate_scoring_invariants,
    verify_convexity_property,
    verify_wilson_monotonicity,
)


# =============================================================================
# WILSON SCORE INTERVAL TESTS
# =============================================================================


class TestWilsonScoreInterval:
    """Tests for Wilson score interval (Wilson 1927, JASA)."""

    def test_wilson_basic_properties(self) -> None:
        """Test basic properties of Wilson interval."""
        # Test with p=0.75, n=100
        lower, upper = wilson_score_interval(0.75, 100, 0.05)

        # Interval should contain the point estimate
        assert lower <= 0.75 <= upper

        # Interval should be in [0, 1]
        assert 0.0 <= lower <= 1.0
        assert 0.0 <= upper <= 1.0

        # Upper bound should be greater than lower bound
        assert lower < upper

    def test_wilson_extreme_cases(self) -> None:
        """Test Wilson interval at extreme proportions."""
        # p=0 (all failures)
        lower, upper = wilson_score_interval(0.0, 100, 0.05)
        assert lower == 0.0
        assert upper > 0.0  # Should have positive upper bound

        # p=1 (all successes)
        lower, upper = wilson_score_interval(1.0, 100, 0.05)
        assert lower < 1.0  # Should have lower bound less than 1
        assert math.isclose(upper, 1.0, abs_tol=1e-10)  # Should be approximately 1

    def test_wilson_monotonicity(self) -> None:
        """Test Wilson interval monotonicity property (O'Neill 2021)."""
        # For p̂₁ < p̂₂, should have [L₁, U₁] ⊆ [L₂, U₂]
        assert verify_wilson_monotonicity(0.5, 0.7, 100)
        assert verify_wilson_monotonicity(0.3, 0.8, 50)
        assert verify_wilson_monotonicity(0.1, 0.9, 200)

    def test_wilson_sample_size_effect(self) -> None:
        """Test that larger n gives narrower intervals."""
        p_hat = 0.6

        lower_n50, upper_n50 = wilson_score_interval(p_hat, 50, 0.05)
        lower_n200, upper_n200 = wilson_score_interval(p_hat, 200, 0.05)

        width_n50 = upper_n50 - lower_n50
        width_n200 = upper_n200 - lower_n200

        # Larger sample size should give narrower interval
        assert width_n200 < width_n50

    def test_wilson_confidence_level_effect(self) -> None:
        """Test that higher confidence gives wider intervals."""
        p_hat = 0.7
        n = 100

        lower_95, upper_95 = wilson_score_interval(p_hat, n, 0.05)
        lower_99, upper_99 = wilson_score_interval(p_hat, n, 0.01)

        width_95 = upper_95 - lower_95
        width_99 = upper_99 - lower_99

        # Higher confidence (99% vs 95%) should give wider interval
        assert width_99 > width_95

    @pytest.mark.parametrize(
        "p_hat,n",
        [
            (0.5, 30),
            (0.75, 50),
            (0.25, 100),
            (0.9, 200),
        ],
    )
    def test_wilson_contains_estimate(self, p_hat: float, n: int) -> None:
        """Test that Wilson interval always contains point estimate."""
        lower, upper = wilson_score_interval(p_hat, n, 0.05)
        assert lower <= p_hat <= upper


# =============================================================================
# WEIGHTED AGGREGATION TESTS
# =============================================================================


class TestWeightedAggregation:
    """Tests for weighted aggregation (Convexity Theorem)."""

    def test_convexity_property(self) -> None:
        """Test Theorem 2: min(sᵢ) ≤ weighted_mean ≤ max(sᵢ)."""
        scores = [0.6, 0.8, 0.7, 0.9]
        weights = [0.25, 0.25, 0.25, 0.25]

        result = weighted_aggregation(scores, weights)

        assert min(scores) <= result <= max(scores)
        assert verify_convexity_property(scores, weights)

    def test_idempotency(self) -> None:
        """Test that identical scores give that score as result."""
        score = 0.75
        scores = [score] * 5
        weights = [0.2] * 5

        result = weighted_aggregation(scores, weights)

        assert math.isclose(result, score, abs_tol=1e-6)

    def test_monotonicity(self) -> None:
        """Test that increasing a score increases the result."""
        scores1 = [0.5, 0.6, 0.7]
        scores2 = [0.5, 0.8, 0.7]  # Increased middle score
        weights = [0.33, 0.34, 0.33]

        result1 = weighted_aggregation(scores1, weights)
        result2 = weighted_aggregation(scores2, weights)

        assert result2 > result1

    def test_boundedness(self) -> None:
        """Test that result is in [0, 1] when all scores are."""
        scores = [0.3, 0.7, 0.9, 0.1, 0.5]
        weights = [0.2, 0.2, 0.2, 0.2, 0.2]

        result = weighted_aggregation(scores, weights)

        assert 0.0 <= result <= 1.0

    def test_validation_rejects_invalid_scores(self) -> None:
        """Test that validation rejects out-of-range scores."""
        scores = [0.5, 1.5, 0.7]  # 1.5 is out of range
        weights = [0.33, 0.34, 0.33]

        with pytest.raises(ValueError, match="must be in"):
            weighted_aggregation(scores, weights, validate=True)

    def test_validation_rejects_invalid_weights(self) -> None:
        """Test that validation rejects weights not summing to 1."""
        scores = [0.5, 0.6, 0.7]
        weights = [0.5, 0.5, 0.5]  # Sum > 1

        with pytest.raises(ValueError, match="must sum to 1"):
            weighted_aggregation(scores, weights, validate=True)

    @pytest.mark.parametrize(
        "scores,weights",
        [
            ([0.8, 0.6], [0.7, 0.3]),
            ([0.5, 0.5, 0.5], [0.33, 0.33, 0.34]),
            ([0.9, 0.1, 0.5, 0.7], [0.25, 0.25, 0.25, 0.25]),
        ],
    )
    def test_various_configurations(self, scores: list[float], weights: list[float]) -> None:
        """Test weighted aggregation with various configurations."""
        result = weighted_aggregation(scores, weights)

        # Verify convexity
        assert min(scores) <= result <= max(scores)

        # Verify boundedness
        assert 0.0 <= result <= 1.0


# =============================================================================
# DEMPSTER-SHAFER TESTS
# =============================================================================


class TestDempsterCombination:
    """Tests for Dempster-Shafer belief combination."""

    def test_commutativity(self) -> None:
        """Test Theorem 3: m₁ ⊕ m₂ = m₂ ⊕ m₁."""
        m1 = {
            frozenset(["A"]): 0.6,
            frozenset(["B"]): 0.4,
        }
        m2 = {
            frozenset(["A"]): 0.5,
            frozenset(["A", "B"]): 0.5,
        }

        result_12 = dempster_combination(m1, m2)
        result_21 = dempster_combination(m2, m1)

        # Should be commutative
        assert set(result_12.keys()) == set(result_21.keys())
        for focal in result_12:
            assert math.isclose(result_12[focal], result_21[focal], abs_tol=1e-6)

    def test_normalization(self) -> None:
        """Test that combined belief function sums to 1."""
        m1 = {
            frozenset(["A"]): 0.7,
            frozenset(["B"]): 0.3,
        }
        m2 = {
            frozenset(["A"]): 0.6,
            frozenset(["B"]): 0.4,
        }

        result = dempster_combination(m1, m2)

        # Sum of all masses should be 1
        total = sum(result.values())
        assert math.isclose(total, 1.0, abs_tol=1e-6)

    def test_consensus_reinforcement(self) -> None:
        """Test that agreement increases belief."""
        m1 = {
            frozenset(["A"]): 0.6,
            frozenset(["B"]): 0.4,
        }
        m2 = {
            frozenset(["A"]): 0.7,
            frozenset(["B"]): 0.3,
        }

        result = dempster_combination(m1, m2)

        # A has agreement in both sources, should have increased belief
        assert result[frozenset(["A"])] > max(m1[frozenset(["A"])], m2[frozenset(["A"])])

    def test_total_conflict_raises(self) -> None:
        """Test that total conflict is detected and raises error."""
        m1 = {frozenset(["A"]): 1.0}
        m2 = {frozenset(["B"]): 1.0}

        with pytest.raises(ValueError, match="Total conflict"):
            dempster_combination(m1, m2)


# =============================================================================
# CONFIDENCE CALIBRATION TESTS
# =============================================================================


class TestConfidenceCalibration:
    """Tests for confidence calibration."""

    def test_calibration_increases_with_sample_size(self) -> None:
        """Test that calibration factor increases with sample size."""
        confidence = 0.85

        calibrated_n50 = calibrate_confidence(confidence, 50, 0.95)
        calibrated_n200 = calibrate_confidence(confidence, 200, 0.95)

        # Both should be close to original for large n
        assert calibrated_n50 >= confidence
        assert calibrated_n200 >= confidence

        # Larger n should give calibrated value closer to original
        assert abs(calibrated_n200 - confidence) < abs(calibrated_n50 - confidence)

    def test_calibration_bounded(self) -> None:
        """Test that calibrated confidence stays in [0, 1]."""
        for conf in [0.5, 0.7, 0.9, 0.95]:
            for n in [30, 100, 500]:
                calibrated = calibrate_confidence(conf, n, 0.95)
                assert 0.0 <= calibrated <= 1.0


# =============================================================================
# VARIANCE ANALYSIS TESTS
# =============================================================================


class TestScoreVariance:
    """Tests for score variance computation."""

    def test_variance_for_certain_scores(self) -> None:
        """Test that certain scores (0 or 1) have zero variance."""
        scores = {"c1": 1.0, "c2": 1.0, "c3": 1.0}
        weights = {"c1": 0.33, "c2": 0.34, "c3": 0.33}

        variance = compute_score_variance(scores, weights)

        assert math.isclose(variance, 0.0, abs_tol=1e-6)

    def test_variance_maximum_at_half(self) -> None:
        """Test that variance is maximum when all scores are 0.5."""
        scores_half = {"c1": 0.5, "c2": 0.5}
        scores_extreme = {"c1": 0.9, "c2": 0.1}
        weights = {"c1": 0.5, "c2": 0.5}

        var_half = compute_score_variance(scores_half, weights)
        var_extreme = compute_score_variance(scores_extreme, weights)

        # Variance is maximum at p=0.5 for binomial
        assert var_half > var_extreme


# =============================================================================
# INVARIANT VALIDATION TESTS
# =============================================================================


class TestInvariantValidation:
    """Tests for scoring invariant validation."""

    def test_all_invariants_satisfied(self) -> None:
        """Test that valid scoring satisfies all invariants."""
        score = 0.75
        threshold = 0.70
        ci = (0.65, 0.85)

        invariants = validate_scoring_invariants(score, threshold, ci)

        # All invariants should be satisfied
        assert all(invariants.values())

    def test_detect_score_out_of_bounds(self) -> None:
        """Test detection of score outside [0, 1]."""
        score = 1.5  # Out of bounds
        threshold = 0.70
        ci = (0.65, 0.85)

        invariants = validate_scoring_invariants(score, threshold, ci)

        assert not invariants["INV-SC-001_score_bounded"]

    def test_detect_ci_not_containing_score(self) -> None:
        """Test detection of CI not containing score."""
        score = 0.75
        threshold = 0.70
        ci = (0.80, 0.90)  # Doesn't contain 0.75

        invariants = validate_scoring_invariants(score, threshold, ci)

        assert not invariants["INV-SC-004_ci_contains_score"]

    def test_detect_ci_misordered(self) -> None:
        """Test detection of misordered CI bounds."""
        score = 0.75
        threshold = 0.70
        ci = (0.85, 0.65)  # Upper < lower

        invariants = validate_scoring_invariants(score, threshold, ci)

        assert not invariants["INV-SC-003_ci_ordered"]


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestMathematicalIntegration:
    """Integration tests combining multiple theorems."""

    def test_complete_scoring_pipeline(self) -> None:
        """Test complete scoring pipeline with all mathematical components."""
        # 1. Compute component scores
        scores = [0.8, 0.7, 0.75]
        weights = [0.5, 0.3, 0.2]

        # 2. Weighted aggregation (Theorem 2)
        final_score = weighted_aggregation(scores, weights)
        assert verify_convexity_property(scores, weights)

        # 3. Compute Wilson CI (Theorem 1)
        lower, upper = wilson_score_interval(final_score, 100, 0.05)

        # 4. Validate all invariants
        invariants = validate_scoring_invariants(final_score, 0.70, (lower, upper))
        assert all(invariants.values())

    def test_300_questions_mathematical_stability(self) -> None:
        """Test mathematical stability across 300 questions."""
        import random

        random.seed(42)  # Deterministic

        for i in range(300):
            # Generate random but valid scores and weights
            n_components = random.randint(2, 5)
            scores = [random.uniform(0.3, 0.9) for _ in range(n_components)]
            weights = [random.random() for _ in range(n_components)]
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]  # Normalize

            # Apply weighted aggregation
            final_score = weighted_aggregation(scores, weights)

            # Verify convexity holds
            assert verify_convexity_property(scores, weights)

            # Compute Wilson CI
            n = random.randint(30, 200)
            lower, upper = wilson_score_interval(final_score, n, 0.05)

            # Verify invariants
            invariants = validate_scoring_invariants(final_score, 0.60, (lower, upper))
            assert all(invariants.values()), f"Question {i+1} failed invariants: {invariants}"


# =============================================================================
# PYTEST MARKERS
# =============================================================================

pytestmark = pytest.mark.updated
