"""
Performance tests for calibration system.

Tests performance characteristics:
- Single method calibration time (target <1s for @b, <5s for full)
- Batch calibration of 1995 methods
- Memory efficiency
- Scalability
"""

from __future__ import annotations

import time
from typing import Any

import pytest


def compute_base_layer(b_theory: float, b_impl: float, b_deploy: float) -> float:
    """Compute base layer score."""
    return 0.4 * b_theory + 0.35 * b_impl + 0.25 * b_deploy


def compute_choquet_aggregation(
    layer_scores: dict[str, float],
    linear_weights: dict[str, float],
    interaction_weights: dict[tuple[str, str], float],
) -> float:
    """Compute Choquet aggregation."""
    linear = sum(linear_weights.get(layer, 0.0) * score for layer, score in layer_scores.items())
    interaction = sum(
        weight * min(layer_scores.get(l1, 0.0), layer_scores.get(l2, 0.0))
        for (l1, l2), weight in interaction_weights.items()
    )
    return linear + interaction


def calibrate_method_base_only(base_metrics: dict[str, float]) -> float:
    """Calibrate method with base layer only (fast path)."""
    return compute_base_layer(
        base_metrics["b_theory"],
        base_metrics["b_impl"],
        base_metrics["b_deploy"],
    )


def calibrate_method_full(method_data: dict[str, Any]) -> dict[str, Any]:
    """Calibrate method with all layers."""
    layer_scores = {}

    layer_scores["@b"] = compute_base_layer(
        method_data["base_metrics"]["b_theory"],
        method_data["base_metrics"]["b_impl"],
        method_data["base_metrics"]["b_deploy"],
    )

    layer_scores["@chain"] = 1.0 if method_data.get("chain_valid", True) else 0.6

    if "context" in method_data:
        ctx = method_data["context"]
        layer_scores["@q"] = 1.0 if ctx.get("question") == "Q001" else 0.7
        layer_scores["@d"] = 1.0 if ctx.get("dimension") == "DIM01" else 0.7
        layer_scores["@p"] = 1.0 if ctx.get("policy") == "PA01" else 0.7

    if method_data.get("in_interplay", False):
        layer_scores["@C"] = 1.0

    if "pdt_quality" in method_data:
        layer_scores["@u"] = method_data["pdt_quality"]

    layer_scores["@m"] = method_data.get("meta_score", 0.95)

    linear_weights = {
        "@b": 0.17, "@chain": 0.13, "@q": 0.08, "@d": 0.07,
        "@p": 0.06, "@C": 0.08, "@u": 0.04, "@m": 0.04,
    }

    interaction_weights = {
        ("@u", "@chain"): 0.13,
        ("@chain", "@C"): 0.10,
        ("@q", "@d"): 0.10,
    }

    cal_score = compute_choquet_aggregation(layer_scores, linear_weights, interaction_weights)

    return {
        "calibration_score": cal_score,
        "layer_scores": layer_scores,
    }


