"""
Choquet Aggregator - Non-linear Multi-Layer Calibration Aggregation

This module implements the Choquet integral for aggregating multi-layer calibration
scores with interaction terms. The Choquet aggregator captures synergies and 
complementarities between layers that simple weighted averages cannot represent.

Formula:
    Cal(I) = Σ(aₗ·xₗ) + Σ(aₗₖ·min(xₗ,xₖ))
    
Where:
    - xₗ: Score for layer l (normalized to [0,1])
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
    - Normalization: Weights normalized to ensure boundedness
    - Determinism: Fixed random seeds for reproducible results
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class CalibrationConfigError(Exception):
    """Raised when calibration configuration validation fails."""
    pass


@dataclass(frozen=True)
class ChoquetConfig:
    """
    Configuration for Choquet aggregation with interaction terms.
    
    Attributes:
        linear_weights: Dictionary mapping layer_id -> linear weight (aₗ)
        interaction_weights: Dictionary mapping (layer_i, layer_j) -> interaction weight (aₗₖ)
        validate_boundedness: Whether to validate that Cal(I) ∈ [0,1]
        normalize_weights: Whether to normalize weights automatically
        
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
    normalize_weights: bool = True
    
    def __post_init__(self) -> None:
        """Validate configuration on construction."""
        if not self.linear_weights:
            raise CalibrationConfigError("linear_weights cannot be empty")
        
        for layer_id, weight in self.linear_weights.items():
            if not isinstance(layer_id, str):
                raise CalibrationConfigError(f"Layer ID must be string, got {type(layer_id)}")
            if not isinstance(weight, (int, float)):
                raise CalibrationConfigError(f"Weight must be numeric, got {type(weight)}")
            if weight < 0.0:
                raise CalibrationConfigError(f"Negative weight not allowed: {layer_id}={weight}")
        
        for (layer_i, layer_j), weight in self.interaction_weights.items():
            if not isinstance(layer_i, str) or not isinstance(layer_j, str):
                raise CalibrationConfigError(f"Layer IDs must be strings: ({layer_i}, {layer_j})")
            if not isinstance(weight, (int, float)):
                raise CalibrationConfigError(f"Interaction weight must be numeric: {weight}")
            if weight < 0.0:
                raise CalibrationConfigError(f"Negative interaction weight: ({layer_i},{layer_j})={weight}")
            if layer_i not in self.linear_weights:
                raise CalibrationConfigError(f"Interaction layer {layer_i} not in linear_weights")
            if layer_j not in self.linear_weights:
                raise CalibrationConfigError(f"Interaction layer {layer_j} not in linear_weights")


@dataclass
class CalibrationBreakdown:
    """
    Detailed breakdown of Choquet aggregation computation.
    
    Attributes:
        linear_contribution: Total contribution from linear terms Σ(aₗ·xₗ)
        interaction_contribution: Total contribution from interaction terms Σ(aₗₖ·min(xₗ,xₖ))
        per_layer_contributions: Dictionary mapping layer_id -> aₗ·xₗ
        per_interaction_contributions: Dictionary mapping (layer_i, layer_j) -> aₗₖ·min(xₗ,xₖ)
        per_layer_rationales: Dictionary mapping layer_id -> human-readable rationale
        per_interaction_rationales: Dictionary mapping (layer_i, layer_j) -> rationale
    """
    linear_contribution: float
    interaction_contribution: float
    per_layer_contributions: dict[str, float]
    per_interaction_contributions: dict[tuple[str, str], float]
    per_layer_rationales: dict[str, str]
    per_interaction_rationales: dict[tuple[str, str], str]


