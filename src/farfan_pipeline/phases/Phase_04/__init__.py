# -*- coding: utf-8 -*-
"""
Phase 4 - Dimension Aggregation Pipeline

This is the CANONICAL location for Phase 4 dimension aggregation modules.
Phase 4 is responsible ONLY for aggregating 300 micro-questions into 60 dimension scores.

Phases 5, 6, and 7 have been separated into their own modules.

Document ID: PHASE-4-INIT-2026-01-13
Status: ACTIVE
"""

from __future__ import annotations

# ==============================================================================
# LOCAL IMPORTS — Files live in this directory
# ==============================================================================

# Core Aggregation Pipeline (Phase 4 only)
# Import AggregationSettings from primitives module (correct location)
from farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_aggregation_settings import (
    AggregationSettings,
)
# Import DimensionScore from primitives (shared with Phase 5)
from farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_types import (
    DimensionScore,
)
from farfan_pipeline.phases.Phase_04.phase4_30_00_aggregation import (
    # Dataclasses (ScoredResult)
    ScoredResult,
    # Aggregators
    DimensionAggregator,
    # Provenance (integrated)
    AggregationDAG,
    ProvenanceNode,
    # Utilities
    group_by,
    validate_scored_results,
    # Exceptions
    AggregationError,
    ValidationError,
    WeightValidationError,
    ThresholdValidationError,
    HermeticityValidationError,
    CoverageError,
)

# Choquet Integral Aggregator
from farfan_pipeline.phases.Phase_04.phase4_30_00_choquet_aggregator import (
    ChoquetAggregator,
)

# Choquet Adapter
from farfan_pipeline.phases.Phase_04.phase4_20_00_choquet_adapter import (
    create_default_choquet_adapter,
)

# Uncertainty Quantification
from farfan_pipeline.phases.Phase_04.phase4_10_00_uncertainty_quantification import (
    BootstrapAggregator,
    UncertaintyMetrics,
    aggregate_with_uncertainty,
)

# Provenance (standalone import)
from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation_provenance import (
    AggregationDAG as ProvenanceDAG,
    ProvenanceNode as ProvenanceEntry,
)

# Signal-Enriched Aggregation
from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
    SignalEnrichedAggregator,
)

# Enhanced Aggregation
from farfan_pipeline.phases.Phase_04.enhancements import (
    EnhancedDimensionAggregator,
    DispersionMetrics,
    HermeticityDiagnosis,
    enhance_aggregator,
)

# Constants
from farfan_pipeline.phases.Phase_04.PHASE_4_CONSTANTS import (
    PHASE_ID,
    PHASE_NAME,
    EXPECTED_INPUT_MICRO_QUESTIONS,
    EXPECTED_OUTPUT_DIMENSION_SCORES,
    get_quality_level,
)

# ==============================================================================
# VERSION METADATA
# ==============================================================================

__version__ = "1.0.0"
__canonical_date__ = "2026-01-13"
__status__ = "ACTIVE"
__phase__ = 4

# ==============================================================================
# PUBLIC API
# ==============================================================================

__all__ = [
    # Settings & Configuration
    "AggregationSettings",
    # Score Dataclasses (Phase 4 only)
    "ScoredResult",
    "DimensionScore",
    # Core Aggregators (Phase 4 only)
    "DimensionAggregator",
    "group_by",
    "validate_scored_results",
    # Choquet
    "ChoquetAggregator",
    "create_default_choquet_adapter",
    # Enhanced
    "EnhancedDimensionAggregator",
    "DispersionMetrics",
    "HermeticityDiagnosis",
    "enhance_aggregator",
    # Provenance
    "AggregationDAG",
    "ProvenanceNode",
    "ProvenanceDAG",
    "ProvenanceEntry",
    # Bootstrap & Uncertainty
    "BootstrapAggregator",
    "UncertaintyMetrics",
    "aggregate_with_uncertainty",
    # Signal
    "SignalEnrichedAggregator",
    # Exceptions
    "AggregationError",
    "ValidationError",
    "WeightValidationError",
    "ThresholdValidationError",
    "HermeticityValidationError",
    "CoverageError",
    # Constants
    "PHASE_ID",
    "PHASE_NAME",
    "EXPECTED_INPUT_MICRO_QUESTIONS",
    "EXPECTED_OUTPUT_DIMENSION_SCORES",
    "get_quality_level",
]

# ==============================================================================
# CONTRACT SIGNATURE
# ==============================================================================
# This package GUARANTEES (Phase 4 ONLY):
# 1. Input: 300 ScoredMicroQuestion from Phase 3
# 2. Output: 60 DimensionScore (6 dimensions × 10 policy areas)
# 3. Full provenance DAG for all aggregation operations
# 4. Hermetic validation at phase boundary
# 5. Uncertainty quantification via bootstrap resampling
#
# NOTE: Phases 5, 6, and 7 are handled by separate modules.
# ==============================================================================

