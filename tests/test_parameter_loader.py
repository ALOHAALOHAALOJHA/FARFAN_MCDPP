"""Tests for parameter loading hierarchy."""

import json
import os
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from farfan_pipeline.core.orchestrator.executor_config import ExecutorConfig
from farfan_pipeline.core.orchestrator.parameter_loader import (
    CONSERVATIVE_CONFIG,
    get_conservative_defaults,
    load_executor_config,
)


class TestParameterLoader:
    """Test suite for parameter loading with hierarchy."""

    def test_conservative_defaults(self) -> None:
        """Test that conservative defaults are returned."""
        defaults = get_conservative_defaults()
        assert defaults["timeout_s"] == 300.0
        assert defaults["retry"] == 3
        assert defaults["max_tokens"] == 2048
        assert defaults["temperature"] == 0.7
        assert defaults["seed"] == 42

    def test_load_with_defaults_only(self, tmp_path: Path) -> None:
        """Test loading with only conservative defaults (no files, no env vars)."""
        with patch(
            "farfan_pipeline.core.orchestrator.parameter_loader.Path"
        ) as mock_path:
            mock_path.return_value.exists.return_value = False

            config = load_executor_config(env="production")

            assert config.timeout_s == CONSERVATIVE_CONFIG["timeout_s"]
            assert config.retry == CONSERVATIVE_CONFIG["retry"]
            assert config.max_tokens == CONSERVATIVE_CONFIG["max_tokens"]
            assert config.temperature == CONSERVATIVE_CONFIG["temperature"]
            assert config.seed == CONSERVATIVE_CONFIG["seed"]

    def test_load_with_environment_file(self, tmp_path: Path) -> None:
        """Test loading with environment file overrides."""
        env_config = {
            "executor": {
                "timeout_s": 120.0,
                "retry": 5,
                "max_tokens": 4096,
            }
        }

        env_file = tmp_path / "production.json"
        env_file.write_text(json.dumps(env_config))

        with patch(
            "farfan_pipeline.core.orchestrator.parameter_loader.Path"
        ) as mock_path:
            mock_path.return_value = env_file
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=json.dumps(env_config))):
                config = load_executor_config(env="production")

                assert config.timeout_s == 120.0
                assert config.retry == 5
                assert config.max_tokens == 4096
                assert config.temperature == CONSERVATIVE_CONFIG["temperature"]

    def test_load_with_environment_variables(self) -> None:
        """Test loading with environment variable overrides."""
        env_vars = {
            "FARFAN_TIMEOUT_S": "90.0",
            "FARFAN_RETRY": "7",
            "FARFAN_MAX_TOKENS": "8192",
        }

        with patch.dict(os.environ, env_vars):
            with patch(
                "farfan_pipeline.core.orchestrator.parameter_loader.Path"
            ) as mock_path:
                mock_path.return_value.exists.return_value = False

                config = load_executor_config(env="production")

                assert config.timeout_s == 90.0
                assert config.retry == 7
                assert config.max_tokens == 8192

    def test_load_with_cli_overrides(self) -> None:
        """Test loading with CLI argument overrides (highest priority)."""
        cli_overrides = {
            "timeout_s": 60.0,
            "retry": 2,
        }

        with patch(
            "farfan_pipeline.core.orchestrator.parameter_loader.Path"
        ) as mock_path:
            mock_path.return_value.exists.return_value = False

            config = load_executor_config(env="production", cli_overrides=cli_overrides)

            assert config.timeout_s == 60.0
            assert config.retry == 2
            assert config.max_tokens == CONSERVATIVE_CONFIG["max_tokens"]

    def test_hierarchy_precedence(self, tmp_path: Path) -> None:
        """Test complete hierarchy: CLI > ENV > file > defaults."""
        env_config = {
            "executor": {
                "timeout_s": 120.0,
                "retry": 5,
                "max_tokens": 4096,
                "temperature": 0.8,
            }
        }

        env_file = tmp_path / "production.json"
        env_file.write_text(json.dumps(env_config))

        env_vars = {
            "FARFAN_TIMEOUT_S": "90.0",
            "FARFAN_RETRY": "7",
        }

        cli_overrides = {
            "timeout_s": 60.0,
        }

        with patch.dict(os.environ, env_vars):
            with patch(
                "farfan_pipeline.core.orchestrator.parameter_loader.Path"
            ) as mock_path:
                mock_path.return_value = env_file
                mock_path.return_value.exists.return_value = True

                with patch(
                    "builtins.open", mock_open(read_data=json.dumps(env_config))
                ):
                    config = load_executor_config(
                        env="production", cli_overrides=cli_overrides
                    )

                    assert config.timeout_s == 60.0
                    assert config.retry == 7
                    assert config.max_tokens == 4096
                    assert config.temperature == 0.8

    def test_reject_quality_params_in_environment_file(self, tmp_path: Path) -> None:
        """Test that environment files with quality parameters are rejected."""
        env_config = {
            "executor": {
                "timeout_s": 120.0,
                "b_theory": 0.85,
            }
        }

        env_file = tmp_path / "production.json"
        env_file.write_text(json.dumps(env_config))

        with patch(
            "farfan_pipeline.core.orchestrator.parameter_loader.Path"
        ) as mock_path:
            mock_path.return_value = env_file
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=json.dumps(env_config))):
                with pytest.raises(
                    ValueError, match="forbidden quality score parameters"
                ):
                    load_executor_config(env="production")

    def test_reject_quality_params_in_cli_overrides(self) -> None:
        """Test that CLI overrides with quality parameters are rejected."""
        cli_overrides = {
            "timeout_s": 60.0,
            "fusion_weights": {"@b": 0.5},
        }

        with patch(
            "farfan_pipeline.core.orchestrator.parameter_loader.Path"
        ) as mock_path:
            mock_path.return_value.exists.return_value = False

            with pytest.raises(ValueError, match="forbidden quality score parameters"):
                load_executor_config(env="production", cli_overrides=cli_overrides)

    def test_reject_unknown_params_in_environment_file(self, tmp_path: Path) -> None:
        """Test that environment files with unknown parameters are rejected."""
        env_config = {
            "executor": {
                "timeout_s": 120.0,
                "unknown_param": "value",
            }
        }

        env_file = tmp_path / "production.json"
        env_file.write_text(json.dumps(env_config))

        with patch(
            "farfan_pipeline.core.orchestrator.parameter_loader.Path"
        ) as mock_path:
            mock_path.return_value = env_file
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=json.dumps(env_config))):
                with pytest.raises(ValueError, match="unknown parameters"):
                    load_executor_config(env="production")


