# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/__init__.py

from .base_consumer import BaseConsumer, ConsumerHealth

# Phase 0 consumers
from .phase0.phase0_90_02_bootstrap import Phase0BootstrapConsumer
from .phase0.providers import Phase0ProvidersConsumer
from .phase0.wiring_types import Phase0WiringTypesConsumer

# Phase 1 consumers
from .phase1.phase1_11_00_signal_enrichment import Phase1SignalEnrichmentConsumer
from .phase1.phase1_13_00_cpp_ingestion import Phase1CppIngestionConsumer

# Phase 2 consumers
from .phase2.phase2_factory_consumer import Phase2FactoryConsumer
from .phase2.phase2_evidence_consumer import Phase2EvidenceConsumer
from .phase2.phase2_contract_consumer import Phase2ContractConsumer
from .phase2.phase2_executor_consumer import Phase2ExecutorConsumer

# Phase 3 consumers
from .phase3.phase3_10_00_signal_enriched_scoring import Phase3SignalEnrichedScoringConsumer

# Phase 4 consumers
from .phase4.phase4_aggregation_consumer import Phase4AggregationConsumer

# Phase 5 consumers
from .phase5.phase5_uncertainty_consumer import Phase5UncertaintyConsumer

# Phase 6 consumers
from .phase6.phase6_configuration_consumer import Phase6ConfigurationConsumer

# Phase 7 consumers
from .phase7.phase7_meso_consumer import Phase7MesoConsumer

# Phase 8 consumers
from .phase8.phase8_30_00_signal_enriched_recommendations import Phase8SignalEnrichedRecommendationsConsumer

# Phase 9 consumers
from .phase9.phase9_reporting_consumer import Phase9ReportingConsumer

__all__ = [
    "BaseConsumer",
    "ConsumerHealth",
    # Phase 0
    "Phase0BootstrapConsumer",
    "Phase0ProvidersConsumer",
    "Phase0WiringTypesConsumer",
    # Phase 1
    "Phase1SignalEnrichmentConsumer",
    "Phase1CppIngestionConsumer",
    # Phase 2
    "Phase2FactoryConsumer",
    "Phase2EvidenceConsumer",
    "Phase2ContractConsumer",
    "Phase2ExecutorConsumer",
    # Phase 3
    "Phase3SignalEnrichedScoringConsumer",
    # Phase 4
    "Phase4AggregationConsumer",
    # Phase 5
    "Phase5UncertaintyConsumer",
    # Phase 6
    "Phase6ConfigurationConsumer",
    # Phase 7
    "Phase7MesoConsumer",
    # Phase 8
    "Phase8SignalEnrichedRecommendationsConsumer",
    # Phase 9
    "Phase9ReportingConsumer",
]
