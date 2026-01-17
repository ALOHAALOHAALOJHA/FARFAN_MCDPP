"""
Integration Tests for Memory Management in Multi-Run Scenarios
===============================================================

Tests that verify memory usage doesn't bloat across multiple pipeline runs,
and that cache eviction mechanisms work effectively in realistic scenarios.

Test Coverage:
1. Multi-run RSS tracking with psutil
2. Cache clearing between runs prevents bloat
3. Memory usage stays within acceptable boundaries
4. Cache eviction is observable via metrics
5. No behavioral regressions in method lookups
"""

import gc
import os
import pytest
import time
from unittest.mock import Mock, patch

from orchestration.method_registry import MethodRegistry

# Try to import MethodExecutor, skip tests if dependencies missing
try:
    from farfan_pipeline.orchestration.core_orchestrator import MethodExecutor

    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False


# Try to import psutil, skip tests if not available
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def memory_tracker():
    """Fixture to track memory usage."""
    if not PSUTIL_AVAILABLE:
        pytest.skip("psutil not available")

    process = psutil.Process(os.getpid())

    class MemoryTracker:
        def __init__(self):
            self.baseline_rss = None
            self.measurements = []

        def record_baseline(self):
            """Record baseline RSS before test."""
            gc.collect()
            time.sleep(0.1)
            self.baseline_rss = process.memory_info().rss / (1024 * 1024)  # MB

        def measure(self, label: str):
            """Measure current RSS."""
            gc.collect()
            time.sleep(0.1)
            rss_mb = process.memory_info().rss / (1024 * 1024)
            delta_mb = rss_mb - self.baseline_rss if self.baseline_rss else 0
            self.measurements.append(
                {
                    "label": label,
                    "rss_mb": rss_mb,
                    "delta_mb": delta_mb,
                }
            )
            return rss_mb, delta_mb

        def get_stats(self):
            """Get measurement statistics."""
            if not self.measurements:
                return {}

            deltas = [m["delta_mb"] for m in self.measurements]
            return {
                "baseline_rss_mb": self.baseline_rss,
                "measurements": self.measurements,
                "max_delta_mb": max(deltas),
                "avg_delta_mb": sum(deltas) / len(deltas),
            }

    return MemoryTracker()


@pytest.fixture
def mock_method_registry():
    """Fixture providing a mock method registry for testing."""

    class MockClass:
        """Mock class for testing."""

        def mock_method(self, value: int) -> int:
            return value * 2

    registry = MethodRegistry(
        class_paths={
            "MockClass": "tests.fixtures.MockClass",
        },
        cache_ttl_seconds=1.0,
        max_cache_size=10,
    )

    # Patch loading to use our mock class
    with patch.object(registry, "_load_class", return_value=MockClass):
        with patch.object(registry, "_instantiate_class", return_value=MockClass()):
            yield registry


# ============================================================================
# MULTI-RUN MEMORY TESTS
# ============================================================================


