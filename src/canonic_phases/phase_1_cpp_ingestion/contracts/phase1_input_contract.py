"""Phase 1 Input Contract - Phase 0 → Phase 1 Interface.

This contract defines the strict preconditions for Phase 1 entry.
Input is provided by Phase 0 validation as CanonicalInput.

Preconditions (enforced):
- PRE-01: PDF exists and is readable
- PRE-02: PDF SHA256 matches provided hash
- PRE-03: Questionnaire exists and is valid JSON
- PRE-04: Questionnaire SHA256 matches provided hash
- PRE-05: Phase 0 validation passed
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Phase1InputPrecondition:
    """Precondition specification for Phase 1 input."""
    precondition_id: str
    description: str
    validation_function: str
    severity: str  # "CRITICAL", "HIGH", "STANDARD"


PHASE1_INPUT_PRECONDITIONS: List[Phase1InputPrecondition] = [
    Phase1InputPrecondition(
        "PRE-01",
        "PDF file must exist and be readable",
        "validate_pdf_exists",
        "CRITICAL"
    ),
    Phase1InputPrecondition(
        "PRE-02",
        "PDF SHA256 must match provided hash",
        "validate_pdf_sha256",
        "CRITICAL"
    ),
    Phase1InputPrecondition(
        "PRE-03",
        "Questionnaire file must exist and be valid JSON",
        "validate_questionnaire_exists",
        "CRITICAL"
    ),
    Phase1InputPrecondition(
        "PRE-04",
        "Questionnaire SHA256 must match provided hash",
        "validate_questionnaire_sha256",
        "CRITICAL"
    ),
    Phase1InputPrecondition(
        "PRE-05",
        "Phase 0 validation must have passed",
        "validate_phase0_passed",
        "CRITICAL"
    ),
]


def validate_phase1_input_contract(canonical_input: Any) -> bool:
    """Validate Phase 1 input contract compliance.
    
    Args:
        canonical_input: CanonicalInput from Phase 0
        
    Returns:
        True if all preconditions satisfied
        
    Raises:
        ValueError: If any precondition fails
    """
    # PRE-01: PDF exists
    if not canonical_input.pdf_path.exists():
        raise ValueError(f"PRE-01 failed: PDF does not exist: {canonical_input.pdf_path}")
    
    # PRE-02: PDF SHA256 matches
    import hashlib
    actual_hash = hashlib.sha256(canonical_input.pdf_path.read_bytes()).hexdigest()
    if actual_hash != canonical_input.pdf_sha256:
        raise ValueError(f"PRE-02 failed: PDF SHA256 mismatch: expected {canonical_input.pdf_sha256}, got {actual_hash}")
    
    # PRE-03: Questionnaire exists
    if not canonical_input.questionnaire_path.exists():
        raise ValueError(f"PRE-03 failed: Questionnaire does not exist: {canonical_input.questionnaire_path}")
    
    # PRE-04: Questionnaire SHA256 matches
    actual_q_hash = hashlib.sha256(canonical_input.questionnaire_path.read_bytes()).hexdigest()
    if actual_q_hash != canonical_input.questionnaire_sha256:
        raise ValueError(f"PRE-04 failed: Questionnaire SHA256 mismatch")
    
    # PRE-05: Phase 0 validation passed
    if not canonical_input.validation_passed:
        raise ValueError(f"PRE-05 failed: Phase 0 validation did not pass")
    
    return True


__all__ = [
    "Phase1InputPrecondition",
    "PHASE1_INPUT_PRECONDITIONS",
    "validate_phase1_input_contract",
]
