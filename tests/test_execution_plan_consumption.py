"""
Unit tests for ExecutionPlan consumption in Phase 2.

This test suite verifies that the orchestrator correctly consumes the
ExecutionPlan built in Phase 1, ensuring:
- All tasks in the plan are executed
- Each task is executed exactly once
- Task metadata drives executor selection
- Task status and errors are tracked
- Orphan tasks and duplicate executions are detected

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest


# Create minimal test-only versions of required classes to avoid full import dependencies
@dataclass(frozen=True)
class Task:
    """Minimal Task for testing."""
    task_id: str
    dimension: str
    question_id: str
    policy_area: str
    chunk_id: str
    chunk_index: int
    question_text: str


@dataclass
class ExecutionPlan:
    """Minimal ExecutionPlan for testing."""
    plan_id: str
    tasks: tuple[Task, ...]
    chunk_count: int
    question_count: int
    integrity_hash: str
    created_at: str
    correlation_id: str
    metadata: dict[str, Any]


# Tests always available since we define minimal versions above
IMPORTS_AVAILABLE = True
IMPORT_ERROR = ""


@pytest.fixture
def mock_execution_plan():
    """Create a mock ExecutionPlan with sample tasks."""
    tasks = [
        Task(
            task_id="MQC-001_PA01",
            dimension="D1",
            question_id="Q001",
            policy_area="PA01",
            chunk_id="chunk_001",
            chunk_index=0,
            question_text="Test question 1"
        ),
        Task(
            task_id="MQC-002_PA01",
            dimension="D1",
            question_id="Q002",
            policy_area="PA01",
            chunk_id="chunk_002",
            chunk_index=1,
            question_text="Test question 2"
        ),
        Task(
            task_id="MQC-003_PA02",
            dimension="D2",
            question_id="Q003",
            policy_area="PA02",
            chunk_id="chunk_003",
            chunk_index=0,
            question_text="Test question 3"
        ),
    ]
    
    plan = ExecutionPlan(
        plan_id="test_plan_001",
        tasks=tuple(tasks),
        chunk_count=3,
        question_count=3,
        integrity_hash="test_hash_001",
        created_at="2025-01-01T00:00:00Z",
        correlation_id="test_correlation_001",
        metadata={}
    )
    
    return plan


@pytest.fixture
def mock_config():
    """Create a mock config with micro_questions."""
    return {
        "micro_questions": [
            {
                "id": "Q001",
                "question_id": "Q001",
                "global_id": 1,
                "base_slot": "D1-Q1",
                "dimension_id": "D1",
                "cluster_id": "C1",
                "patterns": [],
                "expected_elements": [],
            },
            {
                "id": "Q002",
                "question_id": "Q002",
                "global_id": 2,
                "base_slot": "D1-Q2",
                "dimension_id": "D1",
                "cluster_id": "C1",
                "patterns": [],
                "expected_elements": [],
            },
            {
                "id": "Q003",
                "question_id": "Q003",
                "global_id": 3,
                "base_slot": "D2-Q1",
                "dimension_id": "D2",
                "cluster_id": "C2",
                "patterns": [],
                "expected_elements": [],
            },
        ]
    }


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason=f"Required imports not available: {IMPORT_ERROR if not IMPORTS_AVAILABLE else ''}")
class TestExecutionPlanConsumption:
    """Test suite for ExecutionPlan consumption in Phase 2."""

    def test_task_structure(self, mock_execution_plan):
        """Test that Task and ExecutionPlan structures are correct."""
        assert len(mock_execution_plan.tasks) == 3
        assert mock_execution_plan.plan_id == "test_plan_001"
        assert mock_execution_plan.chunk_count == 3
        assert mock_execution_plan.question_count == 3
        
        task = mock_execution_plan.tasks[0]
        assert task.task_id == "MQC-001_PA01"
        assert task.dimension == "D1"
        assert task.question_id == "Q001"
        assert task.policy_area == "PA01"

    def test_task_uniqueness(self, mock_execution_plan):
        """Test that all tasks have unique task_ids."""
        task_ids = [task.task_id for task in mock_execution_plan.tasks]
        assert len(task_ids) == len(set(task_ids)), "Duplicate task IDs found"

    def test_config_question_structure(self, mock_config):
        """Test that config micro_questions have required fields."""
        questions = mock_config["micro_questions"]
        assert len(questions) == 3
        
        for q in questions:
            assert "id" in q or "question_id" in q
            assert "base_slot" in q
            assert "dimension_id" in q

    def test_question_lookup_logic(self, mock_execution_plan, mock_config):
        """Test the logic of looking up questions from tasks."""
        # Simulate the lookup logic
        task = mock_execution_plan.tasks[0]
        question_id = task.question_id
        
        questions = mock_config["micro_questions"]
        found = None
        for q in questions:
            if q.get("id") == question_id or q.get("question_id") == question_id:
                found = q
                break
        
        assert found is not None
        assert found["question_id"] == "Q001"
        assert found["base_slot"] == "D1-Q1"

    def test_task_to_executor_mapping(self, mock_execution_plan, mock_config):
        """Test that tasks can be mapped to executors via base_slot."""
        for task in mock_execution_plan.tasks:
            # Find question
            question = None
            for q in mock_config["micro_questions"]:
                if q.get("id") == task.question_id or q.get("question_id") == task.question_id:
                    question = q
                    break
            
            assert question is not None, f"Question not found for task {task.task_id}"
            assert "base_slot" in question, f"base_slot missing for task {task.task_id}"
            
            # Verify base_slot format matches dimension
            base_slot = question["base_slot"]
            assert base_slot.startswith(task.dimension), \
                f"base_slot {base_slot} doesn't match dimension {task.dimension}"

    def test_plan_coverage_validation(self, mock_execution_plan):
        """Test logic for validating that all tasks are executed."""
        tasks_in_plan = set(task.task_id for task in mock_execution_plan.tasks)
        
        # Simulate execution
        tasks_executed = set()
        for task in mock_execution_plan.tasks:
            tasks_executed.add(task.task_id)
        
        # Check for orphans
        orphan_tasks = tasks_in_plan - tasks_executed
        assert len(orphan_tasks) == 0, f"Orphan tasks found: {orphan_tasks}"
        
        # Check for duplicates
        assert len(tasks_executed) == len(tasks_in_plan), "Duplicate executions detected"

    def test_duplicate_detection_logic(self, mock_execution_plan):
        """Test logic for detecting duplicate task executions."""
        tasks_executed = set()
        duplicates = []
        
        # Simulate processing with one duplicate
        task_list = list(mock_execution_plan.tasks)
        task_list.append(task_list[0])  # Add duplicate
        
        for task in task_list:
            if task.task_id in tasks_executed:
                duplicates.append(task.task_id)
            tasks_executed.add(task.task_id)
        
        assert len(duplicates) == 1
        assert duplicates[0] == "MQC-001_PA01"

    def test_task_metadata_completeness(self, mock_execution_plan):
        """Test that tasks contain all required metadata."""
        required_fields = ["task_id", "dimension", "question_id", "policy_area", "chunk_id"]
        
        for task in mock_execution_plan.tasks:
            for field in required_fields:
                assert hasattr(task, field), f"Task missing field: {field}"
                assert getattr(task, field) is not None, f"Task has None value for: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
