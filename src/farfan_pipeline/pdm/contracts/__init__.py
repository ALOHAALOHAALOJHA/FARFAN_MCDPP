"""
PDM Contracts Module

Provides contracts for PDM profile validation and phase handoffs.

Components:
    - PDMProfileContract: Validates PDM profile presence and integrity
    - SP2Obligations: SP2 constitutional obligations
    - Phase1Phase2HandoffContract: Validates Phase 1 to Phase 2 data transfer
    - PrerequisiteError: Raised when prerequisites not met
    - ValidationError: Raised when validation fails

Author: FARFAN Engineering Team
Version: 1.0.0
"""

from .pdm_contracts import (
    PDMProfileContract,
    SP2Obligations,
    Phase1Phase2HandoffContract,
    PrerequisiteError,
    ValidationError as PDMValidationError,
)

# Convenience function for enforcing profile presence
def enforce_profile_presence(profile_path=None):
    """Convenience wrapper for PDMProfileContract.enforce_profile_presence"""
    return PDMProfileContract.enforce_profile_presence(profile_path)

__all__ = [
    "PDMProfileContract",
    "SP2Obligations",
    "Phase1Phase2HandoffContract",
    "PrerequisiteError",
    "PDMValidationError",
    "enforce_profile_presence",
]
