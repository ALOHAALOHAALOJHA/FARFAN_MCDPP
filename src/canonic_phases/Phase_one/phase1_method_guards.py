#!/usr/bin/env python3
"""
Phase 1 Method Guards - Defensive Wrappers for Derek Beach & Theory of Change

This module provides comprehensive defensive programming and adversarial validation
for the critical methodological frameworks used in Phase 1:
- Derek Beach's Process Tracing and Evidential Tests (Beach & Pedersen 2019)
- Theory of Change DAG Validation (Goertz & Mahoney 2012)

AUDIT REQUIREMENTS (per problem statement):
1. Instantaneous invocation readiness - all pre-conditions validated upfront
2. Non-problematic execution - graceful degradation, no crashes
3. Adversarial testing - all theoretical blockers considered and handled
4. Definitive solutions - permanent fixes with audit trails

Author: AI Systems Architect
Version: 1.0.0 (Hardened Production Grade)
"""

import logging
import sys
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, cast

import numpy as np

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class MethodStatus(Enum):
    """Status of method availability and health."""
    AVAILABLE = auto()
    DEGRADED = auto()
    UNAVAILABLE = auto()
    CIRCUIT_OPEN = auto()


class FailureCategory(Enum):
    """Categories of failures for circuit breaker pattern."""
    IMPORT_ERROR = auto()
    RUNTIME_ERROR = auto()
    VALIDATION_ERROR = auto()
    TIMEOUT_ERROR = auto()
    RESOURCE_ERROR = auto()


@dataclass
class MethodHealth:
    """Health status tracking for a method."""
    name: str
    status: MethodStatus
    last_success: Optional[float] = None
    last_failure: Optional[float] = None
    failure_count: int = 0
    success_count: int = 0
    circuit_breaker_threshold: int = 3
    circuit_breaker_timeout: float = 300.0  # 5 minutes
    errors: List[str] = field(default_factory=list)
    
    def record_success(self) -> None:
        """Record successful invocation."""
        self.last_success = time.time()
        self.success_count += 1
        self.failure_count = max(0, self.failure_count - 1)  # Decay failures
        if self.status == MethodStatus.CIRCUIT_OPEN:
            # Check if enough time has passed to close circuit
            if self.last_failure and (time.time() - self.last_failure) > self.circuit_breaker_timeout:
                self.status = MethodStatus.AVAILABLE
                logger.info(f"Circuit breaker closed for {self.name} after timeout")
    
    def record_failure(self, error: str, category: FailureCategory) -> None:
        """Record failed invocation."""
        self.last_failure = time.time()
        self.failure_count += 1
        self.errors.append(f"{category.name}: {error}")
        
        # Keep only last 10 errors
        if len(self.errors) > 10:
            self.errors = self.errors[-10:]
        
        # Open circuit breaker if threshold exceeded
        if self.failure_count >= self.circuit_breaker_threshold:
            self.status = MethodStatus.CIRCUIT_OPEN
            logger.error(
                f"Circuit breaker opened for {self.name} after {self.failure_count} failures. "
                f"Will retry after {self.circuit_breaker_timeout}s"
            )
    
    def is_available(self) -> bool:
        """Check if method is available for invocation."""
        if self.status == MethodStatus.UNAVAILABLE:
            return False
        
        if self.status == MethodStatus.CIRCUIT_OPEN:
            # Check if circuit breaker timeout has passed
            if self.last_failure and (time.time() - self.last_failure) > self.circuit_breaker_timeout:
                self.status = MethodStatus.DEGRADED
                logger.info(f"Circuit breaker testing {self.name} after timeout")
                return True
            return False
        
        return True


