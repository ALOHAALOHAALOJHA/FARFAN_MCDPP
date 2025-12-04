"""
Test Phase 2: Executor Context Preparation Integration Tests

Tests validation of routing key extraction, execution metadata extraction,
logging output structure, and deterministic task ordering for Phase 2.

CRITICAL VALIDATION AREAS:
1. Routing key extraction (pa_id, dim_id, question_global, question_id)
2. Execution metadata (expected_elements, signal_requirements, patterns)
3. Logging output structure and traceability
4. Deterministic task ordering across multiple runs
"""

import json
from dataclasses import asdict
from typing import Any
from unittest.mock import patch

import pytest

from farfan_pipeline.core.orchestrator.task_planner import (
    ExecutableTask,
    _construct_task,
    _validate_cross_task,
    _validate_schema,
)

TOTAL_QUESTIONS = 300
TOTAL_DIMENSIONS = 6
TOTAL_POLICY_AREAS = 10
QUESTIONS_PER_DIMENSION = 50
POLICY_AREA_ID_LENGTH = 4
DIMENSION_ID_LENGTH = 5
PA_DIM_COMBINATIONS = 60


@pytest.fixture
def sample_question() -> dict[str, Any]:
    """Sample microquestion for Phase 2."""
    return {
        "question_id": "MICRO_001",
        "question_global": 1,
        "base_slot": "D1-Q1",
        "dimension_id": "DIM01",
        "policy_area_id": "PA01",
        "cluster_id": "C01",
        "text": "Sample question text",
        "expected_elements": [
            {"field": "evidence", "type": "list"},
            {"field": "confidence", "type": "float"},
        ],
    }


@pytest.fixture
def sample_chunk() -> dict[str, Any]:
    """Sample chunk for Phase 2."""
    return {
        "id": "CHUNK_001",
        "policy_area_id": "PA01",
        "dimension_id": "DIM01",
        "expected_elements": [
            {"field": "evidence", "type": "list"},
            {"field": "confidence", "type": "float"},
        ],
    }


@pytest.fixture
def sample_patterns() -> list[dict[str, Any]]:
    """Sample patterns for signal extraction."""
    return [
        {
            "pattern_id": "PAT_001",
            "pattern_text": "problema.*identificado",
            "pattern_type": "diagnostic",
            "weight": 0.8,
        },
        {
            "pattern_id": "PAT_002",
            "pattern_text": "brecha.*detectada",
            "pattern_type": "gap_analysis",
            "weight": 0.9,
        },
    ]


@pytest.fixture
def sample_signals() -> dict[str, Any]:
    """Sample signals for question answering."""
    return {
        "required_signals": ["diagnostic_evidence", "gap_metrics"],
        "thresholds": {"min_confidence": 0.7, "min_evidence_count": 3},
        "signal_weights": {"diagnostic_evidence": 0.6, "gap_metrics": 0.4},
    }


