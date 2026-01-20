"""
Phase 9 Output Contract
========================

PHASE_LABEL: Phase 9
Module: contracts/phase9_output_contract.py
Purpose: Defines the output specifications and validation for Phase 9

This contract specifies the expected outputs, their types, validation rules,
and postconditions for Phase 9 execution.

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
Date: 2026-01-19
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol

__version__ = "1.0.0"
__phase__ = 9

logger = logging.getLogger(__name__)


@dataclass
class Phase9Output:
    """Output data structure for Phase 9."""
    
    # Generated reports
    institutional_reports: list[dict[str, Any]]
    
    # Entity annexes
    entity_annexes: list[dict[str, Any]]
    
    # Metadata
    generation_metadata: dict[str, Any]
    
    # Quality metrics
    quality_metrics: dict[str, Any]


class Phase9OutputValidator(Protocol):
    """Protocol defining output validation interface for Phase 9."""
    
    def validate_output(self, output_data: Phase9Output) -> tuple[bool, list[str]]:
        """Validate Phase 9 output data.
        
        Args:
            output_data: Output data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        ...


def validate_phase9_output(output_data: Phase9Output) -> tuple[bool, list[str]]:
    """Validate output from Phase 9.
    
    Args:
        output_data: Output data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate institutional reports
    if not hasattr(output_data, 'institutional_reports'):
        errors.append("Missing institutional_reports in output")
    elif not isinstance(output_data.institutional_reports, list):
        errors.append("Institutional reports must be a list")
    elif len(output_data.institutional_reports) == 0:
        errors.append("Institutional reports list cannot be empty")
    
    # Validate entity annexes
    if not hasattr(output_data, 'entity_annexes'):
        errors.append("Missing entity_annexes in output")
    elif not isinstance(output_data.entity_annexes, list):
        errors.append("Entity annexes must be a list")
    
    # Validate generation metadata
    if not hasattr(output_data, 'generation_metadata'):
        errors.append("Missing generation_metadata in output")
    elif not isinstance(output_data.generation_metadata, dict):
        errors.append("Generation metadata must be a dictionary")
    
    # Validate quality metrics
    if not hasattr(output_data, 'quality_metrics'):
        errors.append("Missing quality_metrics in output")
    elif not isinstance(output_data.quality_metrics, dict):
        errors.append("Quality metrics must be a dictionary")
    
    is_valid = len(errors) == 0
    if not is_valid:
        logger.error(f"Phase 9 output validation failed: {errors}")
    
    return is_valid, errors


def get_expected_outputs() -> list[str]:
    """Get list of expected output fields from Phase 9.
    
    Returns:
        List of expected output field names
    """
    return [
        "institutional_reports",
        "entity_annexes", 
        "generation_metadata",
        "quality_metrics"
    ]


def verify_output_structure(output_data: Phase9Output) -> tuple[bool, list[str]]:
    """Verify the structure of Phase 9 output.
    
    Args:
        output_data: Output data to verify
        
    Returns:
        Tuple of (structure_valid, list_of_issues)
    """
    issues = []
    
    # Check report structure
    for i, report in enumerate(getattr(output_data, 'institutional_reports', [])):
        if not isinstance(report, dict):
            issues.append(f"Report {i} is not a dictionary")
            continue
            
        required_fields = ['report_id', 'content', 'metadata', 'timestamp']
        for field in required_fields:
            if field not in report:
                issues.append(f"Report {i} missing required field: {field}")
    
    # Check annex structure
    for i, annex in enumerate(getattr(output_data, 'entity_annexes', [])):
        if not isinstance(annex, dict):
            issues.append(f"Annex {i} is not a dictionary")
            continue
            
        required_fields = ['entity_id', 'annex_content', 'institutional_linkage']
        for field in required_fields:
            if field not in annex:
                issues.append(f"Annex {i} missing required field: {field}")
    
    structure_valid = len(issues) == 0
    return structure_valid, issues


def get_consumer_downstream() -> str:
    """Get the downstream consumer of Phase 9 output.
    
    Returns:
        Description of downstream consumer
    """
    return "Institutional delivery system and final pipeline output"


def check_postconditions(output_data: Phase9Output) -> tuple[bool, list[str]]:
    """Check postconditions for Phase 9 execution.
    
    Args:
        output_data: Output data to check postconditions for
        
    Returns:
        Tuple of (postconditions_met, list_of_failures)
    """
    failures = []
    
    # Check that we have at least one institutional report
    if (hasattr(output_data, 'institutional_reports') and 
        len(output_data.institutional_reports) < 1):
        failures.append("At least 1 institutional report required in output")
    
    # Check that generation metadata is populated
    metadata = getattr(output_data, 'generation_metadata', {})
    if not metadata:
        failures.append("Generation metadata cannot be empty")
    elif 'timestamp' not in metadata:
        failures.append("Generation metadata must include timestamp")
    elif 'phase_id' not in metadata or metadata.get('phase_id') != 9:
        failures.append("Generation metadata must include correct phase_id (9)")
    
    postconditions_met = len(failures) == 0
    return postconditions_met, failures


def verify_output_contract() -> bool:
    """Verify the Phase 9 output contract.
    
    Returns:
        True if contract is properly defined
    """
    print("Phase 9 Output Contract Verification")
    print("=" * 60)
    
    expected_outputs = get_expected_outputs()
    print(f"Expected outputs: {expected_outputs}")
    
    print(f"Validation function: {validate_phase9_output.__name__}")
    print(f"Postcondition checker: {check_postconditions.__name__}")
    print(f"Downstream consumer: {get_consumer_downstream()}")
    
    return True


def get_certification_requirements() -> list[str]:
    """Get certification requirements for Phase 9 output.
    
    Returns:
        List of certification requirements
    """
    return [
        "All institutional reports must be properly structured",
        "Entity annexes must link to institutional entities",
        "Quality metrics must be computed and valid",
        "Metadata must include all required fields",
        "Output must satisfy downstream consumer requirements"
    ]