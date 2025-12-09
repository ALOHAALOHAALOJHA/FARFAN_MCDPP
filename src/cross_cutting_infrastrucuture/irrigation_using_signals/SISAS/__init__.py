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

# Sentinel class for unavailable modules
class _UnavailableModule:
    """
    Sentinel class for modules that failed to import.
    
    Provides helpful error messages when attempting to use unavailable SISAS functionality.
    Common causes: missing pydantic, missing numpy, or other dependencies.
    """
    def __init__(self, module_name: str, typical_dependency: str = "required dependencies"):
        self.module_name = module_name
        self.typical_dependency = typical_dependency
    
    def __call__(self, *args, **kwargs):
        raise AttributeError(
            f"SISAS module '{self.module_name}' is not available. "
            f"Please install {self.typical_dependency} to use this functionality. "
            f"Common dependencies: pydantic>=2.0, numpy, pandas"
        )
    
    def __getattr__(self, name):
        raise AttributeError(
            f"SISAS module '{self.module_name}' is not available. "
            f"Cannot access attribute '{name}'. "
            f"Please install {self.typical_dependency}. "
            f"Common dependencies: pydantic>=2.0, numpy, pandas"
        )

# Core signal abstractions
try:
    from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signals import (
        SignalPack,
        SignalRegistry,
        SignalClient,
        create_default_signal_pack,
    )
except ImportError:
    SignalPack = _UnavailableModule('signals.SignalPack')
    SignalRegistry = _UnavailableModule('signals.SignalRegistry')
    SignalClient = _UnavailableModule('signals.SignalClient')
    create_default_signal_pack = _UnavailableModule('signals.create_default_signal_pack')

# Signal registry for questionnaires and chunks
try:
    from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_registry import (
        QuestionnaireSignalRegistry,
        ChunkingSignalPack,
        MicroAnsweringSignalPack,
        create_signal_registry,
    )
except ImportError:
    QuestionnaireSignalRegistry = _UnavailableModule('signal_registry.QuestionnaireSignalRegistry')
    ChunkingSignalPack = _UnavailableModule('signal_registry.ChunkingSignalPack')
    MicroAnsweringSignalPack = _UnavailableModule('signal_registry.MicroAnsweringSignalPack')
    create_signal_registry = _UnavailableModule('signal_registry.create_signal_registry')

# Quality metrics
try:
    from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_quality_metrics import (
        SignalQualityMetrics,
        compute_signal_quality_metrics,
        analyze_coverage_gaps,
        generate_quality_report,
    )
except ImportError:
    SignalQualityMetrics = _UnavailableModule('signal_quality_metrics.SignalQualityMetrics')
    compute_signal_quality_metrics = _UnavailableModule('signal_quality_metrics.compute_signal_quality_metrics')
    analyze_coverage_gaps = _UnavailableModule('signal_quality_metrics.analyze_coverage_gaps')
    generate_quality_report = _UnavailableModule('signal_quality_metrics.generate_quality_report')

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
