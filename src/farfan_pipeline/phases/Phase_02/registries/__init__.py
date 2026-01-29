"""
Phase 2 Registries - Signal and Question Routing Components.

This package provides registries for robust signal routing and question mapping
in the F.A.R.F.A.N MCDPP pipeline.
"""

from .questionnaire_signal_registry import (
    QuestionnaireSignalRegistry,
    QuestionSignalMapping,
    SignalTypeMapping,
)

__all__ = [
    "QuestionnaireSignalRegistry",
    "QuestionSignalMapping",
    "SignalTypeMapping",
]
