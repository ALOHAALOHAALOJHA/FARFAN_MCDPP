"""
SISAS Canonical Map Registry

This directory contains the definitive mapping between:
- Signal types
- Consumers
- Information items (questions, policy areas, dimensions, clusters)

Files:
- signal_consumer_map.json: Complete canonical mapping

Usage:
    from canonic_questionnaire_central._registry.sisas_canonical_map import load_canonical_map

    canonical_map = load_canonical_map()
    signal_info = canonical_map["signal_types"]["MC01"]
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_canonical_map() -> Dict[str, Any]:
    """Load the canonical signal-consumer-item map."""
    map_path = Path(__file__).parent / "signal_consumer_map.json"
    with open(map_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_signal_info(signal_type: str) -> Dict[str, Any]:
    """Get information for a specific signal type."""
    canonical_map = load_canonical_map()
    return canonical_map["signal_types"].get(signal_type, {})


def get_consumer_info(consumer_id: str) -> Dict[str, Any]:
    """Get information for a specific consumer."""
    canonical_map = load_canonical_map()
    return canonical_map["consumers"].get(consumer_id, {})


def get_irrigation_summary() -> Dict[str, Any]:
    """Get irrigation summary statistics."""
    canonical_map = load_canonical_map()
    return canonical_map["irrigation_summary"]


__all__ = [
    "load_canonical_map",
    "get_signal_info",
    "get_consumer_info",
    "get_irrigation_summary",
]