class TestExecutorConfig:
    """Test ExecutorConfig dataclass."""

    def test_executor_config_creation(self) -> None:
        """Test creating ExecutorConfig with valid parameters."""
        config = ExecutorConfig(
            timeout_s=120.0,
            retry=5,
            max_tokens=2048,
            temperature=0.7,
            seed=42,
        )

        assert config.timeout_s == 120.0
        assert config.retry == 5
        assert config.max_tokens == 2048
        assert config.temperature == 0.7
        assert config.seed == 42

    def test_executor_config_validation(self) -> None:
        """Test ExecutorConfig validation."""
        with pytest.raises(ValueError, match="max_tokens must be positive"):
            ExecutorConfig(max_tokens=-1)

        with pytest.raises(ValueError, match="retry must be non-negative"):
            ExecutorConfig(retry=-1)

    def test_executor_config_no_quality_fields(self) -> None:
        """Test that ExecutorConfig has no quality score fields."""
        from dataclasses import fields

        config_fields = {f.name for f in fields(ExecutorConfig)}
        quality_fields = {
            "b_theory",
            "b_impl",
            "b_deploy",
            "fusion_weights",
            "linear_weights",
            "interaction_weights",
            "quality_score",
        }

        assert config_fields.isdisjoint(quality_fields), (
            f"ExecutorConfig contains forbidden quality fields: "
            f"{config_fields & quality_fields}"
        )
