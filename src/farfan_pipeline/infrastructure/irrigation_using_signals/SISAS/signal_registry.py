"""
Signal Registry Compatibility Module
=====================================

Re-exports signal registry from vehicles submodule.
"""

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_registry import (
    SignalRegistryVehicle,
    QuestionnaireSignalRegistry,
)

__all__ = [
    "SignalRegistryVehicle",
    "QuestionnaireSignalRegistry",
]
