"""
Test Helper - Questionnaire Compatibility Module

Provides compatibility functions for tests that previously used questionnaire_monolith.json.
This module bridges the gap between legacy monolith references and the modular CQC.

Migration Guide:
---------------

OLD (deprecated):
    monolith_path = Path("canonic_questionnaire_central/questionnaire_monolith.json")
    with open(monolith_path) as f:
        questionnaire = json.load(f)

NEW (use modular):
    from tests.test_helpers.questionnaire_compat import (
        get_questionnaire_data,
        get_questionnaire_resolver,
        get_cqc_loader,
    )
    questionnaire = get_questionnaire_data()  # Returns dict for backward compatibility
    # OR use the resolver for deep access
    resolver = get_questionnaire_resolver()

Version: 1.0.0
Date: 2026-01-19
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# QUESTIONNAIRE DATA COMPATIBILITY
# =============================================================================


def get_questionnaire_data(
    use_resolver: bool = True,
    force_legacy_monolith: bool = False,
) -> Dict[str, Any]:
    """
    Get questionnaire data in legacy monolith format.

    This function returns a dict that mimics the old questionnaire_monolith.json
    structure, assembled from the modular CQC components.

    Args:
        use_resolver: If True, use CanonicalQuestionnaireResolver to assemble data.
                     If False, return minimal stub.
        force_legacy_monolith: If True and questionnaire_monolith.json exists,
                              load it directly. Otherwise use modular assembly.

    Returns:
        Dict with questionnaire data in monolith-compatible format:
        {
            "version": "1.0.0",
            "dimensions": {...},
            "policy_areas": {...},
            "clusters": {...},
            "questions": [...],
            "metadata": {...},
        }
    """
    # Check if legacy monolith exists and force_legacy is True
    monolith_path = (
        Path(__file__).resolve().parent.parent.parent
        / "canonic_questionnaire_central"
        / "questionnaire_monolith.json"
    )

    if force_legacy_monolith and monolith_path.exists():
        with open(monolith_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Use modular assembly via resolver
    if use_resolver:
        try:
            from canonic_questionnaire_central.resolver import (
                CanonicalQuestionnaireResolver,
            )

            resolver = CanonicalQuestionnaireResolver()

            # Assemble monolith-compatible structure from modular components
            return {
                "version": "2.0.0-modular",
                "source": "modular_cqc",
                "dimensions": resolver.get_dimensions(),
                "policy_areas": resolver.get_policy_areas(),
                "clusters": resolver.get_clusters(),
                "questions": list(resolver.get_all_questions()),
                "metadata": {
                    "total_questions": len(list(resolver.get_all_questions())),
                    "total_dimensions": len(resolver.get_dimensions()),
                    "total_policy_areas": len(resolver.get_policy_areas()),
                    "total_clusters": len(resolver.get_clusters()),
                },
            }
        except ImportError:
            # Resolver not available, return minimal stub
            pass

    # Return minimal stub for tests that just need some structure
    return {
        "version": "2.0.0-stub",
        "source": "stub",
        "dimensions": {},
        "policy_areas": {},
        "clusters": {},
        "questions": [],
        "metadata": {"note": "Stub data - resolver not available"},
    }


def get_questionnaire_resolver():
    """
    Get the CanonicalQuestionnaireResolver for deep access.

    Returns:
        CanonicalQuestionnaireResolver instance or None if not available
    """
    try:
        from canonic_questionnaire_central.resolver import (
            CanonicalQuestionnaireResolver,
        )

        return CanonicalQuestionnaireResolver()
    except ImportError:
        return None


def get_cqc_loader():
    """
    Get the CQCLoader for optimized question access.

    Returns:
        CQCLoader instance or None if not available
    """
    try:
        from canonic_questionnaire_central import CQCConfig, CQCLoader

        return CQCLoader(config=CQCConfig())
    except ImportError:
        return None


def get_questionnaire_sha256() -> Optional[str]:
    """
    Get SHA256 hash of questionnaire data for integrity checks.

    Returns:
        SHA256 hash string or None if not available
    """
    try:
        from canonic_questionnaire_central import CQCLoader

        loader = CQCLoader()
        return getattr(loader, "sha256", None)
    except (ImportError, AttributeError):
        # Fallback: compute hash from assembled data
        import hashlib

        data = get_questionnaire_data()
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


# =============================================================================
# SIGNAL REGISTRY COMPATIBILITY
# =============================================================================


def get_signal_registry() -> Dict[str, Any]:
    """
    Get signal registry data from canonical notation.

    Returns:
        Dict with signal registry containing dimensions, policy_areas, clusters
    """
    try:
        from farfan_pipeline.orchestration.factory import get_factory

        factory = get_factory()
        return factory.create_signal_registry()
    except ImportError:
        # Fallback to direct loading
        canonical_path = (
            Path(__file__).resolve().parent.parent.parent
            / "canonic_questionnaire_central"
            / "config"
            / "canonical_notation.json"
        )

        if canonical_path.exists():
            with open(canonical_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "dimensions": data.get("dimensions", {}),
                    "policy_areas": data.get("policy_areas", {}),
                    "clusters": data.get("clusters", {}),
                }

        return {"dimensions": {}, "policy_areas": {}, "clusters": {}}


# =============================================================================
# QUESTION ACCESS HELPERS
# =============================================================================


def get_question_by_id(question_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific question by ID.

    Args:
        question_id: Question ID (e.g., "Q001", "Q001_PA01_DIM01")

    Returns:
        Question data dict or None if not found
    """
    loader = get_cqc_loader()
    if loader:
        question = loader.get_question(question_id)
        if question and hasattr(question, "to_dict"):
            return question.to_dict()
        elif question:
            return {"question_id": question_id, "data": question}
    return None


