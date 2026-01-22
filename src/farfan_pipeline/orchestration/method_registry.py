"""
DEPRECATED: This module is a legacy compatibility stub.

Actual method injection is performed by:
- UnifiedFactory.execute_contract() (factory.py:706-1024)
- Direct method binding via executor_binding configuration

This stub will be removed in v3.0.0.
"""
import warnings
warnings.warn(
    "method_registry.py is deprecated. Use UnifiedFactory for method injection.",
    DeprecationWarning,
    stacklevel=2
)

import time
from typing import Any, Dict, Optional, Type

class CacheEntry:
    """Stub for CacheEntry."""
    def __init__(self, instance: Any, created_at: float, last_accessed: float, access_count: int):
        self.instance = instance
        self.created_at = created_at
        self.last_accessed = last_accessed
        self.access_count = access_count

class MethodRegistry:
    """Stub for MethodRegistry."""
    
    def __init__(self, class_paths: Dict[str, str], cache_ttl_seconds: float = 300.0, max_cache_size: int = 100):
        self.class_paths = class_paths
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._evictions = 0
        self._instantiations = 0

    def get_method(self, class_name: str, method_name: str) -> Any:
        instance = self._get_instance(class_name)
        if hasattr(instance, method_name):
            return getattr(instance, method_name)
        return None

    def _get_instance(self, class_name: str) -> Any:
        if class_name in self._cache:
            entry = self._cache[class_name]
            # Check TTL
            if self.cache_ttl_seconds > 0 and (time.time() - entry.last_accessed > self.cache_ttl_seconds):
                 self.evict_expired()
            else:
                self._cache_hits += 1
                entry.last_accessed = time.time()
                entry.access_count += 1
                return entry.instance
        
        self._cache_misses += 1
        instance = self._instantiate_class(class_name)
        self._instantiations += 1
        self._cache[class_name] = CacheEntry(instance, time.time(), time.time(), 1)
        return instance

    def _load_class(self, class_path: str) -> Type:
        # Stub implementation
        return object

    def _instantiate_class(self, class_name: str) -> Any:
        # Stub implementation
        return object()

    def has_method(self, class_name: str, method_name: str) -> bool:
        return True

    def clear_cache(self) -> Dict[str, Any]:
        entries_cleared = len(self._cache)
        self._cache.clear()
        return {
            "entries_cleared": entries_cleared,
            "total_hits": self._cache_hits,
            "total_misses": self._cache_misses,
            "total_evictions": self._evictions,
            "total_instantiations": self._instantiations
        }

    def evict_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._cache.items() if self.cache_ttl_seconds > 0 and (now - v.last_accessed > self.cache_ttl_seconds)]
        for k in expired:
            del self._cache[k]
        count = len(expired)
        self._evictions += count
        return count

    def get_stats(self) -> Dict[str, Any]:
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": hit_rate,
            "evictions": self._evictions,
            "total_instantiations": self._instantiations,
            "cache_entries": [
                {
                    "class_name": k,
                    "age_seconds": time.time() - v.created_at,
                    "last_accessed_seconds_ago": time.time() - v.last_accessed,
                    "access_count": v.access_count
                }
                for k, v in self._cache.items()
            ]
        }
