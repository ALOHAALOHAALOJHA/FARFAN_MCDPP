"""
F.A.R.F.A.N Infrastructure Layer
=================================

This layer contains all infrastructure concerns including:
- Calibration: Parameter governance and unit-of-analysis
- Contractual: Dura lex architectural contracts
- Extractors: Empirical evidence extraction
- Irrigation: Signal-based evidence irrigation

Dependencies:
    The SINGLE SOURCE OF TRUTH for all dependencies is maintained in
    infrastructure/dependencies.py. All dependency changes must go through
    that module.
"""

from farfan_pipeline.infrastructure.dependencies import (
    CANONICAL_DEPENDENCIES,
    DependencyLayer,
    DependencySpec,
    DependencyStatus,
    get_active_dependencies,
    get_dependency_hash,
    get_layer,
    get_owner,
    get_status,
)

__all__ = [
    # Dependency governance
    "CANONICAL_DEPENDENCIES",
    "DependencyLayer",
    "DependencySpec",
    "DependencyStatus",
    "get_active_dependencies",
    "get_dependency_hash",
    "get_layer",
    "get_owner",
    "get_status",
]