class TestRoutingKeyExtraction:
    """Test routing key extraction from questions and chunks."""

    def test_extract_pa_id_from_question(self, sample_question):
        """Test policy area ID extraction."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert task.policy_area_id == "PA01"
        assert task.policy_area_id.startswith("PA")
        assert len(task.policy_area_id) == POLICY_AREA_ID_LENGTH

    def test_extract_dim_id_from_question(self, sample_question):
        """Test dimension ID extraction."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert task.dimension_id == "DIM01"
        assert task.dimension_id.startswith("DIM")
        assert len(task.dimension_id) == DIMENSION_ID_LENGTH

    def test_extract_question_global_from_question(self, sample_question):
        """Test question_global extraction."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert task.question_global == 1
        assert isinstance(task.question_global, int)
        assert 1 <= task.question_global <= TOTAL_QUESTIONS

    def test_extract_question_id_from_question(self, sample_question):
        """Test question_id extraction."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert task.question_id == "MICRO_001"
        assert isinstance(task.question_id, str)

    def test_task_id_format_consistency(self, sample_question):
        """Test task_id follows MQC-{question_global:03d}_{policy_area_id} format."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert task.task_id == "MQC-001_PA01"
        assert task.task_id.startswith("MQC-")
        assert "_PA" in task.task_id

    def test_routing_keys_all_dimensions(self):
        """Test routing key extraction for all 6 dimensions."""
        for dim_num in range(1, 7):
            question = {
                "question_id": f"MICRO_{dim_num:03d}",
                "question_global": dim_num,
                "dimension_id": f"DIM0{dim_num}",
                "policy_area_id": "PA01",
                "expected_elements": [],
            }

            task = _construct_task(
                question=question,
                chunk={"id": "CHUNK_001", "expected_elements": []},
                patterns=[],
                signals={},
                generated_ids=set(),
            )

            assert task.dimension_id == f"DIM0{dim_num}"

    def test_routing_keys_all_policy_areas(self):
        """Test routing key extraction for all 10 policy areas."""
        for pa_num in range(1, 11):
            question = {
                "question_id": f"MICRO_{pa_num:03d}",
                "question_global": pa_num,
                "dimension_id": "DIM01",
                "policy_area_id": f"PA{pa_num:02d}",
                "expected_elements": [],
            }

            task = _construct_task(
                question=question,
                chunk={"id": "CHUNK_001", "expected_elements": []},
                patterns=[],
                signals={},
                generated_ids=set(),
            )

            assert task.policy_area_id == f"PA{pa_num:02d}"

    def test_chunk_id_extraction(self, sample_question):
        """Test chunk_id extraction from chunk metadata."""
        chunk = {"id": "CHUNK_042", "expected_elements": []}

        task = _construct_task(
            question=sample_question,
            chunk=chunk,
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert task.chunk_id == "CHUNK_042"


class TestExecutionMetadataExtraction:
    """Test execution metadata extraction for Phase 2 context."""

    def test_extract_expected_elements(self, sample_question, sample_chunk):
        """Test expected_elements extraction and validation."""
        task = _construct_task(
            question=sample_question,
            chunk=sample_chunk,
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert len(task.expected_elements) == 2
        assert task.expected_elements[0]["field"] == "evidence"
        assert task.expected_elements[1]["field"] == "confidence"

    def test_schema_validation_success(self, sample_question, sample_chunk):
        """Test schema validation passes when schemas match."""
        _validate_schema(sample_question, sample_chunk)

    def test_schema_validation_failure(self, sample_question):
        """Test schema validation fails when schemas mismatch."""
        mismatched_chunk = {
            "id": "CHUNK_001",
            "expected_elements": [{"field": "different", "type": "string"}],
        }

        with pytest.raises(ValueError, match="Schema mismatch"):
            _validate_schema(sample_question, mismatched_chunk)

    def test_extract_signal_requirements(self, sample_question, sample_signals):
        """Test signal requirements extraction."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals=sample_signals,
            generated_ids=set(),
        )

        assert "required_signals" in task.signals
        assert "thresholds" in task.signals
        assert task.signals["required_signals"] == [
            "diagnostic_evidence",
            "gap_metrics",
        ]

    def test_extract_patterns(self, sample_question, sample_patterns):
        """Test pattern extraction for evidence matching."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=sample_patterns,
            signals={},
            generated_ids=set(),
        )

        assert len(task.patterns) == 2
        assert task.patterns[0]["pattern_id"] == "PAT_001"
        assert task.patterns[1]["pattern_type"] == "gap_analysis"

    def test_metadata_cluster_id(self, sample_question):
        """Test cluster_id metadata extraction."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert task.metadata["cluster_id"] == "C01"

    def test_metadata_base_slot(self, sample_question):
        """Test base_slot metadata extraction."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert task.metadata["base_slot"] == "D1-Q1"

    def test_creation_timestamp_format(self, sample_question):
        """Test creation_timestamp is in ISO format."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert isinstance(task.creation_timestamp, str)
        assert "T" in task.creation_timestamp
        assert "Z" in task.creation_timestamp or "+" in task.creation_timestamp


