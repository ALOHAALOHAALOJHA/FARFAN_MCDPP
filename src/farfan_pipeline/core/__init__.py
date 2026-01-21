"""
F.A.R.F.A.N Core Module
========================

Core types, canonical notation, and fundamental definitions
for the F.A.R.F.A.N framework.

This module provides the foundational types and interfaces used
throughout the pipeline.

Key Exports:
------------
- UnitOfAnalysis: Core unit of analysis type
- FiscalContext: Fiscal and financial context
- PolicyDocument: Policy document representation
- AnalysisResult: Analysis result container
"""

from farfan_pipeline.core.types import (
    UnitOfAnalysis,
    FiscalContext,
    PolicyDocument,
    AnalysisResult,
)

__all__ = [
    "UnitOfAnalysis",
    "FiscalContext",
    "PolicyDocument",
    "AnalysisResult",
]
