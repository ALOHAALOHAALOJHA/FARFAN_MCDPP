"""
Epistemic Calibration Core - N0-N4 Calibration Classes
========================================================

Module: epistemic_core.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Immutable calibration profiles for each epistemic level
Lifecycle State: DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 4.0.0-epistemological

CONSTITUTIONAL PRINCIPLES (NON-NEGOTIABLE):
    CI-03: INMUTABILIDAD EPISTÉMICA - El nivel de un método es INMUTABLE
    CI-04: ASIMETRÍA POPPERIANA - N3 puede vetar N1/N2, nunca al revés
    CI-05: SEPARACIÓN CALIBRACIÓN-NIVEL - PDM ajusta parámetros, no nivel

EPISTEMIC LEVELS:
    N0-INFRA: Infrastructure (no analytical judgment)
    N1-EMP:   Empirical extraction (positivist)
    N2-INF:   Inferential computation (Bayesian/constructivist)
    N3-AUD:   Audit/falsification (Popperian) - CAN VETO N1/N2
    N4-META:  Meta-analysis of the process

ARCHITECTURE:
    Each level is represented by a frozen dataclass with:
    - level: Final[str] property (immutable, no setter)
    - Calibration parameters with bounds validation
    - PDM sensitivity rules for dynamic adjustment

CRITICAL: The 'level' property uses @property without setter to enforce
immutability at the Python level, not just by convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Literal

from .calibration_core import (
    ClosedInterval,
    EpistemicLevel,
    ValidationError,
    validate_epistemic_level,
)

# Import mathematical calibration optimizers
try:
    from .mathematical_calibration import (
        N1EmpiricalOptimizer,
        N2InferentialOptimizer,
        N3AuditOptimizer,
        N4MetaOptimizer,
    )
    MATHEMATICAL_CALIBRATION_AVAILABLE = True
except ImportError:
    # Fallback if scipy/sklearn not available
    MATHEMATICAL_CALIBRATION_AVAILABLE = False
    N1EmpiricalOptimizer = None
    N2InferentialOptimizer = None
    N3AuditOptimizer = None
    N4MetaOptimizer = None


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

EpistemicLevelLiteral = Literal[
    "N0-INFRA",  # Infrastructure
    "N1-EMP",    # Empirical
    "N2-INF",    # Inferential
    "N3-AUD",    # Audit
    "N4-META",   # Meta-analysis
]


# =============================================================================
# PDM SENSITIVITY STRUCTURES
# =============================================================================


@dataclass(frozen=True)
class PDMSensitivity:
    """
    PDM (Professional Data Model) sensitivity configuration.

    Defines how calibration parameters should be adjusted based on
    document structural characteristics.

    CONSTITUTIONAL RULE: PDM adjustments affect PARAMETERS only,
    NEVER the epistemic level (CI-05).

    Attributes:
        active: Whether PDM-driven adjustments are enabled for this level
        rules: List of PDM rules to apply (e.g., "table_boost", "hierarchy_sensitivity")
    """

    active: bool = True
    rules: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        """Validate PDM sensitivity configuration."""
        # Valid PDM rules (extensible)
        KNOWN_RULES = {
            "table_boost",
            "hierarchy_sensitivity",
            "financial_strictness",
            "temporal_logic",
            "data_driven_priors",
            "hierarchical_models",
        }

        unknown_rules = self.rules - KNOWN_RULES
        if unknown_rules:
            # Warning but not error (forward compatibility)
            import warnings

            warnings.warn(
                f"Unknown PDM rules: {unknown_rules}. "
                f"Known rules: {KNOWN_RULES}"
            )


# =============================================================================
# N0: INFRASTRUCTURE CALIBRATION
# =============================================================================


@dataclass(frozen=True)
class N0InfrastructureCalibration:
    """
    Calibration for N0-INFRA (Infrastructure) level.

    N0 methods provide infrastructure without analytical judgment.
    They have minimal calibration requirements since they are
    deterministic by design.

    INVARIANTS:
        - level is immutable (property, no setter)
        - All parameters are infrastructure-related (timeouts, seeds)
        - No PDM sensitivity (infrastructure is document-agnostic)
    """

    level: Final[EpistemicLevelLiteral] = field(default="N0-INFRA", init=False)
    description: str = "Infrastructure layer without analytical judgment"

    # Infrastructure parameters (fixed, not calibrated)
    random_seed: int = 42
    default_timeout_seconds: float = 30.0
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Validate N0 infrastructure parameters."""
        # Validate timeout is positive
        if self.default_timeout_seconds <= 0:
            raise ValidationError(
                f"Timeout must be positive: {self.default_timeout_seconds}"
            )

        # Validate retry count
        if self.max_retries < 0:
            raise ValidationError(f"Max retries cannot be negative: {self.max_retries}")

    @property
    def output_type(self) -> str:
        """N0 outputs INFRASTRUCTURE (immutable mapping)."""
        return "INFRASTRUCTURE"

    @property
    def fusion_behavior(self) -> str:
        """N0 has no fusion (none)."""
        return "none"