def get_questions_by_policy_area(policy_area_id: str) -> List[Dict[str, Any]]:
    """
    Get all questions for a specific policy area.

    Args:
        policy_area_id: Policy area ID (e.g., "PA01")

    Returns:
        List of question data dicts
    """
    resolver = get_questionnaire_resolver()
    if resolver:
        questions = []
        for q in resolver.get_questions_by_policy_area(policy_area_id):
            if hasattr(q, "to_dict"):
                questions.append(q.to_dict())
            else:
                questions.append({"question_id": str(q), "data": q})
        return questions
    return []


def get_questions_by_dimension(dimension_id: str) -> List[Dict[str, Any]]:
    """
    Get all questions for a specific dimension.

    Args:
        dimension_id: Dimension ID (e.g., "DIM01")

    Returns:
        List of question data dicts
    """
    resolver = get_questionnaire_resolver()
    if resolver:
        questions = []
        for q in resolver.get_questions_by_dimension(dimension_id):
            if hasattr(q, "to_dict"):
                questions.append(q.to_dict())
            else:
                questions.append({"question_id": str(q), "data": q})
        return questions
    return []


# =============================================================================
# LEGACY PATH HELPERS
# =============================================================================


def get_monolith_path() -> Path:
    """
    Get the path to the legacy questionnaire_monolith.json.

    Note: This file may not exist in the modular version.
    Use get_questionnaire_data() instead for actual data access.

    Returns:
        Path to questionnaire_monolith.json location
    """
    return (
        Path(__file__).resolve().parent.parent.parent
        / "canonic_questionnaire_central"
        / "questionnaire_monolith.json"
    )


def monolith_exists() -> bool:
    """
    Check if the legacy questionnaire_monolith.json file exists.

    Returns:
        True if monolith file exists, False otherwise
    """
    return get_monolith_path().exists()


# =============================================================================
# PYTEST FIXTURES
# =============================================================================


def pytest_questionnaire_data():
    """
    Pytest fixture for questionnaire data.

    Usage in pytest tests:
        from tests.test_helpers.questionnaire_compat import pytest_questionnaire_data

        def test_something(pytest_questionnaire_data):
            questionnaire = pytest_questionnaire_data
            assert questionnaire["version"] == "2.0.0-modular"
    """
    return get_questionnaire_data()


def pytest_questionnaire_resolver():
    """
    Pytest fixture for questionnaire resolver.

    Usage in pytest tests:
        from tests.test_helpers.questionnaire_compat import pytest_questionnaire_resolver

        def test_something(pytest_questionnaire_resolver):
            resolver = pytest_questionnaire_resolver
            questions = list(resolver.get_all_questions())
    """
    return get_questionnaire_resolver()


def pytest_cqc_loader():
    """
    Pytest fixture for CQC loader.

    Usage in pytest tests:
        from tests.test_helpers.questionnaire_compat import pytest_cqc_loader

        def test_something(pytest_cqc_loader):
            loader = pytest_cqc_loader
            question = loader.get_question("Q001")
    """
    return get_cqc_loader()


def pytest_signal_registry():
    """
    Pytest fixture for signal registry.

    Usage in pytest tests:
        from tests.test_helpers.questionnaire_compat import pytest_signal_registry

        def test_something(pytest_signal_registry):
            registry = pytest_signal_registry
            dimensions = registry["dimensions"]
    """
    return get_signal_registry()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data access
    "get_questionnaire_data",
    "get_questionnaire_resolver",
    "get_cqc_loader",
    "get_questionnaire_sha256",
    "get_signal_registry",
    # Question access
    "get_question_by_id",
    "get_questions_by_policy_area",
    "get_questions_by_dimension",
    # Legacy helpers
    "get_monolith_path",
    "monolith_exists",
    # Pytest fixtures
    "pytest_questionnaire_data",
    "pytest_questionnaire_resolver",
    "pytest_cqc_loader",
    "pytest_signal_registry",
]
