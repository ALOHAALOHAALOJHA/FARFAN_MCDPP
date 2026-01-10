# tests/test_retry_annotations.py
import pytest
from farfan_pipeline.utils.retry import RetryConfig


class TestRetryAnnotations:
    """Validate retry pattern degradation annotations."""
    
    def test_retry_config_has_degradation_metadata(self):
        config = RetryConfig()
        
        # Check that degradation metadata exists
        assert hasattr(config, 'degradation_instance')
        assert hasattr(config, 'fallback_strategy')
        
        # Check specific values
        assert config.degradation_instance == "RETRY_PATTERN_7"
        assert config.fallback_strategy == "PROPAGATE_AFTER_EXHAUST"
    
    def test_retry_config_functionality(self):
        config = RetryConfig(
            max_retries=3,
            base_delay_seconds=1.0,
            multiplier=2.0,
            max_delay_seconds=60.0,
            jitter_factor=0.1
        )
        
        assert config.max_retries == 3
        assert config.base_delay_seconds == 1.0
        assert config.multiplier == 2.0
        assert config.max_delay_seconds == 60.0
        assert config.jitter_factor == 0.1
        
        # Test metrics are initialized
        assert config.total_chunks == 0
        assert config.successful_chunks == 0
        assert config.failed_chunks == 0
        assert config.total_retries == 0
        assert config.total_time_ms == 0.0