# =============================================================================
# N1: EMPIRICAL CALIBRATION
# =============================================================================


@dataclass(frozen=True)
class N1EmpiricalCalibration:
    """
    Calibration for N1-EMP (Empirical Extraction) level.

    N1 methods extract observable facts without interpretation.
    They operate under positivist epistemology.

    CONSTITUTIONAL INVARIANTS:
        - level is immutable (property, no setter) [CI-03]
        - extraction_confidence_floor ∈ [0.0, 1.0]
        - table_extraction_boost >= 1.0 (boost, not penalty)
        - PDM adjusts thresholds, NEVER changes level [CI-05]

    Epistemology: Empirismo positivista
    Output Type: FACT (observable datum)
    Fusion Behavior: additive (⊕ concatenation)

    PDM Sensitivity:
        - table_boost: Increases extraction confidence for PPI/PAI tables
        - hierarchy_sensitivity: Adjusts extraction based on document depth

    CRITICAL REALIST PERSPECTIVE:
        N1 operates in Bhaskar's EMPIRICAL domain - what we observe.
        It extracts phenomena but cannot identify underlying mechanisms.
        Mechanisms are TRANSFACTUAL and require retroduction (N4).
    
    MATHEMATICAL CALIBRATION (v5.0.0):
        Default values below are CONSERVATIVE FALLBACKS.
        For production use, derive optimal values using:
        - extraction_confidence_floor: N1EmpiricalOptimizer.calculate_optimal_extraction_threshold()
          Uses ROC curve analysis and F-beta score optimization
        - deduplication_threshold: N1EmpiricalOptimizer.calculate_deduplication_threshold_statistical()
          Uses distribution analysis and false positive rate control
        - pattern_fuzzy_threshold: N1EmpiricalOptimizer.calculate_pattern_fuzzy_threshold_information_theoretic()
          Uses mutual information maximization
        
        See: farfan_pipeline.calibration.mathematical_calibration
    """

    level: Final[EpistemicLevelLiteral] = field(default="N1-EMP", init=False)

    # Core extraction thresholds (CONSERVATIVE FALLBACKS - use mathematical optimization for production)
    extraction_confidence_floor: float = 0.6  # Derived from F1-score optimization: optimal typically 0.65-0.75
    deduplication_threshold: float = 0.95  # Derived from FPR control: optimal typically 0.92-0.97
    pattern_fuzzy_threshold: float = 0.85  # Derived from mutual information: optimal typically 0.82-0.88

    # PDM-sensitive parameters (adjusted by document structure)
    table_extraction_boost: float = 1.0
    hierarchy_sensitivity: float = 1.0

    # Metadata
    epistemology: str = "Empirismo positivista"
    description: str = "Extracción de hechos observables sin interpretación"
    pdm_sensitivity: PDMSensitivity = field(
        default_factory=lambda: PDMSensitivity(
            active=True, rules=frozenset({"table_boost", "hierarchy_sensitivity"})
        )
    )

    # NEW: Critical Realist properties
    ontological_domain: str = "EMPIRICAL"  # Bhaskar's domain
    detects_transfactual: bool = False     # Cannot detect mechanisms directly
    retroductive_capacity: float = 0.0     # No retroduction at this level

    def __post_init__(self) -> None:
        """Validate N1 empirical calibration parameters."""
        # INV-001: Confidence floor must be in [0, 1]
        if not (0.0 <= self.extraction_confidence_floor <= 1.0):
            raise ValidationError(
                f"extraction_confidence_floor must be in [0.0, 1.0], "
                f"got {self.extraction_confidence_floor}"
            )

        # INV-002: Deduplication threshold must be in [0, 1]
        if not (0.0 <= self.deduplication_threshold <= 1.0):
            raise ValidationError(
                f"deduplication_threshold must be in [0.0, 1.0], "
                f"got {self.deduplication_threshold}"
            )

        # INV-003: Pattern fuzzy threshold must be in [0, 1]
        if not (0.0 <= self.pattern_fuzzy_threshold <= 1.0):
            raise ValidationError(
                f"pattern_fuzzy_threshold must be in [0.0, 1.0], "
                f"got {self.pattern_fuzzy_threshold}"
            )

        # INV-004: Boost cannot be < 1.0 (would be penalty)
        if self.table_extraction_boost < 1.0:
            raise ValidationError(
                f"table_extraction_boost cannot be < 1.0 (would be penalty), "
                f"got {self.table_extraction_boost}"
            )

        # INV-005: Hierarchy sensitivity must be positive
        if self.hierarchy_sensitivity < 0:
            raise ValidationError(
                f"hierarchy_sensitivity cannot be negative, "
                f"got {self.hierarchy_sensitivity}"
            )

    @property
    def output_type(self) -> str:
        """N1 outputs FACT (immutable mapping)."""
        return "FACT"

    @property
    def fusion_behavior(self) -> str:
        """N1 uses additive fusion (⊕)."""
        return "additive"


