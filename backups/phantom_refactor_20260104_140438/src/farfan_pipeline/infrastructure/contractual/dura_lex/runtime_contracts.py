"""
Runtime Contracts Module
=========================

Provides runtime contract types for pipeline operations.
This module was created to support flux/phases.py and analysis imports.

Note: FallbackCategory is re-exported from core.runtime_config for convenience.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class SegmentationMethod(Enum):
    """
    Defines the method used for document segmentation.

    Used by flux phases to track which segmentation approach was applied.
    """

    REGEX = auto()
    SENTENCE = auto()
    PARAGRAPH = auto()
    SEMANTIC = auto()
    HYBRID = auto()
    FALLBACK = auto()
    MANUAL = auto()
    NONE = auto()


class CalibrationMode(Enum):
    """
    Defines calibration modes for method execution.

    Used by observability metrics to track calibration behavior.
    """

    FULL = auto()
    PARTIAL = auto()
    MINIMAL = auto()
    DISABLED = auto()
    FALLBACK = auto()


class DocumentIdSource(Enum):
    """
    Defines the source of document identifiers.

    Used to track where document IDs originate from.
    """

    METADATA = auto()
    FILENAME = auto()
    HASH = auto()
    UUID = auto()
    SEQUENCE = auto()
    EXTERNAL = auto()


@dataclass
class SegmentationInfo:
    """
    Metadata about document segmentation.

    Attributes:
        method: The segmentation method used
        segment_count: Number of segments produced
        avg_segment_length: Average segment length in characters
        source_length: Original document length
        metadata: Additional segmentation metadata
    """

    method: SegmentationMethod
    segment_count: int = 0
    avg_segment_length: float = 0.0
    source_length: int = 0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class GraphMetricsInfo:
    """
    Metadata about graph metrics computation.

    Attributes:
        computed: Whether graph metrics were successfully computed
        networkx_available: Whether NetworkX library is available
        reason: Reason for skipping computation (if not computed)
    """

    computed: bool
    networkx_available: bool
    reason: Optional[str] = None


# Re-export FallbackCategory from runtime_config for convenience
try:
    from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import FallbackCategory
except ImportError:
    # Fallback definition if runtime_config not available
    class FallbackCategory(Enum):
        """Categories of fallback behavior for error handling."""

        GRACEFUL = "graceful"
        STRICT = "strict"
        NONE = "none"
        DEFAULT = "default"
        SILENT = "silent"
        LOGGING = "logging"


__all__ = [
    "SegmentationMethod",
    "SegmentationInfo",
    "GraphMetricsInfo",
    "CalibrationMode",
    "DocumentIdSource",
    "FallbackCategory",
]
