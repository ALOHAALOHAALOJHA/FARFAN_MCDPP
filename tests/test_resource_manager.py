"""Tests for adaptive resource management system."""

import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from farfan_pipeline.core.orchestrator.core import ResourceLimits
from farfan_pipeline.core.orchestrator.resource_manager import (
    AdaptiveResourceManager,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    DegradationStrategy,
    ExecutorPriority,
    ResourceAllocationPolicy,
    ResourcePressureLevel,
)
from farfan_pipeline.core.orchestrator.resource_alerts import (
    AlertChannel,
    AlertSeverity,
    ResourceAlertManager,
)
from farfan_pipeline.core.orchestrator.resource_integration import (
    create_resource_manager,
    register_default_policies,
)


@pytest.fixture
def resource_limits():
    """Create ResourceLimits instance for testing."""
    return ResourceLimits(
        max_memory_mb=1024.0,
        max_cpu_percent=80.0,
        max_workers=8,
        min_workers=2,
        hard_max_workers=16,
    )


@pytest.fixture
def resource_manager(resource_limits):
    """Create AdaptiveResourceManager instance for testing."""
    return AdaptiveResourceManager(
        resource_limits=resource_limits,
        enable_circuit_breakers=True,
        enable_degradation=True,
    )


@pytest.fixture
def alert_manager():
    """Create ResourceAlertManager instance for testing."""
    return ResourceAlertManager(
        channels=[AlertChannel.LOG],
    )


class TestCircuitBreaker:
    """Tests for CircuitBreaker functionality."""
    
    def test_initial_state_closed(self):
        """Circuit breaker should start in closed state."""
        breaker = CircuitBreaker(executor_id="test-executor")
        assert breaker.state == CircuitState.CLOSED
        assert breaker.can_execute()
    
    def test_opens_after_threshold_failures(self):
        """Circuit breaker should open after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(executor_id="test-executor", config=config)
        
        breaker.record_failure()
        assert breaker.state == CircuitState.CLOSED
        
        breaker.record_failure()
        assert breaker.state == CircuitState.CLOSED
        
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        assert not breaker.can_execute()
    
    def test_opens_on_memory_threshold(self):
        """Circuit breaker should open on memory threshold."""
        config = CircuitBreakerConfig(
            failure_threshold=10, memory_threshold_mb=512.0
        )
        breaker = CircuitBreaker(executor_id="test-executor", config=config)
        
        breaker.record_failure(memory_mb=1024.0)
        assert breaker.state == CircuitState.OPEN
    
    def test_reset_on_success(self):
        """Failure count should reset on success."""
        breaker = CircuitBreaker(executor_id="test-executor")
        
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.failure_count == 2
        
        breaker.record_success()
        assert breaker.failure_count == 0
    
    def test_half_open_to_closed(self):
        """Circuit breaker should close after successes in half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=0.1,
        )
        breaker = CircuitBreaker(executor_id="test-executor", config=config)
        
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        
        import time
        time.sleep(0.2)
        
        assert breaker.can_execute()
        assert breaker.state == CircuitState.HALF_OPEN
        
        breaker.record_success()
        breaker.record_success()
        assert breaker.state == CircuitState.CLOSED


class TestDegradationStrategy:
    """Tests for DegradationStrategy functionality."""
    
    def test_should_apply_at_threshold(self):
        """Strategy should apply at or above threshold."""
        strategy = DegradationStrategy(
            name="test",
            pressure_threshold=ResourcePressureLevel.HIGH,
        )
        
        assert not strategy.should_apply(ResourcePressureLevel.NORMAL)
        assert not strategy.should_apply(ResourcePressureLevel.ELEVATED)
        assert strategy.should_apply(ResourcePressureLevel.HIGH)
        assert strategy.should_apply(ResourcePressureLevel.CRITICAL)
        assert strategy.should_apply(ResourcePressureLevel.EMERGENCY)
    
    def test_disabled_strategy_never_applies(self):
        """Disabled strategy should never apply."""
        strategy = DegradationStrategy(
            name="test",
            pressure_threshold=ResourcePressureLevel.NORMAL,
            enabled=False,
        )
        
        assert not strategy.should_apply(ResourcePressureLevel.EMERGENCY)


