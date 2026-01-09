"""
Property-Based Tests for Choquet Aggregator

This test suite validates the Choquet aggregator using property-based testing
with Hypothesis to ensure mathematical correctness across a wide range of inputs.

Properties tested:
1. Boundedness: 0.0 ≤ Cal(I) ≤ 1.0 for all valid inputs
2. Monotonicity: Higher layer scores → higher aggregate score
3. Normalization: Proper weight normalization
4. Interaction correctness: min(xₗ, xₖ) constraint
5. Determinism: Same inputs → same outputs

Test markers:
- updated: Current, maintained tests
- outdated: Deprecated tests (excluded from CI)
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st, assume, settings

import sys
from pathlib import Path

# Add src to path for direct module import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.choquet_aggregator import (
    ChoquetAggregator,
    ChoquetConfig,
    CalibrationConfigError,
)


@pytest.mark.updated
class TestChoquetBoundedness:
    """Test boundedness property: 0.0 ≤ Cal(I) ≤ 1.0"""
    
    @given(
        scores=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q", "@d"]),
            values=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=4
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_boundedness_uniform_weights(self, scores: dict[str, float]) -> None:
        """Cal(I) must be in [0,1] with uniform weights."""
        layers = list(scores.keys())
        n = len(layers)
        weight = 1.0 / n
        
        config = ChoquetConfig(
            linear_weights={layer: weight for layer in layers},
            interaction_weights={},
            validate_boundedness=True,
            normalize_weights=False
        )
        
        aggregator = ChoquetAggregator(config)
        result = aggregator.aggregate(
            subject="test_subject",
            layer_scores=scores
        )
        
        assert 0.0 <= result.calibration_score <= 1.0, (
            f"Boundedness violated: Cal(I)={result.calibration_score}, scores={scores}"
        )
        assert result.validation_passed
    
    @given(
        scores=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q"]),
            values=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=3,
            max_size=3
        ),
        interaction_weight=st.floats(min_value=0.0, max_value=0.2, allow_nan=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_boundedness_with_interactions(
        self, 
        scores: dict[str, float],
        interaction_weight: float
    ) -> None:
        """Cal(I) must be in [0,1] with interaction terms (after clamping)."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
            interaction_weights={
                ("@b", "@chain"): interaction_weight
            },
            validate_boundedness=False,
            normalize_weights=True
        )
        
        aggregator = ChoquetAggregator(config)
        result = aggregator.aggregate(
            subject="test_subject",
            layer_scores=scores
        )
        
        assert 0.0 <= result.calibration_score <= 1.0, (
            f"Boundedness violated: Cal(I)={result.calibration_score}, "
            f"interaction_weight={interaction_weight}"
        )
    
    @given(
        n_layers=st.integers(min_value=2, max_value=8),
        n_interactions=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=50, deadline=None)
    def test_boundedness_random_config(
        self, 
        n_layers: int,
        n_interactions: int
    ) -> None:
        """Cal(I) bounded for random layer/interaction configurations."""
        layer_ids = [f"@layer{i}" for i in range(n_layers)]
        
        linear_weights = {
            layer: 1.0 / n_layers for layer in layer_ids
        }
        
        interaction_weights = {}
        for i in range(min(n_interactions, n_layers * (n_layers - 1) // 2)):
            if i < n_layers - 1:
                interaction_weights[(layer_ids[i], layer_ids[i+1])] = 0.05
        
        config = ChoquetConfig(
            linear_weights=linear_weights,
            interaction_weights=interaction_weights,
            validate_boundedness=True,
            normalize_weights=True
        )
        
        layer_scores = {layer: 0.5 for layer in layer_ids}
        
        aggregator = ChoquetAggregator(config)
        result = aggregator.aggregate(
            subject="test_subject",
            layer_scores=layer_scores
        )
        
        assert 0.0 <= result.calibration_score <= 1.0
        assert result.validation_passed


@pytest.mark.updated
class TestChoquetMonotonicity:
    """Test monotonicity property: higher inputs → higher outputs"""
    
    @given(
        base_score=st.floats(min_value=0.1, max_value=0.5, allow_nan=False),
        increment=st.floats(min_value=0.01, max_value=0.4, allow_nan=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_monotonicity_single_layer(
        self,
        base_score: float,
        increment: float
    ) -> None:
        """Increasing single layer score increases Cal(I)."""
        assume(base_score + increment <= 1.0)
        
        config = ChoquetConfig(
            linear_weights={"@b": 0.5, "@chain": 0.5},
            interaction_weights={},
            validate_boundedness=True
        )
        
        aggregator = ChoquetAggregator(config)
        
        scores_low = {"@b": base_score, "@chain": 0.5}
        result_low = aggregator.aggregate("test", scores_low)
        
        scores_high = {"@b": base_score + increment, "@chain": 0.5}
        result_high = aggregator.aggregate("test", scores_high)
        
        assert result_high.calibration_score >= result_low.calibration_score, (
            f"Monotonicity violated: "
            f"scores_low={scores_low} → {result_low.calibration_score:.4f}, "
            f"scores_high={scores_high} → {result_high.calibration_score:.4f}"
        )
    
    @given(
        scores=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q"]),
            values=st.floats(min_value=0.0, max_value=0.8, allow_nan=False),
            min_size=3,
            max_size=3
        ),
        scale_factor=st.floats(min_value=1.0, max_value=1.25, allow_nan=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_monotonicity_all_layers(
        self,
        scores: dict[str, float],
        scale_factor: float
    ) -> None:
        """Scaling all scores up increases Cal(I)."""
        scaled_scores = {
            layer: min(1.0, score * scale_factor)
            for layer, score in scores.items()
        }
        
        assume(any(
            scaled_scores[layer] > scores[layer]
            for layer in scores
        ))
        
        config = ChoquetConfig(
            linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
            interaction_weights={("@b", "@chain"): 0.1},
            validate_boundedness=True
        )
        
        aggregator = ChoquetAggregator(config)
        
        result_base = aggregator.aggregate("test", scores)
        result_scaled = aggregator.aggregate("test", scaled_scores)
        
        assert result_scaled.calibration_score >= result_base.calibration_score, (
            f"Monotonicity violated: base={result_base.calibration_score:.4f}, "
            f"scaled={result_scaled.calibration_score:.4f}"
        )


@pytest.mark.updated
class TestChoquetNormalization:
    """Test weight normalization behavior"""
    
    def test_normalization_linear_weights(self) -> None:
        """Linear weights are normalized to sum to 1.0."""
        config = ChoquetConfig(
            linear_weights={"@b": 2.0, "@chain": 3.0, "@q": 5.0},
            interaction_weights={},
            normalize_weights=True
        )
        
        aggregator = ChoquetAggregator(config)
        
        total = sum(aggregator._normalized_linear_weights.values())
        assert abs(total - 1.0) < 1e-10, f"Normalization failed: sum={total}"
    
    def test_normalization_preserves_ratios(self) -> None:
        """Normalization preserves weight ratios."""
        config = ChoquetConfig(
            linear_weights={"@b": 4.0, "@chain": 2.0, "@q": 2.0},
            interaction_weights={},
            normalize_weights=True
        )
        
        aggregator = ChoquetAggregator(config)
        normalized = aggregator._normalized_linear_weights
        
        assert abs(normalized["@b"] - 0.5) < 1e-10
        assert abs(normalized["@chain"] - 0.25) < 1e-10
        assert abs(normalized["@q"] - 0.25) < 1e-10
    
    @given(
        weights=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q", "@d"]),
            values=st.floats(min_value=0.1, max_value=10.0, allow_nan=False),
            min_size=2,
            max_size=4
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_normalization_property(self, weights: dict[str, float]) -> None:
        """Normalized weights always sum to 1.0."""
        config = ChoquetConfig(
            linear_weights=weights,
            interaction_weights={},
            normalize_weights=True
        )
        
        aggregator = ChoquetAggregator(config)
        total = sum(aggregator._normalized_linear_weights.values())
        
        assert abs(total - 1.0) < 1e-10, f"Normalization failed: sum={total}"


@pytest.mark.updated
class TestChoquetInteractionTerms:
    """Test interaction term computation"""
    
    def test_interaction_uses_min(self) -> None:
        """Interaction term uses min(xₗ, xₖ) as expected."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.5, "@chain": 0.5},
            interaction_weights={("@b", "@chain"): 0.2},
            normalize_weights=False,
            validate_boundedness=False
        )
        
        aggregator = ChoquetAggregator(config)
        
        scores = {"@b": 0.8, "@chain": 0.6}
        result = aggregator.aggregate("test", scores)
        
        expected_linear = 0.5 * 0.8 + 0.5 * 0.6
        expected_interaction = 0.2 * min(0.8, 0.6)
        expected_total = expected_linear + expected_interaction
        
        assert abs(result.breakdown.linear_contribution - expected_linear) < 1e-10
        assert abs(result.breakdown.interaction_contribution - expected_interaction) < 1e-10
        assert abs(result.calibration_score - expected_total) < 1e-10
    
    @given(
        score_b=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        score_chain=st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_interaction_symmetry(
        self,
        score_b: float,
        score_chain: float
    ) -> None:
        """Interaction term respects min() symmetry."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.5, "@chain": 0.5},
            interaction_weights={("@b", "@chain"): 0.1},
            normalize_weights=False,
            validate_boundedness=False
        )
        
        aggregator = ChoquetAggregator(config)
        
        scores = {"@b": score_b, "@chain": score_chain}
        result = aggregator.aggregate("test", scores)
        
        expected_min = min(score_b, score_chain)
        interaction_contrib = result.breakdown.per_interaction_contributions[("@b", "@chain")]
        expected_interaction = 0.1 * expected_min
        
        assert abs(interaction_contrib - expected_interaction) < 1e-10, (
            f"Interaction computation incorrect: expected={expected_interaction:.4f}, "
            f"got={interaction_contrib:.4f}"
        )


@pytest.mark.updated
class TestChoquetDeterminism:
    """Test deterministic behavior"""
    
    @given(
        scores=st.dictionaries(
            keys=st.sampled_from(["@b", "@chain", "@q"]),
            values=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            min_size=3,
            max_size=3
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_deterministic_output(self, scores: dict[str, float]) -> None:
        """Same inputs produce same outputs."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
            interaction_weights={("@b", "@chain"): 0.1},
            validate_boundedness=False
        )
        
        aggregator = ChoquetAggregator(config)
        
        result1 = aggregator.aggregate("test", scores)
        result2 = aggregator.aggregate("test", scores)
        
        assert result1.calibration_score == result2.calibration_score
        assert result1.breakdown.linear_contribution == result2.breakdown.linear_contribution
        assert result1.breakdown.interaction_contribution == result2.breakdown.interaction_contribution


@pytest.mark.updated
class TestChoquetConfigValidation:
    """Test configuration validation"""
    
    def test_empty_linear_weights_raises(self) -> None:
        """Empty linear_weights raises CalibrationConfigError."""
        with pytest.raises(CalibrationConfigError, match="linear_weights cannot be empty"):
            ChoquetConfig(linear_weights={})
    
    def test_negative_linear_weight_raises(self) -> None:
        """Negative linear weight raises CalibrationConfigError."""
        with pytest.raises(CalibrationConfigError, match="Negative weight not allowed"):
            ChoquetConfig(linear_weights={"@b": -0.5})
    
    def test_negative_interaction_weight_raises(self) -> None:
        """Negative interaction weight raises CalibrationConfigError."""
        with pytest.raises(CalibrationConfigError, match="Negative interaction weight"):
            ChoquetConfig(
                linear_weights={"@b": 0.5, "@chain": 0.5},
                interaction_weights={("@b", "@chain"): -0.1}
            )
    
    def test_interaction_missing_layer_raises(self) -> None:
        """Interaction referencing missing layer raises CalibrationConfigError."""
        with pytest.raises(CalibrationConfigError, match="not in linear_weights"):
            ChoquetConfig(
                linear_weights={"@b": 0.5},
                interaction_weights={("@b", "@missing"): 0.1}
            )
    
    def test_invalid_layer_id_type_raises(self) -> None:
        """Non-string layer ID raises CalibrationConfigError."""
        with pytest.raises(CalibrationConfigError, match="Layer ID must be string"):
            ChoquetConfig(linear_weights={123: 0.5})  # type: ignore
    
    def test_invalid_weight_type_raises(self) -> None:
        """Non-numeric weight raises CalibrationConfigError."""
        with pytest.raises(CalibrationConfigError, match="Weight must be numeric"):
            ChoquetConfig(linear_weights={"@b": "invalid"})  # type: ignore


@pytest.mark.updated
class TestChoquetAggregatorErrors:
    """Test error handling in aggregation"""
    
    def test_missing_layer_scores_raises(self) -> None:
        """Missing required layer in layer_scores raises ValueError."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.5, "@chain": 0.5}
        )
        aggregator = ChoquetAggregator(config)
        
        with pytest.raises(ValueError, match="Missing required layers"):
            aggregator.aggregate("test", layer_scores={"@b": 0.8})
    
    def test_boundedness_violation_raises(self) -> None:
        """Boundedness violation raises CalibrationConfigError when enabled."""
        config = ChoquetConfig(
            linear_weights={"@b": 2.0, "@chain": 2.0},
            interaction_weights={},
            normalize_weights=False,
            validate_boundedness=True
        )
        aggregator = ChoquetAggregator(config)
        
        with pytest.raises(CalibrationConfigError, match="Boundedness violation"):
            aggregator.aggregate("test", layer_scores={"@b": 1.0, "@chain": 1.0})
    
    def test_boundedness_violation_warning_only(self) -> None:
        """Boundedness violation logs warning when validation disabled."""
        config = ChoquetConfig(
            linear_weights={"@b": 2.0, "@chain": 2.0},
            interaction_weights={},
            normalize_weights=False,
            validate_boundedness=False
        )
        aggregator = ChoquetAggregator(config)
        
        result = aggregator.aggregate("test", layer_scores={"@b": 1.0, "@chain": 1.0})
        
        assert not result.validation_passed
        assert result.calibration_score == 1.0


@pytest.mark.updated
class TestChoquetBreakdown:
    """Test breakdown computation and rationales"""
    
    def test_breakdown_components_sum_to_total(self) -> None:
        """Linear + interaction contributions sum to total score."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
            interaction_weights={("@b", "@chain"): 0.1},
            normalize_weights=False
        )
        
        aggregator = ChoquetAggregator(config)
        scores = {"@b": 0.8, "@chain": 0.7, "@q": 0.9}
        result = aggregator.aggregate("test", scores)
        
        total_from_breakdown = (
            result.breakdown.linear_contribution +
            result.breakdown.interaction_contribution
        )
        
        assert abs(result.calibration_score - total_from_breakdown) < 1e-10
    
    def test_per_layer_contributions_sum_to_linear(self) -> None:
        """Per-layer contributions sum to total linear contribution."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
            interaction_weights={},
            normalize_weights=False
        )
        
        aggregator = ChoquetAggregator(config)
        scores = {"@b": 0.8, "@chain": 0.7, "@q": 0.9}
        result = aggregator.aggregate("test", scores)
        
        per_layer_sum = sum(result.breakdown.per_layer_contributions.values())
        
        assert abs(result.breakdown.linear_contribution - per_layer_sum) < 1e-10
    
    def test_rationales_present(self) -> None:
        """All layers and interactions have rationales."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
            interaction_weights={("@b", "@chain"): 0.1},
            normalize_weights=False
        )
        
        aggregator = ChoquetAggregator(config)
        scores = {"@b": 0.8, "@chain": 0.7, "@q": 0.9}
        result = aggregator.aggregate("test", scores)
        
        assert len(result.breakdown.per_layer_rationales) == 3
        assert len(result.breakdown.per_interaction_rationales) == 1
        
        for layer in ["@b", "@chain", "@q"]:
            assert layer in result.breakdown.per_layer_rationales
            rationale = result.breakdown.per_layer_rationales[layer]
            assert "weight=" in rationale
            assert "score=" in rationale
        
        assert ("@b", "@chain") in result.breakdown.per_interaction_rationales
        interaction_rationale = result.breakdown.per_interaction_rationales[("@b", "@chain")]
        assert "min(" in interaction_rationale