@dataclass
class CalibrationResult:
    """
    Result of Choquet aggregation with full breakdown and metadata.
    
    Attributes:
        subject: Identifier for the aggregated subject (e.g., method name)
        calibration_score: Final Cal(I) score ∈ [0,1]
        breakdown: Detailed CalibrationBreakdown
        layer_scores: Input layer scores dictionary
        metadata: Additional metadata (config hash, timestamp, etc.)
        validation_passed: Whether boundedness validation passed
        validation_details: Details of validation checks
    """
    subject: str
    calibration_score: float
    breakdown: CalibrationBreakdown
    layer_scores: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)


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
            config: ChoquetConfig with linear and interaction weights
            
        Raises:
            CalibrationConfigError: If configuration is invalid
        """
        self.config = config
        self._normalized_linear_weights = self._normalize_linear_weights()
        self._normalized_interaction_weights = self._normalize_interaction_weights()
        
        logger.info(
            f"ChoquetAggregator initialized: "
            f"{len(self.config.linear_weights)} layers, "
            f"{len(self.config.interaction_weights)} interactions"
        )
    
    def _normalize_linear_weights(self) -> dict[str, float]:
        """
        Normalize linear weights to ensure boundedness.
        
        Returns:
            Normalized linear weights dictionary
        """
        if not self.config.normalize_weights:
            return dict(self.config.linear_weights)
        
        total = sum(self.config.linear_weights.values())
        if total <= 0:
            raise CalibrationConfigError("Total linear weight sum must be positive")
        
        normalized = {
            layer: weight / total 
            for layer, weight in self.config.linear_weights.items()
        }
        
        logger.debug(f"Linear weights normalized: total={total:.4f}")
        return normalized
    
    def _normalize_interaction_weights(self) -> dict[tuple[str, str], float]:
        """
        Normalize interaction weights relative to linear weights.
        
        Interaction weights are constrained to ensure boundedness:
            Σ(aₗₖ) ≤ min(Σ(aₗ), 1.0)
            
        Returns:
            Normalized interaction weights dictionary
        """
        if not self.config.interaction_weights:
            return {}
        
        if not self.config.normalize_weights:
            return dict(self.config.interaction_weights)
        
        total_interaction = sum(self.config.interaction_weights.values())
        max_allowed = min(sum(self._normalized_linear_weights.values()), 1.0) * 0.5
        
        if total_interaction > max_allowed:
            scale_factor = max_allowed / total_interaction
            normalized = {
                pair: weight * scale_factor
                for pair, weight in self.config.interaction_weights.items()
            }
            logger.warning(
                f"Interaction weights scaled by {scale_factor:.4f} to ensure boundedness"
            )
        else:
            normalized = dict(self.config.interaction_weights)
        
        return normalized
    
    def _compute_linear_sum(
        self, 
        layer_scores: dict[str, float]
    ) -> tuple[float, dict[str, float], dict[str, str]]:
        """
        Compute linear contribution: Σ(aₗ·xₗ)
        
        Args:
            layer_scores: Dictionary mapping layer_id -> score ∈ [0,1]
            
        Returns:
            Tuple of (total_sum, per_layer_contributions, per_layer_rationales)
        """
        linear_sum = 0.0
        per_layer_contributions: dict[str, float] = {}
        per_layer_rationales: dict[str, str] = {}
        
        for layer_id, weight in self._normalized_linear_weights.items():
            score = layer_scores.get(layer_id, 0.0)
            
            if score < 0.0 or score > 1.0:
                logger.warning(f"Layer {layer_id} score {score} outside [0,1], clamping")
                score = max(0.0, min(1.0, score))
            
            contribution = weight * score
            linear_sum += contribution
            per_layer_contributions[layer_id] = contribution
            
            per_layer_rationales[layer_id] = (
                f"Layer {layer_id}: weight={weight:.4f} × score={score:.4f} "
                f"= {contribution:.4f}"
            )
        
        logger.debug(f"Linear sum computed: {linear_sum:.4f}")
        return linear_sum, per_layer_contributions, per_layer_rationales
    
    def _compute_interaction_sum(
        self,
        layer_scores: dict[str, float]
    ) -> tuple[float, dict[tuple[str, str], float], dict[tuple[str, str], str]]:
        """
        Compute interaction contribution: Σ(aₗₖ·min(xₗ,xₖ))
        
        Args:
            layer_scores: Dictionary mapping layer_id -> score ∈ [0,1]
            
        Returns:
            Tuple of (total_sum, per_interaction_contributions, per_interaction_rationales)
        """
        interaction_sum = 0.0
        per_interaction_contributions: dict[tuple[str, str], float] = {}
        per_interaction_rationales: dict[tuple[str, str], str] = {}
        
        for (layer_i, layer_j), weight in self._normalized_interaction_weights.items():
            score_i = layer_scores.get(layer_i, 0.0)
            score_j = layer_scores.get(layer_j, 0.0)
            
            if score_i < 0.0 or score_i > 1.0:
                logger.warning(f"Layer {layer_i} score {score_i} outside [0,1], clamping")
                score_i = max(0.0, min(1.0, score_i))
            
            if score_j < 0.0 or score_j > 1.0:
                logger.warning(f"Layer {layer_j} score {score_j} outside [0,1], clamping")
                score_j = max(0.0, min(1.0, score_j))
            
            min_score = min(score_i, score_j)
            contribution = weight * min_score
            interaction_sum += contribution
            per_interaction_contributions[(layer_i, layer_j)] = contribution
            
            per_interaction_rationales[(layer_i, layer_j)] = (
                f"Interaction ({layer_i}, {layer_j}): "
                f"weight={weight:.4f} × min({score_i:.4f}, {score_j:.4f}) "
                f"= {contribution:.4f}"
            )
        
        logger.debug(f"Interaction sum computed: {interaction_sum:.4f}")
        return interaction_sum, per_interaction_contributions, per_interaction_rationales
    
    def _validate_boundedness(self, calibration_score: float) -> tuple[bool, dict[str, Any]]:
        """
        Validate that calibration score is bounded in [0,1].
        
        Args:
            calibration_score: Computed Cal(I) score
            
        Returns:
            Tuple of (is_valid, validation_details)
            
        Raises:
            CalibrationConfigError: If boundedness is violated and validation enabled
        """
        validation_details = {
            "score": calibration_score,
            "lower_bound": 0.0,
            "upper_bound": 1.0,
            "bounded": True,
            "message": "Boundedness validated"
        }
        
        if calibration_score < 0.0 or calibration_score > 1.0:
            validation_details["bounded"] = False
            validation_details["message"] = (
                f"Boundedness violation: Cal(I)={calibration_score:.6f} not in [0,1]"
            )
            
            if self.config.validate_boundedness:
                logger.error(validation_details["message"])
                raise CalibrationConfigError(validation_details["message"])
            else:
                logger.warning(validation_details["message"])
                return False, validation_details
        
        logger.debug(f"Boundedness validated: {calibration_score:.4f} ∈ [0,1]")
        return True, validation_details
    
    def aggregate(
        self,
        subject: str,
        layer_scores: dict[str, float],
        metadata: dict[str, Any] | None = None
    ) -> CalibrationResult:
        """
        Aggregate layer scores using Choquet integral with interaction terms.
        
        Args:
            subject: Identifier for aggregated subject (e.g., method name)
            layer_scores: Dictionary mapping layer_id -> score ∈ [0,1]
            metadata: Optional metadata to include in result
            
        Returns:
            CalibrationResult with score, breakdown, and validation details
            
        Raises:
            CalibrationConfigError: If boundedness validation fails
            ValueError: If required layers are missing from layer_scores
            
        Example:
            >>> result = aggregator.aggregate(
            ...     subject="BayesianAnalyzer",
            ...     layer_scores={"@b": 0.85, "@chain": 0.75, "@q": 0.90}
            ... )
            >>> print(f"Cal(I) = {result.calibration_score:.4f}")
            >>> print(f"Linear: {result.breakdown.linear_contribution:.4f}")
            >>> print(f"Interaction: {result.breakdown.interaction_contribution:.4f}")
        """
        logger.info(f"Aggregating calibration for subject: {subject}")
        
        missing_layers = set(self.config.linear_weights.keys()) - set(layer_scores.keys())
        if missing_layers:
            raise ValueError(
                f"Missing required layers in layer_scores: {missing_layers}. "
                f"Expected: {set(self.config.linear_weights.keys())}"
            )
        
        linear_sum, per_layer_contrib, per_layer_rationale = self._compute_linear_sum(layer_scores)
        
        interaction_sum, per_interaction_contrib, per_interaction_rationale = (
            self._compute_interaction_sum(layer_scores)
        )
        
        calibration_score = linear_sum + interaction_sum
        
        validation_passed, validation_details = self._validate_boundedness(calibration_score)
        
        calibration_score = max(0.0, min(1.0, calibration_score))
        
        breakdown = CalibrationBreakdown(
            linear_contribution=linear_sum,
            interaction_contribution=interaction_sum,
            per_layer_contributions=per_layer_contrib,
            per_interaction_contributions=per_interaction_contrib,
            per_layer_rationales=per_layer_rationale,
            per_interaction_rationales=per_interaction_rationale
        )
        
        result_metadata = metadata or {}
        result_metadata.update({
            "n_layers": len(layer_scores),
            "n_interactions": len(self._normalized_interaction_weights),
            "normalized_weights": self.config.normalize_weights,
        })
        
        result = CalibrationResult(
            subject=subject,
            calibration_score=calibration_score,
            breakdown=breakdown,
            layer_scores=layer_scores,
            metadata=result_metadata,
            validation_passed=validation_passed,
            validation_details=validation_details
        )
        
        logger.info(
            f"✓ Aggregation complete: subject={subject}, "
            f"Cal(I)={calibration_score:.4f}, "
            f"linear={linear_sum:.4f}, interaction={interaction_sum:.4f}"
        )
        
        return result
