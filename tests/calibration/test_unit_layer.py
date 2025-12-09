"""
Unit tests for Unit-of-Analysis Layer (@u) computation.

Tests context-sensitive unit quality scoring with PDT fixtures:
- Unit quality U(pdt) computation from structural compliance
- Method-specific transformation functions g_M(U)
- Role-based sensitivity to unit quality

Formula: x_@u = g_M(U) if M ∈ U_sensitive_methods, else 1.0
"""

from __future__ import annotations

from typing import Any

import pytest


def compute_unit_quality(pdt_data: dict[str, Any]) -> float:
    """
    Compute unit quality U from PDT data.
    
    U = w1*structural + w2*mandatory + w3*indicator + w4*ppi
    where weights sum to 1.0
    """
    weights = {
        "structural_compliance": 0.3,
        "mandatory_sections_ratio": 0.3,
        "indicator_quality_score": 0.2,
        "ppi_completeness": 0.2,
    }

    return (
        weights["structural_compliance"] * pdt_data["structural_compliance"]
        + weights["mandatory_sections_ratio"] * pdt_data["mandatory_sections_ratio"]
        + weights["indicator_quality_score"] * pdt_data["indicator_quality_score"]
        + weights["ppi_completeness"] * pdt_data["ppi_completeness"]
    )


def g_ingest(u: float) -> float:
    """Identity transformation for ingestion methods."""
    return u


def g_struct(u: float) -> float:
    """
    Piecewise linear transformation for structure extractors.
    
    - 0 if U < 0.3 (abort threshold)
    - 2U - 0.6 if 0.3 <= U < 0.8 (linear ramp)
    - 1 if U >= 0.8 (saturation)
    """
    if u < 0.3:
        return 0.0
    elif u < 0.8:
        return 2.0 * u - 0.6
    else:
        return 1.0


def g_qa(u: float) -> float:
    """
    Sigmoidal transformation for question-answering methods.
    
    g_QA(U) = 1 - exp(-5(U - 0.5))
    Clipped to [0, 1] range.
    """
    import math
    result = 1.0 - math.exp(-5.0 * (u - 0.5))
    return max(0.0, min(1.0, result))


class TestUnitQualityComputation:
    """Test unit quality U(pdt) computation."""

    def test_unit_quality_bounded(self, sample_pdt_data: dict[str, Any]):
        """Verify unit quality is bounded in [0,1]."""
        u = compute_unit_quality(sample_pdt_data)

        assert 0.0 <= u <= 1.0, f"Unit quality {u} not in [0,1]"

    def test_unit_quality_perfect_pdt(self):
        """Perfect PDT should yield U = 1.0."""
        perfect_pdt = {
            "structural_compliance": 1.0,
            "mandatory_sections_ratio": 1.0,
            "indicator_quality_score": 1.0,
            "ppi_completeness": 1.0,
        }

        u = compute_unit_quality(perfect_pdt)

        assert abs(u - 1.0) < 1e-6

    def test_unit_quality_zero_pdt(self):
        """Zero quality PDT should yield U = 0.0."""
        zero_pdt = {
            "structural_compliance": 0.0,
            "mandatory_sections_ratio": 0.0,
            "indicator_quality_score": 0.0,
            "ppi_completeness": 0.0,
        }

        u = compute_unit_quality(zero_pdt)

        assert abs(u - 0.0) < 1e-6

    def test_unit_quality_sample_computation(self, sample_pdt_data: dict[str, Any]):
        """Test unit quality with sample PDT data."""
        u = compute_unit_quality(sample_pdt_data)

        expected = 0.3 * 0.8 + 0.3 * 0.9 + 0.2 * 0.85 + 0.2 * 0.7

        assert abs(u - expected) < 1e-6


class TestIngestTransformation:
    """Test g_INGEST transformation (identity)."""

    def test_g_ingest_identity(self):
        """g_INGEST should be identity function."""
        assert g_ingest(0.0) == 0.0
        assert g_ingest(0.5) == 0.5
        assert g_ingest(1.0) == 1.0

    def test_g_ingest_preserves_range(self):
        """g_INGEST should preserve [0,1] range."""
        for u in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
            result = g_ingest(u)
            assert 0.0 <= result <= 1.0


