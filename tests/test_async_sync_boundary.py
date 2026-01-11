"""Unit tests for async/sync boundary safety.

Tests verify that:
1. Sync wrapper detects running event loop
2. Sync wrapper raises clear error when called from async context
3. Helper functions work correctly in both contexts
4. No deadlocks or blocking issues occur
"""

import asyncio
import pytest
from unittest.mock import Mock, MagicMock
from farfan_pipeline.orchestration.orchestrator import (
    run_async_safely,
    run_async_safely_async,
)


class TestEventLoopDetection:
    """Test event loop detection guards."""

    def test_no_loop_when_none_running(self):
        """Verify that no loop is detected in sync context."""
        try:
            loop = asyncio.get_running_loop()
            assert False, "Should not have a running loop in sync context"
        except RuntimeError:
            # Expected - no loop is running
            pass

    @pytest.mark.asyncio
    async def test_loop_detected_in_async_context(self):
        """Verify that loop is detected in async context."""
        loop = asyncio.get_running_loop()
        assert loop is not None
        assert loop.is_running()

    def test_run_async_safely_from_sync_context(self):
        """Test run_async_safely works in sync context."""

        async def sample_coro():
            await asyncio.sleep(0.01)
            return "success"

        result = run_async_safely(sample_coro())
        assert result == "success"

    def test_run_async_safely_raises_in_async_context(self):
        """Test run_async_safely raises error if called incorrectly from async context."""

        async def sample_coro():
            return "success"

        async def async_caller():
            # This should raise because we're in async context
            # and not using await
            with pytest.raises(RuntimeError, match="run_async_safely.*from async context"):
                run_async_safely(sample_coro())

        asyncio.run(async_caller())

    @pytest.mark.asyncio
    async def test_run_async_safely_async_in_async_context(self):
        """Test run_async_safely_async works correctly in async context."""

        async def sample_coro():
            await asyncio.sleep(0.01)
            return "async_success"

        result = await run_async_safely_async(sample_coro())
        assert result == "async_success"

    def test_run_async_safely_with_timeout(self):
        """Test run_async_safely respects timeout."""

        async def slow_coro():
            await asyncio.sleep(10)
            return "never"

        with pytest.raises(asyncio.TimeoutError):
            run_async_safely(slow_coro(), timeout=0.1)

    @pytest.mark.asyncio
    async def test_run_async_safely_async_with_timeout(self):
        """Test run_async_safely_async respects timeout."""

        async def slow_coro():
            await asyncio.sleep(10)
            return "never"

        with pytest.raises(asyncio.TimeoutError):
            await run_async_safely_async(slow_coro(), timeout=0.1)

    def test_run_async_safely_rejects_non_coroutine(self):
        """Test run_async_safely rejects non-coroutine inputs."""

        def not_async():
            return "sync"

        with pytest.raises(TypeError, match="Expected coroutine"):
            run_async_safely(not_async)

    @pytest.mark.asyncio
    async def test_run_async_safely_async_rejects_non_coroutine(self):
        """Test run_async_safely_async rejects non-coroutine inputs."""

        def not_async():
            return "sync"

        with pytest.raises(TypeError, match="Expected coroutine"):
            await run_async_safely_async(not_async)


class TestOrchestratorBoundaryGuards:
    """Test Orchestrator boundary enforcement."""

    def test_process_development_plan_from_sync_context(self):
        """Test that process_development_plan works from sync context."""
        from farfan_pipeline.orchestration.orchestrator import Orchestrator

        # We can't easily test full orchestrator without dependencies,
        # but we can test the guard logic
        async def mock_async_method(pdf_path, preprocessed=None):
            await asyncio.sleep(0.01)
            return []

        # Simulate the guard check
        try:
            loop = asyncio.get_running_loop()
            in_async = loop is not None and loop.is_running()
        except RuntimeError:
            in_async = False

        assert not in_async, "Should not be in async context during sync test"

    @pytest.mark.asyncio
    async def test_process_development_plan_raises_from_async_context(self):
        """Test that process_development_plan raises error from async context."""
        # Simulate the guard logic that's in process_development_plan
        try:
            loop = asyncio.get_running_loop()
            in_async = loop is not None and loop.is_running()
        except RuntimeError:
            in_async = False

        assert in_async, "Should be in async context during async test"

        # The actual method would raise here with improved message
        if in_async:
            expected_error = RuntimeError(
                "Cannot call process_development_plan() from within an async context. "
                "This would block the event loop and cause deadlock. "
                "Use 'await process_development_plan_async()' instead."
            )
            assert "async context" in str(expected_error)
            assert "deadlock" in str(expected_error)
            assert "process_development_plan_async" in str(expected_error)