class TestAdaptiveResourceManager:
    """Tests for AdaptiveResourceManager functionality."""
    
    @pytest.mark.asyncio
    async def test_assess_pressure_normal(self, resource_manager):
        """Should assess normal pressure with low resource usage."""
        with patch.object(
            resource_manager.resource_limits,
            "get_resource_usage",
            return_value={
                "cpu_percent": 30.0,
                "memory_percent": 40.0,
                "rss_mb": 200.0,
                "worker_budget": 8.0,
            },
        ):
            pressure = await resource_manager.assess_resource_pressure()
            assert pressure == ResourcePressureLevel.NORMAL
    
    @pytest.mark.asyncio
    async def test_assess_pressure_elevated(self, resource_manager):
        """Should assess elevated pressure with moderate resource usage."""
        with patch.object(
            resource_manager.resource_limits,
            "get_resource_usage",
            return_value={
                "cpu_percent": 55.0,
                "memory_percent": 66.0,
                "rss_mb": 676.0,
                "worker_budget": 8.0,
            },
        ):
            pressure = await resource_manager.assess_resource_pressure()
            assert pressure == ResourcePressureLevel.ELEVATED
    
    @pytest.mark.asyncio
    async def test_assess_pressure_critical(self, resource_manager):
        """Should assess critical pressure with high resource usage."""
        with patch.object(
            resource_manager.resource_limits,
            "get_resource_usage",
            return_value={
                "cpu_percent": 75.0,
                "memory_percent": 88.0,
                "rss_mb": 900.0,
                "worker_budget": 8.0,
            },
        ):
            pressure = await resource_manager.assess_resource_pressure()
            assert pressure == ResourcePressureLevel.CRITICAL
    
    def test_can_execute_with_closed_breaker(self, resource_manager):
        """Should allow execution with closed circuit breaker."""
        can_exec, reason = resource_manager.can_execute("test-executor")
        assert can_exec
        assert reason == "OK"
    
    def test_can_execute_with_open_breaker(self, resource_manager):
        """Should block execution with open circuit breaker."""
        breaker = resource_manager.get_or_create_circuit_breaker("test-executor")
        breaker.state = CircuitState.OPEN
        breaker.last_state_change = datetime.utcnow()
        
        can_exec, reason = resource_manager.can_execute("test-executor")
        assert not can_exec
        assert "open" in reason.lower()
    
    def test_get_degradation_config_normal(self, resource_manager):
        """Should get normal config at normal pressure."""
        config = resource_manager.get_degradation_config("test-executor")
        
        assert config["entity_limit_factor"] == 1.0
        assert not config["disable_expensive_computations"]
        assert not config["use_simplified_methods"]
        assert len(config["applied_strategies"]) == 0
    
    def test_get_degradation_config_critical(self, resource_manager):
        """Should get degraded config at critical pressure."""
        resource_manager.current_pressure = ResourcePressureLevel.CRITICAL
        config = resource_manager.get_degradation_config("test-executor")
        
        assert config["entity_limit_factor"] < 1.0
        assert config["disable_expensive_computations"]
        assert config["use_simplified_methods"]
        assert len(config["applied_strategies"]) > 0
    
    @pytest.mark.asyncio
    async def test_allocate_resources_for_critical_executor(
        self, resource_manager
    ):
        """Should allocate more resources for critical executors."""
        allocation = await resource_manager.allocate_resources("D3-Q3")
        
        assert allocation["priority"] == ExecutorPriority.CRITICAL.value
        assert "max_memory_mb" in allocation
        assert "max_workers" in allocation
    
    @pytest.mark.asyncio
    async def test_start_end_executor_execution(self, resource_manager):
        """Should track executor execution lifecycle."""
        allocation = await resource_manager.start_executor_execution("test-exec")
        assert "test-exec" in resource_manager._active_executors
        
        await resource_manager.end_executor_execution(
            executor_id="test-exec",
            success=True,
            duration_ms=100.0,
            memory_mb=256.0,
        )
        
        assert "test-exec" not in resource_manager._active_executors
        assert "test-exec" in resource_manager.executor_metrics
        
        metrics = resource_manager.get_executor_metrics("test-exec")
        assert metrics["total_executions"] == 1
        assert metrics["successful_executions"] == 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_on_failure(self, resource_manager):
        """Circuit breaker should open after repeated failures."""
        executor_id = "failing-executor"
        
        await resource_manager.start_executor_execution(executor_id)
        
        for _ in range(5):
            await resource_manager.end_executor_execution(
                executor_id=executor_id,
                success=False,
                duration_ms=100.0,
                memory_mb=512.0,
            )
        
        breaker = resource_manager.circuit_breakers[executor_id]
        assert breaker.state == CircuitState.OPEN
    
    def test_register_allocation_policy(self, resource_manager):
        """Should register custom allocation policy."""
        policy = ResourceAllocationPolicy(
            executor_id="custom-exec",
            priority=ExecutorPriority.HIGH,
            min_memory_mb=128.0,
            max_memory_mb=512.0,
            min_workers=1,
            max_workers=4,
        )
        
        resource_manager.register_allocation_policy(policy)
        assert "custom-exec" in resource_manager.allocation_policies
    
    def test_reset_circuit_breaker(self, resource_manager):
        """Should reset circuit breaker manually."""
        breaker = resource_manager.get_or_create_circuit_breaker("test-exec")
        breaker.state = CircuitState.OPEN
        breaker.failure_count = 10
        
        success = resource_manager.reset_circuit_breaker("test-exec")
        assert success
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
    
    def test_get_resource_status(self, resource_manager):
        """Should get comprehensive resource status."""
        status = resource_manager.get_resource_status()
        
        assert "timestamp" in status
        assert "current_pressure" in status
        assert "resource_usage" in status
        assert "executor_metrics" in status
        assert "circuit_breakers" in status


