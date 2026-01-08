"""
Canonical Scoring Modules
==========================

This package provides core scoring modules aligned with Phase Three
(src/farfan_pipeline/phases/Phase_three/primitives/).

Modules:
--------
- quality_levels: Quality level enumeration and thresholds
- scoring_modalities: Six scoring types (TYPE_A through TYPE_F)
- pdet_scoring_enrichment: PDET municipality context enrichment for scoring

Usage:
------
    from canonic_questionnaire_central.scoring.modules import (
        QualityLevel,
        determine_quality_level,
        apply_scoring,
        PDETScoringEnricher,
    )

Author: F.A.R.F.A.N Pipeline Team
Version: 1.1.0
"""

from .quality_levels import (
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
)

from .scoring_modalities import (
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

from .pdet_scoring_enrichment import (
    PDETScoringContext,
    EnrichedScoredResult,
    PDETScoringEnricher,
    create_pdet_enricher,
)

__all__ = [
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
    # PDET enrichment
    "PDETScoringContext",
    "EnrichedScoredResult",
    "PDETScoringEnricher",
    "create_pdet_enricher",
]
