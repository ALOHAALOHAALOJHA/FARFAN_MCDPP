"""
Phase 2 Output Contract
=======================

PHASE_LABEL: Phase 2
Module: contracts/phase2_output_contract.py
Purpose: Defines and validates output postconditions and compatibility for Phase 3

This contract ensures that Phase 2 produces complete, valid, and compatible
output for consumption by Phase 3 (Scoring).

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
Date: 2026-01-13
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Final

__version__ = "1.0.0"
__phase__ = 2

# =============================================================================
# OUTPUT POSTCONDITIONS
# =============================================================================

@dataclass(frozen=True)
class Phase2OutputPostconditions:
    """Defines all postconditions that MUST be satisfied after Phase 2 execution."""
    
    # POST-001: Result completeness
    EXPECTED_RESULT_COUNT: Final[int] = 300
    ALL_CONTRACTS_MUST_EXECUTE: Final[bool] = True
    
    # POST-002: Chunk coverage
    EXPECTED_CHUNKS_PROCESSED: Final[int] = 60
    COMPLETE_CHUNK_COVERAGE: Final[bool] = True
    
    # POST-003: Evidence extraction
    ALL_RESULTS_MUST_HAVE_EVIDENCE: Final[bool] = True
    EVIDENCE_MUST_BE_STRUCTURED: Final[bool] = True
    
    # POST-004: Narrative synthesis
    ALL_RESULTS_MUST_HAVE_NARRATIVE: Final[bool] = True
    NARRATIVE_MIN_LENGTH: Final[int] = 100  # characters
    
    # POST-005: Confidence scores
    ALL_RESULTS_MUST_HAVE_SCORES: Final[bool] = True
    CONFIDENCE_RANGE: Final[tuple[float, float]] = (0.0, 1.0)
    
    # POST-006: Provenance tracking
    ALL_RESULTS_MUST_HAVE_PROVENANCE: Final[bool] = True
    PROVENANCE_MUST_INCLUDE_SHA256: Final[bool] = True
    
    # POST-007: Output schema
    REQUIRED_OUTPUT_SCHEMA_VERSION: Final[str] = "Phase2Result-2025.1"
    
    # POST-008: Phase 3 compatibility
    MUST_BE_PHASE3_COMPATIBLE: Final[bool] = True
    CERTIFICATE_MUST_BE_GENERATED: Final[bool] = True


@dataclass
class Phase2Result:
    """Structure for a single Phase 2 question result."""
    question_id: str
    policy_area: str
    narrative: str
    evidence: dict[str, Any]
    confidence_score: float
    provenance: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate this result against postconditions."""
        errors = []
        
        if not self.narrative or len(self.narrative) < 100:
            errors.append(f"Narrative too short: {len(self.narrative)} chars")
        
        if not self.evidence:
            errors.append("Evidence is empty")
        
        if not (0.0 <= self.confidence_score <= 1.0):
            errors.append(f"Confidence score out of range: {self.confidence_score}")
        
        if not self.provenance:
            errors.append("Provenance is empty")
        elif 'sha256' not in self.provenance:
            errors.append("Provenance missing SHA-256 hash")
        
        return len(errors) == 0, errors


@dataclass
class Phase2Output:
    """Complete output package from Phase 2."""
    results: list[Phase2Result]
    execution_metadata: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "Phase2Result-2025.1"
    
    def get_result_count(self) -> int:
        """Get the number of results."""
        return len(self.results)
    
    def get_chunk_coverage(self) -> set[str]:
        """Get the set of chunks covered by results."""
        chunks = set()
        for result in self.results:
            if 'chunk_ids' in result.metadata:
                chunks.update(result.metadata['chunk_ids'])
        return chunks


class Phase2OutputContractError(Exception):
    """Raised when output contract validation fails."""
    pass


