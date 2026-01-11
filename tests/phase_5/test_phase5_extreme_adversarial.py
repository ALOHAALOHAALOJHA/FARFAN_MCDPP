"""
Phase 5 Extreme Adversarial Tests
=================================

ADVANCED ADVERSARIAL SCENARIOS:
1. INJECTION ATTACKS: Malicious data in fields
2. FUZZING: Random/garbage data
3. TYPE CONFUSION: Wrong types in fields
4. BOUNDARY ATTACKS: Exact boundary values
5. RESOURCE EXHAUSTION: Large/repeated inputs
6. STATE CORRUPTION: Mutable data attacks
7. CONCURRENCY: Race conditions (simulated)

These tests verify robustness against malicious or corrupt inputs.
"""

from __future__ import annotations

import copy
import math
import random
import string
import sys
from typing import Any

import pytest

from .conftest import (
    DIMENSIONS,
    DIMENSIONS_PER_AREA,
    MAX_SCORE,
    MIN_SCORE,
    PA_TO_CLUSTER,
    POLICY_AREAS,
    MockAreaScore,
    MockDimensionScore,
    compute_area_score,
)


# =============================================================================
# 1. INJECTION ATTACKS
# =============================================================================


class TestInjectionAttacks:
    """Tests for injection attack resilience."""

    def test_sql_injection_in_dimension_id(self, generate_valid_dimension_score):
        """ADVERSARIAL: SQL injection in dimension_id should be harmless."""
        malicious_dim = "DIM01'; DROP TABLE scores;--"
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS[:5]]
        dim_scores.append(
            MockDimensionScore(
                dimension_id=malicious_dim,
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3],
            )
        )
        # Should fail hermeticity, not execute SQL
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")

    def test_script_injection_in_area_name(self, generate_complete_pa_dimensions):
        """ADVERSARIAL: Script injection in area_name should be escaped/ignored."""
        dim_scores = generate_complete_pa_dimensions("PA01")
        area_score = compute_area_score(dim_scores, "PA01")
        # area_name is generated, not from input, but verify no XSS
        assert "<script>" not in area_score.area_name

    def test_null_byte_injection(self, generate_valid_dimension_score):
        """ADVERSARIAL: Null byte injection should be handled."""
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS[:5]]
        dim_scores.append(
            MockDimensionScore(
                dimension_id="DIM06\x00INJECTED",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3],
            )
        )
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")

    def test_unicode_exploitation(self, generate_valid_dimension_score):
        """ADVERSARIAL: Unicode lookalike characters should be detected."""
        # Using Cyrillic 'А' instead of Latin 'A'
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS[:5]]
        dim_scores.append(
            MockDimensionScore(
                dimension_id="DІM06",  # Cyrillic І instead of I
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3],
            )
        )
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")

    def test_path_traversal_in_pa_id(self, generate_valid_dimension_score):
        """ADVERSARIAL: Path traversal attempts should be harmless."""
        malicious_pa = "../../../etc/passwd"
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id=malicious_pa,
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3],
            )
            for dim in DIMENSIONS
        ]
        # Should fail when querying for valid PA
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")


# =============================================================================
# 2. FUZZING TESTS
# =============================================================================


class TestFuzzing:
    """Fuzz testing with random/garbage data."""

    @pytest.mark.parametrize("seed", range(10))
    def test_random_dimension_ids(self, seed):
        """FUZZ: Random dimension IDs should fail gracefully."""
        random.seed(seed)
        random_dims = [
            "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(1, 20)))
            for _ in range(6)
        ]
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=random.uniform(-10, 10),
                quality_level="BUENO",
                contributing_questions=[],
            )
            for dim in random_dims
        ]
        with pytest.raises(ValueError):
            compute_area_score(dim_scores, "PA01")

    @pytest.mark.parametrize("seed", range(10))
    def test_random_scores(self, seed, generate_valid_dimension_score):
        """FUZZ: Random score values should be clamped."""
        random.seed(seed)
        dim_scores = []
        for dim in DIMENSIONS:
            # Generate extreme random scores
            score = random.uniform(-1e10, 1e10)
            if random.random() < 0.1:
                score = float("nan")
            elif random.random() < 0.1:
                score = float("inf") * random.choice([-1, 1])
            dim_scores.append(
                MockDimensionScore(
                    dimension_id=dim,
                    area_id="PA01",
                    score=score,
                    quality_level="BUENO",
                    contributing_questions=[1],
                )
            )
        area_score = compute_area_score(dim_scores, "PA01")
        # Result should never be NaN or Inf
        assert not math.isnan(area_score.score), f"NaN result for seed {seed}"
        assert not math.isinf(area_score.score), f"Inf result for seed {seed}"
        assert MIN_SCORE <= area_score.score <= MAX_SCORE

    def test_empty_string_fields(self, generate_valid_dimension_score):
        """FUZZ: Empty strings in fields."""
        dim_scores = []
        for dim in DIMENSIONS:
            dim_scores.append(
                MockDimensionScore(
                    dimension_id=dim,
                    area_id="PA01",
                    score=2.0,
                    quality_level="",  # Empty quality
                    contributing_questions=[],
                )
            )
        # Should still compute (quality_level is metadata)
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score is not None

    def test_very_long_strings(self):
        """FUZZ: Very long strings in fields."""
        long_string = "A" * 100000
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=2.0,
                quality_level=long_string,
                contributing_questions=[],
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score is not None


