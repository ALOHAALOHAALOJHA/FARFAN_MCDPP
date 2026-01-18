"""
Phase 4 Primitives Package
============================

This package contains primitive components for the Phase 4 aggregation pipeline.
Primitives are foundational, reusable components with ZERO dependencies on other Phase 4 modules.

Layer: primitives (Layer 0 - Foundation)
Dependencies: NONE (only stdlib and external packages)

Primitive Modules:
    - phase4_00_00_aggregation_settings: Pure AggregationSettings dataclass
    - phase4_00_00_types: Type definitions, protocols, and type validation
    - quality_levels: Quality level determination logic
    - aggregation_weights: Hierarchical weight management
    - scoring_modalities: Score transformation rules
    - uncertainty_metrics: Bootstrap and uncertainty quantification
    - choquet_primitives: Choquet integral fuzzy measure operations
    - signal_enriched_primitives: Signal-based aggregation enhancements
    - provenance_nodes: DAG-based provenance tracking nodes

Author: F.A.R.F.A.N. Pipeline Team
Version: 2.0.0 (Refactored with Clean Architecture)
"""

from __future__ import annotations

# Layer 0: Pure primitives (new Clean Architecture additions)
from .phase4_00_00_aggregation_settings import (
    AggregationSettings,
    validate_aggregation_settings,
)
from .phase4_00_00_types import (
    # Type aliases
    AggregationMethod,
    ClusterID,
    DimensionID,
    MAX_SCORE,
    MAX_WEIGHT,
    MIN_SCORE,
    MIN_WEIGHT,
    PolicyAreaID,
    QualityLevel,
    QuestionID,
    Score,
    WEIGHT_SUM_TOLERANCE,
    Weight,
    # Protocols
    IAggregator,
    IConfigBuilder,
    # Validation functions
    are_weights_normalized,
    is_valid_score,
    is_valid_weight,
)

# Import phase4_00_00 primitive modules (from manifest)
from . import (
    phase4_00_00_choquet_primitives as choquet_primitives,
    phase4_00_00_quality_levels as quality_levels,
    phase4_00_00_signal_enriched_primitives as signal_enriched_primitives,
    phase4_00_00_uncertainty_metrics as uncertainty_metrics,
)

__all__ = [
    # Layer 0 (Pure primitives)
    "AggregationSettings",
    "validate_aggregation_settings",
    "PolicyAreaID",
    "DimensionID",
    "QuestionID",
    "ClusterID",
    "Score",
    "Weight",
    "AggregationMethod",
    "QualityLevel",
    "IAggregator",
    "IConfigBuilder",
    "MIN_SCORE",
    "MAX_SCORE",
    "MIN_WEIGHT",
    "MAX_WEIGHT",
    "WEIGHT_SUM_TOLERANCE",
    "is_valid_score",
    "is_valid_weight",
    "are_weights_normalized",
    # Existing primitives
    "choquet_primitives",
    "quality_levels",
    "signal_enriched_primitives",
    "uncertainty_metrics",
]

