"""Tests for signal registry circuit breaker and degradation handling.

This module tests the circuit breaker pattern implementation in the
signal registry, including:
- Circuit state transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Graceful degradation under failure conditions
- Health check reporting
- Manual recovery operations
- Availability monitoring

Author: F.A.R.F.A.N Pipeline Team
Status: Production Test Suite
"""

import time
from unittest.mock import Mock, MagicMock, patch
import pytest

# Import circuit breaker components
from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_registry import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerConfig,
    QuestionnaireSignalRegistry,
    SignalExtractionError,
)


class TestCircuitBreakerBasics:
    """Test basic circuit breaker functionality."""

    def test_circuit_breaker_default_state(self):
        """Circuit breaker starts in CLOSED state."""
        breaker = CircuitBreaker()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_available() is True
        assert breaker.failure_count == 0
        assert breaker.success_count == 0

    def test_circuit_breaker_custom_config(self):
        """Circuit breaker accepts custom configuration."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=1,
        )
        breaker = CircuitBreaker(config=config)
        assert breaker.config.failure_threshold == 3
        assert breaker.config.recovery_timeout == 30.0
        assert breaker.config.success_threshold == 1

    def test_circuit_opens_after_threshold_failures(self):
        """Circuit opens after reaching failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config=config)
        
        # Record failures up to threshold
        for i in range(3):
            breaker.record_failure()
        
        assert breaker.state == CircuitState.OPEN
        assert breaker.is_available() is False

    def test_circuit_remains_closed_below_threshold(self):
        """Circuit remains closed below failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=5)
        breaker = CircuitBreaker(config=config)
        
        # Record failures below threshold
        breaker.record_failure()
        breaker.record_failure()
        
        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_available() is True

    def test_success_resets_failure_count(self):
        """Success in CLOSED state resets failure count."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config=config)
        
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.failure_count == 2
        
        breaker.record_success()
        assert breaker.failure_count == 0


class TestCircuitBreakerRecovery:
    """Test circuit breaker recovery mechanisms."""

    def test_circuit_transitions_to_half_open_after_timeout(self):
        """Circuit transitions to HALF_OPEN after recovery timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1,  # 100ms
        )
        breaker = CircuitBreaker(config=config)
        
        # Open the circuit
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        # Check availability (should transition to HALF_OPEN)
        assert breaker.is_available() is True
        assert breaker.state == CircuitState.HALF_OPEN

    def test_circuit_closes_after_successful_recovery(self):
        """Circuit closes after success threshold in HALF_OPEN state."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1,
            success_threshold=2,
        )
        breaker = CircuitBreaker(config=config)
        
        # Open circuit
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        
        # Wait and transition to HALF_OPEN
        time.sleep(0.15)
        breaker.is_available()
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Record successes
        breaker.record_success()
        breaker.record_success()
        
        assert breaker.state == CircuitState.CLOSED

    def test_circuit_reopens_on_failure_during_recovery(self):
        """Circuit reopens if failure occurs during HALF_OPEN state."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1,
        )
        breaker = CircuitBreaker(config=config)
        
        # Open circuit
        breaker.record_failure()
        breaker.record_failure()
        
        # Wait and transition to HALF_OPEN
        time.sleep(0.15)
        breaker.is_available()
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Failure during recovery
        breaker.record_failure()
        
        assert breaker.state == CircuitState.OPEN


class TestCircuitBreakerStatus:
    """Test circuit breaker status and monitoring."""

    def test_get_status_returns_complete_info(self):
        """get_status returns comprehensive status information."""
        breaker = CircuitBreaker()
        status = breaker.get_status()
        
        assert "state" in status
        assert "failure_count" in status
        assert "success_count" in status
        assert "time_since_last_failure" in status
        assert "time_in_current_state" in status

    def test_status_reflects_current_state(self):
        """Status accurately reflects current circuit state."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config=config)
        
        # Initial state
        status = breaker.get_status()
        assert status["state"] == CircuitState.CLOSED
        
        # Open state
        breaker.record_failure()
        breaker.record_failure()
        status = breaker.get_status()
        assert status["state"] == CircuitState.OPEN
        assert status["failure_count"] == 0  # Reset after opening


