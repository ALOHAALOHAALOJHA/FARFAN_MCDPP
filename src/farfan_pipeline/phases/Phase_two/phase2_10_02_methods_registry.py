"""
Module: phase2_10_02_methods_registry
PHASE_LABEL: Phase 2
Sequence: O
Description: Methods registry with lazy loading

Version: 1.0.0
Last Modified: 2025-12-20
Author: F.A.R.F.A.N Policy Pipeline
License: Proprietary

This module is part of Phase 2: Analysis & Question Execution.
All files in Phase_two/ must contain PHASE_LABEL: Phase 2.
"""
from __future__ import annotations

import logging
import threading
import time
import weakref
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable

logger = logging.getLogger(__name__)


class MethodRegistryError(RuntimeError):
    """Raised when a method cannot be retrieved."""


@dataclass
class CacheEntry:
    """Cache entry with TTL tracking."""
    
    instance: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    
    def is_expired(self, ttl_seconds: float) -> bool:
        """Check if entry has exceeded TTL."""
        if ttl_seconds <= 0:
            return False
        return (time.time() - self.last_accessed) > ttl_seconds
    
    def touch(self) -> None:
        """Update access timestamp and counter."""
        self.last_accessed = time.time()
        self.access_count += 1


class MethodRegistry:
    """Registry for lazy method injection without full class instantiation.
    
    Features memory management with TTL-based eviction and weakref support.
    """

    def __init__(
        self,
        class_paths: dict[str, str] | None = None,
        cache_ttl_seconds: float = 300.0,
        enable_weakref: bool = False,
        max_cache_size: int = 100,
    ) -> None:
        """Initialize the method registry.

        Args:
            class_paths: Optional mapping of class names to import paths.
                        If None, uses default paths from class_registry.
            cache_ttl_seconds: Time-to-live for cache entries in seconds.
                             Set to 0 to disable TTL-based eviction.
            enable_weakref: If True, use weak references for instances.
            max_cache_size: Maximum number of instances to cache.
        """
        # Import class paths from existing registry
        if class_paths is None:
            from orchestration.class_registry import get_class_paths
            class_paths = dict(get_class_paths())

        self._class_paths = class_paths
        self._cache: dict[str, CacheEntry] = {}
        self._weakref_cache: dict[str, weakref.ref[Any]] = {}
        self._direct_methods: dict[tuple[str, str], Callable[..., Any]] = {}
        self._failed_classes: set[str] = set()
        self._lock = threading.Lock()
        self._cache_ttl_seconds = cache_ttl_seconds
        self._enable_weakref = enable_weakref
        self._max_cache_size = max_cache_size

        # Special instantiation rules (from original MethodExecutor)
        self._special_instantiation: dict[str, Callable[[type], Any]] = {}
        
        # Metrics
        self._cache_hits = 0
        self._cache_misses = 0
        self._evictions = 0
        self._total_instantiations = 0

    def inject_method(
        self,
        class_name: str,
        method_name: str,
        method: Callable[..., Any],
    ) -> None:
        """Directly inject a method without needing a class.

        This allows bypassing class instantiation entirely.

        Args:
            class_name: Virtual class name for routing
            method_name: Method name
            method: Callable to inject
        """
        key = (class_name, method_name)
        self._direct_methods[key] = method
        logger.info(
            "method_injected_directly",
            class_name=class_name,
            method_name=method_name,
        )

    def register_instantiation_rule(
        self,
        class_name: str,
        instantiator: Callable[[type], Any],
    ) -> None:
        """Register special instantiation logic for a class.

        Args:
            class_name: Class name requiring special instantiation
            instantiator: Function that takes class type and returns instance
        """
        self._special_instantiation[class_name] = instantiator
        logger.debug(
            "instantiation_rule_registered",
            class_name=class_name,
        )

    def _load_class(self, class_name: str) -> type:
        """Load a class type from import path.

        Args:
            class_name: Name of class to load

        Returns:
            Class type

        Raises:
            MethodRegistryError: If class cannot be loaded
        """
        if class_name not in self._class_paths:
            raise MethodRegistryError(
                f"Class '{class_name}' not found in registry paths"
            )

        path = self._class_paths[class_name]
        module_name, _, attr_name = path.rpartition(".")

        if not module_name:
            raise MethodRegistryError(
                f"Invalid path for '{class_name}': {path}"
            )

        try:
            module = import_module(module_name)
            cls = getattr(module, attr_name)

            if not isinstance(cls, type):
                raise MethodRegistryError(
                    f"'{class_name}' is not a class: {type(cls).__name__}"
                )

            return cls

        except ImportError as exc:
            raise MethodRegistryError(
                f"Cannot import class '{class_name}' from {path}: {exc}"
            ) from exc
        except AttributeError as exc:
            raise MethodRegistryError(
                f"Class '{attr_name}' not found in module {module_name}: {exc}"
            ) from exc

    def _instantiate_class(self, class_name: str, cls: type) -> Any:
        """Instantiate a class using special rules or default constructor.

        Args:
            class_name: Name of class (for special rule lookup)
            cls: Class type to instantiate

        Returns:
            Instance of the class

        Raises:
            MethodRegistryError: If instantiation fails
        """
        # Use special instantiation rule if registered
        if class_name in self._special_instantiation:
            try:
                instantiator = self._special_instantiation[class_name]
                instance = instantiator(cls)
                logger.debug(
                    "class_instantiated_with_special_rule",
                    class_name=class_name,
                )
                return instance
            except Exception as exc:
                raise MethodRegistryError(
                    f"Special instantiation failed for '{class_name}': {exc}"
                ) from exc

        # Default instantiation (no-args constructor)
        try:
            instance = cls()
            logger.debug(
                "class_instantiated_default",
                class_name=class_name,
            )
            return instance
        except Exception as exc:
            raise MethodRegistryError(
                f"Default instantiation failed for '{class_name}': {exc}"
            ) from exc

    def _get_instance(self, class_name: str) -> Any:
        """Get or create instance of a class (lazy + cached).

        Args:
            class_name: Name of class to instantiate

        Returns:
            Instance of the class

        Raises:
            MethodRegistryError: If class cannot be instantiated
        """
        # Check if already failed
        if class_name in self._failed_classes:
            raise MethodRegistryError(
                f"Class '{class_name}' previously failed to instantiate"
            )

        # Use a lock to ensure thread-safe instantiation
        with self._lock:
            # Check weakref cache first
            if self._enable_weakref and class_name in self._weakref_cache:
                instance = self._weakref_cache[class_name]()
                if instance is not None:
                    self._cache_hits += 1
                    logger.debug(
                        "class_retrieved_from_weakref_cache",
                        class_name=class_name,
                    )
                    return instance
                else:
                    # Weakref was garbage collected
                    del self._weakref_cache[class_name]
            
            # Check regular cache and evict if expired
            if class_name in self._cache:
                entry = self._cache[class_name]
                if entry.is_expired(self._cache_ttl_seconds):
                    logger.info(
                        "cache_entry_expired",
                        class_name=class_name,
                        age_seconds=time.time() - entry.created_at,
                        access_count=entry.access_count,
                    )
                    del self._cache[class_name]
                    self._evictions += 1
                else:
                    entry.touch()
                    self._cache_hits += 1
                    return entry.instance

            # Cache miss - need to instantiate
            self._cache_misses += 1
            
            # Evict oldest entries if cache is full
            self._evict_if_full()

            # Load and instantiate class
            try:
                cls = self._load_class(class_name)
                instance = self._instantiate_class(class_name, cls)
                self._total_instantiations += 1
                
                # Store in appropriate cache
                if self._enable_weakref:
                    self._weakref_cache[class_name] = weakref.ref(instance)
                    logger.info(
                        "class_instantiated_weakref",
                        class_name=class_name,
                    )
                else:
                    entry = CacheEntry(
                        instance=instance,
                        created_at=time.time(),
                        last_accessed=time.time(),
                        access_count=1,
                    )
                    self._cache[class_name] = entry
                    logger.info(
                        "class_instantiated_cached",
                        class_name=class_name,
                    )
                
                return instance

            except MethodRegistryError:
                # Mark as failed to avoid repeated attempts
                self._failed_classes.add(class_name)
                raise
    
    def _evict_if_full(self) -> None:
        """Evict oldest cache entries if cache size exceeds maximum."""
        if len(self._cache) <= self._max_cache_size:
            return
        
        # Sort by last accessed time and evict oldest
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed,
        )
        
        evict_count = len(self._cache) - self._max_cache_size
        for class_name, entry in sorted_entries[:evict_count]:
            logger.info(
                "cache_entry_evicted_size_limit",
                class_name=class_name,
                age_seconds=time.time() - entry.created_at,
                access_count=entry.access_count,
            )
            del self._cache[class_name]
            self._evictions += 1

    def get_method(
        self,
        class_name: str,
        method_name: str,
    ) -> Callable[..., Any]:
        """Get method callable with lazy instantiation.

        This is the main entry point for retrieving methods.

        Args:
            class_name: Name of class containing the method
            method_name: Name of method to retrieve

        Returns:
            Callable method (bound or injected)

        Raises:
            MethodRegistryError: If method cannot be retrieved
        """
        # Check for directly injected method first
        key = (class_name, method_name)
        if key in self._direct_methods:
            logger.debug(
                "method_retrieved_direct",
                class_name=class_name,
                method_name=method_name,
            )
            return self._direct_methods[key]

        # Get instance (lazy) and retrieve method
        try:
            instance = self._get_instance(class_name)
            method = getattr(instance, method_name)

            if not callable(method):
                raise MethodRegistryError(
                    f"'{class_name}.{method_name}' is not callable"
                )

            logger.debug(
                "method_retrieved_from_instance",
                class_name=class_name,
                method_name=method_name,
            )
            return method

        except AttributeError as exc:
            raise MethodRegistryError(
                f"Method '{method_name}' not found on class '{class_name}'"
            ) from exc

    def has_method(self, class_name: str, method_name: str) -> bool:
        """Check if a method is available (without instantiating).

        Args:
            class_name: Name of class
            method_name: Name of method

        Returns:
            True if method exists (or is directly injected)
        """
        # Check direct injection
        key = (class_name, method_name)
        if key in self._direct_methods:
            return True

        # Check if class is known and not failed
        if class_name in self._failed_classes:
            return False

        if class_name not in self._class_paths:
            return False

        # If instance exists, check method
        if class_name in self._cache:
            instance = self._cache[class_name].instance
            return hasattr(instance, method_name)

        # Otherwise, assume it exists (lazy check)
        # Full validation happens on first get_method() call
        return True
    
    def clear_cache(self) -> dict[str, Any]:
        """Clear all cached instances.
        
        This should be called between pipeline runs to prevent memory bloat.
        
        Returns:
            Statistics about cleared cache entries.
        """
        with self._lock:
            cache_size = len(self._cache)
            weakref_size = len(self._weakref_cache)
            
            stats = {
                "entries_cleared": cache_size,
                "weakrefs_cleared": weakref_size,
                "total_hits": self._cache_hits,
                "total_misses": self._cache_misses,
                "total_evictions": self._evictions,
                "total_instantiations": self._total_instantiations,
            }
            
            # Clear caches
            self._cache.clear()
            self._weakref_cache.clear()
            
            logger.info(
                "cache_cleared",
                **stats,
            )
            
            return stats
    
    def evict_expired(self) -> int:
        """Manually evict expired entries.
        
        Returns:
            Number of entries evicted.
        """
        with self._lock:
            expired = []
            for class_name, entry in self._cache.items():
                if entry.is_expired(self._cache_ttl_seconds):
                    expired.append(class_name)
            
            for class_name in expired:
                entry = self._cache[class_name]
                logger.info(
                    "cache_entry_evicted_manual",
                    class_name=class_name,
                    age_seconds=time.time() - entry.created_at,
                    access_count=entry.access_count,
                )
                del self._cache[class_name]
                self._evictions += 1
            
            return len(expired)

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics.

        Returns:
            Dictionary with registry stats including cache performance metrics
        """
        with self._lock:
            cache_entries = []
            for class_name, entry in self._cache.items():
                cache_entries.append({
                    "class_name": class_name,
                    "age_seconds": time.time() - entry.created_at,
                    "last_accessed_seconds_ago": time.time() - entry.last_accessed,
                    "access_count": entry.access_count,
                })
            
            hit_rate = 0.0
            total_accesses = self._cache_hits + self._cache_misses
            if total_accesses > 0:
                hit_rate = self._cache_hits / total_accesses
            
            return {
                "total_classes_registered": len(self._class_paths),
                "cached_instances": len(self._cache),
                "weakref_instances": len(self._weakref_cache),
                "failed_classes": len(self._failed_classes),
                "direct_methods_injected": len(self._direct_methods),
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_hit_rate": hit_rate,
                "evictions": self._evictions,
                "total_instantiations": self._total_instantiations,
                "cache_ttl_seconds": self._cache_ttl_seconds,
                "max_cache_size": self._max_cache_size,
                "enable_weakref": self._enable_weakref,
                "cache_entries": cache_entries,
                "failed_class_names": list(self._failed_classes),
            }


def setup_default_instantiation_rules(registry: MethodRegistry) -> None:
    """Setup default special instantiation rules.

    These rules replicate the logic from the original MethodExecutor
    for classes that need non-default instantiation.

    Args:
        registry: MethodRegistry to configure
    """
    # MunicipalOntology - shared instance pattern
    ontology_instance = None

    def instantiate_ontology(cls: type) -> Any:
        nonlocal ontology_instance
        if ontology_instance is None:
            ontology_instance = cls()
        return ontology_instance

    registry.register_instantiation_rule("MunicipalOntology", instantiate_ontology)

    # SemanticAnalyzer, PerformanceAnalyzer, TextMiningEngine - need ontology
    def instantiate_with_ontology(cls: type) -> Any:
        if ontology_instance is None:
            raise MethodRegistryError(
                f"Cannot instantiate {cls.__name__}: MunicipalOntology not available"
            )
        return cls(ontology_instance)

    for class_name in ["SemanticAnalyzer", "PerformanceAnalyzer", "TextMiningEngine"]:
        registry.register_instantiation_rule(class_name, instantiate_with_ontology)

    # PolicyTextProcessor - needs ProcessorConfig
    def instantiate_policy_processor(cls: type) -> Any:
        try:
            from farfan_pipeline.processing.policy_processor import ProcessorConfig
            return cls(ProcessorConfig())
        except ImportError as exc:
            raise MethodRegistryError(
                "Cannot instantiate PolicyTextProcessor: ProcessorConfig unavailable"
            ) from exc

    registry.register_instantiation_rule("PolicyTextProcessor", instantiate_policy_processor)


__all__ = [
    "MethodRegistry",
    "MethodRegistryError",
    "setup_default_instantiation_rules",
]
