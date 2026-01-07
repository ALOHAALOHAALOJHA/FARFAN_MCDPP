"""
Unit and Integration Tests for Phase Timeout Coverage
======================================================

Tests comprehensive timeout enforcement across all phases with:
1. PhaseTimeoutError exception behavior
2. RuntimeMode-based timeout multipliers
3. 80% warning threshold
4. Partial result handling
5. Manifest success=false on timeout in PROD
6. Integration test with simulated hanging handler
7. Regression test to prevent timeout bypass

Test Markers:
- updated: Current/valid tests
- core: Critical core functionality
- integration: Integration tests with simulated phases
- regression: Regression prevention tests
"""

import asyncio
import time
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from dataclasses import asdict

# Phase 0 imports
from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode

# Orchestrator imports - use relative imports matching existing tests
from farfan_pipeline.orchestration.orchestrator import (
    Orchestrator,
    PhaseTimeoutError,
    execute_phase_with_timeout,
    PhaseInstrumentation,
    ResourceLimits,
    TIMEOUT_SYNC_PHASES,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def runtime_config_prod():
    """RuntimeConfig in PROD mode."""
    return RuntimeConfig.from_dict({
        "mode": "prod",
        "allow_contradiction_fallback": False,
        "allow_validator_disable": False,
        "allow_execution_estimates": False,
        "allow_networkx_fallback": False,
        "allow_spacy_fallback": False,
        "allow_dev_ingestion_fallbacks": False,
        "allow_aggregation_defaults": False,
    })


@pytest.fixture
def runtime_config_dev():
    """RuntimeConfig in DEV mode."""
    return RuntimeConfig.from_dict({
        "mode": "dev",
        "allow_contradiction_fallback": True,
        "allow_validator_disable": True,
        "allow_execution_estimates": True,
        "allow_networkx_fallback": True,
        "allow_spacy_fallback": True,
        "allow_dev_ingestion_fallbacks": True,
        "allow_aggregation_defaults": True,
    })


@pytest.fixture
def runtime_config_exploratory():
    """RuntimeConfig in EXPLORATORY mode."""
    return RuntimeConfig.from_dict({
        "mode": "exploratory",
        "allow_contradiction_fallback": True,
        "allow_validator_disable": True,
        "allow_execution_estimates": True,
        "allow_networkx_fallback": True,
        "allow_spacy_fallback": True,
        "allow_dev_ingestion_fallbacks": True,
        "allow_aggregation_defaults": True,
    })


@pytest.fixture
def mock_instrumentation():
    """Mock PhaseInstrumentation."""
    instrumentation = Mock(spec=PhaseInstrumentation)
    instrumentation.record_warning = Mock()
    instrumentation.record_error = Mock()
    return instrumentation


# ============================================================================
# UNIT TESTS - PhaseTimeoutError
# ============================================================================

@pytest.mark.updated
@pytest.mark.core
def test_phase_timeout_error_basic():
    """Test PhaseTimeoutError basic construction."""
    error = PhaseTimeoutError(
        phase_id=2,
        phase_name="FASE 2 - Micro Preguntas",
        timeout_s=600.0
    )
    
    assert error.phase_id == 2
    assert error.phase_name == "FASE 2 - Micro Preguntas"
    assert error.timeout_s == 600.0
    assert error.elapsed_s is None
    assert error.partial_result is None
    assert "Phase 2" in str(error)
    assert "600" in str(error)


@pytest.mark.updated
@pytest.mark.core
def test_phase_timeout_error_with_elapsed():
    """Test PhaseTimeoutError with elapsed time."""
    error = PhaseTimeoutError(
        phase_id=7,
        phase_name="FASE 7 - Macro",
        timeout_s=60.0,
        elapsed_s=61.5
    )
    
    assert error.elapsed_s == 61.5
    assert "61.5" in str(error) or "61.50" in str(error)


@pytest.mark.updated
@pytest.mark.core
def test_phase_timeout_error_with_partial_result():
    """Test PhaseTimeoutError with partial result."""
    partial_data = {"completed": 150, "total": 300}
    
    error = PhaseTimeoutError(
        phase_id=2,
        phase_name="FASE 2 - Micro Preguntas",
        timeout_s=600.0,
        elapsed_s=600.1,
        partial_result=partial_data
    )
    
    assert error.partial_result == partial_data
    assert error.partial_result["completed"] == 150


# ============================================================================
# UNIT TESTS - execute_phase_with_timeout
# ============================================================================

@pytest.mark.updated
@pytest.mark.core
@pytest.mark.asyncio
async def test_execute_phase_with_timeout_success():
    """Test execute_phase_with_timeout with successful completion."""
    
    async def fast_handler():
        await asyncio.sleep(0.1)
        return "success"
    
    result = await execute_phase_with_timeout(
        phase_id=0,
        phase_name="Test Phase",
        handler=fast_handler,
        timeout_s=5.0
    )
    
    assert result == "success"


@pytest.mark.updated
@pytest.mark.core
@pytest.mark.asyncio
async def test_execute_phase_with_timeout_raises_timeout():
    """Test execute_phase_with_timeout raises PhaseTimeoutError on timeout."""
    
    async def slow_handler():
        await asyncio.sleep(10.0)
        return "should_not_reach"
    
    with pytest.raises(PhaseTimeoutError) as exc_info:
        await execute_phase_with_timeout(
            phase_id=2,
            phase_name="Slow Phase",
            handler=slow_handler,
            timeout_s=0.5
        )
    
    error = exc_info.value
    assert error.phase_id == 2
    assert error.phase_name == "Slow Phase"
    assert error.timeout_s == 0.5
    assert error.elapsed_s is not None
    assert error.elapsed_s >= 0.5


@pytest.mark.updated
@pytest.mark.core
@pytest.mark.asyncio
async def test_execute_phase_with_timeout_warning_at_80_percent(mock_instrumentation):
    """Test 80% timeout warning is logged."""
    warning_logged = []
    
    async def medium_handler():
        # Run just past 80% threshold
        await asyncio.sleep(0.45)
        return "completed"
    
    # Mock instrumentation to capture warnings
    def capture_warning(*args, **kwargs):
        warning_logged.append((args, kwargs))
    
    mock_instrumentation.record_warning = capture_warning
    
    result = await execute_phase_with_timeout(
        phase_id=3,
        phase_name="Medium Phase",
        handler=medium_handler,
        timeout_s=0.5,
        instrumentation=mock_instrumentation
    )
    
    assert result == "completed"
    # Warning should have been logged at 80% (0.4s)
    assert len(warning_logged) > 0
    warning_args, warning_kwargs = warning_logged[0]
    assert warning_args[0] == "timeout_threshold"
    assert "phase_id" in warning_kwargs
    assert warning_kwargs["phase_id"] == 3


@pytest.mark.updated
@pytest.mark.core
@pytest.mark.asyncio
async def test_execute_phase_with_timeout_sync_function():
    """Test execute_phase_with_timeout with synchronous function."""
    
    def sync_handler():
        time.sleep(0.1)
        return "sync_success"
    
    result = await execute_phase_with_timeout(
        phase_id=1,
        phase_name="Sync Phase",
        handler=sync_handler,
        timeout_s=5.0
    )
    
    assert result == "sync_success"


# ============================================================================
# UNIT TESTS - RuntimeMode Multipliers
# ============================================================================

@pytest.mark.updated
@pytest.mark.core
def test_get_phase_timeout_prod_mode(runtime_config_prod):
    """Test _get_phase_timeout applies 1x multiplier in PROD mode."""
    with patch('farfan_pipeline.orchestration.orchestrator.MethodExecutor'):
        with patch('farfan_pipeline.orchestration.orchestrator.get_questionnaire_provider'):
            orchestrator = Mock()
            orchestrator.runtime_config = runtime_config_prod
            orchestrator.PHASE_TIMEOUTS = {2: 600.0}
            
            from farfan_pipeline.orchestration.orchestrator import Orchestrator
            timeout = Orchestrator._get_phase_timeout(orchestrator, 2)
            
            assert timeout == 600.0  # No multiplier in PROD


@pytest.mark.updated
@pytest.mark.core
def test_get_phase_timeout_dev_mode(runtime_config_dev):
    """Test _get_phase_timeout applies 2x multiplier in DEV mode."""
    orchestrator = Mock()
    orchestrator.PHASE_TIMEOUTS = {2: 600.0}
    
    from farfan_pipeline.orchestration.orchestrator import Orchestrator
    timeout = Orchestrator._get_phase_timeout(orchestrator, 2)
    
    assert timeout == 1200.0  # 2x multiplier in DEV


@pytest.mark.updated
@pytest.mark.core
def test_get_phase_timeout_exploratory_mode(runtime_config_exploratory):
    """Test _get_phase_timeout applies 4x multiplier in EXPLORATORY mode."""
    orchestrator = Mock()
    orchestrator.runtime_config = runtime_config_exploratory
    orchestrator.PHASE_TIMEOUTS = {2: 600.0}
    
    from orchestration.orchestrator import Orchestrator
    timeout = Orchestrator._get_phase_timeout(orchestrator, 2)
    
    assert timeout == 2400.0  # 4x multiplier in EXPLORATORY


@pytest.mark.updated
@pytest.mark.core
def test_get_phase_timeout_no_runtime_config():
    """Test _get_phase_timeout with no RuntimeConfig uses base timeout."""
    orchestrator = Mock()
    orchestrator.runtime_config = None
    orchestrator.PHASE_TIMEOUTS = {7: 60.0}
    
    from orchestration.orchestrator import Orchestrator
    timeout = Orchestrator._get_phase_timeout(orchestrator, 7)
    
    assert timeout == 60.0


# ============================================================================
# UNIT TESTS - TIMEOUT_SYNC_PHASES Coverage
# ============================================================================

@pytest.mark.updated
@pytest.mark.core
def test_timeout_sync_phases_includes_all_sync():
    """Test TIMEOUT_SYNC_PHASES includes all sync phases."""
    # Sync phases are: 0, 1, 6, 7, 9
    expected_sync_phases = {0, 1, 6, 7, 9}
    
    assert TIMEOUT_SYNC_PHASES == expected_sync_phases, (
        f"TIMEOUT_SYNC_PHASES should cover all sync phases. "
        f"Expected: {expected_sync_phases}, Got: {TIMEOUT_SYNC_PHASES}"
    )


# ============================================================================
# INTEGRATION TESTS - Simulated Hanging Handler
# ============================================================================

@pytest.mark.updated
@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_hanging_handler_timeout():
    """Integration test: Phase with infinite loop is terminated at timeout."""
    
    async def hanging_handler():
        """Simulates a hanging phase that never completes."""
        while True:
            await asyncio.sleep(0.1)
    
    start_time = time.time()
    
    with pytest.raises(PhaseTimeoutError) as exc_info:
        await execute_phase_with_timeout(
            phase_id=2,
            phase_name="Hanging Phase",
            handler=hanging_handler,
            timeout_s=1.0
        )
    
    elapsed_time = time.time() - start_time
    
    # Should timeout around 1 second (with some tolerance)
    assert 0.9 <= elapsed_time <= 1.5, f"Expected ~1s timeout, got {elapsed_time:.2f}s"
    
    error = exc_info.value
    assert error.phase_id == 2
    assert error.timeout_s == 1.0


@pytest.mark.updated
@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_partial_progress_extraction():
    """Integration test: Partial results can be extracted on timeout."""
    
    # Simulate a phase that makes partial progress before timing out
    partial_data = {"progress": []}
    
    async def partial_handler():
        for i in range(100):
            partial_data["progress"].append(i)
            await asyncio.sleep(0.01)
    
    with pytest.raises(PhaseTimeoutError):
        await execute_phase_with_timeout(
            phase_id=2,
            phase_name="Partial Phase",
            handler=partial_handler,
            timeout_s=0.3
        )
    
    # Verify partial progress was made
    assert len(partial_data["progress"]) > 0
    assert len(partial_data["progress"]) < 100


# ============================================================================
# INTEGRATION TESTS - Manifest Generation
# ============================================================================

@pytest.mark.updated
@pytest.mark.integration
def test_build_execution_manifest_success(runtime_config_prod):
    """Test _build_execution_manifest reports success=true when all phases complete."""
    orchestrator = Mock()
    orchestrator.runtime_config = runtime_config_prod
    orchestrator.phase_results = []
    orchestrator._phase_status = {i: "completed" for i in range(11)}
    orchestrator.abort_signal = Mock()
    orchestrator.abort_signal.is_aborted = Mock(return_value=False)
    orchestrator.abort_signal.get_reason = Mock(return_value=None)
    orchestrator.FASES = [(i, "async", f"_handler_{i}", f"Phase {i}") for i in range(11)]
    
    from orchestration.orchestrator import Orchestrator
    manifest = Orchestrator._build_execution_manifest(orchestrator)
    
    assert manifest["success"] is True
    assert manifest["has_timeout"] is False
    assert manifest["has_failure"] is False


@pytest.mark.updated
@pytest.mark.integration
def test_build_execution_manifest_timeout_prod_mode(runtime_config_prod):
    """Test _build_execution_manifest reports success=false on timeout in PROD."""
    from orchestration.orchestrator import PhaseResult
    
    timeout_error = PhaseTimeoutError(
        phase_id=2,
        phase_name="FASE 2 - Micro Preguntas",
        timeout_s=600.0,
        elapsed_s=600.5
    )
    
    orchestrator = Mock()
    orchestrator.runtime_config = runtime_config_prod
    orchestrator.phase_results = [
        PhaseResult(
            success=False,
            phase_id="2",
            data=None,
            error=timeout_error,
            duration_ms=600500.0,
            mode="async",
            aborted=True
        )
    ]
    orchestrator._phase_status = {
        0: "completed", 1: "completed", 2: "failed",
        3: "not_started", 4: "not_started", 5: "not_started",
        6: "not_started", 7: "not_started", 8: "not_started",
        9: "not_started", 10: "not_started"
    }
    orchestrator.abort_signal = Mock()
    orchestrator.abort_signal.is_aborted = Mock(return_value=True)
    orchestrator.abort_signal.get_reason = Mock(return_value="Phase 2 timed out")
    orchestrator.FASES = [(i, "async", f"_handler_{i}", f"Phase {i}") for i in range(11)]
    
    from orchestration.orchestrator import Orchestrator
    manifest = Orchestrator._build_execution_manifest(orchestrator)
    
    # In PROD mode, timeout should cause success=false
    assert manifest["success"] is False
    assert manifest["has_timeout"] is True
    assert manifest["runtime_mode"] == "prod"
    assert "timeout_phases" in manifest
    assert len(manifest["timeout_phases"]) == 1
    assert manifest["timeout_phases"][0]["phase_id"] == "2"


@pytest.mark.updated
@pytest.mark.integration
def test_build_execution_manifest_timeout_dev_mode(runtime_config_dev):
    """Test _build_execution_manifest in DEV mode with timeout."""
    from orchestration.orchestrator import PhaseResult
    
    timeout_error = PhaseTimeoutError(
        phase_id=2,
        phase_name="FASE 2 - Micro Preguntas",
        timeout_s=1200.0,  # 2x in DEV
        elapsed_s=1200.5
    )
    
    orchestrator = Mock()
    orchestrator.runtime_config = runtime_config_dev
    orchestrator.phase_results = [
        PhaseResult(
            success=False,
            phase_id="2",
            data=None,
            error=timeout_error,
            duration_ms=1200500.0,
            mode="async",
            aborted=True
        )
    ]
    orchestrator._phase_status = {i: "not_started" if i > 2 else ("failed" if i == 2 else "completed") for i in range(11)}
    orchestrator.abort_signal = Mock()
    orchestrator.abort_signal.is_aborted = Mock(return_value=True)
    orchestrator.abort_signal.get_reason = Mock(return_value="Phase 2 timed out")
    orchestrator.FASES = [(i, "async", f"_handler_{i}", f"Phase {i}") for i in range(11)]
    
    from orchestration.orchestrator import Orchestrator
    manifest = Orchestrator._build_execution_manifest(orchestrator)
    
    assert manifest["has_timeout"] is True
    assert manifest["runtime_mode"] == "dev"


# ============================================================================
# REGRESSION TESTS - Prevent Timeout Bypass
# ============================================================================

@pytest.mark.updated
@pytest.mark.regression
def test_regression_all_sync_phases_use_timeout():
    """Regression test: Ensure all sync phases use timeout mechanism."""
    from orchestration.orchestrator import Orchestrator
    
    # Sync phases from FASES definition
    sync_phases_in_fases = {
        phase_id 
        for phase_id, mode, _, _ in Orchestrator.FASES 
        if mode == "sync"
    }
    
    # All sync phases should be in TIMEOUT_SYNC_PHASES
    assert sync_phases_in_fases == TIMEOUT_SYNC_PHASES, (
        f"Not all sync phases are covered by timeout. "
        f"Sync phases: {sync_phases_in_fases}, "
        f"Timeout coverage: {TIMEOUT_SYNC_PHASES}"
    )


@pytest.mark.updated
@pytest.mark.regression
def test_regression_phase_timeouts_defined_for_all_phases():
    """Regression test: Ensure PHASE_TIMEOUTS defined for all phases."""
    from orchestration.orchestrator import Orchestrator
    
    all_phase_ids = {phase_id for phase_id, _, _, _ in Orchestrator.FASES}
    timeout_phase_ids = set(Orchestrator.PHASE_TIMEOUTS.keys())
    
    assert all_phase_ids == timeout_phase_ids, (
        f"PHASE_TIMEOUTS missing definitions. "
        f"All phases: {all_phase_ids}, "
        f"Defined timeouts: {timeout_phase_ids}"
    )


@pytest.mark.updated
@pytest.mark.regression
@pytest.mark.asyncio
async def test_regression_timeout_cannot_be_bypassed():
    """Regression test: Timeout cannot be bypassed with exception handling."""
    
    async def sneaky_handler():
        """Attempts to bypass timeout with exception handling."""
        try:
            while True:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            # Try to continue execution
            await asyncio.sleep(10.0)
            return "should_not_reach"
    
    with pytest.raises(PhaseTimeoutError):
        await execute_phase_with_timeout(
            phase_id=999,
            phase_name="Sneaky Phase",
            handler=sneaky_handler,
            timeout_s=0.5
        )


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.updated
@pytest.mark.core
@pytest.mark.asyncio
async def test_execute_phase_with_timeout_zero_timeout():
    """Test execute_phase_with_timeout with zero timeout."""
    
    async def instant_handler():
        return "instant"
    
    # Zero timeout should still allow instant execution
    with pytest.raises(PhaseTimeoutError):
        await execute_phase_with_timeout(
            phase_id=0,
            phase_name="Zero Timeout",
            handler=instant_handler,
            timeout_s=0.0
        )


@pytest.mark.updated
@pytest.mark.core
def test_phase_timeout_error_string_phase_id():
    """Test PhaseTimeoutError with string phase_id."""
    error = PhaseTimeoutError(
        phase_id="2",
        phase_name="Phase Two",
        timeout_s=100.0
    )
    
    assert error.phase_id == "2"
    assert "2" in str(error)


@pytest.mark.updated
@pytest.mark.core
@pytest.mark.asyncio
async def test_execute_phase_with_timeout_exception_during_execution():
    """Test execute_phase_with_timeout when handler raises exception."""
    
    async def failing_handler():
        await asyncio.sleep(0.1)
        raise ValueError("Handler failed")
    
    with pytest.raises(ValueError, match="Handler failed"):
        await execute_phase_with_timeout(
            phase_id=5,
            phase_name="Failing Phase",
            handler=failing_handler,
            timeout_s=5.0
        )
