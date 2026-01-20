"""
DEPRECATED: This module is deprecated as of 2026-01-19.

All functionality has been consolidated into:
    src/farfan_pipeline/orchestration/orchestrator.py (UnifiedOrchestrator)

Migration:
    Instead of:
        from farfan_pipeline.infrastructure.extractors.extractor_orchestrator import ExtractorOrchestrator

    Use:
        from farfan_pipeline.orchestration import UnifiedOrchestrator

This file will be removed in version 3.0.0.

See: docs/sisas_unification/MIGRATION_CHECKLIST.md

---
Original Documentation (preserved for reference):

Extractor Orchestrator - SISAS 2.0 Integration Layer

Connects existing extractors (MC01-MC10) with the Signal Distribution Orchestrator.
Serves as the bridge between legacy extraction logic and the new signal-based architecture.

Architecture:
    Document → ExtractorOrchestrator → [MC01-MC10 Extractors] → Signals → SDO → Phase Consumers

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
Date: 2026-01-14
"""
import warnings
warnings.warn(
    "extractor_orchestrator is deprecated. Use UnifiedOrchestrator instead.",
    DeprecationWarning,
    stacklevel=2
)

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# SISAS 2.0 Core imports
try:
    from canonic_questionnaire_central.core.signal import (
        Signal, SignalType, SignalScope, SignalProvenance
    )
    from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
        SignalDistributionOrchestrator
    )
    SISAS_AVAILABLE = True
except ImportError:
    SISAS_AVAILABLE = False

# Existing extractor imports
from .structural_marker_extractor import StructuralMarkerExtractor
from .quantitative_triplet_extractor import QuantitativeTripletExtractor
from .normative_reference_extractor import NormativeReferenceExtractor
from .programmatic_hierarchy_extractor import ProgrammaticHierarchyExtractor
from .financial_chain_extractor import FinancialChainExtractor
from .population_disaggregation_extractor import PopulationDisaggregationExtractor
from .temporal_consistency_extractor import TemporalConsistencyExtractor
from .causal_verb_extractor import CausalVerbExtractor
from .institutional_ner_extractor import InstitutionalNERExtractor
from .semantic_relationship_extractor import SemanticRelationshipExtractor

logger = logging.getLogger(__name__)


# ============================================================================
# EXTRACTOR MAPPING (MC01-MC10 to SignalType)
# ============================================================================

