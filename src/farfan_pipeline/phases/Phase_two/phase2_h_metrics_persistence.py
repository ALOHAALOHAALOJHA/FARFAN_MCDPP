"""
Module: src.farfan_pipeline.phases.Phase_two.phase2_h_metrics_persistence
Phase: 2 (Evidence Nexus & Executor Orchestration)
Purpose: Persist execution metrics to structured storage

Writes execution metrics to Arrow IPC or JSON-Lines format for analysis.
Tracks performance, resource usage, and execution statistics for 300 contracts.

Architecture:
- MetricsPersister: Writes metrics to storage backend
- ArrowIPCWriter: Apache Arrow IPC format writer
- JSONLinesWriter: JSON-Lines format writer
- MetricsBuffer: In-memory buffer with batch writes

Integration:
- Collects metrics from ExecutorInstrumentationMixin
- Persists after each contract execution
- Enables post-execution analysis and optimization

Success Criteria:
- Write metrics to Arrow IPC or JSON-Lines format
- Batch writes for performance (default: 100 records)
- Zero data loss on graceful shutdown
- Query-able format for analytics
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

try:
    import pyarrow as pa  # type: ignore
    import pyarrow.ipc as ipc  # type: ignore
    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """Metrics for a single contract execution."""
    
    question_id: str
    dimension_id: str
    policy_area_id: str
    execution_time_ms: float
    memory_peak_mb: float
    cpu_percent: float
    method_count: int
    evidence_node_count: int
    confidence_score: float
    timestamp: str
    success: bool
    error_message: str | None = None


class MetricsPersister:
    """Persist execution metrics to structured storage.
    
    Supports Apache Arrow IPC and JSON-Lines formats.
    """
    
    def __init__(
        self,
        output_path: Path,
        format: Literal["arrow", "jsonl"] = "jsonl",
        buffer_size: int = 100,
    ) -> None:
        self.output_path = output_path
        self.format = format
        self.buffer_size = buffer_size
        self._buffer: list[ExecutionMetrics] = []
        self._arrow_writer: Any | None = None
        
        if format == "arrow" and not ARROW_AVAILABLE:
            logger.warning("PyArrow not available, falling back to JSON-Lines")
            self.format = "jsonl"
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def write_metrics(self, metrics: ExecutionMetrics) -> None:
        """Write metrics to storage.
        
        Args:
            metrics: Execution metrics to persist
        """
        self._buffer.append(metrics)
        
        if len(self._buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self) -> None:
        """Flush buffered metrics to storage."""
        if not self._buffer:
            return
        
        if self.format == "arrow":
            self._flush_arrow()
        else:
            self._flush_jsonl()
        
        self._buffer.clear()
    
    def _flush_arrow(self) -> None:
        """Flush to Apache Arrow IPC format."""
        if not ARROW_AVAILABLE:
            return
        
        # Convert metrics to Arrow table
        data = {
            "question_id": [m.question_id for m in self._buffer],
            "dimension_id": [m.dimension_id for m in self._buffer],
            "policy_area_id": [m.policy_area_id for m in self._buffer],
            "execution_time_ms": [m.execution_time_ms for m in self._buffer],
            "memory_peak_mb": [m.memory_peak_mb for m in self._buffer],
            "cpu_percent": [m.cpu_percent for m in self._buffer],
            "method_count": [m.method_count for m in self._buffer],
            "evidence_node_count": [m.evidence_node_count for m in self._buffer],
            "confidence_score": [m.confidence_score for m in self._buffer],
            "timestamp": [m.timestamp for m in self._buffer],
            "success": [m.success for m in self._buffer],
            "error_message": [m.error_message for m in self._buffer],
        }
        
        table = pa.table(data)
        
        # Write to IPC file (append mode)
        if self._arrow_writer is None:
            self._arrow_writer = ipc.new_file(
                self.output_path.open("wb"),
                table.schema
            )
        
        self._arrow_writer.write_table(table)
    
    def _flush_jsonl(self) -> None:
        """Flush to JSON-Lines format."""
        mode = "a" if self.output_path.exists() else "w"
        
        with self.output_path.open(mode) as f:
            for metrics in self._buffer:
                json.dump(asdict(metrics), f)
                f.write("\n")
    
    def close(self) -> None:
        """Close persister and flush remaining metrics."""
        self.flush()
        
        if self._arrow_writer is not None:
            self._arrow_writer.close()
            self._arrow_writer = None


# Global persister instance
_persister: MetricsPersister | None = None


def initialize_metrics_persistence(
    output_path: Path,
    format: Literal["arrow", "jsonl"] = "jsonl",
    buffer_size: int = 100,
) -> None:
    """Initialize global metrics persister.
    
    Args:
        output_path: Path to write metrics file
        format: Storage format (arrow or jsonl)
        buffer_size: Number of records to buffer before writing
    """
    global _persister
    _persister = MetricsPersister(output_path, format, buffer_size)


def persist_metrics(metrics: ExecutionMetrics) -> None:
    """Persist execution metrics using global persister.
    
    Args:
        metrics: Execution metrics to persist
    """
    if _persister is None:
        logger.warning("Metrics persister not initialized, skipping persistence")
        return
    
    _persister.write_metrics(metrics)


def flush_metrics() -> None:
    """Flush buffered metrics to storage."""
    if _persister is not None:
        _persister.flush()


def close_metrics_persistence() -> None:
    """Close metrics persister and flush remaining data."""
    global _persister
    if _persister is not None:
        _persister.close()
        _persister = None
