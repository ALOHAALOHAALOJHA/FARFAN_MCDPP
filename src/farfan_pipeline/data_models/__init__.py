"""
F.A.R.F.A.N Data Models
========================

Pydantic models and data structures for the F.A.R.F.A.N framework.

Key Models:
-----------
- UnitOfAnalysis: Core unit of analysis representation
- FiscalContext: Fiscal and financial context
- Phase1Manifest: Phase 1 -> Phase 2 handoff contract
"""

from farfan_pipeline.data_models.unit_of_analysis import (
    UnitOfAnalysis,
    FiscalContext,
)

from farfan_pipeline.data_models.handoff_contracts import (
    Phase1Manifest,
)

__all__ = [
    "UnitOfAnalysis",
    "FiscalContext",
    "Phase1Manifest",
]
