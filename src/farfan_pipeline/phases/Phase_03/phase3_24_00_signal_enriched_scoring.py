"""Phase 3 Signal-Enriched Scoring Module

Extends Phase 3 scoring with signal-based enhancements for increased rigor
and determinism. Provides signal-driven threshold adjustments and quality
mapping with full provenance tracking.

Enhancement Value:
- Signal-based threshold adaptation based on question complexity
- Signal-driven quality level validation
- Enhanced scoring provenance with signal metadata
- Deterministic, byte-reproducible scoring with signal context

Integration: Used by orchestrator._score_micro_results_async() to enhance
basic scoring with signal intelligence.

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 3
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    try:
        from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals import (
            QuestionnaireSignalRegistry,
        )
    except ImportError:
        QuestionnaireSignalRegistry = Any  # type: ignore

# Runtime import of QuestionnaireSignalRegistry for scoring logic.
# This makes the dependency explicit while still allowing hard failure if missing.
try:
    from farfan_pipeline.phases.Phase_02.registries.questionnaire_signal_registry import (
        QuestionnaireSignalRegistry as _QuestionnaireSignalRegistryRuntime,
    )
    _questionnaire_signal_registry_import_error: Exception | None = None
except ImportError as e:
    _QuestionnaireSignalRegistryRuntime = None  # type: ignore[assignment]
    _questionnaire_signal_registry_import_error = e

# EMPIRICAL CORPUS INTEGRATION
try:
    from farfan_pipeline.phases.Phase_03.phase3_15_00_empirical_thresholds_loader import (
        get_global_thresholds_loader,
    )

    _empirical_loader = get_global_thresholds_loader()
    logger = logging.getLogger(__name__)
    logger.info("Empirical thresholds loader initialized for SignalEnrichedScorer")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to load empirical thresholds, using hardcoded defaults: {e}")
    _empirical_loader = None

logger = logging.getLogger(__name__)

# Quality level constants
QUALITY_EXCELENTE = "EXCELENTE"
QUALITY_ACEPTABLE = "ACEPTABLE"
QUALITY_INSUFICIENTE = "INSUFICIENTE"
QUALITY_NO_APLICABLE = "NO_APLICABLE"
QUALITY_ERROR = "ERROR"

# Threshold constants are now provided by config/signal_scoring_thresholds.json
# via get_threshold_config() from farfan_pipeline.config.threshold_config.
# This module only defines last-resort hardcoded values if the config system fails.

# Load centralized configuration
try:
    from farfan_pipeline.config.threshold_config import get_threshold_config

    _threshold_config = get_threshold_config()
    if not _threshold_config.validation_passed:
        logger.warning(
            f"Threshold config validation failed: {_threshold_config.validation_errors}. "
            "Using potentially degraded but centralized values."
        )

    HIGH_PATTERN_THRESHOLD = _threshold_config.high_pattern_threshold
    HIGH_INDICATOR_THRESHOLD = _threshold_config.high_indicator_threshold
    PATTERN_COMPLEXITY_ADJUSTMENT = _threshold_config.pattern_complexity_adjustment
    INDICATOR_SPECIFICITY_ADJUSTMENT = _threshold_config.indicator_specificity_adjustment
    COMPLETE_EVIDENCE_ADJUSTMENT = _threshold_config.complete_evidence_adjustment
    HIGH_SCORE_THRESHOLD = _threshold_config.high_score_threshold
    LOW_SCORE_THRESHOLD = _threshold_config.low_score_threshold

    logger.info(
        f"Threshold config loaded: HIGH_PATTERN={HIGH_PATTERN_THRESHOLD}, "
        f"HIGH_SCORE={HIGH_SCORE_THRESHOLD}"
    )
except Exception as e:
    logger.warning(f"Failed to load threshold config: {e}. Using fallback values.")
    HIGH_PATTERN_THRESHOLD = 15
    HIGH_INDICATOR_THRESHOLD = 10
    PATTERN_COMPLEXITY_ADJUSTMENT = -0.05
    INDICATOR_SPECIFICITY_ADJUSTMENT = 0.03
    COMPLETE_EVIDENCE_ADJUSTMENT = 0.02
    HIGH_SCORE_THRESHOLD = 0.8
    LOW_SCORE_THRESHOLD = 0.3

__all__ = [
    "SignalEnrichedScorer",
    "get_signal_adjusted_threshold",
    "get_signal_quality_validation",
    "generate_quality_promotion_report",
    # Constants
    "QUALITY_EXCELENTE",
    "QUALITY_ACEPTABLE",
    "QUALITY_INSUFICIENTE",
    "QUALITY_NO_APLICABLE",
    "QUALITY_ERROR",
]


class SignalEnrichedScorer:
    """Signal-enriched scorer for Phase 3 with deterministic enhancements.

    Adds signal intelligence to basic Phase 3 scoring without changing
    core scoring logic. All enhancements are additive and optional.

    Attributes:
        signal_registry: Optional signal registry for signal-driven scoring
        enable_threshold_adjustment: Enable signal-based threshold tuning
        enable_quality_validation: Enable signal-based quality validation
    """

    def __init__(
        self,
        signal_registry: QuestionnaireSignalRegistry | None = None,
        enable_threshold_adjustment: bool = True,
        enable_quality_validation: bool = True,
    ) -> None:
        """Initialize signal-enriched scorer.

        Args:
            signal_registry: Optional signal registry for signal access
            enable_threshold_adjustment: Enable threshold adjustment feature
            enable_quality_validation: Enable quality validation feature
        """
        self.signal_registry = signal_registry
        self.enable_threshold_adjustment = enable_threshold_adjustment
        self.enable_quality_validation = enable_quality_validation

        logger.info(
            f"SignalEnrichedScorer initialized: "
            f"registry={'enabled' if signal_registry else 'disabled'}, "
            f"threshold_adj={enable_threshold_adjustment}, "
            f"quality_val={enable_quality_validation}"
        )

    def adjust_threshold_for_question(
        self,
        question_id: str,
        base_threshold: float,
        score: float,
        metadata: dict[str, Any],
    ) -> tuple[float, dict[str, Any]]:
        """Adjust scoring threshold based on signal-driven question complexity.

        Uses signal registry to determine question complexity and adjust
        thresholds accordingly. More complex questions get slightly lower
        thresholds to account for increased difficulty.

        Args:
            question_id: Question identifier (e.g., "Q001")
            base_threshold: Base threshold from scoring system
            score: Computed score for the question
            metadata: Question metadata dict

        Returns:
            Tuple of (adjusted_threshold, adjustment_details)
        """
        if not self.enable_threshold_adjustment or not self.signal_registry:
            return base_threshold, {"adjustment": "none", "reason": "disabled_or_no_registry"}

        adjustment_details: dict[str, Any] = {
            "base_threshold": base_threshold,
            "adjustments": [],
        }

        adjusted = base_threshold

        try:
            # Get micro answering signals for question
            signal_pack = self.signal_registry.get_micro_answering_signals(question_id)

            # Adjust based on pattern complexity (more patterns = more complex)
            pattern_count = len(getattr(signal_pack, "patterns", []))
            if pattern_count > HIGH_PATTERN_THRESHOLD:
                adjustment = PATTERN_COMPLEXITY_ADJUSTMENT
                adjusted = max(0.3, adjusted + adjustment)
                adjustment_details["adjustments"].append(
                    {
                        "type": "high_pattern_complexity",
                        "pattern_count": pattern_count,
                        "adjustment": adjustment,
                    }
                )

            # Adjust based on indicator count (more indicators = more specific)
            indicator_count = len(getattr(signal_pack, "indicators", []))
            if indicator_count > HIGH_INDICATOR_THRESHOLD:
                adjustment = INDICATOR_SPECIFICITY_ADJUSTMENT
                adjusted = min(0.9, adjusted + adjustment)
                adjustment_details["adjustments"].append(
                    {
                        "type": "high_indicator_specificity",
                        "indicator_count": indicator_count,
                        "adjustment": adjustment,
                    }
                )

            # Adjust based on evidence quality from metadata
            completeness = metadata.get("completeness", "").lower()
            if completeness == "complete":
                adjustment = COMPLETE_EVIDENCE_ADJUSTMENT
                adjusted = min(0.9, adjusted + adjustment)
                adjustment_details["adjustments"].append(
                    {
                        "type": "complete_evidence",
                        "completeness": completeness,
                        "adjustment": adjustment,
                    }
                )

            adjustment_details["adjusted_threshold"] = adjusted
            adjustment_details["total_adjustment"] = adjusted - base_threshold

            logger.debug(
                f"Threshold adjusted for {question_id}: "
                f"{base_threshold:.3f} → {adjusted:.3f} "
                f"(Δ={adjusted - base_threshold:+.3f})"
            )

        except Exception as e:
            logger.warning(
                f"Failed to adjust threshold for {question_id}: {e}. "
                f"Using base threshold {base_threshold:.3f}"
            )
            adjustment_details["error"] = str(e)
            adjusted = base_threshold

        return adjusted, adjustment_details

    def validate_quality_level(
        self,
        question_id: str,
        quality_level: str,
        score: float,
        completeness: str | None,
    ) -> tuple[str, dict[str, Any]]:
        """Validate and potentially adjust quality level using signal intelligence.

        Uses signal-based heuristics to ensure quality level is consistent
        with score, completeness, and question characteristics.

        QUALITY PROMOTION/DEMOTION TRACKING:
        All quality level changes are logged explicitly with full provenance
        including original quality, new quality, trigger reason, score, and completeness.

        Args:
            question_id: Question identifier
            quality_level: Computed quality level from Phase 3
            score: Numeric score (0.0-1.0)
            completeness: Completeness enum from EvidenceNexus

        Returns:
            Tuple of (validated_quality_level, validation_details)
            validation_details includes:
              - original_quality: Original quality level
              - validated_quality: Final quality level
              - adjusted: Boolean whether quality was changed
              - promotion_reason: If promoted, the reason
              - demotion_reason: If demoted, the reason
              - checks: List of all validation checks performed
        """
        if not self.enable_quality_validation:
            return quality_level, {"validation": "disabled"}

        validation_details: dict[str, Any] = {
            "original_quality": quality_level,
            "score": score,
            "completeness": completeness,
            "checks": [],
            "promotion_reason": None,
            "demotion_reason": None,
        }

        validated = quality_level
        was_promoted = False
        was_demoted = False

        try:
            # Check 1: Score-quality consistency
            if score >= HIGH_SCORE_THRESHOLD and quality_level in [
                QUALITY_INSUFICIENTE,
                QUALITY_NO_APLICABLE,
            ]:
                validation_details["checks"].append(
                    {
                        "check": "score_quality_consistency",
                        "issue": "high_score_low_quality",
                        "action": "promote_quality",
                        "score": score,
                        "threshold": HIGH_SCORE_THRESHOLD,
                    }
                )
                validated = QUALITY_ACEPTABLE  # Promote to at least ACEPTABLE
                validation_details["promotion_reason"] = (
                    f"High score {score:.3f} >= {HIGH_SCORE_THRESHOLD} "
                    f"inconsistent with {quality_level}"
                )
                was_promoted = True
                logger.warning(
                    f"[QUALITY PROMOTION] {question_id}: "
                    f"{quality_level} → {validated} | "
                    f"Reason: high_score={score:.3f} >= {HIGH_SCORE_THRESHOLD} | "
                    f"Completeness: {completeness}"
                )

            # Check 2: Completeness-quality alignment
            if completeness == "complete" and quality_level == QUALITY_INSUFICIENTE:
                validation_details["checks"].append(
                    {
                        "check": "completeness_quality_alignment",
                        "issue": "complete_evidence_low_quality",
                        "action": "promote_quality",
                        "completeness": completeness,
                    }
                )
                validated = QUALITY_ACEPTABLE  # At least ACEPTABLE for complete evidence
                if not was_promoted:  # Don't override previous promotion reason
                    validation_details["promotion_reason"] = (
                        f"Complete evidence with {quality_level} quality is inconsistent"
                    )
                was_promoted = True
                logger.warning(
                    f"[QUALITY PROMOTION] {question_id}: "
                    f"{quality_level} → {validated} | "
                    f"Reason: complete_evidence with {quality_level} | "
                    f"Score: {score:.3f}"
                )

            # Check 3: Low score validation
            if score < LOW_SCORE_THRESHOLD and quality_level == QUALITY_EXCELENTE:
                validation_details["checks"].append(
                    {
                        "check": "low_score_validation",
                        "issue": "low_score_high_quality",
                        "action": "demote_quality",
                        "score": score,
                        "threshold": LOW_SCORE_THRESHOLD,
                    }
                )
                validated = QUALITY_ACEPTABLE  # Demote to ACEPTABLE
                validation_details["demotion_reason"] = (
                    f"Low score {score:.3f} < {LOW_SCORE_THRESHOLD} "
                    f"inconsistent with {quality_level}"
                )
                was_demoted = True
                logger.warning(
                    f"[QUALITY DEMOTION] {question_id}: "
                    f"{quality_level} → {validated} | "
                    f"Reason: low_score={score:.3f} < {LOW_SCORE_THRESHOLD} | "
                    f"Completeness: {completeness}"
                )

            validation_details["validated_quality"] = validated
            validation_details["adjusted"] = validated != quality_level
            validation_details["was_promoted"] = was_promoted
            validation_details["was_demoted"] = was_demoted

            # Add cascade check: warn if both promotion and demotion attempted
            if was_promoted and was_demoted:
                logger.error(
                    f"[QUALITY CASCADE DETECTED] {question_id}: "
                    f"Both promotion and demotion attempted! Original: {quality_level}, "
                    f"Final: {validated}. This indicates conflicting quality signals."
                )
                validation_details["cascade_detected"] = True

        except Exception as e:
            logger.error(
                f"[QUALITY VALIDATION ERROR] {question_id}: "
                f"Failed to validate quality: {type(e).__name__}: {e}. "
                f"Using original quality {quality_level}"
            )
            validation_details["error"] = str(e)
            validated = quality_level

        return validated, validation_details

    def apply_signal_adjustments(
        self,
        raw_score: float,
        question_id: str,
        enriched_pack: dict[str, Any] | None,
    ) -> tuple[float, dict[str, Any]]:
        """
        Apply signal presence bonus/penalty to raw score.

        Implements SISAS signal-driven scoring adjustments:
        - +0.05 bonus per primary signal present (cap at +0.15)
        - -0.10 penalty per missing primary signal (no floor)

        This is called AFTER existing modality scoring, before final threshold checks.

        Args:
            raw_score: Score after modality (TYPE_A-F) scoring
            question_id: Question being scored
            enriched_pack: Signal enrichment pack from Phase 1

        Returns:
            Tuple of (adjusted_score, adjustment_log)
        """
        adjustment_log = {
            "raw_score": raw_score,
            "signal_bonus": 0.0,
            "signal_penalty": 0.0,
            "net_adjustment": 0.0,
            "adjusted_score": raw_score,
            "signals_evaluated": [],
        }

        if not enriched_pack:
            adjustment_log["status"] = "no_enriched_pack"
            return raw_score, adjustment_log

        # Get expected signals for question using QuestionnaireSignalRegistry
        # Error handling strategy:
        # - Import/registry availability failures cause an explicit hard fail
        # - Other issues are logged and we proceed with a well-defined fallback
        expected_primary = []
        try:
            if _QuestionnaireSignalRegistryRuntime is None:
                # Hard fail if registry is not available - this is a critical dependency
                raise RuntimeError(
                    "QuestionnaireSignalRegistry is required but not available. "
                    "Cannot perform signal-enriched scoring without signal registry."
                ) from _questionnaire_signal_registry_import_error

            registry = _QuestionnaireSignalRegistryRuntime()
            mapping = registry.get_question_mapping(question_id)
            if mapping:
                # Primary signals are the ones we expect
                expected_primary = mapping.primary_signals
            else:
                logger.warning(
                    f"No signal mapping found for question {question_id} in QuestionnaireSignalRegistry"
                )
        except Exception as e:
            # Log and fail explicitly for other errors - NO SILENT FAILURES
            logger.error(
                f"Failed to get expected signals for {question_id}: {type(e).__name__}: {e}"
            )
            raise RuntimeError(
                f"Failed to retrieve signal mapping for {question_id}: {e}"
            ) from e

        # Get signals that were actually detected
        received_signals = enriched_pack.get("signals_detected", [])

        # Calculate bonus for present signals
        signal_bonus = 0.0
        for signal in expected_primary:
            if signal in received_signals:
                signal_bonus += 0.05
                adjustment_log["signals_evaluated"].append(
                    {
                        "signal": signal,
                        "status": "present",
                        "adjustment": 0.05,
                    }
                )
        signal_bonus = min(0.15, signal_bonus)  # Cap at +0.15

        # Calculate penalty for missing signals
        signal_penalty = 0.0
        for signal in expected_primary:
            if signal not in received_signals:
                signal_penalty += 0.10
                adjustment_log["signals_evaluated"].append(
                    {
                        "signal": signal,
                        "status": "missing",
                        "adjustment": -0.10,
                    }
                )

        # Apply adjustments
        net_adjustment = signal_bonus - signal_penalty
        adjusted_score = max(0.0, min(1.0, raw_score + net_adjustment))

        adjustment_log.update(
            {
                "signal_bonus": round(signal_bonus, 3),
                "signal_penalty": round(signal_penalty, 3),
                "net_adjustment": round(net_adjustment, 3),
                "adjusted_score": round(adjusted_score, 3),
                "status": "applied",
            }
        )

        logger.info(
            f"Signal adjustment for {question_id}: "
            f"{raw_score:.3f} → {adjusted_score:.3f} (Δ={net_adjustment:+.3f})"
        )

        return adjusted_score, adjustment_log

    def enrich_scoring_details(
        self,
        question_id: str,
        base_scoring_details: dict[str, Any],
        threshold_adjustment: dict[str, Any],
        quality_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Enrich scoring details with signal provenance.

        Adds signal-based metadata to scoring details for full transparency
        and reproducibility.

        Args:
            question_id: Question identifier
            base_scoring_details: Base scoring details from Phase 3
            threshold_adjustment: Threshold adjustment details
            quality_validation: Quality validation details

        Returns:
            Enriched scoring details dict
        """
        enriched = {
            **base_scoring_details,
            "signal_enrichment": {
                "enabled": True,
                "registry_available": self.signal_registry is not None,
                "threshold_adjustment": threshold_adjustment,
                "quality_validation": quality_validation,
            },
        }

        return enriched


