"""Dynamic class registry for orchestrator method execution.

Module: phase2_10_01_class_registry
PHASE_LABEL: Phase 2
Sequence: X
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 2
__stage__ = 10
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"



from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


class ClassRegistryError(RuntimeError):
    """Raised when one or more classes cannot be loaded."""


# Map of orchestrator-facing class names to their import paths.
# CORRECTED: Using actual package path farfan_pipeline.methods
_CLASS_PATHS: Mapping[str, str] = {
    # Policy Processing
    "IndustrialPolicyProcessor": "farfan_pipeline.methods.policy_processor.IndustrialPolicyProcessor",
    "PolicyTextProcessor": "farfan_pipeline.methods.policy_processor.PolicyTextProcessor",
    "BayesianEvidenceScorer": "farfan_pipeline.methods.policy_processor.BayesianEvidenceScorer",
    "_FallbackTemporalVerifier": "farfan_pipeline.methods.policy_processor._FallbackTemporalVerifier",
    # Contradiction Detection
    "PolicyContradictionDetector": "farfan_pipeline.methods.contradiction_deteccion.PolicyContradictionDetector",
    "TemporalLogicVerifier": "farfan_pipeline.methods.contradiction_deteccion.TemporalLogicVerifier",
    "BayesianConfidenceCalculator": "farfan_pipeline.methods.contradiction_deteccion.BayesianConfidenceCalculator",
    "SemanticValidator": "farfan_pipeline.methods.contradiction_deteccion.SemanticValidator",
    "ContradictionDominator": "farfan_pipeline.methods.contradiction_deteccion.ContradictionDominator",
    "LogicalConsistencyChecker": "farfan_pipeline.methods.contradiction_deteccion.LogicalConsistencyChecker",
    # Financial Analysis
    "PDETMunicipalPlanAnalyzer": "farfan_pipeline.methods.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer",
    "FinancialAggregator": "farfan_pipeline.methods.financiero_viabilidad_tablas.FinancialAggregator",
    # Derek Beach
    "CDAFFramework": "farfan_pipeline.methods.derek_beach.CDAFFramework",
    "CausalExtractor": "farfan_pipeline.methods.derek_beach.CausalExtractor",
    "OperationalizationAuditor": "farfan_pipeline.methods.derek_beach.OperationalizationAuditor",
    "FinancialAuditor": "farfan_pipeline.methods.derek_beach.FinancialAuditor",
    "BayesianMechanismInference": "farfan_pipeline.methods.derek_beach.BayesianMechanismInference",
    "BayesianCounterfactualAuditor": "farfan_pipeline.methods.derek_beach.BayesianCounterfactualAuditor",
    "BeachEvidentialTest": "farfan_pipeline.methods.derek_beach.BeachEvidentialTest",
    "ConfigLoader": "farfan_pipeline.methods.derek_beach.ConfigLoader",
    "PDFProcessor": "farfan_pipeline.methods.derek_beach.PDFProcessor",
    "ReportingEngine": "farfan_pipeline.methods.derek_beach.ReportingEngine",
    "BayesFactorTable": "farfan_pipeline.methods.derek_beach.BayesFactorTable",
    "AdaptivePriorCalculator": "farfan_pipeline.methods.derek_beach.AdaptivePriorCalculator",
    "HierarchicalGenerativeModel": "farfan_pipeline.methods.derek_beach.HierarchicalGenerativeModel",
    "MechanismPartExtractor": "farfan_pipeline.methods.derek_beach.MechanismPartExtractor",
    "CausalInferenceSetup": "farfan_pipeline.methods.derek_beach.CausalInferenceSetup",
    "DerekBeachProducer": "farfan_pipeline.methods.derek_beach.DerekBeachProducer",
    # Embedding & Semantic Processing
    "BayesianNumericalAnalyzer": "farfan_pipeline.methods.embedding_policy.BayesianNumericalAnalyzer",
    "PolicyAnalysisEmbedder": "farfan_pipeline.methods.embedding_policy.PolicyAnalysisEmbedder",
    "AdvancedSemanticChunker": "farfan_pipeline.methods.embedding_policy.AdvancedSemanticChunker",
    "EmbeddingPolicyProducer": "farfan_pipeline.methods.embedding_policy.EmbeddingPolicyProducer",
    "SemanticChunker": "farfan_pipeline.methods.embedding_policy.AdvancedSemanticChunker",
    # Semantic Chunking
    "SemanticProcessor": "farfan_pipeline.methods.semantic_chunking_policy.SemanticProcessor",
    "SemanticChunkingProducer": "farfan_pipeline.methods.semantic_chunking_policy.SemanticChunkingProducer",
    "PolicyDocumentAnalyzer": "farfan_pipeline.methods.semantic_chunking_policy.PolicyDocumentAnalyzer",
    "BayesianEvidenceIntegrator": "farfan_pipeline.methods.semantic_chunking_policy.BayesianEvidenceIntegrator",
    # Analyzer One
    "SemanticAnalyzer": "farfan_pipeline.methods.analyzer_one.SemanticAnalyzer",
    "PerformanceAnalyzer": "farfan_pipeline.methods.analyzer_one.PerformanceAnalyzer",
    "TextMiningEngine": "farfan_pipeline.methods.analyzer_one.TextMiningEngine",
    "MunicipalOntology": "farfan_pipeline.methods.analyzer_one.MunicipalOntology",
    "DocumentProcessor": "farfan_pipeline.methods.analyzer_one.DocumentProcessor",
    # Teoria de Cambio
    "TeoriaCambio": "farfan_pipeline.methods.teoria_cambio.TeoriaCambio",
    "AdvancedDAGValidator": "farfan_pipeline.methods.teoria_cambio.AdvancedDAGValidator",
    "IndustrialGradeValidator": "farfan_pipeline.methods.teoria_cambio.IndustrialGradeValidator",
    "DAGCycleDetector": "farfan_pipeline.methods.teoria_cambio.DAGCycleDetector",
    # Bayesian Multilevel System
    "DispersionEngine": "farfan_pipeline.methods.bayesian_multilevel_system.DispersionEngine",
    "PeerCalibrator": "farfan_pipeline.methods.bayesian_multilevel_system.PeerCalibrator",
    "ContradictionScanner": "farfan_pipeline.methods.bayesian_multilevel_system.ContradictionScanner",
    "BayesianPortfolioComposer": "farfan_pipeline.methods.bayesian_multilevel_system.BayesianPortfolioComposer",
    "BayesianEvidenceExtractor": "farfan_pipeline.methods.bayesian_multilevel_system.BayesianEvidenceExtractor",
    # Evidence Nexus (Phase Two)
    "EvidenceNexus": "farfan_pipeline.phases.Phase_2.evidence_nexus.EvidenceNexus",
    "EvidenceAssembler": "farfan_pipeline.phases.Phase_2.evidence_nexus.EvidenceNexus",
}


def build_class_registry() -> dict[str, type[object]]:
    """Return a mapping of class names to loaded types, validating availability.

    Classes that depend on optional dependencies (e.g., torch) are skipped
    gracefully if those dependencies are not available.
    """
    resolved: dict[str, type[object]] = {}
    missing: dict[str, str] = {}
    skipped_optional: dict[str, str] = {}

    for name, path in _CLASS_PATHS.items():
        module_name, _, class_name = path.rpartition(".")
        if not module_name:
            missing[name] = path
            continue
        try:
            module = import_module(module_name)
        except ImportError as exc:
            exc_str = str(exc)
            # Check if this is an optional dependency error
            optional_deps = [
                "torch",
                "tensorflow",
                "pyarrow",
                "camelot",
                "sentence_transformers",
                "transformers",
                "spacy",
                "pymc",
                "arviz",
                "dowhy",
                "econml",
            ]
            if any(opt_dep in exc_str for opt_dep in optional_deps):
                # Mark as skipped optional rather than missing
                skipped_optional[name] = f"{path} (optional dependency: {exc})"
            else:
                missing[name] = f"{path} (import error: {exc})"
            continue
        try:
            attr = getattr(module, class_name)
        except AttributeError:
            missing[name] = f"{path} (attribute missing)"
        else:
            if not isinstance(attr, type):
                missing[name] = f"{path} (attribute is not a class: {type(attr).__name__})"
            else:
                resolved[name] = attr

    # Log skipped optional dependencies
    if skipped_optional:
        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            f"Skipped {len(skipped_optional)} optional classes due to missing dependencies: "
            f"{', '.join(skipped_optional.keys())}"
        )

    if missing:
        formatted = ", ".join(f"{name}: {reason}" for name, reason in missing.items())
        raise ClassRegistryError(f"Failed to load orchestrator classes: {formatted}")
    return resolved


def get_class_paths() -> Mapping[str, str]:
    """Expose the raw class path mapping for diagnostics."""
    return _CLASS_PATHS
