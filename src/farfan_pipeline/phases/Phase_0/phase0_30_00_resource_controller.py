"""
Module: src.farfan_pipeline.phases.Phase_0.phase0_30_00_resource_controller
PHASE_LABEL: Phase 0
Purpose: Hard kernel-level resource enforcement for Phase Zero
Owner: phase0_resources
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-29

Prevents OOM kills and runaway processes at OS level.
This module provides the LAST LINE OF DEFENSE against resource exhaustion.
It uses kernel-level primitives (resource.setrlimit) that CANNOT be bypassed
by Python code.

ARCHITECTURE:
    ResourceLimits: Dataclass defining hard limits
    ResourceExhausted: Exception for pre-flight failures
    MemoryWatchdog: Background thread for early warnings
    ResourceController: Main enforcement engine with context manager

USAGE:
    controller = ResourceController(ResourceLimits(memory_mb=2048))
    with controller.enforced_execution():
        # Your code runs with kernel-enforced limits
        run_pipeline()

Determinism:
    Seed-Strategy: NOT_APPLICABLE
    State-Management: Thread-safe with locks

Inputs:
    - ResourceLimits: Dataclass with memory_mb, cpu_seconds, disk_mb, file_descriptors

Outputs:
    - EnforcementMetrics: Dataclass with execution metrics

Failure-Modes:
    - ResourceExhausted: Pre-flight checks fail (insufficient resources)
    - MemoryError: Kernel limit exceeded during execution
    - RuntimeError: Enforcement already active (re-entry attempt)
"""

from __future__ import annotations

import logging
import resource
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator

logger = logging.getLogger(__name__)

# Optional psutil import with fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - resource monitoring degraded")


@dataclass(frozen=True)
class ResourceLimits:
    """
    Kernel-level resource limits with hard enforcement.

    Degradation Instance: 8
    Pattern: MEMORY_GUARD
    Fallback Behavior: Pre-flight check fails -> ResourceExhausted exception
    Recovery: Process SIGKILL if limits exceeded (no graceful recovery)

    These limits are NON-NEGOTIABLE once set. The kernel will SIGKILL
    the process if they are exceeded.

    Attributes:
        memory_mb: Maximum address space in megabytes (RLIMIT_AS)
        cpu_seconds: Maximum CPU time in seconds (RLIMIT_CPU)
        disk_mb: Minimum required disk space in /tmp
        file_descriptors: Maximum open file descriptors (RLIMIT_NOFILE)
    """
    memory_mb: int = 2048
    cpu_seconds: int = 300
    disk_mb: int = 500
    file_descriptors: int = 1024

    def __post_init__(self) -> None:
        if self.memory_mb < 256:
            raise ValueError(f"memory_mb must be >= 256, got {self.memory_mb}")
        if self.cpu_seconds < 10:
            raise ValueError(f"cpu_seconds must be >= 10, got {self.cpu_seconds}")
        if self.disk_mb < 50:
            raise ValueError(f"disk_mb must be >= 50, got {self.disk_mb}")
        if self.file_descriptors < 64:
            raise ValueError(f"file_descriptors must be >= 64, got {self.file_descriptors}")


class ResourceExhausted(Exception):
    """Raised when resource pre-flight checks fail.
    
    This exception indicates that the system does not have sufficient
    resources to safely execute the pipeline. The operation should be
    aborted or retried when resources become available.
    """
    
    def __init__(self, message: str, resource_type: str = "unknown") -> None:
        super().__init__(message)
        self.resource_type = resource_type


