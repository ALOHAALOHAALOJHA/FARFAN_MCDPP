"""
Phase-2 Calibrator
==================
Calibrates N2-INF and orchestration methods for TYPE-specific fusion.

DESIGN PATTERNS:
- Builder Pattern: Incremental construction with validation
- Template Method: Subclassable calibration steps

CRITICAL CONSTRAINTS:
- TYPE_E: MUST use MIN logic, NEVER averaging
- TYPE_B: Bayesian methods are epistemically necessary (force inclusion)
- TYPE_C: Cycle detection is mandatory at N3

Module: phase2_calibrator.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Phase-2 calibration for N2-INF methods
Lifecycle State: DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 2.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

from .calibration_core import (
    CalibrationLayer,
    CalibrationPhase,
    ClosedInterval,
    create_calibration_parameter,
)
from .method_binding_validator import (
    EpistemicViolation,
    MethodBindingSet,
    MethodBindingValidator,
    ValidationSeverity,
)
from .type_defaults import (
    PROHIBITED_OPERATIONS,
    VALID_CONTRACT_TYPES,
    UnknownContractTypeError,
    get_type_defaults,
)

logger = logging.getLogger(__name__)


# Fusion strategies by type (MUST match epistemic_minima_by_type.json)
_TYPE_FUSION_STRATEGIES: Final[dict[str, str]] = {
    "TYPE_A": "semantic_triangulation",
    "TYPE_B": "bayesian_update",
    "TYPE_C": "topological_overlay",
    "TYPE_D": "weighted_mean",
    "TYPE_E": "min_consistency",  # CRITICAL: Never average
    "SUBTIPO_F": "concat",
}

_EPISTEMIC_MINIMA_PATH: Final[str] = (
    "artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json"
)
_DEFAULT_EVIDENCE_COMMIT: Final[str] = "0" * 40


@dataclass(frozen=True)
class Phase2CalibrationResult:
    """Result of Phase-2 calibration."""

    calibration_layer: CalibrationLayer
    fusion_strategy: str
    prohibited_operations: frozenset[str]
    validation_passed: bool
    warnings: tuple[str, ...]


class Phase2Calibrator:
    """
    Calibrates Phase-2 methods for TYPE-specific requirements.

    RESPONSIBILITIES:
    1. Validate method binding against TYPE constraints
    2. Select correct fusion strategy
    3. Enforce prohibited operations
    4. Produce frozen calibration layer
    """

    def __init__(self, evidence_commit: str | None = None) -> None:
        self._validator = MethodBindingValidator()
        self._evidence_commit = evidence_commit or _DEFAULT_EVIDENCE_COMMIT
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calibrate(
        self,
        binding_set: MethodBindingSet,
        unit_of_analysis_id: str,
    ) -> Phase2CalibrationResult:
        """
        Calibrate Phase-2 methods.

        Args:
            binding_set: Methods bound to contract (already selected)
            unit_of_analysis_id: Hash identifying unit of analysis

        Returns:
            Phase2CalibrationResult with frozen calibration layer

        Raises:
            EpistemicViolation: If TYPE constraints cannot be satisfied
            UnknownContractTypeError: If contract_type_code is not recognized
        """
        contract_type = binding_set.contract_type_code

        if contract_type not in VALID_CONTRACT_TYPES:
            raise UnknownContractTypeError(contract_type, VALID_CONTRACT_TYPES)

        self._logger.info(
            f"Calibrating Phase-2 for contract={binding_set.contract_id}, "
            f"type={contract_type}, methods={binding_set.get_total_count()}"
        )

        # Step 1: Validate bindings (raises on FATAL)
        validation_results = self._validator.validate(binding_set)
        warnings = tuple(
            r.message for r in validation_results if r.severity == ValidationSeverity.WARNING
        )

        # Step 2: Get fusion strategy (MUST match TYPE)
        fusion_strategy = _TYPE_FUSION_STRATEGIES.get(contract_type)
        if fusion_strategy is None:
            raise EpistemicViolation(f"No fusion strategy for type: {contract_type}")

        # Step 3: Get prohibited operations
        prohibited = PROHIBITED_OPERATIONS.get(contract_type, frozenset())

        # Step 4: Build calibration layer
        type_defaults = get_type_defaults(contract_type)
        now = datetime.now(UTC)
        validity_days = 365

        prior_param = create_calibration_parameter(
            name="prior_strength",
            value=type_defaults.get_default_prior_strength(),
            bounds=type_defaults.prior_strength,
            unit="dimensionless",
            rationale=f"Phase-2 {contract_type} prior for Bayesian fusion",
            evidence_path=_EPISTEMIC_MINIMA_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Epistemic minima by contract type",
            validity_days=validity_days,
            calibrated_at=now,
        )

        veto_param = create_calibration_parameter(
            name="veto_threshold",
            value=type_defaults.get_default_veto_threshold(),
            bounds=type_defaults.veto_threshold,
            unit="dimensionless",
            rationale=f"Phase-2 {contract_type} N3 veto threshold",
            evidence_path=_EPISTEMIC_MINIMA_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Epistemic minima by contract type",
            validity_days=validity_days,
            calibrated_at=now,
        )

        # Placeholder params for ingestion-specific values (not used in Phase-2)
        placeholder_bounds = ClosedInterval(lower=100.0, upper=10000.0)
        chunk_param = create_calibration_parameter(
            name="chunk_size",
            value=2000.0,
            bounds=placeholder_bounds,
            unit="tokens",
            rationale="Not applicable to Phase-2 (ingestion parameter)",
            evidence_path="src/farfan_pipeline/phases/Phase_2/README.md",
            evidence_commit=self._evidence_commit,
            evidence_description="Phase-2 documentation",
            validity_days=validity_days,
            calibrated_at=now,
        )

        coverage_bounds = ClosedInterval(lower=0.5, upper=1.0)
        coverage_param = create_calibration_parameter(
            name="extraction_coverage_target",
            value=0.85,
            bounds=coverage_bounds,
            unit="fraction",
            rationale="Not applicable to Phase-2 (ingestion parameter)",
            evidence_path="src/farfan_pipeline/phases/Phase_2/README.md",
            evidence_commit=self._evidence_commit,
            evidence_description="Phase-2 documentation",
            validity_days=validity_days,
            calibrated_at=now,
        )

        layer = CalibrationLayer(
            unit_of_analysis_id=unit_of_analysis_id,
            phase=CalibrationPhase.PHASE_2_COMPUTATION,
            contract_type_code=contract_type,
            parameters=(prior_param, veto_param, chunk_param, coverage_param),
            created_at=now,
        )

        self._logger.info(
            f"Phase-2 calibration complete: fusion={fusion_strategy}, "
            f"prohibited={len(prohibited)}, warnings={len(warnings)}"
        )

        return Phase2CalibrationResult(
            calibration_layer=layer,
            fusion_strategy=fusion_strategy,
            prohibited_operations=prohibited,
            validation_passed=True,
            warnings=warnings,
        )


__all__ = [
    "Phase2CalibrationResult",
    "Phase2Calibrator",
]
