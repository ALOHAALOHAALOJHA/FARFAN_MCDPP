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
All files in Phase_2/ must contain PHASE_LABEL: Phase 2.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import weakref
from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Canonical inventory path
_CANONICAL_INVENTORY_PATH = (
    Path(__file__).resolve().parent / "json_files_phase_two" / "canonical_methods_triangulated.json"
)

# Mother file to module mapping
_MOTHER_FILE_TO_MODULE: dict[str, str] = {
    "derek_beach.py": "methods_dispensary.derek_beach",
    "policy_processor.py": "methods_dispensary.policy_processor",
    "teoria_cambio.py": "methods_dispensary.teoria_cambio",
    "financiero_viabilidad_tablas.py": "methods_dispensary.financiero_viabilidad_tablas",
    "embedding_policy.py": "methods_dispensary.embedding_policy",
    "analyzer_one.py": "methods_dispensary.analyzer_one",
    "contradiction_deteccion.py": "methods_dispensary.contradiction_deteccion",
    "semantic_chunking_policy.py": "methods_dispensary.semantic_chunking_policy",
    "bayesian_multilevel_system.py": "methods_dispensary.bayesian_multilevel_system",
}


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
            from farfan_pipeline.phases.Phase_2.phase2_10_01_class_registry import get_class_paths

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
            raise MethodRegistryError(f"Class '{class_name}' not found in registry paths")

        path = self._class_paths[class_name]
        module_name, _, attr_name = path.rpartition(".")

        if not module_name:
            raise MethodRegistryError(f"Invalid path for '{class_name}': {path}")

        try:
            module = import_module(module_name)
            cls = getattr(module, attr_name)

            if not isinstance(cls, type):
                raise MethodRegistryError(f"'{class_name}' is not a class: {type(cls).__name__}")

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
            raise MethodRegistryError(f"Class '{class_name}' previously failed to instantiate")

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
                raise MethodRegistryError(f"'{class_name}.{method_name}' is not callable")

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
                cache_entries.append(
                    {
                        "class_name": class_name,
                        "age_seconds": time.time() - entry.created_at,
                        "last_accessed_seconds_ago": time.time() - entry.last_accessed,
                        "access_count": entry.access_count,
                    }
                )

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


def load_canonical_methods_inventory() -> list[dict[str, Any]]:
    """Load the canonical methods inventory from JSON.

    Returns:
        List of base question entries with canonical methods.

    Raises:
        FileNotFoundError: If canonical inventory file not found.
    """
    if not _CANONICAL_INVENTORY_PATH.exists():
        raise FileNotFoundError(
            f"Canonical methods inventory not found: {_CANONICAL_INVENTORY_PATH}"
        )

    with open(_CANONICAL_INVENTORY_PATH) as f:
        return json.load(f)


