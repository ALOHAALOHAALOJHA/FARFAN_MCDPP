# MethodRegistry Cache Eviction Policy

## Overview

The MethodRegistry implements a sophisticated caching mechanism to prevent memory bloat in long-lived processes while maintaining optimal performance through instance reuse.

## Cache Eviction Strategies

### 1. TTL-Based Eviction

**Configuration**: `cache_ttl_seconds` parameter (default: 300 seconds)

Entries are automatically evicted after a configurable time-to-live (TTL) based on their last access time.

```python
registry = MethodRegistry(cache_ttl_seconds=300.0)  # 5 minutes
```

**Behavior**:
- Entries are checked for expiration on each access
- Expired entries are removed and metrics are updated
- Setting `cache_ttl_seconds=0.0` disables TTL-based eviction

**Use Case**: Prevents stale instances from accumulating in long-running services.

### 2. Size-Based LRU Eviction

**Configuration**: `max_cache_size` parameter (default: 100)

When cache size exceeds the maximum, oldest entries (by last access time) are evicted.

```python
registry = MethodRegistry(max_cache_size=50)  # Limit to 50 instances
```

**Behavior**:
- Eviction triggers when cache size exceeds `max_cache_size`
- Entries sorted by `last_accessed` timestamp
- Oldest entries evicted until size reaches `max_cache_size`

**Use Case**: Hard memory limits in resource-constrained environments.

### 3. Weakref-Based Eviction

**Configuration**: `enable_weakref` parameter (default: False)

Instances are stored as weak references, allowing Python's garbage collector to reclaim them when no strong references remain.

```python
registry = MethodRegistry(enable_weakref=True)
```

**Behavior**:
- Instances stored as `weakref.ref()` objects
- Automatic eviction when GC reclaims the instance
- No explicit TTL or size limit needed
- May cause more frequent instantiations

**Use Case**: Fine-grained automatic memory management, useful when instance lifecycle is well-defined.

### 4. Explicit Manual Eviction

**Methods**:
- `clear_cache()`: Remove all cached instances
- `evict_expired()`: Remove only expired entries

```python
# Between pipeline runs
stats = registry.clear_cache()

# Periodic cleanup
count = registry.evict_expired()
```

**Use Case**: Pipeline run boundaries, scheduled maintenance, testing.

## Cache Performance Metrics

The registry tracks comprehensive metrics for observability:

```python
stats = registry.get_stats()
```

**Metrics Include**:
- `cache_hits`: Number of successful cache retrievals
- `cache_misses`: Number of instantiations required
- `cache_hit_rate`: Hit rate (hits / total accesses)
- `evictions`: Total evictions performed
- `total_instantiations`: Total instances created
- `cached_instances`: Current cache size
- `cache_entries`: Detailed per-entry statistics

**Per-Entry Stats**:
- `age_seconds`: Time since creation
- `last_accessed_seconds_ago`: Time since last access
- `access_count`: Number of times accessed

## Thread Safety

All cache operations are thread-safe via internal locking:
- Concurrent access to same class triggers single instantiation
- Multiple threads safely share cached instances
- Eviction operations are atomic

## Integration with MethodExecutor

The MethodExecutor exposes cache management through convenient methods:

```python
from orchestration.orchestrator import MethodExecutor

executor = MethodExecutor()

# Clear cache between pipeline runs
stats = executor.clear_instance_cache()

# Manually evict expired entries
count = executor.evict_expired_instances()

# Get performance metrics
stats = executor.get_registry_stats()
```

## Recommended Configuration

### Production Long-Lived Services

```python
registry = MethodRegistry(
    cache_ttl_seconds=600.0,     # 10 minutes
    max_cache_size=100,           # Limit total instances
    enable_weakref=False,         # Use explicit eviction
)
```

### Batch Processing / Pipeline Runs

```python
registry = MethodRegistry(
    cache_ttl_seconds=0.0,        # Disable TTL
    max_cache_size=200,           # Larger cache for batch
    enable_weakref=False,         # Manual clearing between runs
)

# Clear after each run
for run in pipeline_runs:
    execute_pipeline(run)
    registry.clear_cache()
```

### Memory-Constrained Environments

```python
registry = MethodRegistry(
    cache_ttl_seconds=120.0,      # 2 minutes
    max_cache_size=20,            # Small cache
    enable_weakref=True,          # Aggressive GC
)
```

## Monitoring and Alerting

Monitor these metrics for operational health:

1. **Cache Hit Rate**: Should be > 50% for effective caching
   - Low hit rate may indicate TTL too aggressive or cache too small
   
2. **Eviction Rate**: Track `evictions` over time
   - High eviction rate may indicate cache too small or TTL too low
   
3. **Cache Size**: Monitor `cached_instances`
   - Approaching `max_cache_size` indicates potential bottleneck
   
4. **Total Instantiations**: Track growth over time
   - Should scale sub-linearly with request volume

## Testing Cache Behavior

Unit tests verify cache eviction works correctly:

```bash
pytest tests/test_method_registry_memory_management.py -v
pytest tests/test_method_registry_integration.py -v
```

## Performance Impact

**Cache Hit**:
- O(1) dictionary lookup
- Minimal overhead (~microseconds)

**Cache Miss + Instantiation**:
- O(1) cache check
- O(n) eviction check if at capacity (n = cache size)
- O(instantiation) for class creation
- Typically ~milliseconds depending on class complexity

**Eviction**:
- O(n log n) for sorting by access time (n = cache size)
- Amortized across many cache hits
- Typically runs in background when cache is full

## Troubleshooting

### Memory Still Growing

1. Verify cache clearing is called between runs
2. Check `get_stats()` - are evictions happening?
3. Reduce `max_cache_size` or `cache_ttl_seconds`
4. Enable `enable_weakref` for automatic GC

### Low Cache Hit Rate

1. Increase `cache_ttl_seconds` or `max_cache_size`
2. Check if method access patterns are truly reusable
3. Verify thread-safe access isn't causing false misses

### Frequent Instantiations

1. Increase cache limits
2. Disable or increase TTL
3. Verify clear_cache() not called too frequently

## Future Enhancements

Potential improvements for future versions:

1. **Adaptive TTL**: Auto-adjust based on access patterns
2. **Priority-based eviction**: Keep frequently-used instances longer
3. **Memory-aware eviction**: Evict based on actual memory consumption
4. **Distributed caching**: Share instances across processes
5. **Warm-up strategies**: Pre-populate cache for known patterns
