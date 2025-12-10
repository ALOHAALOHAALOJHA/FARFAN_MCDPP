"""Wiring feature flags - Configuration flags for wiring behavior."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WiringFeatureFlags:
    """Feature flags for wiring configuration."""
    
    strict_validation: bool = True
    allow_missing_optional: bool = True
    enable_lazy_loading: bool = False
    
    
__all__ = ["WiringFeatureFlags"]
