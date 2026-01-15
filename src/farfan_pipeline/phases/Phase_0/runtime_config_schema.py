"""Pydantic schema for runtime configuration (compatibility with legacy imports)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from farfan_pipeline.phases.Phase_0.phase0_10_01_runtime_config import RuntimeMode


class RuntimeConfigSchema(BaseModel):
    """Runtime configuration with PROD-mode enforcement."""

    mode: RuntimeMode = RuntimeMode.PROD

    # Category A - Critical
    allow_contradiction_fallback: bool = False
    allow_validator_disable: bool = False
    allow_execution_estimates: bool = False

    # Category B - Quality
    allow_networkx_fallback: bool = False
    allow_spacy_fallback: bool = False

    # Category C - Development
    allow_dev_ingestion_fallbacks: bool = False
    allow_aggregation_defaults: bool = False
    allow_missing_base_weights: bool = False

    # Category D - Operational
    allow_hash_fallback: bool = True
    allow_pdfplumber_fallback: bool = False

    # Processing configuration
    expected_question_count: int = Field(default=305)
    expected_method_count: int = Field(default=416)
    phase_timeout_seconds: int = Field(default=300)
    max_workers: int = Field(default=4)
    batch_size: int = Field(default=100)

    @field_validator("expected_question_count")
    @classmethod
    def _validate_expected_question_count(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("expected_question_count must be positive")
        return value

    @field_validator("expected_method_count")
    @classmethod
    def _validate_expected_method_count(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("expected_method_count must be positive")
        return value

    @field_validator("phase_timeout_seconds")
    @classmethod
    def _validate_phase_timeout(cls, value: int) -> int:
        if value < 10:
            raise ValueError("phase_timeout_seconds must be at least 10")
        return value

    @field_validator("max_workers")
    @classmethod
    def _validate_max_workers(cls, value: int) -> int:
        if not 1 <= value <= 64:
            raise ValueError("max_workers must be between 1 and 64")
        return value

    @field_validator("batch_size")
    @classmethod
    def _validate_batch_size(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("batch_size must be positive")
        return value

    @model_validator(mode="after")
    def _enforce_prod_mode(self) -> "RuntimeConfigSchema":
        if self.mode == RuntimeMode.PROD:
            forbidden_flags = (
                self.allow_dev_ingestion_fallbacks
                or self.allow_execution_estimates
                or self.allow_aggregation_defaults
                or self.allow_missing_base_weights
            )
            if forbidden_flags:
                raise ValueError("PROD mode forbids development fallbacks")
        return self


__all__ = ["RuntimeConfigSchema", "RuntimeMode"]
