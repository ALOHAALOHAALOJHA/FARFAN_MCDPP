"""Tests for Phase 2 executor profiler psutil initialization fixes.

Verifies:
1. psutil init path is reachable when psutil is available
2. ImportError path disables memory tracking and logs appropriately
3. _load_default_thresholds only returns thresholds (no side effects)
4. Public API is preserved

Contract Properties:
- Preconditions: memory_tracking flag controls psutil initialization
- Postconditions: _psutil_process set if psutil available, None if not
- Invariants: memory_tracking=False when psutil unavailable
"""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import directly to avoid syntax errors in other Phase_02 files
spec = importlib.util.spec_from_file_location(
    "executor_profiler",
    Path(__file__).resolve().parent.parent
    / "src"
    / "farfan_pipeline"
    / "phases"
    / "Phase_02"
    / "executor_profiler.py",
)
assert spec is not None and spec.loader is not None
executor_profiler_module = importlib.util.module_from_spec(spec)
sys.modules["executor_profiler"] = executor_profiler_module
spec.loader.exec_module(executor_profiler_module)

ExecutorProfiler = executor_profiler_module.ExecutorProfiler
ExecutorMetrics = executor_profiler_module.ExecutorMetrics
MethodCallMetrics = executor_profiler_module.MethodCallMetrics


