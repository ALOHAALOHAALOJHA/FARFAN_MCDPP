"""
Phase6 Cluster Consumer - MESO Level Signal Consumption

This consumer handles SISAS signal irrigation for Phase 6 cluster aggregation.
It processes uncertainty, confidence, and aggregation signals from Phase 5 to
inform MESO-level cluster scoring with signal-based adjustments.

Enhanced Features:
- Consumes uncertainty signals from Phase 5 for cluster penalty modulation
- Consumes confidence signals for area weight adjustment
- Consumes aggregation signals for cross-cluster coherence analysis
- Maintains signal contexts for ClusterAggregator integration
- Provides cluster-level signal summaries

Module: src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase6/phase6_cluster_consumer.py
Phase: 6 (Cluster Aggregation - MESO)
Owner: phase6_sisas
Version: 2.0.0
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..base_consumer import BaseConsumer
from ...core.signal import Signal, SignalType, SignalContext, SignalSource

logger = logging.getLogger(__name__)


# =============================================================================
# SIGNAL CONTEXT STORAGE FOR CLUSTER AGGREGATOR
# =============================================================================

@dataclass
class ClusterSignalContext:
    """
    Signal context for a specific cluster.

    Stores aggregated signals that influence cluster scoring:
    - Uncertainty signals from Phase 5 area scoring
    - Confidence signals from dimension aggregation
    - Coherence signals for cluster internal alignment
    """
    cluster_id: str
    uncertainty_signals: Dict[str, float] = field(default_factory=dict)  # area_id -> uncertainty
    confidence_signals: Dict[str, float] = field(default_factory=dict)  # area_id -> confidence
    coherence_signals: Dict[str, float] = field(default_factory=dict)  # area_id -> coherence
    signal_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    aggregate_confidence: float = 1.0
    aggregate_uncertainty: float = 0.0

    def compute_signal_adjustment(self) -> float:
        """
        Compute signal-based adjustment factor for cluster score.

        Formula:
            adjustment = 1.0 - (uncertainty_penalty - confidence_boost)

        Where:
            uncertainty_penalty = avg_uncertainty * 0.3 (max 15%)
            confidence_boost = (avg_confidence - 1.0) * 0.15 (max ±10%)

        Returns:
            Adjustment factor in [0.8, 1.2]
        """
        if not self.uncertainty_signals and not self.confidence_signals:
            return 1.0

        # Compute uncertainty penalty
        uncertainty_penalty = 0.0
        if self.uncertainty_signals:
            avg_uncertainty = sum(self.uncertainty_signals.values()) / len(self.uncertainty_signals)
            uncertainty_penalty = min(0.15, avg_uncertainty * 0.3)

        # Compute confidence boost
        confidence_boost = 0.0
        if self.confidence_signals:
            # Confidence is typically [0.5, 1.5], normalize to [-0.5, 0.5]
            avg_confidence = sum(self.confidence_signals.values()) / len(self.confidence_signals)
            confidence_boost = (avg_confidence - 1.0) * 0.15
            confidence_boost = max(-0.1, min(0.1, confidence_boost))

        # Coherence adjustment
        coherence_adjustment = 0.0
        if self.coherence_signals:
            avg_coherence = sum(self.coherence_signals.values()) / len(self.coherence_signals)
            if avg_coherence < 0.5:
                coherence_adjustment = -0.05  # Penalty for low coherence
            elif avg_coherence > 0.8:
                coherence_adjustment = 0.03  # Bonus for high coherence

        # Combine adjustments
        adjustment = 1.0 - uncertainty_penalty + confidence_boost + coherence_adjustment

        # Bound to reasonable range
        return max(0.8, min(1.2, adjustment))

    def update_aggregates(self) -> None:
        """Update aggregate confidence and uncertainty metrics."""
        if self.confidence_signals:
            self.aggregate_confidence = sum(self.confidence_signals.values()) / len(self.confidence_signals)
        if self.uncertainty_signals:
            self.aggregate_uncertainty = sum(self.uncertainty_signals.values()) / len(self.uncertainty_signals)
        self.last_updated = datetime.utcnow()


@dataclass
class Phase6ClusterConsumerConfig:
    """Configuration for Phase6ClusterConsumer."""

    enabled_signal_types: List[str] = field(default_factory=list)
    process_signals_asynchronously: bool = False
    max_batch_size: int = 100
    enable_signal_context_storage: bool = True
    cluster_ids: List[str] = field(default_factory=lambda: [
        "CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"
    ])

    def __post_init__(self):
        if not self.enabled_signal_types:
            self.enabled_signal_types = [
                'MESO_AGGREGATION',
                'MICRO_SCORE',  # From Phase 5
                'UNCERTAINTY_SIGNAL',  # From Phase 5 uncertainty consumer
                'CONFIDENCE_SIGNAL',  # From area scoring
                'COHERENCE_SIGNAL',  # From cluster analysis
            ]


class Phase6ClusterConsumer(BaseConsumer):
    """
    Sophisticated cluster aggregation consumer for Phase 6.

    This consumer handles SISAS signal irrigation for cluster aggregation,
    processing signals from Phase 5 that inform MESO-level cluster scoring.

    Signal Types Consumed:
        - MESO_AGGREGATION: High-level cluster aggregation events
        - MICRO_SCORE: Area score signals from Phase 5
        - UNCERTAINTY_SIGNAL: Uncertainty quantification signals
        - CONFIDENCE_SIGNAL: Confidence scores from validation
        - COHERENCE_SIGNAL: Internal cluster coherence signals

    Integration:
        - Maintains ClusterSignalContext for each cluster
        - Provides signal contexts to ClusterAggregator
        - Computes cluster-level signal adjustments
    """

    def __init__(self, config: Phase6ClusterConsumerConfig = None):
        """
        Initialize Phase6ClusterConsumer.

        Args:
            config: Configuration for this consumer
        """
        self.config = config or Phase6ClusterConsumerConfig()
        self.consumer_id = "phase6_cluster_consumer"
        self.consumer_phase = "phase6"
        self.subscribed_signal_types = self.config.enabled_signal_types

        # Signal storage for cluster contexts
        self._cluster_contexts: Dict[str, ClusterSignalContext] = {
            cluster_id: ClusterSignalContext(cluster_id=cluster_id)
            for cluster_id in self.config.cluster_ids
        }
        self._signal_buffer: List[Signal] = []
        self._area_to_cluster_map = self._build_area_to_cluster_map()

        logger.info(
            f"Phase6ClusterConsumer initialized with {len(self.subscribed_signal_types)} "
            f"signal types and {len(self._cluster_contexts)} cluster contexts"
        )

    def _build_area_to_cluster_map(self) -> Dict[str, str]:
        """Build mapping from area_id to cluster_id."""
        return {
            "PA01": "CLUSTER_MESO_1", "PA02": "CLUSTER_MESO_1", "PA03": "CLUSTER_MESO_1",
            "PA04": "CLUSTER_MESO_2", "PA05": "CLUSTER_MESO_2", "PA06": "CLUSTER_MESO_2",
            "PA07": "CLUSTER_MESO_3", "PA08": "CLUSTER_MESO_3",
            "PA09": "CLUSTER_MESO_4", "PA10": "CLUSTER_MESO_4",
        }

    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """
        Consume a signal from the irrigation system.

        Args:
            signal: Signal to consume

        Returns:
            Consumption result dict or None if signal type not subscribed
        """
        if signal.signal_type not in self.subscribed_signal_types:
            return None

        # Process signal based on type
        result = self._process_signal(signal)

        # Update statistics
        self.stats["processed"] += 1

        return {
            "consumer_id": self.consumer_id,
            "signal_type": signal.signal_type,
            "signal_id": signal.signal_id,
            "processed": True,
            "result": result,
        }

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Process signal - main entry point from BaseConsumer.

        Args:
            signal: Signal to process

        Returns:
            Processing result with cluster-level analysis
        """
        return self._process_signal(signal)

    def _process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Process signal based on its type with sophisticated analysis.

        Args:
            signal: Signal to process

        Returns:
            Processing result with cluster context updates
        """
        signal_type = signal.signal_type
        result = {
            "signal_type": signal_type,
            "timestamp": datetime.utcnow().isoformat(),
            "cluster_contexts_updated": [],
            "signal_value": None,
            "analysis": {},
        }

        # Extract cluster ID from signal context
        cluster_id = self._extract_cluster_id(signal)
        if cluster_id and cluster_id not in self._cluster_contexts:
            logger.warning(f"Unknown cluster_id: {cluster_id}, creating new context")
            self._cluster_contexts[cluster_id] = ClusterSignalContext(cluster_id=cluster_id)

        # Process based on signal type
        if signal_type == "UNCERTAINTY_SIGNAL":
            result.update(self._process_uncertainty_signal(signal, cluster_id))
        elif signal_type == "CONFIDENCE_SIGNAL":
            result.update(self._process_confidence_signal(signal, cluster_id))
        elif signal_type == "COHERENCE_SIGNAL":
            result.update(self._process_coherence_signal(signal, cluster_id))
        elif signal_type == "MICRO_SCORE":
            result.update(self._process_micro_score_signal(signal, cluster_id))
        elif signal_type == "MESO_AGGREGATION":
            result.update(self._process_meso_aggregation_signal(signal, cluster_id))
        else:
            result["analysis"]["status"] = "unhandled_signal_type"

        # Update cluster aggregates if context was modified
        if cluster_id and result.get("cluster_contexts_updated"):
            self._cluster_contexts[cluster_id].update_aggregates()

        return result

    def _extract_cluster_id(self, signal: Signal) -> Optional[str]:
        """Extract cluster_id from signal context or value."""
        # Try signal context first
        if signal.context and hasattr(signal.context, "node_id"):
            node_id = signal.context.node_id
            if node_id.startswith("CLUSTER_MESO_"):
                return node_id
            # Map area_id to cluster_id
            if node_id in self._area_to_cluster_map:
                return self._area_to_cluster_map[node_id]

        # Try signal value
        if hasattr(signal, "value") and isinstance(signal.value, dict):
            return signal.value.get("cluster_id")

        # Try metadata
        if hasattr(signal, "metadata") and isinstance(signal.metadata, dict):
            return signal.metadata.get("cluster_id")

        return None

    def _process_uncertainty_signal(self, signal: Signal, cluster_id: Optional[str]) -> Dict[str, Any]:
        """Process uncertainty signal from Phase 5."""
        if not cluster_id:
            return {"analysis": {"error": "No cluster_id found in uncertainty signal"}}

        # Extract uncertainty value
        uncertainty_value = 0.0
        if isinstance(signal.value, dict):
            uncertainty_value = signal.value.get("uncertainty_score", 0.0)
            area_id = signal.value.get("area_id")
        elif isinstance(signal.value, (int, float)):
            uncertainty_value = float(signal.value)
            area_id = signal.metadata.get("area_id") if hasattr(signal, "metadata") else None
        else:
            return {"analysis": {"error": f"Unknown uncertainty value format: {type(signal.value)}"}}

        # Store in cluster context
        if area_id:
            self._cluster_contexts[cluster_id].uncertainty_signals[area_id] = uncertainty_value

        return {
            "signal_value": uncertainty_value,
            "cluster_contexts_updated": [cluster_id] if area_id else [],
            "analysis": {
                "status": "processed",
                "area_id": area_id,
                "cluster_id": cluster_id,
                "uncertainty_level": "high" if uncertainty_value > 0.3 else "medium" if uncertainty_value > 0.15 else "low",
            }
        }

    def _process_confidence_signal(self, signal: Signal, cluster_id: Optional[str]) -> Dict[str, Any]:
        """Process confidence signal from validation."""
        if not cluster_id:
            return {"analysis": {"error": "No cluster_id found in confidence signal"}}

        # Extract confidence value
        confidence_value = 1.0
        if isinstance(signal.value, dict):
            confidence_value = signal.value.get("confidence", 1.0)
            area_id = signal.value.get("area_id")
        elif isinstance(signal.value, (int, float)):
            confidence_value = float(signal.value)
            area_id = signal.metadata.get("area_id") if hasattr(signal, "metadata") else None
        else:
            return {"analysis": {"error": f"Unknown confidence value format: {type(signal.value)}"}}

        # Store in cluster context
        if area_id:
            self._cluster_contexts[cluster_id].confidence_signals[area_id] = confidence_value

        return {
            "signal_value": confidence_value,
            "cluster_contexts_updated": [cluster_id] if area_id else [],
            "analysis": {
                "status": "processed",
                "area_id": area_id,
                "cluster_id": cluster_id,
                "confidence_level": "high" if confidence_value > 0.8 else "medium" if confidence_value > 0.6 else "low",
            }
        }

    def _process_coherence_signal(self, signal: Signal, cluster_id: Optional[str]) -> Dict[str, Any]:
        """Process coherence signal for cluster analysis."""
        if not cluster_id:
            return {"analysis": {"error": "No cluster_id found in coherence signal"}}

        # Extract coherence value
        coherence_value = 0.5
        if isinstance(signal.value, dict):
            coherence_value = signal.value.get("coherence", 0.5)
            area_id = signal.value.get("area_id")
        elif isinstance(signal.value, (int, float)):
            coherence_value = float(signal.value)
            area_id = signal.metadata.get("area_id") if hasattr(signal, "metadata") else None
        else:
            return {"analysis": {"error": f"Unknown coherence value format: {type(signal.value)}"}}

        # Store in cluster context
        if area_id:
            self._cluster_contexts[cluster_id].coherence_signals[area_id] = coherence_value

        return {
            "signal_value": coherence_value,
            "cluster_contexts_updated": [cluster_id] if area_id else [],
            "analysis": {
                "status": "processed",
                "area_id": area_id,
                "cluster_id": cluster_id,
                "coherence_level": "high" if coherence_value > 0.8 else "medium" if coherence_value > 0.5 else "low",
            }
        }

    def _process_micro_score_signal(self, signal: Signal, cluster_id: Optional[str]) -> Dict[str, Any]:
        """Process micro (area) score signal from Phase 5."""
        if not cluster_id:
            return {"analysis": {"error": "No cluster_id found in micro score signal"}}

        # Extract score and metadata
        score_value = 0.0
        area_id = None
        if isinstance(signal.value, dict):
            score_value = signal.value.get("score", 0.0)
            area_id = signal.value.get("area_id")
        elif isinstance(signal.value, (int, float)):
            score_value = float(signal.value)
            area_id = signal.metadata.get("area_id") if hasattr(signal, "metadata") else None

        return {
            "signal_value": score_value,
            "cluster_contexts_updated": [],
            "analysis": {
                "status": "processed",
                "area_id": area_id,
                "cluster_id": cluster_id,
                "score_level": "high" if score_value > 2.0 else "medium" if score_value > 1.0 else "low",
            }
        }

    def _process_meso_aggregation_signal(self, signal: Signal, cluster_id: Optional[str]) -> Dict[str, Any]:
        """Process MESO aggregation signal."""
        return {
            "signal_value": signal.value,
            "cluster_contexts_updated": [],
            "analysis": {
                "status": "processed",
                "cluster_id": cluster_id,
                "signal_type": "MESO_AGGREGATION",
            }
        }

    def consume_batch(self, signals: List[Signal]) -> List[Dict[str, Any]]:
        """
        Consume multiple signals in batch.

        Args:
            signals: List of signals to consume

        Returns:
            List of consumption results
        """
        results = []
        for signal in signals:
            result = self.consume(signal)
            if result:
                results.append(result)
        return results

    def flush_buffer(self) -> List[Dict[str, Any]]:
        """
        Flush the internal signal buffer.

        Returns:
            List of buffered consumption results
        """
        results = []
        for signal in self._signal_buffer:
            result = self.consume(signal)
            if result:
                results.append(result)
        self._signal_buffer.clear()
        return results

    # ========================================================================
    # CLUSTER AGGREGATOR INTEGRATION
    # ========================================================================

    def get_cluster_context(self, cluster_id: str) -> Optional[ClusterSignalContext]:
        """
        Get signal context for a specific cluster.

        This method is used by ClusterAggregator to retrieve SISAS signal
        information for cluster score adjustment.

        Args:
            cluster_id: Cluster identifier (e.g., "CLUSTER_MESO_1")

        Returns:
            ClusterSignalContext or None if not found
        """
        return self._cluster_contexts.get(cluster_id)

    def get_all_cluster_contexts(self) -> Dict[str, ClusterSignalContext]:
        """Get all cluster signal contexts."""
        return self._cluster_contexts.copy()

    def get_signal_adjustment_for_cluster(self, cluster_id: str) -> float:
        """
        Get signal-based adjustment factor for a cluster.

        This is the main integration point for ClusterAggregator.

        Args:
            cluster_id: Cluster identifier

        Returns:
            Adjustment factor in [0.8, 1.2]
        """
        context = self._cluster_contexts.get(cluster_id)
        if not context:
            return 1.0
        return context.compute_signal_adjustment()

    def get_cluster_summary(self, cluster_id: str) -> Dict[str, Any]:
        """
        Get summary of signal context for a cluster.

        Args:
            cluster_id: Cluster identifier

        Returns:
            Summary dictionary with signal statistics
        """
        context = self._cluster_contexts.get(cluster_id)
        if not context:
            return {"error": f"Cluster {cluster_id} not found"}

        return {
            "cluster_id": cluster_id,
            "signal_count": context.signal_count,
            "aggregate_confidence": round(context.aggregate_confidence, 4),
            "aggregate_uncertainty": round(context.aggregate_uncertainty, 4),
            "adjustment_factor": round(context.compute_signal_adjustment(), 4),
            "areas_with_uncertainty": list(context.uncertainty_signals.keys()),
            "areas_with_confidence": list(context.confidence_signals.keys()),
            "areas_with_coherence": list(context.coherence_signals.keys()),
            "last_updated": context.last_updated.isoformat(),
        }

    # ========================================================================
    # CONTRACT AND STATUS
    # ========================================================================

    def get_consumption_contract(self) -> Dict[str, Any]:
        """
        Get the consumption contract for this consumer.

        Returns:
            Dict with contract details
        """
        return {
            "consumer_id": self.consumer_id,
            "phase": "phase6",
            "subscribed_signal_types": self.subscribed_signal_types,
            "cluster_ids": self.config.cluster_ids,
            "required_capabilities": [
                "process_signal",
                "consume_batch",
                "flush_buffer",
                "get_cluster_context",
                "get_signal_adjustment_for_cluster",
            ],
            "config": {
                "process_signals_asynchronously": self.config.process_signals_asynchronously,
                "max_batch_size": self.config.max_batch_size,
                "enable_signal_context_storage": self.config.enable_signal_context_storage,
            },
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the consumer.

        Returns:
            Dict with status information
        """
        return {
            "consumer_id": self.consumer_id,
            "status": "active",
            "buffer_size": len(self._signal_buffer),
            "subscribed_types": self.subscribed_signal_types,
            "cluster_contexts_count": len(self._cluster_contexts),
            "total_signals_processed": self.stats.get("processed", 0),
            "clusters_with_signals": [
                cluster_id for cluster_id, context in self._cluster_contexts.items()
                if context.signal_count > 0
            ],
        }
