"""Signal Registry Cache for SISAS.

This module provides an LRU cache with TTL management for SignalPack instances.
This is the OLD SignalRegistry - distinct from the new signals/registry.py which
handles signal TYPE registration.

Components:
- CacheEntry: Entry in the signal registry cache
- SignalRegistry: LRU cache for signal packs with TTL management

Note: This is the CACHE layer - for signal pack instances, not signal types.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import SignalPack

# Optional dependency - structlog
try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entry in the signal registry cache."""

    signal_pack: SignalPack  # type: ignore[name-defined]
    inserted_at: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)


class SignalRegistry:
    """
    In-memory LRU cache for signal packs with TTL management.

    Features:
    - LRU eviction when capacity exceeded
    - TTL-based expiration
    - Access tracking for observability
    - Thread-safe operations (single-process)

    Note: This is a CACHE for SignalPack instances, distinct from the
    signal TYPE registry in signals/registry.py.

    Attributes:
        max_size: Maximum number of cached signal packs
        default_ttl_s: Default TTL for cached entries
    """

    def __init__(self, max_size: int = 100, default_ttl_s: int = 3600) -> None:
        """
        Initialize signal registry.

        Args:
            max_size: Maximum cache size
            default_ttl_s: Default TTL in seconds
        """
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._default_ttl_s = default_ttl_s
        self._hits = 0
        self._misses = 0
        self._evictions = 0

        logger.info(
            "signal_registry_cache_initialized",
            max_size=max_size,
            default_ttl_s=default_ttl_s,
        )

    def put(self, policy_area: str, signal_pack: SignalPack) -> None:  # type: ignore[name-defined]
        """
        Store signal pack in registry.

        Args:
            policy_area: Policy area key
            signal_pack: Signal pack to store
        """
        now = time.time()

        # Remove expired entries before insertion
        self._evict_expired()

        # LRU eviction if at capacity
        if len(self._cache) >= self._max_size and policy_area not in self._cache:
            oldest_key = next(iter(self._cache))
            self._cache.pop(oldest_key)
            self._evictions += 1
            logger.debug("signal_registry_evicted_lru", key=oldest_key)

        # Insert or update
        entry = CacheEntry(signal_pack=signal_pack, inserted_at=now)
        self._cache[policy_area] = entry
        self._cache.move_to_end(policy_area)  # Mark as most recently used

        logger.info(
            "signal_registry_put",
            policy_area=policy_area,
            version=signal_pack.version,
            hash=signal_pack.compute_hash()[:16],
        )

    def get(self, policy_area: str) -> SignalPack | None:  # type: ignore[name-defined]
        """
        Retrieve signal pack from registry.

        Args:
            policy_area: Policy area key

        Returns:
            Signal pack if found and valid, None otherwise
        """
        now = time.time()

        entry = self._cache.get(policy_area)
        if entry is None:
            self._misses += 1
            logger.debug("signal_registry_miss", policy_area=policy_area)
            return None

        # Check TTL expiration
        ttl = entry.signal_pack.ttl_s or self._default_ttl_s
        if now - entry.inserted_at > ttl:
            # Expired, remove from cache
            self._cache.pop(policy_area)
            self._misses += 1
            logger.debug(
                "signal_registry_expired",
                policy_area=policy_area,
                age_s=now - entry.inserted_at,
            )
            return None

        # Check validity window
        if not entry.signal_pack.is_valid():
            self._cache.pop(policy_area)
            self._misses += 1
            logger.debug("signal_registry_invalid", policy_area=policy_area)
            return None

        # Valid hit
        entry.access_count += 1
        entry.last_accessed = now
        self._cache.move_to_end(policy_area)  # Mark as most recently used
        self._hits += 1

        logger.debug(
            "signal_registry_hit",
            policy_area=policy_area,
            access_count=entry.access_count,
        )

        return entry.signal_pack

    def _evict_expired(self) -> None:
        """Remove expired entries from cache."""
        now = time.time()
        expired_keys = []

        for key, entry in self._cache.items():
            ttl = entry.signal_pack.ttl_s or self._default_ttl_s
            if now - entry.inserted_at > ttl:
                expired_keys.append(key)

        for key in expired_keys:
            self._cache.pop(key)
            self._evictions += 1

        if expired_keys:
            logger.debug("signal_registry_evicted_expired", count=len(expired_keys))

    def get_metrics(self) -> dict[str, Any]:
        """
        Get registry metrics for observability.

        Returns:
            Dict with metrics:
            - hit_rate: Cache hit rate [0.0, 1.0]
            - size: Current cache size
            - capacity: Maximum cache size
            - hits: Total cache hits
            - misses: Total cache misses
            - evictions: Total evictions
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        # Compute staleness stats
        now = time.time()
        staleness_values = []
        for entry in self._cache.values():
            staleness_values.append(now - entry.inserted_at)

        avg_staleness = sum(staleness_values) / len(staleness_values) if staleness_values else 0.0
        max_staleness = max(staleness_values) if staleness_values else 0.0

        return {
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "capacity": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "staleness_avg_s": avg_staleness,
            "staleness_max_s": max_staleness,
        }

    def clear(self) -> None:
        """Clear all entries from registry."""
        self._cache.clear()
        logger.info("signal_registry_cleared")


__all__ = [
    "SignalRegistry",
    "CacheEntry",
]
