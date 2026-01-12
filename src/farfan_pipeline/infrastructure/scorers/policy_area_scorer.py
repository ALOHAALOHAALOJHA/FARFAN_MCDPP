"""
Policy Area Scorer (@p) - Signal-based PA Scoring with Normative Compliance

This scorer consumes signals delivered by SignalIrrigator and scores Policy Areas
with mandatory normative compliance validation.

Key Features:
- Consumes NORMATIVE_REFERENCE, QUANTITATIVE_TRIPLET, FINANCIAL_CHAIN signals
- Validates normative compliance using NormativeComplianceValidator
- Calculates PA-level scores with empirical weights
- Applies penalties for missing mandatory norms
- Tracks signal coverage and quality per PA

Author: FARFAN Pipeline Team
Date: 2026-01-07
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from farfan_pipeline.infrastructure.validators import (
    NormativeComplianceValidator,
    ComplianceResult
)

logger = logging.getLogger(__name__)


@dataclass
class PolicyAreaScore:
    """Score result for a Policy Area."""
    policy_area: str
    total_score: float  # 0.0-1.0
    normative_compliance_score: float
    signal_coverage_score: float
    quality_score: float
    penalties_applied: float
    signals_consumed: int
    questions_answered: int
    compliance_result: Optional[ComplianceResult] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PolicyAreaScorer:
    """
    Scores Policy Areas using delivered signals and normative compliance.

    This is the @p scorer in the FARFAN notation (Phase 3 scoring).

    Scoring Components:
    1. Normative Compliance (40%): Mandatory norms present
    2. Signal Coverage (30%): Expected signals delivered
    3. Quality Score (30%): Signal confidence and completeness

    Usage:
        scorer = PolicyAreaScorer()

        # Score a policy area
        score = scorer.score_policy_area(
            policy_area="PA01",
            signal_deliveries=deliveries,
            questions_answered=30
        )

        print(f"PA01 Score: {score.total_score:.2f}")
        print(f"Normative Compliance: {score.normative_compliance_score:.2f}")
    """

    # Scoring weights
    NORMATIVE_COMPLIANCE_WEIGHT = 0.40
    SIGNAL_COVERAGE_WEIGHT = 0.30
    QUALITY_WEIGHT = 0.30

    def __init__(self, compliance_validator: Optional[NormativeComplianceValidator] = None):
        """
        Initialize scorer.

        Args:
            compliance_validator: Optional NormativeComplianceValidator. If None, creates new instance.
        """
        self.compliance_validator = compliance_validator or NormativeComplianceValidator()

        logger.info("PolicyAreaScorer initialized")

    def score_policy_area(
        self,
        policy_area: str,
        signal_deliveries: List[Any],  # List[SignalDelivery]
        questions_answered: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PolicyAreaScore:
        """
        Score a Policy Area using delivered signals.

        Args:
            policy_area: Policy area ID (e.g., "PA01")
            signal_deliveries: List of SignalDelivery objects
            questions_answered: Number of questions answered (for coverage)
            metadata: Optional additional metadata

        Returns:
            PolicyAreaScore with detailed scoring breakdown
        """
        # 1. Validate normative compliance
        compliance_result = self.compliance_validator.validate_from_signals(
            policy_area=policy_area,
            signal_deliveries=signal_deliveries
        )

        normative_score = compliance_result.compliance_score

        # 2. Calculate signal coverage score
        coverage_score = self._calculate_signal_coverage(
            policy_area=policy_area,
            signal_deliveries=signal_deliveries,
            questions_answered=questions_answered
        )

        # 3. Calculate quality score
        quality_score = self._calculate_quality_score(signal_deliveries)

        # 4. Calculate total score (weighted average)
        total_score = (
            normative_score * self.NORMATIVE_COMPLIANCE_WEIGHT +
            coverage_score * self.SIGNAL_COVERAGE_WEIGHT +
            quality_score * self.QUALITY_WEIGHT
        )

        return PolicyAreaScore(
            policy_area=policy_area,
            total_score=total_score,
            normative_compliance_score=normative_score,
            signal_coverage_score=coverage_score,
            quality_score=quality_score,
            penalties_applied=compliance_result.penalties_applied,
            signals_consumed=len(signal_deliveries),
            questions_answered=questions_answered,
            compliance_result=compliance_result,
            metadata={
                "compliance_details": {
                    "mandatory_norms_found": compliance_result.mandatory_norms_found,
                    "mandatory_norms_total": compliance_result.mandatory_norms_total,
                    "missing_norms": compliance_result.missing_norms,
                    "citation_rate": compliance_result.citation_rate
                },
                "signal_breakdown": self._get_signal_breakdown(signal_deliveries),
                **(metadata or {})
            }
        )

    def _calculate_signal_coverage(
        self,
        policy_area: str,
        signal_deliveries: List[Any],
        questions_answered: int
    ) -> float:
        """
        Calculate signal coverage score.

        Coverage is based on:
        - Number of signals delivered vs expected
        - Diversity of signal types
        - Question coverage
        """
        if not signal_deliveries:
            return 0.0

        # Get unique signal types delivered
        delivered_types = set(d.signal_type for d in signal_deliveries)

        # Expected signal types for this PA (simplified - ideally load from config)
        expected_types = {
            "QUANTITATIVE_TRIPLET",
            "NORMATIVE_REFERENCE",
            "STRUCTURAL_MARKER",
            "FINANCIAL_CHAIN"
        }

        # Type diversity score
        type_coverage = len(delivered_types & expected_types) / len(expected_types)

        # Question coverage (assume 30 questions per PA)
        expected_questions = 30
        question_coverage = min(1.0, questions_answered / expected_questions)

        # Signal density (signals per question)
        signal_density = min(1.0, len(signal_deliveries) / (questions_answered * 2))

        # Weighted average
        coverage_score = (
            type_coverage * 0.4 +
            question_coverage * 0.4 +
            signal_density * 0.2
        )

        return coverage_score

    def _calculate_quality_score(self, signal_deliveries: List[Any]) -> float:
        """
        Calculate quality score based on signal confidence and completeness.
        """
        if not signal_deliveries:
            return 0.0

        # Average confidence across all signals
        avg_confidence = sum(d.confidence for d in signal_deliveries) / len(signal_deliveries)

        # Average value_added across all signals
        avg_value_added = sum(d.value_added for d in signal_deliveries) / len(signal_deliveries)

        # Check for primary signals (higher quality)
        primary_signal_ratio = sum(
            1 for d in signal_deliveries
            if d.metadata.get("is_primary", False)
        ) / len(signal_deliveries)

        # Weighted quality score
        quality_score = (
            avg_confidence * 0.5 +
            avg_value_added * 0.3 +
            primary_signal_ratio * 0.2
        )

        return quality_score

    def _get_signal_breakdown(self, signal_deliveries: List[Any]) -> Dict[str, Any]:
        """Get breakdown of signals by type."""
        breakdown = {}

        for delivery in signal_deliveries:
            signal_type = delivery.signal_type
            if signal_type not in breakdown:
                breakdown[signal_type] = {
                    "count": 0,
                    "avg_confidence": 0.0,
                    "avg_value_added": 0.0
                }

            breakdown[signal_type]["count"] += 1

        # Calculate averages
        for signal_type in breakdown:
            type_deliveries = [d for d in signal_deliveries if d.signal_type == signal_type]
            breakdown[signal_type]["avg_confidence"] = (
                sum(d.confidence for d in type_deliveries) / len(type_deliveries)
            )
            breakdown[signal_type]["avg_value_added"] = (
                sum(d.value_added for d in type_deliveries) / len(type_deliveries)
            )

        return breakdown

    def score_all_policy_areas(
        self,
        signal_deliveries_by_pa: Dict[str, List[Any]],
        questions_answered_by_pa: Dict[str, int]
    ) -> Dict[str, PolicyAreaScore]:
        """
        Score all policy areas in batch.

        Args:
            signal_deliveries_by_pa: Dict mapping PA IDs to signal deliveries
            questions_answered_by_pa: Dict mapping PA IDs to question counts

        Returns:
            Dict mapping PA IDs to PolicyAreaScore
        """
        results = {}

        for pa_id in signal_deliveries_by_pa.keys():
            deliveries = signal_deliveries_by_pa.get(pa_id, [])
            questions = questions_answered_by_pa.get(pa_id, 0)

            results[pa_id] = self.score_policy_area(
                policy_area=pa_id,
                signal_deliveries=deliveries,
                questions_answered=questions
            )

        return results

    def generate_scoring_report(
        self,
        scores: Dict[str, PolicyAreaScore]
    ) -> Dict[str, Any]:
        """
        Generate a scoring report from PA scores.

        Args:
            scores: Dict of PA ID to PolicyAreaScore

        Returns:
            Dict with aggregated scoring metrics
        """
        total_pas = len(scores)
        avg_total_score = sum(s.total_score for s in scores.values()) / total_pas if total_pas > 0 else 0.0
        avg_normative_score = sum(s.normative_compliance_score for s in scores.values()) / total_pas if total_pas > 0 else 0.0
        avg_coverage_score = sum(s.signal_coverage_score for s in scores.values()) / total_pas if total_pas > 0 else 0.0
        avg_quality_score = sum(s.quality_score for s in scores.values()) / total_pas if total_pas > 0 else 0.0

        total_signals = sum(s.signals_consumed for s in scores.values())
        total_questions = sum(s.questions_answered for s in scores.values())

        return {
            "total_policy_areas": total_pas,
            "average_total_score": avg_total_score,
            "average_normative_score": avg_normative_score,
            "average_coverage_score": avg_coverage_score,
            "average_quality_score": avg_quality_score,
            "total_signals_consumed": total_signals,
            "total_questions_answered": total_questions,
            "signals_per_question": total_signals / total_questions if total_questions > 0 else 0.0,
            "policy_areas_above_threshold": sum(
                1 for s in scores.values()
                if s.total_score >= 0.70
            ),
            "lowest_scoring_pa": min(scores.items(), key=lambda x: x[1].total_score)[0] if scores else None,
            "highest_scoring_pa": max(scores.items(), key=lambda x: x[1].total_score)[0] if scores else None
        }


__all__ = [
    'PolicyAreaScorer',
    'PolicyAreaScore',
]
