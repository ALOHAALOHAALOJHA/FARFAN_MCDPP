"""
Calibration Infrastructure
==========================
Public API for calibration layer.

DESIGN PATTERN: Facade Pattern
- Single entry point for all calibration operations
- Hides internal complexity from consumers

SYSTEM CAPABILITIES:
1. Calibration within epistemic regime (not parallel)
2. TYPE-specific defaults and prohibitions (cached via Flyweight)
3. Ingestion/Phase-2 calibration with bounded strategies
4. Manifest hashing and optional cryptographic signatures
5. Drift auditing and N3-AUD veto gates
6. Interaction governance (acyclicity, bounded fusion, veto cascades)
7. Fact registry (deduplication, verbosity threshold >= 0.90)

INVARIANTS ENFORCED:
- INV-CAL-FREEZE-001: All calibration parameters immutable post-construction
- INV-CAL-REGIME-001: Calibration operates within epistemic regime
- INV-CAL-AUDIT-001: All parameters subject to N3-AUD verification
- INV-CAL-HASH-001: Canonical JSON serialization for deterministic hashing
- INV-CAL-TZ-001: All timestamps timezone-aware UTC
- INV-CAL-SIG-001: Optional Ed25519 signatures for cryptographic attestation

Schema Version: 2.0.0
"""
from .calibration_core import (
    CalibrationError,
    CalibrationLayer,
    CalibrationParameter,
    CalibrationPhase,
    ClosedInterval,
    EvidenceReference,
    ExpirationError,
    IntegrityError,
    ValidationError,
    ValidityStatus,
    create_calibration_parameter,
    create_default_bounds,
)
from .type_defaults import (
    PROHIBITED_OPERATIONS,
    VALID_CONTRACT_TYPES,
    CONTRACT_TYPE_A,
    CONTRACT_TYPE_B,
    CONTRACT_TYPE_C,
    CONTRACT_TYPE_D,
    CONTRACT_TYPE_E,
    CONTRACT_SUBTIPO_F,
    PRIOR_STRENGTH_MIN,
    PRIOR_STRENGTH_MAX,
    ContractTypeDefaults,
    EpistemicLayerRatios,
    get_type_defaults,
    get_all_type_defaults,
    is_operation_prohibited,
    is_operation_permitted,
    clear_defaults_cache,
    UnknownContractTypeError,
    CanonicalSourceError,
    ConfigurationError,
)
from .unit_of_analysis import (
    FiscalContext,
    MunicipalityCategory,
    UnitOfAnalysis,
)
from .ingestion_calibrator import (
    CalibrationStrategy,
    IngestionCalibrator,
    StandardCalibrationStrategy,
    AggressiveCalibrationStrategy,
    ConservativeCalibrationStrategy,
)
from .method_binding_validator import (
    EpistemicViolation,
    MethodBinding,
    MethodBindingSet,
    MethodBindingValidator,
    ValidationResult,
    ValidationSeverity,
)
from .phase2_calibrator import (
    Phase2CalibrationResult,
    Phase2Calibrator,
)
from .calibration_manifest import (
    CalibrationManifest,
    CalibrationDecision,
    ManifestBuilder,
    DriftIndicator,
    DriftReport,
)
from .calibration_auditor import (
    CalibrationAuditor,
    AuditResult,
    CalibrationViolation,
    CalibrationSpecification,
    PriorStrengthSpecification,
    VetoThresholdSpecification,
    FusionStrategySpecification,
)
from .interaction_governor import (
    InteractionGovernor,
    DependencyGraph,
    MethodNode,
    CycleDetector,
    LevelInversionDetector,
    VetoCoordinator,
    VetoResult,
    VetoReport,
    InteractionViolation,
    InteractionViolationType,
    bounded_multiplicative_fusion,
)
from .fact_registry import (
    CanonicalFactRegistry,
    FactEntry,
    FactFactory,
    EpistemologicalLevel,
    DuplicateRecord,
    RegistryStatistics,
)

__all__ = [
    # =========================================================================
    # CORE TYPES
    # =========================================================================
    "CalibrationLayer",
    "CalibrationParameter",
    "CalibrationPhase",
    "ClosedInterval",
    "EvidenceReference",
    "ValidityStatus",
    # Factory functions
    "create_calibration_parameter",
    "create_default_bounds",
    
    # =========================================================================
    # EXCEPTIONS
    # =========================================================================
    "CalibrationError",
    "ValidationError",
    "IntegrityError",
    "ExpirationError",
    "EpistemicViolation",
    "UnknownContractTypeError",
    "CanonicalSourceError",
    "ConfigurationError",
    
    # =========================================================================
    # TYPE DEFAULTS (Flyweight cached)
    # =========================================================================
    "get_type_defaults",
    "get_all_type_defaults",
    "is_operation_prohibited",
    "is_operation_permitted",
    "clear_defaults_cache",
    "PROHIBITED_OPERATIONS",
    "VALID_CONTRACT_TYPES",
    "CONTRACT_TYPE_A",
    "CONTRACT_TYPE_B",
    "CONTRACT_TYPE_C",
    "CONTRACT_TYPE_D",
    "CONTRACT_TYPE_E",
    "CONTRACT_SUBTIPO_F",
    "PRIOR_STRENGTH_MIN",
    "PRIOR_STRENGTH_MAX",
    "ContractTypeDefaults",
    "EpistemicLayerRatios",
    
    # =========================================================================
    # UNIT OF ANALYSIS
    # =========================================================================
    "FiscalContext",
    "MunicipalityCategory",
    "UnitOfAnalysis",
    
    # =========================================================================
    # INGESTION CALIBRATOR (N1-EMP)
    # =========================================================================
    "CalibrationStrategy",
    "IngestionCalibrator",
    "StandardCalibrationStrategy",
    "AggressiveCalibrationStrategy",
    "ConservativeCalibrationStrategy",
    
    # =========================================================================
    # METHOD BINDING VALIDATOR
    # =========================================================================
    "MethodBinding",
    "MethodBindingSet",
    "MethodBindingValidator",
    "ValidationResult",
    "ValidationSeverity",
    
    # =========================================================================
    # PHASE-2 CALIBRATOR (N2-INF)
    # =========================================================================
    "Phase2CalibrationResult",
    "Phase2Calibrator",
    
    # =========================================================================
    # CALIBRATION MANIFEST (Audit Trail)
    # =========================================================================
    "CalibrationManifest",
    "CalibrationDecision",
    "ManifestBuilder",
    "DriftIndicator",
    "DriftReport",
    
    # =========================================================================
    # CALIBRATION AUDITOR (N3-AUD Veto Gate)
    # =========================================================================
    "CalibrationAuditor",
    "AuditResult",
    "CalibrationViolation",
    "CalibrationSpecification",
    "PriorStrengthSpecification",
    "VetoThresholdSpecification",
    "FusionStrategySpecification",
    
    # =========================================================================
    # INTERACTION GOVERNOR (Bounded Fusion, Veto Cascade)
    # =========================================================================
    "InteractionGovernor",
    "DependencyGraph",
    "MethodNode",
    "CycleDetector",
    "LevelInversionDetector",
    "VetoCoordinator",
    "VetoResult",
    "VetoReport",
    "InteractionViolation",
    "InteractionViolationType",
    "bounded_multiplicative_fusion",
    
    # =========================================================================
    # FACT REGISTRY (Deduplication, Verbosity)
    # =========================================================================
    "CanonicalFactRegistry",
    "FactEntry",
    "FactFactory",
    "EpistemologicalLevel",
    "DuplicateRecord",
    "RegistryStatistics",
]
