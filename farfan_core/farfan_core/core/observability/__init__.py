"""Observability module for F.A.R.F.A.N runtime monitoring."""

from farfan_core.core.observability.structured_logging import log_fallback, get_logger
from farfan_core.core.observability.metrics import (
    increment_fallback,
    increment_segmentation_method,
    increment_calibration_mode,
    increment_document_id_source,
    increment_hash_algo,
    increment_graph_metrics_skipped,
    increment_contradiction_mode,
)

__all__ = [
    "log_fallback",
    "get_logger",
    "increment_fallback",
    "increment_segmentation_method",
    "increment_calibration_mode",
    "increment_document_id_source",
    "increment_hash_algo",
    "increment_graph_metrics_skipped",
    "increment_contradiction_mode",
]
