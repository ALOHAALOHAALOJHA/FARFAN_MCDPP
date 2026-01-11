"""
Pytest fixtures for Phase 6 adversarial tests.

Phase 6: Cluster Aggregation (10 AreaScore → 4 ClusterScore)

ADVERSARIAL TESTING PILLARS:
1. HERMETICITY: Correct policy areas per cluster
2. BOUNDS: All scores in [0.0, 3.0]
3. DISPERSION: CV classification and adaptive penalty
4. COHERENCE: Cross-area coherence validation
5. INPUT VALIDATION: Reject malformed/incomplete inputs

REAL STRUCTURE:
- 4 Clusters: CLUSTER_MESO_1 to CLUSTER_MESO_4
- Cluster composition:
  - CLUSTER_MESO_1: PA01, PA02, PA03 (3 PAs)
  - CLUSTER_MESO_2: PA04, PA05, PA06 (3 PAs)
  - CLUSTER_MESO_3: PA07, PA08 (2 PAs)
  - CLUSTER_MESO_4: PA09, PA10 (2 PAs)
"""

from __future__ import annotations

import json
import math
import random
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


# =============================================================================
# CANONICAL CONSTANTS - Ground Truth for Phase 6
# =============================================================================

CLUSTERS = ["CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"]
EXPECTED_CLUSTER_COUNT = 4
MIN_SCORE = 0.0
MAX_SCORE = 3.0

# Cluster composition from Phase 6 constants
CLUSTER_COMPOSITION = {
    "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],
    "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],
    "CLUSTER_MESO_3": ["PA07", "PA08"],
    "CLUSTER_MESO_4": ["PA09", "PA10"],
}

# Dispersion thresholds
DISPERSION_THRESHOLDS = {
    "CV_CONVERGENCE": 0.2,
    "CV_MODERATE": 0.4,
    "CV_HIGH": 0.6,
    "CV_EXTREME": 1.0,
}

PENALTY_WEIGHT = 0.3
COHERENCE_THRESHOLD_LOW = 0.5
COHERENCE_THRESHOLD_HIGH = 0.8

# Dimensions per policy area (for nested validation)
DIMENSIONS = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]

# Policy areas list
POLICY_AREAS = ["PA01", "PA02", "PA03", "PA04", "PA05", "PA06", "PA07", "PA08", "PA09", "PA10"]


# =============================================================================
# LOCAL DATACLASSES - Isolated test models
# =============================================================================


@dataclass
class MockDimensionScore:
    """Test-local DimensionScore model."""

    dimension_id: str
    area_id: str
    score: float
    quality_level: str
    contributing_questions: list[int | str]
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)


@dataclass
class MockAreaScore:
    """Test-local AreaScore model."""

    area_id: str
    area_name: str
    score: float
    quality_level: str
    dimension_scores: list[MockDimensionScore]
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    cluster_id: str | None = None


@dataclass
class MockClusterScore:
    """Test-local ClusterScore model."""

    cluster_id: str
    cluster_name: str
    areas: list[str]
    score: float
    coherence: float
    variance: float
    weakest_area: str | None
    area_scores: list[MockAreaScore]
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"
    dispersion_scenario: str = "moderate"
    penalty_applied: float = 0.0


# =============================================================================
# DISPERSION CLASSIFICATION
# =============================================================================


def classify_dispersion(cv: float) -> str:
    """Classify dispersion scenario based on coefficient of variation."""
    if cv < DISPERSION_THRESHOLDS["CV_CONVERGENCE"]:
        return "convergence"
    elif cv < DISPERSION_THRESHOLDS["CV_MODERATE"]:
        return "moderate"
    elif cv < DISPERSION_THRESHOLDS["CV_HIGH"]:
        return "high"
    else:
        return "extreme"


def compute_cv(scores: list[float]) -> float:
    """Compute coefficient of variation. Handles NaN/Inf gracefully."""
    if len(scores) < 2:
        return 0.0
    
    # Filter out NaN and Inf
    clean_scores = [s for s in scores if math.isfinite(s)]
    if len(clean_scores) < 2:
        return 0.0
    
    mean = statistics.mean(clean_scores)
    if mean == 0:
        return 0.0
    std = statistics.stdev(clean_scores)
    return std / mean


