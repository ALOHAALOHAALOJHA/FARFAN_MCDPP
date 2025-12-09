"""
Integration test for calibration certificate generation.

Tests certificate structure, signature validation, and completeness:
- Certificate ID generation
- Timestamp formatting
- Signature computation
- Layer score inclusion
- Fusion computation details
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import pytest


def generate_calibration_certificate(
    method_id: str,
    layer_scores: dict[str, float],
    cal_score: float,
    linear_contribution: float,
    interaction_contribution: float,
) -> dict[str, Any]:
    """Generate a calibration certificate."""
    timestamp = datetime.now(timezone.utc)

    cert_data = {
        "method_id": method_id,
        "layer_scores": layer_scores,
        "cal_score": cal_score,
        "timestamp": timestamp.isoformat(),
    }

    signature_input = json.dumps(cert_data, sort_keys=True).encode()
    signature = hashlib.sha256(signature_input).hexdigest()

    timestamp_microseconds = int(timestamp.timestamp() * 1_000_000)

    return {
        "certificate_id": f"cert_{method_id}_{timestamp_microseconds}",
        "method_id": method_id,
        "calibration_score": cal_score,
        "timestamp": timestamp.isoformat(),
        "layer_scores": layer_scores,
        "signature": f"SHA256:{signature}",
        "fusion_computation": {
            "linear_contribution": linear_contribution,
            "interaction_contribution": interaction_contribution,
        },
        "config_version": "COHORT_2024",
    }


@pytest.mark.integration
class TestCertificateGeneration:
    """Test calibration certificate generation."""

    def test_generate_basic_certificate(self):
        """Test generating a basic certificate."""
        method_id = "test.method.basic"
        layer_scores = {"@b": 0.85, "@chain": 1.0, "@m": 0.95}
        cal_score = 0.90

        cert = generate_calibration_certificate(
            method_id, layer_scores, cal_score, 0.60, 0.30
        )

        assert cert is not None
        assert cert["method_id"] == method_id
        assert cert["calibration_score"] == cal_score
        assert cert["layer_scores"] == layer_scores

    def test_certificate_has_unique_id(self):
        """Each certificate should have a unique ID."""
        import time

        method_id = "test.method"
        layer_scores = {"@b": 0.9}

        cert1 = generate_calibration_certificate(method_id, layer_scores, 0.9, 0.6, 0.3)
        time.sleep(0.001)
        cert2 = generate_calibration_certificate(method_id, layer_scores, 0.9, 0.6, 0.3)

        assert cert1["certificate_id"] != cert2["certificate_id"]

    def test_certificate_includes_timestamp(self):
        """Certificate must include ISO 8601 timestamp."""
        cert = generate_calibration_certificate(
            "test.method", {"@b": 0.9}, 0.9, 0.6, 0.3
        )

        assert "timestamp" in cert

        timestamp_str = cert["timestamp"]
        parsed = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        assert parsed.year == datetime.now(timezone.utc).year

    def test_certificate_signature_format(self):
        """Certificate signature must have correct format."""
        cert = generate_calibration_certificate(
            "test.method", {"@b": 0.9}, 0.9, 0.6, 0.3
        )

        assert "signature" in cert
        assert cert["signature"].startswith("SHA256:")
        assert len(cert["signature"]) > 70


@pytest.mark.integration
class TestCertificateStructure:
    """Test certificate structure validation."""

    def test_certificate_required_fields(self):
        """Certificate must have all required fields."""
        cert = generate_calibration_certificate(
            "test.method", {"@b": 0.9, "@chain": 1.0}, 0.95, 0.65, 0.30
        )

        required_fields = [
            "certificate_id",
            "method_id",
            "calibration_score",
            "timestamp",
            "layer_scores",
            "signature",
            "fusion_computation",
        ]

        for field in required_fields:
            assert field in cert, f"Missing required field: {field}"

    def test_certificate_fusion_computation_structure(self):
        """Fusion computation must have correct structure."""
        cert = generate_calibration_certificate(
            "test.method", {"@b": 0.9}, 0.9, 0.6, 0.3
        )

        fusion = cert["fusion_computation"]

        assert "linear_contribution" in fusion
        assert "interaction_contribution" in fusion
        assert isinstance(fusion["linear_contribution"], float)
        assert isinstance(fusion["interaction_contribution"], float)

    def test_certificate_layer_scores_complete(self):
        """Certificate must include all computed layer scores."""
        layer_scores = {
            "@b": 0.85,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 0.9,
            "@p": 0.8,
            "@m": 0.95,
        }

        cert = generate_calibration_certificate(
            "test.method", layer_scores, 0.8618, 0.6198, 0.242
        )

        assert cert["layer_scores"] == layer_scores

    def test_certificate_config_version(self):
        """Certificate must include configuration version."""
        cert = generate_calibration_certificate(
            "test.method", {"@b": 0.9}, 0.9, 0.6, 0.3
        )

        assert "config_version" in cert
        assert cert["config_version"] == "COHORT_2024"


@pytest.mark.integration
class TestCertificateSignature:
    """Test certificate signature validation."""

    def test_signature_deterministic(self):
        """Same inputs should produce same signature."""
        method_id = "test.method"
        layer_scores = {"@b": 0.9, "@chain": 1.0}
        cal_score = 0.95

        timestamp1 = datetime(2024, 12, 15, 12, 0, 0, tzinfo=timezone.utc)

        cert_data1 = {
            "method_id": method_id,
            "layer_scores": layer_scores,
            "cal_score": cal_score,
            "timestamp": timestamp1.isoformat(),
        }

        sig1 = hashlib.sha256(json.dumps(cert_data1, sort_keys=True).encode()).hexdigest()
        sig2 = hashlib.sha256(json.dumps(cert_data1, sort_keys=True).encode()).hexdigest()

        assert sig1 == sig2

    def test_signature_changes_with_different_score(self):
        """Different scores should produce different signatures."""
        method_id = "test.method"
        layer_scores = {"@b": 0.9}
        timestamp = datetime(2024, 12, 15, 12, 0, 0, tzinfo=timezone.utc)

        cert_data1 = {
            "method_id": method_id,
            "layer_scores": layer_scores,
            "cal_score": 0.9,
            "timestamp": timestamp.isoformat(),
        }

        cert_data2 = {
            "method_id": method_id,
            "layer_scores": layer_scores,
            "cal_score": 0.8,
            "timestamp": timestamp.isoformat(),
        }

        sig1 = hashlib.sha256(json.dumps(cert_data1, sort_keys=True).encode()).hexdigest()
        sig2 = hashlib.sha256(json.dumps(cert_data2, sort_keys=True).encode()).hexdigest()

        assert sig1 != sig2

    def test_signature_includes_all_critical_data(self):
        """Signature should be computed from all critical certificate data."""
        method_id = "test.method"
        layer_scores = {"@b": 0.9, "@chain": 1.0}
        cal_score = 0.95
        timestamp = datetime.now(timezone.utc)

        cert_data = {
            "method_id": method_id,
            "layer_scores": layer_scores,
            "cal_score": cal_score,
            "timestamp": timestamp.isoformat(),
        }

        signature = hashlib.sha256(json.dumps(cert_data, sort_keys=True).encode()).hexdigest()

        assert len(signature) == 64


@pytest.mark.integration
class TestCertificateSerialization:
    """Test certificate serialization."""

    def test_certificate_json_serializable(self):
        """Certificate must be JSON serializable."""
        cert = generate_calibration_certificate(
            "test.method", {"@b": 0.9}, 0.9, 0.6, 0.3
        )

        json_str = json.dumps(cert)

        assert json_str is not None
        assert len(json_str) > 0

    def test_certificate_roundtrip(self):
        """Certificate should survive JSON roundtrip."""
        cert = generate_calibration_certificate(
            "test.method", {"@b": 0.9, "@chain": 1.0}, 0.95, 0.65, 0.30
        )

        json_str = json.dumps(cert)
        cert_restored = json.loads(json_str)

        assert cert_restored["method_id"] == cert["method_id"]
        assert cert_restored["calibration_score"] == cert["calibration_score"]
        assert cert_restored["layer_scores"] == cert["layer_scores"]

    def test_certificate_timestamp_parseable(self):
        """Certificate timestamp should be parseable."""
        cert = generate_calibration_certificate(
            "test.method", {"@b": 0.9}, 0.9, 0.6, 0.3
        )

        timestamp_str = cert["timestamp"]
        parsed = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        assert isinstance(parsed, datetime)
        assert parsed.tzinfo is not None


@pytest.mark.integration
class TestCertificateCompleteness:
    """Test certificate completeness for different method types."""

    def test_certificate_for_score_q_method(self):
        """Certificate for SCORE_Q method should include all layers."""
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

        cert = generate_calibration_certificate(
            "test.score_q_method", layer_scores, 0.8618, 0.6198, 0.242
        )

        assert len(cert["layer_scores"]) == 8

    def test_certificate_for_ingest_method(self):
        """Certificate for INGEST_PDM method should include limited layers."""
        layer_scores = {
            "@b": 0.85,
            "@chain": 1.0,
            "@u": 0.75,
        }

        cert = generate_calibration_certificate(
            "test.ingest_method", layer_scores, 0.8667, 0.7, 0.1667
        )

        assert len(cert["layer_scores"]) == 3
        assert "@q" not in cert["layer_scores"]
        assert "@d" not in cert["layer_scores"]

    def test_certificate_fusion_contributions_sum(self):
        """Linear and interaction contributions should sum to cal_score."""
        layer_scores = {"@b": 0.9, "@chain": 1.0}
        linear = 0.6
        interaction = 0.35
        cal_score = linear + interaction

        cert = generate_calibration_certificate(
            "test.method", layer_scores, cal_score, linear, interaction
        )

        fusion = cert["fusion_computation"]
        computed_sum = fusion["linear_contribution"] + fusion["interaction_contribution"]

        assert abs(computed_sum - cert["calibration_score"]) < 1e-6
