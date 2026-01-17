"""
Choquet Aggregator - Non-linear Multi-Layer Calibration Aggregation

This module implements the Choquet integral for aggregating multi-layer calibration
scores with interaction terms. The Choquet aggregator captures synergies and
complementarities between layers that simple weighted averages cannot represent. 

Formula: 
    Cal(I) = Σ(aₗ·xₗ) + Σ(aₗₖ·min(xₗ,xₖ))

Where:
    - xₗ:  Score for layer l (normalized to [0,1])
    - aₗ: Linear weight for layer l
    - aₗₖ: Interaction weight for layer pair (l,k)
    - Cal(I): Choquet-aggregated calibration score ∈ [0,1]

Architecture:
    - ChoquetConfig: Configuration with linear and interaction weights
    - ChoquetAggregator: Main aggregation engine
    - CalibrationResult: Output with score breakdown and rationales

Requirements:
    - Boundedness: 0.0 ≤ Cal(I) ≤ 1.0 (enforced via validation)
    - Monotonicity: Higher layer scores → higher aggregate score
    - Normalization:  Weights normalized to ensure boundedness
    - Determinism: Fixed random seeds for reproducible results

Note:
    The weights in this module are BUSINESS/PRESENTATION CONSTANTS, not epistemic
    parameters. They should NOT be included in any parameterization system for
    Phase 4. See README Section 10.4 for rationale. 

Author: F. A. R.F. A.N.  Core Team
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 4
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A. N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
from dataclasses import dataclass, field
from typing import Final

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS - BUSINESS/PRESENTATION (NOT EPISTEMIC PARAMETERS)
# =============================================================================

# These are fixed business constants, not tunable parameters. 
# DO NOT create a parameterization system for these values.

DEFAULT_BOUNDEDNESS_LOWER:  Final[float] = 0.0
DEFAULT_BOUNDEDNESS_UPPER: Final[float] = 1.0
INTERACTION_WEIGHT_MAX_RATIO: Final[float] = 0.5  # Max interaction as fraction of linear
WEIGHT_NORMALIZATION_EPSILON: Final[float] = 1e-12


# =============================================================================
# EXCEPTIONS
# =============================================================================


class CalibrationConfigError(Exception):
    """Raised when calibration configuration validation fails."""

    pass


class BoundednessViolationError(CalibrationConfigError):
    """Raised when computed calibration score violates [0,1] bounds."""

    pass


class MissingLayerError(ValueError):
    """Raised when required layers are missing from input scores."""

    pass


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass(frozen=True)
class ChoquetConfig:
    """
    Configuration for Choquet aggregation with interaction terms.

    Attributes:
        linear_weights: Dictionary mapping layer_id -> linear weight (aₗ)
        interaction_weights:  Dictionary mapping (layer_i, layer_j) -> interaction weight (aₗₖ)
        validate_boundedness: Whether to validate that Cal(I) ∈ [0,1]
        normalize_weights: Whether to normalize weights automatically

    Note:
        These weights are BUSINESS CONSTANTS.  They represent fixed domain-specific
        importance factors, NOT epistemic parameters to be tuned or learned. 

    Example:
        >>> config = ChoquetConfig(
        ...     linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.2},
        ...     interaction_weights={("@b", "@chain"): 0.1},
        ...     validate_boundedness=True
        ... )
    """

    linear_weights: dict[str, float]
    interaction_weights: dict[tuple[str, str], float] = field(default_factory=dict)
    validate_boundedness: bool = True
    normalize_weights:  bool = True

    def __post_init__(self) -> None:
        """Validate configuration on construction."""
        self._validate_linear_weights()
        self._validate_interaction_weights()

    def _validate_linear_weights(self) -> None:
        """Validate linear weights structure and values."""
        if not self.linear_weights:
            raise CalibrationConfigError("linear_weights cannot be empty")

        for layer_id, weight in self.linear_weights.items():
            if not isinstance(layer_id, str):
                raise CalibrationConfigError(
                    f"Layer ID must be string, got {type(layer_id).__name__}:  {layer_id!r}"
                )
            if not isinstance(weight, (int, float)):
                raise CalibrationConfigError(
                    f"Weight must be numeric, got {type(weight).__name__} for layer {layer_id!r}"
                )
            if weight < 0.0:
                raise CalibrationConfigError(
                    f"Negative linear weight not allowed:  {layer_id}={weight}"
                )

    def _validate_interaction_weights(self) -> None:
        """Validate interaction weights structure and layer references."""
        for (layer_i, layer_j), weight in self.interaction_weights.items():
            if not isinstance(layer_i, str) or not isinstance(layer_j, str):
                raise CalibrationConfigError(
                    f"Layer IDs in interaction must be strings:  ({layer_i!r}, {layer_j!r})"
                )
            if not isinstance(weight, (int, float)):
                raise CalibrationConfigError(
                    f"Interaction weight must be numeric:  ({layer_i}, {layer_j})={weight!r}"
                )
            # Note: Negative interaction weights ARE allowed (substitution effects).
            # See README Section 10.4. 
            if layer_i not in self.linear_weights:
                raise CalibrationConfigError(
                    f"Interaction layer {layer_i!r} not found in linear_weights.  "
                    f"Available:  {set(self.linear_weights.keys())}"
                )
            if layer_j not in self.linear_weights:
                raise CalibrationConfigError(
                    f"Interaction layer {layer_j!r} not found in linear_weights. "
                    f"Available: {set(self.linear_weights. keys())}"
                )

    @property
    def layer_ids(self) -> frozenset[str]: 
        """Return immutable set of all layer IDs."""
        return frozenset(self.linear_weights.keys())

    @property
    def n_layers(self) -> int:
        """Return number of layers."""
        return len(self.linear_weights)

    @property
    def n_interactions(self) -> int:
        """Return number of interaction pairs."""
        return len(self. interaction_weights)

    def has_interactions(self) -> bool:
        """Check if configuration includes interaction terms."""
        return len(self.interaction_weights) > 0


@dataclass(frozen=True)
class CalibrationBreakdown:
    """
    Detailed breakdown of Choquet aggregation computation.

    Attributes:
        linear_contribution: Total contribution from linear terms Σ(aₗ·xₗ)
        interaction_contribution: Total contribution from interaction terms Σ(aₗₖ·min(xₗ,xₖ))
        per_layer_contributions:  Dictionary mapping layer_id -> aₗ·xₗ
        per_interaction_contributions: Dictionary mapping (layer_i, layer_j) -> aₗₖ·min(xₗ,xₖ)
        per_layer_rationales: Dictionary mapping layer_id -> human-readable rationale
        per_interaction_rationales: Dictionary mapping (layer_i, layer_j) -> rationale
    """

    linear_contribution: float
    interaction_contribution:  float
    per_layer_contributions: dict[str, float]
    per_interaction_contributions: dict[tuple[str, str], float]
    per_layer_rationales: dict[str, str]
    per_interaction_rationales: dict[tuple[str, str], str]

    @property
    def total_contribution(self) -> float:
        """Return total contribution (linear + interaction)."""
        return self.linear_contribution + self.interaction_contribution

    def get_dominant_layer(self) -> tuple[str, float] | None:
        """Return the layer with highest contribution, or None if empty."""
        if not self.per_layer_contributions:
            return None
        max_layer = max(self. per_layer_contributions.items(), key=lambda x: x[1])
        return max_layer

    def get_dominant_interaction(self) -> tuple[tuple[str, str], float] | None: 
        """Return the interaction pair with highest contribution, or None if empty."""
        if not self.per_interaction_contributions:
            return None
        max_interaction = max(self.per_interaction_contributions.items(), key=lambda x:  abs(x[1]))
        return max_interaction

    def summary(self) -> str:
        """Generate human-readable summary of breakdown."""
        lines = [
            f"Linear Contribution: {self.linear_contribution:. 4f}",
            f"Interaction Contribution: {self.interaction_contribution:. 4f}",
            f"Total:  {self.total_contribution:.4f}",
            "",
            "Per-Layer Contributions:",
        ]
        for layer_id, contrib in sorted(self.per_layer_contributions.items()):
            lines.append(f"  {layer_id}:  {contrib:.4f}")

        if self.per_interaction_contributions:
            lines.append("")
            lines.append("Per-Interaction Contributions:")
            for (layer_i, layer_j), contrib in sorted(self.per_interaction_contributions.items()):
                lines.append(f"  ({layer_i}, {layer_j}): {contrib:.4f}")

        return "\n".join(lines)


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of boundedness validation.

    Attributes:
        passed: Whether validation passed
        score: The calibration score that was validated
        lower_bound: Lower bound (0.0)
        upper_bound: Upper bound (1.0)
        message: Human-readable validation message
        clamped_score: Score after clamping to bounds (if needed)
    """

    passed:  bool
    score:  float
    lower_bound: float
    upper_bound: float
    message: str
    clamped_score: float

    def as_dict(self) -> dict[str, object]:
        """Convert to dictionary for serialization."""
        return {
            "passed": self.passed,
            "score":  self.score,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "message":  self.message,
            "clamped_score": self. clamped_score,
        }


