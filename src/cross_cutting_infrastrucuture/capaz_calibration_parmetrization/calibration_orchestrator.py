"""
Calibration Orchestrator for Method Quality Assessment

Implements multi-layer calibration system for method quality scoring:
- Base layer (@b): Intrinsic method quality from calibration JSON
- Context layers: Unit, question, dimension, policy
- Meta layers: Congruence, chain, meta
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MethodBelowThresholdError(Exception):
    """Raised when calibration score is below threshold."""
    
    def __init__(self, method_id: str, score: float, threshold: float):
        self.method_id = method_id
        self.score = score
        self.threshold = threshold
        super().__init__(
            f"Method {method_id} calibration score {score:.3f} below threshold {threshold:.3f}"
        )


@dataclass
class CalibrationResult:
    """Result of calibration assessment."""
    
    method_id: str
    final_score: float
    layer_scores: Dict[str, float]
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None
    breakdown: Optional[Dict[str, Any]] = None
    
    def passes_threshold(self, threshold: float = 0.7) -> bool:
        """Check if score passes threshold."""
        return self.final_score >= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "method_id": self.method_id,
            "final_score": self.final_score,
            "layer_scores": self.layer_scores,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "breakdown": self.breakdown,
        }


class IntrinsicCalibrationLoader:
    """Loads intrinsic calibration scores from JSON."""
    
    def __init__(self, json_path: str | Path):
        self.json_path = Path(json_path)
        self._cache: Optional[Dict[str, Any]] = None
    
    def _load(self) -> Dict[str, Any]:
        """Load JSON with caching."""
        if self._cache is None:
            if not self.json_path.exists():
                logger.warning(f"Calibration JSON not found: {self.json_path}")
                self._cache = {"methods": {}}
            else:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
                logger.info(f"Loaded calibration data from {self.json_path}")
        return self._cache
    
    def get_score(self, method_id: str, default: float = 0.5) -> float:
        """Get intrinsic score for method."""
        data = self._load()
        methods = data.get("methods", {})
        
        if method_id not in methods:
            logger.debug(f"Method {method_id} not in calibration data, using default {default}")
            return default
        
        method_data = methods[method_id]
        
        status = method_data.get("calibration_status", "computed")
        if status == "excluded":
            logger.debug(f"Method {method_id} excluded from calibration")
            return 0.0
        
        intrinsic_score = method_data.get("intrinsic_score")
        if intrinsic_score is None:
            logger.warning(f"Method {method_id} missing intrinsic_score, using default {default}")
            return default
        
        return float(intrinsic_score)
    
    def get_breakdown(self, method_id: str) -> Optional[Dict[str, Any]]:
        """Get calibration breakdown for method."""
        data = self._load()
        methods = data.get("methods", {})
        
        if method_id not in methods:
            return None
        
        return methods[method_id].get("breakdown", {})


class CalibrationOrchestrator:
    """Orchestrates multi-layer calibration for methods."""
    
    def __init__(
        self,
        intrinsic_json_path: str | Path | None = None,
        default_threshold: float = 0.7,
        enable_threshold_gate: bool = True,
    ):
        if intrinsic_json_path is None:
            intrinsic_json_path = Path(__file__).parent / "calibration" / "COHORT_2024_intrinsic_calibration.json"
        
        self.intrinsic_loader = IntrinsicCalibrationLoader(intrinsic_json_path)
        self.default_threshold = default_threshold
        self.enable_threshold_gate = enable_threshold_gate
        
        logger.info(
            f"CalibrationOrchestrator initialized: threshold={default_threshold}, "
            f"gate_enabled={enable_threshold_gate}"
        )
    
    def calibrate(
        self,
        method_id: str,
        context: Optional[Dict[str, Any]] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> CalibrationResult:
        """
        Calibrate a method with multi-layer scoring.
        
        Args:
            method_id: Method identifier (e.g., "module.Class.method")
            context: Execution context (document, tables, etc.)
            evidence: Raw evidence from method execution
        
        Returns:
            CalibrationResult with final score and layer breakdown
        
        Raises:
            MethodBelowThresholdError: If score below threshold and gate enabled
        """
        logger.debug(f"Calibrating method: {method_id}")
        
        base_score = self.intrinsic_loader.get_score(method_id)
        breakdown = self.intrinsic_loader.get_breakdown(method_id)
        
        layer_scores = {"@b": base_score}
        
        final_score = self._aggregate_layers(layer_scores)
        
        result = CalibrationResult(
            method_id=method_id,
            final_score=final_score,
            layer_scores=layer_scores,
            timestamp=datetime.utcnow(),
            context=context,
            breakdown=breakdown,
        )
        
        if self.enable_threshold_gate and not result.passes_threshold(self.default_threshold):
            raise MethodBelowThresholdError(method_id, final_score, self.default_threshold)
        
        logger.debug(
            f"Calibration complete: {method_id} scored {final_score:.3f} "
            f"(threshold: {self.default_threshold})"
        )
        
        return result
    
    def _aggregate_layers(self, layer_scores: Dict[str, float]) -> float:
        """
        Aggregate layer scores using weighted sum.
        
        For now, with only base layer, this returns the base score.
        Future: Implement Choquet integral or other aggregation.
        """
        if "@b" in layer_scores:
            return layer_scores["@b"]
        return 0.5


__all__ = [
    "CalibrationOrchestrator",
    "CalibrationResult",
    "MethodBelowThresholdError",
    "IntrinsicCalibrationLoader",
]
