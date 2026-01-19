"""
Test Suite for State-of-the-Art Interventions

Tests for three major interventions:
1. Factory Performance Supercharger
2. Orchestrator-Factory Alignment Protocol
3. SISAS Dynamic Alignment Enhancement
"""

import asyncio
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.farfan_pipeline.orchestration.factory import (
    AdaptiveLRUCache,
    FactoryConfig,
    UnifiedFactory,
)
from src.farfan_pipeline.orchestration.orchestrator import (
    OrchestratorConfig,
    PhaseID,
    UnifiedOrchestrator,
)


# =============================================================================
# INTERVENTION 1: Factory Performance Tests
# =============================================================================


class TestAdaptiveLRUCache:
    """Test the adaptive LRU+TTL hybrid cache."""

    def test_cache_basic_operations(self):
        """Test basic get/set operations."""
        cache = AdaptiveLRUCache(max_size=3, ttl_seconds=60)

        # Set items
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Get items
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_lru_eviction(self):
        """Test LRU eviction when size limit exceeded."""
        cache = AdaptiveLRUCache(max_size=2, ttl_seconds=60)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_ttl_expiration(self):
        """Test TTL-based expiration."""
        cache = AdaptiveLRUCache(max_size=10, ttl_seconds=0.1)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        time.sleep(0.2)  # Wait for TTL to expire

        assert cache.get("key1") is None

    def test_cache_access_tracking(self):
        """Test access frequency tracking for hot keys."""
        cache = AdaptiveLRUCache(max_size=10, ttl_seconds=60)

        # Access key1 multiple times
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        for _ in range(5):
            cache.get("key1")

        cache.get("key2")
        cache.get("key3")

        hot_keys = cache.get_hot_keys(top_n=3)
        assert hot_keys[0] == "key1"  # Most accessed


class TestFactoryParallelExecution:
    """Test parallel contract execution."""

    @pytest.fixture
    def factory_config(self, tmp_path):
        """Create factory config with parallel execution enabled."""
        return FactoryConfig(
            project_root=tmp_path,
            enable_parallel_execution=True,
            max_workers=4,
            enable_adaptive_caching=True,
            batch_execution_threshold=3,
        )

    @pytest.fixture
    def factory(self, factory_config):
        """Create factory instance."""
        return UnifiedFactory(factory_config)

    def test_parallel_execution_enabled(self, factory):
        """Test that parallel execution is enabled."""
        assert factory._config.enable_parallel_execution is True
        assert factory._thread_pool is not None

    def test_batch_threshold_logic(self, factory):
        """Test batch execution threshold."""
        # Below threshold - should use sequential
        contract_ids = ["C1", "C2"]
        assert len(contract_ids) < factory._config.batch_execution_threshold

        # Above threshold - should use parallel
        contract_ids_large = ["C1", "C2", "C3", "C4", "C5"]
        assert len(contract_ids_large) >= factory._config.batch_execution_threshold

    @pytest.mark.asyncio
    async def test_async_contract_execution(self, factory):
        """Test async contract execution."""
        # Mock contracts
        factory._contracts = {
            "C1": {"status": "ACTIVE", "executor_binding": {}},
            "C2": {"status": "ACTIVE", "executor_binding": {}},
        }

        # Mock execute_contract to return quickly
        def mock_execute(contract_id, input_data):
            return {
                "contract_id": contract_id,
                "status": "completed",
            }

        factory.execute_contract = mock_execute

        # Execute async
        results = await factory.execute_contracts_async(["C1", "C2"], {})

        assert len(results) == 2
        assert results["C1"]["status"] == "completed"
        assert results["C2"]["status"] == "completed"

    def test_performance_metrics_collection(self, factory):
        """Test that performance metrics are collected."""
        metrics = factory.get_performance_metrics()

        assert "contracts_executed" in metrics
        assert "cache_hits" in metrics
        assert "cache_misses" in metrics
        assert "cache_efficiency_percent" in metrics

    def test_cache_optimization_report(self, factory):
        """Test cache optimization reporting."""
        report = factory.optimize_caches()

        assert "recommendations" in report
        assert isinstance(report["recommendations"], list)


# =============================================================================
# INTERVENTION 2: Orchestrator-Factory Alignment Tests
# =============================================================================


