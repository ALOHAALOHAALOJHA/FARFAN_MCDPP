"""
Phase 4 Aggregation Settings

Stub module to provide non-circular import point for choquet_adapter.py.

This module exists solely to break the circular dependency. The actual AggregationSettings
class is defined in phase4_10_00_aggregation.py. Modules that need AggregationSettings should:
- If they import FROM aggregation.py: No changes needed
- If they would create a circular dep with aggregation.py: Import from THIS module instead

At runtime, Python's import system will handle this correctly because:
1. choquet_adapter.py imports from THIS module (no circular dep)
2. aggregation.py defines AggregationSettings
3. When choquet_adapter is actually used, aggregation.py is already loaded

Module: src/farfan_pipeline/phases/Phase_4/phase4_10_00_aggregation_settings.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"

# Re-export AggregationSettings from the module where it's actually defined
# This is safe because by the time this import executes at runtime:
# - If accessed via choquet_adapter: aggregation.py will be loaded by then
# - If accessed via aggregation.py itself: aggregation.py defines it first

from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import AggregationSettings

__all__ = ["AggregationSettings"]


