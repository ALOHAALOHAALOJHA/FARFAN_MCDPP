"""
Parametrization infrastructure for FARFAN pipeline.

This module contains configuration and parametrization systems
for PDM structural recognition according to Ley 152/94.
"""

from .pdm_structural_profile import (
    HierarchyLevel,
    CanonicalSection,
    ContextualMarker,
    TableSchema,
    SemanticRule,
    StructuralTransition,
    PDMStructuralProfile,
    get_default_profile,
)

__all__ = [
    "HierarchyLevel",
    "CanonicalSection",
    "ContextualMarker",
    "TableSchema",
    "SemanticRule",
    "StructuralTransition",
    "PDMStructuralProfile",
    "get_default_profile",
]
