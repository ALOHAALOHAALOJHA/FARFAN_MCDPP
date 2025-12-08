"""
Tests for method signature chain layer validation.

Validates that signature validation system properly:
- Detects missing required fields
- Validates signature completeness
- Classifies input types correctly
- Generates proper validation reports
"""

import json
from pathlib import Path

import pytest

from farfan_pipeline.core.orchestrator.method_signature_validator import (
    MethodSignatureValidator,
)


@pytest.fixture
def temp_signatures_file(tmp_path: Path) -> Path:
    """Create temporary signatures file for testing."""
    signatures_data = {
        "signatures_version": "2.0.0",
        "last_updated": "2025-01-01",
        "schema_version": "chain_layer_validation_v1",
        "methods": {
            "complete_method": {
                "signature": {
                    "required_inputs": ["text", "question_id"],
                    "optional_inputs": ["context", "threshold"],
                    "critical_optional": ["context"],
                    "output_type": "float",
                    "output_range": [0.0, 1.0],
                    "description": "Complete method signature",
                }
            },
            "minimal_method": {
                "signature": {"required_inputs": ["text"], "output_type": "dict"}
            },
            "invalid_method_missing_required": {
                "signature": {"optional_inputs": ["context"], "output_type": "str"}
            },
            "invalid_method_wrong_types": {
                "signature": {"required_inputs": "not_a_list", "output_type": "float"}
            },
        },
    }

    signatures_file = tmp_path / "method_signatures.json"
    with open(signatures_file, "w") as f:
        json.dump(signatures_data, f, indent=2)

    return signatures_file


def test_validator_loads_signatures(temp_signatures_file: Path) -> None:
    """Test that validator can load signatures file."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    assert validator.signatures_data is not None
    assert "methods" in validator.signatures_data
    assert len(validator.signatures_data["methods"]) == 4


def test_validate_complete_signature(temp_signatures_file: Path) -> None:
    """Test validation of complete signature."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = {
        "required_inputs": ["text", "question_id"],
        "optional_inputs": ["context", "threshold"],
        "critical_optional": ["context"],
        "output_type": "float",
        "output_range": [0.0, 1.0],
        "description": "Complete method signature",
    }

    result = validator.validate_signature("complete_method", signature)

    assert result["is_valid"] is True
    assert len(result["missing_fields"]) == 0
    assert len(result["issues"]) == 0


def test_validate_minimal_signature(temp_signatures_file: Path) -> None:
    """Test validation of minimal valid signature."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = {"required_inputs": ["text"], "output_type": "dict"}

    result = validator.validate_signature("minimal_method", signature)

    assert result["is_valid"] is True
    assert len(result["missing_fields"]) == 0
    # Should have warnings for missing recommended fields
    assert len(result["warnings"]) > 0


def test_validate_missing_required_inputs(temp_signatures_file: Path) -> None:
    """Test detection of missing required_inputs field."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = {"optional_inputs": ["context"], "output_type": "str"}

    result = validator.validate_signature("invalid_method", signature)

    assert result["is_valid"] is False
    assert "required_inputs" in result["missing_fields"]
    assert any("required_inputs" in issue for issue in result["issues"])


def test_validate_missing_output_type(temp_signatures_file: Path) -> None:
    """Test detection of missing output_type field."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = {"required_inputs": ["text"]}

    result = validator.validate_signature("invalid_method", signature)

    assert result["is_valid"] is False
    assert "output_type" in result["missing_fields"]


def test_validate_invalid_required_inputs_type(temp_signatures_file: Path) -> None:
    """Test detection of wrong type for required_inputs."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = {"required_inputs": "not_a_list", "output_type": "float"}

    result = validator.validate_signature("invalid_method", signature)

    assert result["is_valid"] is False
    assert any("must be a list" in issue for issue in result["issues"])


def test_validate_invalid_output_range(temp_signatures_file: Path) -> None:
    """Test detection of invalid output_range."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    # Test output_range with wrong length
    signature = {
        "required_inputs": ["text"],
        "output_type": "float",
        "output_range": [0.0],  # Should be 2 elements
    }

    result = validator.validate_signature("test_method", signature)

    assert result["is_valid"] is False
    assert any("exactly 2 elements" in issue for issue in result["issues"])


def test_validate_invalid_range_order(temp_signatures_file: Path) -> None:
    """Test detection of invalid range order (min >= max)."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = {
        "required_inputs": ["text"],
        "output_type": "float",
        "output_range": [1.0, 0.0],  # min > max
    }

    result = validator.validate_signature("test_method", signature)

    assert result["is_valid"] is False
    assert any("min must be less than max" in issue for issue in result["issues"])


def test_validate_critical_optional_not_in_optional(temp_signatures_file: Path) -> None:
    """Test warning when critical_optional not in optional_inputs."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = {
        "required_inputs": ["text"],
        "optional_inputs": ["context"],
        "critical_optional": ["threshold"],  # Not in optional_inputs
        "output_type": "dict",
    }

    result = validator.validate_signature("test_method", signature)

    assert any(
        "not found in optional_inputs" in warning for warning in result["warnings"]
    )


def test_validate_all_signatures(temp_signatures_file: Path) -> None:
    """Test validation of all signatures in file."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    report = validator.validate_all_signatures()

    assert report["total_methods"] == 4
    assert report["valid_methods"] >= 2  # complete_method and minimal_method
    assert report["invalid_methods"] >= 2  # invalid methods
    assert "completeness_rate" in report["summary"]


def test_check_signature_completeness(temp_signatures_file: Path) -> None:
    """Test checking completeness of specific method signature."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    assert validator.check_signature_completeness("complete_method") is True
    assert validator.check_signature_completeness("minimal_method") is True
    assert (
        validator.check_signature_completeness("invalid_method_missing_required")
        is False
    )


def test_get_method_signature(temp_signatures_file: Path) -> None:
    """Test retrieving method signature by ID."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = validator.get_method_signature("complete_method")

    assert signature is not None
    assert "required_inputs" in signature
    assert "text" in signature["required_inputs"]
    assert "question_id" in signature["required_inputs"]


def test_get_nonexistent_method_signature(temp_signatures_file: Path) -> None:
    """Test retrieving signature for non-existent method."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    signature = validator.get_method_signature("nonexistent_method")

    assert signature is None


def test_validation_report_has_summary_statistics(temp_signatures_file: Path) -> None:
    """Test that validation report includes summary statistics."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    report = validator.validate_all_signatures()

    assert "summary" in report
    assert "completeness_rate" in report["summary"]
    assert "output_type_distribution" in report["summary"]
    assert "most_common_required_inputs" in report["summary"]


def test_validation_report_has_timestamp(temp_signatures_file: Path) -> None:
    """Test that validation report includes timestamp."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    report = validator.validate_all_signatures()

    assert "validation_timestamp" in report
    assert "Z" in report["validation_timestamp"]  # UTC timestamp


def test_generate_validation_report_creates_file(
    temp_signatures_file: Path, tmp_path: Path
) -> None:
    """Test that validation report is generated as JSON file."""
    validator = MethodSignatureValidator(temp_signatures_file)
    validator.load_signatures()

    output_path = tmp_path / "validation_report.json"
    validator.generate_validation_report(output_path)

    assert output_path.exists()

    with open(output_path) as f:
        report = json.load(f)

    assert "validation_timestamp" in report
    assert "total_methods" in report
    assert "validation_details" in report
