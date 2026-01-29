"""
Phase 6 Adversarial Tests - Cluster Aggregation (MESO)
======================================================

ADVERSARIAL TEST CATEGORIES:
1. HERMETICITY VIOLATIONS: Missing/extra PAs per cluster
2. BOUNDS VIOLATIONS: Out-of-range scores, NaN, Inf
3. DISPERSION ANALYSIS: CV classification, adaptive penalty
4. COHERENCE: Cross-area coherence validation
5. INPUT VALIDATION: Malformed inputs, type errors
6. DETERMINISM: Same inputs → same outputs
7. EDGE CASES: Empty inputs, single inputs, extremes

Contract: 10 AreaScore → 4 ClusterScore
- Each cluster has specific PA composition
- All scores in [0.0, 3.0]
- Dispersion-based adaptive penalty
"""

from __future__ import annotations

import math
import random
import statistics

import pytest

from .conftest import (
    CLUSTER_COMPOSITION,
    CLUSTERS,
    COHERENCE_THRESHOLD_HIGH,
    COHERENCE_THRESHOLD_LOW,
    DISPERSION_THRESHOLDS,
    EXPECTED_CLUSTER_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    PENALTY_WEIGHT,
    POLICY_AREAS,
    MockAreaScore,
    MockClusterScore,
    classify_dispersion,
    compute_cluster_score,
    compute_coherence,
    compute_cv,
)


# =============================================================================
# 1. HERMETICITY TESTS - Correct PAs per cluster
# =============================================================================


class TestHermeticityValidation:
    """Tests for cluster hermeticity (correct PA composition)."""

    def test_complete_cluster_accepted(
        self, generate_cluster_area_scores, validate_cluster_hermeticity
    ):
        """PASS: All expected PAs present for a cluster."""
        for cluster_id in CLUSTERS:
            area_scores = generate_cluster_area_scores(cluster_id)
            cluster_score = compute_cluster_score(area_scores, cluster_id)
            valid, msg = validate_cluster_hermeticity(cluster_score)
            assert valid, f"Cluster {cluster_id} hermeticity failed: {msg}"

    def test_missing_area_rejected(self, generate_missing_area_cluster):
        """FAIL: Missing one PA should raise error."""
        area_scores = generate_missing_area_cluster("CLUSTER_MESO_1", "PA01")
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_cluster_score(area_scores, "CLUSTER_MESO_1")

    @pytest.mark.parametrize("cluster_id", CLUSTERS)
    def test_each_cluster_hermeticity(self, cluster_id, generate_cluster_area_scores):
        """PASS: Each cluster maintains hermeticity."""
        area_scores = generate_cluster_area_scores(cluster_id)
        cluster_score = compute_cluster_score(area_scores, cluster_id)
        
        expected_pas = set(CLUSTER_COMPOSITION[cluster_id])
        actual_pas = {a.area_id for a in cluster_score.area_scores}
        assert actual_pas == expected_pas

    def test_wrong_cluster_area_not_included(self, generate_valid_area_score):
        """FAIL: Areas from wrong cluster should not be included."""
        # All areas are from CLUSTER_MESO_1, but we compute CLUSTER_MESO_2
        cluster1_pas = CLUSTER_COMPOSITION["CLUSTER_MESO_1"]
        area_scores = [generate_valid_area_score(pa) for pa in cluster1_pas]
        
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_cluster_score(area_scores, "CLUSTER_MESO_2")

    def test_empty_area_list_rejected(self):
        """FAIL: Empty input should raise error."""
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_cluster_score([], "CLUSTER_MESO_1")

    def test_extra_area_from_other_cluster(self, generate_cluster_area_scores, generate_valid_area_score):
        """TEST: Extra area from another cluster should be ignored."""
        # Get areas for CLUSTER_MESO_1
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1")
        # Add an area from CLUSTER_MESO_2 (PA04)
        area_scores.append(generate_valid_area_score("PA04", cluster_id="CLUSTER_MESO_2"))
        
        # Should still work - extra areas are filtered out
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        assert len(cluster_score.area_scores) == 3  # Only PA01, PA02, PA03


# =============================================================================
# 2. BOUNDS TESTS - Scores in [0.0, 3.0]
# =============================================================================


