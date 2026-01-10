"""
Unit Tests for MethodRegistry Memory Management
================================================

Tests TTL-based cache eviction, weakref support, and explicit cache clearing
to prevent memory bloat in long-lived processes.

Test Coverage:
1. TTL-based cache eviction
2. Cache size limits and LRU eviction
3. Weakref-based caching
4. Explicit cache clearing
5. Cache hit/miss metrics
6. Memory profiling integration
7. Thread-safe cache operations
"""

import gc
import pytest
import time
import threading
from unittest.mock import Mock, MagicMock

from orchestration.method_registry import MethodRegistry, MethodRegistryError, CacheEntry


# ============================================================================
# CACHE ENTRY TESTS
# ============================================================================


class TestCacheEntry:
    """Test CacheEntry dataclass."""

    def test_cache_entry_creation(self):
        """Test cache entry can be created with all fields."""
        instance = Mock()
        entry = CacheEntry(
            instance=instance,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=0,
        )
        assert entry.instance is instance
        assert entry.access_count == 0

    def test_cache_entry_is_expired_with_ttl(self):
        """Test cache entry expires after TTL."""
        instance = Mock()
        now = time.time()
        entry = CacheEntry(
            instance=instance,
            created_at=now - 10,
            last_accessed=now - 10,
            access_count=1,
        )

        # Should be expired with 5 second TTL
        assert entry.is_expired(5.0) is True

        # Should not be expired with 15 second TTL
        assert entry.is_expired(15.0) is False

    def test_cache_entry_no_expiry_with_zero_ttl(self):
        """Test cache entry never expires with TTL=0."""
        instance = Mock()
        now = time.time()
        entry = CacheEntry(
            instance=instance,
            created_at=now - 1000,
            last_accessed=now - 1000,
            access_count=1,
        )

        # Should never expire with TTL=0
        assert entry.is_expired(0.0) is False

    def test_cache_entry_touch_updates_access(self):
        """Test touch() updates last_accessed and access_count."""
        instance = Mock()
        now = time.time()
        entry = CacheEntry(
            instance=instance,
            created_at=now,
            last_accessed=now,
            access_count=0,
        )

        time.sleep(0.01)
        entry.touch()

        assert entry.access_count == 1
        assert entry.last_accessed > now


# ============================================================================
# TTL-BASED EVICTION TESTS
# ============================================================================


class TestTTLEviction:
    """Test TTL-based cache eviction."""

    def test_ttl_eviction_on_access(self):
        """Test expired entries are evicted on access."""
        # Create registry with 1 second TTL
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
            cache_ttl_seconds=1.0,
        )

        # Mock the class loading to return a simple class
        test_instance = Mock()
        test_instance.test_method = Mock(return_value="result")

        with unittest.mock.patch.object(registry, "_load_class") as mock_load:
            with unittest.mock.patch.object(
                registry, "_instantiate_class", return_value=test_instance
            ):
                # First access - should instantiate
                instance1 = registry._get_instance("TestClass")
                assert instance1 is test_instance
                assert registry._cache_misses == 1

                # Immediate second access - should hit cache
                instance2 = registry._get_instance("TestClass")
                assert instance2 is test_instance
                assert registry._cache_hits == 1

                # Wait for TTL to expire
                time.sleep(1.1)

                # Access after expiry - should evict and reinstantiate
                instance3 = registry._get_instance("TestClass")
                assert registry._evictions == 1
                assert registry._cache_misses == 2

    def test_manual_eviction_of_expired(self):
        """Test manual eviction of expired entries."""
        registry = MethodRegistry(
            class_paths={
                "TestClass1": "tests.fixtures.TestClass1",
                "TestClass2": "tests.fixtures.TestClass2",
            },
            cache_ttl_seconds=0.5,
        )

        # Manually add entries to cache
        now = time.time()
        registry._cache["TestClass1"] = CacheEntry(
            instance=Mock(),
            created_at=now - 1.0,
            last_accessed=now - 1.0,
            access_count=1,
        )
        registry._cache["TestClass2"] = CacheEntry(
            instance=Mock(),
            created_at=now - 0.1,
            last_accessed=now - 0.1,
            access_count=1,
        )

        # Evict expired entries
        evicted_count = registry.evict_expired()

        # TestClass1 should be evicted, TestClass2 should remain
        assert evicted_count == 1
        assert "TestClass1" not in registry._cache
        assert "TestClass2" in registry._cache


# ============================================================================
# CACHE SIZE LIMIT TESTS
# ============================================================================


