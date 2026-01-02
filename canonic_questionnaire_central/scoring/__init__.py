"""
Canonical Scoring System
========================

This package provides the canonical scoring system for the questionnaire
central, fully aligned with Phase Three (src/farfan_pipeline/phases/Phase_three/).

Architecture:
-------------
1. Quality Levels (modules.quality_levels)
   - Enumeration of quality levels (EXCELENTE, BUENO, ACEPTABLE, INSUFICIENTE)
   - Threshold constants aligned with Phase Three primitives
   - Quality level determination from scores

2. Scoring Modalities (modules.scoring_modalities)
   - Six scoring types (TYPE_A through TYPE_F)
   - Evidence structure validation
   - Modality-specific scoring functions

3. Validators (validators.scoring_validators)
   - Contract validation for entry/exit contracts
   - Score range validation
   - Quality level consistency validation
   - Batch validation support

Alignment with Phase Three:
---------------------------
This scoring system is fully aligned with:
- Phase Three primitives (quality_levels.py, scoring_modalities.py)
- Phase Three interface contracts (phase3_entry_contract.py, phase3_exit_contract.py)
- Phase Three scoring implementation (phase3_score_extraction.py, phase3_signal_enriched_scoring.py)

Quality Level Mapping:
----------------------
Spanish (Canonical) | Phase Three (English)
---------------------|----------------------
EXCELENTE           | EXCELLENT
BUENO               | GOOD
ACEPTABLE           | ADEQUATE
INSUFICIENTE        | POOR

Scoring Invariants:
-------------------
[INV-SC-001] All scores must be in range [0.0, 1.0]
[INV-SC-002] Quality level must be deterministic from score
[INV-SC-003] Scoring metadata must include modality and threshold
[INV-SC-004] Normalized scores must be in range [0, 100]

Usage Examples:
---------------

Basic scoring:
    from canonic_questionnaire_central.scoring import apply_scoring

    result = apply_scoring(
        evidence={"elements": [...], "confidence": 0.8},
        modality="TYPE_A"
    )
    print(result.quality_level)  # "BUENO"

Validation:
    from canonic_questionnaire_central.scoring.validators import ScoredResultValidator

    validation = ScoredResultValidator.validate(result)
    if validation.is_valid:
        print("Score is valid")

Quality level determination:
    from canonic_questionnaire_central.scoring import determine_quality_level

    quality = determine_quality_level(0.87)  # "EXCELENTE"

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
Aligned with: Phase Three v1.0.0
"""

# Import modules
from .modules import (
    QualityLevel,
    THRESHOLD_EXCELENTE,
    THRESHOLD_BUENO,
    THRESHOLD_ACEPTABLE,
    THRESHOLD_INSUFICIENTE,
    VALID_QUALITY_LEVELS,
    determine_quality_level,
    determine_quality_level_from_completeness,
    is_valid_quality_level,
    get_color_for_quality,
    ScoringModality,
    ModalityType,
    ModalityConfig,
    ScoredResult,
    EvidenceValidator,
    apply_scoring,
    get_modality_config,
    score_type_a,
    score_type_b,
    score_type_c,
    score_type_d,
    score_type_e,
    score_type_f,
    clamp,
    get_all_modalities,
    is_valid_modality,
)

# Import validators
from .validators import (
    ScoringValidationError,
    ScoreRangeError,
    QualityLevelError,
    EvidenceStructureError,
    ModalityError,
    QuestionIdError,
    ValidationResult,
    QuestionIdValidator,
    EvidenceValidator as ScoringEvidenceValidator,
    ScoreValidator,
    QualityLevelValidator,
    ScoredResultValidator,
    MetadataValidator,
    validate_batch,
)

# Version info
__version__ = "1.0.0"
__aligned_with__ = "Phase Three v1.0.0"

__all__ = [
    # Version
    "__version__",
    "__aligned_with__",
    # Quality levels
    "QualityLevel",
    "THRESHOLD_EXCELENTE",
    "THRESHOLD_BUENO",
    "THRESHOLD_ACEPTABLE",
    "THRESHOLD_INSUFICIENTE",
    "VALID_QUALITY_LEVELS",
    "determine_quality_level",
    "determine_quality_level_from_completeness",
    "is_valid_quality_level",
    "get_color_for_quality",
    # Scoring modalities
    "ScoringModality",
    "ModalityType",
    "ModalityConfig",
    "ScoredResult",
    "EvidenceValidator",
    "apply_scoring",
    "get_modality_config",
    "score_type_a",
    "score_type_b",
    "score_type_c",
    "score_type_d",
    "score_type_e",
    "score_type_f",
    "clamp",
    "get_all_modalities",
    "is_valid_modality",
    # Exceptions
    "ScoringValidationError",
    "ScoreRangeError",
    "QualityLevelError",
    "EvidenceStructureError",
    "ModalityError",
    "QuestionIdError",
    # Validation
    "ValidationResult",
    "QuestionIdValidator",
    "ScoringEvidenceValidator",
    "ScoreValidator",
    "QualityLevelValidator",
    "ScoredResultValidator",
    "MetadataValidator",
    "validate_batch",
]
