"""Pydantic schema for RuntimeConfig with strict PROD mode validation."""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 0
__stage__ = 10
__order__ = 3
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"



from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RuntimeMode(str, Enum):
    PROD = "prod"
    DEV = "dev"
    EXPLORATORY = "exploratory"


class RuntimeConfigSchema(BaseModel):
    """Pydantic-validated RuntimeConfig with PROD mode enforcement."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        extra="forbid",
    )

    mode: RuntimeMode = Field(default=RuntimeMode.DEV)

    # Category A - Critical System Integrity
    allow_contradiction_fallback: bool = Field(default=False)
    allow_validator_disable: bool = Field(default=False)
    allow_execution_estimates: bool = Field(default=False)

    # Category B - Quality Degradation
    allow_networkx_fallback: bool = Field(default=False)
    allow_spacy_fallback: bool = Field(default=False)

    # Category C - Development Convenience
    allow_dev_ingestion_fallbacks: bool = Field(default=False)
    allow_aggregation_defaults: bool = Field(default=False)
    allow_missing_base_weights: bool = Field(default=False)

    # Category D - Operational Flexibility
    allow_hash_fallback: bool = Field(default=True)
    allow_pdfplumber_fallback: bool = Field(default=False)

    # Model and Processing Configuration
    preferred_spacy_model: str = Field(default="es_core_news_lg")
    preferred_embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Path Configuration
    project_root_override: str | None = Field(default=None)
    data_dir_override: str | None = Field(default=None)
    output_dir_override: str | None = Field(default=None)
    cache_dir_override: str | None = Field(default=None)
    logs_dir_override: str | None = Field(default=None)

    # External Dependencies
    hf_online: bool = Field(default=False)

    # Processing Configuration
    expected_question_count: int = Field(default=305, ge=1, le=10000)
    expected_method_count: int = Field(default=416, ge=1, le=10000)
    phase_timeout_seconds: int = Field(default=300, ge=10, le=7200)
    max_workers: int = Field(default=4, ge=1, le=64)
    batch_size: int = Field(default=100, ge=1, le=10000)

    # Illegal PROD combinations
    _PROD_FORBIDDEN: ClassVar[set[str]] = {
        "allow_dev_ingestion_fallbacks",
        "allow_execution_estimates",
        "allow_aggregation_defaults",
        "allow_missing_base_weights",
    }

    @model_validator(mode="after")
    def validate_prod_constraints(self) -> RuntimeConfigSchema:
        """Enforce PROD mode constraints."""
        if self.mode == RuntimeMode.PROD:
            violations = []
            for field_name in self._PROD_FORBIDDEN:
                if getattr(self, field_name, False):
                    violations.append(field_name)
            if violations:
                raise ValueError(
                    f"PROD mode forbids: {', '.join(violations)}. "
                    "These fallbacks bypass quality gates."
                )
        return self

    @model_validator(mode="after")
    def validate_processing_config(self) -> RuntimeConfigSchema:
        """Validate processing configuration parameters."""
        if self.expected_question_count <= 0:
            raise ValueError("expected_question_count must be positive")

        if self.expected_method_count <= 0:
            raise ValueError("expected_method_count must be positive")

        if self.phase_timeout_seconds < 10:
            raise ValueError("phase_timeout_seconds must be at least 10")

        if self.max_workers < 1 or self.max_workers > 64:
            raise ValueError("max_workers must be between 1 and 64")

        if self.batch_size < 1:
            raise ValueError("batch_size must be positive")

        return self
