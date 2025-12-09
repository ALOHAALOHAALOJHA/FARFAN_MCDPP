"""
Global runtime configuration system for F.A.R.F.A.N.

This module provides runtime mode enforcement (PROD/DEV/EXPLORATORY) with strict
fallback policies, configuration validation, and environment variable parsing.

FALLBACK CATEGORIZATION AND ASSESSMENT:

CATEGORY A (CRITICAL - System Integrity):
    Variables: ALLOW_CONTRADICTION_FALLBACK, ALLOW_VALIDATOR_DISABLE, ALLOW_EXECUTION_ESTIMATES
    Assessment: These indicate missing CRITICAL components. In PROD, the system MUST fail fast
    to prevent incorrect analysis results. No fallback is acceptable.

CATEGORY B (QUALITY - Quality Degradation):
    Variables: ALLOW_NETWORKX_FALLBACK, ALLOW_SPACY_FALLBACK
    Assessment: These degrade output quality but don't invalidate core analysis. Allowed in
    PROD with explicit flag and warnings logged. Results remain scientifically valid but less rich.

CATEGORY C (DEVELOPMENT - Development Convenience):
    Variables: ALLOW_DEV_INGESTION_FALLBACKS, ALLOW_AGGREGATION_DEFAULTS, ALLOW_MISSING_BASE_WEIGHTS
    Assessment: STRICTLY FORBIDDEN in PROD. These exist only for development/testing to avoid
    infrastructure dependencies. Using these in PROD invalidates results.

CATEGORY D (OPERATIONAL - Operational Flexibility):
    Variables: ALLOW_HASH_FALLBACK, ALLOW_PDFPLUMBER_FALLBACK
    Assessment: Safe fallbacks maintaining correctness with different implementation strategies.
    Generally allowed as they don't affect scientific validity.

Environment Variables:
    SAAAAAA_RUNTIME_MODE: Runtime mode (prod/dev/exploratory), default: prod
    
    # Category A - Critical System Integrity
    ALLOW_CONTRADICTION_FALLBACK: Allow contradiction detection fallback, default: false
    ALLOW_VALIDATOR_DISABLE: Allow wiring validator disabling, default: false
    ALLOW_EXECUTION_ESTIMATES: Allow execution metric estimation, default: false
    
    # Category B - Quality Degradation
    ALLOW_NETWORKX_FALLBACK: Allow NetworkX unavailability, default: false
    ALLOW_SPACY_FALLBACK: Allow spaCy model fallback, default: false
    
    # Category C - Development Convenience (FORBIDDEN in PROD)
    ALLOW_DEV_INGESTION_FALLBACKS: Allow dev ingestion fallbacks, default: false
    ALLOW_AGGREGATION_DEFAULTS: Allow aggregation defaults, default: false
    ALLOW_MISSING_BASE_WEIGHTS: Allow missing _base_weights in calibration, default: false
    
    # Category D - Operational Flexibility
    ALLOW_HASH_FALLBACK: Allow hash algorithm fallback, default: true
    ALLOW_PDFPLUMBER_FALLBACK: Allow pdfplumber unavailability, default: false
    
    # Calibration and Quality Controls
    STRICT_CALIBRATION: Require complete calibration files, default: true
    
    # Model and Processing Configuration
    PREFERRED_SPACY_MODEL: Preferred spaCy model, default: es_core_news_lg
    PREFERRED_EMBEDDING_MODEL: Preferred embedding model, default: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    
    # Path Configuration
    SAAAAAA_PROJECT_ROOT: Project root override
    SAAAAAA_DATA_DIR: Data directory override
    SAAAAAA_OUTPUT_DIR: Output directory override
    SAAAAAA_CACHE_DIR: Cache directory override
    SAAAAAA_LOGS_DIR: Logs directory override
    
    # External Dependencies
    HF_ONLINE: Allow HuggingFace online access (0 or 1), default: 0
    
    # Processing Limits
    EXPECTED_QUESTION_COUNT: Expected question count, default: 305
    EXPECTED_METHOD_COUNT: Expected method count, default: 416
    PHASE_TIMEOUT_SECONDS: Phase timeout in seconds, default: 300
    MAX_WORKERS: Maximum worker threads, default: 4
    BATCH_SIZE: Batch size for processing, default: 100

Example:
    >>> config = RuntimeConfig.from_env()
    >>> if config.mode == RuntimeMode.PROD:
    ...     assert not config.allow_dev_ingestion_fallbacks
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Optional


class RuntimeMode(Enum):
    """Runtime execution mode with different strictness levels."""
    
    PROD = "prod"
    """Production mode: strict enforcement, no fallbacks unless explicitly allowed."""
    
    DEV = "dev"
    """Development mode: permissive with flags, allows controlled degradation."""
    
    EXPLORATORY = "exploratory"
    """Exploratory mode: maximum flexibility for research and experimentation."""


class FallbackCategory(Enum):
    """Categorization of fallback types by impact."""
    
    CRITICAL = "critical"
    """Category A: System integrity - failures indicate missing critical dependencies."""
    
    QUALITY = "quality"
    """Category B: Quality degradation - system continues with reduced quality."""
    
    DEVELOPMENT = "development"
    """Category C: Development convenience - only allowed in DEV/EXPLORATORY."""
    
    OPERATIONAL = "operational"
    """Category D: Operational flexibility - safe fallbacks for operational concerns."""


class ConfigurationError(Exception):
    """Raised when runtime configuration is invalid or contains illegal combinations."""

    def __init__(self, message: str, illegal_combo: str | None = None) -> None:
        self.illegal_combo = illegal_combo
        super().__init__(message)


@dataclass(frozen=True)
class RuntimeConfig:
    """
    Immutable runtime configuration parsed from environment variables.
    
    This configuration controls system behavior across all components, enforcing
    strict policies in PROD mode and allowing controlled degradation in DEV/EXPLORATORY.
    
    Attributes:
        mode: Runtime execution mode
        
        # Category A - Critical System Integrity
        allow_contradiction_fallback: Allow fallback when contradiction module unavailable
        allow_validator_disable: Allow disabling wiring validator
        allow_execution_estimates: Allow execution metric estimation
        
        # Category B - Quality Degradation
        allow_networkx_fallback: Allow NetworkX unavailability
        allow_spacy_fallback: Allow spaCy model fallback
        
        # Category C - Development Convenience
        allow_dev_ingestion_fallbacks: Allow development ingestion fallbacks
        allow_aggregation_defaults: Allow aggregation default values
        allow_missing_base_weights: Allow missing _base_weights in calibration
        
        # Category D - Operational Flexibility
        allow_hash_fallback: Allow hash algorithm fallback
        allow_pdfplumber_fallback: Allow pdfplumber unavailability
        
        # Calibration
        strict_calibration: Require complete calibration files with _base_weights
        
        # Model Configuration
        preferred_spacy_model: Preferred spaCy model name
        preferred_embedding_model: Preferred embedding model name
        
        # Path Configuration
        project_root_override: Project root path override
        data_dir_override: Data directory override
        output_dir_override: Output directory override
        cache_dir_override: Cache directory override
        logs_dir_override: Logs directory override
        
        # External Dependencies
        hf_online: Allow HuggingFace online access
        
        # Processing Configuration
        expected_question_count: Expected question count for validation
        expected_method_count: Expected method count for validation
        phase_timeout_seconds: Phase timeout in seconds
        max_workers: Maximum worker threads
        batch_size: Batch size for processing
    """
    
    mode: RuntimeMode
    
    # Category A - Critical
    allow_contradiction_fallback: bool
    allow_validator_disable: bool
    allow_execution_estimates: bool
    
    # Category B - Quality
    allow_networkx_fallback: bool
    allow_spacy_fallback: bool
    
    # Category C - Development
    allow_dev_ingestion_fallbacks: bool
    allow_aggregation_defaults: bool
    allow_missing_base_weights: bool
    
    # Category D - Operational
    allow_hash_fallback: bool
    allow_pdfplumber_fallback: bool
    
    # Calibration
    strict_calibration: bool
    
    # Model Configuration
    preferred_spacy_model: str
    preferred_embedding_model: str
    
    # Path Configuration
    project_root_override: Optional[str]
    data_dir_override: Optional[str]
    output_dir_override: Optional[str]
    cache_dir_override: Optional[str]
    logs_dir_override: Optional[str]
    
    # External Dependencies
    hf_online: bool
    
    # Processing Configuration
    expected_question_count: int
    expected_method_count: int
    phase_timeout_seconds: int
    max_workers: int
    batch_size: int
    
    # Illegal combinations in PROD mode
    _PROD_ILLEGAL_COMBOS: ClassVar[dict[str, tuple[str, FallbackCategory]]] = {
        "ALLOW_DEV_INGESTION_FALLBACKS": (
            "Development ingestion fallbacks not allowed in PROD - they bypass quality gates",
            FallbackCategory.DEVELOPMENT
        ),
        "ALLOW_EXECUTION_ESTIMATES": (
            "Execution metric estimation not allowed in PROD - actual measurements required",
            FallbackCategory.CRITICAL
        ),
        "ALLOW_AGGREGATION_DEFAULTS": (
            "Aggregation defaults not allowed in PROD - explicit calibration required",
            FallbackCategory.DEVELOPMENT
        ),
        "ALLOW_MISSING_BASE_WEIGHTS": (
            "Missing base weights not allowed in PROD - complete calibration required",
            FallbackCategory.DEVELOPMENT
        ),
    }
    
    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        """
        Parse runtime configuration from environment variables.
        
        Returns:
            RuntimeConfig: Validated configuration instance
            
        Raises:
            ConfigurationError: If configuration is invalid or contains illegal combinations
            
        Example:
            >>> os.environ['SAAAAAA_RUNTIME_MODE'] = 'prod'
            >>> config = RuntimeConfig.from_env()
            >>> assert config.mode == RuntimeMode.PROD
        """
        # Parse runtime mode
        mode_str = os.getenv("SAAAAAA_RUNTIME_MODE", "prod").lower()
        try:
            mode = RuntimeMode(mode_str)
        except ValueError as e:
            raise ConfigurationError(
                f"Invalid SAAAAAA_RUNTIME_MODE: {mode_str}. "
                f"Must be one of: {', '.join(m.value for m in RuntimeMode)}"
            ) from e
        
        # Parse Category A - Critical Fallbacks
        allow_contradiction_fallback = _parse_bool_env("ALLOW_CONTRADICTION_FALLBACK", False)
        allow_validator_disable = _parse_bool_env("ALLOW_VALIDATOR_DISABLE", False)
        allow_execution_estimates = _parse_bool_env("ALLOW_EXECUTION_ESTIMATES", False)
        
        # Parse Category B - Quality Fallbacks
        allow_networkx_fallback = _parse_bool_env("ALLOW_NETWORKX_FALLBACK", False)
        allow_spacy_fallback = _parse_bool_env("ALLOW_SPACY_FALLBACK", False)
        
        # Parse Category C - Development Fallbacks
        allow_dev_ingestion_fallbacks = _parse_bool_env("ALLOW_DEV_INGESTION_FALLBACKS", False)
        allow_aggregation_defaults = _parse_bool_env("ALLOW_AGGREGATION_DEFAULTS", False)
        allow_missing_base_weights = _parse_bool_env("ALLOW_MISSING_BASE_WEIGHTS", False)
        
        # Parse Category D - Operational Fallbacks
        allow_hash_fallback = _parse_bool_env("ALLOW_HASH_FALLBACK", True)
        allow_pdfplumber_fallback = _parse_bool_env("ALLOW_PDFPLUMBER_FALLBACK", False)
        
        # Parse calibration config
        strict_calibration = _parse_bool_env("STRICT_CALIBRATION", True)
        
        # Parse model configuration
        preferred_spacy_model = os.getenv("PREFERRED_SPACY_MODEL", "es_core_news_lg")
        preferred_embedding_model = os.getenv(
            "PREFERRED_EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Parse path configuration
        project_root_override = os.getenv("SAAAAAA_PROJECT_ROOT")
        data_dir_override = os.getenv("SAAAAAA_DATA_DIR")
        output_dir_override = os.getenv("SAAAAAA_OUTPUT_DIR")
        cache_dir_override = os.getenv("SAAAAAA_CACHE_DIR")
        logs_dir_override = os.getenv("SAAAAAA_LOGS_DIR")
        
        # Parse external dependencies
        hf_online = os.getenv("HF_ONLINE", "0") == "1"
        
        # Parse processing configuration
        expected_question_count = _parse_int_env("EXPECTED_QUESTION_COUNT", 305)
        expected_method_count = _parse_int_env("EXPECTED_METHOD_COUNT", 416)
        phase_timeout_seconds = _parse_int_env("PHASE_TIMEOUT_SECONDS", 300)
        max_workers = _parse_int_env("MAX_WORKERS", 4)
        batch_size = _parse_int_env("BATCH_SIZE", 100)
        
        # Create config instance
        config = cls(
            mode=mode,
            allow_contradiction_fallback=allow_contradiction_fallback,
            allow_validator_disable=allow_validator_disable,
            allow_execution_estimates=allow_execution_estimates,
            allow_networkx_fallback=allow_networkx_fallback,
            allow_spacy_fallback=allow_spacy_fallback,
            allow_dev_ingestion_fallbacks=allow_dev_ingestion_fallbacks,
            allow_aggregation_defaults=allow_aggregation_defaults,
            allow_missing_base_weights=allow_missing_base_weights,
            allow_hash_fallback=allow_hash_fallback,
            allow_pdfplumber_fallback=allow_pdfplumber_fallback,
            strict_calibration=strict_calibration,
            preferred_spacy_model=preferred_spacy_model,
            preferred_embedding_model=preferred_embedding_model,
            project_root_override=project_root_override,
            data_dir_override=data_dir_override,
            output_dir_override=output_dir_override,
            cache_dir_override=cache_dir_override,
            logs_dir_override=logs_dir_override,
            hf_online=hf_online,
            expected_question_count=expected_question_count,
            expected_method_count=expected_method_count,
            phase_timeout_seconds=phase_timeout_seconds,
            max_workers=max_workers,
            batch_size=batch_size,
        )
        
        # Validate configuration
        config._validate()
        
        return config
    
    def _validate(self) -> None:
        """
        Validate configuration for illegal combinations.
        
        In PROD mode, certain ALLOW_* flags are prohibited to ensure strict behavior.
        
        Raises:
            ConfigurationError: If illegal combination detected
        """
        if self.mode != RuntimeMode.PROD:
            return  # DEV/EXPLORATORY modes allow all combinations
        
        # Check for illegal PROD combinations
        violations = []
        
        if self.allow_dev_ingestion_fallbacks:
            msg, cat = self._PROD_ILLEGAL_COMBOS["ALLOW_DEV_INGESTION_FALLBACKS"]
            violations.append(
                f"PROD + ALLOW_DEV_INGESTION_FALLBACKS=true: {msg} [Category: {cat.value}]"
            )
        
        if self.allow_execution_estimates:
            msg, cat = self._PROD_ILLEGAL_COMBOS["ALLOW_EXECUTION_ESTIMATES"]
            violations.append(
                f"PROD + ALLOW_EXECUTION_ESTIMATES=true: {msg} [Category: {cat.value}]"
            )
        
        if self.allow_aggregation_defaults:
            msg, cat = self._PROD_ILLEGAL_COMBOS["ALLOW_AGGREGATION_DEFAULTS"]
            violations.append(
                f"PROD + ALLOW_AGGREGATION_DEFAULTS=true: {msg} [Category: {cat.value}]"
            )
        
        if self.allow_missing_base_weights:
            msg, cat = self._PROD_ILLEGAL_COMBOS["ALLOW_MISSING_BASE_WEIGHTS"]
            violations.append(
                f"PROD + ALLOW_MISSING_BASE_WEIGHTS=true: {msg} [Category: {cat.value}]"
            )
        
        if violations:
            raise ConfigurationError(
                "Illegal configuration combinations detected:\n" + "\n".join(f"  - {v}" for v in violations),
                illegal_combo="; ".join(violations)
            )
    
    def is_strict_mode(self) -> bool:
        """Check if running in strict mode (PROD with no fallbacks allowed)."""
        return (
            self.mode == RuntimeMode.PROD
            and not self.allow_contradiction_fallback
            and not self.allow_validator_disable
        )
    
    def get_fallback_summary(self) -> dict[str, dict[str, bool]]:
        """
        Get summary of all fallback configurations grouped by category.
        
        Returns:
            Dictionary mapping category names to flag dictionaries
        """
        return {
            "critical": {
                "contradiction_fallback": self.allow_contradiction_fallback,
                "validator_disable": self.allow_validator_disable,
                "execution_estimates": self.allow_execution_estimates,
            },
            "quality": {
                "networkx_fallback": self.allow_networkx_fallback,
                "spacy_fallback": self.allow_spacy_fallback,
            },
            "development": {
                "dev_ingestion_fallbacks": self.allow_dev_ingestion_fallbacks,
                "aggregation_defaults": self.allow_aggregation_defaults,
                "missing_base_weights": self.allow_missing_base_weights,
            },
            "operational": {
                "hash_fallback": self.allow_hash_fallback,
                "pdfplumber_fallback": self.allow_pdfplumber_fallback,
            },
        }
    
    def __repr__(self) -> str:
        """String representation showing mode and key flags."""
        flags = []
        if self.allow_contradiction_fallback:
            flags.append("contradiction_fallback")
        if self.allow_validator_disable:
            flags.append("validator_disable")
        if self.allow_execution_estimates:
            flags.append("execution_estimates")
        if self.allow_networkx_fallback:
            flags.append("networkx_fallback")
        if self.allow_spacy_fallback:
            flags.append("spacy_fallback")
        if self.allow_dev_ingestion_fallbacks:
            flags.append("dev_ingestion_fallbacks")
        if self.allow_aggregation_defaults:
            flags.append("aggregation_defaults")
        if self.allow_missing_base_weights:
            flags.append("missing_base_weights")
        if not self.strict_calibration:
            flags.append("relaxed_calibration")
        
        flags_str = f", flags={flags}" if flags else ""
        return f"RuntimeConfig(mode={self.mode.value}{flags_str})"


def _parse_bool_env(var_name: str, default: bool) -> bool:
    """
    Parse boolean environment variable with case-insensitive handling.
    
    Args:
        var_name: Environment variable name
        default: Default value if not set
        
    Returns:
        Parsed boolean value
        
    Raises:
        ConfigurationError: If value is not a valid boolean
    """
    value = os.getenv(var_name)
    if value is None:
        return default
    
    value_lower = value.lower()
    if value_lower in ("true", "1", "yes", "on"):
        return True
    elif value_lower in ("false", "0", "no", "off"):
        return False
    else:
        raise ConfigurationError(
            f"Invalid boolean value for {var_name}: {value}. "
            f"Must be one of: true/false, 1/0, yes/no, on/off"
        )


def _parse_int_env(var_name: str, default: int) -> int:
    """
    Parse integer environment variable with validation.
    
    Args:
        var_name: Environment variable name
        default: Default value if not set
        
    Returns:
        Parsed integer value
        
    Raises:
        ConfigurationError: If value is not a valid integer
    """
    value = os.getenv(var_name)
    if value is None:
        return default
    
    try:
        return int(value)
    except ValueError:
        raise ConfigurationError(
            f"Invalid integer value for {var_name}: {value}. "
            f"Must be a valid integer."
        )


# Global singleton instance (lazy-initialized)
_global_config: RuntimeConfig | None = None


def get_runtime_config() -> RuntimeConfig:
    """
    Get global runtime configuration instance (lazy-initialized).
    
    Returns:
        RuntimeConfig: Global configuration instance
        
    Note:
        This is initialized once on first call. For testing, use from_env() directly.
    """
    global _global_config
    if _global_config is None:
        _global_config = RuntimeConfig.from_env()
    return _global_config


def reset_runtime_config() -> None:
    """
    Reset global runtime configuration (for testing only).
    
    Warning:
        This should only be used in tests. Production code should never reset config.
    """
    global _global_config
    _global_config = None
