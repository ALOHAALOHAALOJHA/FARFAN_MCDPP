"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00
Updated: 2025-12-09T00:00:00+00:00

Congruence Layer (@C) Evaluator - COHORT Export

Production implementation at: src/orchestration/congruence_layer.py

Implements contract compliance evaluation with:
- c_scale: Output range compatibility (min/max overlap analysis)
- c_sem: Semantic tag alignment (Jaccard similarity >= 0.3 threshold)
- c_fusion: Fusion rule validity (validates aggregation operators)

Formula: C_play = c_scale × c_sem × c_fusion
Weights: 0.4·scale + 0.35·semantic + 0.25·fusion
"""

from orchestration.congruence_layer import (
    CongruenceLayerConfig,
    CongruenceRequirements,
    CongruenceThresholds,
    OutputRangeSpec,
    SemanticTagSet,
    FusionRule,
    CongruenceLayerEvaluator,
    create_default_congruence_config,
)

# COHORT Metadata
COHORT_METADATA = {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "layer_symbol": "@C",
    "layer_name": "Congruence Layer",
    "production_path": "src.orchestration.congruence_layer",
    "implementation_status": "complete",
    "lines_of_code": 221,
    "formula": "C_play = c_scale × c_sem × c_fusion",
    "components": {
        "c_scale": "Output Range Compatibility",
        "c_sem": "Semantic Tag Alignment",
        "c_fusion": "Fusion Rule Validity"
    },
    "weights": {
        "w_scale": 0.4,
        "w_semantic": 0.35,
        "w_fusion": 0.25
    },
    "thresholds": {
        "min_jaccard_similarity": 0.3,
        "max_range_mismatch_ratio": 0.5,
        "min_fusion_validity_score": 0.6
    }
}


def get_cohort_metadata() -> dict:
    """Return COHORT metadata for this layer."""
    return COHORT_METADATA.copy()


__all__ = [
    # Production exports
    "CongruenceLayerConfig",
    "CongruenceRequirements",
    "CongruenceThresholds",
    "OutputRangeSpec",
    "SemanticTagSet",
    "FusionRule",
    "CongruenceLayerEvaluator",
    "create_default_congruence_config",
    # COHORT metadata
    "COHORT_METADATA",
    "get_cohort_metadata",
]