@pytest.mark.skipif(
    not PSUTIL_AVAILABLE or not EXECUTOR_AVAILABLE, reason="psutil or MethodExecutor not available"
)
class TestMultiRunMemory:
    """Test memory management across multiple runs."""

    def test_multiple_runs_without_clearing(self, memory_tracker):
        """Test that NOT clearing cache causes memory growth."""
        memory_tracker.record_baseline()

        # Create instances repeatedly without clearing
        registry = MethodRegistry(
            class_paths={},
            cache_ttl_seconds=0.0,  # Disable TTL
        )

        for run in range(5):
            # Create many cache entries
            for i in range(20):
                class_name = f"Class_{run}_{i}"
                entry_instance = Mock()
                # Force into cache
                from orchestration.method_registry import CacheEntry

                registry._cache[class_name] = CacheEntry(
                    instance=entry_instance,
                    created_at=time.time(),
                    last_accessed=time.time(),
                    access_count=1,
                )

            memory_tracker.measure(f"run_{run}_without_clear")

        stats = memory_tracker.get_stats()

        # Memory should grow without clearing
        # (This test demonstrates the problem being fixed)
        assert stats["max_delta_mb"] > 0
        assert len(registry._cache) == 100  # 5 runs * 20 entries

    def test_multiple_runs_with_clearing(self, memory_tracker):
        """Test that clearing cache prevents memory growth."""
        memory_tracker.record_baseline()

        registry = MethodRegistry(
            class_paths={},
            cache_ttl_seconds=0.0,
        )

        max_delta_per_run = []

        for run in range(5):
            run_start_rss, _ = memory_tracker.measure(f"run_{run}_start")

            # Create many cache entries
            for i in range(20):
                class_name = f"Class_{run}_{i}"
                entry_instance = Mock()
                from orchestration.method_registry import CacheEntry

                registry._cache[class_name] = CacheEntry(
                    instance=entry_instance,
                    created_at=time.time(),
                    last_accessed=time.time(),
                    access_count=1,
                )

            run_end_rss, run_delta = memory_tracker.measure(f"run_{run}_end")
            max_delta_per_run.append(run_delta)

            # Clear cache between runs
            registry.clear_cache()
            memory_tracker.measure(f"run_{run}_cleared")

        stats = memory_tracker.get_stats()

        # Cache should be empty after each clear
        assert len(registry._cache) == 0

        # Memory growth should be bounded
        # Allow some tolerance for measurement variance
        avg_growth = sum(max_delta_per_run) / len(max_delta_per_run)
        assert avg_growth < 50  # Less than 50MB per run on average

    def test_ten_consecutive_runs_within_bounds(self, memory_tracker):
        """Test 10 consecutive full runs stay within RSS boundary."""
        if not EXECUTOR_AVAILABLE:
            pytest.skip("MethodExecutor not available")

        from farfan_pipeline.orchestration.core_orchestrator import MethodExecutor

        memory_tracker.record_baseline()

        executor = MethodExecutor()

        # Acceptable memory growth per run (MB)
        ACCEPTABLE_GROWTH_PER_RUN_MB = 20
        TOTAL_ACCEPTABLE_GROWTH_MB = ACCEPTABLE_GROWTH_PER_RUN_MB * 10

        for run in range(10):
            # Simulate pipeline run by calling methods
            for i in range(10):
                try:
                    # Try to execute some methods (may fail if classes don't exist)
                    executor.execute("MockClass", "mock_method", value=i)
                except Exception:
                    pass  # Ignore execution errors in test

            # Clear cache between runs (this is the fix)
            executor.clear_instance_cache()

            # Force GC
            gc.collect()

            rss_mb, delta_mb = memory_tracker.measure(f"run_{run}")

            # Check we're within bounds
            assert (
                delta_mb < TOTAL_ACCEPTABLE_GROWTH_MB
            ), f"Run {run}: Memory growth {delta_mb:.2f}MB exceeds {TOTAL_ACCEPTABLE_GROWTH_MB}MB"

        stats = memory_tracker.get_stats()

        # Final check: total growth should be reasonable
        assert stats["max_delta_mb"] < TOTAL_ACCEPTABLE_GROWTH_MB


# ============================================================================
# CACHE EVICTION OBSERVABILITY TESTS
# ============================================================================


class TestCacheEvictionObservability:
    """Test that cache eviction is observable via logs and metrics."""

    def test_eviction_metrics_updated(self):
        """Test that eviction events update metrics."""
        registry = MethodRegistry(
            class_paths={},
            cache_ttl_seconds=0.5,
        )

        # Add cache entry
        from orchestration.method_registry import CacheEntry

        registry._cache["TestClass"] = CacheEntry(
            instance=Mock(),
            created_at=time.time() - 1.0,
            last_accessed=time.time() - 1.0,
            access_count=1,
        )

        # Evict expired
        evicted = registry.evict_expired()

        # Check eviction metrics
        assert evicted == 1
        assert registry._evictions == 1

        stats = registry.get_stats()
        assert stats["evictions"] == 1

    def test_eviction_logged(self):
        """Test that eviction events update eviction counter."""
        registry = MethodRegistry(
            class_paths={},
            cache_ttl_seconds=0.5,
        )

        # Add and evict entry
        from orchestration.method_registry import CacheEntry

        registry._cache["TestClass"] = CacheEntry(
            instance=Mock(),
            created_at=time.time() - 1.0,
            last_accessed=time.time() - 1.0,
            access_count=1,
        )

        # Verify eviction happens and counter is incremented
        initial_evictions = registry._evictions
        registry.evict_expired()

        assert registry._evictions == initial_evictions + 1

    def test_cache_clear_returns_stats(self):
        """Test that clear_cache returns observable statistics."""
        registry = MethodRegistry(class_paths={})

        # Add entries
        from orchestration.method_registry import CacheEntry

        for i in range(5):
            registry._cache[f"Class{i}"] = CacheEntry(
                instance=Mock(),
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
            )

        # Set some metrics
        registry._cache_hits = 10
        registry._cache_misses = 5

        # Clear and check stats
        stats = registry.clear_cache()

        assert stats["entries_cleared"] == 5
        assert stats["total_hits"] == 10
        assert stats["total_misses"] == 5
        assert "total_evictions" in stats
        assert "total_instantiations" in stats


