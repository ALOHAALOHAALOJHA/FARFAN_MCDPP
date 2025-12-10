"""
F.A.R.F.A.N Pipeline Paths Configuration
========================================

Canonical paths for the F.A.R.F.A.N pipeline.
All path references should use this module to ensure consistency.

This module provides:
- PROJECT_ROOT: Root directory of the repository
- QUESTIONNAIRE_FILE: Canonical questionnaire monolith
- DATA_DIR: Data directory for plans and inputs
- ARTIFACTS_DIR: Output artifacts directory
"""

from pathlib import Path
from typing import Final

# Detect project root by walking up from this file
def _detect_project_root() -> Path:
    """
    Detect project root by looking for pyproject.toml.
    
    Returns:
        Absolute path to project root
    """
    current = Path(__file__).resolve().parent
    
    # Walk up to find pyproject.toml or src directory
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
        if (parent / "src" / "farfan_pipeline").exists():
            return parent
    
    # Fallback: assume we're in src/farfan_pipeline/config
    return current.parent.parent.parent


# Global constants
PROJECT_ROOT: Final[Path] = _detect_project_root()
SRC_DIR: Final[Path] = PROJECT_ROOT / "src"
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
ARTIFACTS_DIR: Final[Path] = PROJECT_ROOT / "artifacts"

# Canonical questionnaire path (F0 requirement)
QUESTIONNAIRE_FILE: Final[Path] = PROJECT_ROOT / "canonic_questionnaire_central" / "questionnaire_monolith.json"

# Plan directory
PLANS_DIR: Final[Path] = DATA_DIR / "plans"


__all__ = [
    "PROJECT_ROOT",
    "SRC_DIR",
    "DATA_DIR",
    "ARTIFACTS_DIR",
    "QUESTIONNAIRE_FILE",
    "PLANS_DIR",
]
