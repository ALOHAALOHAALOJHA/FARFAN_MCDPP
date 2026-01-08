"""
Thread-Safe Subphase Results Container.

Purpose: Prevent race conditions in concurrent Phase 1 execution.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State: ACTIVE
"""

from collections import UserDict
import threading
from typing import Any, Dict, Optional, Iterator

class ThreadSafeResults(UserDict):
    """
    A thread-safe dictionary wrapper for storing subphase results.
    Inherits from UserDict to ensure compatibility with dict interfaces.
    """

    def __init__(self, initial_data: Optional[Dict[Any, Any]] = None):
        super().__init__(initial_data)
        self.lock = threading.Lock()

    def __getitem__(self, key: Any) -> Any:
        with self.lock:
            return super().__getitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        with self.lock:
            super().__setitem__(key, value)

    def __delitem__(self, key: Any) -> None:
        with self.lock:
            super().__delitem__(key)

    def __contains__(self, key: Any) -> bool:
        with self.lock:
            return super().__contains__(key)

    def __iter__(self) -> Iterator[Any]:
        with self.lock:
            # Iterate over a copy of keys to be safe
            return iter(list(self.data.keys()))

    def __len__(self) -> int:
        with self.lock:
            return len(self.data)

    def get(self, key: Any, default: Any = None) -> Any:
        with self.lock:
            return super().get(key, default)

    def copy(self) -> 'ThreadSafeResults':
        with self.lock:
            return ThreadSafeResults(self.data.copy())

    def to_dict(self) -> Dict[Any, Any]:
        """Return a copy as a standard dict."""
        with self.lock:
            return self.data.copy()

    def update(self, *args, **kwargs) -> None:
        with self.lock:
            super().update(*args, **kwargs)

    def items(self):
        with self.lock:
            return list(super().items())

    def values(self):
        with self.lock:
            return list(super().values())

    def keys(self):
        with self.lock:
            return list(super().keys())
