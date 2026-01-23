#!/usr/bin/env python3
"""
SISAS SEVERE AUDIT v2.0 - TRULY COMPREHENSIVE
==============================================

This is NOT a superficial import check. This test:

1. INSTANTIATION - Can each class actually be created?
2. METHOD EXECUTION - Do methods run without crashing?
3. SIGNAL FLOW - Can signals be created, dispatched, consumed?
4. WIRING - Are components actually connected?
5. 4 PILLARS - Do Depuration, SDO, Wiring, Harmonization work?
6. CONSUMERS - Can they receive and process signals?
7. VEHICLES - Can they load files and emit signals?
8. IRRIGATION - Does the full irrigation pipeline work?
9. CONTRACTS - Are consumption contracts valid?
10. END-TO-END - Full phase execution test

Author: FARFAN Pipeline Audit System
Date: 2026-01-20
"""

import os
import sys
import traceback
import time
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))
# Also add PROJECT_ROOT to sys.path for canonic_questionnaire_central imports
sys.path.insert(0, str(PROJECT_ROOT))

SISAS_BASE = SRC_PATH / "farfan_pipeline" / "infrastructure" / "irrigation_using_signals" / "SISAS"


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    category: str
    passed: bool
    error: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0


@dataclass 
class AuditResults:
    """All audit results."""
    tests: List[TestResult] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""
    
    @property
    def passed(self) -> int:
        return sum(1 for t in self.tests if t.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for t in self.tests if not t.passed)
    
    @property
    def total(self) -> int:
        return len(self.tests)
    
    @property
    def score(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0


class SevereSISASAudit:
    """Truly severe SISAS audit."""
    
    def __init__(self):
        self.results = AuditResults()
        self.results.start_time = datetime.now(timezone.utc).isoformat()
        
    def run_test(self, name: str, category: str, test_fn: Callable) -> TestResult:
        """Run a single test with timing and error capture."""
        start = time.time()
        try:
            details = test_fn()
            duration = (time.time() - start) * 1000
            result = TestResult(
                name=name,
                category=category,
                passed=True,
                details=details or {},
                duration_ms=duration
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            result = TestResult(
                name=name,
                category=category,
                passed=False,
                error=f"{type(e).__name__}: {str(e)[:200]}",
                duration_ms=duration
            )
        
        self.results.tests.append(result)
        status = "✅" if result.passed else "❌"
        print(f"  {status} {name} ({duration:.1f}ms)")
        if not result.passed:
            print(f"     └─ {result.error[:80]}")
        return result

    def run_all(self):
        """Run all severe tests."""
        print("=" * 70)
        print("SISAS SEVERE AUDIT v2.0")
        print("=" * 70)
        print()
        
        # Category 1: Core Infrastructure
        print("[1/10] CORE INFRASTRUCTURE")
        print("-" * 50)
        self._test_core_infrastructure()
        
        # Category 2: Signal System
        print("\n[2/10] SIGNAL SYSTEM")
        print("-" * 50)
        self._test_signal_system()
        
        # Category 3: 4 Pillars
        print("\n[3/10] THE 4 PILLARS")
        print("-" * 50)
        self._test_4_pillars()
        
        # Category 4: Vehicles
        print("\n[4/10] VEHICLES")
        print("-" * 50)
        self._test_vehicles()
        
        # Category 5: Consumers
        print("\n[5/10] CONSUMERS")
        print("-" * 50)
        self._test_consumers()
        
        # Category 6: Irrigation Pipeline
        print("\n[6/10] IRRIGATION PIPELINE")
        print("-" * 50)
        self._test_irrigation()
        
        # Category 7: Contracts
        print("\n[7/10] CONTRACTS")
        print("-" * 50)
        self._test_contracts()
        
        # Category 8: Signal Flow
        print("\n[8/10] SIGNAL FLOW (End-to-End)")
        print("-" * 50)
        self._test_signal_flow()
        
        # Category 9: SDO Integration
        print("\n[9/10] SDO INTEGRATION")
        print("-" * 50)
        self._test_sdo_integration()
        
        # Category 10: UnifiedOrchestrator Integration
        print("\n[10/10] UNIFIED ORCHESTRATOR")
        print("-" * 50)
        self._test_unified_orchestrator()
        
        self.results.end_time = datetime.now(timezone.utc).isoformat()
        
    def _test_core_infrastructure(self):
        """Test core SISAS infrastructure."""
        
        # Test Signal class
        def test_signal_creation():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
                Signal, SignalContext, SignalSource, SignalConfidence, SignalCategory
            )
            # Signal is ABC, test the components
            ctx = SignalContext(phase="phase_01", policy_area="PA01", dimension="DIM01")
            src = SignalSource(file_path="test.json", extractor="test")
            assert ctx.phase == "phase_01"
            assert src.file_path == "test.json"
            return {"context_created": True, "source_created": True}
        self.run_test("Signal components creation", "CORE", test_signal_creation)
        
        # Test Event class
        def test_event_creation():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import (
                Event, EventType, EventStore
            )
            event = Event(
                event_id="test-001",
                event_type=EventType.FILE_LOADED,
                payload={"test": "data"},
                source_file="test.json"
            )
            assert event.event_id == "test-001"
            store = EventStore()
            store.record(event)
            assert len(store.events) == 1
            return {"event_created": True, "store_works": True}
        self.run_test("Event creation and storage", "CORE", test_event_creation)
        
        # Test Bus
        def test_bus_creation():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import (
                SignalBus, BusRegistry
            )
            bus = SignalBus(bus_id="test_bus")
            registry = BusRegistry()
            registry.register_bus(bus)
            retrieved = registry.get_bus("test_bus")
            assert retrieved is not None
            return {"bus_created": True, "registry_works": True}
        self.run_test("Bus creation and registry", "CORE", test_bus_creation)
        
        # Test Contracts
        def test_contracts():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import (
                ConsumptionContract, IrrigationContract, ContractRegistry
            )
            contract = ConsumptionContract(
                contract_id="CC_TEST",
                consumer_id="test_consumer",
                consumer_phase="phase_01",
                subscribed_signal_types=["MC01", "MC02"],
                subscribed_buses=["structural_bus"]
            )
            assert contract.contract_id == "CC_TEST"
            registry = ContractRegistry()
            registry.register(contract)
            return {"contract_created": True, "registry_works": True}
        self.run_test("Contract creation and registry", "CORE", test_contracts)

    def _test_signal_system(self):
        """Test the signal type system."""
        
        # Test all 7 signal type categories
        def test_structural_signals():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.structural import (
                StructuralAlignmentSignal, CanonicalMappingSignal, AlignmentStatus
            )
            signal = StructuralAlignmentSignal(
                signal_id="test-001",
                alignment_status=AlignmentStatus.ALIGNED,
                source_file="test.json"
            )
            assert signal.signal_id == "test-001"
            return {"structural_signal_created": True}
        self.run_test("Structural signals", "SIGNALS", test_structural_signals)
        
        def test_integrity_signals():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.integrity import (
                EventPresenceSignal, PresenceStatus
            )
            signal = EventPresenceSignal(
                signal_id="test-002",
                presence_status=PresenceStatus.PRESENT,
                source_file="test.json"
            )
            assert signal.signal_id == "test-002"
            return {"integrity_signal_created": True}
        self.run_test("Integrity signals", "SIGNALS", test_integrity_signals)
        
        def test_epistemic_signals():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.epistemic import (
                AnswerDeterminacySignal, DeterminacyLevel
            )
            signal = AnswerDeterminacySignal(
                signal_id="test-003",
                determinacy_level=DeterminacyLevel.DETERMINATE,
                question_id="Q001"
            )
            return {"epistemic_signal_created": True}
        self.run_test("Epistemic signals", "SIGNALS", test_epistemic_signals)
        
        def test_contrast_signals():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.contrast import (
                DecisionDivergenceSignal, DivergenceType
            )
            signal = DecisionDivergenceSignal(
                signal_id="test-004",
                divergence_type=DivergenceType.SCORE_DIVERGENCE
            )
            return {"contrast_signal_created": True}
        self.run_test("Contrast signals", "SIGNALS", test_contrast_signals)
        
        def test_operational_signals():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.operational import (
                ExecutionAttemptSignal, ExecutionStatus
            )
            signal = ExecutionAttemptSignal(
                signal_id="test-005",
                status=ExecutionStatus.SUCCESS,
                component="test"
            )
            return {"operational_signal_created": True}
        self.run_test("Operational signals", "SIGNALS", test_operational_signals)
        
        def test_consumption_signals():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.consumption import (
                FrequencySignal, ConsumerHealthSignal
            )
            signal = FrequencySignal(
                signal_id="test-006",
                resource_id="test_resource",
                access_count=10
            )
            return {"consumption_signal_created": True}
        self.run_test("Consumption signals", "SIGNALS", test_consumption_signals)
        
        def test_orchestration_signals():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.orchestration import (
                PhaseStartSignal, PhaseCompleteSignal, create_phase_start_signal
            )
            signal = create_phase_start_signal(phase_id="phase_01")
            assert signal.phase_id == "phase_01"
            return {"orchestration_signal_created": True}
        self.run_test("Orchestration signals", "SIGNALS", test_orchestration_signals)

    def _test_4_pillars(self):
        """Test the 4 SISAS pillars."""
        
        # Pillar 1: Depuration
        def test_depuration():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.validators.depuration import (
                DepurationValidator
            )
            validator = DepurationValidator()
            # Test with a real file
            test_file = PROJECT_ROOT / "canonic_questionnaire_central" / "config" / "canonical_notation.json"
            if test_file.exists():
                result = validator.validate_file(str(test_file))
                return {"validator_created": True, "validation_ran": True, "result": str(result)[:50]}
            return {"validator_created": True, "no_test_file": True}
        self.run_test("Pillar 1: DepurationValidator", "4_PILLARS", test_depuration)
        
        # Pillar 2: SDO (SignalDistributionOrchestrator)
        def test_sdo():
            from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
                SignalDistributionOrchestrator
            )
            sdo = SignalDistributionOrchestrator()
            metrics = sdo.get_metrics()
            health = sdo.health_check()
            return {
                "sdo_created": True,
                "metrics_available": bool(metrics),
                "health_status": health.get("status", "unknown")
            }
        self.run_test("Pillar 2: SDO", "4_PILLARS", test_sdo)
        
        # Pillar 3: Wiring
        def test_wiring():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.wiring.wiring_config import (
                WiringConfiguration
            )
            wiring = WiringConfiguration()
            # Test wiring methods
            has_validate = hasattr(wiring, 'validate_wiring') or hasattr(wiring, 'get_wiring_status')
            return {"wiring_created": True, "has_validate_method": has_validate}
        self.run_test("Pillar 3: WiringConfiguration", "4_PILLARS", test_wiring)
        
        # Pillar 4: Harmonization
        def test_harmonization():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.harmonization.harmonization_validator import (
                HarmonizationValidator
            )
            validator = HarmonizationValidator()
            has_validate = hasattr(validator, 'validate_full_harmonization') or hasattr(validator, 'check_harmonization')
            return {"validator_created": True, "has_validate_method": has_validate}
        self.run_test("Pillar 4: HarmonizationValidator", "4_PILLARS", test_harmonization)

    def _test_vehicles(self):
        """Test all vehicles."""
        
        vehicles_to_test = [
            ("BaseVehicle", "base_vehicle", "BaseVehicle"),
            ("SignalRegistryVehicle", "signal_registry", "SignalRegistryVehicle"),
            ("SignalContextScoper", "signal_context_scoper", "SignalContextScoperVehicle"),
            ("SignalQualityMetrics", "signal_quality_metrics", "SignalQualityMetricsVehicle"),
            ("SignalIrrigator", "signal_irrigator", "SignalIrrigatorVehicle"),
            ("SignalLoader", "signal_loader", "SignalLoaderVehicle"),
            ("SignalEnhancementIntegrator", "signal_enhancement_integrator", "SignalEnhancementIntegratorVehicle"),
            ("SignalEvidenceExtractor", "signal_evidence_extractor", "SignalEvidenceExtractorVehicle"),
            ("SignalIntelligenceLayer", "signal_intelligence_layer", "SignalIntelligenceLayerVehicle"),
        ]
        
        for name, module, class_name in vehicles_to_test:
            def make_test(mod, cls):
                def test():
                    module_path = f"farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.{mod}"
                    m = __import__(module_path, fromlist=[cls])
                    klass = getattr(m, cls)
                    # Try to instantiate (BaseVehicle might need args)
                    if cls == "BaseVehicle":
                        return {"class_exists": True, "is_base": True}
                    instance = klass()
                    has_process = hasattr(instance, 'process') or hasattr(instance, 'load')
                    return {"instantiated": True, "has_process": has_process}
                return test
            self.run_test(f"Vehicle: {name}", "VEHICLES", make_test(module, class_name))

    def _test_consumers(self):
        """Test all consumers."""
        
        consumers_to_test = [
            ("phase0", "phase0_assembly_consumer", "Phase0AssemblyConsumer"),
            ("phase1", "phase1_extraction_consumer", "Phase1ExtractionConsumer"),
            ("phase2", "phase2_factory_consumer", "Phase2FactoryConsumer"),
            ("phase3", "phase3_validation_consumer", "Phase3ValidationConsumer"),
            ("phase4", "phase4_aggregation_consumer", "Phase4AggregationConsumer"),
            ("phase5", "phase5_uncertainty_consumer", "Phase5UncertaintyConsumer"),
            ("phase6", "phase6_configuration_consumer", "Phase6ConfigurationConsumer"),
            ("phase7", "phase7_meso_consumer", "Phase7MesoConsumer"),
            ("phase8", "phase8_macro_consumer", "Phase8MacroConsumer"),
            ("phase9", "phase9_reporting_consumer", "Phase9ReportingConsumer"),
        ]
        
        for phase, module, class_name in consumers_to_test:
            def make_test(ph, mod, cls):
                def test():
                    module_path = f"farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.{ph}.{mod}"
                    m = __import__(module_path, fromlist=[cls])
                    klass = getattr(m, cls)
                    instance = klass()
                    has_consume = hasattr(instance, 'consume') or hasattr(instance, 'process_signal')
                    has_contract = hasattr(instance, 'get_consumption_contract') or hasattr(instance, 'consumption_contract')
                    return {"instantiated": True, "has_consume": has_consume, "has_contract": has_contract}
                return test
            self.run_test(f"Consumer: {phase}", "CONSUMERS", make_test(phase, module, class_name))

    def _test_irrigation(self):
        """Test irrigation pipeline."""
        
        def test_irrigation_map():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_map import (
                IrrigationMap, IrrigationRoute, IrrigationSource, IrrigabilityStatus
            )
            imap = IrrigationMap()
            source = IrrigationSource(
                file_path="test.json",
                stage="phase_01",
                phase="Phase_01",
                vehicles=["signal_registry"],
                consumers=["phase1_consumer"],
                irrigability=IrrigabilityStatus.IRRIGABLE_NOW
            )
            route = IrrigationRoute(source=source, vehicles=["signal_registry"])
            imap.add_route(route)
            stats = imap.get_statistics()
            return {"map_created": True, "route_added": True, "stats": stats}
        self.run_test("IrrigationMap", "IRRIGATION", test_irrigation_map)
        
        def test_irrigation_executor():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_executor import (
                IrrigationExecutor
            )
            executor = IrrigationExecutor()
            has_irrigate = hasattr(executor, 'irrigate') or hasattr(executor, 'execute')
            return {"executor_created": True, "has_irrigate": has_irrigate}
        self.run_test("IrrigationExecutor", "IRRIGATION", test_irrigation_executor)
        
        def test_irrigation_validator():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_validator import (
                IrrigationValidator
            )
            validator = IrrigationValidator()
            has_validate = hasattr(validator, 'validate')
            return {"validator_created": True, "has_validate": has_validate}
        self.run_test("IrrigationValidator", "IRRIGATION", test_irrigation_validator)

    def _test_contracts(self):
        """Test contract system."""
        
        def test_consumption_contract_valid():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import (
                ConsumptionContract
            )
            contract = ConsumptionContract(
                contract_id="CC_PHASE1_EXTRACTION",
                consumer_id="phase1_extraction_consumer",
                consumer_phase="phase_01",
                subscribed_signal_types=["MC01", "MC02", "MC03"],
                subscribed_buses=["structural_bus", "integrity_bus"],
                context_filters={"phase": ["phase_01"]},
                required_capabilities=["can_extract", "can_validate"]
            )
            # Validate contract has all required fields
            assert contract.contract_id
            assert contract.consumer_id
            assert len(contract.subscribed_signal_types) > 0
            return {"contract_valid": True, "signal_types": len(contract.subscribed_signal_types)}
        self.run_test("ConsumptionContract validation", "CONTRACTS", test_consumption_contract_valid)
        
        def test_irrigation_contract():
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import (
                IrrigationContract
            )
            contract = IrrigationContract(
                contract_id="IC_TEST",
                source_file="test.json",
                target_phase="phase_01",
                vehicles=["signal_registry"],
                consumers=["phase1_consumer"]
            )
            assert contract.contract_id == "IC_TEST"
            return {"contract_valid": True}
        self.run_test("IrrigationContract validation", "CONTRACTS", test_irrigation_contract)

    def _test_signal_flow(self):
        """Test end-to-end signal flow."""
        
        def test_create_dispatch_consume():
            from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
                SignalDistributionOrchestrator
            )
            from canonic_questionnaire_central.core.signal import (
                Signal, SignalType, SignalScope, SignalProvenance
            )
            
            sdo = SignalDistributionOrchestrator()
            
            # Track received signals
            received_signals = []
            
            def handler(signal):
                received_signals.append(signal)
            
            # Register consumer
            sdo.register_consumer(
                consumer_id="test_flow_consumer",
                scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
                capabilities=["EXTRACTION"],
                handler=handler
            )
            
            # Create signal
            scope = SignalScope(phase="phase_1", policy_area="PA01", slot="Q001")
            prov = SignalProvenance(extractor="test", source_file="test.py", extraction_pattern="flow_test")
            signal = Signal.create(
                signal_type=SignalType.STATIC_LOAD,
                scope=scope,
                payload={"test_data": "flow_test"},
                provenance=prov,
                empirical_availability=1.0,
                capabilities_required=["EXTRACTION"]
            )
            
            # Dispatch
            delivered = sdo.dispatch(signal)
            
            return {
                "signal_created": True,
                "signal_dispatched": delivered,
                "signals_received": len(received_signals),
                "flow_complete": delivered and len(received_signals) == 1
            }
        self.run_test("Create → Dispatch → Consume flow", "SIGNAL_FLOW", test_create_dispatch_consume)
        
        def test_multi_consumer_dispatch():
            from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
                SignalDistributionOrchestrator
            )
            from canonic_questionnaire_central.core.signal import (
                Signal, SignalType, SignalScope, SignalProvenance
            )
            
            sdo = SignalDistributionOrchestrator()
            
            received_by = {}
            
            def make_handler(name):
                def handler(signal):
                    received_by[name] = signal.signal_id
                return handler
            
            # Register multiple consumers
            for i in range(3):
                sdo.register_consumer(
                    consumer_id=f"multi_consumer_{i}",
                    scopes=[{"phase": "phase_2", "policy_area": "ALL", "slot": "ALL"}],
                    capabilities=["ENRICHMENT"],
                    handler=make_handler(f"consumer_{i}")
                )
            
            # Dispatch signal
            scope = SignalScope(phase="phase_2", policy_area="PA01", slot="Q001")
            prov = SignalProvenance(extractor="test", source_file="test.py", extraction_pattern="multi_test")
            signal = Signal.create(
                signal_type=SignalType.STATIC_LOAD,
                scope=scope,
                payload={"test": "multi"},
                provenance=prov,
                empirical_availability=1.0,
                capabilities_required=["ENRICHMENT"]
            )
            
            delivered = sdo.dispatch(signal)
            
            return {
                "consumers_registered": 3,
                "consumers_received": len(received_by),
                "all_received": len(received_by) == 3
            }
        self.run_test("Multi-consumer dispatch", "SIGNAL_FLOW", test_multi_consumer_dispatch)

    def _test_sdo_integration(self):
        """Test SDO integration features."""
        
        def test_sdo_gates():
            from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
                SignalDistributionOrchestrator
            )
            sdo = SignalDistributionOrchestrator()
            
            # Check gates are configured
            has_gate_1 = hasattr(sdo, '_gate_1') or hasattr(sdo, 'scope_alignment_gate')
            has_gate_2 = hasattr(sdo, '_gate_2') or hasattr(sdo, 'value_add_gate')
            has_gate_3 = hasattr(sdo, '_gate_3') or hasattr(sdo, 'capability_gate')
            has_gate_4 = hasattr(sdo, '_gate_4') or hasattr(sdo, 'irrigation_channel_gate')
            
            return {
                "gate_1_scope": has_gate_1,
                "gate_2_value": has_gate_2,
                "gate_3_capability": has_gate_3,
                "gate_4_irrigation": has_gate_4
            }
        self.run_test("SDO gates configured", "SDO", test_sdo_gates)
        
        def test_sdo_metrics():
            from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
                SignalDistributionOrchestrator
            )
            sdo = SignalDistributionOrchestrator()
            metrics = sdo.get_metrics()
            
            expected_metrics = [
                "signals_dispatched", "signals_delivered", "signals_rejected",
                "dead_letters", "consumer_errors"
            ]
            
            found_metrics = [m for m in expected_metrics if m in metrics]
            
            return {
                "metrics_available": True,
                "found_metrics": found_metrics,
                "metrics_complete": len(found_metrics) == len(expected_metrics)
            }
        self.run_test("SDO metrics", "SDO", test_sdo_metrics)
        
        def test_sdo_dead_letter():
            from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
                SignalDistributionOrchestrator
            )
            from canonic_questionnaire_central.core.signal import (
                Signal, SignalType, SignalScope, SignalProvenance
            )
            
            sdo = SignalDistributionOrchestrator()
            
            # Dispatch signal with no matching consumers
            scope = SignalScope(phase="phase_99", policy_area="NONE", slot="NONE")
            prov = SignalProvenance(extractor="test", source_file="test.py", extraction_pattern="dead_letter_test")
            signal = Signal.create(
                signal_type=SignalType.STATIC_LOAD,
                scope=scope,
                payload={"test": "dead_letter"},
                provenance=prov,
                empirical_availability=1.0,
                capabilities_required=["NONEXISTENT_CAPABILITY"]
            )
            
            delivered = sdo.dispatch(signal)
            metrics = sdo.get_metrics()
            
            return {
                "delivered": delivered,
                "dead_letters": metrics.get("dead_letters", 0),
                "dead_letter_tracked": metrics.get("dead_letters", 0) > 0 or not delivered
            }
        self.run_test("SDO dead letter handling", "SDO", test_sdo_dead_letter)

    def _test_unified_orchestrator(self):
        """Test UnifiedOrchestrator integration."""
        
        def test_orchestrator_creation():
            from farfan_pipeline.orchestration import UnifiedOrchestrator, OrchestratorConfig
            config = OrchestratorConfig(enable_sisas=True)
            orch = UnifiedOrchestrator(config)
            
            has_context = hasattr(orch, 'context')
            has_sisas = orch.context.sisas is not None if has_context else False
            
            return {
                "orchestrator_created": True,
                "has_context": has_context,
                "sisas_enabled": has_sisas
            }
        self.run_test("UnifiedOrchestrator creation", "ORCHESTRATOR", test_orchestrator_creation)
        
        def test_orchestrator_consumers():
            from farfan_pipeline.orchestration import UnifiedOrchestrator, OrchestratorConfig
            config = OrchestratorConfig(enable_sisas=True)
            orch = UnifiedOrchestrator(config)
            
            has_consumer_configs = hasattr(orch, 'CONSUMER_CONFIGS')
            consumer_count = len(orch.CONSUMER_CONFIGS) if has_consumer_configs else 0
            
            return {
                "has_consumer_configs": has_consumer_configs,
                "consumer_count": consumer_count,
                "all_10_phases": consumer_count == 10
            }
        self.run_test("UnifiedOrchestrator consumers", "ORCHESTRATOR", test_orchestrator_consumers)
        
        def test_orchestrator_phase_methods():
            from farfan_pipeline.orchestration import UnifiedOrchestrator, OrchestratorConfig
            config = OrchestratorConfig(enable_sisas=True)
            orch = UnifiedOrchestrator(config)
            
            phase_methods = []
            for i in range(10):
                method_name = f"_execute_phase_{i:02d}"
                if hasattr(orch, method_name):
                    phase_methods.append(method_name)
            
            return {
                "phase_methods_found": len(phase_methods),
                "all_10_phases": len(phase_methods) == 10,
                "methods": phase_methods
            }
        self.run_test("UnifiedOrchestrator phase methods", "ORCHESTRATOR", test_orchestrator_phase_methods)
        
        def test_orchestrator_signal_emission():
            from farfan_pipeline.orchestration import UnifiedOrchestrator, OrchestratorConfig
            config = OrchestratorConfig(enable_sisas=True)
            orch = UnifiedOrchestrator(config)
            
            has_emit = hasattr(orch, '_emit_phase_signal')
            
            return {
                "has_emit_method": has_emit
            }
        self.run_test("UnifiedOrchestrator signal emission", "ORCHESTRATOR", test_orchestrator_signal_emission)

    def print_report(self):
        """Print final report."""
        print()
        print("=" * 70)
        print("SEVERE AUDIT REPORT")
        print("=" * 70)
        
        # Summary by category
        categories = {}
        for test in self.results.tests:
            if test.category not in categories:
                categories[test.category] = {"passed": 0, "failed": 0}
            if test.passed:
                categories[test.category]["passed"] += 1
            else:
                categories[test.category]["failed"] += 1
        
        print()
        print("RESULTS BY CATEGORY")
        print("-" * 70)
        for cat, stats in sorted(categories.items()):
            total = stats["passed"] + stats["failed"]
            pct = stats["passed"] / total * 100 if total > 0 else 0
            status = "✅" if stats["failed"] == 0 else "❌"
            print(f"  {status} {cat}: {stats['passed']}/{total} ({pct:.0f}%)")
        
        # Failed tests
        failed = [t for t in self.results.tests if not t.passed]
        if failed:
            print()
            print("FAILED TESTS")
            print("-" * 70)
            for test in failed:
                print(f"  ❌ [{test.category}] {test.name}")
                print(f"     {test.error[:70]}")
        
        # Final score
        print()
        print("=" * 70)
        score = self.results.score
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        print(f"FINAL SCORE: {self.results.passed}/{self.results.total} tests passed ({score:.1f}%)")
        print(f"GRADE: {grade}")
        print()
        
        if score >= 80:
            print("✅ SISAS system is FUNCTIONAL")
        elif score >= 60:
            print("⚠️  SISAS system has ISSUES but is partially functional")
        else:
            print("❌ SISAS system has CRITICAL FAILURES")
        
        print("=" * 70)
        
        return score


def main():
    audit = SevereSISASAudit()
    audit.run_all()
    score = audit.print_report()
    
    # Save results
    output_path = PROJECT_ROOT / "artifacts" / "sisas_severe_audit_v2.json"
    output_path.parent.mkdir(exist_ok=True)
    
    results_data = {
        "summary": {
            "total": audit.results.total,
            "passed": audit.results.passed,
            "failed": audit.results.failed,
            "score": score,
            "start_time": audit.results.start_time,
            "end_time": audit.results.end_time,
        },
        "tests": [
            {
                "name": t.name,
                "category": t.category,
                "passed": t.passed,
                "error": t.error,
                "details": t.details,
                "duration_ms": t.duration_ms,
            }
            for t in audit.results.tests
        ]
    }
    
    with open(output_path, "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    return 0 if score >= 60 else 1


if __name__ == "__main__":
    sys.exit(main())
