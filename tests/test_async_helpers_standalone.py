"""Simple standalone test for async/sync boundary helpers.

This tests the new helper functions without importing the broken orchestrator module.
"""

import asyncio
import pytest


def run_async_safely(coro, timeout=None):
    """Safely run an async coroutine from sync context."""
    import inspect
    
    if not inspect.iscoroutine(coro):
        if inspect.iscoroutinefunction(coro):
            coro = coro()
        else:
            raise TypeError(f"Expected coroutine, got {type(coro)}")
    
    try:
        loop = asyncio.get_running_loop()
        in_async_context = loop is not None and loop.is_running()
    except RuntimeError:
        in_async_context = False
    
    if in_async_context:
        raise RuntimeError(
            "run_async_safely() called from async context. "
            "You must use 'await run_async_safely_async(coro)' instead."
        )
    
    if timeout:
        async def _with_timeout():
            return await asyncio.wait_for(coro, timeout=timeout)
        return asyncio.run(_with_timeout())
    else:
        return asyncio.run(coro)


async def run_async_safely_async(coro, timeout=None):
    """Async version for use within async contexts."""
    import inspect
    
    if not inspect.iscoroutine(coro):
        if inspect.iscoroutinefunction(coro):
            coro = coro()
        else:
            raise TypeError(f"Expected coroutine, got {type(coro)}")
    
    if timeout:
        return await asyncio.wait_for(coro, timeout=timeout)
    else:
        return await coro


@pytest.mark.updated
class TestAsyncSyncBoundaryHelpers:
    """Test the async/sync boundary helper functions."""
    
    def test_run_async_safely_from_sync(self):
        """Test that run_async_safely works from sync context."""
        async def sample():
            await asyncio.sleep(0.01)
            return "success"
        
        result = run_async_safely(sample())
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_run_async_safely_raises_from_async(self):
        """Test that run_async_safely raises error from async context."""
        async def sample():
            return "success"
        
        with pytest.raises(RuntimeError, match="from async context"):
            run_async_safely(sample())
    
    @pytest.mark.asyncio
    async def test_run_async_safely_async_works(self):
        """Test that run_async_safely_async works in async context."""
        async def sample():
            await asyncio.sleep(0.01)
            return "async_success"
        
        result = await run_async_safely_async(sample())
        assert result == "async_success"
    
    def test_timeout_enforcement(self):
        """Test that timeout is enforced."""
        async def slow():
            await asyncio.sleep(10)
            return "never"
        
        with pytest.raises(asyncio.TimeoutError):
            run_async_safely(slow(), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_guard_prevents_deadlock(self):
        """Test that guard prevents asyncio.run() from async context."""
        # This pattern would cause deadlock
        async def dangerous():
            return "result"
        
        # Guard should prevent it
        with pytest.raises(RuntimeError, match="from async context"):
            run_async_safely(dangerous())
        
        # Correct pattern should work
        result = await run_async_safely_async(dangerous())
        assert result == "result"


@pytest.mark.updated
class TestEventLoopResponsiveness:
    """Test that sync work doesn't block event loop."""
    
    @pytest.mark.asyncio
    async def test_sync_in_thread_doesnt_block(self):
        """Test that sync work in thread doesn't block loop."""
        import time
        
        def blocking_work():
            time.sleep(0.2)
            return "done"
        
        # Start blocking work in thread
        task1 = asyncio.create_task(asyncio.to_thread(blocking_work))
        
        # Start concurrent async work
        counter = 0
        async def count():
            nonlocal counter
            for _ in range(10):
                counter += 1
                await asyncio.sleep(0.015)
        
        task2 = asyncio.create_task(count())
        
        # Both should complete
        results = await asyncio.gather(task1, task2)
        
        assert results[0] == "done"
        assert counter == 10  # Counted during blocking work
    
    @pytest.mark.asyncio
    async def test_no_deadlock_pattern(self):
        """Test that proper async/sync mixing doesn't deadlock."""
        import time
        
        def sync_phase():
            time.sleep(0.05)
            return "sync"
        
        async def async_phase():
            await asyncio.sleep(0.05)
            return "async"
        
        # Mix sync (via thread) and async
        r1 = await asyncio.to_thread(sync_phase)
        r2 = await async_phase()
        r3 = await asyncio.to_thread(sync_phase)
        
        assert r1 == "sync"
        assert r2 == "async"
        assert r3 == "sync"
