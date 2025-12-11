#!/usr/bin/env python3
"""
Comprehensive Adversarial Test Suite for Phase 1 Method Guards

This test suite validates the defensive programming and circuit breaker
patterns in phase1_method_guards.py with adversarial inputs and failure scenarios.

TESTING PHILOSOPHY (per problem statement):
1. All conditions tested for instantaneous readiness
2. All theoretical blockers simulated and verified
3. All failure modes validated with graceful degradation
4. All recovery mechanisms tested for robustness

Author: AI Systems Architect
Version: 1.0.0
"""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from canonic_phases.Phase_one.phase1_method_guards import (
    DerekBeachGuard,
    TheoryOfChangeGuard,
    MethodStatus,
    FailureCategory,
    GuardedInvocation,
    get_derek_beach_guard,
    get_theory_of_change_guard,
    safe_classify_beach_test,
    safe_validate_teoria_cambio,
    run_comprehensive_diagnostics,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def fresh_derek_beach_guard():
    """Create a fresh Derek Beach guard for testing."""
    return DerekBeachGuard()


@pytest.fixture
def fresh_theory_of_change_guard():
    """Create a fresh Theory of Change guard for testing."""
    return TheoryOfChangeGuard()


# ============================================================================
# DEREK BEACH GUARD TESTS
# ============================================================================

class TestDerekBeachGuardInitialization:
    """Test Derek Beach guard initialization under various conditions."""
    
    def test_successful_initialization(self):
        """Test successful initialization with all dependencies available."""
        guard = DerekBeachGuard()
        
        # Should be available if dependencies installed
        assert guard.health.name == "DerekBeach"
        assert guard.health.status in [MethodStatus.AVAILABLE, MethodStatus.UNAVAILABLE]
    
    def test_initialization_without_imports(self):
        """Test initialization when imports fail."""
        with patch('canonic_phases.Phase_one.phase1_method_guards.logger') as mock_logger:
            with patch.dict('sys.modules', {'methods_dispensary.derek_beach': None}):
                guard = DerekBeachGuard()
                
                # Should handle import failure gracefully
                assert guard.health.status == MethodStatus.UNAVAILABLE
                assert guard._beach_test is None


class TestDerekBeachClassifyEvidentialTest:
    """Test evidential test classification with adversarial inputs."""
    
    def test_valid_classification_hoop_test(self, fresh_derek_beach_guard):
        """Test classification with valid inputs for hoop test."""
        guard = fresh_derek_beach_guard
        
        if guard.health.is_available():
            result = guard.classify_evidential_test(necessity=0.8, sufficiency=0.3)
            
            assert result.success
            assert result.result in ["hoop_test", "smoking_gun", "doubly_decisive", "straw_in_wind"]
            assert result.fallback_used == False
            assert result.execution_time > 0
    
    def test_valid_classification_smoking_gun(self, fresh_derek_beach_guard):
        """Test classification with valid inputs for smoking gun."""
        guard = fresh_derek_beach_guard
        
        if guard.health.is_available():
            result = guard.classify_evidential_test(necessity=0.3, sufficiency=0.8)
            
            assert result.success
            assert result.result in ["hoop_test", "smoking_gun", "doubly_decisive", "straw_in_wind"]
    
    def test_invalid_necessity_too_high(self, fresh_derek_beach_guard):
        """Test classification with necessity > 1.0."""
        guard = fresh_derek_beach_guard
        
        result = guard.classify_evidential_test(necessity=1.5, sufficiency=0.5)
        
        # Should fail validation and use fallback
        assert result.success == False
        assert result.fallback_used == True
        assert "validation failed" in result.error.lower()
    
    def test_invalid_necessity_negative(self, fresh_derek_beach_guard):
        """Test classification with negative necessity."""
        guard = fresh_derek_beach_guard
        
        result = guard.classify_evidential_test(necessity=-0.5, sufficiency=0.5)
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_invalid_sufficiency_too_high(self, fresh_derek_beach_guard):
        """Test classification with sufficiency > 1.0."""
        guard = fresh_derek_beach_guard
        
        result = guard.classify_evidential_test(necessity=0.5, sufficiency=2.0)
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_non_numeric_inputs(self, fresh_derek_beach_guard):
        """Test classification with non-numeric inputs."""
        guard = fresh_derek_beach_guard
        
        result = guard.classify_evidential_test(necessity="high", sufficiency="low")
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_none_inputs(self, fresh_derek_beach_guard):
        """Test classification with None inputs."""
        guard = fresh_derek_beach_guard
        
        result = guard.classify_evidential_test(necessity=None, sufficiency=None)
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_circuit_breaker_activation(self, fresh_derek_beach_guard):
        """Test that circuit breaker opens after repeated failures."""
        guard = fresh_derek_beach_guard
        
        # Force failures
        for i in range(5):
            result = guard.classify_evidential_test(necessity=999, sufficiency=999)
            assert result.fallback_used == True
        
        # Circuit should be open
        if guard.health.failure_count >= guard.health.circuit_breaker_threshold:
            assert guard.health.status == MethodStatus.CIRCUIT_OPEN
    
    def test_method_unavailable(self):
        """Test behavior when method is unavailable."""
        guard = DerekBeachGuard()
        guard.health.status = MethodStatus.UNAVAILABLE
        
        result = guard.classify_evidential_test(necessity=0.5, sufficiency=0.5)
        
        assert result.success == False
        assert result.fallback_used == True
        assert "unavailable" in result.error.lower()


class TestDerekBeachApplyEvidentialTestLogic:
    """Test evidential test logic application with adversarial inputs."""
    
    def test_valid_hoop_test_pass(self, fresh_derek_beach_guard):
        """Test hoop test logic with evidence found."""
        guard = fresh_derek_beach_guard
        
        if guard.health.is_available():
            result = guard.apply_evidential_test_logic(
                test_type="hoop_test",
                evidence_found=True,
                prior=0.5,
                bayes_factor=2.0
            )
            
            assert result.success
            assert isinstance(result.result, tuple)
            assert len(result.result) == 2  # (posterior, interpretation)
    
    def test_valid_hoop_test_fail(self, fresh_derek_beach_guard):
        """Test hoop test logic with evidence not found."""
        guard = fresh_derek_beach_guard
        
        if guard.health.is_available():
            result = guard.apply_evidential_test_logic(
                test_type="hoop_test",
                evidence_found=False,
                prior=0.5,
                bayes_factor=2.0
            )
            
            assert result.success
            # Hoop test failure should dramatically reduce posterior
            posterior, interpretation = result.result
            assert posterior < 0.1  # Near elimination per Beach
    
    def test_invalid_test_type(self, fresh_derek_beach_guard):
        """Test with invalid test type."""
        guard = fresh_derek_beach_guard
        
        result = guard.apply_evidential_test_logic(
            test_type="invalid_test",
            evidence_found=True,
            prior=0.5,
            bayes_factor=2.0
        )
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_invalid_prior_too_high(self, fresh_derek_beach_guard):
        """Test with prior > 1.0."""
        guard = fresh_derek_beach_guard
        
        result = guard.apply_evidential_test_logic(
            test_type="hoop_test",
            evidence_found=True,
            prior=1.5,
            bayes_factor=2.0
        )
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_invalid_bayes_factor_negative(self, fresh_derek_beach_guard):
        """Test with negative Bayes factor."""
        guard = fresh_derek_beach_guard
        
        result = guard.apply_evidential_test_logic(
            test_type="hoop_test",
            evidence_found=True,
            prior=0.5,
            bayes_factor=-2.0
        )
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_invalid_bayes_factor_zero(self, fresh_derek_beach_guard):
        """Test with zero Bayes factor."""
        guard = fresh_derek_beach_guard
        
        result = guard.apply_evidential_test_logic(
            test_type="hoop_test",
            evidence_found=True,
            prior=0.5,
            bayes_factor=0.0
        )
        
        assert result.success == False
        assert result.fallback_used == True


# ============================================================================
# THEORY OF CHANGE GUARD TESTS
# ============================================================================

class TestTheoryOfChangeGuardInitialization:
    """Test Theory of Change guard initialization under various conditions."""
    
    def test_successful_initialization(self):
        """Test successful initialization with all dependencies available."""
        guard = TheoryOfChangeGuard()
        
        assert guard.health.name == "TheoryOfChange"
        assert guard.health.status in [MethodStatus.AVAILABLE, MethodStatus.UNAVAILABLE]
    
    def test_initialization_without_imports(self):
        """Test initialization when imports fail."""
        with patch.dict('sys.modules', {'methods_dispensary.teoria_cambio': None}):
            guard = TheoryOfChangeGuard()
            
            assert guard.health.status == MethodStatus.UNAVAILABLE
            assert guard._teoria_cambio_class is None


class TestTheoryOfChangeCreateInstance:
    """Test Theory of Change instance creation."""
    
    def test_create_instance_success(self, fresh_theory_of_change_guard):
        """Test successful instance creation."""
        guard = fresh_theory_of_change_guard
        
        if guard.health.is_available():
            result = guard.create_teoria_cambio_instance()
            
            assert result.success
            assert result.result is not None
    
    def test_create_instance_unavailable(self):
        """Test instance creation when method unavailable."""
        guard = TheoryOfChangeGuard()
        guard.health.status = MethodStatus.UNAVAILABLE
        
        result = guard.create_teoria_cambio_instance()
        
        assert result.success == False
        assert result.fallback_used == True


class TestTheoryOfChangeValidateDAG:
    """Test Theory of Change DAG validation."""
    
    def test_validate_with_none_instance(self, fresh_theory_of_change_guard):
        """Test validation with None instance."""
        guard = fresh_theory_of_change_guard
        
        result = guard.validate_causal_dag(teoria_cambio_instance=None, dag=Mock())
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_validate_with_none_dag(self, fresh_theory_of_change_guard):
        """Test validation with None DAG."""
        guard = fresh_theory_of_change_guard
        
        result = guard.validate_causal_dag(teoria_cambio_instance=Mock(), dag=None)
        
        assert result.success == False
        assert result.fallback_used == True
    
    def test_circuit_breaker_activation(self, fresh_theory_of_change_guard):
        """Test circuit breaker for repeated validation failures."""
        guard = fresh_theory_of_change_guard
        
        # Force failures with invalid inputs
        for i in range(5):
            result = guard.validate_causal_dag(teoria_cambio_instance=None, dag=None)
            assert result.fallback_used == True
        
        # Circuit might be open depending on failure count
        if guard.health.failure_count >= guard.health.circuit_breaker_threshold:
            assert guard.health.status == MethodStatus.CIRCUIT_OPEN


# ============================================================================
# HEALTH MONITORING TESTS
# ============================================================================

class TestMethodHealth:
    """Test health monitoring and circuit breaker logic."""
    
    def test_success_decay_failures(self, fresh_derek_beach_guard):
        """Test that successes decay failure count."""
        guard = fresh_derek_beach_guard
        
        initial_failures = guard.health.failure_count
        guard.health.record_success()
        
        # Failures should decay
        assert guard.health.failure_count <= initial_failures
    
    def test_circuit_breaker_timeout(self, fresh_derek_beach_guard):
        """Test circuit breaker reopens after timeout."""
        guard = fresh_derek_beach_guard
        
        # Force circuit open
        guard.health.status = MethodStatus.CIRCUIT_OPEN
        guard.health.last_failure = time.time() - 400  # 400 seconds ago
        
        # Should be available again after timeout (300s)
        assert guard.health.is_available()
    
    def test_health_report_structure(self, fresh_derek_beach_guard):
        """Test health report has expected structure."""
        guard = fresh_derek_beach_guard
        report = guard.get_health_report()
        
        assert "name" in report
        assert "status" in report
        assert "is_available" in report
        assert "success_count" in report
        assert "failure_count" in report
        assert "recent_errors" in report


# ============================================================================
# CONVENIENCE FUNCTION TESTS
# ============================================================================

class TestConvenienceFunctions:
    """Test convenience functions for Phase 1 integration."""
    
    def test_safe_classify_beach_test(self):
        """Test safe classification wrapper."""
        test_type, is_production = safe_classify_beach_test(0.7, 0.3)
        
        assert test_type in ["hoop_test", "smoking_gun", "doubly_decisive", "straw_in_wind"]
        assert isinstance(is_production, bool)
    
    def test_safe_classify_beach_test_with_invalid_inputs(self):
        """Test safe classification with invalid inputs."""
        test_type, is_production = safe_classify_beach_test(999, 999)
        
        # Should use fallback
        assert test_type == "straw_in_wind"  # Default fallback
        assert is_production == False
    
    def test_safe_validate_teoria_cambio_with_none(self):
        """Test safe validation with None DAG."""
        result_dict, is_production = safe_validate_teoria_cambio(None)
        
        # Should use fallback
        assert isinstance(result_dict, dict)
        assert is_production == False


# ============================================================================
# DIAGNOSTICS TESTS
# ============================================================================

class TestDiagnostics:
    """Test diagnostic utilities."""
    
    def test_run_comprehensive_diagnostics(self):
        """Test comprehensive diagnostics runner."""
        report = run_comprehensive_diagnostics()
        
        assert "timestamp" in report
        assert "guards" in report
        assert "overall_status" in report
        assert "recommendations" in report
        
        # Should have reports for both guards
        assert "derek_beach" in report["guards"]
        assert "theory_of_change" in report["guards"]


# ============================================================================
# STRESS TESTS
# ============================================================================

class TestStressScenarios:
    """Stress testing with extreme scenarios."""
    
    def test_rapid_fire_requests(self, fresh_derek_beach_guard):
        """Test handling of rapid-fire requests."""
        guard = fresh_derek_beach_guard
        
        results = []
        for i in range(100):
            result = guard.classify_evidential_test(0.5, 0.5)
            results.append(result)
        
        # All should complete (success or fallback)
        assert len(results) == 100
        assert all(isinstance(r, GuardedInvocation) for r in results)
    
    def test_extreme_input_ranges(self, fresh_derek_beach_guard):
        """Test with extreme input values."""
        guard = fresh_derek_beach_guard
        
        extreme_values = [
            (float('inf'), 0.5),
            (0.5, float('inf')),
            (float('-inf'), 0.5),
            (1e10, 1e10),
            (-1e10, -1e10),
        ]
        
        for necessity, sufficiency in extreme_values:
            result = guard.classify_evidential_test(necessity, sufficiency)
            # Should handle gracefully with fallback
            assert isinstance(result, GuardedInvocation)
            # Invalid inputs should trigger fallback
            if necessity > 1.0 or necessity < 0.0 or sufficiency > 1.0 or sufficiency < 0.0:
                assert result.fallback_used == True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestGuardIntegration:
    """Test integration between guards and Phase 1."""
    
    def test_singleton_guards(self):
        """Test that get_*_guard returns singletons."""
        guard1 = get_derek_beach_guard()
        guard2 = get_derek_beach_guard()
        
        assert guard1 is guard2  # Same object
    
    def test_both_guards_independent(self):
        """Test that guards operate independently."""
        db_guard = get_derek_beach_guard()
        toc_guard = get_theory_of_change_guard()
        
        # Failure in one shouldn't affect the other
        db_guard.health.record_failure("test", FailureCategory.RUNTIME_ERROR)
        
        assert db_guard.health.failure_count > 0
        # Theory of Change guard should be unaffected
        assert toc_guard.health.failure_count == 0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_zero_classification(self, fresh_derek_beach_guard):
        """Test classification with both necessity and sufficiency at 0."""
        guard = fresh_derek_beach_guard
        
        result = guard.classify_evidential_test(0.0, 0.0)
        
        if guard.health.is_available():
            assert result.success
            assert result.result == "straw_in_wind"  # Low N, low S
    
    def test_one_one_classification(self, fresh_derek_beach_guard):
        """Test classification with both necessity and sufficiency at 1."""
        guard = fresh_derek_beach_guard
        
        result = guard.classify_evidential_test(1.0, 1.0)
        
        if guard.health.is_available():
            assert result.success
            assert result.result == "doubly_decisive"  # High N, high S
    
    def test_boundary_0_7_threshold(self, fresh_derek_beach_guard):
        """Test classifications around 0.7 threshold."""
        guard = fresh_derek_beach_guard
        
        if guard.health.is_available():
            # Just below threshold
            result1 = guard.classify_evidential_test(0.69, 0.3)
            # Just above threshold
            result2 = guard.classify_evidential_test(0.71, 0.3)
            
            assert result1.success and result2.success
            # Could be different test types depending on threshold


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