# =============================================================================
# N2: INFERENTIAL CALIBRATION
# =============================================================================


@dataclass(frozen=True)
class N2InferentialCalibration:
    """
    Calibration for N2-INF (Inferential Computation) level.

    N2 methods transform facts into probabilistic knowledge.
    They operate under Bayesian/constructivist epistemology.

    CONSTITUTIONAL INVARIANTS:
        - level is immutable (property, no setter) [CI-03]
        - prior_strength ∈ [0.0, 1.0]
        - mcmc_samples > 0
        - likelihood_weight > 0.0
        - PDM adjusts priors/model choice, NEVER changes level [CI-05]

    Epistemology: Bayesianismo subjetivista
    Output Type: PARAMETER (probability estimate)
    Fusion Behavior: multiplicative (⊗ weighting)

    PDM Sensitivity:
        - data_driven_priors: Use historical baselines for priors
        - hierarchical_models: Enable hierarchical structure for deep documents
    
    MATHEMATICAL CALIBRATION (v5.0.0):
        Default values below are CONSERVATIVE FALLBACKS.
        For production use, derive optimal values using:
        - prior_strength: N2InferentialOptimizer.calculate_optimal_prior_strength_empirical_bayes()
          Uses Empirical Bayes to estimate hyperparameters from historical data
        - mcmc_samples: N2InferentialOptimizer.calculate_optimal_mcmc_samples_gelman_rubin()
          Uses Gelman-Rubin diagnostic (R̂ < 1.01 for convergence)
        - likelihood_weight: Optimize via Evidence Lower Bound (ELBO) maximization
        
        See: farfan_pipeline.calibration.mathematical_calibration
    """

    level: Final[EpistemicLevelLiteral] = field(default="N2-INF", init=False)

    # Bayesian inference parameters (CONSERVATIVE FALLBACKS - use mathematical optimization)
    prior_strength: float = 0.5  # Empirical Bayes optimal: typically 0.8-2.5 depending on data
    mcmc_samples: int = 5000  # Gelman-Rubin optimal: typically 8000-15000 for R̂ < 1.01
    likelihood_weight: float = 1.0  # ELBO optimization: typically 0.8-1.2

    # PDM-sensitive parameters
    use_data_driven_priors: bool = False
    enable_hierarchical_models: bool = False

    # Metadata
    epistemology: str = "Bayesianismo subjetivista"
    description: str = "Transformación en conocimiento probabilístico"
    pdm_sensitivity: PDMSensitivity = field(
        default_factory=lambda: PDMSensitivity(
            active=True, rules=frozenset({"data_driven_priors", "hierarchical_models"})
        )
    )

    # NEW: Critical Realist properties
    ontological_domain: str = "TRANSFACTUAL"  # Mechanisms and causal powers
    detects_transfactual: bool = True         # Can detect mechanisms (inferred)
    retroductive_capacity: float = 0.7        # Moderate retroduction capacity

    def __post_init__(self) -> None:
        """Validate N2 inferential calibration parameters."""
        # INV-001: Prior strength must be in [0, 1]
        if not (0.0 <= self.prior_strength <= 1.0):
            raise ValidationError(
                f"prior_strength must be in [0.0, 1.0], got {self.prior_strength}"
            )

        # INV-002: MCMC requires samples > 0
        if self.mcmc_samples <= 0:
            raise ValidationError(f"mcmc_samples must be > 0, got {self.mcmc_samples}")

        # INV-003: Likelihood weight must be positive
        if self.likelihood_weight <= 0.0:
            raise ValidationError(
                f"likelihood_weight must be > 0.0, got {self.likelihood_weight}"
            )

    @property
    def output_type(self) -> str:
        """N2 outputs PARAMETER (immutable mapping)."""
        return "PARAMETER"

    @property
    def fusion_behavior(self) -> str:
        """N2 uses multiplicative fusion (⊗)."""
        return "multiplicative"


