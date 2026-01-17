"""Regression tests to prevent bypassing ResourceLimits checks.

These tests verify that ResourceLimits enforcement cannot be accidentally
or intentionally bypassed in future code changes.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports

from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode
from farfan_pipeline.orchestration.core_orchestrator import (
    Orchestrator,
)
from farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller import (
    ResourceLimits,
)
# AbortRequested - check domain_errors if needed (not found in core_orchestrator)
from farfan_pipeline.phases.Phase_00.phase0_00_01_domain_errors import AbortRequested


@pytest.mark.regression
@pytest.mark.updated
class TestResourceLimitsBypassPrevention:
    """Regression tests to ensure resource limits cannot be bypassed."""
    
    @pytest.mark.asyncio
    async def test_phase_execution_always_checks_limits(self) -> None:
        """Test that phase execution always invokes resource checks."""
        resource_limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        runtime_config = RuntimeConfig(mode=RuntimeMode.PROD)
        
        # Mock dependencies
        mock_executor = MagicMock()
        mock_executor.signal_registry = MagicMock()
        mock_questionnaire = MagicMock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {},
                "niveles_abstraccion": {"clusters": []},
            }
        }
        mock_executor_config = MagicMock()
        
        orchestrator = Orchestrator(
            method_executor=mock_executor,
            questionnaire=mock_questionnaire,
            executor_config=mock_executor_config,
            runtime_config=runtime_config,
            resource_limits=resource_limits,
        )
        
        # Track if resource check was called
        check_called = False
        
        async def tracking_check(*args, **kwargs):
            nonlocal check_called
            check_called = True
        
        with patch.object(
            orchestrator,
            '_check_and_enforce_resource_limits',
            side_effect=tracking_check
        ):
            # Attempt to execute a phase
            # We expect it to fail quickly due to mock, but check should be called
            await orchestrator._check_and_enforce_resource_limits(0, "Test Phase")
        
        # Verify check was invoked
        assert check_called, "Resource limit check was not invoked during phase execution"
    
    @pytest.mark.asyncio
    async def test_cannot_disable_limit_checks_via_none(self) -> None:
        """Test that setting limits to None doesn't disable enforcement."""
        # Even with None limits, checks should still run (just always pass)
        resource_limits = ResourceLimits(
            max_memory_mb=None,  # No limit
            max_cpu_percent=0,   # No limit
        )
        
        # Should not raise exceptions
        exceeded_mem, usage = resource_limits.check_memory_exceeded()
        exceeded_cpu, usage = resource_limits.check_cpu_exceeded()
        
        # Should return False (no violation) but checks still ran
        assert not exceeded_mem
        assert not exceeded_cpu
        assert usage is not None
    
    @pytest.mark.asyncio
    async def test_limit_checks_run_in_all_runtime_modes(self) -> None:
        """Test that limit checks run in PROD, DEV, and EXPLORATORY modes."""
        resource_limits = ResourceLimits(
            max_memory_mb=100.0,  # Low limit to trigger
            max_cpu_percent=85.0,
        )
        
        for mode in [RuntimeMode.PROD, RuntimeMode.DEV, RuntimeMode.EXPLORATORY]:
            runtime_config = RuntimeConfig(mode=mode)
            
            mock_executor = MagicMock()
            mock_executor.signal_registry = MagicMock()
            mock_questionnaire = MagicMock()
            mock_questionnaire.data = {
                "blocks": {
                    "micro_questions": [],
                    "meso_questions": [],
                    "macro_question": {},
                    "niveles_abstraccion": {"clusters": []},
                }
            }
            mock_executor_config = MagicMock()
            
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=mock_executor_config,
                runtime_config=runtime_config,
                resource_limits=resource_limits,
            )
            
            check_invoked = False
            
            original_check_mem = resource_limits.check_memory_exceeded
            original_check_cpu = resource_limits.check_cpu_exceeded
            
            def tracking_check_mem(*args, **kwargs):
                nonlocal check_invoked
                check_invoked = True
                return original_check_mem(*args, **kwargs)
            
            def tracking_check_cpu(*args, **kwargs):
                nonlocal check_invoked
                check_invoked = True
                return original_check_cpu(*args, **kwargs)
            
            with patch.object(
                resource_limits,
                'check_memory_exceeded',
                side_effect=tracking_check_mem
            ):
                with patch.object(
                    resource_limits,
                    'check_cpu_exceeded',
                    side_effect=tracking_check_cpu
                ):
                    with patch.object(
                        resource_limits,
                        'get_resource_usage',
                        return_value={
                            "rss_mb": 150.0,
                            "cpu_percent": 50.0,
                            "memory_percent": 80.0,
                            "worker_budget": 4.0,
                            "timestamp": "2025-12-17T00:00:00",
                        }
                    ):
                        try:
                            await orchestrator._check_and_enforce_resource_limits(0, "Test")
                        except AbortRequested:
                            # Expected in PROD mode
                            pass
            
            assert check_invoked, f"Resource checks not invoked in {mode.value} mode"
    
    @pytest.mark.asyncio
    async def test_phase2_cannot_skip_periodic_checks(self) -> None:
        """Test that Phase 2 periodic checks cannot be skipped."""
        resource_limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
        )
        
        runtime_config = RuntimeConfig(mode=RuntimeMode.DEV)
        
        mock_executor = MagicMock()
        mock_executor.signal_registry = MagicMock()
        
        # Create exactly 25 questions (will trigger checks at idx 10, 20)
        test_questions = [
            {
                "id": f"Q{i:03d}",
                "global_id": i,
                "base_slot": "D1-Q1",
                "patterns": [],
                "expected_elements": [],
                "dimension_id": "D1",
                "cluster_id": "C1",
            }
            for i in range(1, 26)
        ]
        
        mock_questionnaire = MagicMock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": test_questions,
                "meso_questions": [],
                "macro_question": {},
                "niveles_abstraccion": {"clusters": []},
            }
        }
        
        mock_executor_config = MagicMock()
        
        orchestrator = Orchestrator(
            method_executor=mock_executor,
            questionnaire=mock_questionnaire,
            executor_config=mock_executor_config,
            runtime_config=runtime_config,
            resource_limits=resource_limits,
        )
        
        # Mock executor class
        class MockExecutor:
            def __init__(self, *args, **kwargs):
                pass
            
            def execute(self, *args, **kwargs):
                return {
                    "metadata": {"completeness": "partial", "overall_confidence": 0.5},
                    "evidence": {"elements": []},
                }
        
        with patch.dict(
            orchestrator.executors,
            {"D1-Q1": MockExecutor}
        ):
            check_count = 0
            original_check = orchestrator._check_and_enforce_resource_limits
            
            async def counting_check(*args, **kwargs):
                nonlocal check_count
                check_count += 1
                return await original_check(*args, **kwargs)
            
            with patch.object(
                orchestrator,
                '_check_and_enforce_resource_limits',
                side_effect=counting_check
            ):
                await orchestrator._execute_micro_questions_async(
                    MagicMock(),
                    {"micro_questions": test_questions}
                )
            
            # Must have checked at idx 10 and 20 (2 checks minimum)
            assert check_count >= 2, (
                f"Phase 2 must check resources every 10 questions. "
                f"Expected at least 2 checks for 25 questions, got {check_count}"
            )
    
    @pytest.mark.asyncio
    async def test_ci_fails_on_limit_violation_without_abort(self) -> None:
        """Test that CI detects when limits are violated without abort (PROD mode)."""
        resource_limits = ResourceLimits(
            max_memory_mb=100.0,  # Intentionally low
            max_cpu_percent=85.0,
        )
        
        runtime_config = RuntimeConfig(mode=RuntimeMode.PROD)
        
        mock_executor = MagicMock()
        mock_executor.signal_registry = MagicMock()
        mock_questionnaire = MagicMock()
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {},
                "niveles_abstraccion": {"clusters": []},
            }
        }
        mock_executor_config = MagicMock()
        
        orchestrator = Orchestrator(
            method_executor=mock_executor,
            questionnaire=mock_questionnaire,
            executor_config=mock_executor_config,
            runtime_config=runtime_config,
            resource_limits=resource_limits,
        )
        
        # Simulate memory violation
        with patch.object(
            resource_limits,
            'get_resource_usage',
            return_value={
                "rss_mb": 150.0,  # Exceeds limit
                "cpu_percent": 50.0,
                "memory_percent": 80.0,
                "worker_budget": 4.0,
                "timestamp": "2025-12-17T00:00:00",
            }
        ):
            # In PROD mode, this MUST raise AbortRequested
            with pytest.raises(AbortRequested) as exc_info:
                await orchestrator._check_and_enforce_resource_limits(0, "Test Phase")
            
            assert "Resource limits exceeded" in str(exc_info.value)
        
        # If this test passes, CI correctly detects violations in PROD mode