def inject_canonical_methods(registry: MethodRegistry) -> dict[str, Any]:
    """Inject all canonical methods directly into registry.

    This is the DEFAULT operation for executor methods - bypasses class
    instantiation entirely by importing methods as unbound functions and
    wrapping them to handle 'self' parameter.

    The injection flow:
    1. Load canonical_methods_triangulated.json
    2. For each (class, method) pair:
       a. Import the class from its mother module
       b. Get the unbound method from the class
       c. Create a wrapper that instantiates class lazily on first call
       d. Inject wrapper into registry._direct_methods
    3. When get_method() is called, wrapper is returned (no class instantiation)
    4. When wrapper is called, it instantiates class ONCE and caches it

    Args:
        registry: MethodRegistry to populate with canonical methods.

    Returns:
        Statistics about injection results.
    """
    stats = {
        "total_methods": 0,
        "injected": 0,
        "failed": 0,
        "failures": [],
        "classes_loaded": set(),
    }

    try:
        inventory = load_canonical_methods_inventory()
    except FileNotFoundError as e:
        logger.error("canonical_inventory_not_found error=%s", e)
        return {"error": str(e), **stats}

    # Cache for class instances (lazy instantiation on first method call)
    class_instances: dict[str, Any] = {}
    class_types: dict[str, type] = {}

    # Collect unique (class, method, mother_file) tuples
    unique_methods: dict[tuple[str, str], str] = {}
    for entry in inventory:
        for m in entry.get("canonical_methods", []):
            key = (m["class"], m["method"])
            if key not in unique_methods:
                unique_methods[key] = m["mother_file"]

    stats["total_methods"] = len(unique_methods)
    logger.info("canonical_injection_start total_methods=%d", len(unique_methods))

    for (class_name, method_name), mother_file in unique_methods.items():
        try:
            # Get module path from mother file
            module_path = _MOTHER_FILE_TO_MODULE.get(mother_file)
            if not module_path:
                raise ValueError(f"Unknown mother file: {mother_file}")

            # Load class type if not cached
            if class_name not in class_types:
                module = import_module(module_path)
                cls = getattr(module, class_name)
                if not isinstance(cls, type):
                    raise TypeError(f"{class_name} is not a class")
                class_types[class_name] = cls
                stats["classes_loaded"].add(class_name)

            cls = class_types[class_name]

            # Verify method exists on class
            if not hasattr(cls, method_name):
                raise AttributeError(f"Method {method_name} not found on {class_name}")

            # Create lazy wrapper that instantiates class on first call
            def create_wrapper(cls_name: str, meth_name: str, cls_type: type) -> Callable:
                """Create wrapper with closure over class info."""

                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    # Lazy instantiation
                    if cls_name not in class_instances:
                        # Use special instantiation if available
                        if cls_name in registry._special_instantiation:
                            class_instances[cls_name] = registry._special_instantiation[cls_name](
                                cls_type
                            )
                        else:
                            try:
                                class_instances[cls_name] = cls_type()
                            except TypeError:
                                # Class requires arguments - try common patterns
                                class_instances[cls_name] = cls_type.__new__(cls_type)
                        logger.debug("lazy_class_instantiated class=%s", cls_name)

                    instance = class_instances[cls_name]
                    method = getattr(instance, meth_name)
                    return method(*args, **kwargs)

                wrapper.__name__ = f"{cls_name}.{meth_name}"
                wrapper.__qualname__ = f"{cls_name}.{meth_name}"
                return wrapper

            wrapped_method = create_wrapper(class_name, method_name, cls)

            # Inject into registry
            registry.inject_method(class_name, method_name, wrapped_method)
            stats["injected"] += 1

        except Exception as e:
            stats["failed"] += 1
            stats["failures"].append(
                {
                    "class": class_name,
                    "method": method_name,
                    "error": str(e),
                }
            )
            logger.warning(
                "canonical_method_injection_failed class=%s method=%s error=%s",
                class_name,
                method_name,
                e,
            )

    stats["classes_loaded"] = list(stats["classes_loaded"])

    logger.info(
        "canonical_injection_complete injected=%d failed=%d classes=%d",
        stats["injected"],
        stats["failed"],
        len(stats["classes_loaded"]),
    )

    return stats


def setup_registry_with_canonical_methods(
    class_paths: dict[str, str] | None = None,
    cache_ttl_seconds: float = 300.0,
) -> tuple[MethodRegistry, dict[str, Any]]:
    """Create and configure MethodRegistry with canonical methods pre-injected.

    This is the RECOMMENDED way to create a MethodRegistry for executor use.
    All canonical methods are injected directly, bypassing class instantiation.

    Args:
        class_paths: Optional class paths (uses default if None).
        cache_ttl_seconds: Cache TTL for fallback instantiation.

    Returns:
        Tuple of (configured MethodRegistry, injection statistics).
    """
    registry = MethodRegistry(
        class_paths=class_paths,
        cache_ttl_seconds=cache_ttl_seconds,
    )

    # Setup special instantiation rules first (used by lazy wrappers)
    setup_default_instantiation_rules(registry)

    # Inject all canonical methods
    stats = inject_canonical_methods(registry)

    return registry, stats


__all__ = [
    "MethodRegistry",
    "MethodRegistryError",
    "inject_canonical_methods",
    "load_canonical_methods_inventory",
    "setup_default_instantiation_rules",
    "setup_registry_with_canonical_methods",
]
