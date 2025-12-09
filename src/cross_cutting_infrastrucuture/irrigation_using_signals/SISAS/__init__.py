"""
SISAS - Signal Intelligence System for Advanced Structuring
============================================================

Production implementation of the signal-based enrichment system for the
F.A.R.F.A.N pipeline.

Main Components:
- signal_registry: Central registry for signal packs and questionnaire signals
- signals: Core signal abstractions and client
- signal_quality_metrics: Quality assessment for signal coverage
- signal_intelligence_layer: Advanced signal processing
- signal_contract_validator: Contract enforcement for signals
- signal_evidence_extractor: Evidence extraction from signals
- signal_semantic_expander: Semantic expansion of signal meanings
- signal_context_scoper: Context scoping for signals
- signal_consumption: Signal consumption patterns
- signal_loader: Signal loading utilities
- signal_resolution: Signal resolution strategies
"""

# Core signal abstractions
try:
    from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signals import (
        SignalPack,
        SignalRegistry,
        SignalClient,
        create_default_signal_pack,
    )
except ImportError:
    SignalPack = None
    SignalRegistry = None
    SignalClient = None
    create_default_signal_pack = None

# Signal registry for questionnaires and chunks
try:
    from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_registry import (
        QuestionnaireSignalRegistry,
        ChunkingSignalPack,
        MicroAnsweringSignalPack,
        create_signal_registry,
    )
except ImportError:
    QuestionnaireSignalRegistry = None
    ChunkingSignalPack = None
    MicroAnsweringSignalPack = None
    create_signal_registry = None

# Quality metrics
try:
    from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_quality_metrics import (
        SignalQualityMetrics,
        compute_signal_quality_metrics,
        analyze_coverage_gaps,
        generate_quality_report,
    )
except ImportError:
    SignalQualityMetrics = None
    compute_signal_quality_metrics = None
    analyze_coverage_gaps = None
    generate_quality_report = None

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
    # Quality
    "SignalQualityMetrics",
    "compute_signal_quality_metrics",
    "analyze_coverage_gaps",
    "generate_quality_report",
]
