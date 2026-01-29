"""SISAS Signals Compatibility Layer.

This module provides backward compatibility for code importing from SISAS.signals.
It re-exports components from the new modular architecture:

- signals/client.py: SignalClient, SignalPack, InMemorySignalSource
- signals/cache.py: SignalRegistry (LRU cache for SignalPack instances)
- signals/registry.py: SignalRegistry (TYPE registry - different from cache!)

Note: There are TWO different SignalRegistry classes:
1. signals.cache.SignalRegistry - LRU cache for SignalPack instances (OLD, for bootstrap)
2. signals.registry.SignalRegistry - Factory/registry for signal TYPE classes (NEW architecture)

This module exports the cache version for backward compatibility.
"""

# Export signal client infrastructure (transport layer)
from .signal_types.client import (
    SignalPack,
    InMemorySignalSource,
    SignalClient,
    CircuitBreakerError,
    SignalUnavailableError,
    PolicyArea,
    create_default_signal_pack,
)

# Export signal registry cache (for SignalPack instances)
from .signal_types.cache import (
    SignalRegistry,
    CacheEntry,
)

# Export for backward compatibility
__all__ = [
    # Client infrastructure
    "SignalPack",
    "InMemorySignalSource",
    "SignalClient",
    "CircuitBreakerError",
    "SignalUnavailableError",
    "PolicyArea",
    "create_default_signal_pack",
    # Cache
    "SignalRegistry",
    "CacheEntry",
]