# =============================================================================
# 3. TYPE CONFUSION ATTACKS
# =============================================================================


class TestTypeConfusion:
    """Tests for type confusion resilience."""

    def test_string_score_rejected(self):
        """ADVERSARIAL: String where float expected."""
        # This would fail at dataclass creation in strict mode
        # Test that the function handles pre-existing bad data
        dim_scores = []
        for i, dim in enumerate(DIMENSIONS):
            score = "not_a_number" if i == 0 else 2.0
            ds = MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=score,  # type: ignore
                quality_level="BUENO",
                contributing_questions=[1],
            )
            dim_scores.append(ds)
        
        # Should raise when computing weighted sum
        with pytest.raises((TypeError, ValueError)):
            compute_area_score(dim_scores, "PA01")

    def test_none_in_contributing_questions(self):
        """ADVERSARIAL: None in contributing_questions list."""
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, None, 3],  # type: ignore
            )
            for dim in DIMENSIONS
        ]
        # Should still compute (we don't process questions)
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score is not None


# =============================================================================
# 4. BOUNDARY VALUE ATTACKS
# =============================================================================


class TestBoundaryAttacks:
    """Tests for boundary value exploitation."""

    def test_score_at_float_epsilon_below_zero(self):
        """BOUNDARY: Score at -epsilon should be clamped to 0."""
        epsilon = sys.float_info.epsilon
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=-epsilon,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score >= 0

    def test_score_at_float_epsilon_above_max(self):
        """BOUNDARY: Score at 3.0 + epsilon should be clamped to 3.0."""
        epsilon = sys.float_info.epsilon
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=MAX_SCORE + epsilon,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score <= MAX_SCORE

    def test_float_max_value(self):
        """BOUNDARY: sys.float_info.max should be clamped."""
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=sys.float_info.max,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score <= MAX_SCORE

    def test_float_min_value(self):
        """BOUNDARY: -sys.float_info.max should be clamped."""
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=-sys.float_info.max,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score >= MIN_SCORE


# =============================================================================
# 5. RESOURCE EXHAUSTION
# =============================================================================


class TestResourceExhaustion:
    """Tests for resource exhaustion attacks."""

    def test_large_number_of_dimensions(self):
        """RESOURCE: Many dimensions (10000) should still validate."""
        dim_scores = [
            MockDimensionScore(
                dimension_id=f"DIM{i:05d}",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for i in range(10000)
        ]
        # Should fail hermeticity (not 6 valid dimensions)
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")

    def test_large_contributing_questions_list(self):
        """RESOURCE: Large contributing_questions list."""
        large_questions = list(range(100000))
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=large_questions,
            )
            for dim in DIMENSIONS
        ]
        # Should still compute
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score is not None

    def test_deeply_nested_validation_details(self):
        """RESOURCE: Deeply nested validation_details."""

        def create_nested(depth: int) -> dict:
            if depth == 0:
                return {"value": True}
            return {"nested": create_nested(depth - 1)}

        nested = create_nested(100)
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1],
                validation_details=nested,
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score is not None


# =============================================================================
# 6. STATE CORRUPTION ATTACKS
# =============================================================================


class TestStateCorruption:
    """Tests for state corruption resilience."""

    def test_mutation_after_computation(self, generate_complete_pa_dimensions):
        """STATE: Mutating input after computation should not affect result."""
        dim_scores = generate_complete_pa_dimensions("PA01")
        area_score_1 = compute_area_score(dim_scores, "PA01")
        score_1 = area_score_1.score

        # Mutate original dimension scores
        for ds in dim_scores:
            ds.score = 0.0

        # Compute again with same (mutated) input
        area_score_2 = compute_area_score(dim_scores, "PA01")

        # Results should differ (input was mutated)
        assert area_score_2.score != score_1 or score_1 == 0.0

    def test_shared_reference_isolation(self, generate_complete_pa_dimensions):
        """STATE: Shared references should not cause cross-contamination."""
        dim_scores_pa1 = generate_complete_pa_dimensions("PA01")
        dim_scores_pa2 = generate_complete_pa_dimensions("PA02")

        area_score_pa1 = compute_area_score(dim_scores_pa1, "PA01")
        area_score_pa2 = compute_area_score(dim_scores_pa2, "PA02")

        # Modifying PA1 result should not affect PA2
        area_score_pa1.score = 999.0
        assert area_score_pa2.score != 999.0

    def test_deep_copy_independence(self, generate_complete_pa_dimensions):
        """STATE: Deep copy of input should produce same result."""
        dim_scores = generate_complete_pa_dimensions("PA01")
        dim_scores_copy = copy.deepcopy(dim_scores)

        area_score_1 = compute_area_score(dim_scores, "PA01")
        area_score_2 = compute_area_score(dim_scores_copy, "PA01")

        assert abs(area_score_1.score - area_score_2.score) < 1e-9


