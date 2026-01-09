"""Tests for get_executor_config integration with ExecutorConfig.

Verifies:
1. Delegation to ExecutorConfig.load_from_sources()
2. Proper field mapping to legacy schema
3. Environment variable overrides work
4. Precondition validation preserved
5. Debug logging shows loaded configuration
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the module under test
from farfan_pipeline.phases.Phase_two.phase2_95_03_executor_calibration_integration import (
    get_executor_config,
)


class TestGetExecutorConfigIntegration:
    """Test get_executor_config integration with ExecutorConfig."""

    def test_returns_valid_config_dict(self) -> None:
        """Test that get_executor_config returns valid configuration."""
        config = get_executor_config("test_executor", "D1", "Q1")

        assert isinstance(config, dict)
        assert len(config) > 0

    def test_config_has_required_keys(self) -> None:
        """Test that config contains expected runtime parameters."""
        config = get_executor_config("test_executor", "D1", "Q1")

        # Legacy schema keys should be present
        assert "timeout_seconds" in config
        assert "max_retries" in config
        assert "retry_delay_seconds" in config
        assert "memory_limit_mb" in config
        assert "enable_caching" in config
        assert "enable_profiling" in config

    def test_default_values_match_conservative_defaults(self) -> None:
        """Test that default values match ExecutorConfig conservative defaults."""
        config = get_executor_config("test_executor", "D1", "Q1")

        # Should use ExecutorConfig's conservative defaults
        assert config["timeout_seconds"] == 300
        assert config["max_retries"] == 3
        assert config["retry_delay_seconds"] == 1.0
        assert config["memory_limit_mb"] == 512  # ExecutorConfig default
        assert config["enable_caching"] is True
        assert config["enable_profiling"] is True

    def test_environment_variable_timeout_override(self) -> None:
        """Test that FARFAN_TIMEOUT_S environment variable overrides default."""
        with patch.dict(os.environ, {"FARFAN_TIMEOUT_S": "120"}):
            config = get_executor_config("test_executor", "D1", "Q1")
            assert config["timeout_seconds"] == 120

    def test_environment_variable_retry_override(self) -> None:
        """Test that FARFAN_RETRY environment variable overrides default."""
        with patch.dict(os.environ, {"FARFAN_RETRY": "5"}):
            config = get_executor_config("test_executor", "D1", "Q1")
            assert config["max_retries"] == 5

    def test_environment_variable_memory_override(self) -> None:
        """Test that FARFAN_MEMORY_LIMIT_MB environment variable overrides default."""
        with patch.dict(os.environ, {"FARFAN_MEMORY_LIMIT_MB": "2048"}):
            config = get_executor_config("test_executor", "D1", "Q1")
            assert config["memory_limit_mb"] == 2048

    def test_cli_overrides_have_highest_priority(self) -> None:
        """Test that CLI overrides have highest priority."""
        cli_overrides = {
            "timeout_s": 180,
            "retry": 7,
            "memory_limit_mb": 4096,
        }

        with patch.dict(os.environ, {"FARFAN_TIMEOUT_S": "120"}):
            config = get_executor_config(
                "test_executor", "D1", "Q1", cli_overrides=cli_overrides
            )
            # CLI should override environment variable
            assert config["timeout_seconds"] == 180
            assert config["max_retries"] == 7
            assert config["memory_limit_mb"] == 4096

    def test_environment_parameter_passed_through(self) -> None:
        """Test that environment parameter is passed to ExecutorConfig."""
        # This should not raise an error even with non-default environment
        config = get_executor_config(
            "test_executor", "D1", "Q1", environment="development"
        )
        assert isinstance(config, dict)
        assert "timeout_seconds" in config

    def test_precondition_non_empty_executor_id(self) -> None:
        """Test that empty executor_id raises ValueError."""
        with pytest.raises(ValueError, match="executor_id cannot be empty"):
            get_executor_config("", "D1", "Q1")

    def test_precondition_non_empty_dimension(self) -> None:
        """Test that empty dimension raises ValueError."""
        with pytest.raises(ValueError, match="dimension cannot be empty"):
            get_executor_config("test", "", "Q1")

    def test_precondition_non_empty_question(self) -> None:
        """Test that empty question raises ValueError."""
        with pytest.raises(ValueError, match="question cannot be empty"):
            get_executor_config("test", "D1", "")

    def test_backward_compatibility_with_existing_calls(self) -> None:
        """Test backward compatibility with calls not passing new parameters."""
        # Should work without environment and cli_overrides
        config = get_executor_config("test_executor", "D1", "Q1")
        assert config["timeout_seconds"] == 300
        assert config["max_retries"] == 3

    def test_field_mapping_handles_none_values(self) -> None:
        """Test that None values from ExecutorConfig use fallback defaults."""
        config = get_executor_config("test_executor", "D1", "Q1")

        # All values should be present and non-None
        assert config["timeout_seconds"] is not None
        assert config["max_retries"] is not None
        assert config["memory_limit_mb"] is not None
        assert config["enable_profiling"] is not None

    def test_constants_not_in_executor_config(self) -> None:
        """Test that constants not in ExecutorConfig remain constant."""
        config = get_executor_config("test_executor", "D1", "Q1")

        # These are not in ExecutorConfig, should always be these values
        assert config["retry_delay_seconds"] == 1.0
        assert config["enable_caching"] is True


class TestGetExecutorConfigLogging:
    """Test logging behavior of get_executor_config."""

    def test_debug_logging_on_config_request(self, caplog) -> None:
        """Test that debug logging shows config request."""
        import logging

        caplog.set_level(logging.DEBUG)

        get_executor_config("test_executor", "D1", "Q1", environment="production")

        # Should log the config request
        assert any(
            "Config requested for test_executor" in record.message
            for record in caplog.records
        )
        assert any(
            "dimension=D1" in record.message for record in caplog.records
        )
        assert any(
            "question=Q1" in record.message for record in caplog.records
        )
        assert any(
            "environment=production" in record.message for record in caplog.records
        )

    def test_debug_logging_shows_loaded_values(self, caplog) -> None:
        """Test that debug logging shows loaded configuration values."""
        import logging

        caplog.set_level(logging.DEBUG)

        get_executor_config("test_executor", "D1", "Q1")

        # Should log the loaded values
        assert any(
            "Loaded config for test_executor" in record.message
            for record in caplog.records
        )
        assert any("timeout=" in record.message for record in caplog.records)
        assert any("retries=" in record.message for record in caplog.records)
        assert any("memory=" in record.message for record in caplog.records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
