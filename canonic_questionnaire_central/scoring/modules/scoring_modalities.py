"""
Canonical Scoring Modalities Module
===================================

Scoring modality implementations aligned with Phase Three
(src/farfan_pipeline/phases/Phase_three/primitives/scoring_modalities.py).

This module provides the six scoring types (TYPE_A through TYPE_F)
used across the questionnaire central, with complete alignment to
Phase 3 evidence-based scoring.

Architecture:
-------------
1. Evidence Structure Validation → Ensures compatibility with Nexus output
2. Modality-Based Scoring → Six scoring types (TYPE_A through TYPE_F)
3. Adaptive Threshold Application → Context-aware from scoring context
4. Quality Level Determination → Granular quality assessment
5. Provenance Tracking → Full traceability to evidence graph

Scoring Modalities:
-------------------
- TYPE_A: Quantitative indicators (high threshold, precise)
    - Aggregation: presence_threshold (0.7)
    - Used for: numeric indicators, budgets, goals

- TYPE_B: Qualitative descriptors (medium threshold, patterns)
    - Aggregation: binary_sum (max 3)
    - Used for: institutional actors, policy instruments

- TYPE_C: Mixed evidence (balanced weights)
    - Aggregation: presence_threshold (0.5)
    - Used for: mixed quantitative/qualitative questions

- TYPE_D: Temporal series (sequence-aware)
    - Aggregation: weighted_sum (0.4, 0.3, 0.3)
    - Used for: time series, historical trends

- TYPE_E: Territorial coverage (spatial)
    - Aggregation: binary_presence
    - Used for: geographic distribution, regional policies

- TYPE_F: Institutional actors (relational)
    - Aggregation: normalized_continuous (minmax)
    - Used for: actor networks, governance structures

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
Aligned with: Phase Three scoring_modalities.py v2.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

# Import quality levels (local module)
from .quality_levels import (
    QualityLevel,
    determine_quality_level,
)

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


# =============================================================================
# MODALITY ENUMERATION
# =============================================================================

class ModalityType(Enum):
    """Canonical scoring modality types."""
    TYPE_A = "TYPE_A"
    TYPE_B = "TYPE_B"
    TYPE_C = "TYPE_C"
    TYPE_D = "TYPE_D"
    TYPE_E = "TYPE_E"
    TYPE_F = "TYPE_F"


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True)
class ModalityConfig:
    """Configuration for a scoring modality.

    Aligned with scoring_system.json modality_definitions.
    """
    modality: ScoringModality
    threshold: float
    aggregation: str
    weights: list[float] | None = None
    normalization: str | None = None
    failure_code: str = "F-UNKNOWN"

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError(
                f"Threshold must be in [0, 1], got {self.threshold}"
            )

        if self.weights is not None:
            if not math.isclose(sum(self.weights), 1.0, abs_tol=0.01):
                raise ValueError(
                    f"Weights must sum to 1.0, got {sum(self.weights)}"
                )


@dataclass
class ScoredResult:
    """Result of scoring operation.

    Aligned with Phase Three ScoredResult dataclass.
    """
    score: float  # Raw score [0, 1]
    normalized_score: float  # Normalized [0, 100]
    quality_level: str  # Quality level string
    passes_threshold: bool
    modality: ScoringModality
    scoring_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "score": self.score,
            "normalized_score": self.normalized_score,
            "quality_level": self.quality_level,
            "passes_threshold": self.passes_threshold,
            "modality": self.modality,
            "scoring_metadata": self.scoring_metadata
        }


# =============================================================================
# MODALITY CONFIGURATIONS (Aligned with scoring_system.json)
# =============================================================================

def get_modality_config(modality: ScoringModality) -> ModalityConfig:
    """Get configuration for a scoring modality.

    Aligned with scoring_system.json modality_definitions.

    Args:
        modality: Scoring modality type

    Returns:
        ModalityConfig for the modality
    """
    configs = {
        "TYPE_A": ModalityConfig(
            modality="TYPE_A",
            threshold=0.7,
            aggregation="presence_threshold",
            failure_code="F-A-MIN"
        ),
        "TYPE_B": ModalityConfig(
            modality="TYPE_B",
            threshold=0.65,
            aggregation="binary_sum",
            failure_code="F-B-MIN"
        ),
        "TYPE_C": ModalityConfig(
            modality="TYPE_C",
            threshold=0.5,
            aggregation="presence_threshold",
            failure_code="F-C-MIN"
        ),
        "TYPE_D": ModalityConfig(
            modality="TYPE_D",
            threshold=0.65,
            aggregation="weighted_sum",
            weights=[0.4, 0.3, 0.3],
            failure_code="F-D-MIN"
        ),
        "TYPE_E": ModalityConfig(
            modality="TYPE_E",
            threshold=0.65,
            aggregation="binary_presence",
            failure_code="F-E-MIN"
        ),
        "TYPE_F": ModalityConfig(
            modality="TYPE_F",
            threshold=0.65,
            aggregation="normalized_continuous",
            normalization="minmax",
            failure_code="F-F-MIN"
        ),
    }

    return configs[modality]


# =============================================================================
# EVIDENCE STRUCTURE VALIDATION
# =============================================================================

class EvidenceValidator:
    """Validates evidence structure for scoring compatibility.

    Aligned with Phase Three ScoringValidator.
    """

    REQUIRED_KEYS = {"elements", "confidence"}
    OPTIONAL_KEYS = {"by_type", "completeness", "graph_hash", "patterns"}

    @classmethod
    def validate(cls, evidence: dict[str, Any]) -> None:
        """Validate evidence structure matches Nexus output contract.

        Args:
            evidence: Evidence dict from Phase 2

        Raises:
            ValueError: If structure is invalid
        """
        if not isinstance(evidence, dict):
            raise ValueError(
                f"Evidence must be dict, got {type(evidence).__name__}"
            )

        missing = cls.REQUIRED_KEYS - evidence.keys()
        if missing:
            raise ValueError(f"Missing required keys: {missing}")

        elements = evidence.get("elements", [])
        if not isinstance(elements, list):
            raise ValueError(
                f"'elements' must be list, got {type(elements).__name__}"
            )

        confidence = evidence.get("confidence", 0.0)
        if not isinstance(confidence, (int, float)):
            raise ValueError(
                f"'confidence' must be numeric, got {type(confidence).__name__}"
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                f"'confidence' must be in [0, 1], got {confidence}"
            )

    @classmethod
    def extract_scores(cls, evidence: dict[str, Any]) -> dict[str, float]:
        """Extract component scores from evidence.

        Args:
            evidence: Validated evidence dict

        Returns:
            Dict with elements_score, similarity_score, patterns_score
        """
        elements = evidence.get("elements", [])
        elements_score = min(len(elements) / 10.0, 1.0)

        confidence = evidence.get("confidence", 0.0)
        similarity_score = confidence

        patterns = evidence.get("patterns", {})
        if isinstance(patterns, dict):
            patterns_score = min(len(patterns) / 5.0, 1.0)
        else:
            patterns_score = 0.0

        return {
            "elements_score": float(elements_score),
            "similarity_score": float(similarity_score),
            "patterns_score": float(patterns_score)
        }


# =============================================================================
# SCORING FUNCTIONS BY MODALITY
# =============================================================================

def score_type_a(
    evidence: dict[str, Any],
    config: ModalityConfig | None = None
) -> ScoredResult:
    """TYPE_A: Quantitative indicators (high precision required).

    Characteristics:
    - High threshold (0.7)
    - Emphasizes elements found (presence_threshold)
    - Used for numeric indicators, budgets, goals

    Args:
        evidence: Evidence dict from Phase 2
        config: Optional modality configuration

    Returns:
        ScoredResult with score and quality level
    """
    if config is None:
        config = get_modality_config("TYPE_A")

    EvidenceValidator.validate(evidence)
    scores = EvidenceValidator.extract_scores(evidence)

    # Apply presence_threshold aggregation
    raw_score = (
        scores["elements_score"] * 0.5 +
        scores["similarity_score"] * 0.3 +
        scores["patterns_score"] * 0.2
    )

    # Apply threshold-based adjustment
    if raw_score >= config.threshold:
        adjusted_score = raw_score
    else:
        adjusted_score = raw_score * 0.8  # Penalty for not meeting threshold

    adjusted_score = clamp(adjusted_score, 0.0, 1.0)
    normalized = adjusted_score * 100.0
    quality = determine_quality_level(adjusted_score)
    passes = adjusted_score >= config.threshold

    return ScoredResult(
        score=adjusted_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        modality=config.modality,
        scoring_metadata={
            "threshold": config.threshold,
            "aggregation": config.aggregation,
            "component_scores": scores
        }
    )


def score_type_b(
    evidence: dict[str, Any],
    config: ModalityConfig | None = None
) -> ScoredResult:
    """TYPE_B: Qualitative descriptors (pattern matching emphasized).

    Characteristics:
    - Medium threshold (0.65)
    - Binary sum aggregation (max 3)
    - Used for institutional actors, policy instruments

    Args:
        evidence: Evidence dict from Phase 2
        config: Optional modality configuration

    Returns:
        ScoredResult with score and quality level
    """
    if config is None:
        config = get_modality_config("TYPE_B")

    EvidenceValidator.validate(evidence)
    scores = EvidenceValidator.extract_scores(evidence)

    elements = evidence.get("elements", [])
    element_score = min(len(elements), 3) / 3.0  # Max 3 elements

    raw_score = (
        element_score * 0.4 +
        scores["similarity_score"] * 0.3 +
        scores["patterns_score"] * 0.3
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        modality=config.modality,
        scoring_metadata={
            "threshold": config.threshold,
            "aggregation": config.aggregation,
            "component_scores": scores,
            "max_elements": 3
        }
    )


def score_type_c(
    evidence: dict[str, Any],
    config: ModalityConfig | None = None
) -> ScoredResult:
    """TYPE_C: Mixed evidence (balanced approach).

    Characteristics:
    - Medium threshold (0.5)
    - Presence threshold aggregation
    - Used for mixed quantitative/qualitative questions

    Args:
        evidence: Evidence dict from Phase 2
        config: Optional modality configuration

    Returns:
        ScoredResult with score and quality level
    """
    if config is None:
        config = get_modality_config("TYPE_C")

    EvidenceValidator.validate(evidence)
    scores = EvidenceValidator.extract_scores(evidence)

    raw_score = (
        scores["elements_score"] * 0.33 +
        scores["similarity_score"] * 0.34 +
        scores["patterns_score"] * 0.33
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        modality=config.modality,
        scoring_metadata={
            "threshold": config.threshold,
            "aggregation": config.aggregation,
            "component_scores": scores
        }
    )


def score_type_d(
    evidence: dict[str, Any],
    config: ModalityConfig | None = None
) -> ScoredResult:
    """TYPE_D: Temporal series (sequence awareness).

    Characteristics:
    - Medium-high threshold (0.65)
    - Weighted sum aggregation (0.4, 0.3, 0.3)
    - Used for time series, historical trends

    Args:
        evidence: Evidence dict from Phase 2
        config: Optional modality configuration

    Returns:
        ScoredResult with score and quality level
    """
    if config is None:
        config = get_modality_config("TYPE_D")

    EvidenceValidator.validate(evidence)
    scores = EvidenceValidator.extract_scores(evidence)

    weights = config.weights or [0.4, 0.3, 0.3]
    raw_score = (
        scores["elements_score"] * weights[0] +
        scores["similarity_score"] * weights[1] +
        scores["patterns_score"] * weights[2]
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        modality=config.modality,
        scoring_metadata={
            "threshold": config.threshold,
            "aggregation": config.aggregation,
            "component_scores": scores,
            "weights": weights
        }
    )


def score_type_e(
    evidence: dict[str, Any],
    config: ModalityConfig | None = None
) -> ScoredResult:
    """TYPE_E: Territorial coverage (spatial awareness).

    Characteristics:
    - Medium threshold (0.65)
    - Binary presence aggregation
    - Used for geographic distribution, regional policies

    Args:
        evidence: Evidence dict from Phase 2
        config: Optional modality configuration

    Returns:
        ScoredResult with score and quality level
    """
    if config is None:
        config = get_modality_config("TYPE_E")

    EvidenceValidator.validate(evidence)
    scores = EvidenceValidator.extract_scores(evidence)

    # Check for territorial elements
    by_type = evidence.get("by_type", {})
    territorial_elements = by_type.get("territorial_coverage", [])
    coverage_bonus = min(len(territorial_elements) / 5.0, 0.1)

    raw_score = (
        scores["elements_score"] * 0.35 +
        scores["similarity_score"] * 0.35 +
        scores["patterns_score"] * 0.3 +
        coverage_bonus
    )

    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        modality=config.modality,
        scoring_metadata={
            "threshold": config.threshold,
            "aggregation": config.aggregation,
            "component_scores": scores,
            "coverage_bonus": coverage_bonus
        }
    )


def score_type_f(
    evidence: dict[str, Any],
    config: ModalityConfig | None = None
) -> ScoredResult:
    """TYPE_F: Institutional actors (relational emphasis).

    Characteristics:
    - Medium threshold (0.65)
    - Normalized continuous aggregation (minmax)
    - Used for actor networks, governance structures

    Args:
        evidence: Evidence dict from Phase 2
        config: Optional modality configuration

    Returns:
        ScoredResult with score and quality level
    """
    if config is None:
        config = get_modality_config("TYPE_F")

    EvidenceValidator.validate(evidence)
    scores = EvidenceValidator.extract_scores(evidence)

    # Check for institutional elements
    by_type = evidence.get("by_type", {})
    institutional_elements = by_type.get("institutional_actor", [])
    institutional_bonus = min(len(institutional_elements) / 3.0, 0.1)

    raw_score = (
        scores["elements_score"] * 0.35 +
        scores["similarity_score"] * 0.3 +
        scores["patterns_score"] * 0.35 +
        institutional_bonus
    )

    # Apply minmax normalization
    raw_score = clamp(raw_score, 0.0, 1.0)
    normalized = raw_score * 100.0
    quality = determine_quality_level(raw_score)
    passes = raw_score >= config.threshold

    return ScoredResult(
        score=raw_score,
        normalized_score=normalized,
        quality_level=quality,
        passes_threshold=passes,
        modality=config.modality,
        scoring_metadata={
            "threshold": config.threshold,
            "aggregation": config.aggregation,
            "component_scores": scores,
            "institutional_bonus": institutional_bonus
        }
    )


# =============================================================================
# MAIN SCORING INTERFACE
# =============================================================================

def apply_scoring(
    evidence: dict[str, Any],
    modality: ScoringModality,
    config: ModalityConfig | None = None
) -> ScoredResult:
    """Apply scoring to evidence based on modality.

    Args:
        evidence: Evidence dict from Phase 2 (EvidenceNexus)
        modality: Scoring modality (TYPE_A through TYPE_F)
        config: Optional modality configuration

    Returns:
        ScoredResult with score, quality level, and metadata

    Raises:
        ValueError: If evidence structure is invalid or modality unknown
    """
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
        raise ValueError(f"Unknown modality: {modality}")

    logger.debug(
        "applying_scoring",
        modality=modality,
        config_threshold=config.threshold if config else None,
        elements_count=len(evidence.get("elements", []))
    )

    return scoring_func(evidence, config)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def get_all_modalities() -> tuple[ScoringModality, ...]:
    """Get all available scoring modalities."""
    return ("TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E", "TYPE_F")


def is_valid_modality(modality: str) -> bool:
    """Check if modality is valid."""
    return modality in get_all_modalities()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ScoringModality",
    "ModalityType",
    "ModalityConfig",
    "ScoredResult",
    # Validator
    "EvidenceValidator",
    # Main interface
    "apply_scoring",
    "get_modality_config",
    # Modality functions
    "score_type_a",
    "score_type_b",
    "score_type_c",
    "score_type_d",
    "score_type_e",
    "score_type_f",
    # Utilities
    "clamp",
    "get_all_modalities",
    "is_valid_modality",
]
