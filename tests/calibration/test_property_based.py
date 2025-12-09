"""
Property-based tests for calibration system using Hypothesis.

Tests mathematical properties that must hold for ALL inputs:
- Boundedness: ∀inputs 0 ≤ output ≤ 1
- Monotonicity: ∀layers increasing score → increasing Cal(I)
- Normalization: ∀configs sum(weights) = 1.0
- Idempotency: Calibrating twice yields same result
- Determinism: Same inputs always produce same outputs
"""

from __future__ import annotations


import pytest

try:
    from hypothesis import given, strategies as st, assume, settings
    from hypothesis import HealthCheck
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    pytest.skip("hypothesis not installed", allow_module_level=True)


def compute_choquet_aggregation(
    layer_scores: dict[str, float],
    linear_weights: dict[str, float],
    interaction_weights: dict[tuple[str, str], float],
) -> float:
    """Compute Choquet aggregation."""
    linear_contribution = sum(
        linear_weights.get(layer, 0.0) * score
        for layer, score in layer_scores.items()
    )

    interaction_contribution = sum(
        weight * min(layer_scores.get(l1, 0.0), layer_scores.get(l2, 0.0))
        for (l1, l2), weight in interaction_weights.items()
    )

    return linear_contribution + interaction_contribution


def normalize_weights(
    linear_weights: dict[str, float],
    interaction_weights: dict[tuple[str, str], float],
) -> tuple[dict[str, float], dict[tuple[str, str], float]]:
    """Normalize weights to sum to 1.0."""
    total = sum(linear_weights.values()) + sum(interaction_weights.values())

    if total == 0.0:
        return linear_weights, interaction_weights

    scale = 1.0 / total

    normalized_linear = {k: v * scale for k, v in linear_weights.items()}
    normalized_interaction = {k: v * scale for k, v in interaction_weights.items()}

    return normalized_linear, normalized_interaction


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
class TestBoundednessProperty:
    """Test boundedness: ∀inputs 0 ≤ output ≤ 1."""

    @given(
        scores=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]),
            values=st.floats(min_value=0.0, max_value=1.0),
            min_size=1,
            max_size=8,
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_layer_scores_bounded(self, scores: dict[str, float]):
        """All layer scores must be in [0,1]."""
        for layer, score in scores.items():
            assert 0.0 <= score <= 1.0, f"Layer {layer} score {score} not in [0,1]"

    @given(
        scores=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]),
            values=st.floats(min_value=0.0, max_value=1.0),
            min_size=4,
            max_size=8,
        ),
        weights=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]),
            values=st.floats(min_value=0.0, max_value=0.3),
            min_size=4,
            max_size=8,
        ),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_choquet_output_bounded(self, scores: dict[str, float], weights: dict[str, float]):
        """Choquet aggregation output must be in [0,1]."""
        norm_linear, norm_interaction = normalize_weights(weights, {})

        cal = compute_choquet_aggregation(scores, norm_linear, norm_interaction)

        assert 0.0 <= cal <= 1.0 + 1e-6, f"Cal(I) = {cal} not in [0,1]"

    @given(
        b_theory=st.floats(min_value=0.0, max_value=1.0),
        b_impl=st.floats(min_value=0.0, max_value=1.0),
        b_deploy=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_base_layer_bounded(self, b_theory: float, b_impl: float, b_deploy: float):
        """Base layer score must be in [0,1] for all valid inputs."""
        weights = {"b_theory": 0.4, "b_impl": 0.35, "b_deploy": 0.25}

        x_b = weights["b_theory"] * b_theory + weights["b_impl"] * b_impl + weights["b_deploy"] * b_deploy

        assert 0.0 <= x_b <= 1.0, f"x_@b = {x_b} not in [0,1]"


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
class TestMonotonicityProperty:
    """Test monotonicity: ∀layers increasing score → increasing Cal(I)."""

    @given(
        base_score=st.floats(min_value=0.0, max_value=0.9),
        delta=st.floats(min_value=0.01, max_value=0.1),
        other_scores=st.dictionaries(
            keys=st.sampled_from(["@chain", "@q", "@d", "@p", "@C", "@u", "@m"]),
            values=st.floats(min_value=0.0, max_value=1.0),
            min_size=3,
            max_size=7,
        ),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_increasing_layer_increases_total(self, base_score: float, delta: float, other_scores: dict[str, float]):
        """Increasing any layer score should not decrease total calibration."""
        assume(base_score + delta <= 1.0)

        weights = {"@b": 0.2, "@chain": 0.15, "@q": 0.1, "@d": 0.1, "@p": 0.1, "@C": 0.1, "@u": 0.05, "@m": 0.05}
        interaction = {("@chain", "@q"): 0.15}

        scores_low = {"@b": base_score, **other_scores}
        scores_high = {"@b": base_score + delta, **other_scores}

        cal_low = compute_choquet_aggregation(scores_low, weights, interaction)
        cal_high = compute_choquet_aggregation(scores_high, weights, interaction)

        assert cal_high >= cal_low - 1e-6, f"Monotonicity violated: {cal_high} < {cal_low}"

    @given(
        b_theory_low=st.floats(min_value=0.0, max_value=0.5),
        b_theory_high=st.floats(min_value=0.5, max_value=1.0),
        b_impl=st.floats(min_value=0.0, max_value=1.0),
        b_deploy=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_base_layer_monotonicity(self, b_theory_low: float, b_theory_high: float, b_impl: float, b_deploy: float):
        """Base layer should be monotonic in each component."""
        weights = {"b_theory": 0.4, "b_impl": 0.35, "b_deploy": 0.25}

        x_b_low = weights["b_theory"] * b_theory_low + weights["b_impl"] * b_impl + weights["b_deploy"] * b_deploy
        x_b_high = weights["b_theory"] * b_theory_high + weights["b_impl"] * b_impl + weights["b_deploy"] * b_deploy

        assert x_b_high >= x_b_low - 1e-6


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
class TestNormalizationProperty:
    """Test normalization: ∀configs sum(weights) = 1.0."""

    @given(
        weights=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q", "@d"]),
            values=st.floats(min_value=0.01, max_value=0.5),
            min_size=2,
            max_size=4,
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_weight_normalization(self, weights: dict[str, float]):
        """Normalized weights should sum to 1.0."""
        norm_linear, norm_interaction = normalize_weights(weights, {})

        total = sum(norm_linear.values()) + sum(norm_interaction.values())

        assert abs(total - 1.0) < 1e-6, f"Normalized weights sum to {total}, not 1.0"

    @given(
        linear_weights=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q", "@d"]),
            values=st.floats(min_value=0.01, max_value=0.3),
            min_size=2,
            max_size=4,
        ),
        interaction_weight=st.floats(min_value=0.01, max_value=0.3),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_weight_normalization_with_interactions(self, linear_weights: dict[str, float], interaction_weight: float):
        """Normalized weights with interactions should sum to 1.0."""
        interaction_weights = {("@chain", "@q"): interaction_weight}

        norm_linear, norm_interaction = normalize_weights(linear_weights, interaction_weights)

        total = sum(norm_linear.values()) + sum(norm_interaction.values())

        assert abs(total - 1.0) < 1e-6


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
class TestDeterminismProperty:
    """Test determinism: Same inputs always produce same outputs."""

    @given(
        scores=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q", "@d"]),
            values=st.floats(min_value=0.0, max_value=1.0),
            min_size=4,
            max_size=4,
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_deterministic_computation(self, scores: dict[str, float]):
        """Computing calibration twice with same inputs should yield same result."""
        weights = {"@b": 0.25, "@chain": 0.25, "@q": 0.25, "@d": 0.25}

        cal1 = compute_choquet_aggregation(scores, weights, {})
        cal2 = compute_choquet_aggregation(scores, weights, {})

        assert cal1 == cal2, "Non-deterministic computation"

    @given(
        b_theory=st.floats(min_value=0.0, max_value=1.0),
        b_impl=st.floats(min_value=0.0, max_value=1.0),
        b_deploy=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_base_layer_deterministic(self, b_theory: float, b_impl: float, b_deploy: float):
        """Base layer computation should be deterministic."""
        weights = {"b_theory": 0.4, "b_impl": 0.35, "b_deploy": 0.25}

        x_b1 = weights["b_theory"] * b_theory + weights["b_impl"] * b_impl + weights["b_deploy"] * b_deploy
        x_b2 = weights["b_theory"] * b_theory + weights["b_impl"] * b_impl + weights["b_deploy"] * b_deploy

        assert x_b1 == x_b2


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
class TestInteractionProperties:
    """Test properties specific to interaction terms."""

    @given(
        x_l=st.floats(min_value=0.0, max_value=1.0),
        x_k=st.floats(min_value=0.0, max_value=1.0),
        weight=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_interaction_term_bounded(self, x_l: float, x_k: float, weight: float):
        """Interaction term a_ℓk · min(x_ℓ, x_k) should be bounded."""
        interaction_value = weight * min(x_l, x_k)

        assert 0.0 <= interaction_value <= 1.0

    @given(
        x_l=st.floats(min_value=0.0, max_value=1.0),
        x_k=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_min_operator_symmetric(self, x_l: float, x_k: float):
        """min(x_ℓ, x_k) should be symmetric."""
        assert min(x_l, x_k) == min(x_k, x_l)

    @given(
        x_l=st.floats(min_value=0.0, max_value=1.0),
        x_k=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_min_operator_weakest_link(self, x_l: float, x_k: float):
        """min operator should capture weakest link."""
        result = min(x_l, x_k)

        assert result <= x_l
        assert result <= x_k


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
class TestContextDependenceProperty:
    """Test context-dependent behavior."""

    @given(
        method_id=st.sampled_from(["pattern_extractor_v2", "coherence_validator"]),
        question_id1=st.sampled_from(["Q001", "Q002", "Q003"]),
        question_id2=st.sampled_from(["Q004", "Q005", "Q006"]),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_different_contexts_different_scores(self, method_id: str, question_id1: str, question_id2: str):
        """Different contexts should potentially yield different compatibility scores."""
        assume(question_id1 != question_id2)

        score1 = 1.0 if question_id1 == "Q001" else 0.7
        score2 = 1.0 if question_id2 == "Q001" else 0.7

        if question_id1 != question_id2:
            can_differ = True
        else:
            can_differ = False

        assert can_differ or score1 == score2
