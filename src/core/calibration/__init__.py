"""
CANONICAL CALIBRATION SYSTEM ACCESS
ALL calibration access MUST go through these functions.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.orchestration.calibration_orchestrator import CalibrationOrchestrator

_calibration_orchestrator: CalibrationOrchestrator | None = None


def get_calibration_orchestrator() -> CalibrationOrchestrator:
    """
    OBLIGATORIO: Única forma de obtener el orchestrator.
    Singleton global - garantiza que TODOS usan el mismo.
    """
    global _calibration_orchestrator
    if _calibration_orchestrator is None:
        from pathlib import Path

        from src.orchestration.calibration_orchestrator import (
            CalibrationOrchestrator,
        )

        config_dir = (
            Path(__file__).parent.parent.parent
            / "cross_cutting_infrastrucuture"
            / "capaz_calibration_parmetrization"
            / "calibration"
        )
        _calibration_orchestrator = CalibrationOrchestrator.from_config_dir(
            config_dir
        )
    return _calibration_orchestrator


from .layer_requirements import (
    LAYER_REQUIREMENTS,
    get_required_layers,
)
from .intrinsic_loader import (
    IntrinsicCalibrationLoader,
    get_intrinsic_loader,
)
from .decorators import (
    calibrated_method,
    calibration_required,
)

__all__ = [
    "get_calibration_orchestrator",
    "LAYER_REQUIREMENTS",
    "get_required_layers",
    "IntrinsicCalibrationLoader",
    "get_intrinsic_loader",
    "calibrated_method",
    "calibration_required",
]