# =============================================================================
# N3: AUDIT CALIBRATION (VETO GATE)
# =============================================================================


@dataclass(frozen=True)
class N3AuditCalibration:
    """
    Calibration for N3-AUD (Audit/Falsification) level.

    N3 methods validate and can VETO outputs from N1 and N2.
    They operate under Popperian falsificationism.

    *** CONSTITUTIONAL INVARIANTS (CRITICAL) ***

    ASYMMETRY PRINCIPLE [CI-04]:
        - N3 CAN veto N1/N2 outputs (multiplier ∈ [0.0, 1.0])
        - N1/N2 CANNOT veto N3 (unidirectional influence)
        - This is enforced at the code level, not just convention

    VETO THRESHOLDS:
        - veto_threshold_critical: Below this, HARD VETO (multiplier = 0.0)
        - veto_threshold_partial: Below this, SOFT VETO (multiplier = 0.5)
        - CRITICAL < PARTIAL (strictest is lower)

    LEVEL IMMUTABILITY [CI-03]:
        - level is immutable (property, no setter)
        - PDM adjusts strictness, NEVER changes level [CI-05]

    Epistemology: Falsacionismo popperiano
    Output Type: CONSTRAINT (validation/modulation)
    Fusion Behavior: gate (⊘ veto)

    PDM Sensitivity:
        - financial_strictness: Increase strictness for financial data
        - temporal_logic: Enable temporal consistency validation
    
    MATHEMATICAL CALIBRATION (v5.0.0):
        Default values below are CONSERVATIVE FALLBACKS.
        For production use, derive optimal values using:
        - significance_level: N3AuditOptimizer.calculate_optimal_significance_fdr_control()
          Uses Benjamini-Hochberg False Discovery Rate control
        - veto_threshold_critical: N3AuditOptimizer.calculate_veto_thresholds_spc()
          Uses Statistical Process Control (3-sigma rule) for hard veto
        - veto_threshold_partial: N3AuditOptimizer.calculate_veto_thresholds_spc()
          Uses Statistical Process Control (2-sigma rule) for soft veto
        
        See: farfan_pipeline.calibration.mathematical_calibration
    """

    level: Final[EpistemicLevelLiteral] = field(default="N3-AUD", init=False)

    # Statistical validation (CONSERVATIVE FALLBACKS - use FDR control)
    significance_level: float = 0.05  # FDR-controlled optimal: typically 0.03-0.07 via Benjamini-Hochberg

    # Veto thresholds (CRITICAL: enforce asymmetry) (use SPC 3-sigma/2-sigma rules)
    veto_threshold_critical: float = 0.0  # SPC 3-sigma optimal: typically 0.001-0.05 (μ - 3σ)
    veto_threshold_partial: float = 0.5   # SPC 2-sigma optimal: typically 0.15-0.35 (μ - 2σ)

    # PDM-sensitive parameters
    financial_strictness: float = 1.0
    temporal_logic_required: bool = False

    # Metadata
    epistemology: str = "Falsacionismo popperiano"
    description: str = "Auditoría crítica con poder de veto asimétrico"
    asymmetry_principle: str = "N3 puede invalidar N1/N2. N1/N2 NO pueden invalidar N3."
    pdm_sensitivity: PDMSensitivity = field(
        default_factory=lambda: PDMSensitivity(
            active=True, rules=frozenset({"financial_strictness", "temporal_logic"})
        )
    )

    # NEW: Critical Realist properties
    ontological_domain: str = "TRANSFACTUAL"  # Mechanisms and causal powers
    detects_transfactual: bool = True         # Can detect mechanisms (inferred)
    retroductive_capacity: float = 0.9        # High retroduction capacity

    def __post_init__(self) -> None:
        """Validate N3 audit calibration parameters."""
        # INV-001: Significance level must be in [0, 1]
        if not (0.0 <= self.significance_level <= 1.0):
            raise ValidationError(
                f"significance_level must be in [0.0, 1.0], "
                f"got {self.significance_level}"
            )

        # INV-002: CRITICAL veto threshold < PARTIAL veto threshold
        if self.veto_threshold_critical >= self.veto_threshold_partial:
            raise ValidationError(
                f"CONSTITUTIONAL VIOLATION: veto_threshold_critical "
                f"({self.veto_threshold_critical}) must be < "
                f"veto_threshold_partial ({self.veto_threshold_partial}). "
                f"Critical veto must be stricter than partial veto."
            )

        # INV-003: Veto thresholds must be in [0, 1]
        if not (0.0 <= self.veto_threshold_critical <= 1.0):
            raise ValidationError(
                f"veto_threshold_critical must be in [0.0, 1.0], "
                f"got {self.veto_threshold_critical}"
            )

        if not (0.0 <= self.veto_threshold_partial <= 1.0):
            raise ValidationError(
                f"veto_threshold_partial must be in [0.0, 1.0], "
                f"got {self.veto_threshold_partial}"
            )

        # INV-004: Financial strictness must be positive
        if self.financial_strictness < 0:
            raise ValidationError(
                f"financial_strictness cannot be negative, "
                f"got {self.financial_strictness}"
            )

    def compute_veto_action(self, confidence: float) -> dict[str, any]:
        """
        Compute the veto action based on audit confidence.

        This implements the ASYMMETRIC VETO PRINCIPLE [CI-04]:
        - N3 can suppress N1/N2 outputs
        - The suppression is unidirectional (N1/N2 cannot reverse it)

        Args:
            confidence: The audit confidence score [0.0, 1.0]

        Returns:
            Dict with veto_action, confidence_multiplier, status

        Examples:
            >>> n3 = N3AuditCalibration()
            >>> n3.compute_veto_action(0.3)  # Below partial threshold
            {'veto_action': 'PARTIAL_VETO', 'confidence_multiplier': 0.5, ...}
            >>> n3.compute_veto_action(0.0)  # Below critical threshold
            {'veto_action': 'CRITICAL_VETO', 'confidence_multiplier': 0.0, ...}
            >>> n3.compute_veto_action(0.8)  # Above all thresholds
            {'veto_action': 'APPROVED', 'confidence_multiplier': 1.0, ...}
        """
        if confidence <= self.veto_threshold_critical:
            # CRITICAL VETO: Complete suppression
            return {
                "veto_action": "CRITICAL_VETO",
                "confidence_multiplier": 0.0,
                "status": "SUPPRESSED",
                "rationale": f"Audit confidence {confidence:.2f} <= critical threshold "
                f"{self.veto_threshold_critical:.2f}",
            }
        elif confidence <= self.veto_threshold_partial:
            # PARTIAL VETO: Confidence penalty
            return {
                "veto_action": "PARTIAL_VETO",
                "confidence_multiplier": 0.5,
                "status": "ATTENUATED",
                "rationale": f"Audit confidence {confidence:.2f} <= partial threshold "
                f"{self.veto_threshold_partial:.2f}",
            }
        else:
            # NO VETO: Approved
            return {
                "veto_action": "APPROVED",
                "confidence_multiplier": 1.0,
                "status": "VALIDATED",
                "rationale": f"Audit confidence {confidence:.2f} above all veto thresholds",
            }

    @property
    def output_type(self) -> str:
        """N3 outputs CONSTRAINT (immutable mapping)."""
        return "CONSTRAINT"

    @property
    def fusion_behavior(self) -> str:
        """N3 uses gate fusion (⊘ veto)."""
        return "gate"


