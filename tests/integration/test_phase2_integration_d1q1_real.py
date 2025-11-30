from __future__ import annotations

from pathlib import Path

import pytest

from farfan_core.core.orchestrator.core import Orchestrator, PreprocessedDocument
from farfan_core.core.orchestrator.executors_contract import D1Q1_Executor_Contract
from farfan_core.core.orchestrator.factory import build_processor
from farfan_core.core.orchestrator.questionnaire import load_questionnaire
from farfan_core.core.phases.phase0_input_validation import Phase0Input, Phase0ValidationContract
from farfan_core.core.phases.phase1_spc_ingestion import Phase1SPCIngestionContract
from farfan_core.core.phases.phase1_to_phase2_adapter import AdapterContract


def _load_d1q1_question() -> dict:
    questionnaire = load_questionnaire()
    for question in questionnaire.data.get("blocks", {}).get("micro_questions", []):
        if question.get("base_slot") == "D1-Q1":
            return question
    raise RuntimeError("D1-Q1 question not found in questionnaire")


@pytest.mark.asyncio
async def test_d1q1_real_integration():
    pdf_path = Path("data/plans/Plan_1.pdf")
    assert pdf_path.exists(), "Test PDF fixture not found"

    # Phase 0 → Phase 1 → Adapter
    phase0 = Phase0ValidationContract()
    phase1 = Phase1SPCIngestionContract()
    adapter = AdapterContract()

    phase0_input = Phase0Input(pdf_path=pdf_path, run_id="test_d1q1_integration")
    canonical_input = await phase0.execute(phase0_input)
    cpp = await phase1.execute(canonical_input)
    preprocessed = await adapter.execute(cpp)

    assert isinstance(preprocessed, PreprocessedDocument)
    assert preprocessed.raw_text

    # Build processor bundle and orchestrator for questionnaire_provider wiring
    bundle = build_processor()
    orchestrator = Orchestrator(
        method_executor=bundle.method_executor,
        questionnaire=bundle.questionnaire,
        executor_config=bundle.executor_config,
        calibration_orchestrator=None,
    )

    d1q1_question = _load_d1q1_question()

    executor = D1Q1_Executor_Contract(
        method_executor=bundle.method_executor,
        signal_registry=bundle.signal_registry,
        config=bundle.executor_config,
        questionnaire_provider=orchestrator.questionnaire_provider,
        calibration_orchestrator=orchestrator.calibration_orchestrator,
    )

    result = executor.execute(
        preprocessed,
        bundle.method_executor,
        question_context=d1q1_question,
    )

    assert result["base_slot"] == "D1-Q1"
    assert result["question_id"] == d1q1_question["question_id"]
    assert "evidence" in result
    assert "validation" in result
    assert isinstance(result["validation"].get("valid"), bool)