EXTRACTOR_SIGNAL_MAP = {
    "MC01": {
        "signal_type": SignalType.MC01_STRUCTURAL if SISAS_AVAILABLE else "MC01",
        "extractor_class": StructuralMarkerExtractor,
        "capabilities": ["STRUCTURAL_PARSING", "SECTION_DETECTION"],
        "empirical_availability": 0.92,
        "slot_prefix": "D3"
    },
    "MC02": {
        "signal_type": SignalType.MC02_QUANTITATIVE if SISAS_AVAILABLE else "MC02",
        "extractor_class": QuantitativeTripletExtractor,
        "capabilities": ["TRIPLET_EXTRACTION", "NUMERIC_PARSING"],
        "empirical_availability": 0.78,
        "slot_prefix": "D1"
    },
    "MC03": {
        "signal_type": SignalType.MC03_NORMATIVE if SISAS_AVAILABLE else "MC03",
        "extractor_class": NormativeReferenceExtractor,
        "capabilities": ["NORMATIVE_LOOKUP", "CITATION_PARSING"],
        "empirical_availability": 0.85,
        "slot_prefix": "D5"
    },
    "MC04": {
        "signal_type": SignalType.MC04_PROGRAMMATIC if SISAS_AVAILABLE else "MC04",
        "extractor_class": ProgrammaticHierarchyExtractor,
        "capabilities": ["HIERARCHY_PARSING", "TREE_CONSTRUCTION"],
        "empirical_availability": 0.71,
        "slot_prefix": "D4"
    },
    "MC05": {
        "signal_type": SignalType.MC05_FINANCIAL if SISAS_AVAILABLE else "MC05",
        "extractor_class": FinancialChainExtractor,
        "capabilities": ["NUMERIC_PARSING", "FINANCIAL_ANALYSIS", "CURRENCY_NORMALIZATION"],
        "empirical_availability": 0.85,
        "slot_prefix": "D1"
    },
    "MC06": {
        "signal_type": SignalType.MC06_POPULATION if SISAS_AVAILABLE else "MC06",
        "extractor_class": PopulationDisaggregationExtractor,
        "capabilities": ["POPULATION_PARSING", "DEMOGRAPHIC_ANALYSIS"],
        "empirical_availability": 0.65,
        "slot_prefix": "D2"
    },
    "MC07": {
        "signal_type": SignalType.MC07_TEMPORAL if SISAS_AVAILABLE else "MC07",
        "extractor_class": TemporalConsistencyExtractor,
        "capabilities": ["TEMPORAL_PARSING", "DATE_NORMALIZATION"],
        "empirical_availability": 0.88,
        "slot_prefix": "D4"
    },
    "MC08": {
        "signal_type": SignalType.MC08_CAUSAL if SISAS_AVAILABLE else "MC08",
        "extractor_class": CausalVerbExtractor,
        "capabilities": ["CAUSAL_INFERENCE", "GRAPH_CONSTRUCTION", "VERB_ANALYSIS"],
        "empirical_availability": 0.72,
        "slot_prefix": "D6"
    },
    "MC09": {
        "signal_type": SignalType.MC09_INSTITUTIONAL if SISAS_AVAILABLE else "MC09",
        "extractor_class": InstitutionalNERExtractor,
        "capabilities": ["NER_EXTRACTION", "ENTITY_RESOLUTION", "COREFERENCE"],
        "empirical_availability": 0.68,
        "slot_prefix": "D2"
    },
    "MC10": {
        "signal_type": SignalType.MC10_SEMANTIC if SISAS_AVAILABLE else "MC10",
        "extractor_class": SemanticRelationshipExtractor,
        "capabilities": ["SEMANTIC_SIMILARITY", "EMBEDDING_LOOKUP"],
        "empirical_availability": 0.55,
        "slot_prefix": "D6"
    },
}


@dataclass
class ExtractionContext:
    """Context for extraction operations."""
    source_file: str
    policy_area: str = "UNKNOWN"
    document_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_file": self.source_file,
            "policy_area": self.policy_area,
            "document_id": self.document_id,
            "metadata": self.metadata
        }


@dataclass
class OrchestrationResult:
    """Result of full extraction orchestration."""
    document_id: str
    extractors_run: int
    signals_created: int
    signals_delivered: int
    signals_rejected: int
    dead_letters: int
    extraction_time_ms: float
    extractor_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "extractors_run": self.extractors_run,
            "signals_created": self.signals_created,
            "signals_delivered": self.signals_delivered,
            "signals_rejected": self.signals_rejected,
            "dead_letters": self.dead_letters,
            "extraction_time_ms": round(self.extraction_time_ms, 2),
            "extractor_results": self.extractor_results,
            "errors": self.errors
        }


