# phase8_00_00_data_models.py - Data Models for Phase 8
"""
Module: src.farfan_pipeline.phases.Phase_eight.phase8_00_00_data_models
Purpose: Core data structures for Phase 8 recommendations
Owner: phase8_core
Stage: 0 (Base)
Order: 00
Type: DATA
Lifecycle: ACTIVE
Version: 3.0.0
Effective-Date: 2026-01-10

This module centralizes all data structures for Phase 8.
Extracted from phase8_20_00_recommendation_engine.py for better separation of concerns.

Enhancement: Window 1 - Schema-driven data models
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 8
__stage__ = 0
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "LOW"
__execution_pattern__ = "On-Demand"

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from farfan_pipeline.calibration.decorators import (
    calibrated_method,
)

logger = logging.getLogger(__name__)

__all__ = [
    "Recommendation",
    "RecommendationSet",
    "RuleCondition",
    "TemplateContext",
    "ValidationResult",
]

# ============================================================================
# RECOMMENDATION DATA STRUCTURES
# ============================================================================


@dataclass
class Recommendation:
    """
    Structured recommendation with full intervention details.

    Supports both v1.0 (simple) and v2.0 (enhanced with 7 advanced features):
    1. Template parameterization
    2. Execution logic
    3. Measurable indicators
    4. Unambiguous time horizons
    5. Testable verification
    6. Cost tracking
    7. Authority mapping

    Attributes:
        rule_id: Unique identifier for the rule that generated this recommendation
        level: Recommendation level (MICRO, MESO, or MACRO)
        problem: Description of the problem being addressed
        intervention: Detailed intervention description
        indicator: Measurable indicator dictionary
        responsible: Entity and role responsible for implementation
        horizon: Time horizon dictionary with start and end dates
        verification: List of verification artifacts
        metadata: Additional metadata about the recommendation
        execution: Execution logic block (v2.0)
        budget: Budget information (v2.0)
        template_id: Template identifier used (v2.0)
        template_params: Template parameters used (v2.0)
    """

    rule_id: str
    level: str  # MICRO, MESO, or MACRO
    problem: str
    intervention: str
    indicator: dict[str, Any]
    responsible: dict[str, Any]
    horizon: dict[str, Any]
    verification: list[Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    # Enhanced fields (v2.0) - optional for backward compatibility
    execution: dict[str, Any] | None = None
    budget: dict[str, Any] | None = None
    template_id: str | None = None
    template_params: dict[str, Any] | None = None

    @calibrated_method(
        "farfan_core.analysis.recommendation_engine.Recommendation.to_dict"
    )
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation with None values removed
        """
        result = asdict(self)
        # Remove None values for cleaner output
        return {k: v for k, v in result.items() if v is not None}

    def get_confidence(self) -> float:
        """
        Calculate confidence score for this recommendation.

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from metadata
        if "gap" in self.metadata:
            gap = self.metadata["gap"]
            # Larger gap = higher confidence
            confidence = min(0.6 + (gap * 0.2), 1.0)
        else:
            confidence = 0.6  # Minimum threshold

        return round(confidence, 2)


@dataclass
class RecommendationSet:
    """
    Collection of recommendations with metadata.

    Attributes:
        level: Level of recommendations (MICRO, MESO, or MACRO)
        recommendations: List of recommendations at this level
        generated_at: ISO timestamp of generation
        total_rules_evaluated: Total number of rules evaluated
        rules_matched: Number of rules that matched and generated recommendations
        metadata: Additional metadata about the recommendation set
    """

    level: str
    recommendations: list[Recommendation]
    generated_at: str
    total_rules_evaluated: int
    rules_matched: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @calibrated_method(
        "farfan_core.analysis.recommendation_engine.RecommendationSet.to_dict"
    )
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the recommendation set
        """
        return {
            "level": self.level,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "generated_at": self.generated_at,
            "total_rules_evaluated": self.total_rules_evaluated,
            "rules_matched": self.rules_matched,
            "metadata": self.metadata,
        }

    def get_match_rate(self) -> float:
        """
        Calculate the match rate (rules matched / rules evaluated).

        Returns:
            Match rate as a float between 0.0 and 1.0
        """
        if self.total_rules_evaluated == 0:
            return 0.0
        return round(self.rules_matched / self.total_rules_evaluated, 3)

    def get_average_confidence(self) -> float:
        """
        Calculate average confidence across all recommendations.

        Returns:
            Average confidence score
        """
        if not self.recommendations:
            return 0.0

        confidences = [r.get_confidence() for r in self.recommendations]
        return round(sum(confidences) / len(confidences), 3)

    def filter_by_confidence(self, min_confidence: float = 0.7) -> list[Recommendation]:
        """
        Filter recommendations by minimum confidence threshold.

        Args:
            min_confidence: Minimum confidence threshold (default 0.7)

        Returns:
            List of recommendations meeting the confidence threshold
        """
        return [r for r in self.recommendations if r.get_confidence() >= min_confidence]


