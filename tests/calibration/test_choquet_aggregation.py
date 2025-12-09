"""
Unit tests for Choquet Aggregation computation.

Tests the 2-additive Choquet integral fusion operator:
- Linear weight terms: Σ(a_ℓ · x_ℓ)
- Interaction weight terms: Σ(a_ℓk · min(x_ℓ, x_k))
- Weight normalization: Σ(a_ℓ) + Σ(a_ℓk) = 1.0
- Bounded output: Cal(I) ∈ [0,1]
- Monotonicity: ∂Cal/∂x_ℓ ≥ 0

Formula: Cal(I) = Σ_{ℓ ∈ L(M)} a_ℓ · x_ℓ(I) + Σ_{(ℓ,k) ∈ S_int} a_ℓk · min(x_ℓ(I), x_k(I))
"""

from __future__ import annotations

from typing import Any



def compute_choquet_aggregation(
    layer_scores: dict[str, float],
    linear_weights: dict[str, float],
    interaction_weights: dict[tuple[str, str], float],
) -> float:
    """
    Compute Choquet aggregation with linear and interaction terms.
    
    Args:
        layer_scores: Layer scores (x_ℓ)
        linear_weights: Linear weights (a_ℓ)
        interaction_weights: Interaction weights (a_ℓk)
    
    Returns:
        Aggregated calibration score Cal(I)
    """
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
    """
    Normalize weights to sum to 1.0.
    
    Returns:
        (normalized_linear, normalized_interaction)
    """
    total = sum(linear_weights.values()) + sum(interaction_weights.values())

    if abs(total - 1.0) < 1e-6:
        return linear_weights, interaction_weights

    scale = 1.0 / total

    normalized_linear = {k: v * scale for k, v in linear_weights.items()}
    normalized_interaction = {k: v * scale for k, v in interaction_weights.items()}

    return normalized_linear, normalized_interaction


class TestChoquetLinearTerms:
    """Test linear contribution computation."""

    def test_linear_terms_only(self, sample_layer_scores_full: dict[str, float]):
        """Test Choquet with only linear terms (no interactions)."""
        linear_weights = {
            "@b": 0.25,
            "@chain": 0.25,
            "@q": 0.25,
            "@m": 0.25,
        }

        score = compute_choquet_aggregation(sample_layer_scores_full, linear_weights, {})

        expected = (
            0.25 * 0.85
            + 0.25 * 1.0
            + 0.25 * 1.0
            + 0.25 * 0.95
        )

        assert abs(score - expected) < 1e-6

    def test_linear_contribution_bounded(self, sample_layer_scores_full: dict[str, float], sample_choquet_weights: dict[str, Any]):
        """Linear contribution should be bounded."""
        linear_contrib = sum(
            sample_choquet_weights["linear"].get(layer, 0.0) * score
            for layer, score in sample_layer_scores_full.items()
        )

        assert 0.0 <= linear_contrib <= 1.0


class TestChoquetInteractionTerms:
    """Test interaction contribution computation."""

    def test_interaction_terms_only(self):
        """Test Choquet with only interaction terms."""
        layer_scores = {"@u": 0.6, "@chain": 1.0}
        interaction_weights = {("@u", "@chain"): 1.0}

        score = compute_choquet_aggregation(layer_scores, {}, interaction_weights)

        expected = 1.0 * min(0.6, 1.0)

        assert abs(score - expected) < 1e-6

    def test_interaction_min_operator(self):
        """Interaction terms should use min operator."""
        layer_scores = {"@u": 0.6, "@chain": 1.0}
        interaction_weights = {("@u", "@chain"): 0.5}

        score = compute_choquet_aggregation(layer_scores, {}, interaction_weights)

        expected = 0.5 * min(0.6, 1.0)
        assert abs(score - 0.3) < 1e-6

    def test_multiple_interactions(self):
        """Test multiple interaction terms."""
        layer_scores = {"@u": 0.6, "@chain": 1.0, "@C": 1.0, "@q": 1.0, "@d": 0.9}
        interaction_weights = {
            ("@u", "@chain"): 0.3,
            ("@chain", "@C"): 0.2,
            ("@q", "@d"): 0.5,
        }

        score = compute_choquet_aggregation(layer_scores, {}, interaction_weights)

        expected = 0.3 * min(0.6, 1.0) + 0.2 * min(1.0, 1.0) + 0.5 * min(1.0, 0.9)

        assert abs(score - expected) < 1e-6

    def test_interaction_contribution_bounded(self, sample_layer_scores_full: dict[str, float], sample_choquet_weights: dict[str, Any]):
        """Interaction contribution should be bounded."""
        interaction_contrib = sum(
            weight * min(sample_layer_scores_full.get(l1, 0.0), sample_layer_scores_full.get(l2, 0.0))
            for (l1, l2), weight in sample_choquet_weights["interaction"].items()
        )

        assert 0.0 <= interaction_contrib <= 1.0


