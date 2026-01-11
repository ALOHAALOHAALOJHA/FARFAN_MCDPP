"""
Phase 5 Tests - Policy Area Aggregation
=======================================

This package contains adversarial tests for Phase 5: Policy Area Aggregation.

Phase 5 transforms: 60 DimensionScore → 10 AreaScore

Test Categories:
----------------
- Hermeticity: All 6 dimensions per policy area must be present
- Bounds: Scores must be in [0.0, 3.0]
- Cluster mapping: PA→Cluster assignments must be correct
- Edge cases: Missing data, malformed inputs, boundary values
"""