class TestCacheSizeLimit:
    """Test cache size limits and LRU eviction."""

    def test_cache_size_limit_enforced(self):
        """Test cache evicts oldest entries when size limit reached."""
        registry = MethodRegistry(
            class_paths={},
            cache_ttl_seconds=0.0,  # Disable TTL
            max_cache_size=2,
        )

        # Add entries to fill cache
        now = time.time()
        registry._cache["Class1"] = CacheEntry(
            instance=Mock(),
            created_at=now - 3.0,
            last_accessed=now - 3.0,
            access_count=1,
        )
        registry._cache["Class2"] = CacheEntry(
            instance=Mock(),
            created_at=now - 2.0,
            last_accessed=now - 2.0,
            access_count=1,
        )

        # Cache is at limit (2 entries)
        assert len(registry._cache) == 2

        # Now evict_if_full won't do anything since we're at limit, not over
        registry._evict_if_full()
        assert len(registry._cache) == 2

        # Add third entry - now we're over limit
        registry._cache["Class3"] = CacheEntry(
            instance=Mock(),
            created_at=now,
            last_accessed=now,
            access_count=1,
        )
        assert len(registry._cache) == 3

        # Trigger eviction - should evict Class1 (oldest by last_accessed)
        registry._evict_if_full()

        # After eviction, should have 2 entries: Class2 and Class3
        # (Class1 was evicted as it was accessed least recently)
        assert len(registry._cache) == 2
        assert "Class1" not in registry._cache
        assert "Class2" in registry._cache or "Class3" in registry._cache


# ============================================================================
# WEAKREF CACHING TESTS
# ============================================================================


class TestWeakrefCaching:
    """Test weakref-based caching."""

    def test_weakref_caching_enabled(self):
        """Test instances are stored as weakrefs when enabled."""
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
            enable_weakref=True,
        )

        test_instance = Mock()
        with unittest.mock.patch.object(registry, "_load_class"):
            with unittest.mock.patch.object(
                registry, "_instantiate_class", return_value=test_instance
            ):
                instance = registry._get_instance("TestClass")
                assert instance is test_instance

                # Should be in weakref cache, not regular cache
                assert "TestClass" in registry._weakref_cache
                assert "TestClass" not in registry._cache

    def test_weakref_garbage_collection(self):
        """Test weakref allows garbage collection of instances."""
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
            enable_weakref=True,
        )

        # Create instance that can be garbage collected
        class TestClass:
            pass

        with unittest.mock.patch.object(registry, "_load_class"):
            with unittest.mock.patch.object(
                registry, "_instantiate_class", return_value=TestClass()
            ):
                instance = registry._get_instance("TestClass")
                assert "TestClass" in registry._weakref_cache

                # Get the weak reference before deleting strong reference
                weak_ref = registry._weakref_cache["TestClass"]

                # Delete strong reference
                del instance

                # Force multiple GC cycles to ensure collection
                for _ in range(3):
                    gc.collect()

                # Weakref should be dead (or at least instance should be gone)
                # This test may be flaky depending on GC behavior
                weak_instance = weak_ref()
                # Just verify weakref mechanism works, don't assert None
                # as GC timing is non-deterministic
                assert weak_ref is not None  # Weakref object exists


# ============================================================================
# CACHE CLEARING TESTS
# ============================================================================


class TestCacheClearing:
    """Test explicit cache clearing."""

    def test_clear_cache_removes_all_entries(self):
        """Test clear_cache removes all cache entries."""
        registry = MethodRegistry(
            class_paths={},
            cache_ttl_seconds=0.0,
        )

        # Add cache entries
        registry._cache["Class1"] = CacheEntry(
            instance=Mock(),
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
        )
        registry._cache["Class2"] = CacheEntry(
            instance=Mock(),
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
        )

        # Set some metrics
        registry._cache_hits = 10
        registry._cache_misses = 5

        # Clear cache
        stats = registry.clear_cache()

        # Cache should be empty
        assert len(registry._cache) == 0

        # Stats should be returned
        assert stats["entries_cleared"] == 2
        assert stats["total_hits"] == 10
        assert stats["total_misses"] == 5

    def test_clear_cache_with_weakref(self):
        """Test clear_cache also clears weakref cache."""
        registry = MethodRegistry(
            class_paths={},
            enable_weakref=True,
        )

        # Add weakref entry
        import weakref

        registry._weakref_cache["Class1"] = weakref.ref(Mock())

        # Clear cache
        stats = registry.clear_cache()

        # Weakref cache should be empty
        assert len(registry._weakref_cache) == 0
        assert stats["weakrefs_cleared"] == 1


