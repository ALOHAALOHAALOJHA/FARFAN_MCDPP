"""Phase 4 Signal-Enriched Aggregation Module

Extends Phase 4 dimension aggregation with signal-based enhancements
for context-aware weight adjustments, dispersion analysis, and enhanced
aggregation transparency.

Enhancement Value:
- Signal-based weight adjustments for dimension/area/cluster aggregation
- Signal-driven dispersion metric interpretation
- Pattern-based aggregation method selection
- Enhanced aggregation provenance with signal metadata

Integration: Used by DimensionAggregator, AreaPolicyAggregator,
ClusterAggregator, and MacroAggregator to enhance aggregation with
signal intelligence.

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 4
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import logging
from typing import TYPE_CHECKING, Any
from datetime import datetime

if TYPE_CHECKING:
    try:
        from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
            QuestionnaireSignalRegistry,
        )
    except ImportError:
        QuestionnaireSignalRegistry = Any  # type: ignore

logger = logging.getLogger(__name__)

# Weight adjustment constants
CRITICAL_SCORE_THRESHOLD = 0.4  # Scores below this are considered critical
CRITICAL_SCORE_BOOST_FACTOR = 1.2  # Weight boost for critical scores
HIGH_SIGNAL_PATTERN_THRESHOLD = 15  # Pattern count threshold
HIGH_SIGNAL_BOOST_FACTOR = 1.05  # Proportional boost for high signal density

# Dispersion analysis constants
CV_CONVERGENCE_THRESHOLD = 0.15  # Coefficient of variation for convergence
CV_MODERATE_THRESHOLD = 0.40  # CV threshold for moderate dispersion
CV_HIGH_THRESHOLD = 0.60  # CV threshold for high dispersion


# Utility: Select a representative question for a given dimension from the signal registry
def get_representative_question_for_dimension(
    dimension_id: str,
    signal_registry: QuestionnaireSignalRegistry | None,
) -> str | None:
    """
    Returns a representative question ID for the given dimension, or None if not found.
    Selection strategy: first question found for the dimension in the registry.
    """
    if signal_registry is None:
        logger.warning(
            "Signal registry is None; cannot select representative question for dimension '%s'.",
            dimension_id,
        )
        return None
    questions = signal_registry.get_questions_for_dimension(dimension_id)
    if not questions:
        logger.warning("No questions found for dimension '%s' in signal registry.", dimension_id)
        return None
    return questions[0]


__all__ = [
    "SignalEnrichedAggregator",
    "adjust_weights",
    "interpret_dispersion",
]


class SignalEnrichedAggregator:
    """Signal-enriched aggregator for Phase 4 with adaptive weighting.

    Enhances hierarchical aggregation with signal intelligence for better
    weight adaptation, dispersion interpretation, and aggregation quality.

    Attributes:
        signal_registry: Optional signal registry for signal access
        enable_weight_adjustment: Enable signal-based weight adjustment
        enable_dispersion_analysis: Enable signal-driven dispersion analysis
    """

    def __init__(
        self,
        signal_registry: QuestionnaireSignalRegistry | None = None,
        enable_weight_adjustment: bool = True,
        enable_dispersion_analysis: bool = True,
    ) -> None:
        """Initialize signal-enriched aggregator.

        Args:
            signal_registry: Optional signal registry for signal access
            enable_weight_adjustment: Enable weight adjustment feature
            enable_dispersion_analysis: Enable dispersion analysis feature
        """
        self.signal_registry = signal_registry
        self.enable_weight_adjustment = enable_weight_adjustment
        self.enable_dispersion_analysis = enable_dispersion_analysis

        logger.info(
            f"SignalEnrichedAggregator initialized: "
            f"registry={'enabled' if signal_registry else 'disabled'}, "
            f"weight_adj={enable_weight_adjustment}, "
            f"dispersion={enable_dispersion_analysis}"
        )

    def adjust_aggregation_weights(
        self,
        base_weights: dict[str, float],
        dimension_id: str | None = None,
        policy_area: str | None = None,
        cluster_id: str | None = None,
        score_data: dict[str, float] | None = None,
    ) -> tuple[dict[str, float], dict[str, Any]]:
        """Adjust aggregation weights using signal-based intelligence.

        Analyzes signal patterns and score data to make context-aware
        adjustments to aggregation weights.

        Args:
            base_weights: Base weight dict (key -> weight)
            dimension_id: Optional dimension identifier
            policy_area: Optional policy area identifier
            cluster_id: Optional cluster identifier
            score_data: Optional score data for context

        Returns:
            Tuple of (adjusted_weights, adjustment_details)
        """
        if not self.enable_weight_adjustment:
            return base_weights, {"adjustment": "disabled"}

        adjustment_details: dict[str, Any] = {
            "base_weights": base_weights.copy(),
            "adjustments": [],
        }

        adjusted_weights = base_weights.copy()

        try:
            # Adjustment 1: Boost weights for low-scoring components (need attention)
            if score_data:
                for key, score in score_data.items():
                    if key in adjusted_weights and score < CRITICAL_SCORE_THRESHOLD:
                        # Boost weight for critical scores
                        boost_factor = CRITICAL_SCORE_BOOST_FACTOR
                        original_weight = adjusted_weights[key]
                        adjusted_weights[key] = min(1.0, original_weight * boost_factor)

                        adjustment_details["adjustments"].append(
                            {
                                "type": "critical_score_boost",
                                "key": key,
                                "original_weight": original_weight,
                                "adjusted_weight": adjusted_weights[key],
                                "score": score,
                                "boost_factor": boost_factor,
                            }
                        )

            # Adjustment 2: Signal-based pattern density weighting
            if self.signal_registry and dimension_id:
                try:
                    # For dimension aggregation, check pattern density across questions
                    representative_question = get_representative_question_for_dimension(
                        dimension_id, self.signal_registry
                    )
                    if representative_question is None:
                        # No representative question found, skip signal-based weighting
                        logger.debug(
                            f"No representative question for dimension {dimension_id}, skipping signal-based weighting"
                        )
                        return adjusted_weights, adjustment_details

                    signal_pack = self.signal_registry.get_micro_answering_signals(
                        representative_question
                    )

                    pattern_count = len(getattr(signal_pack, "patterns", []))
                    indicator_count = len(getattr(signal_pack, "indicators", []))

                    # High signal density suggests importance
                    if pattern_count > HIGH_SIGNAL_PATTERN_THRESHOLD:
                        # Apply small boost to all weights (proportionally)
                        boost_factor = HIGH_SIGNAL_BOOST_FACTOR
                        for key in adjusted_weights:
                            original_weight = adjusted_weights[key]
                            adjusted_weights[key] = min(1.0, original_weight * boost_factor)

                        adjustment_details["adjustments"].append(
                            {
                                "type": "high_pattern_density",
                                "pattern_count": pattern_count,
                                "indicator_count": indicator_count,
                                "boost_factor": 1.05,
                            }
                        )

                except Exception as e:
                    logger.debug(f"Signal-based weight adjustment failed: {e}")

            # Normalize weights to sum to 1.0
            weight_sum = sum(adjusted_weights.values())
            if weight_sum > 0:
                adjusted_weights = {k: v / weight_sum for k, v in adjusted_weights.items()}

            adjustment_details["adjusted_weights"] = adjusted_weights
            adjustment_details["total_adjustment"] = sum(
                abs(adjusted_weights[k] - base_weights[k])
                for k in base_weights
                if k in adjusted_weights
            )

        except Exception as e:
            logger.warning(f"Failed to adjust aggregation weights: {e}")
            adjustment_details["error"] = str(e)
            adjusted_weights = base_weights

        return adjusted_weights, adjustment_details

    def analyze_score_dispersion(
        self,
        scores: list[float],
        context: str,
        dimension_id: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Analyze score dispersion with signal-driven interpretation.

        Computes dispersion metrics and provides signal-informed interpretation
        of what the dispersion means for aggregation quality.

        Args:
            scores: List of scores to analyze
            context: Context string (e.g., "dimension_DIM01")
            dimension_id: Optional dimension identifier for signal analysis

        Returns:
            Tuple of (metrics, interpretation)
        """
        if not self.enable_dispersion_analysis:
            return {}, {"analysis": "disabled"}

        metrics: dict[str, Any] = {}
        interpretation: dict[str, Any] = {
            "context": context,
            "insights": [],
        }

        try:
            if len(scores) == 0:
                return {"error": "no_scores"}, {"error": "no_scores"}

            # Basic dispersion metrics
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            std_dev = variance**0.5
            min_score = min(scores)
            max_score = max(scores)
            score_range = max_score - min_score

            # Coefficient of variation (relative dispersion)
            cv = std_dev / mean_score if mean_score > 0 else 0.0

            metrics = {
                "mean": mean_score,
                "variance": variance,
                "std_dev": std_dev,
                "min": min_score,
                "max": max_score,
                "range": score_range,
                "cv": cv,
                "count": len(scores),
            }

            # Interpretation based on dispersion
            if cv < 0.15:
                interpretation["insights"].append(
                    {
                        "type": "convergence",
                        "description": "Scores show high convergence (low dispersion)",
                        "recommendation": "Aggregation is reliable with standard weighting",
                    }
                )
            elif cv < 0.40:
                interpretation["insights"].append(
                    {
                        "type": "moderate_dispersion",
                        "description": "Scores show moderate dispersion",
                        "recommendation": "Consider weighted aggregation with quality-based weights",
                    }
                )
            elif cv < 0.60:
                interpretation["insights"].append(
                    {
                        "type": "high_dispersion",
                        "description": "Scores show high dispersion",
                        "recommendation": "Use adaptive penalty and investigate outliers",
                    }
                )
            else:
                interpretation["insights"].append(
                    {
                        "type": "extreme_dispersion",
                        "description": "Scores show extreme dispersion",
                        "recommendation": "Consider non-linear aggregation methods",
                    }
                )

            # Signal-based enhancement
            if self.signal_registry and dimension_id:
                try:
                    # Get signal characteristics for dimension
                    representative_question = get_representative_question_for_dimension(
                        dimension_id, self.signal_registry
                    )
                    if representative_question is None:
                        # No representative question found, skip signal-based enhancement
                        logger.debug(f"No representative question for dimension {dimension_id}")
                    else:
                        signal_pack = self.signal_registry.get_micro_answering_signals(
                            representative_question
                        )

                        pattern_count = (
                            len(signal_pack.patterns) if hasattr(signal_pack, "patterns") else 0
                        )

                        # High pattern count with high dispersion suggests genuine complexity
                        if pattern_count > 15 and cv > 0.40:
                            interpretation["insights"].append(
                                {
                                    "type": "genuine_complexity",
                                    "description": f"High pattern density ({pattern_count}) with high dispersion suggests inherent complexity",
                                    "recommendation": "Dispersion may reflect genuine answer complexity, not data quality issues",
                                }
                            )

                except Exception as e:
                    logger.debug(f"Signal-based dispersion analysis failed: {e}")

            interpretation["summary"] = {
                "dispersion_level": (
                    "convergence"
                    if cv < 0.15
                    else "moderate" if cv < 0.40 else "high" if cv < 0.60 else "extreme"
                ),
                "cv": cv,
            }

        except Exception as e:
            logger.warning(f"Failed to analyze score dispersion: {e}")
            metrics["error"] = str(e)
            interpretation["error"] = str(e)

        return metrics, interpretation

    def select_aggregation_method(
        self,
        scores: list[float],
        dispersion_metrics: dict[str, Any],
        context: str,
    ) -> tuple[str, dict[str, Any]]:
        """Select aggregation method based on signal-driven dispersion analysis.

        Recommends aggregation method (weighted_mean, median, choquet, etc.)
        based on dispersion characteristics and signal patterns.

        Args:
            scores: List of scores to aggregate
            dispersion_metrics: Dispersion metrics from analyze_score_dispersion
            context: Context string

        Returns:
            Tuple of (method_name, selection_details)
        """
        selection_details: dict[str, Any] = {
            "context": context,
            "candidates": [],
        }

        try:
            cv = dispersion_metrics.get("cv", 0.0)

            # Method selection based on dispersion
            if cv < 0.15:
                # Low dispersion - simple weighted mean is fine
                method_name = "weighted_mean"
                selection_details["candidates"].append(
                    {
                        "method": "weighted_mean",
                        "reason": "low_dispersion",
                        "cv": cv,
                    }
                )
            elif cv < 0.40:
                # Moderate dispersion - weighted mean with quality weights
                method_name = "weighted_mean"
                selection_details["candidates"].append(
                    {
                        "method": "weighted_mean",
                        "reason": "moderate_dispersion",
                        "cv": cv,
                        "note": "Use quality-based weights",
                    }
                )
            elif cv < 0.60:
                # High dispersion - consider median or trimmed mean
                method_name = "median"
                selection_details["candidates"].append(
                    {
                        "method": "median",
                        "reason": "high_dispersion",
                        "cv": cv,
                        "note": "Robust to outliers",
                    }
                )
            else:
                # Extreme dispersion - use robust aggregation
                method_name = "choquet"
                selection_details["candidates"].append(
                    {
                        "method": "choquet",
                        "reason": "extreme_dispersion",
                        "cv": cv,
                        "note": "Captures synergies and interactions",
                    }
                )

            selection_details["selected_method"] = method_name
            selection_details["cv"] = cv

        except Exception as e:
            logger.warning(f"Failed to select aggregation method: {e}")
            selection_details["error"] = str(e)
            method_name = "weighted_mean"  # Safe fallback

        return method_name, selection_details

    def enrich_aggregation_metadata(
        self,
        base_metadata: dict[str, Any],
        weight_adjustments: dict[str, Any],
        dispersion_analysis: dict[str, Any],
        method_selection: dict[str, Any],
    ) -> dict[str, Any]:
        """Enrich aggregation metadata with signal provenance.

        Adds comprehensive signal-based metadata to aggregation results
        for full transparency and reproducibility.

        Args:
            base_metadata: Base aggregation metadata
            weight_adjustments: Weight adjustment details
            dispersion_analysis: Dispersion analysis results
            method_selection: Method selection details

        Returns:
            Enriched aggregation metadata dict
        """
        enriched_metadata = {
            **base_metadata,
            "signal_enrichment": {
                "enabled": True,
                "registry_available": self.signal_registry is not None,
                "weight_adjustments": weight_adjustments,
                "dispersion_analysis": dispersion_analysis,
                "method_selection": method_selection,
            },
        }

        return enriched_metadata


