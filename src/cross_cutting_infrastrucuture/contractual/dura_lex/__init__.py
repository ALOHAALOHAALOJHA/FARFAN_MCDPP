# Core contracts __init__.py
"""Core contracts package for runtime contract infrastructure."""

from farfan_pipeline.core.contracts.runtime_contracts import (
    SegmentationMethod,
    SegmentationInfo,
    FallbackCategory,
)

__all__ = [
    "SegmentationMethod",
    "SegmentationInfo", 
    "FallbackCategory",
]
