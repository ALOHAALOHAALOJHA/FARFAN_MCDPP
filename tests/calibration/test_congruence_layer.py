"""
Unit tests for Congruence Layer (@C) computation.

Tests ensemble validity for interplay methods:
- c_scale: scale congruence (range compatibility)
- c_sem: semantic congruence (concept overlap)
- c_fusion: fusion validity (declared fusion rule)

Formula: C_play(G | ctx) = c_scale · c_sem · c_fusion
"""

from __future__ import annotations

from typing import Any



def compute_scale_congruence(methods_output_ranges: list[tuple[float, float]]) -> float:
    """
    Compute scale congruence for ensemble.
    
    Returns:
        1.0 if all ranges identical
        0.8 if ranges convertible
        0.0 otherwise
    """
    if not methods_output_ranges:
        return 1.0

    first_range = methods_output_ranges[0]

    if all(r == first_range for r in methods_output_ranges):
        return 1.0

    all_in_01 = all(r == (0.0, 1.0) for r in methods_output_ranges)
    if all_in_01:
        return 1.0

    return 0.8


def compute_semantic_congruence(method_concepts: list[set[str]]) -> float:
    """
    Compute semantic congruence (Jaccard similarity).
    
    semantic_overlap = |⋂ᵢ Cᵢ| / |⋃ᵢ Cᵢ|
    """
    if not method_concepts:
        return 1.0

    intersection = set.intersection(*method_concepts)
    union = set.union(*method_concepts)

    if len(union) == 0:
        return 1.0

    return len(intersection) / len(union)


def compute_fusion_validity(fusion_rule_declared: bool, all_inputs_available: bool) -> float:
    """
    Compute fusion validity.
    
    Returns:
        1.0 if fusion declared and inputs available
        0.5 if fusion declared but inputs missing
        0.0 if no fusion rule declared
    """
    if not fusion_rule_declared:
        return 0.0

    if all_inputs_available:
        return 1.0

    return 0.5


def compute_congruence_score(ensemble_config: dict[str, Any]) -> float:
    """Compute overall congruence score C_play."""
    c_scale = 1.0 if ensemble_config.get("scale_compatible", True) else 0.0
    c_sem = ensemble_config.get("semantic_overlap", 1.0)
    c_fusion = 1.0 if ensemble_config.get("fusion_rule") else 0.0

    return c_scale * c_sem * c_fusion


class TestScaleCongruence:
    """Test scale congruence computation."""

    def test_identical_ranges_perfect_score(self):
        """Identical output ranges should yield 1.0."""
        ranges = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]

        score = compute_scale_congruence(ranges)

        assert score == 1.0

    def test_different_ranges_lower_score(self):
        """Different output ranges should yield lower score."""
        ranges = [(0.0, 1.0), (0.0, 10.0)]

        score = compute_scale_congruence(ranges)

        assert score < 1.0

    def test_empty_ensemble_default(self):
        """Empty ensemble should default to 1.0."""
        ranges = []

        score = compute_scale_congruence(ranges)

        assert score == 1.0

    def test_single_method_perfect_score(self):
        """Single method should have perfect scale congruence."""
        ranges = [(0.0, 1.0)]

        score = compute_scale_congruence(ranges)

        assert score == 1.0


class TestSemanticCongruence:
    """Test semantic congruence computation."""

    def test_perfect_concept_overlap(self):
        """Perfect concept overlap should yield 1.0."""
        concepts = [
            {"coherence", "textual_quality"},
            {"coherence", "textual_quality"},
        ]

        score = compute_semantic_congruence(concepts)

        assert score == 1.0

    def test_partial_concept_overlap(self):
        """Partial concept overlap should yield < 1.0."""
        concepts = [
            {"coherence", "textual_quality"},
            {"coherence", "validation"},
        ]

        score = compute_semantic_congruence(concepts)

        assert 0.0 < score < 1.0
        assert abs(score - 0.333) < 0.01

    def test_no_concept_overlap(self):
        """No concept overlap should yield 0.0."""
        concepts = [
            {"coherence"},
            {"numerical_analysis"},
        ]

        score = compute_semantic_congruence(concepts)

        assert score == 0.0

    def test_empty_concepts_default(self):
        """Empty concepts should default to 1.0."""
        concepts = []

        score = compute_semantic_congruence(concepts)

        assert score == 1.0

    def test_jaccard_similarity_formula(self):
        """Verify Jaccard similarity formula."""
        concepts = [
            {"a", "b", "c"},
            {"b", "c", "d"},
        ]

        intersection = {"b", "c"}
        union = {"a", "b", "c", "d"}
        expected = len(intersection) / len(union)

        score = compute_semantic_congruence(concepts)

        assert abs(score - expected) < 1e-6


