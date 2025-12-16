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
    
    expected_dims = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]
    for dim_id in expected_dims:
        if dim_id not in dimensions:
            raise ValueError(f"Missing dimension: {dim_id}")
    
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
