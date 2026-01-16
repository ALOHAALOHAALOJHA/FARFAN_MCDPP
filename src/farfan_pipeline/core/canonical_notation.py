"""
Canonical Notation Module for F.A.R.F.A.N Pipeline.

This module provides programmatic access to canonical dimensions and policy areas
as defined in the canonical questionnaire central configuration.

The module loads data from:
    canonic_questionnaire_central/config/canonical_notation.json

Exports:
    - CANONICAL_DIMENSIONS: Dictionary of dimension definitions (D1-D6)
    - CANONICAL_POLICY_AREAS: Dictionary of policy area definitions (PA01-PA10)
    - get_dimension_description(dim_id): Get human-readable dimension description
    - get_dimension_info(dim_id): Get full dimension information dictionary
    - get_policy_description(policy_id): Get human-readable policy area description
    - get_all_dimensions(): Get list of all dimension IDs
    - get_all_policy_areas(): Get list of all policy area IDs

Architecture Notes:
    This module bridges the gap between the canonic_questionnaire_central package
    (external configuration) and the farfan_pipeline methods layer (programmatic API).
    
    Methods that require canonical notation can import from this module instead of
    manually loading and parsing JSON files.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# =============================================================================
# Constants and Configuration
# =============================================================================

_CANONICAL_NOTATION_FILE = "canonical_notation.json"
_CANONICAL_CONFIG_PATH = Path(__file__).resolve().parents[3] / "canonic_questionnaire_central" / "config"


# =============================================================================
# JSON Data Loading
# =============================================================================

@lru_cache(maxsize=1)
def _load_canonical_notation() -> dict[str, Any]:
    """
    Load canonical notation from JSON configuration file.
    
    Returns:
        dict: Complete canonical notation data with 'dimensions' and 'policy_areas' keys
        
    Raises:
        FileNotFoundError: If canonical_notation.json is not found
        json.JSONDecodeError: If JSON file is malformed
    """
    json_path = _CANONICAL_CONFIG_PATH / _CANONICAL_NOTATION_FILE
    
    if not json_path.exists():
        raise FileNotFoundError(
            f"Canonical notation file not found at {json_path}. "
            f"Expected path: {_CANONICAL_CONFIG_PATH}"
        )
    
    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Failed to parse canonical notation JSON: {e.msg}",
            e.doc,
            e.pos
        ) from e
    
    # Validate structure
    if "dimensions" not in data:
        raise ValueError("Canonical notation JSON missing 'dimensions' key")
    if "policy_areas" not in data:
        raise ValueError("Canonical notation JSON missing 'policy_areas' key")
    
    return data


# =============================================================================
# Exported Constants
# =============================================================================

def _get_canonical_dimensions() -> dict[str, dict[str, Any]]:
    """Get canonical dimensions dictionary."""
    return _load_canonical_notation()["dimensions"]


def _get_canonical_policy_areas() -> dict[str, dict[str, Any]]:
    """Get canonical policy areas dictionary."""
    return _load_canonical_notation()["policy_areas"]


# Lazy-loaded module-level constants
CANONICAL_DIMENSIONS: dict[str, dict[str, Any]] = {}
CANONICAL_POLICY_AREAS: dict[str, dict[str, Any]] = {}


def _initialize_constants() -> None:
    """Initialize module-level constants on first access."""
    global CANONICAL_DIMENSIONS, CANONICAL_POLICY_AREAS
    
    if not CANONICAL_DIMENSIONS:
        CANONICAL_DIMENSIONS = _get_canonical_dimensions()
    
    if not CANONICAL_POLICY_AREAS:
        CANONICAL_POLICY_AREAS = _get_canonical_policy_areas()


# =============================================================================
# Public API Functions
# =============================================================================

def get_dimension_description(dim_id: str) -> str:
    """
    Get human-readable description for a dimension.
    
    Args:
        dim_id: Dimension identifier (e.g., 'D1', 'D2', ... 'D6')
        
    Returns:
        str: Description of the dimension in Spanish
        
    Raises:
        KeyError: If dimension ID is not found
        
    Example:
        >>> get_dimension_description('D1')
        'Evalúa la calidad del diagnóstico territorial, líneas base cuantitativas...'
    """
    _initialize_constants()
    
    if dim_id not in CANONICAL_DIMENSIONS:
        raise KeyError(
            f"Dimension '{dim_id}' not found. "
            f"Available dimensions: {list(CANONICAL_DIMENSIONS.keys())}"
        )
    
    return CANONICAL_DIMENSIONS[dim_id]["description"]


def get_dimension_info(dim_id: str) -> dict[str, Any]:
    """
    Get complete information dictionary for a dimension.
    
    Args:
        dim_id: Dimension identifier (e.g., 'D1', 'D2', ... 'D6')
        
    Returns:
        dict: Complete dimension information including code, name, label, description, etc.
        
    Raises:
        KeyError: If dimension ID is not found
        
    Example:
        >>> info = get_dimension_info('D1')
        >>> info['name']
        'INSUMOS'
        >>> info['code']
        'DIM01'
    """
    _initialize_constants()
    
    if dim_id not in CANONICAL_DIMENSIONS:
        raise KeyError(
            f"Dimension '{dim_id}' not found. "
            f"Available dimensions: {list(CANONICAL_DIMENSIONS.keys())}"
        )
    
    return CANONICAL_DIMENSIONS[dim_id].copy()


def get_policy_description(policy_id: str) -> str:
    """
    Get human-readable name/description for a policy area.
    
    Args:
        policy_id: Policy area identifier (e.g., 'PA01', 'PA02', ... 'PA10')
        
    Returns:
        str: Name of the policy area in Spanish
        
    Raises:
        KeyError: If policy area ID is not found
        
    Example:
        >>> get_policy_description('PA01')
        'Derechos de las mujeres e igualdad de género'
    """
    _initialize_constants()
    
    if policy_id not in CANONICAL_POLICY_AREAS:
        raise KeyError(
            f"Policy area '{policy_id}' not found. "
            f"Available policy areas: {list(CANONICAL_POLICY_AREAS.keys())}"
        )
    
    return CANONICAL_POLICY_AREAS[policy_id]["name"]


def get_all_dimensions() -> list[str]:
    """
    Get list of all dimension IDs in canonical order.
    
    Returns:
        list[str]: List of dimension IDs (e.g., ['D1', 'D2', 'D3', 'D4', 'D5', 'D6'])
        
    Example:
        >>> get_all_dimensions()
        ['D1', 'D2', 'D3', 'D4', 'D5', 'D6']
    """
    _initialize_constants()
    return list(CANONICAL_DIMENSIONS.keys())


def get_all_policy_areas() -> list[str]:
    """
    Get list of all policy area IDs in canonical order.
    
    Returns:
        list[str]: List of policy area IDs (e.g., ['PA01', 'PA02', ..., 'PA10'])
        
    Example:
        >>> get_all_policy_areas()
        ['PA01', 'PA02', 'PA03', 'PA04', 'PA05', 'PA06', 'PA07', 'PA08', 'PA09', 'PA10']
    """
    _initialize_constants()
    return list(CANONICAL_POLICY_AREAS.keys())


# =============================================================================
# Module Initialization
# =============================================================================

# Initialize constants when module is imported
_initialize_constants()


__all__ = [
    "CANONICAL_DIMENSIONS",
    "CANONICAL_POLICY_AREAS",
    "get_dimension_description",
    "get_dimension_info",
    "get_policy_description",
    "get_all_dimensions",
    "get_all_policy_areas",
]