class TestLoggingOutputStructure:
    """Test logging output structure and traceability."""

    def test_task_serialization_to_dict(self, sample_question):
        """Test ExecutableTask can be serialized to dict."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        task_dict = asdict(task)

        assert isinstance(task_dict, dict)
        assert "task_id" in task_dict
        assert "question_id" in task_dict
        assert "policy_area_id" in task_dict

    def test_task_serialization_to_json(self, sample_question):
        """Test ExecutableTask can be serialized to JSON."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        task_dict = asdict(task)
        json_str = json.dumps(task_dict)

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["task_id"] == task.task_id

    def test_logging_contains_all_routing_keys(self, sample_question):
        """Test logging output includes all routing keys."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        task_dict = asdict(task)

        assert "policy_area_id" in task_dict
        assert "dimension_id" in task_dict
        assert "question_global" in task_dict
        assert "question_id" in task_dict

    def test_logging_contains_execution_metadata(self, sample_question, sample_signals):
        """Test logging output includes execution metadata."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals=sample_signals,
            generated_ids=set(),
        )

        task_dict = asdict(task)

        assert "expected_elements" in task_dict
        assert "signals" in task_dict
        assert "patterns" in task_dict
        assert "creation_timestamp" in task_dict

    def test_logging_metadata_nested_structure(self, sample_question):
        """Test metadata field contains nested structure."""
        task = _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=set(),
        )

        assert isinstance(task.metadata, dict)
        assert "base_slot" in task.metadata
        assert "cluster_id" in task.metadata

    def test_duplicate_task_id_detection(self, sample_question):
        """Test duplicate task_id raises error."""
        generated_ids = set()

        _construct_task(
            question=sample_question,
            chunk={"id": "CHUNK_001", "expected_elements": []},
            patterns=[],
            signals={},
            generated_ids=generated_ids,
        )

        with pytest.raises(ValueError, match="Duplicate task_id"):
            _construct_task(
                question=sample_question,
                chunk={"id": "CHUNK_002", "expected_elements": []},
                patterns=[],
                signals={},
                generated_ids=generated_ids,
            )


class TestDeterministicTaskOrdering:
    """Test deterministic task ordering across multiple runs."""

    def test_dimension_first_ordering(self):
        """Test tasks are ordered by dimension first."""
        questions = [
            {
                "question_id": f"Q{i:03d}",
                "question_global": i,
                "dimension_id": f"DIM0{(i % 6) + 1}",
                "policy_area_id": "PA01",
                "expected_elements": [],
            }
            for i in range(1, 13)
        ]

        tasks = [
            _construct_task(
                question=q,
                chunk={"id": f"CHUNK_{i:03d}", "expected_elements": []},
                patterns=[],
                signals={},
                generated_ids=set(),
            )
            for i, q in enumerate(questions, 1)
        ]

        sorted_tasks = sorted(tasks, key=lambda t: (t.dimension_id, t.policy_area_id))

        for i in range(len(sorted_tasks) - 1):
            assert sorted_tasks[i].dimension_id <= sorted_tasks[i + 1].dimension_id

    def test_policy_area_ordering_within_dimension(self):
        """Test tasks are ordered by policy area within each dimension."""
        questions = [
            {
                "question_id": f"Q{i:03d}",
                "question_global": i,
                "dimension_id": "DIM01",
                "policy_area_id": f"PA{(i % 10) + 1:02d}",
                "expected_elements": [],
            }
            for i in range(1, 21)
        ]

        tasks = [
            _construct_task(
                question=q,
                chunk={"id": f"CHUNK_{i:03d}", "expected_elements": []},
                patterns=[],
                signals={},
                generated_ids=set(),
            )
            for i, q in enumerate(questions, 1)
        ]

        dim01_tasks = [t for t in tasks if t.dimension_id == "DIM01"]
        sorted_tasks = sorted(dim01_tasks, key=lambda t: t.policy_area_id)

        for i in range(len(sorted_tasks) - 1):
            assert sorted_tasks[i].policy_area_id <= sorted_tasks[i + 1].policy_area_id

    def test_ordering_deterministic_across_runs(self):
        """Test task ordering is deterministic across multiple runs."""
        questions = [
            {
                "question_id": f"Q{i:03d}",
                "question_global": i,
                "dimension_id": f"DIM0{((i - 1) // 50) + 1}",
                "policy_area_id": f"PA{((i - 1) % 10) + 1:02d}",
                "expected_elements": [],
            }
            for i in range(1, 31)
        ]

        task_ids_runs = []
        for _run in range(5):
            tasks = [
                _construct_task(
                    question=q,
                    chunk={"id": f"CHUNK_{i:03d}", "expected_elements": []},
                    patterns=[],
                    signals={},
                    generated_ids=set(),
                )
                for i, q in enumerate(questions, 1)
            ]

            sorted_tasks = sorted(
                tasks, key=lambda t: (t.dimension_id, t.policy_area_id, t.question_id)
            )
            task_ids = [t.task_id for t in sorted_tasks]
            task_ids_runs.append(task_ids)

        first_run = task_ids_runs[0]
        for subsequent_run in task_ids_runs[1:]:
            assert first_run == subsequent_run

    def test_300_questions_ordering(self):
        """Test all 300 questions maintain deterministic ordering."""
        questions = [
            {
                "question_id": f"MICRO_{i:03d}",
                "question_global": i,
                "dimension_id": f"DIM{((i - 1) // 50) + 1:02d}",
                "policy_area_id": f"PA{((i - 1) % 10) + 1:02d}",
                "expected_elements": [],
            }
            for i in range(1, 301)
        ]

        generated_ids = set()
        tasks = [
            _construct_task(
                question=q,
                chunk={"id": f"CHUNK_{i:03d}", "expected_elements": []},
                patterns=[],
                signals={},
                generated_ids=generated_ids,
            )
            for i, q in enumerate(questions, 1)
        ]

        assert len(tasks) == TOTAL_QUESTIONS

        sorted_tasks = sorted(
            tasks, key=lambda t: (t.dimension_id, t.policy_area_id, t.question_global)
        )

        for i in range(len(sorted_tasks) - 1):
            if sorted_tasks[i].dimension_id == sorted_tasks[i + 1].dimension_id:
                assert (
                    sorted_tasks[i].policy_area_id <= sorted_tasks[i + 1].policy_area_id
                )