class TestBoundsValidation:
    """Tests for score bounds enforcement."""

    def test_score_within_bounds_accepted(
        self, generate_cluster_area_scores, validate_cluster_bounds
    ):
        """PASS: Score within [0.0, 3.0] accepted."""
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0)
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        valid, msg = validate_cluster_bounds(cluster_score)
        assert valid, f"Bounds validation failed: {msg}"

    def test_minimum_score_boundary(self, generate_cluster_area_scores):
        """PASS: Score exactly at minimum (0.0) is valid."""
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=0.0)
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        assert cluster_score.score >= MIN_SCORE

    def test_maximum_score_boundary(self, generate_cluster_area_scores):
        """PASS: Score exactly at maximum (3.0) is valid."""
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=3.0)
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        assert cluster_score.score <= MAX_SCORE

    def test_all_clusters_within_bounds(self, generate_all_area_scores, validate_cluster_bounds):
        """PASS: All 4 cluster scores within bounds."""
        all_areas = generate_all_area_scores()
        for cluster_id in CLUSTERS:
            cluster_score = compute_cluster_score(all_areas, cluster_id)
            valid, msg = validate_cluster_bounds(cluster_score)
            assert valid, f"Cluster {cluster_id} bounds failed: {msg}"

    def test_negative_area_score_handled(self, generate_valid_area_score):
        """ADVERSARIAL: Negative area scores should be handled gracefully."""
        # Create areas with one negative score
        areas = []
        for i, pa_id in enumerate(CLUSTER_COMPOSITION["CLUSTER_MESO_1"]):
            score = -1.0 if i == 0 else 2.0
            areas.append(generate_valid_area_score(pa_id, score=score, cluster_id="CLUSTER_MESO_1"))
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score.score >= MIN_SCORE


# =============================================================================
# 3. DISPERSION ANALYSIS TESTS
# =============================================================================


class TestDispersionAnalysis:
    """Tests for dispersion classification and adaptive penalty."""

    def test_convergence_classification(self, validate_dispersion_classification):
        """PASS: Low CV classified as convergence."""
        cv = 0.1  # < 0.2
        valid, msg = validate_dispersion_classification(cv, "convergence")
        assert valid, msg

    def test_moderate_classification(self, validate_dispersion_classification):
        """PASS: Moderate CV classified correctly."""
        cv = 0.3  # 0.2 <= cv < 0.4
        valid, msg = validate_dispersion_classification(cv, "moderate")
        assert valid, msg

    def test_high_classification(self, validate_dispersion_classification):
        """PASS: High CV classified correctly."""
        cv = 0.5  # 0.4 <= cv < 0.6
        valid, msg = validate_dispersion_classification(cv, "high")
        assert valid, msg

    def test_extreme_classification(self, validate_dispersion_classification):
        """PASS: Extreme CV classified correctly."""
        cv = 0.8  # >= 0.6
        valid, msg = validate_dispersion_classification(cv, "extreme")
        assert valid, msg

    def test_convergent_cluster_no_penalty(self, generate_convergent_cluster):
        """PASS: Convergent cluster has no penalty."""
        random.seed(42)
        area_scores = generate_convergent_cluster("CLUSTER_MESO_1", base_score=2.0)
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        
        # Convergent should have no/minimal penalty
        assert cluster_score.penalty_applied < 0.1

    def test_high_dispersion_cluster_penalty(self, generate_high_dispersion_cluster):
        """PASS: High dispersion cluster has penalty applied."""
        area_scores = generate_high_dispersion_cluster("CLUSTER_MESO_1")
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        
        # High dispersion should have penalty
        assert cluster_score.dispersion_scenario in ("high", "extreme")
        assert cluster_score.penalty_applied > 0

    def test_penalty_reduces_score(self, generate_high_dispersion_cluster):
        """PASS: Penalty reduces the final score."""
        area_scores = generate_high_dispersion_cluster("CLUSTER_MESO_1")
        
        # Compute with and without penalty
        cluster_with_penalty = compute_cluster_score(area_scores, "CLUSTER_MESO_1", apply_penalty=True)
        cluster_no_penalty = compute_cluster_score(area_scores, "CLUSTER_MESO_1", apply_penalty=False)
        
        # With penalty should have lower score
        assert cluster_with_penalty.score <= cluster_no_penalty.score

    @pytest.mark.parametrize("cv,expected", [
        (0.0, "convergence"),
        (0.19, "convergence"),
        (0.2, "moderate"),
        (0.39, "moderate"),
        (0.4, "high"),
        (0.59, "high"),
        (0.6, "extreme"),
        (1.0, "extreme"),
    ])
    def test_cv_boundary_classification(self, cv, expected, validate_dispersion_classification):
        """BOUNDARY: Test CV classification at exact boundaries."""
        valid, msg = validate_dispersion_classification(cv, expected)
        assert valid, msg


# =============================================================================
# 4. COHERENCE TESTS
# =============================================================================


