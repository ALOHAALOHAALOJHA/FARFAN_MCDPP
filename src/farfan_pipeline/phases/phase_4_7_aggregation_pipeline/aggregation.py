"""
Aggregation Pipeline Compatibility Module
==========================================

Backward compatibility layer for phase 4-7 aggregation pipeline.
Re-exports from actual implementation locations.
"""

from farfan_pipeline.phases.Phase_04.phase4_30_00_aggregation import (
    DimensionAggregator,
)
from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation_settings import (
    AggregationSettings,
)
from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
    SignalEnrichedAggregator,
)

# Import ScoredResult from appropriate location
try:
    from farfan_pipeline.phases.Phase_03 import ScoredResult
except ImportError:
    # Fallback: define a minimal stub
    from dataclasses import dataclass
    from typing import Any, Dict
    
    @dataclass
    class ScoredResult:
        """Stub for ScoredResult when not available."""
        question_id: str
        score: float
        confidence: float = 1.0
        metadata: Dict[str, Any] = None
        
        def __post_init__(self):
            if self.metadata is None:
                self.metadata = {}

__all__ = [
    "DimensionAggregator",
    "AggregationSettings",
    "SignalEnrichedAggregator",
    "ScoredResult",
]