def compute_coherence(scores: list[float]) -> float:
    """Compute coherence as 1 - normalized variance. Handles NaN/Inf gracefully."""
    if len(scores) < 2:
        return 1.0
    
    # Filter out NaN and Inf
    clean_scores = [s for s in scores if math.isfinite(s)]
    if len(clean_scores) < 2:
        return 1.0
    
    variance = statistics.variance(clean_scores)
    # Normalize by max possible variance (for scores in [0, 3])
    max_variance = (MAX_SCORE - MIN_SCORE) ** 2 / 4
    coherence = 1.0 - (variance / max_variance)
    return max(0.0, min(1.0, coherence))


# =============================================================================
# PATH FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def cqc_base_path() -> Path:
    """Base path to the canonical questionnaire central."""
    return Path(__file__).resolve().parent.parent.parent / "canonic_questionnaire_central"


# =============================================================================
# AREA SCORE GENERATORS
# =============================================================================


@pytest.fixture
def generate_valid_area_score():
    """Generate a valid AreaScore for a specific PA."""

    def _generate(
        pa_id: str,
        score: float = 2.0,
        quality_level: str = "BUENO",
        cluster_id: str | None = None,
    ) -> MockAreaScore:
        # Determine cluster from composition
        if cluster_id is None:
            for cl_id, pas in CLUSTER_COMPOSITION.items():
                if pa_id in pas:
                    cluster_id = cl_id
                    break

        dim_scores = [
            MockDimensionScore(
                dimension_id=dim,
                area_id=pa_id,
                score=score,
                quality_level=quality_level,
                contributing_questions=[1, 2, 3, 4, 5],
            )
            for dim in DIMENSIONS
        ]

        return MockAreaScore(
            area_id=pa_id,
            area_name=f"Policy Area {pa_id}",
            score=score,
            quality_level=quality_level,
            dimension_scores=dim_scores,
            cluster_id=cluster_id,
        )

    return _generate


@pytest.fixture
def generate_cluster_area_scores(generate_valid_area_score):
    """Generate all AreaScores for a specific cluster."""

    def _generate(cluster_id: str, base_score: float = 2.0, variance: float = 0.0) -> list[MockAreaScore]:
        pas = CLUSTER_COMPOSITION.get(cluster_id, [])
        scores = []
        for i, pa_id in enumerate(pas):
            # Add variance to scores
            pa_score = base_score + (i - len(pas) / 2) * variance
            pa_score = max(MIN_SCORE, min(MAX_SCORE, pa_score))
            scores.append(generate_valid_area_score(pa_id, score=pa_score, cluster_id=cluster_id))
        return scores

    return _generate


@pytest.fixture
def generate_all_area_scores(generate_valid_area_score):
    """Generate all 10 AreaScores."""

    def _generate(base_score: float = 2.0) -> list[MockAreaScore]:
        scores = []
        for pa_id in POLICY_AREAS:
            score = base_score + random.uniform(-0.3, 0.3)
            score = max(MIN_SCORE, min(MAX_SCORE, score))
            scores.append(generate_valid_area_score(pa_id, score=score))
        return scores

    return _generate


# =============================================================================
# CLUSTER SCORE COMPUTATION
# =============================================================================


