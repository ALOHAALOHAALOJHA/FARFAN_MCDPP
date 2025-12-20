"""Phase 2 boundary types/validators.

The verified runner expects a validator entrypoint. This is intentionally minimal
until Phase 2 contracts are formalized in one location.
"""

from __future__ import annotations

from typing import Any


def validate_phase2_result(_result: Any) -> bool:
    """Placeholder validator for Phase 2 results.

    Returns True for now (Phase 2 calibration/parametrization removed).
    """

    return True