class TestPsutilInitialization:
    """Test psutil initialization paths in ExecutorProfiler."""

    def test_psutil_init_reachable_when_available(self) -> None:
        """Test that psutil init path is reachable when psutil is available."""
        # Mock psutil module
        mock_psutil = MagicMock()
        mock_process = MagicMock()
        mock_psutil.Process.return_value = mock_process

        with patch.dict("sys.modules", {"psutil": mock_psutil}):
            profiler = ExecutorProfiler(memory_tracking=True)

            # Verify psutil was imported and initialized
            assert profiler.memory_tracking is True
            assert profiler._psutil is mock_psutil
            assert profiler._psutil_process is mock_process
            mock_psutil.Process.assert_called_once()

    def test_import_error_disables_memory_tracking(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that ImportError disables memory tracking and logs warning."""
        with caplog.at_level(logging.WARNING):
            # Simulate psutil not available by making import fail
            with patch("builtins.__import__", side_effect=ImportError("No module named 'psutil'")):
                profiler = ExecutorProfiler(memory_tracking=True)

                # Verify memory tracking was disabled
                assert profiler.memory_tracking is False
                assert profiler._psutil is None
                assert profiler._psutil_process is None

                # Verify warning was logged
                assert any("psutil not available" in record.message for record in caplog.records)

    def test_memory_tracking_disabled_by_flag(self) -> None:
        """Test that memory tracking can be disabled via constructor flag."""
        profiler = ExecutorProfiler(memory_tracking=False)

        assert profiler.memory_tracking is False
        assert profiler._psutil is None
        assert profiler._psutil_process is None

    def test_load_default_thresholds_pure_function(self) -> None:
        """Test that _load_default_thresholds only returns thresholds with no side effects."""
        profiler = ExecutorProfiler(memory_tracking=False)

        # Call multiple times to verify idempotence
        thresholds1 = profiler._load_default_thresholds()
        thresholds2 = profiler._load_default_thresholds()

        # Verify return value structure
        assert isinstance(thresholds1, dict)
        assert "execution_time_ms" in thresholds1
        assert "memory_mb" in thresholds1
        assert "serialization_ms" in thresholds1

        # Verify idempotence
        assert thresholds1 == thresholds2

        # Verify no side effects on profiler state
        assert profiler.memory_tracking is False
        assert profiler._psutil is None
        assert profiler._psutil_process is None

    def test_memory_usage_returns_zero_when_disabled(self) -> None:
        """Test that _get_memory_usage_mb returns 0.0 when memory tracking disabled."""
        profiler = ExecutorProfiler(memory_tracking=False)

        memory_usage = profiler._get_memory_usage_mb()

        assert memory_usage == 0.0

    def test_memory_usage_callable_when_enabled(self) -> None:
        """Test that _get_memory_usage_mb returns positive value when memory tracking enabled."""
        mock_psutil = MagicMock()
        mock_process = MagicMock()
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB in bytes
        mock_process.memory_info.return_value = mock_memory_info
        mock_psutil.Process.return_value = mock_process

        with patch.dict("sys.modules", {"psutil": mock_psutil}):
            profiler = ExecutorProfiler(memory_tracking=True)

            memory_usage = profiler._get_memory_usage_mb()

            # Verify memory usage is reported correctly (100 MB)
            assert memory_usage > 0
            assert abs(memory_usage - 100.0) < 0.1  # Allow small floating point error


class TestExecutorProfilerAPI:
    """Test that public API is preserved after refactoring."""

    def test_profile_executor_context_manager(self) -> None:
        """Test that profile_executor returns ProfilerContext."""
        profiler = ExecutorProfiler(memory_tracking=False)

        ctx = profiler.profile_executor("test_executor")

        assert ctx is not None
        assert hasattr(ctx, "__enter__")
        assert hasattr(ctx, "__exit__")

    def test_profiler_context_records_metrics(self) -> None:
        """Test that ProfilerContext records metrics correctly."""
        profiler = ExecutorProfiler(memory_tracking=False)

        with profiler.profile_executor("test_executor") as ctx:
            ctx.add_method_call("TestClass", "test_method", 10.5, 2.0)
            ctx.set_result({"test": "data"})

        # Verify metrics were recorded
        assert "test_executor" in profiler.metrics
        assert len(profiler.metrics["test_executor"]) == 1

        metrics = profiler.metrics["test_executor"][0]
        assert metrics.executor_id == "test_executor"
        assert metrics.success is True
        assert len(metrics.method_calls) == 1

    def test_generate_report_api(self) -> None:
        """Test that generate_report API is preserved."""
        profiler = ExecutorProfiler(memory_tracking=False)

        with profiler.profile_executor("test_executor"):
            pass

        report = profiler.generate_report()

        assert report is not None
        assert report.total_executors == 1
        assert hasattr(report, "to_dict")


class TestExecutorProfilerContract:
    """Test Design by Contract properties."""

    def test_postcondition_psutil_process_set_when_available(self) -> None:
        """Test postcondition: _psutil_process is non-None when psutil available and enabled."""
        mock_psutil = MagicMock()
        mock_process = MagicMock()
        mock_psutil.Process.return_value = mock_process

        with patch.dict("sys.modules", {"psutil": mock_psutil}):
            profiler = ExecutorProfiler(memory_tracking=True)

            # Postcondition: _psutil_process is set
            assert profiler._psutil_process is not None
            assert profiler._psutil_process is mock_process

    def test_postcondition_memory_tracking_false_on_import_error(self) -> None:
        """Test postcondition: memory_tracking=False when psutil import fails."""
        with patch("builtins.__import__", side_effect=ImportError("No psutil")):
            profiler = ExecutorProfiler(memory_tracking=True)

            # Postcondition: memory_tracking is False
            assert profiler.memory_tracking is False

    def test_invariant_memory_usage_positive_when_measurable(self) -> None:
        """Test invariant: memory usage is positive when actually measurable."""
        mock_psutil = MagicMock()
        mock_process = MagicMock()
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 50 * 1024 * 1024  # 50 MB
        mock_process.memory_info.return_value = mock_memory_info
        mock_psutil.Process.return_value = mock_process

        with patch.dict("sys.modules", {"psutil": mock_psutil}):
            profiler = ExecutorProfiler(memory_tracking=True)

            memory_usage = profiler._get_memory_usage_mb()

            # Invariant: memory usage is positive under measurable allocation
            assert memory_usage > 0
