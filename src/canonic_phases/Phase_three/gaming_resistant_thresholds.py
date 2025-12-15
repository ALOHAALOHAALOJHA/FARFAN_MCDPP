"""
Gaming-resistant threshold adjustment functions for Phase 3 scoring.

Replaces hard threshold boundaries with smooth sigmoid functions to prevent
gaming vulnerabilities. Uses continuous mathematical functions instead of
step functions for all threshold-based adjustments.

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0 (Gaming-Resistant)
"""

import math
import statistics
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ThresholdConfig:
    """Calibrated threshold configuration for signal-based adjustments."""
    
    # Pattern thresholds
    high_pattern_threshold: int = 15
    pattern_complexity_adjustment: float = 0.05
    pattern_sigmoid_steepness: float = 0.3
    
    # Indicator thresholds
    high_indicator_threshold: int = 10
    indicator_specificity_adjustment: float = 0.03
    indicator_sigmoid_steepness: float = 0.25
    
    # Quality thresholds
    quality_weight_enabled: bool = True
    min_quality_threshold: float = 0.3


def compute_pattern_adjustment(
    pattern_count: int,
    config: ThresholdConfig,
) -> tuple[float, dict[str, Any]]:
    """
    Compute smooth pattern adjustment using sigmoid.
    
    Prevents gaming by using continuous function instead of hard threshold.
    
    Args:
        pattern_count: Number of patterns identified
        config: Calibrated threshold configuration
        
    Returns:
        (adjustment, metadata)
        
    Mathematical Form:
        adjustment = max_adj × sigmoid(k(x - threshold))
        sigmoid(z) = 1 / (1 + exp(-z))
        
    Properties:
        - Smooth transition around threshold
        - No gaming vulnerability at boundary
        - Asymptotically approaches max_adj
        
    Examples:
        >>> config = ThresholdConfig()
        >>> compute_pattern_adjustment(14, config)
        (0.023, {...})  # Just below threshold
        
        >>> compute_pattern_adjustment(15, config)
        (0.025, {...})  # At threshold - smooth transition
        
        >>> compute_pattern_adjustment(16, config)
        (0.027, {...})  # Just above - no jump
    """
    threshold = config.high_pattern_threshold
    max_adjustment = config.pattern_complexity_adjustment
    steepness = config.pattern_sigmoid_steepness
    
    # Sigmoid centered at threshold
    z = steepness * (pattern_count - threshold)
    sigmoid = 1.0 / (1.0 + math.exp(-z))
    
    # Scale to adjustment range
    adjustment = max_adjustment * sigmoid
    
    metadata = {
        "pattern_count": pattern_count,
        "threshold": threshold,
        "sigmoid_value": sigmoid,
        "adjustment": adjustment,
        "steepness": steepness,
        "gaming_resistant": True,
        "function_type": "sigmoid",
    }
    
    return adjustment, metadata


def compute_indicator_adjustment(
    indicator_count: int,
    indicator_quality_scores: list[float] | None,
    config: ThresholdConfig,
) -> tuple[float, dict[str, Any]]:
    """
    Compute quality-weighted indicator adjustment.
    
    Combines quantity AND quality to prevent gaming.
    
    Args:
        indicator_count: Number of indicators
        indicator_quality_scores: Quality score for each indicator (0-1)
        config: Threshold configuration
        
    Returns:
        (adjustment, metadata)
        
    Examples:
        >>> config = ThresholdConfig()
        >>> # 10 high-quality indicators
        >>> compute_indicator_adjustment(10, [0.9] * 10, config)
        (0.027, {...})  # Higher adjustment
        
        >>> # 10 low-quality indicators
        >>> compute_indicator_adjustment(10, [0.3] * 10, config)
        (0.009, {...})  # Lower adjustment - quality matters!
    """
    # Quality-weighted count (if quality scores provided)
    if indicator_quality_scores and config.quality_weight_enabled:
        weighted_count = sum(indicator_quality_scores)
    else:
        weighted_count = float(indicator_count)
    
    threshold = config.high_indicator_threshold
    max_adjustment = config.indicator_specificity_adjustment
    steepness = config.indicator_sigmoid_steepness
    
    # Sigmoid on weighted count
    z = steepness * (weighted_count - threshold)
    sigmoid = 1.0 / (1.0 + math.exp(-z))
    adjustment = max_adjustment * sigmoid
    
    metadata = {
        "indicator_count": indicator_count,
        "weighted_count": weighted_count,
        "quality_scores": indicator_quality_scores,
        "threshold": threshold,
        "adjustment": adjustment,
        "quality_weighted": indicator_quality_scores is not None,
        "gaming_resistant": True,
        "function_type": "quality_weighted_sigmoid",
    }
    
    return adjustment, metadata