def generate_quality_promotion_report(
    all_validation_details: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate comprehensive report of all quality promotions/demotions.

    This function aggregates all quality level changes across all questions
    and generates a summary report for audit and debugging purposes.

    Args:
        all_validation_details: List of validation_details dicts from all questions

    Returns:
        Report dict with:
          - summary: Overall promotion/demotion statistics
          - promotions: List of all promotions with full context
          - demotions: List of all demotions with full context
          - cascades: List of questions where both promotion and demotion occurred
          - by_reason: Breakdown of changes by trigger reason
    """
    promotions = []
    demotions = []
    cascades = []
    no_change = 0

    reason_counts = {}

    for details in all_validation_details:
        if not details.get("adjusted", False):
            no_change += 1
            continue

        question_id = details.get("question_id", "UNKNOWN")

        # Track promotions
        if details.get("was_promoted", False):
            promotion_reason = details.get("promotion_reason", "Unknown reason")
            promotions.append(
                {
                    "question_id": question_id,
                    "original_quality": details.get("original_quality"),
                    "new_quality": details.get("validated_quality"),
                    "reason": promotion_reason,
                    "score": details.get("score"),
                    "completeness": details.get("completeness"),
                }
            )
            reason_counts[promotion_reason] = reason_counts.get(promotion_reason, 0) + 1

        # Track demotions
        if details.get("was_demoted", False):
            demotion_reason = details.get("demotion_reason", "Unknown reason")
            demotions.append(
                {
                    "question_id": question_id,
                    "original_quality": details.get("original_quality"),
                    "new_quality": details.get("validated_quality"),
                    "reason": demotion_reason,
                    "score": details.get("score"),
                    "completeness": details.get("completeness"),
                }
            )
            reason_counts[demotion_reason] = reason_counts.get(demotion_reason, 0) + 1

        # Track cascades (both promotion and demotion)
        if details.get("cascade_detected", False):
            cascades.append(
                {
                    "question_id": question_id,
                    "original_quality": details.get("original_quality"),
                    "final_quality": details.get("validated_quality"),
                    "promotion_reason": details.get("promotion_reason"),
                    "demotion_reason": details.get("demotion_reason"),
                }
            )

    report = {
        "summary": {
            "total_questions": len(all_validation_details),
            "promotions": len(promotions),
            "demotions": len(demotions),
            "no_change": no_change,
            "cascades_detected": len(cascades),
            "promotion_rate": round(len(promotions) / len(all_validation_details) * 100, 2)
            if all_validation_details
            else 0,
            "demotion_rate": round(len(demotions) / len(all_validation_details) * 100, 2)
            if all_validation_details
            else 0,
        },
        "promotions": promotions,
        "demotions": demotions,
        "cascades": cascades,
        "by_reason": reason_counts,
    }

    logger.info(
        f"[QUALITY PROMOTION REPORT] "
        f"Total: {len(all_validation_details)} | "
        f"Promotions: {len(promotions)} ({report['summary']['promotion_rate']:.1f}%) | "
        f"Demotions: {len(demotions)} ({report['summary']['demotion_rate']:.1f}%) | "
        f"Cascades: {len(cascades)}"
    )

    return report


def get_signal_adjusted_threshold(
    signal_registry: QuestionnaireSignalRegistry | None,
    question_id: str,
    base_threshold: float,
    score: float,
    metadata: dict[str, Any],
) -> tuple[float, dict[str, Any]]:
    """Convenience function for signal-based threshold adjustment.

    Creates a temporary SignalEnrichedScorer and returns adjusted threshold.

    Args:
        signal_registry: Signal registry instance (optional)
        question_id: Question identifier
        base_threshold: Base threshold value
        score: Computed score
        metadata: Question metadata

    Returns:
        Tuple of (adjusted_threshold, adjustment_details)
    """
    scorer = SignalEnrichedScorer(signal_registry=signal_registry)
    return scorer.adjust_threshold_for_question(
        question_id=question_id,
        base_threshold=base_threshold,
        score=score,
        metadata=metadata,
    )


def get_signal_quality_validation(
    question_id: str,
    quality_level: str,
    score: float,
    completeness: str | None,
) -> tuple[str, dict[str, Any]]:
    """Convenience function for signal-based quality validation.

    Creates a temporary SignalEnrichedScorer and returns validated quality.

    Args:
        question_id: Question identifier
        quality_level: Original quality level
        score: Computed score
        completeness: Completeness enum

    Returns:
        Tuple of (validated_quality, validation_details)
    """
    scorer = SignalEnrichedScorer()
    return scorer.validate_quality_level(
        question_id=question_id,
        quality_level=quality_level,
        score=score,
        completeness=completeness,
    )
