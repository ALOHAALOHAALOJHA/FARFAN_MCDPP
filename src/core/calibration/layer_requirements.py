"""
CANONICAL LAYER_REQUIREMENTS - SINGLE SOURCE OF TRUTH
NO OTHER FILE may define layer requirements.
"""
from typing import TypedDict


class LayerConfig(TypedDict):
    layers: list[str]
    count: int
    description: str
    min_confidence: float


LAYER_REQUIREMENTS: dict[str, LayerConfig] = {
    "ingest": {
        "layers": ["@b", "@chain", "@u", "@m"],
        "count": 4,
        "description": "Data ingestion",
        "min_confidence": 0.5,
    },
    "processor": {
        "layers": ["@b", "@chain", "@u", "@m"],
        "count": 4,
        "description": "Data processing",
        "min_confidence": 0.5,
    },
    "analyzer": {
        "layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
        "count": 8,
        "description": "Complex analysis - ALL context",
        "min_confidence": 0.7,
    },
    "extractor": {
        "layers": ["@b", "@chain", "@u", "@m"],
        "count": 4,
        "description": "Feature extraction",
        "min_confidence": 0.5,
    },
    "score": {
        "layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
        "count": 8,
        "description": "Scoring methods",
        "min_confidence": 0.7,
    },
    "executor": {
        "layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
        "count": 8,
        "description": "D1Q1-D6Q5 executors - ALL context",
        "min_confidence": 0.7,
    },
    "utility": {
        "layers": ["@b", "@chain", "@m"],
        "count": 3,
        "description": "Helpers",
        "min_confidence": 0.3,
    },
    "orchestrator": {
        "layers": ["@b", "@chain", "@m"],
        "count": 3,
        "description": "Coordination",
        "min_confidence": 0.5,
    },
    "core": {
        "layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
        "count": 8,
        "description": "Critical foundation",
        "min_confidence": 0.8,
    },
}

# MANDATORY VALIDATION AT IMPORT TIME
assert all(
    len(cfg["layers"]) == cfg["count"] for cfg in LAYER_REQUIREMENTS.values()
), "Layer count mismatch in LAYER_REQUIREMENTS"


def get_required_layers(method_type: str) -> list[str]:
    """ÚNICO punto de acceso para obtener capas requeridas."""
    if method_type not in LAYER_REQUIREMENTS:
        return LAYER_REQUIREMENTS["core"]["layers"]
    return LAYER_REQUIREMENTS[method_type]["layers"]