class TestSignalRegistryIntegration:
    """Test circuit breaker integration with signal registry."""

    @pytest.fixture
    def mock_questionnaire(self):
        """Create mock questionnaire."""
        questionnaire = Mock()
        questionnaire.version = "1.0.0"
        questionnaire.sha256 = "a" * 64
        questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {},
                "scoring": {},
            }
        }
        questionnaire.micro_questions = []
        return questionnaire

    def test_registry_initializes_with_circuit_breaker(self, mock_questionnaire):
        """Registry initializes with circuit breaker."""
        registry = QuestionnaireSignalRegistry(mock_questionnaire)
        assert hasattr(registry, "_circuit_breaker")
        assert registry._circuit_breaker.state == CircuitState.CLOSED

    def test_registry_health_check_reports_healthy(self, mock_questionnaire):
        """Health check reports healthy when circuit is closed."""
        registry = QuestionnaireSignalRegistry(mock_questionnaire)
        health = registry.health_check()
        
        assert health["healthy"] is True
        assert health["status"] == "healthy"
        assert "circuit_breaker" in health
        assert "metrics" in health
        assert "timestamp" in health

    def test_registry_health_check_reports_degraded_when_open(self, mock_questionnaire):
        """Health check reports degraded when circuit is open."""
        registry = QuestionnaireSignalRegistry(mock_questionnaire)
        
        # Force circuit to open
        config = CircuitBreakerConfig(failure_threshold=1)
        registry._circuit_breaker.config = config
        registry._circuit_breaker.record_failure()
        
        health = registry.health_check()
        assert health["healthy"] is False
        assert health["status"] == "degraded"

    def test_registry_get_metrics_includes_circuit_breaker(self, mock_questionnaire):
        """get_metrics includes circuit breaker status."""
        registry = QuestionnaireSignalRegistry(mock_questionnaire)
        metrics = registry.get_metrics()
        
        assert "circuit_breaker" in metrics
        assert metrics["circuit_breaker"]["state"] == CircuitState.CLOSED

    def test_registry_manual_reset_closes_circuit(self, mock_questionnaire):
        """Manual reset closes open circuit."""
        registry = QuestionnaireSignalRegistry(mock_questionnaire)
        
        # Open circuit
        config = CircuitBreakerConfig(failure_threshold=1)
        registry._circuit_breaker.config = config
        registry._circuit_breaker.record_failure()
        assert registry._circuit_breaker.state == CircuitState.OPEN
        
        # Manual reset
        registry.reset_circuit_breaker()
        assert registry._circuit_breaker.state == CircuitState.CLOSED


class TestGracefulDegradation:
    """Test graceful degradation scenarios."""

    @pytest.fixture
    def mock_questionnaire(self):
        """Create mock questionnaire."""
        questionnaire = Mock()
        questionnaire.version = "1.0.0"
        questionnaire.sha256 = "a" * 64
        questionnaire.data = {
            "blocks": {
                "micro_questions": [],
                "meso_questions": [],
                "macro_question": {},
                "scoring": {},
                "niveles_abstraccion": {
                    "clusters": [],
                    "policy_areas": [],
                },
            }
        }
        questionnaire.micro_questions = []
        return questionnaire

    def test_registry_rejects_requests_when_circuit_open(self, mock_questionnaire):
        """Registry rejects requests when circuit is open."""
        registry = QuestionnaireSignalRegistry(mock_questionnaire)
        
        # Force circuit to open
        config = CircuitBreakerConfig(failure_threshold=1)
        registry._circuit_breaker.config = config
        registry._circuit_breaker.record_failure()
        
        # Attempt to get signals should raise error
        with pytest.raises(SignalExtractionError) as exc_info:
            registry.get_assembly_signals("meso")
        
        assert "Circuit breaker" in str(exc_info.value)
        assert "open" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
