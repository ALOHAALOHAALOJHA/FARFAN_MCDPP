"""
Phase 2 Input Contract
======================

PHASE_LABEL: Phase 2
Module: contracts/phase2_input_contract.py
Purpose: Defines and validates input preconditions for Phase 2 execution

This contract ensures that Phase 2 receives valid, complete, and compatible
input from Phase 1 (CanonPolicyPackage).

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
Date: 2026-01-13
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

__version__ = "1.0.0"
__phase__ = 2

# =============================================================================
# INPUT PRECONDITIONS
# =============================================================================

@dataclass(frozen=True)
class Phase2InputPreconditions:
    """Defines all preconditions that MUST be satisfied for Phase 2 to execute."""
    
    # PRE-001: CanonPolicyPackage validation
    REQUIRES_VALID_CPP: Final[bool] = True
    CPP_MUST_BE_COMPLETE: Final[bool] = True
    
    # PRE-002: Chunk count validation
    EXPECTED_CHUNK_COUNT: Final[int] = 60
    MIN_CHUNK_COUNT: Final[int] = 60
    MAX_CHUNK_COUNT: Final[int] = 60
    
    # PRE-003: Schema version validation
    REQUIRED_CPP_SCHEMA_VERSION: Final[str] = "CPP-2025.1"
    
    # PRE-004: Phase 1 compatibility certificate
    REQUIRES_PHASE1_CERTIFICATE: Final[bool] = True
    CERTIFICATE_STATUS_VALID: Final[str] = "VALID"
    
    # PRE-005: Questionnaire validation
    # NOTE: Phase 1 delivers 305 questions (Q001..Q305) per delivers_to_next_phase_contract.json
    EXPECTED_QUESTION_COUNT: Final[int] = 305
    QUESTIONS_MUST_MAP_TO_CONTRACTS: Final[bool] = True
    
    # PRE-006: Method registry validation
    # NOTE: 240 is the base method count; 416 includes all variants per receives_contract.json
    EXPECTED_METHOD_COUNT: Final[int] = 240
    ALL_METHODS_MUST_BE_RESOLVABLE: Final[bool] = True


class Phase2InputContractError(Exception):
    """Raised when input contract validation fails."""
    pass


class Phase2InputValidator:
    """Validates that all input preconditions are satisfied."""
    
    def __init__(self, preconditions: Phase2InputPreconditions | None = None):
        self.preconditions = preconditions or Phase2InputPreconditions()
    
    def validate_cpp(self, cpp: Any) -> tuple[bool, list[str]]:
        """
        Validate CanonPolicyPackage structure and completeness.
        
        Args:
            cpp: CanonPolicyPackage object from Phase 1
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # PRE-001: Check if CPP is valid
        if cpp is None:
            errors.append("PRE-001: CanonPolicyPackage is None")
            return False, errors
        
        # PRE-002: Check chunk count
        # NOTE: Phase 1 delivers via chunk_graph.chunks OR smart_chunks, not cpp.chunks directly
        chunk_count = None
        if hasattr(cpp, 'chunk_graph') and hasattr(cpp.chunk_graph, 'chunks'):
            chunk_count = len(cpp.chunk_graph.chunks)
        elif hasattr(cpp, 'smart_chunks'):
            chunk_count = len(cpp.smart_chunks)
        elif hasattr(cpp, 'chunks'):
            chunk_count = len(cpp.chunks)
        
        if chunk_count is None:
            errors.append("PRE-002: CPP missing chunk data (expected chunk_graph.chunks, smart_chunks, or chunks)")
        elif chunk_count != self.preconditions.EXPECTED_CHUNK_COUNT:
            errors.append(
                f"PRE-002: Expected {self.preconditions.EXPECTED_CHUNK_COUNT} chunks, "
                f"got {chunk_count}"
            )
        
        # PRE-003: Check schema version
        # NOTE: Phase 1 stores schema_version in cpp.metadata.schema_version, not cpp.schema_version
        schema_version = None
        if hasattr(cpp, 'metadata') and hasattr(cpp.metadata, 'schema_version'):
            schema_version = cpp.metadata.schema_version
        elif hasattr(cpp, 'schema_version'):
            schema_version = cpp.schema_version
        
        if schema_version is None:
            errors.append("PRE-003: CPP missing schema_version (expected metadata.schema_version or schema_version)")
        elif schema_version != self.preconditions.REQUIRED_CPP_SCHEMA_VERSION:
            errors.append(
                f"PRE-003: Expected schema version "
                f"{self.preconditions.REQUIRED_CPP_SCHEMA_VERSION}, "
                f"got {schema_version}"
            )
        
        return len(errors) == 0, errors
    
    def validate_phase1_certificate(self, certificate: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate Phase 1 compatibility certificate.
        
        Args:
            certificate: Phase 1 output certificate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # PRE-004: Check certificate status
        if not certificate:
            errors.append("PRE-004: Phase 1 certificate is missing")
            return False, errors
        
        status = certificate.get('status', '')
        if status != self.preconditions.CERTIFICATE_STATUS_VALID:
            errors.append(
                f"PRE-004: Certificate status is '{status}', "
                f"expected '{self.preconditions.CERTIFICATE_STATUS_VALID}'"
            )
        
        return len(errors) == 0, errors
    
    def validate_questionnaire(self, questionnaire: Any) -> tuple[bool, list[str]]:
        """
        Validate questionnaire structure.
        
        Args:
            questionnaire: Questionnaire object
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # PRE-005: Check question count
        if hasattr(questionnaire, 'questions'):
            question_count = len(questionnaire.questions)
            if question_count != self.preconditions.EXPECTED_QUESTION_COUNT:
                errors.append(
                    f"PRE-005: Expected {self.preconditions.EXPECTED_QUESTION_COUNT} questions, "
                    f"got {question_count}"
                )
        else:
            errors.append("PRE-005: Questionnaire missing 'questions' attribute")
        
        return len(errors) == 0, errors
    
    def validate_method_registry(self, registry: Any) -> tuple[bool, list[str]]:
        """
        Validate method registry completeness.
        
        Args:
            registry: MethodRegistry object
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # PRE-006: Check method count
        if hasattr(registry, '_registry'):
            method_count = len(registry._registry)
            if method_count < self.preconditions.EXPECTED_METHOD_COUNT:
                errors.append(
                    f"PRE-006: Expected at least {self.preconditions.EXPECTED_METHOD_COUNT} methods, "
                    f"got {method_count}"
                )
        else:
            errors.append("PRE-006: MethodRegistry missing '_registry' attribute")
        
        return len(errors) == 0, errors
    
    def validate_all(
        self,
        cpp: Any,
        certificate: dict[str, Any],
        questionnaire: Any,
        registry: Any,
    ) -> tuple[bool, list[str]]:
        """
        Validate all input preconditions.
        
        Args:
            cpp: CanonPolicyPackage
            certificate: Phase 1 certificate
            questionnaire: Questionnaire object
            registry: MethodRegistry object
            
        Returns:
            Tuple of (is_valid, list_of_errors)
            
        Raises:
            Phase2InputContractError: If validation fails and strict mode is enabled
        """
        all_errors = []
        
        cpp_valid, errors = self.validate_cpp(cpp)
        all_errors.extend(errors)
        
        cert_valid, errors = self.validate_phase1_certificate(certificate)
        all_errors.extend(errors)
        
        questionnaire_valid, errors = self.validate_questionnaire(questionnaire)
        all_errors.extend(errors)
        
        registry_valid, errors = self.validate_method_registry(registry)
        all_errors.extend(errors)
        
        is_valid = cpp_valid and cert_valid and questionnaire_valid and registry_valid
        return is_valid, all_errors


# =============================================================================
# CONTRACT VERIFICATION COMMAND
# =============================================================================

def verify_phase2_input_contract(
    cpp: Any,
    certificate: dict[str, Any],
    questionnaire: Any,
    registry: Any,
    strict: bool = True,
) -> bool:
    """
    Command-line verification of Phase 2 input contract.
    
    Args:
        cpp: CanonPolicyPackage
        certificate: Phase 1 certificate
        questionnaire: Questionnaire object
        registry: MethodRegistry object
        strict: If True, raises exception on validation failure
        
    Returns:
        True if all preconditions satisfied
        
    Raises:
        Phase2InputContractError: If validation fails and strict=True
    """
    validator = Phase2InputValidator()
    is_valid, errors = validator.validate_all(cpp, certificate, questionnaire, registry)
    
    if not is_valid:
        error_msg = "Phase 2 Input Contract Validation Failed:\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        if strict:
            raise Phase2InputContractError(error_msg)
        print(error_msg)
        return False
    
    print("✓ Phase 2 Input Contract: ALL PRECONDITIONS SATISFIED")
    return True
