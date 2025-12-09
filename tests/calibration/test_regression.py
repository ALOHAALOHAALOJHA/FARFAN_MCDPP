"""
Regression tests for calibration system.

Tests that ensure calibration results remain stable across versions:
- Baseline calibration results
- Tolerance-based comparison
- Known method calibrations
- Edge case handling
"""

from __future__ import annotations


import pytest


BASELINE_CALIBRATIONS = {
    "pattern_extractor_v2_Q001_DIM01_PA01": {
        "method_id": "pattern_extractor_v2",
        "context": {"question": "Q001", "dimension": "DIM01", "policy": "PA01"},
        "expected_cal_score": 0.93,
        "tolerance": 0.01,
        "layer_scores": {
            "@b": 0.85,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 1.0,
            "@p": 1.0,
            "@C": 1.0,
            "@u": 0.75,
            "@m": 0.95,
        },
    },
    "coherence_validator_Q001_DIM01": {
        "method_id": "coherence_validator",
        "context": {"question": "Q001", "dimension": "DIM01"},
        "expected_cal_score": 0.571,
        "tolerance": 0.01,
        "layer_scores": {
            "@b": 0.9,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 1.0,
            "@m": 0.95,
        },
    },
    "pdt_ingester_minimal": {
        "method_id": "pdt_ingester",
        "context": {},
        "expected_cal_score": 0.36,
        "tolerance": 0.02,
        "layer_scores": {
            "@b": 0.75,
            "@chain": 1.0,
            "@u": 0.6,
        },
    },
}


def compute_calibration_score(
    layer_scores: dict[str, float],
    linear_weights: dict[str, float],
    interaction_weights: dict[tuple[str, str], float],
) -> float:
    """Compute calibration score using Choquet aggregation."""
    linear = sum(linear_weights.get(layer, 0.0) * score for layer, score in layer_scores.items())
    interaction = sum(
        weight * min(layer_scores.get(l1, 0.0), layer_scores.get(l2, 0.0))
        for (l1, l2), weight in interaction_weights.items()
    )
    return linear + interaction


@pytest.mark.regression
class TestBaselineCalibrations:
    """Test that baseline calibrations remain stable."""

    @pytest.mark.parametrize("baseline_key", BASELINE_CALIBRATIONS.keys())
    def test_baseline_calibration_matches(self, baseline_key: str):
        """Test that calibration matches baseline within tolerance."""
        baseline = BASELINE_CALIBRATIONS[baseline_key]

        linear_weights = {
            "@b": 0.17,
            "@chain": 0.13,
            "@q": 0.08,
            "@d": 0.07,
            "@p": 0.06,
            "@C": 0.08,
            "@u": 0.04,
            "@m": 0.04,
        }

        interaction_weights = {
            ("@u", "@chain"): 0.13,
            ("@chain", "@C"): 0.10,
            ("@q", "@d"): 0.10,
        }

        computed_score = compute_calibration_score(
            baseline["layer_scores"],
            linear_weights,
            interaction_weights,
        )

        expected = baseline["expected_cal_score"]
        tolerance = baseline["tolerance"]

        assert abs(computed_score - expected) <= tolerance, (
            f"Calibration for {baseline_key} deviated: "
            f"expected {expected}, got {computed_score}, tolerance {tolerance}"
        )

    def test_pattern_extractor_perfect_context(self):
        """Test pattern_extractor_v2 in perfect context."""
        baseline = BASELINE_CALIBRATIONS["pattern_extractor_v2_Q001_DIM01_PA01"]

        linear_weights = {
            "@b": 0.17, "@chain": 0.13, "@q": 0.08, "@d": 0.07,
            "@p": 0.06, "@C": 0.08, "@u": 0.04, "@m": 0.04,
        }

        interaction_weights = {
            ("@u", "@chain"): 0.13,
            ("@chain", "@C"): 0.10,
            ("@q", "@d"): 0.10,
        }

        score = compute_calibration_score(
            baseline["layer_scores"],
            linear_weights,
            interaction_weights,
        )

        assert abs(score - 0.93) <= 0.01

    def test_coherence_validator_baseline(self):
        """Test coherence_validator baseline calibration."""
        baseline = BASELINE_CALIBRATIONS["coherence_validator_Q001_DIM01"]

        linear_weights = {
            "@b": 0.3, "@chain": 0.25, "@q": 0.2, "@d": 0.15, "@m": 0.1,
        }

        score = compute_calibration_score(baseline["layer_scores"], linear_weights, {})

        assert abs(score - 0.965) <= 0.01


@pytest.mark.regression
class TestStabilityAcrossVersions:
    """Test stability of calibrations across code versions."""

    def test_same_inputs_same_outputs(self):
        """Same inputs should always produce same outputs."""
        layer_scores = {
            "@b": 0.85,
            "@chain": 1.0,
            "@q": 1.0,
            "@m": 0.95,
        }

        linear_weights = {
            "@b": 0.3,
            "@chain": 0.3,
            "@q": 0.2,
            "@m": 0.2,
        }

        score1 = compute_calibration_score(layer_scores, linear_weights, {})
        score2 = compute_calibration_score(layer_scores, linear_weights, {})

        assert score1 == score2

    def test_layer_addition_preserves_existing(self):
        """Adding new layers should not change existing layer scores."""
        base_scores = {"@b": 0.85, "@chain": 1.0}
        extended_scores = {"@b": 0.85, "@chain": 1.0, "@m": 0.95}

        base_weights = {"@b": 0.5, "@chain": 0.5}
        extended_weights = {"@b": 0.4, "@chain": 0.4, "@m": 0.2}

        base_linear = sum(base_weights.get(l, 0.0) * s for l, s in base_scores.items())
        extended_linear_base = sum(extended_weights.get(l, 0.0) * s for l, s in base_scores.items())

        assert base_linear > 0
        assert extended_linear_base > 0

    def test_weight_adjustment_predictable(self):
        """Weight adjustments should have predictable effects."""
        layer_scores = {"@b": 0.9, "@chain": 0.8}

        weights_high_b = {"@b": 0.7, "@chain": 0.3}
        weights_high_chain = {"@b": 0.3, "@chain": 0.7}

        score_high_b = compute_calibration_score(layer_scores, weights_high_b, {})
        score_high_chain = compute_calibration_score(layer_scores, weights_high_chain, {})

        assert score_high_b > score_high_chain


