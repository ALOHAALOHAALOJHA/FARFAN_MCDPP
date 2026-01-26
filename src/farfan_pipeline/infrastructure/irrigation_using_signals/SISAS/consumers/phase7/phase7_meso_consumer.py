# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase7/phase7_meso_consumer.py

"""
Phase 7 MESO Consumer - Sophisticated Multi-Bus Signal Processing

Enhanced consumer for Phase 7 (Macro Evaluation) that subscribes to multiple
buses and signal types for comprehensive irrigation of the aggregation phase.

Buses Subscribed:
    - structural_bus: CanonicalMappingSignal, StructuralAlignmentSignal
    - orchestration_bus: PhaseCompleteSignal, PhaseReadyToStartSignal
    - integrity_bus: DataIntegritySignal, EventCompletenessSignal
    - epistemic_bus: EmpiricalSupportSignal, AnswerDeterminacySignal
    - contrast_bus: DecisionDivergenceSignal

Enhanced Features (v2.1.0):
    - Per-cluster irrigation state tracking
    - Event correlation for audit traceability (correlation_id chain)
    - Coherence adjustment factor from mapping variance
    - Gap severity amplification from divergence signals
    - Exportable metrics for MacroAggregator consumption

Version: 2.1.0
Effective-Date: 2026-01-25
"""

from __future__ import annotations

import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract

logger = logging.getLogger(__name__)


# =============================================================================
# CLUSTER-LEVEL IRRIGATION STATE
# =============================================================================


@dataclass
class ClusterIrrigationMetrics:
    """Per-cluster aggregated irrigation metrics from SISAS signals."""
    
    cluster_id: str
    mapping_scores: List[float] = field(default_factory=list)
    alignment_scores: List[float] = field(default_factory=list)
    completeness_scores: List[float] = field(default_factory=list)
    empirical_support_scores: List[float] = field(default_factory=list)
    signal_count: int = 0
    correlation_ids: set[str] = field(default_factory=set)
    
    @property
    def avg_mapping(self) -> float:
        return statistics.mean(self.mapping_scores) if self.mapping_scores else 0.0
    
    @property
    def avg_alignment(self) -> float:
        return statistics.mean(self.alignment_scores) if self.alignment_scores else 0.0
    
    @property
    def avg_completeness(self) -> float:
        return statistics.mean(self.completeness_scores) if self.completeness_scores else 0.0
    
    @property
    def avg_empirical_support(self) -> float:
        return statistics.mean(self.empirical_support_scores) if self.empirical_support_scores else 0.0
    
    @property
    def irrigation_health(self) -> float:
        """
        Combined irrigation health [0, 1].
        
        Weighted average: mapping(30%), alignment(30%), completeness(20%), empirical(20%).
        """
        components = [
            (0.30, self.avg_mapping),
            (0.30, self.avg_alignment),
            (0.20, self.avg_completeness),
            (0.20, self.avg_empirical_support),
        ]
        # Only include components with data
        active = [(w, s) for w, s in components if s > 0]
        if not active:
            return 0.0
        total_weight = sum(w for w, _ in active)
        return sum(w * s for w, s in active) / total_weight if total_weight else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "avg_mapping": round(self.avg_mapping, 4),
            "avg_alignment": round(self.avg_alignment, 4),
            "avg_completeness": round(self.avg_completeness, 4),
            "avg_empirical_support": round(self.avg_empirical_support, 4),
            "irrigation_health": round(self.irrigation_health, 4),
            "signal_count": self.signal_count,
            "correlation_ids": list(self.correlation_ids)[:10],  # Limit for JSON
        }


# =============================================================================
# AGGREGATED INSIGHTS
# =============================================================================