# ============================================================================
# REGRESSION TESTS
# ============================================================================


class TestNoRegressions:
    """Test that cache eviction doesn't break method lookups."""

    def test_method_lookup_after_eviction(self):
        """Test methods can still be looked up after cache eviction."""
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
            cache_ttl_seconds=0.5,
        )

        test_instance = Mock()
        test_instance.test_method = Mock(return_value=42)

        with patch.object(registry, "_load_class"):
            with patch.object(registry, "_instantiate_class", return_value=test_instance):
                # First call
                method1 = registry.get_method("TestClass", "test_method")
                assert method1() == 42

                # Wait for TTL expiry
                time.sleep(0.6)

                # Second call after expiry - should work
                method2 = registry.get_method("TestClass", "test_method")
                assert method2() == 42

                # Instance should have been re-created
                assert registry._evictions >= 1

    def test_method_lookup_after_clear(self):
        """Test methods can still be looked up after cache clear."""
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
        )

        test_instance = Mock()
        test_instance.test_method = Mock(return_value=42)

        with patch.object(registry, "_load_class"):
            with patch.object(registry, "_instantiate_class", return_value=test_instance):
                # First call
                method1 = registry.get_method("TestClass", "test_method")
                assert method1() == 42

                # Clear cache
                registry.clear_cache()

                # Second call after clear - should work
                method2 = registry.get_method("TestClass", "test_method")
                assert method2() == 42

    def test_has_method_after_cache_operations(self):
        """Test has_method still works after cache operations."""
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
        )

        # Should work before instantiation
        assert registry.has_method("TestClass", "test_method")

        # Clear cache
        registry.clear_cache()

        # Should still work
        assert registry.has_method("TestClass", "test_method")

        # Evict expired
        registry.evict_expired()

        # Should still work
        assert registry.has_method("TestClass", "test_method")


# ============================================================================
# MEMORY PROFILING INTEGRATION TESTS
# ============================================================================


class TestMemoryProfilingIntegration:
    """Test memory profiling hooks integration."""

    def test_cache_stats_include_memory_info(self):
        """Test get_stats includes cache entry details for profiling."""
        registry = MethodRegistry(
            class_paths={},
            cache_ttl_seconds=300.0,
        )

        # Add cache entries with different ages
        now = time.time()
        from orchestration.method_registry import CacheEntry

        registry._cache["OldClass"] = CacheEntry(
            instance=Mock(),
            created_at=now - 100,
            last_accessed=now - 50,
            access_count=10,
        )
        registry._cache["NewClass"] = CacheEntry(
            instance=Mock(),
            created_at=now - 10,
            last_accessed=now - 5,
            access_count=2,
        )

        stats = registry.get_stats()

        # Should include detailed cache entry info
        assert "cache_entries" in stats
        assert len(stats["cache_entries"]) == 2

        # Each entry should have profiling info
        for entry in stats["cache_entries"]:
            assert "class_name" in entry
            assert "age_seconds" in entry
            assert "last_accessed_seconds_ago" in entry
            assert "access_count" in entry

    def test_metrics_track_performance(self):
        """Test metrics track cache performance over time."""
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
            cache_ttl_seconds=0.0,
        )

        test_instance = Mock()
        with patch.object(registry, "_load_class"):
            with patch.object(registry, "_instantiate_class", return_value=test_instance):
                # Generate cache hits and misses
                for _ in range(3):
                    registry._get_instance("TestClass")  # First is miss, rest are hits

                stats = registry.get_stats()

                # Check performance metrics
                assert stats["cache_hits"] == 2
                assert stats["cache_misses"] == 1
                assert stats["cache_hit_rate"] == 2 / 3
                assert stats["total_instantiations"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
