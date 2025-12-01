from __future__ import annotations

from dataclasses import dataclass, field, FrozenInstanceError
from typing import Any, Mapping, Tuple
from types import MappingProxyType
from collections.abc import Mapping as ABCMapping, Sequence as ABCSequence

def _freeze(obj: Any) -> Any:
    # Recursively make structures immutable
    if isinstance(obj, ABCMapping):
        # copy first to avoid aliasing; then wrap in read-only proxy
        return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, (list, tuple)):
        return tuple(_freeze(x) for x in obj)
    if isinstance(obj, set):
        return frozenset(_freeze(x) for x in obj)
    # dataclasses inside are assumed already frozen; otherwise treat as opaque
    return obj

@dataclass(frozen=True, slots=True)
class QuestionContext:
    """Carries question requirements through entire pipeline (deep-immutable)."""
    question_mapping: Any                  # keep your existing type (e.g., QuestionMapping)
    dnp_standards: Mapping[str, Any]
    required_evidence_types: Tuple[str, ...]
    search_queries: Tuple[str, ...]
    validation_criteria: Mapping[str, Any]
    traceability_id: str

    def __post_init__(self):
        # Lock inner structures deterministically
        object.__setattr__(self, "question_mapping", _freeze(self.question_mapping))
        object.__setattr__(self, "dnp_standards", _freeze(self.dnp_standards))
        object.__setattr__(self, "required_evidence_types", tuple(self.required_evidence_types))
        object.__setattr__(self, "search_queries", tuple(self.search_queries))
        object.__setattr__(self, "validation_criteria", _freeze(self.validation_criteria))

    def __setattr__(self, name, value):
        raise FrozenInstanceError(f"Cannot assign to frozen QuestionContext attribute: {name}")
