"""Unit tests for ResourceLimits enforcement.

Tests the decision logic, budget adaptation, and circuit breaker behavior
for resource limit management in the orchestrator.
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Add src to path for imports

from farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller import ResourceLimits


class TestResourceLimitsDecisionLogic:
    """Test ResourceLimits check methods and decision logic."""
    
    def test_check_memory_exceeded_when_under_limit(self) -> None:
        """Test memory check returns False when under limit."""
        limits = ResourceLimits(max_memory_mb=4096.0, max_cpu_percent=85.0)
        
        usage = {"rss_mb": 2048.0, "cpu_percent": 50.0}
        exceeded, returned_usage = limits.check_memory_exceeded(usage)
        
        assert not exceeded
        assert returned_usage["rss_mb"] == 2048.0
    
    def test_check_memory_exceeded_when_over_limit(self) -> None:
        """Test memory check returns True when over limit."""
        limits = ResourceLimits(max_memory_mb=4096.0, max_cpu_percent=85.0)
        
        usage = {"rss_mb": 5000.0, "cpu_percent": 50.0}
        exceeded, returned_usage = limits.check_memory_exceeded(usage)
        
        assert exceeded
        assert returned_usage["rss_mb"] == 5000.0
    
    def test_check_memory_exceeded_no_limit_set(self) -> None:
        """Test memory check returns False when no limit set."""
        limits = ResourceLimits(max_memory_mb=None, max_cpu_percent=85.0)
        
        usage = {"rss_mb": 10000.0, "cpu_percent": 50.0}
        exceeded, returned_usage = limits.check_memory_exceeded(usage)
        
        assert not exceeded
    
    def test_check_cpu_exceeded_when_under_limit(self) -> None:
        """Test CPU check returns False when under limit."""
        limits = ResourceLimits(max_memory_mb=4096.0, max_cpu_percent=85.0)
        
        usage = {"rss_mb": 2048.0, "cpu_percent": 70.0}
        exceeded, returned_usage = limits.check_cpu_exceeded(usage)
        
        assert not exceeded
        assert returned_usage["cpu_percent"] == 70.0
    
    def test_check_cpu_exceeded_when_over_limit(self) -> None:
        """Test CPU check returns True when over limit."""
        limits = ResourceLimits(max_memory_mb=4096.0, max_cpu_percent=85.0)
        
        usage = {"rss_mb": 2048.0, "cpu_percent": 90.0}
        exceeded, returned_usage = limits.check_cpu_exceeded(usage)
        
        assert exceeded
        assert returned_usage["cpu_percent"] == 90.0
    
    def test_check_cpu_exceeded_no_limit_set(self) -> None:
        """Test CPU check returns False when no limit set."""
        limits = ResourceLimits(max_memory_mb=4096.0, max_cpu_percent=0)
        
        usage = {"rss_mb": 2048.0, "cpu_percent": 100.0}
        exceeded, returned_usage = limits.check_cpu_exceeded(usage)
        
        assert not exceeded


class TestResourceLimitsBudgetAdaptation:
    """Test worker budget adaptation logic."""
    
    @pytest.mark.asyncio
    async def test_apply_worker_budget_initial_state(self) -> None:
        """Test worker budget returns max_workers initially."""
        limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        semaphore = asyncio.Semaphore(32)
        limits.attach_semaphore(semaphore)
        
        budget = await limits.apply_worker_budget()
        
        assert budget == 32
    
    @pytest.mark.asyncio
    async def test_apply_worker_budget_reduces_on_high_load(self) -> None:
        """Test worker budget reduces when CPU/memory high."""
        limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        semaphore = asyncio.Semaphore(32)
        limits.attach_semaphore(semaphore)
        
        # Simulate high load
        for _ in range(5):
            usage = {"rss_mb": 4000.0, "cpu_percent": 92.0, "memory_percent": 95.0}
            limits._record_usage(usage)
        
        budget = await limits.apply_worker_budget()
        
        # Budget should be reduced
        assert budget < 32
        assert budget >= limits.min_workers
    
    @pytest.mark.asyncio
    async def test_apply_worker_budget_increases_on_low_load(self) -> None:
        """Test worker budget increases when CPU/memory low."""
        limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4,
            hard_max_workers=64
        )
        
        # Start with reduced budget
        limits._max_workers = 20
        
        semaphore = asyncio.Semaphore(20)
        limits.attach_semaphore(semaphore)
        
        # Simulate low load
        for _ in range(5):
            usage = {"rss_mb": 1000.0, "cpu_percent": 40.0, "memory_percent": 50.0}
            limits._record_usage(usage)
        
        budget = await limits.apply_worker_budget()
        
        # Budget should increase
        assert budget > 20
        assert budget <= limits.hard_max_workers
    
    @pytest.mark.asyncio
    async def test_apply_worker_budget_respects_min_workers(self) -> None:
        """Test worker budget never goes below min_workers."""
        limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        semaphore = asyncio.Semaphore(32)
        limits.attach_semaphore(semaphore)
        
        # Simulate extreme load
        for _ in range(10):
            usage = {"rss_mb": 5000.0, "cpu_percent": 99.0, "memory_percent": 99.0}
            limits._record_usage(usage)
        
        budget = await limits.apply_worker_budget()
        
        assert budget >= limits.min_workers
    
    @pytest.mark.asyncio
    async def test_apply_worker_budget_respects_hard_max(self) -> None:
        """Test worker budget never exceeds hard_max_workers."""
        limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4,
            hard_max_workers=48
        )
        
        semaphore = asyncio.Semaphore(32)
        limits.attach_semaphore(semaphore)
        
        # Simulate very low load
        for _ in range(10):
            usage = {"rss_mb": 100.0, "cpu_percent": 5.0, "memory_percent": 10.0}
            limits._record_usage(usage)
        
        budget = await limits.apply_worker_budget()
        
        assert budget <= limits.hard_max_workers


class TestResourceLimitsUsageHistory:
    """Test usage history tracking."""
    
    def test_get_usage_history_empty(self) -> None:
        """Test usage history starts empty."""
        limits = ResourceLimits(max_memory_mb=4096.0, max_cpu_percent=85.0)
        
        history = limits.get_usage_history()
        
        assert len(history) == 0
    
    def test_get_usage_history_after_checks(self) -> None:
        """Test usage history accumulates after checks."""
        limits = ResourceLimits(max_memory_mb=4096.0, max_cpu_percent=85.0, history=10)
        
        for i in range(5):
            limits.get_resource_usage()
        
        history = limits.get_usage_history()
        
        assert len(history) == 5
        assert all("cpu_percent" in entry for entry in history)
        assert all("rss_mb" in entry for entry in history)
    
    def test_usage_history_respects_maxlen(self) -> None:
        """Test usage history respects maximum length."""
        limits = ResourceLimits(max_memory_mb=4096.0, max_cpu_percent=85.0, history=5)
        
        for i in range(10):
            limits.get_resource_usage()
        
        history = limits.get_usage_history()
        
        assert len(history) == 5


@pytest.mark.updated
class TestResourceLimitsIntegration:
    """Integration tests for resource limits."""
    
    @pytest.mark.asyncio
    async def test_full_workflow_under_limits(self) -> None:
        """Test full workflow when resources stay under limits."""
        limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        semaphore = asyncio.Semaphore(32)
        limits.attach_semaphore(semaphore)
        
        # Simulate normal operation
        for _ in range(3):
            exceeded_mem, usage = limits.check_memory_exceeded()
            exceeded_cpu, usage = limits.check_cpu_exceeded(usage)
            
            assert not exceeded_mem
            assert not exceeded_cpu
            
            budget = await limits.apply_worker_budget()
            assert budget >= limits.min_workers
    
    @pytest.mark.asyncio
    async def test_full_workflow_exceeding_limits(self) -> None:
        """Test full workflow when resources exceed limits."""
        limits = ResourceLimits(
            max_memory_mb=4096.0,
            max_cpu_percent=85.0,
            max_workers=32,
            min_workers=4
        )
        
        semaphore = asyncio.Semaphore(32)
        limits.attach_semaphore(semaphore)
        
        # Simulate exceeding limits
        for _ in range(5):
            usage = {"rss_mb": 5000.0, "cpu_percent": 92.0, "memory_percent": 95.0}
            limits._record_usage(usage)
        
        exceeded_mem, usage = limits.check_memory_exceeded()
        exceeded_cpu, usage = limits.check_cpu_exceeded(usage)
        
        # Should detect violations
        assert exceeded_mem or exceeded_cpu
        
        # Budget should reduce
        old_budget = limits.max_workers
        new_budget = await limits.apply_worker_budget()
        assert new_budget < old_budget or new_budget == limits.min_workers