def compute_cluster_score(
    area_scores: list[MockAreaScore],
    cluster_id: str,
    apply_penalty: bool = True,
) -> MockClusterScore:
    """
    Compute ClusterScore from AreaScores - test implementation.

    This is the logic that Phase 6 should implement. Tests verify this behavior.
    """
    expected_pas = set(CLUSTER_COMPOSITION.get(cluster_id, []))
    
    # Validate cluster ID exists
    if not expected_pas:
        raise ValueError(f"Hermeticity violation for {cluster_id}: missing=set(), extra=set()")
    
    # Filter area scores for this cluster
    cluster_areas = [a for a in area_scores if a.area_id in expected_pas]
    
    # Validate hermeticity
    actual_pas = {a.area_id for a in cluster_areas}
    if actual_pas != expected_pas:
        missing = expected_pas - actual_pas
        extra = actual_pas - expected_pas
        raise ValueError(f"Hermeticity violation for {cluster_id}: missing={missing}, extra={extra}")
    
    # Extract scores, filtering NaN/Inf
    raw_scores = [a.score for a in cluster_areas]
    clean_scores = [s for s in raw_scores if math.isfinite(s)]
    
    # Use clean scores for computation, fallback to 0 if all invalid
    if not clean_scores:
        clean_scores = [0.0]
    
    # Compute metrics with clean scores
    mean_score = statistics.mean(clean_scores)
    cv = compute_cv(clean_scores)
    coherence = compute_coherence(clean_scores)
    variance = statistics.variance(clean_scores) if len(clean_scores) > 1 else 0.0
    
    # Find weakest area (use clean score, or 0 for invalid)
    def get_score_safe(a):
        return a.score if math.isfinite(a.score) else 0.0
    
    weakest_area = min(cluster_areas, key=get_score_safe).area_id if cluster_areas else None
    
    # Classify dispersion and apply penalty
    dispersion = classify_dispersion(cv)
    penalty = 0.0
    if apply_penalty and dispersion in ("high", "extreme"):
        penalty = PENALTY_WEIGHT * cv
    
    final_score = max(MIN_SCORE, min(MAX_SCORE, mean_score - penalty))
    
    # Determine quality level
    normalized = final_score / MAX_SCORE
    if normalized >= 0.85:
        quality = "EXCELENTE"
    elif normalized >= 0.70:
        quality = "BUENO"
    elif normalized >= 0.55:
        quality = "ACEPTABLE"
    else:
        quality = "INSUFICIENTE"
    
    return MockClusterScore(
        cluster_id=cluster_id,
        cluster_name=f"Cluster {cluster_id}",
        areas=list(expected_pas),
        score=final_score,
        coherence=coherence,
        variance=variance,
        weakest_area=weakest_area,
        area_scores=cluster_areas,
        validation_passed=True,
        dispersion_scenario=dispersion,
        penalty_applied=penalty,
        validation_details={
            "cv": cv,
            "dispersion": dispersion,
            "penalty": penalty,
        },
    )


@pytest.fixture
def compute_cluster_score_fixture():
    """Fixture wrapping compute_cluster_score."""
    return compute_cluster_score


# =============================================================================
# ADVERSARIAL INPUT GENERATORS
# =============================================================================


@pytest.fixture
def generate_missing_area_cluster():
    """Generate AreaScores for cluster with one PA missing."""

    def _generate(cluster_id: str, missing_pa: str | None = None) -> list[MockAreaScore]:
        pas = CLUSTER_COMPOSITION.get(cluster_id, [])
        if missing_pa is None:
            missing_pa = pas[0] if pas else None
        
        scores = []
        for pa_id in pas:
            if pa_id == missing_pa:
                continue  # Skip to create hermeticity violation
            scores.append(
                MockAreaScore(
                    area_id=pa_id,
                    area_name=f"Policy Area {pa_id}",
                    score=2.0,
                    quality_level="BUENO",
                    dimension_scores=[],
                    cluster_id=cluster_id,
                )
            )
        return scores

    return _generate


@pytest.fixture
def generate_high_dispersion_cluster(generate_valid_area_score):
    """Generate AreaScores with high dispersion (extreme CV)."""

    def _generate(cluster_id: str) -> list[MockAreaScore]:
        pas = CLUSTER_COMPOSITION.get(cluster_id, [])
        scores = []
        # Alternate between 0.0 and 3.0 for maximum dispersion
        for i, pa_id in enumerate(pas):
            score = 0.0 if i % 2 == 0 else 3.0
            scores.append(generate_valid_area_score(pa_id, score=score, cluster_id=cluster_id))
        return scores

    return _generate


@pytest.fixture
def generate_convergent_cluster(generate_valid_area_score):
    """Generate AreaScores with low dispersion (convergent)."""

    def _generate(cluster_id: str, base_score: float = 2.0) -> list[MockAreaScore]:
        pas = CLUSTER_COMPOSITION.get(cluster_id, [])
        scores = []
        for pa_id in pas:
            # Very small variance
            score = base_score + random.uniform(-0.05, 0.05)
            scores.append(generate_valid_area_score(pa_id, score=score, cluster_id=cluster_id))
        return scores

    return _generate


