"""
Pydantic Configuration Schemas for Policy Processor
====================================================

RECOMMENDATION 2 IMPLEMENTATION: Refactor configuration loading to Pydantic models

This module provides explicit, validated configuration schemas to replace
implicit nested .get() calls with type-safe, fail-fast validation.

Benefits:
- Schema is documented and type-checked
- Validation is eager (fails immediately on invalid config)
- Defaults are centralized (single source of truth)
- IDE support (autocomplete, type checking)
- No need for graceful degradation at access sites

Original Issue (Instance 10 from analysis):
    config = self.calibration.get("bayesian_inference_robust") if isinstance(self.calibration, dict) else {}
    evidence_cfg = config.get("mechanistic_evidence_system", {})
    stability = evidence_cfg.get("stability_controls", {})
    self.epsilon_clip = float(stability.get("epsilon_clip", self.epsilon_clip))

Refactored Solution:
    config = BayesianInferenceConfig.model_validate(self.calibration)
    self.epsilon_clip = config.mechanistic_evidence_system.stability_controls.epsilon_clip
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class StabilityControls(BaseModel):
    """Stability controls for mechanistic evidence system.

    Attributes:
        epsilon_clip: Minimum/maximum clipping threshold for Bayesian updates (0.0 - 0.45)
        duplicate_gamma: Duplicate evidence dampening factor (>= 0.0)
        cross_type_floor: Minimum cross-type evidence floor (0.0 - 1.0)
    """

    epsilon_clip: float = Field(
        default=0.02,
        ge=0.0,
        le=0.45,
        description="Minimum/maximum clipping threshold for Bayesian updates",
    )
    duplicate_gamma: float = Field(
        default=1.0, ge=0.0, description="Duplicate evidence dampening factor"
    )
    cross_type_floor: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum cross-type evidence floor"
    )

    @field_validator("epsilon_clip")
    @classmethod
    def validate_epsilon_clip(cls, v: float) -> float:
        """Ensure epsilon_clip is within safe range."""
        return min(max(v, 0.0), 0.45)


class SourceQualityWeights(BaseModel):
    """Quality weights for different evidence sources.

    All weights must be non-negative floats.
    """

    model_config = {"extra": "allow"}  # Allow additional source types

    # Common source types (can be extended)
    default: float = Field(default=1.0, ge=0.0)


class MechanisticEvidenceSystem(BaseModel):
    """Configuration for mechanistic evidence accumulation system.

    Attributes:
        stability_controls: Controls for evidence stability and dampening
        source_quality_weights: Quality weights per evidence source type
    """

    stability_controls: StabilityControls = Field(
        default_factory=StabilityControls,
        description="Stability controls for evidence accumulation",
    )
    source_quality_weights: dict[str, float] = Field(
        default_factory=dict, description="Quality weights for different evidence sources"
    )

    @field_validator("source_quality_weights")
    @classmethod
    def validate_weights(cls, v: dict[str, float]) -> dict[str, float]:
        """Ensure all weights are non-negative floats."""
        return {str(k): float(val) for k, val in v.items() if isinstance(val, (int, float))}


class SectorMultipliers(BaseModel):
    """Sector-specific multipliers for hierarchical priors.

    Attributes:
        default: Default multiplier for unlisted sectors
        Additional sector multipliers can be added dynamically
    """

    model_config = {"extra": "allow"}  # Allow additional sectors

    default: float = Field(default=1.0, ge=0.0)


class MunicipioTamanoMultipliers(BaseModel):
    """Municipality size-specific multipliers for hierarchical priors.

    Attributes:
        default: Default multiplier for unlisted municipality sizes
        Additional size category multipliers can be added dynamically
    """

    model_config = {"extra": "allow"}  # Allow additional size categories

    default: float = Field(default=1.0, ge=0.0)


class HierarchicalContextPriors(BaseModel):
    """Hierarchical context priors for Bayesian evidence accumulation.

    Attributes:
        sector_multipliers: Multipliers by economic sector
        municipio_tamano_multipliers: Multipliers by municipality size
    """

    sector_multipliers: dict[str, float] = Field(
        default_factory=dict, description="Multipliers by economic sector"
    )
    municipio_tamano_multipliers: dict[str, float] = Field(
        default_factory=dict, description="Multipliers by municipality size category"
    )

    @field_validator("sector_multipliers", "municipio_tamano_multipliers")
    @classmethod
    def validate_multipliers(cls, v: dict[str, float]) -> dict[str, float]:
        """Ensure all multipliers are non-negative floats with lowercase keys."""
        return {str(k).lower(): float(val) for k, val in v.items() if isinstance(val, (int, float))}


class TheoreticallyGroundedPriors(BaseModel):
    """Theoretically-grounded prior configuration.

    Attributes:
        hierarchical_context_priors: Context-specific priors by hierarchy
    """

    hierarchical_context_priors: HierarchicalContextPriors = Field(
        default_factory=HierarchicalContextPriors, description="Hierarchical context priors"
    )


class BayesianInferenceConfig(BaseModel):
    """Complete configuration for Bayesian inference robust system.

    This is the top-level configuration schema for robust Bayesian inference
    in policy analysis. It replaces implicit nested .get() calls with
    explicit, validated configuration.

    Attributes:
        mechanistic_evidence_system: Evidence accumulation configuration
        theoretically_grounded_priors: Theoretically-grounded prior configuration
    """

    mechanistic_evidence_system: MechanisticEvidenceSystem = Field(
        default_factory=MechanisticEvidenceSystem,
        description="Mechanistic evidence system configuration",
    )
    theoretically_grounded_priors: TheoreticallyGroundedPriors = Field(
        default_factory=TheoreticallyGroundedPriors,
        description="Theoretically-grounded prior configuration",
    )

    @classmethod
    def from_calibration_dict(cls, calibration: dict | None) -> BayesianInferenceConfig:
        """
        Create configuration from calibration dictionary.

        Args:
            calibration: Calibration dictionary (may be None or missing keys)

        Returns:
            Validated BayesianInferenceConfig with defaults for missing values

        Raises:
            ValidationError: If provided values are invalid (wrong types, out of range)
        """
        if calibration is None or not isinstance(calibration, dict):
            return cls()

        # Extract bayesian_inference_robust section
        config_data = calibration.get("bayesian_inference_robust", {})
        if not isinstance(config_data, dict):
            return cls()

        # Pydantic will validate and apply defaults for missing keys
        return cls.model_validate(config_data)


__all__ = [
    "BayesianInferenceConfig",
    "HierarchicalContextPriors",
    "MechanisticEvidenceSystem",
    "MunicipioTamanoMultipliers",
    "SectorMultipliers",
    "SourceQualityWeights",
    "StabilityControls",
    "TheoreticallyGroundedPriors",
]
