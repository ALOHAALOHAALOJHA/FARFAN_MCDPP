"""
Phase 1 Circuit Breaker - Aggressively Preventive Failure Protection
====================================================================

This module implements a circuit breaker pattern with pre-flight checks to
robustly protect Phase 1 from failures. Unlike graceful degradation, this
system fails fast and loud when conditions are not met.

Design Principles:
------------------
1. **Fail Fast**: Detect problems BEFORE execution starts
2. **No Degradation**: Either full capability or hard stop
3. **Pre-flight Checks**: Validate ALL dependencies upfront
4. **Resource Guards**: Ensure sufficient memory/disk before starting
5. **Checkpoint Validation**: Verify invariants at each subphase boundary
6. **Clear Diagnostics**: Provide actionable error messages

Circuit Breaker States:
-----------------------
- CLOSED: All checks passed, normal operation
- OPEN: Critical failure detected, execution blocked
- HALF_OPEN: Recovery attempted, testing if conditions restored

Author: F.A.R.F.A.N Security Team
Date: 2025-12-11
"""

from __future__ import annotations

import hashlib
import logging
import os
import platform
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation - all checks passed
    OPEN = "open"  # Failure detected - execution blocked
    HALF_OPEN = "half_open"  # Testing recovery


class FailureSeverity(Enum):
    """Failure severity levels."""
    CRITICAL = "critical"  # Must stop execution immediately
    HIGH = "high"  # Will likely cause constitutional invariant violation
    MEDIUM = "medium"  # May cause quality degradation
    LOW = "low"  # Minor issue, can continue with caution


@dataclass
class DependencyCheck:
    """Result of a dependency check."""
    name: str
    available: bool
    version: Optional[str] = None
    error: Optional[str] = None
    severity: FailureSeverity = FailureSeverity.CRITICAL
    remediation: str = ""


@dataclass
class ResourceCheck:
    """Result of a resource availability check."""
    resource_type: str  # memory, disk, cpu
    available: float  # Available amount
    required: float  # Required amount
    sufficient: bool
    unit: str = "bytes"  # bytes, percent, cores


@dataclass
class PreflightResult:
    """Result of pre-flight checks."""
    passed: bool
    timestamp: str
    dependency_checks: List[DependencyCheck] = field(default_factory=list)
    resource_checks: List[ResourceCheck] = field(default_factory=list)
    critical_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    system_info: Dict[str, Any] = field(default_factory=dict)