@dataclass
class AggregatedInsights:
    """Accumulated insights from cross-signal analysis for MacroAggregator."""
    
    # Structural insights
    mapping_completeness_scores: List[float] = field(default_factory=list)
    alignment_issues: List[str] = field(default_factory=list)
    
    # Orchestration insights
    upstream_phase_statuses: Dict[str, str] = field(default_factory=dict)
    ready_signal_received: bool = False
    
    # Integrity insights
    data_completeness_level: float = 1.0
    integrity_violations: List[str] = field(default_factory=list)
    
    # Epistemic insights
    empirical_support_levels: Dict[str, float] = field(default_factory=dict)
    low_determinacy_areas: List[str] = field(default_factory=list)
    # v2.1.0: Per-area determinacy level tracking for gap detection
    determinacy_levels: Dict[str, float] = field(default_factory=dict)
    
    # Contrast insights
    divergences_detected: List[Dict[str, Any]] = field(default_factory=list)
    severity_adjustment_factor: float = 1.0
    
    # =========================================================================
    # NEW: Per-cluster irrigation metrics
    # =========================================================================
    cluster_metrics: Dict[str, ClusterIrrigationMetrics] = field(default_factory=dict)
    policy_area_signal_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    dimension_signal_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Event correlation chain
    correlation_chain: List[str] = field(default_factory=list)
    phase_correlation_id: Optional[str] = None
    
    # Metadata
    last_updated: Optional[datetime] = None
    signals_processed_count: int = 0
    
    # =========================================================================
    # CLUSTER MAPPING (PA -> Cluster)
    # =========================================================================
    _cluster_mapping: Dict[str, str] = field(default_factory=lambda: {
        "PA01": "CLUSTER_MESO_1", "PA02": "CLUSTER_MESO_1", "PA03": "CLUSTER_MESO_1",
        "PA04": "CLUSTER_MESO_2", "PA05": "CLUSTER_MESO_2", "PA06": "CLUSTER_MESO_2",
        "PA07": "CLUSTER_MESO_3", "PA08": "CLUSTER_MESO_3",
        "PA09": "CLUSTER_MESO_4", "PA10": "CLUSTER_MESO_4",
    })

    def get_cluster_metrics(self, cluster_id: str) -> ClusterIrrigationMetrics:
        """Get or create cluster metrics."""
        if cluster_id not in self.cluster_metrics:
            self.cluster_metrics[cluster_id] = ClusterIrrigationMetrics(cluster_id=cluster_id)
        return self.cluster_metrics[cluster_id]
    
    def resolve_cluster(self, policy_area: Optional[str] = None, node_id: Optional[str] = None) -> Optional[str]:
        """Resolve cluster from policy area or node_id path."""
        if policy_area and policy_area in self._cluster_mapping:
            return self._cluster_mapping[policy_area]
        if node_id:
            import re
            pa_match = re.search(r'PA(\d{2})', node_id)
            if pa_match:
                pa = f"PA{pa_match.group(1)}"
                return self._cluster_mapping.get(pa)
            cluster_match = re.search(r'(CLUSTER_MESO_\d)', node_id)
            if cluster_match:
                return cluster_match.group(1)
        return None

    def compute_overall_health(self) -> float:
        """Compute overall health score from accumulated insights."""
        scores = []
        
        # Mapping completeness average
        if self.mapping_completeness_scores:
            scores.append(sum(self.mapping_completeness_scores) / len(self.mapping_completeness_scores))
        
        # Data completeness
        scores.append(self.data_completeness_level)
        
        # Penalty for integrity violations
        if self.integrity_violations:
            scores.append(max(0.0, 1.0 - len(self.integrity_violations) * 0.1))
        
        # Empirical support average
        if self.empirical_support_levels:
            scores.append(sum(self.empirical_support_levels.values()) / len(self.empirical_support_levels))
        
        return sum(scores) / len(scores) if scores else 1.0
    
    def compute_coherence_adjustment(self) -> float:
        """
        Compute coherence adjustment factor from irrigation variance.
        
        High variance in cluster irrigation health indicates structural
        coherence issues. Returns [0.85, 1.0] where lower = more variance.
        """
        if len(self.cluster_metrics) < 2:
            return 1.0
        
        healths = [m.irrigation_health for m in self.cluster_metrics.values()]
        if not healths or all(h == 0 for h in healths):
            return 1.0
        
        variance = statistics.variance(healths) if len(healths) > 1 else 0.0
        # Max expected variance ~0.25 for [0,1] scores
        adjustment = max(0.85, 1.0 - (variance * 0.6))
        return adjustment
    
    def compute_gap_severity_amplifier(self) -> float:
        """
        Compute gap severity amplifier from divergence signals.
        
        Critical divergences amplify gap severity detection.
        Returns [1.0, 2.0] where higher = more severe divergences.
        """
        if not self.divergences_detected:
            return 1.0
        
        # Count severity levels
        severity_counts = {"CRITICAL": 0, "SEVERE": 0, "MODERATE": 0, "LOW": 0}
        for div in self.divergences_detected:
            sev = div.get("severity", "LOW")
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        # Weighted amplification
        amplifier = 1.0 + (
            severity_counts["CRITICAL"] * 0.25 +
            severity_counts["SEVERE"] * 0.15 +
            severity_counts["MODERATE"] * 0.05
        )
        return min(amplifier, 2.0)
    
    def to_macro_aggregator_payload(self) -> Dict[str, Any]:
        """
        Export comprehensive payload for MacroAggregator consumption.
        
        This is the main API for MacroAggregator to consume SISAS irrigation data.
        Enhanced v2.1.0: Includes determinacy_levels and correlation_chain.
        """
        return {
            "overall_health": round(self.compute_overall_health(), 4),
            "coherence_adjustment": round(self.compute_coherence_adjustment(), 4),
            "gap_severity_amplifier": round(self.compute_gap_severity_amplifier(), 4),
            "cluster_metrics": {k: v.to_dict() for k, v in self.cluster_metrics.items()},
            "policy_area_coverage": dict(self.policy_area_signal_counts),
            "dimension_coverage": dict(self.dimension_signal_counts),
            "integrity_violations_count": len(self.integrity_violations),
            "low_determinacy_areas": self.low_determinacy_areas,
            # v2.1.0: Per-area determinacy levels for gap detection
            "determinacy_levels": dict(self.determinacy_levels),
            "divergences_count": len(self.divergences_detected),
            "upstream_phases_complete": sum(
                1 for s in self.upstream_phase_statuses.values() if s == "COMPLETE"
            ),
            "signals_processed": self.signals_processed_count,
            "phase_correlation_id": self.phase_correlation_id,
            # v2.1.0: Full correlation chain for traceability
            "correlation_chain": self.correlation_chain.copy(),
        }


