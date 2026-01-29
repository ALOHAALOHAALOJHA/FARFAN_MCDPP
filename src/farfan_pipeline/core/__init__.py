"""
F.A.R.F.A.N Core Module
========================

Core types, canonical notation, and fundamental definitions
for the F.A.R.F.A.N framework.

This module provides the foundational types and interfaces used
throughout the pipeline.

Key Exports:
------------
- CategoriaCausal: Causal category enumeration
- UnitOfAnalysis: Core unit of analysis type (from data_models)
- FiscalContext: Fiscal and financial context (from data_models)
"""

# Import from core.types
from farfan_pipeline.core.types import CategoriaCausal

# Import from data_models (canonical location for UnitOfAnalysis)
from farfan_pipeline.data_models.unit_of_analysis import (
    UnitOfAnalysis,
    FiscalContext,
)

__all__ = [
    "CategoriaCausal",
    "UnitOfAnalysis",
    "FiscalContext",
]
