"""
Phase 4-7 Primitives Package
============================

This package contains primitive components for the hierarchical aggregation
pipeline (Phases 4-7). Primitives are foundational, reusable components that
implement core mathematical and logical operations.

Primitive Modules:
    - quality_levels: Quality level determination logic
    - aggregation_weights: Hierarchical weight management
    - scoring_modalities: Score transformation rules
    - uncertainty_metrics: Bootstrap and uncertainty quantification
    - choquet_primitives: Choquet integral fuzzy measure operations
    - signal_enriched_primitives: Signal-based aggregation enhancements
    - provenance_nodes: DAG-based provenance tracking nodes

Author: F.A.R.F.A.N. Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

# Import core primitive modules using actual file names
from . import (
    phase4_10_00_choquet_primitives as choquet_primitives,
    phase4_10_00_quality_levels as quality_levels,
    phase4_10_00_signal_enriched_primitives as signal_enriched_primitives,
    phase4_10_00_uncertainty_metrics as uncertainty_metrics,
)

__all__ = [
    "choquet_primitives",
    "quality_levels",
    "signal_enriched_primitives",
    "uncertainty_metrics",
]