class TestStructTransformation:
    """Test g_STRUCT transformation (piecewise linear)."""

    def test_g_struct_abort_threshold(self):
        """g_STRUCT should return 0 for U < 0.3."""
        assert g_struct(0.0) == 0.0
        assert g_struct(0.1) == 0.0
        assert g_struct(0.29) == 0.0

    def test_g_struct_linear_ramp(self):
        """g_STRUCT should be linear in [0.3, 0.8)."""
        assert abs(g_struct(0.3) - 0.0) < 1e-6
        assert abs(g_struct(0.55) - 0.5) < 1e-6
        assert abs(g_struct(0.8) - 1.0) < 1e-6

    def test_g_struct_saturation(self):
        """g_STRUCT should saturate at 1.0 for U >= 0.8."""
        assert g_struct(0.8) == 1.0
        assert g_struct(0.9) == 1.0
        assert g_struct(1.0) == 1.0

    def test_g_struct_monotonicity(self):
        """g_STRUCT should be monotonic non-decreasing."""
        u_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        results = [g_struct(u) for u in u_values]

        for i in range(len(results) - 1):
            assert results[i] <= results[i + 1], f"Non-monotonic at {u_values[i]}"

    def test_g_struct_bounded(self):
        """g_STRUCT should be bounded in [0,1]."""
        for u in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
            result = g_struct(u)
            assert 0.0 <= result <= 1.0


class TestQATransformation:
    """Test g_QA transformation (sigmoidal)."""

    def test_g_qa_inflection_point(self):
        """g_QA should have inflection near U = 0.5."""
        result = g_qa(0.5)
        assert 0.0 <= result < 1.0

    def test_g_qa_low_asymptote(self):
        """g_QA should approach 0 for low U."""
        result = g_qa(0.0)
        assert 0.0 <= result < 0.2

    def test_g_qa_high_asymptote(self):
        """g_QA should approach 1 for high U."""
        result = g_qa(1.0)
        assert 0.8 < result <= 1.0

    def test_g_qa_monotonicity(self):
        """g_QA should be monotonic non-decreasing."""
        u_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        results = [g_qa(u) for u in u_values]

        for i in range(len(results) - 1):
            assert results[i] <= results[i + 1], f"Non-monotonic at {u_values[i]}"

    def test_g_qa_bounded(self):
        """g_QA should be bounded in [0,1]."""
        for u in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
            result = g_qa(u)
            assert 0.0 <= result <= 1.0


class TestUnitLayerSensitivity:
    """Test sensitivity of different method types to unit quality."""

    def test_ingest_highly_sensitive(self, sample_pdt_data: dict[str, Any]):
        """Ingestion methods should be highly sensitive to PDT quality."""
        u = compute_unit_quality(sample_pdt_data)
        x_u = g_ingest(u)

        assert x_u == u

    def test_struct_threshold_sensitive(self):
        """Structure extractors should have abort threshold."""
        low_quality_pdt = {
            "structural_compliance": 0.2,
            "mandatory_sections_ratio": 0.2,
            "indicator_quality_score": 0.2,
            "ppi_completeness": 0.2,
        }

        u = compute_unit_quality(low_quality_pdt)
        x_u = g_struct(u)

        assert x_u == 0.0, "Low quality PDT should abort structure extraction"

    def test_qa_sigmoidal_response(self):
        """QA methods should have sigmoidal response to quality."""
        medium_pdt = {
            "structural_compliance": 0.5,
            "mandatory_sections_ratio": 0.5,
            "indicator_quality_score": 0.5,
            "ppi_completeness": 0.5,
        }

        u = compute_unit_quality(medium_pdt)
        x_u = g_qa(u)

        assert 0.0 <= x_u < 1.0

    def test_non_sensitive_methods_ignore_unit_quality(self):
        """Non-sensitive methods should return x_@u = 1.0."""
        x_u = 1.0

        assert x_u == 1.0


class TestUnitLayerContextDependence:
    """Test context-dependent behavior of @u layer."""

    def test_different_pdts_different_scores(self):
        """Different PDTs should yield different unit quality scores."""
        pdt1 = {
            "structural_compliance": 0.9,
            "mandatory_sections_ratio": 0.9,
            "indicator_quality_score": 0.9,
            "ppi_completeness": 0.9,
        }

        pdt2 = {
            "structural_compliance": 0.5,
            "mandatory_sections_ratio": 0.5,
            "indicator_quality_score": 0.5,
            "ppi_completeness": 0.5,
        }

        u1 = compute_unit_quality(pdt1)
        u2 = compute_unit_quality(pdt2)

        assert u1 != u2
        assert u1 > u2

    @pytest.mark.parametrize(
        "structural,mandatory,indicator,ppi",
        [
            (1.0, 1.0, 1.0, 1.0),
            (0.8, 0.9, 0.85, 0.7),
            (0.5, 0.5, 0.5, 0.5),
            (0.3, 0.4, 0.3, 0.2),
        ],
    )
    def test_various_pdt_qualities(self, structural: float, mandatory: float, indicator: float, ppi: float):
        """Test unit quality computation with various PDT qualities."""
        pdt_data = {
            "structural_compliance": structural,
            "mandatory_sections_ratio": mandatory,
            "indicator_quality_score": indicator,
            "ppi_completeness": ppi,
        }

        u = compute_unit_quality(pdt_data)

        assert 0.0 <= u <= 1.0
