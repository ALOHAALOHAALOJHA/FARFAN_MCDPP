"""
COHORT_2024 Calibration System

Complete 8-layer calibration with role-based activation and Choquet aggregation.

Layers:
- @b (Base): Intrinsic method quality (b_theory, b_impl, b_deploy)
- @chain: Method wiring/orchestration validation
- @q: Question appropriateness
- @d: Dimension alignment
- @p: Policy area fit
- @C: Contract/congruence compliance
- @u: PDT document quality (S·M·I·P components)
- @m: Governance/meta maturity

Production implementations in: src/orchestration/
COHORT exports with metadata in: calibration/COHORT_2024_*.py
"""

# Chain Layer
from .COHORT_2024_chain_layer import (
    ChainEvaluationResult,
    ChainLayerEvaluator,
    ChainSequenceResult,
    create_evaluator_from_validator,
)

# Contextual Layers (@q, @d, @p)
from .COHORT_2024_contextual_layers import (
    CompatibilityRegistry,
    CompatibilityMapping,
    QuestionEvaluator,
    DimensionEvaluator,
    PolicyEvaluator,
    create_contextual_evaluators,
)

# Unit Layer (@u)
from .COHORT_2024_unit_layer import (
    UnitLayerConfig,
    UnitLayerEvaluator,
    UnitLayerResult,
    StructuralCompliance,
    MandatorySections,
    IndicatorQuality,
    PPICompleteness,
    create_default_config as create_unit_config,
    COHORT_METADATA as UNIT_LAYER_METADATA,
)

# Congruence Layer (@C)
from .COHORT_2024_congruence_layer import (
    CongruenceLayerConfig,
    CongruenceLayerEvaluator,
    CongruenceRequirements,
    CongruenceThresholds,
    OutputRangeSpec,
    SemanticTagSet,
    FusionRule,
    create_default_congruence_config,
    COHORT_METADATA as CONGRUENCE_LAYER_METADATA,
)

# Intrinsic Calibration Loader (@b)
from .COHORT_2024_intrinsic_calibration_loader import (
    CalibrationScore,
    IntrinsicCalibrationLoader,
    load_intrinsic_calibration,
    get_score,
    get_detailed_score,
    is_excluded,
    is_pending,
    list_calibrated_methods,
    get_role_default,
    get_calibration_statistics,
)

# Layer Assignment
from .COHORT_2024_layer_assignment import (
    LAYER_REQUIREMENTS,
    CHOQUET_WEIGHTS,
    CHOQUET_INTERACTION_WEIGHTS,
    identify_executors,
    assign_layers_and_weights,
    generate_canonical_inventory,
)

# Layer Metadata Registry (COHORT_2024 discovery and compatibility)
from .layer_metadata_registry import (
    LayerMetadataRegistry,
    LayerMetadata,
    create_default_registry,
)

# Layer Versioning (cross-COHORT comparison)
from .layer_versioning import (
    LayerMetadataRegistry as VersioningRegistry,
    FormulaChangeDetector,
    WeightDiffAnalyzer,
    MigrationImpactAssessor,
    LayerEvolutionValidator,
    LayerMetadata as VersioningLayerMetadata,
    WeightChange,
    FormulaChange,
    MigrationImpact,
    DiffThresholds,
    create_versioning_tools,
)

__all__ = [
    # Chain Layer
    "ChainLayerEvaluator",
    "ChainEvaluationResult",
    "ChainSequenceResult",
    "create_evaluator_from_validator",
    # Contextual Layers
    "CompatibilityRegistry",
    "CompatibilityMapping",
    "QuestionEvaluator",
    "DimensionEvaluator",
    "PolicyEvaluator",
    "create_contextual_evaluators",
    # Unit Layer
    "UnitLayerConfig",
    "UnitLayerEvaluator",
    "UnitLayerResult",
    "StructuralCompliance",
    "MandatorySections",
    "IndicatorQuality",
    "PPICompleteness",
    "create_unit_config",
    "UNIT_LAYER_METADATA",
    # Congruence Layer
    "CongruenceLayerConfig",
    "CongruenceLayerEvaluator",
    "CongruenceRequirements",
    "CongruenceThresholds",
    "OutputRangeSpec",
    "SemanticTagSet",
    "FusionRule",
    "create_default_congruence_config",
    "CONGRUENCE_LAYER_METADATA",
    # Intrinsic Calibration
    "CalibrationScore",
    "IntrinsicCalibrationLoader",
    "load_intrinsic_calibration",
    "get_score",
    "get_detailed_score",
    "is_excluded",
    "is_pending",
    "list_calibrated_methods",
    "get_role_default",
    "get_calibration_statistics",
    # Layer Assignment
    "LAYER_REQUIREMENTS",
    "CHOQUET_WEIGHTS",
    "CHOQUET_INTERACTION_WEIGHTS",
    "identify_executors",
    "assign_layers_and_weights",
    "generate_canonical_inventory",
    # Layer Metadata Registry
    "LayerMetadataRegistry",
    "LayerMetadata",
    "create_default_registry",
    # Layer Versioning
    "VersioningRegistry",
    "FormulaChangeDetector",
    "WeightDiffAnalyzer",
    "MigrationImpactAssessor",
    "LayerEvolutionValidator",
    "VersioningLayerMetadata",
    "WeightChange",
    "FormulaChange",
    "MigrationImpact",
    "DiffThresholds",
    "create_versioning_tools",
]