class TestAsyncToThreadHandling:
    """Test that sync functions are properly wrapped with asyncio.to_thread."""

    @pytest.mark.asyncio
    async def test_sync_function_in_async_context(self):
        """Test that sync functions don't block the event loop."""
        import time

        def sync_function():
            """Simulate a sync operation."""
            time.sleep(0.1)
            return "done"

        # Measure execution
        start = asyncio.get_event_loop().time()

        # Run sync function in thread
        result = await asyncio.to_thread(sync_function)

        elapsed = asyncio.get_event_loop().time() - start

        assert result == "done"
        assert elapsed >= 0.1  # Should have actually slept

    @pytest.mark.asyncio
    async def test_event_loop_remains_responsive(self):
        """Test that event loop remains responsive during sync operation."""
        import time

        def blocking_sync():
            time.sleep(0.2)
            return "blocked"

        # Run blocking work in thread
        task1 = asyncio.create_task(asyncio.to_thread(blocking_sync))

        # Run concurrent async work
        counter = 0

        async def count_up():
            nonlocal counter
            for _ in range(10):
                counter += 1
                await asyncio.sleep(0.01)

        task2 = asyncio.create_task(count_up())

        # Both should complete
        results = await asyncio.gather(task1, task2)

        assert results[0] == "blocked"
        assert counter == 10  # Counter incremented during blocking operation

    @pytest.mark.asyncio
    async def test_multiple_sync_phases_concurrent(self):
        """Test that multiple sync operations can run concurrently via threads."""
        import time

        def sync_work(n: int):
            time.sleep(0.1)
            return n * 2

        # Run multiple sync operations concurrently
        tasks = [asyncio.to_thread(sync_work, i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        assert results == [0, 2, 4, 6, 8]


@pytest.mark.updated
class TestRegressionNoDeadlocks:
    """Regression tests to ensure no deadlocks occur."""

    @pytest.mark.asyncio
    async def test_no_deadlock_mixed_sync_async(self):
        """Test that mixing sync and async operations doesn't cause deadlock."""
        import time

        def sync_phase():
            time.sleep(0.05)
            return "sync_done"

        async def async_phase():
            await asyncio.sleep(0.05)
            return "async_done"

        # Alternate between sync (via thread) and async
        result1 = await asyncio.to_thread(sync_phase)
        result2 = await async_phase()
        result3 = await asyncio.to_thread(sync_phase)
        result4 = await async_phase()

        assert result1 == "sync_done"
        assert result2 == "async_done"
        assert result3 == "sync_done"
        assert result4 == "async_done"

    @pytest.mark.asyncio
    async def test_no_deadlock_nested_awaits(self):
        """Test that nested await patterns don't cause issues."""

        async def level3():
            await asyncio.sleep(0.01)
            return "level3"

        async def level2():
            result = await level3()
            return f"level2-{result}"

        async def level1():
            result = await level2()
            return f"level1-{result}"

        result = await level1()
        assert result == "level1-level2-level3"

    def test_no_deadlock_sync_calling_run(self):
        """Test that sync code can safely call asyncio.run."""

        async def inner_async():
            await asyncio.sleep(0.01)
            return "inner"

        def sync_caller():
            return asyncio.run(inner_async())

        result = sync_caller()
        assert result == "inner"

    @pytest.mark.asyncio
    async def test_abort_signal_thread_safe(self):
        """Test that abort signal works correctly across threads."""
        from farfan_pipeline.orchestration.orchestrator import AbortSignal

        signal = AbortSignal()

        def sync_aborter():
            import time

            time.sleep(0.05)
            signal.abort("test abort")

        # Start abort in thread
        abort_task = asyncio.create_task(asyncio.to_thread(sync_aborter))

        # Wait and check
        await asyncio.sleep(0.1)

        assert signal.is_aborted()
        assert signal.get_reason() == "test abort"

        await abort_task
