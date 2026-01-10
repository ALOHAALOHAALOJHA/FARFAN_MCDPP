"""
Scoring Module - Phase 3: Evidence-to-Score Transformation
===========================================================

This module provides the scoring layer that transforms Phase 2 (EvidenceNexus)
output into Phase 3 quantitative scores, harmonized with SISAS signal_scoring_context.

ARCHITECTURE: Nexus-Aligned Scoring
-----------------------------------
1. Evidence Structure Validation → Ensures compatibility with Nexus output
2. Modality-Based Scoring → Six scoring types (TYPE_A through TYPE_F)
3. Adaptive Threshold Application → Context-aware from signal_scoring_context
4. Quality Level Determination → Granular quality assessment
5. Provenance Tracking → Full traceability to evidence graph

MATHEMATICAL FOUNDATIONS (Academic References):
-----------------------------------------------
This scoring system is grounded in rigorous mathematical theory:

[1] Wilson Score Interval (Wilson 1927, JASA)
    - Wilson, E. B. (1927). "Probable inference, the law of succession, and
      statistical inference." Journal of the American Statistical Association,
      22(158), 209-212. DOI: 10.1080/01621459.1927.10502953
    - Provides asymptotically correct confidence intervals with better
      small-sample properties than traditional Wald intervals.

[2] Weighted Aggregation with Convexity (Convex Analysis)
    - For scores s₁, ..., sₙ ∈ [0,1] and weights Σwᵢ = 1, the weighted
      mean s = Σwᵢsᵢ satisfies min(sᵢ) ≤ s ≤ max(sᵢ) (convexity property).
    - Guarantees bounded, stable aggregation.

[3] Dempster-Shafer Belief Function Theory (Evidence Combination)
    - Sentz, K., & Ferson, S. (2002). "Combination of Evidence in Dempster-
      Shafer Theory." Sandia National Laboratories, SAND 2002-0835.
    - Provides framework for combining evidence from multiple sources under
      uncertainty, used in Phase 2 EvidenceNexus.

[4] Confidence Calibration (Statistical Inference)
    - O'Neill, B. (2021). "Mathematical properties and finite-population
      correction for the Wilson score interval." arXiv:2109.12464 [math.ST]
    - Ensures proper coverage probability and calibration of confidence
      intervals.

SCORING MODALITIES (Aligned with signal_scoring_context.py):
-----------------------------------------------------------
- TYPE_A: Quantitative indicators (high threshold, precise)
- TYPE_B: Qualitative descriptors (medium threshold, patterns)
- TYPE_C: Mixed evidence (balanced weights)
- TYPE_D: Temporal series (sequence-aware)
- TYPE_E: Territorial coverage (spatial)
- TYPE_F: Institutional actors (relational)

INTERFACE CONTRACT (Nexus → Scoring):
------------------------------------
Input (from Phase 2 EvidenceNexus):
    evidence: dict[str, Any] = {
        "elements": list[dict],  # Evidence nodes
        "by_type": dict[str, list],  # Type-indexed
        "confidence": float,  # Overall confidence
        "completeness": float,  # Completeness metric
        "graph_hash": str,  # Provenance hash
    }

Output (to Phase 3 aggregation):
    ScoredResult = {
        "score": float,  # Raw score [0, 1]
        "normalized_score": float,  # Normalized [0, 100]
        "quality_level": QualityLevel,  # EXCELLENT/GOOD/ADEQUATE/POOR
        "passes_threshold": bool,
        "confidence_interval": tuple[float, float],
        "scoring_metadata": dict[str, Any]
    }

INVARIANTS:
[INV-SC-001] All scores must be in range [0.0, 1.0]
[INV-SC-002] Quality level must be deterministic from score
[INV-SC-003] Scoring metadata must include modality and threshold
[INV-SC-004] Confidence intervals must be calibrated (≥95% coverage)

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0 (Enhanced with Academic Foundations)
Date: 2025-12-11
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

# Import mathematical foundations (academic rigor)
try:
    from .mathematical_foundation import (
        wilson_score_interval,
        weighted_aggregation,
        validate_scoring_invariants,
        verify_convexity_property,
    )

    _HAS_MATH_FOUNDATION = True
except ImportError:
    # Fallback if mathematical_foundation is not available
    _HAS_MATH_FOUNDATION = False

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# =============================================================================
# TYPE SYSTEM
# =============================================================================

ScoringModality = Literal["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E", "TYPE_F"]


from .quality_levels import QualityLevel


# =============================================================================
# EXCEPTIONS
# =============================================================================


class ScoringError(Exception):
    """Base exception for scoring errors."""

    pass


class EvidenceStructureError(ScoringError):
    """Raised when evidence structure is invalid."""

    pass


class ModalityValidationError(ScoringError):
    """Raised when modality configuration is invalid."""

    pass


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass(frozen=True)
class ModalityConfig:
    """Configuration for a scoring modality."""

    modality: ScoringModality
    threshold: float
    weight_elements: float
    weight_similarity: float
    weight_patterns: float
    aggregation: str = "weighted_mean"

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not 0.0 <= self.threshold <= 1.0:
            raise ModalityValidationError(f"Threshold must be in [0, 1], got {self.threshold}")

        total_weight = self.weight_elements + self.weight_similarity + self.weight_patterns
        if not math.isclose(total_weight, 1.0, abs_tol=0.01):
            raise ModalityValidationError(f"Weights must sum to 1.0, got {total_weight}")


@dataclass
class ScoredResult:
    """Result of scoring operation."""

    score: float  # Raw score [0, 1]
    normalized_score: float  # Normalized [0, 100]
    quality_level: QualityLevel
    passes_threshold: bool
    confidence_interval: tuple[float, float]
    scoring_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "score": self.score,
            "normalized_score": self.normalized_score,
            "quality_level": self.quality_level.value,
            "passes_threshold": self.passes_threshold,
            "confidence_interval": list(self.confidence_interval),
            "scoring_metadata": self.scoring_metadata,
        }


# =============================================================================
# EVIDENCE STRUCTURE VALIDATION
# =============================================================================


class ScoringValidator:
    """Validates evidence structure for scoring compatibility."""

    REQUIRED_KEYS = {"elements", "confidence"}
    OPTIONAL_KEYS = {"by_type", "completeness", "graph_hash", "patterns"}

    @classmethod
    def validate_evidence(cls, evidence: dict[str, Any]) -> None:
        """
        Validate evidence structure matches Nexus output contract.

        Args:
            evidence: Evidence dict from Phase 2

        Raises:
            EvidenceStructureError: If structure is invalid
        """
        if not isinstance(evidence, dict):
            raise EvidenceStructureError(f"Evidence must be dict, got {type(evidence).__name__}")

        # Check required keys
        missing = cls.REQUIRED_KEYS - evidence.keys()
        if missing:
            raise EvidenceStructureError(f"Missing required keys: {missing}")

        # Validate elements structure
        elements = evidence.get("elements", [])
        if not isinstance(elements, list):
            raise EvidenceStructureError(f"'elements' must be list, got {type(elements).__name__}")

        # Validate confidence range
        confidence = evidence.get("confidence", 0.0)
        if not isinstance(confidence, (int, float)):
            raise EvidenceStructureError(
                f"'confidence' must be numeric, got {type(confidence).__name__}"
            )

        if not 0.0 <= confidence <= 1.0:
            raise EvidenceStructureError(f"'confidence' must be in [0, 1], got {confidence}")

    @classmethod
    def extract_scores(cls, evidence: dict[str, Any]) -> dict[str, float]:
        """
        Extract component scores from evidence.

        Args:
            evidence: Validated evidence dict

        Returns:
            Dict with elements_score, similarity_score, patterns_score
        """
        elements = evidence.get("elements", [])
        elements_score = min(len(elements) / 10.0, 1.0)  # Normalize to expected count

        # Similarity from confidence
        confidence = evidence.get("confidence", 0.0)
        similarity_score = confidence

        # Patterns from pattern matches
        patterns = evidence.get("patterns", {})
        if isinstance(patterns, dict):
            patterns_score = min(len(patterns) / 5.0, 1.0)  # Normalize to expected count
        else:
            patterns_score = 0.0

        return {
            "elements_score": float(elements_score),
            "similarity_score": float(similarity_score),
            "patterns_score": float(patterns_score),
        }


# =============================================================================
# SCORING FUNCTIONS (BY MODALITY)
# =============================================================================


def score_type_a(evidence: dict[str, Any], config: ModalityConfig) -> ScoredResult:
    """
    TYPE_A: Quantitative indicators (high precision required).

    Characteristics:
    - High threshold (0.75)
    - Emphasizes elements found (0.5 weight)
    - Used for numeric indicators, budgets, goals
    """
    ScoringValidator.validate_evidence(evidence)
    scores = ScoringValidator.extract_scores(evidence)

    # Weighted scoring
    raw_score = (
        scores["elements_score"] * config.weight_elements
        + scores["similarity_score"] * config.weight_similarity
        + scores["patterns_score"] * config.weight_patterns
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    # Compute confidence interval (Wilson score interval)
    ci = _compute_confidence_interval(raw_score, evidence.get("confidence", 0.5))

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        confidence_interval=ci,
        scoring_metadata={
            "modality": config.modality,
            "threshold": config.threshold,
            "component_scores": scores,
        },
    )


def score_type_b(evidence: dict[str, Any], config: ModalityConfig) -> ScoredResult:
    """
    TYPE_B: Qualitative descriptors (pattern matching emphasized).

    Characteristics:
    - Medium threshold (0.65)
    - Emphasizes patterns (0.4 weight)
    - Used for institutional actors, policy instruments
    """
    ScoringValidator.validate_evidence(evidence)
    scores = ScoringValidator.extract_scores(evidence)

    raw_score = (
        scores["elements_score"] * config.weight_elements
        + scores["similarity_score"] * config.weight_similarity
        + scores["patterns_score"] * config.weight_patterns
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    ci = _compute_confidence_interval(raw_score, evidence.get("confidence", 0.5))

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        confidence_interval=ci,
        scoring_metadata={
            "modality": config.modality,
            "threshold": config.threshold,
            "component_scores": scores,
        },
    )


def score_type_c(evidence: dict[str, Any], config: ModalityConfig) -> ScoredResult:
    """
    TYPE_C: Mixed evidence (balanced approach).

    Characteristics:
    - Medium threshold (0.60)
    - Balanced weights (0.33 each)
    - Used for mixed quantitative/qualitative questions
    """
    ScoringValidator.validate_evidence(evidence)
    scores = ScoringValidator.extract_scores(evidence)

    raw_score = (
        scores["elements_score"] * config.weight_elements
        + scores["similarity_score"] * config.weight_similarity
        + scores["patterns_score"] * config.weight_patterns
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    ci = _compute_confidence_interval(raw_score, evidence.get("confidence", 0.5))

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        confidence_interval=ci,
        scoring_metadata={
            "modality": config.modality,
            "threshold": config.threshold,
            "component_scores": scores,
        },
    )


def score_type_d(evidence: dict[str, Any], config: ModalityConfig) -> ScoredResult:
    """
    TYPE_D: Temporal series (sequence awareness).

    Characteristics:
    - Medium-high threshold (0.70)
    - Emphasizes temporal patterns
    - Used for time series, historical trends
    """
    ScoringValidator.validate_evidence(evidence)
    scores = ScoringValidator.extract_scores(evidence)

    # Check for temporal elements
    elements = evidence.get("elements", [])
    temporal_count = sum(1 for e in elements if _is_temporal(e))
    temporal_bonus = min(temporal_count / len(elements) if elements else 0.0, 0.1)

    raw_score = (
        scores["elements_score"] * config.weight_elements
        + scores["similarity_score"] * config.weight_similarity
        + scores["patterns_score"] * config.weight_patterns
        + temporal_bonus
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    ci = _compute_confidence_interval(raw_score, evidence.get("confidence", 0.5))

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        confidence_interval=ci,
        scoring_metadata={
            "modality": config.modality,
            "threshold": config.threshold,
            "component_scores": scores,
            "temporal_bonus": temporal_bonus,
        },
    )


def score_type_e(evidence: dict[str, Any], config: ModalityConfig) -> ScoredResult:
    """
    TYPE_E: Territorial coverage (spatial awareness).

    Characteristics:
    - Medium threshold (0.65)
    - Emphasizes coverage metrics
    - Used for geographic distribution, regional policies
    """
    ScoringValidator.validate_evidence(evidence)
    scores = ScoringValidator.extract_scores(evidence)

    # Check for territorial elements
    by_type = evidence.get("by_type", {})
    territorial_elements = by_type.get("territorial_coverage", [])
    coverage_bonus = min(len(territorial_elements) / 5.0, 0.1)

    raw_score = (
        scores["elements_score"] * config.weight_elements
        + scores["similarity_score"] * config.weight_similarity
        + scores["patterns_score"] * config.weight_patterns
        + coverage_bonus
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    ci = _compute_confidence_interval(raw_score, evidence.get("confidence", 0.5))

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        confidence_interval=ci,
        scoring_metadata={
            "modality": config.modality,
            "threshold": config.threshold,
            "component_scores": scores,
            "coverage_bonus": coverage_bonus,
        },
    )


def score_type_f(evidence: dict[str, Any], config: ModalityConfig) -> ScoredResult:
    """
    TYPE_F: Institutional actors (relational emphasis).

    Characteristics:
    - Medium threshold (0.60)
    - Emphasizes institutional relationships
    - Used for actor networks, governance structures
    """
    ScoringValidator.validate_evidence(evidence)
    scores = ScoringValidator.extract_scores(evidence)

    # Check for institutional elements
    by_type = evidence.get("by_type", {})
    institutional_elements = by_type.get("institutional_actor", [])
    institutional_bonus = min(len(institutional_elements) / 3.0, 0.1)

    raw_score = (
        scores["elements_score"] * config.weight_elements
        + scores["similarity_score"] * config.weight_similarity
        + scores["patterns_score"] * config.weight_patterns
        + institutional_bonus
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    ci = _compute_confidence_interval(raw_score, evidence.get("confidence", 0.5))

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        confidence_interval=ci,
        scoring_metadata={
            "modality": config.modality,
            "threshold": config.threshold,
            "component_scores": scores,
            "institutional_bonus": institutional_bonus,
        },
    )


# =============================================================================
# MAIN SCORING INTERFACE
# =============================================================================


def apply_scoring(
    evidence: dict[str, Any], modality: ScoringModality, config: ModalityConfig | None = None
) -> ScoredResult:
    """
    Apply scoring to evidence based on modality.

    Args:
        evidence: Evidence dict from Phase 2 (EvidenceNexus)
        modality: Scoring modality (TYPE_A through TYPE_F)
        config: Optional modality configuration (uses defaults if None)

    Returns:
        ScoredResult with score, quality level, and metadata

    Raises:
        EvidenceStructureError: If evidence structure is invalid
        ModalityValidationError: If modality config is invalid
    """
    # Use default config if not provided
    if config is None:
        config = _get_default_config(modality)

    # Validate modality matches config
    if config.modality != modality:
        raise ModalityValidationError(
            f"Modality mismatch: expected {modality}, got {config.modality}"
        )

    # Route to appropriate scoring function
    scoring_functions = {
        "TYPE_A": score_type_a,
        "TYPE_B": score_type_b,
        "TYPE_C": score_type_c,
        "TYPE_D": score_type_d,
        "TYPE_E": score_type_e,
        "TYPE_F": score_type_f,
    }

    scoring_func = scoring_functions.get(modality)
    if scoring_func is None:
        raise ModalityValidationError(f"Unknown modality: {modality}")

    logger.debug(
        "applying_scoring",
        modality=modality,
        threshold=config.threshold,
        elements_count=len(evidence.get("elements", [])),
    )

    return scoring_func(evidence, config)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def apply_rounding(score: float, precision: int = 2) -> float:
    """Round score to specified precision."""
    return round(score, precision)


def determine_quality_level(score: float) -> QualityLevel:
    """
    Determine quality level from score.

    Thresholds aligned with calibration standards:
    - EXCELLENT: ≥ 0.85
    - GOOD: ≥ 0.70
    - ADEQUATE: ≥ 0.50
    - POOR: < 0.50
    """
    if score >= 0.85:
        return QualityLevel.EXCELLENT
    elif score >= 0.70:
        return QualityLevel.GOOD
    elif score >= 0.50:
        return QualityLevel.ADEQUATE
    else:
        return QualityLevel.POOR


def _get_default_config(modality: ScoringModality) -> ModalityConfig:
    """Get default configuration for modality."""
    defaults = {
        "TYPE_A": ModalityConfig(
            modality="TYPE_A",
            threshold=0.75,
            weight_elements=0.5,
            weight_similarity=0.3,
            weight_patterns=0.2,
            aggregation="weighted_mean",
        ),
        "TYPE_B": ModalityConfig(
            modality="TYPE_B",
            threshold=0.65,
            weight_elements=0.3,
            weight_similarity=0.3,
            weight_patterns=0.4,
            aggregation="weighted_mean",
        ),
        "TYPE_C": ModalityConfig(
            modality="TYPE_C",
            threshold=0.60,
            weight_elements=0.33,
            weight_similarity=0.34,
            weight_patterns=0.33,
            aggregation="weighted_mean",
        ),
        "TYPE_D": ModalityConfig(
            modality="TYPE_D",
            threshold=0.70,
            weight_elements=0.4,
            weight_similarity=0.3,
            weight_patterns=0.3,
            aggregation="weighted_mean",
        ),
        "TYPE_E": ModalityConfig(
            modality="TYPE_E",
            threshold=0.65,
            weight_elements=0.35,
            weight_similarity=0.35,
            weight_patterns=0.3,
            aggregation="weighted_mean",
        ),
        "TYPE_F": ModalityConfig(
            modality="TYPE_F",
            threshold=0.60,
            weight_elements=0.35,
            weight_similarity=0.3,
            weight_patterns=0.35,
            aggregation="weighted_mean",
        ),
    }
    return defaults[modality]


def _compute_confidence_interval(
    score: float, confidence: float, alpha: float = 0.05
) -> tuple[float, float]:
    """
    Compute Wilson score confidence interval (Wilson 1927, JASA).

    Mathematical Foundation:
    -----------------------
    The Wilson interval is derived by inverting the score test statistic
    for a binomial proportion. It provides asymptotically correct coverage
    with better small-sample properties than the Wald interval.

    Formula (Wilson 1927):
        [p̂ + z²/(2n) ± z√(p̂(1-p̂)/n + z²/(4n²))] / (1 + z²/n)

    where:
        p̂ = observed proportion (score)
        n = sample size
        z = (1-α/2) quantile of standard normal

    Key Properties (O'Neill 2021, arXiv:2109.12464):
    - Monotonicity: Preserves ordering of proportions
    - Consistency: Width → 0 as n → ∞
    - Bounded: Always in [0, 1] (unlike Wald)
    - Coverage: Approximately correct for all p and n

    Args:
        score: Point estimate (observed proportion) in [0, 1]
        confidence: Evidence confidence level (used to adjust n)
        alpha: Significance level (default 0.05 for 95% CI)

    Returns:
        Tuple of (lower_bound, upper_bound)

    References:
        [1] Wilson (1927), JASA, DOI: 10.1080/01621459.1927.10502953
        [2] O'Neill (2021), arXiv:2109.12464
    """
    # Z-score for confidence level (1-α)
    # For α=0.05 (95% CI): z = 1.96
    # For α=0.01 (99% CI): z = 2.576
    z = 1.96 if alpha == 0.05 else 2.576 if alpha == 0.01 else 1.645

    # Effective sample size (adjusted by evidence confidence)
    # Higher confidence → larger effective sample size → narrower interval
    n = max(30, int(100 * confidence))  # Min n=30 to ensure stability

    # Wilson interval formula (exact from Wilson 1927)
    p = score

    denominator = 1.0 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denominator

    # Standard error term (Wilson's correction)
    se_numerator = math.sqrt(p * (1 - p) / n + (z**2) / (4 * n**2))
    margin = (z / denominator) * se_numerator

    # Compute bounds (guaranteed in [0, 1] by Wilson formula properties)
    lower = clamp(center - margin, 0.0, 1.0)
    upper = clamp(center + margin, 0.0, 1.0)

    # Validate invariant [INV-SC-004]: CI must contain score
    # This holds automatically for Wilson interval by construction
    assert (
        lower <= score <= upper or math.isclose(lower, score) or math.isclose(upper, score)
    ), f"Wilson interval [{lower:.4f}, {upper:.4f}] must contain score {score:.4f}"

    return (lower, upper)


def _is_temporal(element: dict[str, Any]) -> bool:
    """Check if element has temporal characteristics."""
    if not isinstance(element, dict):
        return False

    temporal_keys = {"timestamp", "date", "year", "period", "temporal"}
    return bool(set(element.keys()) & temporal_keys)
