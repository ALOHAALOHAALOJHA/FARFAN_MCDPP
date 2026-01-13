"""
Phase 4 Aggregation Settings - Import Redirect

This module exists to provide backward compatibility and break circular dependencies.
The actual AggregationSettings class is now in primitives/ layer.

Import hierarchy (Clean Architecture):
1. primitives/phase4_00_00_aggregation_settings.py - Pure dataclass (no deps)
2. configuration/ - Factory methods (depends on primitives)  
3. THIS MODULE - Convenience re-export (depends on primitives)
4. aggregation.py, choquet_adapter.py - Import from THIS MODULE or primitives

Module: src/farfan_pipeline/phases/Phase_4/phase4_10_00_aggregation_settings.py
"""
from __future__ import annotations

__version__ = "2.0.0"
__author__ = "F.A.R.F.A.N Core Team"
__layer__ = "redirect"

# Re-export from primitives layer (the source of truth)
from farfan_pipeline.phases.Phase_4.primitives.phase4_00_00_aggregation_settings import (
    AggregationSettings,
    validate_aggregation_settings,
)

__all__ = [
    "AggregationSettings",
    "validate_aggregation_settings",
]



