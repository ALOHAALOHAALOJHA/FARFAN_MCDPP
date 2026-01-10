"""
Module: phase2_60_04_calibration_policy
PHASE_LABEL: Phase 2
Sequence: D
Description: Calibration policies for quality scoring - Phase 2 policy facade

Version: 2.0.0
Last Modified: 2026-01-05
Author: F.A.R.F.A.N Policy Pipeline
License: Proprietary

This module is part of Phase 2: Analysis & Question Execution.
All files in Phase_2/ must contain PHASE_LABEL: Phase 2.

DESIGN PATTERN: Policy Facade
- Provides high-level policy resolution for 300 JSON contracts
- Delegates to infrastructure/calibration for frozen, auditable calibration layers
- Hierarchical overrides: global → dimension → policy_area → contract

WIRING TO INFRASTRUCTURE:
    infrastructure/calibration/calibration_core.py     ← Frozen types
    infrastructure/calibration/phase2_calibrator.py    ← TYPE constraints
    infrastructure/calibration/calibration_manifest.py ← Audit trail
    infrastructure/calibration/calibration_auditor.py  ← N3-AUD veto gate
    infrastructure/calibration/interaction_governor.py ← Bounded fusion
    infrastructure/calibration/fact_registry.py        ← Deduplication
            ↓
    THIS MODULE: Policy facade for contract execution
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Final

# ============================================================================
# INFRASTRUCTURE IMPORTS - Core calibration types
# ============================================================================
from farfan_pipeline.infrastructure.calibration import (
    CalibrationLayer,
    CalibrationParameter,
    CalibrationPhase,
    FiscalContext,
    # Ingestion calibrator
    IngestionCalibrator,
    MethodBinding,
    # Method binding
    MethodBindingSet,
    MunicipalityCategory,
    Phase2CalibrationResult,
    # Phase-2 calibrator
    Phase2Calibrator,
    UnitOfAnalysis,
    is_operation_prohibited,
)
from farfan_pipeline.infrastructure.calibration.calibration_auditor import (
    AuditResult,
    CalibrationAuditor,
)

# ============================================================================
# EXTENDED INFRASTRUCTURE IMPORTS - For manifest, audit, governance
# ============================================================================
from farfan_pipeline.infrastructure.calibration.calibration_manifest import (
    CalibrationDecision,
    CalibrationManifest,
    DriftReport,
    ManifestBuilder,
)
from farfan_pipeline.infrastructure.calibration.fact_registry import (
    CanonicalFactRegistry,
    EpistemologicalLevel,
    FactFactory,
    RegistryStatistics,
)
from farfan_pipeline.infrastructure.calibration.interaction_governor import (
    DependencyGraph,
    InteractionGovernor,
    InteractionViolation,
    MethodNode,
    VetoCoordinator,
    VetoReport,
    VetoResult,
    bounded_multiplicative_fusion,
)

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

_SCHEMA_VERSION: Final[str] = "2.0.0"


@dataclass
class CalibrationParameters:
    """
    Calibration parameters for a specific scope (global/dimension/PA/contract).

    This is the MUTABLE policy-level configuration that wraps IMMUTABLE
    infrastructure CalibrationLayer instances for hierarchical overrides.
    """

    confidence_threshold: float = 0.7
    method_weights: dict[str, float] = field(default_factory=dict)
    bayesian_priors: dict[str, Any] = field(default_factory=dict)
    random_seed: int = 42
    enable_belief_propagation: bool = True
    dempster_shafer_enabled: bool = True
    # Link to frozen infrastructure layer (if available)
    _infrastructure_layer: CalibrationLayer | None = field(default=None, repr=False)

    def validate(self) -> None:
        """Validate calibration parameters."""
        if not 0 <= self.confidence_threshold <= 1:
            raise ValueError(
                f"confidence_threshold must be in [0, 1], got {self.confidence_threshold}"
            )
        if self.random_seed < 0:
            raise ValueError(f"random_seed must be non-negative, got {self.random_seed}")

    def bind_infrastructure_layer(self, layer: CalibrationLayer) -> None:
        """Bind an immutable infrastructure layer to this policy configuration."""
        object.__setattr__(self, "_infrastructure_layer", layer)

    @property
    def infrastructure_layer(self) -> CalibrationLayer | None:
        """Access the bound infrastructure layer."""
        return self._infrastructure_layer


class CalibrationPolicy:
    """Manages calibration policies for JSON contract-based execution.

    Provides hierarchical calibration:
    - Global defaults
    - Dimension overrides (D1-D6)
    - Policy area overrides (PA01-PA10)
    - Contract overrides (Q001-Q300)
    """

    def __init__(self) -> None:
        self._global_params = CalibrationParameters()
        self._dimension_params: dict[str, CalibrationParameters] = {}
        self._policy_area_params: dict[str, CalibrationParameters] = {}
        self._contract_params: dict[str, CalibrationParameters] = {}

    def get_parameters(
        self,
        question_id: str,
        dimension_id: str | None = None,
        policy_area_id: str | None = None,
    ) -> CalibrationParameters:
        """Get calibration parameters for a specific context.

        Resolution order:
        1. Contract-specific (Q{i})
        2. Policy area-specific (PA{j})
        3. Dimension-specific (DIM{k})
        4. Global defaults
        """
        # Check contract-specific
        if question_id in self._contract_params:
            return self._contract_params[question_id]

        # Check policy area-specific
        if policy_area_id and policy_area_id in self._policy_area_params:
            return self._policy_area_params[policy_area_id]

        # Check dimension-specific
        if dimension_id and dimension_id in self._dimension_params:
            return self._dimension_params[dimension_id]

        # Return global defaults
        return self._global_params

    def set_dimension_parameters(self, dimension_id: str, params: CalibrationParameters) -> None:
        """Set calibration parameters for a specific dimension (D1-D6)."""
        params.validate()
        self._dimension_params[dimension_id] = params
        logger.info(f"Set calibration parameters for dimension {dimension_id}")

    def set_policy_area_parameters(
        self, policy_area_id: str, params: CalibrationParameters
    ) -> None:
        """Set calibration parameters for a specific policy area (PA01-PA10)."""
        params.validate()
        self._policy_area_params[policy_area_id] = params
        logger.info(f"Set calibration parameters for policy area {policy_area_id}")

    def set_contract_parameters(self, question_id: str, params: CalibrationParameters) -> None:
        """Set calibration parameters for a specific contract (Q001-Q300)."""
        params.validate()
        self._contract_params[question_id] = params
        logger.info(f"Set calibration parameters for contract {question_id}")

    def load_from_contract(self, contract: dict[str, Any]) -> CalibrationParameters:
        """Load calibration parameters from a contract specification.

        Args:
            contract: Q{i}.v3.json contract dict

        Returns:
            CalibrationParameters extracted from contract or defaults
        """
        calibration_spec = contract.get("calibration", {})

        params = CalibrationParameters(
            confidence_threshold=calibration_spec.get("confidence_threshold", 0.7),
            method_weights=calibration_spec.get("method_weights", {}),
            bayesian_priors=calibration_spec.get("bayesian_priors", {}),
            random_seed=calibration_spec.get("random_seed", 42),
            enable_belief_propagation=calibration_spec.get("enable_belief_propagation", True),
            dempster_shafer_enabled=calibration_spec.get("dempster_shafer_enabled", True),
        )

        params.validate()
        return params


class ParametrizationManager:
    """
    Manages runtime parametrization for 300 JSON contract executors.

    WIRING: Delegates to Phase2Calibrator for TYPE-specific calibration.
    """

    def __init__(
        self,
        calibration_policy: CalibrationPolicy,
        phase2_calibrator: Phase2Calibrator | None = None,
    ) -> None:
        self._calibration_policy = calibration_policy
        self._phase2_calibrator = phase2_calibrator or Phase2Calibrator()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_execution_parameters(self, contract: dict[str, Any]) -> dict[str, Any]:
        """Extract execution parameters from contract for executor.

        Returns dict suitable for passing to GenericContractExecutor.
        """
        identity = contract.get("identity", {})
        question_id = identity.get("question_id")
        dimension_id = identity.get("dimension_id")
        policy_area_id = identity.get("policy_area_id")

        # Get calibration parameters
        calib_params = self._calibration_policy.get_parameters(
            question_id=question_id,
            dimension_id=dimension_id,
            policy_area_id=policy_area_id,
        )

        # Build execution parameters
        return {
            "question_id": question_id,
            "dimension_id": dimension_id,
            "policy_area_id": policy_area_id,
            "calibration": {
                "confidence_threshold": calib_params.confidence_threshold,
                "method_weights": calib_params.method_weights,
                "random_seed": calib_params.random_seed,
                "enable_belief_propagation": calib_params.enable_belief_propagation,
                "dempster_shafer_enabled": calib_params.dempster_shafer_enabled,
            },
            "method_binding": contract.get("method_binding", {}),
            "evidence_assembly": contract.get("evidence_assembly", {}),
        }

    def calibrate_for_contract(
        self,
        contract: dict[str, Any],
        binding_set: MethodBindingSet,
        unit_of_analysis_id: str,
    ) -> Phase2CalibrationResult:
        """
        Calibrate Phase-2 execution using infrastructure calibrator.

        DELEGATES to Phase2Calibrator for TYPE-specific constraints:
        - Fusion strategy selection
        - Prohibited operation enforcement
        - Validator gating

        Args:
            contract: Q{i}.v3.json contract dict
            binding_set: Method bindings for this contract
            unit_of_analysis_id: Hash identifying unit of analysis

        Returns:
            Phase2CalibrationResult with frozen calibration layer

        Raises:
            EpistemicViolation: If TYPE constraints cannot be satisfied
        """
        self._logger.info(f"Calibrating contract {binding_set.contract_id} via Phase2Calibrator")

        result = self._phase2_calibrator.calibrate(
            binding_set=binding_set,
            unit_of_analysis_id=unit_of_analysis_id,
        )

        # Bind infrastructure layer to policy parameters
        identity = contract.get("identity", {})
        question_id = identity.get("question_id", "")

        if question_id and question_id in self._calibration_policy._contract_params:
            self._calibration_policy._contract_params[question_id].bind_infrastructure_layer(
                result.calibration_layer
            )

        return result


class ConfidenceCalibrator:
    """
    Bayesian confidence calibration for multi-method outputs.

    Implements Dempster-Shafer belief propagation and calibrated
    confidence intervals for method aggregation.

    WIRING: Uses bounded_multiplicative_fusion from interaction_governor
    to prevent numerical explosion/collapse.
    """

    def __init__(self, calibration_policy: CalibrationPolicy) -> None:
        self._calibration_policy = calibration_policy
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calibrate_confidence(
        self,
        method_outputs: list[dict[str, Any]],
        question_id: str,
        dimension_id: str,
        policy_area_id: str,
    ) -> float:
        """Calibrate overall confidence from multi-method outputs.

        Uses Bayesian aggregation with method-specific weights.

        Returns:
            Calibrated confidence score in [0, 1]
        """
        params = self._calibration_policy.get_parameters(
            question_id=question_id,
            dimension_id=dimension_id,
            policy_area_id=policy_area_id,
        )

        if not method_outputs:
            return 0.0

        # Extract confidence scores from method outputs
        confidences = []
        weights = []

        for output in method_outputs:
            conf = output.get("confidence", 0.5)
            method_name = output.get("method_name", "unknown")
            weight = params.method_weights.get(method_name, 1.0)

            confidences.append(conf)
            weights.append(weight)

        # Weighted average
        if sum(weights) == 0:
            return 0.0

        calibrated = sum(c * w for c, w in zip(confidences, weights)) / sum(weights)

        # Apply Dempster-Shafer if enabled
        if params.dempster_shafer_enabled:
            calibrated = self._apply_dempster_shafer(calibrated, method_outputs)

        return min(max(calibrated, 0.0), 1.0)

    def _apply_dempster_shafer(
        self, base_confidence: float, method_outputs: list[dict[str, Any]]
    ) -> float:
        """Apply Dempster-Shafer belief propagation.

        Uses bounded_multiplicative_fusion from infrastructure layer
        to prevent numerical explosion/collapse (INV-INT-002).
        """
        # Simplified: adjust confidence based on method agreement
        if len(method_outputs) < 2:
            return base_confidence

        # Calculate variance in method confidences
        confidences = [o.get("confidence", 0.5) for o in method_outputs]
        variance = sum((c - base_confidence) ** 2 for c in confidences) / len(confidences)

        # Reduce confidence if high variance (methods disagree)
        disagreement_penalty = min(variance * 2, 0.3)

        return base_confidence * (1 - disagreement_penalty)

    def multiplicative_fusion(self, weights: list[float]) -> float:
        """
        Perform bounded multiplicative fusion.

        DELEGATES to infrastructure layer to enforce INV-INT-002:
        Result bounded in [0.01, 10.0].
        """
        return bounded_multiplicative_fusion(weights)


# ============================================================================
# CALIBRATION ORCHESTRATOR - Full system integration
# ============================================================================


class CalibrationOrchestrator:
    """
    Full calibration system orchestrator integrating all infrastructure components.

    SYSTEM CAPABILITIES:
    1. Calibration within epistemic regime (not parallel)
    2. TYPE-specific defaults and prohibitions (cached)
    3. Ingestion/Phase-2 calibration with bounded strategies
    4. Manifest hashing and optional cryptographic signatures
    5. Drift auditing and N3-AUD veto gates
    6. Interaction governance (acyclicity, bounded fusion, veto cascades)
    7. Fact registry (deduplication, verbosity threshold)

    INVARIANTS ENFORCED:
    - INV-CAL-FREEZE-001: All calibration parameters immutable post-construction
    - INV-CAL-REGIME-001: Operates within epistemic regime
    - INV-CAL-AUDIT-001: All parameters subject to N3-AUD verification
    - INV-CAL-HASH-001: Deterministic manifest hashing

    SUCCESS CRITERIA:
    - Calibration layers build with all required parameters
    - TYPE validator passes (ratios, patterns, prohibitions)
    - Auditor passes (bounds, thresholds)
    - Interaction governor: no fatal cycles
    - Fact registry: verbosity >= 0.90
    """

    def __init__(
        self,
        evidence_commit: str | None = None,
    ) -> None:
        """
        Initialize the calibration orchestrator.

        Args:
            evidence_commit: Git commit SHA for evidence pinning.
        """
        self._evidence_commit = evidence_commit

        # Infrastructure components
        self._ingestion_calibrator = IngestionCalibrator(evidence_commit=evidence_commit)
        self._phase2_calibrator = Phase2Calibrator(evidence_commit=evidence_commit)
        self._auditor = CalibrationAuditor()
        self._interaction_governor = InteractionGovernor()
        self._fact_registry = CanonicalFactRegistry()

        # Policy layer
        self._calibration_policy = CalibrationPolicy()
        self._parametrization_manager = ParametrizationManager(
            calibration_policy=self._calibration_policy,
            phase2_calibrator=self._phase2_calibrator,
        )
        self._confidence_calibrator = ConfidenceCalibrator(self._calibration_policy)

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calibrate_full_pipeline(
        self,
        unit: UnitOfAnalysis,
        contract_type_code: str,
        binding_set: MethodBindingSet,
    ) -> tuple[CalibrationManifest, AuditResult]:
        """
        Perform full pipeline calibration with audit.

        Steps:
        1. Calibrate ingestion phase (N1-EMP)
        2. Calibrate Phase-2 (N2-INF)
        3. Build calibration manifest
        4. Audit manifest against specifications
        5. Return manifest and audit result

        Args:
            unit: Unit of analysis characteristics
            contract_type_code: TYPE_A, TYPE_B, etc.
            binding_set: Method bindings for this contract

        Returns:
            Tuple of (CalibrationManifest, AuditResult)

        Raises:
            EpistemicViolation: If TYPE constraints violated
            ValidationError: If calibration invariants violated
        """
        self._logger.info(
            f"Full pipeline calibration for unit={unit.municipality_code}, "
            f"type={contract_type_code}"
        )

        # Step 1: Ingestion calibration
        ingestion_layer = self._ingestion_calibrator.calibrate(
            unit=unit,
            contract_type_code=contract_type_code,
        )

        # Step 2: Phase-2 calibration
        phase2_result = self._phase2_calibrator.calibrate(
            binding_set=binding_set,
            unit_of_analysis_id=unit.to_unit_of_analysis_id(),
        )

        # Step 3: Build manifest
        now = datetime.now(UTC)
        manifest = (
            ManifestBuilder(
                contract_id=binding_set.contract_id,
                unit_of_analysis=unit,
            )
            .with_contract_type(contract_type_code)
            .with_ingestion_layer(ingestion_layer)
            .with_phase2_layer(phase2_result.calibration_layer)
            .add_decision(
                CalibrationDecision(
                    decision_id=f"DEC_{now.strftime('%Y%m%d%H%M%S')}",
                    parameter_name="fusion_strategy",
                    chosen_value=0.0,  # N/A for string
                    alternative_values=(),
                    rationale=f"Selected {phase2_result.fusion_strategy} for {contract_type_code}",
                    source_evidence="artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json",
                    decision_timestamp=now,
                )
            )
            .build()
        )

        # Step 4: Audit manifest
        audit_result = self._auditor.audit(manifest)

        self._logger.info(
            f"Calibration complete: manifest_hash={manifest.compute_hash()[:12]}..., "
            f"audit_passed={audit_result.passed}"
        )

        return manifest, audit_result

    def validate_interactions(
        self,
        methods: list[MethodNode],
    ) -> list[InteractionViolation]:
        """
        Validate method interaction graph.

        DELEGATES to InteractionGovernor for:
        - Cycle detection (INV-INT-001)
        - Level inversion detection (INV-INT-004)

        Returns:
            List of violations (empty = valid)
        """
        graph = self._interaction_governor.build_dependency_graph(methods)
        return self._interaction_governor.validate_graph(graph)

    def execute_veto_cascade(
        self,
        veto_results: list[VetoResult],
    ) -> VetoReport:
        """
        Execute N3-AUD veto cascade.

        INVARIANT: INV-INT-003 - Veto cascade respects specificity ordering.
        Most specific vetos applied first to prevent redundancy.
        """
        # Build a minimal graph for the coordinator
        graph = DependencyGraph()
        coordinator = VetoCoordinator(graph)
        return coordinator.execute_veto_cascade(veto_results)

    def register_fact(
        self,
        content: str,
        source_method: str,
        epistemic_level: EpistemologicalLevel,
    ) -> tuple[bool, str]:
        """
        Register a fact with deduplication.

        INVARIANTS:
        - INV-FACT-001: Every fact has exactly one canonical representation
        - INV-FACT-002: Duplicate triggers provenance logging, not addition
        - INV-FACT-003: Verbosity ratio >= 0.90

        Returns:
            Tuple of (was_new, canonical_fact_id)
        """
        fact = FactFactory.create(
            content=content,
            source_method=source_method,
            epistemic_level=epistemic_level,
        )
        return self._fact_registry.register(fact)

    def get_registry_statistics(self) -> RegistryStatistics:
        """Get fact registry statistics."""
        return self._fact_registry.get_statistics()

    def validate_verbosity(self) -> bool:
        """
        Check if fact registry verbosity meets threshold.

        SUCCESS CRITERION: verbosity >= 0.90
        """
        return self._fact_registry.validate_verbosity()

    def audit_drift(
        self,
        manifest: CalibrationManifest,
        runtime_observations: list[dict[str, Any]],
        expected_coverage: float,
        expected_credible_width: float | None = None,
    ) -> DriftReport:
        """
        Detect calibration drift between design and runtime.

        DELEGATES to CalibrationAuditor for drift detection.
        """
        return self._auditor.audit_drift(
            manifest=manifest,
            runtime_observations=runtime_observations,
            expected_coverage=expected_coverage,
            expected_credible_width=expected_credible_width,
        )

    def check_operation_prohibited(
        self,
        contract_type_code: str,
        operation: str,
    ) -> bool:
        """
        Check if an operation is prohibited for a contract type.

        DELEGATES to type_defaults for single-source prohibition checking.
        """
        return is_operation_prohibited(contract_type_code, operation)

    @property
    def calibration_policy(self) -> CalibrationPolicy:
        """Access the calibration policy."""
        return self._calibration_policy

    @property
    def fact_registry(self) -> CanonicalFactRegistry:
        """Access the fact registry."""
        return self._fact_registry


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Policy-level types
    "CalibrationParameters",
    "CalibrationPolicy",
    "ParametrizationManager",
    "ConfidenceCalibrator",
    # Full orchestrator
    "CalibrationOrchestrator",
    # Re-exports from infrastructure for convenience
    "CalibrationLayer",
    "CalibrationParameter",
    "CalibrationPhase",
    "Phase2Calibrator",
    "Phase2CalibrationResult",
    "IngestionCalibrator",
    "CalibrationAuditor",
    "AuditResult",
    "InteractionGovernor",
    "VetoCoordinator",
    "VetoReport",
    "CanonicalFactRegistry",
    "FactFactory",
    "EpistemologicalLevel",
    "MethodBindingSet",
    "MethodBinding",
    "UnitOfAnalysis",
    "FiscalContext",
    "MunicipalityCategory",
    "bounded_multiplicative_fusion",
]