class TestResourceAlertManager:
    """Tests for ResourceAlertManager functionality."""
    
    def test_memory_warning_alert(self, alert_manager):
        """Should generate memory warning alert."""
        from farfan_pipeline.core.orchestrator.resource_manager import (
            ResourcePressureEvent,
        )
        
        event = ResourcePressureEvent(
            timestamp=datetime.utcnow(),
            pressure_level=ResourcePressureLevel.HIGH,
            cpu_percent=50.0,
            memory_mb=800.0,
            memory_percent=78.0,
            worker_count=8,
            active_executors=5,
            degradation_applied=[],
            circuit_breakers_open=[],
            message="High memory usage",
        )
        
        alerts = alert_manager.process_event(event)
        assert len(alerts) > 0
        
        memory_alerts = [
            a for a in alerts if "memory" in a.title.lower()
        ]
        assert len(memory_alerts) > 0
    
    def test_circuit_breaker_alert(self, alert_manager):
        """Should generate circuit breaker alert."""
        from farfan_pipeline.core.orchestrator.resource_manager import (
            ResourcePressureEvent,
        )
        
        event = ResourcePressureEvent(
            timestamp=datetime.utcnow(),
            pressure_level=ResourcePressureLevel.HIGH,
            cpu_percent=50.0,
            memory_mb=500.0,
            memory_percent=50.0,
            worker_count=8,
            active_executors=5,
            degradation_applied=[],
            circuit_breakers_open=["D3-Q3", "D4-Q2"],
            message="Circuit breakers opened",
        )
        
        alerts = alert_manager.process_event(event)
        
        cb_alerts = [
            a for a in alerts if "circuit" in a.title.lower()
        ]
        assert len(cb_alerts) > 0
    
    def test_alert_rate_limiting(self, alert_manager):
        """Should rate limit repeated alerts."""
        from farfan_pipeline.core.orchestrator.resource_manager import (
            ResourcePressureEvent,
        )
        
        event = ResourcePressureEvent(
            timestamp=datetime.utcnow(),
            pressure_level=ResourcePressureLevel.HIGH,
            cpu_percent=78.0,
            memory_mb=500.0,
            memory_percent=50.0,
            worker_count=8,
            active_executors=5,
            degradation_applied=[],
            circuit_breakers_open=[],
            message="High CPU",
        )
        
        alerts1 = alert_manager.process_event(event)
        alerts2 = alert_manager.process_event(event)
        
        cpu_alerts1 = [a for a in alerts1 if "cpu" in a.title.lower()]
        cpu_alerts2 = [a for a in alerts2 if "cpu" in a.title.lower()]
        
        assert len(cpu_alerts1) >= len(cpu_alerts2)
    
    def test_get_alert_summary(self, alert_manager):
        """Should get alert summary."""
        summary = alert_manager.get_alert_summary()
        
        assert "total_alerts" in summary
        assert "last_hour" in summary
        assert "last_24_hours" in summary
        assert "by_severity" in summary


class TestResourceIntegration:
    """Tests for resource integration functions."""
    
    def test_create_resource_manager(self, resource_limits):
        """Should create resource manager with alerts."""
        manager, alerts = create_resource_manager(
            resource_limits=resource_limits,
            enable_circuit_breakers=True,
            enable_degradation=True,
            enable_alerts=True,
        )
        
        assert manager is not None
        assert alerts is not None
        assert manager.enable_circuit_breakers
        assert manager.enable_degradation
    
    def test_register_default_policies(self, resource_manager):
        """Should register default policies for critical executors."""
        register_default_policies(resource_manager)
        
        assert "D3-Q3" in resource_manager.allocation_policies
        assert "D4-Q2" in resource_manager.allocation_policies
        
        d3q3_policy = resource_manager.allocation_policies["D3-Q3"]
        assert d3q3_policy.priority == ExecutorPriority.CRITICAL
