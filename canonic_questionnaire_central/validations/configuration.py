"""
Configuration Management for Enrichment System

Externalized, version-controlled configuration for policies,
thresholds, and validator settings.
"""

import json
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidatorConfig:
    """Configuration for a specific validator."""

    enabled: bool = True
    strict_mode: bool = True
    threshold: Optional[float] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0


@dataclass
class GateConfig:
    """Configuration for validation gates."""

    gate_1_scope: ValidatorConfig = field(default_factory=ValidatorConfig)
    gate_2_value_add: ValidatorConfig = field(
        default_factory=lambda: ValidatorConfig(threshold=0.10)
    )
    gate_3_capability: ValidatorConfig = field(default_factory=ValidatorConfig)
    gate_4_channel: ValidatorConfig = field(default_factory=ValidatorConfig)


@dataclass
class EnrichmentConfig:
    """Main enrichment configuration."""

    version: str = "1.0.0"
    strict_mode: bool = True
    enable_all_gates: bool = True
    async_enabled: bool = True
    max_concurrent_validations: int = 4
    default_timeout: float = 30.0
    cache_enabled: bool = True
    audit_trail_enabled: bool = True

    gates: GateConfig = field(default_factory=GateConfig)

    # Data sources
    pdet_data_path: Optional[str] = None

    # Observability
    logging_level: str = "INFO"
    metrics_enabled: bool = True

    # Security
    require_documentation: bool = True
    require_change_control: bool = True

    # Performance
    connection_pool_size: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0


class ConfigurationManager:
    """
    Manages configuration loading, validation, and hot-reloading.

    Supports JSON, YAML, and Python dict formats.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path
        self._config: Optional[EnrichmentConfig] = None
        self._watchers: List[Any] = []

    def load_config(
        self, config_path: Optional[Path] = None, config_dict: Optional[Dict[str, Any]] = None
    ) -> EnrichmentConfig:
        """
        Load configuration from file or dictionary.

        Args:
            config_path: Path to config file (JSON or YAML)
            config_dict: Configuration dictionary

        Returns:
            EnrichmentConfig object
        """
        if config_dict:
            self._config = self._dict_to_config(config_dict)
            return self._config

        if config_path is None:
            config_path = self._config_path

        if config_path is None:
            # Use defaults
            logger.info("No config file specified, using defaults")
            self._config = EnrichmentConfig()
            return self._config

        if not config_path.exists():
            logger.warning(f"Config file {config_path} not found, using defaults")
            self._config = EnrichmentConfig()
            return self._config

        # Load from file
        suffix = config_path.suffix.lower()

        try:
            if suffix == ".json":
                with open(config_path, "r") as f:
                    data = json.load(f)
            elif suffix in [".yaml", ".yml"]:
                with open(config_path, "r") as f:
                    data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config format: {suffix}")

            self._config = self._dict_to_config(data)
            logger.info(f"Loaded configuration from {config_path}")
            return self._config

        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            self._config = EnrichmentConfig()
            return self._config

    def _dict_to_config(self, data: Dict[str, Any]) -> EnrichmentConfig:
        """Convert dictionary to EnrichmentConfig."""
        # Parse gates config
        gates_data = data.get("gates", {})
        gates = GateConfig(
            gate_1_scope=ValidatorConfig(**gates_data.get("gate_1_scope", {})),
            gate_2_value_add=ValidatorConfig(
                **gates_data.get("gate_2_value_add", {"threshold": 0.10})
            ),
            gate_3_capability=ValidatorConfig(**gates_data.get("gate_3_capability", {})),
            gate_4_channel=ValidatorConfig(**gates_data.get("gate_4_channel", {})),
        )

        # Create config
        config = EnrichmentConfig(
            version=data.get("version", "1.0.0"),
            strict_mode=data.get("strict_mode", True),
            enable_all_gates=data.get("enable_all_gates", True),
            async_enabled=data.get("async_enabled", True),
            max_concurrent_validations=data.get("max_concurrent_validations", 4),
            default_timeout=data.get("default_timeout", 30.0),
            cache_enabled=data.get("cache_enabled", True),
            audit_trail_enabled=data.get("audit_trail_enabled", True),
            gates=gates,
            pdet_data_path=data.get("pdet_data_path"),
            logging_level=data.get("logging_level", "INFO"),
            metrics_enabled=data.get("metrics_enabled", True),
            require_documentation=data.get("require_documentation", True),
            require_change_control=data.get("require_change_control", True),
            connection_pool_size=data.get("connection_pool_size", 10),
            retry_attempts=data.get("retry_attempts", 3),
            retry_delay=data.get("retry_delay", 1.0),
        )

        return config

    def save_config(self, path: Path, format: str = "json") -> None:
        """
        Save current configuration to file.

        Args:
            path: Output path
            format: Output format ('json' or 'yaml')
        """
        if self._config is None:
            raise ValueError("No configuration loaded")

        data = self._config_to_dict(self._config)

        with open(path, "w") as f:
            if format == "json":
                json.dump(data, f, indent=2)
            elif format == "yaml":
                yaml.dump(data, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Saved configuration to {path}")

    def _config_to_dict(self, config: EnrichmentConfig) -> Dict[str, Any]:
        """Convert EnrichmentConfig to dictionary."""
        return asdict(config)

    def get_config(self) -> EnrichmentConfig:
        """Get current configuration."""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update specific configuration values.

        Args:
            updates: Dictionary of config keys to update
        """
        if self._config is None:
            self._config = EnrichmentConfig()

        current_dict = self._config_to_dict(self._config)
        self._deep_update(current_dict, updates)
        self._config = self._dict_to_config(current_dict)

        logger.info(f"Updated configuration: {updates}")

    def _deep_update(self, base: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Deep update dictionary."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def validate_config(self) -> List[str]:
        """
        Validate current configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        if self._config is None:
            return ["No configuration loaded"]

        errors = []

        # Validate thresholds
        if self._config.gates.gate_2_value_add.threshold is not None:
            threshold = self._config.gates.gate_2_value_add.threshold
            if threshold < 0 or threshold > 1:
                errors.append(f"Gate 2 threshold must be between 0 and 1, got {threshold}")

        # Validate timeouts
        if self._config.default_timeout <= 0:
            errors.append(f"default_timeout must be positive, got {self._config.default_timeout}")

        # Validate pool size
        if self._config.connection_pool_size <= 0:
            errors.append(
                f"connection_pool_size must be positive, got {self._config.connection_pool_size}"
            )

        # Validate retry attempts
        if self._config.retry_attempts < 0:
            errors.append(f"retry_attempts must be non-negative, got {self._config.retry_attempts}")

        return errors

    def get_validator_config(self, gate_name: str) -> ValidatorConfig:
        """Get configuration for a specific gate."""
        if self._config is None:
            self._config = self.load_config()

        gate_map = {
            "gate_1": self._config.gates.gate_1_scope,
            "gate_2": self._config.gates.gate_2_value_add,
            "gate_3": self._config.gates.gate_3_capability,
            "gate_4": self._config.gates.gate_4_channel,
        }

        return gate_map.get(gate_name, ValidatorConfig())


# Global configuration manager
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get or create global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def load_config_from_file(path: Path) -> EnrichmentConfig:
    """Load configuration from file."""
    manager = get_config_manager()
    return manager.load_config(path)


def get_current_config() -> EnrichmentConfig:
    """Get current configuration."""
    manager = get_config_manager()
    return manager.get_config()
