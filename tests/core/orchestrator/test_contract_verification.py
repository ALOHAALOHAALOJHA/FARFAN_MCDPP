"""Tests for pre-execution contract verification in BaseExecutorWithContract.

This test module validates the contract verification functionality that ensures
all 30 base executor contracts are valid before execution begins.
"""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from farfan_pipeline.core.orchestrator.base_executor_with_contract import (
    BaseExecutorWithContract,
)


class TestContractVerification:
    """Test suite for contract verification functionality."""

    def test_verify_all_base_contracts_calls_verify_single(self):
        """Test that verify_all_base_contracts attempts to verify all 30 contracts."""
        with patch.object(
            BaseExecutorWithContract,
            "_verify_single_contract",
            return_value={
                "passed": True,
                "errors": [],
                "warnings": [],
                "contract_version": "v3",
                "contract_path": "/fake/path",
            },
        ) as mock_verify:
            result = BaseExecutorWithContract.verify_all_base_contracts(
                class_registry={}
            )

            assert mock_verify.call_count == 30
            assert result["total_contracts"] == 30
            assert result["passed"] is True
            assert len(result["verified_contracts"]) == 30

    def test_verify_all_base_contracts_with_errors(self):
        """Test that errors are accumulated correctly."""

        def mock_verify_single(base_slot, class_registry=None):
            if base_slot in ["D1-Q1", "D2-Q2"]:
                return {
                    "passed": False,
                    "errors": [f"Error in {base_slot}"],
                    "warnings": [],
                    "contract_version": "v3",
                    "contract_path": "/fake/path",
                }
            return {
                "passed": True,
                "errors": [],
                "warnings": [],
                "contract_version": "v3",
                "contract_path": "/fake/path",
            }

        with patch.object(
            BaseExecutorWithContract,
            "_verify_single_contract",
            side_effect=mock_verify_single,
        ):
            result = BaseExecutorWithContract.verify_all_base_contracts(
                class_registry={}
            )

            assert result["total_contracts"] == 30
            assert result["passed"] is False
            assert len(result["errors"]) == 2
            assert len(result["verified_contracts"]) == 28
            assert any("D1-Q1" in err for err in result["errors"])
            assert any("D2-Q2" in err for err in result["errors"])

    def test_verify_all_base_contracts_caches_result(self):
        """Test that subsequent calls use cached result."""
        BaseExecutorWithContract._factory_contracts_verified = False
        BaseExecutorWithContract._factory_verification_errors = []

        with patch.object(
            BaseExecutorWithContract,
            "_verify_single_contract",
            return_value={
                "passed": True,
                "errors": [],
                "warnings": [],
                "contract_version": "v3",
                "contract_path": "/fake/path",
            },
        ) as mock_verify:
            result1 = BaseExecutorWithContract.verify_all_base_contracts(
                class_registry={}
            )
            result2 = BaseExecutorWithContract.verify_all_base_contracts(
                class_registry={}
            )

            assert mock_verify.call_count == 30
            assert result1 == result2

    def test_verify_single_contract_missing_file(self):
        """Test verification fails when contract file doesn't exist."""
        BaseExecutorWithContract._factory_contracts_verified = False

        result = BaseExecutorWithContract._verify_single_contract(
            "D99-Q99", class_registry={}
        )

        assert result["passed"] is False
        assert len(result["errors"]) > 0
        assert any("not found" in err.lower() for err in result["errors"])
        assert result["contract_path"] is None

    def test_verify_v2_contract_fields(self):
        """Test v2 contract field validation."""
        valid_contract = {
            "method_inputs": [
                {"class": "TestClass", "method": "test_method"}
            ],
            "assembly_rules": [],
            "validation_rules": [],
        }

        errors = BaseExecutorWithContract._verify_v2_contract_fields(
            valid_contract, "D1-Q1", class_registry={"TestClass": object}
        )
        assert len(errors) == 0

    def test_verify_v2_contract_missing_fields(self):
        """Test v2 contract validation catches missing fields."""
        invalid_contract = {
            "method_inputs": []
        }

        errors = BaseExecutorWithContract._verify_v2_contract_fields(
            invalid_contract, "D1-Q1", class_registry={}
        )

        assert len(errors) >= 2
        assert any("assembly_rules" in err for err in errors)
        assert any("validation_rules" in err for err in errors)

    def test_verify_v2_contract_method_class_not_in_registry(self):
        """Test v2 contract validation catches missing method classes."""
        contract = {
            "method_inputs": [
                {"class": "MissingClass", "method": "test_method"}
            ],
            "assembly_rules": [],
            "validation_rules": [],
        }

        errors = BaseExecutorWithContract._verify_v2_contract_fields(
            contract, "D1-Q1", class_registry={}
        )

        assert len(errors) >= 1
        assert any("MissingClass" in err and "not found" in err for err in errors)

    def test_verify_v3_contract_fields(self):
        """Test v3 contract field validation."""
        valid_contract = {
            "identity": {
                "base_slot": "D1-Q1"
            },
            "method_binding": {
                "orchestration_mode": "single_method",
                "class_name": "TestClass",
                "method_name": "test_method",
            },
            "evidence_assembly": {
                "assembly_rules": []
            },
            "validation_rules": {},
            "question_context": {
                "expected_elements": []
            },
            "error_handling": {},
        }

        errors = BaseExecutorWithContract._verify_v3_contract_fields(
            valid_contract, "D1-Q1", class_registry={"TestClass": object}
        )
        assert len(errors) == 0

    def test_verify_v3_contract_missing_identity(self):
        """Test v3 contract validation catches missing identity."""
        invalid_contract = {
            "method_binding": {},
            "evidence_assembly": {"assembly_rules": []},
            "validation_rules": {},
            "question_context": {"expected_elements": []},
            "error_handling": {},
        }

        errors = BaseExecutorWithContract._verify_v3_contract_fields(
            invalid_contract, "D1-Q1", class_registry={}
        )

        assert any("identity" in err.lower() for err in errors)

    def test_verify_v3_contract_base_slot_mismatch(self):
        """Test v3 contract validation catches base_slot mismatch."""
        contract = {
            "identity": {
                "base_slot": "D2-Q1"
            },
            "method_binding": {
                "class_name": "TestClass",
                "method_name": "test_method",
            },
            "evidence_assembly": {"assembly_rules": []},
            "validation_rules": {},
            "question_context": {"expected_elements": []},
            "error_handling": {},
        }

        errors = BaseExecutorWithContract._verify_v3_contract_fields(
            contract, "D1-Q1", class_registry={"TestClass": object}
        )

        assert any("mismatch" in err.lower() and "D1-Q1" in err for err in errors)

    def test_verify_v3_contract_multi_method_pipeline(self):
        """Test v3 contract validation for multi_method_pipeline mode."""
        contract = {
            "identity": {"base_slot": "D1-Q1"},
            "method_binding": {
                "orchestration_mode": "multi_method_pipeline",
                "methods": [
                    {"class_name": "Class1", "method_name": "method1"},
                    {"class_name": "Class2", "method_name": "method2"},
                ]
            },
            "evidence_assembly": {"assembly_rules": []},
            "validation_rules": {},
            "question_context": {"expected_elements": []},
            "error_handling": {},
        }

        errors = BaseExecutorWithContract._verify_v3_contract_fields(
            contract,
            "D1-Q1",
            class_registry={"Class1": object, "Class2": object}
        )

        assert len(errors) == 0

    def test_verify_v3_contract_multi_method_missing_class(self):
        """Test v3 multi-method validation catches missing classes."""
        contract = {
            "identity": {"base_slot": "D1-Q1"},
            "method_binding": {
                "orchestration_mode": "multi_method_pipeline",
                "methods": [
                    {"class_name": "Class1", "method_name": "method1"},
                    {"class_name": "MissingClass", "method_name": "method2"},
                ]
            },
            "evidence_assembly": {"assembly_rules": []},
            "validation_rules": {},
            "question_context": {"expected_elements": []},
            "error_handling": {},
        }

        errors = BaseExecutorWithContract._verify_v3_contract_fields(
            contract,
            "D1-Q1",
            class_registry={"Class1": object}
        )

        assert any("MissingClass" in err and "not found" in err for err in errors)

    def test_verify_v3_contract_missing_expected_elements(self):
        """Test v3 contract validation catches missing expected_elements."""
        contract = {
            "identity": {"base_slot": "D1-Q1"},
            "method_binding": {
                "class_name": "TestClass",
                "method_name": "test_method",
            },
            "evidence_assembly": {"assembly_rules": []},
            "validation_rules": {},
            "question_context": {},
            "error_handling": {},
        }

        errors = BaseExecutorWithContract._verify_v3_contract_fields(
            contract, "D1-Q1", class_registry={"TestClass": object}
        )

        assert any("expected_elements" in err for err in errors)

    def test_base_slot_to_q_number_calculation(self):
        """Test that base slot to Q number calculation is correct."""
        test_cases = [
            ("D1-Q1", "Q001"),
            ("D1-Q5", "Q005"),
            ("D2-Q1", "Q006"),
            ("D3-Q3", "Q013"),
            ("D6-Q5", "Q030"),
        ]

        for base_slot, expected_q_id in test_cases:
            dimension = int(base_slot[1])
            question = int(base_slot[4])
            q_number = (dimension - 1) * 5 + question
            q_id = f"Q{q_number:03d}"
            assert q_id == expected_q_id, f"Failed for {base_slot}: got {q_id}, expected {expected_q_id}"
