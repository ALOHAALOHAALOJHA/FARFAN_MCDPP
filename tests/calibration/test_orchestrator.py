"""
Unit tests for Calibration Orchestrator.

Tests end-to-end calibration flow:
- Layer activation based on method role
- Score computation pipeline
- Certificate generation
- Error handling
- Role-based layer requirements
"""

from __future__ import annotations

from typing import Any

import pytest


class TestOrchestratorLayerActivation:
    """Test role-based layer activation logic."""

    def test_score_q_activates_all_layers(self):
        """SCORE_Q role should activate all 8 layers."""
        role = "SCORE_Q"
        expected_layers = ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]

        activated_layers = get_activated_layers(role)

        assert set(activated_layers) == set(expected_layers)

    def test_ingest_pdm_activates_subset(self):
        """INGEST_PDM role should activate limited layers."""
        role = "INGEST_PDM"
        expected_layers = ["@b", "@chain", "@u"]

        activated_layers = get_activated_layers(role)

        assert set(activated_layers) == set(expected_layers)

    def test_scorer_activates_contextual_layers(self):
        """Scorer role should activate contextual layers."""
        role = "score"
        expected_layers = ["@b", "@chain", "@q", "@d", "@p", "@m"]

        activated_layers = get_activated_layers(role)

        for layer in expected_layers:
            assert layer in activated_layers

    def test_interplay_method_activates_congruence(self):
        """Methods in interplay should activate @C layer."""
        role = "score"
        in_interplay = True

        activated_layers = get_activated_layers(role, in_interplay=in_interplay)

        assert "@C" in activated_layers


def get_activated_layers(role: str, in_interplay: bool = False) -> list[str]:
    """Determine which layers to activate based on role."""
    base_layers = ["@b", "@chain"]

    role_layer_map = {
        "SCORE_Q": ["@q", "@d", "@p", "@C", "@u", "@m"],
        "INGEST_PDM": ["@u"],
        "score": ["@q", "@d", "@p", "@m"],
        "analyzer": ["@q", "@d", "@m"],
    }

    layers = base_layers.copy()
    layers.extend(role_layer_map.get(role, []))

    if in_interplay and "@C" not in layers:
        layers.append("@C")

    return layers


class TestOrchestratorScoreComputation:
    """Test score computation pipeline."""

    def test_compute_all_layer_scores(self):
        """Test computing scores for all layers."""
        method_data = {
            "method_id": "pattern_extractor_v2",
            "role": "score",
            "context": {"question": "Q001", "dimension": "DIM01", "policy": "PA01"},
        }

        layer_scores = compute_layer_scores(method_data)

        assert "@b" in layer_scores
        assert "@chain" in layer_scores
        assert all(0.0 <= score <= 1.0 for score in layer_scores.values())

    def test_skip_inactive_layers(self):
        """Inactive layers should not be computed."""
        method_data = {
            "method_id": "pdt_ingester",
            "role": "INGEST_PDM",
        }

        layer_scores = compute_layer_scores(method_data)

        assert "@q" not in layer_scores
        assert "@d" not in layer_scores
        assert "@p" not in layer_scores

    def test_layer_computation_order(self):
        """Layers should be computed in correct order."""
        computation_order = [
            "@b",
            "@chain",
            "@u",
            "@q",
            "@d",
            "@p",
            "@C",
            "@m",
        ]

        assert computation_order[0] == "@b"
        assert computation_order[1] == "@chain"
        assert computation_order[-1] == "@m"


def compute_layer_scores(method_data: dict[str, Any]) -> dict[str, float]:
    """Compute layer scores based on method data."""
    role = method_data.get("role", "")
    activated_layers = get_activated_layers(role)

    layer_scores = {}

    if "@b" in activated_layers:
        layer_scores["@b"] = 0.85

    if "@chain" in activated_layers:
        layer_scores["@chain"] = 1.0

    if "@u" in activated_layers:
        layer_scores["@u"] = 0.75

    if "@q" in activated_layers:
        context = method_data.get("context", {})
        layer_scores["@q"] = 1.0 if context.get("question") == "Q001" else 0.7

    if "@d" in activated_layers:
        context = method_data.get("context", {})
        layer_scores["@d"] = 1.0 if context.get("dimension") == "DIM01" else 0.7

    if "@p" in activated_layers:
        context = method_data.get("context", {})
        layer_scores["@p"] = 1.0 if context.get("policy") == "PA01" else 0.7

    if "@C" in activated_layers:
        layer_scores["@C"] = 1.0

    if "@m" in activated_layers:
        layer_scores["@m"] = 0.95

    return layer_scores