class MemoryWatchdog(threading.Thread):
    """Background thread monitoring memory pressure.
    
    This watchdog provides EARLY WARNING before hitting hard limits.
    It does NOT prevent OOM - it only logs warnings for observability.
    
    Attributes:
        threshold_percent: Memory usage percentage to trigger warnings
        check_interval: Seconds between checks
        triggered_count: Number of times threshold was exceeded
    """
    
    def __init__(
        self,
        threshold_percent: int = 90,
        check_interval: float = 1.0,
    ) -> None:
        if not isinstance(threshold_percent, int):
            raise TypeError(f"threshold_percent must be int, got {type(threshold_percent).__name__}")
        if not isinstance(check_interval, (int, float)):
            raise TypeError(f"check_interval must be int or float, got {type(check_interval).__name__}")
        super().__init__(daemon=True, name="MemoryWatchdog")
        self.threshold_percent = threshold_percent
        self.check_interval = check_interval
        self._stop_event = threading.Event()
        self.triggered_count = 0
        self.peak_memory_percent: float = 0.0
        self._lock = threading.Lock()
        
    def run(self) -> None:
        """Main watchdog loop - monitors memory continuously."""
        if not PSUTIL_AVAILABLE:
            logger.warning("MemoryWatchdog disabled - psutil not available")
            return
            
        while not self._stop_event.is_set():
            try:
                mem = psutil.virtual_memory()
                
                with self._lock:
                    if mem.percent > self.peak_memory_percent:
                        self.peak_memory_percent = mem.percent
                
                if mem.percent > self.threshold_percent:
                    with self._lock:
                        self.triggered_count += 1
                    logger.critical(
                        "MEMORY CRITICAL: %.1f%% used (%.2fGB/%.2fGB) - trigger #%d",
                        mem.percent,
                        mem.used / (1024**3),
                        mem.total / (1024**3),
                        self.triggered_count,
                    )
            except Exception as e:
                logger.warning("Watchdog check failed: %s", e)
                
            self._stop_event.wait(self.check_interval)
    
    def stop(self) -> None:
        """Stop the watchdog thread gracefully."""
        self._stop_event.set()
        self.join(timeout=2.0)
        
    def get_stats(self) -> dict[str, Any]:
        """Get watchdog statistics."""
        with self._lock:
            return {
                "triggered_count": self.triggered_count,
                "peak_memory_percent": self.peak_memory_percent,
                "threshold_percent": self.threshold_percent,
            }


@dataclass
class EnforcementMetrics:
    """Metrics collected during enforced execution."""
    
    preflight_memory_mb: float = 0.0
    preflight_disk_mb: float = 0.0
    peak_memory_mb: float = 0.0
    total_cpu_seconds: float = 0.0
    watchdog_triggers: int = 0
    enforcement_duration_s: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "preflight_memory_mb": round(self.preflight_memory_mb, 2),
            "preflight_disk_mb": round(self.preflight_disk_mb, 2),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "total_cpu_seconds": round(self.total_cpu_seconds, 2),
            "watchdog_triggers": self.watchdog_triggers,
            "enforcement_duration_s": round(self.enforcement_duration_s, 3),
        }


