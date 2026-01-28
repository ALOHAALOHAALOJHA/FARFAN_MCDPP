"""
Aggregation Enhancements Compatibility Module
==============================================

Re-exports aggregation enhancements from Phase 4.
"""

from farfan_pipeline.phases.Phase_04.primitives.phase4_40_00_aggregation_enhancements import (
    AdaptiveMesoScoring,
)

try:
    from farfan_pipeline.phases.Phase_04.primitives.phase4_40_00_adaptive_meso_scoring import (
        AdaptiveMesoScoring as AdaptiveMesoScoring2,
        AdaptiveScoringConfig,
        ScoringMetrics,
        create_adaptive_scorer,
    )
except ImportError:
    # If specific module doesn't exist, use stubs
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class AdaptiveScoringConfig:
        """Stub configuration."""
        pass
    
    @dataclass
    class ScoringMetrics:
        """Stub metrics."""
        pass
    
    def create_adaptive_scorer(config=None):
        """Stub creator."""
        return AdaptiveMesoScoring()

__all__ = [
    "AdaptiveMesoScoring",
    "AdaptiveScoringConfig",
    "ScoringMetrics",
    "create_adaptive_scorer",
]
