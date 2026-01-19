"""
DEPRECATED - Phase 2 Factory

This file has been DEPRECATED and is replaced by the UNIFIED FACTORY.

ALL imports from this file should now use:
    from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig

The unified factory consolidates all factory logic including:
- Questionnaire loading via CQCLoader (modular CQC)
- Signal registry creation from canonical notation
- Component instantiation (detectors, calculators, analyzers)
- File I/O utilities
- Contract loading and execution with method injection
- SISAS central initialization

Migration Guide:
---------------

OLD (deprecated):
    from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
        load_questionnaire,
        create_signal_registry,
        create_contradiction_detector,
        # ... other factory methods
    )

NEW (use unified factory):
    from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig

    factory = UnifiedFactory(config=FactoryConfig(project_root=Path(".")))
    questionnaire = factory.load_questionnaire()
    signal_registry = factory.create_signal_registry()
    detector = factory.create_contradiction_detector()

This file is kept for backward compatibility during migration period.
It will be removed in a future version.

Version: 1.0.0 (Unified)
Date: 2026-01-19
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict

# =============================================================================
# DEPRECATION NOTICE
# =============================================================================


class Phase2FactoryDeprecationWarning(DeprecationWarning):
    """Warning for using deprecated Phase 2 factory."""


def _emit_deprecation_warning(item_name: str = "phase2_10_00_factory") -> None:
    """Emit deprecation warning for legacy imports."""
    warnings.warn(
        f"{item_name} is DEPRECATED. "
        f"Use 'from farfan_pipeline.orchestration.factory import UnifiedFactory' instead. "
        f"This legacy import will be removed in a future version.",
        Phase2FactoryDeprecationWarning,
        stacklevel=3,
    )


# =============================================================================
# LEGACY COMPATIBILITY STUBS
# =============================================================================


def load_questionnaire(path: str | Path | None = None) -> Any:
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.load_questionnaire() instead.
    """
    _emit_deprecation_warning("load_questionnaire")
    from farfan_pipeline.orchestration.factory import get_factory

    factory = get_factory()
    return factory.load_questionnaire()


def create_signal_registry() -> Dict[str, Any]:
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.create_signal_registry() instead.
    """
    _emit_deprecation_warning("create_signal_registry")
    from farfan_pipeline.orchestration.factory import get_factory

    factory = get_factory()
    return factory.create_signal_registry()


def create_contradiction_detector():
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.create_contradiction_detector() instead.
    """
    _emit_deprecation_warning("create_contradiction_detector")
    from farfan_pipeline.orchestration.factory import get_factory

    factory = get_factory()
    return factory.create_contradiction_detector()


def create_temporal_logic_verifier():
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.create_temporal_logic_verifier() instead.
    """
    _emit_deprecation_warning("create_temporal_logic_verifier")
    from farfan_pipeline.orchestration.factory import get_factory

    factory = get_factory()
    return factory.create_temporal_logic_verifier()


def create_bayesian_confidence_calculator():
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.create_bayesian_confidence_calculator() instead.
    """
    _emit_deprecation_warning("create_bayesian_confidence_calculator")
    from farfan_pipeline.orchestration.factory import get_factory

    factory = get_factory()
    return factory.create_bayesian_confidence_calculator()


def create_municipal_analyzer():
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.create_municipal_analyzer() instead.
    """
    _emit_deprecation_warning("create_municipal_analyzer")
    from farfan_pipeline.orchestration.factory import get_factory

    factory = get_factory()
    return factory.create_municipal_analyzer()


def create_analysis_components() -> Dict[str, Any]:
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.create_analysis_components() instead.
    """
    _emit_deprecation_warning("create_analysis_components")
    from farfan_pipeline.orchestration.factory import get_factory

    factory = get_factory()
    return factory.create_analysis_components()


def save_json(path: Path, data: Dict[str, Any]) -> None:
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.save_json() instead.
    """
    _emit_deprecation_warning("save_json")
    from farfan_pipeline.orchestration.factory import UnifiedFactory

    UnifiedFactory.save_json(path, data)


def write_text_file(path: Path, content: str) -> None:
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.write_text_file() instead.
    """
    _emit_deprecation_warning("write_text_file")
    from farfan_pipeline.orchestration.factory import UnifiedFactory

    UnifiedFactory.write_text_file(path, content)


def load_json(path: Path) -> Dict[str, Any]:
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.load_json() instead.
    """
    _emit_deprecation_warning("load_json")
    from farfan_pipeline.orchestration.factory import UnifiedFactory

    return UnifiedFactory.load_json(path)


def read_text_file(path: Path) -> str:
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.read_text_file() instead.
    """
    _emit_deprecation_warning("read_text_file")
    from farfan_pipeline.orchestration.factory import UnifiedFactory

    return UnifiedFactory.read_text_file(path)


def get_questionnaire_provider() -> Any:
    """
    LEGACY STUB - Redirects to UnifiedFactory.

    DEPRECATED: Use UnifiedFactory.get_questionnaire_provider() instead.
    """
    _emit_deprecation_warning("get_questionnaire_provider")
    from farfan_pipeline.orchestration.factory import get_factory

    factory = get_factory()
    return factory.get_questionnaire_provider()


# =============================================================================
# EXPORTS (for backward compatibility)
# =============================================================================

__all__ = [
    "load_questionnaire",
    "create_signal_registry",
    "create_contradiction_detector",
    "create_temporal_logic_verifier",
    "create_bayesian_confidence_calculator",
    "create_municipal_analyzer",
    "create_analysis_components",
    "save_json",
    "write_text_file",
    "load_json",
    "read_text_file",
    "get_questionnaire_provider",
]
