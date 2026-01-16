"""
Sistema PDM (Plan de Desarrollo Municipal) FARFAN 2025.1

Este módulo proporciona acceso al sistema de reconocimiento estructural
PDM conforme a la Ley 152/94 de Colombia.

Componentes:
    profile: PDMStructuralProfile con secciones canónicas y niveles jerárquicos
    contracts: PDMProfileContract para validación de perfiles
    integration: Integración con Phase 1 SP2 y SP4
    calibrator: Calibrador ex-post PDM

Author: FARFAN Engineering Team
Version: 1.0.0
"""

from __future__ import annotations

# Profile
try:
    from .profile.pdm_structural_profile import (
        CanonicalSection,
        ContextualMarker,
        HierarchyLevel,
        SemanticRule,
        PDMStructuralProfile,
        get_default_profile,
    )
except ImportError:
    CanonicalSection = None
    ContextualMarker = None
    HierarchyLevel = None
    SemanticRule = None
    PDMStructuralProfile = None
    get_default_profile = None

# Contracts
try:
    from .contracts.pdm_contracts import (
        PDMProfileContract,
        enforce_profile_presence,
    )
except ImportError:
    PDMProfileContract = None
    enforce_profile_presence = None

__all__ = [
    # Profile
    "CanonicalSection",
    "ContextualMarker",
    "HierarchyLevel",
    "SemanticRule",
    "PDMStructuralProfile",
    "get_default_profile",
    # Contracts
    "PDMProfileContract",
    "enforce_profile_presence",
]
