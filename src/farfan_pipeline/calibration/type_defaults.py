"""
Type-Specific Calibration Defaults
==================================

Module:  calibration_defaults.py
Owner: farfan_pipeline. infrastructure.calibration
Purpose: Contract-type-specific calibration bounds and prohibited operations
Lifecycle State:  DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 2.0.0

CANONICAL SOURCE:
    src/farfan_pipeline/phases/Phase_02/epistemological_assets/contratos_clasificados.json

    Only authorized files from epistemological_assets directory are used.
    This module infers calibration bounds from the contract taxonomies and fusion strategies
    defined in that canonical source.

DESIGN PATTERN:  Flyweight Pattern
    - Each ContractType has ONE canonical CalibrationDefaults instance
    - Prevents proliferation of duplicate configuration objects
    - LRU cache guarantees identity:  get_type_defaults("TYPE_A") is get_type_defaults("TYPE_A")

INVARIANTS ENFORCED:
    INV-DEF-001: All bounds satisfy lower <= default <= upper
    INV-DEF-002: Epistemic layer ratios sum to 1.0 (within tolerance)
    INV-DEF-003: Prohibited operations are disjoint from permitted operations per type
    INV-DEF-004: Canonical source file must exist and be valid JSON

EPISTEMIC REGIME LAYERS:
    - N1_EMP (Empirical): Extraction, raw data gathering
    - N2_INF (Inferential): Analysis, computation, reasoning
    - N3_AUD (Audit): Validation, consistency checking, veto gates

CONTRACT TYPE CHARACTERISTICS:
    - TYPE_A (Semantic): N2-dominant for semantic triangulation
    - TYPE_B (Bayesian): Balanced, strong priors for statistical inference
    - TYPE_C (Causal): Strong N3 for DAG validation
    - TYPE_D (Financial): N2-dominant for aggregation, lenient veto
    - TYPE_E (Logical): Strong N3 for contradiction detection, strict veto
    - SUBTIPO_F (Hybrid): Fallback configuration for composite contracts

FAILURE MODES:
    FM-DEF-001: Canonical source file missing → CanonicalSourceError
    FM-DEF-002: Canonical source invalid JSON → CanonicalSourceError
    FM-DEF-003: Unknown contract type code → UnknownContractTypeError
    FM-DEF-004: Epistemic ratios don't sum to 1.0 → ConfigurationError

VERIFICATION STRATEGY:
    - Static analysis: Ensure all TYPE_* constants have corresponding entries
    - Runtime validation: Bounds checked at construction via ClosedInterval
    - Property tests: ratio_sum ∈ [0.99, 1.01] for all type configurations

DEPENDENCIES:
    - calibration_core: ClosedInterval, ValidationError
    - Standard library: json, pathlib, functools
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Final

from .calibration_core import (
    ClosedInterval,
)

# =============================================================================
# MODULE CONSTANTS
# =============================================================================

_CONTRATOS_CLASIFICADOS_PATH: Final[Path] = Path(
    "src/farfan_pipeline/phases/Phase_02/epistemological_assets/contratos_clasificados.json"
)

# Epistemic ratio sum tolerance (accounts for floating-point arithmetic)
RATIO_SUM_TOLERANCE: Final[float] = 0.01

# Contract type codes (canonical identifiers)
CONTRACT_TYPE_A: Final[str] = "TYPE_A"  # Semantic
CONTRACT_TYPE_B: Final[str] = "TYPE_B"  # Bayesian
CONTRACT_TYPE_C: Final[str] = "TYPE_C"  # Causal
CONTRACT_TYPE_D: Final[str] = "TYPE_D"  # Financial
CONTRACT_TYPE_E: Final[str] = "TYPE_E"  # Logical
CONTRACT_SUBTIPO_F: Final[str] = "SUBTIPO_F"  # Hybrid/Fallback

VALID_CONTRACT_TYPES: Final[frozenset[str]] = frozenset(
    {
        CONTRACT_TYPE_A,
        CONTRACT_TYPE_B,
        CONTRACT_TYPE_C,
        CONTRACT_TYPE_D,
        CONTRACT_TYPE_E,
        CONTRACT_SUBTIPO_F,
    }
)

# -----------------------------------------------------------------------------
# Prior Strength Bounds (Bayesian inference weight)
# -----------------------------------------------------------------------------
# Prior strength controls the weight given to prior beliefs vs. observed evidence
# in Bayesian updating operations.  Higher values = stronger prior influence.

PRIOR_STRENGTH_MIN: Final[float] = 0.1
PRIOR_STRENGTH_MAX: Final[float] = 10.0
PRIOR_STRENGTH_DEFAULT: Final[float] = 1.0
PRIOR_STRENGTH_BAYESIAN: Final[float] = 2.0  # TYPE_B uses stronger priors

# -----------------------------------------------------------------------------
# Veto Threshold Bounds (probability for veto gates)
# -----------------------------------------------------------------------------
# Veto threshold is the probability below which a veto gate rejects a result.
# Lower threshold = stricter veto (rejects more), Higher = more lenient.

# Strictest:  TYPE_E (logical consistency must be near-absolute)
VETO_THRESHOLD_STRICTEST_MIN: Final[float] = 0.01
VETO_THRESHOLD_STRICTEST_MAX: Final[float] = 0.05
VETO_THRESHOLD_STRICTEST_DEFAULT: Final[float] = 0.03

# Standard: TYPE_A, TYPE_B, TYPE_C (balanced strictness)
VETO_THRESHOLD_STANDARD_MIN: Final[float] = 0.03
VETO_THRESHOLD_STANDARD_MAX: Final[float] = 0.07
VETO_THRESHOLD_STANDARD_DEFAULT: Final[float] = 0.05

# Lenient: TYPE_D (financial aggregation tolerates more variance)
VETO_THRESHOLD_LENIENT_MIN: Final[float] = 0.05
VETO_THRESHOLD_LENIENT_MAX: Final[float] = 0.10
VETO_THRESHOLD_LENIENT_DEFAULT: Final[float] = 0.07

# -----------------------------------------------------------------------------
# Epistemic Layer Ratio Defaults (per contract type)
# -----------------------------------------------------------------------------
# These ratios define the distribution of processing effort across N1/N2/N3 layers
# Derived from episteme_rules.md taxonomies

# TYPE_A (Semantic): N2-dominant
N1_RATIO_TYPE_A: Final[float] = 0.30
N2_RATIO_TYPE_A: Final[float] = 0.50
N3_RATIO_TYPE_A: Final[float] = 0.20

# TYPE_B (Bayesian): Balanced with strong N2
N1_RATIO_TYPE_B: Final[float] = 0.35
N2_RATIO_TYPE_B: Final[float] = 0.40
N3_RATIO_TYPE_B: Final[float] = 0.25

# TYPE_C (Causal): Strong N3 for DAG validation
N1_RATIO_TYPE_C: Final[float] = 0.30
N2_RATIO_TYPE_C: Final[float] = 0.35
N3_RATIO_TYPE_C: Final[float] = 0.35

# TYPE_D (Financial): N2-dominant, lenient N3
N1_RATIO_TYPE_D: Final[float] = 0.25
N2_RATIO_TYPE_D: Final[float] = 0.55
N3_RATIO_TYPE_D: Final[float] = 0.20

# TYPE_E (Logical): Strong N3 for contradiction detection
N1_RATIO_TYPE_E: Final[float] = 0.25
N2_RATIO_TYPE_E: Final[float] = 0.40
N3_RATIO_TYPE_E: Final[float] = 0.35

# SUBTIPO_F (Hybrid): Balanced fallback
N1_RATIO_SUBTIPO_F: Final[float] = 0.30
N2_RATIO_SUBTIPO_F: Final[float] = 0.40
N3_RATIO_SUBTIPO_F: Final[float] = 0.30

# -----------------------------------------------------------------------------
# Fusion Strategy Constants (from episteme_rules.md PARTE IV)
# -----------------------------------------------------------------------------
FUSION_STRATEGY_SEMANTIC_CORROBORATION: Final[str] = "semantic_corroboration"
FUSION_STRATEGY_BAYESIAN_UPDATE: Final[str] = "bayesian_update"
FUSION_STRATEGY_TOPOLOGICAL_OVERLAY: Final[str] = "topological_overlay"
FUSION_STRATEGY_WEIGHTED_MEAN: Final[str] = "weighted_mean"
FUSION_STRATEGY_VETO_GATE: Final[str] = "veto_gate"
FUSION_STRATEGY_CONCAT: Final[str] = "concat"
FUSION_STRATEGY_DEMPSTER_SHAFER: Final[str] = "dempster_shafer"
FUSION_STRATEGY_GRAPH_CONSTRUCTION: Final[str] = "graph_construction"
FUSION_STRATEGY_FINANCIAL_COHERENCE: Final[str] = "financial_coherence_audit"
FUSION_STRATEGY_LOGICAL_VALIDATION: Final[str] = "logical_consistency_validation"
FUSION_STRATEGY_CARVER_SYNTHESIS: Final[str] = "carver_doctoral_synthesis"

# -----------------------------------------------------------------------------
# Contract Type to Fusion Strategy Mapping (from episteme_rules.md PARTE IV, Sec 4.3)
# -----------------------------------------------------------------------------
TYPE_FUSION_STRATEGIES: Final[dict[str, dict[str, str]]] = {
    CONTRACT_TYPE_A: {
        "N1": FUSION_STRATEGY_SEMANTIC_CORROBORATION,
        "N2": FUSION_STRATEGY_DEMPSTER_SHAFER,
        "N3": FUSION_STRATEGY_VETO_GATE,
    },
    CONTRACT_TYPE_B: {
        "N1": FUSION_STRATEGY_CONCAT,
        "N2": FUSION_STRATEGY_BAYESIAN_UPDATE,
        "N3": FUSION_STRATEGY_VETO_GATE,
    },
    CONTRACT_TYPE_C: {
        "N1": FUSION_STRATEGY_GRAPH_CONSTRUCTION,
        "N2": FUSION_STRATEGY_TOPOLOGICAL_OVERLAY,
        "N3": FUSION_STRATEGY_VETO_GATE,
    },
    CONTRACT_TYPE_D: {
        "N1": FUSION_STRATEGY_CONCAT,
        "N2": FUSION_STRATEGY_WEIGHTED_MEAN,
        "N3": FUSION_STRATEGY_FINANCIAL_COHERENCE,
    },
    CONTRACT_TYPE_E: {
        "N1": FUSION_STRATEGY_CONCAT,
        "N2": FUSION_STRATEGY_WEIGHTED_MEAN,
        "N3": FUSION_STRATEGY_LOGICAL_VALIDATION,
    },
    CONTRACT_SUBTIPO_F: {
        "N1": FUSION_STRATEGY_CONCAT,
        "N2": FUSION_STRATEGY_WEIGHTED_MEAN,
        "N3": FUSION_STRATEGY_VETO_GATE,
    },
}

# Public API for this module
__all__ = [
    "CONTRACT_SUBTIPO_F",
    "CONTRACT_TYPE_A",
    "CONTRACT_TYPE_B",
    "CONTRACT_TYPE_C",
    "CONTRACT_TYPE_D",
    "CONTRACT_TYPE_E",
    "PRIOR_STRENGTH_BAYESIAN",
    "PRIOR_STRENGTH_DEFAULT",
    "PRIOR_STRENGTH_MAX",
    "PRIOR_STRENGTH_MIN",
    "RATIO_SUM_TOLERANCE",
    "VALID_CONTRACT_TYPES",
    "VETO_THRESHOLD_LENIENT_DEFAULT",
    "VETO_THRESHOLD_LENIENT_MAX",
    "VETO_THRESHOLD_LENIENT_MIN",
    "VETO_THRESHOLD_STANDARD_DEFAULT",
    "VETO_THRESHOLD_STANDARD_MAX",
    "VETO_THRESHOLD_STANDARD_MIN",
    "VETO_THRESHOLD_STRICTEST_DEFAULT",
    "VETO_THRESHOLD_STRICTEST_MAX",
    "VETO_THRESHOLD_STRICTEST_MIN",
    "CalibrationDefaultsError",
    "CanonicalSourceError",
    "UnknownContractTypeError",
]


# =============================================================================
# EXCEPTIONS
# =============================================================================


class CalibrationDefaultsError(Exception):
    """Base exception for calibration defaults module errors."""

    pass


class CanonicalSourceError(CalibrationDefaultsError):
    """
    Raised when the canonical source file is missing or invalid.

    This indicates a deployment or configuration error—the canonical
    contracts file is required for the pipeline to function.
    """

    pass


class UnknownContractTypeError(CalibrationDefaultsError):
    """
    Raised when an unknown contract type code is requested.

    This indicates either a programming error (typo in type code) or
    a schema evolution issue (new type added without defaults).
    """

    def __init__(self, contract_type_code: str, valid_types: frozenset[str]) -> None:
        self.contract_type_code = contract_type_code
        self.valid_types = valid_types
        super().__init__(
            f"Unknown contract type:  '{contract_type_code}'. "
            f"Valid types: {sorted(valid_types)}"
        )


class ConfigurationError(CalibrationDefaultsError):
    """
    Raised when calibration configuration violates invariants.

    This indicates a bug in the defaults definition that must be
    fixed before deployment.
    """

    pass


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass(frozen=True, slots=True)
class EpistemicLayerRatios:
    """
    Distribution of processing effort across epistemic regime layers.

    The three layers (N1_EMP, N2_INF, N3_AUD) must sum to 1.0 within tolerance.
    Different contract types emphasize different layers based on their
    epistemic requirements.

    Invariants:
        INV-ELR-001: All ratios in [0.0, 1.0]
        INV-ELR-002: n1 + n2 + n3 ∈ [1.0 - tolerance, 1.0 + tolerance]

    Attributes:
        n1_empirical: Ratio for N1_EMP (extraction, data gathering).
        n2_inferential:  Ratio for N2_INF (analysis, computation).
        n3_audit: Ratio for N3_AUD (validation, veto gates).
    """

    n1_empirical: ClosedInterval
    n2_inferential: ClosedInterval
    n3_audit: ClosedInterval

    def __post_init__(self) -> None:
        """Validate that default ratios sum to 1.0 within tolerance."""
        # Extract default values (midpoints would also work, but defaults are canonical)
        # We check that the default configuration is valid
        default_sum = (
            self.n1_empirical.midpoint() + self.n2_inferential.midpoint() + self.n3_audit.midpoint()
        )

        if abs(default_sum - 1.0) > RATIO_SUM_TOLERANCE:
            raise ConfigurationError(
                f"Epistemic layer ratio midpoints must sum to 1.0 (±{RATIO_SUM_TOLERANCE}); "
                f"got {default_sum:.4f} = "
                f"n1({self.n1_empirical.midpoint():.3f}) + "
                f"n2({self.n2_inferential.midpoint():.3f}) + "
                f"n3({self.n3_audit.midpoint():.3f})"
            )

    def validate_concrete_ratios(self, n1: float, n2: float, n3: float) -> tuple[bool, str]:
        """
        Validate a concrete ratio configuration against bounds.

        Args:
            n1: Concrete N1_EMP ratio value.
            n2: Concrete N2_INF ratio value.
            n3: Concrete N3_AUD ratio value.

        Returns:
            Tuple of (is_valid, error_message). error_message is empty if valid.
        """
        errors: list[str] = []

        if not self.n1_empirical.contains(n1):
            errors.append(
                f"n1_empirical={n1} not in [{self.n1_empirical.lower}, {self.n1_empirical.upper}]"
            )
        if not self.n2_inferential.contains(n2):
            errors.append(
                f"n2_inferential={n2} not in [{self.n2_inferential.lower}, {self.n2_inferential.upper}]"
            )
        if not self.n3_audit.contains(n3):
            errors.append(f"n3_audit={n3} not in [{self.n3_audit.lower}, {self.n3_audit.upper}]")

        ratio_sum = n1 + n2 + n3
        if abs(ratio_sum - 1.0) > RATIO_SUM_TOLERANCE:
            errors.append(f"ratios sum to {ratio_sum:.4f}, expected 1.0 (±{RATIO_SUM_TOLERANCE})")

        return (len(errors) == 0, "; ".join(errors))

    def to_canonical_dict(self) -> dict[str, dict[str, float]]:
        """Convert to canonical dictionary for serialization."""
        return {
            "n1_empirical": self.n1_empirical.to_canonical_dict(),
            "n2_inferential": self.n2_inferential.to_canonical_dict(),
            "n3_audit": self.n3_audit.to_canonical_dict(),
        }


@dataclass(frozen=True, slots=True)
class ContractTypeDefaults:
    """
    Complete calibration defaults for a contract type.

    This dataclass aggregates all calibration bounds for a specific contract
    type, including epistemic layer ratios, veto thresholds, and prior strength.

    Invariants:
        INV-CTD-001: All bounds are valid ClosedIntervals
        INV-CTD-002: Epistemic ratios pass EpistemicLayerRatios validation
        INV-CTD-003: contract_type_code is in VALID_CONTRACT_TYPES

    Attributes:
        contract_type_code: Canonical identifier for this contract type.
        description: Human-readable description of the contract type.
        epistemic_ratios: Distribution across N1/N2/N3 layers.
        veto_threshold: Bounds for veto gate probability threshold.
        prior_strength: Bounds for Bayesian prior weight.
        permitted_operations: Operations allowed for this contract type.
        prohibited_operations: Operations forbidden for this contract type.
    """

    contract_type_code: str
    description: str
    epistemic_ratios: EpistemicLayerRatios
    veto_threshold: ClosedInterval
    prior_strength: ClosedInterval
    permitted_operations: frozenset[str]
    prohibited_operations: frozenset[str]

    def __post_init__(self) -> None:
        """Validate contract type defaults."""
        if self.contract_type_code not in VALID_CONTRACT_TYPES:
            raise UnknownContractTypeError(self.contract_type_code, VALID_CONTRACT_TYPES)

        # Verify permitted and prohibited are disjoint
        overlap = self.permitted_operations & self.prohibited_operations
        if overlap:
            raise ConfigurationError(
                f"Contract type {self.contract_type_code}:  operations cannot be both "
                f"permitted and prohibited:  {sorted(overlap)}"
            )

    def is_operation_permitted(self, operation: str) -> bool:
        """
        Check if an operation is permitted for this contract type.

        Args:
            operation: Operation name to check.

        Returns:
            True if operation is in permitted_operations.
        """
        return operation.lower() in self.permitted_operations

    def is_operation_prohibited(self, operation: str) -> bool:
        """
        Check if an operation is prohibited for this contract type.

        An operation is prohibited if:
        1. It is explicitly in prohibited_operations, OR
        2. Any prohibited operation name is a substring of the operation name

        Args:
            operation: Operation name to check.

        Returns:
            True if operation is prohibited.
        """
        op_lower = operation.lower()
        if op_lower in self.prohibited_operations:
            return True
        # Check for substring matches (e.g., "weighted_mean_v2" matches "weighted_mean")
        return any(prohibited in op_lower for prohibited in self.prohibited_operations)

    def get_default_veto_threshold(self) -> float:
        """Return the default veto threshold value."""
        return self.veto_threshold.midpoint()

    def get_default_prior_strength(self) -> float:
        """Return the default prior strength value."""
        return self.prior_strength.midpoint()

    def to_canonical_dict(self) -> dict[str, object]:
        """Convert to canonical dictionary for serialization."""
        return {
            "contract_type_code": self.contract_type_code,
            "description": self.description,
            "epistemic_ratios": self.epistemic_ratios.to_canonical_dict(),
            "permitted_operations": sorted(self.permitted_operations),
            "prior_strength": self.prior_strength.to_canonical_dict(),
            "prohibited_operations": sorted(self.prohibited_operations),
            "veto_threshold": self.veto_threshold.to_canonical_dict(),
        }


# =============================================================================
# TYPE-SPECIFIC DEFAULTS DEFINITIONS
# =============================================================================

# These definitions encode the epistemic characteristics of each contract type.
# Derived from analysis of contratos_clasificados.json and domain requirements.


def _create_type_a_defaults() -> ContractTypeDefaults:
    """
    Create defaults for TYPE_A (Semantic) contracts.

    TYPE_A emphasizes semantic triangulation via N2 layer operations.
    Uses semantic_corroboration, dempster_shafer, and veto_gate.
    """
    return ContractTypeDefaults(
        contract_type_code=CONTRACT_TYPE_A,
        description="Semantic contracts:  N2-dominant for semantic triangulation and corroboration",
        epistemic_ratios=EpistemicLayerRatios(
            n1_empirical=ClosedInterval(lower=0.20, upper=0.40),
            n2_inferential=ClosedInterval(lower=0.40, upper=0.60),
            n3_audit=ClosedInterval(lower=0.10, upper=0.30),
        ),
        veto_threshold=ClosedInterval(
            lower=VETO_THRESHOLD_STANDARD_MIN,
            upper=VETO_THRESHOLD_STANDARD_MAX,
        ),
        prior_strength=ClosedInterval(
            lower=PRIOR_STRENGTH_MIN,
            upper=PRIOR_STRENGTH_MAX,
        ),
        permitted_operations=frozenset(
            {
                "semantic_corroboration",
                "dempster_shafer",
                "veto_gate",
                "semantic_triangulation",
                "embedding_similarity",
                "concat",  # Added: Required for R1 assembly
                "carver_doctoral_synthesis",  # Added: Required for R4 synthesis
            }
        ),
        prohibited_operations=frozenset(
            {
                "weighted_mean",
                "simple_average",
                "bayesian_update",
                "arithmetic_aggregation",
            }
        ),
    )


def _create_type_b_defaults() -> ContractTypeDefaults:
    """
    Create defaults for TYPE_B (Bayesian) contracts.

    TYPE_B emphasizes Bayesian inference with strong priors.
    Uses bayesian_update, concat, veto_gate, carver_doctoral_synthesis.
    """
    return ContractTypeDefaults(
        contract_type_code=CONTRACT_TYPE_B,
        description="Bayesian contracts: balanced layers with strong priors for statistical inference",
        epistemic_ratios=EpistemicLayerRatios(
            n1_empirical=ClosedInterval(lower=0.25, upper=0.45),
            n2_inferential=ClosedInterval(lower=0.30, upper=0.50),
            n3_audit=ClosedInterval(lower=0.15, upper=0.35),
        ),
        veto_threshold=ClosedInterval(
            lower=VETO_THRESHOLD_STANDARD_MIN,
            upper=VETO_THRESHOLD_STANDARD_MAX,
        ),
        prior_strength=ClosedInterval(
            lower=PRIOR_STRENGTH_MIN,
            upper=PRIOR_STRENGTH_MAX,
        ),
        permitted_operations=frozenset(
            {
                "bayesian_update",
                "concat",
                "veto_gate",
                "carver_doctoral_synthesis",
                "prior_posterior_update",
                "credible_interval",
            }
        ),
        prohibited_operations=frozenset(
            {
                "weighted_mean",
                "simple_average",
                "semantic_corroboration",
                "arithmetic_aggregation",
            }
        ),
    )


def _create_type_c_defaults() -> ContractTypeDefaults:
    """
    Create defaults for TYPE_C (Causal) contracts.

    TYPE_C emphasizes N3 layer for DAG validation and causal consistency.
    Uses topological_overlay, graph_construction, veto_gate, carver_doctoral_synthesis.
    """
    return ContractTypeDefaults(
        contract_type_code=CONTRACT_TYPE_C,
        description="Causal contracts: strong N3 for DAG validation and causal graph consistency",
        epistemic_ratios=EpistemicLayerRatios(
            n1_empirical=ClosedInterval(lower=0.20, upper=0.40),
            n2_inferential=ClosedInterval(lower=0.25, upper=0.45),
            n3_audit=ClosedInterval(lower=0.25, upper=0.45),  # Strong N3
        ),
        veto_threshold=ClosedInterval(
            lower=VETO_THRESHOLD_STANDARD_MIN,
            upper=VETO_THRESHOLD_STANDARD_MAX,
        ),
        prior_strength=ClosedInterval(
            lower=PRIOR_STRENGTH_MIN,
            upper=PRIOR_STRENGTH_MAX,
        ),
        permitted_operations=frozenset(
            {
                "topological_overlay",
                "graph_construction",
                "veto_gate",
                "carver_doctoral_synthesis",
                "dag_validation",
                "causal_path_analysis",
            }
        ),
        prohibited_operations=frozenset(
            {
                "weighted_mean",
                "concat",
                "simple_average",
                "arithmetic_aggregation",
            }
        ),
    )


def _create_type_d_defaults() -> ContractTypeDefaults:
    """
    Create defaults for TYPE_D (Financial) contracts.

    TYPE_D emphasizes N2 for financial aggregation with lenient veto.
    Uses weighted_mean, concat, financial_coherence_audit.
    Note: weighted_mean IS permitted for financial data aggregation.
    """
    return ContractTypeDefaults(
        contract_type_code=CONTRACT_TYPE_D,
        description="Financial contracts: N2-dominant for aggregation with lenient veto thresholds",
        epistemic_ratios=EpistemicLayerRatios(
            n1_empirical=ClosedInterval(lower=0.15, upper=0.35),
            n2_inferential=ClosedInterval(lower=0.45, upper=0.65),  # Dominant
            n3_audit=ClosedInterval(lower=0.10, upper=0.30),  # Adjusted for sum=1.0
        ),
        veto_threshold=ClosedInterval(
            lower=VETO_THRESHOLD_LENIENT_MIN,
            upper=VETO_THRESHOLD_LENIENT_MAX,
        ),
        prior_strength=ClosedInterval(
            lower=PRIOR_STRENGTH_MIN,
            upper=PRIOR_STRENGTH_MAX,
        ),
        permitted_operations=frozenset(
            {
                "weighted_mean",
                "concat",
                "financial_coherence_audit",
                "budget_aggregation",
                "fiscal_validation",
                "arithmetic_aggregation",
            }
        ),
        prohibited_operations=frozenset(
            {
                "semantic_corroboration",
                "topological_overlay",
                "bayesian_update",
                "graph_construction",
            }
        ),
    )


def _create_type_e_defaults() -> ContractTypeDefaults:
    """
    Create defaults for TYPE_E (Logical) contracts.

    TYPE_E emphasizes N3 for contradiction detection with strict veto.
    Uses concat, weighted_mean, logical_consistency_validation.
    Note: weighted_mean IS permitted per canonical source analysis.
    """
    return ContractTypeDefaults(
        contract_type_code=CONTRACT_TYPE_E,
        description="Logical contracts: strong N3 for contradiction detection with strictest veto",
        epistemic_ratios=EpistemicLayerRatios(
            n1_empirical=ClosedInterval(lower=0.15, upper=0.35),
            n2_inferential=ClosedInterval(lower=0.30, upper=0.50),
            n3_audit=ClosedInterval(lower=0.25, upper=0.45),  # Strong N3
        ),
        veto_threshold=ClosedInterval(
            lower=VETO_THRESHOLD_STRICTEST_MIN,
            upper=VETO_THRESHOLD_STRICTEST_MAX,
        ),
        prior_strength=ClosedInterval(
            lower=PRIOR_STRENGTH_MIN,
            upper=PRIOR_STRENGTH_MAX,
        ),
        permitted_operations=frozenset(
            {
                "concat",
                "weighted_mean",  # Permitted per canonical source
                "logical_consistency_validation",
                "contradiction_detection",
                "veto_gate",
                "propositional_analysis",
            }
        ),
        prohibited_operations=frozenset(
            {
                "bayesian_update",
                "semantic_corroboration",
                "graph_construction",
                "topological_overlay",
            }
        ),
    )


def _create_subtipo_f_defaults() -> ContractTypeDefaults:
    """
    Create defaults for SUBTIPO_F (Hybrid/Fallback) contracts.

    SUBTIPO_F provides balanced defaults for hybrid or unclassified contracts.
    Uses conservative bounds appropriate for mixed-mode processing.
    """
    return ContractTypeDefaults(
        contract_type_code=CONTRACT_SUBTIPO_F,
        description="Hybrid contracts: balanced defaults for composite or unclassified contracts",
        epistemic_ratios=EpistemicLayerRatios(
            n1_empirical=ClosedInterval(lower=0.20, upper=0.40),
            n2_inferential=ClosedInterval(lower=0.30, upper=0.50),
            n3_audit=ClosedInterval(lower=0.20, upper=0.40),
        ),
        veto_threshold=ClosedInterval(
            lower=VETO_THRESHOLD_STANDARD_MIN,
            upper=VETO_THRESHOLD_STANDARD_MAX,
        ),
        prior_strength=ClosedInterval(
            lower=PRIOR_STRENGTH_MIN,
            upper=PRIOR_STRENGTH_MAX,
        ),
        permitted_operations=frozenset(
            {
                "concat",
                "veto_gate",
                "weighted_mean",
            }
        ),
        prohibited_operations=frozenset(),  # No prohibitions for fallback type
    )


# =============================================================================
# FACTORY REGISTRY
# =============================================================================

# Mapping from contract type code to factory function
_TYPE_FACTORY_REGISTRY: Final[Mapping[str, type[ContractTypeDefaults] | object]] = {
    CONTRACT_TYPE_A: _create_type_a_defaults,
    CONTRACT_TYPE_B: _create_type_b_defaults,
    CONTRACT_TYPE_C: _create_type_c_defaults,
    CONTRACT_TYPE_D: _create_type_d_defaults,
    CONTRACT_TYPE_E: _create_type_e_defaults,
    CONTRACT_SUBTIPO_F: _create_subtipo_f_defaults,
}


# =============================================================================
# PUBLIC API
# =============================================================================


@lru_cache(maxsize=8)  # 6 types + buffer for potential future types
def get_type_defaults(contract_type_code: str) -> ContractTypeDefaults:
    """
    Load calibration defaults for a contract type.

    This function implements the Flyweight pattern:  each contract type's
    defaults are computed once and cached for the lifetime of the process.
    Subsequent calls return the identical cached instance.

    The function first validates that the canonical source file exists
    and contains the requested contract type, then constructs the defaults
    using the appropriate factory function.

    Args:
        contract_type_code:  Canonical identifier (e.g., "TYPE_A", "TYPE_B").

    Returns:
        ContractTypeDefaults instance with all calibration bounds.

    Raises:
        CanonicalSourceError: If contratos_clasificados.json is missing or invalid.
        UnknownContractTypeError: If contract_type_code is not recognized.

    Example:
        >>> defaults = get_type_defaults("TYPE_A")
        >>> defaults. get_default_veto_threshold()
        0.05
        >>> defaults.is_operation_prohibited("weighted_mean")
        True
    """
    # Validate canonical source exists (INV-DEF-004)
    _validate_canonical_source_exists()

    # Validate contract type is in canonical source
    _validate_contract_type_in_source(contract_type_code)

    # Get factory function
    factory = _TYPE_FACTORY_REGISTRY.get(contract_type_code)
    if factory is None:
        raise UnknownContractTypeError(contract_type_code, VALID_CONTRACT_TYPES)

    # Construct and return defaults
    if callable(factory):
        return factory()  # type: ignore[no-any-return]
    return factory  # type: ignore[no-any-return]


def _validate_canonical_source_exists() -> None:
    """
    Validate that the canonical contracts file exists.

    Raises:
        CanonicalSourceError: If file is missing.
    """
    if not _CONTRATOS_CLASIFICADOS_PATH.exists():
        raise CanonicalSourceError(
            f"Canonical contracts file not found at {_CONTRATOS_CLASIFICADOS_PATH}.  "
            f"This file is required for calibration defaults.  "
            f"Ensure the repository is complete and the file has not been moved."
        )


def _validate_contract_type_in_source(contract_type_code: str) -> None:
    """
    Validate that the contract type exists in the canonical source.

    Args:
        contract_type_code: Contract type to validate.

    Raises:
        CanonicalSourceError: If file cannot be read or parsed.
        UnknownContractTypeError:  If type not in canonical source.
    """
    try:
        with open(_CONTRATOS_CLASIFICADOS_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise CanonicalSourceError(f"Canonical contracts file is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise CanonicalSourceError(f"Cannot read canonical contracts file: {exc}") from exc

    # Extract valid types from canonical source
    taxonomies = data.get("taxonomias_aplicadas", {})
    source_types = taxonomies.get("tipos_contrato", [])

    if not source_types:
        # Fall back to our known types if not in file
        source_types = list(VALID_CONTRACT_TYPES)

    if contract_type_code not in source_types and contract_type_code not in VALID_CONTRACT_TYPES:
        raise UnknownContractTypeError(
            contract_type_code,
            frozenset(source_types) | VALID_CONTRACT_TYPES,
        )


def is_operation_prohibited(contract_type_code: str, operation: str) -> bool:
    """
    Check if an operation is prohibited for a contract type.

    Convenience function that retrieves type defaults and checks prohibition.

    Args:
        contract_type_code: Canonical contract type identifier.
        operation: Operation name to check.

    Returns:
        True if operation is prohibited for the contract type.

    Raises:
        CanonicalSourceError: If canonical source is unavailable.
        UnknownContractTypeError: If contract type is not recognized.

    Example:
        >>> is_operation_prohibited("TYPE_A", "weighted_mean")
        True
        >>> is_operation_prohibited("TYPE_D", "weighted_mean")
        False
    """
    defaults = get_type_defaults(contract_type_code)
    return defaults.is_operation_prohibited(operation)


def is_operation_permitted(contract_type_code: str, operation: str) -> bool:
    """
    Check if an operation is permitted for a contract type.

    Convenience function that retrieves type defaults and checks permission.

    Args:
        contract_type_code: Canonical contract type identifier.
        operation: Operation name to check.

    Returns:
        True if operation is in the permitted set for the contract type.

    Raises:
        CanonicalSourceError: If canonical source is unavailable.
        UnknownContractTypeError: If contract type is not recognized.

    Example:
        >>> is_operation_permitted("TYPE_A", "semantic_corroboration")
        True
        >>> is_operation_permitted("TYPE_A", "weighted_mean")
        False
    """
    defaults = get_type_defaults(contract_type_code)
    return defaults.is_operation_permitted(operation)


def get_all_type_defaults() -> dict[str, ContractTypeDefaults]:
    """
    Load calibration defaults for all known contract types.

    Returns:
        Dictionary mapping contract type codes to their defaults.

    Raises:
        CanonicalSourceError: If canonical source is unavailable.
    """
    return {type_code: get_type_defaults(type_code) for type_code in VALID_CONTRACT_TYPES}


def clear_defaults_cache() -> None:
    """
    Clear the cached type defaults.

    This function should only be called in testing scenarios or when
    the canonical source file has been updated and defaults need to
    be recomputed.
    """
    get_type_defaults.cache_clear()


# =============================================================================
# PROHIBITED OPERATIONS CONSTANT (BACKWARD COMPATIBILITY)
# =============================================================================

# This constant maintains backward compatibility with code that directly
# accesses PROHIBITED_OPERATIONS.  New code should use get_type_defaults().

PROHIBITED_OPERATIONS: Final[dict[str, frozenset[str]]] = {
    CONTRACT_TYPE_A: frozenset(
        {
            "weighted_mean",
            "simple_average",
            "bayesian_update",
            "arithmetic_aggregation",
        }
    ),
    CONTRACT_TYPE_B: frozenset(
        {
            "weighted_mean",
            "simple_average",
            "semantic_corroboration",
            "arithmetic_aggregation",
        }
    ),
    CONTRACT_TYPE_C: frozenset(
        {
            "weighted_mean",
            "concat",
            "simple_average",
            "arithmetic_aggregation",
        }
    ),
    CONTRACT_TYPE_D: frozenset(
        {
            "semantic_corroboration",
            "topological_overlay",
            "bayesian_update",
            "graph_construction",
        }
    ),
    CONTRACT_TYPE_E: frozenset(
        {
            "bayesian_update",
            "semantic_corroboration",
            "graph_construction",
            "topological_overlay",
        }
    ),
    CONTRACT_SUBTIPO_F: frozenset(),
}


# =============================================================================
# NEW: FUSION STRATEGY HELPERS
# =============================================================================


def get_fusion_strategy(contract_type_code: str, epistemic_level: str) -> str:
    """
    Get the canonical fusion strategy for a contract type and epistemic level.

    This function returns the fusion strategy specified in episteme_rules.md
    PARTE IV, Sección 4.3.

    Args:
        contract_type_code: Contract type (TYPE_A, TYPE_B, etc.).
        epistemic_level: Epistemic level ("N1", "N2", or "N3").

    Returns:
        Fusion strategy name (e.g., "semantic_corroboration", "bayesian_update").

    Raises:
        UnknownContractTypeError: If contract_type_code is not recognized.
        ValueError: If epistemic_level is not N1, N2, or N3.

    Example:
        >>> get_fusion_strategy("TYPE_A", "N1")
        'semantic_corroboration'
        >>> get_fusion_strategy("TYPE_B", "N2")
        'bayesian_update'
    """
    if contract_type_code not in VALID_CONTRACT_TYPES:
        raise UnknownContractTypeError(contract_type_code, VALID_CONTRACT_TYPES)

    valid_levels = {"N1", "N2", "N3"}
    if epistemic_level not in valid_levels:
        raise ValueError(
            f"epistemic_level must be one of {valid_levels}; got: '{epistemic_level}'"
        )

    return TYPE_FUSION_STRATEGIES[contract_type_code][epistemic_level]


def get_all_fusion_strategies(contract_type_code: str) -> dict[str, str]:
    """
    Get all fusion strategies for a contract type.

    Args:
        contract_type_code: Contract type (TYPE_A, TYPE_B, etc.).

    Returns:
        Dictionary mapping epistemic levels to fusion strategies.

    Raises:
        UnknownContractTypeError: If contract_type_code is not recognized.

    Example:
        >>> get_all_fusion_strategies("TYPE_A")
        {'N1': 'semantic_corroboration', 'N2': 'dempster_shafer', 'N3': 'veto_gate'}
    """
    if contract_type_code not in VALID_CONTRACT_TYPES:
        raise UnknownContractTypeError(contract_type_code, VALID_CONTRACT_TYPES)

    return dict(TYPE_FUSION_STRATEGIES[contract_type_code])


def validate_fusion_strategy_for_type(
    contract_type_code: str,
    strategy: str,
    epistemic_level: str,
) -> tuple[bool, str]:
    """
    Validate that a fusion strategy is appropriate for a contract type and level.

    This function checks:
    1. The strategy is not in prohibited_operations for the type
    2. The strategy matches the canonical strategy for the level (warning if not)

    Args:
        contract_type_code: Contract type (TYPE_A, TYPE_B, etc.).
        strategy: Fusion strategy to validate.
        epistemic_level: Epistemic level ("N1", "N2", or "N3").

    Returns:
        Tuple of (is_valid, message). If invalid, message contains error description.
        If valid but non-canonical, message contains warning.

    Example:
        >>> validate_fusion_strategy_for_type("TYPE_A", "weighted_mean", "N2")
        (False, "Strategy 'weighted_mean' is prohibited for TYPE_A")
        >>> validate_fusion_strategy_for_type("TYPE_A", "concat", "N1")
        (True, "Warning: 'concat' is not canonical for TYPE_A N1; expected 'semantic_corroboration'")
    """
    defaults = get_type_defaults(contract_type_code)

    # Check if prohibited
    if defaults.is_operation_prohibited(strategy):
        return (False, f"Strategy '{strategy}' is prohibited for {contract_type_code}")

    # Check if canonical
    canonical_strategy = get_fusion_strategy(contract_type_code, epistemic_level)
    if strategy != canonical_strategy:
        return (
            True,
            f"Warning: '{strategy}' is not canonical for {contract_type_code} {epistemic_level}; "
            f"expected '{canonical_strategy}'",
        )

    return (True, "")


# =============================================================================
# NEW: QUESTION TO CONTRACT TYPE MAPPING
# =============================================================================

# Mapping from base question IDs to contract types (from episteme_rules.md PARTE I, Sec 1.1)
QUESTION_TO_CONTRACT_TYPE: Final[dict[str, str]] = {
    # TYPE_A (Semantic): Q001, Q013
    "Q001": CONTRACT_TYPE_A,
    "Q013": CONTRACT_TYPE_A,
    # TYPE_B (Bayesian): Q002, Q005, Q007, Q011, Q017, Q018, Q020, Q023, Q024, Q025, Q027, Q029
    "Q002": CONTRACT_TYPE_B,
    "Q005": CONTRACT_TYPE_B,
    "Q007": CONTRACT_TYPE_B,
    "Q011": CONTRACT_TYPE_B,
    "Q017": CONTRACT_TYPE_B,
    "Q018": CONTRACT_TYPE_B,
    "Q020": CONTRACT_TYPE_B,
    "Q023": CONTRACT_TYPE_B,
    "Q024": CONTRACT_TYPE_B,
    "Q025": CONTRACT_TYPE_B,
    "Q027": CONTRACT_TYPE_B,
    "Q029": CONTRACT_TYPE_B,
    # TYPE_C (Causal): Q008, Q016, Q026, Q030
    "Q008": CONTRACT_TYPE_C,
    "Q016": CONTRACT_TYPE_C,
    "Q026": CONTRACT_TYPE_C,
    "Q030": CONTRACT_TYPE_C,
    # TYPE_D (Financial): Q003, Q004, Q006, Q009, Q012, Q015, Q021, Q022
    "Q003": CONTRACT_TYPE_D,
    "Q004": CONTRACT_TYPE_D,
    "Q006": CONTRACT_TYPE_D,
    "Q009": CONTRACT_TYPE_D,
    "Q012": CONTRACT_TYPE_D,
    "Q015": CONTRACT_TYPE_D,
    "Q021": CONTRACT_TYPE_D,
    "Q022": CONTRACT_TYPE_D,
    # TYPE_E (Logical): Q010, Q014, Q019, Q028
    "Q010": CONTRACT_TYPE_E,
    "Q014": CONTRACT_TYPE_E,
    "Q019": CONTRACT_TYPE_E,
    "Q028": CONTRACT_TYPE_E,
}


def get_contract_type_for_question(question_id: str) -> str:
    """
    Get the contract type for a base question ID.

    This function implements the mapping from episteme_rules.md PARTE I, Sec 1.1.
    For extended question IDs (Q031-Q300), it extracts the base question.

    Args:
        question_id: Question ID (e.g., "Q001", "Q031", "Q271").

    Returns:
        Contract type code (TYPE_A, TYPE_B, etc.).

    Raises:
        KeyError: If question ID cannot be mapped to a contract type.

    Example:
        >>> get_contract_type_for_question("Q001")
        'TYPE_A'
        >>> get_contract_type_for_question("Q031")  # Maps to base Q001
        'TYPE_A'
        >>> get_contract_type_for_question("Q045")  # Maps to base Q015
        'TYPE_D'
    """
    # Extract numeric part
    if not question_id.startswith("Q"):
        raise KeyError(f"Invalid question ID format: '{question_id}'")

    try:
        q_num = int(question_id[1:])
    except ValueError as exc:
        raise KeyError(f"Invalid question ID format: '{question_id}'") from exc

    # Map extended questions (Q031-Q300) to base questions (Q001-Q030)
    # Q031-Q060 → PA02 (same base questions)
    # Q061-Q090 → PA03, etc.
    base_q_num = ((q_num - 1) % 30) + 1
    base_question_id = f"Q{base_q_num:03d}"

    if base_question_id not in QUESTION_TO_CONTRACT_TYPE:
        raise KeyError(
            f"No contract type mapping for question '{question_id}' "
            f"(base: '{base_question_id}')"
        )

    return QUESTION_TO_CONTRACT_TYPE[base_question_id]


# =============================================================================
# CANONICAL METHOD CLASSIFICATION (from episteme_rules.md)
# =============================================================================
# FUENTE CANÓNICA: episteme_rules.md - TAXONOMÍA EPISTEMOLÓGICA DE MÉTODOS
#
# IMPORTANTE: Esta clasificación es INMUTABLE y deriva directamente de la
# taxonomía epistemológica. NO usar heurísticas basadas en nombres de métodos.
#
# Niveles:
#   N0-INFRA: Infraestructura sin juicio analítico
#   N1-EMP (Empirical): Extracción de hechos brutos sin juicio
#   N2-INF (Inferential): Transformación en conocimiento probabilístico
#   N3-AUD (Audit): Validación, refutación, veto gates
#   N4-META: Meta-análisis del proceso analítico
# =============================================================================

# -----------------------------------------------------------------------------
# N0: Infraestructura Metodológica
# -----------------------------------------------------------------------------
N0_INFRASTRUCTURE_METHODS: Final[frozenset[str]] = frozenset({
    "ConfigLoader.load",
    "ConfigLoader.validate",
    "PDETMunicipalPlanAnalyzer._get_spanish_stopwords",
    "PDETMunicipalPlanAnalyzer._deduplicate_tables",
    "PDETMunicipalPlanAnalyzer._indicator_to_dict",
    "AdaptivePriorCalculator.generate_traceability_record",
})

# -----------------------------------------------------------------------------
# N1: Base Empírica (Detection & Extraction)
# -----------------------------------------------------------------------------
# CORRECCIÓN CRÍTICA: TextMiningEngine.diagnose_critical_links es N1, NO N2
# Justificación: EXTRAE vínculos críticos, no los EVALÚA probabilísticamente
N1_CANONICAL_METHODS: Final[frozenset[str]] = frozenset({
    # TextMiningEngine - NIVEL 1 (minería textual, NO inferencial)
    "TextMiningEngine.diagnose_critical_links",
    "TextMiningEngine._analyze_link_text",
    
    # IndustrialPolicyProcessor - N1 extraction methods
    "IndustrialPolicyProcessor._extract_point_evidence",
    "IndustrialPolicyProcessor._extract_metadata",
    
    # CausalExtractor - N1 (extracción de metas, no inferencia causal)
    "CausalExtractor._extract_goals",
    "CausalExtractor._parse_goal_context",
    "CausalExtractor._calculate_language_specificity",
    
    # PDETMunicipalPlanAnalyzer - N1 (extracción estructurada)
    "PDETMunicipalPlanAnalyzer._extract_financial_amounts",
    "PDETMunicipalPlanAnalyzer._extract_from_budget_table",
    "PDETMunicipalPlanAnalyzer._extract_entities_syntax",
    
    # SemanticProcessor - N1 (preprocesamiento semántico)
    # CORRECCIÓN: embed_single es N1 porque genera representación, no inferencia
    "SemanticProcessor.chunk_text",
    "SemanticProcessor.embed_single",
    "SemanticProcessor._detect_pdm_structure",
    
    # SemanticAnalyzer - N1 (análisis temático base)
    "SemanticAnalyzer.analyze_coherence",
    "SemanticAnalyzer.extract_themes",
    
    # PolicyContradictionDetector - N1 extraction only
    "PolicyContradictionDetector._extract_quantitative_claims",
    "PolicyContradictionDetector._parse_number",
})

# -----------------------------------------------------------------------------
# N2: Procesamiento Inferencial (Computation & Synthesis)
# -----------------------------------------------------------------------------
N2_CANONICAL_METHODS: Final[frozenset[str]] = frozenset({
    # BayesianNumericalAnalyzer - N2 (comparación bayesiana)
    "BayesianNumericalAnalyzer.evaluate_policy_metric",
    "BayesianNumericalAnalyzer.compare_policies",
    
    # AdaptivePriorCalculator - N2 (priors adaptativos)
    "AdaptivePriorCalculator.calculate_likelihood_adaptativo",
    "AdaptivePriorCalculator._adjust_domain_weights",
    "AdaptivePriorCalculator.sensitivity_analysis",
    
    # HierarchicalGenerativeModel - N2 (modelos jerárquicos)
    "HierarchicalGenerativeModel.verify_conditional_independence",
    "HierarchicalGenerativeModel._generate_independence_tests",
    "HierarchicalGenerativeModel._calculate_r_hat",
    "HierarchicalGenerativeModel._calculate_ess",
    
    # BayesFactorTable - N2 (cuantificación de evidencia)
    "BayesFactorTable.get_bayes_factor",
    
    # BayesianMechanismInference - N2 (inferencia mecanística)
    "BayesianMechanismInference.aggregate_confidence",
    "BayesianMechanismInference._test_sufficiency",
    "BayesianMechanismInference._test_necessity",
    "BayesianMechanismInference._calculate_coherence_factor",
    
    # TeoriaCambio - N2 (reconstrucción de teorías de cambio)
    "TeoriaCambio._encontrar_caminos_completos",
    "TeoriaCambio.validacion_completa",
    "TeoriaCambio._extraer_categorias",
    "TeoriaCambio._generar_sugerencias",
    
    # IndustrialPolicyProcessor - N2 (process transforma, no extrae)
    "IndustrialPolicyProcessor.process",
    "IndustrialPolicyProcessor._match_patterns_in_sentences",
    "IndustrialPolicyProcessor._analyze_causal_dimensions",
})

# -----------------------------------------------------------------------------
# N3: Auditoría y Robustez (Refutation & Control)
# -----------------------------------------------------------------------------
N3_CANONICAL_METHODS: Final[frozenset[str]] = frozenset({
    # PolicyContradictionDetector - N3 (validación, no extracción)
    "PolicyContradictionDetector._detect_logical_incompatibilities",
    "PolicyContradictionDetector._calculate_coherence_metrics",
    "PolicyContradictionDetector._statistical_significance_test",
    
    # FinancialAuditor - N3 (validación de viabilidad)
    "FinancialAuditor._detect_allocation_gaps",
    "FinancialAuditor._calculate_sufficiency",
    
    # IndustrialGradeValidator - N3 (validación industrial rigurosa)
    "IndustrialGradeValidator.execute_suite",
    "IndustrialGradeValidator.validate_connection_matrix",
    "IndustrialGradeValidator.validate_engine_readiness",
    
    # AdvancedDAGValidator - N3 (validación de grafos causales)
    "AdvancedDAGValidator._is_acyclic",
    "AdvancedDAGValidator.calculate_acyclicity_pvalue",
    "AdvancedDAGValidator._calculate_statistical_power",
    "AdvancedDAGValidator._calculate_bayesian_posterior",
    "AdvancedDAGValidator._calculate_confidence_interval",
    "AdvancedDAGValidator._perform_sensitivity_analysis",
    
    # BayesianCounterfactualAuditor - N3 (auditoría contrafactual)
    "BayesianCounterfactualAuditor.construct_scm",
    "BayesianCounterfactualAuditor.counterfactual_query",
    
    # OperationalizationAuditor - N3 (validación de secuencias)
    "OperationalizationAuditor.audit_sequence_logic",
    "OperationalizationAuditor._audit_systemic_risk",
    
    # TemporalLogicVerifier - N3 (verificación temporal)
    "TemporalLogicVerifier.verify_temporal_consistency",
})

# -----------------------------------------------------------------------------
# N4: Meta-Análisis (Identification of Failures)
# -----------------------------------------------------------------------------
N4_CANONICAL_METHODS: Final[frozenset[str]] = frozenset({
    "CausalInferenceSetup.identify_failure_points",
    "CausalInferenceSetup._get_dynamics_pattern",
    "PerformanceAnalyzer.analyze_performance",
    "PerformanceAnalyzer.loss_functions",
})

# =============================================================================
# METHOD CLASSIFICATION LOOKUP
# =============================================================================

# Unified lookup: method_name -> (level_code, decorator_type, output_type)
METHOD_EPISTEMIC_CLASSIFICATION: Final[dict[str, tuple[str, str | None, str]]] = {
    **{m: ("N0-INFRA", None, "INFRASTRUCTURE") for m in N0_INFRASTRUCTURE_METHODS},
    **{m: ("N1-EMP", "fact_aware", "FACT") for m in N1_CANONICAL_METHODS},
    **{m: ("N2-INF", "parameter_aware", "PARAMETER") for m in N2_CANONICAL_METHODS},
    **{m: ("N3-AUD", "constraint_aware", "CONSTRAINT") for m in N3_CANONICAL_METHODS},
    **{m: ("N4-META", "meta_aware", "META_ANALYSIS") for m in N4_CANONICAL_METHODS},
}

# Decorator aliases
DECORATOR_TO_LEVEL: Final[dict[str, str]] = {
    "fact_aware": "N1-EMP",
    "parameter_aware": "N2-INF",
    "constraint_aware": "N3-AUD",
    "meta_aware": "N4-META",
    "chunk_size_aware": "N1-EMP",
    "prior_aware": "N2-INF",
    "veto_aware": "N3-AUD",
}

LEVEL_TO_OUTPUT_TYPE: Final[dict[str, str]] = {
    "N0-INFRA": "INFRASTRUCTURE",
    "N1-EMP": "FACT",
    "N2-INF": "PARAMETER",
    "N3-AUD": "CONSTRAINT",
    "N4-META": "META_ANALYSIS",
}


def get_method_epistemic_level(class_name: str, method_name: str) -> str | None:
    """
    Get the canonical epistemic level for a method.
    
    Args:
        class_name: Name of the class containing the method.
        method_name: Name of the method.
    
    Returns:
        Epistemic level code (N0-INFRA, N1-EMP, N2-INF, N3-AUD, N4-META),
        or None if method is not in the canonical classification.
    
    Example:
        >>> get_method_epistemic_level("TextMiningEngine", "diagnose_critical_links")
        'N1-EMP'  # NOT N2-INF despite "diagnose" sounding inferential
    """
    full_name = f"{class_name}.{method_name}"
    classification = METHOD_EPISTEMIC_CLASSIFICATION.get(full_name)
    return classification[0] if classification else None


def get_method_decorator_type(class_name: str, method_name: str) -> str | None:
    """
    Get the appropriate decorator type for a method.
    
    Args:
        class_name: Name of the class containing the method.
        method_name: Name of the method.
    
    Returns:
        Decorator type (fact_aware, parameter_aware, constraint_aware, meta_aware),
        or None if method requires no calibration (N0-INFRA).
    """
    full_name = f"{class_name}.{method_name}"
    classification = METHOD_EPISTEMIC_CLASSIFICATION.get(full_name)
    return classification[1] if classification else None


def get_method_output_type(class_name: str, method_name: str) -> str | None:
    """Get the expected output type for a method."""
    full_name = f"{class_name}.{method_name}"
    classification = METHOD_EPISTEMIC_CLASSIFICATION.get(full_name)
    return classification[2] if classification else None


def validate_method_classification(
    class_name: str,
    method_name: str,
    claimed_level: str,
) -> tuple[bool, str]:
    """
    Validate that a method's claimed epistemic level matches canonical classification.
    
    Args:
        class_name: Name of the class containing the method.
        method_name: Name of the method.
        claimed_level: The epistemic level claimed for the method.
    
    Returns:
        Tuple of (is_valid, error_message). error_message is empty if valid.
    
    Example:
        >>> validate_method_classification("TextMiningEngine", "diagnose_critical_links", "N2-INF")
        (False, "Method 'TextMiningEngine.diagnose_critical_links' is canonically N1-EMP, not N2-INF")
    """
    canonical_level = get_method_epistemic_level(class_name, method_name)
    full_name = f"{class_name}.{method_name}"
    
    if canonical_level is None:
        return (True, f"Warning: Method '{full_name}' not in canonical classification")
    
    if canonical_level != claimed_level:
        return (
            False,
            f"Method '{full_name}' is canonically {canonical_level}, not {claimed_level}. "
            f"See episteme_rules.md for authoritative classification."
        )
    
    return (True, "")


def get_methods_by_level(level: str) -> frozenset[str]:
    """
    Get all methods classified at a specific epistemic level.
    
    Args:
        level: Epistemic level code (N0-INFRA, N1-EMP, N2-INF, N3-AUD, N4-META).
    
    Returns:
        Frozenset of fully-qualified method names (ClassName.method_name).
    """
    level_to_set: dict[str, frozenset[str]] = {
        "N0-INFRA": N0_INFRASTRUCTURE_METHODS,
        "N1-EMP": N1_CANONICAL_METHODS,
        "N2-INF": N2_CANONICAL_METHODS,
        "N3-AUD": N3_CANONICAL_METHODS,
        "N4-META": N4_CANONICAL_METHODS,
    }
    return level_to_set.get(level, frozenset())


# =============================================================================
# CALIBRATION BINDING SCHEMA (PASO 1 - from episteme_rules.md)
# =============================================================================

CALIBRATION_BINDING_SCHEMA: Final[dict[str, object]] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "properties": {
        "method_bindings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["class_name", "method_name", "level", "output_type", "fusion_behavior", "decorator"],
                "properties": {
                    "class_name": {"type": "string"},
                    "method_name": {"type": "string"},
                    "level": {
                        "type": "string",
                        "enum": ["N0-INFRA", "N1-EMP", "N2-INF", "N3-AUD", "N4-META"],
                    },
                    "output_type": {
                        "type": "string",
                        "enum": ["INFRASTRUCTURE", "FACT", "PARAMETER", "CONSTRAINT", "NARRATIVE", "META_ANALYSIS"],
                    },
                    "fusion_behavior": {
                        "type": "string",
                        "enum": ["none", "additive", "multiplicative", "gate", "terminal"],
                    },
                    "decorator": {
                        "type": "string",
                        "enum": ["@fact_aware", "@parameter_aware", "@constraint_aware", "@fully_calibrated"],
                    },
                    "veto_conditions": {
                        "type": "object",
                        "description": "Solo para N3-AUD con fusion_behavior=gate",
                    },
                },
            },
        },
    },
}

LEVEL_TO_FUSION_BEHAVIOR: Final[dict[str, str]] = {
    "N0-INFRA": "none",
    "N1-EMP": "additive",
    "N2-INF": "multiplicative",
    "N3-AUD": "gate",
    "N4-META": "terminal",
}

LEVEL_TO_DECORATOR: Final[dict[str, str]] = {
    "N0-INFRA": "@fact_aware",
    "N1-EMP": "@fact_aware",
    "N2-INF": "@parameter_aware",
    "N3-AUD": "@constraint_aware",
    "N4-META": "@fully_calibrated",
}

FUSION_BEHAVIOR_SYMBOLS: Final[dict[str, str]] = {
    "none": "∅",
    "additive": "⊕",
    "multiplicative": "⊗",
    "gate": "⊘",
    "terminal": "⊙",
}


def create_method_binding(
    class_name: str,
    method_name: str,
    level: str | None = None,
    output_type: str | None = None,
    fusion_behavior: str | None = None,
    decorator: str | None = None,
    veto_conditions: dict[str, object] | None = None,
) -> dict[str, object]:
    """Create method binding conforming to CALIBRATION_BINDING_SCHEMA."""
    if level is None:
        level = get_method_epistemic_level(class_name, method_name)
        if level is None:
            raise ValueError(f"Method '{class_name}.{method_name}' not in canonical classification.")
    
    if output_type is None:
        output_type = LEVEL_TO_OUTPUT_TYPE.get(level, "FACT")
    if fusion_behavior is None:
        fusion_behavior = LEVEL_TO_FUSION_BEHAVIOR.get(level, "additive")
    if decorator is None:
        decorator = LEVEL_TO_DECORATOR.get(level, "@fact_aware")
    
    if level == "N3-AUD" and fusion_behavior == "gate" and veto_conditions is None:
        raise ValueError(f"N3-AUD method '{class_name}.{method_name}' with gate behavior MUST have veto_conditions.")
    
    binding: dict[str, object] = {
        "class_name": class_name,
        "method_name": method_name,
        "level": level,
        "output_type": output_type,
        "fusion_behavior": fusion_behavior,
        "decorator": decorator,
    }
    if veto_conditions:
        binding["veto_conditions"] = veto_conditions
    return binding


def validate_method_binding(binding: dict[str, object]) -> tuple[bool, list[str]]:
    """Validate method binding against schema."""
    errors: list[str] = []
    required = ["class_name", "method_name", "level", "output_type", "fusion_behavior", "decorator"]
    for field in required:
        if field not in binding:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return (False, errors)
    
    # Validate canonical classification match
    canonical = get_method_epistemic_level(str(binding["class_name"]), str(binding["method_name"]))
    if canonical and canonical != binding["level"]:
        errors.append(f"Level mismatch: canonical={canonical}, binding={binding['level']}")
    
    # Validate N3-AUD veto_conditions
    if binding["level"] == "N3-AUD" and binding["fusion_behavior"] == "gate":
        if "veto_conditions" not in binding:
            errors.append("N3-AUD with gate behavior MUST have veto_conditions")
    
    return (len(errors) == 0, errors)


# =============================================================================
# MODULE EXPORTS (UPDATED con Fase 3)
# =============================================================================

__all__ = [
    # Constants
    "VALID_CONTRACT_TYPES",
    "CONTRACT_TYPE_A",
    "CONTRACT_TYPE_B",
    "CONTRACT_TYPE_C",
    "CONTRACT_TYPE_D",
    "CONTRACT_TYPE_E",
    "CONTRACT_SUBTIPO_F",
    "PRIOR_STRENGTH_MIN",
    "PRIOR_STRENGTH_MAX",
    "PRIOR_STRENGTH_DEFAULT",
    "PRIOR_STRENGTH_BAYESIAN",
    "VETO_THRESHOLD_STRICTEST_MIN",
    "VETO_THRESHOLD_STRICTEST_MAX",
    "VETO_THRESHOLD_STRICTEST_DEFAULT",
    "VETO_THRESHOLD_STANDARD_MIN",
    "VETO_THRESHOLD_STANDARD_MAX",
    "VETO_THRESHOLD_STANDARD_DEFAULT",
    "VETO_THRESHOLD_LENIENT_MIN",
    "VETO_THRESHOLD_LENIENT_MAX",
    "VETO_THRESHOLD_LENIENT_DEFAULT",
    "RATIO_SUM_TOLERANCE",
    "PROHIBITED_OPERATIONS",
    # Fusion strategy constants
    "FUSION_STRATEGY_SEMANTIC_CORROBORATION",
    "FUSION_STRATEGY_BAYESIAN_UPDATE",
    "FUSION_STRATEGY_TOPOLOGICAL_OVERLAY",
    "FUSION_STRATEGY_WEIGHTED_MEAN",
    "FUSION_STRATEGY_VETO_GATE",
    "FUSION_STRATEGY_CONCAT",
    "FUSION_STRATEGY_DEMPSTER_SHAFER",
    "FUSION_STRATEGY_GRAPH_CONSTRUCTION",
    "FUSION_STRATEGY_FINANCIAL_COHERENCE",
    "FUSION_STRATEGY_LOGICAL_VALIDATION",
    "FUSION_STRATEGY_CARVER_SYNTHESIS",
    "TYPE_FUSION_STRATEGIES",
    # Epistemic ratio constants
    "N1_RATIO_TYPE_A",
    "N2_RATIO_TYPE_A",
    "N3_RATIO_TYPE_A",
    "N1_RATIO_TYPE_B",
    "N2_RATIO_TYPE_B",
    "N3_RATIO_TYPE_B",
    "N1_RATIO_TYPE_C",
    "N2_RATIO_TYPE_C",
    "N3_RATIO_TYPE_C",
    "N1_RATIO_TYPE_D",
    "N2_RATIO_TYPE_D",
    "N3_RATIO_TYPE_D",
    "N1_RATIO_TYPE_E",
    "N2_RATIO_TYPE_E",
    "N3_RATIO_TYPE_E",
    "N1_RATIO_SUBTIPO_F",
    "N2_RATIO_SUBTIPO_F",
    "N3_RATIO_SUBTIPO_F",
    # Question mapping
    "QUESTION_TO_CONTRACT_TYPE",
    # Exceptions
    "CalibrationDefaultsError",
    "CanonicalSourceError",
    "UnknownContractTypeError",
    "ConfigurationError",
    # Data structures
    "EpistemicLayerRatios",
    "ContractTypeDefaults",
    # Public API
    "get_type_defaults",
    "get_all_type_defaults",
    "is_operation_prohibited",
    "is_operation_permitted",
    "clear_defaults_cache",
    # Fusion strategy helpers
    "get_fusion_strategy",
    "get_all_fusion_strategies",
    "validate_fusion_strategy_for_type",
    # Question mapping helpers
    "get_contract_type_for_question",
    # Canonical method classification
    "N0_INFRASTRUCTURE_METHODS",
    "N1_CANONICAL_METHODS",
    "N2_CANONICAL_METHODS",
    "N3_CANONICAL_METHODS",
    "N4_CANONICAL_METHODS",
    "METHOD_EPISTEMIC_CLASSIFICATION",
    "DECORATOR_TO_LEVEL",
    "LEVEL_TO_OUTPUT_TYPE",
    # Method classification helpers
    "get_method_epistemic_level",
    "get_method_decorator_type",
    "get_method_output_type",
    "validate_method_classification",
    "get_methods_by_level",
    # Calibration binding schema (Fase 3)
    "CALIBRATION_BINDING_SCHEMA",
    "LEVEL_TO_FUSION_BEHAVIOR",
    "LEVEL_TO_DECORATOR",
    "FUSION_BEHAVIOR_SYMBOLS",
    "create_method_binding",
    "validate_method_binding",
]
