"""
Module: src.farfan_pipeline.phases.Phase_two.phase2_i_precision_tracking
Phase: 2 (Evidence Nexus & Executor Orchestration)
Purpose: Track precision/recall of pattern matching

Emits precision metrics per policy area for quality monitoring.
Tracks method accuracy and evidence extraction quality.

Success Criteria:
- Track precision/recall for all 240 methods
- Emit metrics per policy area (PA01-PA10)
- Aggregate statistics for quality dashboards
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PrecisionMetrics:
    """Precision/recall metrics for pattern matching."""
    
    method_name: str
    policy_area_id: str
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    
    @property
    def precision(self) -> float:
        """Calculate precision = TP / (TP + FP)."""
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom > 0 else 0.0
    
    @property
    def recall(self) -> float:
        """Calculate recall = TP / (TP + FN)."""
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom > 0 else 0.0
    
    @property
    def f1_score(self) -> float:
        """Calculate F1 = 2 * (precision * recall) / (precision + recall)."""
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


class PrecisionTracker:
    """Track precision/recall metrics for methods."""
    
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], PrecisionMetrics] = {}
    
    def record_match(
        self,
        method_name: str,
        policy_area_id: str,
        is_true_positive: bool,
        is_false_positive: bool = False,
        is_false_negative: bool = False,
    ) -> None:
        """Record pattern match result."""
        key = (method_name, policy_area_id)
        
        if key not in self._metrics:
            self._metrics[key] = PrecisionMetrics(
                method_name=method_name,
                policy_area_id=policy_area_id,
            )
        
        metrics = self._metrics[key]
        if is_true_positive:
            metrics.true_positives += 1
        if is_false_positive:
            metrics.false_positives += 1
        if is_false_negative:
            metrics.false_negatives += 1
    
    def get_metrics(
        self, method_name: str | None = None, policy_area_id: str | None = None
    ) -> list[PrecisionMetrics]:
        """Get precision metrics, optionally filtered."""
        results = []
        for (m, pa), metrics in self._metrics.items():
            if method_name and m != method_name:
                continue
            if policy_area_id and pa != policy_area_id:
                continue
            results.append(metrics)
        return results


# Global tracker
_tracker = PrecisionTracker()


def record_match(
    method_name: str,
    policy_area_id: str,
    is_true_positive: bool,
    is_false_positive: bool = False,
    is_false_negative: bool = False,
) -> None:
    """Record pattern match result."""
    _tracker.record_match(
        method_name, policy_area_id, is_true_positive, is_false_positive, is_false_negative
    )


def get_precision_metrics(
    method_name: str | None = None, policy_area_id: str | None = None
) -> list[PrecisionMetrics]:
    """Get precision metrics."""
    return _tracker.get_metrics(method_name, policy_area_id)
