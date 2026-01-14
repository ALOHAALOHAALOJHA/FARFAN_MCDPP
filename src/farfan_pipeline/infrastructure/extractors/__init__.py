"""
Empirically-Calibrated Extractor Framework for FARFAN Pipeline.

This module provides state-of-the-art signal extractors calibrated with
empirical data from 14 real PDT plans (2,956 pages analyzed).

Key Features:
- Auto-loading of empirical calibration patterns
- Validation against gold standard examples
- Confidence scoring with empirical thresholds
- Auto-generated tests from corpus
- Performance metrics and reporting

Available Extractors:
- StructuralMarkerExtractor (MC01/Phase 1-SP2): Tables, sections, graphs
- NormativeReferenceExtractor (MC03/Phase 1-SP5): Laws, decrees, treaties
- FinancialChainExtractor (MC05): Budgetary chains
- QuantitativeTripletExtractor (MC06/Phase 1-SP6): Línea Base, Meta, Año
- CausalVerbExtractor (MC08): Causal relationships
- InstitutionalNERExtractor (MC09): Colombian institutions

Usage:
    from farfan_pipeline.infrastructure.extractors import FinancialChainExtractor

    extractor = FinancialChainExtractor()
    result = extractor.extract(text)

    print(f"Found {len(result.matches)} financial chains")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Validation passed: {result.validation_passed}")

Self-Testing:
    extractor.self_test()  # Run against gold standards
    extractor.get_metrics()  # Get performance metrics

Validation:
    from farfan_pipeline.infrastructure.extractors import ExtractorValidator

    validator = ExtractorValidator()
    results = validator.validate_all_extractors()
    report = validator.generate_report(results)
    print(report)

Author: CQC Extractor Excellence Framework
Version: 2.0.0
Date: 2026-01-06
"""

from .empirical_extractor_base import (
    EmpiricallyCalibrated,
    PatternBasedExtractor,
    ExtractionPattern,
    ExtractionResult,
    load_all_extractors_from_calibration,
    generate_test_suite
)

from .structural_marker_extractor import (
    StructuralMarkerExtractor,
    StructuralElement
)

from .normative_reference_extractor import (
    NormativeReferenceExtractor,
    NormativeReference
)

from .quantitative_triplet_extractor import (
    QuantitativeTripletExtractor,
    QuantitativeTriplet
)

from .financial_chain_extractor import (
    FinancialChainExtractor,
    FinancialChain,
    extract_financial_chains
)

from .causal_verb_extractor import (
    CausalVerbExtractor,
    CausalLink,
    extract_causal_links
)

from .institutional_ner_extractor import (
    InstitutionalNERExtractor,
    InstitutionalEntity,
    extract_institutional_entities,
    get_entity_info
)

from .extractor_validator import (
    ExtractorValidator,
    ValidationMetrics
)

# SISAS 2.0 Orchestrator
from .extractor_orchestrator import (
    ExtractorOrchestrator,
    ExtractionContext,
    OrchestrationResult,
    create_orchestrator_from_resolver,
    EXTRACTOR_SIGNAL_MAP
)

__version__ = "2.0.0"

__all__ = [
    # Base framework
    'EmpiricallyCalibrated',
    'PatternBasedExtractor',
    'ExtractionPattern',
    'ExtractionResult',

    # Extractors
    'StructuralMarkerExtractor',
    'NormativeReferenceExtractor',
    'QuantitativeTripletExtractor',
    'FinancialChainExtractor',
    'CausalVerbExtractor',
    'InstitutionalNERExtractor',

    # Data structures
    'StructuralElement',
    'NormativeReference',
    'QuantitativeTriplet',
    'FinancialChain',
    'CausalLink',
    'InstitutionalEntity',

    # Convenience functions
    'extract_financial_chains',
    'extract_causal_links',
    'extract_institutional_entities',
    'get_entity_info',

    # Validation
    'ExtractorValidator',
    'ValidationMetrics',

    # Utilities
    'load_all_extractors_from_calibration',
    'generate_test_suite',
    
    # SISAS 2.0 Orchestrator
    'ExtractorOrchestrator',
    'ExtractionContext',
    'OrchestrationResult',
    'create_orchestrator_from_resolver',
    'EXTRACTOR_SIGNAL_MAP'
]


# Quick validation on import (optional, can be disabled)
def _run_quick_validation():
    """Run quick validation on import to ensure extractors are working."""
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Quick smoke test
        extractor = FinancialChainExtractor()
        result = extractor.extract("El presupuesto es de $500 millones del SGP")

        if len(result.matches) == 0:
            logger.warning("FinancialChainExtractor smoke test failed - no matches")
        else:
            logger.debug(f"✓ FinancialChainExtractor smoke test passed ({len(result.matches)} matches)")
    except Exception as e:
        logger.warning(f"Extractor smoke test failed: {e}")


# Optionally run validation on import (disabled by default for performance)
# _run_quick_validation()
