"""
Adaptive Meso Scoring Compatibility Module
===========================================

Re-exports adaptive meso scoring from Phase 4.
"""

try:
    from farfan_pipeline.phases.Phase_04.primitives.phase4_40_00_adaptive_meso_scoring import (
        AdaptiveMesoScoring,
        AdaptiveScoringConfig,
        ScoringMetrics,
        create_adaptive_scorer,
    )
except ImportError:
    # Fallback stubs
    from dataclasses import dataclass, field
    from typing import List, Dict, Any
    
    @dataclass
    class AdaptiveScoringConfig:
        """Configuration for adaptive scoring."""
        baseline_threshold: float = 0.5
        sensitivity_factor: float = 1.0
    
    @dataclass
    class ScoringMetrics:
        """Scoring metrics."""
        mean_score: float = 0.0
        std_dev: float = 0.0
        convergence: float = 0.0
    
    class AdaptiveMesoScoring:
        """Stub adaptive meso scoring."""
        
        def __init__(self, config: AdaptiveScoringConfig = None):
            self.config = config or AdaptiveScoringConfig()
        
        def score(self, data: List[Dict[str, Any]]) -> ScoringMetrics:
            """Stub scoring method."""
            return ScoringMetrics()
    
    def create_adaptive_scorer(config: AdaptiveScoringConfig = None) -> AdaptiveMesoScoring:
        """Create an adaptive scorer."""
        return AdaptiveMesoScoring(config)

__all__ = [
    "AdaptiveMesoScoring",
    "AdaptiveScoringConfig",
    "ScoringMetrics",
    "create_adaptive_scorer",
]
