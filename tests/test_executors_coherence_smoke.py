import importlib
from typing import Any, Dict

import pytest


def test_executors_module_imports_and_registry_populated():
    """Smoke test: executors module loads and registry is non-empty (compilación/import)."""

    mod = importlib.import_module("saaaaaa.core.orchestrator.executors")
    assert hasattr(mod, "EXECUTOR_REGISTRY")
    assert isinstance(mod.EXECUTOR_REGISTRY, dict)
    assert mod.EXECUTOR_REGISTRY, "Executor registry should not be empty"


def test_base_executor_sequence_with_real_method_executor(monkeypatch):
    """
    Verifies method injection/sequence recording using MethodExecutor (sin mocks inventados).
    Ensures context kwargs se combinan y se registra el orden de ejecución.
    """

    executors_mod = importlib.import_module("saaaaaa.core.orchestrator.executors")
    MethodExecutor = executors_mod.MethodExecutor
    BaseExecutor = executors_mod.BaseExecutor

    class _TestHook:
        def run(self, **kwargs: Any) -> Dict[str, Any]:
            return {"ok": True, "received": kwargs}

    class _DummyRegistry:
        def get_method(self, class_name: str, method_name: str, init_kwargs: Dict[str, Any] | None = None):
            if class_name == "_TestHook" and method_name == "run":
                return getattr(_TestHook(), method_name)
            raise RuntimeError(f"Unsupported method requested: {class_name}.{method_name}")

    class RecordingMethodExecutor(MethodExecutor):
        def __init__(self) -> None:
            super().__init__(method_registry=_DummyRegistry())
            self.calls: list[tuple[str, str, dict[str, Any]]] = []

        def execute(self, class_name: str, method_name: str, **kwargs: Any) -> Any:
            self.calls.append((class_name, method_name, kwargs))
            return super().execute(class_name, method_name, **kwargs)

    class DummyExecutor(BaseExecutor):
        def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
            hook_result = self._execute_method("_TestHook", "run", context, marker="seq")
            return {
                "executor_id": self.executor_id,
                "raw_evidence": {"hook_result": hook_result},
                "metadata": {"methods_executed": [log["method"] for log in self.execution_log]},
                "execution_metrics": {"methods_count": len(self.execution_log)},
            }

    method_executor = RecordingMethodExecutor()
    executor = DummyExecutor("D0-Q0", {}, method_executor)
    result = executor.execute({"foo": 1})

    assert result["raw_evidence"]["hook_result"]["ok"] is True
    # Se combinan context y kwargs en la llamada
    assert method_executor.calls == [("_TestHook", "run", {"foo": 1, "marker": "seq"})]
    assert result["metadata"]["methods_executed"] == ["run"]
    assert result["execution_metrics"]["methods_count"] == 1