class TestChoquetFullAggregation:
    """Test complete Choquet aggregation with linear and interaction terms."""

    def test_full_aggregation(self, sample_layer_scores_full: dict[str, float], sample_choquet_weights: dict[str, Any]):
        """Test complete Choquet aggregation."""
        score = compute_choquet_aggregation(
            sample_layer_scores_full,
            sample_choquet_weights["linear"],
            sample_choquet_weights["interaction"],
        )

        assert 0.0 <= score <= 1.0

    def test_worked_example_from_docs(self):
        """Test worked example from mathematical foundations document."""
        layer_scores = {
            "@b": 0.9,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 1.0,
            "@p": 0.8,
            "@C": 1.0,
            "@u": 0.6,
            "@m": 0.95,
        }

        linear_weights = {
            "@b": 0.167,
            "@chain": 0.125,
            "@q": 0.083,
            "@d": 0.067,
            "@p": 0.058,
            "@C": 0.083,
            "@u": 0.042,
            "@m": 0.042,
        }

        interaction_weights = {
            ("@u", "@chain"): 0.125,
            ("@chain", "@C"): 0.10,
            ("@q", "@d"): 0.067,
        }

        score = compute_choquet_aggregation(layer_scores, linear_weights, interaction_weights)

        linear_part = (
            0.167 * 0.9 + 0.125 * 1.0 + 0.083 * 1.0 + 0.067 * 1.0
            + 0.058 * 0.8 + 0.083 * 1.0 + 0.042 * 0.6 + 0.042 * 0.95
        )

        interaction_part = (
            0.125 * min(0.6, 1.0) + 0.10 * min(1.0, 1.0) + 0.067 * min(1.0, 1.0)
        )

        expected = linear_part + interaction_part

        assert abs(score - expected) < 1e-3

    def test_aggregation_with_normalized_weights(self, sample_layer_scores_full: dict[str, float]):
        """Test aggregation with normalized weights."""
        linear_weights = {
            "@b": 0.2,
            "@chain": 0.15,
            "@q": 0.1,
            "@m": 0.05,
        }

        interaction_weights = {
            ("@chain", "@q"): 0.5,
        }

        norm_linear, norm_interaction = normalize_weights(linear_weights, interaction_weights)

        score = compute_choquet_aggregation(sample_layer_scores_full, norm_linear, norm_interaction)

        assert 0.0 <= score <= 1.0


class TestWeightNormalization:
    """Test weight normalization."""

    def test_already_normalized_weights(self, sample_choquet_weights: dict[str, Any]):
        """Already normalized weights should remain unchanged."""
        norm_linear, norm_interaction = normalize_weights(
            sample_choquet_weights["linear"],
            sample_choquet_weights["interaction"],
        )

        total = sum(norm_linear.values()) + sum(norm_interaction.values())

        assert abs(total - 1.0) < 1e-6

    def test_unnormalized_weights(self):
        """Unnormalized weights should be normalized."""
        linear_weights = {"@b": 0.4, "@chain": 0.3, "@q": 0.2}
        interaction_weights = {("@chain", "@q"): 0.3}

        norm_linear, norm_interaction = normalize_weights(linear_weights, interaction_weights)

        total = sum(norm_linear.values()) + sum(norm_interaction.values())

        assert abs(total - 1.0) < 1e-6

    def test_normalization_preserves_ratios(self):
        """Normalization should preserve weight ratios."""
        linear_weights = {"@b": 0.4, "@chain": 0.2}
        interaction_weights = {}

        norm_linear, _ = normalize_weights(linear_weights, interaction_weights)

        ratio = norm_linear["@b"] / norm_linear["@chain"]
        expected_ratio = 0.4 / 0.2

        assert abs(ratio - expected_ratio) < 1e-6


