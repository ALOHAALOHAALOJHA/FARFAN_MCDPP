"""
Tests for runtime signature validation.

Validates that runtime validator properly:
- Enforces required inputs (hard failure)
- Warns about missing critical optional inputs (penalty)
- Tracks optional inputs
- Validates output types and ranges
"""

import json
from pathlib import Path

import pytest

from farfan_pipeline.core.orchestrator.signature_runtime_validator import (
    SignatureRuntimeValidator,
    ValidationResult,
)


@pytest.fixture
def temp_signatures_file(tmp_path: Path) -> Path:
    """Create temporary signatures file for testing."""
    signatures_data = {
        "signatures_version": "2.0.0",
        "last_updated": "2025-01-01",
        "schema_version": "chain_layer_validation_v1",
        "methods": {
            "test_analyzer": {
                "signature": {
                    "required_inputs": ["extracted_text", "question_id"],
                    "optional_inputs": ["reference_corpus", "threshold", "context"],
                    "critical_optional": ["reference_corpus"],
                    "output_type": "float",
                    "output_range": [0.0, 1.0],
                    "description": "Test analyzer method",
                }
            },
            "simple_method": {
                "signature": {
                    "required_inputs": ["text"],
                    "optional_inputs": [],
                    "critical_optional": [],
                    "output_type": "dict",
                    "output_range": None,
                }
            },
        },
    }

    signatures_file = tmp_path / "method_signatures.json"
    with open(signatures_file, "w") as f:
        json.dump(signatures_data, f, indent=2)

    return signatures_file


def test_runtime_validator_initialization(temp_signatures_file: Path) -> None:
    """Test that runtime validator initializes correctly."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    assert validator.validator is not None
    assert validator.strict_mode is True
    assert validator.penalty_for_missing_critical == 0.1


def test_validate_inputs_with_all_required(temp_signatures_file: Path) -> None:
    """Test validation passes when all required inputs provided."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_inputs(
        "test_analyzer", {"extracted_text": "Some text", "question_id": "Q1"}
    )

    assert result["passed"] is True
    assert len(result["hard_failures"]) == 0


def test_validate_inputs_missing_required(temp_signatures_file: Path) -> None:
    """Test validation fails when required input missing."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_inputs(
        "test_analyzer",
        {
            "extracted_text": "Some text"
            # Missing "question_id"
        },
    )

    assert result["passed"] is False
    assert len(result["hard_failures"]) > 0
    assert any("question_id" in failure for failure in result["hard_failures"])


def test_validate_inputs_required_is_none(temp_signatures_file: Path) -> None:
    """Test validation fails when required input is None."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_inputs(
        "test_analyzer", {"extracted_text": None, "question_id": "Q1"}
    )

    assert result["passed"] is False
    assert len(result["hard_failures"]) > 0
    assert any(
        "extracted_text" in failure and "None" in failure
        for failure in result["hard_failures"]
    )


def test_validate_inputs_missing_critical_optional(temp_signatures_file: Path) -> None:
    """Test soft failure when critical optional input missing."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_inputs(
        "test_analyzer",
        {
            "extracted_text": "Some text",
            "question_id": "Q1",
            # Missing "reference_corpus" (critical optional)
        },
    )

    assert result["passed"] is True  # Soft failure, still passes
    assert len(result["soft_failures"]) > 0
    assert "reference_corpus" in result["missing_critical_optional"]
    assert any("reference_corpus" in failure for failure in result["soft_failures"])


def test_validate_inputs_with_optional(temp_signatures_file: Path) -> None:
    """Test validation with optional inputs provided."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_inputs(
        "test_analyzer",
        {
            "extracted_text": "Some text",
            "question_id": "Q1",
            "reference_corpus": "corpus data",
            "threshold": 0.5,
        },
    )

    assert result["passed"] is True
    assert len(result["hard_failures"]) == 0
    assert len(result["soft_failures"]) == 0


def test_validate_output_correct_type(temp_signatures_file: Path) -> None:
    """Test output validation with correct type."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_output("test_analyzer", 0.85)

    assert result["passed"] is True
    assert len(result["hard_failures"]) == 0


def test_validate_output_in_range(temp_signatures_file: Path) -> None:
    """Test output validation with value in range."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_output("test_analyzer", 0.5)

    assert result["passed"] is True
    assert len(result["soft_failures"]) == 0


def test_validate_output_out_of_range(temp_signatures_file: Path) -> None:
    """Test output validation with value out of range."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_output("test_analyzer", 1.5)

    assert result["passed"] is True  # Soft failure
    assert len(result["soft_failures"]) > 0
    assert any("out of range" in failure for failure in result["soft_failures"])


def test_validate_output_wrong_type(temp_signatures_file: Path) -> None:
    """Test output validation with wrong type."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = validator.validate_output("simple_method", "string instead of dict")

    assert len(result["soft_failures"]) > 0 or len(result["warnings"]) > 0