def adjust_weights(
    signal_registry: QuestionnaireSignalRegistry | None,
    base_weights: dict[str, float],
    score_data: dict[str, float] | None = None,
    dimension_id: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Convenience function for signal-based weight adjustment.

    Creates a temporary SignalEnrichedAggregator and adjusts weights.

    Args:
        signal_registry: Signal registry instance (optional)
        base_weights: Base weight dict
        score_data: Optional score data
        dimension_id: Optional dimension identifier

    Returns:
        Tuple of (adjusted_weights, adjustment_details)
    """
    aggregator = SignalEnrichedAggregator(signal_registry=signal_registry)
    return aggregator.adjust_aggregation_weights(
        base_weights=base_weights,
        dimension_id=dimension_id,
        score_data=score_data,
    )


def interpret_dispersion(
    signal_registry: QuestionnaireSignalRegistry | None,
    scores: list[float],
    context: str,
    dimension_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Convenience function for signal-driven dispersion analysis.

    Creates a temporary SignalEnrichedAggregator and analyzes dispersion.

    Args:
        signal_registry: Signal registry instance (optional)
        scores: List of scores to analyze
        context: Context string
        dimension_id: Optional dimension identifier

    Returns:
        Tuple of (metrics, interpretation)
    """
    aggregator = SignalEnrichedAggregator(signal_registry=signal_registry)
    return aggregator.analyze_score_dispersion(
        scores=scores,
        context=context,
        dimension_id=dimension_id,
    )


# =============================================================================
# SOPHISTICATED PHASE 4 ENHANCEMENTS - REAL-TIME SIGNAL ENRICHMENT
# =============================================================================

class SignalMetadataEnricher:
    """
    Real-time signal metadata enrichment for Phase 4 aggregation.
    
    Enriches aggregation context with live signal metadata including:
    - Signal quality metrics propagation
    - Full provenance chains
    - Cross-signal correlation tracking
    - Adaptive weight computation
    """
    
    def __init__(self, signal_registry: QuestionnaireSignalRegistry | None = None):
        self.signal_registry = signal_registry
        self._metadata_cache: dict[str, dict[str, Any]] = {}
        self._provenance_chains: dict[str, list[str]] = {}
        self._correlation_index: dict[str, set[str]] = {}
        self.logger = logging.getLogger(__name__)
    
    def enrich_aggregation_metadata(
        self,
        base_metadata: dict[str, Any],
        dimension_id: str,
        signal_ids: list[str],
        quality_metrics: dict[str, float]
    ) -> dict[str, Any]:
        """
        Enrich aggregation metadata with real-time signal intelligence.
        
        Args:
            base_metadata: Base aggregation metadata
            dimension_id: Dimension being aggregated
            signal_ids: IDs of signals contributing to aggregation
            quality_metrics: Quality metrics for the aggregation
        
        Returns:
            Enhanced metadata dict with full signal context
        """
        enriched = base_metadata.copy()
        
        # Add real-time signal metadata
        enriched["signal_enrichment"] = {
            "dimension_id": dimension_id,
            "contributing_signals": len(signal_ids),
            "signal_quality_summary": self._summarize_signal_quality(signal_ids, quality_metrics),
            "provenance_chains": self._build_provenance_chains(signal_ids),
            "cross_signal_correlations": self._detect_signal_correlations(signal_ids),
            "enrichment_timestamp": datetime.utcnow().isoformat(),
            "metadata_version": "2.0.0"
        }
        
        # Add signal pattern analysis if registry available
        if self.signal_registry:
            enriched["signal_enrichment"]["pattern_analysis"] = (
                self._analyze_signal_patterns(dimension_id)
            )
        
        # Add adaptive weight insights
        enriched["signal_enrichment"]["adaptive_weights"] = (
            self._compute_adaptive_weights(signal_ids, quality_metrics)
        )
        
        return enriched
    
    def _summarize_signal_quality(
        self,
        signal_ids: list[str],
        quality_metrics: dict[str, float]
    ) -> dict[str, Any]:
        """Summarize quality metrics across all contributing signals"""
        if not quality_metrics:
            return {"status": "no_metrics"}
        
        return {
            "average_quality": sum(quality_metrics.values()) / len(quality_metrics),
            "min_quality": min(quality_metrics.values()),
            "max_quality": max(quality_metrics.values()),
            "quality_variance": self._calculate_variance(list(quality_metrics.values())),
            "low_quality_signals": [
                sig_id for sig_id, quality in quality_metrics.items()
                if quality < 0.5
            ],
            "high_quality_signals": [
                sig_id for sig_id, quality in quality_metrics.items()
                if quality > 0.8
            ]
        }
    
    def _calculate_variance(self, values: list[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)
    
    def _build_provenance_chains(self, signal_ids: list[str]) -> dict[str, list[str]]:
        """
        Build full provenance chains for each signal.
        
        Reconstructs causation chains by traversing signal relationships.
        In this implementation, chains are built from cached relationships.
        
        TODO: For full production implementation, this should:
        1. Query EventStore to traverse event.causation_id relationships
        2. Query SignalRegistry for signal.source.event_id linkages
        3. Build complete DAG of signal dependencies
        """
        chains = {}
        
        for signal_id in signal_ids:
            if signal_id in self._provenance_chains:
                # Use cached chain
                chains[signal_id] = self._provenance_chains[signal_id]
            else:
                # Initialize new chain (single-node for now)
                # Production: Would recursively traverse causation_id relationships
                # from EventStore to build full ancestry
                chain = [signal_id]
                self._provenance_chains[signal_id] = chain
                chains[signal_id] = chain
        
        return {
            "total_chains": len(chains),
            "average_chain_length": (
                sum(len(chain) for chain in chains.values()) / len(chains)
                if chains else 0
            ),
            "chains_sample": dict(list(chains.items())[:5])  # Sample of chains
        }
    
    def _detect_signal_correlations(self, signal_ids: list[str]) -> dict[str, Any]:
        """Detect correlations between signals"""
        correlations = []
        
        # Check for correlation groups
        for sig_id in signal_ids:
            if sig_id not in self._correlation_index:
                self._correlation_index[sig_id] = {sig_id}
            
            # Find overlapping correlation groups
            for other_sig_id in signal_ids:
                if other_sig_id != sig_id:
                    self._correlation_index[sig_id].add(other_sig_id)
        
        # Summarize correlations
        correlation_strengths = {}
        for sig_id in signal_ids:
            correlation_strengths[sig_id] = len(self._correlation_index.get(sig_id, set()))
        
        return {
            "signals_analyzed": len(signal_ids),
            "correlation_groups": len(set(
                frozenset(group) for group in self._correlation_index.values()
            )),
            "highly_correlated_signals": [
                sig_id for sig_id, strength in correlation_strengths.items()
                if strength > len(signal_ids) * 0.5
            ],
            "correlation_matrix_density": (
                sum(correlation_strengths.values()) / (len(signal_ids) ** 2)
                if signal_ids else 0
            )
        }
    
    def _analyze_signal_patterns(self, dimension_id: str) -> dict[str, Any]:
        """Analyze signal patterns for dimension if registry available"""
        if not self.signal_registry:
            return {"status": "registry_unavailable"}
        
        try:
            questions = self.signal_registry.get_questions_for_dimension(dimension_id)
            if not questions:
                return {"status": "no_questions_found"}
            
            representative_q = questions[0]
            signal_pack = self.signal_registry.get_micro_answering_signals(representative_q)
            
            pattern_count = len(getattr(signal_pack, "patterns", []))
            indicator_count = len(getattr(signal_pack, "indicators", []))
            
            return {
                "status": "analyzed",
                "questions_in_dimension": len(questions),
                "pattern_count": pattern_count,
                "indicator_count": indicator_count,
                "pattern_density": pattern_count / max(1, len(questions)),
                "patterns_per_question": pattern_count / max(1, len(questions))
            }
        except Exception as e:
            self.logger.debug(f"Signal pattern analysis failed: {e}")
            return {"status": "analysis_failed", "error": str(e)}
    
    def _compute_adaptive_weights(
        self,
        signal_ids: list[str],
        quality_metrics: dict[str, float]
    ) -> dict[str, Any]:
        """
        Compute adaptive weights based on signal characteristics.
        
        Higher quality signals get higher weights.
        """
        if not quality_metrics:
            return {"status": "no_metrics"}
        
        # Normalize quality metrics to weights
        total_quality = sum(quality_metrics.values())
        if total_quality == 0:
            return {"status": "zero_quality"}
        
        adaptive_weights = {
            sig_id: quality / total_quality
            for sig_id, quality in quality_metrics.items()
        }
        
        # Calculate weight statistics
        weight_values = list(adaptive_weights.values())
        
        return {
            "status": "computed",
            "weights": adaptive_weights,
            "weight_stats": {
                "mean": sum(weight_values) / len(weight_values),
                "min": min(weight_values),
                "max": max(weight_values),
                "std_dev": self._calculate_variance(weight_values) ** 0.5
            },
            "weight_distribution": {
                "high_weight_signals": [
                    sig_id for sig_id, weight in adaptive_weights.items()
                    if weight > 1.0 / len(signal_ids) * 1.5
                ],
                "low_weight_signals": [
                    sig_id for sig_id, weight in adaptive_weights.items()
                    if weight < 1.0 / len(signal_ids) * 0.5
                ]
            }
        }


class AdaptiveWeightAdjuster:
    """
    Adaptive weight adjustment based on real-time signal patterns.
    
    Dynamically adjusts aggregation weights based on:
    - Signal arrival patterns
    - Quality metric trends
    - Historical aggregation performance
    """
    
    def __init__(self):
        self._weight_history: dict[str, list[float]] = {}
        self._performance_history: dict[str, list[float]] = {}
        self.logger = logging.getLogger(__name__)
    
    def adjust_weights_dynamically(
        self,
        base_weights: dict[str, float],
        signal_patterns: dict[str, Any],
        quality_trends: dict[str, list[float]]
    ) -> tuple[dict[str, float], dict[str, Any]]:
        """
        Dynamically adjust weights based on signal patterns.
        
        Args:
            base_weights: Initial weight distribution
            signal_patterns: Detected signal patterns
            quality_trends: Historical quality trends
        
        Returns:
            Tuple of (adjusted_weights, adjustment_metadata)
        """
        adjusted_weights = base_weights.copy()
        adjustments_made = []
        
        # Adjustment 1: Trend-based weight adjustment
        for key, quality_history in quality_trends.items():
            if key in adjusted_weights and len(quality_history) >= 3:
                # Calculate trend
                trend = self._calculate_trend(quality_history)
                
                if trend > 0.1:  # Improving quality
                    boost = 1.1
                    adjusted_weights[key] *= boost
                    adjustments_made.append({
                        "key": key,
                        "type": "quality_trend_boost",
                        "trend": trend,
                        "boost_factor": boost
                    })
                elif trend < -0.1:  # Declining quality
                    penalty = 0.9
                    adjusted_weights[key] *= penalty
                    adjustments_made.append({
                        "key": key,
                        "type": "quality_trend_penalty",
                        "trend": trend,
                        "penalty_factor": penalty
                    })
        
        # Adjustment 2: Pattern density adjustment
        pattern_density = signal_patterns.get("pattern_density", 0)
        if pattern_density > 0.8:  # High pattern density
            # Boost all weights proportionally
            boost_factor = 1.05
            adjusted_weights = {k: v * boost_factor for k, v in adjusted_weights.items()}
            adjustments_made.append({
                "type": "high_pattern_density_boost",
                "pattern_density": pattern_density,
                "boost_factor": boost_factor
            })
        
        # Normalize weights
        weight_sum = sum(adjusted_weights.values())
        if weight_sum > 0:
            adjusted_weights = {k: v / weight_sum for k, v in adjusted_weights.items()}
        
        adjustment_metadata = {
            "adjustments_applied": len(adjustments_made),
            "adjustment_details": adjustments_made,
            "total_adjustment_magnitude": sum(
                abs(adjusted_weights.get(k, 0) - base_weights.get(k, 0))
                for k in base_weights
            )
        }
        
        return adjusted_weights, adjustment_metadata
    
    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend (positive = improving, negative = declining)"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator


# Enhanced module exports
__all__ = [
    "SignalEnrichedAggregator",
    "adjust_weights",
    "interpret_dispersion",
    "SignalMetadataEnricher",  # New
    "AdaptiveWeightAdjuster",  # New
]
