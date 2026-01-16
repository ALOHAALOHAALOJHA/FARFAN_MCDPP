"""
Phase 2 → Phase 3 Interface Adapter
===================================

PHASE_LABEL: Phase 2
Module: interphase/phase2_phase3_adapter.py
Purpose: Pure functional adapter for Phase 2 output to Phase 3 input transformation

This adapter resolves the structural incompatibilities between Phase 2 output
(Phase2Result-based) and Phase 3 input (MicroQuestionRun-based).

Version: 1.0.0
Date: 2026-01-13
Author: F.A.R.F.A.N Formal Verification System

INCOMPATIBILITIES RESOLVED:
- INC-P23-001: question_id format (Q001_PA01 → PA01-DIM01-Q001)
- INC-P23-002: Container type (Phase2Result → MicroQuestionRun)
- INC-P23-003: confidence location (result level → evidence level)
- INC-P23-004: question_global derivation
- INC-P23-005: base_slot derivation

INVARIANTS PRESERVED:
- Result count (300)
- Confidence range [0.0, 1.0]
- Evidence structure
- Question coverage

DECLARED INFORMATION LOSS:
- narrative: Not transferred (not required by Phase 3)
- provenance: Not transferred (not required by Phase 3)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Final, Protocol, runtime_checkable


# =============================================================================
# CONSTANTS
# =============================================================================

ADAPTER_VERSION: Final[str] = "1.0.0"
QUESTIONS_PER_DIMENSION: Final[int] = 5
TOTAL_DIMENSIONS: Final[int] = 6
TOTAL_POLICY_AREAS: Final[int] = 10
QUESTIONS_PER_PA: Final[int] = QUESTIONS_PER_DIMENSION * TOTAL_DIMENSIONS  # 30

# Regex patterns for question_id formats
PHASE2_QID_PATTERN: Final[re.Pattern] = re.compile(r'^Q(\d{3})_PA(\d{2})$')
PHASE3_QID_PATTERN: Final[re.Pattern] = re.compile(r'^PA(\d{2})-DIM(\d{2})-Q(\d{3})$')


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

@runtime_checkable
class Phase2ResultProtocol(Protocol):
    """Protocol for Phase 2 result structure."""
    
    @property
    def question_id(self) -> str:
        """Question ID in format Q###_PA##."""
        ...
    
    @property
    def policy_area(self) -> str:
        """Policy area ID."""
        ...
    
    @property
    def narrative(self) -> str:
        """Doctoral narrative synthesis."""
        ...
    
    @property
    def evidence(self) -> dict[str, Any]:
        """Evidence from EvidenceNexus."""
        ...
    
    @property
    def confidence_score(self) -> float:
        """Confidence score [0.0, 1.0]."""
        ...
    
    @property
    def provenance(self) -> dict[str, Any]:
        """Provenance chain."""
        ...
    
    @property
    def metadata(self) -> dict[str, Any]:
        """Execution metadata."""
        ...


@dataclass(frozen=True)
class MicroQuestionRun:
    """
    Phase 3 input structure: MicroQuestionRun.
    
    Represents a single micro-question execution result ready for scoring.
    """
    question_id: str                    # Format: PA##-DIM##-Q###
    question_global: int                # 1..300
    base_slot: str                      # Format: D#-Q#
    evidence: dict[str, Any] | None     # EvidenceNexus output or None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None            # Error message if failed
    duration_ms: float | None = None    # Execution duration
    aborted: bool = False               # Abort flag
    
    # Provenance tracking (adapter metadata)
    _adapted_from: str | None = field(default=None, compare=False)
    _adapter_version: str = field(default=ADAPTER_VERSION, compare=False)


@dataclass
class AdaptationResult:
    """Result of Phase 2 → Phase 3 adaptation."""
    micro_runs: list[MicroQuestionRun]
    success_count: int
    error_count: int
    warnings: list[str]
    adaptation_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success_count': self.success_count,
            'error_count': self.error_count,
            'total_count': len(self.micro_runs),
            'warnings': self.warnings,
            'adaptation_timestamp': self.adaptation_timestamp.isoformat(),
        }


# =============================================================================
# DERIVATION FUNCTIONS
# =============================================================================

def parse_phase2_question_id(question_id: str) -> tuple[int, int]:
    """
    Parse Phase 2 question_id format.
    
    Args:
        question_id: Format "Q###_PA##" (e.g., "Q015_PA05")
        
    Returns:
        Tuple of (q_base, pa_num) e.g., (15, 5)
        
    Raises:
        ValueError: If format doesn't match
    """
    match = PHASE2_QID_PATTERN.match(question_id)
    if not match:
        raise ValueError(
            f"Invalid Phase 2 question_id format: '{question_id}'. "
            f"Expected format: Q###_PA## (e.g., Q015_PA05)"
        )
    
    q_base = int(match.group(1))
    pa_num = int(match.group(2))
    
    # Validate ranges
    if not (1 <= q_base <= 30):
        raise ValueError(f"Question base {q_base} out of range [1, 30]")
    if not (1 <= pa_num <= 10):
        raise ValueError(f"Policy area {pa_num} out of range [1, 10]")
    
    return q_base, pa_num


