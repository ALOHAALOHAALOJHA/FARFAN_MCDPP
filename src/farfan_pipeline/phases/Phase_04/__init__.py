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
# Imports are ordered by manifest execution order (Stage 00 → 10 → 20 → 30 → 40 → 50 → 60)

# STAGE 00: PRIMITIVES - Foundation types and settings
# Import AggregationSettings from primitives module
from farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_aggregation_settings import (
    AggregationSettings,
)

# STAGE 10: FOUNDATION - Core foundational modules
# Provenance tracking
from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation_provenance import (
    AggregationDAG as ProvenanceDAG,
    ProvenanceNode as ProvenanceEntry,
)

# Uncertainty Quantification
from farfan_pipeline.phases.Phase_04.phase4_10_00_uncertainty_quantification import (
    BootstrapAggregator,
    UncertaintyMetrics,
    aggregate_with_uncertainty,
)

# STAGE 20: CORE PROCESSING
# Choquet Adapter
from farfan_pipeline.phases.Phase_04.phase4_20_00_choquet_adapter import (
    create_default_choquet_adapter,
)

# STAGE 30: AGGREGATORS - Main aggregation engines
# Main Dimension Aggregation
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

# Signal-Enriched Aggregation
from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
    SignalEnrichedAggregator,
)

# STAGE 40: ENHANCEMENTS - Performance and optimization
# Adaptive Meso Scoring
from farfan_pipeline.phases.Phase_04.enhancements.phase4_40_00_adaptive_meso_scoring import (
    AdaptiveMesoScoring,
    AdaptiveScoringConfig,
    ScoringMetrics,
)

# Aggregation Enhancements
from farfan_pipeline.phases.Phase_04.enhancements import (
    ConfidenceInterval,
    DispersionMetrics,
    HermeticityDiagnosis,
)

# Enhanced Aggregation (composite from enhancements package)
from farfan_pipeline.phases.Phase_04.enhancements import (
    EnhancedDimensionAggregator,
    enhance_aggregator,
)

# STAGE 50: INTEGRATION - Cross-phase integration
from farfan_pipeline.phases.Phase_04.phase4_50_00_aggregation_integration import (
    ClusterAggregator,
)

# STAGE 60: VALIDATION - Output validation
from farfan_pipeline.phases.Phase_04.phase4_60_00_aggregation_validation import (
    ValidationResult,
    AggregationValidationError,
    validate_phase4_output,
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
    "enhance_aggregator",
    # Enhancement Metrics & Config
    "ConfidenceInterval",
    "DispersionMetrics",
    "HermeticityDiagnosis",
    "AdaptiveMesoScoring",
    "AdaptiveScoringConfig",
    "ScoringMetrics",
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
    # Integration (Stage 50)
    "ClusterAggregator",
    # Validation (Stage 60)
    "ValidationResult",
    "AggregationValidationError",
    "validate_phase4_output",
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