@dataclass
class GuardedInvocation:
    """Result of a guarded method invocation."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    fallback_used: bool = False
    execution_time: float = 0.0
    method_name: str = ""


# ============================================================================
# DEREK BEACH METHOD GUARD
# ============================================================================

class DerekBeachGuard:
    """
    Defensive wrapper for Derek Beach evidential tests and causal extraction.
    
    RESPONSIBILITIES:
    1. Pre-flight validation of all dependencies
    2. Runtime protection with try-catch wrappers
    3. Circuit breaker pattern for repeated failures
    4. Fallback strategies for graceful degradation
    5. Comprehensive logging and diagnostics
    """
    
    def __init__(self):
        """Initialize Derek Beach guard with health monitoring."""
        self.health = MethodHealth(
            name="DerekBeach",
            status=MethodStatus.UNAVAILABLE
        )
        self._beach_test = None
        self._causal_extractor = None
        self._mechanism_extractor = None
        self._initialize_methods()
    
    def _initialize_methods(self) -> None:
        """
        Initialize Derek Beach methods with comprehensive error handling.
        
        AUDIT POINT 1: Instantaneous Readiness Check
        All dependencies validated upfront before any runtime invocation.
        """
        try:
            from methods_dispensary.derek_beach import (
                BeachEvidentialTest,
                CausalExtractor,
                MechanismPartExtractor,
            )
            
            self._beach_test = BeachEvidentialTest
            self._causal_extractor = CausalExtractor
            self._mechanism_extractor = MechanismPartExtractor
            
            # Validate that key methods exist
            if not hasattr(BeachEvidentialTest, 'classify_test'):
                raise AttributeError("BeachEvidentialTest missing classify_test method")
            if not hasattr(BeachEvidentialTest, 'apply_test_logic'):
                raise AttributeError("BeachEvidentialTest missing apply_test_logic method")
            
            self.health.status = MethodStatus.AVAILABLE
            logger.info("✓ Derek Beach methods initialized successfully")
            
        except ImportError as e:
            self.health.status = MethodStatus.UNAVAILABLE
            self.health.record_failure(str(e), FailureCategory.IMPORT_ERROR)
            logger.error(f"✗ Derek Beach import failed: {e}")
        
        except AttributeError as e:
            self.health.status = MethodStatus.DEGRADED
            self.health.record_failure(str(e), FailureCategory.VALIDATION_ERROR)
            logger.error(f"✗ Derek Beach validation failed: {e}")
        
        except Exception as e:
            self.health.status = MethodStatus.UNAVAILABLE
            self.health.record_failure(str(e), FailureCategory.RUNTIME_ERROR)
            logger.error(f"✗ Derek Beach initialization failed: {e}")
    
    def classify_evidential_test(
        self,
        necessity: float,
        sufficiency: float,
        fallback: str = "straw_in_wind"
    ) -> GuardedInvocation:
        """
        Classify evidential test type with comprehensive guards.
        
        AUDIT POINT 2: Non-Problematic Execution
        All inputs validated, all exceptions caught, fallback provided.
        
        Args:
            necessity: Necessity score [0, 1]
            sufficiency: Sufficiency score [0, 1]
            fallback: Fallback test type if method unavailable
        
        Returns:
            GuardedInvocation with result or fallback
        """
        start_time = time.time()
        
        # Pre-condition validation
        if not self.health.is_available():
            return GuardedInvocation(
                success=False,
                result=fallback,
                error=f"Method unavailable: {self.health.status.name}",
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="classify_evidential_test"
            )
        
        # Input validation
        try:
            necessity = float(necessity)
            sufficiency = float(sufficiency)
            
            if not (0.0 <= necessity <= 1.0):
                raise ValueError(f"Necessity must be in [0,1], got {necessity}")
            if not (0.0 <= sufficiency <= 1.0):
                raise ValueError(f"Sufficiency must be in [0,1], got {sufficiency}")
        
        except (TypeError, ValueError) as e:
            self.health.record_failure(str(e), FailureCategory.VALIDATION_ERROR)
            return GuardedInvocation(
                success=False,
                result=fallback,
                error=f"Input validation failed: {e}",
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="classify_evidential_test"
            )
        
        # Protected invocation
        try:
            if self._beach_test is None:
                raise RuntimeError("BeachEvidentialTest not initialized")
            
            result = self._beach_test.classify_test(necessity, sufficiency)
            
            self.health.record_success()
            
            return GuardedInvocation(
                success=True,
                result=result,
                execution_time=time.time() - start_time,
                method_name="classify_evidential_test"
            )
        
        except Exception as e:
            self.health.record_failure(str(e), FailureCategory.RUNTIME_ERROR)
            logger.error(f"classify_evidential_test failed: {e}\n{traceback.format_exc()}")
            
            return GuardedInvocation(
                success=False,
                result=fallback,
                error=str(e),
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="classify_evidential_test"
            )
    
    def apply_evidential_test_logic(
        self,
        test_type: str,
        evidence_found: bool,
        prior: float,
        bayes_factor: float
    ) -> GuardedInvocation:
        """
        Apply evidential test logic with comprehensive guards.
        
        Args:
            test_type: Type of evidential test
            evidence_found: Whether evidence was found
            prior: Prior probability
            bayes_factor: Bayes factor for evidence
        
        Returns:
            GuardedInvocation with (posterior, interpretation) or fallback
        """
        start_time = time.time()
        
        # Fallback result
        fallback_result = (prior, "DEGRADED: Method unavailable")
        
        if not self.health.is_available():
            return GuardedInvocation(
                success=False,
                result=fallback_result,
                error=f"Method unavailable: {self.health.status.name}",
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="apply_evidential_test_logic"
            )
        
        # Input validation
        try:
            prior = float(prior)
            bayes_factor = float(bayes_factor)
            
            if not (0.0 <= prior <= 1.0):
                raise ValueError(f"Prior must be in [0,1], got {prior}")
            if bayes_factor <= 0:
                raise ValueError(f"Bayes factor must be positive, got {bayes_factor}")
            
            if test_type not in ["hoop_test", "smoking_gun", "doubly_decisive", "straw_in_wind"]:
                raise ValueError(f"Invalid test_type: {test_type}")
        
        except (TypeError, ValueError) as e:
            self.health.record_failure(str(e), FailureCategory.VALIDATION_ERROR)
            return GuardedInvocation(
                success=False,
                result=fallback_result,
                error=f"Input validation failed: {e}",
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="apply_evidential_test_logic"
            )
        
        # Protected invocation
        try:
            if self._beach_test is None:
                raise RuntimeError("BeachEvidentialTest not initialized")
            
            result = self._beach_test.apply_test_logic(
                test_type, evidence_found, prior, bayes_factor
            )
            
            self.health.record_success()
            
            return GuardedInvocation(
                success=True,
                result=result,
                execution_time=time.time() - start_time,
                method_name="apply_evidential_test_logic"
            )
        
        except Exception as e:
            self.health.record_failure(str(e), FailureCategory.RUNTIME_ERROR)
            logger.error(f"apply_evidential_test_logic failed: {e}\n{traceback.format_exc()}")
            
            return GuardedInvocation(
                success=False,
                result=fallback_result,
                error=str(e),
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="apply_evidential_test_logic"
            )
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report for diagnostics."""
        return {
            "name": self.health.name,
            "status": self.health.status.name,
            "is_available": self.health.is_available(),
            "success_count": self.health.success_count,
            "failure_count": self.health.failure_count,
            "last_success": self.health.last_success,
            "last_failure": self.health.last_failure,
            "recent_errors": self.health.errors[-5:],  # Last 5 errors
            "circuit_breaker_threshold": self.health.circuit_breaker_threshold,
            "circuit_breaker_timeout": self.health.circuit_breaker_timeout,
        }


