"""
Unit tests for SOTA Performance Primitives.

Tests the three surgical optimizations:
1. Lazy evaluation with memoization chain
2. Vectorized coherence analysis
3. Content-hash-based caching
"""



def test_lazy_property():
    """Test lazy property decorator."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import lazy_property
    
    class TestClass:
        def __init__(self):
            self.call_count = 0
        
        @lazy_property
        def expensive_computation(self):
            self.call_count += 1
            return sum(range(1000))
    
    obj = TestClass()
    assert obj.call_count == 0
    
    # First access computes
    result1 = obj.expensive_computation
    assert obj.call_count == 1
    assert result1 == 499500
    
    # Second access uses cache
    result2 = obj.expensive_computation
    assert obj.call_count == 1  # Still 1, not recomputed
    assert result2 == result1


def test_vectorized_coherence_analyzer():
    """Test vectorized coherence analyzer."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import VectorizedCoherenceAnalyzer
    
    analyzer = VectorizedCoherenceAnalyzer()
    
    # Test variance coherence
    scores = [2.5, 2.3, 2.1, 2.4]
    coherence = analyzer.compute_variance_coherence(scores)
    assert 0.0 <= coherence <= 1.0
    
    # Test pairwise coherence
    pairwise = analyzer.compute_pairwise_coherence(scores, max_diff=3.0)
    assert 0.0 <= pairwise <= 1.0
    
    # Test alignment metrics
    score_map = {
        "CLUSTER_MESO_1": 2.5,
        "CLUSTER_MESO_2": 2.3,
        "CLUSTER_MESO_3": 2.1,
        "CLUSTER_MESO_4": 2.4,
    }
    alignment = analyzer.compute_alignment_metrics(score_map)
    assert "vertical_alignment" in alignment
    assert "horizontal_alignment" in alignment
    assert "temporal_alignment" in alignment
    assert all(0.0 <= v <= 1.0 for v in alignment.values())


def test_vectorized_vs_fallback():
    """Test that vectorized and fallback implementations give same results."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import VectorizedCoherenceAnalyzer
    
    scores = [2.5, 2.3, 2.1, 2.4]
    
    # Vectorized (with NumPy if available)
    analyzer_vec = VectorizedCoherenceAnalyzer(use_numpy=True)
    vec_result = analyzer_vec.compute_pairwise_coherence(scores)
    
    # Fallback (pure Python)
    analyzer_fallback = VectorizedCoherenceAnalyzer(use_numpy=False)
    fallback_result = analyzer_fallback.compute_pairwise_coherence(scores)
    
    # Results should be nearly identical
    assert abs(vec_result - fallback_result) < 1e-6


def test_content_hash_cache():
    """Test content-hash-based caching."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import ContentHashCache
    
    cache = ContentHashCache(maxsize=10)
    
    # Test cache miss
    hit, value = cache.get({"key": "value1"})
    assert hit is False
    assert value is None
    
    # Store value
    cache.put({"key": "value1"}, "result1")
    
    # Test cache hit
    hit, value = cache.get({"key": "value1"})
    assert hit is True
    assert value == "result1"
    
    # Test cache stats
    stats = cache.stats
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 0.5


def test_content_hash_cache_decorator():
    """Test content-hash-based caching decorator."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import content_hash_cache
    
    call_count = {"value": 0}
    
    @content_hash_cache
    def expensive_function(x, y):
        call_count["value"] += 1
        return x + y
    
    # First call computes
    result1 = expensive_function(1, 2)
    assert result1 == 3
    assert call_count["value"] == 1
    
    # Second call with same args uses cache
    result2 = expensive_function(1, 2)
    assert result2 == 3
    assert call_count["value"] == 1  # Not recomputed
    
    # Different args computes again
    result3 = expensive_function(2, 3)
    assert result3 == 5
    assert call_count["value"] == 2


def test_content_hash_consistency():
    """Test that content hash is consistent for equivalent objects."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import ContentHashCache
    
    cache = ContentHashCache()
    
    # Same content, different object instances
    obj1 = {"a": 1, "b": 2, "c": [3, 4, 5]}
    obj2 = {"a": 1, "b": 2, "c": [3, 4, 5]}
    obj3 = {"c": [3, 4, 5], "a": 1, "b": 2}  # Different order, same content
    
    # All should have same hash
    hash1 = cache._compute_hash(obj1)
    hash2 = cache._compute_hash(obj2)
    hash3 = cache._compute_hash(obj3)
    
    assert hash1 == hash2 == hash3


def test_cache_lru_eviction():
    """Test that cache evicts oldest entries when full."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import ContentHashCache
    
    cache = ContentHashCache(maxsize=3)
    
    # Fill cache
    cache.put({"key": 1}, "value1")
    cache.put({"key": 2}, "value2")
    cache.put({"key": 3}, "value3")
    
    assert cache.stats["size"] == 3
    
    # Add one more - should evict oldest
    cache.put({"key": 4}, "value4")
    
    assert cache.stats["size"] == 3
    
    # First entry should be gone
    hit, _ = cache.get({"key": 1})
    assert hit is False
    
    # Last entry should be present
    hit, value = cache.get({"key": 4})
    assert hit is True
    assert value == "value4"


def test_integrated_performance_gains():
    """Integration test: verify SOTA optimizations work together."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import (
        VectorizedCoherenceAnalyzer,
        content_hash_cache,
        get_cache_stats,
        clear_all_caches,
    )
    
    # Clear caches before test
    clear_all_caches()
    
    analyzer = VectorizedCoherenceAnalyzer()
    
    @content_hash_cache
    def compute_metrics(scores):
        return {
            "variance": analyzer.compute_variance_coherence(scores),
            "pairwise": analyzer.compute_pairwise_coherence(scores),
        }
    
    scores = [2.5, 2.3, 2.1, 2.4]
    
    # First call
    result1 = compute_metrics(scores)
    
    # Second call with same input (should use cache)
    result2 = compute_metrics(scores)
    
    assert result1 == result2
    
    # Check cache was used
    stats = get_cache_stats()
    assert stats["hits"] >= 1


def test_numpy_availability_fallback():
    """Test graceful fallback when NumPy is not available."""
    from farfan_pipeline.phases.Phase_7.primitives.performance_primitives import VectorizedCoherenceAnalyzer
    
    # Force fallback mode
    analyzer = VectorizedCoherenceAnalyzer(use_numpy=False)
    
    scores = [2.5, 2.3, 2.1, 2.4]
    
    # Should work without NumPy
    coherence = analyzer.compute_variance_coherence(scores)
    assert 0.0 <= coherence <= 1.0
    
    pairwise = analyzer.compute_pairwise_coherence(scores)
    assert 0.0 <= pairwise <= 1.0
