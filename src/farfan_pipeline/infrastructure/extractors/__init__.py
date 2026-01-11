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
- FinancialChainExtractor (MC05): Budgetary chains
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

from .causal_verb_extractor import CausalLink, CausalVerbExtractor, extract_causal_links
from .empirical_extractor_base import (
    EmpiricallyCalibrated,
    ExtractionPattern,
    ExtractionResult,
    PatternBasedExtractor,
    generate_test_suite,
    load_all_extractors_from_calibration,
)
from .extractor_validator import ExtractorValidator, ValidationMetrics
from .financial_chain_extractor import (
    FinancialChain,
    FinancialChainExtractor,
    extract_financial_chains,
)
from .institutional_ner_extractor import (
    InstitutionalEntity,
    InstitutionalNERExtractor,
)
from .normative_reference_extractor import (
    NormativeReference,
    NormativeReferenceExtractor,
)
from .population_disaggregation_extractor import (
    CSVPopulationAdapter,
    DictPopulationAdapter,
    DisaggregationAxis,
    DisaggregationError,
    DisaggregationErrorType,
    DisaggregationReport,
    JSONPopulationAdapter,
    PopulationDisaggregationExtractor,
    PopulationGroup,
    PopulationSourceAdapter,
)
from .programmatic_hierarchy_extractor import (
    CSVSourceAdapter,
    DictSourceAdapter,
    HierarchyError,
    HierarchyErrorType,
    HierarchyNode,
    HierarchySourceAdapter,
    JSONFileSourceAdapter,
    ProgrammaticHierarchyExtractor,
)
from .quantitative_triplet_extractor import (
    QuantitativeTriplet,
    QuantitativeTripletExtractor,
)
from .semantic_relationship_extractor import (
    CSVRelationshipAdapter,
    DictRelationshipAdapter,
    JSONRelationshipAdapter,
    RelationshipCluster,
    RelationshipError,
    RelationshipErrorType,
    RelationshipReport,
    RelationshipSourceAdapter,
    RelationshipType,
    SemanticRelationship,
    SemanticRelationshipExtractor,
)
from .structural_marker_extractor import (
    StructuralMarker,
    StructuralMarkerExtractor,
    StructureType,
)
from .temporal_consistency_extractor import (
    ConsistencyReport,
    CSVTemporalAdapter,
    DictTemporalAdapter,
    JSONTemporalAdapter,
    TemporalConsistencyExtractor,
    TemporalError,
    TemporalErrorType,
    TemporalGap,
    TemporalOverlap,
    TemporalSourceAdapter,
    TimeInterval,
)

__version__ = "2.0.0"

__all__ = [
    # Base framework
    "EmpiricallyCalibrated",
    "PatternBasedExtractor",
    "ExtractionPattern",
    "ExtractionResult",
    # Extractors
    "FinancialChainExtractor",
    "CausalVerbExtractor",
    "InstitutionalNERExtractor",
    "QuantitativeTripletExtractor",
    "NormativeReferenceExtractor",
    "StructuralMarkerExtractor",
    # Data structures
    "FinancialChain",
    "CausalLink",
    "InstitutionalEntity",
    "QuantitativeTriplet",
    "NormativeReference",
    "StructuralMarker",
    "StructureType",
    # Convenience functions
    "extract_financial_chains",
    "extract_causal_links",
    # Validation
    "ExtractorValidator",
    "ValidationMetrics",
    # Utilities
    "load_all_extractors_from_calibration",
    "generate_test_suite",
    # Hierarchy Extractor
    "ProgrammaticHierarchyExtractor",
    "HierarchySourceAdapter",
    "DictSourceAdapter",
    "JSONFileSourceAdapter",
    "CSVSourceAdapter",
    "HierarchyNode",
    "HierarchyError",
    "HierarchyErrorType",
    # Population Disaggregation Extractor
    "PopulationDisaggregationExtractor",
    "PopulationSourceAdapter",
    "DictPopulationAdapter",
    "CSVPopulationAdapter",
    "JSONPopulationAdapter",
    "DisaggregationAxis",
    "DisaggregationError",
    "DisaggregationErrorType",
    "DisaggregationReport",
    "PopulationGroup",
    # Temporal Consistency Extractor
    "TemporalConsistencyExtractor",
    "TemporalSourceAdapter",
    "DictTemporalAdapter",
    "CSVTemporalAdapter",
    "JSONTemporalAdapter",
    "TemporalError",
    "TemporalErrorType",
    "TimeInterval",
    "TemporalGap",
    "TemporalOverlap",
    "ConsistencyReport",
    # Semantic Relationship Extractor
    "SemanticRelationshipExtractor",
    "RelationshipSourceAdapter",
    "DictRelationshipAdapter",
    "CSVRelationshipAdapter",
    "JSONRelationshipAdapter",
    "RelationshipType",
    "RelationshipError",
    "RelationshipErrorType",
    "SemanticRelationship",
    "RelationshipCluster",
    "RelationshipReport",
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
            logger.debug(
                f"✓ FinancialChainExtractor smoke test passed ({len(result.matches)} matches)"
            )
    except Exception as e:
        logger.warning(f"Extractor smoke test failed: {e}")


# Optionally run validation on import (disabled by default for performance)
# _run_quick_validation()
