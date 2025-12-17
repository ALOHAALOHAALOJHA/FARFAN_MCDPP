from __future__ import annotations

from typing import Any, Protocol


class QuestionnairePort(Protocol):
    """Minimal questionnaire contract for signal infrastructure."""

    @property
    def data(self) -> dict[str, Any]:
        ...

    @property
    def version(self) -> str:
        ...

    @property
    def sha256(self) -> str:
        ...

    @property
    def micro_questions(self) -> list[dict[str, Any]]:
        ...

    def __iter__(self) -> Any:  # pragma: no cover - structural typing only
        ...


class SignalRegistryPort(Protocol):
    """Port for accessing signal packs."""

    def get_chunking_signals(self) -> Any:
        ...

    def get_micro_answering_signals(self, question_id: str) -> Any:
        ...

    def get_validation_signals(self, level: str) -> Any:
        ...

    def get_assembly_signals(self, level: str) -> Any:
        ...

    def get_scoring_signals(self) -> Any:
        ...
