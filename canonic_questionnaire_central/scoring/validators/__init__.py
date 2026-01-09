"""
Canonical Scoring Validators
=============================

This package provides validation contracts and utilities aligned with
Phase Three (src/farfan_pipeline/phases/Phase_three/interface/).

Validators:
-----------
- QuestionIdValidator: Validates question_id format
- EvidenceValidator: Validates evidence structure from Phase 2
- ScoreValidator: Validates score ranges
- QualityLevelValidator: Validates quality levels
- ScoredResultValidator: Complete validation of scored results
- MetadataValidator: Validates scoring metadata
- PDETContextValidator: Validates PDET municipality context enrichment

Usage:
------
    from canonic_questionnaire_central.scoring.validators import (
        ScoredResultValidator,
        PDETContextValidator,
        validate_batch,
        ValidationResult,
    )

    result = ScoredResultValidator.validate(scored_result)

Author: F.A.R.F.A.N Pipeline Team
Version: 1.1.0
"""

from .scoring_validators import (
    ScoringValidationError,
    ScoreRangeError,
    QualityLevelError,
    EvidenceStructureError,
    ModalityError,
    QuestionIdError,
    ValidationResult,
    QuestionIdValidator,
    EvidenceValidator,
    ScoreValidator,
    QualityLevelValidator,
    ScoredResultValidator,
    MetadataValidator,
    PDETContextValidator,
    validate_batch,
)

__all__ = [
    # Exceptions
    "ScoringValidationError",
    "ScoreRangeError",
    "QualityLevelError",
    "EvidenceStructureError",
    "ModalityError",
    "QuestionIdError",
    # Result
    "ValidationResult",
    # Validators
    "QuestionIdValidator",
    "EvidenceValidator",
    "ScoreValidator",
    "QualityLevelValidator",
    "ScoredResultValidator",
    "MetadataValidator",
    "PDETContextValidator",
    # Batch
    "validate_batch",
]
