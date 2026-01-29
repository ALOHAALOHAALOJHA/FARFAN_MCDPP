"""
Phase Eight: Unified Recommendation Engine
==========================================

Module: src.farfan_pipeline.phases.Phase_08
Purpose: Phase 8 of F.A.R.F.A.N pipeline - UNIFIED recommendation generation
Owner: phase8_core
Lifecycle: ACTIVE
Version: 3.0.0
Effective-Date: 2026-01-22
Codename: UNIFIED-BIFURCATOR

Phase 8 generates actionable recommendations at three levels (MICRO, MESO, MACRO)
with EXPONENTIAL amplification through bifurcation analysis.

CONSOLIDATION (v3.0.0):
    Phase 8 now uses a SINGLE unified recommendation engine:
    - phase8_25_00_recommendation_bifurcator.py (UNIFIED ENGINE)
    - Replaces: phase8_20_00, phase8_20_01, phase8_20_02, phase8_30_00

    ONE ENGINE THAT DOES EVERYTHING:
    1. Loads rules from JSON
    2. Generates base recommendations from score data
    3. Applies exponential amplification via bifurcation

EXPONENTIAL FEATURES:
    - Dimensional Resonance: Hidden DIM interdependencies
    - Cross-Pollination: PA improvements that ripple
    - Temporal Cascades: Short fixes unlocking long capabilities
    - Synergy Matrix: Combinations > sum of parts

Directory Structure (GNEA Compliant):
------------------------------------
Phase_08/
├── __init__.py                                     # This file
├── PHASE_8_MANIFEST.json                           # Phase manifest
├── phase8_00_00_data_models.py                     # Data models
├── phase8_10_00_schema_validation.py               # Schema validation
├── phase8_25_00_recommendation_bifurcator.py       # UNIFIED ENGINE (v3.0.0) 🔱
├── interfaces/                                     # Interface contracts & validation
├── primitives/                                     # Constants, types, enums
├── interphase/                                     # Interphase adapters
├── json_phase_eight/                               # Rule definitions
│   └── recommendation_rules_enhanced.json          # Enhanced v3.0 rules
└── tests/                                          # Test suite
    └── test_bifurcator_hardening.py                # Bifurcator regression tests
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# Phase metadata
__version__ = "3.0.0"
__phase__ = 8
__codename__ = "UNIFIED-BIFURCATOR"

# Lazy imports for performance
if TYPE_CHECKING:
    from .phase8_25_00_recommendation_bifurcator import (
        # Main engine
        UnifiedBifurcator,
        RecommendationBifurcator,  # Alias
        # Result types
        BifurcationResult,
        UnifiedRecommendationResult,
        CrossPollinationNode,
        TemporalCascade,
        SynergyMatrix,
        # Configuration
        AmplificationConfig,
        # Convenience functions
        bifurcate_recommendations,
        generate_recommendations,
        enrich_recommendation_with_bifurcation,
        integrate_bifurcator_into_recommendation_set,
        # Data models
        Recommendation,
        RecommendationSet,
    )
    from .phase8_00_00_data_models import (
        TemplateContext,
        ValidationResult,
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


def get_unified_bifurcator(
    rules_path: str | None = None,
    apply_bifurcation: bool = True,
    **kwargs,
) -> "UnifiedBifurcator":
    """
    Get the unified recommendation engine.

    This is the PRIMARY entry point for Phase 8 recommendations.
    Combines rule generation with exponential bifurcation amplification.

    Args:
        rules_path: Optional path to rules JSON file
        apply_bifurcation: Whether to apply exponential amplification
        **kwargs: Additional arguments passed to UnifiedBifurcator

    Returns:
        UnifiedBifurcator instance

    Example:
        >>> from farfan_pipeline.phases.Phase_08 import get_unified_bifurcator
        >>> engine = get_unified_bifurcator()
        >>> result = engine.generate_micro_recommendations(micro_scores)
        >>> print(f"Generated {len(result.base_recommendations)} recommendations")
        >>> if result.bifurcation_result:
        ...     print(f"Amplification: {result.bifurcation_result.amplification_factor:.2f}x")
    """
    from .phase8_25_00_recommendation_bifurcator import UnifiedBifurcator
    return UnifiedBifurcator(rules_path=rules_path, apply_bifurcation=apply_bifurcation, **kwargs)


# Backward compatibility aliases
def get_recommendation_engine(**kwargs) -> "UnifiedBifurcator":
    """Backward compatibility: Alias for get_unified_bifurcator."""
    return get_unified_bifurcator(**kwargs)


def get_recommendation_bifurcator(**kwargs) -> "UnifiedBifurcator":
    """Backward compatibility: Alias for get_unified_bifurcator."""
    return get_unified_bifurcator(**kwargs)


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
    # Primary getter
    "get_unified_bifurcator",
    # Backward compatibility aliases
    "get_recommendation_engine",
    "get_recommendation_bifurcator",
    "get_interface_validator",
]