class TestCrossTaskValidation:
    """Test cross-task validation and consistency checks."""

    def test_chunk_usage_validation(self):
        """Test chunk usage validation (5 tasks per chunk expected)."""
        tasks = []
        for i in range(1, 6):
            task = ExecutableTask(
                task_id=f"MQC-{i:03d}_PA01",
                question_id=f"Q{i:03d}",
                question_global=i,
                policy_area_id="PA01",
                dimension_id="DIM01",
                chunk_id="CHUNK_001",
                patterns=[],
                signals={},
                creation_timestamp="2025-01-01T00:00:00Z",
            )
            tasks.append(task)

        with patch(
            "farfan_pipeline.core.orchestrator.task_planner.logger"
        ) as mock_logger:
            _validate_cross_task(tasks)

        chunk_warnings = [
            call
            for call in mock_logger.warning.call_args_list
            if "Chunk usage deviation" in str(call)
        ]
        assert len(chunk_warnings) == 0

    def test_chunk_usage_deviation_warning(self):
        """Test warning when chunk usage deviates from expected."""
        tasks = []
        for i in range(1, 4):
            task = ExecutableTask(
                task_id=f"MQC-{i:03d}_PA01",
                question_id=f"Q{i:03d}",
                question_global=i,
                policy_area_id="PA01",
                dimension_id="DIM01",
                chunk_id="CHUNK_001",
                patterns=[],
                signals={},
                creation_timestamp="2025-01-01T00:00:00Z",
            )
            tasks.append(task)

        with patch(
            "farfan_pipeline.core.orchestrator.task_planner.logger"
        ) as mock_logger:
            _validate_cross_task(tasks)

        mock_logger.warning.assert_called()
        chunk_warnings = [
            call[0][0]
            for call in mock_logger.warning.call_args_list
            if "Chunk usage deviation" in call[0][0]
        ]
        assert len(chunk_warnings) > 0
        assert "CHUNK_001" in chunk_warnings[0]

    def test_policy_area_usage_validation(self):
        """Test policy area usage validation (30 tasks per PA expected)."""
        tasks = []
        for i in range(1, 31):
            task = ExecutableTask(
                task_id=f"MQC-{i:03d}_PA01",
                question_id=f"Q{i:03d}",
                question_global=i,
                policy_area_id="PA01",
                dimension_id=f"DIM{((i - 1) // 5) + 1:02d}",
                chunk_id=f"CHUNK_{i:03d}",
                patterns=[],
                signals={},
                creation_timestamp="2025-01-01T00:00:00Z",
            )
            tasks.append(task)

        with patch(
            "farfan_pipeline.core.orchestrator.task_planner.logger"
        ) as mock_logger:
            _validate_cross_task(tasks)

        pa_warnings = [
            call
            for call in mock_logger.warning.call_args_list
            if "Policy area usage deviation" in str(call)
        ]
        assert len(pa_warnings) == 0

    def test_policy_area_usage_deviation_warning(self):
        """Test warning when policy area usage deviates from expected."""
        tasks = []
        for i in range(1, 16):
            task = ExecutableTask(
                task_id=f"MQC-{i:03d}_PA01",
                question_id=f"Q{i:03d}",
                question_global=i,
                policy_area_id="PA01",
                dimension_id="DIM01",
                chunk_id=f"CHUNK_{i:03d}",
                patterns=[],
                signals={},
                creation_timestamp="2025-01-01T00:00:00Z",
            )
            tasks.append(task)

        with patch(
            "farfan_pipeline.core.orchestrator.task_planner.logger"
        ) as mock_logger:
            _validate_cross_task(tasks)

        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Policy area usage deviation" in warning_call


