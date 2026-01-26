"""Phase 7 Systemic Gap Detector with Normative Baseline

Enhanced systemic gap detection using normative compliance baseline from
corpus_empirico_normatividad.json. Identifies gaps prioritized by mandatory
norm violations and contextual validation rules.

Key Features:
- Normative baseline-driven gap detection
- Priority classification (CRITICAL/HIGH/MEDIUM/LOW)
- Contextual validation rules (PDET, ethnic, coastal)
- Gap remediation recommendations
- SISAS signal-informed severity adjustment (v2.0)
- Full event traceability correlation chains (v2.1)
- Cluster-level irrigation health integration (v2.1)

EMPIRICAL BASELINE: 14 PDT Colombia 2024-2027
SOURCE: canonic_questionnaire_central/_registry/entities/normative_compliance.json
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "2.1.0"  # SISAS integration + event traceability
__phase__ = 7
__stage__ = 10
__order__ = 10
__author__ = "F.A.R.F.A.N Core Team - Empirical Corpus Integration"
__created__ = "2026-01-12"
__modified__ = "2026-01-26"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase7.phase7_meso_consumer import (
        Phase7MesoConsumer,
    )

logger = logging.getLogger(__name__)

__all__ = [
    "SystemicGapDetector",
    "SystemicGap",
    "detect_systemic_gaps",
]

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class SystemicGap:
    """Represents a detected systemic gap in a policy area.

    Attributes:
        area_id: Policy area ID (e.g., "PA01_mujeres_genero")
        area_name: Human-readable area name
        score: Numeric score (0.0-1.0)
        quality_level: Quality classification
        priority: Gap priority (CRITICAL/HIGH/MEDIUM/LOW)
        missing_norms: List of missing mandatory norms
        normative_compliance_score: Normative compliance score (0.0-1.0)
        recommendation: Actionable recommendation
        context: Optional contextual information
        signal_informed: Whether gap was enhanced by live SISAS signals
        signal_severity_adjustment: Adjustment factor from signals (1.0 = no change)
        correlation_chain: Traceability of events that influenced this gap
        empirical_support_level: Level of empirical support for this area (0.0-1.0)
        determinacy_level: Answer determinacy level for this area (0.0-1.0)
    """

    area_id: str
    area_name: str
    score: float
    quality_level: str
    priority: str
    missing_norms: list[dict[str, Any]] = field(default_factory=list)
    normative_compliance_score: float = 0.0
    recommendation: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    # SISAS signal integration
    signal_informed: bool = False
    signal_severity_adjustment: float = 1.0
    # Event traceability (v2.1.0)
    correlation_chain: list[str] = field(default_factory=list)
    empirical_support_level: float = 1.0
    determinacy_level: float = 1.0


# =============================================================================
# SYSTEMIC GAP DETECTOR
# =============================================================================


class SystemicGapDetector:
    """Detects systemic gaps using normative baseline.

    Enhanced gap detection that combines quality-level thresholds with
    normative compliance validation from empirical corpus and optional
    SISAS signal-informed severity adjustments.

    Attributes:
        score_threshold: Score threshold for gap detection (default: 0.55)
        normative_validator: NormativeComplianceValidator instance
        enable_normative_validation: Enable normative baseline validation
        signal_consumer: Optional Phase7MesoConsumer for signal insights
    """

    def __init__(
        self,
        score_threshold: float = 0.55,
        corpus_path: Path | str | None = None,
        enable_normative_validation: bool = True,
        signal_consumer: "Phase7MesoConsumer | None" = None,
    ):
        """Initialize systemic gap detector.

        Args:
            score_threshold: Score threshold for gap detection (INSUFICIENTE)
            corpus_path: Optional path to normative_compliance.json
            enable_normative_validation: Enable normative baseline validation
            signal_consumer: Optional Phase7MesoConsumer for signal insights
        """
        self.score_threshold = score_threshold
        self.enable_normative_validation = enable_normative_validation
        self.signal_consumer = signal_consumer

        # Load normative compliance validator
        self.normative_validator = None
        if enable_normative_validation:
            try:
                from farfan_pipeline.phases.Phase_03.phase3_10_00_normative_compliance_validator import (
                    NormativeComplianceValidator,
                )

                self.normative_validator = NormativeComplianceValidator(corpus_path=corpus_path)
                logger.info("SystemicGapDetector initialized with normative baseline validation")
            except Exception as e:
                logger.warning(
                    f"Failed to load NormativeComplianceValidator, "
                    f"falling back to quality-level only detection: {e}"
                )
                self.enable_normative_validation = False
        
        # Signal consumer availability check
        if signal_consumer is not None:
            logger.info("SystemicGapDetector initialized with SISAS signal consumer")

    def detect_gaps(
        self,
        area_scores: list[Any],
        extracted_norms_by_area: dict[str, list[str]] | None = None,
        context_by_area: dict[str, dict[str, Any]] | None = None,
    ) -> list[SystemicGap]:
        """Detect systemic gaps across policy areas.

        Args:
            area_scores: List of AreaScore objects from Phase 5
            extracted_norms_by_area: Dict mapping area_id -> list of extracted norm IDs
            context_by_area: Dict mapping area_id -> context dict for validation

        Returns:
            List of SystemicGap objects, sorted by priority
        """
        gaps = []
        
        # Get signal insights if consumer available
        signal_insights = self._get_insights_from_signals()

        for area in area_scores:
            area_id = getattr(area, "area_id", "UNKNOWN")
            area_name = getattr(area, "area_name", area_id)
            score = getattr(area, "score", 0.0)
            quality_level = getattr(area, "quality_level", "INSUFICIENTE")

            # Normalize score to 0-1 range (assuming input is 0-3)
            normalized_score = self._normalize_score(score)

            # Basic gap detection: score below threshold
            if normalized_score < self.score_threshold:
                gap = self._create_basic_gap(area_id, area_name, normalized_score, quality_level)

                # Enhanced: Add normative compliance validation
                if self.enable_normative_validation and self.normative_validator:
                    self._enhance_gap_with_normative_baseline(
                        gap,
                        extracted_norms_by_area or {},
                        context_by_area or {},
                    )
                
                # Enhanced: Apply signal-based severity adjustment
                if signal_insights:
                    self._enhance_gap_with_signals(gap, area_id, signal_insights)

                gaps.append(gap)
                logger.info(
                    f"Systemic gap detected: {area_name} "
                    f"(score={normalized_score:.3f}, priority={gap.priority}, "
                    f"signal_informed={gap.signal_informed})"
                )

        # Sort gaps by priority (CRITICAL first)
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        gaps.sort(key=lambda g: (priority_order.get(g.priority, 4), g.score))

        logger.info(f"Total systemic gaps detected: {len(gaps)}")
        return gaps
    
    def _get_insights_from_signals(self) -> dict[str, Any] | None:
        """Get accumulated insights from signal consumer if available.
        
        Enhanced v2.1.0: Includes full traceability chain for event correlation.
        """
        if self.signal_consumer is None:
            return None
        
        try:
            insights = self.signal_consumer.get_insights()
            
            # Build correlation chain from processed signals
            correlation_chain: list[str] = []
            if hasattr(insights, "correlation_chain"):
                correlation_chain = insights.correlation_chain or []
            
            # Extract cluster-level metrics if available (v2.1.0)
            cluster_metrics: dict[str, Any] = {}
            if hasattr(insights, "cluster_metrics"):
                cluster_metrics = {
                    cid: {
                        "irrigation_health": m.irrigation_health,
                        "mapping_coverage": len(m.mapping_scores) if m.mapping_scores else 0,
                        "alignment_avg": (sum(m.alignment_scores) / len(m.alignment_scores)) 
                                         if m.alignment_scores else 0.0,
                    }
                    for cid, m in (insights.cluster_metrics or {}).items()
                }
            
            return {
                "data_completeness": insights.data_completeness_level,
                "integrity_violations": insights.integrity_violations,
                "empirical_support": insights.empirical_support_levels,
                "low_determinacy": insights.low_determinacy_areas,
                "divergences": insights.divergences_detected,
                "severity_factor": insights.severity_adjustment_factor,
                # v2.1.0 traceability enhancements
                "correlation_chain": correlation_chain,
                "cluster_metrics": cluster_metrics,
                "determinacy_levels": getattr(insights, "determinacy_levels", {}),
            }
        except Exception as e:
            logger.warning(f"Failed to get signal insights: {e}")
            return None
    
    def _enhance_gap_with_signals(
        self,
        gap: SystemicGap,
        area_id: str,
        insights: dict[str, Any],
    ) -> None:
        """Enhance gap detection with signal-derived insights.
        
        Enhanced v2.1.0: Full event traceability correlation and cluster metrics.
        """
        gap.signal_informed = True
        
        # v2.1.0: Capture correlation chain for full traceability
        correlation_chain = insights.get("correlation_chain", [])
        gap.correlation_chain = correlation_chain.copy() if correlation_chain else []
        
        # Apply severity adjustment from divergence signals
        severity_factor = insights.get("severity_factor", 1.0)
        gap.signal_severity_adjustment = severity_factor
        
        # v2.1.0: Capture empirical support level for this area
        empirical_support = insights.get("empirical_support", {})
        if area_id in empirical_support:
            gap.empirical_support_level = empirical_support[area_id]
            # Boost priority if support is critically low
            if gap.empirical_support_level < 0.3 and gap.priority not in ["CRITICAL"]:
                gap.priority = "CRITICAL"
                logger.debug(f"Gap {area_id} priority CRITICAL due to very low empirical support")
            elif gap.empirical_support_level < 0.5 and gap.priority not in ["CRITICAL", "HIGH"]:
                gap.priority = "HIGH"
                logger.debug(f"Gap {area_id} priority boosted due to low empirical support")
        
        # v2.1.0: Capture determinacy level for this area
        determinacy_levels = insights.get("determinacy_levels", {})
        low_determinacy = insights.get("low_determinacy", [])
        if area_id in determinacy_levels:
            gap.determinacy_level = determinacy_levels[area_id]
        elif area_id in low_determinacy:
            gap.determinacy_level = 0.4  # Default low value
            
        # Check if area has low determinacy - boost priority
        if area_id in low_determinacy and gap.priority == "MEDIUM":
            gap.priority = "HIGH"
            logger.debug(f"Gap {area_id} priority boosted due to low determinacy")
        
        # v2.1.0: Cluster metrics integration
        cluster_metrics = insights.get("cluster_metrics", {})
        for cluster_id, metrics in cluster_metrics.items():
            if area_id.startswith(cluster_id.replace("cluster_", "PA").split("_")[0]):
                irrigation_health = metrics.get("irrigation_health", 1.0)
                if irrigation_health < 0.5:
                    # Poor irrigation health indicates data quality issues
                    severity_factor = max(severity_factor, 1.0 + (1.0 - irrigation_health))
                    gap.signal_severity_adjustment = severity_factor
                    gap.correlation_chain.append(f"cluster:{cluster_id}:low_irrigation_health")
        
        # Apply severity factor to recommendation
        if severity_factor > 1.0:
            gap.recommendation = (
                f"[SISAS: severity×{severity_factor:.1f}] {gap.recommendation}"
            )
        
        # v2.1.0: Append traceability info to context
        gap.context["sisas_traceability"] = {
            "correlation_chain": gap.correlation_chain,
            "empirical_support": gap.empirical_support_level,
            "determinacy": gap.determinacy_level,
            "severity_adjustment": gap.signal_severity_adjustment,
            "signal_count": len(correlation_chain),
        }

    def _normalize_score(self, score: float) -> float:
        """Normalize score from 0-3 to 0-1 range.

        In F.A.R.F.A.N, ALL scores use the 0-3 scale (MIN_SCORE=0, MAX_SCORE=3).
        No heuristic detection needed - always divide by 3.

        Args:
            score: Input score in 0-3 range

        Returns:
            Normalized score (0-1)
        """
        # F.A.R.F.A.N uses 0-3 scale consistently - always normalize
        return max(0.0, min(1.0, score / 3.0))

    def _create_basic_gap(
        self,
        area_id: str,
        area_name: str,
        score: float,
        quality_level: str,
    ) -> SystemicGap:
        """Create basic SystemicGap without normative validation.

        Args:
            area_id: Policy area ID
            area_name: Human-readable area name
            score: Normalized score (0-1)
            quality_level: Quality classification

        Returns:
            SystemicGap instance with basic priority
        """
        # Determine basic priority from score
        if score < 0.30:
            priority = "CRITICAL"
        elif score < 0.40:
            priority = "HIGH"
        elif score < self.score_threshold:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        return SystemicGap(
            area_id=area_id,
            area_name=area_name,
            score=score,
            quality_level=quality_level,
            priority=priority,
            recommendation=f"Área {area_name} requiere intervención (score={score:.3f})",
        )

    def _enhance_gap_with_normative_baseline(
        self,
        gap: SystemicGap,
        extracted_norms_by_area: dict[str, list[str]],
        context_by_area: dict[str, dict[str, Any]],
    ) -> None:
        """Enhance gap with normative compliance validation.

        Args:
            gap: SystemicGap to enhance (modified in-place)
            extracted_norms_by_area: Dict of extracted norms per area
            context_by_area: Dict of context per area
        """
        if not self.normative_validator:
            return

        area_id = gap.area_id
        extracted_norms = extracted_norms_by_area.get(area_id, [])
        context = context_by_area.get(area_id, {})

        try:
            # Validate normative compliance
            compliance_result = self.normative_validator.validate_compliance(
                policy_area=area_id,
                extracted_norms=extracted_norms,
                context=context,
            )

            # Update gap with normative data
            gap.missing_norms = compliance_result.get("missing_norms", [])
            gap.normative_compliance_score = compliance_result.get("score", 0.0)
            gap.context = context

            # Upgrade priority if critical norms are missing
            critical_norms = [n for n in gap.missing_norms if n.get("severity") == "CRITICAL"]
            high_norms = [n for n in gap.missing_norms if n.get("severity") == "HIGH"]

            if critical_norms:
                gap.priority = "CRITICAL"
            elif high_norms and gap.priority not in ["CRITICAL"]:
                gap.priority = "HIGH"

            # Enhanced recommendation
            if gap.missing_norms:
                norm_ids = [n["norm_id"] for n in gap.missing_norms[:3]]  # Top 3 missing
                gap.recommendation = (
                    f"Área {gap.area_name} requiere incluir normas obligatorias: "
                    f"{', '.join(norm_ids)}. "
                    f"Score normativo: {gap.normative_compliance_score:.3f}."
                )
            else:
                gap.recommendation = compliance_result.get("recommendation", gap.recommendation)

            logger.debug(
                f"Enhanced gap {area_id} with normative baseline: "
                f"compliance_score={gap.normative_compliance_score:.3f}, "
                f"missing_norms={len(gap.missing_norms)}, "
                f"priority={gap.priority}"
            )

        except Exception as e:
            logger.warning(f"Failed to enhance gap {area_id} with normative baseline: {e}")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def detect_systemic_gaps(
    area_scores: list[Any],
    extracted_norms_by_area: dict[str, list[str]] | None = None,
    context_by_area: dict[str, dict[str, Any]] | None = None,
    score_threshold: float = 0.55,
    corpus_path: Path | str | None = None,
) -> list[SystemicGap]:
    """Convenience function to detect systemic gaps.

    Args:
        area_scores: List of AreaScore objects
        extracted_norms_by_area: Dict of extracted norms per area
        context_by_area: Dict of context per area
        score_threshold: Score threshold for gap detection
        corpus_path: Optional path to normative_compliance.json

    Returns:
        List of detected SystemicGap objects
    """
    detector = SystemicGapDetector(
        score_threshold=score_threshold,
        corpus_path=corpus_path,
        enable_normative_validation=True,
    )

    return detector.detect_gaps(
        area_scores=area_scores,
        extracted_norms_by_area=extracted_norms_by_area,
        context_by_area=context_by_area,
    )
