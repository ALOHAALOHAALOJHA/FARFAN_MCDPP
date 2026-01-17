"""
Test Phase 2 Micro-Question Execution Logic

This test suite validates the Phase 2 execution logic that uses
IrrigationSynchronizer execution plan to dispatch micro-questions
across document chunks with retry logic.

Requirements tested:
- Uses IrrigationSynchronizer execution_plan to dispatch all tasks
- Selects and runs appropriate executors for each question/task
- Handles transient executor failures with up to 3 retries
- Populates all MicroQuestionRun objects with evidence
- Propagates errors and abort signals appropriately

Run with:  pytest tests/test_phase2_execution_logic.py -v --tb=short
"""

from __future__ import annotations

import asyncio
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from farfan_pipeline.orchestration.core_orchestrator import (
    Evidence,
    MicroQuestionRun,
    Orchestrator,
    PhaseInstrumentation,
    ResourceLimits,
)
from farfan_pipeline.orchestration.task_planner import ExecutableTask


class TestPhase2ExecutionPlan:
    """Test Phase 2 uses execution plan instead of questionnaire questions."""
    
    @pytest.mark.asyncio
    async def test_execution_plan_required(self):
        """Test that Phase 2 requires execution plan to be set."""
        mock_executor = Mock()
        mock_executor.signal_registry = Mock()
        mock_executor.instances = {"test": Mock()}
        
        mock_questionnaire = Mock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {}
            }
        }
        
        mock_config = Mock()
        
        with patch("orchestration.questionnaire_validation._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=mock_config,
            )
        orchestrator._phase_instrumentation[2] = PhaseInstrumentation(2, "Phase 2")
        orchestrator._execution_plan = None
        
        document = Mock()
        config = {}
        
        with pytest.raises(RuntimeError, match="Execution plan missing"):
            await orchestrator._execute_micro_questions_async(document, config)
    
    @pytest.mark.asyncio
    async def test_uses_execution_plan_tasks(self):
        """Test that Phase 2 iterates over execution plan tasks, not questions."""
        mock_executor = Mock()
        mock_executor.signal_registry = Mock()
        mock_executor.instances = {"test": Mock()}
        
        mock_questionnaire = Mock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [{"id": "Q001"}],  # Should be ignored
                "meso_questions": [],
                "macro_question": {}
            }
        }
        
        mock_config = Mock()
        
        with patch("orchestration.questionnaire_validation._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=mock_config,
            )
        orchestrator._phase_instrumentation[2] = PhaseInstrumentation(2, "Phase 2")
        orchestrator._canonical_questionnaire = mock_questionnaire
        orchestrator.executor_config = mock_config
        orchestrator.calibration_orchestrator = None
        orchestrator._enriched_packs = {}
        
        task1 = ExecutableTask(
            task_id="T001",
            question_id="Q001",
            question_global=1,
            policy_area_id="PA01",
            dimension_id="D1",
            chunk_id="PA01-D1",
            patterns=[],
            signals={},
            creation_timestamp="2024-01-01T00:00:00Z",
            expected_elements=[],
            metadata={"base_slot": "D1-Q1", "cluster_id": "C1"}
        )
        
        mock_plan = Mock()
        mock_plan.tasks = [task1]
        mock_plan.plan_id = "PLAN001"
        mock_plan.chunk_count = 60
        mock_plan.question_count = 305
        
        orchestrator._execution_plan = mock_plan
        
        mock_executor_class = Mock()
        mock_instance = Mock()
        mock_executor_class.return_value = mock_instance
        
        mock_instance.execute.return_value = {
            "metadata": {"test": "data"},
            "evidence": Evidence(
                modality="text",
                elements=["test evidence"],
                raw_results={"confidence": 0.9, "source": "test"}
            )
        }
        
        orchestrator.executors = {"D1-Q1": mock_executor_class}
        
        document = Mock()
        config = {}
        
        results = await orchestrator._execute_micro_questions_async(document, config)
        
        assert len(results) == 1
        assert results[0].question_id == "Q001"
        assert results[0].question_global == 1
        assert results[0].base_slot == "D1-Q1"
        assert results[0].evidence is not None
        assert results[0].metadata["task_id"] == "T001"
        assert results[0].metadata["chunk_id"] == "PA01-D1"


