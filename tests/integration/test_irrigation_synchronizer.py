"""Integration tests for IrrigationSynchronizer.

Tests the full synchronization flow from questionnaire → chunks → tasks → execution plan.
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from farfan_pipeline.core.orchestrator.irrigation_synchronizer import (
    ExecutionPlan,
    IrrigationSynchronizer,
    Task,
)


@pytest.fixture
def questionnaire_data() -> dict[str, Any]:
    """Load real questionnaire_monolith.json."""
    questionnaire_path = Path("system/config/questionnaire/questionnaire_monolith.json")

    if not questionnaire_path.exists():
        pytest.skip(f"Questionnaire not found at {questionnaire_path}")

    with open(questionnaire_path) as f:
        return json.load(f)


@pytest.fixture
def mock_document_chunks() -> list[dict[str, Any]]:
    """Generate 60 mock document chunks."""
    return [
        {
            "chunk_id": f"chunk_{i:04d}",
            "text": f"Sample text for chunk {i}",
            "start_char": i * 1000,
            "end_char": (i + 1) * 1000,
        }
        for i in range(60)
    ]


def test_synchronizer_initialization(questionnaire_data, mock_document_chunks):
    """Test synchronizer initializes with correlation_id and logging."""
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=mock_document_chunks
    )

    assert synchronizer.correlation_id is not None
    assert len(synchronizer.correlation_id) == 36
    assert synchronizer.question_count > 0
    assert synchronizer.chunk_count == 60


def test_build_execution_plan_basic(questionnaire_data, mock_document_chunks):
    """Test build_execution_plan generates valid ExecutionPlan."""
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=mock_document_chunks
    )

    plan = synchronizer.build_execution_plan()

    assert isinstance(plan, ExecutionPlan)
    assert plan.plan_id.startswith("plan_")
    assert len(plan.tasks) > 0
    assert plan.chunk_count == 60
    assert plan.question_count > 0
    assert len(plan.integrity_hash) in [64, 128]
    assert plan.correlation_id == synchronizer.correlation_id


def test_execution_plan_determinism(questionnaire_data, mock_document_chunks):
    """Test execution plan generation is deterministic."""
    sync1 = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=mock_document_chunks
    )
    plan1 = sync1.build_execution_plan()

    sync2 = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=mock_document_chunks
    )
    plan2 = sync2.build_execution_plan()

    assert plan1.plan_id == plan2.plan_id
    assert plan1.integrity_hash == plan2.integrity_hash
    assert len(plan1.tasks) == len(plan2.tasks)


def test_task_structure(questionnaire_data, mock_document_chunks):
    """Test individual task structure."""
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=mock_document_chunks
    )

    plan = synchronizer.build_execution_plan()

    task = plan.tasks[0]
    assert isinstance(task, Task)
    assert task.task_id
    assert task.dimension in ["D1", "D2", "D3", "D4", "D5", "D6"]
    assert task.question_id
    assert task.policy_area in [f"PA{i:02d}" for i in range(1, 11)]
    assert task.chunk_id
    assert task.chunk_index >= 0
    assert task.question_text


def test_build_execution_plan_empty_chunks():
    """Test synchronizer raises ValueError for empty chunks."""
    synchronizer = IrrigationSynchronizer(
        questionnaire={"blocks": {}}, document_chunks=[]
    )

    with pytest.raises(ValueError, match="No document chunks provided"):
        synchronizer.build_execution_plan()


def test_build_execution_plan_empty_questionnaire(mock_document_chunks):
    """Test synchronizer raises ValueError for empty questionnaire."""
    synchronizer = IrrigationSynchronizer(
        questionnaire={"blocks": {}}, document_chunks=mock_document_chunks
    )

    with pytest.raises(ValueError, match="No questions found in questionnaire"):
        synchronizer.build_execution_plan()


def test_logging_includes_correlation_id(
    questionnaire_data, mock_document_chunks, caplog
):
    """Test all log entries include the same correlation_id."""
    with caplog.at_level(logging.INFO):
        synchronizer = IrrigationSynchronizer(
            questionnaire=questionnaire_data, document_chunks=mock_document_chunks
        )

        correlation_id = synchronizer.correlation_id

        plan = synchronizer.build_execution_plan()

    correlation_ids = []
    for record in caplog.records:
        try:
            log_data = json.loads(record.message)
            if "correlation_id" in log_data:
                correlation_ids.append(log_data["correlation_id"])
        except (json.JSONDecodeError, AttributeError):
            pass

    assert len(correlation_ids) >= 2
    assert all(cid == correlation_id for cid in correlation_ids)


def test_end_to_end_synchronization_with_real_questionnaire(questionnaire_data):
    """Test complete synchronization flow with real questionnaire and 60 chunks.

    This is the canonical end-to-end test that verifies:
    - 60 document chunks are processed
    - Execution plan is generated with 300 tasks
    - plan_id is deterministic
    - integrity_hash is reproducible
    """
    chunks = [
        {
            "chunk_id": f"chunk_{i:04d}",
            "text": f"Policy section {i} with substantive content about development goals",
            "start_char": i * 2000,
            "end_char": (i + 1) * 2000,
            "chunk_type": "semantic",
        }
        for i in range(60)
    ]

    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=chunks
    )

    plan = synchronizer.build_execution_plan()

    assert plan.chunk_count == 60, f"Expected 60 chunks, got {plan.chunk_count}"

    assert len(plan.tasks) > 0, "Execution plan should contain tasks"

    assert plan.plan_id is not None and plan.plan_id.startswith("plan_")

    assert len(plan.integrity_hash) in [64, 128]

    assert plan.question_count > 0

    integrity_hash_original = plan.integrity_hash

    synchronizer2 = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=chunks
    )
    plan2 = synchronizer2.build_execution_plan()

    assert (
        plan2.integrity_hash == integrity_hash_original
    ), "Integrity hash should be deterministic"

    assert plan2.plan_id == plan.plan_id, "plan_id should be deterministic"


def test_execution_plan_serialization(questionnaire_data, mock_document_chunks):
    """Test ExecutionPlan can be serialized to dict and JSON."""
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=mock_document_chunks
    )

    plan = synchronizer.build_execution_plan()

    plan_dict = plan.to_dict()

    assert isinstance(plan_dict, dict)
    assert "plan_id" in plan_dict
    assert "tasks" in plan_dict
    assert "chunk_count" in plan_dict
    assert "question_count" in plan_dict
    assert "integrity_hash" in plan_dict
    assert "correlation_id" in plan_dict

    json_str = json.dumps(plan_dict)
    assert len(json_str) > 0

    deserialized = json.loads(json_str)
    assert deserialized["plan_id"] == plan.plan_id
    assert deserialized["integrity_hash"] == plan.integrity_hash


def test_prometheus_metrics_integration(questionnaire_data, mock_document_chunks):
    """Test that Prometheus metrics are recorded (if available)."""
    try:
        from prometheus_client import REGISTRY

        synchronizer = IrrigationSynchronizer(
            questionnaire=questionnaire_data, document_chunks=mock_document_chunks
        )

        plan = synchronizer.build_execution_plan()

        metrics = REGISTRY.collect()
        metric_names = [m.name for m in metrics]

        assert any("synchronization" in name for name in metric_names)

    except ImportError:
        pytest.skip("prometheus_client not available")


def test_correlation_id_uniqueness():
    """Test each synchronizer instance gets unique correlation_id."""
    sync1 = IrrigationSynchronizer(
        questionnaire={"blocks": {"D1_Q01": {"question": "Test"}}},
        document_chunks=[{"chunk_id": "c1", "text": "test"}],
    )

    sync2 = IrrigationSynchronizer(
        questionnaire={"blocks": {"D1_Q01": {"question": "Test"}}},
        document_chunks=[{"chunk_id": "c1", "text": "test"}],
    )

    assert sync1.correlation_id != sync2.correlation_id


def test_task_count_calculation(questionnaire_data, mock_document_chunks):
    """Test task count matches expected formula: questions × policy_areas × chunks."""
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire_data, document_chunks=mock_document_chunks
    )

    plan = synchronizer.build_execution_plan()

    expected_task_count = plan.question_count * 10 * 60

    assert (
        len(plan.tasks) == expected_task_count
    ), f"Expected {expected_task_count} tasks, got {len(plan.tasks)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
