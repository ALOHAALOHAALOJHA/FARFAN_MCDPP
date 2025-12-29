from __future__ import annotations

import sys
from dataclasses import dataclass, fields
from pathlib import Path

import pytest

# Keep consistent with the rest of the repo's tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from classification.hash_utils import compute_classification_hash, decision_payload_for_hash


@dataclass(frozen=True)
class MethodDecisionFixture:
    level: str
    epistemology: str
    decision_path: str
    skip_rest: bool
    precheck: bool


def test_decision_payload_covers_all_dataclass_fields() -> None:
    decision = MethodDecisionFixture(
        level="N2-INF",
        epistemology="DETERMINISTIC_LOGICAL",
        decision_path="PASO 6 → default",
        skip_rest=False,
        precheck=False,
    )

    payload = decision_payload_for_hash(decision)

    assert set(payload.keys()) == {f.name for f in fields(decision)}


def test_compute_hash_changes_if_any_decision_field_changes() -> None:
    method = {
        "return_type": "float",
        "docstring": "Computes a score.",
        "parameters": [{"name": "x", "type": "float"}],
    }

    base = MethodDecisionFixture(
        level="N2-INF",
        epistemology="DETERMINISTIC_LOGICAL",
        decision_path="PASO 5",
        skip_rest=False,
        precheck=False,
    )

    h0 = compute_classification_hash(method, base, method_name="compute")

    variants = [
        base.__class__(
            level="N3-AUD",
            epistemology=base.epistemology,
            decision_path=base.decision_path,
            skip_rest=base.skip_rest,
            precheck=base.precheck,
        ),
        base.__class__(
            level=base.level,
            epistemology="BAYESIAN_PROBABILISTIC",
            decision_path=base.decision_path,
            skip_rest=base.skip_rest,
            precheck=base.precheck,
        ),
        base.__class__(
            level=base.level,
            epistemology=base.epistemology,
            decision_path="PASO 4",
            skip_rest=base.skip_rest,
            precheck=base.precheck,
        ),
        base.__class__(
            level=base.level,
            epistemology=base.epistemology,
            decision_path=base.decision_path,
            skip_rest=True,
            precheck=base.precheck,
        ),
        base.__class__(
            level=base.level,
            epistemology=base.epistemology,
            decision_path=base.decision_path,
            skip_rest=base.skip_rest,
            precheck=True,
        ),
    ]

    for v in variants:
        assert compute_classification_hash(method, v, method_name="compute") != h0


def test_method_signature_normalizes_none_to_empty_string() -> None:
    decision = MethodDecisionFixture(
        level="N1-EMP",
        epistemology="POSITIVIST_EMPIRICAL",
        decision_path="PASO 4",
        skip_rest=False,
        precheck=False,
    )

    method_none = {"return_type": None, "docstring": None, "parameters": [{"name": None, "type": None}]}
    method_empty = {"return_type": "", "docstring": "", "parameters": [{"name": "", "type": ""}]}

    h1 = compute_classification_hash(method_none, decision, method_name="extract")
    h2 = compute_classification_hash(method_empty, decision, method_name="extract")

    assert h1 == h2


def test_non_dataclass_decision_fails_loudly() -> None:
    with pytest.raises(TypeError):
        compute_classification_hash({"return_type": "str"}, object(), method_name="x")
