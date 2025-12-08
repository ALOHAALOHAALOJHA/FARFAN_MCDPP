"""
Parameter loading with strict hierarchy enforcement.

This module implements the loading hierarchy for ExecutorConfig runtime parameters:
    1. CLI Arguments (highest priority)
    2. Environment Variables
    3. Environment File (system/config/environments/{env}.json)
    4. Conservative Defaults (fallback)

CRITICAL: This loader handles ONLY runtime parameters (HOW), never calibration data (WHAT).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from farfan_pipeline.core.orchestrator.executor_config import ExecutorConfig

CONSERVATIVE_CONFIG: dict[str, Any] = {
    "timeout_s": 300.0,
    "retry": 3,
    "max_tokens": 2048,
    "temperature": 0.7,
    "seed": 42,
}


def load_executor_config(
    env: str = "production",
    cli_overrides: dict[str, Any] | None = None,
) -> ExecutorConfig:
    """
    Load ExecutorConfig with proper hierarchy.

    Precedence: CLI args > ENV vars > environment file > defaults

    Args:
        env: Environment name (development, staging, production)
        cli_overrides: Optional CLI argument overrides (highest priority)

    Returns:
        ExecutorConfig instance with resolved parameters

    Raises:
        ValueError: If environment file is invalid or contains forbidden parameters
    """
    config = dict(CONSERVATIVE_CONFIG)

    env_file = Path(f"system/config/environments/{env}.json")
    if env_file.exists():
        with open(env_file) as f:
            env_config = json.load(f)
            if "executor" in env_config:
                _validate_environment_config(env_config["executor"], env_file)
                config.update(env_config["executor"])

    env_vars = _load_from_environment_variables()
    config.update(env_vars)

    if cli_overrides:
        _validate_cli_overrides(cli_overrides)
        config.update(cli_overrides)

    return ExecutorConfig(**config)


def _load_from_environment_variables() -> dict[str, Any]:
    """Load parameters from environment variables with FARFAN_ prefix."""
    env_config: dict[str, Any] = {}

    if "FARFAN_TIMEOUT_S" in os.environ:
        env_config["timeout_s"] = float(os.environ["FARFAN_TIMEOUT_S"])

    if "FARFAN_RETRY" in os.environ:
        env_config["retry"] = int(os.environ["FARFAN_RETRY"])

    if "FARFAN_MAX_TOKENS" in os.environ:
        env_config["max_tokens"] = int(os.environ["FARFAN_MAX_TOKENS"])

    if "FARFAN_TEMPERATURE" in os.environ:
        env_config["temperature"] = float(os.environ["FARFAN_TEMPERATURE"])

    if "FARFAN_SEED" in os.environ:
        env_config["seed"] = int(os.environ["FARFAN_SEED"])

    return env_config


def _validate_environment_config(
    executor_config: dict[str, Any], file_path: Path
) -> None:
    """
    Validate that environment config contains only runtime parameters.

    Args:
        executor_config: Executor configuration from environment file
        file_path: Path to environment file (for error messages)

    Raises:
        ValueError: If forbidden parameters are found
    """
    allowed_keys = {"timeout_s", "retry", "max_tokens", "temperature", "seed", "extra"}
    forbidden_keys = {
        "b_theory",
        "b_impl",
        "b_deploy",
        "fusion_weights",
        "linear_weights",
        "interaction_weights",
        "quality_score",
    }

    actual_keys = set(executor_config.keys())
    invalid_keys = actual_keys - allowed_keys
    quality_keys = actual_keys & forbidden_keys

    if quality_keys:
        raise ValueError(
            f"Environment file {file_path} contains forbidden quality score parameters: "
            f"{quality_keys}. Quality scores must be in calibration files."
        )

    if invalid_keys:
        raise ValueError(
            f"Environment file {file_path} contains unknown parameters: {invalid_keys}. "
            f"Allowed: {allowed_keys}"
        )


def _validate_cli_overrides(cli_overrides: dict[str, Any]) -> None:
    """
    Validate that CLI overrides contain only runtime parameters.

    Args:
        cli_overrides: CLI argument overrides

    Raises:
        ValueError: If forbidden parameters are found
    """
    allowed_keys = {"timeout_s", "retry", "max_tokens", "temperature", "seed", "extra"}
    forbidden_keys = {
        "b_theory",
        "b_impl",
        "b_deploy",
        "fusion_weights",
        "linear_weights",
        "interaction_weights",
        "quality_score",
    }

    actual_keys = set(cli_overrides.keys())
    invalid_keys = actual_keys - allowed_keys
    quality_keys = actual_keys & forbidden_keys

    if quality_keys:
        raise ValueError(
            f"CLI overrides contain forbidden quality score parameters: {quality_keys}. "
            f"Quality scores must be in calibration files."
        )

    if invalid_keys:
        raise ValueError(
            f"CLI overrides contain unknown parameters: {invalid_keys}. "
            f"Allowed: {allowed_keys}"
        )


def get_conservative_defaults() -> dict[str, Any]:
    """Get conservative default configuration."""
    return dict(CONSERVATIVE_CONFIG)


__all__ = [
    "load_executor_config",
    "get_conservative_defaults",
    "CONSERVATIVE_CONFIG",
]