def test_calculate_penalty_no_failures(temp_signatures_file: Path) -> None:
    """Test penalty calculation with no failures."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = ValidationResult(
        passed=True,
        hard_failures=[],
        soft_failures=[],
        warnings=[],
        missing_critical_optional=[],
    )

    penalty = validator.calculate_penalty(result)

    assert penalty == 0.0


def test_calculate_penalty_hard_failure(temp_signatures_file: Path) -> None:
    """Test penalty calculation with hard failures."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    result = ValidationResult(
        passed=False,
        hard_failures=["Missing required input"],
        soft_failures=[],
        warnings=[],
        missing_critical_optional=[],
    )

    penalty = validator.calculate_penalty(result)

    assert penalty == 1.0  # Maximum penalty


def test_calculate_penalty_missing_critical_optional(
    temp_signatures_file: Path,
) -> None:
    """Test penalty calculation for missing critical optional."""
    validator = SignatureRuntimeValidator(
        temp_signatures_file, penalty_for_missing_critical=0.1
    )

    result = ValidationResult(
        passed=True,
        hard_failures=[],
        soft_failures=["Missing critical optional"],
        warnings=[],
        missing_critical_optional=["reference_corpus"],
    )

    penalty = validator.calculate_penalty(result)

    assert penalty == 0.1  # One critical optional missing


def test_calculate_penalty_multiple_critical_optional(
    temp_signatures_file: Path,
) -> None:
    """Test penalty calculation for multiple missing critical optional."""
    validator = SignatureRuntimeValidator(
        temp_signatures_file, penalty_for_missing_critical=0.2
    )

    result = ValidationResult(
        passed=True,
        hard_failures=[],
        soft_failures=[],
        warnings=[],
        missing_critical_optional=["ref1", "ref2", "ref3"],
    )

    penalty = validator.calculate_penalty(result)

    assert penalty == 0.6  # 3 * 0.2


def test_validate_method_call_success(temp_signatures_file: Path) -> None:
    """Test successful method call validation."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    passed, penalty, messages = validator.validate_method_call(
        "test_analyzer",
        {
            "extracted_text": "Some text",
            "question_id": "Q1",
            "reference_corpus": "corpus",
        },
        raise_on_failure=False,
    )

    assert passed is True
    assert penalty == 0.0


def test_validate_method_call_failure_raises(temp_signatures_file: Path) -> None:
    """Test method call validation raises on hard failure."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    with pytest.raises(ValueError, match="validation failed"):
        validator.validate_method_call(
            "test_analyzer",
            {
                "extracted_text": "Some text"
                # Missing "question_id"
            },
            raise_on_failure=True,
        )


def test_validate_method_call_failure_no_raise(temp_signatures_file: Path) -> None:
    """Test method call validation returns failure without raising."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    passed, penalty, messages = validator.validate_method_call(
        "test_analyzer",
        {
            "extracted_text": "Some text"
            # Missing "question_id"
        },
        raise_on_failure=False,
    )

    assert passed is False
    assert penalty == 1.0  # Hard failure
    assert len(messages) > 0


def test_validate_method_call_with_penalty(temp_signatures_file: Path) -> None:
    """Test method call validation with penalty for missing critical optional."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    passed, penalty, messages = validator.validate_method_call(
        "test_analyzer",
        {
            "extracted_text": "Some text",
            "question_id": "Q1",
            # Missing "reference_corpus" (critical optional)
        },
        raise_on_failure=False,
    )

    assert passed is True
    assert penalty > 0.0  # Should have penalty
    assert any("reference_corpus" in msg for msg in messages)


def test_validation_stats_tracking(temp_signatures_file: Path) -> None:
    """Test that validation statistics are tracked."""
    validator = SignatureRuntimeValidator(temp_signatures_file)

    # Make several validation calls
    validator.validate_inputs(
        "test_analyzer", {"extracted_text": "text", "question_id": "Q1"}
    )

    validator.validate_inputs(
        "test_analyzer",
        {
            "extracted_text": "text"
            # Missing required
        },
    )

    stats = validator.get_validation_stats()

    assert "test_analyzer" in stats
    assert stats["test_analyzer"]["calls"] == 2
    assert stats["test_analyzer"]["hard_failures"] == 1


def test_validate_nonexistent_method(temp_signatures_file: Path) -> None:
    """Test validation of non-existent method."""
    validator = SignatureRuntimeValidator(temp_signatures_file, strict_mode=True)

    result = validator.validate_inputs("nonexistent_method", {"input": "value"})

    assert result["passed"] is False
    assert any("not found" in failure for failure in result["hard_failures"])


def test_validate_nonexistent_method_non_strict(temp_signatures_file: Path) -> None:
    """Test validation of non-existent method in non-strict mode."""
    validator = SignatureRuntimeValidator(temp_signatures_file, strict_mode=False)

    result = validator.validate_inputs("nonexistent_method", {"input": "value"})

    assert result["passed"] is True  # Passes in non-strict mode
    assert len(result["warnings"]) > 0