class TestPhase2IntegrationScenarios:
    """Test complete Phase 2 integration scenarios."""

    def test_complete_task_construction_pipeline(
        self, sample_question, sample_chunk, sample_patterns, sample_signals
    ):
        """Test complete task construction with all components."""
        task = _construct_task(
            question=sample_question,
            chunk=sample_chunk,
            patterns=sample_patterns,
            signals=sample_signals,
            generated_ids=set(),
        )

        assert task.task_id == "MQC-001_PA01"
        assert task.question_id == "MICRO_001"
        assert task.policy_area_id == "PA01"
        assert task.dimension_id == "DIM01"
        assert len(task.patterns) == 2
        assert "required_signals" in task.signals
        assert len(task.expected_elements) == 2

    def test_dimension_scoped_execution_plan(self):
        """Test execution plan for single dimension (50 questions)."""
        questions = [
            {
                "question_id": f"MICRO_{i:03d}",
                "question_global": i,
                "dimension_id": "DIM01",
                "policy_area_id": f"PA{((i - 1) % 10) + 1:02d}",
                "expected_elements": [],
            }
            for i in range(1, 51)
        ]

        generated_ids = set()
        tasks = [
            _construct_task(
                question=q,
                chunk={"id": f"CHUNK_{i:03d}", "expected_elements": []},
                patterns=[],
                signals={},
                generated_ids=generated_ids,
            )
            for i, q in enumerate(questions, 1)
        ]

        assert len(tasks) == QUESTIONS_PER_DIMENSION
        assert all(t.dimension_id == "DIM01" for t in tasks)
        assert len({t.policy_area_id for t in tasks}) == TOTAL_POLICY_AREAS

    def test_full_300_question_execution_plan(self):
        """Test complete 300-question execution plan."""
        questions = [
            {
                "question_id": f"MICRO_{i:03d}",
                "question_global": i,
                "dimension_id": f"DIM{((i - 1) // 50) + 1:02d}",
                "policy_area_id": f"PA{((i - 1) % 10) + 1:02d}",
                "base_slot": f"D{((i - 1) // 50) + 1}-Q{((i - 1) % 5) + 1}",
                "expected_elements": [],
            }
            for i in range(1, 301)
        ]

        generated_ids = set()
        tasks = [
            _construct_task(
                question=q,
                chunk={
                    "id": f"CHUNK_{((i - 1) // 5) + 1:03d}",
                    "expected_elements": [],
                },
                patterns=[],
                signals={},
                generated_ids=generated_ids,
            )
            for i, q in enumerate(questions, 1)
        ]

        assert len(tasks) == TOTAL_QUESTIONS
        assert len({t.dimension_id for t in tasks}) == TOTAL_DIMENSIONS
        assert len({t.policy_area_id for t in tasks}) == TOTAL_POLICY_AREAS

        for dim_id in [f"DIM{i:02d}" for i in range(1, 7)]:
            dim_tasks = [t for t in tasks if t.dimension_id == dim_id]
            assert len(dim_tasks) == QUESTIONS_PER_DIMENSION

    def test_pa_dim_isolation(self):
        """Test PA×DIM isolation in task construction."""
        tasks_matrix = {}

        for dim in range(1, 7):
            for pa in range(1, 11):
                question = {
                    "question_id": f"Q_D{dim}_PA{pa:02d}",
                    "question_global": (dim - 1) * 10 + pa,
                    "dimension_id": f"DIM{dim:02d}",
                    "policy_area_id": f"PA{pa:02d}",
                    "expected_elements": [],
                }

                task = _construct_task(
                    question=question,
                    chunk={"id": f"CHUNK_D{dim}_PA{pa:02d}", "expected_elements": []},
                    patterns=[],
                    signals={},
                    generated_ids=set(),
                )

                key = (task.dimension_id, task.policy_area_id)
                if key not in tasks_matrix:
                    tasks_matrix[key] = []
                tasks_matrix[key].append(task)

        assert len(tasks_matrix) == PA_DIM_COMBINATIONS

        for (dim_id, pa_id), task_list in tasks_matrix.items():
            for task in task_list:
                assert task.dimension_id == dim_id
                assert task.policy_area_id == pa_id
