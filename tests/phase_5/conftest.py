"""
Pytest fixtures for Phase 5 adversarial tests.

Phase 5: Policy Area Aggregation (60 DimensionScore → 10 AreaScore)

ADVERSARIAL TESTING PILLARS:
1. HERMETICITY: Exactly 6 dimensions per policy area
2. BOUNDS: All scores in [0.0, 3.0]
3. CLUSTER MAPPING: Correct PA→Cluster assignments
4. INPUT VALIDATION: Reject malformed/incomplete inputs

REAL STRUCTURE:
- 10 Policy Areas: PA01-PA10
- 6 Dimensions per PA: DIM01-DIM06
- 4 Clusters: CL01-CL04
  - CL01: PA02, PA03, PA07
  - CL02: PA01, PA05, PA06
  - CL03: PA04, PA08
  - CL04: PA09, PA10
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


# =============================================================================
# CANONICAL CONSTANTS - Ground Truth for Phase 5
# =============================================================================

POLICY_AREAS = ["PA01", "PA02", "PA03", "PA04", "PA05", "PA06", "PA07", "PA08", "PA09", "PA10"]
DIMENSIONS = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]
DIMENSIONS_PER_AREA = 6
EXPECTED_AREA_COUNT = 10
MIN_SCORE = 0.0
MAX_SCORE = 3.0

# Real cluster mappings from canonical questionnaire
CLUSTER_TO_PAS = {
    "CL01": ["PA02", "PA03", "PA07"],
    "CL02": ["PA01", "PA05", "PA06"],
    "CL03": ["PA04", "PA08"],
    "CL04": ["PA09", "PA10"],
}

PA_TO_CLUSTER = {}
for cluster_id, pas in CLUSTER_TO_PAS.items():
    for pa in pas:
        PA_TO_CLUSTER[pa] = cluster_id

# Quality thresholds (normalized 0-1 scale)
QUALITY_THRESHOLDS = {
    "EXCELENTE": 0.85,
    "BUENO": 0.70,
    "ACEPTABLE": 0.55,
    "INSUFICIENTE": 0.0,
}


# =============================================================================
# LOCAL DATACLASSES - Isolated test models (no external dependencies)
# =============================================================================


@dataclass
class MockDimensionScore:
    """Test-local DimensionScore model for adversarial testing."""

    dimension_id: str
    area_id: str
    score: float
    quality_level: str
    contributing_questions: list[int | str]
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    epistemic_uncertainty: float = 0.0
    aleatoric_uncertainty: float = 0.0
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"


@dataclass
class MockAreaScore:
    """Test-local AreaScore model for adversarial testing."""

    area_id: str
    area_name: str
    score: float
    quality_level: str
    dimension_scores: list[MockDimensionScore]
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    cluster_id: str | None = None
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"


# =============================================================================
# PATH FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def cqc_base_path() -> Path:
    """Base path to the canonical questionnaire central."""
    return Path(__file__).resolve().parent.parent.parent / "canonic_questionnaire_central"


@pytest.fixture(scope="session")
def modular_manifest(cqc_base_path: Path) -> dict:
    """Load the modular manifest."""
    manifest_path = cqc_base_path / "modular_manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# =============================================================================
# DIMENSION SCORE GENERATORS - For adversarial testing
# =============================================================================


@pytest.fixture
def generate_valid_dimension_score():
    """Generate a valid DimensionScore for a specific PA and dimension."""

    def _generate(
        pa_id: str,
        dim_id: str,
        score: float = 2.0,
        quality_level: str = "BUENO",
        questions: list[int] | None = None,
    ) -> MockDimensionScore:
        return MockDimensionScore(
            dimension_id=dim_id,
            area_id=pa_id,
            score=score,
            quality_level=quality_level,
            contributing_questions=questions or [1, 2, 3, 4, 5],
            validation_passed=True,
            validation_details={"hermeticity": True, "bounds": True},
        )

    return _generate


@pytest.fixture
def generate_complete_pa_dimensions(generate_valid_dimension_score):
    """Generate all 6 DimensionScores for a policy area (complete hermeticity)."""

    def _generate(pa_id: str, base_score: float = 2.0) -> list[MockDimensionScore]:
        scores = []
        for dim in DIMENSIONS:
            # Add small variance for realism
            score = max(MIN_SCORE, min(MAX_SCORE, base_score + random.uniform(-0.3, 0.3)))
            scores.append(generate_valid_dimension_score(pa_id, dim, score))
        return scores

    return _generate


@pytest.fixture
def generate_all_dimension_scores(generate_complete_pa_dimensions):
    """Generate all 60 DimensionScores (10 PAs × 6 dimensions)."""

    def _generate(base_score: float = 2.0) -> list[MockDimensionScore]:
        all_scores = []
        for pa_id in POLICY_AREAS:
            all_scores.extend(generate_complete_pa_dimensions(pa_id, base_score))
        return all_scores

    return _generate


# =============================================================================
# ADVERSARIAL INPUT GENERATORS
# =============================================================================


@pytest.fixture
def generate_missing_dimension():
    """Generate DimensionScores with one dimension missing (hermeticity violation)."""

    def _generate(pa_id: str, missing_dim: str = "DIM03") -> list[MockDimensionScore]:
        scores = []
        for dim in DIMENSIONS:
            if dim == missing_dim:
                continue  # Skip to create hermeticity violation
            scores.append(
                MockDimensionScore(
                    dimension_id=dim,
                    area_id=pa_id,
                    score=2.0,
                    quality_level="BUENO",
                    contributing_questions=[1, 2, 3, 4, 5],
                )
            )
        return scores

    return _generate


@pytest.fixture
def generate_out_of_bounds_score():
    """Generate DimensionScores with out-of-bounds values."""

    def _generate(
        pa_id: str, dim_id: str, score: float, expect_clamped: bool = True
    ) -> MockDimensionScore:
        return MockDimensionScore(
            dimension_id=dim_id,
            area_id=pa_id,
            score=score,  # Could be negative or > 3.0
            quality_level="INSUFICIENTE" if score < 0.55 else "ACEPTABLE",
            contributing_questions=[1, 2, 3, 4, 5],
            validation_passed=False if not expect_clamped else True,
            validation_details={"bounds_violation": score < MIN_SCORE or score > MAX_SCORE},
        )

    return _generate


@pytest.fixture
def generate_duplicate_dimension():
    """Generate DimensionScores with duplicate dimensions (invalid)."""

    def _generate(pa_id: str, duplicate_dim: str = "DIM01") -> list[MockDimensionScore]:
        scores = []
        for dim in DIMENSIONS:
            scores.append(
                MockDimensionScore(
                    dimension_id=dim,
                    area_id=pa_id,
                    score=2.0,
                    quality_level="BUENO",
                    contributing_questions=[1, 2, 3, 4, 5],
                )
            )
        # Add duplicate
        scores.append(
            MockDimensionScore(
                dimension_id=duplicate_dim,
                area_id=pa_id,
                score=2.5,  # Different score to detect duplicate
                quality_level="BUENO",
                contributing_questions=[6, 7, 8, 9, 10],
            )
        )
        return scores

    return _generate


@pytest.fixture
def generate_wrong_pa_dimension():
    """Generate DimensionScore with mismatched PA ID."""

    def _generate(claimed_pa: str, actual_pa: str, dim_id: str) -> MockDimensionScore:
        return MockDimensionScore(
            dimension_id=dim_id,
            area_id=actual_pa,  # Wrong PA
            score=2.0,
            quality_level="BUENO",
            contributing_questions=[1, 2, 3, 4, 5],
        )

    return _generate


# =============================================================================
# AREA SCORE VALIDATORS
# =============================================================================


@pytest.fixture
def validate_area_score_hermeticity():
    """Validate that an AreaScore has exactly 6 dimensions."""

    def _validate(area_score: MockAreaScore) -> tuple[bool, str]:
        dim_count = len(area_score.dimension_scores)
        if dim_count != DIMENSIONS_PER_AREA:
            return False, f"Expected {DIMENSIONS_PER_AREA} dimensions, got {dim_count}"

        dim_ids = {ds.dimension_id for ds in area_score.dimension_scores}
        expected_dims = set(DIMENSIONS)
        if dim_ids != expected_dims:
            missing = expected_dims - dim_ids
            extra = dim_ids - expected_dims
            return False, f"Missing: {missing}, Extra: {extra}"

        return True, "Hermeticity OK"

    return _validate


@pytest.fixture
def validate_area_score_bounds():
    """Validate that an AreaScore has score in [0.0, 3.0]."""

    def _validate(area_score: MockAreaScore) -> tuple[bool, str]:
        if area_score.score < MIN_SCORE:
            return False, f"Score {area_score.score} below minimum {MIN_SCORE}"
        if area_score.score > MAX_SCORE:
            return False, f"Score {area_score.score} above maximum {MAX_SCORE}"
        return True, "Bounds OK"

    return _validate


@pytest.fixture
def validate_cluster_assignment():
    """Validate that AreaScore has correct cluster_id."""

    def _validate(area_score: MockAreaScore) -> tuple[bool, str]:
        expected_cluster = PA_TO_CLUSTER.get(area_score.area_id)
        if expected_cluster is None:
            return False, f"Unknown PA: {area_score.area_id}"
        if area_score.cluster_id != expected_cluster:
            return (
                False,
                f"PA {area_score.area_id} should be in {expected_cluster}, got {area_score.cluster_id}",
            )
        return True, "Cluster assignment OK"

    return _validate


# =============================================================================
# AREA AGGREGATION LOGIC - Isolated for testing
# =============================================================================


def compute_area_score(
    dimension_scores: list[MockDimensionScore],
    pa_id: str,
    weights: dict[str, float] | None = None,
) -> MockAreaScore:
    """
    Compute AreaScore from DimensionScores - test implementation.

    This is the logic that Phase 5 should implement. Tests verify this behavior.
    """
    # Filter scores for this PA
    pa_scores = [ds for ds in dimension_scores if ds.area_id == pa_id]

    # Validate hermeticity - check for duplicates AND exact count
    dim_ids = [ds.dimension_id for ds in pa_scores]
    unique_dim_ids = set(dim_ids)
    
    # Check for duplicates first
    if len(dim_ids) != len(unique_dim_ids):
        duplicates = [d for d in unique_dim_ids if dim_ids.count(d) > 1]
        raise ValueError(f"Hermeticity violation for {pa_id}: duplicate dimensions {duplicates}")
    
    # Check for correct count and exact set
    if len(unique_dim_ids) != DIMENSIONS_PER_AREA or unique_dim_ids != set(DIMENSIONS):
        raise ValueError(f"Hermeticity violation for {pa_id}: got {unique_dim_ids}")

    # Use equal weights if not specified
    if weights is None:
        weights = {dim: 1.0 / DIMENSIONS_PER_AREA for dim in DIMENSIONS}

    # Compute weighted average
    total_weight = sum(weights.values())
    weighted_sum = sum(ds.score * weights.get(ds.dimension_id, 0) for ds in pa_scores)
    score = weighted_sum / total_weight if total_weight > 0 else 0.0

    # Clamp to bounds
    score = max(MIN_SCORE, min(MAX_SCORE, score))

    # Determine quality level
    normalized = score / MAX_SCORE
    if normalized >= QUALITY_THRESHOLDS["EXCELENTE"]:
        quality = "EXCELENTE"
    elif normalized >= QUALITY_THRESHOLDS["BUENO"]:
        quality = "BUENO"
    elif normalized >= QUALITY_THRESHOLDS["ACEPTABLE"]:
        quality = "ACEPTABLE"
    else:
        quality = "INSUFICIENTE"

    return MockAreaScore(
        area_id=pa_id,
        area_name=f"Policy Area {pa_id}",
        score=score,
        quality_level=quality,
        dimension_scores=pa_scores,
        cluster_id=PA_TO_CLUSTER.get(pa_id),
        validation_passed=True,
    )


@pytest.fixture
def compute_area_score_fixture():
    """Fixture wrapping compute_area_score."""
    return compute_area_score


# =============================================================================
# EDGE CASE GENERATORS
# =============================================================================


@pytest.fixture
def generate_nan_score():
    """Generate a DimensionScore with NaN value."""

    def _generate(pa_id: str, dim_id: str) -> MockDimensionScore:
        return MockDimensionScore(
            dimension_id=dim_id,
            area_id=pa_id,
            score=float("nan"),
            quality_level="INSUFICIENTE",
            contributing_questions=[],
            validation_passed=False,
        )

    return _generate


@pytest.fixture
def generate_inf_score():
    """Generate a DimensionScore with infinity value."""

    def _generate(pa_id: str, dim_id: str, positive: bool = True) -> MockDimensionScore:
        return MockDimensionScore(
            dimension_id=dim_id,
            area_id=pa_id,
            score=float("inf") if positive else float("-inf"),
            quality_level="INSUFICIENTE",
            contributing_questions=[],
            validation_passed=False,
        )

    return _generate


@pytest.fixture
def generate_empty_questions_score():
    """Generate a DimensionScore with no contributing questions."""

    def _generate(pa_id: str, dim_id: str) -> MockDimensionScore:
        return MockDimensionScore(
            dimension_id=dim_id,
            area_id=pa_id,
            score=0.0,
            quality_level="INSUFICIENTE",
            contributing_questions=[],  # Empty - potentially invalid
            validation_passed=False,
            validation_details={"no_contributing_questions": True},
        )

    return _generate


# =============================================================================
# STATISTICAL FIXTURES
# =============================================================================


@pytest.fixture
def generate_dimension_score_distribution():
    """Generate DimensionScores following a specific distribution."""

    def _generate(
        pa_id: str,
        distribution: str = "uniform",
        mean: float = 2.0,
        std: float = 0.5,
    ) -> list[MockDimensionScore]:
        scores = []
        for dim in DIMENSIONS:
            if distribution == "uniform":
                score = random.uniform(MIN_SCORE, MAX_SCORE)
            elif distribution == "normal":
                score = random.gauss(mean, std)
                score = max(MIN_SCORE, min(MAX_SCORE, score))
            elif distribution == "extreme_low":
                score = random.uniform(MIN_SCORE, 0.5)
            elif distribution == "extreme_high":
                score = random.uniform(2.5, MAX_SCORE)
            elif distribution == "bimodal":
                score = random.choice([random.uniform(0, 1), random.uniform(2, 3)])
            else:
                score = mean

            quality = "INSUFICIENTE"
            if score / MAX_SCORE >= QUALITY_THRESHOLDS["EXCELENTE"]:
                quality = "EXCELENTE"
            elif score / MAX_SCORE >= QUALITY_THRESHOLDS["BUENO"]:
                quality = "BUENO"
            elif score / MAX_SCORE >= QUALITY_THRESHOLDS["ACEPTABLE"]:
                quality = "ACEPTABLE"

            scores.append(
                MockDimensionScore(
                    dimension_id=dim,
                    area_id=pa_id,
                    score=score,
                    quality_level=quality,
                    contributing_questions=[1, 2, 3, 4, 5],
                )
            )
        return scores

    return _generate


# =============================================================================
# ASSERTION HELPERS
# =============================================================================


@pytest.fixture
def assert_all_pas_present():
    """Assert all 10 policy areas are present in output."""

    def _assert(area_scores: list[MockAreaScore]) -> None:
        pa_ids = {score.area_id for score in area_scores}
        expected = set(POLICY_AREAS)
        assert pa_ids == expected, f"Missing PAs: {expected - pa_ids}, Extra: {pa_ids - expected}"

    return _assert


@pytest.fixture
def assert_deterministic():
    """Assert that same inputs produce same outputs."""

    def _assert(
        func,
        dimension_scores: list[MockDimensionScore],
        num_runs: int = 5,
    ) -> None:
        results = []
        for _ in range(num_runs):
            result = func(dimension_scores)
            results.append(result)

        # All results should be identical
        first = results[0]
        for i, result in enumerate(results[1:], 2):
            assert len(result) == len(first), f"Run {i}: Different count"
            for j, (a, b) in enumerate(zip(first, result)):
                assert a.area_id == b.area_id, f"Run {i}, score {j}: Different PA"
                assert abs(a.score - b.score) < 1e-9, f"Run {i}, score {j}: Different score"

    return _assert