class ExtractorOrchestrator:
    """
    Orchestrates all MC01-MC10 extractors and dispatches results through SDO.
    
    This is the main entry point for document extraction in SISAS 2.0.
    
    Usage:
        resolver = CanonicalQuestionnaireResolver()
        orchestrator = ExtractorOrchestrator(sdo=resolver.sdo)
        
        result = orchestrator.process_document(
            text="...",
            context=ExtractionContext(source_file="doc.pdf", policy_area="PA01")
        )
        
        print(f"Signals delivered: {result.signals_delivered}")
    """
    
    def __init__(
        self,
        sdo: Optional[SignalDistributionOrchestrator] = None,
        extractors: Optional[List[str]] = None,
        parallel: bool = True,
        max_workers: int = 4
    ):
        """
        Initialize extractor orchestrator.
        
        Args:
            sdo: Signal Distribution Orchestrator (required for signal dispatch)
            extractors: List of extractor IDs to use (default: all MC01-MC10)
            parallel: Run extractors in parallel (default: True)
            max_workers: Max parallel workers (default: 4)
        """
        self.sdo = sdo
        self.parallel = parallel
        self.max_workers = max_workers
        
        # Initialize specified extractors or all
        extractor_ids = extractors or list(EXTRACTOR_SIGNAL_MAP.keys())
        self.extractors: Dict[str, Any] = {}
        
        for mc_id in extractor_ids:
            if mc_id in EXTRACTOR_SIGNAL_MAP:
                config = EXTRACTOR_SIGNAL_MAP[mc_id]
                try:
                    self.extractors[mc_id] = {
                        "instance": config["extractor_class"](),
                        "config": config
                    }
                except Exception as e:
                    logger.warning(f"Failed to initialize {mc_id}: {e}")
        
        logger.info(
            "extractor_orchestrator_initialized",
            extractors=list(self.extractors.keys()),
            parallel=parallel,
            sdo_enabled=sdo is not None
        )
    
    def process_document(
        self,
        text: str,
        context: ExtractionContext
    ) -> OrchestrationResult:
        """
        Process document through all extractors and dispatch signals.
        
        Args:
            text: Document text to process
            context: Extraction context with metadata
            
        Returns:
            OrchestrationResult with all extraction and dispatch metrics
        """
        start_time = time.perf_counter()
        
        result = OrchestrationResult(
            document_id=context.document_id or f"doc_{int(time.time())}",
            extractors_run=0,
            signals_created=0,
            signals_delivered=0,
            signals_rejected=0,
            dead_letters=0,
            extraction_time_ms=0.0
        )
        
        if self.parallel:
            self._process_parallel(text, context, result)
        else:
            self._process_sequential(text, context, result)
        
        result.extraction_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Get dead letter count from SDO
        if self.sdo:
            sdo_metrics = self.sdo.get_metrics()
            result.dead_letters = sdo_metrics.get("dead_letters", 0)
        
        logger.info(
            "document_processed",
            document_id=result.document_id,
            extractors_run=result.extractors_run,
            signals_created=result.signals_created,
            signals_delivered=result.signals_delivered,
            extraction_time_ms=result.extraction_time_ms
        )
        
        return result
    
    def _process_sequential(
        self,
        text: str,
        context: ExtractionContext,
        result: OrchestrationResult
    ) -> None:
        """Process extractors sequentially."""
        for mc_id, extractor_data in self.extractors.items():
            try:
                self._run_extractor(mc_id, extractor_data, text, context, result)
            except Exception as e:
                result.errors.append(f"{mc_id}: {str(e)}")
                logger.error(f"Extractor {mc_id} failed: {e}")
    
    def _process_parallel(
        self,
        text: str,
        context: ExtractionContext,
        result: OrchestrationResult
    ) -> None:
        """Process extractors in parallel."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for mc_id, extractor_data in self.extractors.items():
                future = executor.submit(
                    self._run_extractor_safe,
                    mc_id, extractor_data, text, context
                )
                futures[future] = mc_id
            
            for future in as_completed(futures):
                mc_id = futures[future]
                try:
                    extractor_result = future.result()
                    if extractor_result:
                        result.extractors_run += 1
                        result.signals_created += extractor_result.get("signals_created", 0)
                        result.signals_delivered += extractor_result.get("signals_delivered", 0)
                        result.signals_rejected += extractor_result.get("signals_rejected", 0)
                        result.extractor_results[mc_id] = extractor_result
                except Exception as e:
                    result.errors.append(f"{mc_id}: {str(e)}")
    
    def _run_extractor_safe(
        self,
        mc_id: str,
        extractor_data: Dict[str, Any],
        text: str,
        context: ExtractionContext
    ) -> Optional[Dict[str, Any]]:
        """Run extractor with error handling (for parallel execution)."""
        try:
            temp_result = OrchestrationResult(
                document_id=context.document_id or "",
                extractors_run=0,
                signals_created=0,
                signals_delivered=0,
                signals_rejected=0,
                dead_letters=0,
                extraction_time_ms=0.0
            )
            self._run_extractor(mc_id, extractor_data, text, context, temp_result)
            return {
                "signals_created": temp_result.signals_created,
                "signals_delivered": temp_result.signals_delivered,
                "signals_rejected": temp_result.signals_rejected
            }
        except Exception as e:
            logger.error(f"Extractor {mc_id} failed: {e}")
            return None
    
    def _run_extractor(
        self,
        mc_id: str,
        extractor_data: Dict[str, Any],
        text: str,
        context: ExtractionContext,
        result: OrchestrationResult
    ) -> None:
        """Run single extractor and dispatch signals."""
        instance = extractor_data["instance"]
        config = extractor_data["config"]
        
        # Run extraction
        extraction_result = instance.extract(text)
        result.extractors_run += 1
        
        if not extraction_result or not extraction_result.matches:
            return
        
        # Convert to signals and dispatch
        for match in extraction_result.matches:
            signal = self._create_signal(mc_id, config, match, context)
            if signal:
                result.signals_created += 1
                
                if self.sdo:
                    delivered = self.sdo.dispatch(signal)
                    if delivered:
                        result.signals_delivered += 1
                    else:
                        result.signals_rejected += 1
    
    def _create_signal(
        self,
        mc_id: str,
        config: Dict[str, Any],
        match: Dict[str, Any],
        context: ExtractionContext
    ) -> Optional[Signal]:
        """Create Signal from extraction match."""
        if not SISAS_AVAILABLE:
            return None
        
        try:
            # Determine slot based on match and config
            slot = f"{config['slot_prefix']}-Q1"  # Default, can be refined
            
            scope = SignalScope(
                phase="phase_01",
                policy_area=context.policy_area,
                slot=slot
            )
            
            provenance = SignalProvenance(
                extractor=f"ExtractorOrchestrator.{mc_id}",
                source_file=context.source_file,
                extraction_pattern=match.get("pattern_id", "UNKNOWN")
            )
            
            signal = Signal.create(
                signal_type=config["signal_type"],
                scope=scope,
                payload=match,
                provenance=provenance,
                capabilities_required=config["capabilities"],
                empirical_availability=config["empirical_availability"],
                enrichment=True
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Failed to create signal for {mc_id}: {e}")
            return None
    
    def get_extractor_stats(self) -> Dict[str, Any]:
        """Get statistics about available extractors."""
        return {
            "total_extractors": len(self.extractors),
            "extractor_ids": list(self.extractors.keys()),
            "parallel_enabled": self.parallel,
            "max_workers": self.max_workers,
            "sdo_connected": self.sdo is not None
        }


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def create_orchestrator_from_resolver(resolver) -> ExtractorOrchestrator:
    """
    Create ExtractorOrchestrator from an existing resolver.
    
    Usage:
        from canonic_questionnaire_central import CanonicalQuestionnaireResolver
        from farfan_pipeline.infrastructure.extractors.extractor_orchestrator import (
            create_orchestrator_from_resolver, ExtractionContext
        )
        
        resolver = CanonicalQuestionnaireResolver()
        orchestrator = create_orchestrator_from_resolver(resolver)
        
        result = orchestrator.process_document(
            text="...",
            context=ExtractionContext(source_file="doc.pdf", policy_area="PA01")
        )
    """
    sdo = getattr(resolver, 'sdo', None)
    return ExtractorOrchestrator(sdo=sdo)


__all__ = [
    "ExtractorOrchestrator",
    "ExtractionContext", 
    "OrchestrationResult",
    "create_orchestrator_from_resolver",
    "EXTRACTOR_SIGNAL_MAP"
]
