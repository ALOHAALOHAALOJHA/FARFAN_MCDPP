import json
from pathlib import Path

import pytest

from farfan_core.core.orchestrator.base_executor_with_contract import BaseExecutorWithContract
from farfan_core.core.orchestrator.core import MethodExecutor, PreprocessedDocument
from farfan_core.core.orchestrator.executors_contract import D1Q1_Executor_Contract


def _doc() -> PreprocessedDocument:
    return PreprocessedDocument(
        document_id="doc",
        raw_text="sample text",
        sentences=["sample text"],
        tables=[],
        metadata={},
    )


def _question(base_slot: str = "D1-Q1") -> dict:
    return {"base_slot": base_slot, "question_id": "qid", "question_global": 1}


def test_executor_rejects_foreign_method_executor():
    primary = MethodExecutor()
    foreign = MethodExecutor()
    executor = D1Q1_Executor_Contract(
        method_executor=primary,
        signal_registry=None,
        config=None,
        questionnaire_provider=None,
    )

    with pytest.raises(RuntimeError):
        executor.execute(_doc(), foreign, question_context=_question())


def test_executor_rejects_wrong_base_slot():
    method_executor = MethodExecutor()
    executor = D1Q1_Executor_Contract(
        method_executor=method_executor,
        signal_registry=None,
        config=None,
        questionnaire_provider=None,
    )

    with pytest.raises(ValueError):
        executor.execute(
            _doc(),
            method_executor,
            question_context=_question(base_slot="OTHER"),
        )


def test_invalid_contract_raises(monkeypatch, tmp_path: Path):
    """Ensure contract schema validation failures raise ValueError."""
    config_dir = tmp_path / "config"
    contracts_dir = config_dir / "executor_contracts"
    contracts_dir.mkdir(parents=True)

    schema_path = config_dir / "executor_contract.schema.json"
    schema_path.write_text(
        json.dumps(
            {
                "type": "object",
                "required": ["base_slot", "method_inputs", "assembly_rules", "validation_rules"],
                "properties": {
                    "base_slot": {"type": "string"},
                    "method_inputs": {"type": "array"},
                    "assembly_rules": {"type": "array"},
                    "validation_rules": {"type": "array"},
                },
            }
        ),
        encoding="utf-8",
    )

    # Missing required fields -> should fail validation
    bad_contract = contracts_dir / "D1-Q1.json"
    bad_contract.write_text(json.dumps({"base_slot": "D1-Q1"}), encoding="utf-8")

    from farfan_core.core.orchestrator import base_executor_with_contract as mod

    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    D1Q1_Executor_Contract._contract_cache.clear()
    D1Q1_Executor_Contract._schema_validator = None  # type: ignore[assignment]

    with pytest.raises(ValueError):
        D1Q1_Executor_Contract._load_contract()