class ResourceController:
    """Hard enforcement of resource limits using kernel primitives.
    
    This is the LAST LINE OF DEFENSE against OOM kills and runaway processes.
    It uses resource.setrlimit() which is enforced by the kernel and CANNOT
    be bypassed by Python code.
    
    PATTERNS IMPLEMENTED:
        - Resource Acquisition Is Initialization (RAII): Context manager guarantees cleanup
        - Watchdog Pattern: Background thread for early warnings
        - Fail-Fast: Pre-flight checks prevent doomed execution
        
    USAGE:
        controller = ResourceController(ResourceLimits(memory_mb=2048))
        with controller.enforced_execution() as ctx:
            # Code runs with hard limits
            result = run_analysis()
        # Limits automatically restored
        
    WARNING:
        Setting RLIMIT_AS too low can cause immediate allocation failures.
        The default 2GB is appropriate for most workloads.
    """
    
    def __init__(self, limits: ResourceLimits | None = None) -> None:
        self.limits = limits or ResourceLimits()
        self._watchdog: MemoryWatchdog | None = None
        self._enforcement_active = False
        self._original_limits: dict[str, tuple[int, int]] = {}
        self._limits_applied: dict[str, bool] = {}
        self._start_time: float = 0.0
        self._metrics = EnforcementMetrics()
        self._lock = threading.Lock()
        
    @property
    def is_active(self) -> bool:
        """Check if enforcement is currently active."""
        with self._lock:
            return self._enforcement_active
        
    def preflight_checks(self) -> dict[str, Any]:
        """Pre-execution resource availability checks.
        
        Returns:
            Dictionary of resource availability metrics
            
        Raises:
            ResourceExhausted: If insufficient resources available
        """
        checks: dict[str, Any] = {
            "memory_available_mb": 0.0,
            "disk_available_mb": 0.0,
            "cpu_count": 1,
            "open_files": 0,
            "psutil_available": PSUTIL_AVAILABLE,
        }
        
        if PSUTIL_AVAILABLE:
            checks["memory_available_mb"] = psutil.virtual_memory().available / (1024**2)
            checks["disk_available_mb"] = psutil.disk_usage('/tmp').free / (1024**2)
            checks["cpu_count"] = psutil.cpu_count() or 1
            try:
                checks["open_files"] = len(psutil.Process().open_files())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                checks["open_files"] = 0
        else:
            # Fallback: use resource module for basic checks
            import os
            stat = os.statvfs('/tmp')
            checks["disk_available_mb"] = (stat.f_bavail * stat.f_frsize) / (1024**2)
            checks["cpu_count"] = os.cpu_count() or 1
        
        # Store preflight metrics
        self._metrics.preflight_memory_mb = checks["memory_available_mb"]
        self._metrics.preflight_disk_mb = checks["disk_available_mb"]
        
        # Fail fast if insufficient resources
        if PSUTIL_AVAILABLE and checks["memory_available_mb"] < self.limits.memory_mb * 0.5:
            raise ResourceExhausted(
                f"Insufficient memory: {checks['memory_available_mb']:.1f}MB available "
                f"< {self.limits.memory_mb * 0.5:.1f}MB required (50% of limit)",
                resource_type="memory",
            )
            
        if checks["disk_available_mb"] < self.limits.disk_mb:
            raise ResourceExhausted(
                f"Insufficient disk: {checks['disk_available_mb']:.1f}MB available "
                f"< {self.limits.disk_mb}MB required",
                resource_type="disk",
            )
            
        logger.info("Pre-flight checks PASSED: %s", checks)
        return checks
    
    def _set_kernel_limits(self) -> None:
        """Set hard limits via kernel (resource.setrlimit).
        
        NOTE: Kernel only allows LOWERING limits, not raising them.
        We track which limits were actually changed for restoration.
        """
        # Store original limits
        self._original_limits['as'] = resource.getrlimit(resource.RLIMIT_AS)
        self._original_limits['cpu'] = resource.getrlimit(resource.RLIMIT_CPU)
        self._original_limits['nofile'] = resource.getrlimit(resource.RLIMIT_NOFILE)
        
        # Track which limits were actually set (for proper restoration)
        self._limits_applied: dict[str, bool] = {}
        
        # Set address space limit (memory) - only if lower than current
        memory_bytes = self.limits.memory_mb * 1024 * 1024
        current_as_soft, current_as_hard = self._original_limits['as']
        if current_as_hard == -1 or memory_bytes < current_as_hard:
            try:
                # Set soft limit only, keep hard limit unchanged if possible
                new_hard = memory_bytes if current_as_hard == -1 else min(memory_bytes, current_as_hard)
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, new_hard))
                self._limits_applied['as'] = True
                logger.debug("RLIMIT_AS set to %d bytes", memory_bytes)
            except (ValueError, OSError) as e:
                self._limits_applied['as'] = False
                logger.warning("Could not set RLIMIT_AS: %s", e)
        else:
            self._limits_applied['as'] = False
            logger.debug("RLIMIT_AS not lowered (current=%d, requested=%d)", current_as_hard, memory_bytes)
        
        # Set CPU time limit
        current_cpu_soft, current_cpu_hard = self._original_limits['cpu']
        if current_cpu_hard == -1 or self.limits.cpu_seconds < current_cpu_hard:
            try:
                new_hard = self.limits.cpu_seconds if current_cpu_hard == -1 else min(self.limits.cpu_seconds, current_cpu_hard)
                resource.setrlimit(
                    resource.RLIMIT_CPU,
                    (self.limits.cpu_seconds, new_hard),
                )
                self._limits_applied['cpu'] = True
                logger.debug("RLIMIT_CPU set to %d seconds", self.limits.cpu_seconds)
            except (ValueError, OSError) as e:
                self._limits_applied['cpu'] = False
                logger.warning("Could not set RLIMIT_CPU: %s", e)
        else:
            self._limits_applied['cpu'] = False
        
        # Set file descriptor limit - only lower soft limit
        current_nofile_soft, current_nofile_hard = self._original_limits['nofile']
        if self.limits.file_descriptors <= current_nofile_hard:
            try:
                resource.setrlimit(
                    resource.RLIMIT_NOFILE,
                    (self.limits.file_descriptors, current_nofile_hard),
                )
                self._limits_applied['nofile'] = True
                logger.debug("RLIMIT_NOFILE soft set to %d", self.limits.file_descriptors)
            except (ValueError, OSError) as e:
                self._limits_applied['nofile'] = False
                logger.warning("Could not set RLIMIT_NOFILE: %s", e)
        else:
            self._limits_applied['nofile'] = False
    
    def _restore_kernel_limits(self) -> None:
        """Restore original kernel limits where possible.
        
        NOTE: We can only restore soft limits up to the hard limit.
        Hard limits cannot be raised once lowered.
        """
        for limit_name, (orig_soft, orig_hard) in self._original_limits.items():
            # Only restore if we actually changed this limit
            if not self._limits_applied.get(limit_name, False):
                continue
                
            try:
                if limit_name == 'as':
                    # Get current hard limit (may have been lowered)
                    _, current_hard = resource.getrlimit(resource.RLIMIT_AS)
                    # Restore soft to min of original and current hard
                    restore_soft = orig_soft if orig_soft == -1 else min(orig_soft, current_hard) if current_hard != -1 else orig_soft
                    resource.setrlimit(resource.RLIMIT_AS, (restore_soft, current_hard))
                elif limit_name == 'cpu':
                    _, current_hard = resource.getrlimit(resource.RLIMIT_CPU)
                    restore_soft = orig_soft if orig_soft == -1 else min(orig_soft, current_hard) if current_hard != -1 else orig_soft
                    resource.setrlimit(resource.RLIMIT_CPU, (restore_soft, current_hard))
                elif limit_name == 'nofile':
                    _, current_hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                    restore_soft = min(orig_soft, current_hard)
                    resource.setrlimit(resource.RLIMIT_NOFILE, (restore_soft, current_hard))
                    
                logger.debug("Restored %s soft limit", limit_name)
            except (ValueError, OSError) as e:
                # This is expected if hard limit was lowered
                logger.debug("Could not fully restore %s limit: %s", limit_name, e)
        
        self._original_limits.clear()
        self._limits_applied = {}
    
    @contextmanager
    def enforced_execution(self) -> Generator[ResourceController, None, None]:
        """Context manager enforcing hard resource limits.
        
        Uses kernel-level enforcement that CANNOT be bypassed by Python code.
        Guarantees cleanup even if exceptions occur.
        
        Yields:
            Self for access to metrics and stats
            
        Raises:
            RuntimeError: If enforcement already active
            ResourceExhausted: If pre-flight checks fail
        """
        with self._lock:
            if self._enforcement_active:
                raise RuntimeError("Resource enforcement already active")
            self._enforcement_active = True
        
        self._start_time = time.perf_counter()
        
        try:
            # Pre-flight checks
            self.preflight_checks()
            
            # Set kernel limits
            self._set_kernel_limits()
            
            # Start memory watchdog
            self._watchdog = MemoryWatchdog(threshold_percent=90)
            self._watchdog.start()
            
            logger.info(
                "Resource enforcement ACTIVE: memory=%dMB, cpu=%ds, fds=%d",
                self.limits.memory_mb,
                self.limits.cpu_seconds,
                self.limits.file_descriptors,
            )
            
            yield self
            
        finally:
            # Calculate duration
            self._metrics.enforcement_duration_s = time.perf_counter() - self._start_time
            
            # Stop watchdog and collect metrics
            if self._watchdog is not None:
                self._watchdog.stop()
                stats = self._watchdog.get_stats()
                self._metrics.watchdog_triggers = stats["triggered_count"]
                self._metrics.peak_memory_mb = stats["peak_memory_percent"]
                
                if stats["triggered_count"] > 0:
                    logger.warning(
                        "Watchdog triggered %d times during execution",
                        stats["triggered_count"],
                    )
                self._watchdog = None
            
            # Restore original limits
            self._restore_kernel_limits()
            
            with self._lock:
                self._enforcement_active = False
            
            logger.info(
                "Resource enforcement RELEASED after %.3fs",
                self._metrics.enforcement_duration_s,
            )
    
    def get_usage_stats(self) -> dict[str, Any]:
        """Current resource usage snapshot.
        
        Returns:
            Dictionary with current resource usage metrics
        """
        stats: dict[str, Any] = {
            "enforcement_active": self._enforcement_active,
            "limits": {
                "memory_mb": self.limits.memory_mb,
                "cpu_seconds": self.limits.cpu_seconds,
                "disk_mb": self.limits.disk_mb,
                "file_descriptors": self.limits.file_descriptors,
            },
        }
        
        if PSUTIL_AVAILABLE:
            try:
                proc = psutil.Process()
                mem_info = proc.memory_info()
                cpu_times = proc.cpu_times()
                
                stats["current"] = {
                    "memory_rss_mb": mem_info.rss / (1024**2),
                    "memory_percent": proc.memory_percent(),
                    "cpu_percent": proc.cpu_percent(interval=0.1),
                    "cpu_time_user_s": cpu_times.user,
                    "cpu_time_system_s": cpu_times.system,
                    "cpu_time_total_s": cpu_times.user + cpu_times.system,
                    "num_threads": proc.num_threads(),
                }
                
                # Platform-specific: num_fds on Unix
                if hasattr(proc, 'num_fds'):
                    stats["current"]["num_fds"] = proc.num_fds()
                else:
                    try:
                        stats["current"]["num_fds"] = len(proc.open_files())
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        stats["current"]["num_fds"] = -1
                        
            except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                stats["current"] = {"error": str(e)}
        else:
            stats["current"] = {"psutil_available": False}
        
        return stats
    
    def get_metrics(self) -> EnforcementMetrics:
        """Get enforcement metrics collected during execution."""
        return self._metrics


__all__ = [
    "ResourceLimits",
    "ResourceExhausted",
    "MemoryWatchdog",
    "ResourceController",
    "EnforcementMetrics",
    "PSUTIL_AVAILABLE",
]
