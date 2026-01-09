"""
ExecutorConfig: Runtime parametrization for executors (HOW we execute).

PHASE_LABEL: Phase 2

CRITICAL SEPARATION:
- This file contains ONLY runtime parameters (timeout, retry, etc.)
- NO calibration values (quality scores, fusion weights) are stored here
- Calibration data (WHAT quality) is loaded from:
  * src/cross_cutting_infrastructure/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json
  * canonic_questionnaire_central/questionnaire_monolith.json

Loading hierarchy (highest to lowest priority):
1. CLI arguments (--timeout-s=120)
2. Environment variables (FARFAN_TIMEOUT_S=120)
3. Environment file (system/config/environments/{env}.json)
4. Executor config file (executor_configs/{executor_id}.json)
5. Conservative defaults

See CALIBRATION_VS_PARAMETRIZATION.md for complete specification.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ExecutorConfig:
    """
    Runtime configuration for executor execution (HOW parameters only).
    
    This dataclass contains ONLY execution parameters that control HOW
    executors run, NOT calibration values that define WHAT quality we measure.
    
    Loading Hierarchy:
        CLI args > ENV vars > environment file > executor config file > defaults
    
    Attributes:
        timeout_s: Maximum execution time in seconds
        retry: Number of retry attempts on failure
        temperature: LLM sampling temperature (0.0 = deterministic)
        max_tokens: Maximum LLM output tokens
        memory_limit_mb: Memory limit in megabytes
        enable_profiling: Whether to enable execution profiling
        seed: Random seed for reproducibility
        extra: Additional executor-specific parameters
    """

    timeout_s: float | None = None
    retry: int | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    memory_limit_mb: int | None = None
    enable_profiling: bool = True
    seed: int | None = None
    extra: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.timeout_s is not None and self.timeout_s <= 0:
            raise ValueError("timeout_s must be positive when provided")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive when provided")
        if self.retry is not None and self.retry < 0:
            raise ValueError("retry must be non-negative when provided")
        if self.temperature is not None and not (0.0 <= self.temperature <= 2.0):
            raise ValueError("temperature must be in range [0.0, 2.0]")
        if self.memory_limit_mb is not None and self.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive when provided")

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> ExecutorConfig:
        """Create ExecutorConfig from dictionary."""
        valid_fields = {
            "timeout_s", "retry", "temperature", "max_tokens",
            "memory_limit_mb", "enable_profiling", "seed", "extra"
        }
        filtered = {k: v for k, v in config_dict.items() if k in valid_fields}
        return cls(**filtered)

    @classmethod
    def load_from_sources(
        cls,
        executor_id: str,
        environment: str = "production",
        cli_overrides: Optional[Dict[str, Any]] = None
    ) -> ExecutorConfig:
        """
        Load ExecutorConfig from multiple sources with proper hierarchy.
        
        Loading order (highest to lowest priority):
        1. CLI arguments (passed via cli_overrides)
        2. Environment variables (FARFAN_*)
        3. Environment file (system/config/environments/{env}.json)
        4. Executor config file (executor_configs/{executor_id}.json)
        5. Conservative defaults
        
        Args:
            executor_id: Executor identifier (e.g., "Q001" or legacy "D3_Q2_TargetProportionalityAnalyzer")
            environment: Environment name (development, staging, production)
            cli_overrides: CLI argument overrides
        
        Returns:
            ExecutorConfig with merged configuration
        """
        config = cls._get_conservative_defaults()
        
        executor_config = cls._load_executor_config_file(executor_id)
        if executor_config:
            config.update(executor_config)
        
        env_config = cls._load_environment_file(environment)
        if env_config and "executor" in env_config:
            config.update(env_config["executor"])
        
        env_vars = cls._load_environment_variables()
        config.update(env_vars)
        
        if cli_overrides:
            config.update(cli_overrides)
        
        return cls.from_dict(config)

    @staticmethod
    def _get_conservative_defaults() -> Dict[str, Any]:
        """Get conservative default parameters."""
        return {
            "timeout_s": 300.0,
            "retry": 3,
            "temperature": 0.0,
            "max_tokens": 4096,
            "memory_limit_mb": 512,
            "enable_profiling": True,
            "seed": 42,
        }

    @staticmethod
    def _load_executor_config_file(executor_id: str) -> Optional[Dict[str, Any]]:
        """Load executor-specific config file."""
        config_file = Path(__file__).resolve().parent / "executor_configs" / f"{executor_id}.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file) as f:
                data = json.load(f)
                return data.get("runtime_parameters", {})
        except (json.JSONDecodeError, IOError):
            return None

    @staticmethod
    def _load_environment_file(environment: str) -> Optional[Dict[str, Any]]:
        """Load environment-specific config file."""
        base_path = Path(__file__).resolve().parent.parent.parent.parent / "system" / "config" / "environments"
        env_file = base_path / f"{environment}.json"
        
        if not env_file.exists():
            return None
        
        try:
            with open(env_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    @staticmethod
    def _load_environment_variables() -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        if "FARFAN_TIMEOUT_S" in os.environ:
            config["timeout_s"] = float(os.environ["FARFAN_TIMEOUT_S"])
        if "FARFAN_RETRY" in os.environ:
            config["retry"] = int(os.environ["FARFAN_RETRY"])
        if "FARFAN_TEMPERATURE" in os.environ:
            config["temperature"] = float(os.environ["FARFAN_TEMPERATURE"])
        if "FARFAN_MAX_TOKENS" in os.environ:
            config["max_tokens"] = int(os.environ["FARFAN_MAX_TOKENS"])
        if "FARFAN_MEMORY_LIMIT_MB" in os.environ:
            config["memory_limit_mb"] = int(os.environ["FARFAN_MEMORY_LIMIT_MB"])
        if "FARFAN_SEED" in os.environ:
            config["seed"] = int(os.environ["FARFAN_SEED"])
        
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {
            k: v for k, v in {
                "timeout_s": self.timeout_s,
                "retry": self.retry,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "memory_limit_mb": self.memory_limit_mb,
                "enable_profiling": self.enable_profiling,
                "seed": self.seed,
                "extra": self.extra,
            }.items() if v is not None
        }


__all__ = ["ExecutorConfig"]
