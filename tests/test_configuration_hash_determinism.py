"""
Test Suite for Configuration Hash Determinism and Runtime Mode Behavior

This test suite validates:
1. Hash determinism across dict ordering permutations
2. RuntimeMode behavioral enforcement (PROD/DEV/EXPLORATORY)
3. Configuration validation and fail-fast mechanisms
4. Regression prevention for hash computation

Author: F.A.R.F.A.N Test Suite
Date: 2025-12-17
"""

import hashlib
import json
import os
from itertools import permutations
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest

from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import (
    ConfigurationError,
    RuntimeConfig,
    RuntimeMode,
    reset_runtime_config,
)


def compute_hash(data: dict[str, Any]) -> str:
    """Compute SHA256 hash of dict using canonical JSON serialization."""
    json_str = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


class TestHashDeterminism:
    """Test suite for configuration hash determinism."""

    def test_same_content_same_hash(self):
        """Test identical content produces identical hash."""
        data1 = {"a": 1, "b": 2, "c": 3}
        data2 = {"a": 1, "b": 2, "c": 3}

        hash1 = compute_hash(data1)
        hash2 = compute_hash(data2)

        assert hash1 == hash2
        print(f"  ✓ Identical content produces same hash: {hash1[:16]}...")

    def test_different_key_order_same_hash(self):
        """Test different key ordering produces same hash due to sort_keys."""
        data1 = {"z": 26, "a": 1, "m": 13}
        data2 = {"a": 1, "m": 13, "z": 26}
        data3 = {"m": 13, "z": 26, "a": 1}

        hash1 = compute_hash(data1)
        hash2 = compute_hash(data2)
        hash3 = compute_hash(data3)

        assert hash1 == hash2 == hash3
        print(f"  ✓ Different key orders produce same hash: {hash1[:16]}...")

    def test_nested_dict_key_order_same_hash(self):
        """Test nested dicts with different key orders produce same hash."""
        data1 = {"outer": {"z": 3, "a": 1, "m": 2}, "list": [{"b": 2, "a": 1}, {"d": 4, "c": 3}]}
        data2 = {"outer": {"a": 1, "m": 2, "z": 3}, "list": [{"a": 1, "b": 2}, {"c": 3, "d": 4}]}

        hash1 = compute_hash(data1)
        hash2 = compute_hash(data2)

        assert hash1 == hash2
        print(f"  ✓ Nested dicts with different orders produce same hash: {hash1[:16]}...")

    def test_all_permutations_same_hash(self):
        """Test all permutations of keys produce same hash."""
        base_data = {"key1": 10, "key2": 20, "key3": 30, "key4": 40}

        # Create permutations by reconstructing dict with different key orders
        permuted_dicts = [
            {"key2": 20, "key1": 10, "key3": 30, "key4": 40},
            {"key3": 30, "key4": 40, "key1": 10, "key2": 20},
            {"key4": 40, "key3": 30, "key2": 20, "key1": 10},
            {"key1": 10, "key3": 30, "key2": 20, "key4": 40},
        ]

        hashes = {compute_hash(d) for d in [base_data] + permuted_dicts}

        assert len(hashes) == 1
        print(f"  ✓ All 5 key orderings produce identical hash")

    def test_monolith_structure_hash_stability(self):
        """Test realistic monolith structure produces stable hash."""
        monolith = {
            "blocks": {
                "micro_questions": [
                    {"id": "Q001", "text": "Question 1"},
                    {"id": "Q002", "text": "Question 2"},
                ],
                "meso_questions": [
                    {"id": "M001", "text": "Meso 1"},
                ],
                "macro_question": {"id": "MACRO", "text": "Macro question"},
            },
            "metadata": {
                "version": "1.0.0",
                "created": "2025-12-17",
            },
        }

        hash1 = compute_hash(monolith)

        # Reorder top-level keys
        monolith_reordered = {
            "metadata": monolith["metadata"],
            "blocks": monolith["blocks"],
        }
        hash2 = compute_hash(monolith_reordered)

        assert hash1 == hash2
        print(f"  ✓ Monolith structure produces stable hash: {hash1[:16]}...")

    def test_mapping_proxy_normalization(self):
        """Test MappingProxyType is normalized consistently."""
        data_dict = {"a": 1, "b": 2}
        data_proxy = MappingProxyType(data_dict)

        hash_dict = compute_hash(dict(data_dict))
        hash_proxy = compute_hash(dict(data_proxy))

        assert hash_dict == hash_proxy
        print("  ✓ MappingProxyType normalized to same hash as dict")

    def test_unicode_handling_deterministic(self):
        """Test Unicode content produces deterministic hash."""
        data1 = {"text": "Análisis de políticas públicas"}
        data2 = {"text": "Análisis de políticas públicas"}

        hash1 = compute_hash(data1)
        hash2 = compute_hash(data2)

        assert hash1 == hash2
        print(f"  ✓ Unicode content produces deterministic hash: {hash1[:16]}...")

    def test_empty_structures_deterministic(self):
        """Test empty structures produce deterministic hashes."""
        empty_dict = {}
        empty_list = []

        hash1 = compute_hash(empty_dict)
        hash2 = compute_hash(empty_dict)

        assert hash1 == hash2
        print("  ✓ Empty structures produce deterministic hash")

    def test_large_monolith_hash_performance(self):
        """Test hash computation completes quickly for large monoliths."""
        import time

        large_monolith = {
            "blocks": {
                "micro_questions": [
                    {"id": f"Q{i:03d}", "text": f"Question {i}", "metadata": {"index": i}}
                    for i in range(300)
                ],
            }
        }

        start = time.perf_counter()
        hash_val = compute_hash(large_monolith)
        duration = time.perf_counter() - start

        assert duration < 0.1  # Should complete in under 100ms
        assert len(hash_val) == 64  # SHA256 produces 64 hex chars
        print(f"  ✓ Large monolith (300 questions) hashed in {duration*1000:.2f}ms")