class TestPhase2RetryLogic:
    """Test retry logic for transient executor failures."""
    
    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self):
        """Test that executor failures trigger retries."""
        mock_executor = Mock()
        mock_executor.signal_registry = Mock()
        mock_executor.instances = {"test": Mock()}
        
        mock_questionnaire = Mock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {}
            }
        }
        
        mock_config = Mock()
        
        with patch("orchestration.questionnaire_validation._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=mock_config,
            )
        orchestrator._phase_instrumentation[2] = PhaseInstrumentation(2, "Phase 2")
        orchestrator._canonical_questionnaire = mock_questionnaire
        orchestrator.executor_config = mock_config
        orchestrator.calibration_orchestrator = None
        orchestrator._enriched_packs = {}
        
        task1 = ExecutableTask(
            task_id="T001",
            question_id="Q001",
            question_global=1,
            policy_area_id="PA01",
            dimension_id="D1",
            chunk_id="PA01-D1",
            patterns=[],
            signals={},
            creation_timestamp="2024-01-01T00:00:00Z",
            expected_elements=[],
            metadata={"base_slot": "D1-Q1", "cluster_id": "C1"}
        )
        
        mock_plan = Mock()
        mock_plan.tasks = [task1]
        mock_plan.plan_id = "PLAN001"
        mock_plan.chunk_count = 60
        mock_plan.question_count = 305
        
        orchestrator._execution_plan = mock_plan
        
        mock_executor_class = Mock()
        mock_instance = Mock()
        mock_executor_class.return_value = mock_instance
        
        call_count = 0
        def execute_with_retries(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient network error")
            return {
                "metadata": {"attempts": call_count},
                "evidence": Evidence(
                    modality="text",
                    elements=["success after retry"],
                    raw_results={"confidence": 0.9, "source": "test"}
                )
            }
        
        mock_instance.execute.side_effect = execute_with_retries
        orchestrator.executors = {"D1-Q1": mock_executor_class}
        
        document = Mock()
        config = {}
        
        start = time.time()
        results = await orchestrator._execute_micro_questions_async(document, config)
        duration = time.time() - start
        
        assert len(results) == 1
        assert results[0].evidence is not None
        assert results[0].error is None
        assert results[0].metadata["attempts"] == 3
        assert call_count == 3
        assert duration > 1.0
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that failures after max retries are recorded as errors."""
        mock_executor = Mock()
        mock_executor.signal_registry = Mock()
        mock_executor.instances = {"test": Mock()}
        
        mock_questionnaire = Mock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {}
            }
        }
        
        mock_config = Mock()
        
        with patch("orchestration.questionnaire_validation._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=mock_config,
            )
        orchestrator._phase_instrumentation[2] = PhaseInstrumentation(2, "Phase 2")
        orchestrator._canonical_questionnaire = mock_questionnaire
        orchestrator.executor_config = mock_config
        orchestrator.calibration_orchestrator = None
        orchestrator._enriched_packs = {}
        
        task1 = ExecutableTask(
            task_id="T001",
            question_id="Q001",
            question_global=1,
            policy_area_id="PA01",
            dimension_id="D1",
            chunk_id="PA01-D1",
            patterns=[],
            signals={},
            creation_timestamp="2024-01-01T00:00:00Z",
            expected_elements=[],
            metadata={"base_slot": "D1-Q1", "cluster_id": "C1"}
        )
        
        mock_plan = Mock()
        mock_plan.tasks = [task1]
        mock_plan.plan_id = "PLAN001"
        mock_plan.chunk_count = 60
        mock_plan.question_count = 305
        
        orchestrator._execution_plan = mock_plan
        
        mock_executor_class = Mock()
        mock_instance = Mock()
        mock_executor_class.return_value = mock_instance
        mock_instance.execute.side_effect = RuntimeError("Persistent error")
        
        orchestrator.executors = {"D1-Q1": mock_executor_class}
        
        document = Mock()
        config = {}
        
        results = await orchestrator._execute_micro_questions_async(document, config)
        
        assert len(results) == 1
        assert results[0].evidence is None
        assert results[0].error is not None
        assert "Failed after 3 attempts" in results[0].error
        assert results[0].metadata["attempts"] == 3
        assert mock_instance.execute.call_count == 3


class TestPhase2EvidenceValidation:
    """Test evidence validation and null evidence handling."""
    
    @pytest.mark.asyncio
    async def test_null_evidence_logged(self):
        """Test that null evidence is logged as a warning."""
        mock_executor = Mock()
        mock_executor.signal_registry = Mock()
        mock_executor.instances = {"test": Mock()}
        
        mock_questionnaire = Mock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {}
            }
        }
        
        mock_config = Mock()
        
        with patch("orchestration.questionnaire_validation._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=mock_config,
            )
        orchestrator._phase_instrumentation[2] = PhaseInstrumentation(2, "Phase 2")
        orchestrator._canonical_questionnaire = mock_questionnaire
        orchestrator.executor_config = mock_config
        orchestrator.calibration_orchestrator = None
        orchestrator._enriched_packs = {}
        
        task1 = ExecutableTask(
            task_id="T001",
            question_id="Q001",
            question_global=1,
            policy_area_id="PA01",
            dimension_id="D1",
            chunk_id="PA01-D1",
            patterns=[],
            signals={},
            creation_timestamp="2024-01-01T00:00:00Z",
            expected_elements=[],
            metadata={"base_slot": "D1-Q1", "cluster_id": "C1"}
        )
        
        mock_plan = Mock()
        mock_plan.tasks = [task1]
        mock_plan.plan_id = "PLAN001"
        mock_plan.chunk_count = 60
        mock_plan.question_count = 305
        
        orchestrator._execution_plan = mock_plan
        
        mock_executor_class = Mock()
        mock_instance = Mock()
        mock_executor_class.return_value = mock_instance
        mock_instance.execute.return_value = {
            "metadata": {"test": "data"},
            "evidence": None  # Null evidence
        }
        
        orchestrator.executors = {"D1-Q1": mock_executor_class}
        
        document = Mock()
        config = {}
        
        with patch("farfan_pipeline.orchestration.orchestrator.logger") as mock_logger:
            results = await orchestrator._execute_micro_questions_async(document, config)
            
            mock_logger.warning.assert_any_call(
                "executor_returned_null_evidence",
                task_id="T001",
                base_slot="D1-Q1",
                attempt=1
            )
        
        assert len(results) == 1
        assert results[0].evidence is None


class TestPhase2Integration:
    """Integration tests for full Phase 2 execution."""
    
    @pytest.mark.asyncio
    async def test_multiple_tasks_executed(self):
        """Test that multiple tasks are executed correctly."""
        mock_executor = Mock()
        mock_executor.signal_registry = Mock()
        mock_executor.instances = {"test": Mock()}
        
        mock_questionnaire = Mock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {}
            }
        }
        
        mock_config = Mock()
        
        with patch("orchestration.questionnaire_validation._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=mock_config,
            )
        orchestrator._phase_instrumentation[2] = PhaseInstrumentation(2, "Phase 2")
        orchestrator._canonical_questionnaire = mock_questionnaire
        orchestrator.executor_config = mock_config
        orchestrator.calibration_orchestrator = None
        orchestrator._enriched_packs = {}
        
        tasks = []
        for i in range(10):
            task = ExecutableTask(
                task_id=f"T{i:03d}",
                question_id=f"Q{i:03d}",
                question_global=i + 1,
                policy_area_id=f"PA{(i % 10) + 1:02d}",
                dimension_id=f"D{(i % 6) + 1}",
                chunk_id=f"PA{(i % 10) + 1:02d}-D{(i % 6) + 1}",
                patterns=[],
                signals={},
                creation_timestamp="2024-01-01T00:00:00Z",
                expected_elements=[],
                metadata={"base_slot": f"D{(i % 6) + 1}-Q{(i % 5) + 1}", "cluster_id": "C1"}
            )
            tasks.append(task)
        
        mock_plan = Mock()
        mock_plan.tasks = tasks
        mock_plan.plan_id = "PLAN001"
        mock_plan.chunk_count = 60
        mock_plan.question_count = 305
        
        orchestrator._execution_plan = mock_plan
        
        mock_executor_class = Mock()
        mock_instance = Mock()
        mock_executor_class.return_value = mock_instance
        
        def execute_mock(*args, **kwargs):
            q_context = kwargs.get("question_context", {})
            return {
                "metadata": {"task_id": q_context.get("task_id")},
                "evidence": Evidence(
                    modality="text",
                    elements=[f"evidence for {q_context.get('task_id')}"],
                    raw_results={"confidence": 0.9, "source": "test"}
                )
            }
        
        mock_instance.execute.side_effect = execute_mock
        
        orchestrator.executors = {
            "D1-Q1": mock_executor_class,
            "D1-Q2": mock_executor_class,
            "D1-Q3": mock_executor_class,
            "D1-Q4": mock_executor_class,
            "D1-Q5": mock_executor_class,
            "D2-Q1": mock_executor_class,
            "D2-Q2": mock_executor_class,
            "D2-Q3": mock_executor_class,
            "D2-Q4": mock_executor_class,
            "D2-Q5": mock_executor_class,
            "D3-Q1": mock_executor_class,
            "D3-Q2": mock_executor_class,
            "D3-Q3": mock_executor_class,
            "D3-Q4": mock_executor_class,
            "D3-Q5": mock_executor_class,
            "D4-Q1": mock_executor_class,
            "D4-Q2": mock_executor_class,
            "D4-Q3": mock_executor_class,
            "D4-Q4": mock_executor_class,
            "D4-Q5": mock_executor_class,
            "D5-Q1": mock_executor_class,
            "D5-Q2": mock_executor_class,
            "D5-Q3": mock_executor_class,
            "D5-Q4": mock_executor_class,
            "D5-Q5": mock_executor_class,
            "D6-Q1": mock_executor_class,
            "D6-Q2": mock_executor_class,
            "D6-Q3": mock_executor_class,
            "D6-Q4": mock_executor_class,
            "D6-Q5": mock_executor_class,
        }
        
        document = Mock()
        config = {}
        
        results = await orchestrator._execute_micro_questions_async(document, config)
        
        assert len(results) == 10
        assert all(r.evidence is not None for r in results)
        assert all(r.error is None for r in results)
        assert [r.question_id for r in results] == [f"Q{i:03d}" for i in range(10)]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
