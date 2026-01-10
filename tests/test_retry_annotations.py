"""Tests for retry pattern degradation annotations."""

import pytest
from farfan_pipeline.utils.retry import RetryConfig


class TestRetryPatternAnnotations:
    """Test retry pattern degradation annotations."""

    def test_retry_config_degradation_metadata(self):
        config = RetryConfig()

        # Check that degradation metadata exists as attributes
        assert hasattr(config, "degradation_instance")
        assert hasattr(config, "fallback_strategy")

        # Check specific values
        assert config.degradation_instance == "RETRY_PATTERN_7"
        assert config.fallback_strategy == "PROPAGATE_AFTER_EXHAUST"

    def test_retry_config_attributes(self):
        config = RetryConfig(
            max_retries=3,
            base_delay_seconds=0.5,
            multiplier=1.5,
            max_delay_seconds=30.0,
            jitter_factor=0.05,
        )

        assert config.max_retries == 3
        assert config.base_delay_seconds == 0.5
        assert config.multiplier == 1.5
        assert config.max_delay_seconds == 30.0
        assert config.jitter_factor == 0.05

        # Verify degradation metadata still present
        assert config.degradation_instance == "RETRY_PATTERN_7"
        assert config.fallback_strategy == "PROPAGATE_AFTER_EXHAUST"

    def test_retry_config_docstring_contains_degradation_info(self):
        config = RetryConfig()

        # Check that the class docstring contains degradation information
        docstring = RetryConfig.__doc__
        assert "Degradation Instance: 7" in docstring
        assert "Pattern: RETRY_WITH_BACKOFF" in docstring
        assert "Fallback Behavior" in docstring
        assert "Recovery:" in docstring

    def test_retry_config_validation(self):
        # Test valid configuration
        config = RetryConfig(max_retries=5, base_delay_seconds=1.0)
        assert config.max_retries == 5

        # Test invalid configuration raises error
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            RetryConfig(max_retries=-1)
