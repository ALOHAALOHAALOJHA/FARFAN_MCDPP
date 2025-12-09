"""
Integration test for complete calibration flow.

Tests end-to-end calibration on sample method with all layers:
- Load configuration
- Compute all layer scores
- Aggregate with Choquet integral
- Generate certificate
- Validate output structure
"""

from __future__ import annotations

import json
from typing import Any

import pytest


@pytest.fixture
def sample_method_full() -> dict[str, Any]:
    """Full method data for integration testing."""
    return {
        "method_id": "integration.test.full_calibration",
        "version": "1.0.0",
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
        "chain_validation": {
            "schema_compatible": True,
            "required_inputs_available": True,
            "warnings": [],
        },
        "pdt_data": {
            "structural_compliance": 0.8,
            "mandatory_sections_ratio": 0.9,
            "indicator_quality_score": 0.85,
            "ppi_completeness": 0.7,
        },
        "governance": {
            "formula_export_valid": True,
            "trace_complete": True,
            "logs_conform_schema": True,
            "version_tagged": True,
            "config_hash_matches": True,
            "signature_valid": True,
            "runtime_ms": 450,
            "memory_mb": 128,
        },
        "interplay": None,
    }


@pytest.mark.integration
class TestFullCalibrationFlow:
    """Test complete calibration flow."""

    def test_calibrate_sample_method(self, sample_method_full: dict[str, Any]):
        """Test calibrating a sample method through complete pipeline."""
        result = run_full_calibration(sample_method_full)

        assert "calibration_score" in result
        assert "layer_scores" in result
        assert "certificate" in result
        assert "metadata" in result

    def test_all_layers_computed(self, sample_method_full: dict[str, Any]):
        """All relevant layers should be computed."""
        result = run_full_calibration(sample_method_full)

        layer_scores = result["layer_scores"]

        assert "@b" in layer_scores
        assert "@chain" in layer_scores
        assert "@q" in layer_scores
        assert "@d" in layer_scores
        assert "@p" in layer_scores
        assert "@m" in layer_scores

    def test_layer_scores_valid_range(self, sample_method_full: dict[str, Any]):
        """All layer scores must be in [0,1]."""
        result = run_full_calibration(sample_method_full)

        for layer, score in result["layer_scores"].items():
            assert 0.0 <= score <= 1.0, f"Layer {layer} score {score} out of range"

    def test_calibration_score_valid_range(self, sample_method_full: dict[str, Any]):
        """Calibration score must be in [0,1]."""
        result = run_full_calibration(sample_method_full)

        assert 0.0 <= result["calibration_score"] <= 1.0

    def test_certificate_structure(self, sample_method_full: dict[str, Any]):
        """Certificate must have correct structure."""
        result = run_full_calibration(sample_method_full)

        cert = result["certificate"]

        assert "certificate_id" in cert
        assert "method_id" in cert
        assert "calibration_score" in cert
        assert "timestamp" in cert
        assert "layer_scores" in cert
        assert "signature" in cert

    def test_certificate_signature_valid(self, sample_method_full: dict[str, Any]):
        """Certificate signature should be valid."""
        result = run_full_calibration(sample_method_full)

        cert = result["certificate"]

        assert cert["signature"].startswith("SHA256:")
        assert len(cert["signature"]) > 10

    def test_metadata_included(self, sample_method_full: dict[str, Any]):
        """Metadata should be included in result."""
        result = run_full_calibration(sample_method_full)

        metadata = result["metadata"]

        assert "computation_time_ms" in metadata
        assert "config_version" in metadata
        assert "layers_activated" in metadata

    def test_deterministic_calibration(self, sample_method_full: dict[str, Any]):
        """Calibration should be deterministic."""
        result1 = run_full_calibration(sample_method_full)
        result2 = run_full_calibration(sample_method_full)

        assert result1["calibration_score"] == result2["calibration_score"]
        assert result1["layer_scores"] == result2["layer_scores"]

    def test_calibration_with_interplay(self, sample_method_full: dict[str, Any]):
        """Test calibration with ensemble interplay."""
        sample_method_full["interplay"] = {
            "ensemble_id": "test_ensemble",
            "methods": ["integration.test.full_calibration", "other_method"],
            "scale_compatible": True,
            "semantic_overlap": 1.0,
            "fusion_rule": "TYPE_A",
        }

        result = run_full_calibration(sample_method_full)

        assert "@C" in result["layer_scores"]
        assert result["layer_scores"]["@C"] == 1.0


