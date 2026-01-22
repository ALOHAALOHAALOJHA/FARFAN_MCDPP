"""
Phase 0 → Phase 1 Bridge Contract
=================================

This module defines the explicit transformation from Phase 0 output
(WiringComponents) to Phase 1 input (CanonicalInput).

INTERPHASE CONTRACT:
    Source: Phase 0 (phase0_90_02_bootstrap.py:WiringComponents)
    Target: Phase 1 (phase1_13_00_cpp_ingestion.py:CanonicalInput)
    Transformation: Extract and validate required fields

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import hashlib


@dataclass(frozen=True)
class Phase0OutputContract:
    """Contract defining expected Phase 0 output structure.

    Attributes:
        document_path: Path to input PDF document
        document_hash: SHA-256 hash of the PDF document
        questionnaire_hash: SHA-256 hash of questionnaire file
        preprocessed_text: Optional preprocessed text content
        validation_passed: Whether Phase 0 validation passed
        pdm_profile: Optional PDM structural profile
        signal_registry: Optional signal registry from factory
        seed: Random seed for reproducibility
    """

    document_path: str
    document_hash: str  # SHA-256
    questionnaire_hash: str  # SHA-256
    preprocessed_text: Optional[str]
    validation_passed: bool
    pdm_profile: Optional[Any] = None
    signal_registry: Optional[Any] = None
    seed: int = 42


class Phase0ToPhase1BridgeError(Exception):
    """Raised when Phase 0 → Phase 1 bridge transformation fails."""

    pass


def extract_from_wiring_components(wiring: Any) -> Phase0OutputContract:
    """
    Extract Phase 0 output contract from WiringComponents.

    This function extracts all required and optional fields from the
    WiringComponents object produced by Phase 0 bootstrap.

    Args:
        wiring: WiringComponents from Phase 0 bootstrap

    Returns:
        Phase0OutputContract with validated fields

    Raises:
        Phase0ToPhase1BridgeError: If required fields are missing

    Example:
        >>> from farfan_pipeline.phases.Phase_00.phase0_90_02_bootstrap import WiringComponents
        >>> wiring = WiringComponents(...)
        >>> contract = extract_from_wiring_components(wiring)
        >>> print(contract.document_path)
        '/path/to/document.pdf'
    """
    # Required fields
    document_path = getattr(wiring, 'document_path', None)
    if document_path is None:
        raise Phase0ToPhase1BridgeError("WiringComponents missing document_path")

    document_hash = getattr(wiring, 'document_hash', None)
    if document_hash is None:
        # Try to compute from document
        document_hash = _compute_document_hash(document_path)

    questionnaire_hash = getattr(wiring, 'questionnaire_hash', "")
    preprocessed_text = getattr(wiring, 'preprocessed_text', None)
    validation_passed = getattr(wiring, 'validation_passed', True)

    # Optional fields
    pdm_profile = getattr(wiring, 'pdm_profile', None)
    signal_registry = getattr(wiring, 'signal_registry', None)
    seed = getattr(wiring, 'seed', 42)

    return Phase0OutputContract(
        document_path=str(document_path),
        document_hash=document_hash,
        questionnaire_hash=questionnaire_hash,
        preprocessed_text=preprocessed_text,
        validation_passed=validation_passed,
        pdm_profile=pdm_profile,
        signal_registry=signal_registry,
        seed=seed,
    )


def transform_to_canonical_input(
    phase0_output: Phase0OutputContract,
) -> Any:
    """
    Transform Phase 0 output to Phase 1 CanonicalInput.

    Args:
        phase0_output: Validated Phase 0 output contract

    Returns:
        CanonicalInput ready for Phase 1 execution

    Example:
        >>> contract = Phase0OutputContract(...)
        >>> canonical_input = transform_to_canonical_input(contract)
        >>> print(canonical_input.validation_passed)
        True
    """
    # Import here to avoid circular dependency
    from farfan_pipeline.phases.Phase_01.phase1_01_00_cpp_models import CanonicalInput

    return CanonicalInput(
        document_path=phase0_output.document_path,
        document_sha256=phase0_output.document_hash,
        questionnaire_sha256=phase0_output.questionnaire_hash,
        validation_passed=phase0_output.validation_passed,
        preprocessed_text=phase0_output.preprocessed_text,
    )


def bridge_phase0_to_phase1(wiring: Any) -> Any:
    """
    Complete bridge from WiringComponents to CanonicalInput.

    This is the main entry point for Phase 0 → Phase 1 bridging.
    It combines extraction and transformation into a single operation.

    Args:
        wiring: WiringComponents from Phase 0

    Returns:
        CanonicalInput for Phase 1

    Raises:
        Phase0ToPhase1BridgeError: If transformation fails

    Example:
        >>> from farfan_pipeline.phases.Phase_00.phase0_90_02_bootstrap import WiringComponents
        >>> from farfan_pipeline.phases.Phase_01.interphase import bridge_phase0_to_phase1
        >>>
        >>> wiring = WiringComponents(...)
        >>> canonical_input = bridge_phase0_to_phase1(wiring)
        >>> # Use canonical_input in Phase 1
    """
    phase0_output = extract_from_wiring_components(wiring)
    return transform_to_canonical_input(phase0_output)


def _compute_document_hash(document_path: str) -> str:
    """
    Compute SHA-256 hash of document.

    Args:
        document_path: Path to document file

    Returns:
        Hex-encoded SHA-256 hash

    Raises:
        Phase0ToPhase1BridgeError: If hash computation fails
    """
    try:
        with open(document_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        raise Phase0ToPhase1BridgeError(f"Failed to compute document hash: {e}")


__all__ = [
    "Phase0OutputContract",
    "Phase0ToPhase1BridgeError",
    "bridge_phase0_to_phase1",
    "extract_from_wiring_components",
    "transform_to_canonical_input",
]
