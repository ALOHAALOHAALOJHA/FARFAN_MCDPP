"""Calibration Policy System for Method Selection and Weighting.

This module implements policies for how calibration scores influence:
- Method selection when alternatives exist
- Weighting in aggregation layers
- Diagnostic output in manifests and reports

Calibration scores are expected to be in [0, 1] where:
- [0.8, 1.0]: Excellent - full weight
- [0.6, 0.8): Good - minor downweight
- [0.4, 0.6): Acceptable - significant downweight
- [0.0, 0.4): Poor - major downweight or exclusion
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CalibrationWeight:
    """Calibration-adjusted weight for a method or result."""
    
    base_weight: float
    calibration_score: float
    adjusted_weight: float
    adjustment_factor: float
    quality_band: str
    reason: str
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "base_weight": self.base_weight,
            "calibration_score": self.calibration_score,
            "adjusted_weight": self.adjusted_weight,
            "adjustment_factor": self.adjustment_factor,
            "quality_band": self.quality_band,
            "reason": self.reason,
        }


@dataclass
class CalibrationMetrics:
    """Metrics for tracking calibration influence over time."""
    
    timestamp: str
    phase_id: int | str
    method_id: str
    calibration_score: float
    quality_band: str
    weight_adjustment: float
    influenced_output: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "phase_id": self.phase_id,
            "method_id": self.method_id,
            "calibration_score": self.calibration_score,
            "quality_band": self.quality_band,
            "weight_adjustment": self.weight_adjustment,
            "influenced_output": self.influenced_output,
            "metadata": self.metadata,
        }


class CalibrationPolicy:
    """Policy engine for calibration-based adjustments."""
    
    QUALITY_BANDS = {
        "EXCELLENT": (0.8, 1.0),
        "GOOD": (0.6, 0.8),
        "ACCEPTABLE": (0.4, 0.6),
        "POOR": (0.0, 0.4),
    }
    
    WEIGHT_ADJUSTMENT_FACTORS = {
        "EXCELLENT": 1.0,      # No downweight
        "GOOD": 0.9,           # 10% downweight
        "ACCEPTABLE": 0.7,     # 30% downweight
        "POOR": 0.4,           # 60% downweight
    }
    
    MIN_EXECUTION_THRESHOLD = 0.3
    
    def __init__(
        self,
        strict_mode: bool = False,
        custom_thresholds: dict[str, tuple[float, float]] | None = None,
        custom_factors: dict[str, float] | None = None,
    ) -> None:
        """Initialize calibration policy.
        
        Args:
            strict_mode: If True, reject methods below MIN_EXECUTION_THRESHOLD
            custom_thresholds: Override default quality band thresholds
            custom_factors: Override default weight adjustment factors
        """
        self.strict_mode = strict_mode
        self.quality_bands = custom_thresholds or self.QUALITY_BANDS
        self.adjustment_factors = custom_factors or self.WEIGHT_ADJUSTMENT_FACTORS
        self._metrics_history: list[CalibrationMetrics] = []
    
    def get_quality_band(self, calibration_score: float) -> str:
        """Determine quality band for a calibration score.
        
        Args:
            calibration_score: Score in [0, 1]
            
        Returns:
            Quality band string (EXCELLENT, GOOD, ACCEPTABLE, POOR)
        """
        for band, (low, high) in self.quality_bands.items():
            if low <= calibration_score < high:
                return band
        return "POOR"
    
    def should_execute_method(
        self, method_id: str, calibration_score: float | None
    ) -> tuple[bool, str]:
        """Decide whether a method should be executed based on calibration.
        
        Args:
            method_id: Method identifier
            calibration_score: Calibration score or None if not available
            
        Returns:
            (should_execute, reason) tuple
        """
        if calibration_score is None:
            return True, "No calibration data available - executing by default"
        
        if calibration_score < self.MIN_EXECUTION_THRESHOLD:
            if self.strict_mode:
                return (
                    False,
                    f"Method {method_id} calibration {calibration_score:.3f} "
                    f"below threshold {self.MIN_EXECUTION_THRESHOLD}",
                )
            else:
                logger.warning(
                    f"Method {method_id} has low calibration {calibration_score:.3f} "
                    f"but executing anyway (strict_mode=False)"
                )
                return True, "Low calibration but executing (non-strict mode)"
        
        quality_band = self.get_quality_band(calibration_score)
        return True, f"Calibration {calibration_score:.3f} ({quality_band}) - executing"
    
    def compute_adjusted_weight(
        self,
        base_weight: float,
        calibration_score: float | None,
        method_id: str = "",
    ) -> CalibrationWeight:
        """Compute calibration-adjusted weight for aggregation.
        
        Args:
            base_weight: Original weight before calibration adjustment
            calibration_score: Calibration score or None
            method_id: Optional method identifier for logging
            
        Returns:
            CalibrationWeight with adjustment details
        """
        if calibration_score is None:
            return CalibrationWeight(
                base_weight=base_weight,
                calibration_score=0.0,
                adjusted_weight=base_weight,
                adjustment_factor=1.0,
                quality_band="UNKNOWN",
                reason="No calibration data - using base weight",
            )
        
        quality_band = self.get_quality_band(calibration_score)
        adjustment_factor = self.adjustment_factors.get(quality_band, 1.0)
        adjusted_weight = base_weight * adjustment_factor
        
        reason = (
            f"Calibration {calibration_score:.3f} ({quality_band}) "
            f"→ weight {base_weight:.3f} × {adjustment_factor:.2f} = {adjusted_weight:.3f}"
        )
        
        if method_id:
            logger.info(f"[{method_id}] {reason}")
        
        return CalibrationWeight(
            base_weight=base_weight,
            calibration_score=calibration_score,
            adjusted_weight=adjusted_weight,
            adjustment_factor=adjustment_factor,
            quality_band=quality_band,
            reason=reason,
        )
    
    def select_best_method(
        self,
        candidates: dict[str, float],
    ) -> tuple[str, float, str]:
        """Select best method from alternatives based on calibration.
        
        Args:
            candidates: Dict mapping method_id to calibration_score
            
        Returns:
            (selected_method_id, calibration_score, reason) tuple
        """
        if not candidates:
            raise ValueError("No candidate methods provided")
        
        if len(candidates) == 1:
            method_id, score = next(iter(candidates.items()))
            return method_id, score, "Only one candidate"
        
        sorted_candidates = sorted(
            candidates.items(), key=lambda x: x[1], reverse=True
        )
        
        best_method, best_score = sorted_candidates[0]
        second_best = sorted_candidates[1][1] if len(sorted_candidates) > 1 else 0.0
        
        margin = best_score - second_best
        reason = (
            f"Selected {best_method} (calibration {best_score:.3f}) "
            f"over alternatives (margin {margin:.3f})"
        )
        
        logger.info(reason)
        return best_method, best_score, reason
    
    def record_influence(
        self,
        phase_id: int | str,
        method_id: str,
        calibration_score: float,
        weight_adjustment: float,
        influenced_output: bool,
        **metadata: Any,
    ) -> None:
        """Record calibration influence for drift detection.
        
        Args:
            phase_id: Pipeline phase identifier
            method_id: Method identifier
            calibration_score: Calibration score used
            weight_adjustment: How much weight was adjusted
            influenced_output: Whether calibration changed the output
            **metadata: Additional context
        """
        quality_band = self.get_quality_band(calibration_score)
        
        metric = CalibrationMetrics(
            timestamp=datetime.now().astimezone().isoformat(),
            phase_id=phase_id,
            method_id=method_id,
            calibration_score=calibration_score,
            quality_band=quality_band,
            weight_adjustment=weight_adjustment,
            influenced_output=influenced_output,
            metadata=metadata,
        )
        
        self._metrics_history.append(metric)
    
    def detect_drift(
        self, window_size: int = 50, threshold: float = 0.15
    ) -> dict[str, Any]:
        """Detect calibration drift over time.
        
        Args:
            window_size: Number of recent metrics to analyze
            threshold: Drift threshold (std dev relative to mean)
            
        Returns:
            Drift analysis dict with detected issues
        """
        if len(self._metrics_history) < window_size:
            return {
                "drift_detected": False,
                "reason": f"Insufficient data ({len(self._metrics_history)} < {window_size})",
            }
        
        recent_metrics = self._metrics_history[-window_size:]
        scores = [m.calibration_score for m in recent_metrics]
        
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
        
        drift_detected = std_score > (mean_score * threshold) if mean_score > 0 else False
        
        band_distribution = {}
        for metric in recent_metrics:
            band = metric.quality_band
            band_distribution[band] = band_distribution.get(band, 0) + 1
        
        influenced_count = sum(1 for m in recent_metrics if m.influenced_output)
        
        return {
            "drift_detected": drift_detected,
            "window_size": window_size,
            "mean_score": mean_score,
            "std_score": std_score,
            "drift_threshold": threshold,
            "band_distribution": band_distribution,
            "influenced_outputs": influenced_count,
            "total_metrics": len(recent_metrics),
            "drift_ratio": std_score / mean_score if mean_score > 0 else 0.0,
        }
    
    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of all calibration metrics.
        
        Returns:
            Summary dict with statistics and history
        """
        if not self._metrics_history:
            return {
                "total_metrics": 0,
                "summary": "No calibration metrics recorded",
            }
        
        scores = [m.calibration_score for m in self._metrics_history]
        adjustments = [m.weight_adjustment for m in self._metrics_history]
        influenced = sum(1 for m in self._metrics_history if m.influenced_output)
        
        by_phase: dict[str, int] = {}
        by_band: dict[str, int] = {}
        
        for metric in self._metrics_history:
            phase_key = str(metric.phase_id)
            by_phase[phase_key] = by_phase.get(phase_key, 0) + 1
            by_band[metric.quality_band] = by_band.get(metric.quality_band, 0) + 1
        
        return {
            "total_metrics": len(self._metrics_history),
            "mean_calibration_score": statistics.mean(scores),
            "median_calibration_score": statistics.median(scores),
            "std_calibration_score": statistics.stdev(scores) if len(scores) > 1 else 0.0,
            "mean_weight_adjustment": statistics.mean(adjustments),
            "influenced_outputs": influenced,
            "influence_rate": influenced / len(self._metrics_history),
            "by_phase": by_phase,
            "by_quality_band": by_band,
            "drift_analysis": self.detect_drift(),
        }
    
    def export_metrics(self) -> list[dict[str, Any]]:
        """Export all metrics for external analysis.
        
        Returns:
            List of metric dictionaries
        """
        return [m.to_dict() for m in self._metrics_history]


def create_default_policy(strict_mode: bool = False) -> CalibrationPolicy:
    """Factory function for default calibration policy.
    
    Args:
        strict_mode: Whether to enforce strict calibration thresholds
        
    Returns:
        Configured CalibrationPolicy instance
    """
    return CalibrationPolicy(strict_mode=strict_mode)


__all__ = [
    "CalibrationPolicy",
    "CalibrationWeight",
    "CalibrationMetrics",
    "create_default_policy",
]