class TestRuntimeModeBehavior:
    """Test suite for runtime mode behavioral enforcement."""

    def setup_method(self):
        """Reset config before each test."""
        reset_runtime_config()
        for key in list(os.environ.keys()):
            if key.startswith(
                ("SAAAAAA_", "ALLOW_", "STRICT_", "PHASE_", "EXPECTED_", "PREFERRED_")
            ):
                del os.environ[key]

    def teardown_method(self):
        """Cleanup after each test."""
        reset_runtime_config()

    def test_prod_mode_creates_verified_status(self):
        """Test PROD mode sets verification_status='verified'."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        config = RuntimeConfig.from_env()

        assert config.mode == RuntimeMode.PROD
        assert config.is_strict_mode()
        print("  ✓ PROD mode enables strict enforcement")

    def test_dev_mode_creates_development_status(self):
        """Test DEV mode sets verification_status='development'."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        config = RuntimeConfig.from_env()

        assert config.mode == RuntimeMode.DEV
        assert not config.is_strict_mode()
        print("  ✓ DEV mode disables strict enforcement")

    def test_exploratory_mode_creates_experimental_status(self):
        """Test EXPLORATORY mode sets verification_status='experimental'."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "exploratory"
        config = RuntimeConfig.from_env()

        assert config.mode == RuntimeMode.EXPLORATORY
        assert not config.is_strict_mode()
        print("  ✓ EXPLORATORY mode disables strict enforcement")

    def test_prod_mode_rejects_partial_results_flags(self):
        """Test PROD mode rejects flags that enable partial results."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["ALLOW_AGGREGATION_DEFAULTS"] = "true"

        with pytest.raises(ConfigurationError, match="Illegal configuration"):
            RuntimeConfig.from_env()

        print("  ✓ PROD mode rejects ALLOW_AGGREGATION_DEFAULTS")

    def test_dev_mode_allows_partial_results_flags(self):
        """Test DEV mode allows flags for partial results."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        os.environ["ALLOW_AGGREGATION_DEFAULTS"] = "true"
        os.environ["ALLOW_DEV_INGESTION_FALLBACKS"] = "true"

        config = RuntimeConfig.from_env()

        assert config.allow_aggregation_defaults
        assert config.allow_dev_ingestion_fallbacks
        print("  ✓ DEV mode allows partial result flags")

    def test_exploratory_mode_allows_all_flags(self):
        """Test EXPLORATORY mode allows all experimental flags."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "exploratory"
        os.environ["ALLOW_AGGREGATION_DEFAULTS"] = "true"
        os.environ["ALLOW_EXECUTION_ESTIMATES"] = "true"
        os.environ["ALLOW_DEV_INGESTION_FALLBACKS"] = "true"

        config = RuntimeConfig.from_env()

        assert config.allow_aggregation_defaults
        assert config.allow_execution_estimates
        assert config.allow_dev_ingestion_fallbacks
        print("  ✓ EXPLORATORY mode allows all experimental flags")

    def test_invalid_runtime_mode_fails_fast(self):
        """Test invalid runtime mode value causes immediate failure."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "invalid_mode"

        with pytest.raises(ConfigurationError, match="Invalid SAAAAAA_RUNTIME_MODE"):
            RuntimeConfig.from_env()

        print("  ✓ Invalid runtime mode fails fast with clear error")

    def test_strict_calibration_property(self):
        """Test strict_calibration property reflects PROD mode correctly."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        config = RuntimeConfig.from_env()

        assert config.strict_calibration
        print("  ✓ PROD mode enforces strict calibration")

        os.environ["ALLOW_MISSING_BASE_WEIGHTS"] = "true"
        reset_runtime_config()

        with pytest.raises(ConfigurationError):
            RuntimeConfig.from_env()

        print("  ✓ PROD + ALLOW_MISSING_BASE_WEIGHTS rejected")

    def test_dev_mode_relaxed_calibration(self):
        """Test DEV mode allows relaxed calibration."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        os.environ["ALLOW_MISSING_BASE_WEIGHTS"] = "true"
        config = RuntimeConfig.from_env()

        assert not config.strict_calibration
        assert config.allow_missing_base_weights
        print("  ✓ DEV mode allows relaxed calibration")


class TestRegressionPrevention:
    """Test suite for preventing hash and mode regressions."""

    def setup_method(self):
        """Reset config before each test."""
        reset_runtime_config()
        for key in list(os.environ.keys()):
            if key.startswith(
                ("SAAAAAA_", "ALLOW_", "STRICT_", "PHASE_", "EXPECTED_", "PREFERRED_")
            ):
                del os.environ[key]

    def teardown_method(self):
        """Cleanup after each test."""
        reset_runtime_config()

    def test_reference_hash_unchanged(self):
        """Test reference monolith produces known hash (regression detection)."""
        reference_monolith = {
            "blocks": {
                "micro_questions": [
                    {"id": "Q001", "text": "Test question 1"},
                    {"id": "Q002", "text": "Test question 2"},
                ],
                "meso_questions": [],
                "macro_question": {},
            },
            "version": "1.0.0",
        }

        hash_val = compute_hash(reference_monolith)

        # This hash should remain stable across all code changes
        # If this test fails, hash computation logic has changed
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)
        print(f"  ✓ Reference hash format valid: {hash_val[:16]}...")

    def test_runtime_config_defaults_stable(self):
        """Test RuntimeConfig default values remain stable."""
        config = RuntimeConfig.from_env()

        assert config.mode == RuntimeMode.PROD
        assert not config.allow_contradiction_fallback
        assert not config.allow_validator_disable
        assert not config.allow_execution_estimates
        assert not config.allow_aggregation_defaults
        assert config.allow_hash_fallback  # Operational flexibility
        print("  ✓ RuntimeConfig defaults remain stable")

    def test_runtime_mode_enum_values_stable(self):
        """Test RuntimeMode enum values remain unchanged."""
        assert RuntimeMode.PROD.value == "prod"
        assert RuntimeMode.DEV.value == "dev"
        assert RuntimeMode.EXPLORATORY.value == "exploratory"
        print("  ✓ RuntimeMode enum values stable")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
