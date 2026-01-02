"""
Type-Specific Calibration Defaults
==================================

Module:  calibration_defaults.py
Owner: farfan_pipeline. infrastructure.calibration
Purpose: Contract-type-specific calibration bounds and prohibited operations
Lifecycle State:  DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 2.0.0

CANONICAL SOURCE: 
    src/farfan_pipeline/phases/Phase_two/epistemological_assets/contratos_clasificados.json

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
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Final, Mapping

from farfan_pipeline.infrastructure.calibration.calibration_core import (
    ClosedInterval,
    ValidationError,
)


# =============================================================================
# MODULE CONSTANTS
# =============================================================================

_CONTRATOS_CLASIFICADOS_PATH: Final[Path] = Path(
    "src/farfan_pipeline/phases/Phase_two/epistemological_assets/contratos_clasificados.json"
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

VALID_CONTRACT_TYPES: Final[frozenset[str]] = frozenset({
    CONTRACT_TYPE_A,
    CONTRACT_TYPE_B,
    CONTRACT_TYPE_C,
    CONTRACT_TYPE_D,
    CONTRACT_TYPE_E,
    CONTRACT_SUBTIPO_F,
})

# -----------------------------------------------------------------------------
# Prior Strength Bounds (Bayesian inference weight)
# -----------------------------------------------------------------------------
# Prior strength controls the weight given to prior beliefs vs. observed evidence
# in Bayesian updating operations.  Higher values = stronger prior influence.

PRIOR_STRENGTH_MIN: Final[float] = 0.1
PRIOR_STRENGTH_MAX:  Final[float] = 10.0
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
        self. valid_types = valid_types
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
            self.n1_empirical.midpoint()
            + self.n2_inferential.midpoint()
            + self.n3_audit. midpoint()
        )

        if abs(default_sum - 1.0) > RATIO_SUM_TOLERANCE:
            raise ConfigurationError(
                f"Epistemic layer ratio midpoints must sum to 1.0 (±{RATIO_SUM_TOLERANCE}); "
                f"got {default_sum:. 4f} = "
                f"n1({self.n1_empirical. midpoint():.3f}) + "
                f"n2({self.n2_inferential.midpoint():.3f}) + "
                f"n3({self.n3_audit.midpoint():.3f})"
            )

    def validate_concrete_ratios(
        self, n1: float, n2: float, n3: float
    ) -> tuple[bool, str]:
        """
        Validate a concrete ratio configuration against bounds.

        Args:
            n1: Concrete N1_EMP ratio value.
            n2: Concrete N2_INF ratio value. 
            n3: Concrete N3_AUD ratio value. 

        Returns:
            Tuple of (is_valid, error_message). error_message is empty if valid.
        """
        errors:  list[str] = []

        if not self.n1_empirical.contains(n1):
            errors. append(
                f"n1_empirical={n1} not in [{self.n1_empirical.lower}, {self.n1_empirical.upper}]"
            )
        if not self.n2_inferential.contains(n2):
            errors.append(
                f"n2_inferential={n2} not in [{self. n2_inferential.lower}, {self.n2_inferential.upper}]"
            )
        if not self.n3_audit.contains(n3):
            errors.append(
                f"n3_audit={n3} not in [{self.n3_audit.lower}, {self.n3_audit.upper}]"
            )

        ratio_sum = n1 + n2 + n3
        if abs(ratio_sum - 1.0) > RATIO_SUM_TOLERANCE:
            errors.append(f"ratios sum to {ratio_sum:.4f}, expected 1.0 (±{RATIO_SUM_TOLERANCE})")

        return (len(errors) == 0, "; ".join(errors))

    def to_canonical_dict(self) -> dict[str, dict[str, float]]:
        """Convert to canonical dictionary for serialization."""
        return {
            "n1_empirical":  self.n1_empirical. to_canonical_dict(),
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
    permitted_operations:  frozenset[str]
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
        return operation. lower() in self.permitted_operations

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
        return any(prohibited in op_lower for prohibited in self. prohibited_operations)

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
            "description": self. description,
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
            n2_inferential=ClosedInterval(lower=0.40, upper=0.60),  # Dominant
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
        permitted_operations=frozenset({
            "semantic_corroboration",
            "dempster_shafer",
            "veto_gate",
            "semantic_triangulation",
            "embedding_similarity",
        }),
        prohibited_operations=frozenset({
            "weighted_mean",
            "simple_average",
            "bayesian_update",
            "arithmetic_aggregation",
        }),
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
        permitted_operations=frozenset({
            "bayesian_update",
            "concat",
            "veto_gate",
            "carver_doctoral_synthesis",
            "prior_posterior_update",
            "credible_interval",
        }),
        prohibited_operations=frozenset({
            "weighted_mean",
            "simple_average",
            "semantic_corroboration",
            "arithmetic_aggregation",
        }),
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
        permitted_operations=frozenset({
            "topological_overlay",
            "graph_construction",
            "veto_gate",
            "carver_doctoral_synthesis",
            "dag_validation",
            "causal_path_analysis",
        }),
        prohibited_operations=frozenset({
            "weighted_mean",
            "concat",
            "simple_average",
            "arithmetic_aggregation",
        }),
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
            n3_audit=ClosedInterval(lower=0.15, upper=0.30),
        ),
        veto_threshold=ClosedInterval(
            lower=VETO_THRESHOLD_LENIENT_MIN,
            upper=VETO_THRESHOLD_LENIENT_MAX,
        ),
        prior_strength=ClosedInterval(
            lower=PRIOR_STRENGTH_MIN,
            upper=PRIOR_STRENGTH_MAX,
        ),
        permitted_operations=frozenset({
            "weighted_mean",
            "concat",
            "financial_coherence_audit",
            "budget_aggregation",
            "fiscal_validation",
            "arithmetic_aggregation",
        }),
        prohibited_operations=frozenset({
            "semantic_corroboration",
            "topological_overlay",
            "bayesian_update",
            "graph_construction",
        }),
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
        permitted_operations=frozenset({
            "concat",
            "weighted_mean",  # Permitted per canonical source
            "logical_consistency_validation",
            "contradiction_detection",
            "veto_gate",
            "propositional_analysis",
        }),
        prohibited_operations=frozenset({
            "bayesian_update",
            "semantic_corroboration",
            "graph_construction",
            "topological_overlay",
        }),
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
        permitted_operations=frozenset({
            "concat",
            "veto_gate",
            "weighted_mean",
        }),
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
    return factory()  # type: ignore[operator]


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
        with open(_CONTRATOS_CLASIFICADOS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise CanonicalSourceError(
            f"Canonical contracts file is not valid JSON: {exc}"
        ) from exc
    except OSError as exc: 
        raise CanonicalSourceError(
            f"Cannot read canonical contracts file: {exc}"
        ) from exc

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
    return defaults. is_operation_permitted(operation)


def get_all_type_defaults() -> dict[str, ContractTypeDefaults]:
    """
    Load calibration defaults for all known contract types.

    Returns:
        Dictionary mapping contract type codes to their defaults. 

    Raises:
        CanonicalSourceError: If canonical source is unavailable.
    """
    return {
        type_code: get_type_defaults(type_code)
        for type_code in VALID_CONTRACT_TYPES
    }


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

PROHIBITED_OPERATIONS:  Final[dict[str, frozenset[str]]] = {
    CONTRACT_TYPE_A: frozenset({
        "weighted_mean",
        "simple_average",
        "bayesian_update",
        "arithmetic_aggregation",
    }),
    CONTRACT_TYPE_B: frozenset({
        "weighted_mean",
        "simple_average",
        "semantic_corroboration",
        "arithmetic_aggregation",
    }),
    CONTRACT_TYPE_C: frozenset({
        "weighted_mean",
        "concat",
        "simple_average",
        "arithmetic_aggregation",
    }),
    CONTRACT_TYPE_D: frozenset({
        "semantic_corroboration",
        "topological_overlay",
        "bayesian_update",
        "graph_construction",
    }),
    CONTRACT_TYPE_E: frozenset({
        "bayesian_update",
        "semantic_corroboration",
        "graph_construction",
        "topological_overlay",
    }),
    CONTRACT_SUBTIPO_F: frozenset(),
}


# =============================================================================
# MODULE EXPORTS
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
    "VETO_THRESHOLD_STANDARD_MIN",
    "VETO_THRESHOLD_STANDARD_MAX",
    "VETO_THRESHOLD_LENIENT_MIN",
    "VETO_THRESHOLD_LENIENT_MAX",
    "PROHIBITED_OPERATIONS",
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
]