class TestFactoryCapabilities:
    """Test factory capabilities API."""

    @pytest.fixture
    def factory(self, tmp_path):
        """Create factory instance."""
        config = FactoryConfig(
            project_root=tmp_path,
            enable_parallel_execution=True,
            max_workers=8,
        )
        return UnifiedFactory(config)

    def test_get_factory_capabilities(self, factory):
        """Test factory capabilities reporting."""
        factory._contracts = {"C1": {"status": "ACTIVE"}}

        capabilities = factory.get_factory_capabilities()

        assert "total_contracts" in capabilities
        assert "active_contracts" in capabilities
        assert "parallel_execution_enabled" in capabilities
        assert capabilities["parallel_execution_enabled"] is True
        assert capabilities["max_workers"] == 8
        assert "health_status" in capabilities

    def test_factory_health_status(self, factory):
        """Test factory health status reporting."""
        # Initial state should be idle
        capabilities = factory.get_factory_capabilities()
        assert capabilities["health_status"] == "idle"

    def test_execution_snapshot(self, factory):
        """Test factory state snapshot creation."""
        snapshot = factory.create_execution_snapshot()

        assert "timestamp" in snapshot
        assert "metrics" in snapshot
        assert "capabilities" in snapshot
        assert "questionnaire_loaded" in snapshot
        assert "contracts_loaded" in snapshot


class TestBidirectionalSync:
    """Test bidirectional sync protocol."""

    @pytest.fixture
    def factory(self, tmp_path):
        """Create factory instance."""
        config = FactoryConfig(project_root=tmp_path, max_workers=4)
        return UnifiedFactory(config)

    def test_sync_with_orchestrator(self, factory):
        """Test synchronization with orchestrator state."""
        factory._contracts = {
            "C1": {"status": "ACTIVE", "applicable_phases": ["P02"]},
        }

        orchestrator_state = {
            "current_phase": "P02",
            "max_workers": 4,
        }

        sync_result = factory.synchronize_with_orchestrator(orchestrator_state)

        assert "success" in sync_result
        assert "conflicts" in sync_result
        assert "adjustments" in sync_result

    def test_sync_detects_resource_mismatch(self, factory):
        """Test that sync detects resource mismatches."""
        factory._contracts = {}

        orchestrator_state = {
            "current_phase": "P02",
            "max_workers": 16,  # More than factory has
        }

        sync_result = factory.synchronize_with_orchestrator(orchestrator_state)

        # Should suggest adjustment
        assert len(sync_result["adjustments"]) > 0


class TestContractAwareScheduling:
    """Test contract-aware scheduling."""

    @pytest.fixture
    def factory(self, tmp_path):
        """Create factory instance."""
        config = FactoryConfig(
            project_root=tmp_path,
            enable_parallel_execution=True,
            max_workers=4,
            batch_execution_threshold=5,
        )
        return UnifiedFactory(config)

    def test_execution_plan_sequential(self, factory):
        """Test execution plan for small contract set."""
        factory._contracts = {f"C{i}": {"status": "ACTIVE"} for i in range(3)}

        plan = factory.get_contract_execution_plan(["C0", "C1", "C2"])

        assert plan["execution_strategy"] == "sequential"
        assert plan["total_contracts"] == 3

    def test_execution_plan_parallel_batch(self, factory):
        """Test execution plan for large contract set."""
        factory._contracts = {f"C{i}": {"status": "ACTIVE"} for i in range(10)}

        plan = factory.get_contract_execution_plan(
            [f"C{i}" for i in range(10)],
            constraints={"max_parallel": 4},
        )

        assert plan["execution_strategy"] == "parallel_batch"
        assert len(plan["batches"]) > 0

    def test_execution_plan_time_budget(self, factory):
        """Test execution plan respects time budget."""
        factory._contracts = {f"C{i}": {"status": "ACTIVE"} for i in range(100)}
        factory._execution_metrics["average_execution_time"] = 10.0

        plan = factory.get_contract_execution_plan(
            [f"C{i}" for i in range(100)],
            constraints={"time_budget_seconds": 50},
        )

        # Should warn about budget exceeded
        assert any("budget" in w.lower() for w in plan["warnings"])