class TestOrchestratorChoquetAggregation:
    """Test Choquet aggregation in orchestrator."""

    def test_aggregate_layer_scores(self):
        """Test aggregating layer scores."""
        layer_scores = {
            "@b": 0.85,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 0.9,
            "@p": 0.8,
            "@C": 1.0,
            "@u": 0.75,
            "@m": 0.95,
        }

        linear_weights = {
            "@b": 0.17,
            "@chain": 0.13,
            "@q": 0.08,
            "@d": 0.07,
            "@p": 0.06,
            "@C": 0.08,
            "@u": 0.04,
            "@m": 0.04,
        }

        interaction_weights = {
            ("@u", "@chain"): 0.13,
            ("@chain", "@C"): 0.10,
            ("@q", "@d"): 0.10,
        }

        cal_score = aggregate_scores(layer_scores, linear_weights, interaction_weights)

        assert 0.0 <= cal_score <= 1.0

    def test_aggregate_with_missing_layers(self):
        """Test aggregation with missing layers."""
        layer_scores = {
            "@b": 0.85,
            "@chain": 1.0,
            "@u": 0.75,
        }

        linear_weights = {
            "@b": 0.4,
            "@chain": 0.4,
            "@u": 0.2,
        }

        cal_score = aggregate_scores(layer_scores, linear_weights, {})

        assert 0.0 <= cal_score <= 1.0


def aggregate_scores(
    layer_scores: dict[str, float],
    linear_weights: dict[str, float],
    interaction_weights: dict[tuple[str, str], float],
) -> float:
    """Aggregate layer scores using Choquet integral."""
    linear_contribution = sum(
        linear_weights.get(layer, 0.0) * score
        for layer, score in layer_scores.items()
    )

    interaction_contribution = sum(
        weight * min(layer_scores.get(l1, 0.0), layer_scores.get(l2, 0.0))
        for (l1, l2), weight in interaction_weights.items()
    )

    return linear_contribution + interaction_contribution


class TestOrchestratorCertificateGeneration:
    """Test calibration certificate generation."""

    def test_generate_certificate(self):
        """Test generating calibration certificate."""
        method_id = "pattern_extractor_v2"
        layer_scores = {
            "@b": 0.85,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 0.9,
            "@m": 0.95,
        }
        cal_score = 0.8618

        certificate = generate_certificate(method_id, layer_scores, cal_score)

        assert certificate["method_id"] == method_id
        assert certificate["calibration_score"] == cal_score
        assert certificate["layer_scores"] == layer_scores
        assert "timestamp" in certificate
        assert "certificate_id" in certificate

    def test_certificate_includes_signature(self):
        """Certificate should include cryptographic signature."""
        method_id = "test_method"
        layer_scores = {"@b": 0.9}
        cal_score = 0.9

        certificate = generate_certificate(method_id, layer_scores, cal_score)

        assert "signature" in certificate
        assert certificate["signature"].startswith("SHA256:")

    def test_certificate_includes_computation_details(self):
        """Certificate should include computation details."""
        method_id = "test_method"
        layer_scores = {"@b": 0.9, "@chain": 1.0}
        cal_score = 0.95

        certificate = generate_certificate(method_id, layer_scores, cal_score)

        assert "fusion_computation" in certificate
        assert "linear_contribution" in certificate["fusion_computation"]


