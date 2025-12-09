"""
Type definitions for method signature validation system.

Provides comprehensive type definitions for signature validation,
ensuring type safety across the validation chain.
"""

from typing import Literal, TypedDict

# Input Classification Types
InputClassification = Literal["required", "optional", "critical_optional"]


# Output Type Literals
OutputType = Literal["float", "int", "dict", "list", "str", "bool", "tuple", "Any"]


class MethodSignature(TypedDict, total=False):
    """
    Complete method signature with input/output contracts.

    Fields:
        required_inputs: Inputs that MUST be present (hard failure if missing)
        optional_inputs: Inputs that are nice to have (no penalty)
        critical_optional: Inputs that should be present (penalty if missing)
        output_type: Expected output type
        output_range: Valid range for numeric outputs [min, max]
        description: Human-readable description
    """

    required_inputs: list[str]
    optional_inputs: list[str]
    critical_optional: list[str]
    output_type: str
    output_range: list[float] | None
    description: str


class SignatureValidationResult(TypedDict):
    """
    Result of signature validation.

    Fields:
        is_valid: Whether signature is valid
        missing_fields: Required fields that are missing
        issues: Critical validation issues
        warnings: Non-critical validation warnings
    """

    is_valid: bool
    missing_fields: list[str]
    issues: list[str]
    warnings: list[str]


class ValidationResult(TypedDict):
    """
    Runtime validation result for method execution.

    Fields:
        passed: Whether validation passed (no hard failures)
        hard_failures: Critical failures (missing required inputs)
        soft_failures: Non-critical failures (missing critical optional)
        warnings: Non-blocking warnings
        missing_critical_optional: List of missing critical optional inputs
    """

    passed: bool
    hard_failures: list[str]
    soft_failures: list[str]
    warnings: list[str]
    missing_critical_optional: list[str]


class ValidationSummaryStats(TypedDict):
    """
    Summary statistics for validation report.

    Fields:
        completeness_rate: Percentage of methods with valid signatures
        methods_with_required_fields: Count of valid methods
        methods_missing_required_fields: Count of invalid methods
        methods_with_incomplete_signatures: Count with missing recommended fields
        most_common_required_inputs: Top required inputs by frequency
        most_common_optional_inputs: Top optional inputs by frequency
        most_common_critical_optional: Top critical optional inputs by frequency
        output_type_distribution: Count of methods by output type
    """

    completeness_rate: float
    methods_with_required_fields: int
    methods_missing_required_fields: int
    methods_with_incomplete_signatures: int
    most_common_required_inputs: list[tuple[str, int]]
    most_common_optional_inputs: list[tuple[str, int]]
    most_common_critical_optional: list[tuple[str, int]]
    output_type_distribution: dict[str, int]


class ValidationReport(TypedDict):
    """
    Complete validation report with all details.

    Fields:
        validation_timestamp: ISO 8601 timestamp of validation
        signatures_version: Version of signatures schema
        total_methods: Total number of methods
        valid_methods: Count of valid methods
        invalid_methods: Count of invalid methods
        incomplete_methods: Count of incomplete methods
        methods_with_warnings: Count of methods with warnings
        validation_details: Detailed validation results per method
        summary: Summary statistics
    """

    validation_timestamp: str
    signatures_version: str
    total_methods: int
    valid_methods: int
    invalid_methods: int
    incomplete_methods: int
    methods_with_warnings: int
    validation_details: dict[str, SignatureValidationResult]
    summary: ValidationSummaryStats


class ExecutionMetadata(TypedDict):
    """
    Metadata for method execution with signature validation.

    Fields:
        method_id: Method identifier
        validation_passed: Whether validation passed
        penalty: Penalty applied for missing inputs
        validation_messages: Validation messages/warnings
        execution_status: Status of execution
        adjusted_confidence: Confidence after penalty (optional)
        error: Error message if execution failed (optional)
    """

    method_id: str
    validation_passed: bool
    penalty: float
    validation_messages: list[str]
    execution_status: str
    adjusted_confidence: float | None
    error: str | None


class SignatureSchema(TypedDict):
    """
    Top-level signature schema structure.

    Fields:
        signatures_version: Schema version
        last_updated: Last update date
        schema_version: Schema version identifier
        methods: Dictionary of method signatures
    """

    signatures_version: str
    last_updated: str
    schema_version: str
    methods: dict[str, dict[str, MethodSignature]]


class InputValidationConfig(TypedDict, total=False):
    """
    Configuration for input validation.

    Fields:
        strict_mode: Raise exceptions for missing signatures
        penalty_for_missing_critical: Penalty per missing critical optional
        apply_penalties: Whether to apply penalties to results
        raise_on_failure: Whether to raise on validation failure
    """

    strict_mode: bool
    penalty_for_missing_critical: float
    apply_penalties: bool
    raise_on_failure: bool


class ValidationStats(TypedDict):
    """
    Statistics for method validation tracking.

    Fields:
        calls: Total number of validation calls
        hard_failures: Count of hard failures
        soft_failures: Count of soft failures
    """

    calls: int
    hard_failures: int
    soft_failures: int


# Validation Status Types
ValidationStatus = Literal["pending", "success", "failed_validation", "error"]


# Failure Severity Types
FailureSeverity = Literal[
    "hard",  # Critical failure, execution cannot proceed
    "soft",  # Non-critical failure, penalty applied
    "warning",  # Informational, no penalty
]


class ValidationFailure(TypedDict):
    """
    Detailed information about a validation failure.

    Fields:
        severity: Severity level of failure
        message: Failure message
        field: Field that caused failure (if applicable)
        expected: Expected value/type
        actual: Actual value/type
    """

    severity: FailureSeverity
    message: str
    field: str | None
    expected: str | None
    actual: str | None


class PenaltyCalculation(TypedDict):
    """
    Details of penalty calculation.

    Fields:
        total_penalty: Total penalty value
        hard_failure_penalty: Penalty from hard failures (1.0 if any)
        critical_optional_penalty: Penalty from missing critical optional
        soft_failure_penalty: Penalty from soft failures
        missing_critical_inputs: List of missing critical inputs
        penalty_breakdown: Detailed breakdown
    """

    total_penalty: float
    hard_failure_penalty: float
    critical_optional_penalty: float
    soft_failure_penalty: float
    missing_critical_inputs: list[str]
    penalty_breakdown: dict[str, float]


# Constants for validation
REQUIRED_SIGNATURE_FIELDS = {"required_inputs", "output_type"}
RECOMMENDED_SIGNATURE_FIELDS = {"optional_inputs", "critical_optional", "output_range"}
ALL_SIGNATURE_FIELDS = (
    REQUIRED_SIGNATURE_FIELDS | RECOMMENDED_SIGNATURE_FIELDS | {"description"}
)
VALID_OUTPUT_TYPES = {"float", "int", "dict", "list", "str", "bool", "tuple", "Any"}

# Penalty constants
DEFAULT_MISSING_CRITICAL_PENALTY = 0.1
DEFAULT_SOFT_FAILURE_PENALTY = 0.05
HARD_FAILURE_PENALTY = 1.0
MAX_TOTAL_PENALTY = 1.0

# Validation modes
STRICT_MODE = True
NON_STRICT_MODE = False