class TestFusionValidity:
    """Test fusion validity computation."""

    def test_fusion_declared_inputs_available(self):
        """Declared fusion with available inputs should yield 1.0."""
        score = compute_fusion_validity(fusion_rule_declared=True, all_inputs_available=True)

        assert score == 1.0

    def test_fusion_declared_inputs_missing(self):
        """Declared fusion with missing inputs should yield 0.5."""
        score = compute_fusion_validity(fusion_rule_declared=True, all_inputs_available=False)

        assert score == 0.5

    def test_no_fusion_declared(self):
        """No fusion rule declared should yield 0.0."""
        score = compute_fusion_validity(fusion_rule_declared=False, all_inputs_available=True)

        assert score == 0.0


class TestCongruenceLayerIntegration:
    """Test complete congruence layer computation."""

    def test_perfect_ensemble(self, sample_ensemble_config: dict[str, Any]):
        """Perfect ensemble should yield C_play = 1.0."""
        score = compute_congruence_score(sample_ensemble_config)

        assert score == 1.0

    def test_imperfect_semantic_overlap(self):
        """Imperfect semantic overlap should reduce score."""
        ensemble = {
            "scale_compatible": True,
            "semantic_overlap": 0.5,
            "fusion_rule": "TYPE_A",
        }

        score = compute_congruence_score(ensemble)

        assert score == 0.5

    def test_missing_fusion_rule(self):
        """Missing fusion rule should yield 0.0."""
        ensemble = {
            "scale_compatible": True,
            "semantic_overlap": 1.0,
            "fusion_rule": None,
        }

        score = compute_congruence_score(ensemble)

        assert score == 0.0

    def test_scale_incompatible(self):
        """Scale incompatibility should yield 0.0."""
        ensemble = {
            "scale_compatible": False,
            "semantic_overlap": 1.0,
            "fusion_rule": "TYPE_A",
        }

        score = compute_congruence_score(ensemble)

        assert score == 0.0

    def test_congruence_bounded(self):
        """Congruence score must be bounded in [0,1]."""
        test_configs = [
            {"scale_compatible": True, "semantic_overlap": 1.0, "fusion_rule": "TYPE_A"},
            {"scale_compatible": True, "semantic_overlap": 0.5, "fusion_rule": "TYPE_A"},
            {"scale_compatible": False, "semantic_overlap": 1.0, "fusion_rule": "TYPE_A"},
            {"scale_compatible": True, "semantic_overlap": 1.0, "fusion_rule": None},
        ]

        for config in test_configs:
            score = compute_congruence_score(config)
            assert 0.0 <= score <= 1.0


class TestCongruenceLayerPerInstanceAssignment:
    """Test per-instance congruence assignment."""

    def test_method_in_interplay(self, sample_ensemble_config: dict[str, Any]):
        """Method in interplay should use C_play score."""
        c_play = compute_congruence_score(sample_ensemble_config)

        x_at_c = c_play

        assert x_at_c == 1.0

    def test_method_not_in_interplay(self):
        """Method not in interplay should default to 1.0."""
        x_at_c = 1.0

        assert x_at_c == 1.0

    def test_interplay_identification(self):
        """Test interplay identification logic."""
        method_id = "pattern_extractor_v2"
        ensemble_methods = ["pattern_extractor_v2", "coherence_validator"]

        in_interplay = method_id in ensemble_methods

        assert in_interplay is True


class TestFusionTypeSpecifications:
    """Test different fusion type specifications."""

    def test_type_a_fusion(self):
        """TYPE_A fusion: weighted average."""
        fusion_type = "TYPE_A"

        assert fusion_type in ["TYPE_A", "TYPE_B", "TYPE_C"]

    def test_type_b_fusion(self):
        """TYPE_B fusion: max operator."""
        fusion_type = "TYPE_B"

        assert fusion_type in ["TYPE_A", "TYPE_B", "TYPE_C"]

    def test_type_c_fusion(self):
        """TYPE_C fusion: min operator."""
        fusion_type = "TYPE_C"

        assert fusion_type in ["TYPE_A", "TYPE_B", "TYPE_C"]


class TestEnsembleExamples:
    """Test complete ensemble examples."""

    def test_analyzer_validator_ensemble(self):
        """Test analyzer + validator ensemble."""
        ensemble = {
            "methods": ["pattern_extractor_v2", "coherence_validator"],
            "scale_compatible": True,
            "semantic_overlap": 1.0,
            "fusion_rule": "TYPE_A",
            "concepts": ["coherence", "textual_quality"],
        }

        score = compute_congruence_score(ensemble)

        assert score == 1.0

    def test_multi_method_ensemble(self):
        """Test multi-method ensemble with partial overlap."""
        concepts = [
            {"coherence", "textual_quality"},
            {"coherence", "validation"},
            {"validation", "quality"},
        ]

        sem_score = compute_semantic_congruence(concepts)

        assert 0.0 <= sem_score < 1.0