# ============================================================================
# THEORY OF CHANGE GUARD
# ============================================================================

class TheoryOfChangeGuard:
    """
    Defensive wrapper for Theory of Change DAG validation.
    
    RESPONSIBILITIES:
    1. Pre-flight validation of causal hierarchy axioms
    2. Runtime protection for DAG construction and validation
    3. Circuit breaker pattern for repeated failures
    4. Fallback strategies for degraded validation
    5. Comprehensive logging and diagnostics
    """
    
    def __init__(self):
        """Initialize Theory of Change guard with health monitoring."""
        self.health = MethodHealth(
            name="TheoryOfChange",
            status=MethodStatus.UNAVAILABLE
        )
        self._teoria_cambio_class = None
        self._validacion_resultado_class = None
        self._dag_validator_class = None
        self._initialize_methods()
    
    def _initialize_methods(self) -> None:
        """
        Initialize Theory of Change methods with comprehensive error handling.
        
        AUDIT POINT 1: Instantaneous Readiness Check
        All dependencies validated upfront before any runtime invocation.
        """
        try:
            from methods_dispensary.teoria_cambio import (
                TeoriaCambio,
                ValidacionResultado,
                AdvancedDAGValidator,
            )
            
            self._teoria_cambio_class = TeoriaCambio
            self._validacion_resultado_class = ValidacionResultado
            self._dag_validator_class = AdvancedDAGValidator
            
            # Validate that key methods exist
            if not hasattr(TeoriaCambio, 'construir_grafo_causal'):
                raise AttributeError("TeoriaCambio missing construir_grafo_causal method")
            if not hasattr(TeoriaCambio, 'validacion_completa'):
                raise AttributeError("TeoriaCambio missing validacion_completa method")
            
            self.health.status = MethodStatus.AVAILABLE
            logger.info("✓ Theory of Change methods initialized successfully")
        
        except ImportError as e:
            self.health.status = MethodStatus.UNAVAILABLE
            self.health.record_failure(str(e), FailureCategory.IMPORT_ERROR)
            logger.error(f"✗ Theory of Change import failed: {e}")
        
        except AttributeError as e:
            self.health.status = MethodStatus.DEGRADED
            self.health.record_failure(str(e), FailureCategory.VALIDATION_ERROR)
            logger.error(f"✗ Theory of Change validation failed: {e}")
        
        except Exception as e:
            self.health.status = MethodStatus.UNAVAILABLE
            self.health.record_failure(str(e), FailureCategory.RUNTIME_ERROR)
            logger.error(f"✗ Theory of Change initialization failed: {e}")
    
    def create_teoria_cambio_instance(self) -> GuardedInvocation:
        """
        Create TeoriaCambio instance with guards.
        
        Returns:
            GuardedInvocation with TeoriaCambio instance or None
        """
        start_time = time.time()
        
        if not self.health.is_available():
            return GuardedInvocation(
                success=False,
                result=None,
                error=f"Method unavailable: {self.health.status.name}",
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="create_teoria_cambio_instance"
            )
        
        try:
            if self._teoria_cambio_class is None:
                raise RuntimeError("TeoriaCambio not initialized")
            
            instance = self._teoria_cambio_class()
            self.health.record_success()
            
            return GuardedInvocation(
                success=True,
                result=instance,
                execution_time=time.time() - start_time,
                method_name="create_teoria_cambio_instance"
            )
        
        except Exception as e:
            self.health.record_failure(str(e), FailureCategory.RUNTIME_ERROR)
            logger.error(f"create_teoria_cambio_instance failed: {e}\n{traceback.format_exc()}")
            
            return GuardedInvocation(
                success=False,
                result=None,
                error=str(e),
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="create_teoria_cambio_instance"
            )
    
    def validate_causal_dag(
        self,
        teoria_cambio_instance: Any,
        dag: Any
    ) -> GuardedInvocation:
        """
        Validate causal DAG with comprehensive guards.
        
        Args:
            teoria_cambio_instance: TeoriaCambio instance
            dag: NetworkX DiGraph to validate
        
        Returns:
            GuardedInvocation with ValidacionResultado or degraded result
        """
        start_time = time.time()
        
        # Fallback result
        fallback_result = {
            "es_valida": False,
            "violaciones_orden": [],
            "caminos_completos": [],
            "categorias_faltantes": [],
            "sugerencias": ["DEGRADED: Theory of Change unavailable"],
            "degraded": True
        }
        
        if not self.health.is_available():
            return GuardedInvocation(
                success=False,
                result=fallback_result,
                error=f"Method unavailable: {self.health.status.name}",
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="validate_causal_dag"
            )
        
        # Input validation
        if teoria_cambio_instance is None:
            return GuardedInvocation(
                success=False,
                result=fallback_result,
                error="teoria_cambio_instance is None",
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="validate_causal_dag"
            )
        
        if dag is None:
            return GuardedInvocation(
                success=False,
                result=fallback_result,
                error="dag is None",
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="validate_causal_dag"
            )
        
        # Protected invocation
        try:
            result = teoria_cambio_instance.validacion_completa(dag)
            self.health.record_success()
            
            return GuardedInvocation(
                success=True,
                result=result,
                execution_time=time.time() - start_time,
                method_name="validate_causal_dag"
            )
        
        except Exception as e:
            self.health.record_failure(str(e), FailureCategory.RUNTIME_ERROR)
            logger.error(f"validate_causal_dag failed: {e}\n{traceback.format_exc()}")
            
            return GuardedInvocation(
                success=False,
                result=fallback_result,
                error=str(e),
                fallback_used=True,
                execution_time=time.time() - start_time,
                method_name="validate_causal_dag"
            )
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report for diagnostics."""
        return {
            "name": self.health.name,
            "status": self.health.status.name,
            "is_available": self.health.is_available(),
            "success_count": self.health.success_count,
            "failure_count": self.health.failure_count,
            "last_success": self.health.last_success,
            "last_failure": self.health.last_failure,
            "recent_errors": self.health.errors[-5:],  # Last 5 errors
            "circuit_breaker_threshold": self.health.circuit_breaker_threshold,
            "circuit_breaker_timeout": self.health.circuit_breaker_timeout,
        }


# ============================================================================
# GLOBAL GUARD INSTANCES (SINGLETONS)
# ============================================================================

# Initialize guards as module-level singletons
_derek_beach_guard: Optional[DerekBeachGuard] = None
_theory_of_change_guard: Optional[TheoryOfChangeGuard] = None


def get_derek_beach_guard() -> DerekBeachGuard:
    """Get or create Derek Beach guard singleton."""
    global _derek_beach_guard
    if _derek_beach_guard is None:
        _derek_beach_guard = DerekBeachGuard()
    return _derek_beach_guard


def get_theory_of_change_guard() -> TheoryOfChangeGuard:
    """Get or create Theory of Change guard singleton."""
    global _theory_of_change_guard
    if _theory_of_change_guard is None:
        _theory_of_change_guard = TheoryOfChangeGuard()
    return _theory_of_change_guard


# ============================================================================
# CONVENIENCE FUNCTIONS FOR PHASE 1 INTEGRATION
# ============================================================================

def safe_classify_beach_test(
    necessity: float,
    sufficiency: float,
    fallback: str = "straw_in_wind"
) -> Tuple[str, bool]:
    """
    Safely classify Beach evidential test with automatic fallback.
    
    Returns:
        (test_type, is_production) - test_type and whether production method was used
    """
    guard = get_derek_beach_guard()
    invocation = guard.classify_evidential_test(necessity, sufficiency, fallback)
    return (invocation.result, not invocation.fallback_used)


def safe_validate_teoria_cambio(
    dag: Any
) -> Tuple[Dict[str, Any], bool]:
    """
    Safely validate Theory of Change DAG with automatic fallback.
    
    Returns:
        (result_dict, is_production) - validation result and whether production method was used
    """
    guard = get_theory_of_change_guard()
    
    # First, create instance
    create_result = guard.create_teoria_cambio_instance()
    if not create_result.success:
        return (create_result.result or {}, False)
    
    # Then validate
    validate_result = guard.validate_causal_dag(create_result.result, dag)
    
    # Convert ValidacionResultado to dict if needed
    result = validate_result.result
    if hasattr(result, '__dict__'):
        result = {
            'es_valida': getattr(result, 'es_valida', False),
            'violaciones_orden': getattr(result, 'violaciones_orden', []),
            'caminos_completos': getattr(result, 'caminos_completos', []),
            'categorias_faltantes': getattr(result, 'categorias_faltantes', []),
            'sugerencias': getattr(result, 'sugerencias', []),
            'degraded': False
        }
    
    return (result, not validate_result.fallback_used)


def get_all_health_reports() -> Dict[str, Dict[str, Any]]:
    """Get health reports for all guards."""
    return {
        "derek_beach": get_derek_beach_guard().get_health_report(),
        "theory_of_change": get_theory_of_change_guard().get_health_report(),
    }


# ============================================================================
# DIAGNOSTIC UTILITIES
# ============================================================================

def run_comprehensive_diagnostics() -> Dict[str, Any]:
    """
    Run comprehensive diagnostics on all Phase 1 methods.
    
    Returns:
        Detailed diagnostic report
    """
    logger.info("=" * 80)
    logger.info("PHASE 1 METHOD GUARDS COMPREHENSIVE DIAGNOSTICS")
    logger.info("=" * 80)
    
    report = {
        "timestamp": time.time(),
        "guards": get_all_health_reports(),
        "overall_status": "HEALTHY",
        "recommendations": []
    }
    
    # Check Derek Beach
    db_guard = get_derek_beach_guard()
    if not db_guard.health.is_available():
        report["overall_status"] = "DEGRADED"
        report["recommendations"].append(
            "Derek Beach methods unavailable - install methods_dispensary.derek_beach"
        )
    
    # Check Theory of Change
    toc_guard = get_theory_of_change_guard()
    if not toc_guard.health.is_available():
        report["overall_status"] = "DEGRADED"
        report["recommendations"].append(
            "Theory of Change methods unavailable - install methods_dispensary.teoria_cambio"
        )
    
    # Log summary
    logger.info(f"Overall Status: {report['overall_status']}")
    logger.info(f"Derek Beach: {db_guard.health.status.name} ({db_guard.health.success_count} successes, {db_guard.health.failure_count} failures)")
    logger.info(f"Theory of Change: {toc_guard.health.status.name} ({toc_guard.health.success_count} successes, {toc_guard.health.failure_count} failures)")
    
    if report["recommendations"]:
        logger.warning("Recommendations:")
        for rec in report["recommendations"]:
            logger.warning(f"  - {rec}")
    
    logger.info("=" * 80)
    
    return report


if __name__ == "__main__":
    # Run diagnostics if executed directly
    run_comprehensive_diagnostics()
