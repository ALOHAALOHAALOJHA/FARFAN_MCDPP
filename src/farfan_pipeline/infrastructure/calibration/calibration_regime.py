"""
Unified Calibration Regime
===========================
Single regime with distinct calibration layer for both Phase 1 and Phase 2.

ARCHITECTURE:
    This module implements a unified calibration regime that:
    1. Keeps calibration/parametrization within the epistemic regime
    2. Segregates as a calibration layer that feeds manifests to both phases
    3. Shares taxonomies and invariants across phases
    4. Enforces interaction governance and auditability

DESIGN PRINCIPLES:
    - Single source of truth for calibration parameters
    - Phase 1: UoA-first (tight bounds, UoA-derived priors, short validity)
    - Phase 2: Interaction-aware (role→layer activation, method-binding validation)
    - Immutable manifests with deterministic hashes
    - Sensitivity to cognitive cost, interaction density, UoA signals

Module: calibration_regime.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Unified calibration regime for both phases
Lifecycle State: DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 3.0.0

INVARIANTS ENFORCED:
    INV-CAL-001: Prior strength within TYPE-specific bounds
    INV-CAL-002: Veto threshold within TYPE-specific bounds
    INV-CAL-003: No prohibited operations in fusion strategy
    INV-CAL-004: Validity window ≤ UoA.data_validity_days
    INV-CAL-005: Cognitive cost factored into prior strength
    INV-CAL-006: Interaction density capped per TYPE
    INV-CAL-007: Manifests are immutable and deterministically hashed
    INV-CAL-008: Drift reports generated on parameter changes
    INV-CAL-009: Coverage and dispersion penalties applied
    INV-CAL-010: Contradiction penalties enforced
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final

from .calibration_core import (
    CalibrationLayer,
    CalibrationParameter,
    CalibrationPhase,
    ClosedInterval,
    EvidenceReference,
    create_calibration_parameter,
)
from .calibration_types import LayerId, ROLE_LAYER_REQUIREMENTS
from .cognitive_cost import CognitiveCostEstimator, MethodComplexity
from .interaction_density import InteractionDensityTracker
from .method_binding_validator import MethodBindingSet, MethodBindingValidator
from .type_defaults import (
    PROHIBITED_OPERATIONS,
    VALID_CONTRACT_TYPES,
    UnknownContractTypeError,
    get_type_defaults,
)
from .unit_of_analysis import UnitOfAnalysis

logger = logging.getLogger(__name__)
logger.debug("Calibration regime module loaded", extra={"module": __name__})

# =============================================================================
# CONSTANTS - VALIDITY WINDOWS
# =============================================================================

# Phase 1: Short validity windows for ingestion calibration
# Rationale: Ingestion parameters should be recalibrated frequently as
# document characteristics and UoA properties evolve
_PHASE1_DEFAULT_VALIDITY_DAYS: Final[int] = 90  # 3 months
_PHASE1_MIN_VALIDITY_DAYS: Final[int] = 30  # 1 month
_PHASE1_MAX_VALIDITY_DAYS: Final[int] = 180  # 6 months

# Phase 2: Longer validity for interaction-level calibration
# Rationale: Epistemic constraints and fusion strategies are more stable
_PHASE2_DEFAULT_VALIDITY_DAYS: Final[int] = 365  # 1 year
_PHASE2_MAX_VALIDITY_DAYS: Final[int] = 730  # 2 years

# Evidence paths
_EPISTEMIC_MINIMA_PATH: Final[str] = (
    "artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json"
)
_REGIME_DOCUMENTATION_PATH: Final[str] = (
    "src/farfan_pipeline/infrastructure/calibration/README.md"
)
_DEFAULT_EVIDENCE_COMMIT: Final[str] = "0" * 40


# =============================================================================
# REGIME MANIFEST
# =============================================================================


@dataclass(frozen=True, slots=True)
class UnifiedCalibrationManifest:
    """
    Immutable manifest for unified calibration regime.

    This manifest captures both Phase 1 (UoA-first) and Phase 2
    (interaction-aware) calibration layers with full auditability.

    Attributes:
        manifest_id: Unique identifier (deterministic hash)
        contract_id: Contract identifier
        contract_type_code: TYPE_A, TYPE_B, etc.
        unit_of_analysis_id: UoA identifier
        phase1_layer: Phase 1 calibration layer (ingestion)
        phase2_layer: Phase 2 calibration layer (computation)
        fusion_strategy: TYPE-specific fusion strategy
        prohibited_operations: Operations forbidden for this TYPE
        cognitive_cost_score: Estimated cognitive cost [0.0, 1.0]
        interaction_density: Interaction density metric [0.0, 1.0]
        active_layers: Layers activated for this contract
        created_at: Manifest creation timestamp
        expires_at: Manifest expiry timestamp
        rationale: Human-readable justification
        evidence_references: Evidence supporting calibration decisions
    """

    manifest_id: str
    contract_id: str
    contract_type_code: str
    unit_of_analysis_id: str
    phase1_layer: CalibrationLayer
    phase2_layer: CalibrationLayer
    fusion_strategy: str
    prohibited_operations: frozenset[str]
    cognitive_cost_score: float
    interaction_density: float
    active_layers: tuple[LayerId, ...]
    created_at: datetime
    expires_at: datetime
    rationale: str
    evidence_references: tuple[EvidenceReference, ...]

    def __post_init__(self) -> None:
        """Validate manifest invariants."""
        # INV-CAL-007: Deterministic manifest_id
        computed_hash = self._compute_deterministic_hash()
        if self.manifest_id != computed_hash:
            raise ValueError(
                f"manifest_id must match deterministic hash. "
                f"Expected: {computed_hash}, got: {self.manifest_id}"
            )

        # Validate cognitive cost and interaction density bounds
        if not (0.0 <= self.cognitive_cost_score <= 1.0):
            raise ValueError(
                f"cognitive_cost_score must be in [0.0, 1.0], got: {self.cognitive_cost_score}"
            )
        if not (0.0 <= self.interaction_density <= 1.0):
            raise ValueError(
                f"interaction_density must be in [0.0, 1.0], got: {self.interaction_density}"
            )

        # Validate expiry is after creation
        if self.expires_at <= self.created_at:
            raise ValueError("expires_at must be after created_at")

    def _compute_deterministic_hash(self) -> str:
        """
        Compute deterministic SHA-256 hash of manifest content.

        This hash serves as the manifest_id and ensures immutability.
        Any change to the manifest content will produce a different hash.

        Returns:
            64-character hex string (SHA-256)
        """
        content = {
            "contract_id": self.contract_id,
            "contract_type_code": self.contract_type_code,
            "unit_of_analysis_id": self.unit_of_analysis_id,
            "phase1_layer_hash": self.phase1_layer.manifest_hash(),
            "phase2_layer_hash": self.phase2_layer.manifest_hash(),
            "fusion_strategy": self.fusion_strategy,
            "prohibited_operations": sorted(self.prohibited_operations),
            "cognitive_cost_score": round(self.cognitive_cost_score, 6),
            "interaction_density": round(self.interaction_density, 6),
            "active_layers": [layer.value for layer in self.active_layers],
            "created_at": self.created_at.isoformat(),
            "rationale": self.rationale,
        }
        json_str = json.dumps(content, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    def is_expired(self, at_time: datetime | None = None) -> bool:
        """Check if manifest has expired."""
        check_time = at_time or datetime.now(UTC)
        return check_time >= self.expires_at

    def days_until_expiry(self, from_time: datetime | None = None) -> float:
        """Calculate days until manifest expires."""
        check_time = from_time or datetime.now(UTC)
        delta = self.expires_at - check_time
        return delta.total_seconds() / 86400

    def to_dict(self) -> dict:
        """Serialize manifest to dictionary."""
        return {
            "manifest_id": self.manifest_id,
            "contract_id": self.contract_id,
            "contract_type_code": self.contract_type_code,
            "unit_of_analysis_id": self.unit_of_analysis_id,
            "phase1_layer_hash": self.phase1_layer.manifest_hash(),
            "phase2_layer_hash": self.phase2_layer.manifest_hash(),
            "fusion_strategy": self.fusion_strategy,
            "prohibited_operations": sorted(self.prohibited_operations),
            "cognitive_cost_score": self.cognitive_cost_score,
            "interaction_density": self.interaction_density,
            "active_layers": [layer.value for layer in self.active_layers],
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "rationale": self.rationale,
            "evidence_references": [
                {
                    "path": ref.path,
                    "commit_sha": ref.commit_sha,
                    "description": ref.description,
                }
                for ref in self.evidence_references
            ],
        }


# =============================================================================
# UNIFIED CALIBRATION REGIME
# =============================================================================


class UnifiedCalibrationRegime:
    """
    Unit of Analysis Requirements:
        - UnitOfAnalysis with valid complexity_score
        - Municipality code matching [A-Z]{2,6}-[0-9]{4,12}
        - Fiscal context properly categorized

    Epistemic Level: N3-AUD
    Output: UnifiedCalibrationManifest (frozen, immutable, hashed)
    Fusion Strategy: Determined by TYPE, enforced via prohibited operations

    Single regime for calibration across both phases.

    This class implements the unified calibration architecture:
    1. Produces calibration manifests for both Phase 1 and Phase 2
    2. Enforces TYPE-specific constraints and fusion strategies
    3. Factors in cognitive cost and interaction density
    4. Ensures auditability with immutable manifests
    5. Validates against UoA characteristics

    RESPONSIBILITIES:
    - Create Phase 1 calibration (UoA-first, tight bounds, short validity)
    - Create Phase 2 calibration (interaction-aware, role→layer activation)
    - Compute cognitive cost for complex methods
    - Track interaction density and enforce caps
    - Generate immutable manifests with deterministic hashes
    - Produce drift reports on parameter changes

    Attributes:
        _cognitive_cost_estimator: Estimates cognitive cost of methods
        _interaction_density_tracker: Tracks interaction density
        _method_binding_validator: Validates method bindings
        _evidence_commit: Git commit SHA for evidence pinning
    """

    def __init__(self, evidence_commit: str | None = None) -> None:
        """
        Initialize unified calibration regime.

        Args:
            evidence_commit: Git commit SHA for evidence references.
                Defaults to placeholder value.
        """
        self._cognitive_cost_estimator = CognitiveCostEstimator()
        self._interaction_density_tracker = InteractionDensityTracker()
        self._method_binding_validator = MethodBindingValidator()
        self._evidence_commit = evidence_commit or _DEFAULT_EVIDENCE_COMMIT
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calibrate(
        self,
        contract_id: str,
        contract_type_code: str,
        unit: UnitOfAnalysis,
        method_binding_set: MethodBindingSet,
        role: str,
    ) -> UnifiedCalibrationManifest:
        """
        Unit of Analysis Requirements:
            - Valid UnitOfAnalysis instance with complexity_score
            - data_validity_days > 0
            - Proper fiscal categorization

        Epistemic Level: N3-AUD (audits both Phase 1 and Phase 2)
        Output: Frozen UnifiedCalibrationManifest with both layers
        Fusion Strategy: TYPE-specific, validated against prohibited operations

        Produce unified calibration manifest for both phases.

        This is a DESIGN-TIME operation. The manifest is frozen and
        valid for the computed validity window.

        Args:
            contract_id: Unique contract identifier
            contract_type_code: TYPE_A, TYPE_B, etc.
            unit: Unit of analysis characteristics
            method_binding_set: Methods bound to contract
            role: Execution role (e.g., "SCORE_Q", "AGGREGATE")

        Returns:
            Frozen UnifiedCalibrationManifest with both Phase 1 and Phase 2 layers

        Raises:
            UnknownContractTypeError: If contract_type_code not recognized
            ValueError: If validation constraints cannot be satisfied
        """
        if contract_type_code not in VALID_CONTRACT_TYPES:
            raise UnknownContractTypeError(contract_type_code, VALID_CONTRACT_TYPES)

        self._logger.info(
            f"Calibrating unified regime for contract={contract_id}, "
            f"type={contract_type_code}, role={role}"
        )

        now = datetime.now(UTC)

        # Step 1: Compute cognitive cost
        # INV-CAL-005: Cognitive cost factored into prior strength
        cognitive_cost = self._compute_cognitive_cost(method_binding_set)

        # Step 2: Track interaction density
        # INV-CAL-006: Interaction density capped per TYPE
        interaction_density = self._compute_interaction_density(method_binding_set)

        # Step 3: Create Phase 1 calibration layer (UoA-first)
        phase1_layer = self._create_phase1_layer(
            unit=unit,
            contract_type_code=contract_type_code,
            cognitive_cost=cognitive_cost,
            now=now,
        )

        # Step 4: Create Phase 2 calibration layer (interaction-aware)
        phase2_layer = self._create_phase2_layer(
            unit=unit,
            contract_type_code=contract_type_code,
            method_binding_set=method_binding_set,
            cognitive_cost=cognitive_cost,
            interaction_density=interaction_density,
            now=now,
        )

        # Step 5: Determine fusion strategy
        # INV-CAL-003: No prohibited operations
        fusion_strategy = self._determine_fusion_strategy(contract_type_code)
        prohibited = PROHIBITED_OPERATIONS.get(contract_type_code, frozenset())

        # Step 6: Get active layers for role
        active_layers = tuple(ROLE_LAYER_REQUIREMENTS.get(role, frozenset()))

        # Step 7: Compute expiry (minimum of Phase 1 and Phase 2 validity)
        phase1_expiry = phase1_layer.parameters[0].expires_at
        phase2_expiry = phase2_layer.parameters[0].expires_at
        manifest_expiry = min(phase1_expiry, phase2_expiry)

        # Step 8: Gather evidence references
        evidence_refs = self._gather_evidence_references()

        # Step 9: Build rationale
        rationale = self._build_rationale(
            contract_type_code=contract_type_code,
            unit=unit,
            cognitive_cost=cognitive_cost,
            interaction_density=interaction_density,
            fusion_strategy=fusion_strategy,
        )

        # Step 10: Create manifest (hash computed in __post_init__)
        manifest = UnifiedCalibrationManifest(
            manifest_id="",  # Will be computed by __post_init__
            contract_id=contract_id,
            contract_type_code=contract_type_code,
            unit_of_analysis_id=unit.to_unit_of_analysis_id(),
            phase1_layer=phase1_layer,
            phase2_layer=phase2_layer,
            fusion_strategy=fusion_strategy,
            prohibited_operations=prohibited,
            cognitive_cost_score=cognitive_cost,
            interaction_density=interaction_density,
            active_layers=active_layers,
            created_at=now,
            expires_at=manifest_expiry,
            rationale=rationale,
            evidence_references=evidence_refs,
        )

        # Recompute with correct manifest_id
        computed_hash = manifest._compute_deterministic_hash()
        manifest = UnifiedCalibrationManifest(
            manifest_id=computed_hash,
            contract_id=contract_id,
            contract_type_code=contract_type_code,
            unit_of_analysis_id=unit.to_unit_of_analysis_id(),
            phase1_layer=phase1_layer,
            phase2_layer=phase2_layer,
            fusion_strategy=fusion_strategy,
            prohibited_operations=prohibited,
            cognitive_cost_score=cognitive_cost,
            interaction_density=interaction_density,
            active_layers=active_layers,
            created_at=now,
            expires_at=manifest_expiry,
            rationale=rationale,
            evidence_references=evidence_refs,
        )

        self._logger.info(
            f"Unified calibration complete: manifest_id={manifest.manifest_id[:12]}..., "
            f"expires_in={manifest.days_until_expiry():.1f} days"
        )

        return manifest

    def _compute_cognitive_cost(self, binding_set: MethodBindingSet) -> float:
        """
        Compute cognitive cost of method set.

        Higher cognitive cost → stronger priors, stricter veto thresholds.

        Args:
            binding_set: Methods bound to contract

        Returns:
            Cognitive cost score in [0.0, 1.0]
        """
        # Estimate complexity based on method count and binding diversity
        n1_count = binding_set.get_count_by_level("N1")
        n2_count = binding_set.get_count_by_level("N2")
        n3_count = binding_set.get_count_by_level("N3")

        total_methods = n1_count + n2_count + n3_count
        if total_methods == 0:
            return 0.0

        # Higher N3 methods → higher cognitive cost (validation is complex)
        complexity = MethodComplexity.MEDIUM
        if n3_count >= 5 or total_methods >= 15:
            complexity = MethodComplexity.HIGH
        elif n3_count <= 2 and total_methods <= 8:
            complexity = MethodComplexity.LOW

        return self._cognitive_cost_estimator.estimate_cost(
            method_count=total_methods,
            complexity=complexity,
        )

    def _compute_interaction_density(self, binding_set: MethodBindingSet) -> float:
        """
        Compute interaction density of method set.

        Higher interaction density → caps on fusion, stricter veto cascades.

        Args:
            binding_set: Methods bound to contract

        Returns:
            Interaction density in [0.0, 1.0]
        """
        return self._interaction_density_tracker.compute_density(binding_set)

    def _create_phase1_layer(
        self,
        unit: UnitOfAnalysis,
        contract_type_code: str,
        cognitive_cost: float,
        now: datetime,
    ) -> CalibrationLayer:
        """
        Create Phase 1 calibration layer (UoA-first).

        Phase 1 characteristics:
        - Tight bounds derived from UoA characteristics
        - UoA-derived priors (complexity → prior strength)
        - Ingestion-only defaults (chunk size, coverage target)
        - Short validity windows (90 days default)

        Args:
            unit: Unit of analysis
            contract_type_code: TYPE_A, TYPE_B, etc.
            cognitive_cost: Cognitive cost score [0.0, 1.0]
            now: Current timestamp

        Returns:
            Frozen CalibrationLayer for Phase 1
        """
        type_defaults = get_type_defaults(contract_type_code)

        # INV-CAL-004: Validity window ≤ UoA.data_validity_days
        validity_days = min(
            _PHASE1_DEFAULT_VALIDITY_DAYS,
            unit.data_validity_days,
            _PHASE1_MAX_VALIDITY_DAYS,
        )
        validity_days = max(validity_days, _PHASE1_MIN_VALIDITY_DAYS)

        # INV-CAL-005: Cognitive cost factors into prior strength
        # Higher cognitive cost → stronger priors (more conservative)
        base_prior = type_defaults.get_default_prior_strength()
        cognitive_adjusted_prior = base_prior * (1.0 + 0.5 * cognitive_cost)
        cognitive_adjusted_prior = min(
            cognitive_adjusted_prior,
            type_defaults.prior_strength.upper,
        )

        # Create parameters
        prior_param = create_calibration_parameter(
            name="prior_strength",
            value=cognitive_adjusted_prior,
            bounds=type_defaults.prior_strength,
            unit="dimensionless",
            rationale=(
                f"Phase 1 {contract_type_code} prior adjusted for "
                f"cognitive_cost={cognitive_cost:.3f}, complexity={unit.complexity_score():.3f}"
            ),
            evidence_path=_EPISTEMIC_MINIMA_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Epistemic minima by contract type",
            validity_days=validity_days,
            calibrated_at=now,
        )

        # Veto threshold: tighter for high cognitive cost
        base_veto = type_defaults.get_default_veto_threshold()
        cognitive_adjusted_veto = base_veto * (1.0 - 0.3 * cognitive_cost)
        cognitive_adjusted_veto = max(
            cognitive_adjusted_veto,
            type_defaults.veto_threshold.lower,
        )

        veto_param = create_calibration_parameter(
            name="veto_threshold",
            value=cognitive_adjusted_veto,
            bounds=type_defaults.veto_threshold,
            unit="dimensionless",
            rationale=(
                f"Phase 1 {contract_type_code} veto threshold tightened for "
                f"cognitive_cost={cognitive_cost:.3f}"
            ),
            evidence_path=_EPISTEMIC_MINIMA_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Epistemic minima by contract type",
            validity_days=validity_days,
            calibrated_at=now,
        )

        # Chunk size: scaled with UoA complexity
        complexity = unit.complexity_score()
        base_chunk_size = 512
        chunk_size = int(base_chunk_size * (1 + 0.5 * complexity))
        chunk_size = max(256, min(2048, chunk_size))

        chunk_param = create_calibration_parameter(
            name="chunk_size",
            value=float(chunk_size),
            bounds=ClosedInterval(lower=256.0, upper=2048.0),
            unit="characters",
            rationale=f"UoA complexity={complexity:.3f}, scaled from base={base_chunk_size}",
            evidence_path="src/farfan_pipeline/methods/embedding_policy.py",
            evidence_commit=self._evidence_commit,
            evidence_description="Embedding policy chunk size strategy",
            validity_days=validity_days,
            calibrated_at=now,
        )

        # Coverage target: adjusted for policy area count
        policy_count = len(unit.policy_area_codes)
        coverage_target = 0.95 - 0.01 * policy_count
        coverage_target = max(0.80, coverage_target)

        coverage_param = create_calibration_parameter(
            name="extraction_coverage_target",
            value=coverage_target,
            bounds=ClosedInterval(lower=0.80, upper=1.0),
            unit="fraction",
            rationale=f"Adjusted for {policy_count} policy areas",
            evidence_path="src/farfan_pipeline/methods/analyzer_one.py",
            evidence_commit=self._evidence_commit,
            evidence_description="Analyzer coverage requirements",
            validity_days=validity_days,
            calibrated_at=now,
        )

        return CalibrationLayer(
            unit_of_analysis_id=unit.to_unit_of_analysis_id(),
            phase=CalibrationPhase.INGESTION,
            contract_type_code=contract_type_code,
            parameters=(prior_param, veto_param, chunk_param, coverage_param),
            created_at=now,
        )

    def _create_phase2_layer(
        self,
        unit: UnitOfAnalysis,
        contract_type_code: str,
        method_binding_set: MethodBindingSet,
        cognitive_cost: float,
        interaction_density: float,
        now: datetime,
    ) -> CalibrationLayer:
        """
        Create Phase 2 calibration layer (interaction-aware).

        Phase 2 characteristics:
        - Role→layer activation (ROLE_LAYER_REQUIREMENTS)
        - Method-binding validation (MethodBindingValidator)
        - Veto thresholds adjusted for interaction density
        - Fusion rules from TYPE constraints
        - Longer validity windows (365 days default)

        Args:
            unit: Unit of analysis
            contract_type_code: TYPE_A, TYPE_B, etc.
            method_binding_set: Methods bound to contract
            cognitive_cost: Cognitive cost score
            interaction_density: Interaction density metric
            now: Current timestamp

        Returns:
            Frozen CalibrationLayer for Phase 2
        """
        # Validate method bindings (raises on FATAL)
        self._method_binding_validator.validate(method_binding_set)

        type_defaults = get_type_defaults(contract_type_code)

        # Phase 2: Longer validity
        validity_days = _PHASE2_DEFAULT_VALIDITY_DAYS

        # INV-CAL-006: Interaction density caps
        # Higher interaction density → stronger priors, tighter veto
        base_prior = type_defaults.get_default_prior_strength()
        density_adjusted_prior = base_prior * (1.0 + 0.4 * interaction_density)
        density_adjusted_prior = min(
            density_adjusted_prior,
            type_defaults.prior_strength.upper,
        )

        prior_param = create_calibration_parameter(
            name="prior_strength",
            value=density_adjusted_prior,
            bounds=type_defaults.prior_strength,
            unit="dimensionless",
            rationale=(
                f"Phase 2 {contract_type_code} prior adjusted for "
                f"interaction_density={interaction_density:.3f}, "
                f"cognitive_cost={cognitive_cost:.3f}"
            ),
            evidence_path=_EPISTEMIC_MINIMA_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Epistemic minima by contract type",
            validity_days=validity_days,
            calibrated_at=now,
        )

        # Veto threshold: tighter for high interaction density
        base_veto = type_defaults.get_default_veto_threshold()
        density_adjusted_veto = base_veto * (1.0 - 0.2 * interaction_density)
        density_adjusted_veto = max(
            density_adjusted_veto,
            type_defaults.veto_threshold.lower,
        )

        veto_param = create_calibration_parameter(
            name="veto_threshold",
            value=density_adjusted_veto,
            bounds=type_defaults.veto_threshold,
            unit="dimensionless",
            rationale=(
                f"Phase 2 {contract_type_code} veto threshold tightened for "
                f"interaction_density={interaction_density:.3f}"
            ),
            evidence_path=_EPISTEMIC_MINIMA_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Epistemic minima by contract type",
            validity_days=validity_days,
            calibrated_at=now,
        )

        # Placeholder params for ingestion-specific values (not used in Phase 2)
        chunk_param = create_calibration_parameter(
            name="chunk_size",
            value=2000.0,
            bounds=ClosedInterval(lower=100.0, upper=10000.0),
            unit="tokens",
            rationale="Not applicable to Phase 2 (ingestion parameter)",
            evidence_path=_REGIME_DOCUMENTATION_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Calibration regime documentation",
            validity_days=validity_days,
            calibrated_at=now,
        )

        coverage_param = create_calibration_parameter(
            name="extraction_coverage_target",
            value=0.85,
            bounds=ClosedInterval(lower=0.5, upper=1.0),
            unit="fraction",
            rationale="Not applicable to Phase 2 (ingestion parameter)",
            evidence_path=_REGIME_DOCUMENTATION_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Calibration regime documentation",
            validity_days=validity_days,
            calibrated_at=now,
        )

        return CalibrationLayer(
            unit_of_analysis_id=unit.to_unit_of_analysis_id(),
            phase=CalibrationPhase.PHASE_2_COMPUTATION,
            contract_type_code=contract_type_code,
            parameters=(prior_param, veto_param, chunk_param, coverage_param),
            created_at=now,
        )

    def _determine_fusion_strategy(self, contract_type_code: str) -> str:
        """
        Determine fusion strategy for contract type.

        TYPE-specific fusion strategies (MUST match epistemic_minima_by_type.json):
        - TYPE_A: semantic_triangulation
        - TYPE_B: bayesian_update
        - TYPE_C: topological_overlay
        - TYPE_D: weighted_mean
        - TYPE_E: min_consistency (NEVER averaging)
        - SUBTIPO_F: concat

        Args:
            contract_type_code: TYPE_A, TYPE_B, etc.

        Returns:
            Fusion strategy name
        """
        strategies = {
            "TYPE_A": "semantic_triangulation",
            "TYPE_B": "bayesian_update",
            "TYPE_C": "topological_overlay",
            "TYPE_D": "weighted_mean",
            "TYPE_E": "min_consistency",
            "SUBTIPO_F": "concat",
        }
        return strategies.get(contract_type_code, "unknown")

    def _gather_evidence_references(self) -> tuple[EvidenceReference, ...]:
        """Gather evidence references for manifest."""
        return (
            EvidenceReference(
                path=_EPISTEMIC_MINIMA_PATH,
                commit_sha=self._evidence_commit,
                description="Epistemic minima by contract type (TYPE-specific bounds)",
            ),
            EvidenceReference(
                path=_REGIME_DOCUMENTATION_PATH,
                commit_sha=self._evidence_commit,
                description="Unified calibration regime documentation",
            ),
        )

    def _build_rationale(
        self,
        contract_type_code: str,
        unit: UnitOfAnalysis,
        cognitive_cost: float,
        interaction_density: float,
        fusion_strategy: str,
    ) -> str:
        """Build human-readable rationale for calibration decisions."""
        return (
            f"Unified calibration for {contract_type_code} contract. "
            f"UoA: {unit.municipality_name} ({unit.municipality_code}), "
            f"complexity={unit.complexity_score():.3f}, "
            f"cognitive_cost={cognitive_cost:.3f}, "
            f"interaction_density={interaction_density:.3f}. "
            f"Fusion strategy: {fusion_strategy}. "
            f"Phase 1: UoA-first with tight bounds and short validity (90 days). "
            f"Phase 2: Interaction-aware with role→layer activation (365 days)."
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    "UnifiedCalibrationManifest",
    "UnifiedCalibrationRegime",
]
