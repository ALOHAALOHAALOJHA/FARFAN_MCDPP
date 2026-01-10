"""
Phase Eight: Recommendation Engine
===================================

Module: src.farfan_pipeline.phases.Phase_8
Purpose: Phase 8 of F.A.R.F.A.N pipeline - Rule-based recommendation generation
Owner: phase8_core
Lifecycle: ACTIVE
Version: 2.0.0
Effective-Date: 2026-01-05
Codename: RECOMMENDER

Phase 8 generates actionable recommendations at three levels (MICRO, MESO, MACRO)
based on scoring results from Phase 7. Uses enhanced rule templates with:
- Template parameterization
- Execution logic
- Measurable indicators
- Unambiguous time horizons
- Testable verification
- Cost tracking
- Authority mapping

Directory Structure (GNEA Compliant):
-------------------------------------
Phase_8/
├── __init__.py                                     # This file
├── PHASE_8_MANIFEST.json                           # Phase manifest
├── phase8_20_00_recommendation_engine.py           # Stage 20: Core engine (ENG)
├── phase8_20_01_recommendation_engine_adapter.py   # Stage 20: Orchestrator adapter (ADP)
├── phase8_30_00_signal_enriched_recommendations.py # Stage 30: Signal enrichment (ENR)
├── interfaces/                                     # Interface contracts & validation
│   ├── __init__.py
│   ├── INTERFACE_MANIFEST.json
│   ├── README.md
│   └── interface_validator.py
├── primitives/                                     # Constants, types, enums
│   ├── __init__.py
│   ├── PHASE_8_CONSTANTS.py
│   ├── PHASE_8_TYPES.py
│   ├── PHASE_8_ENUMS.py
│   └── README.md
└── json_phase_eight/                               # Rule definitions
    ├── recommendation_rules.json                   # Base rules
    └── recommendation_rules_enhanced.json          # Enhanced v2.0 rules
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# Phase metadata
__version__ = "2.0.0"
__phase__ = 8
__codename__ = "RECOMMENDER"

# Lazy imports for performance
if TYPE_CHECKING:
    from .phase8_20_00_recommendation_engine import (
        RecommendationEngine,
        Recommendation,
        RecommendationSet,
    )
    from .phase8_20_01_recommendation_engine_adapter import (
        RecommendationEngineAdapter,
        create_recommendation_engine_adapter,
    )
    from .phase8_30_00_signal_enriched_recommendations import (
        SignalEnrichedRecommender,
    )
    from .interfaces import (
        Phase8InterfaceValidator,
        validate_phase8_inputs,
        validate_phase8_outputs,
    )
    from .primitives import (
        # Constants
        PHASE_NUMBER,
        PHASE_NAME,
        PHASE_CODENAME,
        MIN_CONFIDENCE_THRESHOLD,
        MAX_RECOMMENDATIONS_PER_AREA,
        # Enums
        Level,
        ScoreBand,
        VarianceLevel,
        # Types
        AnalysisResultsInput,
        RecommendationOutput,
    )

logger = logging.getLogger(__name__)


def get_recommendation_engine() -> "RecommendationEngine":
    """Lazy-load and return RecommendationEngine."""
    from .phase8_20_00_recommendation_engine import RecommendationEngine

    return RecommendationEngine()


def get_recommendation_adapter() -> "RecommendationEngineAdapter":
    """Lazy-load and return RecommendationEngineAdapter."""
    from .phase8_20_01_recommendation_engine_adapter import create_recommendation_engine_adapter

    return create_recommendation_engine_adapter()


def get_signal_enriched_recommender() -> "SignalEnrichedRecommender":
    """Lazy-load and return SignalEnrichedRecommender."""
    from .phase8_30_00_signal_enriched_recommendations import SignalEnrichedRecommender

    return SignalEnrichedRecommender()


def get_interface_validator() -> "Phase8InterfaceValidator":
    """Lazy-load and return Phase8InterfaceValidator."""
    from .interfaces import Phase8InterfaceValidator

    return Phase8InterfaceValidator()


# Public API
__all__ = [
    # Version info
    "__version__",
    "__phase__",
    "__codename__",
    # Lazy getters
    "get_recommendation_engine",
    "get_recommendation_adapter",
    "get_signal_enriched_recommender",
    "get_interface_validator",
]