@pytest.fixture
def generate_wrong_cluster_area():
    """Generate AreaScore claiming wrong cluster."""

    def _generate(claimed_cluster: str, actual_pa: str) -> MockAreaScore:
        return MockAreaScore(
            area_id=actual_pa,
            area_name=f"Policy Area {actual_pa}",
            score=2.0,
            quality_level="BUENO",
            dimension_scores=[],
            cluster_id=claimed_cluster,
        )

    return _generate


# =============================================================================
# VALIDATORS
# =============================================================================


@pytest.fixture
def validate_cluster_hermeticity():
    """Validate that a ClusterScore has correct PAs."""

    def _validate(cluster_score: MockClusterScore) -> tuple[bool, str]:
        expected_pas = set(CLUSTER_COMPOSITION.get(cluster_score.cluster_id, []))
        actual_pas = {a.area_id for a in cluster_score.area_scores}
        
        if actual_pas != expected_pas:
            missing = expected_pas - actual_pas
            extra = actual_pas - expected_pas
            return False, f"Missing: {missing}, Extra: {extra}"
        
        return True, "Hermeticity OK"

    return _validate


@pytest.fixture
def validate_cluster_bounds():
    """Validate that a ClusterScore has score in [0.0, 3.0]."""

    def _validate(cluster_score: MockClusterScore) -> tuple[bool, str]:
        if cluster_score.score < MIN_SCORE:
            return False, f"Score {cluster_score.score} below minimum {MIN_SCORE}"
        if cluster_score.score > MAX_SCORE:
            return False, f"Score {cluster_score.score} above maximum {MAX_SCORE}"
        return True, "Bounds OK"

    return _validate


@pytest.fixture
def validate_dispersion_classification():
    """Validate dispersion is correctly classified."""

    def _validate(cv: float, expected_scenario: str) -> tuple[bool, str]:
        actual = classify_dispersion(cv)
        if actual != expected_scenario:
            return False, f"Expected {expected_scenario}, got {actual} for CV={cv}"
        return True, "Dispersion classification OK"

    return _validate


# =============================================================================
# EDGE CASE GENERATORS
# =============================================================================


@pytest.fixture
def generate_nan_area_score():
    """Generate an AreaScore with NaN value."""

    def _generate(pa_id: str, cluster_id: str) -> MockAreaScore:
        return MockAreaScore(
            area_id=pa_id,
            area_name=f"Policy Area {pa_id}",
            score=float("nan"),
            quality_level="INSUFICIENTE",
            dimension_scores=[],
            cluster_id=cluster_id,
        )

    return _generate


@pytest.fixture
def generate_inf_area_score():
    """Generate an AreaScore with infinity value."""

    def _generate(pa_id: str, cluster_id: str, positive: bool = True) -> MockAreaScore:
        return MockAreaScore(
            area_id=pa_id,
            area_name=f"Policy Area {pa_id}",
            score=float("inf") if positive else float("-inf"),
            quality_level="INSUFICIENTE",
            dimension_scores=[],
            cluster_id=cluster_id,
        )

    return _generate


# =============================================================================
# ASSERTION HELPERS
# =============================================================================


@pytest.fixture
def assert_all_clusters_present():
    """Assert all 4 clusters are present in output."""

    def _assert(cluster_scores: list[MockClusterScore]) -> None:
        cluster_ids = {s.cluster_id for s in cluster_scores}
        expected = set(CLUSTERS)
        assert cluster_ids == expected, f"Missing: {expected - cluster_ids}, Extra: {cluster_ids - expected}"

    return _assert


@pytest.fixture
def assert_deterministic():
    """Assert that same inputs produce same outputs."""

    def _assert(
        func,
        area_scores: list[MockAreaScore],
        cluster_id: str,
        num_runs: int = 5,
    ) -> None:
        results = []
        for _ in range(num_runs):
            result = func(area_scores, cluster_id)
            results.append(result.score)

        # All results should be identical
        first = results[0]
        for i, r in enumerate(results[1:], 2):
            assert abs(r - first) < 1e-9, f"Run {i}: score differs"

    return _assert