# ============================================================================
# RULE PROCESSING DATA STRUCTURES
# ============================================================================


@dataclass
class RuleCondition:
    """
    Parsed rule condition for evaluation.

    Attributes:
        level: Rule level (MICRO, MESO, or MACRO)
        pa_id: Policy area ID (MICRO only)
        dim_id: Dimension ID (MICRO only)
        cluster_id: Cluster ID (MESO only)
        score_range: Optional score range tuple (min, max)
        score_band: Optional score band (BAJO, MEDIO, ALTO)
        variance_level: Optional variance level (BAJA, MEDIA, ALTA)
        variance_threshold: Optional variance threshold
        weak_pa_id: Optional weak policy area ID
        macro_band: Optional macro band
        clusters_below_target: Optional list of clusters below target
        priority_micro_gaps: Optional list of priority micro gaps
    """

    level: str
    pa_id: str | None = None
    dim_id: str | None = None
    cluster_id: str | None = None
    score_range: tuple[float, float] | None = None
    score_band: str | None = None
    variance_level: str | None = None
    variance_threshold: float | None = None
    weak_pa_id: str | None = None
    macro_band: str | None = None
    clusters_below_target: list[str] | None = None
    priority_micro_gaps: list[str] | None = None

    def matches(self, data: dict[str, Any]) -> bool:
        """
        Check if this condition matches the provided data.

        Args:
            data: Data dictionary to check against

        Returns:
            True if condition matches, False otherwise
        """
        if self.level == "MICRO":
            return self._matches_micro(data)
        elif self.level == "MESO":
            return self._matches_meso(data)
        elif self.level == "MACRO":
            return self._matches_macro(data)
        return False

    def _matches_micro(self, data: dict[str, Any]) -> bool:
        """Check MICRO condition match."""
        if self.pa_id and self.dim_id:
            key = f"{self.pa_id}-{self.dim_id}"
            if key not in data:
                return False
            if self.score_range:
                score = data[key]
                min_score, max_score = self.score_range
                return min_score <= score < max_score
        return False

    def _matches_meso(self, data: dict[str, Any]) -> bool:
        """Check MESO condition match."""
        if self.cluster_id and self.cluster_id in data:
            cluster = data[self.cluster_id]
            if self.score_band:
                score = cluster.get("score", 0)
                band_ranges = {"BAJO": (0, 55), "MEDIO": (55, 75), "ALTO": (75, 100)}
                if self.score_band in band_ranges:
                    min_s, max_s = band_ranges[self.score_band]
                    return min_s <= score < max_s
        return False

    def _matches_macro(self, data: dict[str, Any]) -> bool:
        """Check MACRO condition match."""
        if self.macro_band:
            return data.get("macro_band") == self.macro_band
        return True


@dataclass
class TemplateContext:
    """
    Context for template rendering.

    Attributes:
        pa_id: Policy area ID
        dim_id: Dimension ID
        cluster_id: Cluster ID
        question_id: Question ID
        extra: Additional context variables
    """

    pa_id: str | None = None
    dim_id: str | None = None
    cluster_id: str | None = None
    question_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for template rendering."""
        result = {}
        if self.pa_id:
            result["PAxx"] = self.pa_id
            result["pa_id"] = self.pa_id
        if self.dim_id:
            result["DIMxx"] = self.dim_id
            result["dim_id"] = self.dim_id
        if self.cluster_id:
            result["cluster_id"] = self.cluster_id
        if self.question_id:
            result["question_id"] = self.question_id
            result["Q001"] = self.question_id
        result.update(self.extra)
        return result

    @classmethod
    def from_rule_when(cls, when: dict[str, Any]) -> "TemplateContext":
        """
        Create TemplateContext from rule's 'when' clause.

        Args:
            when: Rule's when clause dictionary

        Returns:
            TemplateContext instance
        """
        return cls(
            pa_id=when.get("pa_id"),
            dim_id=when.get("dim_id"),
            cluster_id=when.get("cluster_id"),
            question_id=when.get("question_id"),
        )


# ============================================================================
# VALIDATION DATA STRUCTURES
# ============================================================================


@dataclass
class ValidationResult:
    """
    Result of a validation operation.

    Attributes:
        is_valid: Whether validation passed
        errors: List of error messages
        warnings: List of warning messages
        timestamp: When validation was performed
        rule_hash: Content hash of validated rule
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    rule_hash: str = ""

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """
        Merge another ValidationResult into this one.

        Args:
            other: Another ValidationResult to merge

        Returns:
            Merged ValidationResult
        """
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            timestamp=max(self.timestamp, other.timestamp),
        )