@dataclass
class Phase7MesoConsumer(BaseConsumer):
    """
    Enhanced consumer for Phase 7 macro aggregation.
    
    Multi-bus subscriber that processes signals from 5 buses to provide
    comprehensive insights for the MacroAggregator and SystemicGapDetector.
    
    Key Features (v2.1):
        - Multi-bus subscription (structural, orchestration, integrity, epistemic, contrast)
        - Per-cluster irrigation metrics tracking
        - Aggregated insights accumulation for downstream components
        - Coherence adjustment from irrigation variance
        - Gap severity amplification from divergence signals
        - Event correlation chain for audit traceability
    
    Usage:
        >>> consumer = Phase7MesoConsumer()
        >>> consumer.subscribe(bus_registry)
        >>> # Signals are processed via bus callbacks
        >>> payload = consumer.get_macro_aggregator_payload()
        >>> # Use payload in MacroAggregator for SISAS-enriched coherence
    """
    
    consumer_id: str = "phase7_meso_consumer"
    consumer_phase: str = "phase_07"
    
    # Aggregated insights for export to MacroAggregator
    aggregated_insights: AggregatedInsights = field(default_factory=AggregatedInsights)
    
    def __post_init__(self) -> None:
        super().__post_init__()
        
        # Configure multi-bus consumption contract
        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE7_MESO_ENHANCED",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                # Structural signals
                "CanonicalMappingSignal",
                "StructuralAlignmentSignal",
                # Orchestration signals
                "PhaseCompleteSignal",
                "PhaseReadyToStartSignal",
                # Integrity signals
                "DataIntegritySignal",
                "EventCompletenessSignal",
                # Epistemic signals
                "EmpiricalSupportSignal",
                "AnswerDeterminacySignal",
                # Contrast signals
                "DecisionDivergenceSignal",
            ],
            subscribed_buses=[
                "structural_bus",
                "orchestration_bus",
                "integrity_bus",
                "epistemic_bus",
                "contrast_bus",
            ],
            context_filters={
                "phase": ["phase_05", "phase_06", "phase_07"],
                "node_type": ["question", "cluster", "policy_area", "dimension"],
            },
            required_capabilities=[
                "can_scope_context",
                "can_aggregate_signals",
                "can_compute_health",
            ]
        )
        
        logger.info(
            f"Phase7MesoConsumer v2.1 initialized: "
            f"buses={self.consumption_contract.subscribed_buses}"
        )
    
    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Process a received signal with type-specific analysis.
        
        Routes signal to appropriate handler based on signal_type and
        accumulates insights in aggregated_insights for downstream use.
        Also tracks per-cluster irrigation metrics and event correlation.
        """
        result: Dict[str, Any] = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "analysis": {},
            "cluster_updated": None,
        }
        
        signal_type = signal.signal_type
        
        # Track correlation ID for event chain
        correlation_id = getattr(signal, "correlation_id", None)
        if correlation_id:
            if correlation_id not in self.aggregated_insights.correlation_chain:
                self.aggregated_insights.correlation_chain.append(correlation_id)
            self.aggregated_insights.phase_correlation_id = correlation_id
        
        # Route to appropriate handler
        if signal_type == "CanonicalMappingSignal":
            result["analysis"], result["cluster_updated"] = self._analyze_mapping(signal)
        elif signal_type == "StructuralAlignmentSignal":
            result["analysis"], result["cluster_updated"] = self._analyze_alignment(signal)
        elif signal_type in ("PhaseCompleteSignal", "PhaseReadyToStartSignal"):
            result["analysis"] = self._analyze_phase_lifecycle(signal)
        elif signal_type in ("DataIntegritySignal", "EventCompletenessSignal"):
            result["analysis"], result["cluster_updated"] = self._analyze_integrity(signal)
        elif signal_type in ("EmpiricalSupportSignal", "AnswerDeterminacySignal"):
            result["analysis"], result["cluster_updated"] = self._analyze_epistemic(signal)
        elif signal_type == "DecisionDivergenceSignal":
            result["analysis"] = self._analyze_divergence(signal)
        else:
            result["analysis"] = {"note": "Unknown signal type, logged for audit"}
        
        # Update metadata
        self.aggregated_insights.signals_processed_count += 1
        self.aggregated_insights.last_updated = datetime.now(UTC)
        
        return result
    
    def _extract_context_info(self, signal: Signal) -> tuple[Optional[str], Optional[str]]:
        """Extract policy_area and node_id from signal context."""
        context = getattr(signal, "context", None)
        policy_area = None
        node_id = None
        
        if context:
            node_id = getattr(context, "node_id", None)
            # Try to extract PA from node_id
            if node_id:
                import re
                pa_match = re.search(r'PA(\d{2})', str(node_id))
                if pa_match:
                    policy_area = f"PA{pa_match.group(1)}"
        
        return policy_area, node_id
    
    def _analyze_mapping(self, signal: Signal) -> tuple[Dict[str, Any], Optional[str]]:
        """Analyze canonical mapping signal and update cluster metrics."""
        completeness = getattr(signal, "mapping_completeness", 0.0)
        mapped_entities = getattr(signal, "mapped_entities", {})
        
        self.aggregated_insights.mapping_completeness_scores.append(completeness)
        
        # Resolve cluster and update metrics
        policy_area = mapped_entities.get("policy_area")
        node_id = getattr(getattr(signal, "context", None), "node_id", None)
        cluster_id = self.aggregated_insights.resolve_cluster(policy_area, node_id)
        
        if cluster_id:
            metrics = self.aggregated_insights.get_cluster_metrics(cluster_id)
            metrics.mapping_scores.append(completeness)
            metrics.signal_count += 1
            
            # Track correlation
            if self.aggregated_insights.phase_correlation_id:
                metrics.correlation_ids.add(self.aggregated_insights.phase_correlation_id)
        
        # Track PA/DIM coverage
        if policy_area:
            self.aggregated_insights.policy_area_signal_counts[policy_area] += 1
        if "dimension" in mapped_entities:
            self.aggregated_insights.dimension_signal_counts[mapped_entities["dimension"]] += 1
        
        analysis = {
            "mapped_entities": mapped_entities,
            "mapping_completeness": completeness,
            "unmapped": getattr(signal, "unmapped_aspects", []),
        }
        
        return analysis, cluster_id
    
    def _analyze_alignment(self, signal: Signal) -> tuple[Dict[str, Any], Optional[str]]:
        """Analyze structural alignment signal and update cluster metrics."""
        alignment_status = getattr(signal, "alignment_status", None)
        missing = getattr(signal, "missing_elements", [])
        
        if missing:
            self.aggregated_insights.alignment_issues.extend(missing)
        
        # Compute alignment score
        alignment_score = 0.0
        if hasattr(signal, "compute_alignment_score"):
            alignment_score = signal.compute_alignment_score()
        elif alignment_status:
            status_str = alignment_status.value if hasattr(alignment_status, "value") else str(alignment_status)
            alignment_score = {"ALIGNED": 1.0, "PARTIAL": 0.5, "MISALIGNED": 0.0}.get(status_str, 0.25)
        
        # Resolve cluster from canonical_path
        canonical_path = getattr(signal, "canonical_path", "")
        cluster_id = self.aggregated_insights.resolve_cluster(node_id=canonical_path)
        
        if cluster_id:
            metrics = self.aggregated_insights.get_cluster_metrics(cluster_id)
            metrics.alignment_scores.append(alignment_score)
            metrics.signal_count += 1
        
        analysis = {
            "alignment_status": str(alignment_status) if alignment_status else None,
            "alignment_score": alignment_score,
            "missing_elements": missing,
            "canonical_path": canonical_path,
        }
        
        return analysis, cluster_id
    
    def _analyze_phase_lifecycle(self, signal: Signal) -> Dict[str, Any]:
        """Analyze orchestration lifecycle signals and update insights."""
        phase_id = getattr(signal, "phase_id", "unknown")
        status = getattr(signal, "status", None)
        
        if signal.signal_type == "PhaseCompleteSignal":
            status_str = status.value if hasattr(status, "value") else str(status)
            self.aggregated_insights.upstream_phase_statuses[phase_id] = status_str
        elif signal.signal_type == "PhaseReadyToStartSignal":
            if phase_id in ("phase_07", "phase7"):
                self.aggregated_insights.ready_signal_received = True
        
        logger.debug(f"Phase lifecycle signal: {signal.signal_type} for {phase_id}")
        
        return {
            "phase_id": phase_id,
            "status": str(status) if status else None,
            "execution_time_s": getattr(signal, "execution_time_s", 0.0),
        }
    
    def _analyze_integrity(self, signal: Signal) -> tuple[Dict[str, Any], Optional[str]]:
        """Analyze data integrity signals and update cluster metrics."""
        cluster_id = None
        policy_area, node_id = self._extract_context_info(signal)
        
        if signal.signal_type == "EventCompletenessSignal":
            level = getattr(signal, "completeness_level", None)
            completeness_score = getattr(signal, "completeness_score", 0.5)
            
            if level and hasattr(level, "value"):
                level_scores = {
                    "COMPLETE": 1.0,
                    "MOSTLY_COMPLETE": 0.8,
                    "PARTIAL": 0.5,
                    "INCOMPLETE": 0.2,
                    "EMPTY": 0.0,
                }
                completeness_score = level_scores.get(level.value, completeness_score)
                self.aggregated_insights.data_completeness_level = completeness_score
            
            # Update cluster metrics
            cluster_id = self.aggregated_insights.resolve_cluster(policy_area, node_id)
            if cluster_id:
                metrics = self.aggregated_insights.get_cluster_metrics(cluster_id)
                metrics.completeness_scores.append(completeness_score)
                metrics.signal_count += 1
        
        elif signal.signal_type == "DataIntegritySignal":
            violations = getattr(signal, "violations", [])
            if violations:
                self.aggregated_insights.integrity_violations.extend(violations)
        
        analysis = {
            "integrity_valid": getattr(signal, "is_valid", True),
            "violations": getattr(signal, "violations", []),
            "completeness_level": str(getattr(signal, "completeness_level", "UNKNOWN")),
        }
        
        return analysis, cluster_id
    
    def _analyze_epistemic(self, signal: Signal) -> tuple[Dict[str, Any], Optional[str]]:
        """Analyze epistemic support signals and update cluster metrics."""
        cluster_id = None
        
        if signal.signal_type == "EmpiricalSupportSignal":
            area_id = getattr(signal, "policy_area_id", None)
            support_level = getattr(signal, "support_level", None)
            
            if area_id and support_level:
                level_scores = {
                    "STRONG": 1.0,
                    "MODERATE": 0.7,
                    "WEAK": 0.4,
                    "NONE": 0.1,
                }
                score = level_scores.get(
                    support_level.value if hasattr(support_level, "value") else str(support_level),
                    0.5,
                )
                self.aggregated_insights.empirical_support_levels[area_id] = score
                
                # Update cluster metrics
                cluster_id = self.aggregated_insights.resolve_cluster(area_id)
                if cluster_id:
                    metrics = self.aggregated_insights.get_cluster_metrics(cluster_id)
                    metrics.empirical_support_scores.append(score)
                    metrics.signal_count += 1
        
        elif signal.signal_type == "AnswerDeterminacySignal":
            determinacy = getattr(signal, "determinacy_level", None)
            area_id = getattr(signal, "policy_area_id", "unknown")
            
            # v2.1.0: Track numeric determinacy level per area
            if determinacy:
                # Determinacy may be enum or numeric
                if hasattr(determinacy, "value"):
                    # Enum-based: map to numeric
                    determinacy_map = {
                        "DETERMINATE": 1.0,
                        "PROBABLE": 0.75,
                        "UNCERTAIN": 0.5,
                        "INDETERMINATE": 0.25,
                    }
                    level = determinacy_map.get(determinacy.value, 0.5)
                    self.aggregated_insights.determinacy_levels[area_id] = level
                    
                    if determinacy.value == "INDETERMINATE":
                        self.aggregated_insights.low_determinacy_areas.append(area_id)
                elif isinstance(determinacy, (int, float)):
                    # Already numeric
                    self.aggregated_insights.determinacy_levels[area_id] = float(determinacy)
                    if determinacy < 0.4:
                        self.aggregated_insights.low_determinacy_areas.append(area_id)
        
        analysis = {
            "support_level": str(getattr(signal, "support_level", "UNKNOWN")),
            "determinacy_level": str(getattr(signal, "determinacy_level", "UNKNOWN")),
            "evidence_count": getattr(signal, "evidence_count", 0),
        }
        
        return analysis, cluster_id
    
    def _analyze_divergence(self, signal: Signal) -> Dict[str, Any]:
        """Analyze decision divergence signals and update gap severity."""
        divergence_type = getattr(signal, "divergence_type", None)
        severity = getattr(signal, "severity", None)
        
        divergence_record = {
            "type": str(divergence_type) if divergence_type else None,
            "severity": str(severity.value) if hasattr(severity, "value") else str(severity) if severity else None,
            "confidence_delta": getattr(signal, "confidence_delta", 0.0),
        }
        self.aggregated_insights.divergences_detected.append(divergence_record)
        
        # Adjust severity factor based on detected divergences
        if severity and hasattr(severity, "value"):
            severity_adjustments = {
                "CRITICAL": 1.5,
                "SEVERE": 1.3,
                "MODERATE": 1.1,
                "LOW": 1.0,
            }
            adjustment = severity_adjustments.get(severity.value, 1.0)
            self.aggregated_insights.severity_adjustment_factor = max(
                self.aggregated_insights.severity_adjustment_factor, adjustment
            )
        
        return divergence_record
    
    # =========================================================================
    # PUBLIC API FOR MACRO AGGREGATOR
    # =========================================================================
    
    def get_insights(self) -> AggregatedInsights:
        """Export accumulated insights for MacroAggregator consumption."""
        return self.aggregated_insights
    
    def get_macro_aggregator_payload(self) -> Dict[str, Any]:
        """
        Export comprehensive payload for MacroAggregator consumption.
        
        This is the main API for MacroAggregator to consume SISAS irrigation data
        for coherence adjustment, gap detection, and alignment scoring.
        """
        return self.aggregated_insights.to_macro_aggregator_payload()
    
    def get_cluster_irrigation_health(self, cluster_id: str) -> float:
        """Get irrigation health for a specific cluster."""
        if cluster_id in self.aggregated_insights.cluster_metrics:
            return self.aggregated_insights.cluster_metrics[cluster_id].irrigation_health
        return 0.0
    
    def reset_insights(self) -> None:
        """Reset accumulated insights for new evaluation cycle."""
        self.aggregated_insights = AggregatedInsights()
        logger.info("Phase7MesoConsumer insights reset")