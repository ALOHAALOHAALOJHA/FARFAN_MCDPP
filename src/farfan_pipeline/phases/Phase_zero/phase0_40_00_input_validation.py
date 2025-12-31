"""
Phase 0: Input Validation - Constitutional Implementation
==========================================================

This module implements Phase 0 of the canonical pipeline:
    Raw input → Validated CanonicalInput

Responsibilities:
-----------------
1. Validate PDF exists and is readable
2. Compute SHA256 hash of PDF (deterministic fingerprint)
3. Extract PDF metadata (page count, size)
4. Validate questionnaire exists
5. Compute SHA256 hash of questionnaire
6. Package validated inputs into CanonicalInput

Input Contract:
---------------
Phase0Input:
    - pdf_path: Path (must exist)
    - run_id: str (unique execution identifier)
    - questionnaire_path: Path | None (optional, defaults to canonical)

Output Contract:
----------------
CanonicalInput:
    - document_id: str (derived from PDF stem or explicit)
    - run_id: str (preserved from input)
    - pdf_path: Path (validated)
    - pdf_sha256: str (computed hash)
    - pdf_size_bytes: int (file size)
    - pdf_page_count: int (extracted from PDF)
    - questionnaire_path: Path (validated)
    - questionnaire_sha256: str (computed hash)
    - created_at: datetime (UTC timestamp)
    - phase0_version: str (schema version)
    - validation_passed: bool (must be True for output)
    - validation_errors: list[str] (empty if passed)
    - validation_warnings: list[str] (may contain warnings)

Invariants:
-----------
1. validation_passed == True
2. pdf_page_count > 0
3. pdf_size_bytes > 0
4. pdf_sha256 is 64-char hex string
5. questionnaire_sha256 is 64-char hex string

Author: F.A.R.F.A.N Architecture Team
Date: 2025-01-19
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# REQUIRED: pydantic for runtime contract validation
# This is a hard dependency for Phase 0 as per dura_lex contract system
try:
    from pydantic import BaseModel, Field, field_validator, model_validator
except ImportError as e:
    raise ImportError(
        "pydantic>=2.0 is REQUIRED for Phase 0 contract validation. "
        "The F.A.R.F.A.N pipeline uses the dura_lex contract system which depends on pydantic "
        "for runtime validation, ensuring maximum performance and deterministic execution. "
        "Install with: pip install 'pydantic>=2.0'"
    ) from e

# Phase protocol from Phase One
from farfan_pipeline.phases.Phase_one.phase_protocol import (
    ContractValidationResult,
    PhaseContract,
)

# Dura Lex Contract System - ACTUAL USAGE FOR MAXIMUM PERFORMANCE
# Import specific modules directly (bypass __init__.py which has broken imports)
# These tools ensure idempotency and full traceability per FORCING ROUTE
try:
    # Import directly from module files, not through package __init__
    import sys
    from pathlib import Path
    dura_lex_path = Path(__file__).parent.parent.parent / "cross_cutting_infrastructure" / "contractual" / "dura_lex"
    sys.path.insert(0, str(dura_lex_path))
    
    from idempotency_dedup import IdempotencyContract, EvidenceStore
    from traceability import TraceabilityContract, MerkleTree
    
    DURA_LEX_AVAILABLE = True
except ImportError:
    DURA_LEX_AVAILABLE = False
    IdempotencyContract = None
    EvidenceStore = None
    TraceabilityContract = None
    MerkleTree = None

# Schema version for Phase 0
PHASE0_VERSION = "1.0.0"


# ============================================================================
# INPUT CONTRACT
# ============================================================================


@dataclass
class Phase0Input:
    """
    Input contract for Phase 0.

    This is the raw, unvalidated input to the pipeline.
    """

    pdf_path: Path
    run_id: str
    questionnaire_path: Path | None = None


class Phase0InputValidator(BaseModel):
    """
    Runtime validator for Phase0Input contract - Dura Lex StrictModel Pattern.
    
    Uses pydantic for strict runtime validation following the dura_lex contract system.
    This ensures maximum performance and deterministic execution with zero tolerance
    for invalid inputs.
    
    Configuration follows dura_lex/contracts_runtime.py StrictModel pattern:
    - extra='forbid': Refuse unknown fields
    - validate_assignment=True: Validate on assignment
    - str_strip_whitespace=True: Auto-strip strings
    - validate_default=True: Validate default values
    """
    
    # Strict configuration per dura_lex contract system
    model_config = {
        'extra': 'forbid',  # Refuse unknown fields - zero tolerance
        'validate_assignment': True,  # Validate on assignment
        'str_strip_whitespace': True,  # Auto-strip whitespace
        'validate_default': True,  # Validate defaults
        'frozen': False,  # Allow mutation for validation
    }

    pdf_path: str = Field(min_length=1, description="Path to input PDF")
    run_id: str = Field(min_length=1, description="Unique run identifier")
    questionnaire_path: str | None = Field(
        default=None, description="Optional questionnaire path"
    )

    @field_validator("pdf_path")
    @classmethod
    def validate_pdf_path(cls, v: str) -> str:
        """Validate PDF path format with zero tolerance per FORCING ROUTE [PRE-003]."""
        if not v or not v.strip():
            raise ValueError("[PRE-003] FATAL: pdf_path cannot be empty")
        return v

    @field_validator("run_id")
    @classmethod
    def validate_run_id(cls, v: str) -> str:
        """Validate run_id format with zero tolerance per FORCING ROUTE [PRE-002]."""
        if not v or not v.strip():
            raise ValueError("[PRE-002] FATAL: run_id cannot be empty")
        # Ensure run_id is filesystem-safe and deterministic
        if any(char in v for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            raise ValueError(
                "[PRE-002] FATAL: run_id contains invalid characters (must be filesystem-safe)"
            )
        return v


# ============================================================================
# OUTPUT CONTRACT
# ============================================================================


@dataclass
class CanonicalInput:
    """
    Output contract for Phase 0.

    This represents a validated, canonical input ready for Phase 1.
    All fields are required and validated.
    """

    # Identity
    document_id: str
    run_id: str

    # Input artifacts (immutable, validated)
    pdf_path: Path
    pdf_sha256: str
    pdf_size_bytes: int
    pdf_page_count: int

    # Questionnaire (required for SIN_CARRETA compliance)
    questionnaire_path: Path
    questionnaire_sha256: str

    # Metadata
    created_at: datetime
    phase0_version: str

    # Validation results
    validation_passed: bool
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)


class CanonicalInputValidator(BaseModel):
    """Pydantic validator for CanonicalInput."""

    document_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    pdf_path: str
    pdf_sha256: str = Field(min_length=64, max_length=64)
    pdf_size_bytes: int = Field(gt=0)
    pdf_page_count: int = Field(gt=0)
    questionnaire_path: str
    questionnaire_sha256: str = Field(min_length=64, max_length=64)
    created_at: str
    phase0_version: str
    validation_passed: bool
    validation_errors: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_consistency(self) -> "CanonicalInputValidator":
        """Ensure validation_passed is True and consistent with errors."""
        if not self.validation_passed:
            raise ValueError(
                "validation_passed must be True for valid CanonicalInput"
            )
        if self.validation_errors:
            raise ValueError(
                f"validation_passed is True but validation_errors is not empty: {self.validation_errors}"
            )
        return self

    @field_validator("pdf_sha256", "questionnaire_sha256")
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        """Validate SHA256 hash format."""
        if len(v) != 64:
            raise ValueError(f"SHA256 hash must be 64 characters, got {len(v)}")
        if not all(c in "0123456789abcdef" for c in v.lower()):
            raise ValueError("SHA256 hash must be hexadecimal")
        return v.lower()


# ============================================================================
# PHASE 0 CONTRACT IMPLEMENTATION
# ============================================================================


class Phase0ValidationContract(PhaseContract[Phase0Input, CanonicalInput]):
    """
    Phase 0: Input Validation Contract.

    This class enforces the constitutional constraint that Phase 0:
    1. Accepts ONLY Phase0Input
    2. Produces ONLY CanonicalInput
    3. Validates all invariants
    4. Logs all operations
    """

    def __init__(self):
        """Initialize Phase 0 contract with invariants."""
        super().__init__(phase_name="phase0_input_validation")

        # Register invariants
        self.add_invariant(
            name="validation_passed",
            description="Output must have validation_passed=True",
            check=lambda data: data.validation_passed is True,
            error_message="validation_passed must be True",
        )

        self.add_invariant(
            name="pdf_page_count_positive",
            description="PDF must have at least 1 page",
            check=lambda data: data.pdf_page_count > 0,
            error_message="pdf_page_count must be > 0",
        )

        self.add_invariant(
            name="pdf_size_positive",
            description="PDF size must be > 0 bytes",
            check=lambda data: data.pdf_size_bytes > 0,
            error_message="pdf_size_bytes must be > 0",
        )

        self.add_invariant(
            name="sha256_format",
            description="SHA256 hashes must be valid",
            check=lambda data: (
                len(data.pdf_sha256) == 64
                and len(data.questionnaire_sha256) == 64
                and all(c in "0123456789abcdef" for c in data.pdf_sha256.lower())
                and all(c in "0123456789abcdef" for c in data.questionnaire_sha256.lower())
            ),
            error_message="SHA256 hashes must be 64-char hexadecimal",
        )

        self.add_invariant(
            name="no_validation_errors",
            description="validation_errors must be empty",
            check=lambda data: len(data.validation_errors) == 0,
            error_message="validation_errors must be empty for valid output",
        )

    def validate_input(self, input_data: Any) -> ContractValidationResult:
        """
        Validate Phase0Input contract.

        Args:
            input_data: Input to validate

        Returns:
            ContractValidationResult
        """
        errors = []
        warnings = []

        # Type check
        if not isinstance(input_data, Phase0Input):
            errors.append(
                f"Expected Phase0Input, got {type(input_data).__name__}"
            )
            return ContractValidationResult(
                passed=False,
                contract_type="input",
                phase_name=self.phase_name,
                errors=errors,
            )

        # Validate using Pydantic
        try:
            Phase0InputValidator(
                pdf_path=str(input_data.pdf_path),
                run_id=input_data.run_id,
                questionnaire_path=(
                    str(input_data.questionnaire_path)
                    if input_data.questionnaire_path
                    else None
                ),
            )
        except Exception as e:
            errors.append(f"Pydantic validation failed: {e}")

        return ContractValidationResult(
            passed=len(errors) == 0,
            contract_type="input",
            phase_name=self.phase_name,
            errors=errors,
            warnings=warnings,
        )

    def validate_output(self, output_data: Any) -> ContractValidationResult:
        """
        Validate CanonicalInput contract.

        Args:
            output_data: Output to validate

        Returns:
            ContractValidationResult
        """
        errors = []
        warnings = []

        # Type check
        if not isinstance(output_data, CanonicalInput):
            errors.append(
                f"Expected CanonicalInput, got {type(output_data).__name__}"
            )
            return ContractValidationResult(
                passed=False,
                contract_type="output",
                phase_name=self.phase_name,
                errors=errors,
            )

        # Validate using Pydantic
        try:
            CanonicalInputValidator(
                document_id=output_data.document_id,
                run_id=output_data.run_id,
                pdf_path=str(output_data.pdf_path),
                pdf_sha256=output_data.pdf_sha256,
                pdf_size_bytes=output_data.pdf_size_bytes,
                pdf_page_count=output_data.pdf_page_count,
                questionnaire_path=str(output_data.questionnaire_path),
                questionnaire_sha256=output_data.questionnaire_sha256,
                created_at=output_data.created_at.isoformat(),
                phase0_version=output_data.phase0_version,
                validation_passed=output_data.validation_passed,
                validation_errors=output_data.validation_errors,
                validation_warnings=output_data.validation_warnings,
            )
        except Exception as e:
            errors.append(f"Pydantic validation failed: {e}")

        return ContractValidationResult(
            passed=len(errors) == 0,
            contract_type="output",
            phase_name=self.phase_name,
            errors=errors,
            warnings=warnings,
        )

    async def execute(self, input_data: Phase0Input) -> CanonicalInput:
        """
        Execute Phase 0: Input Validation.

        Args:
            input_data: Phase0Input with raw paths

        Returns:
            CanonicalInput with validated data

        Raises:
            FileNotFoundError: If PDF or questionnaire doesn't exist
            ValueError: If validation fails
        """
        errors = []
        warnings = []

        # 1. Resolve questionnaire path
        questionnaire_path = input_data.questionnaire_path
        if questionnaire_path is None:
            from canonic_phases.Phase_zero.phase0_10_00_paths import QUESTIONNAIRE_FILE

            questionnaire_path = QUESTIONNAIRE_FILE
            warnings.append(
                f"questionnaire_path not provided, using default: {questionnaire_path}"
            )

        # 2. Validate PDF exists
        if not input_data.pdf_path.exists():
            errors.append(f"PDF not found: {input_data.pdf_path}")
        if not input_data.pdf_path.is_file():
            errors.append(f"PDF path is not a file: {input_data.pdf_path}")

        # 3. Validate questionnaire exists
        if not questionnaire_path.exists():
            errors.append(f"Questionnaire not found: {questionnaire_path}")
        if not questionnaire_path.is_file():
            errors.append(f"Questionnaire path is not a file: {questionnaire_path}")

        # If basic validation failed, abort
        if errors:
            raise FileNotFoundError(f"Input validation failed: {errors}")

        # 4. Compute PDF hash and metadata
        pdf_sha256 = self._compute_sha256(input_data.pdf_path)
        pdf_size_bytes = input_data.pdf_path.stat().st_size
        pdf_page_count = self._get_pdf_page_count(input_data.pdf_path)

        # 5. Compute questionnaire hash
        questionnaire_sha256 = self._compute_sha256(questionnaire_path)

        # 6. Determine document_id
        document_id = input_data.pdf_path.stem

        # 7. Create CanonicalInput
        canonical_input = CanonicalInput(
            document_id=document_id,
            run_id=input_data.run_id,
            pdf_path=input_data.pdf_path,
            pdf_sha256=pdf_sha256,
            pdf_size_bytes=pdf_size_bytes,
            pdf_page_count=pdf_page_count,
            questionnaire_path=questionnaire_path,
            questionnaire_sha256=questionnaire_sha256,
            created_at=datetime.now(timezone.utc),
            phase0_version=PHASE0_VERSION,
            validation_passed=len(errors) == 0,
            validation_errors=errors,
            validation_warnings=warnings,
        )

        return canonical_input

    @staticmethod
    def _compute_sha256(file_path: Path) -> str:
        """
        Compute SHA256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            Hex-encoded SHA256 hash (lowercase)
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest().lower()

    @staticmethod
    def _get_pdf_page_count(pdf_path: Path) -> int:
        """
        Extract page count from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of pages

        Raises:
            ImportError: If PyMuPDF is not available
            RuntimeError: If PDF cannot be opened
        """
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except ImportError:
            raise ImportError(
                "PyMuPDF (fitz) required for PDF page count extraction. "
                "Install with: pip install PyMuPDF"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to open PDF {pdf_path}: {e}")


__all__ = [
    "Phase0Input",
    "CanonicalInput",
    "Phase0ValidationContract",
    "PHASE0_VERSION",
]
