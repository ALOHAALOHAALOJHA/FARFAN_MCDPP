"""
Tests for ContractHydrator.

Verifies:
1. V4 contracts are correctly hydrated
2. V3 contracts pass through unchanged
3. Overrides are applied correctly
4. Hydration is idempotent
5. Hydrated contracts are Carver-compatible

Run with: pytest tests/phases/phase_two/test_contract_hydrator.py -v
"""

from __future__ import annotations

import copy
import pytest
from typing import Any, Dict
from unittest.mock import MagicMock

from farfan_pipeline.phases.Phase_two.phase2_95_00_contract_hydrator import (
    ContractHydrator,
    ContractHydrationError,
    HydrationResult,
)


@pytest.fixture
def mock_signal_pack() -> MagicMock:
    """Create mock signal pack with all required fields."""
    pack = MagicMock()
    pack.question_text = "¿El plan declara la alineación de sus resultados?"
    pack.question_type = "micro"
    pack.dimension_id = "DIM04"
    pack.policy_area_id = "PA08"
    pack.scoring_modality = "TYPE_A"
    pack.modality = "TYPE_A"
    pack.expected_elements = {
        "Q230": [
            MagicMock(
                model_dump=lambda: {"type": "alineacion_pnd", "required": True, "minimum": 1}
            ),
            MagicMock(
                model_dump=lambda: {"type": "alineacion_ods", "required": True, "minimum": 1}
            ),
        ]
    }
    pack.question_patterns = {
        "Q230": [
            MagicMock(model_dump=lambda: {"id": "PAT-Q230-000", "pattern": "PND|Plan Nacional"}),
            MagicMock(model_dump=lambda: {"id": "PAT-Q230-001", "pattern": "ODS|Objetivos"}),
        ]
    }
    return pack


@pytest.fixture
def mock_signal_registry(mock_signal_pack: MagicMock) -> MagicMock:
    """Create mock signal registry."""
    registry = MagicMock()
    registry.get_micro_answering_signals.return_value = mock_signal_pack
    return registry


@pytest.fixture
def hydrator(mock_signal_registry: MagicMock) -> ContractHydrator:
    """Create hydrator with mock registry."""
    return ContractHydrator(mock_signal_registry)


@pytest.fixture
def v4_contract() -> Dict[str, Any]:
    """Create a v4 streamlined contract."""
    return {
        "identity": {
            "base_slot": "D4-Q5",
            "question_id": "Q230",
            "contract_version": "4.0.0",
        },
        "executor_binding": {
            "executor_class": "D4_Q5_Executor",
            "executor_module": "farfan_core.core.orchestrator.executors",
        },
        "method_binding": {
            "orchestration_mode": "epistemological_pipeline",
            "method_count": 6,
        },
        "question_context": {
            "monolith_ref": "Q230",
            "overrides": None,
            "failure_contract": {
                "abort_if": ["missing_required_element"],
                "emit_code": "ABORT-Q230-REQ",
            },
        },
        "human_answer_structure": {
            "format": "markdown",
            "template_mode": "epistemological_narrative",
        },
    }


@pytest.fixture
def v3_contract() -> Dict[str, Any]:
    """Create a v3 contract with all fields present."""
    return {
        "identity": {
            "base_slot": "D4-Q5",
            "question_id": "Q230",
            "dimension_id": "DIM04",
            "policy_area_id": "PA08",
            "contract_version": "3.0.0",
        },
        "question_context": {
            "question_text": "¿El plan declara la alineación?",
            "question_type": "micro",
            "scoring_modality": "TYPE_A",
            "modality": "TYPE_A",
            "expected_elements": [
                {"type": "alineacion_pnd", "required": True},
            ],
            "patterns": [
                {"id": "PAT-Q230-000", "pattern": "PND"},
            ],
        },
    }


