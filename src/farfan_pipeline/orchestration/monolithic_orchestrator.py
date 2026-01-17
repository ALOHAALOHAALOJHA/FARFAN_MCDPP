"""
ORQUESTADOR MONOLÍTICO UNIFICADO - FARFAN MCDPP
================================================

Fusión completa y explícita de:
- canonical_executors.py
- cli.py
- core_orchestrator.py
- Subsistema SISAS (bus, event, contracts, irrigation, vehicles, consumers)
- Subsistema de calibración (registry, core, epistemic)
- Secuencia completa P00-P09 sin omisiones

GARANTÍAS CONSTITUCIONALES:
- Ejecución automática por defecto (sin flags ad hoc)
- Sin activación manual requerida
- Sin disparadores externos
- Sin intervención operativa
- Flujo determinista end-to-end
- Materialización explícita de TODAS las fases
- Subsistemas SISAS y calibración integrados

Autor: F.A.R.F.A.N Core Team
Versión: 4.0.0 MONOLITHIC
"""

from __future__ import annotations

__version__ = "4.0.0-MONOLITHIC"
__module_type__ = "MONOLITHIC_ORCHESTRATOR"
__criticality__ = "CRITICAL"
__lifecycle__ = "ACTIVE"
__execution_pattern__ = "Singleton"
__compliance_status__ = "GNEA_COMPLIANT"
__sin_carreta_compliant__ = True

# =============================================================================
# IMPORTS EXHAUSTIVOS
# =============================================================================

import argparse
import asyncio
import csv
import json
import logging
import os
import sys
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import blake3
import structlog

# Canonic questionnaire central
from canonic_questionnaire_central import (
    QuestionnairePort,
    resolve_questionnaire,
)

# =============================================================================
# SUBSISTEMA SISAS - MATERIALIZACIÓN EXPLÍCITA
# =============================================================================

