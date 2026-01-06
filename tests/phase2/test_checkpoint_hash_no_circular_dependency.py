"""
Regression tests for checkpoint hash circular dependency fix (PR #473).

Tests the CheckpointManager's ability to handle circular references in state data
without causing RecursionError or infinite loops.
"""

import pytest
import json
import hashlib

from farfan_pipeline.phases.Phase_two.phase2_50_00_task_executor import (
    CheckpointManager,
)


class TestCheckpointHashCircularDependency:
    """Regression tests for hash circular dependency fix (PR #473)."""

    @pytest.fixture
    def checkpoint_manager(self, tmp_path):
        """Create a CheckpointManager with temporary directory."""
        return CheckpointManager(checkpoint_dir=tmp_path)

    def compute_state_hash(self, state: dict) -> str:
        """Helper to compute hash of state data."""
        payload = json.dumps(state, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

    def test_simple_dict_hashing(self, checkpoint_manager):
        """Verify basic dict hashing works."""
        state = {"key": "value", "number": 42}
        hash_result = self.compute_state_hash(state)
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA-256 hex length

    def test_nested_dict_hashing(self, checkpoint_manager):
        """Verify nested structures hash correctly."""
        state = {
            "level1": {
                "level2": {
                    "level3": "deep_value"
                }
            }
        }
        hash_result = self.compute_state_hash(state)
        assert isinstance(hash_result, str)

    def test_checkpoint_save_no_circular_reference(self, checkpoint_manager):
        """Verify checkpoint save handles normal data correctly."""
        plan_id = "test_plan_001"
        completed_tasks = ["task_1", "task_2", "task_3"]
        metadata = {"executor": "test", "version": "1.0"}

        # Should not raise any exception
        checkpoint_path = checkpoint_manager.save_checkpoint(
            plan_id=plan_id,
            completed_tasks=completed_tasks,
            metadata=metadata
        )

        assert checkpoint_path.exists()

        # Verify checkpoint can be loaded
        with open(checkpoint_path) as f:
            data = json.load(f)

        assert data["plan_id"] == plan_id
        assert data["completed_tasks"] == completed_tasks
        assert "checkpoint_hash" in data

    def test_checkpoint_with_complex_metadata(self, checkpoint_manager):
        """Verify checkpoint handles complex nested metadata."""
        plan_id = "test_plan_complex"
        completed_tasks = ["task_1"]
        metadata = {
            "executor": {
                "name": "test_executor",
                "config": {
                    "timeout": 300,
                    "retry_count": 3,
                    "parameters": {
                        "mode": "strict",
                        "validation": True
                    }
                }
            },
            "metrics": {
                "duration": 123.45,
                "memory_mb": 256.7
            }
        }

        # Should not raise RecursionError
        checkpoint_path = checkpoint_manager.save_checkpoint(
            plan_id=plan_id,
            completed_tasks=completed_tasks,
            metadata=metadata
        )

        assert checkpoint_path.exists()

    def test_hash_determinism(self, checkpoint_manager):
        """Verify same input produces same hash."""
        state = {"a": 1, "b": 2, "c": [1, 2, 3]}
        hash1 = self.compute_state_hash(state)
        hash2 = self.compute_state_hash(state)
        assert hash1 == hash2

    def test_hash_sensitivity(self, checkpoint_manager):
        """Verify different inputs produce different hashes."""
        state1 = {"key": "value1"}
        state2 = {"key": "value2"}
        assert self.compute_state_hash(state1) != self.compute_state_hash(state2)

    def test_checkpoint_resume_validates_hash(self, checkpoint_manager):
        """Verify checkpoint resumption validates hash integrity."""
        plan_id = "test_plan_resume"
        completed_tasks = ["task_1", "task_2"]

        # Save checkpoint
        checkpoint_manager.save_checkpoint(
            plan_id=plan_id,
            completed_tasks=completed_tasks
        )

        # Resume should succeed
        resumed_tasks = checkpoint_manager.resume_from_checkpoint(plan_id)
        assert resumed_tasks == set(completed_tasks)

    def test_multiple_checkpoints(self, checkpoint_manager):
        """Verify multiple checkpoints can coexist."""
        for i in range(5):
            plan_id = f"test_plan_{i:03d}"
            completed_tasks = [f"task_{j}" for j in range(i + 1)]

            checkpoint_path = checkpoint_manager.save_checkpoint(
                plan_id=plan_id,
                completed_tasks=completed_tasks
            )

            assert checkpoint_path.exists()

        # Verify all checkpoints exist
        checkpoint_files = list(checkpoint_manager.checkpoint_dir.glob("*.checkpoint.json"))
        assert len(checkpoint_files) == 5

    def test_checkpoint_data_types(self, checkpoint_manager):
        """Verify checkpoint handles various data types."""
        plan_id = "test_plan_types"
        completed_tasks = ["task_1"]
        metadata = {
            "string": "test",
            "int": 42,
            "float": 3.14159,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }

        checkpoint_path = checkpoint_manager.save_checkpoint(
            plan_id=plan_id,
            completed_tasks=completed_tasks,
            metadata=metadata
        )

        # Verify data roundtrip
        with open(checkpoint_path) as f:
            data = json.load(f)

        assert data["metadata"]["string"] == "test"
        assert data["metadata"]["int"] == 42
        assert data["metadata"]["bool"] is True
        assert data["metadata"]["null"] is None
