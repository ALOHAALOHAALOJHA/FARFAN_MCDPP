"""
Phase 6 Extreme Adversarial Tests
=================================

ADVANCED ADVERSARIAL SCENARIOS:
1. INJECTION ATTACKS: Malicious data in fields
2. FUZZING: Random/garbage data
3. BOUNDARY ATTACKS: Exact boundary values
4. RESOURCE EXHAUSTION: Large/repeated inputs
5. STATE CORRUPTION: Mutable data attacks
6. PENALTY EDGE CASES: Extreme penalty scenarios
7. CROSS-CLUSTER ATTACKS: Cluster confusion
"""

from __future__ import annotations

import copy
import math
import random
import string
import sys

import pytest

from .conftest import (
    CLUSTER_COMPOSITION,
    CLUSTERS,
    DISPERSION_THRESHOLDS,
    EXPECTED_CLUSTER_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    PENALTY_WEIGHT,
    POLICY_AREAS,
    MockAreaScore,
    MockClusterScore,
    MockDimensionScore,
    classify_dispersion,
    compute_cluster_score,
    compute_coherence,
    compute_cv,
)


# =============================================================================
# 1. INJECTION ATTACKS
# =============================================================================


class TestInjectionAttacks:
    """Tests for injection attack resilience."""

    def test_sql_injection_in_cluster_id(self, generate_valid_area_score):
        """ADVERSARIAL: SQL injection in cluster_id should be harmless."""
        malicious_cluster = "CLUSTER'; DROP TABLE clusters;--"
        areas = [generate_valid_area_score(pa) for pa in ["PA01", "PA02", "PA03"]]
        
        # Should fail with hermeticity violation, not execute SQL
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_cluster_score(areas, malicious_cluster)

    def test_null_byte_injection(self, generate_valid_area_score):
        """ADVERSARIAL: Null byte injection in area_id."""
        areas = [
            MockAreaScore(
                area_id="PA01\x00INJECTED",
                area_name="Test",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CLUSTER_MESO_1",
            ),
            generate_valid_area_score("PA02", cluster_id="CLUSTER_MESO_1"),
            generate_valid_area_score("PA03", cluster_id="CLUSTER_MESO_1"),
        ]
        
        # Should fail hermeticity (PA01 doesn't match)
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_cluster_score(areas, "CLUSTER_MESO_1")

    def test_unicode_lookalike_cluster(self, generate_valid_area_score):
        """ADVERSARIAL: Unicode lookalike in cluster name."""
        # Using Cyrillic characters
        malicious_cluster = "СLUSTER_MESO_1"  # Cyrillic С instead of C
        areas = [generate_valid_area_score(pa) for pa in ["PA01", "PA02", "PA03"]]
        
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_cluster_score(areas, malicious_cluster)


# =============================================================================
# 2. FUZZING TESTS
# =============================================================================


class TestFuzzing:
    """Fuzz testing with random/garbage data."""

    @pytest.mark.parametrize("seed", range(10))
    def test_random_cluster_ids(self, seed, generate_valid_area_score):
        """FUZZ: Random cluster IDs should fail gracefully."""
        random.seed(seed)
        random_cluster = "".join(random.choices(string.ascii_letters + string.digits, k=20))
        areas = [generate_valid_area_score(pa) for pa in ["PA01", "PA02", "PA03"]]
        
        with pytest.raises(ValueError):
            compute_cluster_score(areas, random_cluster)

    @pytest.mark.parametrize("seed", range(10))
    def test_random_area_scores(self, seed, generate_valid_area_score):
        """FUZZ: Random score values should be handled."""
        random.seed(seed)
        areas = []
        for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]:
            score = random.uniform(-1e10, 1e10)
            if random.random() < 0.1:
                score = float("nan")
            elif random.random() < 0.1:
                score = float("inf") * random.choice([-1, 1])
            areas.append(
                MockAreaScore(
                    area_id=pa,
                    area_name=f"Area {pa}",
                    score=score,
                    quality_level="BUENO",
                    dimension_scores=[],
                    cluster_id="CLUSTER_MESO_1",
                )
            )
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert not math.isnan(cluster_score.score)
        assert not math.isinf(cluster_score.score)
        assert MIN_SCORE <= cluster_score.score <= MAX_SCORE

    def test_very_long_area_name(self, generate_valid_area_score):
        """FUZZ: Very long area names."""
        long_name = "A" * 100000
        areas = []
        for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]:
            areas.append(
                MockAreaScore(
                    area_id=pa,
                    area_name=long_name,
                    score=2.0,
                    quality_level="BUENO",
                    dimension_scores=[],
                    cluster_id="CLUSTER_MESO_1",
                )
            )
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score is not None