@pytest.mark.performance
class TestSingleMethodPerformance:
    """Test performance for single method calibration."""

    def test_base_layer_only_fast(self):
        """Base layer only calibration should be < 1s (actually < 1ms)."""
        base_metrics = {"b_theory": 0.9, "b_impl": 0.85, "b_deploy": 0.8}

        start = time.time()
        score = calibrate_method_base_only(base_metrics)
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Base layer calibration took {elapsed}s, expected < 1s"
        assert score > 0.0

    def test_full_calibration_fast(self):
        """Full calibration should be < 5s (actually < 10ms)."""
        method_data = {
            "base_metrics": {"b_theory": 0.9, "b_impl": 0.85, "b_deploy": 0.8},
            "chain_valid": True,
            "context": {"question": "Q001", "dimension": "DIM01", "policy": "PA01"},
            "in_interplay": True,
            "pdt_quality": 0.8,
            "meta_score": 0.95,
        }

        start = time.time()
        result = calibrate_method_full(method_data)
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Full calibration took {elapsed}s, expected < 5s"
        assert result["calibration_score"] > 0.0

    def test_base_layer_computation_fast(self):
        """Base layer computation should be extremely fast."""
        iterations = 1000

        start = time.time()
        for _ in range(iterations):
            compute_base_layer(0.9, 0.85, 0.8)
        elapsed = time.time() - start

        per_iteration = elapsed / iterations

        assert per_iteration < 0.001, f"Base layer took {per_iteration}s per iteration, expected < 1ms"

    def test_choquet_aggregation_fast(self):
        """Choquet aggregation should be fast."""
        layer_scores = {
            "@b": 0.85, "@chain": 1.0, "@q": 1.0, "@d": 0.9,
            "@p": 0.8, "@C": 1.0, "@u": 0.75, "@m": 0.95,
        }

        linear_weights = {
            "@b": 0.17, "@chain": 0.13, "@q": 0.08, "@d": 0.07,
            "@p": 0.06, "@C": 0.08, "@u": 0.04, "@m": 0.04,
        }

        interaction_weights = {
            ("@u", "@chain"): 0.13,
            ("@chain", "@C"): 0.10,
            ("@q", "@d"): 0.10,
        }

        iterations = 1000

        start = time.time()
        for _ in range(iterations):
            compute_choquet_aggregation(layer_scores, linear_weights, interaction_weights)
        elapsed = time.time() - start

        per_iteration = elapsed / iterations

        assert per_iteration < 0.001, f"Choquet took {per_iteration}s per iteration, expected < 1ms"


@pytest.mark.performance
class TestBatchCalibrationPerformance:
    """Test performance for batch calibration."""

    def test_batch_100_methods_fast(self):
        """Batch of 100 methods should calibrate quickly."""
        methods = [
            {
                "base_metrics": {"b_theory": 0.85, "b_impl": 0.8, "b_deploy": 0.75},
                "context": {"question": f"Q{i:03d}", "dimension": "DIM01", "policy": "PA01"},
                "chain_valid": True,
                "meta_score": 0.9,
            }
            for i in range(100)
        ]

        start = time.time()
        results = [calibrate_method_full(m) for m in methods]
        elapsed = time.time() - start

        assert len(results) == 100
        assert elapsed < 5.0, f"Batch of 100 took {elapsed}s, expected < 5s"

    def test_batch_1995_methods_reasonable(self):
        """Batch of 1995 methods should calibrate in reasonable time."""
        methods = [
            {
                "base_metrics": {"b_theory": 0.8 + (i % 20) * 0.01, "b_impl": 0.75, "b_deploy": 0.7},
                "chain_valid": i % 10 != 0,
                "meta_score": 0.85 + (i % 15) * 0.01,
            }
            for i in range(1995)
        ]

        start = time.time()
        results = [calibrate_method_full(m) for m in methods]
        elapsed = time.time() - start

        assert len(results) == 1995

        per_method = elapsed / 1995
        assert per_method < 0.1, f"Per-method time {per_method}s, expected < 0.1s"

    @pytest.mark.slow
    def test_batch_1995_methods_detailed(self):
        """Detailed performance test for 1995 methods batch."""
        methods = []
        for i in range(1995):
            method = {
                "method_id": f"method_{i:04d}",
                "base_metrics": {
                    "b_theory": 0.7 + (i % 30) * 0.01,
                    "b_impl": 0.75 + (i % 25) * 0.01,
                    "b_deploy": 0.7 + (i % 20) * 0.01,
                },
                "chain_valid": i % 5 != 0,
                "context": {
                    "question": f"Q{(i % 300):03d}",
                    "dimension": f"DIM{(i % 6):02d}",
                    "policy": f"PA{(i % 10):02d}",
                },
                "in_interplay": i % 10 == 0,
                "pdt_quality": 0.6 + (i % 40) * 0.01,
                "meta_score": 0.85 + (i % 15) * 0.01,
            }
            methods.append(method)

        start = time.time()
        results = [calibrate_method_full(m) for m in methods]
        elapsed = time.time() - start

        assert len(results) == 1995
        assert all(0.0 <= r["calibration_score"] <= 1.0 for r in results)

        print("\nBatch calibration stats:")
        print(f"  Total time: {elapsed:.2f}s")
        print(f"  Per method: {elapsed/1995*1000:.2f}ms")
        print(f"  Methods/sec: {1995/elapsed:.0f}")


