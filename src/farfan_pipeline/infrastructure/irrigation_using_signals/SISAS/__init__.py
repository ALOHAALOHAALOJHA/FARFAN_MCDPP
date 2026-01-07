"""
SISAS - Signal Intelligence System for Advanced Structuring
============================================================

Production implementation of the signal-based enrichment system for the
F.A.R.F.A.N pipeline.

Main Components:
- signal_registry: Central registry for signal packs and questionnaire signals
- signals: Core signal abstractions and client
- signal_irrigator: Signal delivery system (extractor → question routing) **NEW**
- signal_quality_metrics: Quality assessment for signal coverage
- signal_intelligence_layer: Advanced signal processing
- signal_contract_validator: Contract enforcement for signals
- signal_evidence_extractor: Evidence extraction from signals
- signal_semantic_expander: Semantic expansion of signal meanings
- signal_context_scoper: Context scoping for signals
- signal_consumption: Signal consumption patterns
- signal_loader: Signal loading utilities
- signal_resolution: Signal resolution strategies

Strategic Irrigation Enhancements (2025-12-11):
- signal_method_metadata: Method execution metadata (Enhancement #1)
- signal_validation_specs: Structured validation specifications (Enhancement #2)
- signal_scoring_context: Scoring modality context (Enhancement #3)
- signal_semantic_context: Semantic disambiguation layer (Enhancement #4)
- signal_enhancement_integrator: Unified enhancement integration

IMPORTANT: This module requires pydantic>=2.0 as part of the dura_lex contract system.
The F.A.R.F.A.N pipeline enforces contracts with zero tolerance for maximum performance.
"""

# Core signal abstractions - REQUIRED for dura_lex contract system
# Note: 'infrastrucuture' spelling is intentional - matches actual folder name
try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals import (
        SignalPack,
        SignalRegistry,
        SignalClient,
        create_default_signal_pack,
    )
except ImportError as e:
    raise ImportError(
        "SISAS signals module requires pydantic>=2.0 (REQUIRED dependency). "
        "The F.A.R.F.A.N pipeline uses the dura_lex contract system for maximum performance "
        "and deterministic execution with zero tolerance for contract violations. "
        f"Install with: pip install 'pydantic>=2.0'. Original error: {e}"
    ) from e

# Signal registry for questionnaires and chunks - REQUIRED
try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
        QuestionnaireSignalRegistry,
        ChunkingSignalPack,
        MicroAnsweringSignalPack,
        create_signal_registry,
    )
except ImportError as e:
    raise ImportError(
        "SISAS signal_registry module requires pydantic>=2.0 (REQUIRED dependency). "
        f"Install with: pip install 'pydantic>=2.0'. Original error: {e}"
    ) from e

# Quality metrics - REQUIRED
try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_quality_metrics import (
        SignalQualityMetrics,
        compute_signal_quality_metrics,
        analyze_coverage_gaps,
        generate_quality_report,
    )
except ImportError as e:
    raise ImportError(
        "SISAS signal_quality_metrics module failed to import. "
        f"Ensure all dependencies are installed. Original error: {e}"
    ) from e

# Strategic Enhancements - NEW 2025-12-11
try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_irrigator import (
        SignalIrrigator,
        SignalDelivery,
        IrrigationStats,
        irrigate_extraction_result,
    )
except ImportError as e:
    raise ImportError(
        "SISAS signal_irrigator module failed to import. "
        f"Ensure signal_irrigator.py is present. Original error: {e}"
    ) from e

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_method_metadata import (
        MethodMetadata,
        MethodExecutionMetadata,
        extract_method_metadata,
    )
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_validation_specs import (
        ValidationSpec,
        ValidationSpecifications,
        extract_validation_specifications,
    )
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_scoring_context import (
        ScoringModalityDefinition,
        ScoringContext,
        extract_scoring_context,
    )
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_semantic_context import (
        SemanticContext,
        DisambiguationRule,
        extract_semantic_context,
    )
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_enhancement_integrator import (
        SignalEnhancementIntegrator,
        create_enhancement_integrator,
    )
except ImportError as e:
    raise ImportError(
        "SISAS strategic enhancements failed to import. "
        f"Ensure all dependencies are installed. Original error: {e}"
    ) from e

__all__ = [
    # Core
    "SignalPack",
    "SignalRegistry",
    "SignalClient",
    "create_default_signal_pack",
    # Registry
    "QuestionnaireSignalRegistry",
    "ChunkingSignalPack",
    "MicroAnsweringSignalPack",
    "create_signal_registry",
    # Signal Irrigation - NEW
    "SignalIrrigator",
    "SignalDelivery",
    "IrrigationStats",
    "irrigate_extraction_result",
    # Quality
    "SignalQualityMetrics",
    "compute_signal_quality_metrics",
    "analyze_coverage_gaps",
    "generate_quality_report",
    # Enhancements
    "MethodMetadata",
    "MethodExecutionMetadata",
    "extract_method_metadata",
    "ValidationSpec",
    "ValidationSpecifications",
    "extract_validation_specifications",
    "ScoringModalityDefinition",
    "ScoringContext",
    "extract_scoring_context",
    "SemanticContext",
    "DisambiguationRule",
    "extract_semantic_context",
    "SignalEnhancementIntegrator",
    "create_enhancement_integrator",
]