class Phase2OutputValidator:
    """Validates that all output postconditions are satisfied."""
    
    def __init__(self, postconditions: Phase2OutputPostconditions | None = None):
        self.postconditions = postconditions or Phase2OutputPostconditions()
    
    def validate_completeness(self, output: Phase2Output) -> tuple[bool, list[str]]:
        """
        Validate result completeness.
        
        Args:
            output: Phase2Output object
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # POST-001: Check result count
        result_count = output.get_result_count()
        if result_count != self.postconditions.EXPECTED_RESULT_COUNT:
            errors.append(
                f"POST-001: Expected {self.postconditions.EXPECTED_RESULT_COUNT} results, "
                f"got {result_count}"
            )
        
        return len(errors) == 0, errors
    
    def validate_chunk_coverage(self, output: Phase2Output) -> tuple[bool, list[str]]:
        """
        Validate chunk coverage.
        
        Args:
            output: Phase2Output object
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # POST-002: Check chunk coverage
        chunks = output.get_chunk_coverage()
        if len(chunks) < self.postconditions.EXPECTED_CHUNKS_PROCESSED:
            errors.append(
                f"POST-002: Expected coverage of {self.postconditions.EXPECTED_CHUNKS_PROCESSED} chunks, "
                f"got {len(chunks)}"
            )
        
        return len(errors) == 0, errors
    
    def validate_individual_results(self, output: Phase2Output) -> tuple[bool, list[str]]:
        """
        Validate individual results.
        
        Args:
            output: Phase2Output object
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        all_errors = []
        
        for i, result in enumerate(output.results):
            is_valid, errors = result.validate()
            if not is_valid:
                all_errors.append(f"Result {i} ({result.question_id}): " + "; ".join(errors))
        
        return len(all_errors) == 0, all_errors
    
    def validate_schema(self, output: Phase2Output) -> tuple[bool, list[str]]:
        """
        Validate output schema version.
        
        Args:
            output: Phase2Output object
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # POST-007: Check schema version
        if output.schema_version != self.postconditions.REQUIRED_OUTPUT_SCHEMA_VERSION:
            errors.append(
                f"POST-007: Expected schema version "
                f"{self.postconditions.REQUIRED_OUTPUT_SCHEMA_VERSION}, "
                f"got {output.schema_version}"
            )
        
        return len(errors) == 0, errors
    
    def validate_all(self, output: Phase2Output) -> tuple[bool, list[str]]:
        """
        Validate all output postconditions.
        
        Args:
            output: Phase2Output object
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        all_errors = []
        
        is_valid, errors = self.validate_completeness(output)
        all_errors.extend(errors)
        
        is_valid, errors = self.validate_chunk_coverage(output)
        all_errors.extend(errors)
        
        is_valid, errors = self.validate_individual_results(output)
        all_errors.extend(errors)
        
        is_valid, errors = self.validate_schema(output)
        all_errors.extend(errors)
        
        return len(all_errors) == 0, all_errors


# =============================================================================
# PHASE 3 COMPATIBILITY CERTIFICATE
# =============================================================================

@dataclass
class Phase3CompatibilityCertificate:
    """Certificate ensuring Phase 2 output is compatible with Phase 3."""
    
    phase: int = 2
    status: str = "UNKNOWN"  # VALID, INVALID, WARNING
    timestamp: datetime = field(default_factory=datetime.now)
    validation_results: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    # Metrics
    total_results: int = 0
    valid_results: int = 0
    chunks_covered: int = 0
    
    # Hashes for integrity
    output_hash: str = ""
    certificate_version: str = "CERT-P2-2025.1"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert certificate to dictionary."""
        return {
            'phase': self.phase,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'validation_results': self.validation_results,
            'errors': self.errors,
            'warnings': self.warnings,
            'metrics': {
                'total_results': self.total_results,
                'valid_results': self.valid_results,
                'chunks_covered': self.chunks_covered,
            },
            'output_hash': self.output_hash,
            'certificate_version': self.certificate_version,
        }


def generate_phase3_compatibility_certificate(
    output: Phase2Output,
    strict: bool = True,
) -> Phase3CompatibilityCertificate:
    """
    Generate a Phase 3 compatibility certificate.
    
    Args:
        output: Phase2Output object
        strict: If True, any error results in INVALID status
        
    Returns:
        Phase3CompatibilityCertificate
    """
    validator = Phase2OutputValidator()
    is_valid, errors = validator.validate_all(output)
    
    certificate = Phase3CompatibilityCertificate()
    certificate.total_results = output.get_result_count()
    certificate.chunks_covered = len(output.get_chunk_coverage())
    
    if is_valid:
        certificate.status = "VALID"
        certificate.valid_results = certificate.total_results
    else:
        certificate.status = "INVALID" if strict else "WARNING"
        certificate.errors = errors
        
        # Count valid results
        valid_count = 0
        for result in output.results:
            is_result_valid, _ = result.validate()
            if is_result_valid:
                valid_count += 1
        certificate.valid_results = valid_count
    
    # Calculate output hash (simplified)
    import hashlib
    import json
    
    result_data = json.dumps(
        [r.question_id for r in output.results],
        sort_keys=True
    )
    certificate.output_hash = hashlib.sha256(result_data.encode()).hexdigest()
    
    certificate.validation_results = {
        'completeness': output.get_result_count() == 300,
        'chunk_coverage': certificate.chunks_covered >= 60,
        'schema_version': output.schema_version == "Phase2Result-2025.1",
    }
    
    return certificate


# =============================================================================
# CONTRACT VERIFICATION COMMAND
# =============================================================================

def verify_phase2_output_contract(
    output: Phase2Output,
    strict: bool = True,
) -> bool:
    """
    Command-line verification of Phase 2 output contract.
    
    Args:
        output: Phase2Output object
        strict: If True, raises exception on validation failure
        
    Returns:
        True if all postconditions satisfied
        
    Raises:
        Phase2OutputContractError: If validation fails and strict=True
    """
    validator = Phase2OutputValidator()
    is_valid, errors = validator.validate_all(output)
    
    if not is_valid:
        error_msg = "Phase 2 Output Contract Validation Failed:\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        if strict:
            raise Phase2OutputContractError(error_msg)
        print(error_msg)
        return False
    
    # Generate compatibility certificate
    certificate = generate_phase3_compatibility_certificate(output, strict)
    
    print("✓ Phase 2 Output Contract: ALL POSTCONDITIONS SATISFIED")
    print(f"✓ Phase 3 Compatibility Certificate: {certificate.status}")
    print(f"  - Total Results: {certificate.total_results}")
    print(f"  - Valid Results: {certificate.valid_results}")
    print(f"  - Chunks Covered: {certificate.chunks_covered}")
    print(f"  - Output Hash: {certificate.output_hash[:16]}...")
    
    return True
