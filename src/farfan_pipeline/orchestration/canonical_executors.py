"""Canonical phase executors for the FARFAN pipeline (P02–P09).

These executors implement strict, explicit, phase-by-phase orchestration with
topological ordering, interface contracts, and traceable node sequencing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from farfan_pipeline.orchestration.core_orchestrator import (
    ExecutionContext,
    PhaseExecutor,
    PhaseID,
    PhaseStatus,
)
from farfan_pipeline.phases.Phase_00.interphase.wiring_types import (
    ContractViolation,
    Severity,
    ValidationResult,
)


@dataclass(frozen=True)
class Phase2Output:
    execution_plan: Any
    task_results: list[Any]
    preprocessed_document: Any
    questionnaire_signal_registry: Any
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase3Output:
    layer_scores: list[Any]
    scored_results: list[Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase4Output:
    dimension_scores: list[Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase5Output:
    area_scores: list[Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase6Output:
    cluster_scores: list[Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase7Output:
    macro_score: Any
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase8Output:
    recommendations: dict[str, Any]
    node_trace: tuple[str, ...]


@dataclass(frozen=True)
class Phase9Output:
    report: Any
    node_trace: tuple[str, ...]


def _validation_passed(violations: list[ContractViolation]) -> ValidationResult:
    return ValidationResult(
        passed=not any(v.severity == Severity.CRITICAL for v in violations),
        violations=violations,
        validation_time_ms=0.0,
    )


def _assert_node_trace(node_trace: list[str], expected: tuple[str, ...]) -> None:
    if tuple(node_trace) != expected:
        raise ValueError(
            "Phase node sequence violation. "
            f"Expected {expected}, got {tuple(node_trace)}"
        )


class Phase2Executor(PhaseExecutor):
    """Phase 2: Executor factory, synchronization, and task execution."""

    NODE_SEQUENCE = (
        "phase2.signal_registry",
        "phase2.cpp_adapter",
        "phase2.irrigation_synchronizer",
        "phase2.execution_plan",
        "phase2.task_execution",
    )

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []

        cpp = context.get_phase_output(PhaseID.PHASE_1)
        if cpp is None:
            violations.append(
                ContractViolation(
                    type="MISSING_CPP",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.input",
                    message="Phase 2 requires CPP output from Phase 1",
                )
            )

        if context.questionnaire is None:
            violations.append(
                ContractViolation(
                    type="MISSING_QUESTIONNAIRE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.input",
                    message="Phase 2 requires canonical questionnaire",
                )
            )

        return _validation_passed(violations)

    def execute(self, context: ExecutionContext) -> Phase2Output:
        node_trace: list[str] = []

        from farfan_pipeline.phases.Phase_01.interphase.phase1_08_00_adapter import (
            adapt_cpp_to_orchestrator,
        )
        from farfan_pipeline.phases.Phase_02.phase2_40_03_irrigation_synchronizer import (
            IrrigationSynchronizer,
        )
        from farfan_pipeline.phases.Phase_02.phase2_50_00_task_executor import (
            TaskExecutor,
        )
        from farfan_pipeline.phases.Phase_02.registries import (
            QuestionnaireSignalRegistry,
        )

        cpp = context.get_phase_output(PhaseID.PHASE_1)
        if cpp is None:
            raise ValueError("Phase 2 cannot execute without CPP output")

        questionnaire_data = context.questionnaire.data

        registry_override = context.phase_inputs.get(PhaseID.PHASE_2, {}).get(
            "questionnaire_signal_registry"
        )
        questionnaire_signal_registry = (
            registry_override or QuestionnaireSignalRegistry()
        )
        node_trace.append(self.NODE_SEQUENCE[0])

        preprocessed_document = adapt_cpp_to_orchestrator(
            cpp, getattr(cpp, "document_id", "UNKNOWN")
        )
        node_trace.append(self.NODE_SEQUENCE[1])

        enable_join_table = context.phase_inputs.get(PhaseID.PHASE_2, {}).get(
            "enable_join_table", False
        )
        contracts = context.phase_inputs.get(PhaseID.PHASE_2, {}).get(
            "executor_contracts"
        )
        if enable_join_table and not contracts:
            raise ValueError("Phase 2 JOIN table enabled but executor_contracts missing")

        synchronizer = IrrigationSynchronizer(
            questionnaire=questionnaire_data,
            preprocessed_document=preprocessed_document,
            signal_registry=questionnaire_signal_registry,
            contracts=contracts,
            enable_join_table=enable_join_table,
        )
        node_trace.append(self.NODE_SEQUENCE[2])

        execution_plan = synchronizer.build_execution_plan()
        node_trace.append(self.NODE_SEQUENCE[3])

        calibration_registry = context.phase_inputs.get(PhaseID.PHASE_2, {}).get(
            "calibration_registry"
        )
        pdm_profile = context.phase_inputs.get(PhaseID.PHASE_2, {}).get("pdm_profile")

        executor = TaskExecutor(
            questionnaire_monolith=questionnaire_data,
            preprocessed_document=preprocessed_document,
            signal_registry=questionnaire_signal_registry,
            calibration_registry=calibration_registry,
            pdm_profile=pdm_profile,
        )
        task_results = executor.execute_plan(execution_plan)
        node_trace.append(self.NODE_SEQUENCE[4])

        if len(task_results) != 300:
            raise ValueError(
                f"Phase 2 expected 300 task results, got {len(task_results)}"
            )

        _assert_node_trace(node_trace, self.NODE_SEQUENCE)

        return Phase2Output(
            execution_plan=execution_plan,
            task_results=task_results,
            preprocessed_document=preprocessed_document,
            questionnaire_signal_registry=questionnaire_signal_registry,
            node_trace=tuple(node_trace),
        )

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, Phase2Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.output",
                    message="Phase 2 must return Phase2Output",
                )
            )
            return _validation_passed(violations)

        if len(output.task_results) != 300:
            violations.append(
                ContractViolation(
                    type="TASK_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_02.output.task_results",
                    message="Phase 2 must produce 300 task results",
                    expected=300,
                    actual=len(output.task_results),
                )
            )

        return _validation_passed(violations)


class Phase3Executor(PhaseExecutor):
    """Phase 3: Score extraction and signal-enriched validation."""

    NODE_SEQUENCE = (
        "phase3.input_projection",
        "phase3.score_extraction",
        "phase3.quality_validation",
        "phase3.output_projection",
    )

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        phase2_output = context.get_phase_output(PhaseID.PHASE_2)
        if phase2_output is None:
            violations.append(
                ContractViolation(
                    type="MISSING_PHASE2_OUTPUT",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.input",
                    message="Phase 3 requires Phase 2 output",
                )
            )
        return _validation_passed(violations)

    def execute(self, context: ExecutionContext) -> Phase3Output:
        node_trace: list[str] = []

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
        from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import (
            ScoredResult,
        )

        phase2_output = context.get_phase_output(PhaseID.PHASE_2)
        if phase2_output is None:
            raise ValueError("Phase 3 cannot execute without Phase 2 output")

        questionnaire_data = context.questionnaire.data
        questions = {
            q.get("question_id"): q
            for q in questionnaire_data.get("blocks", {}).get("micro_questions", [])
            if q.get("question_id")
        }

        scorer = SignalEnrichedScorer(
            signal_registry=getattr(phase2_output, "questionnaire_signal_registry", None)
        )
        node_trace.append(self.NODE_SEQUENCE[0])

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

        node_trace.append(self.NODE_SEQUENCE[1])
        node_trace.append(self.NODE_SEQUENCE[2])

        if len(scored_micro_questions) != 300:
            raise ValueError(
                f"Phase 3 expected 300 scored micro questions, got {len(scored_micro_questions)}"
            )

        node_trace.append(self.NODE_SEQUENCE[3])

        _assert_node_trace(node_trace, self.NODE_SEQUENCE)

        return Phase3Output(
            layer_scores=scored_micro_questions,
            scored_results=scored_results,
            node_trace=tuple(node_trace),
        )

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, Phase3Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.output",
                    message="Phase 3 must return Phase3Output",
                )
            )
            return _validation_passed(violations)

        if len(output.layer_scores) != 300:
            violations.append(
                ContractViolation(
                    type="SCORE_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_03.output.layer_scores",
                    message="Phase 3 must output 300 layer scores",
                    expected=300,
                    actual=len(output.layer_scores),
                )
            )

        return _validation_passed(violations)


class Phase4Executor(PhaseExecutor):
    """Phase 4: Dimension aggregation."""

    NODE_SEQUENCE = (
        "phase4.aggregation_settings",
        "phase4.dimension_aggregation",
    )

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if context.get_phase_output(PhaseID.PHASE_3) is None:
            violations.append(
                ContractViolation(
                    type="MISSING_PHASE3_OUTPUT",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.input",
                    message="Phase 4 requires Phase 3 output",
                )
            )
        return _validation_passed(violations)

    def execute(self, context: ExecutionContext) -> Phase4Output:
        from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import (
            DimensionAggregator,
        )

        phase3_output = context.get_phase_output(PhaseID.PHASE_3)
        if phase3_output is None:
            raise ValueError("Phase 4 cannot execute without Phase 3 output")

        aggregator = DimensionAggregator(
            monolith=context.questionnaire.data,
            abort_on_insufficient=True,
            signal_registry=getattr(
                context.get_phase_output(PhaseID.PHASE_2),
                "questionnaire_signal_registry",
                None,
            ),
        )

        node_trace = [self.NODE_SEQUENCE[0]]
        dimension_scores = aggregator.run(
            phase3_output.scored_results,
            group_by_keys=aggregator.dimension_group_by_keys,
        )
        node_trace.append(self.NODE_SEQUENCE[1])

        _assert_node_trace(node_trace, self.NODE_SEQUENCE)

        return Phase4Output(
            dimension_scores=dimension_scores,
            node_trace=tuple(node_trace),
        )

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, Phase4Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.output",
                    message="Phase 4 must return Phase4Output",
                )
            )
            return _validation_passed(violations)

        if len(output.dimension_scores) != 60:
            violations.append(
                ContractViolation(
                    type="DIMENSION_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_04.output.dimension_scores",
                    message="Phase 4 must output 60 dimension scores",
                    expected=60,
                    actual=len(output.dimension_scores),
                )
            )

        return _validation_passed(violations)


class Phase5Executor(PhaseExecutor):
    """Phase 5: Policy area aggregation."""

    NODE_SEQUENCE = (
        "phase5.aggregation",
        "phase5.validation",
    )

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if context.get_phase_output(PhaseID.PHASE_4) is None:
            violations.append(
                ContractViolation(
                    type="MISSING_PHASE4_OUTPUT",
                    severity=Severity.CRITICAL,
                    component_path="Phase_05.input",
                    message="Phase 5 requires Phase 4 output",
                )
            )
        return _validation_passed(violations)

    def execute(self, context: ExecutionContext) -> Phase5Output:
        import asyncio
        from farfan_pipeline.phases.Phase_05.phase5_30_00_area_integration import (
            run_phase5_aggregation,
        )

        phase4_output = context.get_phase_output(PhaseID.PHASE_4)
        if phase4_output is None:
            raise ValueError("Phase 5 cannot execute without Phase 4 output")

        async def _run() -> list[Any]:
            return await run_phase5_aggregation(
                dimension_scores=phase4_output.dimension_scores,
                questionnaire=context.questionnaire.data,
                signal_registry=getattr(
                    context.get_phase_output(PhaseID.PHASE_2),
                    "questionnaire_signal_registry",
                    None,
                ),
                validate=True,
            )

        node_trace = [self.NODE_SEQUENCE[0]]

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

        node_trace.append(self.NODE_SEQUENCE[1])

        _assert_node_trace(node_trace, self.NODE_SEQUENCE)

        return Phase5Output(area_scores=area_scores, node_trace=tuple(node_trace))

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, Phase5Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_05.output",
                    message="Phase 5 must return Phase5Output",
                )
            )
            return _validation_passed(violations)

        if len(output.area_scores) != 10:
            violations.append(
                ContractViolation(
                    type="POLICY_AREA_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_05.output.area_scores",
                    message="Phase 5 must output 10 area scores",
                    expected=10,
                    actual=len(output.area_scores),
                )
            )

        return _validation_passed(violations)


class Phase6Executor(PhaseExecutor):
    """Phase 6: Cluster aggregation."""

    NODE_SEQUENCE = (
        "phase6.cluster_aggregation",
    )

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if context.get_phase_output(PhaseID.PHASE_5) is None:
            violations.append(
                ContractViolation(
                    type="MISSING_PHASE5_OUTPUT",
                    severity=Severity.CRITICAL,
                    component_path="Phase_06.input",
                    message="Phase 6 requires Phase 5 output",
                )
            )
        return _validation_passed(violations)

    def execute(self, context: ExecutionContext) -> Phase6Output:
        from farfan_pipeline.phases.Phase_06.phase6_30_00_cluster_aggregator import (
            ClusterAggregator,
        )

        phase5_output = context.get_phase_output(PhaseID.PHASE_5)
        if phase5_output is None:
            raise ValueError("Phase 6 cannot execute without Phase 5 output")

        aggregator = ClusterAggregator(
            monolith=context.questionnaire.data,
            abort_on_insufficient=True,
            enforce_contracts=True,
            contract_mode="strict",
        )

        cluster_scores = aggregator.aggregate(phase5_output.area_scores)

        _assert_node_trace(list(self.NODE_SEQUENCE), self.NODE_SEQUENCE)

        return Phase6Output(cluster_scores=cluster_scores, node_trace=self.NODE_SEQUENCE)

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, Phase6Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_06.output",
                    message="Phase 6 must return Phase6Output",
                )
            )
            return _validation_passed(violations)

        if len(output.cluster_scores) != 4:
            violations.append(
                ContractViolation(
                    type="CLUSTER_COUNT_VIOLATION",
                    severity=Severity.CRITICAL,
                    component_path="Phase_06.output.cluster_scores",
                    message="Phase 6 must output 4 cluster scores",
                    expected=4,
                    actual=len(output.cluster_scores),
                )
            )

        return _validation_passed(violations)


class Phase7Executor(PhaseExecutor):
    """Phase 7: Macro aggregation."""

    NODE_SEQUENCE = (
        "phase7.macro_aggregation",
    )

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if context.get_phase_output(PhaseID.PHASE_6) is None:
            violations.append(
                ContractViolation(
                    type="MISSING_PHASE6_OUTPUT",
                    severity=Severity.CRITICAL,
                    component_path="Phase_07.input",
                    message="Phase 7 requires Phase 6 output",
                )
            )
        return _validation_passed(violations)

    def execute(self, context: ExecutionContext) -> Phase7Output:
        from farfan_pipeline.phases.Phase_07.phase7_20_00_macro_aggregator import (
            MacroAggregator,
        )

        phase6_output = context.get_phase_output(PhaseID.PHASE_6)
        if phase6_output is None:
            raise ValueError("Phase 7 cannot execute without Phase 6 output")

        aggregator = MacroAggregator()
        macro_score = aggregator.aggregate(phase6_output.cluster_scores)

        _assert_node_trace(list(self.NODE_SEQUENCE), self.NODE_SEQUENCE)

        return Phase7Output(macro_score=macro_score, node_trace=self.NODE_SEQUENCE)

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, Phase7Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_07.output",
                    message="Phase 7 must return Phase7Output",
                )
            )
            return _validation_passed(violations)

        if not hasattr(output.macro_score, "score"):
            violations.append(
                ContractViolation(
                    type="INVALID_MACRO_SCORE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_07.output.macro_score",
                    message="Phase 7 macro_score must expose score",
                )
            )

        return _validation_passed(violations)


class Phase8Executor(PhaseExecutor):
    """Phase 8: Recommendation generation."""

    NODE_SEQUENCE = (
        "phase8.adapter_init",
        "phase8.recommendation_generation",
    )

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if context.get_phase_output(PhaseID.PHASE_7) is None:
            violations.append(
                ContractViolation(
                    type="MISSING_PHASE7_OUTPUT",
                    severity=Severity.CRITICAL,
                    component_path="Phase_08.input",
                    message="Phase 8 requires Phase 7 output",
                )
            )
        return _validation_passed(violations)

    def execute(self, context: ExecutionContext) -> Phase8Output:
        from farfan_pipeline.phases.Phase_08.phase8_20_01_recommendation_engine_adapter import (
            RecommendationEngineAdapter,
        )
        from farfan_pipeline.phases.Phase_08.primitives.PHASE_8_CONSTANTS import (
            RULES_PATH_ENHANCED,
            SCHEMA_PATH,
        )

        phase4_output = context.get_phase_output(PhaseID.PHASE_4)
        phase6_output = context.get_phase_output(PhaseID.PHASE_6)
        phase7_output = context.get_phase_output(PhaseID.PHASE_7)

        if phase4_output is None or phase6_output is None or phase7_output is None:
            raise ValueError("Phase 8 requires outputs from phases 4, 6, and 7")

        phase8_root = Path(__file__).resolve().parents[2] / "phases" / "Phase_08"
        rules_path = phase8_root / RULES_PATH_ENHANCED
        schema_path = phase8_root / SCHEMA_PATH

        adapter = RecommendationEngineAdapter(
            rules_path=rules_path,
            schema_path=schema_path,
            questionnaire_provider=context.wiring.provider if context.wiring else None,
            orchestrator=None,
        )

        node_trace = [self.NODE_SEQUENCE[0]]

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

        recommendations = adapter.generate_all_recommendations(
            micro_scores=micro_scores,
            cluster_data=cluster_data,
            macro_data=macro_data,
            context={"pipeline_version": "3.0.0"},
        )
        node_trace.append(self.NODE_SEQUENCE[1])

        _assert_node_trace(node_trace, self.NODE_SEQUENCE)

        return Phase8Output(recommendations=recommendations, node_trace=tuple(node_trace))

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, Phase8Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_08.output",
                    message="Phase 8 must return Phase8Output",
                )
            )
            return _validation_passed(violations)

        if not output.recommendations:
            violations.append(
                ContractViolation(
                    type="EMPTY_RECOMMENDATIONS",
                    severity=Severity.HIGH,
                    component_path="Phase_08.output.recommendations",
                    message="Phase 8 recommendations are empty",
                )
            )

        return _validation_passed(violations)


class Phase9Executor(PhaseExecutor):
    """Phase 9: Report assembly."""

    NODE_SEQUENCE = (
        "phase9.report_assembler",
        "phase9.report_assembly",
    )

    def validate_input(self, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if context.get_phase_output(PhaseID.PHASE_8) is None:
            violations.append(
                ContractViolation(
                    type="MISSING_PHASE8_OUTPUT",
                    severity=Severity.CRITICAL,
                    component_path="Phase_09.input",
                    message="Phase 9 requires Phase 8 output",
                )
            )
        if context.wiring is None:
            violations.append(
                ContractViolation(
                    type="MISSING_WIRING",
                    severity=Severity.CRITICAL,
                    component_path="Phase_09.input",
                    message="Phase 9 requires wiring provider",
                )
            )
        return _validation_passed(violations)

    def execute(self, context: ExecutionContext) -> Phase9Output:
        from farfan_pipeline.phases.Phase_09.phase9_10_00_report_assembly import (
            create_report_assembler,
        )

        phase3_output = context.get_phase_output(PhaseID.PHASE_3)
        phase6_output = context.get_phase_output(PhaseID.PHASE_6)
        phase7_output = context.get_phase_output(PhaseID.PHASE_7)
        phase8_output = context.get_phase_output(PhaseID.PHASE_8)

        if any(output is None for output in [phase3_output, phase6_output, phase7_output, phase8_output]):
            raise ValueError("Phase 9 requires outputs from phases 3, 6, 7, and 8")

        node_trace = [self.NODE_SEQUENCE[0]]

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
                    "completeness": q.scoring_details.get("quality_validation", {}).get(
                        "completeness"
                    ),
                    "validation": {"status": "passed" if q.error is None else "failed"},
                }
                for q in phase3_output.layer_scores
            },
        }

        enriched_packs = context.phase_inputs.get(PhaseID.PHASE_9, {}).get(
            "enriched_packs"
        )
        plan_name = context.config.get("plan_name", "Plan")

        assembler = create_report_assembler(
            questionnaire_provider=context.wiring.provider,
            evidence_registry=context.phase_inputs.get(PhaseID.PHASE_9, {}).get(
                "evidence_registry"
            ),
            qmcm_recorder=context.phase_inputs.get(PhaseID.PHASE_9, {}).get(
                "qmcm_recorder"
            ),
            orchestrator=None,
        )

        node_trace.append(self.NODE_SEQUENCE[1])

        report = assembler.assemble_report(
            plan_name=plan_name,
            execution_results=execution_results,
            enriched_packs=enriched_packs,
        )

        _assert_node_trace(node_trace, self.NODE_SEQUENCE)

        return Phase9Output(report=report, node_trace=tuple(node_trace))

    def validate_output(self, output: Any, context: ExecutionContext) -> ValidationResult:
        violations: list[ContractViolation] = []
        if not isinstance(output, Phase9Output):
            violations.append(
                ContractViolation(
                    type="INVALID_OUTPUT_TYPE",
                    severity=Severity.CRITICAL,
                    component_path="Phase_09.output",
                    message="Phase 9 must return Phase9Output",
                )
            )
            return _validation_passed(violations)

        if not hasattr(output.report, "micro_analyses"):
            violations.append(
                ContractViolation(
                    type="INVALID_REPORT",
                    severity=Severity.HIGH,
                    component_path="Phase_09.output.report",
                    message="Report missing micro_analyses",
                )
            )

        return _validation_passed(violations)


def build_canonical_phase_executors() -> dict[PhaseID, PhaseExecutor]:
    """Factory for canonical phase executors (P02–P09)."""
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
    "Phase2Output",
    "Phase3Output",
    "Phase4Output",
    "Phase5Output",
    "Phase6Output",
    "Phase7Output",
    "Phase8Output",
    "Phase9Output",
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