@dataclass(frozen=True)
class CalibrationResult: 
    """
    Result of Choquet aggregation with full breakdown and metadata.

    Attributes:
        subject:  Identifier for the aggregated subject (e. g., method name)
        calibration_score: Final Cal(I) score ∈ [0,1]
        breakdown: Detailed CalibrationBreakdown
        layer_scores: Input layer scores dictionary
        metadata: Additional metadata (config hash, timestamp, etc.)
        validation:  ValidationResult with boundedness check details
    """

    subject:  str
    calibration_score: float
    breakdown: CalibrationBreakdown
    layer_scores:  dict[str, float]
    metadata:  dict[str, object]
    validation: ValidationResult

    @property
    def validation_passed(self) -> bool:
        """Return whether boundedness validation passed."""
        return self.validation.passed

    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if calibration score exceeds confidence threshold."""
        return self.calibration_score >= threshold

    def is_low_confidence(self, threshold: float = 0.3) -> bool:
        """Check if calibration score is below concern threshold."""
        return self.calibration_score <= threshold

    def summary(self) -> str:
        """Generate human-readable summary of result."""
        lines = [
            f"Calibration Result: {self.subject}",
            f"  Score: {self.calibration_score:.4f}",
            f"  Validation: {'PASSED' if self.validation_passed else 'FAILED'}",
            f"  Linear: {self.breakdown.linear_contribution:. 4f}",
            f"  Interaction: {self. breakdown.interaction_contribution:.4f}",
            f"  Layers: {len(self.layer_scores)}",
        ]
        return "\n".join(lines)


# =============================================================================
# CHOQUET AGGREGATOR
# =============================================================================


class ChoquetAggregator:
    """
    Choquet integral aggregator with interaction terms.

    This aggregator computes: 
        Cal(I) = linear_sum + interaction_sum

    Where: 
        linear_sum = Σ(aₗ·xₗ) over all layers
        interaction_sum = Σ(aₗₖ·min(xₗ,xₖ)) over all interaction pairs

    The aggregator enforces boundedness (0 ≤ Cal(I) ≤ 1) and provides detailed
    breakdowns showing contribution of each layer and interaction. 

    Note:
        The weights used are BUSINESS CONSTANTS representing fixed domain importance
        factors.  They are NOT epistemic parameters and should NOT be parameterized
        or tuned.  See module docstring. 

    Example:
        >>> config = ChoquetConfig(
        ...     linear_weights={"@b": 0.4, "@chain": 0.3},
        ...     interaction_weights={("@b", "@chain"): 0.2}
        ... )
        >>> aggregator = ChoquetAggregator(config)
        >>> result = aggregator.aggregate(
        ...     subject="method_X",
        ...     layer_scores={"@b": 0.8, "@chain": 0.7}
        ... )
        >>> print(f"Cal(I) = {result.calibration_score:.4f}")
    """

    def __init__(self, config: ChoquetConfig) -> None:
        """
        Initialize Choquet aggregator with configuration.

        Args:
            config:  ChoquetConfig with linear and interaction weights

        Raises: 
            CalibrationConfigError:  If configuration is invalid
        """
        self._config = config
        self._normalized_linear_weights = self._normalize_linear_weights()
        self._normalized_interaction_weights = self._normalize_interaction_weights()

        logger.info(
            f"ChoquetAggregator initialized:  "
            f"{config.n_layers} layers, "
            f"{config. n_interactions} interactions"
        )

    @property
    def config(self) -> ChoquetConfig:
        """Return the aggregator configuration."""
        return self._config

    @property
    def layer_ids(self) -> frozenset[str]:
        """Return immutable set of expected layer IDs."""
        return self._config.layer_ids

    def _normalize_linear_weights(self) -> dict[str, float]:
        """
        Normalize linear weights to ensure boundedness. 

        Returns: 
            Normalized linear weights dictionary

        Raises:
            CalibrationConfigError:  If total weight sum is non-positive
        """
        if not self._config.normalize_weights:
            return dict(self._config. linear_weights)

        total = sum(self._config.linear_weights. values())
        if total <= WEIGHT_NORMALIZATION_EPSILON: 
            raise CalibrationConfigError(
                f"Total linear weight sum must be positive, got {total}"
            )

        normalized = {
            layer:  weight / total
            for layer, weight in self._config. linear_weights.items()
        }

        logger.debug(f"Linear weights normalized: sum={total:.6f} -> 1.0")
        return normalized

    def _normalize_interaction_weights(self) -> dict[tuple[str, str], float]:
        """
        Normalize interaction weights relative to linear weights. 

        Interaction weights are constrained to ensure boundedness: 
            Σ|aₗₖ| ≤ INTERACTION_WEIGHT_MAX_RATIO × Σ(aₗ)

        Returns: 
            Normalized interaction weights dictionary
        """
        if not self._config. interaction_weights:
            return {}

        if not self._config. normalize_weights:
            return dict(self._config.interaction_weights)

        # Use sum of ABSOLUTE values for constraint check per README 10.3
        total_interaction_magnitude = sum(
            abs(w) for w in self._config.interaction_weights.values()
        )
        linear_sum = sum(self._normalized_linear_weights. values())
        max_allowed = min(linear_sum, 1.0) * INTERACTION_WEIGHT_MAX_RATIO

        if total_interaction_magnitude > max_allowed + WEIGHT_NORMALIZATION_EPSILON: 
            scale_factor = max_allowed / total_interaction_magnitude
            normalized = {
                pair: weight * scale_factor
                for pair, weight in self._config.interaction_weights.items()
            }
            logger. warning(
                f"Interaction weights scaled by {scale_factor:.4f} to ensure boundedness "
                f"(magnitude {total_interaction_magnitude:.4f} > max {max_allowed:.4f})"
            )
        else:
            normalized = dict(self._config. interaction_weights)

        return normalized

    def _clamp_score(self, score:  float) -> float:
        """Clamp score to [0, 1] bounds."""
        return max(DEFAULT_BOUNDEDNESS_LOWER, min(DEFAULT_BOUNDEDNESS_UPPER, score))

    def _compute_linear_sum(
        self, layer_scores: dict[str, float]
    ) -> tuple[float, dict[str, float], dict[str, str]]:
        """
        Compute linear contribution:  Σ(aₗ·xₗ)

        Args:
            layer_scores: Dictionary mapping layer_id -> score ∈ [0,1]

        Returns:
            Tuple of (total_sum, per_layer_contributions, per_layer_rationales)
        """
        linear_sum = 0.0
        per_layer_contributions:  dict[str, float] = {}
        per_layer_rationales: dict[str, str] = {}

        for layer_id, weight in self._normalized_linear_weights.items():
            raw_score = layer_scores.get(layer_id, 0.0)

            # Clamp and warn if out of bounds
            if raw_score < DEFAULT_BOUNDEDNESS_LOWER or raw_score > DEFAULT_BOUNDEDNESS_UPPER:
                logger.warning(
                    f"Layer {layer_id!r} score {raw_score:.4f} outside [0,1], clamping"
                )
            score = self._clamp_score(raw_score)

            contribution = weight * score
            linear_sum += contribution
            per_layer_contributions[layer_id] = contribution

            per_layer_rationales[layer_id] = (
                f"Layer {layer_id}:  weight={weight:.4f} × score={score:.4f} = {contribution:.4f}"
            )

        logger.debug(f"Linear sum computed: {linear_sum:.6f}")
        return linear_sum, per_layer_contributions, per_layer_rationales

    def _compute_interaction_sum(
        self, layer_scores: dict[str, float]
    ) -> tuple[float, dict[tuple[str, str], float], dict[tuple[str, str], str]]:
        """
        Compute interaction contribution: Σ(aₗₖ·min(xₗ,xₖ))

        Args:
            layer_scores: Dictionary mapping layer_id -> score ∈ [0,1]

        Returns:
            Tuple of (total_sum, per_interaction_contributions, per_interaction_rationales)
        """
        interaction_sum = 0.0
        per_interaction_contributions:  dict[tuple[str, str], float] = {}
        per_interaction_rationales: dict[tuple[str, str], str] = {}

        for (layer_i, layer_j), weight in self._normalized_interaction_weights.items():
            raw_score_i = layer_scores.get(layer_i, 0.0)
            raw_score_j = layer_scores.get(layer_j, 0.0)

            # Clamp scores
            score_i = self._clamp_score(raw_score_i)
            score_j = self._clamp_score(raw_score_j)

            if raw_score_i != score_i: 
                logger.warning(
                    f"Interaction layer {layer_i!r} score {raw_score_i:.4f} clamped to {score_i:.4f}"
                )
            if raw_score_j != score_j:
                logger.warning(
                    f"Interaction layer {layer_j!r} score {raw_score_j:.4f} clamped to {score_j:.4f}"
                )

            min_score = min(score_i, score_j)
            contribution = weight * min_score
            interaction_sum += contribution
            per_interaction_contributions[(layer_i, layer_j)] = contribution

            per_interaction_rationales[(layer_i, layer_j)] = (
                f"Interaction ({layer_i}, {layer_j}): "
                f"weight={weight:.4f} × min({score_i:.4f}, {score_j:.4f}) = {contribution:.4f}"
            )

        logger.debug(f"Interaction sum computed:  {interaction_sum:.6f}")
        return interaction_sum, per_interaction_contributions, per_interaction_rationales

    def _validate_boundedness(self, calibration_score: float) -> ValidationResult:
        """
        Validate that calibration score is bounded in [0,1]. 

        Args: 
            calibration_score: Computed Cal(I) score

        Returns:
            ValidationResult with validation details

        Raises: 
            BoundednessViolationError:  If boundedness is violated and validation enabled
        """
        clamped = self._clamp_score(calibration_score)
        is_bounded = (
            calibration_score >= DEFAULT_BOUNDEDNESS_LOWER - WEIGHT_NORMALIZATION_EPSILON
            and calibration_score <= DEFAULT_BOUNDEDNESS_UPPER + WEIGHT_NORMALIZATION_EPSILON
        )

        if is_bounded: 
            message = f"Boundedness validated: Cal(I)={calibration_score:.6f} ∈ [0,1]"
            logger.debug(message)
        else:
            message = (
                f"Boundedness violation: Cal(I)={calibration_score:.6f} not in [0,1], "
                f"clamped to {clamped:.6f}"
            )
            if self._config.validate_boundedness: 
                logger.error(message)
                raise BoundednessViolationError(message)
            else:
                logger.warning(message)

        return ValidationResult(
            passed=is_bounded,
            score=calibration_score,
            lower_bound=DEFAULT_BOUNDEDNESS_LOWER,
            upper_bound=DEFAULT_BOUNDEDNESS_UPPER,
            message=message,
            clamped_score=clamped,
        )

    def _check_missing_layers(self, layer_scores: dict[str, float]) -> None:
        """
        Check for missing required layers and raise if any are missing.

        Args:
            layer_scores: Input layer scores

        Raises: 
            MissingLayerError: If required layers are missing
        """
        required = set(self._config. linear_weights.keys())
        provided = set(layer_scores.keys())
        missing = required - provided

        if missing:
            raise MissingLayerError(
                f"Missing required layers in layer_scores: {missing}. "
                f"Expected: {required}, got: {provided}"
            )

    def aggregate(
        self,
        subject: str,
        layer_scores: dict[str, float],
        metadata: dict[str, object] | None = None,
    ) -> CalibrationResult:
        """
        Aggregate layer scores using Choquet integral with interaction terms.

        Args:
            subject:  Identifier for aggregated subject (e.g., method name)
            layer_scores: Dictionary mapping layer_id -> score ∈ [0,1]
            metadata: Optional metadata to include in result

        Returns: 
            CalibrationResult with score, breakdown, and validation details

        Raises: 
            BoundednessViolationError: If boundedness validation fails
            MissingLayerError: If required layers are missing from layer_scores

        Example:
            >>> result = aggregator.aggregate(
            ...     subject="BayesianAnalyzer",
            ...     layer_scores={"@b":  0.85, "@chain": 0.75, "@q": 0.90}
            ... )
            >>> print(f"Cal(I) = {result.calibration_score:.4f}")
            >>> print(f"Linear:  {result.breakdown. linear_contribution:.4f}")
            >>> print(f"Interaction: {result.breakdown.interaction_contribution:.4f}")
        """
        logger.info(f"Aggregating calibration for subject: {subject!r}")

        # Validate input completeness
        self._check_missing_layers(layer_scores)

        # Compute linear contribution
        linear_sum, per_layer_contrib, per_layer_rationale = self._compute_linear_sum(
            layer_scores
        )

        # Compute interaction contribution
        (
            interaction_sum,
            per_interaction_contrib,
            per_interaction_rationale,
        ) = self._compute_interaction_sum(layer_scores)

        # Compute raw calibration score
        raw_calibration_score = linear_sum + interaction_sum

        # Validate boundedness
        validation = self._validate_boundedness(raw_calibration_score)

        # Use clamped score as final result
        final_score = validation.clamped_score

        # Build breakdown
        breakdown = CalibrationBreakdown(
            linear_contribution=linear_sum,
            interaction_contribution=interaction_sum,
            per_layer_contributions=per_layer_contrib,
            per_interaction_contributions=per_interaction_contrib,
            per_layer_rationales=per_layer_rationale,
            per_interaction_rationales=per_interaction_rationale,
        )

        # Build metadata
        result_metadata:  dict[str, object] = dict(metadata) if metadata else {}
        result_metadata. update({
            "n_layers": len(layer_scores),
            "n_interactions":  len(self._normalized_interaction_weights),
            "normalized_weights": self._config.normalize_weights,
            "raw_score": raw_calibration_score,
        })

        # Build result
        result = CalibrationResult(
            subject=subject,
            calibration_score=final_score,
            breakdown=breakdown,
            layer_scores=dict(layer_scores),  # Copy to prevent mutation
            metadata=result_metadata,
            validation=validation,
        )

        logger.info(
            f"Aggregation complete:  subject={subject!r}, "
            f"Cal(I)={final_score:.4f}, "
            f"linear={linear_sum:.4f}, interaction={interaction_sum:.4f}"
        )

        return result

    def aggregate_batch(
        self,
        subjects_and_scores: list[tuple[str, dict[str, float]]],
        metadata: dict[str, object] | None = None,
    ) -> list[CalibrationResult]:
        """
        Aggregate multiple subjects in batch.

        Args:
            subjects_and_scores: List of (subject, layer_scores) tuples
            metadata: Optional metadata to include in all results

        Returns: 
            List of CalibrationResult for each subject

        Example:
            >>> results = aggregator.aggregate_batch([
            ...     ("method_A", {"@b":  0.8, "@chain": 0.7}),
            ...     ("method_B", {"@b": 0.6, "@chain": 0.9}),
            ... ])
        """
        results = []
        for subject, layer_scores in subjects_and_scores:
            try:
                result = self.aggregate(subject, layer_scores, metadata)
                results.append(result)
            except (BoundednessViolationError, MissingLayerError) as e:
                logger.error(f"Batch aggregation failed for {subject!r}: {e}")
                raise

        logger.info(f"Batch aggregation complete: {len(results)} subjects processed")
        return results


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_default_aggregator(
    layer_ids: list[str],
    interaction_pairs: list[tuple[str, str]] | None = None,
) -> ChoquetAggregator:
    """
    Create a ChoquetAggregator with uniform weights. 

    Args: 
        layer_ids:  List of layer identifiers
        interaction_pairs: Optional list of (layer_i, layer_j) interaction pairs

    Returns: 
        ChoquetAggregator with uniform linear weights and optional interactions

    Example:
        >>> aggregator = create_default_aggregator(
        ...     layer_ids=["@b", "@chain", "@q"],
        ...     interaction_pairs=[("@b", "@chain")]
        ... )
    """
    if not layer_ids: 
        raise CalibrationConfigError("layer_ids cannot be empty")

    # Uniform linear weights
    uniform_weight = 1.0 / len(layer_ids)
    linear_weights = {layer_id: uniform_weight for layer_id in layer_ids}

    # Uniform interaction weights (if provided)
    interaction_weights:  dict[tuple[str, str], float] = {}
    if interaction_pairs: 
        # Scale interaction weights to satisfy boundedness constraint
        interaction_weight = (uniform_weight * INTERACTION_WEIGHT_MAX_RATIO) / len(interaction_pairs)
        interaction_weights = {pair: interaction_weight for pair in interaction_pairs}

    config = ChoquetConfig(
        linear_weights=linear_weights,
        interaction_weights=interaction_weights,
        validate_boundedness=True,
        normalize_weights=True,
    )

    return ChoquetAggregator(config)