# =============================================================================
# 3. BOUNDARY VALUE ATTACKS
# =============================================================================


class TestBoundaryAttacks:
    """Tests for boundary value exploitation."""

    def test_score_at_float_epsilon_below_zero(self, generate_valid_area_score):
        """BOUNDARY: Score at -epsilon should be clamped."""
        epsilon = sys.float_info.epsilon
        areas = [
            MockAreaScore(
                area_id=pa,
                area_name=f"Area {pa}",
                score=-epsilon,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CLUSTER_MESO_1",
            )
            for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score.score >= 0

    def test_score_at_float_max(self, generate_valid_area_score):
        """BOUNDARY: sys.float_info.max should be clamped."""
        areas = [
            MockAreaScore(
                area_id=pa,
                area_name=f"Area {pa}",
                score=sys.float_info.max,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CLUSTER_MESO_1",
            )
            for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score.score <= MAX_SCORE

    def test_cv_at_threshold_boundaries(self):
        """BOUNDARY: CV at exact threshold boundaries."""
        # At convergence boundary
        assert classify_dispersion(0.199999) == "convergence"
        assert classify_dispersion(0.2) == "moderate"
        
        # At moderate boundary
        assert classify_dispersion(0.399999) == "moderate"
        assert classify_dispersion(0.4) == "high"
        
        # At high boundary
        assert classify_dispersion(0.599999) == "high"
        assert classify_dispersion(0.6) == "extreme"


# =============================================================================
# 4. PENALTY EDGE CASES
# =============================================================================


class TestPenaltyEdgeCases:
    """Tests for penalty computation edge cases."""

    def test_zero_cv_no_penalty(self, generate_cluster_area_scores):
        """PENALTY: Zero CV should have no penalty."""
        # All same scores → CV = 0
        areas = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0, variance=0.0)
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        
        assert cluster_score.dispersion_scenario == "convergence"
        assert cluster_score.penalty_applied == 0.0

    def test_maximum_penalty(self, generate_valid_area_score):
        """PENALTY: Maximum possible penalty."""
        # Create extreme dispersion
        areas = [
            MockAreaScore(
                area_id=pa,
                area_name=f"Area {pa}",
                score=0.0 if i == 0 else 3.0,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CLUSTER_MESO_1",
            )
            for i, pa in enumerate(CLUSTER_COMPOSITION["CLUSTER_MESO_1"])
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        
        # Penalty should be applied
        assert cluster_score.penalty_applied > 0
        # But score should still be in bounds
        assert MIN_SCORE <= cluster_score.score <= MAX_SCORE

    def test_penalty_does_not_exceed_score(self, generate_valid_area_score):
        """PENALTY: Penalty should not make score negative."""
        # Low scores with high dispersion
        areas = [
            MockAreaScore(
                area_id=pa,
                area_name=f"Area {pa}",
                score=0.1 if i == 0 else 0.5,
                quality_level="INSUFICIENTE",
                dimension_scores=[],
                cluster_id="CLUSTER_MESO_1",
            )
            for i, pa in enumerate(CLUSTER_COMPOSITION["CLUSTER_MESO_1"])
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score.score >= MIN_SCORE

    def test_penalty_disabled(self, generate_high_dispersion_cluster):
        """PENALTY: Can disable penalty application."""
        areas = generate_high_dispersion_cluster("CLUSTER_MESO_1")
        
        score_with_penalty = compute_cluster_score(areas, "CLUSTER_MESO_1", apply_penalty=True)
        score_no_penalty = compute_cluster_score(areas, "CLUSTER_MESO_1", apply_penalty=False)
        
        assert score_no_penalty.penalty_applied == 0.0
        assert score_with_penalty.score <= score_no_penalty.score


# =============================================================================
# 5. STATE CORRUPTION ATTACKS
# =============================================================================


class TestStateCorruption:
    """Tests for state corruption resilience."""

    def test_mutation_after_computation(self, generate_cluster_area_scores):
        """STATE: Mutating input after computation."""
        areas = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0)
        score_1 = compute_cluster_score(areas, "CLUSTER_MESO_1").score
        
        # Mutate original areas
        for area in areas:
            area.score = 0.0
        
        # Compute again with mutated input
        score_2 = compute_cluster_score(areas, "CLUSTER_MESO_1").score
        
        # Results should differ (input was mutated)
        assert score_2 != score_1 or score_1 == 0.0

    def test_deep_copy_independence(self, generate_cluster_area_scores):
        """STATE: Deep copy should produce same result."""
        areas = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0)
        areas_copy = copy.deepcopy(areas)
        
        score_1 = compute_cluster_score(areas, "CLUSTER_MESO_1")
        score_2 = compute_cluster_score(areas_copy, "CLUSTER_MESO_1")
        
        assert abs(score_1.score - score_2.score) < 1e-9

    def test_shared_area_reference(self, generate_cluster_area_scores):
        """STATE: Shared area references between clusters."""
        # Create areas for cluster 1
        areas_cluster1 = generate_cluster_area_scores("CLUSTER_MESO_1")
        # Create areas for cluster 2
        areas_cluster2 = generate_cluster_area_scores("CLUSTER_MESO_2")
        
        score_1 = compute_cluster_score(areas_cluster1, "CLUSTER_MESO_1")
        score_2 = compute_cluster_score(areas_cluster2, "CLUSTER_MESO_2")
        
        # Modifying one should not affect the other
        score_1.score = 999.0
        assert score_2.score != 999.0


# =============================================================================
# 6. CROSS-CLUSTER ATTACKS
# =============================================================================


class TestCrossClusterAttacks:
    """Tests for cross-cluster boundary violations."""

    def test_area_with_wrong_cluster_id(self, generate_valid_area_score):
        """CROSS-CLUSTER: Area claims wrong cluster."""
        # PA01 belongs to CLUSTER_MESO_1, but we set cluster_id to CLUSTER_MESO_2
        areas = [
            MockAreaScore(
                area_id="PA01",
                area_name="Area PA01",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CLUSTER_MESO_2",  # Wrong cluster
            ),
            generate_valid_area_score("PA02", cluster_id="CLUSTER_MESO_1"),
            generate_valid_area_score("PA03", cluster_id="CLUSTER_MESO_1"),
        ]
        
        # Should still work - we filter by area_id, not by cluster_id attribute
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert len(cluster_score.area_scores) == 3

    def test_mixed_cluster_areas(self, generate_valid_area_score):
        """CROSS-CLUSTER: Areas from multiple clusters mixed."""
        # Mix areas from cluster 1 and cluster 2
        areas = [
            generate_valid_area_score("PA01", cluster_id="CLUSTER_MESO_1"),
            generate_valid_area_score("PA04", cluster_id="CLUSTER_MESO_2"),  # Wrong cluster
            generate_valid_area_score("PA03", cluster_id="CLUSTER_MESO_1"),
        ]
        
        # Should fail - PA02 missing from cluster 1
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_cluster_score(areas, "CLUSTER_MESO_1")

    def test_duplicate_area_in_cluster(self, generate_valid_area_score):
        """CROSS-CLUSTER: Duplicate area in same cluster."""
        areas = [
            generate_valid_area_score("PA01", cluster_id="CLUSTER_MESO_1"),
            generate_valid_area_score("PA01", score=3.0, cluster_id="CLUSTER_MESO_1"),  # Duplicate
            generate_valid_area_score("PA02", cluster_id="CLUSTER_MESO_1"),
            generate_valid_area_score("PA03", cluster_id="CLUSTER_MESO_1"),
        ]
        
        # Should work - duplicate is filtered by set, but which score is used?
        # The implementation uses list comprehension, so both would be included
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        # We have 4 areas but set {PA01, PA02, PA03} = 3 unique
        # Filter only keeps PA01, PA02, PA03 → all 4 areas pass
        assert cluster_score is not None


# =============================================================================
# 7. FLOATING POINT EDGE CASES
# =============================================================================


class TestFloatingPointEdges:
    """Tests for floating point edge cases."""

    def test_subnormal_scores(self, generate_valid_area_score):
        """FLOAT: Subnormal (denormalized) numbers."""
        subnormal = sys.float_info.min * sys.float_info.epsilon
        areas = [
            MockAreaScore(
                area_id=pa,
                area_name=f"Area {pa}",
                score=subnormal,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CLUSTER_MESO_1",
            )
            for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score.score >= 0

    def test_negative_zero(self, generate_valid_area_score):
        """FLOAT: Negative zero should be treated as zero."""
        areas = [
            MockAreaScore(
                area_id=pa,
                area_name=f"Area {pa}",
                score=-0.0,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CLUSTER_MESO_1",
            )
            for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score.score == 0.0

    def test_cv_with_tiny_mean(self):
        """FLOAT: CV with very small mean."""
        scores = [0.0001, 0.0002, 0.0003]
        cv = compute_cv(scores)
        assert math.isfinite(cv)

    def test_coherence_with_zero_variance(self):
        """FLOAT: Coherence with zero variance."""
        scores = [2.0, 2.0, 2.0]
        coherence = compute_coherence(scores)
        assert coherence == 1.0


# =============================================================================
# 8. RESOURCE EXHAUSTION
# =============================================================================


class TestResourceExhaustion:
    """Tests for resource exhaustion attacks."""

    def test_large_dimension_scores_list(self, generate_valid_area_score):
        """RESOURCE: Large dimension_scores list in areas."""
        large_dims = [
            MockDimensionScore(
                dimension_id=f"DIM{i:05d}",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for i in range(10000)
        ]
        
        areas = [
            MockAreaScore(
                area_id=pa,
                area_name=f"Area {pa}",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=large_dims if pa == "PA01" else [],
                cluster_id="CLUSTER_MESO_1",
            )
            for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]
        ]
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score is not None

    def test_repeated_computations(self, generate_cluster_area_scores):
        """RESOURCE: Many repeated computations."""
        areas = generate_cluster_area_scores("CLUSTER_MESO_1", base_score=2.0)
        
        results = []
        for _ in range(1000):
            cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
            results.append(cluster_score.score)
        
        # All should be identical
        assert all(abs(r - results[0]) < 1e-9 for r in results)


# =============================================================================
# 9. INTEGRATION WITH PHASE 5 OUTPUT
# =============================================================================


class TestPhase5Integration:
    """Tests for integration with Phase 5 output format."""

    def test_accepts_phase5_area_score_format(self, generate_valid_area_score):
        """INTEGRATION: Accepts AreaScore format from Phase 5."""
        # Simulate Phase 5 output
        areas = []
        for pa in CLUSTER_COMPOSITION["CLUSTER_MESO_1"]:
            area = generate_valid_area_score(pa, cluster_id="CLUSTER_MESO_1")
            # Add Phase 5 specific fields
            area.validation_passed = True
            area.validation_details = {"hermeticity": True, "bounds": True}
            areas.append(area)
        
        cluster_score = compute_cluster_score(areas, "CLUSTER_MESO_1")
        assert cluster_score is not None

    def test_10_areas_produce_4_clusters(self, generate_all_area_scores):
        """INTEGRATION: 10 AreaScores produce 4 ClusterScores."""
        all_areas = generate_all_area_scores()
        
        cluster_scores = []
        for cluster_id in CLUSTERS:
            cluster_score = compute_cluster_score(all_areas, cluster_id)
            cluster_scores.append(cluster_score)
        
        assert len(cluster_scores) == 4
        
        # Verify all 10 PAs are covered
        all_pas = set()
        for cs in cluster_scores:
            all_pas.update(a.area_id for a in cs.area_scores)
        
        assert len(all_pas) == 10
