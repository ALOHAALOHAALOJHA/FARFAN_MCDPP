"""
Phase 3: Scoring Transformation (Canonical)
===========================================

Transforms Phase 2 evidence into quantitative scores with signal enrichment.
"""

from .interface.phase3_entry_contract import MicroQuestionRun
from .interface.phase3_exit_contract import ScoredMicroQuestion
from .phase3_score_extraction import extract_score_from_nexus, map_completeness_to_quality
from .phase3_signal_enriched_scoring import SignalEnrichedScorer
from .phase3_validation import ValidationCounters, validate_and_clamp_score, validate_quality_level
from .primitives.quality_levels import QualityLevel
from .primitives.scoring_modalities import ModalityConfig, ScoredResult, apply_scoring

__all__ = [
    "MicroQuestionRun",
    "ModalityConfig",
    "QualityLevel",
    "ScoredMicroQuestion",
    "ScoredResult",
    "SignalEnrichedScorer",
    "ValidationCounters",
    "apply_scoring",
    "extract_score_from_nexus",
    "map_completeness_to_quality",
    "validate_and_clamp_score",
    "validate_quality_level",
]
