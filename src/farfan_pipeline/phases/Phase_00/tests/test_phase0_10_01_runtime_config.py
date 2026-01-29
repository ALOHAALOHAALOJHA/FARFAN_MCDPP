import pytest
import os
from farfan_pipeline.phases.Phase_00.phase0_10_01_runtime_config import (
    RuntimeConfig,
    RuntimeMode,
    ConfigurationError
)

def test_runtime_config_from_env(mock_env):
    """Test loading config from environment."""
    config = RuntimeConfig.from_env()
    assert config.mode == RuntimeMode.DEV
    assert config.allow_hash_fallback is True

def test_strict_mode_constraints():
    """Test PROD mode validation logic."""
    # Illegal combo: PROD + allow_dev_ingestion_fallbacks
    os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
    os.environ["ALLOW_DEV_INGESTION_FALLBACKS"] = "true"
    
    with pytest.raises(ConfigurationError):
        RuntimeConfig.from_env()
    
    # Clean up
    del os.environ["ALLOW_DEV_INGESTION_FALLBACKS"]
    os.environ["SAAAAAA_RUNTIME_MODE"] = "dev" # Reset

def test_runtime_mode_enums():
    """Test enum values."""
    assert RuntimeMode.PROD.value == "prod"
    assert RuntimeMode.DEV.value == "dev"
    assert RuntimeMode.EXPLORATORY.value == "exploratory"
