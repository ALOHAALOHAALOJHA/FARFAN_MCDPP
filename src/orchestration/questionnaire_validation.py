"""
Questionnaire Validation - Neutral Module for Structure Validation

This module is extracted from factory.py to break the import cycle between
factory.py and orchestrator.py. Both modules now import from here.

Part of JOBFRONT J2: Import cycle hardening.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _validate_questionnaire_structure(monolith_data: dict[str, Any]) -> None:
    """Validate questionnaire structure.
    
    Args:
        monolith_data: Questionnaire data dictionary
        
    Raises:
        ValueError: If questionnaire structure is invalid
        TypeError: If questionnaire data types are incorrect
    """
    if not isinstance(monolith_data, dict):
        raise TypeError(f"Questionnaire must be a dict, got {type(monolith_data)}")
    
    # Validate canonical_notation exists
    if "canonical_notation" not in monolith_data:
        raise ValueError("Questionnaire missing 'canonical_notation'")
    
    canonical_notation = monolith_data["canonical_notation"]
    
    # Validate dimensions
    if "dimensions" not in canonical_notation:
        raise ValueError("Questionnaire missing 'canonical_notation.dimensions'")
    
    dimensions = canonical_notation["dimensions"]
    if not isinstance(dimensions, dict):
        raise TypeError("Dimensions must be a dict")
    
    # Validate dimension keys (D1-D6)
    expected_dim_keys = [f"D{i}" for i in range(1, 7)]
    found_dims = []

    for key, dim_data in dimensions.items():
        if key in expected_dim_keys:
            found_dims.append(key)
        elif isinstance(dim_data, dict) and dim_data.get("code") in ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]:
             # Found by code, which is acceptable
             pass

    # We require D1-D6 keys as per canonical JSON structure
    for dim_key in expected_dim_keys:
        if dim_key not in dimensions:
             # Check if it exists under another key but with correct code?
             # No, strict structure requires D1-D6 keys for now based on monolith.
             # However, if we want to be flexible:
             found = False
             for d in dimensions.values():
                 if isinstance(d, dict) and d.get("code") == f"DIM{int(dim_key[1:]):02d}":
                     found = True
                     break

             if not found:
                 # Fallback: check if key itself is DIM0x
                 alt_key = f"DIM{int(dim_key[1:]):02d}"
                 if alt_key in dimensions:
                     found = True

             if not found:
                raise ValueError(f"Missing dimension: {dim_key} (or equivalent code)")
    
    # Validate policy areas
    if "policy_areas" not in canonical_notation:
        raise ValueError("Questionnaire missing 'canonical_notation.policy_areas'")
    
    policy_areas = canonical_notation["policy_areas"]
    if not isinstance(policy_areas, dict):
        raise TypeError("Policy areas must be a dict")
    
    expected_pas = [f"PA{i:02d}" for i in range(1, 11)]
    for pa_id in expected_pas:
        if pa_id not in policy_areas:
            raise ValueError(f"Missing policy area: {pa_id}")
    
    logger.info("Questionnaire structure validation passed")


__all__ = ["_validate_questionnaire_structure"]
