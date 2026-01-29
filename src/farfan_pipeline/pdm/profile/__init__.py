"""
PDM Structural Profile Module

Provides PDM structural profile for Colombian municipal development plans
according to Ley 152/94.

Components:
    - HierarchyLevel: H1-H5 enum (PARTE, CAPITULO, LINEA, SUBPROGRAMA, META)
    - CanonicalSection: Canonical sections enum
    - ContextualMarker: P-D-Q markers (Problem, Decision, Quality)
    - SemanticRule: Semantic integrity rules
    - StructuralTransition: Structural transitions
    - TableSchema: PDM table schemas
    - PDMStructuralProfile: Main profile class
    - get_default_profile(): Get default PDM profile

Author: FARFAN Engineering Team
Version: 1.0.0
"""

from .pdm_structural_profile import (
    HierarchyLevel,
    CanonicalSection,
    ContextualMarker,
    SemanticRule,
    StructuralTransition,
    TableSchema,
    PDMStructuralProfile,
    get_default_profile,
)

__all__ = [
    "HierarchyLevel",
    "CanonicalSection",
    "ContextualMarker",
    "SemanticRule",
    "StructuralTransition",
    "TableSchema",
    "PDMStructuralProfile",
    "get_default_profile",
]
