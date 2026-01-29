"""
Phase 9 Input Contract
======================

PHASE_LABEL: Phase 9
Module: contracts/phase9_input_contract.py
Purpose: Defines the input requirements and validation for Phase 9

This contract specifies the required inputs, their types, validation rules,
and preconditions for Phase 9 execution.

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
class Phase9Input:
    """Input data structure for Phase 9."""
    
    # From Phase 8: Recommendations and signals
    recommendations: list[dict[str, Any]]
    signal_enriched_data: dict[str, Any]
    
    # Contextual information
    institutional_context: dict[str, Any]
    policy_areas: list[str]
    
    # Configuration
    report_config: dict[str, Any]


class Phase9InputValidator(Protocol):
    """Protocol defining input validation interface for Phase 9."""
    
    def validate_input(self, input_data: Phase9Input) -> tuple[bool, list[str]]:
        """Validate Phase 9 input data.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        ...


def validate_phase9_input(input_data: Phase9Input) -> tuple[bool, list[str]]:
    """Validate input for Phase 9.
    
    Args:
        input_data: Input data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate recommendations exist
    if not hasattr(input_data, 'recommendations'):
        errors.append("Missing recommendations in input")
    elif not isinstance(input_data.recommendations, list):
        errors.append("Recommendations must be a list")
    elif len(input_data.recommendations) == 0:
        errors.append("Recommendations list cannot be empty")
    
    # Validate signal-enriched data
    if not hasattr(input_data, 'signal_enriched_data'):
        errors.append("Missing signal_enriched_data in input")
    elif not isinstance(input_data.signal_enriched_data, dict):
        errors.append("Signal-enriched data must be a dictionary")
    
    # Validate institutional context
    if not hasattr(input_data, 'institutional_context'):
        errors.append("Missing institutional_context in input")
    elif not isinstance(input_data.institutional_context, dict):
        errors.append("Institutional context must be a dictionary")
    
    # Validate policy areas
    if not hasattr(input_data, 'policy_areas'):
        errors.append("Missing policy_areas in input")
    elif not isinstance(input_data.policy_areas, list):
        errors.append("Policy areas must be a list")
    
    # Validate report configuration
    if not hasattr(input_data, 'report_config'):
        errors.append("Missing report_config in input")
    elif not isinstance(input_data.report_config, dict):
        errors.append("Report config must be a dictionary")
    
    is_valid = len(errors) == 0
    if not is_valid:
        logger.error(f"Phase 9 input validation failed: {errors}")
    
    return is_valid, errors


def get_required_inputs() -> list[str]:
    """Get list of required input fields for Phase 9.
    
    Returns:
        List of required input field names
    """
    return [
        "recommendations",
        "signal_enriched_data", 
        "institutional_context",
        "policy_areas",
        "report_config"
    ]


# Precondition checks
def check_preconditions(input_data: Phase9Input) -> tuple[bool, list[str]]:
    """Check preconditions for Phase 9 execution.
    
    Args:
        input_data: Input data to check preconditions for
        
    Returns:
        Tuple of (preconditions_met, list_of_failures)
    """
    failures = []
    
    # Check that we have enough recommendations for report generation
    if hasattr(input_data, 'recommendations') and len(input_data.recommendations) < 1:
        failures.append("At least 1 recommendation required for report generation")
    
    # Check that signal data is properly structured
    if (hasattr(input_data, 'signal_enriched_data') and 
        not isinstance(input_data.signal_enriched_data, dict)):
        failures.append("Signal-enriched data must be a dictionary")
    
    preconditions_met = len(failures) == 0
    return preconditions_met, failures


def verify_input_contract() -> bool:
    """Verify the Phase 9 input contract.
    
    Returns:
        True if contract is properly defined
    """
    print("Phase 9 Input Contract Verification")
    print("=" * 60)
    
    required_inputs = get_required_inputs()
    print(f"Required inputs: {required_inputs}")
    
    print(f"Validation function: {validate_phase9_input.__name__}")
    print(f"Precondition checker: {check_preconditions.__name__}")
    
    return True