"""
Phase 4-7 Aggregation Pipeline — Canonical Package

This is the CANONICAL location for Phase 4-7 aggregation modules.
All source files live here. No legacy re-exports.

Document ID: CANONIC-P4-7-INIT-2025-12-18
Status: FROZEN
"""

from __future__ import annotations

# ==============================================================================
# LOCAL IMPORTS — Files live in this directory
# ==============================================================================
# Core Aggregation Pipeline
from farfan_pipeline.phases.Phase_4.aggregation import (
    # Provenance (integrated)
    AggregationDAG,
    # Dataclasses
    AggregationSettings,
    AreaPolicyAggregator,
    AreaScore,
    # Bootstrap
    BootstrapAggregator,
    ClusterAggregator,
    ClusterScore,
    # Aggregators
    DimensionAggregator,
    DimensionScore,
    MacroAggregator,
    MacroScore,
    ProvenanceNode,
    ScoredResult,
    # Utilities
    group_by,
    validate_scored_results,
)

# Provenance (standalone re-export for explicit access)
from farfan_pipeline.phases.Phase_4.aggregation_provenance import (
    AggregationDAG as ProvenanceDAG,
)
from farfan_pipeline.phases.Phase_4.aggregation_provenance import (
    ProvenanceNode as ProvenanceEntry,
)

# Choquet Integral Aggregator
from farfan_pipeline.phases.Phase_4.choquet_aggregator import (
    CalibrationResult,
    ChoquetAggregator,
    ChoquetConfig,
)

# Enhanced Aggregation
from farfan_pipeline.phases.Phase_4.enhancements import (
    DispersionMetrics,
    EnhancedDimensionAggregator,
    HermeticityDiagnosis,
    enhance_aggregator,
)

# Adaptive Meso Scoring
from farfan_pipeline.phases.Phase_4.enhancements.adaptive_meso_scoring import (
    AdaptiveMesoScoring,
)

# Signal-Enriched Aggregation
from farfan_pipeline.phases.Phase_4.enhancements.signal_enriched_aggregation import (
    SignalEnrichedAggregator,
)

# Validation
from farfan_pipeline.phases.Phase_4.validation import (
    AggregationValidationError,
    ValidationResult,
    validate_full_aggregation_pipeline,
    validate_phase4_output,
    validate_phase5_output,
    validate_phase6_output,
    validate_phase7_output,
)

# ==============================================================================
# VERSION METADATA
# ==============================================================================

__version__ = "1.0.0-canonical"
__canonical_date__ = "2025-12-18"
__status__ = "FROZEN"

# ==============================================================================
# PUBLIC API
# ==============================================================================

__all__ = [
    # Settings & Configuration
    "AggregationSettings",
    # Score Dataclasses
    "ScoredResult",
    "DimensionScore",
    "AreaScore",
    "ClusterScore",
    "MacroScore",
    # Core Aggregators
    "DimensionAggregator",
    "AreaPolicyAggregator",
    "ClusterAggregator",
    "MacroAggregator",
    "group_by",
    "validate_scored_results",
    # Choquet
    "ChoquetAggregator",
    "ChoquetConfig",
    "CalibrationResult",
    # Enhanced
    "EnhancedDimensionAggregator",
    "DispersionMetrics",
    "HermeticityDiagnosis",
    "enhance_aggregator",
    # Validation
    "validate_phase4_output",
    "validate_phase5_output",
    "validate_phase6_output",
    "validate_phase7_output",
    "validate_full_aggregation_pipeline",
    "ValidationResult",
    "AggregationValidationError",
    # Provenance
    "AggregationDAG",
    "ProvenanceNode",
    "ProvenanceDAG",
    "ProvenanceEntry",
    # Bootstrap
    "BootstrapAggregator",
    # Signal
    "SignalEnrichedAggregator",
    # Adaptive
    "AdaptiveMesoScoringEngine",
]

# ==============================================================================
# CONTRACT SIGNATURE
# ==============================================================================
# This package GUARANTEES:
# 1. 300 micro → 60 dimension (Phase 4)
# 2. 60 dimension → 10 area (Phase 5)
# 3. 10 area → 4 cluster (Phase 6)
# 4. 4 cluster → 1 macro (Phase 7)
# 5. Full provenance DAG for all operations
# 6. Hermetic validation at each phase boundary
# ==============================================================================