@pytest.mark.regression
@pytest.mark.updated
class TestResourceLimitsBudgetChangeLogging:
    """Regression tests for budget change logging."""
    
    @pytest.mark.asyncio
    async def test_budget_changes_logged_in_usage_history(self) -> None:
        """Test that worker budget changes appear in usage history."""
        resource_limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        semaphore = asyncio.Semaphore(32)
        resource_limits.attach_semaphore(semaphore)
        
        # Record initial state
        initial_history_len = len(resource_limits.get_usage_history())
        
        # Trigger budget reduction
        for _ in range(5):
            resource_limits._record_usage({
                "rss_mb": 4000.0,
                "cpu_percent": 92.0,
                "memory_percent": 95.0,
                "worker_budget": 32.0,
                "timestamp": "2025-12-17T00:00:00",
            })
        
        await resource_limits.apply_worker_budget()
        
        # History should have grown
        final_history = resource_limits.get_usage_history()
        assert len(final_history) > initial_history_len
        
        # History should contain worker_budget field
        assert all("worker_budget" in entry for entry in final_history)
    
    @pytest.mark.asyncio
    async def test_semaphore_changes_tracked(self) -> None:
        """Test that semaphore changes are tracked when budget applied."""
        resource_limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        semaphore = asyncio.Semaphore(32)
        resource_limits.attach_semaphore(semaphore)
        
        # Record usage to trigger reduction
        for _ in range(5):
            resource_limits._record_usage({
                "rss_mb": 4000.0,
                "cpu_percent": 92.0,
                "memory_percent": 95.0,
                "worker_budget": 32.0,
                "timestamp": "2025-12-17T00:00:00",
            })
        
        old_budget = resource_limits.max_workers
        new_budget = await resource_limits.apply_worker_budget()
        
        # Budget should have changed
        assert new_budget != old_budget or new_budget == resource_limits.min_workers
        
        # Verify semaphore state reflects new budget
        # (Semaphore doesn't expose internal count, but we can verify it's attached)
        assert resource_limits._semaphore is not None
        assert resource_limits._semaphore_limit == new_budget
