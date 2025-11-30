import json
import sys
import types
from glob import glob

import pytest
from jsonschema import Draft7Validator

# Stub missing modules to allow importing orchestrator package without circular errors
contract_loader = types.ModuleType("contract_loader")
class _Dummy:
    pass
contract_loader.JSONContractLoader = _Dummy
contract_loader.LoadError = _Dummy
contract_loader.LoadResult = _Dummy
sys.modules.setdefault("farfan_core.core.orchestrator.contract_loader", contract_loader)

core_stub = types.ModuleType("farfan_core.core.orchestrator.core")
class _StubMethodExecutor:
    def execute(self, *args, **kwargs):
        return {}
core_stub.MethodExecutor = _StubMethodExecutor
class _StubPreprocessedDocument:
    def __init__(self, document_id, raw_text, sentences, tables, metadata):
        self.document_id = document_id
        self.raw_text = raw_text
        self.sentences = sentences
        self.tables = tables
        self.metadata = metadata
core_stub.PreprocessedDocument = _StubPreprocessedDocument
core_stub.AbortRequested = type("AbortRequested", (), {})
core_stub.AbortSignal = type("AbortSignal", (), {})
core_stub.ResourceLimits = type("ResourceLimits", (), {})
core_stub.PhaseInstrumentation = type("PhaseInstrumentation", (), {})
core_stub.PhaseResult = type("PhaseResult", (), {})
core_stub.MicroQuestionRun = type("MicroQuestionRun", (), {})
core_stub.ScoredMicroQuestion = type("ScoredMicroQuestion", (), {})
core_stub.Evidence = type("Evidence", (), {})
core_stub.Orchestrator = type("Orchestrator", (), {})
sys.modules.setdefault("farfan_core.core.orchestrator.core", core_stub)

from farfan_core.core.orchestrator.class_registry import build_class_registry, ClassRegistryError
from farfan_core.core.orchestrator.core import PreprocessedDocument, MethodExecutor
from farfan_core.core.orchestrator.executors_contract import D1Q1_Executor_Contract


def test_contracts_validate_against_schema():
    schema_path = "config/executor_contract.schema.json"
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    validator = Draft7Validator(schema)

    for path in glob("config/executor_contracts/*.json"):
        with open(path, encoding="utf-8") as f:
            contract = json.load(f)
        errors = list(validator.iter_errors(contract))
        assert not errors, f"Schema validation failed for {path}: {[e.message for e in errors]}"


def test_contract_methods_exist_in_registry():
    try:
        registry = build_class_registry()
    except ClassRegistryError as exc:  # pragma: no cover - environment-specific
        pytest.skip(f"class registry unavailable: {exc}")

    for path in glob("config/executor_contracts/*.json"):
        contract = json.loads(open(path, encoding="utf-8").read())
        for mi in contract.get("method_inputs", []):
            cls_name = mi["class"]
            method_name = mi["method"]
            assert cls_name in registry, f"{cls_name} not in class registry for {path}"
            cls = registry[cls_name]
            assert hasattr(cls, method_name), f"{cls_name}.{method_name} missing for {path}"


def test_d1q1_executor_contract_smoke(monkeypatch):
    # Fake MethodExecutor to avoid heavy dependencies
    fake_me = MethodExecutor.__new__(MethodExecutor)
    def _fake_execute(class_name: str, method_name: str, **kwargs):
        return {"class": class_name, "method": method_name, "payload": kwargs}
    fake_me.execute = _fake_execute  # type: ignore[attr-defined]

    executor = D1Q1_Executor_Contract(
        fake_me,
        signal_registry=None,
        config=None,
        questionnaire_provider=None,
    )

    doc = PreprocessedDocument(
        document_id="doc1",
        raw_text="some text",
        sentences=["some text"],
        tables=[],
        metadata={"chunk_count": 1},
    )

    question_context = {
        "base_slot": "D1-Q1",
        "question_id": "D1-Q1",
        "question_global": 1,
        "policy_area_id": "PA01",
        "dimension_id": "D1",
        "cluster_id": "C1",
        "patterns": [],
        "expected_elements": [],
    }

    result = executor.execute(doc, fake_me, question_context=question_context)
    assert result["base_slot"] == "D1-Q1"
    assert "evidence" in result
    assert "analysis" in result["evidence"]
    assert result["validation"]["valid"] is True
