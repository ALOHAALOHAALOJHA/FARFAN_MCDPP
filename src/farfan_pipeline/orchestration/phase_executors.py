"""Canonical phase executors for P02–P09.

Implements explicit, phase-by-phase execution using canonical module entrypoints
and strict interface contracts. No legacy fallbacks or implicit shortcuts.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast, override

from canonic_questionnaire_central import QuestionnairePort

from farfan_pipeline.orchestration.core_orchestrator import (
    ExecutionContext,
    PhaseExecutor,
    PhaseID,
)
from farfan_pipeline.phases.Phase_0.interphase.wiring_types import (
    ContractViolation,
    Severity,
    ValidationResult,
)

from farfan_pipeline.phases.Phase_1.interphase.phase1_08_00_adapter import (
    adapt_cpp_to_orchestrator,
)
from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import (
    ExecutionPlan,
    IrrigationSynchronizer,
)
from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import (
    TaskExecutor,
    TaskResult,
    execute_tasks_dry_run,
    execute_tasks_parallel,
)
from farfan_pipeline.phases.Phase_2.registries import QuestionnaireSignalRegistry
from farfan_pipeline.phases.Phase_3.interphase.phase3_10_00_phase3_exit_contract import (
    ScoredMicroQuestion,
)
from farfan_pipeline.phases.Phase_3.phase3_10_00_phase3_score_extraction import (
    extract_score_from_nexus,
    map_completeness_to_quality,
)
from farfan_pipeline.phases.Phase_3.phase3_10_00_phase3_signal_enriched_scoring import (
    SignalEnrichedScorer,
)
from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
    DimensionAggregator,
    DimensionScore,
    ScoredResult,
)
from farfan_pipeline.phases.Phase_5.phase5_10_00_area_integration import (
    run_phase5_aggregation,
)
from farfan_pipeline.phases.Phase_6.phase6_30_00_cluster_aggregator import (
    ClusterAggregator,
)
from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import (
    MacroAggregator,
)
from farfan_pipeline.phases.Phase_8.phase8_20_01_recommendation_engine_adapter import (
    RecommendationEngineAdapter,
)
from farfan_pipeline.phases.Phase_8.primitives.phase8_00_00_phase_8_constants import (
    RULES_PATH_ENHANCED,
    SCHEMA_PATH,
)
from farfan_pipeline.phases.Phase_9.phase9_10_00_report_assembly import (
    create_report_assembler,
)


def _validation_ok(violations: list[ContractViolation]) -> ValidationResult:
    return ValidationResult(
        passed=not any(v.severity == Severity.CRITICAL for v in violations),
        violations=violations,
        validation_time_ms=0.0,
    )


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    if hasattr(value, "to_dict"):
        return cast(dict[str, Any], value.to_dict())
    if hasattr(value, "__dict__"):
        return cast(dict[str, Any], dict(value.__dict__))
    return {"value": value}


@dataclass
class Phase2Executor(PhaseExecutor):
    """Phase 2 executor: synchronizer + task execution."""

    @override
    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        cpp = context.get_phase_output(PhaseID.PHASE_1)
        if cpp is None:
            violations.append(
                ContractViolation(
                    type="MISSING_CPP",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.input.cpp",
                    message="CanonPolicyPackage from Phase 1 is required",
                )
            )
        if context.questionnaire is None:
            violations.append(
                ContractViolation(
                    type="MISSING_QUESTIONNAIRE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.input.questionnaire",
                    message="Canonical questionnaire is required",
                )
            )
        return _validation_ok(violations)

    @override
    def execute(self, context: ExecutionContext) -> dict[str, Any]:
        cpp = context.get_phase_output(PhaseID.PHASE_1)
        if cpp is None:
            raise ValueError("Phase 1 output missing for Phase 2")

        questionnaire = context.questionnaire
        if questionnaire is None:
            raise ValueError("Canonical questionnaire missing for Phase 2")

        document_id = getattr(cpp, "document_id", "document")
        preprocessed_document = adapt_cpp_to_orchestrator(cpp, document_id)

        phase_inputs = context.phase_inputs.get(PhaseID.PHASE_2, {})
        signal_registry = cast(
            Any, phase_inputs.get("signal_registry") or QuestionnaireSignalRegistry()
        )
        executor_contracts = phase_inputs.get("executor_contracts")
        enable_join_table = bool(phase_inputs.get("enable_join_table", False))

        synchronizer = IrrigationSynchronizer(
            questionnaire=_questionnaire_data(questionnaire),
            preprocessed_document=preprocessed_document,
            signal_registry=signal_registry,
            contracts=executor_contracts,
            enable_join_table=enable_join_table,
        )
        execution_plan: ExecutionPlan = synchronizer.build_execution_plan()

        calibration_orchestrator = phase_inputs.get("calibration_orchestrator")
        validation_orchestrator = phase_inputs.get("validation_orchestrator")

        task_executor = TaskExecutor(
            questionnaire_monolith=_questionnaire_data(questionnaire),
            preprocessed_document=preprocessed_document,
            signal_registry=signal_registry,
            calibration_orchestrator=calibration_orchestrator,
            validation_orchestrator=validation_orchestrator,
        )

        execution_mode = phase_inputs.get("execution_mode", "serial")
        if execution_mode == "parallel":
            task_results = execute_tasks_parallel(
                execution_plan=execution_plan,
                questionnaire_monolith=_questionnaire_data(questionnaire),
                preprocessed_document=preprocessed_document,
                signal_registry=signal_registry,
                calibration_orchestrator=calibration_orchestrator,
                validation_orchestrator=validation_orchestrator,
                max_workers=phase_inputs.get("max_workers"),
                checkpoint_dir=phase_inputs.get("checkpoint_dir"),
                checkpoint_batch_size=phase_inputs.get("checkpoint_batch_size", 10),
            )
        elif execution_mode == "dry_run":
            task_results = execute_tasks_dry_run(
                execution_plan=execution_plan,
                questionnaire_monolith=_questionnaire_data(questionnaire),
                preprocessed_document=preprocessed_document,
                signal_registry=signal_registry,
            )
        else:
            task_results = task_executor.execute_plan(execution_plan)

        return {
            "preprocessed_document": preprocessed_document,
            "execution_plan": execution_plan,
            "task_results": task_results,
            "signal_registry": signal_registry,
        }

    @override
    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, dict):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.output",
                    message="Phase 2 output must be a dict",
                )
            )
            return _validation_ok(violations)

        output_dict = cast(dict[str, Any], output)
        task_results = output_dict.get("task_results")
        task_results_list = cast(list[Any], task_results) if isinstance(task_results, list) else None
        if task_results_list is None or len(task_results_list) != 300:
            violations.append(
                ContractViolation(
                    type="TASK_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.output.task_results",
                    message="Phase 2 must return 300 task results",
                    expected=300,
                    actual=len(task_results_list) if task_results_list is not None else None,
                )
            )
        return _validation_ok(violations)


@dataclass
class Phase3Executor(PhaseExecutor):
    """Phase 3 executor: scoring micro-questions."""

    @override
    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        phase2_output = context.get_phase_output(PhaseID.PHASE_2)
        if not isinstance(phase2_output, dict):
            violations.append(
                ContractViolation(
                    type="MISSING_TASK_RESULTS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.input.task_results",
                    message="Task results from Phase 2 are required",
                )
            )
            return _validation_ok(violations)
        phase2_output = cast(dict[str, Any], phase2_output)
        if not phase2_output.get("task_results"):
            violations.append(
                ContractViolation(
                    type="MISSING_TASK_RESULTS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.input.task_results",
                    message="Task results from Phase 2 are required",
                )
            )
        return _validation_ok(violations)

    @override
    def execute(self, context: ExecutionContext) -> dict[str, Any]:
        phase2_output = context.get_phase_output(PhaseID.PHASE_2)
        if not isinstance(phase2_output, dict):
            raise ValueError("Phase 2 output missing for Phase 3")
        phase2_output = cast(dict[str, Any], phase2_output)
        task_results = cast(list[TaskResult], phase2_output["task_results"])

        signal_registry = phase2_output.get("signal_registry")
        scorer = SignalEnrichedScorer(signal_registry=signal_registry)

        scored_micro_questions: list[ScoredMicroQuestion] = []
        scored_results: list[ScoredResult] = []

        for task in task_results:
            result_data: dict[str, Any] = task.output or {}
            score = extract_score_from_nexus(result_data)
            quality_level = map_completeness_to_quality(result_data.get("completeness"))
            quality_level, validation_details = scorer.validate_quality_level(
                task.question_id,
                quality_level,
                score,
                result_data.get("completeness"),
            )

            scored_micro_questions.append(
                ScoredMicroQuestion(
                    question_id=task.question_id,
                    question_global=task.question_global,
                    base_slot=task.metadata.get("base_slot", ""),
                    score=score,
                    normalized_score=score,
                    quality_level=quality_level,
                    evidence=result_data.get("evidence"),
                    scoring_details={
                        "source": "phase3_score_extraction",
                        "signals_resolved": result_data.get("signals_resolved"),
                        "quality_validation": validation_details,
                    },
                    metadata=task.metadata,
                    error=task.error,
                )
            )

            scored_results.append(
                ScoredResult(
                    question_global=task.question_global,
                    base_slot=task.metadata.get("base_slot", ""),
                    policy_area=task.policy_area_id,
                    dimension=task.dimension_id,
                    score=score,
                    quality_level=quality_level,
                    evidence=result_data.get("evidence", {}),
                    raw_results=_as_dict(result_data),
                )
            )

        return {
            "scored_micro_questions": scored_micro_questions,
            "scored_results": scored_results,
        }

    @override
    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, dict):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.output",
                    message="Phase 3 output must be a dict",
                )
            )
            return _validation_ok(violations)

        output_dict = cast(dict[str, Any], output)
        scored_micro = output_dict.get("scored_micro_questions")
        scored_results = output_dict.get("scored_results")
        scored_micro_list = cast(list[Any], scored_micro) if isinstance(scored_micro, list) else None
        scored_results_list = (
            cast(list[Any], scored_results) if isinstance(scored_results, list) else None
        )
        if scored_micro_list is None or len(scored_micro_list) != 300:
            violations.append(
                ContractViolation(
                    type="SCORE_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.output.scored_micro_questions",
                    message="Phase 3 must return 300 scored micro questions",
                    expected=300,
                    actual=len(scored_micro_list) if scored_micro_list is not None else None,
                )
            )
        if scored_results_list is None or len(scored_results_list) != 300:
            violations.append(
                ContractViolation(
                    type="SCORED_RESULT_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.output.scored_results",
                    message="Phase 3 must return 300 scored results",
                    expected=300,
                    actual=len(scored_results_list) if scored_results_list is not None else None,
                )
            )

        return _validation_ok(violations)


@dataclass
class Phase4Executor(PhaseExecutor):
    """Phase 4 executor: dimension aggregation."""

    @override
    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        phase3_output = context.get_phase_output(PhaseID.PHASE_3)
        if not isinstance(phase3_output, dict):
            violations.append(
                ContractViolation(
                    type="MISSING_SCORED_RESULTS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.input.scored_results",
                    message="Scored results from Phase 3 are required",
                )
            )
            return _validation_ok(violations)
        phase3_output = cast(dict[str, Any], phase3_output)
        if not phase3_output.get("scored_results"):
            violations.append(
                ContractViolation(
                    type="MISSING_SCORED_RESULTS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.input.scored_results",
                    message="Scored results from Phase 3 are required",
                )
            )
        return _validation_ok(violations)

    @override
    def execute(self, context: ExecutionContext) -> list[DimensionScore]:
        phase3_output = context.get_phase_output(PhaseID.PHASE_3)
        if not isinstance(phase3_output, dict):
            raise ValueError("Phase 3 output missing for Phase 4")
        phase3_output = cast(dict[str, Any], phase3_output)
        scored_results = cast(list[ScoredResult], phase3_output["scored_results"])
        questionnaire = context.questionnaire
        if questionnaire is None:
            raise ValueError("Canonical questionnaire missing for Phase 4")

        phase2_output = context.get_phase_output(PhaseID.PHASE_2)
        signal_registry = None
        if isinstance(phase2_output, dict):
            phase2_output = cast(dict[str, Any], phase2_output)
            signal_registry = phase2_output.get("signal_registry")

        aggregator = DimensionAggregator(
            monolith=_questionnaire_data(questionnaire),
            abort_on_insufficient=True,
            signal_registry=signal_registry,
        )
        return aggregator.run(scored_results, aggregator.dimension_group_by_keys)

    @override
    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        output_list = cast(list[Any], output) if isinstance(output, list) else None
        if output_list is None or len(output_list) != 60:
            violations.append(
                ContractViolation(
                    type="DIMENSION_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.output",
                    message="Phase 4 must return 60 dimension scores",
                    expected=60,
                    actual=len(output_list) if output_list is not None else None,
                )
            )
        return _validation_ok(violations)


@dataclass
class Phase5Executor(PhaseExecutor):
    """Phase 5 executor: policy area aggregation."""

    @override
    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        dimension_scores = context.get_phase_output(PhaseID.PHASE_4)
        if not isinstance(dimension_scores, list):
            violations.append(
                ContractViolation(
                    type="MISSING_DIMENSION_SCORES",
                    severity=Severity.CRITICAL,
                    component_path="Phase_05.input.dimension_scores",
                    message="Dimension scores from Phase 4 are required",
                )
            )
        return _validation_ok(violations)

    @override
    def execute(self, context: ExecutionContext) -> Any:
        dimension_scores = context.get_phase_output(PhaseID.PHASE_4)
        if not isinstance(dimension_scores, list):
            raise ValueError("Phase 4 output missing for Phase 5")
        dimension_scores = cast(list[Any], dimension_scores)

        phase2_output = context.get_phase_output(PhaseID.PHASE_2)
        signal_registry = None
        if isinstance(phase2_output, dict):
            phase2_output = cast(dict[str, Any], phase2_output)
            signal_registry = phase2_output.get("signal_registry")

        return asyncio.run(
            run_phase5_aggregation(
                dimension_scores=dimension_scores,
                questionnaire=_questionnaire_data(context.questionnaire),
                signal_registry=signal_registry,
            )
        )

    @override
    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        output_list = cast(list[Any], output) if isinstance(output, list) else None
        if output_list is None or len(output_list) != 10:
            violations.append(
                ContractViolation(
                    type="POLICY_AREA_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_05.output",
                    message="Phase 5 must return 10 policy area scores",
                    expected=10,
                    actual=len(output_list) if output_list is not None else None,
                )
            )
        return _validation_ok(violations)


@dataclass
class Phase6Executor(PhaseExecutor):
    """Phase 6 executor: cluster aggregation."""

    @override
    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        area_scores = context.get_phase_output(PhaseID.PHASE_5)
        if not isinstance(area_scores, list):
            violations.append(
                ContractViolation(
                    type="MISSING_AREA_SCORES",
                    severity=Severity.CRITICAL,
                    component_path="Phase_06.input.area_scores",
                    message="Area scores from Phase 5 are required",
                )
            )
        return _validation_ok(violations)

    @override
    def execute(self, context: ExecutionContext) -> Any:
        area_scores = context.get_phase_output(PhaseID.PHASE_5)
        if not isinstance(area_scores, list):
            raise ValueError("Phase 5 output missing for Phase 6")
        area_scores = cast(list[Any], area_scores)

        aggregator = ClusterAggregator(monolith=_questionnaire_data(context.questionnaire))
        return aggregator.aggregate(area_scores)

    @override
    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        output_list = cast(list[Any], output) if isinstance(output, list) else None
        if output_list is None or len(output_list) != 4:
            violations.append(
                ContractViolation(
                    type="CLUSTER_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_06.output",
                    message="Phase 6 must return 4 cluster scores",
                    expected=4,
                    actual=len(output_list) if output_list is not None else None,
                )
            )
        return _validation_ok(violations)


@dataclass
class Phase7Executor(PhaseExecutor):
    """Phase 7 executor: macro aggregation."""

    @override
    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        cluster_scores = context.get_phase_output(PhaseID.PHASE_6)
        if not isinstance(cluster_scores, list):
            violations.append(
                ContractViolation(
                    type="MISSING_CLUSTER_SCORES",
                    severity=Severity.CRITICAL,
                    component_path="Phase_07.input.cluster_scores",
                    message="Cluster scores from Phase 6 are required",
                )
            )
        return _validation_ok(violations)

    @override
    def execute(self, context: ExecutionContext) -> Any:
        cluster_scores = context.get_phase_output(PhaseID.PHASE_6)
        if not isinstance(cluster_scores, list):
            raise ValueError("Phase 6 output missing for Phase 7")
        cluster_scores = cast(list[Any], cluster_scores)

        aggregator = MacroAggregator()
        return aggregator.aggregate(cluster_scores)

    @override
    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not hasattr(output, "score"):
            violations.append(
                ContractViolation(
                    type="MISSING_MACRO_SCORE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_07.output.score",
                    message="MacroScore must expose 'score'",
                )
            )
        return _validation_ok(violations)


@dataclass
class Phase8Executor(PhaseExecutor):
    """Phase 8 executor: recommendation engine."""

    @override
    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if context.get_phase_output(PhaseID.PHASE_7) is None:
            violations.append(
                ContractViolation(
                    type="MISSING_MACRO_SCORE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_08.input.macro_score",
                    message="Macro score from Phase 7 is required",
                )
            )
        return _validation_ok(violations)

    @override
    def execute(self, context: ExecutionContext) -> dict[str, Any]:
        questionnaire = context.questionnaire
        if questionnaire is None:
            raise ValueError("Canonical questionnaire missing for Phase 8")

        phase4_output = context.get_phase_output(PhaseID.PHASE_4)
        phase6_output = context.get_phase_output(PhaseID.PHASE_6)
        phase7_output = context.get_phase_output(PhaseID.PHASE_7)

        micro_scores: dict[str, float] = {}
        if isinstance(phase4_output, list):
            phase4_output = cast(list[DimensionScore], phase4_output)
            for score in phase4_output:
                key = f"{score.area_id}-{score.dimension_id}"
                micro_scores[key] = score.score

        cluster_data: dict[str, Any] = {}
        if isinstance(phase6_output, list):
            phase6_output = cast(list[Any], phase6_output)
            for cluster in phase6_output:
                cluster_data[cluster.cluster_id] = _as_dict(cluster)

        macro_data = _as_dict(phase7_output)

        phase8_root = Path(__file__).resolve().parents[1] / "phases" / "Phase_8"
        rules_path = phase8_root / RULES_PATH_ENHANCED
        schema_path = phase8_root / SCHEMA_PATH

        wiring = cast(Any, getattr(context, "wiring", None))
        provider = cast(Any, getattr(wiring, "provider", None)) if wiring else None
        adapter = RecommendationEngineAdapter(
            rules_path=rules_path,
            schema_path=schema_path,
            questionnaire_provider=provider,
        )

        return adapter.generate_all_recommendations(
            micro_scores=micro_scores,
            cluster_data=cluster_data,
            macro_data=macro_data,
            context={"questionnaire_version": questionnaire.version},
        )

    @override
    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, dict):
            violations.append(
                ContractViolation(
                    type="INVALID_RECOMMENDATIONS",
                    severity=Severity.HIGH,
                    component_path="Phase_08.output",
                    message="Recommendations output must be a dict",
                )
            )
        return _validation_ok(violations)


@dataclass
class Phase9Executor(PhaseExecutor):
    """Phase 9 executor: report assembly."""

    @override
    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if context.questionnaire is None:
            violations.append(
                ContractViolation(
                    type="MISSING_QUESTIONNAIRE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_09.input.questionnaire",
                    message="Canonical questionnaire is required",
                )
            )
        if context.get_phase_output(PhaseID.PHASE_8) is None:
            violations.append(
                ContractViolation(
                    type="MISSING_RECOMMENDATIONS",
                    severity=Severity.CRITICAL,
                    component_path="Phase_09.input.recommendations",
                    message="Phase 8 recommendations are required",
                )
            )
        return _validation_ok(violations)

    @override
    def execute(self, context: ExecutionContext) -> Any:
        questionnaire = context.questionnaire
        if questionnaire is None:
            raise ValueError("Canonical questionnaire missing for Phase 9")

        phase3_output = context.get_phase_output(PhaseID.PHASE_3)
        phase6_output = context.get_phase_output(PhaseID.PHASE_6)
        phase7_output = context.get_phase_output(PhaseID.PHASE_7)
        phase8_output = context.get_phase_output(PhaseID.PHASE_8)

        question_results: dict[str, Any] = {}
        if isinstance(phase3_output, dict):
            phase3_output = cast(dict[str, Any], phase3_output)
            scored_micro = cast(
                list[ScoredMicroQuestion],
                phase3_output.get("scored_micro_questions", []),
            )
            for scored in scored_micro:
                question_results[scored.question_id] = {
                    "score": scored.score,
                    "evidence": scored.evidence or [],
                }

        meso_clusters: dict[str, Any] = {}
        if isinstance(phase6_output, list):
            phase6_output = cast(list[Any], phase6_output)
            for cluster in phase6_output:
                meso_clusters[cluster.cluster_id] = {
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
                    "metadata": {
                        "weakest_area": cluster.weakest_area,
                        "areas": cluster.areas,
                    },
                }

        macro_summary = _macro_summary_from_score(phase7_output, phase8_output)

        execution_results = {
            "questions": question_results,
            "meso_clusters": meso_clusters,
            "macro_summary": macro_summary,
        }

        wiring = cast(Any, getattr(context, "wiring", None))
        provider = cast(Any, getattr(wiring, "provider", None)) if wiring else None
        assembler = create_report_assembler(
            questionnaire_provider=provider,
            evidence_registry=context.phase_inputs.get(PhaseID.PHASE_9, {}).get("evidence_registry"),
            qmcm_recorder=context.phase_inputs.get(PhaseID.PHASE_9, {}).get("qmcm_recorder"),
            orchestrator=context.phase_inputs.get(PhaseID.PHASE_9, {}).get("orchestrator"),
        )

        plan_name = context.phase_inputs.get(PhaseID.PHASE_9, {}).get("plan_name", "plan")
        enriched_packs = context.phase_inputs.get(PhaseID.PHASE_9, {}).get("enriched_packs")

        execution_results_payload = cast(dict[str, object], execution_results)
        return assembler.assemble_report(
            plan_name=plan_name,
            execution_results=execution_results_payload,
            enriched_packs=enriched_packs,
        )

    @override
    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        required = ["metadata", "micro_analyses", "meso_clusters", "macro_summary"]
        for section in required:
            if not hasattr(output, section):
                violations.append(
                    ContractViolation(
                        type="INCOMPLETE_REPORT",
                        severity=Severity.HIGH,
                        component_path=f"Phase_09.output.{section}",
                        message=f"Missing report section '{section}'",
                    )
                )
        return _validation_ok(violations)


def _macro_summary_from_score(macro_score: Any, recommendations: Any) -> dict[str, Any]:
    if macro_score is None:
        return {}

    base = _as_dict(macro_score)
    recs_list: list[Any] = []
    if isinstance(recommendations, dict):
        recommendations = cast(dict[str, Any], recommendations)
        for level in recommendations.values():
            if hasattr(level, "recommendations"):
                recs_list.extend(cast(list[Any], level.recommendations))
            elif isinstance(level, dict):
                level = cast(dict[str, Any], level)
                recs = level.get("recommendations", [])
                if isinstance(recs, list):
                    recs_list.extend(cast(list[Any], recs))

    return {
        "overall_posterior": base.get("score_normalized", 0.0),
        "adjusted_score": base.get("score", 0.0),
        "coverage_penalty": 0.0,
        "dispersion_penalty": 0.0,
        "contradiction_penalty": 0.0,
        "total_penalty": 0.0,
        "contradiction_count": 0,
        "recommendations": recs_list,
        "metadata": {
            "quality_level": base.get("quality_level"),
            "coherence": base.get("cross_cutting_coherence"),
            "strategic_alignment": base.get("strategic_alignment"),
        },
    }


def _questionnaire_data(questionnaire: QuestionnairePort | None) -> dict[str, Any]:
    if questionnaire is None:
        return {}
    return questionnaire.data


def build_canonical_phase_executors() -> dict[PhaseID, PhaseExecutor]:
    """Return canonical executors for phases P02–P09."""
    return {
        PhaseID.PHASE_2: Phase2Executor(),
        PhaseID.PHASE_3: Phase3Executor(),
        PhaseID.PHASE_4: Phase4Executor(),
        PhaseID.PHASE_5: Phase5Executor(),
        PhaseID.PHASE_6: Phase6Executor(),
        PhaseID.PHASE_7: Phase7Executor(),
        PhaseID.PHASE_8: Phase8Executor(),
        PhaseID.PHASE_9: Phase9Executor(),
    }


__all__ = [
    "Phase2Executor",
    "Phase3Executor",
    "Phase4Executor",
    "Phase5Executor",
    "Phase6Executor",
    "Phase7Executor",
    "Phase8Executor",
    "Phase9Executor",
    "build_canonical_phase_executors",
]
