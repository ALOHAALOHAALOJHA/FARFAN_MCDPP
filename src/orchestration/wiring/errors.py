"""Wiring errors - Exception classes for wiring initialization."""

from __future__ import annotations


class WiringInitializationError(Exception):
    """Raised when wiring initialization fails."""
    pass


class MissingDependencyError(WiringInitializationError):
    """Raised when a required dependency is missing during wiring."""
    pass


__all__ = [
    "WiringInitializationError",
    "MissingDependencyError",
]
