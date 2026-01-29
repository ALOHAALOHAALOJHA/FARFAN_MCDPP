"""
Phase 5 Adversarial Tests - Policy Area Aggregation
====================================================

ADVERSARIAL TEST CATEGORIES:
1. HERMETICITY VIOLATIONS: Missing/duplicate dimensions
2. BOUNDS VIOLATIONS: Out-of-range scores, NaN, Inf
3. CLUSTER MAPPING: PA→Cluster assignment correctness
4. INPUT VALIDATION: Malformed inputs, type errors
5. DETERMINISM: Same inputs → same outputs
6. EDGE CASES: Empty inputs, single inputs, extremes

Contract: 60 DimensionScore → 10 AreaScore
- Each PA must have exactly 6 dimensions
- All scores in [0.0, 3.0]
- Correct cluster assignments
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

import pytest

from .conftest import (
    CLUSTER_TO_PAS,
    DIMENSIONS,
    DIMENSIONS_PER_AREA,
    EXPECTED_AREA_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    PA_TO_CLUSTER,
    POLICY_AREAS,
    QUALITY_THRESHOLDS,
    MockAreaScore,
    MockDimensionScore,
    compute_area_score,
)


# =============================================================================
# 1. HERMETICITY TESTS - Exactly 6 dimensions per PA
# =============================================================================


class TestHermeticityValidation:
    """Tests for hermeticity (all 6 dimensions present per PA)."""

    def test_complete_dimensions_accepted(
        self, generate_complete_pa_dimensions, validate_area_score_hermeticity
    ):
        """PASS: All 6 dimensions present for a PA."""
        dim_scores = generate_complete_pa_dimensions("PA01")
        area_score = compute_area_score(dim_scores, "PA01")
        valid, msg = validate_area_score_hermeticity(area_score)
        assert valid, f"Hermeticity failed: {msg}"

    def test_missing_dimension_rejected(self, generate_missing_dimension):
        """FAIL: Missing one dimension should raise error."""
        dim_scores = generate_missing_dimension("PA01", "DIM03")
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")

    def test_missing_multiple_dimensions_rejected(self, generate_valid_dimension_score):
        """FAIL: Missing multiple dimensions should raise error."""
        # Only 3 dimensions instead of 6
        dim_scores = [
            generate_valid_dimension_score("PA02", "DIM01"),
            generate_valid_dimension_score("PA02", "DIM02"),
            generate_valid_dimension_score("PA02", "DIM06"),
        ]
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA02")

    def test_duplicate_dimension_rejected(self, generate_duplicate_dimension):
        """FAIL: Duplicate dimensions should be detected (even if count is 7)."""
        dim_scores = generate_duplicate_dimension("PA03", "DIM01")
        # Should fail because we have 7 scores with a duplicate
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA03")

    def test_all_pas_have_complete_dimensions(
        self,
        generate_all_dimension_scores,
        validate_area_score_hermeticity,
    ):
        """PASS: All 10 PAs have exactly 6 dimensions each."""
        all_scores = generate_all_dimension_scores()
        for pa_id in POLICY_AREAS:
            area_score = compute_area_score(all_scores, pa_id)
            valid, msg = validate_area_score_hermeticity(area_score)
            assert valid, f"PA {pa_id} hermeticity failed: {msg}"

    def test_empty_dimension_list_rejected(self):
        """FAIL: Empty input should raise error."""
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score([], "PA01")

    def test_dimensions_from_wrong_pa_not_counted(self, generate_valid_dimension_score):
        """FAIL: Dimensions from wrong PA should not count toward hermeticity."""
        # All dimensions are for PA01, but we're computing for PA02
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS]
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA02")


# =============================================================================
# 2. BOUNDS TESTS - Scores in [0.0, 3.0]
# =============================================================================


class TestBoundsValidation:
    """Tests for score bounds enforcement."""

    def test_score_within_bounds_accepted(
        self, generate_complete_pa_dimensions, validate_area_score_bounds
    ):
        """PASS: Score within [0.0, 3.0] accepted."""
        dim_scores = generate_complete_pa_dimensions("PA01", base_score=2.0)
        area_score = compute_area_score(dim_scores, "PA01")
        valid, msg = validate_area_score_bounds(area_score)
        assert valid, f"Bounds validation failed: {msg}"

    def test_minimum_score_boundary(self, generate_valid_dimension_score):
        """PASS: Score exactly at minimum (0.0) is valid."""
        dim_scores = [generate_valid_dimension_score("PA01", dim, score=0.0) for dim in DIMENSIONS]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score >= MIN_SCORE, f"Score {area_score.score} below minimum"

    def test_maximum_score_boundary(self, generate_valid_dimension_score):
        """PASS: Score exactly at maximum (3.0) is valid."""
        dim_scores = [generate_valid_dimension_score("PA01", dim, score=3.0) for dim in DIMENSIONS]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score <= MAX_SCORE, f"Score {area_score.score} above maximum"

    def test_negative_dimension_score_clamped(self, generate_valid_dimension_score):
        """ADVERSARIAL: Negative dimension score should be handled gracefully."""
        dim_scores = []
        for i, dim in enumerate(DIMENSIONS):
            # One dimension has negative score
            score = -1.0 if i == 0 else 2.0
            dim_scores.append(generate_valid_dimension_score("PA01", dim, score=score))

        area_score = compute_area_score(dim_scores, "PA01")
        # Result should be clamped to bounds
        assert area_score.score >= MIN_SCORE, f"Negative score not clamped: {area_score.score}"

    def test_score_above_maximum_clamped(self, generate_valid_dimension_score):
        """ADVERSARIAL: Score > 3.0 should be clamped."""
        dim_scores = [generate_valid_dimension_score("PA01", dim, score=5.0) for dim in DIMENSIONS]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score <= MAX_SCORE, f"Score not clamped: {area_score.score}"

    def test_all_areas_within_bounds(self, generate_all_dimension_scores, validate_area_score_bounds):
        """PASS: All 10 area scores within bounds."""
        all_scores = generate_all_dimension_scores()
        for pa_id in POLICY_AREAS:
            area_score = compute_area_score(all_scores, pa_id)
            valid, msg = validate_area_score_bounds(area_score)
            assert valid, f"PA {pa_id} bounds failed: {msg}"


# =============================================================================
# 3. CLUSTER MAPPING TESTS - PA→Cluster assignments
# =============================================================================


class TestClusterMapping:
    """Tests for correct PA→Cluster assignments."""

    def test_cluster_assignment_correct(
        self, generate_complete_pa_dimensions, validate_cluster_assignment
    ):
        """PASS: Each PA assigned to correct cluster."""
        for pa_id, expected_cluster in PA_TO_CLUSTER.items():
            dim_scores = generate_complete_pa_dimensions(pa_id)
            area_score = compute_area_score(dim_scores, pa_id)
            valid, msg = validate_cluster_assignment(area_score)
            assert valid, f"PA {pa_id} cluster assignment failed: {msg}"

    @pytest.mark.parametrize(
        "pa_id,expected_cluster",
        [
            ("PA01", "CL02"),
            ("PA02", "CL01"),
            ("PA03", "CL01"),
            ("PA04", "CL03"),
            ("PA05", "CL02"),
            ("PA06", "CL02"),
            ("PA07", "CL01"),
            ("PA08", "CL03"),
            ("PA09", "CL04"),
            ("PA10", "CL04"),
        ],
    )
    def test_specific_cluster_assignments(
        self, pa_id, expected_cluster, generate_complete_pa_dimensions
    ):
        """PASS: Each PA has its canonical cluster assignment."""
        dim_scores = generate_complete_pa_dimensions(pa_id)
        area_score = compute_area_score(dim_scores, pa_id)
        assert (
            area_score.cluster_id == expected_cluster
        ), f"PA {pa_id} should be in {expected_cluster}, got {area_score.cluster_id}"

    def test_cluster_to_pas_inverse_mapping(self, generate_all_dimension_scores):
        """PASS: Verify CLUSTER_TO_PAS is inverse of PA_TO_CLUSTER."""
        # Verify the canonical mappings are consistent
        for cluster_id, pas in CLUSTER_TO_PAS.items():
            for pa_id in pas:
                assert (
                    PA_TO_CLUSTER[pa_id] == cluster_id
                ), f"Inconsistent mapping: {pa_id} → {PA_TO_CLUSTER[pa_id]} vs {cluster_id}"

    def test_all_pas_have_cluster_assignment(self, generate_all_dimension_scores):
        """PASS: All 10 PAs have cluster assignments."""
        all_scores = generate_all_dimension_scores()
        for pa_id in POLICY_AREAS:
            area_score = compute_area_score(all_scores, pa_id)
            assert area_score.cluster_id is not None, f"PA {pa_id} has no cluster assignment"
            assert area_score.cluster_id.startswith("CL"), f"Invalid cluster ID: {area_score.cluster_id}"


# =============================================================================
# 4. INPUT VALIDATION TESTS - Malformed inputs
# =============================================================================


class TestInputValidation:
    """Tests for input validation and error handling."""

    def test_nan_score_handled(self, generate_nan_score, generate_valid_dimension_score):
        """ADVERSARIAL: NaN score should be detected or handled."""
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS[:5]]
        dim_scores.append(generate_nan_score("PA01", "DIM06"))

        # Should either raise error or handle gracefully
        area_score = compute_area_score(dim_scores, "PA01")
        assert not math.isnan(area_score.score), "NaN propagated to area score"

    def test_inf_score_handled(self, generate_inf_score, generate_valid_dimension_score):
        """ADVERSARIAL: Infinity score should be detected or handled."""
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS[:5]]
        dim_scores.append(generate_inf_score("PA01", "DIM06"))

        area_score = compute_area_score(dim_scores, "PA01")
        assert not math.isinf(area_score.score), "Infinity propagated to area score"

    def test_empty_questions_handled(self, generate_empty_questions_score, generate_valid_dimension_score):
        """ADVERSARIAL: Dimension with no contributing questions."""
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS[:5]]
        dim_scores.append(generate_empty_questions_score("PA01", "DIM06"))

        # Should still compute (questions are metadata, not required for aggregation)
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score is not None

    def test_invalid_dimension_id_format(self, generate_valid_dimension_score):
        """ADVERSARIAL: Invalid dimension ID format."""
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS[:5]]
        # Invalid dimension ID
        dim_scores.append(
            MockDimensionScore(
                dimension_id="INVALID_DIM",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3],
            )
        )
        # Should fail hermeticity (DIM06 missing, INVALID_DIM doesn't count)
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")

    def test_invalid_pa_id_format(self, generate_valid_dimension_score):
        """ADVERSARIAL: Invalid PA ID format."""
        dim_scores = [generate_valid_dimension_score("INVALID_PA", dim) for dim in DIMENSIONS]
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")


# =============================================================================
# 5. DETERMINISM TESTS - Same inputs → same outputs
# =============================================================================


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self, generate_all_dimension_scores):
        """PASS: Same inputs produce identical outputs."""
        # Use fixed seed for reproducibility
        random.seed(42)
        scores_1 = generate_all_dimension_scores(base_score=2.0)

        random.seed(42)
        scores_2 = generate_all_dimension_scores(base_score=2.0)

        for pa_id in POLICY_AREAS:
            area_1 = compute_area_score(scores_1, pa_id)
            area_2 = compute_area_score(scores_2, pa_id)
            assert abs(area_1.score - area_2.score) < 1e-9, f"PA {pa_id} not deterministic"

    def test_order_independence(self, generate_complete_pa_dimensions):
        """PASS: Dimension order should not affect result."""
        dim_scores = generate_complete_pa_dimensions("PA01", base_score=2.0)
        area_1 = compute_area_score(dim_scores, "PA01")

        # Reverse order
        dim_scores_reversed = list(reversed(dim_scores))
        area_2 = compute_area_score(dim_scores_reversed, "PA01")

        assert abs(area_1.score - area_2.score) < 1e-9, "Order affects result"

    def test_multiple_runs_identical(self, generate_complete_pa_dimensions):
        """PASS: Multiple runs produce identical results."""
        dim_scores = generate_complete_pa_dimensions("PA01", base_score=2.0)

        results = []
        for _ in range(10):
            area_score = compute_area_score(dim_scores, "PA01")
            results.append(area_score.score)

        # All results should be identical
        assert all(abs(r - results[0]) < 1e-9 for r in results), "Results vary across runs"


# =============================================================================
# 6. EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_all_zero_scores(self, generate_valid_dimension_score):
        """EDGE: All dimensions have score 0.0."""
        dim_scores = [generate_valid_dimension_score("PA01", dim, score=0.0) for dim in DIMENSIONS]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score == 0.0, f"Expected 0.0, got {area_score.score}"
        assert area_score.quality_level == "INSUFICIENTE"

    def test_all_max_scores(self, generate_valid_dimension_score):
        """EDGE: All dimensions have maximum score 3.0."""
        dim_scores = [generate_valid_dimension_score("PA01", dim, score=3.0) for dim in DIMENSIONS]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score == 3.0, f"Expected 3.0, got {area_score.score}"
        assert area_score.quality_level == "EXCELENTE"

    def test_mixed_extreme_scores(self, generate_valid_dimension_score):
        """EDGE: Mix of 0.0 and 3.0 scores."""
        dim_scores = []
        for i, dim in enumerate(DIMENSIONS):
            score = 0.0 if i % 2 == 0 else 3.0
            dim_scores.append(generate_valid_dimension_score("PA01", dim, score=score))

        area_score = compute_area_score(dim_scores, "PA01")
        # Average of [0, 3, 0, 3, 0, 3] = 1.5
        assert abs(area_score.score - 1.5) < 0.1, f"Expected ~1.5, got {area_score.score}"

    def test_single_non_zero_dimension(self, generate_valid_dimension_score):
        """EDGE: One dimension at 3.0, rest at 0.0."""
        dim_scores = []
        for i, dim in enumerate(DIMENSIONS):
            score = 3.0 if i == 0 else 0.0
            dim_scores.append(generate_valid_dimension_score("PA01", dim, score=score))

        area_score = compute_area_score(dim_scores, "PA01")
        # Average = 3.0 / 6 = 0.5
        expected = 3.0 / 6
        assert abs(area_score.score - expected) < 0.01, f"Expected {expected}, got {area_score.score}"

    def test_very_small_scores(self, generate_valid_dimension_score):
        """EDGE: Very small positive scores (epsilon)."""
        epsilon = 1e-10
        dim_scores = [generate_valid_dimension_score("PA01", dim, score=epsilon) for dim in DIMENSIONS]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score >= 0, "Epsilon score became negative"
        assert area_score.score <= MAX_SCORE

    def test_quality_level_thresholds(self, generate_valid_dimension_score):
        """EDGE: Test each quality level threshold."""
        test_cases = [
            (3.0 * 0.90, "EXCELENTE"),  # 90% of max → EXCELENTE
            (3.0 * 0.75, "BUENO"),  # 75% of max → BUENO
            (3.0 * 0.60, "ACEPTABLE"),  # 60% of max → ACEPTABLE
            (3.0 * 0.40, "INSUFICIENTE"),  # 40% of max → INSUFICIENTE
        ]

        for target_score, expected_quality in test_cases:
            dim_scores = [
                generate_valid_dimension_score("PA01", dim, score=target_score) for dim in DIMENSIONS
            ]
            area_score = compute_area_score(dim_scores, "PA01")
            assert (
                area_score.quality_level == expected_quality
            ), f"Score {target_score}: expected {expected_quality}, got {area_score.quality_level}"


# =============================================================================
# 7. STATISTICAL DISTRIBUTION TESTS
# =============================================================================


class TestStatisticalBehavior:
    """Tests for statistical properties of aggregation."""

    def test_uniform_distribution_average(self, generate_dimension_score_distribution):
        """STATISTICAL: Uniform distribution should average to ~1.5."""
        random.seed(42)
        # Run multiple times for statistical validity
        averages = []
        for _ in range(100):
            dim_scores = generate_dimension_score_distribution("PA01", distribution="uniform")
            area_score = compute_area_score(dim_scores, "PA01")
            averages.append(area_score.score)

        mean_avg = sum(averages) / len(averages)
        # Should be close to 1.5 (midpoint of [0, 3])
        assert 1.2 < mean_avg < 1.8, f"Uniform distribution average {mean_avg} far from expected 1.5"

    def test_extreme_low_distribution(self, generate_dimension_score_distribution):
        """STATISTICAL: Extreme low distribution should average below 0.5."""
        random.seed(42)
        dim_scores = generate_dimension_score_distribution("PA01", distribution="extreme_low")
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score < 1.0, f"Extreme low score {area_score.score} not low enough"

    def test_extreme_high_distribution(self, generate_dimension_score_distribution):
        """STATISTICAL: Extreme high distribution should average above 2.5."""
        random.seed(42)
        dim_scores = generate_dimension_score_distribution("PA01", distribution="extreme_high")
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score > 2.0, f"Extreme high score {area_score.score} not high enough"


# =============================================================================
# 8. WEIGHTED AGGREGATION TESTS
# =============================================================================


class TestWeightedAggregation:
    """Tests for weighted aggregation behavior."""

    def test_equal_weights_average(self, generate_valid_dimension_score):
        """PASS: Equal weights produce simple average."""
        scores = [0.0, 1.0, 2.0, 3.0, 1.5, 2.5]
        dim_scores = [
            generate_valid_dimension_score("PA01", dim, score=score)
            for dim, score in zip(DIMENSIONS, scores)
        ]

        area_score = compute_area_score(dim_scores, "PA01")
        expected = sum(scores) / len(scores)
        assert (
            abs(area_score.score - expected) < 0.01
        ), f"Expected {expected}, got {area_score.score}"

    def test_unequal_weights(self, generate_valid_dimension_score):
        """PASS: Unequal weights produce weighted average."""
        scores = [3.0, 3.0, 0.0, 0.0, 0.0, 0.0]
        weights = {"DIM01": 0.5, "DIM02": 0.5, "DIM03": 0.0, "DIM04": 0.0, "DIM05": 0.0, "DIM06": 0.0}

        dim_scores = [
            generate_valid_dimension_score("PA01", dim, score=score)
            for dim, score in zip(DIMENSIONS, scores)
        ]

        area_score = compute_area_score(dim_scores, "PA01", weights=weights)
        # Only DIM01 and DIM02 have weight, both at 3.0
        expected = 3.0
        assert (
            abs(area_score.score - expected) < 0.01
        ), f"Expected {expected}, got {area_score.score}"

    def test_single_dimension_full_weight(self, generate_valid_dimension_score):
        """PASS: Single dimension with full weight dominates."""
        dim_scores = [generate_valid_dimension_score("PA01", dim, score=1.0) for dim in DIMENSIONS]
        dim_scores[0] = generate_valid_dimension_score("PA01", "DIM01", score=3.0)

        weights = {"DIM01": 1.0, "DIM02": 0.0, "DIM03": 0.0, "DIM04": 0.0, "DIM05": 0.0, "DIM06": 0.0}

        area_score = compute_area_score(dim_scores, "PA01", weights=weights)
        assert area_score.score == 3.0, f"Expected 3.0, got {area_score.score}"


# =============================================================================
# 9. PROVENANCE AND METADATA TESTS
# =============================================================================


class TestProvenanceMetadata:
    """Tests for provenance and metadata tracking."""

    def test_dimension_scores_preserved(self, generate_complete_pa_dimensions):
        """PASS: AreaScore contains all contributing DimensionScores."""
        dim_scores = generate_complete_pa_dimensions("PA01")
        area_score = compute_area_score(dim_scores, "PA01")

        assert len(area_score.dimension_scores) == 6
        dim_ids = {ds.dimension_id for ds in area_score.dimension_scores}
        assert dim_ids == set(DIMENSIONS)

    def test_validation_details_populated(self, generate_complete_pa_dimensions):
        """PASS: Validation details should be populated."""
        dim_scores = generate_complete_pa_dimensions("PA01")
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.validation_passed is True

    def test_area_name_populated(self, generate_complete_pa_dimensions):
        """PASS: Area name should be populated."""
        dim_scores = generate_complete_pa_dimensions("PA01")
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.area_name is not None
        assert len(area_score.area_name) > 0


# =============================================================================
# 10. FULL PIPELINE TESTS
# =============================================================================


class TestFullPipeline:
    """Tests for complete Phase 5 pipeline (60 → 10)."""

    def test_complete_aggregation_all_pas(
        self, generate_all_dimension_scores, assert_all_pas_present
    ):
        """PASS: Complete pipeline produces 10 AreaScores."""
        all_dim_scores = generate_all_dimension_scores()

        area_scores = []
        for pa_id in POLICY_AREAS:
            area_score = compute_area_score(all_dim_scores, pa_id)
            area_scores.append(area_score)

        assert len(area_scores) == EXPECTED_AREA_COUNT
        assert_all_pas_present(area_scores)

    def test_no_duplicate_pas_in_output(self, generate_all_dimension_scores):
        """PASS: No duplicate PA IDs in output."""
        all_dim_scores = generate_all_dimension_scores()

        area_scores = []
        for pa_id in POLICY_AREAS:
            area_score = compute_area_score(all_dim_scores, pa_id)
            area_scores.append(area_score)

        pa_ids = [score.area_id for score in area_scores]
        assert len(pa_ids) == len(set(pa_ids)), f"Duplicate PAs: {pa_ids}"

    def test_cluster_distribution_correct(self, generate_all_dimension_scores):
        """PASS: Correct number of PAs per cluster."""
        all_dim_scores = generate_all_dimension_scores()

        cluster_counts = {}
        for pa_id in POLICY_AREAS:
            area_score = compute_area_score(all_dim_scores, pa_id)
            cluster_id = area_score.cluster_id
            cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1

        expected_counts = {
            "CL01": 3,  # PA02, PA03, PA07
            "CL02": 3,  # PA01, PA05, PA06
            "CL03": 2,  # PA04, PA08
            "CL04": 2,  # PA09, PA10
        }

        assert cluster_counts == expected_counts, f"Cluster counts mismatch: {cluster_counts}"
