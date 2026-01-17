"""
Core Orchestrator - Production-Grade Pipeline Coordination.

This module provides comprehensive orchestration for the canonical F.A.R.F.A.N pipeline
phases Phase 0 through Phase 9 (no implicit transitions), with contract validation,
SISAS lifecycle governance, determinism enforcement, and error handling.

Architecture:
- PipelineOrchestrator: Main coordinator for full pipeline execution (P00–P09)
- ExecutionContext: Shared state and metrics across phases
- ContractEnforcer: Pre/post execution contract validation
- Phase specifications: explicit entry conditions, outputs, and handoffs

Author: F.A.R.F.A.N Core Team
Version: 3.0.0
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "3.0.0"
__module_type__ = "ORCH"
__criticality__ = "CRITICAL"
__lifecycle__ = "ACTIVE"
__execution_pattern__ = "Singleton"
__phase_label__ = "Core Pipeline Orchestrator"
__compliance_status__ = "GNEA_COMPLIANT"
__sin_carreta_compliant__ = True

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import blake3
import structlog

from canonic_questionnaire_central import (
    QuestionnairePort,
    resolve_questionnaire,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import (
    BusRegistry,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import (
    ContractRegistry,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import (
    EventStore,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_executor import (
    IrrigationExecutor,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_map import (
    IrrigationMap,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals import (
    SignalRegistry,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_context_scoper import (
    SignalContextScoperVehicle,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_registry import (
    SignalRegistryVehicle,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.alignment_checker import (
    VocabularyAlignmentChecker,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.capability_vocabulary import (
    CapabilityVocabulary,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.signal_vocabulary import (
    SignalVocabulary,
)
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

logger = structlog.get_logger(__name__)


# =============================================================================
# PHASE DEFINITIONS
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


# Phase metadata registry
PHASE_METADATA = {
    PhaseID.PHASE_0: {
        "name": "Bootstrap & Validation",
        "description": "Infrastructure setup, determinism, resource control",
        "stages": 7,
        "constitutional_invariants": ["wiring_integrity", "resource_limits"],
    },
    PhaseID.PHASE_1: {
        "name": "CPP Ingestion",
        "description": "Document processing and semantic assignment",
        "expected_output_count": 300,  # Updated to question-level granularity
        "constitutional_invariants": ["300_questions", "10_policy_areas", "6_dimensions"],
    },
    PhaseID.PHASE_2: {
        "name": "Executor Factory & Dispatch",
        "description": "Method dispensary instantiation and routing",
        "expected_executor_count": 30,
        "constitutional_invariants": ["method_registry_complete", "executor_wiring"],
    },
    PhaseID.PHASE_3: {
        "name": "Layer Scoring",
        "description": "8-layer quality assessment per micro-question",
        "layers": 8,
        "constitutional_invariants": ["8_layer_completeness", "score_bounds"],
    },
    PhaseID.PHASE_4: {
        "name": "Dimension Aggregation",
        "description": "Choquet integral aggregation to dimensions",
        "expected_output_count": 60,  # 10 PA × 6 DIM
        "constitutional_invariants": ["60_dimensions", "choquet_integrity"],
    },
    PhaseID.PHASE_5: {
        "name": "Policy Area Aggregation",
        "description": "Dimension aggregation to policy areas",
        "expected_output_count": 10,  # 10 policy areas
        "constitutional_invariants": ["10_policy_areas", "coherence_penalty"],
    },
    PhaseID.PHASE_6: {
        "name": "Cluster Aggregation",
        "description": "Policy area aggregation to MESO clusters",
        "expected_output_count": 4,  # 4 clusters
        "constitutional_invariants": ["4_clusters", "cluster_boundaries"],
    },
    PhaseID.PHASE_7: {
        "name": "Macro Aggregation",
        "description": "Cluster aggregation to holistic score",
        "expected_output_count": 1,  # Final macro score
        "constitutional_invariants": ["single_macro_score", "provenance_chain"],
    },
    PhaseID.PHASE_8: {
        "name": "Recommendations Engine",
        "description": "Signal-enriched recommendation generation",
        "constitutional_invariants": ["signal_integration", "sota_findings"],
    },
    PhaseID.PHASE_9: {
        "name": "Report Assembly",
        "description": "Final report generation and assembly",
        "constitutional_invariants": ["report_completeness", "schema_compliance"],
    },
}


# =============================================================================
# FLOW SPECIFICATIONS & SISAS LIFECYCLE
# =============================================================================


class MissingPhaseExecutorError(RuntimeError):
    """Raised when a required phase executor is not registered."""


@dataclass(frozen=True)
class PhaseSpecification:
    """Explicit phase specification with entry conditions and handoff contract."""

    phase_id: PhaseID
    name: str
    entry_conditions: tuple[str, ...]
    required_phases: tuple[PhaseID, ...]
    produces: tuple[str, ...]
    next_phase: PhaseID | None
    phase_root: Path
    manifest_path: Path | None
    inventory_path: Path | None


@dataclass(frozen=True)
class PhaseCoverageReport:
    """Coverage report for phase file and graph validation."""

    phase_id: PhaseID
    expected_files: tuple[str, ...]
    actual_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    extra_files: tuple[str, ...]
    manifest_nodes: tuple[str, ...]
    stage_order: tuple[int, ...]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class PhaseHandoff:
    """Record of a phase handoff for traceability."""

    from_phase: PhaseID | None
    to_phase: PhaseID
    input_keys: tuple[str, ...]
    output_keys: tuple[str, ...]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class Phase0Output:
    """Phase 0 output containing wiring, questionnaire, and SISAS lifecycle."""

    wiring: WiringComponents
    questionnaire: QuestionnairePort
    sisas: "SisasLifecycle"
    signal_registry_types: tuple[str, ...]


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
        bus_registry = BusRegistry()
        contract_registry = ContractRegistry()
        event_store = EventStore()

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
                    "SISAS vocabulary alignment failed with critical issues: "
                    f"{len(critical_issues)}"
                )

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

    def load_irrigation_map_from_csv(self, csv_path: Path) -> None:
        """Load irrigation map from a canonical CSV (sabana)."""
        if not csv_path.exists():
            raise FileNotFoundError(f"Irrigation CSV not found: {csv_path}")

        import csv

        with csv_path.open("r", encoding="utf-8") as handle:
            data = list(csv.DictReader(handle))

        self.irrigation_map = IrrigationMap.from_sabana_csv(data)
        self.irrigation_executor.irrigation_map = self.irrigation_map

    def execute_irrigation_phase(self, phase: str, base_path: str = "") -> Any:
        """Execute all irrigable SISAS routes for a phase."""
        return self.irrigation_executor.execute_phase(phase, base_path)

    def execute_all_irrigable(self, base_path: str = "") -> Any:
        """Execute all currently irrigable SISAS routes."""
        return self.irrigation_executor.execute_all_irrigable(base_path)

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
# EXECUTION CONTEXT
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
    """Shared context across all pipeline phases.

    This context maintains:
    - Wiring components from Phase 0 bootstrap
    - Canonical questionnaire (resolved via canonic_questionnaire_central)
    - SISAS lifecycle manager for signal orchestration
    - Phase outputs for handoff between phases
    - Execution metrics and telemetry
    - Determinism tracking (hashes, seeds)
    """

    # Core components from bootstrap
    wiring: WiringComponents | None = None
    questionnaire: QuestionnairePort | None = None
    sisas: SisasLifecycle | None = None

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
    phase_handoffs: list[PhaseHandoff] = field(default_factory=list)
    phase_coverage: dict[PhaseID, PhaseCoverageReport] = field(default_factory=dict)

    def add_phase_result(self, result: PhaseResult) -> None:
        """Add a phase execution result."""
        self.phase_results[result.phase_id] = result
        self.phase_outputs[result.phase_id] = result.output
        self.total_violations.extend(result.violations)

    def record_handoff(self, handoff: PhaseHandoff) -> None:
        """Record explicit handoff between phases for traceability."""
        self.phase_handoffs.append(handoff)

    def record_phase_coverage(self, report: PhaseCoverageReport) -> None:
        """Record phase coverage validation report."""
        self.phase_coverage[report.phase_id] = report

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
            "handoffs_recorded": len(self.phase_handoffs),
            "sisas_metrics": self.signal_metrics,
        }


# =============================================================================
# CONTRACT ENFORCEMENT
# =============================================================================


class PhaseExecutor(Protocol):
    """Protocol for phase-specific executors."""

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        """Validate input contract before execution."""
        ...

    def execute(self, context: ExecutionContext) -> Any:
        """Execute the phase logic."""
        ...

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        """Validate output contract after execution."""
        ...


class ContractEnforcer:
    """Enforces input/output contracts for phase transitions."""

    def __init__(self, strict_mode: bool = True):
        """Initialize contract enforcer.

        Args:
            strict_mode: If True, raise exceptions on critical violations
        """
        self.strict_mode = strict_mode
        self.logger = structlog.get_logger(f"{__name__}.ContractEnforcer")

    def validate_input_contract(
        self, phase_id: PhaseID, context: ExecutionContext
    ) -> ValidationResult:
        """Validate input contract for a phase.

        Args:
            phase_id: Phase to validate
            context: Execution context with phase outputs

        Returns:
            ValidationResult with violations
        """
        violations = []
        start_time = time.time()

        self.logger.info("validating_input_contract", phase=phase_id.value)

        # Phase-specific input validation
        if phase_id == PhaseID.PHASE_1:
            violations.extend(self._validate_phase1_input(context))
        elif phase_id == PhaseID.PHASE_2:
            violations.extend(self._validate_phase2_input(context))
        elif phase_id == PhaseID.PHASE_3:
            violations.extend(self._validate_phase3_input(context))
        elif phase_id == PhaseID.PHASE_4:
            violations.extend(self._validate_phase4_input(context))
        elif phase_id == PhaseID.PHASE_5:
            violations.extend(self._validate_phase5_input(context))
        elif phase_id == PhaseID.PHASE_6:
            violations.extend(self._validate_phase6_input(context))
        elif phase_id == PhaseID.PHASE_7:
            violations.extend(self._validate_phase7_input(context))
        elif phase_id == PhaseID.PHASE_8:
            violations.extend(self._validate_phase8_input(context))
        elif phase_id == PhaseID.PHASE_9:
            violations.extend(self._validate_phase9_input(context))

        validation_time_ms = (time.time() - start_time) * 1000
        critical_count = sum(1 for v in violations if v.severity == Severity.CRITICAL)

        result = ValidationResult(
            passed=critical_count == 0,
            violations=violations,
            validation_time_ms=validation_time_ms,
        )

        if not result.passed and self.strict_mode:
            raise ValueError(
                f"Input contract validation failed for {phase_id.value} "
                f"with {critical_count} critical violations"
            )

        return result

    def validate_output_contract(
        self, phase_id: PhaseID, output: Any, context: ExecutionContext
    ) -> ValidationResult:
        """Validate output contract for a phase.

        Args:
            phase_id: Phase that produced output
            output: Phase output to validate
            context: Execution context

        Returns:
            ValidationResult with violations
        """
        violations = []
        start_time = time.time()

        self.logger.info("validating_output_contract", phase=phase_id.value)

        # Phase-specific output validation
        if phase_id == PhaseID.PHASE_0:
            violations.extend(self._validate_phase0_output(output, context))
        elif phase_id == PhaseID.PHASE_1:
            violations.extend(self._validate_phase1_output(output, context))
        elif phase_id == PhaseID.PHASE_2:
            violations.extend(self._validate_phase2_output(output, context))
        elif phase_id == PhaseID.PHASE_3:
            violations.extend(self._validate_phase3_output(output, context))
        elif phase_id == PhaseID.PHASE_4:
            violations.extend(self._validate_phase4_output(output, context))
        elif phase_id == PhaseID.PHASE_5:
            violations.extend(self._validate_phase5_output(output, context))
        elif phase_id == PhaseID.PHASE_6:
            violations.extend(self._validate_phase6_output(output, context))
        elif phase_id == PhaseID.PHASE_7:
            violations.extend(self._validate_phase7_output(output, context))
        elif phase_id == PhaseID.PHASE_8:
            violations.extend(self._validate_phase8_output(output, context))
        elif phase_id == PhaseID.PHASE_9:
            violations.extend(self._validate_phase9_output(output, context))

        validation_time_ms = (time.time() - start_time) * 1000
        critical_count = sum(1 for v in violations if v.severity == Severity.CRITICAL)

        result = ValidationResult(
            passed=critical_count == 0,
            violations=violations,
            validation_time_ms=validation_time_ms,
        )

        if not result.passed and self.strict_mode:
            raise ValueError(
                f"Output contract validation failed for {phase_id.value} "
                f"with {critical_count} critical violations"
            )

        return result

    # =========================================================================
    # INPUT VALIDATION METHODS
    # =========================================================================

    def _validate_phase1_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 1 input (requires Phase 0 bootstrap)."""
        violations = []

        # Require Phase 0 completion
        if PhaseID.PHASE_0 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_01.input",
                    message="Phase 0 must complete before Phase 1",
                    remediation="Execute Phase 0 bootstrap first",
                )
            )

        # Validate wiring components
        if not context.wiring:
            violations.append(
                ContractViolation(
                    type="MISSING_WIRING",
                    severity=Severity.CRITICAL,
                    component_path="Phase_01.input",
                    message="Wiring components not initialized",
                    remediation="Phase 0 bootstrap must provide WiringComponents",
                )
            )

        if context.questionnaire is None:
            violations.append(
                ContractViolation(
                    type="MISSING_QUESTIONNAIRE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_01.input",
                    message="Canonical questionnaire not resolved",
                    remediation="Phase 0 must resolve questionnaire via CQC resolver",
                )
            )

        if context.sisas is None:
            violations.append(
                ContractViolation(
                    type="MISSING_SISAS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_01.input",
                    message="SISAS lifecycle not initialized",
                    remediation="Phase 0 must initialize SISAS lifecycle",
                )
            )

        return violations

    def _validate_phase2_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 2 input (requires Phase 1 CPP output)."""
        violations = []

        # Require Phase 1 completion
        if PhaseID.PHASE_1 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.input",
                    message="Phase 1 must complete before Phase 2",
                    remediation="Execute Phase 1 CPP ingestion first",
                )
            )
            return violations

        # Validate CPP output exists
        cpp = context.get_phase_output(PhaseID.PHASE_1)
        if not cpp:
            violations.append(
                ContractViolation(
                    type="MISSING_CPP",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.input",
                    message="Phase 1 did not produce CPP output",
                    remediation="Verify Phase 1 execution completed successfully",
                )
            )

        return violations

    def _validate_phase3_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 3 input (requires Phase 2 executor factory)."""
        violations = []

        if PhaseID.PHASE_2 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.input",
                    message="Phase 2 must complete before Phase 3",
                    remediation="Execute Phase 2 executor factory first",
                )
            )

        return violations

    def _validate_phase4_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 4 input (requires Phase 3 layer scores)."""
        violations = []

        if PhaseID.PHASE_3 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.input",
                    message="Phase 3 must complete before Phase 4",
                    remediation="Execute Phase 3 layer scoring first",
                )
            )

        return violations

    def _validate_phase5_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 5 input (requires Phase 4 dimension scores)."""
        violations = []

        if PhaseID.PHASE_4 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_05.input",
                    message="Phase 4 must complete before Phase 5",
                    remediation="Execute Phase 4 dimension aggregation first",
                )
            )

        return violations

    def _validate_phase6_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 6 input (requires Phase 5 policy area scores)."""
        violations = []

        if PhaseID.PHASE_5 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_06.input",
                    message="Phase 5 must complete before Phase 6",
                    remediation="Execute Phase 5 policy area aggregation first",
                )
            )

        return violations

    def _validate_phase7_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 7 input (requires Phase 6 cluster scores)."""
        violations = []

        if PhaseID.PHASE_6 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_07.input",
                    message="Phase 6 must complete before Phase 7",
                    remediation="Execute Phase 6 cluster aggregation first",
                )
            )

        return violations

    def _validate_phase8_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 8 input (requires Phase 7 macro score)."""
        violations = []

        if PhaseID.PHASE_7 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_08.input",
                    message="Phase 7 must complete before Phase 8",
                    remediation="Execute Phase 7 macro aggregation first",
                )
            )

        return violations

    def _validate_phase9_input(self, context: ExecutionContext) -> list[ContractViolation]:
        """Validate Phase 9 input (requires Phase 8 recommendations)."""
        violations = []

        if PhaseID.PHASE_8 not in context.phase_results:
            violations.append(
                ContractViolation(
                    type="MISSING_PREREQUISITE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_09.input",
                    message="Phase 8 must complete before Phase 9",
                    remediation="Execute Phase 8 recommendations engine first",
                )
            )

        return violations


    # =========================================================================
    # OUTPUT VALIDATION METHODS
    # =========================================================================

    def _validate_phase0_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 0 output (Phase0Output)."""
        violations = []

        if not isinstance(output, Phase0Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_00.output",
                    message="Phase 0 must return Phase0Output",
                    expected="Phase0Output",
                    actual=type(output).__name__,
                )
            )
            return violations

        wiring = output.wiring
        if not isinstance(wiring, WiringComponents):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_00.output.wiring",
                    message="Phase 0 wiring must be WiringComponents",
                    expected="WiringComponents",
                    actual=type(wiring).__name__,
                )
            )
            return violations

        # Validate required components
        required_components = [
            "provider",
            "signal_client",
            "signal_registry",
            "executor_config",
            "factory",
            "arg_router",
            "validator",
        ]

        for component in required_components:
            if not hasattr(wiring, component) or getattr(wiring, component) is None:
                violations.append(
                    ContractViolation(
                        type="MISSING_COMPONENT",
                        severity=Severity.CRITICAL,
                        component_path=f"Phase_00.output.wiring.{component}",
                        message=f"Required component '{component}' is missing or None",
                        remediation="Verify bootstrap initialization completed",
                    )
                )

        if output.questionnaire is None:
            violations.append(
                ContractViolation(
                    type="MISSING_QUESTIONNAIRE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_00.output.questionnaire",
                    message="Canonical questionnaire is required from resolver",
                    remediation="Resolve questionnaire via canonic_questionnaire_central",
                )
            )

        if output.sisas is None:
            violations.append(
                ContractViolation(
                    type="MISSING_SISAS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_00.output.sisas",
                    message="SISAS lifecycle must be initialized",
                    remediation="Initialize SISAS lifecycle in Phase 0",
                )
            )

        return violations

    def _validate_phase1_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 1 output (CanonPolicyPackage with 300 questions)."""
        violations = []

        # Basic structure validation
        if not output:
            violations.append(
                ContractViolation(
                    type="EMPTY_OUTPUT",
                    severity=Severity.CRITICAL,
                    component_path="Phase_01.output",
                    message="Phase 1 produced no output",
                )
            )
            return violations

        # Validate chunk count (300 questions = 10 PA × 6 DIM × 5 Q)
        expected_count = 300
        actual_count = None

        if hasattr(output, "chunk_graph") and hasattr(output.chunk_graph, "chunks"):
            actual_count = len(output.chunk_graph.chunks)
        elif hasattr(output, "smart_chunks"):
            actual_count = len(output.smart_chunks)
        elif hasattr(output, "chunks"):
            actual_count = len(output.chunks)

        if actual_count is None:
            violations.append(
                ContractViolation(
                    type="MISSING_CHUNKS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_01.output.chunks",
                    message="No chunks found in CPP output",
                )
            )
        elif actual_count != expected_count:
            violations.append(
                ContractViolation(
                    type="CHUNK_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_01.output.chunks",
                    message="Constitutional invariant violated: incorrect chunk count",
                    expected=expected_count,
                    actual=actual_count,
                    remediation=f"Expected {expected_count} chunks (10 PA × 6 DIM × 5 Q)",
                )
            )

        return violations

    def _validate_phase2_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 2 output (ExecutionPlan + TaskResults)."""
        violations = []

        if hasattr(output, "task_results"):
            actual_count = len(output.task_results)
            if actual_count != 300:
                violations.append(
                    ContractViolation(
                        type="TASK_COUNT_VIOLATION",
                        severity=Severity.CRITICAL,
                        component_path="Phase_02.output.task_results",
                        message="Phase 2 must produce 300 task results",
                        expected=300,
                        actual=actual_count,
                    )
                )
        else:
            violations.append(
                ContractViolation(
                    type="MISSING_TASK_RESULTS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.output.task_results",
                    message="Phase 2 output missing task_results",
                )
            )

        return violations

    def _validate_phase3_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 3 output (Layer scores for 300 micro-questions)."""
        violations = []

        # Validate score count (300 micro-questions × 8 layers)
        if hasattr(output, "layer_scores"):
            expected_count = 300
            actual_count = len(output.layer_scores)
            if actual_count != expected_count:
                violations.append(
                    ContractViolation(
                        type="SCORE_COUNT_VIOLATION",
                        severity=Severity.CRITICAL,
                        component_path="Phase_03.output.layer_scores",
                        message="Layer score count mismatch",
                        expected=expected_count,
                        actual=actual_count,
                    )
                )
        else:
            violations.append(
                ContractViolation(
                    type="MISSING_LAYER_SCORES",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.output.layer_scores",
                    message="Phase 3 output missing layer_scores",
                )
            )

        return violations

    def _validate_phase4_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 4 output (60 dimension scores)."""
        violations = []

        expected_count = 60  # 10 PA × 6 DIM

        if hasattr(output, "dimension_scores"):
            actual_count = len(output.dimension_scores)
        elif isinstance(output, list):
            actual_count = len(output)
        else:
            actual_count = None

        if actual_count is None:
            violations.append(
                ContractViolation(
                    type="MISSING_DIMENSION_SCORES",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.output",
                    message="Phase 4 output missing dimension scores",
                )
            )
        elif actual_count != expected_count:
            violations.append(
                ContractViolation(
                    type="DIMENSION_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.output",
                    message="Constitutional invariant: 60 dimension scores required",
                    expected=expected_count,
                    actual=actual_count,
                )
            )

        return violations

    def _validate_phase5_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 5 output (10 policy area scores)."""
        violations = []

        expected_count = 10  # 10 policy areas

        if hasattr(output, "area_scores"):
            actual_count = len(output.area_scores)
        elif isinstance(output, list):
            actual_count = len(output)
        else:
            actual_count = None

        if actual_count is None:
            violations.append(
                ContractViolation(
                    type="MISSING_AREA_SCORES",
                    severity=Severity.CRITICAL,
                    component_path="Phase_05.output",
                    message="Phase 5 output missing area scores",
                )
            )
        elif actual_count != expected_count:
            violations.append(
                ContractViolation(
                    type="POLICY_AREA_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_05.output",
                    message="Constitutional invariant: 10 policy area scores required",
                    expected=expected_count,
                    actual=actual_count,
                )
            )

        return violations

    def _validate_phase6_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 6 output (4 cluster scores)."""
        violations = []

        expected_count = 4  # 4 MESO clusters

        if hasattr(output, "cluster_scores"):
            actual_count = len(output.cluster_scores)
        elif isinstance(output, list):
            actual_count = len(output)
        else:
            actual_count = None

        if actual_count is None:
            violations.append(
                ContractViolation(
                    type="MISSING_CLUSTER_SCORES",
                    severity=Severity.CRITICAL,
                    component_path="Phase_06.output",
                    message="Phase 6 output missing cluster scores",
                )
            )
        elif actual_count != expected_count:
            violations.append(
                ContractViolation(
                    type="CLUSTER_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_06.output",
                    message="Constitutional invariant: 4 cluster scores required",
                    expected=expected_count,
                    actual=actual_count,
                )
            )

        return violations

    def _validate_phase7_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 7 output (1 macro score)."""
        violations = []

        # Validate single macro score
        if hasattr(output, "macro_score"):
            score_value = getattr(output.macro_score, "score", output.macro_score)
            if not isinstance(score_value, (int, float)):
                violations.append(
                    ContractViolation(
                        type="INVALID_MACRO_SCORE",
                        severity=Severity.CRITICAL,
                        component_path="Phase_07.output.macro_score",
                        message="Macro score must be numeric",
                        actual=type(score_value).__name__,
                    )
                )

        return violations

    def _validate_phase8_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 8 output (Recommendations)."""
        violations = []

        # Validate recommendations structure
        recommendations = None
        if hasattr(output, "recommendations"):
            recommendations = output.recommendations
        elif isinstance(output, dict):
            recommendations = output

        if recommendations is None:
            violations.append(
                ContractViolation(
                    type="MISSING_RECOMMENDATIONS",
                    severity=Severity.HIGH,
                    component_path="Phase_08.output.recommendations",
                    message="Recommendations output is missing",
                )
            )
        elif not isinstance(recommendations, dict):
            violations.append(
                ContractViolation(
                    type="INVALID_RECOMMENDATIONS",
                    severity=Severity.HIGH,
                    component_path="Phase_08.output.recommendations",
                    message="Recommendations must be a dict keyed by level",
                )
            )

        return violations

    def _validate_phase9_output(
        self, output: Any, context: ExecutionContext
    ) -> list[ContractViolation]:
        """Validate Phase 9 output (Final report)."""
        violations = []

        if hasattr(output, "report"):
            report = output.report
        else:
            report = output

        required_sections = ["micro_analyses", "meso_clusters", "macro_summary"]

        for section in required_sections:
            if not hasattr(report, section) or not getattr(report, section):
                violations.append(
                    ContractViolation(
                        type="INCOMPLETE_REPORT",
                        severity=Severity.HIGH,
                        component_path=f"Phase_09.output.{section}",
                        message=f"Required report section '{section}' is missing or empty",
                    )
                )

        return violations