class TestChoquetProperties:
    """Test mathematical properties of Choquet aggregation."""

    def test_boundedness_all_zeros(self):
        """All zero scores should yield 0.0."""
        layer_scores = {f"@{i}": 0.0 for i in range(8)}
        linear_weights = {f"@{i}": 0.125 for i in range(8)}
        interaction_weights = {}

        score = compute_choquet_aggregation(layer_scores, linear_weights, interaction_weights)

        assert abs(score - 0.0) < 1e-6

    def test_boundedness_all_ones(self):
        """All perfect scores should yield <= 1.0."""
        layer_scores = {f"@{i}": 1.0 for i in range(8)}
        linear_weights = {f"@{i}": 0.1 for i in range(8)}
        interaction_weights = {(f"@{i}", f"@{j}"): 0.05 for i in range(3) for j in range(i + 1, 3)}

        norm_linear, norm_interaction = normalize_weights(linear_weights, interaction_weights)

        score = compute_choquet_aggregation(layer_scores, norm_linear, norm_interaction)

        assert score <= 1.0 + 1e-6

    def test_monotonicity_increasing_single_layer(self, sample_choquet_weights: dict[str, Any]):
        """Increasing a single layer score should not decrease total score."""
        base_scores = {
            "@b": 0.5,
            "@chain": 0.5,
            "@q": 0.5,
            "@d": 0.5,
            "@p": 0.5,
            "@C": 0.5,
            "@u": 0.5,
            "@m": 0.5,
        }

        score_low = compute_choquet_aggregation(
            base_scores,
            sample_choquet_weights["linear"],
            sample_choquet_weights["interaction"],
        )

        high_scores = base_scores.copy()
        high_scores["@b"] = 0.9

        score_high = compute_choquet_aggregation(
            high_scores,
            sample_choquet_weights["linear"],
            sample_choquet_weights["interaction"],
        )

        assert score_high >= score_low

    def test_interaction_captures_weakest_link(self):
        """Interaction term should capture 'weakest link' dynamic."""
        layer_scores_balanced = {"@u": 0.8, "@chain": 0.8}
        layer_scores_imbalanced = {"@u": 0.6, "@chain": 1.0}

        interaction_weights = {("@u", "@chain"): 1.0}

        score_balanced = compute_choquet_aggregation(layer_scores_balanced, {}, interaction_weights)
        score_imbalanced = compute_choquet_aggregation(layer_scores_imbalanced, {}, interaction_weights)

        assert score_balanced > score_imbalanced


class TestStandardInteractionConfigurations:
    """Test standard interaction configurations."""

    def test_unit_chain_interaction(self):
        """Test @u × @chain interaction: plan quality × sound wiring."""
        layer_scores = {"@u": 0.6, "@chain": 1.0}
        interaction_weights = {("@u", "@chain"): 0.15}

        score = compute_choquet_aggregation(layer_scores, {}, interaction_weights)

        expected = 0.15 * min(0.6, 1.0)
        assert abs(score - expected) < 1e-6

    def test_chain_congruence_interaction(self):
        """Test @chain × @C interaction: chain integrity × ensemble validity."""
        layer_scores = {"@chain": 1.0, "@C": 1.0}
        interaction_weights = {("@chain", "@C"): 0.12}

        score = compute_choquet_aggregation(layer_scores, {}, interaction_weights)

        expected = 0.12 * min(1.0, 1.0)
        assert abs(score - expected) < 1e-6

    def test_question_dimension_interaction(self):
        """Test @q × @d interaction: question-dimension alignment."""
        layer_scores = {"@q": 1.0, "@d": 0.9}
        interaction_weights = {("@q", "@d"): 0.08}

        score = compute_choquet_aggregation(layer_scores, {}, interaction_weights)

        expected = 0.08 * min(1.0, 0.9)
        assert abs(score - expected) < 1e-6

    def test_dimension_policy_interaction(self):
        """Test @d × @p interaction: dimension-policy coherence."""
        layer_scores = {"@d": 1.0, "@p": 0.8}
        interaction_weights = {("@d", "@p"): 0.05}

        score = compute_choquet_aggregation(layer_scores, {}, interaction_weights)

        expected = 0.05 * min(1.0, 0.8)
        assert abs(score - expected) < 1e-6
