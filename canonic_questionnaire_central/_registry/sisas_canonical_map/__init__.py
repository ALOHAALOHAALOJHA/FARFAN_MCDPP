"""
SISAS Canonical Map Registry

This directory contains the definitive mapping between:
- Signal types (MC01-MC10, enrichment, scoring, aggregation)
- Signal categories (STRUCTURAL, INTEGRITY, EPISTEMIC, CONTRAST, OPERATIONAL, CONSUMPTION, ORCHESTRATION)
- Consumers (phase_00 through phase_09)
- Buses (8 bus types)
- Vehicles (8 vehicle types)
- Information items (questions, dimensions, policy areas, clusters)

Files:
- signal_consumer_map.json: Complete canonical mapping

Usage:
    from canonic_questionnaire_central._registry.sisas_canonical_map import load_canonical_map

    canonical_map = load_canonical_map()
    signal_info = canonical_map["signal_types"]["MC01"]
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from functools import lru_cache


def load_canonical_map() -> Dict[str, Any]:
    """Load the canonical signal-consumer-item map."""
    map_path = Path(__file__).parent / "signal_consumer_map.json"
    with open(map_path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=128)
def get_signal_info(signal_type: str) -> Dict[str, Any]:
    """Get information for a specific signal type."""
    canonical_map = load_canonical_map()
    return canonical_map["signal_types"].get(signal_type, {})


@lru_cache(maxsize=128)
def get_consumer_info(consumer_id: str) -> Dict[str, Any]:
    """Get information for a specific consumer."""
    canonical_map = load_canonical_map()
    return canonical_map["consumers"].get(consumer_id, {})


@lru_cache(maxsize=128)
def get_dimension_info(dimension_id: str) -> Dict[str, Any]:
    """Get information for a specific dimension."""
    canonical_map = load_canonical_map()
    return canonical_map["dimension_coverage"].get(dimension_id, {})


@lru_cache(maxsize=128)
def get_vehicle_info(vehicle_id: str) -> Dict[str, Any]:
    """Get information for a specific vehicle."""
    canonical_map = load_canonical_map()
    return canonical_map["vehicles"].get(vehicle_id, {})


def get_irrigation_summary() -> Dict[str, Any]:
    """Get irrigation summary statistics."""
    canonical_map = load_canonical_map()
    return canonical_map["irrigation_summary"]


def get_signals_for_dimension(dimension_id: str) -> List[str]:
    """Get all signal types that target a specific dimension."""
    dim_info = get_dimension_info(dimension_id)
    return dim_info.get("mc_signals", [])


def get_signals_for_phase(phase: str) -> List[str]:
    """Get all signal types for a specific phase."""
    canonical_map = load_canonical_map()
    return [
        signal_id
        for signal_id, signal_info in canonical_map["signal_types"].items()
        if signal_info.get("phase") == phase
    ]


def get_consumers_for_phase(phase: str) -> List[str]:
    """Get all consumer IDs for a specific phase."""
    canonical_map = load_canonical_map()
    return [
        consumer_id
        for consumer_id, consumer_info in canonical_map["consumers"].items()
        if consumer_info.get("phase") == phase
    ]


def get_questions_for_signal(signal_type: str) -> List[str]:
    """Get primary question IDs for a specific signal type."""
    signal_info = get_signal_info(signal_type)
    questions = signal_info.get("primary_questions", [])
    return questions if questions != ["ALL"] else []


def get_signal_category(signal_type: str) -> Optional[str]:
    """Get the category for a specific signal type."""
    signal_info = get_signal_info(signal_type)
    return signal_info.get("category")


def get_bus_for_signal(signal_type: str) -> Optional[str]:
    """Get the bus that handles a specific signal type."""
    signal_info = get_signal_info(signal_type)
    return signal_info.get("bus")


def get_policy_areas_for_cluster(cluster_id: str) -> List[str]:
    """Get policy areas that belong to a specific cluster."""
    canonical_map = load_canonical_map()
    for cluster in canonical_map["information_items"]["clusters"]["items"]:
        if cluster["id"] == cluster_id:
            return cluster.get("policy_areas", [])
    return []


def get_cluster_for_policy_area(policy_area_id: str) -> Optional[str]:
    """Get the cluster ID that a policy area belongs to."""
    canonical_map = load_canonical_map()
    for pa in canonical_map["information_items"]["policy_areas"]["items"]:
        if pa["id"] == policy_area_id:
            return pa.get("cluster")
    return None


def get_dimension_boost_value(signal_type: str, dimension_id: str) -> float:
    """Get the boost value for a signal-dimension pair."""
    signal_info = get_signal_info(signal_type)
    boost_values = signal_info.get("boost_values", {})
    return boost_values.get(dimension_id, 0.0)


def get_signal_axioms() -> Dict[str, str]:
    """Get the signal axioms."""
    canonical_map = load_canonical_map()
    return canonical_map.get("signal_axioms", {})


def get_bus_registry() -> List[Dict[str, str]]:
    """Get all bus definitions."""
    canonical_map = load_canonical_map()
    return canonical_map["bus_registry"]["buses"]


def get_all_signal_categories() -> Dict[str, Dict[str, str]]:
    """Get all signal category definitions."""
    canonical_map = load_canonical_map()
    return canonical_map.get("signal_categories", {})


def get_coverage_summary() -> Dict[str, Any]:
    """Get the MC coverage summary."""
    irrigation_summary = get_irrigation_summary()
    return irrigation_summary.get("mc_coverage_summary", {})


def clear_cache():
    """Clear the LRU cache (useful for testing or when map changes)."""
    get_signal_info.cache_clear()
    get_consumer_info.cache_clear()
    get_dimension_info.cache_clear()
    get_vehicle_info.cache_clear()


__all__ = [
    # Core functions
    "load_canonical_map",
    "get_signal_info",
    "get_consumer_info",
    "get_dimension_info",
    "get_vehicle_info",
    "get_irrigation_summary",
    # Query functions
    "get_signals_for_dimension",
    "get_signals_for_phase",
    "get_consumers_for_phase",
    "get_questions_for_signal",
    "get_signal_category",
    "get_bus_for_signal",
    "get_policy_areas_for_cluster",
    "get_cluster_for_policy_area",
    "get_dimension_boost_value",
    # Metadata functions
    "get_signal_axioms",
    "get_bus_registry",
    "get_all_signal_categories",
    "get_coverage_summary",
    # Utility
    "clear_cache",
]