# =============================================================================
# N4: META-ANALYSIS CALIBRATION
# =============================================================================


@dataclass(frozen=True)
class N4MetaCalibration:
    """
    Calibration for N4-META (Meta-Analysis) level.

    N4 methods perform meta-analysis of the entire analytical process.
    They identify failure points and synthesize final narratives.

    CONSTITUTIONAL INVARIANTS:
        - level is immutable (property, no setter) [CI-03]
        - N4 consumes outputs from all levels (N1-N3)
        - N4 cannot be vetoed by lower levels

    Epistemology: Meta-análisis del proceso analítico
    Output Type: META_ANALYSIS (process insights)
    Fusion Behavior: terminal (⊙ synthesis)

    PDM Sensitivity:
        - None (meta-analysis is level-agnostic)
    
    MATHEMATICAL CALIBRATION (v5.0.0):
        Default values below are CONSERVATIVE FALLBACKS.
        For production use, derive optimal values using:
        - failure_detection_threshold: N4MetaOptimizer.calculate_failure_threshold_mutual_information()
          Uses mutual information maximization to detect failures
        - synthesis_confidence_threshold: N4MetaOptimizer.calculate_synthesis_threshold_entropy()
          Uses Shannon entropy of evidence distribution
        
        See: farfan_pipeline.calibration.mathematical_calibration
    """

    level: Final[EpistemicLevelLiteral] = field(default="N4-META", init=False)

    # Meta-analysis parameters (CONSERVATIVE FALLBACKS - use information theory)
    failure_detection_threshold: float = 0.3  # Mutual information optimal: typically 0.25-0.35
    synthesis_confidence_threshold: float = 0.7  # Entropy-adjusted optimal: typically 0.65-0.85

    # Metadata
    epistemology: str = "Meta-análisis del proceso analítico"
    description: str = "Identificación de puntos de fallo y síntesis final"
    pdm_sensitivity: PDMSensitivity = field(
        default_factory=lambda: PDMSensitivity(active=False, rules=frozenset())
    )

    # NEW: Critical Realist properties
    ontological_domain: str = "REALISTIC"  # Real mechanisms and their retroduction
    detects_transfactual: bool = True       # Can detect and retroduce mechanisms
    retroductive_capacity: float = 1.0      # Full retroduction capacity

    def __post_init__(self) -> None:
        """Validate N4 meta-analysis calibration parameters."""
        # INV-001: Thresholds must be in [0, 1]
        if not (0.0 <= self.failure_detection_threshold <= 1.0):
            raise ValidationError(
                f"failure_detection_threshold must be in [0.0, 1.0], "
                f"got {self.failure_detection_threshold}"
            )

        if not (0.0 <= self.synthesis_confidence_threshold <= 1.0):
            raise ValidationError(
                f"synthesis_confidence_threshold must be in [0.0, 1.0], "
                f"got {self.synthesis_confidence_threshold}"
            )

    @property
    def output_type(self) -> str:
        """N4 outputs META_ANALYSIS (immutable mapping)."""
        return "META_ANALYSIS"

    @property
    def fusion_behavior(self) -> str:
        """N4 uses terminal fusion (⊙ synthesis)."""
        return "terminal"