class TestCoherenceValidation:
    """Tests for coherence computation and validation."""

    def test_perfect_coherence(self, generate_cluster_area_scores):
        """PASS: All same scores → coherence = 1.0."""
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0, variance=0.0)
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        assert cluster_score.coherence == 1.0

    def test_low_coherence(self, generate_high_dispersion_cluster):
        """PASS: High variance → low coherence."""
        area_scores = generate_high_dispersion_cluster("CLUSTER_MESO_1")
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        assert cluster_score.coherence < COHERENCE_THRESHOLD_HIGH

    def test_coherence_bounds(self, generate_all_area_scores):
        """PASS: Coherence is always in [0.0, 1.0]."""
        all_areas = generate_all_area_scores()
        for cluster_id in CLUSTERS:
            cluster_score = compute_cluster_score(all_areas, cluster_id)
            assert 0.0 <= cluster_score.coherence <= 1.0

    def test_weakest_area_identified(self, generate_cluster_area_scores):
        """PASS: Weakest area is correctly identified."""
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0, variance=0.5)
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        
        # Find actual weakest
        actual_weakest = min(area_scores, key=lambda a: a.score).area_id
        assert cluster_score.weakest_area == actual_weakest


# =============================================================================
# 5. INPUT VALIDATION TESTS
# =============================================================================


class TestInputValidation:
    """Tests for input validation and error handling."""

    def test_nan_area_score_handled(self, generate_nan_area_score, generate_valid_area_score):
        """ADVERSARIAL: NaN area score should be detected."""
        areas = [
            generate_valid_area_score("PA01", cluster_id="CLUSTER_MESO_1"),
            generate_valid_area_score("PA02", cluster_id="CLUSTER_MESO_1"),
            generate_nan_area_score("PA03", "CLUSTER_MESO_1"),
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        # Result should not propagate NaN
        assert not math.isnan(cluster_score.score)

    def test_inf_area_score_handled(self, generate_inf_area_score, generate_valid_area_score):
        """ADVERSARIAL: Infinity area score should be handled."""
        areas = [
            generate_valid_area_score("PA01", cluster_id="CLUSTER_MESO_1"),
            generate_valid_area_score("PA02", cluster_id="CLUSTER_MESO_1"),
            generate_inf_area_score("PA03", "CLUSTER_MESO_1"),
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert not math.isinf(cluster_score.score)
        assert cluster_score.score <= MAX_SCORE

    def test_invalid_cluster_id_rejected(self, generate_valid_area_score):
        """ADVERSARIAL: Invalid cluster ID should fail."""
        areas = [generate_valid_area_score(pa) for pa in ["PA01", "PA02", "PA03"]]
        
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_cluster_score(areas, "INVALID_CLUSTER")


# =============================================================================
# 6. DETERMINISM TESTS
# =============================================================================


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self, generate_all_area_scores):
        """PASS: Same inputs produce identical outputs."""
        random.seed(42)
        areas_1 = generate_all_area_scores()
        
        random.seed(42)
        areas_2 = generate_all_area_scores()
        
        for cluster_id in CLUSTERS:
            score_1 = compute_cluster_score(areas_1, cluster_id)
            score_2 = compute_cluster_score(areas_2, cluster_id)
            assert abs(score_1.score - score_2.score) < 1e-9

    def test_order_independence(self, generate_cluster_area_scores):
        """PASS: Area order should not affect result."""
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0)
        score_1 = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        
        # Reverse order
        area_scores_reversed = list(reversed(area_scores))
        score_2 = compute_cluster_score(area_scores_reversed, "CLUSTER_MESO_1")
        
        assert abs(score_1.score - score_2.score) < 1e-9

    def test_multiple_runs_identical(self, generate_cluster_area_scores):
        """PASS: Multiple runs produce identical results."""
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0)
        
        results = []
        for _ in range(10):
            cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
            results.append(cluster_score.score)
        
        assert all(abs(r - results[0]) < 1e-9 for r in results)


