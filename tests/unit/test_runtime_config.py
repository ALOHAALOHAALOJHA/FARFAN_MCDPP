"""
Test suite for runtime configuration system.

Tests environment variable parsing, illegal combination detection,
and precedence rules for PROD/DEV/EXPLORATORY modes.
"""

import os
import pytest

from farfan_core.core.runtime_config import (
    RuntimeConfig,
    RuntimeMode,
    ConfigurationError,
    reset_runtime_config,
)


class TestRuntimeConfigParsing:
    """Test environment variable parsing and validation."""
    
    def setup_method(self):
        """Reset config before each test."""
        reset_runtime_config()
        # Clear all relevant env vars
        for var in [
            "SAAAAAA_RUNTIME_MODE",
            "ALLOW_CONTRADICTION_FALLBACK",
            "ALLOW_EXECUTION_ESTIMATES",
            "ALLOW_DEV_INGESTION_FALLBACKS",
            "ALLOW_AGGREGATION_DEFAULTS",
            "STRICT_CALIBRATION",
            "ALLOW_VALIDATOR_DISABLE",
            "ALLOW_HASH_FALLBACK",
            "PREFERRED_SPACY_MODEL",
        ]:
            os.environ.pop(var, None)
    
    def test_default_config(self):
        """Test default configuration (PROD mode)."""
        config = RuntimeConfig.from_env()
        
        assert config.mode == RuntimeMode.PROD
        assert not config.allow_contradiction_fallback
        assert not config.allow_execution_estimates
        assert not config.allow_dev_ingestion_fallbacks
        assert not config.allow_aggregation_defaults
        assert config.strict_calibration
        assert not config.allow_validator_disable
        assert config.allow_hash_fallback
        assert config.preferred_spacy_model == "es_core_news_lg"
    
    def test_dev_mode_parsing(self):
        """Test DEV mode parsing."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        config = RuntimeConfig.from_env()
        
        assert config.mode == RuntimeMode.PROD
    
    def test_exploratory_mode_parsing(self):
        """Test EXPLORATORY mode parsing."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "exploratory"
        config = RuntimeConfig.from_env()
        
        assert config.mode == RuntimeMode.EXPLORATORY
    
    def test_boolean_flag_parsing(self):
        """Test boolean flag parsing with various formats."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        os.environ["ALLOW_CONTRADICTION_FALLBACK"] = "true"
        os.environ["ALLOW_EXECUTION_ESTIMATES"] = "1"
        os.environ["STRICT_CALIBRATION"] = "false"
        
        config = RuntimeConfig.from_env()
        
        assert config.allow_contradiction_fallback
        assert config.allow_execution_estimates
        assert not config.strict_calibration
    
    def test_invalid_mode_raises_error(self):
        """Test that invalid mode raises ConfigurationError."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "invalid"
        
        with pytest.raises(ConfigurationError, match="Invalid SAAAAAA_RUNTIME_MODE"):
            RuntimeConfig.from_env()
    
    def test_invalid_boolean_raises_error(self):
        """Test that invalid boolean value raises ConfigurationError."""
        os.environ["ALLOW_CONTRADICTION_FALLBACK"] = "maybe"
        
        with pytest.raises(ConfigurationError, match="Invalid boolean value"):
            RuntimeConfig.from_env()


class TestIllegalCombinations:
    """Test illegal configuration combination detection."""
    
    def setup_method(self):
        """Reset config before each test."""
        reset_runtime_config()
        for var in os.environ:
            if var.startswith("SAAAAAA_") or var.startswith("ALLOW_"):
                os.environ.pop(var, None)
    
    def test_prod_with_dev_ingestion_fallbacks_rejected(self):
        """Test PROD + ALLOW_DEV_INGESTION_FALLBACKS is rejected."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["ALLOW_DEV_INGESTION_FALLBACKS"] = "true"
        
        with pytest.raises(ConfigurationError, match="Illegal configuration"):
            RuntimeConfig.from_env()
    
    def test_prod_with_execution_estimates_rejected(self):
        """Test PROD + ALLOW_EXECUTION_ESTIMATES is rejected."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["ALLOW_EXECUTION_ESTIMATES"] = "true"
        
        with pytest.raises(ConfigurationError, match="Illegal configuration"):
            RuntimeConfig.from_env()
    
    def test_prod_with_aggregation_defaults_rejected(self):
        """Test PROD + ALLOW_AGGREGATION_DEFAULTS is rejected."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["ALLOW_AGGREGATION_DEFAULTS"] = "true"
        
        with pytest.raises(ConfigurationError, match="Illegal configuration"):
            RuntimeConfig.from_env()
    
    def test_dev_allows_all_flags(self):
        """Test DEV mode allows all ALLOW_* flags."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        os.environ["ALLOW_DEV_INGESTION_FALLBACKS"] = "true"
        os.environ["ALLOW_EXECUTION_ESTIMATES"] = "true"
        os.environ["ALLOW_AGGREGATION_DEFAULTS"] = "true"
        
        config = RuntimeConfig.from_env()
        
        assert config.allow_dev_ingestion_fallbacks
        assert config.allow_execution_estimates
        assert config.allow_aggregation_defaults
    
    def test_exploratory_allows_all_flags(self):
        """Test EXPLORATORY mode allows all ALLOW_* flags."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "exploratory"
        os.environ["ALLOW_DEV_INGESTION_FALLBACKS"] = "true"
        os.environ["ALLOW_EXECUTION_ESTIMATES"] = "true"
        
        config = RuntimeConfig.from_env()
        
        assert config.allow_dev_ingestion_fallbacks
        assert config.allow_execution_estimates


class TestPrecedenceRules:
    """Test configuration precedence rules."""
    
    def setup_method(self):
        """Reset config before each test."""
        reset_runtime_config()
        for var in os.environ:
            if var.startswith("SAAAAAA_") or var.startswith("ALLOW_"):
                os.environ.pop(var, None)
    
    def test_prod_defaults_all_allow_to_false(self):
        """Test PROD mode defaults all ALLOW_* to false."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        # Don't set any ALLOW_* flags
        
        config = RuntimeConfig.from_env()
        
        assert not config.allow_contradiction_fallback
        assert not config.allow_execution_estimates
        assert not config.allow_dev_ingestion_fallbacks
        assert not config.allow_aggregation_defaults
        assert not config.allow_validator_disable
    
    def test_strict_calibration_default_true(self):
        """Test STRICT_CALIBRATION defaults to true."""
        config = RuntimeConfig.from_env()
        
        assert config.strict_calibration
    
    def test_allow_hash_fallback_default_true(self):
        """Test ALLOW_HASH_FALLBACK defaults to true."""
        config = RuntimeConfig.from_env()
        
        assert config.allow_hash_fallback


class TestConfigMethods:
    """Test RuntimeConfig helper methods."""
    
    def test_is_strict_mode_prod_no_fallbacks(self):
        """Test is_strict_mode returns True for PROD with no fallbacks."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        config = RuntimeConfig.from_env()
        
        assert config.is_strict_mode()
    
    def test_is_strict_mode_dev_returns_false(self):
        """Test is_strict_mode returns False for DEV."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        config = RuntimeConfig.from_env()
        
        assert not config.is_strict_mode()
    
    def test_repr_shows_mode_and_flags(self):
        """Test __repr__ shows mode and active flags."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        os.environ["ALLOW_CONTRADICTION_FALLBACK"] = "true"
        config = RuntimeConfig.from_env()
        
        repr_str = repr(config)
        assert "mode=dev" in repr_str
        assert "contradiction_fallback" in repr_str
