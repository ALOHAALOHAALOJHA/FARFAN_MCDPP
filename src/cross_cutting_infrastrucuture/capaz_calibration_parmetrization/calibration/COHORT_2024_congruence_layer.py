"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

Congruence Layer (@C) Evaluator Implementation

This is a COHORT_2024 reference file. For production use, import from:
    from src.orchestration.congruence_layer import (
        CongruenceLayerEvaluator,
        CongruenceLayerConfig,
        create_default_congruence_config,
        OutputRangeSpec,
        SemanticTagSet,
        FusionRule
    )
"""

from src.orchestration.congruence_layer import (
    CongruenceLayerEvaluator,
    CongruenceLayerConfig,
    CongruenceRequirements,
    CongruenceThresholds,
    OutputRangeSpec,
    SemanticTagSet,
    FusionRule,
    create_default_congruence_config
)

__all__ = [
    "CongruenceLayerEvaluator",
    "CongruenceLayerConfig",
    "CongruenceRequirements",
    "CongruenceThresholds",
    "OutputRangeSpec",
    "SemanticTagSet",
    "FusionRule",
    "create_default_congruence_config"
]
