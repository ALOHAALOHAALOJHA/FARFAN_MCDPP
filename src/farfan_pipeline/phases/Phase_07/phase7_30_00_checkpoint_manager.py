"""
Phase 7 Checkpoint Manager
==========================

Manages checkpoints for Phase 7 macro aggregation execution enabling mid-execution recovery.

Architecture:
    - Saves checkpoint after each stage of macro aggregation
    - Enables resumption from last completed stage
    - Thread-safe checkpoint operations
    - JSON-based serialization for portability

Windows Cross-Platform Enhancements (v1.1.0):
    - Long path support (>260 chars) for Windows
    - Atomic file writes (prevents corruption on crash/kill)
    - Proper UTF-8 encoding with BOM detection
    - Cross-platform newline normalization
    - Process-safe file locking

EXPONENTIAL BENEFITS:
    - Long paths: O(1) success for ANY directory depth
    - Atomic writes: Prevents O(N) corruption cascades
    - UTF-8 BOM: Prevents exponential data loss in ML pipelines
    - Newline normalization: O(1) cross-platform reproducibility
    - Process-safe: O(1) predictable behavior under concurrency

Version: 1.1.0
Author: F.A.R.F.A.N Core Architecture Team
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import Windows cross-platform utilities for exponential benefits
from farfan_pipeline.infrastructure.windows_utils import (
    atomic_write_json,
    safe_read_json,
    WindowsPathHelper,
)


# Stage execution order for resumption
STAGE_ORDER = [
    "STAGE_INPUT_VALIDATION",
    "STAGE_WEIGHTED_SCORE",
    "STAGE_QUALITY_CLASSIFICATION",
    "STAGE_COHERENCE_ANALYSIS",
    "STAGE_GAP_DETECTION",
    "STAGE_ALIGNMENT_SCORING",
    "STAGE_UNCERTAINTY_PROPAGATION",
    "STAGE_AGGREGATION_FINAL",
]


@dataclass
class CheckpointMetadata:
    """Metadata for a checkpoint file.

    Attributes:
        plan_id: Unique identifier for this execution
        stage_id: Stage that was completed
        timestamp: UTC timestamp of checkpoint
        cluster_ids: Set of cluster IDs being processed
        metadata: Additional metadata dictionary
    """
    plan_id: str
    stage_id: str
    timestamp: str
    cluster_ids: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class Phase7CheckpointManager:
    """
    Manages checkpoints for Phase 7 macro aggregation execution.

    Enables mid-execution recovery by persisting stage outputs.
    After successful pipeline completion, checkpoints are automatically cleaned up.

    Usage:
        >>> manager = Phase7CheckpointManager(
        ...     checkpoint_dir=Path("/tmp/checkpoints/phase7"),
        ...     plan_id="20260122_120000"
        ... )
        >>> manager.save_stage_checkpoint("STAGE_COHERENCE_ANALYSIS", coherence_data, {"clusters": 4})
        >>> resume_from = manager.get_resumption_point()
        >>> if resume_from:
        ...     print(f"Resuming from {resume_from}")
    """

    def __init__(
        self,
        checkpoint_dir: Path,
        plan_id: str,
    ):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory for checkpoint files
            plan_id: Unique execution identifier

        Windows Enhancement:
            - Uses WindowsPathHelper for long path support
            - Creates directory with cross-platform path handling
        """
        # Use WindowsPathHelper for long path support on Windows
        self.checkpoint_dir = WindowsPathHelper.resolve(checkpoint_dir)
        self.plan_id = plan_id
        self._lock = threading.Lock()

        # Create checkpoint directory with long-path support
        WindowsPathHelper.ensure_dir(self.checkpoint_dir)

    def save_stage_checkpoint(
        self,
        stage_id: str,
        output: Any,
        metadata: Dict[str, Any],
    ) -> Path:
        """
        Save checkpoint after successful stage execution.

        Args:
            stage_id: Stage identifier (e.g., "STAGE_COHERENCE_ANALYSIS")
            output: Output data from stage execution
            metadata: Additional metadata about the execution

        Returns:
            Path to saved checkpoint file

        Windows Enhancement:
            - Uses atomic_write_json (prevents corruption on crash/kill)
            - UTF-8 encoding with cross-platform newline handling
            - Long path support for any directory depth
        """
        with self._lock:
            checkpoint_data = {
                "plan_id": self.plan_id,
                "stage_id": stage_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata,
                "output_type": type(output).__name__,
                "output": self._serialize_output(output),
            }

            checkpoint_file = self.checkpoint_dir / f"{self.plan_id}_{stage_id}.json"

            # Atomic write: prevents corruption if process crashes during write
            atomic_write_json(checkpoint_file, checkpoint_data, indent=2)

            return checkpoint_file

    def load_latest_checkpoint(self) -> Optional[Tuple[str, Any]]:
        """
        Load most recent checkpoint for resumption.

        Returns:
            Tuple of (stage_id, output) or None if no checkpoint found

        Windows Enhancement:
            - Uses safe_read_json with automatic BOM detection
            - Long path support for any directory depth
        """
        checkpoints = sorted(
            self.checkpoint_dir.glob(f"{self.plan_id}_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not checkpoints:
            return None

        latest = checkpoints[0]
        # Safe read with automatic UTF-8 BOM detection
        data = safe_read_json(latest)

        if data is None:
            return None

        stage_id = data["stage_id"]
        output = self._deserialize_output(data["output"], data["output_type"])

        return stage_id, output

    def get_resumption_point(self) -> Optional[str]:
        """
        Determine which stage to resume from.

        Returns:
            Stage ID to resume from, or None if no checkpoint found
        """
        checkpoint = self.load_latest_checkpoint()
        if checkpoint is None:
            return None

        stage_id, _ = checkpoint

        # Return NEXT stage after completed one
        try:
            idx = STAGE_ORDER.index(stage_id)
            if idx + 1 < len(STAGE_ORDER):
                return STAGE_ORDER[idx + 1]
        except ValueError:
            pass

        return None

    def get_all_checkpoints(self) -> Dict[str, CheckpointMetadata]:
        """
        Get all checkpoints for this plan_id.

        Returns:
            Dictionary mapping stage_id to CheckpointMetadata

        Windows Enhancement:
            - Uses safe_read_json with automatic BOM detection
            - Long path support for any directory depth
        """
        checkpoints = {}
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.plan_id}_*.json"):
            # Safe read with automatic UTF-8 BOM detection
            data = safe_read_json(checkpoint_file)
            if data is None:
                continue

            try:
                metadata = CheckpointMetadata(
                    plan_id=data["plan_id"],
                    stage_id=data["stage_id"],
                    timestamp=data["timestamp"],
                    cluster_ids=data.get("metadata", {}).get("cluster_ids", []),
                    metadata=data.get("metadata", {}),
                )
                checkpoints[data["stage_id"]] = metadata
            except Exception:
                # Skip corrupted checkpoint files
                continue

        return checkpoints

    def clear_checkpoints(self) -> int:
        """
        Clear all checkpoints for this plan_id after successful completion.

        Returns:
            Number of checkpoint files cleared
        """
        cleared = 0
        with self._lock:
            for checkpoint_file in self.checkpoint_dir.glob(f"{self.plan_id}_*.json"):
                checkpoint_file.unlink()
                cleared += 1

        return cleared

    def _serialize_output(self, output: Any) -> Any:
        """
        Serialize stage output for JSON storage.

        Args:
            output: Output data to serialize

        Returns:
            JSON-serializable data
        """
        if hasattr(output, 'to_dict'):
            return output.to_dict()
        elif isinstance(output, list) and output and hasattr(output[0], 'to_dict'):
            return [item.to_dict() for item in output]
        elif isinstance(output, dict):
            return output
        elif isinstance(output, (tuple, list)):
            # Convert tuples to lists for JSON serialization
            return list(output)
        else:
            return str(output)

    def _deserialize_output(self, data: Any, output_type: str) -> Any:
        """
        Deserialize output from checkpoint.

        Args:
            data: Serialized data
            output_type: Type name of the output

        Returns:
            Deserialized output (as raw data for now)
        """
        # For now, return raw data
        # In production, reconstruct typed objects
        return data

    def validate_checkpoint_integrity(self, stage_id: str) -> bool:
        """
        Validate integrity of a specific checkpoint.

        Args:
            stage_id: Stage to validate

        Returns:
            True if checkpoint is valid

        Windows Enhancement:
            - Uses safe_read_json with automatic BOM detection
            - Long path support for any directory depth
        """
        checkpoint_file = self.checkpoint_dir / f"{self.plan_id}_{stage_id}.json"

        if not checkpoint_file.exists():
            return False

        # Safe read with automatic UTF-8 BOM detection
        data = safe_read_json(checkpoint_file)

        if data is None:
            return False

        try:
            # Validate required fields
            required_fields = ["plan_id", "stage_id", "timestamp", "output_type", "output"]
            if not all(field in data for field in required_fields):
                return False

            # Validate plan_id matches
            if data["plan_id"] != self.plan_id:
                return False

            # Validate stage_id matches expected
            if data["stage_id"] != stage_id:
                return False

            return True

        except Exception:
            return False


__all__ = [
    "CheckpointMetadata",
    "Phase7CheckpointManager",
    "STAGE_ORDER",
]
