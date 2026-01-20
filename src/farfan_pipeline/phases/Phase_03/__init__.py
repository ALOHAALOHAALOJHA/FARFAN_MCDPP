"""
Phase 3 Public API
"""

from . import (
    PHASE_03_CONSTANTS,
    phase3_26_00_normative_compliance_validator,
)

from .contracts.phase03_input_contract import MicroQuestionRun
from .contracts.phase03_output_contract import ScoredMicroQuestion
from .interphase.phase3_05_00_nexus_interface_validator import NexusScoringValidator
from .phase3_20_00_score_extraction import extract_score_from_nexus, map_completeness_to_quality
from .phase3_22_00_validation import ValidationCounters, validate_and_clamp_score, validate_quality_level
from .phase3_24_00_signal_enriched_scoring import SignalEnrichedScorer
from .phase3_26_00_normative_compliance_validator import NormativeComplianceValidator
from .PHASE_03_CONSTANTS import *
from .primitives.phase3_00_00_quality_levels import QualityLevel
from .primitives.phase3_00_00_scoring_modalities import ModalityConfig, ScoredResult, apply_scoring

__all__ = [
    "MicroQuestionRun",
    "ScoredMicroQuestion",
    "NexusScoringValidator",
    "NormativeComplianceValidator",
    "extract_score_from_nexus",
    "map_completeness_to_quality",
    "ValidationCounters",
    "validate_and_clamp_score",
    "validate_quality_level",
    "SignalEnrichedScorer",
    "QualityLevel",
    "ModalityConfig",
    "ScoredResult",
    "apply_scoring",
    # Constants
    "PHASE_03_CONSTANTS",
]
