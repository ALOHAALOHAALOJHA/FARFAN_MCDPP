"""Dynamic class registry for orchestrator method execution."""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

class ClassRegistryError(RuntimeError):
    """Raised when one or more classes cannot be loaded."""

# Map of orchestrator-facing class names to their import paths.
# CORRECTED: Changed from non-existent 'farfan_core' to actual 'methods_dispensary' package
_CLASS_PATHS: Mapping[str, str] = {
    # Policy Processing
    "IndustrialPolicyProcessor": "methods_dispensary.policy_processor.IndustrialPolicyProcessor",
    "PolicyTextProcessor": "methods_dispensary.policy_processor.PolicyTextProcessor",
    "BayesianEvidenceScorer": "methods_dispensary.policy_processor.BayesianEvidenceScorer",
    
    # Contradiction Detection
    "PolicyContradictionDetector": "methods_dispensary.contradiction_deteccion.PolicyContradictionDetector",
    "TemporalLogicVerifier": "methods_dispensary.contradiction_deteccion.TemporalLogicVerifier",
    "BayesianConfidenceCalculator": "methods_dispensary.contradiction_deteccion.BayesianConfidenceCalculator",
    
    # Financial Analysis (derek_beach.py)
    "PDETMunicipalPlanAnalyzer": "methods_dispensary.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer",
    "CDAFFramework": "methods_dispensary.derek_beach.CDAFFramework",
    "CausalExtractor": "methods_dispensary.derek_beach.CausalExtractor",
    "OperationalizationAuditor": "methods_dispensary.derek_beach.OperationalizationAuditor",
    "FinancialAuditor": "methods_dispensary.derek_beach.FinancialAuditor",
    "BayesianMechanismInference": "methods_dispensary.derek_beach.BayesianMechanismInference",
    "BayesianCounterfactualAuditor": "methods_dispensary.derek_beach.BayesianCounterfactualAuditor",
    
    # Embedding & Semantic Processing
    "BayesianNumericalAnalyzer": "methods_dispensary.embedding_policy.BayesianNumericalAnalyzer",
    "PolicyAnalysisEmbedder": "methods_dispensary.embedding_policy.PolicyAnalysisEmbedder",
    "AdvancedSemanticChunker": "methods_dispensary.embedding_policy.AdvancedSemanticChunker",
    "EmbeddingPolicyProducer": "methods_dispensary.embedding_policy.EmbeddingPolicyProducer",
    # SemanticChunker is an alias maintained for backwards compatibility.
    "SemanticChunker": "methods_dispensary.embedding_policy.AdvancedSemanticChunker",
    "SemanticProcessor": "methods_dispensary.semantic_chunking_policy.SemanticProcessor",
    "SemanticChunkingProducer": "methods_dispensary.semantic_chunking_policy.SemanticChunkingProducer",
    
    # Analyzer One
    "SemanticAnalyzer": "methods_dispensary.analyzer_one.SemanticAnalyzer",
    "PerformanceAnalyzer": "methods_dispensary.analyzer_one.PerformanceAnalyzer",
    "TextMiningEngine": "methods_dispensary.analyzer_one.TextMiningEngine",
    "MunicipalOntology": "methods_dispensary.analyzer_one.MunicipalOntology",
    
    # Teoria de Cambio
    "TeoriaCambio": "methods_dispensary.teoria_cambio.TeoriaCambio",
    "AdvancedDAGValidator": "methods_dispensary.teoria_cambio.AdvancedDAGValidator",
    "IndustrialGradeValidator": "methods_dispensary.teoria_cambio.IndustrialGradeValidator",
    
    # Derek Beach - Additional Classes
    "BeachEvidentialTest": "methods_dispensary.derek_beach.BeachEvidentialTest",
    "ConfigLoader": "methods_dispensary.derek_beach.ConfigLoader",
    "PDFProcessor": "methods_dispensary.derek_beach.PDFProcessor",
    "ReportingEngine": "methods_dispensary.derek_beach.ReportingEngine",
    "BayesFactorTable": "methods_dispensary.derek_beach.BayesFactorTable",
    "AdaptivePriorCalculator": "methods_dispensary.derek_beach.AdaptivePriorCalculator",
    "HierarchicalGenerativeModel": "methods_dispensary.derek_beach.HierarchicalGenerativeModel",
    
    # Evidence Nexus (replaced EvidenceAssembler)
    "EvidenceNexus": "canonic_phases.Phase_two.evidence_nexus.EvidenceNexus",
    "EvidenceAssembler": "canonic_phases.Phase_two.evidence_nexus.EvidenceNexus",  # Alias for backwards compatibility
    
    # Executors (in canonic_phases/Phase_two/executors.py)
    "D1_Q1_QuantitativeBaselineExtractor": "canonic_phases.Phase_two.executors.D1_Q1_QuantitativeBaselineExtractor",
    "D1_Q2_ProblemDimensioningAnalyzer": "canonic_phases.Phase_two.executors.D1_Q2_ProblemDimensioningAnalyzer",
    
    # Additional classes that may be referenced in contracts
    "MechanismPartExtractor": "methods_dispensary.derek_beach.MechanismPartExtractor",
    "CausalInferenceSetup": "methods_dispensary.derek_beach.CausalInferenceSetup",
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
                "torch", "tensorflow", "pyarrow", "camelot",
                "sentence_transformers", "transformers", "spacy",
                "pymc", "arviz", "dowhy", "econml"
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