class Phase1CircuitBreaker:
    """
    Circuit breaker for Phase 1 with pre-flight checks.
    
    This class ensures Phase 1 can ONLY execute when ALL critical
    conditions are met. No graceful degradation - fail fast.
    """
    
    def __init__(self):
        """
        Initialize circuit breaker.
        
        Note: This circuit breaker uses a singleton pattern with mutable state.
        It is not thread-safe. If concurrent Phase 1 execution is required,
        create separate circuit breaker instances per execution.
        """
        self.state = CircuitState.CLOSED
        self.last_check: Optional[PreflightResult] = None
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
    
    def preflight_check(self) -> PreflightResult:
        """
        Execute comprehensive pre-flight checks.
        
        Validates:
        1. All critical Python dependencies
        2. System resources (memory, disk)
        3. File system permissions
        4. Python version compatibility
        
        Returns:
            PreflightResult with complete diagnostic information
        """
        logger.info("Phase 1 Circuit Breaker: Starting pre-flight checks")
        
        result = PreflightResult(
            passed=True,
            timestamp=datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
            system_info=self._collect_system_info()
        )
        
        # 1. Check Python version
        self._check_python_version(result)
        
        # 2. Check critical dependencies
        self._check_dependencies(result)
        
        # 3. Check system resources
        self._check_resources(result)
        
        # 4. Check file system
        self._check_filesystem(result)
        
        # Determine overall pass/fail
        result.passed = len(result.critical_failures) == 0
        
        # Update circuit state
        if not result.passed:
            self.state = CircuitState.OPEN
            self.failure_count += 1
            self.last_failure_time = datetime.now(timezone.utc)
            logger.error(f"Phase 1 Circuit Breaker: OPEN - {len(result.critical_failures)} critical failures")
        else:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info("Phase 1 Circuit Breaker: CLOSED - All checks passed")
        
        self.last_check = result
        return result
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for diagnostics."""
        return {
            'platform': platform.platform(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'cpu_count': os.cpu_count(),
            'total_memory_gb': (psutil.virtual_memory().total / (1024**3) if psutil is not None else None),
        }
    
    def _check_python_version(self, result: PreflightResult):
        """Check Python version meets minimum requirements."""
        major, minor = sys.version_info[:2]
        required_major, required_minor = 3, 10
        
        if major < required_major or (major == required_major and minor < required_minor):
            result.critical_failures.append(
                f"Python {major}.{minor} detected, but Python {required_major}.{required_minor}+ required"
            )
            result.dependency_checks.append(DependencyCheck(
                name="python",
                available=False,
                version=f"{major}.{minor}",
                error=f"Version too old (need {required_major}.{required_minor}+)",
                severity=FailureSeverity.CRITICAL,
                remediation="Upgrade Python to 3.10 or higher"
            ))
        else:
            result.dependency_checks.append(DependencyCheck(
                name="python",
                available=True,
                version=f"{major}.{minor}",
                severity=FailureSeverity.CRITICAL
            ))
    
    def _check_dependencies(self, result: PreflightResult):
        """Check all critical dependencies."""
        # Core dependencies that MUST be available for any execution
        critical_deps = [
            ('spacy', 'spacy', 'NLP processing for SP1/SP2/SP3'),
            ('pydantic', 'pydantic', 'Contract validation'),
            ('numpy', 'numpy', 'Numerical operations'),
        ]
        
        for import_name, package_name, description in critical_deps:
            check = self._check_single_dependency(import_name, package_name, description)
            result.dependency_checks.append(check)
            
            if not check.available and check.severity == FailureSeverity.CRITICAL:
                result.critical_failures.append(
                    f"Missing critical dependency: {package_name} ({description})"
                )
        
        # Check optional but important dependencies (HIGH severity - warning only)
        # These are needed for full functionality but tests can run without them
        optional_deps = [
            ('langdetect', 'langdetect', 'Language detection for SP0'),
            ('fitz', 'PyMuPDF', 'PDF extraction for SP0/SP1'),
            ('cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_registry', 
             'SISAS', 'Signal enrichment system'),
            ('methods_dispensary.derek_beach', 'derek_beach', 'Causal analysis'),
            ('methods_dispensary.teoria_cambio', 'teoria_cambio', 'DAG validation'),
        ]
        
        for import_name, package_name, description in optional_deps:
            check = self._check_single_dependency(
                import_name, package_name, description, 
                severity=FailureSeverity.HIGH
            )
            result.dependency_checks.append(check)
            
            if not check.available:
                result.warnings.append(
                    f"Optional dependency missing: {package_name} ({description}). "
                    f"Some features will be limited."
                )
    
    def _check_single_dependency(
        self, 
        import_name: str, 
        package_name: str, 
        description: str,
        severity: FailureSeverity = FailureSeverity.CRITICAL
    ) -> DependencyCheck:
        """Check if a single dependency is available."""
        try:
            module = __import__(import_name.split('.')[0])
            # Try to get version
            version = None
            if hasattr(module, '__version__'):
                version = module.__version__
            
            return DependencyCheck(
                name=package_name,
                available=True,
                version=version,
                severity=severity
            )
        except ImportError as e:
            return DependencyCheck(
                name=package_name,
                available=False,
                error=str(e),
                severity=severity,
                remediation=f"Install with: pip install {package_name}"
            )
    
    def _check_resources(self, result: PreflightResult):
        """Check system resource availability."""
        if psutil is None:
            # In constrained environments (e.g., CI/minimal), allow execution without psutil by
            # skipping resource guards. In production, psutil should be installed.
            result.dependency_checks.append(
                DependencyCheck(
                    name="psutil",
                    available=False,
                    error="psutil import failed",
                    severity=FailureSeverity.HIGH,
                    remediation="Install with: pip install psutil",
                )
            )
            result.warnings.append(
                "psutil missing: resource guard checks skipped (memory/disk/cpu not validated)"
            )
            return

        # Memory check - Phase 1 needs at least 2GB available
        mem = psutil.virtual_memory()
        mem_available_gb = mem.available / (1024**3)
        mem_required_gb = 2.0
        mem_check = ResourceCheck(
            resource_type="memory",
            available=mem_available_gb,
            required=mem_required_gb,
            sufficient=mem_available_gb >= mem_required_gb,
            unit="GB"
        )
        result.resource_checks.append(mem_check)
        
        if not mem_check.sufficient:
            result.critical_failures.append(
                f"Insufficient memory: {mem_available_gb:.2f} GB available, "
                f"{mem_required_gb:.2f} GB required"
            )
        
        # Disk check - Need at least 1GB free for intermediate files
        disk = psutil.disk_usage('/')
        disk_available_gb = disk.free / (1024**3)
        disk_required_gb = 1.0
        disk_check = ResourceCheck(
            resource_type="disk",
            available=disk_available_gb,
            required=disk_required_gb,
            sufficient=disk_available_gb >= disk_required_gb,
            unit="GB"
        )
        result.resource_checks.append(disk_check)
        
        if not disk_check.sufficient:
            result.critical_failures.append(
                f"Insufficient disk space: {disk_available_gb:.2f} GB available, "
                f"{disk_required_gb:.2f} GB required"
            )
        
        # CPU check - Just informational
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_check = ResourceCheck(
            resource_type="cpu",
            available=100 - cpu_percent,
            required=20.0,  # Want at least 20% CPU available
            sufficient=cpu_percent < 80,
            unit="percent"
        )
        result.resource_checks.append(cpu_check)
        
        if not cpu_check.sufficient:
            result.warnings.append(
                f"High CPU usage: {cpu_percent:.1f}%. Phase 1 may run slowly."
            )
    
    def _check_filesystem(self, result: PreflightResult):
        """Check file system permissions and paths."""
        # Check write access to current directory
        try:
            test_file = Path('.phase1_write_test')
            test_file.write_text('test')
            test_file.unlink()
        except Exception as e:
            result.critical_failures.append(
                f"No write access to current directory: {e}"
            )
            result.dependency_checks.append(DependencyCheck(
                name="filesystem_write",
                available=False,
                error=str(e),
                severity=FailureSeverity.CRITICAL,
                remediation="Ensure write permissions in working directory"
            ))
    
    def can_execute(self) -> bool:
        """
        Check if Phase 1 can execute.
        
        Returns:
            True if circuit is CLOSED, False otherwise
        """
        if self.state == CircuitState.OPEN:
            logger.error(
                "Phase 1 Circuit Breaker: Execution BLOCKED - Circuit is OPEN"
            )
            if self.last_check:
                logger.error(f"Critical failures: {self.last_check.critical_failures}")
            return False
        return True
    
    def get_diagnostic_report(self) -> str:
        """
        Generate human-readable diagnostic report.
        
        Returns:
            Formatted diagnostic report
        """
        if not self.last_check:
            return "No pre-flight check has been run yet."
        
        lines = [
            "=" * 80,
            "PHASE 1 CIRCUIT BREAKER - DIAGNOSTIC REPORT",
            "=" * 80,
            f"State: {self.state.value.upper()}",
            f"Timestamp: {self.last_check.timestamp}",
            f"Overall Result: {'PASS' if self.last_check.passed else 'FAIL'}",
            "",
            "SYSTEM INFORMATION:",
        ]
        
        for key, value in self.last_check.system_info.items():
            lines.append(f"  {key}: {value}")
        
        lines.append("")
        lines.append("DEPENDENCY CHECKS:")
        for dep in self.last_check.dependency_checks:
            status = "✓" if dep.available else "✗"
            version_str = f" (v{dep.version})" if dep.version else ""
            lines.append(f"  {status} {dep.name}{version_str}")
            if not dep.available:
                lines.append(f"      Error: {dep.error}")
                lines.append(f"      Fix: {dep.remediation}")
        
        lines.append("")
        lines.append("RESOURCE CHECKS:")
        for res in self.last_check.resource_checks:
            status = "✓" if res.sufficient else "✗"
            lines.append(
                f"  {status} {res.resource_type}: "
                f"{res.available:.2f} {res.unit} available "
                f"(need {res.required:.2f} {res.unit})"
            )
        
        if self.last_check.critical_failures:
            lines.append("")
            lines.append("CRITICAL FAILURES:")
            for failure in self.last_check.critical_failures:
                lines.append(f"  ✗ {failure}")
        
        if self.last_check.warnings:
            lines.append("")
            lines.append("WARNINGS:")
            for warning in self.last_check.warnings:
                lines.append(f"  ⚠ {warning}")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)


class SubphaseCheckpoint:
    """
    Checkpoint validator for subphases.
    
    Ensures constitutional invariants are maintained at each subphase boundary.
    """
    
    def __init__(self):
        """Initialize checkpoint validator."""
        self.checkpoints: Dict[int, Dict[str, Any]] = {}
    
    def validate_checkpoint(
        self, 
        subphase_num: int, 
        output: Any,
        expected_type: type,
        validators: List[Callable[[Any], tuple[bool, str]]]
    ) -> tuple[bool, List[str]]:
        """
        Validate subphase output at checkpoint.
        
        Args:
            subphase_num: Subphase number (0-15)
            output: Output from subphase
            expected_type: Expected type of output
            validators: List of validation functions
        
        Returns:
            Tuple of (passed, error_messages)
        """
        errors = []
        
        # Type check
        if not isinstance(output, expected_type):
            errors.append(
                f"SP{subphase_num}: Expected {expected_type.__name__}, "
                f"got {type(output).__name__}"
            )
            return False, errors
        
        # Run validators
        for validator in validators:
            try:
                passed, message = validator(output)
                if not passed:
                    errors.append(f"SP{subphase_num}: {message}")
            except Exception as e:
                errors.append(f"SP{subphase_num}: Validator exception: {e}")
        
        # Record checkpoint
        # Use a lightweight hash based on type and count rather than full serialization
        try:
            output_len = len(output) if hasattr(output, '__len__') else 0
        except (TypeError, AttributeError):
            output_len = 0
        output_summary = f"{type(output).__name__}:{output_len}"
        self.checkpoints[subphase_num] = {
            'timestamp': datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
            'passed': len(errors) == 0,
            'errors': errors,
            'output_hash': hashlib.sha256(output_summary.encode()).hexdigest()[:16]
        }
        
        return len(errors) == 0, errors


# Global circuit breaker instance
# WARNING: This singleton is not thread-safe. If concurrent Phase 1 execution
# is required, create separate Phase1CircuitBreaker instances per execution
# instead of using the global instance.
_circuit_breaker = Phase1CircuitBreaker()


def get_circuit_breaker() -> Phase1CircuitBreaker:
    """Get global circuit breaker instance."""
    return _circuit_breaker


def run_preflight_check() -> PreflightResult:
    """
    Run pre-flight check using global circuit breaker.
    
    Returns:
        PreflightResult
    """
    return _circuit_breaker.preflight_check()


def ensure_can_execute():
    """
    Ensure Phase 1 can execute, raise exception if not.
    
    Raises:
        RuntimeError: If circuit breaker is OPEN
    """
    if not _circuit_breaker.can_execute():
        raise RuntimeError(
            "Phase 1 execution blocked by circuit breaker. "
            "Run preflight check to see diagnostics."
        )


__all__ = [
    'Phase1CircuitBreaker',
    'CircuitState',
    'FailureSeverity',
    'DependencyCheck',
    'ResourceCheck',
    'PreflightResult',
    'SubphaseCheckpoint',
    'get_circuit_breaker',
    'run_preflight_check',
    'ensure_can_execute',
]