def derive_dimension(q_base: int) -> int:
    """
    Derive dimension from question base number.
    
    Q001-Q005 → DIM01
    Q006-Q010 → DIM02
    Q011-Q015 → DIM03
    Q016-Q020 → DIM04
    Q021-Q025 → DIM05
    Q026-Q030 → DIM06
    
    Args:
        q_base: Question base number (1-30)
        
    Returns:
        Dimension number (1-6)
    """
    return (q_base - 1) // QUESTIONS_PER_DIMENSION + 1


def derive_question_in_dimension(q_base: int) -> int:
    """
    Derive question position within dimension.
    
    Q001, Q006, Q011, Q016, Q021, Q026 → Q1 in dimension
    Q005, Q010, Q015, Q020, Q025, Q030 → Q5 in dimension
    
    Args:
        q_base: Question base number (1-30)
        
    Returns:
        Position within dimension (1-5)
    """
    return (q_base - 1) % QUESTIONS_PER_DIMENSION + 1


def derive_base_slot(q_base: int) -> str:
    """
    Derive base_slot from question base number.
    
    Args:
        q_base: Question base number (1-30)
        
    Returns:
        Base slot string (e.g., "D3-Q5")
    """
    dimension = derive_dimension(q_base)
    q_in_dim = derive_question_in_dimension(q_base)
    return f"D{dimension}-Q{q_in_dim}"


def derive_question_global(q_base: int, pa_num: int) -> int:
    """
    Derive question_global from question base and policy area.
    
    Formula: (pa_num - 1) * 30 + q_base
    
    Examples:
    - Q001_PA01 → 1
    - Q015_PA05 → 135  (4*30 + 15)
    - Q030_PA10 → 300  (9*30 + 30)
    
    Args:
        q_base: Question base number (1-30)
        pa_num: Policy area number (1-10)
        
    Returns:
        Global question number (1-300)
    """
    return (pa_num - 1) * QUESTIONS_PER_PA + q_base


def transform_question_id(phase2_qid: str) -> str:
    """
    Transform Phase 2 question_id to Phase 3 format.
    
    Phase 2: "Q015_PA05"
    Phase 3: "PA05-DIM03-Q015"
    
    Args:
        phase2_qid: Phase 2 format question ID
        
    Returns:
        Phase 3 format question ID
    """
    q_base, pa_num = parse_phase2_question_id(phase2_qid)
    dimension = derive_dimension(q_base)
    return f"PA{pa_num:02d}-DIM{dimension:02d}-Q{q_base:03d}"


def reverse_transform_question_id(phase3_qid: str) -> str:
    """
    Reverse transform Phase 3 question_id to Phase 2 format.
    
    Phase 3: "PA05-DIM03-Q015"
    Phase 2: "Q015_PA05"
    
    Args:
        phase3_qid: Phase 3 format question ID
        
    Returns:
        Phase 2 format question ID
        
    Raises:
        ValueError: If format doesn't match
    """
    match = PHASE3_QID_PATTERN.match(phase3_qid)
    if not match:
        raise ValueError(
            f"Invalid Phase 3 question_id format: '{phase3_qid}'. "
            f"Expected format: PA##-DIM##-Q### (e.g., PA05-DIM03-Q015)"
        )
    
    pa_num = int(match.group(1))
    # dimension = int(match.group(2))  # Not needed for reverse
    q_base = int(match.group(3))
    
    return f"Q{q_base:03d}_PA{pa_num:02d}"


# =============================================================================
# ADAPTER FUNCTIONS
# =============================================================================

def adapt_single_result(
    result: Any,
    inject_confidence: bool = True,
) -> MicroQuestionRun:
    """
    Adapt a single Phase2Result to MicroQuestionRun.
    
    Args:
        result: Phase2Result or dict with result data
        inject_confidence: If True, inject confidence into evidence
        
    Returns:
        MicroQuestionRun instance
        
    Raises:
        ValueError: If result cannot be adapted
    """
    # Extract fields from result (support both dataclass and dict)
    if hasattr(result, 'question_id'):
        question_id = result.question_id
        confidence_score = getattr(result, 'confidence_score', 0.0)
        evidence = getattr(result, 'evidence', None)
        metadata = getattr(result, 'metadata', {})
    elif isinstance(result, dict):
        question_id = result.get('question_id', '')
        confidence_score = result.get('confidence_score', 0.0)
        evidence = result.get('evidence')
        metadata = result.get('metadata', {})
    else:
        raise ValueError(f"Cannot adapt result of type {type(result).__name__}")
    
    # Parse and derive fields
    try:
        q_base, pa_num = parse_phase2_question_id(question_id)
    except ValueError as e:
        # Return error MicroQuestionRun
        return MicroQuestionRun(
            question_id=question_id,
            question_global=0,
            base_slot="",
            evidence=None,
            metadata=metadata,
            error=str(e),
            aborted=False,
            _adapted_from=question_id,
        )
    
    # Transform question_id
    new_question_id = transform_question_id(question_id)
    
    # Derive question_global and base_slot
    question_global = derive_question_global(q_base, pa_num)
    base_slot = derive_base_slot(q_base)
    
    # Prepare evidence with confidence injection
    adapted_evidence: dict[str, Any] | None = None
    if evidence is not None:
        if isinstance(evidence, dict):
            adapted_evidence = evidence.copy()
        elif hasattr(evidence, '__dict__'):
            adapted_evidence = dict(evidence.__dict__)
        elif hasattr(evidence, 'to_dict'):
            adapted_evidence = evidence.to_dict()
        else:
            adapted_evidence = {'raw': evidence}
        
        # Inject confidence if missing and requested
        if inject_confidence and 'confidence' not in adapted_evidence:
            adapted_evidence['confidence'] = confidence_score
    elif inject_confidence:
        # Create minimal evidence with confidence
        adapted_evidence = {'confidence': confidence_score, 'elements': []}
    
    return MicroQuestionRun(
        question_id=new_question_id,
        question_global=question_global,
        base_slot=base_slot,
        evidence=adapted_evidence,
        metadata=metadata,
        error=None,
        duration_ms=None,
        aborted=False,
        _adapted_from=question_id,
    )


