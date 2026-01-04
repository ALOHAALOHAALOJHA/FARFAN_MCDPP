"""
Phase 3: Scoring Transformation (Canonical)
===========================================

Transforms Phase 2 evidence into quantitative scores with signal enrichment.
"""

from .phase3_score_extraction import extract_score_from_nexus, map_completeness_to_quality
from .phase3_validation import validate_and_clamp_score, validate_quality_level, ValidationCounters
from .phase3_signal_enriched_scoring import SignalEnrichedScorer
from .primitives.scoring_modalities import apply_scoring, ScoredResult, ModalityConfig
from .primitives.quality_levels import QualityLevel
from .interface.phase3_entry_contract import MicroQuestionRun
from .interface.phase3_exit_contract import ScoredMicroQuestion

__all__ = [
    "extract_score_from_nexus",
    "map_completeness_to_quality",
    "validate_and_clamp_score",
    "validate_quality_level",
    "ValidationCounters",
    "SignalEnrichedScorer",
    "apply_scoring",
    "ScoredResult",
    "ModalityConfig",
    "QualityLevel",
    "MicroQuestionRun",
    "ScoredMicroQuestion",
]
