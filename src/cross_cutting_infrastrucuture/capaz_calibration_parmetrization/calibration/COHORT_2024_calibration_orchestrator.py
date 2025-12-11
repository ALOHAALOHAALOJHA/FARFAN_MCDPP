"""
DEPRECATED: Use src.core.calibration.get_calibration_orchestrator()
This file exists only for backwards compatibility.
"""
import warnings

warnings.warn(
    "Import from core.calibration instead",
    DeprecationWarning,
    stacklevel=2,
)

from core.calibration import get_calibration_orchestrator

CalibrationOrchestrator = get_calibration_orchestrator
