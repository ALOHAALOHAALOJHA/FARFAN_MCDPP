"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

Dimension Layer (@d) Evaluator Implementation

This is a COHORT_2024 reference file. For production use, import from:
    from ..COHORT_2024_contextual_layers import *
"""

from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_contextual_layers import (  # noqa: E501
    DIMENSION_LAYER_METADATA,
    CompatibilityRegistry,
    DimensionEvaluator,
    create_contextual_evaluators,
    get_dimension_metadata,
)

__all__ = [
    "DIMENSION_LAYER_METADATA",
    "CompatibilityRegistry",
    "DimensionEvaluator",
    "create_contextual_evaluators",
    "get_dimension_metadata",
]