class TestV4ContractHydration:
    """Test hydration of v4 streamlined contracts."""

    def test_hydrates_question_text(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """V4 contract gets question_text from signals."""
        result = hydrator.hydrate(v4_contract)

        assert "question_text" in result["question_context"]
        assert (
            result["question_context"]["question_text"]
            == "¿El plan declara la alineación de sus resultados?"
        )

    def test_hydrates_expected_elements(
        self, hydrator: ContractHydrator, v4_contract: Dict
    ) -> None:
        """V4 contract gets expected_elements from signals."""
        result = hydrator.hydrate(v4_contract)

        assert "expected_elements" in result["question_context"]
        assert len(result["question_context"]["expected_elements"]) == 2

    def test_hydrates_patterns(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """V4 contract gets patterns from signals."""
        result = hydrator.hydrate(v4_contract)

        assert "patterns" in result["question_context"]
        assert len(result["question_context"]["patterns"]) == 2

    def test_hydrates_identity_fields(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """V4 contract gets dimension_id and policy_area_id."""
        result = hydrator.hydrate(v4_contract)

        assert result["identity"]["dimension_id"] == "DIM04"
        assert result["identity"]["policy_area_id"] == "PA08"

    def test_preserves_original_fields(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """Hydration preserves existing contract fields."""
        result = hydrator.hydrate(v4_contract)

        assert result["identity"]["base_slot"] == "D4-Q5"
        assert result["executor_binding"]["executor_class"] == "D4_Q5_Executor"
        assert result["question_context"]["failure_contract"]["emit_code"] == "ABORT-Q230-REQ"

    def test_adds_hydration_metadata(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """Hydration adds metadata about the process."""
        result = hydrator.hydrate(v4_contract)

        assert "_hydration_metadata" in result
        assert result["_hydration_metadata"]["was_hydrated"] is True
        assert result["_hydration_metadata"]["source_question_id"] == "Q230"
        assert len(result["_hydration_metadata"]["fields_injected"]) > 0

    def test_does_not_mutate_original(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """Hydration does not mutate the original contract."""
        original = copy.deepcopy(v4_contract)
        hydrator.hydrate(v4_contract)

        assert v4_contract == original


class TestV3ContractPassthrough:
    """Test that v3 contracts pass through unchanged."""

    def test_v3_not_modified(self, hydrator: ContractHydrator, v3_contract: Dict) -> None:
        """V3 contract is returned unchanged."""
        result = hydrator.hydrate(v3_contract)

        assert "_hydration_metadata" not in result or not result.get("_hydration_metadata", {}).get(
            "was_hydrated"
        )

    def test_v3_preserves_all_fields(self, hydrator: ContractHydrator, v3_contract: Dict) -> None:
        """V3 contract preserves all its original fields."""
        original = copy.deepcopy(v3_contract)
        result = hydrator.hydrate(v3_contract)

        assert (
            result["question_context"]["question_text"]
            == original["question_context"]["question_text"]
        )
        assert (
            result["question_context"]["expected_elements"]
            == original["question_context"]["expected_elements"]
        )


class TestHydrationIdempotence:
    """Test that hydration is idempotent."""

    def test_double_hydration_same_result(
        self, hydrator: ContractHydrator, v4_contract: Dict
    ) -> None:
        """Hydrating twice produces same result."""
        first = hydrator.hydrate(v4_contract)
        second = hydrator.hydrate(first)

        first_clean = {k: v for k, v in first.items() if k != "_hydration_metadata"}
        second_clean = {k: v for k, v in second.items() if k != "_hydration_metadata"}

        assert first_clean == second_clean

    def test_already_hydrated_detected(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """Already hydrated contracts are detected."""
        first = hydrator.hydrate(v4_contract)

        assert hydrator._is_already_hydrated(first)


class TestOverrides:
    """Test that overrides are applied correctly."""

    def test_override_question_text(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """Override question_text takes precedence."""
        v4_contract["question_context"]["overrides"] = {"question_text": "Custom question text"}

        result = hydrator.hydrate(v4_contract)

        assert result["question_context"]["question_text"] == "Custom question text"
        assert "question_text" in result["_hydration_metadata"]["overrides_applied"]

    def test_override_expected_elements(
        self, hydrator: ContractHydrator, v4_contract: Dict
    ) -> None:
        """Override expected_elements takes precedence."""
        custom_elements = [{"type": "custom_type", "required": True}]
        v4_contract["question_context"]["overrides"] = {"expected_elements": custom_elements}

        result = hydrator.hydrate(v4_contract)

        assert result["question_context"]["expected_elements"] == custom_elements


class TestErrorHandling:
    """Test error handling in hydration."""

    def test_missing_question_id_raises(self, hydrator: ContractHydrator) -> None:
        """Contract without question_id raises error."""
        bad_contract = {
            "identity": {"base_slot": "D4-Q5"},
            "question_context": {},
        }

        with pytest.raises(ContractHydrationError) as exc_info:
            hydrator.hydrate(bad_contract)

        assert "must have question_context.monolith_ref" in str(exc_info.value)

    def test_signal_fetch_failure_raises(
        self, mock_signal_registry: MagicMock, v4_contract: Dict
    ) -> None:
        """Signal fetch failure raises error."""
        mock_signal_registry.get_micro_answering_signals.side_effect = ValueError(
            "Question not found"
        )

        hydrator = ContractHydrator(mock_signal_registry)

        with pytest.raises(ContractHydrationError) as exc_info:
            hydrator.hydrate(v4_contract)

        assert "Failed to fetch signals" in str(exc_info.value)


class TestValidation:
    """Test contract validation."""

    def test_validate_complete_contract(
        self, hydrator: ContractHydrator, v4_contract: Dict
    ) -> None:
        """Complete hydrated contract passes validation."""
        hydrated = hydrator.hydrate(v4_contract)
        issues = hydrator.validate_hydrated_contract(hydrated)

        assert len(issues) == 0

    def test_validate_incomplete_contract(self, hydrator: ContractHydrator) -> None:
        """Incomplete contract fails validation."""
        incomplete = {
            "identity": {},
            "question_context": {
                "question_text": "Some text",
            },
        }

        issues = hydrator.validate_hydrated_contract(incomplete)

        assert len(issues) > 0
        assert any("expected_elements" in issue for issue in issues)


class TestV4Detection:
    """Test v4 contract detection."""

    def test_detects_v4_contract(self, hydrator: ContractHydrator, v4_contract: Dict) -> None:
        """V4 contract is correctly detected."""
        assert hydrator.is_v4_contract(v4_contract) is True

    def test_detects_v3_contract(self, hydrator: ContractHydrator, v3_contract: Dict) -> None:
        """V3 contract is not detected as v4."""
        assert hydrator.is_v4_contract(v3_contract) is False

    def test_hydrated_not_detected_as_v4(
        self, hydrator: ContractHydrator, v4_contract: Dict
    ) -> None:
        """Hydrated v4 contract is not detected as v4."""
        hydrated = hydrator.hydrate(v4_contract)
        assert hydrator.is_v4_contract(hydrated) is False