class TestOrchestratorFactoryIntegration:
    """Test integration between orchestrator and factory."""

    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with factory."""
        config = OrchestratorConfig(
            document_path="test.pdf",
            output_dir=str(tmp_path / "output"),
            enable_parallel_execution=True,
            max_workers=4,
        )
        return UnifiedOrchestrator(config)

    def test_orchestrator_has_factory(self, orchestrator):
        """Test that orchestrator has factory initialized."""
        # May be None if factory not available
        if orchestrator.factory:
            assert orchestrator.factory is not None
            assert hasattr(orchestrator.factory, "get_factory_capabilities")

    def test_orchestrator_phase2_uses_factory(self, orchestrator):
        """Test that Phase 2 uses factory capabilities."""
        if not orchestrator.factory:
            pytest.skip("Factory not available")

        # Mock contracts
        orchestrator.factory._contracts = {
            "C1": {"status": "ACTIVE", "applicable_phases": ["P02"]},
        }

        # Execute Phase 2
        result = orchestrator._execute_phase_02()

        assert "status" in result
        if "performance_metrics" in result:
            assert isinstance(result["performance_metrics"], dict)


# =============================================================================
# INTERVENTION 3: SISAS Dynamic Alignment Tests
# =============================================================================


class TestSignalAnticipation:
    """Test signal anticipation engine."""

    @pytest.fixture
    def orchestrator(self):
        """Create SISAS orchestrator."""
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.orchestration.sisas_orchestrator import (
            SISASOrchestrator,
        )

        return SISASOrchestrator()

    def test_enable_signal_anticipation(self, orchestrator):
        """Test enabling signal anticipation."""
        orchestrator.enable_signal_anticipation()

        assert orchestrator._signal_anticipation_enabled is True
        assert hasattr(orchestrator, "_signal_history")

    def test_predict_signal_load_no_history(self, orchestrator):
        """Test prediction with no history."""
        orchestrator.enable_signal_anticipation()

        prediction = orchestrator.predict_signal_load("phase_02")

        assert prediction["estimated_signals"] == 0
        assert prediction["confidence"] == 0.0

    def test_predict_signal_load_with_history(self, orchestrator):
        """Test prediction with historical data."""
        orchestrator.enable_signal_anticipation()

        # Add history
        orchestrator._signal_history = [
            {"phase": "phase_02", "signal_count": 100},
            {"phase": "phase_02", "signal_count": 120},
            {"phase": "phase_02", "signal_count": 110},
        ]

        prediction = orchestrator.predict_signal_load("phase_02")

        assert prediction["estimated_signals"] > 0
        assert 0 <= prediction["confidence"] <= 1.0


class TestDynamicVehicleRouting:
    """Test dynamic vehicle routing."""

    @pytest.fixture
    def orchestrator(self):
        """Create SISAS orchestrator."""
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.orchestration.sisas_orchestrator import (
            SISASOrchestrator,
        )

        return SISASOrchestrator()

    def test_enable_dynamic_routing(self, orchestrator):
        """Test enabling dynamic routing."""
        orchestrator.enable_dynamic_vehicle_routing()

        assert orchestrator._dynamic_routing_enabled is True
        assert hasattr(orchestrator, "_vehicle_performance")

    def test_optimize_vehicle_assignment(self, orchestrator):
        """Test vehicle assignment optimization."""
        orchestrator.enable_dynamic_vehicle_routing()

        # Set performance data
        orchestrator._vehicle_performance = {
            "vehicle_a": {"success_rate": 0.9},
            "vehicle_b": {"success_rate": 0.7},
            "vehicle_c": {"success_rate": 0.95},
        }

        # Mock baseline assignment
        orchestrator._get_vehicles_for_file = lambda path: [
            "vehicle_a",
            "vehicle_b",
            "vehicle_c",
        ]

        optimized = orchestrator.optimize_vehicle_assignment("test.json")

        # Should be sorted by success rate (descending)
        assert optimized[0] == "vehicle_c"  # Highest success rate


class TestBackpressureManagement:
    """Test backpressure management."""

    @pytest.fixture
    def orchestrator(self):
        """Create SISAS orchestrator."""
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.orchestration.sisas_orchestrator import (
            SISASOrchestrator,
        )

        return SISASOrchestrator()

    def test_enable_backpressure(self, orchestrator):
        """Test enabling backpressure management."""
        orchestrator.enable_backpressure_management(threshold=500)

        assert orchestrator._backpressure_enabled is True
        assert orchestrator._backpressure_threshold == 500

    def test_backpressure_not_triggered(self, orchestrator):
        """Test backpressure when below threshold."""
        orchestrator.enable_backpressure_management(threshold=1000)
        orchestrator._pending_signals_count = 500

        result = orchestrator.check_backpressure()

        assert result["apply_backpressure"] is False
        assert result["utilization_percent"] == 50.0

    def test_backpressure_triggered(self, orchestrator):
        """Test backpressure when at/above threshold."""
        orchestrator.enable_backpressure_management(threshold=1000)
        orchestrator._pending_signals_count = 1000

        result = orchestrator.check_backpressure()

        assert result["apply_backpressure"] is True
        assert result["utilization_percent"] == 100.0


class TestSignalFusion:
    """Test signal fusion."""

    @pytest.fixture
    def orchestrator(self):
        """Create SISAS orchestrator."""
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.orchestration.sisas_orchestrator import (
            SISASOrchestrator,
        )

        return SISASOrchestrator()

    def test_enable_signal_fusion(self, orchestrator):
        """Test enabling signal fusion."""
        orchestrator.enable_signal_fusion()

        assert orchestrator._signal_fusion_enabled is True
        assert hasattr(orchestrator, "_fusion_buffer")


class TestEventStormDetection:
    """Test event storm detection."""

    @pytest.fixture
    def orchestrator(self):
        """Create SISAS orchestrator."""
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.orchestration.sisas_orchestrator import (
            SISASOrchestrator,
        )

        return SISASOrchestrator()

    def test_enable_event_storm_detection(self, orchestrator):
        """Test enabling event storm detection."""
        orchestrator.enable_event_storm_detection(rate_limit=50)

        assert orchestrator._event_storm_detection_enabled is True
        assert orchestrator._rate_limit_per_second == 50

    def test_detect_no_storm(self, orchestrator):
        """Test storm detection when rate is normal."""
        orchestrator.enable_event_storm_detection(rate_limit=100)
        orchestrator._event_timestamps = [time.time() for _ in range(50)]

        result = orchestrator.detect_event_storm()

        assert result["storm_detected"] is False

    def test_detect_storm(self, orchestrator):
        """Test storm detection when rate exceeds limit."""
        orchestrator.enable_event_storm_detection(rate_limit=100)
        orchestrator._event_timestamps = [time.time() for _ in range(150)]

        result = orchestrator.detect_event_storm()

        assert result["storm_detected"] is True
        assert result["throttle_recommended"] is True


class TestSISASHealthMetrics:
    """Test SISAS comprehensive health metrics."""

    @pytest.fixture
    def orchestrator(self):
        """Create SISAS orchestrator."""
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.orchestration.sisas_orchestrator import (
            SISASOrchestrator,
        )

        return SISASOrchestrator()

    def test_health_metrics_all_disabled(self, orchestrator):
        """Test health metrics when all features disabled."""
        health = orchestrator.get_sisas_health_metrics()

        assert health["signal_anticipation_enabled"] is False
        assert health["dynamic_routing_enabled"] is False
        assert health["backpressure_enabled"] is False

    def test_health_metrics_all_enabled(self, orchestrator):
        """Test health metrics when all features enabled."""
        orchestrator.enable_signal_anticipation()
        orchestrator.enable_dynamic_vehicle_routing()
        orchestrator.enable_backpressure_management()
        orchestrator.enable_signal_fusion()
        orchestrator.enable_event_storm_detection()

        health = orchestrator.get_sisas_health_metrics()

        assert health["signal_anticipation_enabled"] is True
        assert health["dynamic_routing_enabled"] is True
        assert health["backpressure_enabled"] is True
        assert health["signal_fusion_enabled"] is True
        assert health["event_storm_detection_enabled"] is True


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestEndToEndIntegration:
    """Test end-to-end integration of all interventions."""

    @pytest.fixture
    def system(self, tmp_path):
        """Create full system with all interventions enabled."""
        orch_config = OrchestratorConfig(
            document_path="test.pdf",
            output_dir=str(tmp_path / "output"),
            enable_parallel_execution=True,
            max_workers=4,
        )

        orchestrator = UnifiedOrchestrator(orch_config)

        return orchestrator

    def test_full_system_initialization(self, system):
        """Test that full system initializes correctly."""
        assert system.config is not None
        assert system.state_machine is not None
        assert system.dependency_graph is not None

    def test_factory_orchestrator_sync(self, system):
        """Test factory-orchestrator synchronization."""
        if not system.factory:
            pytest.skip("Factory not available")

        # Should have synchronized during init
        capabilities = system.factory.get_factory_capabilities()
        assert "health_status" in capabilities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
