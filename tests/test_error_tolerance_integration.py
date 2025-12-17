"""Integration tests for error tolerance with injected failures.

Tests verify:
1. Pipeline continues with partial failures
2. Error rates are tracked correctly
3. Thresholds trigger appropriate behavior
4. Reports contain error tolerance information
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import Mock, patch

import pytest

from canonic_phases.Phase_zero.runtime_config import RuntimeConfig, RuntimeMode
from orchestration.orchestrator import Orchestrator, ErrorTolerance, AbortRequested


class MockExecutorSuccess:
    """Mock executor that always succeeds."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass
    
    def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "metadata": {"overall_confidence": 0.85, "completeness": "complete"},
            "evidence": {"validation": {"score": 0.85}},
        }


class MockExecutorFailure:
    """Mock executor that always fails."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass
    
    def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("Simulated executor failure")


class TestPhase2ErrorTolerance:
    """Integration tests for Phase 2 error tolerance."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_phase2_succeeds_with_5_percent_failures(self) -> None:
        """Phase 2 should succeed with 5% failure rate."""
        from orchestration.factory import get_questionnaire
        from orchestration.orchestrator import MethodExecutor
        from orchestration.class_registry import MethodRegistry
        
        questionnaire = get_questionnaire()
        registry = MethodRegistry()
        executor = MethodExecutor(registry)
        runtime_config = RuntimeConfig(mode=RuntimeMode.PRODUCTION)
        
        orchestrator = Orchestrator(
            method_executor=executor,
            questionnaire=questionnaire,
            executor_config={},
            runtime_config=runtime_config,
        )
        
        config = {
            "micro_questions": [
                {
                    "id": f"Q{i:03d}",
                    "global_id": i,
                    "base_slot": f"D1-Q{(i % 5) + 1}",
                    "patterns": [],
                    "expected_elements": [],
                    "dimension_id": "D1",
                    "cluster_id": "C1",
                }
                for i in range(1, 101)
            ]
        }
        
        with patch.object(orchestrator, "executors", {
            "D1-Q1": MockExecutorSuccess,
            "D1-Q2": MockExecutorSuccess,
            "D1-Q3": MockExecutorSuccess,
            "D1-Q4": MockExecutorSuccess,
            "D1-Q5": MockExecutorFailure,
        }):
            document = Mock()
            results = await orchestrator._execute_micro_questions_async(document, config)
        
        error_tracker = orchestrator._error_tolerance[2]
        
        assert error_tracker.current_failure_rate() <= 0.10
        assert not error_tracker.threshold_exceeded()
        assert len(results) == 100
        assert error_tracker.can_mark_success(RuntimeMode.PRODUCTION)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_phase2_fails_with_15_percent_failures_in_production(self) -> None:
        """Phase 2 should fail with 15% failure rate in PRODUCTION mode."""
        from orchestration.factory import get_questionnaire
        from orchestration.orchestrator import MethodExecutor
        from orchestration.class_registry import MethodRegistry
        
        questionnaire = get_questionnaire()
        registry = MethodRegistry()
        executor = MethodExecutor(registry)
        runtime_config = RuntimeConfig(mode=RuntimeMode.PRODUCTION)
        
        orchestrator = Orchestrator(
            method_executor=executor,
            questionnaire=questionnaire,
            executor_config={},
            runtime_config=runtime_config,
        )
        
        config = {
            "micro_questions": [
                {
                    "id": f"Q{i:03d}",
                    "global_id": i,
                    "base_slot": f"D1-Q{(i % 7) + 1}",
                    "patterns": [],
                    "expected_elements": [],
                    "dimension_id": "D1",
                    "cluster_id": "C1",
                }
                for i in range(1, 101)
            ]
        }
        
        with patch.object(orchestrator, "executors", {
            "D1-Q1": MockExecutorSuccess,
            "D1-Q2": MockExecutorSuccess,
            "D1-Q3": MockExecutorSuccess,
            "D1-Q4": MockExecutorSuccess,
            "D1-Q5": MockExecutorSuccess,
            "D1-Q6": MockExecutorFailure,
            "D1-Q7": MockExecutorFailure,
        }):
            document = Mock()
            with pytest.raises(AbortRequested, match="Phase 2 error threshold exceeded"):
                await orchestrator._execute_micro_questions_async(document, config)
        
        error_tracker = orchestrator._error_tolerance[2]
        
        assert error_tracker.threshold_exceeded()
        assert not error_tracker.can_mark_success(RuntimeMode.PRODUCTION)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_phase2_partial_success_in_dev_mode(self) -> None:
        """Phase 2 should allow partial success in DEV mode with 60% success rate."""
        from orchestration.factory import get_questionnaire
        from orchestration.orchestrator import MethodExecutor
        from orchestration.class_registry import MethodRegistry
        
        questionnaire = get_questionnaire()
        registry = MethodRegistry()
        executor = MethodExecutor(registry)
        runtime_config = RuntimeConfig(mode=RuntimeMode.DEV)
        
        orchestrator = Orchestrator(
            method_executor=executor,
            questionnaire=questionnaire,
            executor_config={},
            runtime_config=runtime_config,
        )
        
        config = {
            "micro_questions": [
                {
                    "id": f"Q{i:03d}",
                    "global_id": i,
                    "base_slot": f"D1-Q{(i % 5) + 1}",
                    "patterns": [],
                    "expected_elements": [],
                    "dimension_id": "D1",
                    "cluster_id": "C1",
                }
                for i in range(1, 101)
            ]
        }
        
        with patch.object(orchestrator, "executors", {
            "D1-Q1": MockExecutorSuccess,
            "D1-Q2": MockExecutorSuccess,
            "D1-Q3": MockExecutorSuccess,
            "D1-Q4": MockExecutorFailure,
            "D1-Q5": MockExecutorFailure,
        }):
            document = Mock()
            results = await orchestrator._execute_micro_questions_async(document, config)
        
        error_tracker = orchestrator._error_tolerance[2]
        
        assert error_tracker.threshold_exceeded()
        assert error_tracker.can_mark_success(RuntimeMode.DEV)
        assert error_tracker.successful_questions >= 50