def adapt_phase2_to_phase3(
    phase2_output: Any,
    inject_confidence: bool = True,
) -> AdaptationResult:
    """
    Adapt Phase2Output to list[MicroQuestionRun].
    
    This function is:
    - Total: Defined for all valid Phase2Output
    - Pure: No side effects
    - Deterministic: Same input → same output
    
    Args:
        phase2_output: Phase2Output instance or dict with 'results' key
        inject_confidence: If True, inject confidence into evidence
        
    Returns:
        AdaptationResult with list of MicroQuestionRun
    """
    # Extract results list
    if hasattr(phase2_output, 'results'):
        results = phase2_output.results
    elif isinstance(phase2_output, dict):
        results = phase2_output.get('results', [])
    elif isinstance(phase2_output, list):
        results = phase2_output
    else:
        raise ValueError(f"Cannot adapt phase2_output of type {type(phase2_output).__name__}")
    
    micro_runs: list[MicroQuestionRun] = []
    warnings: list[str] = []
    success_count = 0
    error_count = 0
    
    for i, result in enumerate(results):
        try:
            mqr = adapt_single_result(result, inject_confidence=inject_confidence)
            micro_runs.append(mqr)
            
            if mqr.error:
                error_count += 1
                warnings.append(f"Result {i}: {mqr.error}")
            else:
                success_count += 1
                
        except Exception as e:
            error_count += 1
            warnings.append(f"Result {i}: Adaptation failed - {str(e)}")
            
            # Create error MicroQuestionRun
            mqr = MicroQuestionRun(
                question_id=f"ERROR_{i}",
                question_global=0,
                base_slot="",
                evidence=None,
                metadata={},
                error=str(e),
                aborted=False,
            )
            micro_runs.append(mqr)
    
    return AdaptationResult(
        micro_runs=micro_runs,
        success_count=success_count,
        error_count=error_count,
        warnings=warnings,
    )


def validate_adaptation(
    original_count: int,
    adapted: AdaptationResult,
) -> tuple[bool, list[str]]:
    """
    Validate adaptation result.
    
    Args:
        original_count: Expected number of results
        adapted: AdaptationResult from adapt_phase2_to_phase3
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors: list[str] = []
    
    # Check count preservation
    if len(adapted.micro_runs) != original_count:
        errors.append(
            f"Count mismatch: original={original_count}, adapted={len(adapted.micro_runs)}"
        )
    
    # Check for errors
    if adapted.error_count > 0:
        errors.append(f"Adaptation errors: {adapted.error_count}")
    
    # Verify question_global uniqueness
    globals_seen = set()
    for mqr in adapted.micro_runs:
        if mqr.question_global in globals_seen:
            errors.append(f"Duplicate question_global: {mqr.question_global}")
        globals_seen.add(mqr.question_global)
    
    # Verify question_id format
    for mqr in adapted.micro_runs:
        if mqr.error:
            continue
        if not PHASE3_QID_PATTERN.match(mqr.question_id):
            errors.append(f"Invalid Phase 3 question_id format: {mqr.question_id}")
    
    return len(errors) == 0, errors


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "Phase2ResultProtocol",
    "MicroQuestionRun",
    "AdaptationResult",
    # Derivation functions
    "parse_phase2_question_id",
    "derive_dimension",
    "derive_question_in_dimension",
    "derive_base_slot",
    "derive_question_global",
    "transform_question_id",
    "reverse_transform_question_id",
    # Adapter functions
    "adapt_single_result",
    "adapt_phase2_to_phase3",
    "validate_adaptation",
    # Constants
    "ADAPTER_VERSION",
    "PHASE2_QID_PATTERN",
    "PHASE3_QID_PATTERN",
]