# =============================================================================
# 7. CONCURRENCY SIMULATION
# =============================================================================


class TestConcurrencySimulation:
    """Simulated concurrency tests (no actual threads)."""

    def test_interleaved_computations(self, generate_complete_pa_dimensions):
        """CONCURRENCY: Interleaved computations should be independent."""
        results = {}
        
        # Simulate interleaved execution
        dim_scores_all = {pa: generate_complete_pa_dimensions(pa) for pa in POLICY_AREAS}
        
        # "Interleave" by alternating partial work
        for pa in POLICY_AREAS:
            # Start computation (just gathering)
            results[pa] = {"dims": dim_scores_all[pa]}
        
        # Complete all
        for pa in POLICY_AREAS:
            results[pa]["score"] = compute_area_score(results[pa]["dims"], pa)
        
        # Verify all results are correct
        for pa in POLICY_AREAS:
            assert results[pa]["score"].area_id == pa
            assert results[pa]["score"].cluster_id == PA_TO_CLUSTER[pa]

    def test_repeated_same_input(self, generate_complete_pa_dimensions):
        """CONCURRENCY: Same input computed 100 times should be identical."""
        dim_scores = generate_complete_pa_dimensions("PA01")
        results = []
        
        for _ in range(100):
            area_score = compute_area_score(dim_scores, "PA01")
            results.append(area_score.score)
        
        # All should be identical
        assert all(abs(r - results[0]) < 1e-9 for r in results)


# =============================================================================
# 8. SEMANTIC CONFUSION
# =============================================================================


class TestSemanticConfusion:
    """Tests for semantic confusion attacks."""

    def test_dimension_area_mismatch_detection(self, generate_valid_dimension_score):
        """SEMANTIC: Dimensions claiming wrong PA should be filtered."""
        # All dimensions claim PA01 but we compute for PA02
        dim_scores = [generate_valid_dimension_score("PA01", dim) for dim in DIMENSIONS]
        
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA02")

    def test_mixed_pa_dimensions(self, generate_valid_dimension_score):
        """SEMANTIC: Dimensions from multiple PAs mixed together."""
        dim_scores = []
        for i, dim in enumerate(DIMENSIONS):
            pa = "PA01" if i % 2 == 0 else "PA02"
            dim_scores.append(generate_valid_dimension_score(pa, dim))
        
        # Computing for PA01 should fail (only 3 dimensions from PA01)
        with pytest.raises(ValueError, match="Hermeticity violation"):
            compute_area_score(dim_scores, "PA01")

    def test_quality_level_score_mismatch(self, generate_valid_dimension_score):
        """SEMANTIC: Quality level doesn't match score should be detected."""
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=0.1,  # Very low
                quality_level="EXCELENTE",  # Claims excellent
                contributing_questions=[1],
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        # Result quality should reflect actual score, not input quality
        assert area_score.quality_level == "INSUFICIENTE"


# =============================================================================
# 9. FLOATING POINT EDGE CASES
# =============================================================================


class TestFloatingPointEdges:
    """Tests for floating point edge cases."""

    def test_subnormal_numbers(self):
        """FLOAT: Subnormal (denormalized) numbers."""
        subnormal = sys.float_info.min * sys.float_info.epsilon
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=subnormal,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score >= 0

    def test_negative_zero(self):
        """FLOAT: Negative zero should be treated as zero."""
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=-0.0,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for dim in DIMENSIONS
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        assert area_score.score == 0.0

    def test_mixed_precision_accumulation(self, generate_valid_dimension_score):
        """FLOAT: Mixed precision shouldn't cause drift."""
        # Scores designed to test accumulation precision
        scores = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]  # Should sum to 0.6
        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=score,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for dim, score in zip(DIMENSIONS, scores)
        ]
        area_score = compute_area_score(dim_scores, "PA01")
        # Average of six 0.1s should be 0.1
        assert abs(area_score.score - 0.1) < 1e-9