# SISAS Core
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import (
    BusRegistry,
    SignalBus,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import (
    ContractRegistry,
    PublicationContract,
    ConsumptionContract,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import (
    EventStore,
    Event,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
    Signal,
    SignalCategory,
    SignalContext,
)

# SISAS Irrigation
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_executor import (
    IrrigationExecutor,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_map import (
    IrrigationMap,
    IrrigationRoute,
)

# SISAS Vehicles
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_context_scoper import (
    SignalContextScoperVehicle,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_registry import (
    SignalRegistryVehicle,
)

# SISAS Vocabulary
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.alignment_checker import (
    VocabularyAlignmentChecker,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.capability_vocabulary import (
    CapabilityVocabulary,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.signal_vocabulary import (
    SignalVocabulary,
)

# SISAS Signals
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals import (
    InMemorySignalSource,
    SignalClient,
    SignalPack,
    SignalRegistry,
)

# SISAS Audit
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.questionnaire_access_audit import (
    AccessLevel,
    get_access_audit,
)

# =============================================================================
# SUBSISTEMA DE CALIBRACIÓN - MATERIALIZACIÓN EXPLÍCITA
# =============================================================================

from farfan_pipeline.calibration.calibration_core import (
    ClosedInterval,
    EpistemicLevel,
)
from farfan_pipeline.calibration.registry import (
    EpistemicCalibrationRegistry,
)

# =============================================================================
# PHASE IMPORTS - MATERIALIZACIÓN EXPLÍCITA
# =============================================================================

# Phase 0
from farfan_pipeline.phases.Phase_00.interphase.wiring_types import (
    ContractViolation,
    Severity,
    ValidationResult,
    WiringComponents,
    WiringFeatureFlags,
)
from farfan_pipeline.phases.Phase_00.phase0_90_02_bootstrap import (
    EnforcedBootstrap,
    WiringBootstrap,
)
from farfan_pipeline.phases.Phase_00.primitives.providers import (
    QuestionnaireResourceProvider,
    CoreModuleFactory,
)
from farfan_pipeline.phases.Phase_00.phase0_10_00_paths import CONFIG_DIR, DATA_DIR

# Phase 1
from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
    execute_phase_1_with_full_contract,
)
from farfan_pipeline.phases.Phase_01.interphase.phase1_08_00_adapter import (
    adapt_cpp_to_orchestrator,
)

# Phase 2
from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
    AnalysisPipelineFactory,
)
from farfan_pipeline.phases.Phase_02.phase2_10_01_class_registry import build_class_registry
from farfan_pipeline.phases.Phase_02.phase2_10_02_methods_registry import MethodRegistry
from farfan_pipeline.phases.Phase_02.phase2_10_03_executor_config import ExecutorConfig
from farfan_pipeline.phases.Phase_02.phase2_40_03_irrigation_synchronizer import (
    IrrigationSynchronizer,
)
from farfan_pipeline.phases.Phase_02.phase2_50_00_task_executor import (
    TaskExecutor,
)
from farfan_pipeline.phases.Phase_02.phase2_60_02_arg_router import ExtendedArgRouter
from farfan_pipeline.phases.Phase_02.registries import (
    QuestionnaireSignalRegistry,
)

# Phase 3
from farfan_pipeline.phases.Phase_03.phase3_20_00_score_extraction import (
    extract_score_from_nexus,
    map_completeness_to_quality,
)
from farfan_pipeline.phases.Phase_03.phase3_24_00_signal_enriched_scoring import (
    SignalEnrichedScorer,
)
from farfan_pipeline.phases.Phase_03.contracts.phase03_output_contract import (
    ScoredMicroQuestion,
)

# Phase 4
from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import (
    DimensionAggregator,
    ScoredResult,
)

# Phase 5
from farfan_pipeline.phases.Phase_05.phase5_10_00_area_integration import (
    run_phase5_aggregation,
)

# Phase 6
from farfan_pipeline.phases.Phase_06.phase6_30_00_cluster_aggregator import (
    ClusterAggregator,
)

# Phase 7
from farfan_pipeline.phases.Phase_07.phase7_20_00_macro_aggregator import (
    MacroAggregator,
)

# Phase 8
from farfan_pipeline.phases.Phase_08.phase8_20_01_recommendation_engine_adapter import (
    RecommendationEngineAdapter,
)
from farfan_pipeline.phases.Phase_08.primitives.PHASE_8_CONSTANTS import (
    RULES_PATH_ENHANCED,
    SCHEMA_PATH,
)

# Phase 9
from farfan_pipeline.phases.Phase_09.phase9_10_00_report_assembly import (
    create_report_assembler,
)

logger = structlog.get_logger(__name__)

# =============================================================================
# CONSTANTES CANÓNICAS
# =============================================================================

CANONICAL_POLICY_AREA_DEFINITIONS: OrderedDict[str, dict[str, Any]] = OrderedDict([
    ("PA01", {"name": "Derechos de las mujeres e igualdad de género", "slug": "genero_mujeres", "aliases": ["fiscal"]}),
    ("PA02", {"name": "Prevención de la violencia y protección", "slug": "seguridad_violencia", "aliases": ["salud"]}),
    ("PA03", {"name": "Ambiente sano y cambio climático", "slug": "ambiente", "aliases": ["ambiente"]}),
    ("PA04", {"name": "Derechos económicos, sociales y culturales", "slug": "derechos_sociales", "aliases": ["energía"]}),
    ("PA05", {"name": "Derechos de las víctimas y construcción de paz", "slug": "paz_victimas", "aliases": ["transporte"]}),
    ("PA06", {"name": "Derecho al futuro de la niñez y juventud", "slug": "ninez_juventud", "aliases": []}),
    ("PA07", {"name": "Tierras y territorios", "slug": "tierras_territorios", "aliases": []}),
    ("PA08", {"name": "Líderes, lideresas y defensores de DD. HH.", "slug": "liderazgos_ddhh", "aliases": []}),
    ("PA09", {"name": "Derechos de personas privadas de libertad", "slug": "privados_libertad", "aliases": []}),
    ("PA10", {"name": "Migración transfronteriza", "slug": "migracion", "aliases": []}),
])

CONSTITUTIONAL_INVARIANTS = {
    "micro_questions": 300,  # 10 PA × 6 DIM × 5 Q
    "dimensions": 60,        # 10 PA × 6 DIM
    "policy_areas": 10,      # 10 PA
    "clusters": 4,           # 4 MESO clusters
    "macro_score": 1,        # 1 holistic score
    "layers": 8,             # 8 epistemic layers
}

# =============================================================================
# ENUMS Y TIPOS BASE
# =============================================================================

class PhaseStatus(str, Enum):
    """Execution status for a pipeline phase."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class PhaseID(str, Enum):
    """Canonical phase identifiers."""
    PHASE_0 = "P00"  # Bootstrap & Validation
    PHASE_1 = "P01"  # CPP Ingestion
    PHASE_2 = "P02"  # Executor Factory & Dispatch
    PHASE_3 = "P03"  # Layer Scoring
    PHASE_4 = "P04"  # Dimension Aggregation
    PHASE_5 = "P05"  # Policy Area Aggregation
    PHASE_6 = "P06"  # Cluster Aggregation
    PHASE_7 = "P07"  # Macro Aggregation
    PHASE_8 = "P08"  # Recommendations Engine
    PHASE_9 = "P09"  # Report Assembly


# =============================================================================
# OUTPUTS DE FASE - MATERIALIZACIÓN EXPLÍCITA
# =============================================================================

@dataclass(frozen=True)
class Phase0Output:
    """Phase 0 output containing wiring, questionnaire, and SISAS lifecycle."""
    wiring: WiringComponents
    questionnaire: QuestionnairePort
    sisas: "SisasLifecycle"
    calibration_registry: EpistemicCalibrationRegistry
    signal_registry_types: tuple[str, ...]


@dataclass(frozen=True)
class Phase1Output:
    """Phase 1 output: CPP with 300 question chunks."""
    cpp: Any
    document_id: str
    chunk_count: int
    structural_profile: dict[str, Any]


@dataclass(frozen=True)
class Phase2Output:
    """Phase 2 output: Execution plan and 300 task results."""
    execution_plan: Any
    task_results: list[Any]
    preprocessed_document: Any
    questionnaire_signal_registry: Any
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase3Output:
    """Phase 3 output: 300 layer scores."""
    layer_scores: list[Any]
    scored_results: list[Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase4Output:
    """Phase 4 output: 60 dimension scores."""
    dimension_scores: list[Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase5Output:
    """Phase 5 output: 10 policy area scores."""
    area_scores: list[Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase6Output:
    """Phase 6 output: 4 cluster scores."""
    cluster_scores: list[Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase7Output:
    """Phase 7 output: 1 macro score."""
    macro_score: Any
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase8Output:
    """Phase 8 output: Recommendations."""
    recommendations: dict[str, Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase9Output:
    """Phase 9 output: Final report."""
    report: Any
    node_trace: tuple[str, ...]


# =============================================================================
# SISAS LIFECYCLE - MATERIALIZACIÓN EXPLÍCITA
# =============================================================================

@dataclass
class SisasLifecycle:
    """Authoritative SISAS lifecycle manager for the pipeline."""

    bus_registry: BusRegistry
    contract_registry: ContractRegistry
    event_store: EventStore
    signal_vocabulary: SignalVocabulary
    capability_vocabulary: CapabilityVocabulary
    alignment_checker: VocabularyAlignmentChecker
    irrigation_executor: IrrigationExecutor
    irrigation_map: IrrigationMap
    vehicles: dict[str, Any] = field(default_factory=dict)
    alignment_report: Any | None = None

    @classmethod
    def initialize(cls, *, strict_mode: bool = True) -> "SisasLifecycle":
        """Initialize SISAS core infrastructure with strict alignment checks."""
        logger.info("sisas_lifecycle_initialization_start")

        # Core SISAS components
        bus_registry = BusRegistry()
        contract_registry = ContractRegistry()
        event_store = EventStore()

        # Vocabulary and alignment
        signal_vocab = SignalVocabulary()
        capability_vocab = CapabilityVocabulary()
        alignment_checker = VocabularyAlignmentChecker(
            signal_vocabulary=signal_vocab,
            capability_vocabulary=capability_vocab,
        )
        alignment_report = alignment_checker.check_alignment()

        if strict_mode and not alignment_report.is_aligned:
            critical_issues = [
                issue for issue in alignment_report.issues if issue.severity == "critical"
            ]
            if critical_issues:
                raise ValueError(
                    f"SISAS vocabulary alignment failed with {len(critical_issues)} critical issues"
                )

        # Irrigation executor
        irrigation_executor = IrrigationExecutor(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store,
        )

        lifecycle = cls(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store,
            signal_vocabulary=signal_vocab,
            capability_vocabulary=capability_vocab,
            alignment_checker=alignment_checker,
            irrigation_executor=irrigation_executor,
            irrigation_map=IrrigationMap(),
            alignment_report=alignment_report,
        )

        lifecycle._register_default_vehicles()

        logger.info(
            "sisas_lifecycle_initialized",
            vehicles=len(lifecycle.vehicles),
            alignment_issues=len(alignment_report.issues) if alignment_report else 0,
        )

        return lifecycle

    def _register_default_vehicles(self) -> None:
        """Register canonical SISAS vehicles in correct order."""
        vehicles = [
            SignalRegistryVehicle(
                bus_registry=self.bus_registry,
                contract_registry=self.contract_registry,
                event_store=self.event_store,
            ),
            SignalContextScoperVehicle(
                bus_registry=self.bus_registry,
                contract_registry=self.contract_registry,
                event_store=self.event_store,
            ),
        ]

        for vehicle in vehicles:
            self.irrigation_executor.register_vehicle(vehicle)
            self.vehicles[vehicle.vehicle_id] = vehicle

    def execute_irrigation_phase(self, phase: str, base_path: str = "") -> Any:
        """Execute all irrigable SISAS routes for a phase."""
        logger.info("sisas_irrigation_phase_execution", phase=phase)
        return self.irrigation_executor.execute_phase(phase, base_path)

    def get_metrics(self) -> dict[str, Any]:
        """Return SISAS lifecycle metrics for orchestration telemetry."""
        alignment_issues = (
            len(self.alignment_report.issues)
            if self.alignment_report is not None
            else 0
        )
        return {
            "alignment_issues": alignment_issues,
            "registered_vehicles": list(self.vehicles.keys()),
            "irrigation_stats": self.irrigation_map.get_statistics(),
        }


# =============================================================================
# EXECUTION CONTEXT - ESTADO COMPARTIDO
# =============================================================================

@dataclass
class PhaseResult:
    """Result of a single phase execution."""
    phase_id: PhaseID
    status: PhaseStatus
    output: Any
    execution_time_s: float
    violations: list[ContractViolation] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error: Exception | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "phase_id": self.phase_id.value,
            "status": self.status.value,
            "execution_time_s": round(self.execution_time_s, 3),
            "violations_count": len(self.violations),
            "critical_violations": sum(
                1 for v in self.violations if v.severity == Severity.CRITICAL
            ),
            "metrics": self.metrics,
            "error": str(self.error) if self.error else None,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ExecutionContext:
    """Shared context across all pipeline phases."""

    # Core components from bootstrap
    wiring: WiringComponents | None = None
    questionnaire: QuestionnairePort | None = None
    sisas: SisasLifecycle | None = None
    calibration_registry: EpistemicCalibrationRegistry | None = None

    # Phase inputs (explicit, no implicit fallback)
    phase_inputs: dict[PhaseID, dict[str, Any]] = field(default_factory=dict)

    # Phase outputs (keyed by PhaseID)
    phase_outputs: dict[PhaseID, Any] = field(default_factory=dict)

    # Phase execution results
    phase_results: dict[PhaseID, PhaseResult] = field(default_factory=dict)

    # Execution metadata
    execution_id: str = field(default_factory=lambda: blake3.blake3(
        f"{time.time()}".encode()
    ).hexdigest()[:16])
    start_time: datetime = field(default_factory=datetime.utcnow)
    config: dict[str, Any] = field(default_factory=dict)

    # Determinism tracking
    input_hashes: dict[str, str] = field(default_factory=dict)
    output_hashes: dict[str, str] = field(default_factory=dict)
    seed: int | None = None

    # Telemetry
    total_violations: list[ContractViolation] = field(default_factory=list)
    signal_metrics: dict[str, Any] = field(default_factory=dict)

    def add_phase_result(self, result: PhaseResult) -> None:
        """Add a phase execution result."""
        self.phase_results[result.phase_id] = result
        self.phase_outputs[result.phase_id] = result.output
        self.total_violations.extend(result.violations)

    def get_phase_output(self, phase_id: PhaseID) -> Any:
        """Get output from a specific phase."""
        return self.phase_outputs.get(phase_id)

    def get_execution_summary(self) -> dict[str, Any]:
        """Get summary of pipeline execution."""
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        completed = sum(
            1 for r in self.phase_results.values() if r.status == PhaseStatus.COMPLETED
        )
        failed = sum(
            1 for r in self.phase_results.values() if r.status == PhaseStatus.FAILED
        )
        critical_violations = sum(
            1 for v in self.total_violations if v.severity == Severity.CRITICAL
        )

        return {
            "execution_id": self.execution_id,
            "elapsed_time_s": round(elapsed, 3),
            "phases_completed": completed,
            "phases_failed": failed,
            "total_phases": len(self.phase_results),
            "total_violations": len(self.total_violations),
            "critical_violations": critical_violations,
            "deterministic": self.seed is not None,
            "sisas_metrics": self.signal_metrics,
        }


# =============================================================================
# ORQUESTADOR MONOLÍTICO - CLASE PRINCIPAL
# =============================================================================

class MonolithicOrchestrator:
    """
    ORQUESTADOR MONOLÍTICO UNIFICADO

    Fusiona y ejecuta explícitamente:
    - Fase 0: Bootstrap con SISAS + Calibración
    - Fase 1: CPP Ingestion (300 questions)
    - Fase 2: Executor Factory & Dispatch (300 tasks)
    - Fase 3: Layer Scoring (300 scores)
    - Fase 4: Dimension Aggregation (60 dimensions)
    - Fase 5: Policy Area Aggregation (10 areas)
    - Fase 6: Cluster Aggregation (4 clusters)
    - Fase 7: Macro Aggregation (1 score)
    - Fase 8: Recommendations
    - Fase 9: Report Assembly

    GARANTÍAS:
    - Ejecución automática por defecto
    - Sin flags ad hoc
    - Sin intervención manual
    - Flujo determinista completo
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        strict_mode: bool = True,
        deterministic: bool = True,
    ):
        """Initialize monolithic orchestrator."""
        self.config = config or self._build_default_config()
        self.strict_mode = strict_mode
        self.deterministic = deterministic
        self.logger = structlog.get_logger(f"{__name__}.MonolithicOrchestrator")

        # Execution context (initialized during pipeline run)
        self.context: ExecutionContext | None = None

        self.logger.info(
            "monolithic_orchestrator_initialized",
            strict_mode=strict_mode,
            deterministic=deterministic,
            version=__version__,
        )

    def _build_default_config(self) -> dict[str, Any]:
        """Build default configuration for autonomous execution."""
        return {
            # Questionnaire
            "questionnaire_path": None,  # Will use canonic_questionnaire_central
            "questionnaire_hash": "",
            "force_questionnaire_rebuild": False,

            # Executor configuration
            "executor_config_path": None,
            "calibration_profile": "default",
            "abort_on_insufficient": True,

            # Resource limits
            "resource_limits": {},

            # Feature flags
            "enable_http_signals": False,
            "enable_calibration": True,
            "enable_sisas": True,

            # SISAS
            "sisas_irrigation_csv_path": None,
            "sisas_base_path": "",

            # Auto-registration
            "load_default_executors": True,
            "auto_register_canonical_executors": True,
        }

    def execute_full_pipeline(self) -> ExecutionContext:
        """
        Execute complete pipeline P00-P09 with automatic configuration.

        Returns:
            ExecutionContext with all results
        """
        self.logger.info("monolithic_pipeline_execution_start")

        # Initialize execution context
        self.context = ExecutionContext(
            config=self.config,
            seed=42 if self.deterministic else None,
        )

        # Execute all phases in sequence
        phases = [
            PhaseID.PHASE_0,
            PhaseID.PHASE_1,
            PhaseID.PHASE_2,
            PhaseID.PHASE_3,
            PhaseID.PHASE_4,
            PhaseID.PHASE_5,
            PhaseID.PHASE_6,
            PhaseID.PHASE_7,
            PhaseID.PHASE_8,
            PhaseID.PHASE_9,
        ]

        for phase_id in phases:
            try:
                self._execute_phase(phase_id)
            except Exception as e:
                self.logger.error(
                    "phase_execution_failed",
                    phase=phase_id.value,
                    error=str(e),
                    error_type=type(e).__name__,
                )

                # Record failure
                result = PhaseResult(
                    phase_id=phase_id,
                    status=PhaseStatus.FAILED,
                    output=None,
                    execution_time_s=0.0,
                    error=e,
                )
                self.context.add_phase_result(result)

                # Stop pipeline on failure if strict mode
                if self.strict_mode:
                    raise

        summary = self.context.get_execution_summary()
        self.logger.info("monolithic_pipeline_execution_complete", summary=summary)

        return self.context

    def _execute_phase(self, phase_id: PhaseID) -> None:
        """Execute a single phase with full integration."""
        self.logger.info("phase_execution_start", phase=phase_id.value)
        start_time = time.time()

        # Phase-specific execution
        try:
            if phase_id == PhaseID.PHASE_0:
                output = self._execute_phase_0()
            elif phase_id == PhaseID.PHASE_1:
                output = self._execute_phase_1()
            elif phase_id == PhaseID.PHASE_2:
                output = self._execute_phase_2()
            elif phase_id == PhaseID.PHASE_3:
                output = self._execute_phase_3()
            elif phase_id == PhaseID.PHASE_4:
                output = self._execute_phase_4()
            elif phase_id == PhaseID.PHASE_5:
                output = self._execute_phase_5()
            elif phase_id == PhaseID.PHASE_6:
                output = self._execute_phase_6()
            elif phase_id == PhaseID.PHASE_7:
                output = self._execute_phase_7()
            elif phase_id == PhaseID.PHASE_8:
                output = self._execute_phase_8()
            elif phase_id == PhaseID.PHASE_9:
                output = self._execute_phase_9()
            else:
                raise ValueError(f"Unknown phase: {phase_id}")
        except Exception as e:
            self.logger.error(
                "phase_execution_error",
                phase=phase_id.value,
                error=str(e),
            )
            raise

        # Record phase result
        execution_time = time.time() - start_time
        result = PhaseResult(
            phase_id=phase_id,
            status=PhaseStatus.COMPLETED,
            output=output,
            execution_time_s=execution_time,
        )

        self.context.add_phase_result(result)

        # Execute SISAS irrigation for this phase
        self._run_sisas_cycle(phase_id)

        self.logger.info(
            "phase_execution_complete",
            phase=phase_id.value,
            execution_time_s=round(execution_time, 3),
        )

    # =========================================================================
    # PHASE EXECUTION METHODS - MATERIALIZACIÓN EXPLÍCITA
    # =========================================================================

    def _execute_phase_0(self) -> Phase0Output:
        """
        PHASE 0: Bootstrap & Validation

        Materializa explícitamente:
        - WiringComponents (provider, signal_client, factory, arg_router)
        - QuestionnairePort (300 questions via canonic_questionnaire_central)
        - SisasLifecycle (bus_registry, event_store, vehicles)
        - EpistemicCalibrationRegistry
        """
        self.logger.info("executing_phase_0_bootstrap")

        # Create feature flags
        flags = WiringFeatureFlags(
            enable_http_signals=self.config.get("enable_http_signals", False),
            enable_calibration=self.config.get("enable_calibration", True),
            strict_validation=self.strict_mode,
            deterministic_mode=self.deterministic,
        )

        # Create bootstrap
        bootstrap = WiringBootstrap(
            questionnaire_path=self.config.get("questionnaire_path"),
            questionnaire_hash=self.config.get("questionnaire_hash", ""),
            executor_config_path=self.config.get("executor_config_path"),
            calibration_profile=self.config.get("calibration_profile", "default"),
            abort_on_insufficient=self.config.get("abort_on_insufficient", True),
            resource_limits=self.config.get("resource_limits", {}),
            flags=flags,
        )

        # Execute bootstrap
        wiring = bootstrap.bootstrap()

        # Resolve canonical questionnaire
        questionnaire = resolve_questionnaire(
            expected_hash=self.config.get("questionnaire_hash") or None,
            force_rebuild=self.config.get("force_questionnaire_rebuild", False),
        )

        # Validate questionnaire granularity (300 questions)
        data = questionnaire.data
        blocks = data.get("blocks", {}) if isinstance(data, dict) else {}
        micro_questions = blocks.get("micro_questions", [])

        if len(micro_questions) != CONSTITUTIONAL_INVARIANTS["micro_questions"]:
            raise ValueError(
                f"Canonical questionnaire must contain {CONSTITUTIONAL_INVARIANTS['micro_questions']} "
                f"micro_questions; got {len(micro_questions)}"
            )

        # Initialize SISAS lifecycle
        sisas = SisasLifecycle.initialize(strict_mode=self.strict_mode)

        # Initialize calibration registry
        calibration_registry = EpistemicCalibrationRegistry()

        # Store in context
        self.context.wiring = wiring
        self.context.questionnaire = questionnaire
        self.context.sisas = sisas
        self.context.calibration_registry = calibration_registry

        registry_types = tuple(SignalRegistry.get_all_types())

        self.logger.info(
            "phase_0_complete",
            components=len(wiring.init_hashes),
            questionnaire_hash=questionnaire.sha256[:16],
            sisas_vehicles=len(sisas.vehicles),
        )

        return Phase0Output(
            wiring=wiring,
            questionnaire=questionnaire,
            sisas=sisas,
            calibration_registry=calibration_registry,
            signal_registry_types=registry_types,
        )

    def _execute_phase_1(self) -> Phase1Output:
        """
        PHASE 1: CPP Ingestion

        Materializa explícitamente:
        - CanonPolicyPackage con 300 question chunks
        - Document ID y structural profile
        """
        self.logger.info("executing_phase_1_cpp_ingestion")

        # Prepare inputs
        canonical_input = self.context.phase_inputs.get(PhaseID.PHASE_1, {}).get(
            "canonical_input"
        ) or {}

        signal_registry = QuestionnaireSignalRegistry()
        structural_profile = self.context.phase_inputs.get(PhaseID.PHASE_1, {}).get(
            "structural_profile"
        )

        # Execute Phase 1 with full contract
        cpp = execute_phase_1_with_full_contract(
            canonical_input=canonical_input,
            signal_registry=signal_registry,
            structural_profile=structural_profile,
        )

        # Extract chunk count
        chunk_count = (
            len(cpp.chunk_graph.chunks)
            if hasattr(cpp, "chunk_graph")
            else len(getattr(cpp, "chunks", []))
        )

        # Validate constitutional invariant
        if chunk_count != CONSTITUTIONAL_INVARIANTS["micro_questions"]:
            raise ValueError(
                f"Phase 1 must produce {CONSTITUTIONAL_INVARIANTS['micro_questions']} chunks, "
                f"got {chunk_count}"
            )

        document_id = getattr(cpp, "document_id", "UNKNOWN")

        self.logger.info("phase_1_complete", chunk_count=chunk_count)

        return Phase1Output(
            cpp=cpp,
            document_id=document_id,
            chunk_count=chunk_count,
            structural_profile=structural_profile or {},
        )

    def _execute_phase_2(self) -> Phase2Output:
        """
        PHASE 2: Executor Factory & Dispatch

        Materializa explícitamente:
        - QuestionnaireSignalRegistry
        - Preprocessed document (CPP adapter)
        - IrrigationSynchronizer
        - ExecutionPlan
        - TaskExecutor con 300 task results
        """
        self.logger.info("executing_phase_2_factory_dispatch")

        phase1_output = self.context.get_phase_output(PhaseID.PHASE_1)
        if phase1_output is None:
            raise ValueError("Phase 2 requires Phase 1 output")

        cpp = phase1_output.cpp
        questionnaire_data = self.context.questionnaire.data

        # Node trace for topological validation
        node_trace: list[str] = []

        # Step 1: Signal registry
        questionnaire_signal_registry = QuestionnaireSignalRegistry()
        node_trace.append("phase2.signal_registry")

        # Step 2: CPP adapter
        preprocessed_document = adapt_cpp_to_orchestrator(cpp, phase1_output.document_id)
        node_trace.append("phase2.cpp_adapter")

        # Step 3: Irrigation synchronizer
        synchronizer = IrrigationSynchronizer(
            questionnaire=questionnaire_data,
            preprocessed_document=preprocessed_document,
            signal_registry=questionnaire_signal_registry,
            contracts=None,
            enable_join_table=False,
        )
        node_trace.append("phase2.irrigation_synchronizer")

        # Step 4: Build execution plan
        execution_plan = synchronizer.build_execution_plan()
        node_trace.append("phase2.execution_plan")

        # Step 5: Task execution
        executor = TaskExecutor(
            questionnaire_monolith=questionnaire_data,
            preprocessed_document=preprocessed_document,
            signal_registry=questionnaire_signal_registry,
            calibration_registry=self.context.calibration_registry,
            pdm_profile=None,
        )
        task_results = executor.execute_plan(execution_plan)
        node_trace.append("phase2.task_execution")

        # Validate constitutional invariant
        if len(task_results) != CONSTITUTIONAL_INVARIANTS["micro_questions"]:
            raise ValueError(
                f"Phase 2 must produce {CONSTITUTIONAL_INVARIANTS['micro_questions']} task results, "
                f"got {len(task_results)}"
            )

        self.logger.info("phase_2_complete", task_count=len(task_results))

        return Phase2Output(
            execution_plan=execution_plan,
            task_results=task_results,
            preprocessed_document=preprocessed_document,
            questionnaire_signal_registry=questionnaire_signal_registry,
            node_trace=tuple(node_trace),
        )

    def _execute_phase_3(self) -> Phase3Output:
        """
        PHASE 3: Layer Scoring

        Materializa explícitamente:
        - SignalEnrichedScorer
        - Score extraction (300 micro-questions)
        - Quality validation
        - 300 ScoredMicroQuestion outputs
        """
        self.logger.info("executing_phase_3_layer_scoring")

        phase2_output = self.context.get_phase_output(PhaseID.PHASE_2)
        if phase2_output is None:
            raise ValueError("Phase 3 requires Phase 2 output")

        questionnaire_data = self.context.questionnaire.data
        questions = {
            q.get("question_id"): q
            for q in questionnaire_data.get("blocks", {}).get("micro_questions", [])
            if q.get("question_id")
        }

        node_trace: list[str] = []

        # Step 1: Initialize scorer
        scorer = SignalEnrichedScorer(
            signal_registry=phase2_output.questionnaire_signal_registry
        )
        node_trace.append("phase3.input_projection")

        # Step 2: Extract and validate scores
        scored_micro_questions: list[ScoredMicroQuestion] = []
        scored_results: list[ScoredResult] = []

        for task_result in phase2_output.task_results:
            if not isinstance(task_result.output, dict):
                raise ValueError(
                    f"Phase 3 requires dict evidence output, got {type(task_result.output).__name__}"
                )

            evidence = task_result.output
            score = extract_score_from_nexus(evidence)
            completeness = evidence.get("completeness")
            quality = map_completeness_to_quality(completeness)

            validated_quality, validation_details = scorer.validate_quality_level(
                question_id=task_result.question_id,
                quality_level=quality,
                score=score,
                completeness=completeness,
            )

            question = questions.get(task_result.question_id, {})
            base_slot = task_result.metadata.get("base_slot", task_result.question_id)

            scored_micro_questions.append(
                ScoredMicroQuestion(
                    question_id=task_result.question_id,
                    question_global=task_result.question_global,
                    base_slot=base_slot,
                    score=score,
                    normalized_score=score,
                    quality_level=validated_quality,
                    evidence=evidence,
                    scoring_details={
                        "quality_validation": validation_details,
                        "signals_resolved": task_result.metadata.get("resolved_signal_count"),
                    },
                    metadata={
                        "policy_area_id": task_result.policy_area_id,
                        "dimension_id": task_result.dimension_id,
                        "question_text": question.get("text", ""),
                    },
                    error=task_result.error,
                )
            )

            scored_results.append(
                ScoredResult(
                    question_global=task_result.question_global,
                    base_slot=base_slot,
                    policy_area=task_result.policy_area_id,
                    dimension=task_result.dimension_id,
                    score=score,
                    quality_level=validated_quality,
                    evidence=evidence,
                    raw_results=evidence,
                )
            )

        node_trace.append("phase3.score_extraction")
        node_trace.append("phase3.quality_validation")

        # Validate constitutional invariant
        if len(scored_micro_questions) != CONSTITUTIONAL_INVARIANTS["micro_questions"]:
            raise ValueError(
                f"Phase 3 must output {CONSTITUTIONAL_INVARIANTS['micro_questions']} scored questions, "
                f"got {len(scored_micro_questions)}"
            )

        node_trace.append("phase3.output_projection")

        self.logger.info("phase_3_complete", score_count=len(scored_micro_questions))

        return Phase3Output(
            layer_scores=scored_micro_questions,
            scored_results=scored_results,
            node_trace=tuple(node_trace),
        )

    def _execute_phase_4(self) -> Phase4Output:
        """
        PHASE 4: Dimension Aggregation

        Materializa explícitamente:
        - DimensionAggregator (Choquet integral)
        - 60 dimension scores (10 PA × 6 DIM)
        """
        self.logger.info("executing_phase_4_dimension_aggregation")

        phase3_output = self.context.get_phase_output(PhaseID.PHASE_3)
        if phase3_output is None:
            raise ValueError("Phase 4 requires Phase 3 output")

        phase2_output = self.context.get_phase_output(PhaseID.PHASE_2)

        node_trace: list[str] = []

        # Initialize aggregator
        aggregator = DimensionAggregator(
            monolith=self.context.questionnaire.data,
            abort_on_insufficient=True,
            signal_registry=getattr(phase2_output, "questionnaire_signal_registry", None),
        )
        node_trace.append("phase4.aggregation_settings")

        # Aggregate to dimensions
        dimension_scores = aggregator.run(
            phase3_output.scored_results,
            group_by_keys=aggregator.dimension_group_by_keys,
        )
        node_trace.append("phase4.dimension_aggregation")

        # Validate constitutional invariant
        if len(dimension_scores) != CONSTITUTIONAL_INVARIANTS["dimensions"]:
            raise ValueError(
                f"Phase 4 must output {CONSTITUTIONAL_INVARIANTS['dimensions']} dimension scores, "
                f"got {len(dimension_scores)}"
            )

        self.logger.info("phase_4_complete", dimension_count=len(dimension_scores))

        return Phase4Output(
            dimension_scores=dimension_scores,
            node_trace=tuple(node_trace),
        )

    def _execute_phase_5(self) -> Phase5Output:
        """
        PHASE 5: Policy Area Aggregation

        Materializa explícitamente:
        - Async aggregation
        - 10 policy area scores
        """
        self.logger.info("executing_phase_5_policy_area_aggregation")

        phase4_output = self.context.get_phase_output(PhaseID.PHASE_4)
        if phase4_output is None:
            raise ValueError("Phase 5 requires Phase 4 output")

        phase2_output = self.context.get_phase_output(PhaseID.PHASE_2)

        node_trace: list[str] = []
        node_trace.append("phase5.aggregation")

        # Define async execution
        async def _run() -> list[Any]:
            return await run_phase5_aggregation(
                dimension_scores=phase4_output.dimension_scores,
                questionnaire=self.context.questionnaire.data,
                signal_registry=getattr(phase2_output, "questionnaire_signal_registry", None),
                validate=True,
            )

        # Execute with event loop handling
        try:
            area_scores = asyncio.run(_run())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                area_scores = loop.run_until_complete(_run())
            finally:
                loop.close()
                asyncio.set_event_loop(None)

        node_trace.append("phase5.validation")

        # Validate constitutional invariant
        if len(area_scores) != CONSTITUTIONAL_INVARIANTS["policy_areas"]:
            raise ValueError(
                f"Phase 5 must output {CONSTITUTIONAL_INVARIANTS['policy_areas']} area scores, "
                f"got {len(area_scores)}"
            )

        self.logger.info("phase_5_complete", area_count=len(area_scores))

        return Phase5Output(
            area_scores=area_scores,
            node_trace=tuple(node_trace),
        )

    def _execute_phase_6(self) -> Phase6Output:
        """
        PHASE 6: Cluster Aggregation

        Materializa explícitamente:
        - ClusterAggregator
        - 4 MESO cluster scores
        """
        self.logger.info("executing_phase_6_cluster_aggregation")

        phase5_output = self.context.get_phase_output(PhaseID.PHASE_5)
        if phase5_output is None:
            raise ValueError("Phase 6 requires Phase 5 output")

        # Initialize aggregator
        aggregator = ClusterAggregator(
            monolith=self.context.questionnaire.data,
            abort_on_insufficient=True,
            enforce_contracts=True,
            contract_mode="strict",
        )

        # Aggregate to clusters
        cluster_scores = aggregator.aggregate(phase5_output.area_scores)

        # Validate constitutional invariant
        if len(cluster_scores) != CONSTITUTIONAL_INVARIANTS["clusters"]:
            raise ValueError(
                f"Phase 6 must output {CONSTITUTIONAL_INVARIANTS['clusters']} cluster scores, "
                f"got {len(cluster_scores)}"
            )

        self.logger.info("phase_6_complete", cluster_count=len(cluster_scores))

        return Phase6Output(
            cluster_scores=cluster_scores,
            node_trace=("phase6.cluster_aggregation",),
        )

    def _execute_phase_7(self) -> Phase7Output:
        """
        PHASE 7: Macro Aggregation

        Materializa explícitamente:
        - MacroAggregator
        - 1 holistic macro score
        """
        self.logger.info("executing_phase_7_macro_aggregation")

        phase6_output = self.context.get_phase_output(PhaseID.PHASE_6)
        if phase6_output is None:
            raise ValueError("Phase 7 requires Phase 6 output")

        # Initialize aggregator
        aggregator = MacroAggregator()

        # Aggregate to macro
        macro_score = aggregator.aggregate(phase6_output.cluster_scores)

        # Validate constitutional invariant
        if not hasattr(macro_score, "score"):
            raise ValueError("Phase 7 macro_score must expose score attribute")

        self.logger.info(
            "phase_7_complete",
            macro_score=getattr(macro_score, "score", None),
        )

        return Phase7Output(
            macro_score=macro_score,
            node_trace=("phase7.macro_aggregation",),
        )

    def _execute_phase_8(self) -> Phase8Output:
        """
        PHASE 8: Recommendations Engine

        Materializa explícitamente:
        - RecommendationEngineAdapter
        - Signal-enriched recommendations
        """
        self.logger.info("executing_phase_8_recommendations")

        phase4_output = self.context.get_phase_output(PhaseID.PHASE_4)
        phase6_output = self.context.get_phase_output(PhaseID.PHASE_6)
        phase7_output = self.context.get_phase_output(PhaseID.PHASE_7)

        if any(output is None for output in [phase4_output, phase6_output, phase7_output]):
            raise ValueError("Phase 8 requires outputs from phases 4, 6, and 7")

        node_trace: list[str] = []

        # Initialize adapter
        phase8_root = Path(__file__).resolve().parents[1] / "phases" / "Phase_08"
        rules_path = phase8_root / RULES_PATH_ENHANCED
        schema_path = phase8_root / SCHEMA_PATH

        adapter = RecommendationEngineAdapter(
            rules_path=rules_path,
            schema_path=schema_path,
            questionnaire_provider=self.context.wiring.provider if self.context.wiring else None,
            orchestrator=None,
        )
        node_trace.append("phase8.adapter_init")

        # Prepare data
        micro_scores = {
            f"{score.area_id}-{score.dimension_id}": score.score
            for score in phase4_output.dimension_scores
        }
        cluster_data = {
            cluster.cluster_id: {
                "cluster_id": cluster.cluster_id,
                "score": cluster.score,
                "coherence": cluster.coherence,
                "variance": cluster.variance,
                "penalty_applied": cluster.penalty_applied,
            }
            for cluster in phase6_output.cluster_scores
        }
        macro_data = {
            "score": phase7_output.macro_score.score,
            "quality_level": phase7_output.macro_score.quality_level,
        }

        # Generate recommendations
        recommendations = adapter.generate_all_recommendations(
            micro_scores=micro_scores,
            cluster_data=cluster_data,
            macro_data=macro_data,
            context={"pipeline_version": __version__},
        )
        node_trace.append("phase8.recommendation_generation")

        self.logger.info("phase_8_complete", recommendation_count=len(recommendations))

        return Phase8Output(
            recommendations=recommendations,
            node_trace=tuple(node_trace),
        )

    def _execute_phase_9(self) -> Phase9Output:
        """
        PHASE 9: Report Assembly

        Materializa explícitamente:
        - ReportAssembler
        - Final comprehensive report
        """
        self.logger.info("executing_phase_9_report_assembly")

        phase3_output = self.context.get_phase_output(PhaseID.PHASE_3)
        phase6_output = self.context.get_phase_output(PhaseID.PHASE_6)
        phase7_output = self.context.get_phase_output(PhaseID.PHASE_7)
        phase8_output = self.context.get_phase_output(PhaseID.PHASE_8)

        if any(output is None for output in [phase3_output, phase6_output, phase7_output, phase8_output]):
            raise ValueError("Phase 9 requires outputs from phases 3, 6, 7, and 8")

        node_trace: list[str] = []

        # Prepare execution results
        execution_results = {
            "questions": {
                q.question_id: {
                    "score": q.score,
                    "evidence": q.evidence,
                    "recommendation": None,
                    "human_answer": None,
                }
                for q in phase3_output.layer_scores
            },
            "meso_clusters": {
                cluster.cluster_id: {
                    "cluster_id": cluster.cluster_id,
                    "raw_meso_score": cluster.score,
                    "adjusted_score": cluster.score,
                    "dispersion_penalty": cluster.penalty_applied,
                    "peer_penalty": 0.0,
                    "total_penalty": cluster.penalty_applied,
                    "dispersion_metrics": {
                        "variance": cluster.variance,
                        "coherence": cluster.coherence,
                    },
                    "micro_scores": [area.score for area in cluster.area_scores],
                    "metadata": cluster.validation_details,
                }
                for cluster in phase6_output.cluster_scores
            },
            "macro_summary": {
                "overall_posterior": phase7_output.macro_score.score,
                "adjusted_score": phase7_output.macro_score.score,
                "coverage_penalty": 0.0,
                "dispersion_penalty": 0.0,
                "contradiction_penalty": 0.0,
                "total_penalty": 0.0,
                "contradiction_count": len(
                    getattr(phase7_output.macro_score, "systemic_gaps", [])
                ),
                "recommendations": phase8_output.recommendations,
                "metadata": {},
            },
            "micro_results": {
                q.question_id: {
                    "policy_area_id": q.metadata.get("policy_area_id"),
                    "patterns_used": [],
                    "completeness": q.scoring_details.get("quality_validation", {}).get("completeness"),
                    "validation": {"status": "passed" if q.error is None else "failed"},
                }
                for q in phase3_output.layer_scores
            },
        }

        # Create assembler
        assembler = create_report_assembler(
            questionnaire_provider=self.context.wiring.provider,
            evidence_registry=None,
            qmcm_recorder=None,
            orchestrator=None,
        )
        node_trace.append("phase9.report_assembler")

        # Assemble report
        plan_name = self.config.get("plan_name", "Plan Municipal de Desarrollo")
        report = assembler.assemble_report(
            plan_name=plan_name,
            execution_results=execution_results,
            enriched_packs=None,
        )
        node_trace.append("phase9.report_assembly")

        self.logger.info("phase_9_complete", report_generated=True)

        return Phase9Output(
            report=report,
            node_trace=tuple(node_trace),
        )

    def _run_sisas_cycle(self, phase_id: PhaseID) -> None:
        """Execute SISAS signal generation/propagation/irrigation for a phase."""
        if self.context.sisas is None:
            return

        if not self.config.get("enable_sisas", True):
            return

        # Map phase to SISAS phase identifier
        sisas_phase_map = {
            PhaseID.PHASE_0: "phase_0",
            PhaseID.PHASE_1: "phase_1",
            PhaseID.PHASE_2: "phase_2",
            PhaseID.PHASE_3: "phase_3",
            PhaseID.PHASE_4: "phase_4",
            PhaseID.PHASE_5: "phase_5",
            PhaseID.PHASE_6: "phase_6",
            PhaseID.PHASE_7: "phase_7",
            PhaseID.PHASE_8: "phase_8",
            PhaseID.PHASE_9: "phase_9",
        }

        sisas_phase = sisas_phase_map.get(phase_id)
        if sisas_phase is None:
            return

        base_path = self.config.get("sisas_base_path", "")
        try:
            results = self.context.sisas.execute_irrigation_phase(sisas_phase, base_path)
            summary = self.context.sisas.irrigation_executor.get_execution_summary()
            self.context.signal_metrics[phase_id.value] = {
                "irrigation_phase": sisas_phase,
                "routes_executed": len(results) if results else 0,
                "summary": summary,
            }
        except Exception as exc:
            if self.strict_mode:
                raise
            self.logger.warning(
                "sisas_irrigation_failed",
                phase=phase_id.value,
                error=str(exc),
            )


# =============================================================================
# CLI INTEGRATION - MATERIALIZACIÓN EXPLÍCITA
# =============================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for monolithic orchestrator."""
    parser = argparse.ArgumentParser(
        description="FARFAN MCDPP - Monolithic Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute full pipeline with defaults
  python -m farfan_pipeline.orchestration.monolithic_orchestrator

  # Execute with custom questionnaire
  python -m farfan_pipeline.orchestration.monolithic_orchestrator --questionnaire /path/to/questionnaire.json

  # Execute with custom plan name
  python -m farfan_pipeline.orchestration.monolithic_orchestrator --plan-name "Mi Plan Municipal"

  # Non-strict mode (continue on errors)
  python -m farfan_pipeline.orchestration.monolithic_orchestrator --no-strict
        """,
    )

    # Questionnaire options
    parser.add_argument(
        "--questionnaire",
        type=str,
        help="Path to questionnaire JSON (default: uses canonic_questionnaire_central)",
    )
    parser.add_argument(
        "--questionnaire-hash",
        type=str,
        default="",
        help="Expected SHA-256 hash of questionnaire",
    )

    # Execution options
    parser.add_argument(
        "--plan-name",
        type=str,
        default="Plan Municipal de Desarrollo",
        help="Name of the municipal development plan",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Enable strict mode (fail on critical violations)",
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Disable strict mode (continue on errors)",
    )
    parser.add_argument(
        "--deterministic",
        action="store_true",
        default=True,
        help="Enable deterministic mode (fixed seed)",
    )
    parser.add_argument(
        "--no-deterministic",
        action="store_false",
        dest="deterministic",
        help="Disable deterministic mode",
    )

    # Feature flags
    parser.add_argument(
        "--enable-sisas",
        action="store_true",
        default=True,
        help="Enable SISAS signal system",
    )
    parser.add_argument(
        "--enable-calibration",
        action="store_true",
        default=True,
        help="Enable calibration system",
    )

    # Logging
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        help="Path to write JSON execution summary",
    )

    return parser


def main() -> int:
    """Main entry point for monolithic orchestrator CLI."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Build configuration
    config = {
        "questionnaire_path": args.questionnaire,
        "questionnaire_hash": args.questionnaire_hash,
        "plan_name": args.plan_name,
        "enable_sisas": args.enable_sisas,
        "enable_calibration": args.enable_calibration,
    }

    # Create and execute orchestrator
    orchestrator = MonolithicOrchestrator(
        config=config,
        strict_mode=args.strict,
        deterministic=args.deterministic,
    )

    try:
        context = orchestrator.execute_full_pipeline()
        summary = context.get_execution_summary()

        print("\n" + "=" * 80)
        print("EJECUCIÓN COMPLETA DEL PIPELINE")
        print("=" * 80)
        print(f"Execution ID: {summary['execution_id']}")
        print(f"Elapsed Time: {summary['elapsed_time_s']:.2f}s")
        print(f"Phases Completed: {summary['phases_completed']}/{summary['total_phases']}")
        print(f"Phases Failed: {summary['phases_failed']}")
        print(f"Total Violations: {summary['total_violations']}")
        print(f"Critical Violations: {summary['critical_violations']}")
        print(f"Deterministic: {summary['deterministic']}")
        print("=" * 80 + "\n")

        # Write JSON output if requested
        if args.json_output:
            output_data = {
                "summary": summary,
                "phase_results": {
                    phase_id.value: result.to_dict()
                    for phase_id, result in context.phase_results.items()
                },
            }
            with open(args.json_output, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"JSON output written to: {args.json_output}\n")

        return 0 if summary["phases_failed"] == 0 else 1

    except Exception as e:
        print(f"\nERROR: Pipeline execution failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main orchestrator
    "MonolithicOrchestrator",

    # Phase identifiers
    "PhaseID",
    "PhaseStatus",

    # Phase outputs
    "Phase0Output",
    "Phase1Output",
    "Phase2Output",
    "Phase3Output",
    "Phase4Output",
    "Phase5Output",
    "Phase6Output",
    "Phase7Output",
    "Phase8Output",
    "Phase9Output",

    # Execution context
    "ExecutionContext",
    "PhaseResult",

    # SISAS lifecycle
    "SisasLifecycle",

    # CLI
    "main",
    "create_argument_parser",

    # Constants
    "CANONICAL_POLICY_AREA_DEFINITIONS",
    "CONSTITUTIONAL_INVARIANTS",
]