# =============================================================================
# 7. EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_all_zero_scores(self, generate_valid_area_score):
        """EDGE: All areas have score 0.0."""
        areas = [
            generate_valid_area_score(pa, score=0.0, cluster_id="CLUSTER_MESO_1")
            for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]
        ]
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score.score == 0.0

    def test_all_max_scores(self, generate_valid_area_score):
        """EDGE: All areas have maximum score 3.0."""
        areas = [
            generate_valid_area_score(pa, score=3.0, cluster_id="CLUSTER_MESO_1")
            for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]
        ]
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score.score == 3.0

    def test_two_area_cluster(self, generate_valid_area_score):
        """EDGE: Cluster with only 2 areas (CLUSTER_MESO_3, CLUSTER_MESO_4)."""
        for cluster_id in ["CLUSTER_MESO_3", "CLUSTER_MESO_4"]:
            areas = [
                generate_valid_area_score(pa, cluster_id=cluster_id)
                for pa in CLUSTER_COMPOSITION[cluster_id]
            ]
            cluster_score = compute_cluster_score(areas, cluster_id)
            assert len(cluster_score.area_scores) == 2

    def test_three_area_cluster(self, generate_valid_area_score):
        """EDGE: Cluster with 3 areas (CLUSTER_MESO_1, CLUSTER_MESO_2)."""
        for cluster_id in ["CLUSTER_MESO_1", "CLUSTER_MESO_2"]:
            areas = [
                generate_valid_area_score(pa, cluster_id=cluster_id)
                for pa in CLUSTER_COMPOSITION[cluster_id]
            ]
            cluster_score = compute_cluster_score(areas, cluster_id)
            assert len(cluster_score.area_scores) == 3

    def test_single_low_area_in_cluster(self, generate_valid_area_score):
        """EDGE: One very low score among high scores."""
        areas = []
        for i, pa in enumerate(CLUSTER_COMPOSITION["CLUSTER_MESO_1"]):
            score = 0.0 if i == 0 else 3.0
            areas.append(generate_valid_area_score(pa, score=score, cluster_id="CLUSTER_MESO_1"))
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        # Weakest should be identified
        assert cluster_score.weakest_area == "PA01"

    def test_cv_compute_edge_cases(self):
        """EDGE: CV computation edge cases."""
        # Single value
        assert compute_cv([2.0]) == 0.0
        
        # Empty list
        assert compute_cv([]) == 0.0
        
        # All same values
        assert compute_cv([2.0, 2.0, 2.0]) == 0.0
        
        # All zeros (mean = 0)
        assert compute_cv([0.0, 0.0, 0.0]) == 0.0


# =============================================================================
# 8. STATISTICAL BEHAVIOR TESTS
# =============================================================================


class TestStatisticalBehavior:
    """Tests for statistical properties of aggregation."""

    def test_variance_preserved_in_output(self, generate_cluster_area_scores):
        """STATISTICAL: Variance is computed and stored."""
        area_scores = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0, variance=0.3)
        cluster_score = compute_cluster_score(area_scores, "CLUSTER_MESO_1")
        
        # Variance should be populated
        assert cluster_score.variance >= 0

    def test_coherence_inversely_related_to_variance(self, generate_cluster_area_scores):
        """STATISTICAL: Higher variance → lower coherence."""
        # Low variance
        low_var_areas = generate_cluster_area_scores("CLUSTER_MESO_1", variance=0.1)
        low_var_score = compute_cluster_score(low_var_areas, "CLUSTER_MESO_1")
        
        # High variance
        high_var_areas = generate_cluster_area_scores("CLUSTER_MESO_1", variance=0.8)
        high_var_score = compute_cluster_score(high_var_areas, "CLUSTER_MESO_1")
        
        assert low_var_score.coherence >= high_var_score.coherence


# =============================================================================
# 9. FULL PIPELINE TESTS
# =============================================================================


class TestFullPipeline:
    """Tests for complete Phase 6 pipeline (10 → 4)."""

    def test_complete_aggregation_all_clusters(
        self, generate_all_area_scores, assert_all_clusters_present
    ):
        """PASS: Complete pipeline produces 4 ClusterScores."""
        all_areas = generate_all_area_scores()
        
        cluster_scores = []
        for cluster_id in CLUSTERS:
            cluster_score = compute_cluster_score(all_areas, cluster_id)
            cluster_scores.append(cluster_score)
        
        assert len(cluster_scores) == EXPECTED_CLUSTER_COUNT
        assert_all_clusters_present(cluster_scores)

    def test_no_duplicate_clusters_in_output(self, generate_all_area_scores):
        """PASS: No duplicate cluster IDs in output."""
        all_areas = generate_all_area_scores()
        
        cluster_scores = []
        for cluster_id in CLUSTERS:
            cluster_score = compute_cluster_score(all_areas, cluster_id)
            cluster_scores.append(cluster_score)
        
        cluster_ids = [s.cluster_id for s in cluster_scores]
        assert len(cluster_ids) == len(set(cluster_ids))

    def test_all_pas_covered_once(self, generate_all_area_scores):
        """PASS: Each PA appears in exactly one cluster."""
        all_areas = generate_all_area_scores()
        
        all_pas_in_clusters = []
        for cluster_id in CLUSTERS:
            cluster_score = compute_cluster_score(all_areas, cluster_id)
            all_pas_in_clusters.extend([a.area_id for a in cluster_score.area_scores])
        
        assert len(all_pas_in_clusters) == 10
        assert set(all_pas_in_clusters) == set(POLICY_AREAS)

    def test_cluster_composition_matches_canonical(self, generate_all_area_scores):
        """PASS: Cluster composition matches canonical definition."""
        all_areas = generate_all_area_scores()
        
        for cluster_id in CLUSTERS:
            cluster_score = compute_cluster_score(all_areas, cluster_id)
            expected_pas = set(CLUSTER_COMPOSITION[cluster_id])
            actual_pas = {a.area_id for a in cluster_score.area_scores}
            assert actual_pas == expected_pas
