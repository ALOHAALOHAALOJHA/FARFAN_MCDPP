"""
Orchestrator Configuration Module.

Provides configuration management for the core pipeline orchestrator,
including defaults, validation, and environment-based configuration.

Author: F.A.R.F.A.N Core Team
Version: 1.0.0
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# =============================================================================
# DEFAULT PATHS
# =============================================================================


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent.parent.parent


def get_data_dir() -> Path:
    """Get the data directory."""
    return get_project_root() / "data"


def get_config_dir() -> Path:
    """Get the configuration directory."""
    return get_project_root() / "config"


def get_default_questionnaire_path() -> Path:
    """Get the default questionnaire monolith path."""
    return get_data_dir() / "questionnaire_monolith.json"


def get_default_executor_config_path() -> Path:
    """Get the default executor configuration path."""
    return get_config_dir() / "executor_config.json"


# =============================================================================
# ORCHESTRATOR CONFIGURATION
# =============================================================================


@dataclass
class OrchestratorConfig:
    """Configuration for the pipeline orchestrator.

    This configuration encapsulates all parameters needed to run the
    complete F.A.R.F.A.N pipeline orchestrator.

    Attributes:
        questionnaire_path: Path to questionnaire monolith JSON
        questionnaire_hash: Expected SHA-256 hash (empty = skip validation)
        executor_config_path: Path to executor configuration
        calibration_profile: Calibration profile to use
        abort_on_insufficient: Abort if insufficient data detected
        resource_limits: Resource limit settings (memory, CPU, etc.)
        enable_http_signals: Use HTTP signal transport (vs in-memory)
        enable_calibration: Enable calibration orchestrator
        strict_mode: Raise exceptions on critical violations
        deterministic: Enforce deterministic execution (SIN_CARRETA)
        output_dir: Directory for outputs and reports
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    # Core paths
    questionnaire_path: Path | None = None
    questionnaire_hash: str = ""
    executor_config_path: Path | None = None

    # Calibration and data handling
    calibration_profile: str = "default"
    abort_on_insufficient: bool = True

    # Resource control
    resource_limits: dict[str, int] = field(default_factory=lambda: {
        "memory_mb": 2048,
        "cpu_seconds": 300,
        "disk_mb": 500,
        "file_descriptors": 1024,
    })

    # Feature flags
    enable_http_signals: bool = False
    enable_calibration: bool = False
    strict_mode: bool = True
    deterministic: bool = True

    # Output and logging
    output_dir: Path | None = None
    log_level: str = "INFO"

    # Execution control
    start_phase: str = "P00"  # Phase 0 (bootstrap)
    end_phase: str = "P10"  # Phase 9 (report assembly)

    def __post_init__(self):
        """Validate and normalize configuration."""
        # Set defaults for None paths
        if self.questionnaire_path is None:
            default_path = get_default_questionnaire_path()
            if default_path.exists():
                self.questionnaire_path = default_path
                logger.info("using_default_questionnaire", path=str(default_path))

        if self.executor_config_path is None:
            default_path = get_default_executor_config_path()
            if default_path.exists():
                self.executor_config_path = default_path
                logger.info("using_default_executor_config", path=str(default_path))

        if self.output_dir is None:
            self.output_dir = get_project_root() / "output"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Validate paths
        self._validate_paths()

    def _validate_paths(self) -> None:
        """Validate that required paths exist."""
        # Questionnaire path is optional (can use embedded defaults)
        if self.questionnaire_path and not self.questionnaire_path.exists():
            logger.warning(
                "questionnaire_path_not_found",
                path=str(self.questionnaire_path),
                note="Will attempt to use embedded defaults",
            )

        # Executor config is optional
        if self.executor_config_path and not self.executor_config_path.exists():
            logger.warning(
                "executor_config_path_not_found",
                path=str(self.executor_config_path),
                note="Will use default executor configuration",
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize configuration to dictionary."""
        return {
            "questionnaire_path": str(self.questionnaire_path) if self.questionnaire_path else None,
            "questionnaire_hash": self.questionnaire_hash,
            "executor_config_path": str(self.executor_config_path) if self.executor_config_path else None,
            "calibration_profile": self.calibration_profile,
            "abort_on_insufficient": self.abort_on_insufficient,
            "resource_limits": self.resource_limits,
            "enable_http_signals": self.enable_http_signals,
            "enable_calibration": self.enable_calibration,
            "strict_mode": self.strict_mode,
            "deterministic": self.deterministic,
            "output_dir": str(self.output_dir),
            "log_level": self.log_level,
            "start_phase": self.start_phase,
            "end_phase": self.end_phase,
        }

    @classmethod
    def from_env(cls) -> OrchestratorConfig:
        """Create configuration from environment variables.

        Environment variables:
            FARFAN_QUESTIONNAIRE_PATH: Path to questionnaire
            FARFAN_QUESTIONNAIRE_HASH: Expected hash
            FARFAN_EXECUTOR_CONFIG_PATH: Path to executor config
            FARFAN_CALIBRATION_PROFILE: Calibration profile
            FARFAN_STRICT_MODE: Strict validation mode (true/false)
            FARFAN_DETERMINISTIC: Deterministic execution (true/false)
            FARFAN_OUTPUT_DIR: Output directory
            FARFAN_LOG_LEVEL: Logging level
            FARFAN_START_PHASE: Starting phase (P00-P10)
            FARFAN_END_PHASE: Ending phase (P00-P10)

        Returns:
            OrchestratorConfig instance
        """
        def parse_bool(value: str | None, default: bool = False) -> bool:
            if value is None:
                return default
            return value.lower() in ("true", "1", "yes", "on")

        def parse_path(value: str | None) -> Path | None:
            if value is None:
                return None
            return Path(value).resolve()

        return cls(
            questionnaire_path=parse_path(os.getenv("FARFAN_QUESTIONNAIRE_PATH")),
            questionnaire_hash=os.getenv("FARFAN_QUESTIONNAIRE_HASH", ""),
            executor_config_path=parse_path(os.getenv("FARFAN_EXECUTOR_CONFIG_PATH")),
            calibration_profile=os.getenv("FARFAN_CALIBRATION_PROFILE", "default"),
            strict_mode=parse_bool(os.getenv("FARFAN_STRICT_MODE"), default=True),
            deterministic=parse_bool(os.getenv("FARFAN_DETERMINISTIC"), default=True),
            output_dir=parse_path(os.getenv("FARFAN_OUTPUT_DIR")),
            log_level=os.getenv("FARFAN_LOG_LEVEL", "INFO"),
            start_phase=os.getenv("FARFAN_START_PHASE", "P00"),
            end_phase=os.getenv("FARFAN_END_PHASE", "P10"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OrchestratorConfig:
        """Create configuration from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            OrchestratorConfig instance
        """
        # Convert string paths to Path objects
        if "questionnaire_path" in data and data["questionnaire_path"]:
            data["questionnaire_path"] = Path(data["questionnaire_path"])

        if "executor_config_path" in data and data["executor_config_path"]:
            data["executor_config_path"] = Path(data["executor_config_path"])

        if "output_dir" in data and data["output_dir"]:
            data["output_dir"] = Path(data["output_dir"])

        return cls(**data)


# =============================================================================
# CONFIGURATION PRESETS
# =============================================================================


def get_development_config() -> OrchestratorConfig:
    """Get configuration preset for development.

    Development preset:
    - Relaxed resource limits
    - Non-strict mode (warnings instead of errors)
    - In-memory signals
    - Debug logging
    """
    return OrchestratorConfig(
        resource_limits={
            "memory_mb": 4096,
            "cpu_seconds": 600,
            "disk_mb": 1000,
            "file_descriptors": 2048,
        },
        strict_mode=False,
        enable_http_signals=False,
        log_level="DEBUG",
    )


def get_production_config() -> OrchestratorConfig:
    """Get configuration preset for production.

    Production preset:
    - Standard resource limits
    - Strict mode enabled
    - HTTP signals (if configured)
    - INFO logging
    - Deterministic execution
    """
    return OrchestratorConfig(
        resource_limits={
            "memory_mb": 2048,
            "cpu_seconds": 300,
            "disk_mb": 500,
            "file_descriptors": 1024,
        },
        strict_mode=True,
        deterministic=True,
        enable_http_signals=False,
        log_level="INFO",
    )


def get_testing_config() -> OrchestratorConfig:
    """Get configuration preset for testing.

    Testing preset:
    - Minimal resource limits
    - Strict mode enabled
    - In-memory signals
    - Deterministic execution (for reproducibility)
    - Warning logging
    """
    return OrchestratorConfig(
        resource_limits={
            "memory_mb": 1024,
            "cpu_seconds": 120,
            "disk_mb": 250,
            "file_descriptors": 512,
        },
        strict_mode=True,
        deterministic=True,
        enable_http_signals=False,
        log_level="WARNING",
    )


# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


def validate_config(config: OrchestratorConfig) -> list[str]:
    """Validate orchestrator configuration.

    Args:
        config: Configuration to validate

    Returns:
        List of validation warnings (empty if valid)

    Raises:
        ConfigValidationError: If configuration is invalid
    """
    warnings = []

    # Validate phase identifiers
    valid_phases = ["P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P10"]
    if config.start_phase not in valid_phases:
        raise ConfigValidationError(f"Invalid start_phase: {config.start_phase}")
    if config.end_phase not in valid_phases:
        raise ConfigValidationError(f"Invalid end_phase: {config.end_phase}")

    # Validate phase order
    start_idx = valid_phases.index(config.start_phase)
    end_idx = valid_phases.index(config.end_phase)
    if start_idx > end_idx:
        raise ConfigValidationError(
            f"start_phase ({config.start_phase}) must come before end_phase ({config.end_phase})"
        )

    # Validate resource limits
    if config.resource_limits.get("memory_mb", 0) < 512:
        warnings.append("Memory limit < 512MB may cause OOM errors")

    if config.resource_limits.get("cpu_seconds", 0) < 60:
        warnings.append("CPU time limit < 60s may cause timeout errors")

    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.log_level not in valid_log_levels:
        raise ConfigValidationError(f"Invalid log_level: {config.log_level}")

    # Validate output directory
    if not config.output_dir:
        raise ConfigValidationError("output_dir is required")

    # Warning for non-deterministic execution
    if not config.deterministic:
        warnings.append("Non-deterministic execution enabled - results may not be reproducible")

    return warnings


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OrchestratorConfig",
    "ConfigValidationError",
    "validate_config",
    "get_development_config",
    "get_production_config",
    "get_testing_config",
    "get_project_root",
    "get_data_dir",
    "get_config_dir",
]
