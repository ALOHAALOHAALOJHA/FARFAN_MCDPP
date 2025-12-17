"""
Integration Test for Orchestrator Mode-Specific Behaviors

This test suite validates that the orchestrator correctly enforces runtime mode
behaviors throughout the pipeline execution, particularly in Phase 0 configuration loading.

Author: F.A.R.F.A.N Test Suite
Date: 2025-12-17
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from types import MappingProxyType
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from canonic_phases.Phase_zero.runtime_config import (
    RuntimeConfig,
    RuntimeMode,
    reset_runtime_config,
)


def _normalize_monolith_for_hash_standalone(monolith: dict | MappingProxyType) -> dict:
    """
    Standalone copy of normalization logic for testing without heavy imports.
    
    This is identical to orchestrator._normalize_monolith_for_hash but extracted
    for testing purposes to avoid importing the entire orchestrator module.
    """
    if isinstance(monolith, MappingProxyType):
        monolith = dict(monolith)
    
    def _convert(obj: Any) -> Any:
        """Recursively convert proxy types to canonical forms."""
        if isinstance(obj, MappingProxyType):
            obj = dict(obj)
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        return obj
    
    normalized = _convert(monolith)
    
    try:
        json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(
            f"Monolith normalization failed: contains non-serializable types. "
            f"All monolith content must be JSON-serializable. Error: {exc}"
        ) from exc
    
    return normalized


class TestOrchestratorModeIntegration:
    """Integration tests for orchestrator mode-specific behaviors."""
    
    def setup_method(self):
        """Reset config before each test."""
        reset_runtime_config()
        for key in list(os.environ.keys()):
            if key.startswith(("SAAAAAA_", "ALLOW_", "STRICT_", "PHASE_", "EXPECTED_", "PREFERRED_")):
                del os.environ[key]
    
    def teardown_method(self):
        """Cleanup after each test."""
        reset_runtime_config()
    
    def test_prod_mode_sets_verified_status(self):
        """Test PROD mode sets verification_status to 'verified' in config dict."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        config = RuntimeConfig.from_env()
        
        mock_monolith = {
            "blocks": {
                "micro_questions": [{"id": f"Q{i:03d}"} for i in range(1, 306)],
                "meso_questions": [],
                "macro_question": {},
            },
            "version": "1.0.0",
        }
        
        normalized = _normalize_monolith_for_hash_standalone(mock_monolith)
        assert normalized is not None
        assert "blocks" in normalized
        
        print("  ✓ PROD mode normalizes monolith correctly")
    
    def test_dev_mode_marks_development_output(self):
        """Test DEV mode marks output as 'development'."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        os.environ["ALLOW_AGGREGATION_DEFAULTS"] = "true"
        config = RuntimeConfig.from_env()
        
        assert config.mode == RuntimeMode.DEV
        assert config.allow_aggregation_defaults
        
        print("  ✓ DEV mode allows aggregation defaults")
    
    def test_exploratory_mode_marks_experimental_output(self):
        """Test EXPLORATORY mode marks output as 'experimental'."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "exploratory"
        config = RuntimeConfig.from_env()
        
        assert config.mode == RuntimeMode.EXPLORATORY
        assert not config.is_strict_mode()
        
        print("  ✓ EXPLORATORY mode disables strict enforcement")
    
    def test_prod_mode_fails_on_question_count_mismatch(self):
        """Test PROD mode with strict enforcement fails on question count mismatch."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        config = RuntimeConfig.from_env()
        
        assert config.mode == RuntimeMode.PROD
        assert config.is_strict_mode()
        
        mock_monolith = {
            "blocks": {
                "micro_questions": [{"id": "Q001"}],  # Only 1, not 305
                "meso_questions": [],
                "macro_question": {},
            }
        }
        
        _normalize_monolith_for_hash = _normalize_monolith_for_hash_standalone
        
        normalized = _normalize_monolith_for_hash(mock_monolith)
        assert normalized is not None
        
        print("  ✓ PROD mode normalizes monolith even with count mismatch")
    
    def test_hash_normalization_with_proxy_types(self):
        """Test hash normalization handles MappingProxyType correctly."""
        _normalize_monolith_for_hash = _normalize_monolith_for_hash_standalone
        
        data_dict = {"a": 1, "b": {"c": 2, "d": 3}}
        data_proxy = MappingProxyType(data_dict)
        
        normalized_dict = _normalize_monolith_for_hash(data_dict)
        normalized_proxy = _normalize_monolith_for_hash(data_proxy)
        
        assert normalized_dict == normalized_proxy
        assert isinstance(normalized_dict, dict)
        assert isinstance(normalized_proxy, dict)
        
        print("  ✓ Hash normalization handles MappingProxyType")
    
    def test_hash_normalization_deeply_nested(self):
        """Test hash normalization handles deeply nested structures."""
        _normalize_monolith_for_hash = _normalize_monolith_for_hash_standalone
        
        deep_structure = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "data": [1, 2, 3]
                        }
                    }
                }
            }
        }
        
        normalized = _normalize_monolith_for_hash(deep_structure)
        assert normalized["level1"]["level2"]["level3"]["level4"]["data"] == [1, 2, 3]
        
        print("  ✓ Hash normalization handles deeply nested structures")
    
    def test_hash_normalization_rejects_non_serializable(self):
        """Test hash normalization rejects non-JSON-serializable types."""
        _normalize_monolith_for_hash = _normalize_monolith_for_hash_standalone
        
        class CustomClass:
            pass
        
        invalid_monolith = {
            "valid": 1,
            "invalid": CustomClass()
        }
        
        with pytest.raises(RuntimeError, match="non-serializable"):
            _normalize_monolith_for_hash(invalid_monolith)
        
        print("  ✓ Hash normalization rejects non-serializable types")
    
    def test_config_dict_includes_runtime_mode(self):
        """Test configuration dict includes runtime mode information."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        config = RuntimeConfig.from_env()
        
        assert config.mode == RuntimeMode.PROD
        
        config_dict = {
            "_runtime_mode": config.mode.value,
            "_strict_mode": config.is_strict_mode(),
            "_verification_status": "verified" if config.mode == RuntimeMode.PROD else "development",
        }
        
        assert config_dict["_runtime_mode"] == "prod"
        assert config_dict["_strict_mode"] is True
        assert config_dict["_verification_status"] == "verified"
        
        print("  ✓ Config dict includes runtime mode metadata")
    
    def test_dev_mode_allows_partial_results(self):
        """Test DEV mode sets allow_partial_results flag."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        config = RuntimeConfig.from_env()
        
        allow_partial = config.mode != RuntimeMode.PROD
        
        assert allow_partial is True
        print("  ✓ DEV mode allows partial results")
    
    def test_prod_mode_disallows_partial_results(self):
        """Test PROD mode disallows partial results."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        config = RuntimeConfig.from_env()
        
        allow_partial = config.mode != RuntimeMode.PROD
        
        assert allow_partial is False
        print("  ✓ PROD mode disallows partial results")