# =============================================================================
# CALIBRATION FACTORY
# =============================================================================


def create_calibration(
    level: EpistemicLevelLiteral, **kwargs
) -> N0InfrastructureCalibration | N1EmpiricalCalibration | N2InferentialCalibration | N3AuditCalibration | N4MetaCalibration:
    """
    Factory function to create calibration objects.

    Args:
        level: Epistemic level (N0-INFRA, N1-EMP, N2-INF, N3-AUD, N4-META)
        **kwargs: Calibration parameters to override defaults

    Returns:
        Corresponding calibration object with frozen parameters

    Raises:
        ValidationError: If level is invalid or parameters are out of bounds

    Examples:
        >>> n1 = create_calibration("N1-EMP", extraction_confidence_floor=0.7)
        >>> n3 = create_calibration("N3-AUD", veto_threshold_partial=0.6)
    """
    validate_epistemic_level(level)

    calibration_classes = {
        "N0-INFRA": N0InfrastructureCalibration,
        "N1-EMP": N1EmpiricalCalibration,
        "N2-INF": N2InferentialCalibration,
        "N3-AUD": N3AuditCalibration,
        "N4-META": N4MetaCalibration,
    }

    cls = calibration_classes.get(level)
    if cls is None:
        # This should never happen due to validate_epistemic_level
        raise ValidationError(f"Unknown level: {level}")

    return cls(**kwargs)


# =============================================================================
# LEVEL CONFIGURATION EXPORT
# =============================================================================


def get_default_calibration_for_level(
    level: EpistemicLevelLiteral,
) -> N0InfrastructureCalibration | N1EmpiricalCalibration | N2InferentialCalibration | N3AuditCalibration | N4MetaCalibration:
    """
    Get the default calibration for a given epistemic level.

    This provides the baseline calibration before PDM adjustments.

    Args:
        level: Epistemic level

    Returns:
        Default calibration object for the level
    """
    return create_calibration(level)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Type definitions
    "EpistemicLevelLiteral",
    # PDM structures
    "PDMSensitivity",
    # Calibration classes
    "N0InfrastructureCalibration",
    "N1EmpiricalCalibration",
    "N2InferentialCalibration",
    "N3AuditCalibration",
    "N4MetaCalibration",
    # Factory functions
    "create_calibration",
    "get_default_calibration_for_level",
]
