"""
CANONICAL LAYER_REQUIREMENTS - SINGLE SOURCE OF TRUTH

This module reads from config/layer_requirements.json.
NO HARDCODED VALUES IN THIS FILE.

JOBFRONT 4 will implement:
- LAYER_REQUIREMENTS dict loaded from JSON
- get_required_layers(method_type) function
- Validation at import time
"""
# STUB - Implementation in JOBFRONT 4

from typing import TypedDict


class LayerConfig(TypedDict):
    """Layer configuration from JSON."""
    layers: list[str]
    count: int
    description: str
    min_confidence: float


# PLACEHOLDER - Will be loaded from JSON in JOBFRONT 4
LAYER_REQUIREMENTS: dict[str, LayerConfig] = {}


def get_required_layers(method_type: str) -> list[str]:
    """
    Get required layers for a method type.
    
    STUB - Will read from layer_requirements.json in JOBFRONT 4.
    """
    raise NotImplementedError("JOBFRONT 4 pending")