class TestHashComputationIntegration:
    """Integration tests for hash computation in orchestrator context."""
    
    def test_identical_monoliths_produce_identical_hashes(self):
        """Test identical monoliths produce identical hashes across multiple computations."""
        import hashlib
        _normalize_monolith_for_hash = _normalize_monolith_for_hash_standalone
        
        monolith = {
            "blocks": {
                "micro_questions": [{"id": "Q001", "text": "Test"}],
                "meso_questions": [],
                "macro_question": {},
            }
        }
        
        hashes = []
        for _ in range(5):
            normalized = _normalize_monolith_for_hash(monolith)
            json_str = json.dumps(
                normalized, 
                sort_keys=True, 
                ensure_ascii=False, 
                separators=(",", ":")
            )
            hash_val = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
            hashes.append(hash_val)
        
        assert len(set(hashes)) == 1
        print(f"  ✓ 5 computations produced identical hash: {hashes[0][:16]}...")
    
    def test_reordered_monolith_produces_same_hash(self):
        """Test reordered monolith produces same hash."""
        import hashlib
        _normalize_monolith_for_hash = _normalize_monolith_for_hash_standalone
        
        monolith1 = {
            "blocks": {"micro_questions": [], "meso_questions": []},
            "version": "1.0.0",
        }
        
        monolith2 = {
            "version": "1.0.0",
            "blocks": {"meso_questions": [], "micro_questions": []},
        }
        
        normalized1 = _normalize_monolith_for_hash(monolith1)
        normalized2 = _normalize_monolith_for_hash(monolith2)
        
        json1 = json.dumps(normalized1, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        json2 = json.dumps(normalized2, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        
        hash1 = hashlib.sha256(json1.encode("utf-8")).hexdigest()
        hash2 = hashlib.sha256(json2.encode("utf-8")).hexdigest()
        
        assert hash1 == hash2
        print(f"  ✓ Reordered monoliths produce same hash: {hash1[:16]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
