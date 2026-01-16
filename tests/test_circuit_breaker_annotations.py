"""Tests for circuit breaker degradation annotations."""

import pytest
from farfan_pipeline.phases.Phase_02.phase2_30_04_circuit_breaker import CircuitBreakerConfig


class TestCircuitBreakerAnnotations:
    """Test circuit breaker degradation annotations."""

    def test_circuit_breaker_degradation_metadata(self):
        config = CircuitBreakerConfig()

        # Check that degradation metadata exists
        assert hasattr(config, "degradation_instance")
        assert hasattr(config, "fallback_strategy")

        # Check specific values
        assert config.degradation_instance == "CIRCUIT_BREAKER_5_6_6a"
        assert config.fallback_strategy == "FAIL_FAST_WITH_CACHED"

    def test_circuit_breaker_config_attributes(self):
        config = CircuitBreakerConfig(
            failure_threshold=3, success_threshold=2, recovery_timeout_s=30.0, half_open_max_calls=2
        )

        assert config.failure_threshold == 3
        assert config.success_threshold == 2
        assert config.recovery_timeout_s == 30.0
        assert config.half_open_max_calls == 2

        # Verify degradation metadata still present
        assert config.degradation_instance == "CIRCUIT_BREAKER_5_6_6a"
        assert config.fallback_strategy == "FAIL_FAST_WITH_CACHED"

    def test_circuit_breaker_docstring_contains_degradation_info(self):
        config = CircuitBreakerConfig()

        # Check that the class docstring contains degradation information
        docstring = CircuitBreakerConfig.__doc__
        assert "Degradation Instance: 5, 6, 6a" in docstring
        assert "Pattern:  CIRCUIT_BREAKER" in docstring
        assert "Fallback Behavior" in docstring
        assert "Recovery:" in docstring
