"""Phase 7 Systemic Gap Detector with Normative Baseline

Enhanced systemic gap detection using normative compliance baseline from
corpus_empirico_normatividad.json. Identifies gaps prioritized by mandatory
norm violations and contextual validation rules.

Key Features:
- Normative baseline-driven gap detection
- Priority classification (CRITICAL/HIGH/MEDIUM/LOW)
- Contextual validation rules (PDET, ethnic, coastal)
- Gap remediation recommendations

EMPIRICAL BASELINE: 14 PDT Colombia 2024-2027
SOURCE: canonic_questionnaire_central/_registry/entities/normative_compliance.json
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 7
__stage__ = 10
__order__ = 10
__author__ = "F.A.R.F.A.N Core Team - Empirical Corpus Integration"
__created__ = "2026-01-12"
__modified__ = "2026-01-12"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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


# =============================================================================
# SYSTEMIC GAP DETECTOR
# =============================================================================


class SystemicGapDetector:
    """Detects systemic gaps using normative baseline.

    Enhanced gap detection that combines quality-level thresholds with
    normative compliance validation from empirical corpus.

    Attributes:
        score_threshold: Score threshold for gap detection (default: 0.55)
        normative_validator: NormativeComplianceValidator instance
        enable_normative_validation: Enable normative baseline validation
    """

    def __init__(
        self,
        score_threshold: float = 0.55,
        corpus_path: Path | str | None = None,
        enable_normative_validation: bool = True,
    ):
        """Initialize systemic gap detector.

        Args:
            score_threshold: Score threshold for gap detection (INSUFICIENTE)
            corpus_path: Optional path to normative_compliance.json
            enable_normative_validation: Enable normative baseline validation
        """
        self.score_threshold = score_threshold
        self.enable_normative_validation = enable_normative_validation

        # Load normative compliance validator
        self.normative_validator = None
        if enable_normative_validation:
            try:
                from farfan_pipeline.phases.Phase_3.phase3_10_00_normative_compliance_validator import (
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

                gaps.append(gap)
                logger.info(
                    f"Systemic gap detected: {area_name} "
                    f"(score={normalized_score:.3f}, priority={gap.priority})"
                )

        # Sort gaps by priority (CRITICAL first)
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        gaps.sort(key=lambda g: (priority_order.get(g.priority, 4), g.score))

        logger.info(f"Total systemic gaps detected: {len(gaps)}")
        return gaps

    def _normalize_score(self, score: float) -> float:
        """Normalize score to 0-1 range.

        Args:
            score: Input score (may be 0-3 or 0-1)

        Returns:
            Normalized score (0-1)
        """
        # Detect if score is already normalized
        if 0.0 <= score <= 1.0:
            return score

        # Assume 0-3 range, normalize
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
