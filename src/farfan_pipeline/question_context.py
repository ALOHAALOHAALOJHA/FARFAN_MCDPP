from __future__ import annotations

from collections.abc import Mapping as ABCMapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


def _freeze(obj: Any) -> Any:  # noqa: ANN401  # type: ignore[misc]
    if isinstance(obj, ABCMapping):
        return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, list | tuple):
        return tuple(_freeze(x) for x in obj)
    if isinstance(obj, set):
        return frozenset(_freeze(x) for x in obj)
    return obj


@dataclass(frozen=True, slots=True)
class QuestionContext:
    """Carries question requirements through entire pipeline (deep-immutable)."""

    question_mapping: Any  # type: ignore[misc]
    dnp_standards: ABCMapping[str, Any]  # type: ignore[misc]
    required_evidence_types: tuple[str, ...]
    search_queries: tuple[str, ...]
    validation_criteria: ABCMapping[str, Any]  # type: ignore[misc]
    traceability_id: str

    def __post_init__(self) -> None:  # type: ignore[misc]
        object.__setattr__(self, "question_mapping", _freeze(self.question_mapping))
        object.__setattr__(self, "dnp_standards", _freeze(self.dnp_standards))
        object.__setattr__(
            self, "required_evidence_types", tuple(self.required_evidence_types)
        )
        object.__setattr__(self, "search_queries", tuple(self.search_queries))
        object.__setattr__(
            self, "validation_criteria", _freeze(self.validation_criteria)
        )