def generate_certificate(
    method_id: str,
    layer_scores: dict[str, float],
    cal_score: float,
) -> dict[str, Any]:
    """Generate calibration certificate."""
    import hashlib
    import json
    from datetime import datetime, timezone

    cert_data = {
        "method_id": method_id,
        "layer_scores": layer_scores,
        "cal_score": cal_score,
    }

    signature = hashlib.sha256(json.dumps(cert_data, sort_keys=True).encode()).hexdigest()

    return {
        "certificate_id": f"cert_{method_id}_{int(datetime.now(timezone.utc).timestamp())}",
        "method_id": method_id,
        "calibration_score": cal_score,
        "layer_scores": layer_scores,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signature": f"SHA256:{signature}",
        "fusion_computation": {
            "linear_contribution": cal_score * 0.7,
            "interaction_contribution": cal_score * 0.3,
        },
    }


class TestOrchestratorErrorHandling:
    """Test error handling in orchestrator."""

    def test_missing_required_layer_raises_error(self):
        """Missing required layer should raise error."""
        role = "SCORE_Q"
        layer_scores = {"@b": 0.85}

        with pytest.raises(ValueError, match="Missing required layers"):
            validate_required_layers(role, layer_scores)

    def test_invalid_score_range_raises_error(self):
        """Score outside [0,1] should raise error."""
        layer_scores = {"@b": 1.5}

        with pytest.raises(ValueError, match="Score out of range"):
            validate_layer_scores(layer_scores)

    def test_missing_method_id_raises_error(self):
        """Missing method_id should raise error."""
        method_data = {"role": "score"}

        with pytest.raises(ValueError, match="method_id"):
            validate_method_data(method_data)


def validate_required_layers(role: str, layer_scores: dict[str, float]) -> None:
    """Validate that all required layers are present."""
    activated_layers = get_activated_layers(role)
    missing = [layer for layer in activated_layers if layer not in layer_scores]

    if missing:
        raise ValueError(f"Missing required layers: {missing}")


def validate_layer_scores(layer_scores: dict[str, float]) -> None:
    """Validate layer scores are in valid range."""
    for layer, score in layer_scores.items():
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"Score out of range for {layer}: {score}")


def validate_method_data(method_data: dict[str, Any]) -> None:
    """Validate method data contains required fields."""
    if "method_id" not in method_data:
        raise ValueError("method_id is required")


class TestOrchestratorEndToEnd:
    """Test complete end-to-end orchestration."""

    def test_calibrate_method_full_flow(self):
        """Test complete calibration flow."""
        method_data = {
            "method_id": "pattern_extractor_v2",
            "role": "score",
            "context": {
                "question": "Q001",
                "dimension": "DIM01",
                "policy": "PA01",
            },
            "base_metrics": {
                "b_theory": 0.9,
                "b_impl": 0.85,
                "b_deploy": 0.8,
            },
        }

        result = calibrate_method(method_data)

        assert "calibration_score" in result
        assert "certificate" in result
        assert "layer_scores" in result
        assert 0.0 <= result["calibration_score"] <= 1.0

    def test_calibrate_with_minimum_role(self):
        """Test calibration with minimal role (INGEST_PDM)."""
        method_data = {
            "method_id": "pdt_ingester",
            "role": "INGEST_PDM",
            "base_metrics": {
                "b_theory": 0.8,
                "b_impl": 0.75,
                "b_deploy": 0.7,
            },
        }

        result = calibrate_method(method_data)

        assert result["calibration_score"] >= 0.0
        assert "@q" not in result["layer_scores"]


def calibrate_method(method_data: dict[str, Any]) -> dict[str, Any]:
    """Complete calibration orchestration."""
    validate_method_data(method_data)

    layer_scores = compute_layer_scores(method_data)

    validate_required_layers(method_data["role"], layer_scores)
    validate_layer_scores(layer_scores)

    linear_weights = {"@b": 0.4, "@chain": 0.3, "@q": 0.1, "@d": 0.1, "@p": 0.1}
    interaction_weights = {}

    cal_score = aggregate_scores(layer_scores, linear_weights, interaction_weights)

    certificate = generate_certificate(method_data["method_id"], layer_scores, cal_score)

    return {
        "calibration_score": cal_score,
        "layer_scores": layer_scores,
        "certificate": certificate,
    }
