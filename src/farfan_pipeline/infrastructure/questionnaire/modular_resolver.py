"""Deterministic loader for the modularized questionnaire.

This module provides a high-integrity resolver that:
- Anchors on modular_manifest.json and questionnaire_index.json
- Resolves exact file paths for policy areas, dimensions, and clusters
- Aggregates modular slices into a monolith-equivalent payload when needed
- Enforces count and ID parity against the manifest/index

Principles:
- No silent fallbacks; all inconsistencies raise explicit errors
- Deterministic ordering: policy areas follow manifest order; IDs follow index order
- No direct writes; read-only boundary for questionnaire assets
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ModularQuestionnaireError(Exception):
    """Base error for modular questionnaire resolution."""


class ManifestValidationError(ModularQuestionnaireError):
    """Raised when the manifest structure is invalid."""


class IndexValidationError(ModularQuestionnaireError):
    """Raised when the questionnaire index is invalid or inconsistent."""


class CountMismatchError(ModularQuestionnaireError):
    """Raised when item counts do not match expectations."""


class IdMismatchError(ModularQuestionnaireError):
    """Raised when question IDs diverge from the expected index order."""


@dataclass(frozen=True)
class QuestionnaireSlice:
    """In-memory representation of a resolved slice."""

    slice_id: str
    path: Path
    questions: list[dict[str, Any]]


@dataclass(frozen=True)
class AggregatePayload:
    """Monolith-equivalent payload assembled from modular sources."""

    data: dict[str, Any]
    sha256: str
    version: str
    load_timestamp: str
    source_paths: list[str]


class QuestionnaireModularResolver:
    """Resolver for modular questionnaire assets with strong validation."""

    def __init__(
        self,
        root: Path | None = None,
        manifest_path: Path | None = None,
        index_path: Path | None = None,
    ) -> None:
        self.root = (
            root or Path(__file__).resolve().parents[3] / "canonic_questionnaire_central"
        ).resolve()
        self.manifest_path = (manifest_path or self.root / "modular_manifest.json").resolve()
        self.index_path = (index_path or self.root / "questionnaire_index.json").resolve()

        self._manifest = self._load_json(self.manifest_path)
        self._index = self._load_json(self.index_path)

        self._validate_manifest_shape()
        self._validate_index_shape()
        self._validate_manifest_vs_index_counts()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def load_policy_area(self, pa_id: str, *, validate_ids: bool = True) -> QuestionnaireSlice:
        record = self._lookup(self._manifest["structure"]["policy_areas"]["items"], pa_id)
        path = (self.root / "policy_areas" / record["folder"] / "questions.json").resolve()
        questions = self._load_questions(
            path,
            expected_count=record["questions"],
            expected_ids=(
                self._index["indices"]["by_policy_area"][pa_id]["question_ids"]
                if validate_ids
                else None
            ),
        )
        return QuestionnaireSlice(slice_id=pa_id, path=path, questions=questions)

    def load_dimension(self, dim_id: str, *, validate_ids: bool = True) -> QuestionnaireSlice:
        record = self._lookup(self._manifest["structure"]["dimensions"]["items"], dim_id)
        path = (self.root / "dimensions" / record["folder"] / "questions.json").resolve()
        questions = self._load_questions(
            path,
            expected_count=record["questions"],
            expected_ids=(
                self._index["indices"]["by_dimension"][dim_id]["question_ids"]
                if validate_ids
                else None
            ),
        )
        return QuestionnaireSlice(slice_id=dim_id, path=path, questions=questions)

    def load_cluster(self, cluster_id: str) -> QuestionnaireSlice:
        record = self._lookup(self._manifest["structure"]["clusters"]["items"], cluster_id)
        path = (self.root / "clusters" / record["folder"] / "questions.json").resolve()
        questions = self._load_questions(
            path, expected_count=record["questions"], expected_ids=None
        )
        return QuestionnaireSlice(slice_id=cluster_id, path=path, questions=questions)

    def aggregate_policy_area_questions(self) -> QuestionnaireSlice:
        questions: list[dict[str, Any]] = []
        source_paths: list[Path] = []

        for record in self._manifest["structure"]["policy_areas"]["items"]:
            slice_obj = self.load_policy_area(record["id"], validate_ids=True)
            questions.extend(slice_obj.questions)
            source_paths.append(slice_obj.path)

        expected_total = self._manifest["totals"]["total_questions"]
        if len(questions) != expected_total:
            raise CountMismatchError(
                f"Aggregated questions={len(questions)} differ from manifest total={expected_total}"
            )

        return QuestionnaireSlice(slice_id="ALL", path=self.manifest_path, questions=questions)

    def build_monolith_payload(self) -> AggregatePayload:
        canonical_notation = self._load_json(self.root / "canonical_notation.json")
        micro_questions = self.aggregate_policy_area_questions().questions
        meso_questions = self._load_json(self.root / "meso_questions.json")
        macro_question = self._load_json(self.root / "macro_question.json")

        data = {
            "version": self._index.get("version")
            or self._manifest.get("_manifest_version", "unknown"),
            "canonical_notation": canonical_notation,
            "blocks": {
                "micro_questions": micro_questions,
                "meso_questions": meso_questions,
                "macro_question": macro_question,
            },
            "provenance": {
                "assembled_from": "modular",
                "manifest_path": str(self.manifest_path),
                "index_path": str(self.index_path),
                "assembly_timestamp": datetime.now(UTC).isoformat(),
            },
        }

        sha256 = hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
        return AggregatePayload(
            data=data,
            sha256=sha256,
            version=data["version"],
            load_timestamp=data["provenance"]["assembly_timestamp"],
            source_paths=[
                str(self.manifest_path),
                str(self.index_path),
                str(self.root / "canonical_notation.json"),
                str(self.root / "meso_questions.json"),
                str(self.root / "macro_question.json"),
            ],
        )

    # ---------------------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------------------
    def _validate_manifest_shape(self) -> None:
        structure = self._manifest.get("structure", {})
        if not structure:
            raise ManifestValidationError("Manifest missing 'structure'")

        for key in ("policy_areas", "dimensions", "clusters"):
            if key not in structure:
                raise ManifestValidationError(f"Manifest missing structure.{key}")
            items = structure[key].get("items", [])
            expected_count = structure[key].get("count")
            if expected_count is None or expected_count != len(items):
                raise ManifestValidationError(
                    f"Manifest {key} count mismatch: expected {expected_count}, found {len(items)}"
                )

    def _validate_index_shape(self) -> None:
        indices = self._index.get("indices")
        if not indices:
            raise IndexValidationError("Index missing 'indices'")
        for key in ("by_policy_area", "by_dimension"):
            if key not in indices:
                raise IndexValidationError(f"Index missing indices.{key}")

    def _validate_manifest_vs_index_counts(self) -> None:
        pa_manifest = self._manifest["structure"]["policy_areas"]["items"]
        dim_manifest = self._manifest["structure"]["dimensions"]["items"]

        pa_index = self._index["indices"]["by_policy_area"]
        dim_index = self._index["indices"]["by_dimension"]

        if len(pa_manifest) != len(pa_index):
            raise IndexValidationError("Policy area count mismatch between manifest and index")
        if len(dim_manifest) != len(dim_index):
            raise IndexValidationError("Dimension count mismatch between manifest and index")

    # ---------------------------------------------------------------------
    # Internals
    # ---------------------------------------------------------------------
    @staticmethod
    def _lookup(items: Iterable[dict[str, Any]], item_id: str) -> dict[str, Any]:
        for item in items:
            if item.get("id") == item_id:
                return item
        raise ManifestValidationError(f"Item id={item_id} not found in manifest")

    @staticmethod
    def _load_json(path: Path) -> Any:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _extract_question_ids(questions: Iterable[dict[str, Any]]) -> list[str]:
        ids: list[str] = []
        for q in questions:
            qid = q.get("question_id")
            if not isinstance(qid, str):
                raise IdMismatchError("Missing or invalid question_id in question object")
            ids.append(qid)
        return ids

    def _load_questions(
        self,
        path: Path,
        *,
        expected_count: int,
        expected_ids: Sequence[str] | None,
    ) -> list[dict[str, Any]]:
        payload = self._load_json(path)
        questions = payload.get("questions")
        if not isinstance(questions, list):
            raise ModularQuestionnaireError(f"questions must be a list in {path}")

        if len(questions) != expected_count:
            raise CountMismatchError(
                f"Count mismatch for {path.name}: expected {expected_count}, found {len(questions)}"
            )

        if expected_ids is not None:
            ids = self._extract_question_ids(questions)
            if ids != list(expected_ids):
                raise IdMismatchError(
                    f"ID order mismatch in {path.name}: expected first={expected_ids[0]}, got first={ids[0]}"
                )

        return questions


__all__ = [
    "AggregatePayload",
    "CountMismatchError",
    "IdMismatchError",
    "IndexValidationError",
    "ManifestValidationError",
    "ModularQuestionnaireError",
    "QuestionnaireModularResolver",
    "QuestionnaireSlice",
]
