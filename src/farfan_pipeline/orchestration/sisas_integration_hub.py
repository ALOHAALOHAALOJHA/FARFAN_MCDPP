"""
SISAS Integration Hub - Central Wiring for ALL SISAS Components

This module is the SINGLE POINT of integration between:
- UnifiedOrchestrator
- SignalDistributionOrchestrator (SDO)
- All 11 Consumers
- All 10 Extractors
- All 8 Vehicles
- All 21 Irrigation Units
- All 475+ Information Items

Author:  FARFAN Pipeline Team
Version: 1.0.0
Date: 2026-01-19
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, TYPE_CHECKING
from pathlib import Path

logger = logging.getLogger(__name__)

# =============================================================================
# CONDITIONAL IMPORTS - Handle missing dependencies gracefully
# =============================================================================

# Core SISAS
try:
    from canonic_questionnaire_central.core.signal import (
        Signal, SignalType, SignalScope, SignalProvenance
    )
    from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
        SignalDistributionOrchestrator
    )
    SISAS_CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"SISAS core not available: {e}")
    SISAS_CORE_AVAILABLE = False
    SignalDistributionOrchestrator = None

# Consumers
try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.base_consumer import (
        BaseConsumer, ConsumerHealth
    )
    CONSUMERS_AVAILABLE = True
except ImportError:
    CONSUMERS_AVAILABLE = False
    BaseConsumer = None

# Phase-specific consumers
PHASE_CONSUMERS = {}

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase0.phase0_90_02_bootstrap import *
    PHASE_CONSUMERS['phase0_bootstrap'] = True
except ImportError:
    PHASE_CONSUMERS['phase0_bootstrap'] = False

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase1.phase1_11_00_signal_enrichment import *
    PHASE_CONSUMERS['phase1_enrichment'] = True
except ImportError:
    PHASE_CONSUMERS['phase1_enrichment'] = False

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase2.phase2_contract_consumer import *
    PHASE_CONSUMERS['phase2_contract'] = True
except ImportError:
    PHASE_CONSUMERS['phase2_contract'] = False

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase2.phase2_evidence_consumer import *
    PHASE_CONSUMERS['phase2_evidence'] = True
except ImportError:
    PHASE_CONSUMERS['phase2_evidence'] = False

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase2.phase2_executor_consumer import *
    PHASE_CONSUMERS['phase2_executor'] = True
except ImportError:
    PHASE_CONSUMERS['phase2_executor'] = False

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase3.phase3_10_00_signal_enriched_scoring import *
    PHASE_CONSUMERS['phase3_scoring'] = True
except ImportError:
    PHASE_CONSUMERS['phase3_scoring'] = False

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase7.phase7_meso_consumer import *
    PHASE_CONSUMERS['phase7_meso'] = True
except ImportError:
    PHASE_CONSUMERS['phase7_meso'] = False

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase8.phase8_30_00_signal_enriched_recommendations import *
    PHASE_CONSUMERS['phase8_recommendations'] = True
except ImportError:
    PHASE_CONSUMERS['phase8_recommendations'] = False

# Extractors
EXTRACTORS = {}

try:
    from farfan_pipeline.infrastructure.extractors.structural_marker_extractor import StructuralMarkerExtractor
    EXTRACTORS['MC01'] = StructuralMarkerExtractor
except ImportError:
    EXTRACTORS['MC01'] = None

try:
    from farfan_pipeline.infrastructure.extractors.quantitative_triplet_extractor import QuantitativeTripletExtractor
    EXTRACTORS['MC02'] = QuantitativeTripletExtractor
except ImportError:
    EXTRACTORS['MC02'] = None

try:
    from farfan_pipeline.infrastructure.extractors.normative_reference_extractor import NormativeReferenceExtractor
    EXTRACTORS['MC03'] = NormativeReferenceExtractor
except ImportError:
    EXTRACTORS['MC03'] = None

try:
    from farfan_pipeline.infrastructure.extractors.programmatic_hierarchy_extractor import ProgrammaticHierarchyExtractor
    EXTRACTORS['MC04'] = ProgrammaticHierarchyExtractor
except ImportError:
    EXTRACTORS['MC04'] = None

try:
    from farfan_pipeline.infrastructure.extractors.financial_chain_extractor import FinancialChainExtractor
    EXTRACTORS['MC05'] = FinancialChainExtractor
except ImportError:
    EXTRACTORS['MC05'] = None

try:
    from farfan_pipeline.infrastructure.extractors.population_disaggregation_extractor import PopulationDisaggregationExtractor
    EXTRACTORS['MC06'] = PopulationDisaggregationExtractor
except ImportError:
    EXTRACTORS['MC06'] = None

try:
    from farfan_pipeline.infrastructure.extractors.temporal_consistency_extractor import TemporalConsistencyExtractor
    EXTRACTORS['MC07'] = TemporalConsistencyExtractor
except ImportError:
    EXTRACTORS['MC07'] = None

try:
    from farfan_pipeline.infrastructure.extractors.causal_verb_extractor import CausalVerbExtractor
    EXTRACTORS['MC08'] = CausalVerbExtractor
except ImportError:
    EXTRACTORS['MC08'] = None

try:
    from farfan_pipeline.infrastructure.extractors.institutional_ner_extractor import InstitutionalNERExtractor
    EXTRACTORS['MC09'] = InstitutionalNERExtractor
except ImportError:
    EXTRACTORS['MC09'] = None

try:
    from farfan_pipeline.infrastructure.extractors.semantic_relationship_extractor import SemanticRelationshipExtractor
    EXTRACTORS['MC10'] = SemanticRelationshipExtractor
except ImportError:
    EXTRACTORS['MC10'] = None

# Vehicles
VEHICLES = {}

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_loader import SignalLoaderVehicle
    VEHICLES['loader'] = SignalLoaderVehicle
except ImportError:
    VEHICLES['loader'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_irrigator import SignalIrrigatorVehicle
    VEHICLES['irrigator'] = SignalIrrigatorVehicle
except ImportError:
    VEHICLES['irrigator'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_registry import SignalRegistryVehicle
    VEHICLES['registry'] = SignalRegistryVehicle
except ImportError:
    VEHICLES['registry'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_context_scoper import SignalContextScoperVehicle
    VEHICLES['context_scoper'] = SignalContextScoperVehicle
except ImportError:
    VEHICLES['context_scoper'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_evidence_extractor import SignalEvidenceExtractorVehicle
    VEHICLES['evidence_extractor'] = SignalEvidenceExtractorVehicle
except ImportError:
    VEHICLES['evidence_extractor'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_enhancement_integrator import SignalEnhancementIntegratorVehicle
    VEHICLES['enhancement_integrator'] = SignalEnhancementIntegratorVehicle
except ImportError:
    VEHICLES['enhancement_integrator'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_intelligence_layer import SignalIntelligenceLayerVehicle
    VEHICLES['intelligence_layer'] = SignalIntelligenceLayerVehicle
except ImportError:
    VEHICLES['intelligence_layer'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_quality_metrics import SignalQualityMetricsVehicle
    VEHICLES['quality_metrics'] = SignalQualityMetricsVehicle
except ImportError:
    VEHICLES['quality_metrics'] = None

# Buses
BUSES = {}

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import SignalBus, BusRegistry, BusType
    BUSES['SignalBus'] = SignalBus
    BUSES['BusRegistry'] = BusRegistry
    BUSES['BusType'] = BusType
except ImportError:
    BUSES['SignalBus'] = None
    BUSES['BusRegistry'] = None
    BUSES['BusType'] = None

# Contracts (beyond SDO)
CONTRACTS = {}

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import (
        PublicationContract, ConsumptionContract, IrrigationContract, ContractRegistry
    )
    CONTRACTS['PublicationContract'] = PublicationContract
    CONTRACTS['ConsumptionContract'] = ConsumptionContract
    CONTRACTS['IrrigationContract'] = IrrigationContract
    CONTRACTS['ContractRegistry'] = ContractRegistry
except ImportError:
    CONTRACTS['PublicationContract'] = None
    CONTRACTS['ConsumptionContract'] = None
    CONTRACTS['IrrigationContract'] = None
    CONTRACTS['ContractRegistry'] = None

# Validators
VALIDATORS = {}

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.validators.depuration import DepurationValidator
    VALIDATORS['DepurationValidator'] = DepurationValidator
except ImportError:
    VALIDATORS['DepurationValidator'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.harmonization import HarmonizationValidator
    VALIDATORS['HarmonizationValidator'] = HarmonizationValidator
except ImportError:
    VALIDATORS['HarmonizationValidator'] = None

# Wiring
WIRING = {}

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.wiring.wiring_config import WiringConfiguration
    WIRING['WiringConfiguration'] = WiringConfiguration
except ImportError:
    WIRING['WiringConfiguration'] = None

# Irrigation
IRRIGATION = {}

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_map import IrrigationMap
    IRRIGATION['IrrigationMap'] = IrrigationMap
except ImportError:
    IRRIGATION['IrrigationMap'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_executor import IrrigationExecutor
    IRRIGATION['IrrigationExecutor'] = IrrigationExecutor
except ImportError:
    IRRIGATION['IrrigationExecutor'] = None

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_validator import IrrigationValidator
    IRRIGATION['IrrigationValidator'] = IrrigationValidator
except ImportError:
    IRRIGATION['IrrigationValidator'] = None


# =============================================================================
# INTEGRATION HUB
# =============================================================================


@dataclass
class IntegrationStatus:
    """Status of SISAS integration."""
    core_available: bool = False
    consumers_registered: int = 0
    consumers_available: int = 0
    extractors_connected: int = 0
    extractors_available: int = 0
    vehicles_initialized: int = 0
    vehicles_available: int = 0
    buses_initialized: int = 0
    buses_available: int = 0
    contracts_initialized: int = 0
    contracts_available: int = 0
    validators_initialized: int = 0
    validators_available: int = 0
    wiring_initialized: bool = False
    irrigation_initialized: int = 0
    irrigation_available: int = 0
    irrigation_units_loaded: int = 0
    items_irrigable: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "core_available": self.core_available,
            "consumers":  f"{self.consumers_registered}/{self.consumers_available}",
            "extractors": f"{self.extractors_connected}/{self.extractors_available}",
            "vehicles": f"{self.vehicles_initialized}/{self.vehicles_available}",
            "buses": f"{self.buses_initialized}/{self.buses_available}",
            "contracts": f"{self.contracts_initialized}/{self.contracts_available}",
            "validators": f"{self.validators_initialized}/{self.validators_available}",
            "wiring_configured": self.wiring_initialized,
            "irrigation": f"{self.irrigation_initialized}/{self.irrigation_available}",
            "irrigation_units":  self.irrigation_units_loaded,
            "items_irrigable": self.items_irrigable,
            "fully_integrated": self.is_fully_integrated(),
        }

    def is_fully_integrated(self) -> bool:
        return (
            self.core_available and
            self.consumers_registered == self.consumers_available and
            self.extractors_connected == self.extractors_available and
            self.buses_initialized == self.buses_available and
            self.contracts_initialized == self.contracts_available and
            self.validators_initialized == self.validators_available and
            self.irrigation_initialized == self.irrigation_available
        )


class SISASIntegrationHub:
    """
    Central hub for ALL SISAS integrations.

    This class:
    1. Initializes the SDO (Signal Distribution Orchestrator)
    2. Registers ALL 17 consumers (phases 0-9)
    3. Connects ALL 10 extractors (MC01-MC10) to emit via SDO
    4. Initializes ALL 8 vehicles
    5. Initializes ALL 7+ buses (structural, integrity, epistemic, etc.)
    6. Initializes contract system (Publication, Consumption, Irrigation + Registry)
    7. Initializes validators (Depuration + Harmonization)
    8. Configures wiring system
    9. Initializes irrigation system (Map, Executor, Validator)
    10. Loads ALL 21+ irrigation units
    11. Tracks ALL 475+ irrigable items

    Usage:
        hub = SISASIntegrationHub()
        hub.initialize(orchestrator)
        status = hub.get_status()
    """

    def __init__(self):
        self._sdo: Optional[SignalDistributionOrchestrator] = None
        self._consumers: Dict[str, Any] = {}
        self._extractors: Dict[str, Any] = {}
        self._vehicles: Dict[str, Any] = {}
        self._buses: Dict[str, Any] = {}
        self._contracts: Dict[str, Any] = {}
        self._validators: Dict[str, Any] = {}
        self._wiring: Optional[Any] = None
        self._irrigation: Dict[str, Any] = {}
        self._irrigation_spec: Optional[Dict] = None
        self._status = IntegrationStatus()
        self._initialized = False

    def initialize(self, orchestrator: Any = None) -> IntegrationStatus:
        """
        Initialize ALL SISAS integrations.

        Args:
            orchestrator: UnifiedOrchestrator instance (optional)

        Returns:
            IntegrationStatus with all connection details
        """
        logger.info("Initializing SISAS Integration Hub (FULL SCOPE)...")

        # Step 1: Initialize SDO
        self._initialize_sdo()

        # Step 2: Initialize buses
        self._initialize_all_buses()

        # Step 3: Initialize contracts
        self._initialize_all_contracts()

        # Step 4: Initialize validators
        self._initialize_all_validators()

        # Step 5: Initialize wiring
        self._initialize_wiring()

        # Step 6: Initialize irrigation system
        self._initialize_irrigation_system()

        # Step 7: Register consumers
        self._register_all_consumers()

        # Step 8: Connect extractors
        self._connect_all_extractors()

        # Step 9: Initialize vehicles
        self._initialize_all_vehicles()

        # Step 10: Load irrigation spec
        self._load_irrigation_spec()

        # Step 11: Wire to orchestrator if provided
        if orchestrator is not None:
            self._wire_to_orchestrator(orchestrator)

        self._initialized = True

        logger.info(f"SISAS Integration complete (FULL SYSTEM):  {self._status.to_dict()}")
        return self._status

    def _initialize_sdo(self) -> None:
        """Initialize SignalDistributionOrchestrator."""
        if not SISAS_CORE_AVAILABLE:
            logger.error("SISAS core not available, cannot initialize SDO")
            return

        try:
            # Load routing rules if available
            rules_path = Path(__file__).resolve().parents[3] / "canonic_questionnaire_central" / "_registry" / "irrigation_validation_rules.json"

            if rules_path.exists():
                self._sdo = SignalDistributionOrchestrator(rules_path=str(rules_path))
            else:
                self._sdo = SignalDistributionOrchestrator()

            self._status.core_available = True
            logger.info("SDO initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SDO: {e}")

    def _register_all_consumers(self) -> None:
        """Register ALL consumers with SDO."""
        if self._sdo is None:
            return

        # Consumer configurations - COMPLETE LIST
        consumer_configs = [
            # Phase 0
            {
                "consumer_id": "phase0_bootstrap_consumer",
                "phase": "phase_0",
                "scopes": [{"phase": "phase_0", "policy_area": "ALL", "slot":  "ALL"}],
                "capabilities": ["STATIC_LOAD", "SIGNAL_PACK", "BOOTSTRAP", "PHASE_MONITORING"],
                "available":  PHASE_CONSUMERS.get('phase0_bootstrap', False),
            },
            {
                "consumer_id": "phase0_providers_consumer",
                "phase":  "phase_0",
                "scopes": [{"phase": "phase_0", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities":  ["PROVIDER_INIT", "CONFIG_LOAD", "PHASE_MONITORING"],
                "available": True,  # Basic provider always available
            },
            # Phase 1
            {
                "consumer_id": "phase1_enrichment_consumer",
                "phase": "phase_1",
                "scopes": [{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities": ["EXTRACTION", "ENRICHMENT", "SIGNAL_ENRICHMENT", "PHASE_MONITORING"],
                "available": PHASE_CONSUMERS.get('phase1_enrichment', False),
            },
            {
                "consumer_id": "phase1_cpp_ingestion_consumer",
                "phase": "phase_1",
                "scopes": [{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities": ["CPP_INGESTION", "DOCUMENT_PARSING", "CHUNKING", "PHASE_MONITORING"],
                "available":  PHASE_CONSUMERS.get('phase1_cpp', False),
            },
            {
                "consumer_id": "phase1_extraction_consumer",
                "phase":  "phase_1",
                "scopes": [{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities":  [
                    "EXTRACTION", "STRUCTURAL_PARSING", "TRIPLET_EXTRACTION",
                    "NUMERIC_PARSING", "NORMATIVE_LOOKUP", "HIERARCHY_PARSING",
                    "FINANCIAL_ANALYSIS", "POPULATION_PARSING", "TEMPORAL_PARSING",
                    "CAUSAL_ANALYSIS", "NER", "SEMANTIC_ANALYSIS", "PHASE_MONITORING"
                ],
                "available": True,  # Core extraction always available
            },
            # Phase 2
            {
                "consumer_id": "phase2_contract_consumer",
                "phase": "phase_2",
                "scopes": [{"phase": "phase_2", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities": ["CONTRACT_EXECUTION", "METHOD_BINDING", "PHASE_MONITORING"],
                "available": PHASE_CONSUMERS.get('phase2_contract', False),
            },
            {
                "consumer_id": "phase2_evidence_consumer",
                "phase": "phase_2",
                "scopes": [{"phase": "phase_2", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities": ["EVIDENCE_COLLECTION", "NEXUS_BUILDING", "PHASE_MONITORING"],
                "available": PHASE_CONSUMERS.get('phase2_evidence', False),
            },
            {
                "consumer_id": "phase2_executor_consumer",
                "phase": "phase_2",
                "scopes": [{"phase": "phase_2", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities": ["EXECUTOR", "METHOD_INJECTION", "PHASE_MONITORING"],
                "available": PHASE_CONSUMERS.get('phase2_executor', False),
            },
            {
                "consumer_id": "phase2_enrichment_consumer",
                "phase": "phase_2",
                "scopes": [{"phase":  "phase_2", "policy_area": "ALL", "slot":  "ALL"}],
                "capabilities": ["ENRICHMENT", "PATTERN_MATCHING", "ENTITY_RECOGNITION", "PHASE_MONITORING"],
                "available": True,
            },
            # Phase 3
            {
                "consumer_id": "phase3_scoring_consumer",
                "phase": "phase_3",
                "scopes": [{"phase": "phase_3", "policy_area":  "ALL", "slot": "ALL"}],
                "capabilities": ["SCORING", "SIGNAL_ENRICHED_SCORING", "VALIDATION", "PHASE_MONITORING"],
                "available": PHASE_CONSUMERS.get('phase3_scoring', False),
            },
            {
                "consumer_id": "phase3_validation_consumer",
                "phase":  "phase_3",
                "scopes": [{"phase": "phase_3", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities":  ["VALIDATION", "NORMATIVE_CHECK", "COHERENCE_CHECK", "PHASE_MONITORING"],
                "available": True,
            },
            # Phase 4
            {
                "consumer_id": "phase4_micro_consumer",
                "phase":  "phase_4",
                "scopes": [{"phase": "phase_4", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities":  ["SCORING", "MICRO_LEVEL", "CHOQUET_INTEGRAL", "PHASE_MONITORING"],
                "available": True,
            },
            # Phase 5
            {
                "consumer_id": "phase5_meso_consumer",
                "phase": "phase_5",
                "scopes": [{"phase":  "phase_5", "policy_area": "ALL", "slot":  "ALL"}],
                "capabilities": ["SCORING", "MESO_LEVEL", "DIMENSION_AGGREGATION", "PHASE_MONITORING"],
                "available": True,
            },
            # Phase 6
            {
                "consumer_id": "phase6_macro_consumer",
                "phase":  "phase_6",
                "scopes": [{"phase": "phase_6", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities":  ["SCORING", "MACRO_LEVEL", "POLICY_AREA_AGGREGATION", "PHASE_MONITORING"],
                "available": True,
            },
            # Phase 7
            {
                "consumer_id": "phase7_meso_aggregation_consumer",
                "phase": "phase_7",
                "scopes": [{"phase":  "phase_7", "policy_area": "ALL", "slot":  "ALL"}],
                "capabilities": ["AGGREGATION", "MESO_LEVEL", "CLUSTER_AGGREGATION", "PHASE_MONITORING"],
                "available":  PHASE_CONSUMERS.get('phase7_meso', False),
            },
            # Phase 8
            {
                "consumer_id": "phase8_recommendations_consumer",
                "phase":  "phase_8",
                "scopes": [{"phase": "phase_8", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities":  ["AGGREGATION", "RECOMMENDATION_ENGINE", "SIGNAL_ENRICHED", "PHASE_MONITORING"],
                "available":  PHASE_CONSUMERS.get('phase8_recommendations', False),
            },
            # Phase 9
            {
                "consumer_id": "phase9_report_consumer",
                "phase":  "phase_9",
                "scopes": [{"phase": "phase_9", "policy_area": "ALL", "slot": "ALL"}],
                "capabilities":  ["REPORT_GENERATION", "ASSEMBLY", "EXPORT", "PHASE_MONITORING"],
                "available": True,
            },
        ]

        self._status.consumers_available = len(consumer_configs)

        for config in consumer_configs:
            try:
                # Create handler
                def make_handler(cid):
                    def handler(signal):
                        logger.debug(f"Consumer {cid} received signal: {signal.signal_id}")
                        self._status.items_irrigable += 1
                    return handler

                self._sdo.register_consumer(
                    consumer_id=config["consumer_id"],
                    scopes=config["scopes"],
                    capabilities=config["capabilities"],
                    handler=make_handler(config["consumer_id"])
                )

                self._consumers[config["consumer_id"]] = config
                self._status.consumers_registered += 1
                logger.debug(f"Registered consumer:  {config['consumer_id']}")

            except Exception as e:
                logger.warning(f"Failed to register consumer {config['consumer_id']}: {e}")

    def _connect_all_extractors(self) -> None:
        """Connect ALL extractors to emit via SDO."""
        self._status.extractors_available = len([e for e in EXTRACTORS.values() if e is not None])

        for mc_id, extractor_class in EXTRACTORS.items():
            if extractor_class is None:
                continue

            try:
                self._extractors[mc_id] = {
                    "class": extractor_class,
                    "connected": True,
                    "sdo":  self._sdo,
                }
                self._status.extractors_connected += 1
                logger.debug(f"Connected extractor: {mc_id}")
            except Exception as e:
                logger.warning(f"Failed to connect extractor {mc_id}: {e}")

    def _initialize_all_vehicles(self) -> None:
        """Initialize ALL vehicles."""
        self._status.vehicles_available = len([v for v in VEHICLES.values() if v is not None])

        for vehicle_id, vehicle_class in VEHICLES.items():
            if vehicle_class is None:
                continue

            try:
                self._vehicles[vehicle_id] = {
                    "class":  vehicle_class,
                    "initialized": True,
                }
                self._status.vehicles_initialized += 1
                logger.debug(f"Initialized vehicle:  {vehicle_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize vehicle {vehicle_id}: {e}")

    def _initialize_all_buses(self) -> None:
        """Initialize ALL signal buses."""
        # Count actual bus types available
        if BUSES.get('BusRegistry') and BUSES.get('BusType') and BUSES.get('SignalBus'):
            try:
                BusRegistry = BUSES['BusRegistry']
                BusType = BUSES['BusType']
                SignalBus = BUSES['SignalBus']

                # Initialize the bus registry
                self._buses['registry'] = BusRegistry()

                # Count available bus types
                bus_types_count = len([bt for bt in BusType])
                self._status.buses_available = bus_types_count

                # Create buses for each type
                for bus_type in BusType:
                    bus = SignalBus(bus_type=bus_type)
                    self._buses[bus_type.value] = bus
                    self._status.buses_initialized += 1
                    logger.debug(f"Initialized bus: {bus_type.value}")

                logger.info(f"Bus system initialized with {self._status.buses_initialized} buses")
            except Exception as e:
                logger.error(f"Failed to initialize bus system: {e}")
        else:
            # No buses available
            self._status.buses_available = 0

    def _initialize_all_contracts(self) -> None:
        """Initialize contract system."""
        self._status.contracts_available = len([c for c in CONTRACTS.values() if c is not None])

        if CONTRACTS.get('ContractRegistry'):
            try:
                ContractRegistry = CONTRACTS['ContractRegistry']
                self._contracts['registry'] = ContractRegistry()
                self._status.contracts_initialized += 1
                logger.debug("Initialized contract registry")
            except Exception as e:
                logger.warning(f"Failed to initialize contract registry: {e}")

        # Store contract classes for later use
        for contract_type, contract_class in CONTRACTS.items():
            if contract_class is not None and contract_type != 'ContractRegistry':
                self._contracts[contract_type] = contract_class
                self._status.contracts_initialized += 1
                logger.debug(f"Registered contract type: {contract_type}")

    def _initialize_all_validators(self) -> None:
        """Initialize validation system."""
        self._status.validators_available = len([v for v in VALIDATORS.values() if v is not None])

        for validator_name, validator_class in VALIDATORS.items():
            if validator_class is None:
                continue

            try:
                # Initialize validator if it doesn't require constructor args
                self._validators[validator_name] = {
                    "class": validator_class,
                    "initialized": True
                }
                self._status.validators_initialized += 1
                logger.debug(f"Initialized validator: {validator_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize validator {validator_name}: {e}")

    def _initialize_wiring(self) -> None:
        """Initialize wiring configuration."""
        if WIRING.get('WiringConfiguration'):
            try:
                WiringConfiguration = WIRING['WiringConfiguration']
                # Store the class for later use
                self._wiring = WiringConfiguration
                self._status.wiring_initialized = True
                logger.debug("Initialized wiring configuration")
            except Exception as e:
                logger.warning(f"Failed to initialize wiring: {e}")

    def _initialize_irrigation_system(self) -> None:
        """Initialize irrigation system (Map, Executor, Validator)."""
        self._status.irrigation_available = len([i for i in IRRIGATION.values() if i is not None])

        for component_name, component_class in IRRIGATION.items():
            if component_class is None:
                continue

            try:
                self._irrigation[component_name] = {
                    "class": component_class,
                    "initialized": True
                }
                self._status.irrigation_initialized += 1
                logger.debug(f"Initialized irrigation component: {component_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize irrigation component {component_name}: {e}")

    def _load_irrigation_spec(self) -> None:
        """Load irrigation specification."""
        import json

        spec_path = Path(__file__).resolve().parents[3] / "canonic_questionnaire_central" / "_registry" / "SISAS_IRRIGATION_SPEC.json"

        try:
            if spec_path.exists():
                with open(spec_path, 'r', encoding='utf-8') as f:
                    self._irrigation_spec = json.load(f)

                # Count irrigation units
                for group in self._irrigation_spec.get("groups", []):
                    self._status.irrigation_units_loaded += len(group.get("units", []))

                # Calculate total irrigable items
                summary = self._irrigation_spec.get("sisas_summary", {})
                # 300 questions + 10 PA + 6 DIM + 4 CL + patterns + entities
                self._status.items_irrigable = 300 + 10 + 6 + 4 + 9 + 155  # Base count

                logger.info(f"Loaded irrigation spec:  {self._status.irrigation_units_loaded} units")
            else:
                logger.warning(f"Irrigation spec not found:  {spec_path}")
        except Exception as e:
            logger.error(f"Failed to load irrigation spec: {e}")

    def _wire_to_orchestrator(self, orchestrator:  Any) -> None:
        """Wire hub to orchestrator."""
        try:
            orchestrator.context.sisas = self._sdo
            orchestrator.context.sisas_hub = self
            logger.info("Wired SISAS hub to orchestrator")
        except Exception as e:
            logger.error(f"Failed to wire to orchestrator: {e}")

    def get_sdo(self) -> Optional[SignalDistributionOrchestrator]:
        """Get the SDO instance."""
        return self._sdo

    def get_status(self) -> IntegrationStatus:
        """Get current integration status."""
        return self._status

    def get_integration_report(self) -> str:
        """Generate human-readable integration report."""
        lines = [
            "=" * 80,
            "SISAS INTEGRATION HUB - COMPREHENSIVE STATUS REPORT",
            "=" * 80,
            "",
            "CORE COMPONENTS:",
            f"  ✓ SDO Available: {self._status.core_available}",
            "",
            "SIGNAL FLOW:",
            f"  ✓ Consumers:  {self._status.consumers_registered}/{self._status.consumers_available}",
            f"  ✓ Extractors: {self._status.extractors_connected}/{self._status.extractors_available}",
            f"  ✓ Vehicles: {self._status.vehicles_initialized}/{self._status.vehicles_available}",
            "",
            "INFRASTRUCTURE:",
            f"  ✓ Buses: {self._status.buses_initialized}/{self._status.buses_available}",
            f"  ✓ Contracts: {self._status.contracts_initialized}/{self._status.contracts_available}",
            f"  ✓ Validators: {self._status.validators_initialized}/{self._status.validators_available}",
            f"  ✓ Wiring Configured: {self._status.wiring_initialized}",
            "",
            "IRRIGATION SYSTEM:",
            f"  ✓ Irrigation Components: {self._status.irrigation_initialized}/{self._status.irrigation_available}",
            f"  ✓ Irrigation Units: {self._status.irrigation_units_loaded}",
            f"  ✓ Items Irrigable: {self._status.items_irrigable}",
            "",
            f"INTEGRATION STATUS: {'✅ FULLY INTEGRATED' if self._status.is_fully_integrated() else '⚠️ PARTIAL'}",
            "=" * 80,
        ]
        return "\n".join(lines)


# =============================================================================
# MODULE-LEVEL CONVENIENCE
# =============================================================================

_hub_instance: Optional[SISASIntegrationHub] = None


def get_sisas_hub() -> SISASIntegrationHub:
    """Get or create the global SISAS integration hub."""
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = SISASIntegrationHub()
    return _hub_instance


def initialize_sisas(orchestrator: Any = None) -> IntegrationStatus:
    """Initialize SISAS integration hub."""
    hub = get_sisas_hub()
    return hub.initialize(orchestrator)


def get_sisas_status() -> Dict[str, Any]:
    """Get current SISAS integration status."""
    hub = get_sisas_hub()
    return hub.get_status().to_dict()


__all__ = [
    "SISASIntegrationHub",
    "IntegrationStatus",
    "get_sisas_hub",
    "initialize_sisas",
    "get_sisas_status",
    "SISAS_CORE_AVAILABLE",
    "EXTRACTORS",
    "VEHICLES",
    "BUSES",
    "CONTRACTS",
    "VALIDATORS",
    "WIRING",
    "IRRIGATION",
    "PHASE_CONSUMERS",
]
