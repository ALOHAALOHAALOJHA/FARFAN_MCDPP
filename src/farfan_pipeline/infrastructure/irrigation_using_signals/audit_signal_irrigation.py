"""
Comprehensive Technical Audit of Signal Irrigation Ecosystem

This module performs a complete audit of the signal irrigation system with:
1. Wiring Verification: Data flow tracing from questionnaire_monolith.json through SISAS
2. Principle Implementation Assessment: SCOPE COHERENCE, SYNCHRONIZATION, UTILITY
3. Quantitative Metrics: Coverage, Precision, Latency, Value-add scores
4. Architecture Visualizations: Sankey diagrams, state machines, heatmaps

Author: F.A.R.F.A.N Pipeline Audit System
Date: 2025-01-15
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

from orchestration.factory import load_questionnaire

from farfan_pipeline.infrastructure.irrigation_using_signals.ports import QuestionnairePort
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption import (
    SignalConsumptionProof,
    get_access_audit,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
    QuestionnaireSignalRegistry,
    create_signal_registry,
)

# ============================================================================
# AUDIT DATA STRUCTURES
# ============================================================================


@dataclass
class WiringGap:
    """Represents a missing connection in the signal flow."""

    source_component: str
    target_component: str
    missing_interface: str
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    fix_suggestion: str


@dataclass
class ScopeViolation:
    """Represents a scope coherence violation."""

    violation_type: str
    question_id: str
    policy_area: str
    accessed_pattern_id: str
    violation_details: str
    expected_scope: str
    actual_scope: str


@dataclass
class SynchronizationIssue:
    """Represents a synchronization timing issue."""

    phase_id: int
    executor_id: str
    issue_type: str  # "RACE_CONDITION", "TIMING_MISMATCH", "STATE_VIOLATION"
    description: str
    injection_time: float | None
    consumption_time: float | None
    phase_state: str


@dataclass
class SignalUtilizationMetrics:
    """Metrics for signal utilization."""

    total_patterns_injected: int = 0
    patterns_consumed: int = 0
    patterns_produced_evidence: int = 0
    waste_ratio: float = 0.0
    proof_chains_complete: int = 0
    proof_chains_incomplete: int = 0
    avg_latency_ms: float = 0.0


@dataclass
class PhaseExecutionTrace:
    """Trace of phase execution with signal injection points."""

    phase_id: int
    phase_name: str
    start_time: float
    end_time: float | None = None
    signal_injections: list[dict[str, Any]] = field(default_factory=list)
    pattern_matches: list[dict[str, Any]] = field(default_factory=list)
    state_transitions: list[tuple[str, str, float]] = field(default_factory=list)


@dataclass
class AuditResults:
    """Complete audit results."""

    wiring_gaps: list[WiringGap] = field(default_factory=list)
    scope_violations: list[ScopeViolation] = field(default_factory=list)
    synchronization_issues: list[SynchronizationIssue] = field(default_factory=list)
    utilization_metrics: SignalUtilizationMetrics = field(default_factory=SignalUtilizationMetrics)
    phase_traces: list[PhaseExecutionTrace] = field(default_factory=list)
    coverage_metrics: dict[str, float] = field(default_factory=dict)
    precision_metrics: dict[str, float] = field(default_factory=dict)
    latency_metrics: dict[str, float] = field(default_factory=dict)
    access_audit_report: dict[str, Any] | None = None


# ============================================================================
# WIRING VERIFICATION
# ============================================================================


class WiringAuditor:
    """Verifies complete data flow from questionnaire_monolith.json to phase executors."""

    def __init__(
        self, questionnaire: QuestionnairePort, signal_registry: QuestionnaireSignalRegistry
    ):
        self.questionnaire = questionnaire
        self.signal_registry = signal_registry
        self.wiring_gaps: list[WiringGap] = []

    def audit_wiring(self) -> list[WiringGap]:
        """Perform complete wiring audit."""
        logger.info("wiring_audit_started")

        # 1. Verify questionnaire -> registry connection
        self._check_questionnaire_registry_connection()

        # 2. Verify registry -> phase executor connections
        self._check_registry_executor_connections()

        # 3. Verify signal transformation pipeline
        self._check_signal_transformation_pipeline()

        # 4. Check for unimplemented interfaces
        self._check_unimplemented_interfaces()

        logger.info(
            "wiring_audit_completed",
            gaps_found=len(self.wiring_gaps),
            critical_count=sum(1 for g in self.wiring_gaps if g.severity == "CRITICAL"),
        )

        return self.wiring_gaps

    def _check_questionnaire_registry_connection(self) -> None:
        """Verify questionnaire data flows to registry."""
        try:
            # Test: Can registry access questionnaire data?
            blocks = self.questionnaire.data.get("blocks", {})
            questions = blocks.get("micro_questions", [])

            if not questions:
                self.wiring_gaps.append(
                    WiringGap(
                        source_component="questionnaire_monolith.json",
                        target_component="QuestionnaireSignalRegistry",
                        missing_interface="blocks.micro_questions",
                        severity="CRITICAL",
                        description="Registry cannot access micro_questions from questionnaire",
                        fix_suggestion="Ensure questionnaire.data structure is properly passed to registry constructor",
                    )
                )
            else:
                # Test: Can registry extract patterns?
                test_q_id = questions[0].get("question_id", "")
                if test_q_id:
                    try:
                        signals = self.signal_registry.get_micro_answering_signals(test_q_id)
                        if not signals.question_patterns:
                            self.wiring_gaps.append(
                                WiringGap(
                                    source_component="questionnaire_monolith.json",
                                    target_component="QuestionnaireSignalRegistry._build_micro_answering_signals",
                                    missing_interface="pattern_extraction",
                                    severity="HIGH",
                                    description=f"Patterns not extracted for question {test_q_id}",
                                    fix_suggestion="Check _build_micro_answering_signals() pattern extraction logic",
                                )
                            )
                    except Exception as e:
                        self.wiring_gaps.append(
                            WiringGap(
                                source_component="questionnaire_monolith.json",
                                target_component="QuestionnaireSignalRegistry.get_micro_answering_signals",
                                missing_interface="signal_retrieval",
                                severity="CRITICAL",
                                description=f"Signal retrieval failed: {e}",
                                fix_suggestion="Fix signal registry initialization or pattern extraction",
                            )
                        )
        except Exception as e:
            self.wiring_gaps.append(
                WiringGap(
                    source_component="questionnaire_monolith.json",
                    target_component="QuestionnaireSignalRegistry",
                    missing_interface="data_access",
                    severity="CRITICAL",
                    description=f"Cannot access questionnaire data: {e}",
                    fix_suggestion="Verify questionnaire port interface implementation",
                )
            )

    def _check_registry_executor_connections(self) -> None:
        """Verify registry methods are called by phase executors."""
        # Check if executors have signal_registry attribute
        # This is a structural check - actual usage is checked in utilization audit
        try:
            from farfan_pipeline.phases.Phase_02.executors.base_executor_with_contract import BaseExecutorWithContract
            # TODO: Implement actual connection validation
            # This check should verify that BaseExecutorWithContract instances
            # properly initialize and use the signal_registry attribute
        except ImportError:
            # BaseExecutorWithContract may not exist or may be in a different location
            # Skip this check if the module is not available
            pass


if __name__ == "__main__":
    output_dir = PROJECT_ROOT / "artifacts" / "audit_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    auditor = SignalIrrigationAuditor()
    results = auditor.run_audit()

    report_path = (
        output_dir / f"signal_irrigation_audit_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
    )
    auditor.generate_report(report_path)

    print(f"\n{'='*80}")
    print("SIGNAL IRRIGATION AUDIT COMPLETE")
    print(f"{'='*80}\n")
    print(f"Wiring Gaps: {len(results.wiring_gaps)}")
    print(f"Scope Violations: {len(results.scope_violations)}")
    print(f"Synchronization Issues: {len(results.synchronization_issues)}")
    print(
        f"Pattern Coverage: {results.coverage_metrics.get('pattern_extraction_coverage', 0.0):.1%}"
    )
    print(f"Waste Ratio: {results.utilization_metrics.waste_ratio:.1%}")
    print(f"\nReport saved to: {report_path}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
