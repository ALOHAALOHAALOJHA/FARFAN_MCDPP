"""
Tests for Phase 1 Circuit Breaker
==================================

Tests the aggressively preventive failure protection system.
Validates that Phase 1 fails fast and loud when conditions are not met.

Author: F.A.R.F.A.N Testing Team
Date: 2025-12-11
"""

import pytest
from unittest.mock import patch, MagicMock

try:
    import psutil  # noqa: F401
except Exception:
    pytest.skip("psutil not installed in this environment", allow_module_level=True)

from farfan_pipeline.phases.Phase_one.phase1_40_00_circuit_breaker import (
    Phase1CircuitBreaker,
    CircuitState,
    FailureSeverity,
    DependencyCheck,
    ResourceCheck,
    PreflightResult,
    SubphaseCheckpoint,
    get_circuit_breaker,
    run_preflight_check,
)


class TestPhase1CircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initializes correctly."""
        cb = Phase1CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.last_check is None
    
    def test_preflight_check_pass(self):
        """Test pre-flight check passes with all dependencies."""
        cb = Phase1CircuitBreaker()
        result = cb.preflight_check()
        
        # Should pass if running in valid environment
        assert isinstance(result, PreflightResult)
        assert result.timestamp is not None
        assert isinstance(result.dependency_checks, list)
        assert isinstance(result.resource_checks, list)
        
        # If it passed, circuit should be CLOSED
        if result.passed:
            assert cb.state == CircuitState.CLOSED
            assert len(result.critical_failures) == 0
    
    def test_python_version_check(self):
        """Test Python version validation."""
        cb = Phase1CircuitBreaker()
        result = PreflightResult(passed=True, timestamp="2025-12-11T00:00:00Z")
        
        cb._check_python_version(result)
        
        # Should have a Python dependency check
        python_checks = [c for c in result.dependency_checks if c.name == "python"]
        assert len(python_checks) == 1
        python_check = python_checks[0]
        
        # Verify version format
        assert python_check.version is not None
        assert '.' in python_check.version
    
    @patch('psutil.virtual_memory')
    def test_insufficient_memory_detection(self, mock_memory):
        """Test circuit breaker detects insufficient memory."""
        # Mock insufficient memory (100 MB available) with all required attributes
        mock_mem = MagicMock()
        mock_mem.available = 100 * 1024 * 1024  # 100 MB
        mock_mem.total = 8 * 1024 * 1024 * 1024  # 8 GB
        mock_memory.return_value = mock_mem
        
        cb = Phase1CircuitBreaker()
        result = cb.preflight_check()
        
        # Should fail due to insufficient memory
        assert not result.passed
        assert any('memory' in f.lower() for f in result.critical_failures)
        assert cb.state == CircuitState.OPEN
    
    @patch('psutil.disk_usage')
    def test_insufficient_disk_detection(self, mock_disk):
        """Test circuit breaker detects insufficient disk space."""
        # Mock insufficient disk (100 MB free)
        mock_disk.return_value = MagicMock(
            free=100 * 1024 * 1024,  # 100 MB
            total=100 * 1024 * 1024 * 1024  # 100 GB
        )
        
        cb = Phase1CircuitBreaker()
        result = cb.preflight_check()
        
        # Should fail due to insufficient disk
        assert not result.passed
        assert any('disk' in f.lower() for f in result.critical_failures)
        assert cb.state == CircuitState.OPEN
    
    def test_can_execute_when_closed(self):
        """Test can_execute returns True when circuit is CLOSED."""
        cb = Phase1CircuitBreaker()
        cb.state = CircuitState.CLOSED
        assert cb.can_execute() is True
    
    def test_cannot_execute_when_open(self):
        """Test can_execute returns False when circuit is OPEN."""
        cb = Phase1CircuitBreaker()
        cb.state = CircuitState.OPEN
        assert cb.can_execute() is False
    
    def test_diagnostic_report_generation(self):
        """Test diagnostic report is generated correctly."""
        cb = Phase1CircuitBreaker()
        result = cb.preflight_check()
        
        report = cb.get_diagnostic_report()
        
        # Verify report contains key sections
        assert "PHASE 1 CIRCUIT BREAKER" in report
        assert "SYSTEM INFORMATION" in report
        assert "DEPENDENCY CHECKS" in report
        assert "RESOURCE CHECKS" in report
        
        if result.passed:
            assert "✓" in report
        else:
            assert "✗" in report
            assert "CRITICAL FAILURES" in report
    
    def test_cannot_execute_when_open(self):
        """Test can_execute returns False when circuit is OPEN."""
        cb = Phase1CircuitBreaker()
        cb.state = CircuitState.OPEN
        
        # Test that execution is blocked when circuit is OPEN
        assert cb.can_execute() is False


class TestSubphaseCheckpoint:
    """Test subphase checkpoint validation."""
    
    def test_checkpoint_initialization(self):
        """Test checkpoint validator initializes correctly."""
        checkpoint = SubphaseCheckpoint()
        assert isinstance(checkpoint.checkpoints, dict)
        assert len(checkpoint.checkpoints) == 0
    
    def test_checkpoint_validation_pass(self):
        """Test checkpoint validation passes with valid output."""
        checkpoint = SubphaseCheckpoint()
        
        # Mock output
        mock_output = [1, 2, 3]
        
        # Validators
        validators = [
            lambda x: (isinstance(x, list), "Must be a list"),
            lambda x: (len(x) == 3, "Must have 3 items"),
        ]
        
        passed, errors = checkpoint.validate_checkpoint(
            subphase_num=1,
            output=mock_output,
            expected_type=list,
            validators=validators
        )
        
        assert passed is True
        assert len(errors) == 0
        assert 1 in checkpoint.checkpoints
        assert checkpoint.checkpoints[1]['passed'] is True
    
    def test_checkpoint_validation_fail_type(self):
        """Test checkpoint validation fails with wrong type."""
        checkpoint = SubphaseCheckpoint()
        
        # Mock output (wrong type)
        mock_output = "string"
        
        passed, errors = checkpoint.validate_checkpoint(
            subphase_num=1,
            output=mock_output,
            expected_type=list,
            validators=[]
        )
        
        assert passed is False
        assert len(errors) == 1
        assert "Expected list" in errors[0]
    
    def test_checkpoint_validation_fail_validator(self):
        """Test checkpoint validation fails when validator fails."""
        checkpoint = SubphaseCheckpoint()
        
        # Mock output
        mock_output = [1, 2]
        
        # Failing validator
        validators = [
            lambda x: (len(x) == 3, "Must have 3 items"),
        ]
        
        passed, errors = checkpoint.validate_checkpoint(
            subphase_num=1,
            output=mock_output,
            expected_type=list,
            validators=validators
        )
        
        assert passed is False
        assert len(errors) == 1
        assert "Must have 3 items" in errors[0]
        assert checkpoint.checkpoints[1]['passed'] is False
    
    def test_checkpoint_records_metadata(self):
        """Test checkpoint records metadata correctly."""
        checkpoint = SubphaseCheckpoint()
        
        mock_output = [1, 2, 3]
        
        checkpoint.validate_checkpoint(
            subphase_num=5,
            output=mock_output,
            expected_type=list,
            validators=[]
        )
        
        assert 5 in checkpoint.checkpoints
        metadata = checkpoint.checkpoints[5]
        
        assert 'timestamp' in metadata
        assert 'passed' in metadata
        assert 'errors' in metadata
        assert 'output_hash' in metadata
        assert len(metadata['output_hash']) == 16  # SHA256 truncated to 16 chars


class TestGlobalCircuitBreaker:
    """Test global circuit breaker functions."""
    
    def test_get_circuit_breaker_returns_singleton(self):
        """Test get_circuit_breaker returns the same instance."""
        cb1 = get_circuit_breaker()
        cb2 = get_circuit_breaker()
        
        assert cb1 is cb2
    
    def test_run_preflight_check(self):
        """Test run_preflight_check executes."""
        result = run_preflight_check()
        
        assert isinstance(result, PreflightResult)
        assert result.timestamp is not None


class TestDependencyCheck:
    """Test DependencyCheck dataclass."""
    
    def test_dependency_check_available(self):
        """Test DependencyCheck for available dependency."""
        check = DependencyCheck(
            name="test_package",
            available=True,
            version="1.0.0",
            severity=FailureSeverity.CRITICAL
        )
        
        assert check.name == "test_package"
        assert check.available is True
        assert check.version == "1.0.0"
        assert check.error is None
    
    def test_dependency_check_unavailable(self):
        """Test DependencyCheck for unavailable dependency."""
        check = DependencyCheck(
            name="missing_package",
            available=False,
            error="ModuleNotFoundError: No module named 'missing_package'",
            severity=FailureSeverity.CRITICAL,
            remediation="pip install missing_package"
        )
        
        assert check.name == "missing_package"
        assert check.available is False
        assert check.error is not None
        assert "ModuleNotFoundError" in check.error
        assert check.remediation == "pip install missing_package"


class TestResourceCheck:
    """Test ResourceCheck dataclass."""
    
    def test_resource_check_sufficient(self):
        """Test ResourceCheck with sufficient resources."""
        check = ResourceCheck(
            resource_type="memory",
            available=8.0,
            required=2.0,
            sufficient=True,
            unit="GB"
        )
        
        assert check.resource_type == "memory"
        assert check.available == 8.0
        assert check.required == 2.0
        assert check.sufficient is True
        assert check.unit == "GB"
    
    def test_resource_check_insufficient(self):
        """Test ResourceCheck with insufficient resources."""
        check = ResourceCheck(
            resource_type="disk",
            available=0.5,
            required=1.0,
            sufficient=False,
            unit="GB"
        )
        
        assert check.resource_type == "disk"
        assert check.available == 0.5
        assert check.required == 1.0
        assert check.sufficient is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