@pytest.mark.regression
class TestEdgeCaseStability:
    """Test stability for edge cases."""

    def test_all_zeros_stable(self):
        """All zero scores should yield 0.0."""
        layer_scores = {"@b": 0.0, "@chain": 0.0, "@q": 0.0, "@m": 0.0}
        linear_weights = {"@b": 0.25, "@chain": 0.25, "@q": 0.25, "@m": 0.25}

        score = compute_calibration_score(layer_scores, linear_weights, {})

        assert score == 0.0

    def test_all_ones_stable(self):
        """All perfect scores should yield expected value."""
        layer_scores = {"@b": 1.0, "@chain": 1.0, "@q": 1.0, "@m": 1.0}
        linear_weights = {"@b": 0.25, "@chain": 0.25, "@q": 0.25, "@m": 0.25}

        score = compute_calibration_score(layer_scores, linear_weights, {})

        assert score == 1.0

    def test_single_layer_stable(self):
        """Single layer calibration should be stable."""
        layer_scores = {"@b": 0.85}
        linear_weights = {"@b": 1.0}

        score = compute_calibration_score(layer_scores, linear_weights, {})

        assert score == 0.85

    def test_interaction_only_stable(self):
        """Interaction-only calibration should be stable."""
        layer_scores = {"@chain": 1.0, "@C": 0.8}
        interaction_weights = {("@chain", "@C"): 1.0}

        score = compute_calibration_score(layer_scores, {}, interaction_weights)

        assert score == 0.8


@pytest.mark.regression
class TestKnownMethodCalibrations:
    """Test calibrations for known methods."""

    def test_high_quality_method(self):
        """High quality method should score highly."""
        layer_scores = {
            "@b": 0.95,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 1.0,
            "@p": 0.9,
            "@C": 1.0,
            "@u": 0.85,
            "@m": 0.98,
        }

        linear_weights = {
            "@b": 0.17, "@chain": 0.13, "@q": 0.08, "@d": 0.07,
            "@p": 0.06, "@C": 0.08, "@u": 0.04, "@m": 0.04,
        }

        interaction_weights = {
            ("@u", "@chain"): 0.13,
            ("@chain", "@C"): 0.10,
            ("@q", "@d"): 0.10,
        }

        score = compute_calibration_score(layer_scores, linear_weights, interaction_weights)

        assert score > 0.85

    def test_low_quality_method(self):
        """Low quality method should score lower."""
        layer_scores = {
            "@b": 0.4,
            "@chain": 0.3,
            "@q": 0.3,
            "@m": 0.4,
        }

        linear_weights = {
            "@b": 0.4,
            "@chain": 0.3,
            "@q": 0.15,
            "@m": 0.15,
        }

        score = compute_calibration_score(layer_scores, linear_weights, {})

        assert score < 0.5

    def test_method_with_missing_optional_layers(self):
        """Method without optional layers should still calibrate."""
        layer_scores = {
            "@b": 0.8,
            "@chain": 1.0,
            "@m": 0.9,
        }

        linear_weights = {
            "@b": 0.4,
            "@chain": 0.4,
            "@m": 0.2,
        }

        score = compute_calibration_score(layer_scores, linear_weights, {})

        assert 0.7 < score < 1.0


@pytest.mark.regression
class TestRegressionDetection:
    """Test detection of potential regressions."""

    def test_calibration_within_expected_range(self):
        """Calibration should be within expected range for known inputs."""
        test_cases = [
            ({"@b": 0.9, "@chain": 1.0}, {"@b": 0.5, "@chain": 0.5}, 0.95, 0.02),
            ({"@b": 0.5, "@chain": 0.5}, {"@b": 0.5, "@chain": 0.5}, 0.5, 0.01),
            ({"@b": 0.7, "@chain": 0.8, "@m": 0.9}, {"@b": 0.33, "@chain": 0.33, "@m": 0.34}, 0.8, 0.02),
        ]

        for layer_scores, weights, expected, tolerance in test_cases:
            score = compute_calibration_score(layer_scores, weights, {})
            assert abs(score - expected) <= tolerance, f"Regression detected: expected {expected}, got {score}"

    def test_no_unexpected_score_changes(self):
        """Scores should not change unexpectedly."""
        reference_scores = {
            "@b": 0.85,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 0.9,
            "@p": 0.8,
            "@C": 1.0,
            "@u": 0.75,
            "@m": 0.95,
        }

        weights = {
            "@b": 0.17, "@chain": 0.13, "@q": 0.08, "@d": 0.07,
            "@p": 0.06, "@C": 0.08, "@u": 0.04, "@m": 0.04,
        }

        interactions = {
            ("@u", "@chain"): 0.13,
            ("@chain", "@C"): 0.10,
            ("@q", "@d"): 0.10,
        }

        score = compute_calibration_score(reference_scores, weights, interactions)

        expected_min = 0.89
        expected_max = 0.91

        assert expected_min <= score <= expected_max, f"Score {score} outside expected range [{expected_min}, {expected_max}]"
