"""
PDET Dimension Enrichment Utilities
====================================

This module provides utilities for loading and working with PDET context enrichment
data for each dimension. It integrates with the broader PDET enrichment system and
validation gates framework.

Usage:
    from canonic_questionnaire_central.dimensions import pdet_enrichment
    
    # Load PDET context for a dimension
    context = pdet_enrichment.load_dimension_pdet_context("DIM01_INSUMOS")
    
    # Get validation gates alignment
    gates = pdet_enrichment.get_validation_gates("DIM01_INSUMOS")
    
    # Get pillar mappings
    pillars = pdet_enrichment.get_pdet_pillars("DIM02_ACTIVIDADES")
    
    # Get policy area specific criteria
    criteria = pdet_enrichment.get_policy_area_criteria("DIM01_INSUMOS", "PA01")

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass


# Path to dimensions directory
_DIMENSIONS_DIR = Path(__file__).parent


@dataclass
class ValidationGate:
    """Validation gate alignment for a dimension."""
    gate_number: int
    gate_name: str
    required_scope: str | None
    allowed_signal_types: list[str]
    estimated_value_add: float | None
    required_capabilities: list[str]
    flow_id: str | None
    justification: str


@dataclass
class PdetPillar:
    """PDET pillar mapping for a dimension."""
    pillar_id: str
    pillar_name: str
    relevance: str
    relevance_score: float
    requirements: list[str]


@dataclass
class PolicyAreaCriteria:
    """Policy area specific criteria for a dimension."""
    policy_area_id: str
    required_elements: list[str]
    pdet_subregions_high_priority: list[str]
    key_indicators: list[str]


def load_dimension_pdet_context(dimension_id: str) -> dict[str, Any]:
    """Load PDET context for a dimension.
    
    Args:
        dimension_id: Dimension identifier (e.g., "DIM01_INSUMOS")
        
    Returns:
        Dict with PDET context data
        
    Raises:
        FileNotFoundError: If dimension or PDET context file not found
        json.JSONDecodeError: If PDET context file is invalid JSON
    """
    dimension_dir = _DIMENSIONS_DIR / dimension_id
    if not dimension_dir.exists():
        raise FileNotFoundError(f"Dimension directory not found: {dimension_id}")
    
    pdet_context_file = dimension_dir / "pdet_context.json"
    if not pdet_context_file.exists():
        raise FileNotFoundError(f"PDET context file not found for dimension: {dimension_id}")
    
    with open(pdet_context_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_validation_gates(dimension_id: str) -> dict[str, ValidationGate]:
    """Get validation gates alignment for a dimension.
    
    Args:
        dimension_id: Dimension identifier
        
    Returns:
        Dict mapping gate name to ValidationGate object
    """
    context = load_dimension_pdet_context(dimension_id)
    gates_data = context.get("validation_gates_alignment", {})
    
    gates = {}
    
    # Gate 1 - Scope
    gate1 = gates_data.get("gate_1_scope", {})
    gates["gate_1_scope"] = ValidationGate(
        gate_number=1,
        gate_name="Scope Validity",
        required_scope=gate1.get("required_scope"),
        allowed_signal_types=gate1.get("allowed_signal_types", []),
        estimated_value_add=None,
        required_capabilities=[],
        flow_id=None,
        justification=gate1.get("justification", "")
    )
    
    # Gate 2 - Value Add
    gate2 = gates_data.get("gate_2_value_add", {})
    gates["gate_2_value_add"] = ValidationGate(
        gate_number=2,
        gate_name="Value Contribution",
        required_scope=None,
        allowed_signal_types=[],
        estimated_value_add=gate2.get("estimated_value_add"),
        required_capabilities=[],
        flow_id=None,
        justification=gate2.get("justification", "")
    )
    
    # Gate 3 - Capability
    gate3 = gates_data.get("gate_3_capability", {})
    gates["gate_3_capability"] = ValidationGate(
        gate_number=3,
        gate_name="Consumer Capability",
        required_scope=None,
        allowed_signal_types=[],
        estimated_value_add=None,
        required_capabilities=gate3.get("required_capabilities", []),
        flow_id=None,
        justification=gate3.get("justification", "")
    )
    
    # Gate 4 - Channel
    gate4 = gates_data.get("gate_4_channel", {})
    gates["gate_4_channel"] = ValidationGate(
        gate_number=4,
        gate_name="Channel Authenticity",
        required_scope=None,
        allowed_signal_types=[],
        estimated_value_add=None,
        required_capabilities=[],
        flow_id=gate4.get("flow_id"),
        justification=gate4.get("justification", "")
    )
    
    return gates


def get_pdet_pillars(dimension_id: str, include_secondary: bool = False) -> list[PdetPillar]:
    """Get PDET pillar mappings for a dimension.
    
    Args:
        dimension_id: Dimension identifier
        include_secondary: Whether to include secondary pillars
        
    Returns:
        List of PdetPillar objects
    """
    context = load_dimension_pdet_context(dimension_id)
    pillar_mapping = context.get("pdet_pillar_mapping", {})
    
    pillars = []
    
    # Primary pillars
    for pillar_data in pillar_mapping.get("primary_pillars", []):
        pillars.append(PdetPillar(
            pillar_id=pillar_data.get("pillar_id", ""),
            pillar_name=pillar_data.get("pillar_name", ""),
            relevance=pillar_data.get("relevance", ""),
            relevance_score=pillar_data.get("relevance_score", 0.0),
            requirements=pillar_data.get("diagnostic_requirements", 
                                        pillar_data.get("activity_requirements",
                                        pillar_data.get("product_requirements",
                                        pillar_data.get("outcome_requirements",
                                        pillar_data.get("impact_requirements", [])))))
        ))
    
    # Secondary pillars if requested
    if include_secondary:
        for pillar_data in pillar_mapping.get("secondary_pillars", []):
            pillars.append(PdetPillar(
                pillar_id=pillar_data.get("pillar_id", ""),
                pillar_name=pillar_data.get("pillar_name", ""),
                relevance=pillar_data.get("relevance", ""),
                relevance_score=pillar_data.get("relevance_score", 0.0),
                requirements=pillar_data.get("diagnostic_requirements",
                                            pillar_data.get("activity_requirements", []))
            ))
    
    return pillars


def get_policy_area_criteria(dimension_id: str, policy_area_id: str) -> PolicyAreaCriteria | None:
    """Get policy area specific criteria for a dimension.
    
    Args:
        dimension_id: Dimension identifier
        policy_area_id: Policy area identifier (e.g., "PA01")
        
    Returns:
        PolicyAreaCriteria object or None if not found
    """
    context = load_dimension_pdet_context(dimension_id)
    pa_specificity = context.get("pdet_specific_criteria", {}).get("policy_area_specificity", {})
    
    if not pa_specificity:
        pa_specificity = context.get("policy_area_specificity", {})
    
    # Try exact match first
    pa_data = pa_specificity.get(policy_area_id)
    
    # Try with underscore format (e.g., PA01_Gender)
    if not pa_data:
        for key in pa_specificity.keys():
            if key.startswith(policy_area_id):
                pa_data = pa_specificity[key]
                break
    
    if not pa_data:
        return None
    
    return PolicyAreaCriteria(
        policy_area_id=policy_area_id,
        required_elements=pa_data.get("required_diagnostics", 
                                     pa_data.get("required_activities",
                                     pa_data.get("required_outcomes", []))),
        pdet_subregions_high_priority=pa_data.get("pdet_subregions_high_priority", []),
        key_indicators=pa_data.get("key_indicators", [])
    )


def get_common_gaps(dimension_id: str) -> dict[str, dict[str, Any]]:
    """Get common planning gaps for a dimension.
    
    Args:
        dimension_id: Dimension identifier
        
    Returns:
        Dict mapping gap ID to gap details (description, prevalence, impact, remediation)
    """
    context = load_dimension_pdet_context(dimension_id)
    
    # Try different gap keys based on dimension
    gap_keys = [
        "common_diagnostic_gaps",
        "common_design_gaps",
        "common_product_gaps",
        "common_outcome_gaps",
        "common_impact_gaps",
        "common_causal_gaps"
    ]
    
    for gap_key in gap_keys:
        if gap_key in context:
            return context[gap_key]
    
    return {}


def get_pdet_specific_criteria(dimension_id: str) -> dict[str, Any]:
    """Get PDET-specific evaluation criteria for a dimension.
    
    Args:
        dimension_id: Dimension identifier
        
    Returns:
        Dict with PDET-specific criteria
    """
    context = load_dimension_pdet_context(dimension_id)
    return context.get("pdet_specific_criteria", {})


def validate_dimension_enrichment(dimension_id: str) -> tuple[bool, list[str]]:
    """Validate PDET enrichment for a dimension.
    
    Args:
        dimension_id: Dimension identifier
        
    Returns:
        Tuple of (is_valid, list of validation errors)
    """
    errors = []
    
    try:
        context = load_dimension_pdet_context(dimension_id)
    except FileNotFoundError as e:
        return False, [str(e)]
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    
    # Check required sections
    required_sections = [
        "validation_gates_alignment",
        "pdet_pillar_mapping",
        "pdet_specific_criteria",
        "metadata"
    ]
    
    for section in required_sections:
        if section not in context:
            errors.append(f"Missing required section: {section}")
    
    # Check validation gates
    if "validation_gates_alignment" in context:
        gates = context["validation_gates_alignment"]
        required_gates = ["gate_1_scope", "gate_2_value_add", "gate_3_capability", "gate_4_channel"]
        for gate in required_gates:
            if gate not in gates:
                errors.append(f"Missing validation gate: {gate}")
    
    # Check metadata
    if "metadata" in context:
        metadata = context["metadata"]
        required_meta = ["created_at", "version", "author", "validated"]
        for meta in required_meta:
            if meta not in metadata:
                errors.append(f"Missing metadata field: {meta}")
    
    return len(errors) == 0, errors


def list_all_dimensions() -> list[str]:
    """List all dimensions with PDET enrichment.
    
    Returns:
        List of dimension IDs
    """
    dimensions = []
    
    for item in _DIMENSIONS_DIR.iterdir():
        if item.is_dir() and item.name.startswith("DIM"):
            pdet_file = item / "pdet_context.json"
            if pdet_file.exists():
                dimensions.append(item.name)
    
    return sorted(dimensions)


__all__ = [
    "load_dimension_pdet_context",
    "get_validation_gates",
    "get_pdet_pillars",
    "get_policy_area_criteria",
    "get_common_gaps",
    "get_pdet_specific_criteria",
    "validate_dimension_enrichment",
    "list_all_dimensions",
    "ValidationGate",
    "PdetPillar",
    "PolicyAreaCriteria",
]
