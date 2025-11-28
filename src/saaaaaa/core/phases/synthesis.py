"""
Phase Synthesis Shim
=====================

This module provides compatibility mapping from legacy phase names to
the new canonical phase system.

Legacy auditors expect `synthesis` module. In the modern architecture,
synthesis happens in the aggregation layer, not as a distinct phase.

For new code, use:
- Aggregation modules in `saaaaaa.processing.aggregation`
- Meso/Macro analysis in `saaaaaa.analysis`
"""

# Re-export aggregation components as "synthesis"
from saaaaaa.processing.aggregation import (
    DimensionAggregator,
    AreaPolicyAggregator,
    ClusterAggregator,
    MacroAggregator,
    run_aggregation_pipeline,
)

__all__ = [
    "DimensionAggregator",
    "AreaPolicyAggregator",
    "ClusterAggregator",
    "MacroAggregator",
    "run_aggregation_pipeline",
]
