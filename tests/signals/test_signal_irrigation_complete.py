"""
Signal Irrigation Completeness Test
====================================

Verifies that ALL 300 questions receive complete signal irrigation with
all fields required by Carver and downstream components.

This test ensures 100% Intelligence Utilization across the pipeline.
"""

import pytest
import json
from pathlib import Path

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
    QuestionnaireSignalRegistry,
)


REQUIRED_SIGNAL_FIELDS = [
    "question_text",
    "question_type",
    "expected_elements",
    "patterns",
    "dimension_id",
    "policy_area_id",
    "scoring_modality",
    "modality",
]


class SimpleQuestionnaire:
    """Minimal questionnaire wrapper for testing."""

    def __init__(self, data):
        self.data = data
        self.version = data.get("metadata", {}).get("version", "unknown")
        self.sha256 = ""


@pytest.fixture(scope="module")
def signal_registry():
    """Load questionnaire and create registry once for all tests."""
    questionnaire_path = Path("canonic_questionnaire_central/questionnaire_monolith.json")
    with open(questionnaire_path) as f:
        questionnaire_data = json.load(f)

    questionnaire = SimpleQuestionnaire(questionnaire_data)
    return QuestionnaireSignalRegistry(questionnaire)


@pytest.mark.parametrize("question_id", [f"Q{i:03d}" for i in range(1, 301)])
def test_all_questions_irrigate_complete_signals(signal_registry, question_id):
    """Every question must have all required signal fields populated."""
    signals = signal_registry.get_micro_answering_signals(question_id)

    missing_fields = []
    empty_fields = []

    for field in REQUIRED_SIGNAL_FIELDS:
        value = getattr(signals, field, None)

        if value is None:
            missing_fields.append(field)
        elif value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
            empty_fields.append(field)

    error_msg = []
    if missing_fields:
        error_msg.append(f"Missing fields: {', '.join(missing_fields)}")
    if empty_fields:
        error_msg.append(f"Empty fields: {', '.join(empty_fields)}")

    assert not error_msg, f"{question_id}: {'; '.join(error_msg)}"


def test_signal_registry_loads_300_questions(signal_registry):
    """Verify registry can access all 300 questions."""
    success_count = 0
    failed_questions = []

    for i in range(1, 301):
        question_id = f"Q{i:03d}"
        try:
            signals = signal_registry.get_micro_answering_signals(question_id)
            if signals:
                success_count += 1
        except Exception as e:
            failed_questions.append((question_id, str(e)))

    assert success_count == 300, (
        f"Only {success_count}/300 questions loaded successfully. "
        f"Failed: {failed_questions[:5]}"
    )


def test_policy_area_distribution(signal_registry):
    """Verify questions are distributed across all policy areas."""
    policy_areas = set()

    for i in range(1, 301):
        question_id = f"Q{i:03d}"
        signals = signal_registry.get_micro_answering_signals(question_id)
        if signals.policy_area_id:
            policy_areas.add(signals.policy_area_id)

    assert (
        len(policy_areas) == 10
    ), f"Expected 10 policy areas, found {len(policy_areas)}: {sorted(policy_areas)}"


def test_scoring_modality_coverage(signal_registry):
    """Verify all questions have a scoring modality assigned."""
    missing_modality = []
    modalities = set()

    for i in range(1, 301):
        question_id = f"Q{i:03d}"
        signals = signal_registry.get_micro_answering_signals(question_id)

        if not signals.scoring_modality:
            missing_modality.append(question_id)
        else:
            modalities.add(signals.scoring_modality)

    assert not missing_modality, (
        f"{len(missing_modality)} questions missing scoring_modality: " f"{missing_modality[:10]}"
    )
    assert len(modalities) > 0, "No scoring modalities found"


def test_dimension_coverage(signal_registry):
    """Verify questions are mapped to dimensions."""
    dimensions = set()
    missing_dimension = []

    for i in range(1, 301):
        question_id = f"Q{i:03d}"
        signals = signal_registry.get_micro_answering_signals(question_id)

        if not signals.dimension_id:
            missing_dimension.append(question_id)
        else:
            dimensions.add(signals.dimension_id)

    assert not missing_dimension, (
        f"{len(missing_dimension)} questions missing dimension_id: " f"{missing_dimension[:10]}"
    )
    assert len(dimensions) >= 1, "No dimensions found"


@pytest.mark.parametrize("question_id", ["Q001", "Q030", "Q150", "Q230", "Q300"])
def test_critical_questions_fully_irrigated(signal_registry, question_id):
    """Spot check critical questions for complete irrigation."""
    signals = signal_registry.get_micro_answering_signals(question_id)

    assert signals.question_text, f"{question_id}: No question text"
    assert signals.question_type == "micro", f"{question_id}: Wrong type"
    assert signals.dimension_id, f"{question_id}: No dimension"
    assert signals.policy_area_id, f"{question_id}: No policy area"
    assert signals.scoring_modality, f"{question_id}: No scoring modality"
    assert signals.modality == signals.scoring_modality, f"{question_id}: modality mismatch"

    assert signals.expected_elements, f"{question_id}: No expected elements"
    assert signals.patterns, f"{question_id}: No patterns"
