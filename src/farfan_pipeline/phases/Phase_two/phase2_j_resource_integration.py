"""
Module: src.farfan_pipeline.phases.Phase_two.phase2_j_resource_integration
Phase: 2 (Evidence Nexus & Executor Orchestration)
Purpose: Resource resolution via QuestionnaireResourceProvider

Replaces monolith access with scoped providers for clean separation.
Provides resource management integration for contract execution.

Success Criteria:
- Replace monolith access patterns
- Scoped resource providers per contract
- Clean dependency injection
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class QuestionnaireResourceProvider:
    """Scoped resource provider for contract execution."""
    
    def __init__(self, questionnaire_data: dict[str, Any]) -> None:
        self._data = questionnaire_data
    
    def get_question_data(self, question_id: str) -> dict[str, Any]:
        """Get data for specific question."""
        return self._data.get(question_id, {})
    
    def get_dimension_data(self, dimension_id: str) -> dict[str, Any]:
        """Get data for specific dimension."""
        return {
            k: v
            for k, v in self._data.items()
            if v.get("dimension_id") == dimension_id
        }


def create_resource_provider(
    questionnaire_data: dict[str, Any]
) -> QuestionnaireResourceProvider:
    """Create scoped resource provider."""
    return QuestionnaireResourceProvider(questionnaire_data)
