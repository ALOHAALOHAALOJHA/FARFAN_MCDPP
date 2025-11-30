import importlib
import sys
import types

import pytest

# Stub orchestrator dependencies to avoid circular imports during test import
core_stub = types.ModuleType("farfan_core.core.orchestrator.core")

class _FakeMethodExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, class_name: str, method_name: str, **payload):
        self.calls.append((class_name, method_name, payload))
        return {"class": class_name, "method": method_name, "payload": payload}

core_stub.MethodExecutor = _FakeMethodExecutor
core_stub.AbortRequested = type("AbortRequested", (), {})
core_stub.AbortSignal = type("AbortSignal", (), {})
core_stub.ResourceLimits = type("ResourceLimits", (), {})
core_stub.PhaseInstrumentation = type("PhaseInstrumentation", (), {})
core_stub.PhaseResult = type("PhaseResult", (), {})
core_stub.MicroQuestionRun = type("MicroQuestionRun", (), {})
core_stub.ScoredMicroQuestion = type("ScoredMicroQuestion", (), {})
core_stub.Evidence = type("Evidence", (), {})
core_stub.PreprocessedDocument = type("PreprocessedDocument", (), {})
core_stub.Orchestrator = type("Orchestrator", (), {})
sys.modules["farfan_core.core.orchestrator.core"] = core_stub

factory_stub = types.ModuleType("farfan_core.core.orchestrator.factory")
def _fake_build_processor(me: _FakeMethodExecutor | None = None):
    bundle = types.SimpleNamespace()
    bundle.method_executor = me or _FakeMethodExecutor()
    return bundle
factory_stub.build_processor = _fake_build_processor
sys.modules["farfan_core.core.orchestrator.factory"] = factory_stub

contract_loader = types.ModuleType("contract_loader")
class _Dummy:  # minimal placeholder types
    pass
contract_loader.JSONContractLoader = _Dummy
contract_loader.LoadError = _Dummy
contract_loader.LoadResult = _Dummy
sys.modules.setdefault("farfan_core.core.orchestrator.contract_loader", contract_loader)

exec_mod = importlib.import_module("farfan_core.core.orchestrator.executors")


def test_run_phase2_executors_uses_method_executor(monkeypatch):
    """Ensure executors are instantiated with MethodExecutor and routed calls go through it."""

    class FakeMethodExecutor:
        def __init__(self):
            self.calls = []

        def execute(self, class_name: str, method_name: str, **payload):
            self.calls.append((class_name, method_name, payload))
            return {"class": class_name, "method": method_name, "payload": payload}

    # Patch MethodExecutor type used by BaseExecutor and factory wiring
    monkeypatch.setattr(exec_mod, "MethodExecutor", FakeMethodExecutor)

    fake_executor = FakeMethodExecutor()

    class FakeBundle:
        def __init__(self, me):
            self.method_executor = me

    # Provide a bundle that supplies the fake MethodExecutor
    monkeypatch.setattr(exec_mod, "build_processor", lambda: FakeBundle(fake_executor))
    monkeypatch.setattr(exec_mod, "load_executor_config", lambda _: {})

    # Minimal executor that exercises _execute_method once
    class DummyExecutor(exec_mod.BaseExecutor):
        def execute(self, context: dict):
            result = self._execute_method("DummyClass", "dummy_method", context, foo="bar")
            return {
                "executor_id": self.executor_id,
                "raw_evidence": result,
                "metadata": {"methods_executed": [log["method"] for log in self.execution_log]},
                "execution_metrics": {},
            }

    monkeypatch.setattr(exec_mod, "EXECUTOR_REGISTRY", {"D-TEST": DummyExecutor})

    context_package = {"doc": "text"}
    results = exec_mod.run_phase2_executors(context_package, ["PA01"])

    # Validate that MethodExecutor.execute was called with merged context + kwargs
    assert fake_executor.calls == [
        ("DummyClass", "dummy_method", {"doc": "text", "policy_area": "PA01", "foo": "bar"})
    ]
    assert "PA01" in results
    assert "D-TEST" in results["PA01"]
