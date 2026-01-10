"""
ExecutorConfig: Runtime parametrization for executors (HOW we execute).

PHASE_LABEL: Phase 2

CRITICAL SEPARATION:
- This file contains ONLY runtime parameters (timeout, retry, etc.)
- NO calibration values (quality scores, fusion weights) are stored here
- Calibration data (WHAT quality) is loaded from:
  * src/farfan_pipeline/infrastructure/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json
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
import logging
import os
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


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
    def from_dict(cls, config_dict: dict[str, Any]) -> ExecutorConfig:
        """Create ExecutorConfig from dictionary."""
        valid_fields = {
            "timeout_s",
            "retry",
            "temperature",
            "max_tokens",
            "memory_limit_mb",
            "enable_profiling",
            "seed",
            "extra",
        }
        filtered = {k: v for k, v in config_dict.items() if k in valid_fields}
        return cls(**filtered)

    @classmethod
    def load_from_sources(
        cls,
        executor_id: str,
        environment: str = "production",
        cli_overrides: dict[str, Any] | None = None,
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
    def _get_conservative_defaults() -> dict[str, Any]:
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
    def _load_executor_config_file(executor_id: str) -> dict[str, Any] | None:
        """Load executor-specific config file."""
        config_file = Path(__file__).resolve().parent / "executor_configs" / f"{executor_id}.json"

        if not config_file.exists():
            return None

        try:
            with open(config_file) as f:
                data = json.load(f)
                return data.get("runtime_parameters", {})
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def _load_environment_file(environment: str) -> dict[str, Any] | None:
        """Load environment-specific config file."""
        base_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "system"
            / "config"
            / "environments"
        )
        env_file = base_path / f"{environment}.json"

        if not env_file.exists():
            return None

        try:
            with open(env_file) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def _load_environment_variables() -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {
            k: v
            for k, v in {
                "timeout_s": self.timeout_s,
                "retry": self.retry,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "memory_limit_mb": self.memory_limit_mb,
                "enable_profiling": self.enable_profiling,
                "seed": self.seed,
                "extra": self.extra,
            }.items()
            if v is not None
        }


# ============================================================================
# Minor Improvement 3: Hot-Reloadable Configuration
# ============================================================================

import signal
import time


class HotReloadableConfig:
    """
    Configuration wrapper with hot-reload support.

    Minor Improvement 3: ExecutorConfig Hot Reload

    Features:
        - Automatic configuration reload on SIGHUP signal
        - File watching for automatic reload on change
        - Thread-safe config access
        - Reload callbacks for notification

    Usage:
        config = HotReloadableConfig(Path("config.json"))
        config.start_watching()  # Optional: watch for file changes

        # Access config
        timeout = config.get("timeout_s", 300)

        # Reload manually
        config.reload()
    """

    def __init__(
        self,
        config_path: Path,
        auto_reload_signal: bool = True,
        reload_interval_seconds: float = 30.0,
    ):
        """
        Initialize hot-reloadable config.

        Args:
            config_path: Path to configuration file.
            auto_reload_signal: Whether to reload on SIGHUP.
            reload_interval_seconds: Interval for file change detection.
        """
        self.config_path = config_path
        self.reload_interval_seconds = reload_interval_seconds
        self._config: dict[str, Any] = {}
        self._lock = threading.RLock()

        # Track both execution time and file modification time
        self._loaded_at: datetime | None = None  # When config was loaded (execution time)
        self._file_modified_at: datetime | None = None  # File modification time (timezone-aware)

        self._watching = False
        self._watch_thread: threading.Thread | None = None
        self._reload_callbacks: list[Callable[[dict[str, Any]], None]] = []

        # Load initial config
        self._load_config()

        # Register signal handler
        if auto_reload_signal:
            self._register_signal_handler()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        with self._lock:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                return self._config

            try:
                with open(self.config_path) as f:
                    self._config = json.load(f)

                # Track when config was loaded (execution time)
                self._loaded_at = datetime.now(UTC)

                # Track file modification time (convert to timezone-aware)
                self._file_modified_at = datetime.fromtimestamp(
                    self.config_path.stat().st_mtime, tz=UTC
                )

                logger.info(f"Configuration loaded from {self.config_path}")
                return self._config
            except (OSError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load config: {e}")
                return self._config

    def _register_signal_handler(self) -> None:
        """
        Register SIGHUP handler for reload.

        Note: Signal handlers must be registered from the main thread.
        If this config is initialized in a non-main thread, signal
        registration will fail silently and hot-reload will not be available.
        """
        try:
            # Check if we're in the main thread
            if threading.current_thread() != threading.main_thread():
                logger.warning(
                    "Cannot register signal handler from non-main thread. "
                    "Signal-based config reload will be disabled."
                )
                return

            signal.signal(signal.SIGHUP, self._reload_handler)
            logger.debug("Registered SIGHUP handler for config reload")
        except (AttributeError, ValueError) as e:
            # SIGHUP not available on Windows or in some contexts
            logger.debug(f"SIGHUP not available, skipping signal handler: {e}")

    def _reload_handler(self, signum: int, frame: Any) -> None:
        """Signal handler for reload."""
        logger.info("Received SIGHUP, reloading configuration")
        self.reload()

    def reload(self) -> dict[str, Any]:
        """
        Reload configuration from file.

        Returns:
            Reloaded configuration dict.
        """
        old_config = dict(self._config)
        new_config = self._load_config()

        # Notify callbacks if config changed
        if old_config != new_config:
            for callback in self._reload_callbacks:
                try:
                    callback(new_config)
                except Exception as e:
                    logger.error(f"Reload callback failed: {e}")

        return new_config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value.
        """
        with self._lock:
            return self._config.get(key, default)

    def get_all(self) -> dict[str, Any]:
        """Get complete configuration."""
        with self._lock:
            return dict(self._config)

    def on_reload(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """
        Register callback for configuration reload.

        Args:
            callback: Function to call with new config on reload.
        """
        self._reload_callbacks.append(callback)

    def start_watching(self) -> None:
        """Start background file watching for auto-reload."""
        if self._watching:
            return

        self._watching = True
        self._watch_thread = threading.Thread(
            target=self._watch_loop, daemon=True, name="ConfigWatcher"
        )
        self._watch_thread.start()
        logger.info(f"Started watching {self.config_path} for changes")

    def stop_watching(self) -> None:
        """Stop background file watching."""
        self._watching = False
        if self._watch_thread:
            self._watch_thread.join(timeout=1.0)
            self._watch_thread = None
        logger.info("Stopped config file watching")

    def _watch_loop(self) -> None:
        """Background loop to detect file changes."""
        while self._watching:
            try:
                if self.config_path.exists():
                    # Convert file mtime to timezone-aware datetime
                    current_file_modified = datetime.fromtimestamp(
                        self.config_path.stat().st_mtime, tz=UTC
                    )

                    # Compare with last known file modification time
                    if (
                        self._file_modified_at is None
                        or current_file_modified > self._file_modified_at
                    ):
                        logger.info("Config file changed, reloading")
                        self.reload()
            except Exception as e:
                logger.debug(f"Error checking config file: {e}")

            time.sleep(self.reload_interval_seconds)

    def to_executor_config(self) -> ExecutorConfig:
        """
        Convert to ExecutorConfig instance.

        Returns:
            ExecutorConfig with current configuration.
        """
        return ExecutorConfig.from_dict(self.get_all())


__all__ = ["ExecutorConfig", "HotReloadableConfig"]