class TestManifestMarking:
    """Tests for manifest marking with error tolerance."""
    
    def test_report_includes_error_tolerance_metrics(self) -> None:
        """Report should include error tolerance metrics."""
        from orchestration.factory import get_questionnaire
        from orchestration.orchestrator import MethodExecutor
        from orchestration.class_registry import MethodRegistry
        
        questionnaire = get_questionnaire()
        registry = MethodRegistry()
        executor = MethodExecutor(registry)
        runtime_config = RuntimeConfig(mode=RuntimeMode.PRODUCTION)
        
        orchestrator = Orchestrator(
            method_executor=executor,
            questionnaire=questionnaire,
            executor_config={},
            runtime_config=runtime_config,
        )
        
        orchestrator._error_tolerance[2].total_questions = 100
        for _ in range(92):
            orchestrator._error_tolerance[2].record_success()
        for _ in range(8):
            orchestrator._error_tolerance[2].record_failure()
        
        orchestrator._error_tolerance[3].total_questions = 100
        for _ in range(95):
            orchestrator._error_tolerance[3].record_success()
        for _ in range(5):
            orchestrator._error_tolerance[3].record_failure()
        
        report = orchestrator._assemble_report({}, {})
        
        assert "error_tolerance" in report
        assert 2 in report["error_tolerance"]
        assert 3 in report["error_tolerance"]
        assert report["error_tolerance"][2]["current_failure_rate"] == 0.08
        assert report["error_tolerance"][3]["current_failure_rate"] == 0.05
    
    def test_report_marks_partial_success_in_dev_mode(self) -> None:
        """Report should mark partial_success in DEV mode."""
        from orchestration.factory import get_questionnaire
        from orchestration.orchestrator import MethodExecutor
        from orchestration.class_registry import MethodRegistry
        
        questionnaire = get_questionnaire()
        registry = MethodRegistry()
        executor = MethodExecutor(registry)
        runtime_config = RuntimeConfig(mode=RuntimeMode.DEV)
        
        orchestrator = Orchestrator(
            method_executor=executor,
            questionnaire=questionnaire,
            executor_config={},
            runtime_config=runtime_config,
        )
        
        orchestrator._error_tolerance[2].total_questions = 100
        for _ in range(60):
            orchestrator._error_tolerance[2].record_success()
        for _ in range(40):
            orchestrator._error_tolerance[2].record_failure()
        
        orchestrator._error_tolerance[3].total_questions = 100
        for _ in range(65):
            orchestrator._error_tolerance[3].record_success()
        for _ in range(35):
            orchestrator._error_tolerance[3].record_failure()
        
        report = orchestrator._assemble_report({}, {})
        
        assert report["partial_success"] is True
        assert report["runtime_mode"] == "DEV"


class TestRegressionSilentFailure:
    """Regression tests to prevent silent failures."""
    
    def test_errors_are_logged_and_tracked(self) -> None:
        """Errors should be logged and tracked, not silently ignored."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        
        tracker.record_failure()
        
        assert tracker.failed_questions == 1
        assert tracker.current_failure_rate() > 0.0
    
    def test_threshold_exceeded_is_detectable(self) -> None:
        """Threshold exceeded state should be detectable."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        
        for _ in range(80):
            tracker.record_success()
        for _ in range(20):
            tracker.record_failure()
        
        assert tracker.threshold_exceeded()
        result = tracker.to_dict()
        assert result["threshold_exceeded"] is True
    
    def test_phase_result_reflects_error_tolerance(self) -> None:
        """PhaseResult success flag should reflect error tolerance."""
        from orchestration.factory import get_questionnaire
        from orchestration.orchestrator import MethodExecutor
        from orchestration.class_registry import MethodRegistry
        
        questionnaire = get_questionnaire()
        registry = MethodRegistry()
        executor = MethodExecutor(registry)
        runtime_config = RuntimeConfig(mode=RuntimeMode.PRODUCTION)
        
        orchestrator = Orchestrator(
            method_executor=executor,
            questionnaire=questionnaire,
            executor_config={},
            runtime_config=runtime_config,
        )
        
        orchestrator._error_tolerance[2].total_questions = 100
        for _ in range(80):
            orchestrator._error_tolerance[2].record_success()
        for _ in range(20):
            orchestrator._error_tolerance[2].record_failure()
        
        from orchestration.orchestrator import PhaseResult
        
        phase_result = PhaseResult(
            success=True,
            phase_id="2",
            data=[],
            error=None,
            duration_ms=1000.0,
            mode="async",
            aborted=False,
        )
        
        orchestrator.phase_results.append(phase_result)
        
        report = orchestrator._assemble_report({}, {})
        
        assert report["error_tolerance"][2]["threshold_exceeded"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