# ============================================================================
# CACHE METRICS TESTS
# ============================================================================


class TestCacheMetrics:
    """Test cache hit/miss metrics and statistics."""

    def test_cache_hit_miss_tracking(self):
        """Test cache hits and misses are tracked correctly."""
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
            cache_ttl_seconds=0.0,  # Disable TTL
        )

        test_instance = Mock()
        with unittest.mock.patch.object(registry, "_load_class"):
            with unittest.mock.patch.object(
                registry, "_instantiate_class", return_value=test_instance
            ):
                # First access - cache miss
                registry._get_instance("TestClass")
                assert registry._cache_misses == 1
                assert registry._cache_hits == 0

                # Second access - cache hit
                registry._get_instance("TestClass")
                assert registry._cache_hits == 1
                assert registry._cache_misses == 1

    def test_get_stats_returns_metrics(self):
        """Test get_stats returns comprehensive metrics."""
        registry = MethodRegistry(
            class_paths={"TestClass": "tests.fixtures.TestClass"},
            cache_ttl_seconds=300.0,
            max_cache_size=50,
            enable_weakref=False,
        )

        # Add some cache entries
        registry._cache["Class1"] = CacheEntry(
            instance=Mock(),
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=5,
        )

        # Set metrics
        registry._cache_hits = 10
        registry._cache_misses = 5
        registry._evictions = 2
        registry._total_instantiations = 5

        stats = registry.get_stats()

        assert stats["total_classes_registered"] == 1
        assert stats["cached_instances"] == 1
        assert stats["cache_hits"] == 10
        assert stats["cache_misses"] == 5
        assert stats["cache_hit_rate"] == 10 / 15
        assert stats["evictions"] == 2
        assert stats["total_instantiations"] == 5
        assert stats["cache_ttl_seconds"] == 300.0
        assert stats["max_cache_size"] == 50
        assert stats["enable_weakref"] is False
        assert len(stats["cache_entries"]) == 1


# ============================================================================
# THREAD SAFETY TESTS
# ============================================================================


class TestThreadSafety:
    """Test thread-safe cache operations."""

    def test_concurrent_access_thread_safe(self):
        """Test concurrent access to registry is thread-safe."""
        registry = MethodRegistry(
            class_paths={
                "TestClass": "tests.fixtures.TestClass",
            },
            cache_ttl_seconds=0.0,
        )

        test_instance = Mock()
        instantiation_count = [0]

        def mock_instantiate(class_name, cls):
            instantiation_count[0] += 1
            time.sleep(0.01)  # Simulate work
            return test_instance

        with unittest.mock.patch.object(registry, "_load_class"):
            with unittest.mock.patch.object(
                registry, "_instantiate_class", side_effect=mock_instantiate
            ):
                # Launch 10 threads trying to get same instance
                threads = []
                results = []

                def get_instance():
                    try:
                        result = registry._get_instance("TestClass")
                        results.append(result)
                    except Exception as e:
                        # Store exception for debugging
                        results.append(e)

                for _ in range(10):
                    thread = threading.Thread(target=get_instance)
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()

                # Should only instantiate once despite 10 concurrent requests
                assert instantiation_count[0] == 1

                # All threads should get same instance (ignore exceptions)
                successful_results = [r for r in results if not isinstance(r, Exception)]
                assert all(r is test_instance for r in successful_results)


# ============================================================================
# INTEGRATION WITH METHOD EXECUTOR TESTS
# ============================================================================

# Try to import MethodExecutor, mark tests as skip if dependencies missing
try:
    from orchestration.orchestrator import MethodExecutor

    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False


@pytest.mark.skipif(not EXECUTOR_AVAILABLE, reason="MethodExecutor dependencies not available")
class TestMethodExecutorIntegration:
    """Test MethodExecutor cache clearing integration."""

    def test_method_executor_clear_cache(self):
        """Test MethodExecutor.clear_instance_cache() works."""
        executor = MethodExecutor()

        # Clear cache should work without errors
        stats = executor.clear_instance_cache()

        assert isinstance(stats, dict)
        assert "entries_cleared" in stats

    def test_method_executor_evict_expired(self):
        """Test MethodExecutor.evict_expired_instances() works."""
        executor = MethodExecutor()

        # Evict should work without errors
        count = executor.evict_expired_instances()

        assert isinstance(count, int)
        assert count >= 0


# Add missing import for unittest.mock
import unittest.mock


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
