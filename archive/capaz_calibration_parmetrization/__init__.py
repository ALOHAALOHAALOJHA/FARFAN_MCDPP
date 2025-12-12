"""
COHORT 2024 Calibration & Parametrization System

Centralized access to all calibration and parametrization configuration files
with strict cohort metadata tracking and auditable migration trail.

Directory Structure:
- calibration/: Intrinsic calibration, layer evaluators, method inventory, fusion weights
- parametrization/: Runtime layers, executor configs, profiler settings

Usage:
    from calibration_parametrization_system import get_calibration_config, get_parametrization_config
    
    # Load calibration configs
    intrinsic_cal = get_calibration_config("intrinsic_calibration")
    rubric = get_calibration_config("intrinsic_calibration_rubric")
    questionnaire = get_calibration_config("questionnaire_monolith")
    method_compat = get_calibration_config("method_compatibility")
    fusion_weights = get_calibration_config("fusion_weights")
    method_inventory = get_calibration_config("canonical_method_inventory")
    
    # Load parametrization configs
    runtime_layers = get_parametrization_config("runtime_layers")
    executor_config = get_parametrization_config("executor_config")
    
    # Access cohort metadata
    metadata = get_cohort_metadata()
"""

from __future__ import annotations

from typing import Any

from .calibration.COHORT_2024_calibration_orchestrator import (
    CalibrationContext,
    CalibrationEvidence,
    CalibrationOrchestrator,
    CalibrationResult,
    FusionWeights,
    LayerScores,
)
from .calibration_orchestrator import (
    CalibrationOrchestrator as LegacyCalibrationOrchestrator,
    CalibrationResult as LegacyCalibrationResult,
    MethodBelowThresholdError,
)
from .cohort_loader import CohortLoader

_loader: CohortLoader | None = None


def _get_loader() -> CohortLoader:
    """Get or create singleton loader instance."""
    global _loader
    if _loader is None:
        _loader = CohortLoader()
    return _loader


def get_calibration_config(name: str) -> dict[str, Any]:
    """
    Load calibration configuration by name.

    Available names:
    - intrinsic_calibration
    - intrinsic_calibration_rubric
    - questionnaire_monolith
    - method_compatibility
    - fusion_weights
    - canonical_method_inventory

    Returns:
        Configuration dict with _cohort_metadata embedded
    """
    return _get_loader().load_calibration(name)


def get_parametrization_config(name: str) -> dict[str, Any]:
    """
    Load parametrization configuration by name.

    Available names:
    - runtime_layers
    - executor_config

    Returns:
        Configuration dict with _cohort_metadata embedded
    """
    return _get_loader().load_parametrization(name)


def get_cohort_metadata() -> dict[str, Any]:
    """
    Get COHORT_2024 metadata.

    Returns:
        Dict with cohort_id, wave_version, migration_date
    """
    return _get_loader().get_cohort_metadata()


def list_available_configs() -> dict[str, list[str]]:
    """
    List all available configuration files.

    Returns:
        Dict with 'calibration' and 'parametrization' keys containing file lists
    """
    loader = _get_loader()
    return {
        "calibration": loader.list_calibration_files(),
        "parametrization": loader.list_parametrization_files(),
    }


__all__ = [
    "get_calibration_config",
    "get_parametrization_config",
    "get_cohort_metadata",
    "list_available_configs",
    "CohortLoader",
    "CalibrationOrchestrator",
    "CalibrationContext",
    "CalibrationEvidence",
    "CalibrationResult",
    "FusionWeights",
    "LayerScores",
    "LegacyCalibrationOrchestrator",
    "LegacyCalibrationResult",
    "MethodBelowThresholdError",
]
