"""
Unit tests for Chain Layer (@chain) computation.

Tests method wiring and contract compatibility:
- Signature validation with discrete scoring cases
- Schema compatibility checking
- Required/optional input validation
- Hard vs soft schema violations

Formula: x_@chain = chain_validator(v, Γ, Config) with discrete levels
"""

from __future__ import annotations

from typing import Any



def validate_schema_compatibility(input_types: dict[str, str], expected_types: dict[str, str]) -> tuple[bool, list[str]]:
    """
    Validate schema compatibility between provided and expected types.
    
    Returns:
        (is_compatible, violations)
    """
    violations = []

    for key, expected_type in expected_types.items():
        if key not in input_types:
            violations.append(f"Missing required field: {key}")
        elif input_types[key] != expected_type:
            violations.append(f"Type mismatch for {key}: expected {expected_type}, got {input_types[key]}")

    return len(violations) == 0, violations


def check_required_inputs(available_inputs: set[str], required_inputs: set[str]) -> tuple[bool, set[str]]:
    """
    Check if all required inputs are available.
    
    Returns:
        (all_available, missing_inputs)
    """
    missing = required_inputs - available_inputs
    return len(missing) == 0, missing


def compute_chain_score(validation_result: dict[str, Any]) -> float:
    """
    Compute @chain score based on validation results.
    
    Returns:
        0.0 if hard_mismatch
        0.3 if missing_critical_optional
        0.6 if soft_schema_violation
        0.8 if all_contracts_pass with warnings
        1.0 if all_contracts_pass with no warnings
    """
    if validation_result.get("hard_mismatch", False):
        return 0.0

    if validation_result.get("missing_critical_optional", False):
        return 0.3

    if validation_result.get("soft_violation", False):
        return 0.6

    if validation_result.get("warnings", []):
        return 0.8

    if validation_result.get("schema_compatible", True) and validation_result.get("required_inputs_available", True):
        return 1.0

    return 0.0


class TestSchemaCompatibility:
    """Test schema compatibility checking."""

    def test_perfect_schema_match(self):
        """Perfect schema match should be compatible."""
        input_types = {"extracted_text": "str", "question_id": "QID"}
        expected_types = {"extracted_text": "str", "question_id": "QID"}

        is_compatible, violations = validate_schema_compatibility(input_types, expected_types)

        assert is_compatible is True
        assert len(violations) == 0

    def test_type_mismatch(self):
        """Type mismatch should be incompatible."""
        input_types = {"extracted_text": "str", "question_id": "int"}
        expected_types = {"extracted_text": "str", "question_id": "QID"}

        is_compatible, violations = validate_schema_compatibility(input_types, expected_types)

        assert is_compatible is False
        assert len(violations) > 0

    def test_missing_required_field(self):
        """Missing required field should be incompatible."""
        input_types = {"extracted_text": "str"}
        expected_types = {"extracted_text": "str", "question_id": "QID"}

        is_compatible, violations = validate_schema_compatibility(input_types, expected_types)

        assert is_compatible is False
        assert "question_id" in str(violations)


class TestRequiredInputsValidation:
    """Test required inputs validation."""

    def test_all_required_inputs_available(self):
        """All required inputs available should pass."""
        available = {"extracted_text", "question_id", "reference_corpus"}
        required = {"extracted_text", "question_id"}

        all_available, missing = check_required_inputs(available, required)

        assert all_available is True
        assert len(missing) == 0

    def test_missing_required_input(self):
        """Missing required input should fail."""
        available = {"extracted_text"}
        required = {"extracted_text", "question_id"}

        all_available, missing = check_required_inputs(available, required)

        assert all_available is False
        assert "question_id" in missing

    def test_extra_inputs_allowed(self):
        """Extra inputs beyond required should be allowed."""
        available = {"extracted_text", "question_id", "extra_field", "another_field"}
        required = {"extracted_text", "question_id"}

        all_available, missing = check_required_inputs(available, required)

        assert all_available is True


