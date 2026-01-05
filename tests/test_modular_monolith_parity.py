"""
Parity tests: Modular questionnaire assembly vs. legacy monolith.

Validates that the modular resolver produces semantically equivalent
payloads to the legacy questionnaire_monolith.json file.

Run via pytest:
    pytest tests/test_modular_monolith_parity.py -v
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from farfan_pipeline.infrastructure.questionnaire import (
    QuestionnaireModularResolver,
    CountMismatchError,
    IdMismatchError,
)

# ---------------------------------------------------------------------------
# Fixture: project root and paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANONIC_ROOT = PROJECT_ROOT / "canonic_questionnaire_central"
MONOLITH_PATH = CANONIC_ROOT / "questionnaire_monolith.json"


@pytest.fixture(scope="module")
def resolver() -> QuestionnaireModularResolver:
    """Build a resolver anchored to the canonical directory."""
    return QuestionnaireModularResolver(root=CANONIC_ROOT)


@pytest.fixture(scope="module")
def monolith_data() -> dict:
    """Load the legacy monolith file for comparison."""
    if not MONOLITH_PATH.exists():
        pytest.skip("Monolith file not found; parity test skipped.")
    return json.loads(MONOLITH_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Test: counts match manifest totals
# ---------------------------------------------------------------------------


def test_policy_area_count_matches_manifest(resolver: QuestionnaireModularResolver) -> None:
    """Each policy area must have exactly 30 questions."""
    manifest = resolver._manifest
    for item in manifest["structure"]["policy_areas"]["items"]:
        pa_id = item["id"]
        expected = item["questions"]
        slice_obj = resolver.load_policy_area(pa_id, validate_ids=True)
        assert len(slice_obj.questions) == expected, f"{pa_id} count mismatch"


def test_dimension_count_matches_manifest(resolver: QuestionnaireModularResolver) -> None:
    """Each dimension must have exactly 50 questions."""
    manifest = resolver._manifest
    for item in manifest["structure"]["dimensions"]["items"]:
        dim_id = item["id"]
        expected = item["questions"]
        slice_obj = resolver.load_dimension(dim_id, validate_ids=True)
        assert len(slice_obj.questions) == expected, f"{dim_id} count mismatch"


def test_aggregate_total_300(resolver: QuestionnaireModularResolver) -> None:
    """Aggregated policy area questions must total 300."""
    aggregate = resolver.aggregate_policy_area_questions()
    assert len(aggregate.questions) == 300, "Expected 300 total questions"


# ---------------------------------------------------------------------------
# Test: ID ordering matches index
# ---------------------------------------------------------------------------


def test_policy_area_ids_ordered(resolver: QuestionnaireModularResolver) -> None:
    """Question IDs in each policy area must match the index order."""
    index = resolver._index["indices"]["by_policy_area"]
    for pa_id, record in index.items():
        expected_ids = record["question_ids"]
        slice_obj = resolver.load_policy_area(pa_id, validate_ids=True)
        actual_ids = [q["question_id"] for q in slice_obj.questions]
        assert actual_ids == expected_ids, f"{pa_id} ID order mismatch"


def test_dimension_ids_ordered(resolver: QuestionnaireModularResolver) -> None:
    """Question IDs in each dimension must match the index order."""
    index = resolver._index["indices"]["by_dimension"]
    for dim_id, record in index.items():
        expected_ids = record["question_ids"]
        slice_obj = resolver.load_dimension(dim_id, validate_ids=True)
        actual_ids = [q["question_id"] for q in slice_obj.questions]
        assert actual_ids == expected_ids, f"{dim_id} ID order mismatch"


# ---------------------------------------------------------------------------
# Test: parity with legacy monolith
# ---------------------------------------------------------------------------


def test_monolith_question_ids_parity(
    resolver: QuestionnaireModularResolver,
    monolith_data: dict,
) -> None:
    """Aggregate modular IDs must match monolith micro_questions IDs."""
    monolith_questions = monolith_data.get("blocks", {}).get("micro_questions", [])
    if not monolith_questions:
        pytest.skip("Monolith has no micro_questions block")

    monolith_ids = [q.get("question_id") for q in monolith_questions]
    aggregate = resolver.aggregate_policy_area_questions()
    modular_ids = [q["question_id"] for q in aggregate.questions]

    assert set(modular_ids) == set(monolith_ids), "ID sets diverge"
    # Order comparison (if ordering is expected to match policy area sequence)
    # Modular aggregates in PA order; monolith may differ. Check set equality here.


def test_monolith_canonical_notation_parity(
    resolver: QuestionnaireModularResolver,
    monolith_data: dict,
) -> None:
    """Canonical notation (dimensions/policy_areas) must align."""
    payload = resolver.build_monolith_payload()
    assembled = payload.data

    assembled_dims = set(assembled.get("canonical_notation", {}).get("dimensions", {}).keys())
    monolith_dims = set(monolith_data.get("canonical_notation", {}).get("dimensions", {}).keys())
    assert assembled_dims == monolith_dims, "Dimension keys diverge"

    assembled_pas = set(assembled.get("canonical_notation", {}).get("policy_areas", {}).keys())
    monolith_pas = set(monolith_data.get("canonical_notation", {}).get("policy_areas", {}).keys())
    assert assembled_pas == monolith_pas, "Policy area keys diverge"


def test_monolith_meso_macro_presence(
    resolver: QuestionnaireModularResolver,
    monolith_data: dict,
) -> None:
    """Assembled payload must contain meso and macro blocks if present in monolith."""
    payload = resolver.build_monolith_payload()
    assembled = payload.data

    if monolith_data.get("blocks", {}).get("meso_questions"):
        assert assembled["blocks"]["meso_questions"], "Missing meso_questions"
    if monolith_data.get("blocks", {}).get("macro_question"):
        assert assembled["blocks"]["macro_question"], "Missing macro_question"


# ---------------------------------------------------------------------------
# Test: deterministic SHA256
# ---------------------------------------------------------------------------


def test_modular_assembly_sha_stable(resolver: QuestionnaireModularResolver) -> None:
    """Two consecutive assemblies must yield identical SHA256."""
    payload1 = resolver.build_monolith_payload()
    payload2 = resolver.build_monolith_payload()
    assert payload1.sha256 == payload2.sha256, "Assembly not deterministic"


# ---------------------------------------------------------------------------
# Test: error handling for malformed selectors
# ---------------------------------------------------------------------------


def test_invalid_policy_area_raises(resolver: QuestionnaireModularResolver) -> None:
    """Requesting a non-existent policy area must raise."""
    with pytest.raises(Exception):
        resolver.load_policy_area("PA99")


def test_invalid_dimension_raises(resolver: QuestionnaireModularResolver) -> None:
    """Requesting a non-existent dimension must raise."""
    with pytest.raises(Exception):
        resolver.load_dimension("DIM99")
