"""
Type-Level Enforcement for Runtime Configuration
=================================================

RECOMMENDATION 3 IMPLEMENTATION: Enforce build-time separation for critical fallbacks

This module provides separate type classes for PROD vs DEV configurations,
using Literal types to enforce restrictions at the type-checker level.

Problem (from analysis Instance 11):
    Current RuntimeConfig allows runtime checking for illegal combinations:
    ```python
    if config.mode == RuntimeMode.PROD and config.allow_dev_ingestion_fallbacks:
        raise ConfigurationError("DEV fallbacks forbidden in PROD")
    ```

    This is runtime enforcement - errors only caught when code runs.

Solution:
    Use separate types with Literal annotations:
    ```python
    @dataclass(frozen=True)
    class ProdRuntimeConfig:
        allow_contradiction_fallback: Literal[False] = False  # Type enforced!
        allow_validator_disable: Literal[False] = False
        allow_dev_ingestion_fallbacks: Literal[False] = False
    ```

    Type checker (mypy) will catch violations at check-time, not runtime.

Benefits:
- Impossible to accidentally enable DEV fallbacks in PROD build
- Type checker prevents misconfiguration
- Self-documenting intent
- Errors caught during development, not deployment

Categorization (from phase0_10_01_runtime_config.py):
- Category A (CRITICAL): Must be False in PROD, type-enforced
- Category B (QUALITY): Can vary in PROD, runtime-configurable
- Category C (DEVELOPMENT): Must be False in PROD, type-enforced
- Category D (OPERATIONAL): Can vary in PROD, runtime-configurable
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 0
__stage__ = 10
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import os
from dataclasses import dataclass
from typing import Literal

from .phase0_10_01_runtime_config import (
    ConfigurationError,
    RuntimeMode,
)

# ====================================================================================
# PROD CONFIGURATION - Type-Level Enforcement of Critical Constraints
# ====================================================================================


@dataclass(frozen=True)
class ProdRuntimeConfig:
    """
    Production runtime configuration with type-level enforcement.

    Category A (CRITICAL) and Category C (DEVELOPMENT) flags are type-enforced
    to Literal[False], making it impossible to enable them in PROD.

    Category B (QUALITY) and Category D (OPERATIONAL) remain runtime-configurable
    as they represent legitimate policy trade-offs.

    Attributes:
        mode: Always RuntimeMode.PROD (type-enforced)

        # Category A - Critical (TYPE-ENFORCED: Must be False)
        allow_contradiction_fallback: Type-enforced to False
        allow_validator_disable: Type-enforced to False
        allow_execution_estimates: Type-enforced to False

        # Category C - Development (TYPE-ENFORCED: Must be False)
        allow_dev_ingestion_fallbacks: Type-enforced to False
        allow_aggregation_defaults: Type-enforced to False
        allow_missing_base_weights: Type-enforced to False

        # Category B - Quality (RUNTIME-CONFIGURABLE: Policy decision)
        allow_networkx_fallback: Can be True if user accepts quality reduction
        allow_spacy_fallback: Can be True if user accepts quality reduction

        # Category D - Operational (RUNTIME-CONFIGURABLE: Platform compatibility)
        allow_hash_fallback: Defaults to True (safe fallback)
        allow_pdfplumber_fallback: Can be True for platform compatibility

        # Other configuration (same as RuntimeConfig)
        preferred_spacy_model: Preferred spaCy model name
        preferred_embedding_model: Preferred embedding model name
        project_root_override: Optional project root override
        data_dir_override: Optional data directory override
        output_dir_override: Optional output directory override
        cache_dir_override: Optional cache directory override
        logs_dir_override: Optional logs directory override
        hf_online: Allow HuggingFace online access
        expected_question_count: Expected question count
        expected_method_count: Expected method count
        phase_timeout_seconds: Phase timeout in seconds
        max_workers: Maximum worker threads
        batch_size: Batch size for processing
    """

    # Mode is type-enforced to PROD
    mode: Literal[RuntimeMode.PROD] = RuntimeMode.PROD

    # Category A - Critical System Integrity (TYPE-ENFORCED TO FALSE)
    allow_contradiction_fallback: Literal[False] = False
    allow_validator_disable: Literal[False] = False
    allow_execution_estimates: Literal[False] = False

    # Category C - Development Convenience (TYPE-ENFORCED TO FALSE)
    allow_dev_ingestion_fallbacks: Literal[False] = False
    allow_aggregation_defaults: Literal[False] = False
    allow_missing_base_weights: Literal[False] = False

    # Category B - Quality Degradation (RUNTIME-CONFIGURABLE)
    allow_networkx_fallback: bool = False
    allow_spacy_fallback: bool = False

    # Category D - Operational Flexibility (RUNTIME-CONFIGURABLE)
    allow_hash_fallback: bool = True
    allow_pdfplumber_fallback: bool = False

    # Model Configuration
    preferred_spacy_model: str = "es_core_news_lg"
    preferred_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # Path Configuration
    project_root_override: str | None = None
    data_dir_override: str | None = None
    output_dir_override: str | None = None
    cache_dir_override: str | None = None
    logs_dir_override: str | None = None

    # External Dependencies
    hf_online: bool = False

    # Processing Configuration
    expected_question_count: int = 305
    expected_method_count: int = 416
    phase_timeout_seconds: int = 300
    max_workers: int = 4
    batch_size: int = 100

    @classmethod
    def from_env(cls) -> ProdRuntimeConfig:
        """
        Parse PROD configuration from environment variables.

        Category A/C flags are ignored even if set in environment - they're
        type-enforced to False. Attempting to enable them will be caught by
        the type checker during development.

        Returns:
            ProdRuntimeConfig with Category B/D configured from environment

        Example:
            >>> os.environ['ALLOW_SPACY_FALLBACK'] = 'true'  # Category B - allowed
            >>> config = ProdRuntimeConfig.from_env()
            >>> assert config.allow_spacy_fallback is True  # Works
            >>>
            >>> # Type checker prevents this at development time:
            >>> bad_config = ProdRuntimeConfig(allow_dev_ingestion_fallbacks=True)
            >>> # mypy error: Literal[False] is not compatible with bool
        """

        def parse_bool(key: str, default: bool) -> bool:
            return os.getenv(key, str(default)).lower() in ("true", "1", "yes")

        return cls(
            # Category B - Quality (runtime-configurable)
            allow_networkx_fallback=parse_bool("ALLOW_NETWORKX_FALLBACK", False),
            allow_spacy_fallback=parse_bool("ALLOW_SPACY_FALLBACK", False),
            # Category D - Operational (runtime-configurable)
            allow_hash_fallback=parse_bool("ALLOW_HASH_FALLBACK", True),
            allow_pdfplumber_fallback=parse_bool("ALLOW_PDFPLUMBER_FALLBACK", False),
            # Model Configuration
            preferred_spacy_model=os.getenv("PREFERRED_SPACY_MODEL", "es_core_news_lg"),
            preferred_embedding_model=os.getenv(
                "PREFERRED_EMBEDDING_MODEL",
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            ),
            # Path Configuration
            project_root_override=os.getenv("FARFAN_PROJECT_ROOT"),
            data_dir_override=os.getenv("FARFAN_DATA_DIR"),
            output_dir_override=os.getenv("FARFAN_OUTPUT_DIR"),
            cache_dir_override=os.getenv("FARFAN_CACHE_DIR"),
            logs_dir_override=os.getenv("FARFAN_LOGS_DIR"),
            # External Dependencies
            hf_online=parse_bool("HF_ONLINE", False),
            # Processing Configuration
            expected_question_count=int(os.getenv("EXPECTED_QUESTION_COUNT", "305")),
            expected_method_count=int(os.getenv("EXPECTED_METHOD_COUNT", "416")),
            phase_timeout_seconds=int(os.getenv("PHASE_TIMEOUT_SECONDS", "300")),
            max_workers=int(os.getenv("MAX_WORKERS", "4")),
            batch_size=int(os.getenv("BATCH_SIZE", "100")),
        )


# ====================================================================================
# DEV CONFIGURATION - Permissive Configuration for Development
# ====================================================================================


@dataclass(frozen=True)
class DevRuntimeConfig:
    """
    Development runtime configuration with permissive settings.

    All flags can be configured at runtime for maximum development flexibility.
    Category A/C flags are allowed to be True for development convenience.

    Attributes:
        mode: Always RuntimeMode.DEV or RuntimeMode.EXPLORATORY

        # Category A/C - Can be True in DEV for testing
        allow_contradiction_fallback: Allowed to vary in DEV
        allow_validator_disable: Allowed to vary in DEV
        allow_execution_estimates: Allowed to vary in DEV
        allow_dev_ingestion_fallbacks: Allowed to vary in DEV
        allow_aggregation_defaults: Allowed to vary in DEV
        allow_missing_base_weights: Allowed to vary in DEV

        # Category B/D - Same as PROD (runtime-configurable)
        allow_networkx_fallback: Allowed to vary
        allow_spacy_fallback: Allowed to vary
        allow_hash_fallback: Allowed to vary
        allow_pdfplumber_fallback: Allowed to vary

        # Other configuration (same as ProdRuntimeConfig)
    """

    # Mode can be DEV or EXPLORATORY
    mode: RuntimeMode = RuntimeMode.DEV

    # All flags can vary in DEV
    # Category A - Critical
    allow_contradiction_fallback: bool = False
    allow_validator_disable: bool = False
    allow_execution_estimates: bool = False

    # Category B - Quality
    allow_networkx_fallback: bool = False
    allow_spacy_fallback: bool = False

    # Category C - Development
    allow_dev_ingestion_fallbacks: bool = True  # Default True in DEV
    allow_aggregation_defaults: bool = True  # Default True in DEV
    allow_missing_base_weights: bool = True  # Default True in DEV

    # Category D - Operational
    allow_hash_fallback: bool = True
    allow_pdfplumber_fallback: bool = False

    # Model Configuration
    preferred_spacy_model: str = "es_core_news_lg"
    preferred_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # Path Configuration
    project_root_override: str | None = None
    data_dir_override: str | None = None
    output_dir_override: str | None = None
    cache_dir_override: str | None = None
    logs_dir_override: str | None = None

    # External Dependencies
    hf_online: bool = False

    # Processing Configuration
    expected_question_count: int = 305
    expected_method_count: int = 416
    phase_timeout_seconds: int = 300
    max_workers: int = 4
    batch_size: int = 100

    @classmethod
    def from_env(cls, mode: RuntimeMode = RuntimeMode.DEV) -> DevRuntimeConfig:
        """
        Parse DEV configuration from environment variables.

        All flags can be configured from environment in DEV mode.

        Args:
            mode: Runtime mode (DEV or EXPLORATORY)

        Returns:
            DevRuntimeConfig with all flags configurable
        """
        if mode not in (RuntimeMode.DEV, RuntimeMode.EXPLORATORY):
            raise ConfigurationError(
                f"DevRuntimeConfig requires DEV or EXPLORATORY mode, got {mode}"
            )

        def parse_bool(key: str, default: bool) -> bool:
            return os.getenv(key, str(default)).lower() in ("true", "1", "yes")

        return cls(
            mode=mode,
            # Category A - Critical (allowed in DEV)
            allow_contradiction_fallback=parse_bool("ALLOW_CONTRADICTION_FALLBACK", False),
            allow_validator_disable=parse_bool("ALLOW_VALIDATOR_DISABLE", False),
            allow_execution_estimates=parse_bool("ALLOW_EXECUTION_ESTIMATES", False),
            # Category B - Quality
            allow_networkx_fallback=parse_bool("ALLOW_NETWORKX_FALLBACK", False),
            allow_spacy_fallback=parse_bool("ALLOW_SPACY_FALLBACK", False),
            # Category C - Development (allowed in DEV, default True)
            allow_dev_ingestion_fallbacks=parse_bool("ALLOW_DEV_INGESTION_FALLBACKS", True),
            allow_aggregation_defaults=parse_bool("ALLOW_AGGREGATION_DEFAULTS", True),
            allow_missing_base_weights=parse_bool("ALLOW_MISSING_BASE_WEIGHTS", True),
            # Category D - Operational
            allow_hash_fallback=parse_bool("ALLOW_HASH_FALLBACK", True),
            allow_pdfplumber_fallback=parse_bool("ALLOW_PDFPLUMBER_FALLBACK", False),
            # Model Configuration
            preferred_spacy_model=os.getenv("PREFERRED_SPACY_MODEL", "es_core_news_lg"),
            preferred_embedding_model=os.getenv(
                "PREFERRED_EMBEDDING_MODEL",
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            ),
            # Path Configuration
            project_root_override=os.getenv("FARFAN_PROJECT_ROOT"),
            data_dir_override=os.getenv("FARFAN_DATA_DIR"),
            output_dir_override=os.getenv("FARFAN_OUTPUT_DIR"),
            cache_dir_override=os.getenv("FARFAN_CACHE_DIR"),
            logs_dir_override=os.getenv("FARFAN_LOGS_DIR"),
            # External Dependencies
            hf_online=parse_bool("HF_ONLINE", False),
            # Processing Configuration
            expected_question_count=int(os.getenv("EXPECTED_QUESTION_COUNT", "305")),
            expected_method_count=int(os.getenv("EXPECTED_METHOD_COUNT", "416")),
            phase_timeout_seconds=int(os.getenv("PHASE_TIMEOUT_SECONDS", "300")),
            max_workers=int(os.getenv("MAX_WORKERS", "4")),
            batch_size=int(os.getenv("BATCH_SIZE", "100")),
        )


# ====================================================================================
# FACTORY FUNCTION - Mode-Aware Configuration Creation
# ====================================================================================


def create_runtime_config_typed(
    mode: RuntimeMode | None = None,
) -> ProdRuntimeConfig | DevRuntimeConfig:
    """
    Factory function to create appropriate typed configuration based on mode.

    Args:
        mode: Runtime mode (defaults to environment variable FARFAN_RUNTIME_MODE)

    Returns:
        ProdRuntimeConfig for PROD mode
        DevRuntimeConfig for DEV/EXPLORATORY modes

    Example:
        >>> os.environ['FARFAN_RUNTIME_MODE'] = 'prod'
        >>> config = create_runtime_config_typed()
        >>> assert isinstance(config, ProdRuntimeConfig)
        >>> # Type checker knows config.allow_dev_ingestion_fallbacks is False
    """
    if mode is None:
        mode_str = os.getenv("FARFAN_RUNTIME_MODE", "prod").lower()
        try:
            mode = RuntimeMode(mode_str)
        except ValueError:
            mode = RuntimeMode.PROD

    if mode == RuntimeMode.PROD:
        return ProdRuntimeConfig.from_env()
    else:
        return DevRuntimeConfig.from_env(mode)


__all__ = [
    "DevRuntimeConfig",
    "ProdRuntimeConfig",
    "create_runtime_config_typed",
]