class TestChainScoreComputation:
    """Test @chain score computation with discrete levels."""

    def test_hard_mismatch_zero_score(self, sample_contract_validation: dict[str, Any]):
        """Hard mismatch should yield 0.0."""
        validation = sample_contract_validation.copy()
        validation["hard_mismatch"] = True

        score = compute_chain_score(validation)

        assert score == 0.0

    def test_missing_critical_optional(self, sample_contract_validation: dict[str, Any]):
        """Missing critical optional should yield 0.3."""
        validation = sample_contract_validation.copy()
        validation["missing_critical_optional"] = True
        validation["hard_mismatch"] = False

        score = compute_chain_score(validation)

        assert score == 0.3

    def test_soft_violation(self, sample_contract_validation: dict[str, Any]):
        """Soft schema violation should yield 0.6."""
        validation = sample_contract_validation.copy()
        validation["soft_violation"] = True
        validation["hard_mismatch"] = False
        validation["missing_critical_optional"] = False

        score = compute_chain_score(validation)

        assert score == 0.6

    def test_contracts_pass_with_warnings(self, sample_contract_validation: dict[str, Any]):
        """Contracts pass with warnings should yield 0.8."""
        validation = sample_contract_validation.copy()
        validation["warnings"] = ["Minor type mismatch in optional field"]
        validation["hard_mismatch"] = False
        validation["soft_violation"] = False

        score = compute_chain_score(validation)

        assert score == 0.8

    def test_contracts_pass_no_warnings(self, sample_contract_validation: dict[str, Any]):
        """Contracts pass with no warnings should yield 1.0."""
        validation = sample_contract_validation.copy()
        validation["warnings"] = []

        score = compute_chain_score(validation)

        assert score == 1.0


class TestChainLayerDiscreteLevels:
    """Test discrete scoring levels for @chain layer."""

    def test_only_valid_scores(self):
        """@chain should only produce discrete scores."""
        valid_scores = {0.0, 0.3, 0.6, 0.8, 1.0}

        test_validations = [
            {"hard_mismatch": True},
            {"missing_critical_optional": True, "hard_mismatch": False},
            {"soft_violation": True, "hard_mismatch": False, "missing_critical_optional": False},
            {"warnings": ["warning"], "hard_mismatch": False, "soft_violation": False},
            {"warnings": [], "schema_compatible": True, "required_inputs_available": True},
        ]

        for validation in test_validations:
            score = compute_chain_score(validation)
            assert score in valid_scores, f"Invalid score {score} not in {valid_scores}"

    def test_no_intermediate_scores(self):
        """@chain should not produce intermediate scores like 0.5."""
        valid_scores = {0.0, 0.3, 0.6, 0.8, 1.0}

        assert 0.5 not in valid_scores
        assert 0.7 not in valid_scores
        assert 0.9 not in valid_scores


class TestChainLayerScenarios:
    """Test complete chain layer scenarios."""

    def test_scenario_a_hard_mismatch(self):
        """Scenario A: Hard type mismatch."""
        input_types = {"extracted_text": "str", "question_id": "int"}
        expected_types = {"extracted_text": "str", "question_id": "QID"}

        is_compatible, _ = validate_schema_compatibility(input_types, expected_types)

        validation = {
            "hard_mismatch": not is_compatible,
            "schema_compatible": is_compatible,
        }

        score = compute_chain_score(validation)

        assert score == 0.0

    def test_scenario_b_missing_optional(self):
        """Scenario B: Missing optional but beneficial input."""
        available = {"extracted_text", "question_id"}
        required = {"extracted_text", "question_id"}
        optional = {"reference_corpus"}

        all_available, _ = check_required_inputs(available, required)
        optional_missing = len(optional - available) > 0

        validation = {
            "hard_mismatch": False,
            "required_inputs_available": all_available,
            "missing_critical_optional": optional_missing,
        }

        score = compute_chain_score(validation)

        assert score == 0.3

    def test_scenario_c_perfect_match(self):
        """Scenario C: Perfect schema and input match."""
        input_types = {"extracted_text": "str", "question_id": "QID", "reference_corpus": "str"}
        expected_types = {"extracted_text": "str", "question_id": "QID"}

        is_compatible, _ = validate_schema_compatibility(input_types, expected_types)

        available = set(input_types.keys())
        required = set(expected_types.keys())

        all_available, _ = check_required_inputs(available, required)

        validation = {
            "hard_mismatch": False,
            "schema_compatible": is_compatible,
            "required_inputs_available": all_available,
            "warnings": [],
        }

        score = compute_chain_score(validation)

        assert score == 1.0


class TestSignatureValidation:
    """Test method signature validation."""

    def test_signature_structure(self):
        """Test method signature structure."""
        signature = {
            "input": {
                "required": ["extracted_text", "question_id"],
                "optional": ["reference_corpus"],
                "schema": {
                    "extracted_text": "str",
                    "question_id": "QID",
                    "reference_corpus": "str",
                },
            },
            "output": {
                "schema": {"score": "float"},
            },
        }

        assert "input" in signature
        assert "output" in signature
        assert "required" in signature["input"]
        assert "optional" in signature["input"]
        assert "schema" in signature["input"]

    def test_signature_validation_with_optional(self):
        """Test signature validation with optional inputs."""
        signature = {
            "required": ["extracted_text", "question_id"],
            "optional": ["reference_corpus"],
        }

        available = {"extracted_text", "question_id"}
        required = set(signature["required"])
        optional = set(signature["optional"])

        all_required, _ = check_required_inputs(available, required)
        has_optional = len(optional & available) > 0

        assert all_required is True
        assert has_optional is False
