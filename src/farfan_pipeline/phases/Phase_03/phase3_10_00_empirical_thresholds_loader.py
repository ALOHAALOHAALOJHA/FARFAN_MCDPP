"""Phase 3 Empirical Thresholds Loader

Loads empirical confidence thresholds and scoring weights from corpus_thresholds_weights.json
for use in Phase 3 scorers. Provides calibrated thresholds validated on 14 real PDT plans.

Key Functions:
- load_empirical_thresholds: Load full corpus with all thresholds
- get_signal_confidence_threshold: Get min_confidence for a signal type
- get_phase3_scoring_weights: Get layer-specific weights (@b, @u, @q, @d, @p, @C, @chain)
- apply_confidence_boost: Apply empirical boosts (completeness, validation, hierarchy)

EMPIRICAL BASELINE: 14 PDT Colombia 2024-2027
SOURCE: canonic_questionnaire_central/scoring/calibration/empirical_weights.json
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 3
__stage__ = 10
__order__ = 6
__author__ = "F.A.R.F.A.N Core Team - Empirical Corpus Integration"
__created__ = "2026-01-12"
__modified__ = "2026-01-12"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "EmpiricalThresholdsLoader",
    "load_empirical_thresholds",
    "get_signal_confidence_threshold",
    "get_phase3_scoring_weights",
]

# =============================================================================
# CORPUS LOADING
# =============================================================================


def load_empirical_thresholds(corpus_path: Path | str | None = None) -> dict[str, Any]:
    """Load empirical thresholds corpus from registry.

    Args:
        corpus_path: Optional path to empirical_weights.json.
                    Defaults to canonic_questionnaire_central/scoring/calibration/

    Returns:
        Parsed JSON corpus with signal thresholds and scoring weights

    Raises:
        FileNotFoundError: If corpus file not found
        json.JSONDecodeError: If corpus file is malformed
    """
    if corpus_path is None:
        # Default path: canonic_questionnaire_central/scoring/calibration/empirical_weights.json
        repo_root = Path(__file__).parents[4]  # src/farfan_pipeline/phases/Phase_3 -> repo root
        corpus_path = (
            repo_root
            / "canonic_questionnaire_central"
            / "scoring"
            / "calibration"
            / "empirical_weights.json"
        )

    corpus_path = Path(corpus_path)

    if not corpus_path.exists():
        raise FileNotFoundError(f"Empirical thresholds corpus not found: {corpus_path}")

    logger.info(f"Loading empirical thresholds corpus from: {corpus_path}")

    with corpus_path.open("r", encoding="utf-8") as f:
        corpus = json.load(f)

    logger.info(
        f"Loaded empirical thresholds v{corpus.get('calibration_config_version', 'unknown')} "
        f"from {corpus.get('empirical_baseline', 'unknown')}"
    )

    return corpus


# =============================================================================
# EMPIRICAL THRESHOLDS LOADER
# =============================================================================


class EmpiricalThresholdsLoader:
    """Loads and provides empirical thresholds for Phase 3 scoring.

    Attributes:
        corpus: Loaded empirical thresholds corpus
        signal_thresholds: Confidence thresholds per signal type
        phase3_weights: Scoring weights for Phase 3 layers
        aggregation_weights: Aggregation weights for Phases 4-7
        value_add_thresholds: Value-add thresholds for signal filtering
    """

    def __init__(self, corpus_path: Path | str | None = None):
        """Initialize loader with empirical thresholds corpus.

        Args:
            corpus_path: Optional path to empirical_weights.json
        """
        self.corpus = load_empirical_thresholds(corpus_path)
        self.signal_thresholds = self.corpus.get("signal_confidence_thresholds", {})
        self.phase3_weights = self.corpus.get("phase3_scoring_weights", {})
        self.aggregation_weights = self.corpus.get("aggregation_weights", {})
        self.value_add_thresholds = self.corpus.get("value_add_thresholds", {})

        logger.info(
            f"EmpiricalThresholdsLoader initialized: "
            f"{len(self.signal_thresholds)} signal types, "
            f"{len(self.phase3_weights)} Phase 3 layers"
        )

    def get_signal_confidence_threshold(
        self,
        signal_type: str,
        extraction_method: str = "default",
    ) -> float:
        """Get minimum confidence threshold for a signal type.

        Args:
            signal_type: Signal type (e.g., "QUANTITATIVE_TRIPLET")
            extraction_method: Extraction method (e.g., "from_table", "from_text")

        Returns:
            Minimum confidence threshold (0.0-1.0), defaults to 0.75
        """
        signal_config = self.signal_thresholds.get(signal_type, {})

        # Try extraction method-specific threshold
        method_config = signal_config.get(extraction_method, {})
        if method_config:
            threshold = method_config.get("min_confidence")
            if threshold is not None:
                return float(threshold)

        # Fallback: Try to find any threshold in signal_config
        for method, config in signal_config.items():
            if isinstance(config, dict) and "min_confidence" in config:
                threshold = config.get("min_confidence")
                logger.debug(
                    f"Using fallback threshold for {signal_type}.{extraction_method}: "
                    f"{threshold} (from {method})"
                )
                return float(threshold)

        # Default threshold
        logger.debug(f"Using default threshold for {signal_type}.{extraction_method}: 0.75")
        return 0.75

    def get_confidence_boost(
        self,
        signal_type: str,
        boost_type: str,
    ) -> float:
        """Get confidence boost factor for a signal type.

        Args:
            signal_type: Signal type (e.g., "QUANTITATIVE_TRIPLET")
            boost_type: Boost type (e.g., "completeness_boost", "validated_closure")

        Returns:
            Boost factor (typically 1.0-1.3), defaults to 1.0
        """
        signal_config = self.signal_thresholds.get(signal_type, {})
        boost_config = signal_config.get(boost_type, {})

        # Handle different boost formats
        if isinstance(boost_config, dict):
            # Format 1: {"boost": 1.20, "conditions": "..."}
            if "boost" in boost_config:
                return float(boost_config["boost"])
            # Format 2: {"value": 1.30, "conditions": "..."}
            if "value" in boost_config:
                return float(boost_config["value"])
            # Format 3: {"COMPLETO": 1.0, "ALTO": 0.95, ...}
            # Return dict for caller to resolve specific key
            return boost_config

        # Scalar boost value
        if isinstance(boost_config, (int, float)):
            return float(boost_config)

        # Default: no boost
        return 1.0

    def get_phase3_layer_weights(self, layer: str) -> dict[str, float]:
        """Get scoring weights for a Phase 3 layer.

        Args:
            layer: Layer name (e.g., "layer_b_baseline", "layer_q_quality")

        Returns:
            Dict of component weights for the layer
        """
        layer_weights = self.phase3_weights.get(layer, {})

        # Filter out non-weight keys (e.g., "note", "required_sections")
        weights = {
            k: v
            for k, v in layer_weights.items()
            if isinstance(v, (int, float)) and not k.startswith("_")
        }

        return weights

    def get_aggregation_weights(self, phase: str) -> dict[str, Any]:
        """Get aggregation weights for a specific phase.

        Args:
            phase: Phase name (e.g., "phase4_dimension_aggregation",
                   "phase5_policy_area_aggregation")

        Returns:
            Aggregation weights dict for the phase
        """
        return self.aggregation_weights.get(phase, {})

    def get_value_add_threshold(self, signal_type: str) -> float:
        """Get value-add threshold for a signal type.

        Args:
            signal_type: Signal type (e.g., "QUANTITATIVE_TRIPLET_complete")

        Returns:
            Value-add threshold (delta_score improvement required)
        """
        high_value = self.value_add_thresholds.get("high_value_signals", {})
        low_value = self.value_add_thresholds.get("low_value_signals", {})
        minimum = self.value_add_thresholds.get("minimum_value_add", {})

        # Check high-value signals
        if signal_type in high_value:
            return float(high_value[signal_type])

        # Check low-value signals
        if signal_type in low_value:
            return float(low_value[signal_type])

        # Default minimum value-add
        return float(minimum.get("delta_score", 0.05))

    def validate_signal_confidence(
        self,
        signal_type: str,
        confidence: float,
        extraction_method: str = "default",
    ) -> bool:
        """Validate if signal confidence meets empirical threshold.

        Args:
            signal_type: Signal type
            confidence: Signal confidence (0.0-1.0)
            extraction_method: Extraction method

        Returns:
            True if confidence >= threshold, False otherwise
        """
        threshold = self.get_signal_confidence_threshold(signal_type, extraction_method)
        return confidence >= threshold


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_signal_confidence_threshold(
    signal_type: str,
    extraction_method: str = "default",
    corpus_path: Path | str | None = None,
) -> float:
    """Convenience function to get signal confidence threshold.

    Args:
        signal_type: Signal type
        extraction_method: Extraction method
        corpus_path: Optional path to empirical_weights.json

    Returns:
        Minimum confidence threshold
    """
    loader = EmpiricalThresholdsLoader(corpus_path=corpus_path)
    return loader.get_signal_confidence_threshold(signal_type, extraction_method)


def get_phase3_scoring_weights(
    layer: str,
    corpus_path: Path | str | None = None,
) -> dict[str, float]:
    """Convenience function to get Phase 3 layer weights.

    Args:
        layer: Layer name (e.g., "layer_b_baseline")
        corpus_path: Optional path to empirical_weights.json

    Returns:
        Layer weights dict
    """
    loader = EmpiricalThresholdsLoader(corpus_path=corpus_path)
    return loader.get_phase3_layer_weights(layer)


# =============================================================================
# SINGLETON INSTANCE (LAZY LOAD)
# =============================================================================

_global_loader: EmpiricalThresholdsLoader | None = None


def get_global_thresholds_loader(corpus_path: Path | str | None = None) -> EmpiricalThresholdsLoader:
    """Get global singleton EmpiricalThresholdsLoader instance.

    Args:
        corpus_path: Optional path to empirical_weights.json

    Returns:
        Global EmpiricalThresholdsLoader instance
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = EmpiricalThresholdsLoader(corpus_path=corpus_path)
    return _global_loader