# =============================================================================
# PIPELINE ORCHESTRATOR
# =============================================================================


class PipelineOrchestrator:
    """
    Production-grade orchestrator for the complete F.A.R.F.A.N pipeline.

    Coordinates all 11 phases with:
    - Bootstrap initialization (Phase 0)
    - Contract validation (input/output)
    - Signal integration
    - Determinism enforcement (SIN_CARRETA)
    - Error handling and recovery
    - Comprehensive telemetry

    Usage:
        orchestrator = PipelineOrchestrator(config)
        result = orchestrator.execute_pipeline(start_phase=PhaseID.PHASE_0)
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        strict_mode: bool = True,
        deterministic: bool = True,
        phase_executors: dict[PhaseID, PhaseExecutor] | None = None,
        phase_inputs: dict[PhaseID, dict[str, Any]] | None = None,
        sisas_phase_map: dict[PhaseID, str] | None = None,
    ):
        """Initialize pipeline orchestrator.

        Args:
            config: Pipeline configuration
            strict_mode: If True, raise exceptions on critical violations
            deterministic: If True, enforce SIN_CARRETA determinism
        """
        self.config = config or {}
        self.strict_mode = strict_mode
        self.deterministic = deterministic
        self.logger = structlog.get_logger(f"{__name__}.PipelineOrchestrator")

        # Explicit phase executor registry
        self._phase_executors: dict[PhaseID, PhaseExecutor] = phase_executors or {}

        # Explicit phase inputs (no implicit fallbacks)
        self._phase_inputs: dict[PhaseID, dict[str, Any]] = phase_inputs or {}

        # SISAS phase mapping
        self._sisas_phase_map = sisas_phase_map or {
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

        # Canonical phase flow
        self._phase_flow = self._build_phase_flow()
        self._phase_spec_map = {spec.phase_id: spec for spec in self._phase_flow}

        if not self._phase_executors and self.config.get("load_default_executors", True):
            self._phase_executors = self._load_default_executors()

        if not self._phase_executors and self.config.get(
            "auto_register_canonical_executors", True
        ):
            from farfan_pipeline.orchestration.canonical_executors import (
                build_canonical_phase_executors,
            )

            self._phase_executors.update(build_canonical_phase_executors())

        # Contract enforcer
        self.enforcer = ContractEnforcer(strict_mode=strict_mode)

        # Execution context (initialized during pipeline run)
        self.context: ExecutionContext | None = None

        self.logger.info(
            "orchestrator_initialized",
            strict_mode=strict_mode,
            deterministic=deterministic,
        )

    def register_phase_executor(self, phase_id: PhaseID, executor: PhaseExecutor) -> None:
        """Register an explicit executor for a phase."""
        self._phase_executors[phase_id] = executor

    def _build_phase_flow(self) -> list[PhaseSpecification]:
        """Build the explicit canonical flow for Phase 0–9."""
        phases_root = Path(__file__).resolve().parents[1] / "phases"
        return [
            PhaseSpecification(
                phase_id=PhaseID.PHASE_0,
                name="Bootstrap & Validation",
                entry_conditions=("bootstrap resources", "initialize SISAS"),
                required_phases=(),
                produces=("wiring", "questionnaire", "sisas"),
                next_phase=PhaseID.PHASE_1,
                phase_root=phases_root / "Phase_00",
                manifest_path=phases_root / "Phase_00" / "PHASE_0_MANIFEST.json",
                inventory_path=None,
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_1,
                name="CPP Ingestion",
                entry_conditions=("phase0 completed", "questionnaire resolved"),
                required_phases=(PhaseID.PHASE_0,),
                produces=("cpp",),
                next_phase=PhaseID.PHASE_2,
                phase_root=phases_root / "Phase_01",
                manifest_path=phases_root / "Phase_01" / "PHASE_1_MANIFEST.json",
                inventory_path=phases_root / "Phase_01" / "INVENTORY.json",
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_2,
                name="Executor Factory & Dispatch",
                entry_conditions=("phase1 cpp",),
                required_phases=(PhaseID.PHASE_1,),
                produces=("executors",),
                next_phase=PhaseID.PHASE_3,
                phase_root=phases_root / "Phase_02",
                manifest_path=phases_root / "Phase_02" / "PHASE_2_MANIFEST.json",
                inventory_path=None,
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_3,
                name="Layer Scoring",
                entry_conditions=("phase2 executors",),
                required_phases=(PhaseID.PHASE_2,),
                produces=("layer_scores",),
                next_phase=PhaseID.PHASE_4,
                phase_root=phases_root / "Phase_03",
                manifest_path=phases_root / "Phase_03" / "PHASE_3_MANIFEST.json",
                inventory_path=None,
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_4,
                name="Dimension Aggregation",
                entry_conditions=("phase3 layer scores",),
                required_phases=(PhaseID.PHASE_3,),
                produces=("dimension_scores",),
                next_phase=PhaseID.PHASE_5,
                phase_root=phases_root / "Phase_04",
                manifest_path=phases_root / "Phase_04" / "PHASE_4_MANIFEST.json",
                inventory_path=None,
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_5,
                name="Policy Area Aggregation",
                entry_conditions=("phase4 dimension scores",),
                required_phases=(PhaseID.PHASE_4,),
                produces=("policy_area_scores",),
                next_phase=PhaseID.PHASE_6,
                phase_root=phases_root / "Phase_05",
                manifest_path=phases_root / "Phase_05" / "PHASE_5_MANIFEST.json",
                inventory_path=None,
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_6,
                name="Cluster Aggregation",
                entry_conditions=("phase5 policy area scores",),
                required_phases=(PhaseID.PHASE_5,),
                produces=("cluster_scores",),
                next_phase=PhaseID.PHASE_7,
                phase_root=phases_root / "Phase_06",
                manifest_path=phases_root / "Phase_06" / "PHASE_6_MANIFEST.json",
                inventory_path=None,
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_7,
                name="Macro Aggregation",
                entry_conditions=("phase6 cluster scores",),
                required_phases=(PhaseID.PHASE_6,),
                produces=("macro_score",),
                next_phase=PhaseID.PHASE_8,
                phase_root=phases_root / "Phase_07",
                manifest_path=phases_root / "Phase_07" / "PHASE_7_MANIFEST.json",
                inventory_path=None,
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_8,
                name="Recommendations Engine",
                entry_conditions=("phase7 macro score",),
                required_phases=(PhaseID.PHASE_7,),
                produces=("recommendations",),
                next_phase=PhaseID.PHASE_9,
                phase_root=phases_root / "Phase_08",
                manifest_path=phases_root / "Phase_08" / "PHASE_8_MANIFEST.json",
                inventory_path=None,
            ),
            PhaseSpecification(
                phase_id=PhaseID.PHASE_9,
                name="Report Assembly",
                entry_conditions=("phase8 recommendations",),
                required_phases=(PhaseID.PHASE_8,),
                produces=("report",),
                next_phase=None,
                phase_root=phases_root / "Phase_09",
                manifest_path=phases_root / "Phase_09" / "PHASE_9_MANIFEST.json",
                inventory_path=None,
            ),
        ]

    def _load_default_executors(self) -> dict[PhaseID, PhaseExecutor]:
        """Load default phase executors without importing analysis into core."""
        from importlib import import_module

        module = import_module("farfan_pipeline.orchestration.phase_executors")
        return module.build_default_phase_executors()

    def execute_pipeline(
        self,
        start_phase: PhaseID = PhaseID.PHASE_0,
        end_phase: PhaseID = PhaseID.PHASE_9,
    ) -> ExecutionContext:
        """
        Execute the complete pipeline from start_phase to end_phase.

        Args:
            start_phase: Phase to start execution (default: Phase 0)
            end_phase: Phase to end execution (default: Phase 10)

        Returns:
            ExecutionContext with results

        Raises:
            ValueError: If contract validation fails in strict mode
        """
        self.logger.info(
            "pipeline_execution_start",
            start_phase=start_phase.value,
            end_phase=end_phase.value,
        )

        # Initialize execution context
        self.context = ExecutionContext(
            config=self.config,
            seed=42 if self.deterministic else None,
            phase_inputs=self._phase_inputs,
        )

        # Determine phases to execute
        phase_order = [spec.phase_id for spec in self._phase_flow]
        if start_phase not in phase_order or end_phase not in phase_order:
            raise ValueError("start_phase/end_phase must be within canonical Phase 0–9")

        start_idx = phase_order.index(start_phase)
        end_idx = phase_order.index(end_phase) + 1
        phases_to_execute = phase_order[start_idx:end_idx]

        # Execute each phase in sequence
        for phase_id in phases_to_execute:
            try:
                self._execute_phase(phase_id)
            except Exception as e:
                self.logger.error(
                    "phase_execution_failed",
                    phase=phase_id.value,
                    error=str(e),
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
        self.logger.info("pipeline_execution_complete", summary=summary)

        return self.context

    def _execute_phase(self, phase_id: PhaseID) -> None:
        """Execute a single phase with contract validation.

        Args:
            phase_id: Phase to execute
        """
        self.logger.info("phase_execution_start", phase=phase_id.value)
        start_time = time.time()

        phase_spec = self._phase_spec_map.get(phase_id)
        if phase_spec is None:
            raise ValueError(f"Phase {phase_id.value} is not in canonical flow")

        self._assert_phase_entry_conditions(phase_spec)

        # Validate input contract
        input_validation = self.enforcer.validate_input_contract(phase_id, self.context)
        if not input_validation.passed:
            self.logger.warning(
                "input_contract_violations",
                phase=phase_id.value,
                violations=len(input_validation.violations),
            )

        executor_input_validation = None
        phase_executor = self._phase_executors.get(phase_id)
        if phase_executor is not None:
            executor_input_validation = phase_executor.validate_input(self.context)
            if not executor_input_validation.passed:
                self.logger.warning(
                    "executor_input_violations",
                    phase=phase_id.value,
                    violations=len(executor_input_validation.violations),
                )

        # Execute phase-specific logic
        try:
            output = self._dispatch_phase_execution(phase_id)
        except Exception as e:
            self.logger.error(
                "phase_execution_error",
                phase=phase_id.value,
                error=str(e),
            )
            raise

        # Validate output contract
        output_validation = self.enforcer.validate_output_contract(
            phase_id, output, self.context
        )
        if not output_validation.passed:
            self.logger.warning(
                "output_contract_violations",
                phase=phase_id.value,
                violations=len(output_validation.violations),
            )

        executor_output_validation = None
        if phase_executor is not None:
            executor_output_validation = phase_executor.validate_output(output, self.context)
            if not executor_output_validation.passed:
                self.logger.warning(
                    "executor_output_violations",
                    phase=phase_id.value,
                    violations=len(executor_output_validation.violations),
                )

        # Record phase result
        execution_time = time.time() - start_time
        all_violations = input_validation.violations + output_validation.violations
        if executor_input_validation is not None:
            all_violations += executor_input_validation.violations
        if executor_output_validation is not None:
            all_violations += executor_output_validation.violations

        result = PhaseResult(
            phase_id=phase_id,
            status=PhaseStatus.COMPLETED,
            output=output,
            execution_time_s=execution_time,
            violations=all_violations,
            metrics={
                "input_validation_ms": input_validation.validation_time_ms,
                "output_validation_ms": output_validation.validation_time_ms,
                "executor_input_validation_ms": (
                    executor_input_validation.validation_time_ms
                    if executor_input_validation is not None
                    else 0.0
                ),
                "executor_output_validation_ms": (
                    executor_output_validation.validation_time_ms
                    if executor_output_validation is not None
                    else 0.0
                ),
            },
        )

        self.context.add_phase_result(result)

        self._record_phase_handoff(phase_spec, output)
        self._run_sisas_cycle(phase_id)

        self.logger.info(
            "phase_execution_complete",
            phase=phase_id.value,
            execution_time_s=round(execution_time, 3),
            violations=len(all_violations),
        )

    def _dispatch_phase_execution(self, phase_id: PhaseID) -> Any:
        """Dispatch to phase-specific execution method.

        Args:
            phase_id: Phase to execute

        Returns:
            Phase output
        """
        if phase_id == PhaseID.PHASE_0:
            return self._execute_phase0()
        elif phase_id == PhaseID.PHASE_1:
            return self._execute_phase1()
        else:
            return self._execute_registered_phase(phase_id)

    # =========================================================================
    # PHASE EXECUTION METHODS
    # =========================================================================

    def _execute_registered_phase(self, phase_id: PhaseID) -> Any:
        """Execute a phase via an explicitly registered executor."""
        executor = self._phase_executors.get(phase_id)
        if executor is None:
            raise MissingPhaseExecutorError(
                f"No executor registered for {phase_id.value}. "
                "Register a PhaseExecutor to execute this phase."
            )

        return executor.execute(self.context)

    def _assert_phase_entry_conditions(self, spec: PhaseSpecification) -> None:
        """Enforce explicit entry conditions and required predecessors."""
        self._validate_phase_coverage(spec)

        missing = [
            phase_id
            for phase_id in spec.required_phases
            if phase_id not in self.context.phase_results
            or self.context.phase_results[phase_id].status != PhaseStatus.COMPLETED
        ]
        if missing:
            raise ValueError(
                f"Phase {spec.phase_id.value} cannot start. "
                f"Missing prerequisites: {[p.value for p in missing]}"
            )

        if spec.phase_id != PhaseID.PHASE_0:
            if self.context.questionnaire is None:
                raise ValueError("Canonical questionnaire missing in ExecutionContext")
            if self.context.sisas is None:
                raise ValueError("SISAS lifecycle missing in ExecutionContext")

    def _validate_phase_coverage(self, spec: PhaseSpecification) -> None:
        """Validate that each phase manifest/inventory matches actual files."""
        expected_files, manifest_nodes, stage_order = self._collect_expected_files(spec)
        actual_files = self._collect_actual_files(spec.phase_root)

        missing = sorted(set(expected_files) - set(actual_files))
        extra = sorted(set(actual_files) - set(expected_files))

        report = PhaseCoverageReport(
            phase_id=spec.phase_id,
            expected_files=tuple(sorted(expected_files)),
            actual_files=tuple(sorted(actual_files)),
            missing_files=tuple(missing),
            extra_files=tuple(extra),
            manifest_nodes=tuple(manifest_nodes),
            stage_order=tuple(stage_order),
        )
        self.context.record_phase_coverage(report)

        violations: list[ContractViolation] = []
        for path in missing:
            violations.append(
                ContractViolation(
                    type="MISSING_PHASE_FILE",
                    severity=Severity.CRITICAL,
                    component_path=f"{spec.phase_id.value}.manifest",
                    message=f"Expected phase file missing: {path}",
                    remediation="Sync manifest/inventory with actual phase files",
                )
            )
        for path in extra:
            violations.append(
                ContractViolation(
                    type="UNDECLARED_PHASE_FILE",
                    severity=Severity.HIGH,
                    component_path=f"{spec.phase_id.value}.manifest",
                    message=f"Phase file not declared in manifest/inventory: {path}",
                    remediation="Declare file in manifest/inventory or remove it",
                )
            )

        if violations:
            self.context.total_violations.extend(violations)
            if self.strict_mode:
                raise ValueError(
                    f"Phase {spec.phase_id.value} coverage validation failed: "
                    f"{len(violations)} violation(s)"
                )

    def _collect_expected_files(
        self, spec: PhaseSpecification
    ) -> tuple[list[str], list[str], list[int]]:
        expected_files: list[str] = []
        manifest_nodes: list[str] = []
        stage_order: list[int] = []

        if spec.manifest_path and spec.manifest_path.exists():
            manifest = json.loads(spec.manifest_path.read_text())

            if "stages" in manifest:
                for stage in manifest.get("stages", []):
                    stage_order.append(int(stage.get("execution_order", stage.get("code", 0))))
                    modules = stage.get("modules", [])
                    for module in modules:
                        location = module.get("location") or module.get("file")
                        canonical = module.get("canonical_name")
                        if location:
                            expected_files.append(str(Path(location)))
                        elif canonical:
                            expected_files.append(f"{canonical}.py")
                        if canonical:
                            manifest_nodes.append(canonical)

            if "modules" in manifest:
                modules = manifest.get("modules", {})
                for stage_modules in modules.values():
                    for module in stage_modules:
                        file_name = module.get("file")
                        canonical = module.get("canonical_name")
                        if file_name:
                            expected_files.append(file_name)
                        elif canonical:
                            expected_files.append(f"{canonical}.py")
                        if canonical:
                            manifest_nodes.append(canonical)

            if "subphases" in manifest:
                for subphase in manifest.get("subphases", []):
                    module = subphase.get("module")
                    if module:
                        expected_files.append(f"{module}.py")
                        manifest_nodes.append(module)

            if "directory_structure" in manifest:
                structure = manifest.get("directory_structure", {})
                root_modules = structure.get("root_modules", [])
                expected_files.extend(root_modules)
                for folder, detail in structure.get("subfolders", {}).items():
                    for module in detail.get("modules", []):
                        expected_files.append(str(Path(folder) / module))
                    for file_name in detail.get("files", []):
                        expected_files.append(str(Path(folder) / file_name))

            if "documentation" in manifest:
                documentation = manifest.get("documentation", {})
                for doc in documentation.values():
                    if isinstance(doc, str):
                        expected_files.append(doc)
                    elif isinstance(doc, dict):
                        for subdoc in doc.values():
                            if isinstance(subdoc, str):
                                expected_files.append(subdoc)

        if spec.inventory_path and spec.inventory_path.exists():
            inventory = json.loads(spec.inventory_path.read_text())
            for module in inventory.get("python_modules", []):
                filename = module.get("filename")
                canonical = module.get("canonical_name")
                if filename:
                    expected_files.append(filename)
                if canonical:
                    manifest_nodes.append(canonical)
            for meta in inventory.get("metadata_files", []):
                filename = meta.get("filename")
                if filename:
                    expected_files.append(filename)

        if not expected_files:
            expected_files = self._collect_actual_files(spec.phase_root)

        normalized = [str(Path(path)) for path in expected_files]
        return normalized, manifest_nodes, stage_order

    def _collect_actual_files(self, phase_root: Path) -> list[str]:
        if not phase_root.exists():
            return []
        files = []
        for path in phase_root.rglob("*"):
            if path.is_dir():
                continue
            if "__pycache__" in path.parts:
                continue
            relative = path.relative_to(phase_root)
            files.append(str(relative))
        return files

    def _record_phase_handoff(self, spec: PhaseSpecification, output: Any) -> None:
        """Record a traceable handoff between phases."""
        previous_phase = spec.required_phases[-1] if spec.required_phases else None

        handoff = PhaseHandoff(
            from_phase=previous_phase,
            to_phase=spec.phase_id,
            input_keys=tuple(spec.entry_conditions),
            output_keys=tuple(spec.produces),
        )
        self.context.record_handoff(handoff)

    def _run_sisas_cycle(self, phase_id: PhaseID) -> None:
        """Execute SISAS signal generation/propagation/irrigation for a phase."""
        if self.context.sisas is None:
            return

        if not self.config.get("enable_sisas", True):
            return

        sisas_phase = self._sisas_phase_map.get(phase_id)
        if sisas_phase is None:
            return

        base_path = self.config.get("sisas_base_path", "")
        try:
            results = self.context.sisas.execute_irrigation_phase(sisas_phase, base_path)
            summary = self.context.sisas.irrigation_executor.get_execution_summary()
            self.context.signal_metrics[phase_id.value] = {
                "irrigation_phase": sisas_phase,
                "routes_executed": len(results),
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

    def _require_phase_input(self, phase_id: PhaseID, key: str) -> Any:
        """Require an explicit phase input key (fail-fast)."""
        if phase_id not in self.context.phase_inputs:
            raise ValueError(
                f"Phase inputs missing for {phase_id.value}. "
                "Provide explicit inputs; no implicit fallbacks are allowed."
            )
        inputs = self.context.phase_inputs[phase_id]
        if key not in inputs:
            raise ValueError(
                f"Required input '{key}' missing for {phase_id.value}."
            )
        return inputs[key]

    def _assert_questionnaire_granularity(self, questionnaire: QuestionnairePort) -> None:
        """Validate questionnaire coverage across micro/meso/macro levels."""
        data = questionnaire.data
        blocks = data.get("blocks", {}) if isinstance(data, dict) else {}
        micro_questions = blocks.get("micro_questions", [])
        meso_questions = blocks.get("meso_questions", [])
        macro_question = blocks.get("macro_question", {})

        if len(micro_questions) != 300:
            raise ValueError(
                "Canonical questionnaire must contain 300 micro_questions; "
                f"got {len(micro_questions)}"
            )
        if not meso_questions:
            raise ValueError("Canonical questionnaire missing meso_questions")
        if not macro_question:
            raise ValueError("Canonical questionnaire missing macro_question")

    def _execute_phase0(self) -> Phase0Output:
        """
        Execute Phase 0: Bootstrap & Validation.

        Returns:
            WiringComponents with all initialized modules
        """
        self.logger.info("executing_phase0_bootstrap")

        # Extract bootstrap configuration
        questionnaire_path = self.config.get("questionnaire_path")
        questionnaire_hash = self.config.get("questionnaire_hash", "")
        executor_config_path = self.config.get("executor_config_path")
        calibration_profile = self.config.get("calibration_profile", "default")
        abort_on_insufficient = self.config.get("abort_on_insufficient", True)
        resource_limits = self.config.get("resource_limits", {})

        # Create feature flags
        flags = WiringFeatureFlags(
            enable_http_signals=self.config.get("enable_http_signals", False),
            enable_calibration=self.config.get("enable_calibration", False),
            strict_validation=self.strict_mode,
            deterministic_mode=self.deterministic,
        )

        # Create bootstrap
        bootstrap = WiringBootstrap(
            questionnaire_path=questionnaire_path,
            questionnaire_hash=questionnaire_hash,
            executor_config_path=executor_config_path,
            calibration_profile=calibration_profile,
            abort_on_insufficient=abort_on_insufficient,
            resource_limits=resource_limits,
            flags=flags,
        )

        # Execute bootstrap
        wiring = bootstrap.bootstrap()

        # Resolve canonical questionnaire via authoritative public interface
        questionnaire = resolve_questionnaire(
            expected_hash=questionnaire_hash or None,
            force_rebuild=self.config.get("force_questionnaire_rebuild", False),
        )
        self._assert_questionnaire_granularity(questionnaire)

        # Initialize SISAS lifecycle (authoritative infra)
        sisas = SisasLifecycle.initialize(strict_mode=self.strict_mode)

        irrigation_csv = self.config.get("sisas_irrigation_csv_path")
        if irrigation_csv:
            sisas.load_irrigation_map_from_csv(Path(irrigation_csv))

        # Store in context
        self.context.wiring = wiring
        self.context.questionnaire = questionnaire
        self.context.sisas = sisas

        registry_types = tuple(SignalRegistry.get_all_types())

        self.logger.info(
            "phase0_complete",
            components=len(wiring.init_hashes),
            questionnaire_hash=questionnaire.sha256[:16],
            sisas_vehicles=len(sisas.vehicles),
        )

        return Phase0Output(
            wiring=wiring,
            questionnaire=questionnaire,
            sisas=sisas,
            signal_registry_types=registry_types,
        )

    def _execute_phase1(self) -> Any:
        """
        Execute Phase 1: CPP Ingestion.

        Returns:
            CanonPolicyPackage with 300 question-level chunks
        """
        self.logger.info("executing_phase1_cpp_ingestion")

        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
        )

        canonical_input = self._require_phase_input(PhaseID.PHASE_1, "canonical_input")
        signal_registry = self._require_phase_input(PhaseID.PHASE_1, "signal_registry")
        structural_profile = self.context.phase_inputs.get(PhaseID.PHASE_1, {}).get(
            "structural_profile"
        )

        cpp = execute_phase_1_with_full_contract(
            canonical_input=canonical_input,
            signal_registry=signal_registry,
            structural_profile=structural_profile,
        )

        chunk_count = (
            len(cpp.chunk_graph.chunks)
            if hasattr(cpp, "chunk_graph")
            else len(getattr(cpp, "chunks", []))
        )
        self.logger.info("phase1_complete", chunk_count=chunk_count)

        return cpp



# =============================================================================
# EXPORTS
# =============================================================================

# =============================================================================
# PHASE 0 VALIDATION TYPES
# =============================================================================


@dataclass(frozen=True)
class GateResult:
    """Result of a Phase 0 exit gate check.

    Attributes:
        gate_name: Name of the gate (e.g., "bootstrap", "input_verification")
        passed: Whether the gate check passed
        message: Optional message describing the result
        check_time: ISO timestamp of when the gate was checked
        details: Optional dictionary with additional details
    """

    gate_name: str
    passed: bool
    message: str = ""
    check_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "gate_name": self.gate_name,
            "passed": self.passed,
            "message": self.message,
            "check_time": self.check_time,
            "details": self.details,
        }


@dataclass
class Phase0ValidationResult:
    """Result of Phase 0 boot checks and exit gate validation.

    Attributes:
        all_passed: Whether all gates passed
        gate_results: List of GateResult objects for each gate
        validation_time: ISO timestamp of when validation was performed
        total_gates: Total number of gates checked
        passed_gates: Number of gates that passed
        failed_gates: Number of gates that failed
    """

    all_passed: bool
    gate_results: list[GateResult]
    validation_time: str
    total_gates: int = field(init=False)
    passed_gates: int = field(init=False)
    failed_gates: int = field(init=False)

    def __post_init__(self) -> None:
        """Compute summary statistics."""
        self.total_gates = len(self.gate_results)
        self.passed_gates = sum(1 for g in self.gate_results if g.passed)
        self.failed_gates = self.total_gates - self.passed_gates

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "all_passed": self.all_passed,
            "validation_time": self.validation_time,
            "total_gates": self.total_gates,
            "passed_gates": self.passed_gates,
            "failed_gates": self.failed_gates,
            "gate_results": [g.to_dict() for g in self.gate_results],
        }

    def get_failed_gates(self) -> list[GateResult]:
        """Get list of failed gate results."""
        return [g for g in self.gate_results if not g.passed]

    def get_gate_result(self, gate_name: str) -> GateResult | None:
        """Get result for a specific gate by name."""
        for g in self.gate_results:
            if g.gate_name == gate_name:
                return g
        return None


# =============================================================================
# METHOD EXECUTOR
# =============================================================================


class MethodExecutor:
    """Executes methods from the method registry with argument routing.

    This class bridges the factory's method registry with the executor classes,
    providing method execution with argument routing and signal registry integration.

    Usage:
        method_executor = MethodExecutor(
            method_registry=registry,
            arg_router=router,
            signal_registry=signal_registry,
        )
        result = method_executor.execute(
            class_name="PDETMunicipalPlanAnalyzer",
            method_name="_score_indicators",
            document=doc,
            signal_pack=pack,
            **context
        )
    """

    def __init__(
        self,
        method_registry: Any,  # MethodRegistry from phase2_10_02_methods_registry
        arg_router: Any,  # ExtendedArgRouter from phase2_60_02_arg_router
        signal_registry: Any,  # QuestionnaireSignalRegistry
    ):
        """Initialize the method executor.

        Args:
            method_registry: MethodRegistry for retrieving methods
            arg_router: ExtendedArgRouter for argument routing
            signal_registry: Signal registry for signal integration
        """
        self._method_registry = method_registry
        self._arg_router = arg_router
        self._signal_registry = signal_registry
        self.logger = structlog.get_logger(f"{__name__}.MethodExecutor")

    def execute(
        self,
        class_name: str,
        method_name: str,
        **kwargs: Any,
    ) -> Any:
        """Execute a method from the registry with argument routing.

        Args:
            class_name: Name of the class containing the method
            method_name: Name of the method to execute
            **kwargs: Arguments to pass to the method (routed via arg_router)

        Returns:
            Result of the method execution

        Raises:
            MethodRegistryError: If method cannot be retrieved
            RuntimeError: If method execution fails
        """
        self.logger.debug(
            "method_execution_start",
            class_name=class_name,
            method_name=method_name,
        )

        # Get method from registry
        method = self._method_registry.get_method(class_name, method_name)

        # Route arguments using arg_router
        # ExtendedArgRouter.route() returns (args_tuple, kwargs_dict)
        payload = dict(kwargs)  # Make mutable copy for routing
        routed_args, routed_kwargs = self._arg_router.route(
            class_name=class_name,
            method_name=method_name,
            payload=payload,
        )

        # Execute method with routed args
        try:
            result = method(*routed_args, **routed_kwargs)
            self.logger.debug(
                "method_execution_complete",
                class_name=class_name,
                method_name=method_name,
            )
            return result
        except Exception as e:
            self.logger.error(
                "method_execution_failed",
                class_name=class_name,
                method_name=method_name,
                error=str(e),
            )
            raise RuntimeError(
                f"Method execution failed for {class_name}.{method_name}: {e}"
            ) from e

    @property
    def method_registry(self) -> Any:
        """Get the method registry."""
        return self._method_registry

    @property
    def arg_router(self) -> Any:
        """Get the argument router."""
        return self._arg_router

    @property
    def signal_registry(self) -> Any:
        """Get the signal registry."""
        return self._signal_registry


# =============================================================================
# FACTORY-ALIGNED ORCHESTRATOR
# =============================================================================


class Orchestrator:
    """Factory-aligned orchestrator for Phase 2 method dispatch.

    This orchestrator bridges the factory's DI pattern with the PipelineOrchestrator,
    providing the interface expected by AnalysisPipelineFactory.

    The canonical flow:
        PHASE_0: Bootstrap & Validation (WiringComponents)
        PHASE_1: CPP Ingestion (CanonPolicyPackage with 300 questions)
        PHASE_2: Executor Factory & Dispatch (~30 executors)
        PHASE_3: Layer Scoring (8 layers × 300 questions)
        PHASE_4: Dimension Aggregation (60 dimensions)
        PHASE_5: Policy Area Aggregation (10 policy areas)
        PHASE_6: Cluster Aggregation (4 MESO clusters)
        PHASE_7: Macro Aggregation (1 holistic score)
        PHASE_8: Recommendations Engine
        PHASE_9: Report Assembly

    Usage:
        orchestrator = Orchestrator(
            method_executor=method_executor,
            questionnaire=questionnaire,
            executor_config=executor_config,
            runtime_config=runtime_config,
            phase0_validation=phase0_validation,
        )
    """

    def __init__(
        self,
        method_executor: MethodExecutor,
        questionnaire: Any,  # CanonicalQuestionnaire
        executor_config: Any,  # ExecutorConfig
        runtime_config: Any | None = None,  # RuntimeConfig
        phase0_validation: Phase0ValidationResult | None = None,
    ):
        """Initialize the orchestrator with dependency injection.

        Args:
            method_executor: MethodExecutor for method dispatch
            questionnaire: CanonicalQuestionnaire with 300 questions
            executor_config: ExecutorConfig for operational parameters
            runtime_config: Optional RuntimeConfig for phase control
            phase0_validation: Optional Phase0ValidationResult from Phase 0
        """
        self._method_executor = method_executor
        self._questionnaire = questionnaire
        self._executor_config = executor_config
        self._runtime_config = runtime_config
        self._phase0_validation = phase0_validation
        self.logger = structlog.get_logger(f"{__name__}.Orchestrator")

        # Internal state
        self._phase_outputs: dict[str, Any] = {}
        self._execution_context: dict[str, Any] = {}

        self.logger.info(
            "orchestrator_initialized",
            questionnaire_hash=getattr(questionnaire, "sha256", "unknown")[:16] if questionnaire else "none",
            phase0_passed=phase0_validation.all_passed if phase0_validation else None,
        )

    @property
    def method_executor(self) -> MethodExecutor:
        """Get the method executor."""
        return self._method_executor

    @property
    def questionnaire(self) -> Any:
        """Get the canonical questionnaire."""
        return self._questionnaire

    @property
    def executor_config(self) -> Any:
        """Get the executor configuration."""
        return self._executor_config

    @property
    def runtime_config(self) -> Any | None:
        """Get the runtime configuration."""
        return self._runtime_config

    @property
    def phase0_validation(self) -> Phase0ValidationResult | None:
        """Get the Phase 0 validation result."""
        return self._phase0_validation

    def execute_phase(
        self,
        phase_id: str,
        **kwargs: Any,
    ) -> Any:
        """Execute a pipeline phase.

        Args:
            phase_id: Phase identifier (e.g., "P01", "P02")
            **kwargs: Additional arguments for the phase

        Returns:
            Phase output

        Raises:
            ValueError: If phase is invalid
            RuntimeError: If phase execution fails
        """
        self.logger.info("phase_execution_start", phase=phase_id)

        # Phase-specific execution
        if phase_id == "P01":
            return self._execute_phase1(**kwargs)
        elif phase_id == "P02":
            return self._execute_phase2(**kwargs)
        elif phase_id == "P03":
            return self._execute_phase3(**kwargs)
        else:
            # Delegate to PipelineOrchestrator for other phases
            return self._execute_via_pipeline_orchestrator(phase_id, **kwargs)

    def _execute_phase1(self, **kwargs: Any) -> Any:
        """Execute Phase 1: CPP Ingestion."""
        self.logger.info("executing_phase1_cpp_ingestion")
        # TODO: Implement Phase 1 execution
        # This is a placeholder - actual implementation will integrate
        # with the Phase 1 module for CPP processing
        return {"status": "P01_placeholder", "chunks": 300}

    def _execute_phase2(self, **kwargs: Any) -> Any:
        """Execute Phase 2: Executor Factory & Dispatch."""
        self.logger.info("executing_phase2_executor_factory")
        # Phase 2 is handled by the factory itself
        # This method returns the method_executor for reference
        return self._method_executor

    def _execute_phase3(self, **kwargs: Any) -> Any:
        """Execute Phase 3: Layer Scoring."""
        self.logger.info("executing_phase3_layer_scoring")
        # TODO: Implement Phase 3 execution
        return {"status": "P03_placeholder", "layer_scores": []}

    def _execute_via_pipeline_orchestrator(
        self, phase_id: str, **kwargs: Any
    ) -> Any:
        """Execute phase via PipelineOrchestrator for phases P04-P09."""
        # Lazy initialization of PipelineOrchestrator
        if not hasattr(self, "_pipeline_orchestrator"):
            self._pipeline_orchestrator = PipelineOrchestrator(
                config={
                    "executor_config": self._executor_config,
                    "runtime_config": self._runtime_config,
                    "phase0_validation": self._phase0_validation,
                }
            )
            # Initialize context with questionnaire
            self._pipeline_orchestrator.context = ExecutionContext(
                config=self._pipeline_orchestrator.config,
            )
            # Store phase outputs
            for phase, output in self._phase_outputs.items():
                self._pipeline_orchestrator.context.phase_outputs[phase] = output

        # Map phase_id to PhaseID enum
        phase_map = {
            "P04": PhaseID.PHASE_4,
            "P05": PhaseID.PHASE_5,
            "P06": PhaseID.PHASE_6,
            "P07": PhaseID.PHASE_7,
            "P08": PhaseID.PHASE_8,
            "P09": PhaseID.PHASE_9,
        }

        if phase_id not in phase_map:
            raise ValueError(f"Unknown phase: {phase_id}")

        # Execute the phase
        self._pipeline_orchestrator._execute_phase(phase_map[phase_id])

        # Store output
        output = self._pipeline_orchestrator.context.get_phase_output(
            phase_map[phase_id]
        )
        self._phase_outputs[phase_id] = output

        return output


__all__ = [
    # Core orchestrator
    "PipelineOrchestrator",
    "ExecutionContext",
    "PhaseResult",
    "PhaseStatus",
    "PhaseID",
    "ContractEnforcer",
    "PHASE_METADATA",
    "PhaseSpecification",
    "PhaseHandoff",
    "Phase0Output",
    "SisasLifecycle",
    "MissingPhaseExecutorError",
    # Phase 0 validation
    "GateResult",
    "Phase0ValidationResult",
    # Method execution
    "MethodExecutor",
    # Factory-aligned orchestrator
    "Orchestrator",
]
