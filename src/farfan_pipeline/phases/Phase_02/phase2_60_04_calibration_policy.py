"""
Module: phase2_60_04_calibration_policy
PHASE_LABEL: Phase 2
Sequence: D
Description: Calibration policies v4.0 - Epistemic System Facade

Version: 4.0.0-epistemological
Last Modified: 2026-01-15
Author: F.A.R.F.A.N Policy Pipeline

CONSTITUCIÓN DEL SISTEMA:
    Este módulo es la fachada para el SISTEMA ÚNICO de calibración epistémica.
    Solo se usa Phase1PDMCalibrator para Fase 1 (ingestión).
    Para Fase 2+, SOLO se usa el sistema epistémico N0-N4.

INVARIANTES CONSTITUCIONALES (CI):
    CI-03: INMUTABILIDAD EPISTÉMICA - Level nunca cambia post-init
    CI-04: ASIMETRÍA POPPERIANA - N3 puede vetar N1/N2, nunca al revés
    CI-05: SEPARACIÓN CALIBRACIÓN-NIVEL - PDM ajusta parámetros, no nivel
"""
from __future__ import annotations

__version__ = "4.0.0-epistemological"

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from farfan_pipeline.calibration import (
    ValidationError,
    CalibrationBoundsError,
    ClosedInterval,
    EpistemicLevel,
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    N3AuditCalibration,
    N4MetaCalibration,
    N0InfrastructureCalibration,
    EpistemicCalibrationRegistry,
    create_registry,
    create_calibration,
    get_default_calibration_for_level,
    get_type_defaults,
)

logger = logging.getLogger(__name__)
_SCHEMA_VERSION: Final[str] = "4.0.0-epistemological"


@dataclass
class CalibrationParameters:
    """
    Parámetros de calibración para un scope específico.

    CONSTITUCIÓN: Wrapper MUTABLE para clases INMUTABLES del sistema epistémico.
    Los niveles N0-N4 son INMUTABLES [CI-03].
    """

    confidence_threshold: float = 0.7
    method_weights: dict[str, float] = field(default_factory=dict)
    bayesian_priors: dict[str, Any] = field(default_factory=dict)
    random_seed: int = 42
    enable_belief_propagation: bool = True
    dempster_shafer_enabled: bool = True
    _epistemic_level: str = field(default="N1-EMP", repr=False)
    _infrastructure_calibration: Any = field(default=None, repr=False)

    def validate(self) -> None:
        """Valida parámetros de calibración."""
        if not 0 <= self.confidence_threshold <= 1:
            raise ValueError(f"confidence_threshold must be in [0, 1], got {self.confidence_threshold}")
        if self.random_seed < 0:
            raise ValueError(f"random_seed must be non-negative, got {self.random_seed}")

    @property
    def epistemic_level(self) -> str:
        """Nivel epistémico INMUTABLE [CI-03]."""
        return self._epistemic_level

    def bind_epistemic_calibration(self, calibration: Any) -> None:
        """Bind an immutable epistemic calibration."""
        object.__setattr__(self, "_infrastructure_calibration", calibration)
        if hasattr(calibration, "level"):
            object.__setattr__(self, "_epistemic_level", calibration.level)


class CalibrationPolicy:
    """
    Gestiona políticas de calibración para ejecución basada en contratos JSON.

    CONSTITUCIÓN: Usa el SISTEMA ÚNICO de calibración epistémica N0-N4.
    """

    def __init__(self, registry_path: Path | None = None) -> None:
        if registry_path is None:
            registry_path = Path(__file__).resolve().parent.parent.parent / "infrastructure" / "calibration"

        self._registry = create_registry(registry_path)
        self._global_params = CalibrationParameters()
        self._dimension_params: dict[str, CalibrationParameters] = {}
        self._policy_area_params: dict[str, CalibrationParameters] = {}
        self._contract_params: dict[str, CalibrationParameters] = {}

        logger.info(f"CalibrationPolicy initialized with registry at {registry_path}")

    def resolve_method_calibration(
        self,
        method_id: str,
        contract_type: str,
        pdm_profile: Any = None,
    ) -> dict[str, Any]:
        """
        Resolve calibration for a specific method using epistemic registry.

        CONSTITUCIÓN [CI-03, CI-05]:
        - Nivel epistémico es INMUTABLE
        - PDM ajusta PARÁMETROS, nunca el nivel
        """
        return self._registry.resolve_calibration(
            method_id=method_id,
            contract_type=contract_type,
            pdm_profile=pdm_profile,
        )

    def get_method_level(self, method_id: str) -> str:
        """Get the immutable epistemic level for a method [CI-03]."""
        return self._registry.get_method_level(method_id)

    def get_parameters(
        self,
        question_id: str,
        dimension_id: str | None = None,
        policy_area_id: str | None = None,
    ) -> CalibrationParameters:
        """Get calibration parameters for a specific context."""
        if question_id in self._contract_params:
            return self._contract_params[question_id]
        if policy_area_id and policy_area_id in self._policy_area_params:
            return self._policy_area_params[policy_area_id]
        if dimension_id and dimension_id in self._dimension_params:
            return self._dimension_params[dimension_id]
        return self._global_params


def create_default_policy() -> CalibrationPolicy:
    """Factory function to create default CalibrationPolicy."""
    return CalibrationPolicy()


__all__ = [
    "CalibrationParameters",
    "CalibrationPolicy",
    "create_default_policy",
]