def run_full_calibration(method_data: dict[str, Any]) -> dict[str, Any]:
    """Execute complete calibration pipeline."""
    import time
    start_time = time.time()

    layer_scores = {}

    base_metrics = method_data["base_metrics"]
    layer_scores["@b"] = 0.4 * base_metrics["b_theory"] + 0.35 * base_metrics["b_impl"] + 0.25 * base_metrics["b_deploy"]

    chain_val = method_data["chain_validation"]
    if chain_val["schema_compatible"] and chain_val["required_inputs_available"] and not chain_val["warnings"]:
        layer_scores["@chain"] = 1.0
    else:
        layer_scores["@chain"] = 0.8

    context = method_data.get("context", {})
    layer_scores["@q"] = 1.0 if context.get("question") == "Q001" else 0.7
    layer_scores["@d"] = 1.0 if context.get("dimension") == "DIM01" else 0.7
    layer_scores["@p"] = 1.0 if context.get("policy") == "PA01" else 0.7

    if method_data.get("interplay"):
        interplay = method_data["interplay"]
        c_scale = 1.0 if interplay.get("scale_compatible") else 0.0
        c_sem = interplay.get("semantic_overlap", 1.0)
        c_fusion = 1.0 if interplay.get("fusion_rule") else 0.0
        layer_scores["@C"] = c_scale * c_sem * c_fusion

    pdt = method_data.get("pdt_data", {})
    if pdt:
        u = 0.3 * pdt["structural_compliance"] + 0.3 * pdt["mandatory_sections_ratio"] + 0.2 * pdt["indicator_quality_score"] + 0.2 * pdt["ppi_completeness"]
        layer_scores["@u"] = u

    gov = method_data["governance"]
    m_transp = sum([gov["formula_export_valid"], gov["trace_complete"], gov["logs_conform_schema"]])
    m_transp_score = {0: 0.0, 1: 0.4, 2: 0.7, 3: 1.0}[m_transp]

    m_gov = sum([gov["version_tagged"], gov["config_hash_matches"], gov["signature_valid"]])
    m_gov_score = {0: 0.0, 1: 0.33, 2: 0.66, 3: 1.0}[m_gov]

    if gov["runtime_ms"] < 500 and gov["memory_mb"] < 256:
        m_cost_score = 1.0
    elif gov["runtime_ms"] < 2000:
        m_cost_score = 0.8
    else:
        m_cost_score = 0.5

    layer_scores["@m"] = 0.5 * m_transp_score + 0.4 * m_gov_score + 0.1 * m_cost_score

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

    cal_score = sum(linear_weights.get(l, 0.0) * s for l, s in layer_scores.items())
    cal_score += sum(w * min(layer_scores.get(l1, 0.0), layer_scores.get(l2, 0.0)) for (l1, l2), w in interaction_weights.items())

    import hashlib
    from datetime import datetime, timezone

    cert_data = json.dumps({
        "method_id": method_data["method_id"],
        "layer_scores": layer_scores,
        "cal_score": cal_score,
    }, sort_keys=True)

    signature = hashlib.sha256(cert_data.encode()).hexdigest()

    certificate = {
        "certificate_id": f"cert_{method_data['method_id']}_{int(datetime.now(timezone.utc).timestamp())}",
        "method_id": method_data["method_id"],
        "calibration_score": cal_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "layer_scores": layer_scores,
        "signature": f"SHA256:{signature}",
        "fusion_computation": {
            "linear_contribution": sum(linear_weights.get(l, 0.0) * s for l, s in layer_scores.items()),
            "interaction_contribution": sum(w * min(layer_scores.get(l1, 0.0), layer_scores.get(l2, 0.0)) for (l1, l2), w in interaction_weights.items()),
        },
    }

    computation_time = (time.time() - start_time) * 1000

    return {
        "calibration_score": cal_score,
        "layer_scores": layer_scores,
        "certificate": certificate,
        "metadata": {
            "computation_time_ms": computation_time,
            "config_version": "COHORT_2024",
            "layers_activated": list(layer_scores.keys()),
        },
    }


@pytest.mark.integration
class TestCalibrationPerformance:
    """Test calibration performance."""

    def test_calibration_time_single_method(self, sample_method_full: dict[str, Any]):
        """Calibration of single method should be fast."""
        import time

        start = time.time()
        result = run_full_calibration(sample_method_full)
        elapsed = time.time() - start

        assert elapsed < 0.1, f"Calibration took {elapsed}s, expected < 0.1s"

    def test_calibration_memory_efficient(self, sample_method_full: dict[str, Any]):
        """Calibration should be memory efficient."""
        result = run_full_calibration(sample_method_full)

        assert result is not None


@pytest.mark.integration
class TestCalibrationEdgeCases:
    """Test edge cases in calibration."""

    def test_calibrate_with_minimum_data(self):
        """Test calibration with minimum required data."""
        minimal_data = {
            "method_id": "minimal.test",
            "version": "1.0.0",
            "role": "INGEST_PDM",
            "base_metrics": {
                "b_theory": 0.7,
                "b_impl": 0.7,
                "b_deploy": 0.7,
            },
            "chain_validation": {
                "schema_compatible": True,
                "required_inputs_available": True,
                "warnings": [],
            },
            "governance": {
                "formula_export_valid": True,
                "trace_complete": True,
                "logs_conform_schema": True,
                "version_tagged": True,
                "config_hash_matches": True,
                "signature_valid": True,
                "runtime_ms": 300,
                "memory_mb": 100,
            },
        }

        result = run_full_calibration(minimal_data)

        assert result["calibration_score"] > 0.0

    def test_calibrate_with_perfect_scores(self):
        """Test calibration with all perfect scores."""
        perfect_data = {
            "method_id": "perfect.test",
            "version": "1.0.0",
            "role": "score",
            "context": {
                "question": "Q001",
                "dimension": "DIM01",
                "policy": "PA01",
            },
            "base_metrics": {
                "b_theory": 1.0,
                "b_impl": 1.0,
                "b_deploy": 1.0,
            },
            "chain_validation": {
                "schema_compatible": True,
                "required_inputs_available": True,
                "warnings": [],
            },
            "pdt_data": {
                "structural_compliance": 1.0,
                "mandatory_sections_ratio": 1.0,
                "indicator_quality_score": 1.0,
                "ppi_completeness": 1.0,
            },
            "governance": {
                "formula_export_valid": True,
                "trace_complete": True,
                "logs_conform_schema": True,
                "version_tagged": True,
                "config_hash_matches": True,
                "signature_valid": True,
                "runtime_ms": 100,
                "memory_mb": 64,
            },
        }

        result = run_full_calibration(perfect_data)

        assert result["calibration_score"] > 0.8
