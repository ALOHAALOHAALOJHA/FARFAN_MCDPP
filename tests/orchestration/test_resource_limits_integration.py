"""Integration test for ResourceLimits enforcement under stress.

Tests that the orchestrator properly enforces resource limits during
execution, including circuit breaker behavior and budget adaptation.
"""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode
from orchestration.orchestrator import (
    AbortRequested,
    Orchestrator,
    ResourceLimits,
)


class SimulatedStressExecutor:
    """Executor that simulates high resource usage."""
    
    def __init__(self, *args, **kwargs):
        self.call_count = 0
    
    def execute(self, *args, **kwargs):
        """Simulate execution with increasing memory pressure."""
        self.call_count += 1
        return {
            "metadata": {"completeness": "partial", "overall_confidence": 0.5},
            "evidence": {"elements": []},
        }


@pytest.mark.integration
@pytest.mark.updated
class TestResourceLimitsStressIntegration:
    """Integration tests for resource limits under simulated stress."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_enforces_limits_in_prod_mode(self) -> None:
        """Test orchestrator aborts in PROD mode when limits exceeded."""
        # Create orchestrator with tight limits
        resource_limits = ResourceLimits(
            max_memory_mb=100.0,  # Very low limit to trigger violation
            max_cpu_percent=85.0,
            max_workers=4,
            min_workers=1
        )
        
        runtime_config = RuntimeConfig(mode=RuntimeMode.PROD)
        
        # Mock dependencies
        mock_executor = MagicMock()
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
        
        # Simulate high memory usage
        with patch.object(
            resource_limits,
            'get_resource_usage',
            return_value={
                "rss_mb": 150.0,  # Exceeds 100MB limit
                "cpu_percent": 50.0,
                "memory_percent": 80.0,
                "worker_budget": 4.0,
                "timestamp": "2025-12-17T00:00:00",
            }
        ):
            # Should raise AbortRequested in PROD mode
            with pytest.raises(AbortRequested) as exc_info:
                await orchestrator._check_and_enforce_resource_limits(0, "Test Phase")
            
            assert "Resource limits exceeded" in str(exc_info.value)
            assert "memory" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_orchestrator_throttles_in_dev_mode(self) -> None:
        """Test orchestrator throttles but continues in DEV mode when limits exceeded."""
        # Create orchestrator with tight limits
        resource_limits = ResourceLimits(
            max_memory_mb=100.0,
            max_cpu_percent=85.0,
            max_workers=4,
            min_workers=1
        )
        
        runtime_config = RuntimeConfig(mode=RuntimeMode.DEV)
        
        # Mock dependencies
        mock_executor = MagicMock()
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
        
        # Simulate high memory usage
        with patch.object(
            resource_limits,
            'get_resource_usage',
            return_value={
                "rss_mb": 150.0,  # Exceeds 100MB limit
                "cpu_percent": 50.0,
                "memory_percent": 80.0,
                "worker_budget": 4.0,
                "timestamp": "2025-12-17T00:00:00",
            }
        ):
            # Should NOT raise in DEV mode - just throttle
            await orchestrator._check_and_enforce_resource_limits(0, "Test Phase")
            
            # Orchestrator should not be aborted
            assert not orchestrator.abort_signal.is_aborted()
    
    @pytest.mark.asyncio
    async def test_budget_reduction_logged(self) -> None:
        """Test worker budget reduction is logged when limits exceeded."""
        resource_limits = ResourceLimits(
            max_memory_mb=100.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        runtime_config = RuntimeConfig(mode=RuntimeMode.DEV)
        
        # Mock dependencies
        mock_executor = MagicMock()
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
        
        # Attach semaphore for budget tracking
        semaphore = asyncio.Semaphore(32)
        resource_limits.attach_semaphore(semaphore)
        
        # Record high usage to trigger budget reduction
        for _ in range(5):
            resource_limits._record_usage({
                "rss_mb": 150.0,
                "cpu_percent": 92.0,
                "memory_percent": 95.0,
                "worker_budget": 32.0,
                "timestamp": "2025-12-17T00:00:00",
            })
        
        old_budget = resource_limits.max_workers
        
        # Simulate exceeding limits
        with patch.object(
            resource_limits,
            'get_resource_usage',
            return_value={
                "rss_mb": 150.0,
                "cpu_percent": 92.0,
                "memory_percent": 95.0,
                "worker_budget": float(old_budget),
                "timestamp": "2025-12-17T00:00:00",
            }
        ):
            await orchestrator._check_and_enforce_resource_limits(0, "Test Phase")
        
        # Check that usage history was recorded
        history = resource_limits.get_usage_history()
        assert len(history) >= 5
    
    @pytest.mark.asyncio
    async def test_phase2_enforces_limits_during_execution(self) -> None:
        """Test Phase 2 enforces limits during long-running async loop."""
        resource_limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        runtime_config = RuntimeConfig(mode=RuntimeMode.DEV)
        
        # Mock dependencies
        mock_executor = MagicMock()
        mock_executor.signal_registry = MagicMock()
        
        mock_questionnaire = MagicMock()
        # Create 30 test questions (enough to trigger multiple checks)
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
            for i in range(1, 31)
        ]
        
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
        with patch.dict(
            orchestrator.executors,
            {"D1-Q1": SimulatedStressExecutor}
        ):
            # Create instrumentation for Phase 2
            from orchestration.orchestrator import PhaseInstrumentation
            instrumentation = PhaseInstrumentation(
                phase_id=2,
                name="FASE 2 - Micro Preguntas",
                items_total=30,
                resource_limits=resource_limits,
            )
            orchestrator._phase_instrumentation[2] = instrumentation
            
            # Mock document
            mock_document = MagicMock()
            
            # Execute Phase 2
            config = {
                "micro_questions": test_questions,
            }
            
            # Track number of resource checks
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
                results = await orchestrator._execute_micro_questions_async(
                    mock_document,
                    config
                )
            
            # Should have checked resources multiple times (every 10 questions)
            # 30 questions = checks at idx 10, 20
            assert check_count >= 2
            assert len(results) == 30


@pytest.mark.performance
@pytest.mark.updated
class TestResourceLimitsPerformance:
    """Performance tests for resource limit checks."""
    
    @pytest.mark.asyncio
    async def test_resource_checks_low_overhead(self) -> None:
        """Test resource checks have acceptable overhead."""
        import time
        
        resource_limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
        )
        
        # Measure time for 1000 checks
        start = time.perf_counter()
        for _ in range(1000):
            resource_limits.check_memory_exceeded()
            resource_limits.check_cpu_exceeded()
        duration = time.perf_counter() - start
        
        # Should complete in reasonable time (< 1 second for 1000 checks)
        assert duration < 1.0
        
        # Average per check should be negligible
        avg_per_check = duration / 1000
        assert avg_per_check < 0.001  # Less than 1ms per check
