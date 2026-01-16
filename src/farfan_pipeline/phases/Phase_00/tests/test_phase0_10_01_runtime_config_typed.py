import pytest
import os
from farfan_pipeline.phases.Phase_00.phase0_10_01_runtime_config_typed import (
    create_runtime_config_typed,
    ProdRuntimeConfig,
    DevRuntimeConfig
)
from farfan_pipeline.phases.Phase_00.phase0_10_01_runtime_config import RuntimeMode

def test_create_typed_config_dev():
    """Test factory creates DevRuntimeConfig in DEV mode."""
    os.environ["FARFAN_RUNTIME_MODE"] = "dev"
    config = create_runtime_config_typed()
    assert isinstance(config, DevRuntimeConfig)
    assert config.mode == RuntimeMode.DEV

def test_create_typed_config_prod():
    """Test factory creates ProdRuntimeConfig in PROD mode."""
    os.environ["FARFAN_RUNTIME_MODE"] = "prod"
    config = create_runtime_config_typed()
    assert isinstance(config, ProdRuntimeConfig)
    assert config.mode == RuntimeMode.PROD
    # Type enforcement check (runtime check of value)
    assert config.allow_dev_ingestion_fallbacks is False