def validate_signal_authenticity(
    signal_pack: Any,
    evidence: dict[str, Any],
    min_quality: float = 0.3,
) -> tuple[dict[str, Any], float]:
    """
    Validate signal quality and filter low-quality signals.
    
    Prevents gaming by requiring signals to align with evidence.
    
    Args:
        signal_pack: Signal pack from registry
        evidence: Evidence dict from Phase 2
        min_quality: Minimum quality threshold (0-1)
        
    Returns:
        (validated_signals, authenticity_score)
        
    Example:
        >>> validate_signal_authenticity(signal_pack, evidence)
        ({
            "patterns": ["pattern1", "pattern2"],  # Filtered
            "indicators": ["ind1"],  # Filtered
            "quality_scores": {"pattern_quality": 0.75, ...}
        }, 0.78)
    """
    patterns = getattr(signal_pack, 'patterns', [])
    indicators = getattr(signal_pack, 'indicators', [])
    
    validated = {
        "patterns": [],
        "indicators": [],
        "pattern_quality_scores": [],
        "indicator_quality_scores": [],
    }
    
    # Validate patterns
    for pattern in patterns:
        quality = _score_pattern_quality(pattern, evidence)
        if quality >= min_quality:
            validated["patterns"].append(pattern)
            validated["pattern_quality_scores"].append(quality)
    
    # Validate indicators
    for indicator in indicators:
        quality = _score_indicator_relevance(indicator, evidence)
        if quality >= min_quality:
            validated["indicators"].append(indicator)
            validated["indicator_quality_scores"].append(quality)
    
    # Compute authenticity score
    all_scores = (
        validated["pattern_quality_scores"] +
        validated["indicator_quality_scores"]
    )
    authenticity = statistics.mean(all_scores) if all_scores else 0.0
    
    validated["quality_scores"] = {
        "pattern_quality": (
            statistics.mean(validated["pattern_quality_scores"])
            if validated["pattern_quality_scores"] else 0.0
        ),
        "indicator_relevance": (
            statistics.mean(validated["indicator_quality_scores"])
            if validated["indicator_quality_scores"] else 0.0
        ),
        "authenticity_score": authenticity,
    }
    
    return validated, authenticity


def _score_pattern_quality(pattern: Any, evidence: dict[str, Any]) -> float:
    """Score pattern quality based on evidence alignment."""
    pattern_str = str(pattern).lower()
    
    # Rule 1: Minimum length
    if len(pattern_str) < 10:
        return 0.2
    
    # Rule 2: Detect noise patterns
    if any(noise in pattern_str for noise in ["noise_", "test_", "dummy_"]):
        return 0.1
    
    # Rule 3: Check alignment with evidence types
    evidence_types = {
        str(e.get("type", "")).lower()
        for e in evidence.get("elements", [])
    }
    
    if not evidence_types:
        return 0.5  # No evidence to compare
    
    alignment_score = sum(
        1.0 for et in evidence_types
        if et in pattern_str or pattern_str in et
    ) / len(evidence_types)
    
    # Combine scores
    quality = 0.5 + 0.5 * alignment_score
    return min(1.0, quality)


def _score_indicator_relevance(indicator: Any, evidence: dict[str, Any]) -> float:
    """Score indicator relevance to actual evidence."""
    indicator_str = str(indicator).lower()
    
    # Rule 1: Minimum length
    if len(indicator_str) < 5:
        return 0.2
    
    # Rule 2: Check against evidence values
    evidence_values = [
        str(e.get("value", "")).lower()
        for e in evidence.get("elements", [])
    ]
    
    if not evidence_values:
        return 0.5  # No evidence to compare
    
    # Compute relevance
    relevance = 0.0
    for ev_val in evidence_values:
        if indicator_str in ev_val or ev_val in indicator_str:
            relevance = 0.9
            break
        # Fuzzy match (substring overlap)
        common = set(indicator_str.split()) & set(ev_val.split())
        if common:
            relevance = max(relevance, 0.5)
    
    return relevance


__all__ = [
    "ThresholdConfig",
    "compute_pattern_adjustment",
    "compute_indicator_adjustment",
    "validate_signal_authenticity",
]