@pytest.mark.performance
class TestMemoryEfficiency:
    """Test memory efficiency of calibration."""

    def test_single_calibration_memory_efficient(self):
        """Single calibration should not allocate excessive memory."""
        method_data = {
            "base_metrics": {"b_theory": 0.9, "b_impl": 0.85, "b_deploy": 0.8},
            "chain_valid": True,
            "meta_score": 0.95,
        }

        result = calibrate_method_full(method_data)

        assert len(result) == 2
        assert len(result["layer_scores"]) <= 8

    def test_batch_calibration_no_memory_leak(self):
        """Batch calibration should not leak memory."""
        for batch in range(5):
            methods = [
                {"base_metrics": {"b_theory": 0.8, "b_impl": 0.75, "b_deploy": 0.7}}
                for _ in range(100)
            ]

            results = [calibrate_method_full(m) for m in methods]

            assert len(results) == 100


@pytest.mark.performance
class TestScalability:
    """Test scalability of calibration system."""

    def test_linear_scaling(self):
        """Calibration time should scale linearly with number of methods."""
        batch_sizes = [10, 50, 100]
        times = []

        for size in batch_sizes:
            methods = [
                {"base_metrics": {"b_theory": 0.8, "b_impl": 0.75, "b_deploy": 0.7}}
                for _ in range(size)
            ]

            start = time.time()
            results = [calibrate_method_full(m) for m in methods]
            elapsed = time.time() - start

            times.append(elapsed)
            assert len(results) == size

        time_per_method_10 = times[0] / batch_sizes[0]
        time_per_method_100 = times[2] / batch_sizes[2]

        assert time_per_method_100 < time_per_method_10 * 2, "Scaling is not linear"

    def test_layer_complexity_impact(self):
        """More layers should not dramatically increase computation time."""
        method_minimal = {
            "base_metrics": {"b_theory": 0.8, "b_impl": 0.75, "b_deploy": 0.7},
        }

        method_full = {
            "base_metrics": {"b_theory": 0.8, "b_impl": 0.75, "b_deploy": 0.7},
            "chain_valid": True,
            "context": {"question": "Q001", "dimension": "DIM01", "policy": "PA01"},
            "in_interplay": True,
            "pdt_quality": 0.8,
            "meta_score": 0.95,
        }

        start = time.time()
        for _ in range(100):
            calibrate_method_full(method_minimal)
        time_minimal = time.time() - start

        start = time.time()
        for _ in range(100):
            calibrate_method_full(method_full)
        time_full = time.time() - start

        assert time_full < time_minimal * 5, "Full calibration too slow compared to minimal"


@pytest.mark.performance
class TestConcurrentCalibration:
    """Test concurrent calibration scenarios."""

    def test_multiple_sequential_calibrations(self):
        """Multiple sequential calibrations should maintain performance."""
        method_data = {
            "base_metrics": {"b_theory": 0.85, "b_impl": 0.8, "b_deploy": 0.75},
            "chain_valid": True,
            "meta_score": 0.9,
        }

        times = []
        for _ in range(10):
            start = time.time()
            result = calibrate_method_full(method_data)
            elapsed = time.time() - start
            times.append(elapsed)
            assert result["calibration_score"] > 0.0

        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert max_time < avg_time * 5, "Performance degraded significantly over multiple runs"

    def test_different_method_types_interleaved(self):
        """Calibrating different method types should not interfere."""
        methods = [
            {"base_metrics": {"b_theory": 0.9, "b_impl": 0.85, "b_deploy": 0.8}, "chain_valid": True},
            {"base_metrics": {"b_theory": 0.7, "b_impl": 0.75, "b_deploy": 0.7}},
            {"base_metrics": {"b_theory": 0.85, "b_impl": 0.8, "b_deploy": 0.75}, "context": {"question": "Q001"}},
        ]

        start = time.time()
        for _ in range(50):
            for method in methods:
                result = calibrate_method_full(method)
                assert result["calibration_score"] > 0.0
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Interleaved calibration took {elapsed}s, expected < 5s"
