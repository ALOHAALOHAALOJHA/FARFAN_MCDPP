"""
Phase 3: Scoring Transformation (Canonical)
===========================================

Transforms Phase 2 evidence into quantitative scores with signal enrichment.
"""

<<<<<<< Updated upstream
from .interface.phase3_10_00_entry_contract import MicroQuestionRun
from .interface.phase3_10_00_exit_contract import ScoredMicroQuestion
from .phase3_10_00_phase3_score_extraction import extract_score_from_nexus, map_completeness_to_quality
from .phase3_10_00_phase3_signal_enriched_scoring import SignalEnrichedScorer
from .phase3_10_00_phase3_validation import ValidationCounters, validate_and_clamp_score, validate_quality_level
from .primitives.phase3_00_00_quality_levels import QualityLevel
from .primitives.phase3_00_00_scoring_modalities import ModalityConfig, ScoredResult, apply_scoring

__all__ = [
    "MicroQuestionRun",
    "ModalityConfig",
    "QualityLevel",
    "ScoredMicroQuestion",
    "ScoredResult",
    "SignalEnrichedScorer",
    "ValidationCounters",
    "apply_scoring",
=======
from .phase3_score_extraction import extract_score_from_nexus, map_completeness_to_quality
from .phase3_validation import validate_and_clamp_score, validate_quality_level, ValidationCounters
from .phase3_signal_enriched_scoring import SignalEnrichedScorer
from .primitives.scoring_modalities import apply_scoring, ScoredResult, ModalityConfig
from .primitives.quality_levels import QualityLevel
from .interface.phase3_entry_contract import MicroQuestionRun
from .interface.phase3_exit_contract import ScoredMicroQuestion

__all__ = [
>>>>>>> Stashed changes
    "extract_score_from_nexus",
    "map_completeness_to_quality",
    "validate_and_clamp_score",
    "validate_quality_level",
<<<<<<< Updated upstream
=======
    "ValidationCounters",
    "SignalEnrichedScorer",
    "apply_scoring",
    "ScoredResult",
    "ModalityConfig",
    "QualityLevel",
    "MicroQuestionRun",
    "ScoredMicroQuestion",
>>>>>>> Stashed changes
]
