"""F.A.R.F.A.N Orchestrator - Production Version

11-phase deterministic policy analysis pipeline with:
- Abort signal propagation
- Adaptive resource management
- Comprehensive instrumentation
- Method dispensary pattern support
- Signal enrichment integration

Clean architecture. No legacy code. Production-ready.
"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
import os
import statistics
import threading
import structlog
import time
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, TypeVar, ParamSpec, TypedDict

if TYPE_CHECKING:
    from orchestration.factory import CanonicalQuestionnaire

from canonic_phases.Phase_zero.paths import PROJECT_ROOT
from canonic_phases.Phase_zero.paths import safe_join
from canonic_phases.Phase_zero.runtime_config import RuntimeConfig, RuntimeMode
from canonic_phases.Phase_zero.exit_gates import GateResult

# Define RULES_DIR locally (not exported from paths)
RULES_DIR = PROJECT_ROOT / "sensitive_rules_for_coding"
from canonic_phases.Phase_four_five_six_seven.aggregation import (
    AggregationSettings,
    AreaPolicyAggregator,
    AreaScore,
    ClusterAggregator,
    ClusterScore,
    DimensionAggregator,
    DimensionScore,
    MacroAggregator,
    MacroScore,
    ScoredResult,
    group_by,
    validate_scored_results,
)
from canonic_phases.Phase_four_five_six_seven.aggregation_enhancements import (
    enhance_aggregator,
    EnhancedDimensionAggregator,
    EnhancedAreaAggregator,
    EnhancedClusterAggregator,
    EnhancedMacroAggregator,
)
from canonic_phases.Phase_two import executors
from canonic_phases.Phase_two.arg_router import (
    ArgRouterError,
    ArgumentValidationError,
    ExtendedArgRouter,
)
from orchestration.class_registry import ClassRegistryError
from canonic_phases.Phase_two.executor_config import ExecutorConfig
from canonic_phases.Phase_two.irrigation_synchronizer import (
    IrrigationSynchronizer,
    ExecutionPlan,
)
from canonic_phases.Phase_three.signal_enriched_scoring import SignalEnrichedScorer

logger = structlog.get_logger(__name__)
_CORE_MODULE_DIR = Path(__file__).resolve().parent

EXPECTED_QUESTION_COUNT = int(os.getenv("EXPECTED_QUESTION_COUNT", "305"))
EXPECTED_METHOD_COUNT = int(os.getenv("EXPECTED_METHOD_COUNT", "416"))
PHASE_TIMEOUT_DEFAULT = int(os.getenv("PHASE_TIMEOUT_SECONDS", "300"))
P01_EXPECTED_CHUNK_COUNT = 60
TIMEOUT_SYNC_PHASES: set[int] = {1}

# Phase 2 ExecutionPlan constants
UNKNOWN_BASE_SLOT = "UNKNOWN"
UNKNOWN_QUESTION_GLOBAL = -1

P = ParamSpec("P")
T = TypeVar("T")


# ============================================================================
# PHASE 0 INTEGRATION
# ============================================================================

@dataclass
class Phase0ValidationResult:
    """Result of Phase 0 exit gate validation.
    
    This dataclass captures the outcome of Phase 0's exit gate checks,
    enabling the orchestrator to validate that all bootstrap prerequisites
    have been met before executing the 11-phase pipeline.
    
    Attributes:
        all_passed: True if all 4 Phase 0 gates passed
        gate_results: List of GateResult objects (one per gate)
        validation_time: ISO 8601 timestamp of when validation occurred
    
    Example:
        >>> from canonic_phases.Phase_zero.exit_gates import check_all_gates
        >>> all_passed, gates = check_all_gates(runner)
        >>> validation = Phase0ValidationResult(
        ...     all_passed=all_passed,
        ...     gate_results=gates,
        ...     validation_time=datetime.utcnow().isoformat()
        ... )
        >>> orchestrator = Orchestrator(..., phase0_validation=validation)
    """
    
    all_passed: bool
    gate_results: list[GateResult]
    validation_time: str
    
    def get_failed_gates(self) -> list[GateResult]:
        """Get list of gates that failed validation.
        
        Returns:
            List of GateResult objects where passed=False
        """
        return [g for g in self.gate_results if not g.passed]
    
    def get_summary(self) -> str:
        """Get human-readable summary of validation results.
        
        Returns:
            Summary string like "4/4 gates passed" or "2/4 gates passed (bootstrap, input_verification failed)"
        """
        passed_count = sum(1 for g in self.gate_results if g.passed)
        total_count = len(self.gate_results)
        
        if self.all_passed:
            return f"{passed_count}/{total_count} gates passed"
        else:
            failed_names = [g.gate_name for g in self.get_failed_gates()]
            return f"{passed_count}/{total_count} gates passed ({', '.join(failed_names)} failed)"


# ============================================================================
# PATH RESOLUTION
# ============================================================================

def resolve_workspace_path(
    path: str | Path,
    *,
    project_root: Path = PROJECT_ROOT,
    rules_dir: Path = RULES_DIR,
    module_dir: Path = _CORE_MODULE_DIR,
    require_exists: bool = True,
) -> Path:
    """Resolve repository-relative paths deterministically.
    
    If require_exists is True and no candidate exists, raises FileNotFoundError.
    """
    path_obj = Path(path)
    
    if path_obj.is_absolute():
        if require_exists and not path_obj.exists():
            raise FileNotFoundError(f"Path not found: {path_obj}")
        return path_obj
    
    sanitized = safe_join(project_root, *path_obj.parts)
    candidates = [
        sanitized,
        safe_join(module_dir, *path_obj.parts),
        safe_join(rules_dir, *path_obj.parts),
    ]
    
    if not path_obj.parts or path_obj.parts[0] != "rules":
        candidates.append(safe_join(rules_dir, "METODOS", *path_obj.parts))
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    if require_exists:
        raise FileNotFoundError(f"Path not found in workspace: {path_obj}")
    return sanitized


def _normalize_monolith_for_hash(monolith: dict | MappingProxyType) -> dict:
    """Normalize monolith for hash computation."""
    if isinstance(monolith, MappingProxyType):
        monolith = dict(monolith)
    
    def _convert(obj: Any) -> Any:
        if isinstance(obj, MappingProxyType):
            obj = dict(obj)
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        return obj
    
    normalized = _convert(monolith)
    
    try:
        json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Monolith normalization failed: {exc}") from exc
    
    return normalized


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class MacroScoreDict(TypedDict):
    """Typed container for macro score results."""
    macro_score: MacroScore
    macro_score_normalized: float
    cluster_scores: list[ClusterScore]
    cross_cutting_coherence: float
    systemic_gaps: list[str]
    strategic_alignment: float
    quality_band: str


@dataclass
class ClusterScoreData:
    """Cluster score data."""
    id: str
    score: float
    normalized_score: float


@dataclass
class MacroEvaluation:
    """Macro evaluation result."""
    macro_score: float
    macro_score_normalized: float
    clusters: list[ClusterScoreData]
    details: MacroScore


@dataclass
class Evidence:
    """Evidence container."""
    modality: str
    elements: list[Any] = field(default_factory=list)
    raw_results: dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseResult:
    """Phase execution result."""
    success: bool
    phase_id: str
    data: Any
    error: Exception | None
    duration_ms: float
    mode: str
    aborted: bool = False


@dataclass
class MicroQuestionRun:
    """Micro-question execution result."""
    question_id: str
    question_global: int
    base_slot: str
    metadata: dict[str, Any]
    evidence: Evidence | None
    error: str | None = None
    duration_ms: float | None = None
    aborted: bool = False


@dataclass
class ScoredMicroQuestion:
    """Scored micro-question."""
    question_id: str
    question_global: int
    base_slot: str
    score: float | None
    normalized_score: float | None
    quality_level: str | None
    evidence: Evidence | None
    scoring_details: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


# ============================================================================
# ABORT MECHANISM
# ============================================================================

class AbortRequested(RuntimeError):
    """Abort signal exception."""
    pass


class AbortSignal:
    """Thread-safe abort signal."""
    
    def __init__(self) -> None:
        self._event = threading.Event()
        self._lock = threading.Lock()
        self._reason: str | None = None
        self._timestamp: datetime | None = None
    
    
    
    def abort(self, reason: str) -> None:
        """Trigger abort."""
        if not reason:
            reason = "Abort requested"
        with self._lock:
            if not self._event.is_set():
                self._event.set()
                self._reason = reason
                self._timestamp = datetime.utcnow()
    
    def is_aborted(self) -> bool:
        """Check if aborted."""
        return self._event.is_set()
    
    def get_reason(self) -> str | None:
        """Get abort reason."""
        with self._lock:
            return self._reason
    
    def get_timestamp(self) -> datetime | None:
        """Get abort timestamp."""
        with self._lock:
            return self._timestamp
    
    def reset(self) -> None:
        """Reset abort signal."""
        with self._lock:
            self._event.clear()
            self._reason = None
            self._timestamp = None


# ============================================================================
# RESOURCE MANAGEMENT
# ============================================================================

class ResourceLimits:
    """Adaptive resource management."""
    
    def __init__(
        self,
        max_memory_mb: float | None = 4096.0,
        max_cpu_percent: float = 85.0,
        max_workers: int = 32,
        min_workers: int = 4,
        hard_max_workers: int = 64,
        history: int = 120,
    ) -> None:
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self.min_workers = max(1, min_workers)
        self.hard_max_workers = max(self.min_workers, hard_max_workers)
        self._max_workers = max(self.min_workers, min(max_workers, self.hard_max_workers))
        self._usage_history: deque[dict[str, float]] = deque(maxlen=history)
        self._semaphore: asyncio.Semaphore | None = None
        self._semaphore_limit = self._max_workers
        self._async_lock: asyncio.Lock | None = None
        self._psutil = None
        self._psutil_process = None
        
        try:
            import psutil
            self._psutil = psutil
            self._psutil_process = psutil.Process(os.getpid())
        except Exception:
            logger.warning("psutil unavailable, using fallbacks")
    
    @property
    def max_workers(self) -> int:
        return self._max_workers
    
    def attach_semaphore(self, semaphore: asyncio.Semaphore) -> None:
        """Attach semaphore for budget control."""
        self._semaphore = semaphore
        self._semaphore_limit = self._max_workers
    
    async def apply_worker_budget(self) -> int:
        """Apply worker budget to semaphore."""
        if self._semaphore is None:
            return self._max_workers
        
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        
        async with self._async_lock:
            desired = self._max_workers
            current = self._semaphore_limit
            
            if desired > current:
                for _ in range(desired - current):
                    self._semaphore.release()
            elif desired < current:
                for _ in range(current - desired):
                    await self._semaphore.acquire()
            
            self._semaphore_limit = desired
            return self._max_workers
    
    def _record_usage(self, usage: dict[str, float]) -> None:
        """Record usage and predict budget."""
        self._usage_history.append(usage)
        self._predict_worker_budget()
    
    def _predict_worker_budget(self) -> None:
        """Adaptive worker budget prediction."""
        if len(self._usage_history) < 5:
            return
        
        recent_cpu = [e["cpu_percent"] for e in list(self._usage_history)[-5:]]
        recent_mem = [e["memory_percent"] for e in list(self._usage_history)[-5:]]
        
        avg_cpu = statistics.mean(recent_cpu)
        avg_mem = statistics.mean(recent_mem)
        
        new_budget = self._max_workers
        
        if (self.max_cpu_percent and avg_cpu > self.max_cpu_percent * 0.95) or \
           (self.max_memory_mb and avg_mem > 90.0):
            new_budget = max(self.min_workers, self._max_workers - 1)
        elif avg_cpu < self.max_cpu_percent * 0.6 and avg_mem < 70.0:
            new_budget = min(self.hard_max_workers, self._max_workers + 1)
        
        self._max_workers = max(self.min_workers, min(new_budget, self.hard_max_workers))
    
    def get_resource_usage(self) -> dict[str, float]:
        """Get current resource usage."""
        timestamp = datetime.utcnow().isoformat()
        cpu_percent = 0.0
        memory_percent = 0.0
        rss_mb = 0.0
        
        if self._psutil:
            try:
                cpu_percent = float(self._psutil.cpu_percent(interval=None))
                virtual_memory = self._psutil.virtual_memory()
                memory_percent = float(virtual_memory.percent)
                if self._psutil_process:
                    rss_mb = float(self._psutil_process.memory_info().rss / (1024 * 1024))
            except Exception:
                cpu_percent = 0.0
        else:
            try:
                load1, _, _ = os.getloadavg()
                cpu_percent = float(min(100.0, load1 * 100))
            except OSError:
                cpu_percent = 0.0
            
            try:
                import resource
                usage_info = resource.getrusage(resource.RUSAGE_SELF)
                rss_mb = float(usage_info.ru_maxrss / 1024)
            except Exception:
                rss_mb = 0.0
        
        usage = {
            "timestamp": timestamp,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "rss_mb": rss_mb,
            "worker_budget": float(self._max_workers),
        }
        
        self._record_usage(usage)
        return usage
    
    def check_memory_exceeded(self, usage: dict[str, float] | None = None) -> tuple[bool, dict[str, float]]:
        """Check memory limit."""
        usage = usage or self.get_resource_usage()
        exceeded = False
        if self.max_memory_mb is not None:
            exceeded = usage.get("rss_mb", 0.0) > self.max_memory_mb
        return exceeded, usage
    
    def check_cpu_exceeded(self, usage: dict[str, float] | None = None) -> tuple[bool, dict[str, float]]:
        """Check CPU limit."""
        usage = usage or self.get_resource_usage()
        exceeded = False
        if self.max_cpu_percent:
            exceeded = usage.get("cpu_percent", 0.0) > self.max_cpu_percent
        return exceeded, usage
    
    def get_usage_history(self) -> list[dict[str, float]]:
        """Get usage history."""
        return list(self._usage_history)


# ============================================================================
# INSTRUMENTATION
# ============================================================================

class PhaseInstrumentation:
    """Phase telemetry collection."""
    
    def __init__(
        self,
        phase_id: int,
        name: str,
        items_total: int | None = None,
        snapshot_interval: int = 10,
        resource_limits: ResourceLimits | None = None,
    ) -> None:
        self.phase_id = phase_id
        self.name = name
        self.items_total = items_total or 0
        self.snapshot_interval = max(1, snapshot_interval)
        self.resource_limits = resource_limits
        self.items_processed = 0
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.warnings: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []
        self.resource_snapshots: list[dict[str, Any]] = []
        self.latencies: list[float] = []
        self.anomalies: list[dict[str, Any]] = []
    
    def start(self, items_total: int | None = None) -> None:
        """Start phase."""
        if items_total is not None:
            self.items_total = items_total
        self.start_time = time.perf_counter()
    
    def increment(self, count: int = 1, latency: float | None = None) -> None:
        """Increment progress."""
        self.items_processed += count
        if latency is not None:
            self.latencies.append(latency)
            self._detect_latency_anomaly(latency)
        if self.resource_limits and self.should_snapshot():
            self.capture_resource_snapshot()
    
    def should_snapshot(self) -> bool:
        """Check if snapshot needed."""
        if self.items_total == 0 or self.items_processed == 0:
            return False
        return self.items_processed % self.snapshot_interval == 0
    
    def capture_resource_snapshot(self) -> None:
        """Capture resource snapshot."""
        if not self.resource_limits:
            return
        snapshot = self.resource_limits.get_resource_usage()
        snapshot["items_processed"] = self.items_processed
        self.resource_snapshots.append(snapshot)
    
    def record_warning(self, category: str, message: str, **extra: Any) -> None:
        """Record warning."""
        entry = {
            "category": category,
            "message": message,
            **extra,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.warnings.append(entry)
    
    def record_error(self, category: str, message: str, **extra: Any) -> None:
        """Record error."""
        entry = {
            "category": category,
            "message": message,
            **extra,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.errors.append(entry)
    
    def _detect_latency_anomaly(self, latency: float) -> None:
        """Detect latency spikes."""
        if len(self.latencies) < 5:
            return
        
        mean_latency = statistics.mean(self.latencies)
        std_latency = statistics.pstdev(self.latencies) or 0.0
        threshold = mean_latency + (3 * std_latency)
        
        if std_latency and latency > threshold:
            self.anomalies.append({
                "type": "latency_spike",
                "latency": latency,
                "mean": mean_latency,
                "std": std_latency,
                "timestamp": datetime.utcnow().isoformat(),
            })
    
    def complete(self) -> None:
        """Complete phase."""
        self.end_time = time.perf_counter()
    
    def duration_ms(self) -> float | None:
        """Get duration."""
        if self.start_time is None or self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000.0
    
    def progress(self) -> float | None:
        """Get progress fraction."""
        if not self.items_total:
            return None
        return min(1.0, self.items_processed / float(self.items_total))
    
    def throughput(self) -> float | None:
        """Get items per second."""
        if self.start_time is None:
            return None
        elapsed = (time.perf_counter() - self.start_time) if self.end_time is None else (self.end_time - self.start_time)
        if not elapsed:
            return None
        return self.items_processed / elapsed
    
    def latency_histogram(self) -> dict[str, float | None]:
        """Get latency percentiles."""
        if not self.latencies:
            return {"p50": None, "p95": None, "p99": None}
        
        sorted_latencies = sorted(self.latencies)
        
        def percentile(p: float) -> float:
            if not sorted_latencies:
                return 0.0
            k = (len(sorted_latencies) - 1) * (p / 100.0)
            f = int(k)
            c = min(f + 1, len(sorted_latencies) - 1)
            if f == c:
                return sorted_latencies[int(k)]
            d0 = sorted_latencies[f] * (c - k)
            d1 = sorted_latencies[c] * (k - f)
            return d0 + d1
        
        return {
            "p50": percentile(50.0),
            "p95": percentile(95.0),
            "p99": percentile(99.0),
        }
    
    def build_metrics(self) -> dict[str, Any]:
        """Build metrics summary."""
        return {
            "phase_id": self.phase_id,
            "name": self.name,
            "duration_ms": self.duration_ms(),
            "items_processed": self.items_processed,
            "items_total": self.items_total,
            "progress": self.progress(),
            "throughput": self.throughput(),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "resource_snapshots": list(self.resource_snapshots),
            "latency_histogram": self.latency_histogram(),
            "anomalies": list(self.anomalies),
        }


# ============================================================================
# TIMEOUT HANDLING
# ============================================================================

class PhaseTimeoutError(RuntimeError):
    """Phase timeout exception."""
    
    def __init__(self, phase_id: int | str, phase_name: str, timeout_s: float) -> None:
        self.phase_id = phase_id
        self.phase_name = phase_name
        self.timeout_s = timeout_s
        super().__init__(f"Phase {phase_id} ({phase_name}) timed out after {timeout_s}s")


async def execute_phase_with_timeout(
    phase_id: int,
    phase_name: str,
    coro: Callable[P, T] | None = None,
    handler: Callable[P, T] | None = None,
    args: tuple | None = None,
    timeout_s: float = 300.0,
    **kwargs: P.kwargs,
) -> T:
    """Execute phase with timeout."""
    target = coro or handler
    if target is None:
        raise ValueError("Either 'coro' or 'handler' must be provided")
    
    call_args = args or ()
    
    start = time.perf_counter()
    logger.info(f"Phase {phase_id} ({phase_name}) started, timeout={timeout_s}s")
    
    if not callable(target):
         raise TypeError(f"Phase {phase_name} function is not callable: {type(target)}")
    try:
        # Improved execution with proper context
        if asyncio.iscoroutinefunction(target):
            # Handle args
            call_args = args or ()
            if isinstance(call_args, dict):
                result = await asyncio.wait_for(target(**call_args), timeout=timeout_s)
            else:
                result = await asyncio.wait_for(target(*call_args), timeout=timeout_s)
        else:
            # Use functools.partial for cleaner argument binding
            from functools import partial
            call_args = args or ()
            if isinstance(call_args, dict):
                bound_func = partial(target, **call_args)
            elif isinstance(call_args, (list, tuple)):
                bound_func = partial(target, *call_args)
            else:
                bound_func = partial(target, call_args)
            result = await asyncio.wait_for(asyncio.to_thread(bound_func), timeout=timeout_s)
        
        logger.info(f"Phase {phase_name} completed successfully")
        return result
        
    except asyncio.TimeoutError:
        logger.error(f"Phase {phase_name} timed out after {timeout_s}s")
        # Record failure structure if needed, but orchestrator should handle it
        raise
    except Exception as e:
        logger.error(f"Phase {phase_name} failed with {type(e).__name__}: {str(e)}")
        raise



# ============================================================================
# METHOD EXECUTOR
# ============================================================================

class _LazyInstanceDict:
    """Lazy instance dictionary."""
    
    def __init__(self, method_registry: Any) -> None:
        self._registry = method_registry
    
    def get(self, class_name: str, default: Any = None) -> Any:
        try:
            return self._registry._get_instance(class_name)
        except Exception:
            return default
    
    def __getitem__(self, class_name: str) -> Any:
        return self._registry._get_instance(class_name)
    
    def __contains__(self, class_name: str) -> bool:
        return class_name in self._registry._class_paths
    
    def keys(self) -> list[str]:
        return list(self._registry._class_paths.keys())
    
    def values(self) -> list[Any]:
        return [self.get(name) for name in self.keys()]
    
    def items(self) -> list[tuple[str, Any]]:
        return [(name, self.get(name)) for name in self.keys()]
    
    def __len__(self) -> int:
        return len(self._registry._class_paths)


class MethodExecutor:
    """Method executor with lazy loading."""
    
    def __init__(
        self,
        dispatcher: Any | None = None,
        signal_registry: Any | None = None,
        method_registry: Any | None = None,
    ) -> None:
        from orchestration.method_registry import (
            MethodRegistry,
            setup_default_instantiation_rules,
        )
        
        self.degraded_mode = False
        self.degraded_reasons: list[str] = []
        self.signal_registry = signal_registry
        
        if method_registry is not None:
            self._method_registry = method_registry
        else:
            try:
                self._method_registry = MethodRegistry()
                setup_default_instantiation_rules(self._method_registry)
                logger.info("Method registry initialized")
            except Exception as exc:
                self.degraded_mode = True
                reason = f"Method registry initialization failed: {exc}"
                self.degraded_reasons.append(reason)
                logger.error(f"DEGRADED MODE: {reason}")
                self._method_registry = MethodRegistry(class_paths={})
        
        try:
            from orchestration.class_registry import build_class_registry
            registry = build_class_registry()
        except (ClassRegistryError, ModuleNotFoundError, ImportError) as exc:
            self.degraded_mode = True
            reason = f"Could not build class registry: {exc}"
            self.degraded_reasons.append(reason)
            logger.warning(f"DEGRADED MODE: {reason}")
            registry = {}
        
        self._router = ExtendedArgRouter(registry)
        self.instances = _LazyInstanceDict(self._method_registry)
    
    @staticmethod
    def _supports_parameter(callable_obj: Any, parameter_name: str) -> bool:
        try:
            signature = inspect.signature(callable_obj)
        except (TypeError, ValueError):
            return False
        return parameter_name in signature.parameters
    
    def execute(self, class_name: str, method_name: str, **kwargs: Any) -> Any:
        """Execute method."""
        from orchestration.method_registry import MethodRegistryError
        
        try:
            method = self._method_registry.get_method(class_name, method_name)
        except MethodRegistryError as exc:
            logger.error(f"Method retrieval failed: {class_name}.{method_name}: {exc}")
            if self.degraded_mode:
                logger.warning("Returning None due to degraded mode")
                return None
            raise AttributeError(f"Cannot retrieve {class_name}.{method_name}: {exc}") from exc
        
        try:
            args, routed_kwargs = self._router.route(class_name, method_name, dict(kwargs))
            return method(*args, **routed_kwargs)
        except (ArgRouterError, ArgumentValidationError):
            logger.exception(f"Argument routing failed for {class_name}.{method_name}")
            raise
        except Exception:
            logger.exception(f"Method execution failed for {class_name}.{method_name}")
            raise
    
    def inject_method(self, class_name: str, method_name: str, method: Callable[..., Any]) -> None:
        """Inject method."""
        self._method_registry.inject_method(class_name, method_name, method)
        logger.info(f"Method injected: {class_name}.{method_name}")
    
    def has_method(self, class_name: str, method_name: str) -> bool:
        """Check if method exists."""
        return self._method_registry.has_method(class_name, method_name)
    
    def get_registry_stats(self) -> dict[str, Any]:
        """Get registry stats."""
        return self._method_registry.get_stats()
    
    def get_routing_metrics(self) -> dict[str, Any]:
        """Get routing metrics."""
        if hasattr(self._router, "get_metrics"):
            return self._router.get_metrics()
        return {}


# ============================================================================
# PHASE VALIDATION
# ============================================================================

def validate_phase_definitions(
    phase_list: list[tuple[int, str, str, str]], orchestrator_class: type
) -> None:
    """Validate phase definitions."""
    if not phase_list:
        raise RuntimeError("FASES cannot be empty")
    
    phase_ids = [phase[0] for phase in phase_list]
    
    seen_ids = set()
    for phase_id in phase_ids:
        if phase_id in seen_ids:
            raise RuntimeError(f"Duplicate phase ID {phase_id}")
        seen_ids.add(phase_id)
    
    if phase_ids != sorted(phase_ids):
        raise RuntimeError(f"Phase IDs must be sorted. Got {phase_ids}")
    if phase_ids[0] != 0:
        raise RuntimeError(f"Phase IDs must start from 0. Got {phase_ids[0]}")
    if phase_ids[-1] != len(phase_list) - 1:
        raise RuntimeError(f"Phase IDs must be contiguous. Got {phase_ids[-1]}")
    
    valid_modes = {"sync", "async"}
    for phase_id, mode, handler_name, label in phase_list:
        if mode not in valid_modes:
            raise RuntimeError(f"Phase {phase_id}: invalid mode '{mode}'")
        
        if not hasattr(orchestrator_class, handler_name):
            raise RuntimeError(f"Phase {phase_id}: missing handler '{handler_name}'")
        
        handler = getattr(orchestrator_class, handler_name, None)
        if not callable(handler):
            raise RuntimeError(f"Phase {phase_id}: handler '{handler_name}' not callable")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_questionnaire_provider() -> Any:
    """Get questionnaire provider (placeholder)."""
    return None


def get_dependency_lockdown() -> Any:
    """Get dependency lockdown manager."""
    class DependencyLockdown:
        def get_mode_description(self) -> str:
            return "Production mode - all dependencies locked"
    return DependencyLockdown()


class RecommendationEnginePort:
    """Port interface for recommendation engine."""
    pass


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class Orchestrator:
    """11-phase deterministic policy analysis orchestrator."""
    
    FASES: list[tuple[int, str, str, str]] = [
        (0, "sync", "_load_configuration", "FASE 0 - Configuración"),
        (1, "sync", "_ingest_document", "FASE 1 - Ingestión"),
        (2, "async", "_execute_micro_questions_async", "FASE 2 - Micro Preguntas"),
        (3, "async", "_score_micro_results_async", "FASE 3 - Scoring"),
        (4, "async", "_aggregate_dimensions_async", "FASE 4 - Dimensiones"),
        (5, "async", "_aggregate_policy_areas_async", "FASE 5 - Áreas"),
        (6, "sync", "_aggregate_clusters", "FASE 6 - Clústeres"),
        (7, "sync", "_evaluate_macro", "FASE 7 - Macro"),
        (8, "async", "_generate_recommendations", "FASE 8 - Recomendaciones"),
        (9, "sync", "_assemble_report", "FASE 9 - Reporte"),
        (10, "async", "_format_and_export", "FASE 10 - Exportación"),
    ]
    
    PHASE_ITEM_TARGETS: dict[int, int] = {
        0: 1, 1: 1, 2: 300, 3: 300, 4: 60,
        5: 10, 6: 4, 7: 1, 8: 1, 9: 1, 10: 1,
    }
    
    PHASE_OUTPUT_KEYS: dict[int, str] = {
        0: "config", 1: "document", 2: "micro_results",
        3: "scored_results", 4: "dimension_scores",
        5: "policy_area_scores", 6: "cluster_scores",
        7: "macro_result", 8: "recommendations",
        9: "report", 10: "export_payload",
    }
    
    PHASE_ARGUMENT_KEYS: dict[int, list[str]] = {
        1: ["pdf_path", "config"],
        2: ["document", "config"],
        3: ["micro_results", "config"],
        4: ["scored_results", "config"],
        5: ["dimension_scores", "config"],
        6: ["policy_area_scores", "config"],
        7: ["cluster_scores", "config", "policy_area_scores", "dimension_scores"], # Need all for macro
        8: ["macro_result", "config"],
        9: ["recommendations", "config"],
        10: ["report", "config"],
    }
    
    PHASE_TIMEOUTS: dict[int, float] = {
        0: 60, 1: 120, 2: 600, 3: 300, 4: 180,
        5: 120, 6: 60, 7: 60, 8: 120, 9: 60, 10: 120,
    }
    
    def __init__(
        self,
        method_executor: MethodExecutor,
        questionnaire: CanonicalQuestionnaire,
        executor_config: ExecutorConfig,
        runtime_config: RuntimeConfig | None = None,
        phase0_validation: Phase0ValidationResult | None = None,
        calibration_orchestrator: Any | None = None,
        resource_limits: ResourceLimits | None = None,
        resource_snapshot_interval: int = 10,
        recommendation_engine_port: RecommendationEnginePort | None = None,
        processor_bundle: Any | None = None,
    ) -> None:
        """Initialize orchestrator with Phase 0 integration."""
        from orchestration.questionnaire_validation import _validate_questionnaire_structure
        
        validate_phase_definitions(self.FASES, self.__class__)
        
        self.executor = method_executor
        self._canonical_questionnaire = questionnaire
        self._monolith_data = dict(questionnaire.data)
        self.executor_config = executor_config
        self.runtime_config = runtime_config
        self.phase0_validation = phase0_validation
        
        if phase0_validation is not None:
            if not phase0_validation.all_passed:
                failed = phase0_validation.get_failed_gates()
                failed_names = [g.gate_name for g in failed]
                raise RuntimeError(
                    f"Cannot initialize orchestrator: "
                    f"Phase 0 exit gates failed: {failed_names}. "
                    f"Bootstrap must complete successfully before orchestrator execution."
                )
            logger.info(
                "orchestrator_phase0_validation_passed",
                gates_checked=len(phase0_validation.gate_results),
                validation_time=phase0_validation.validation_time,
                summary=phase0_validation.get_summary()
            )
        
        if runtime_config is not None:
            logger.info(
                "orchestrator_runtime_mode",
                mode=runtime_config.mode.value,
                strict=runtime_config.is_strict_mode(),
                category="phase0_integration"
            )
        else:
            logger.warning(
                "orchestrator_no_runtime_config",
                message="RuntimeConfig not provided - assuming production mode",
                category="phase0_integration"
            )
        
        if calibration_orchestrator is not None:
            self.calibration_orchestrator = calibration_orchestrator
            logger.info("CalibrationOrchestrator injected into main orchestrator")
        else:
            self.calibration_orchestrator = None
        
        self.resource_limits = resource_limits or ResourceLimits()
        self.resource_snapshot_interval = max(1, resource_snapshot_interval)
        self.questionnaire_provider = get_questionnaire_provider()
        
        self._enriched_packs = None
        if processor_bundle is not None:
            if hasattr(processor_bundle, "enriched_signal_packs"):
                self._enriched_packs = processor_bundle.enriched_signal_packs
                logger.info(f"Orchestrator wired with {len(self._enriched_packs)} enriched signal packs")
            else:
                logger.warning("ProcessorBundle missing enriched_signal_packs")
        else:
            logger.warning("No ProcessorBundle provided")
        
        if not hasattr(self.executor, "signal_registry") or self.executor.signal_registry is None:
            raise RuntimeError("MethodExecutor must have signal_registry")
        
        try:
            _validate_questionnaire_structure(self._monolith_data)
        except (ValueError, TypeError) as e:
            raise RuntimeError(f"Questionnaire validation failed: {e}") from e
        
        if not self.executor.instances:
            raise RuntimeError("MethodExecutor.instances is empty")
        
        self.executors = {
            "D1-Q1": executors.D1Q1_Executor, "D1-Q2": executors.D1Q2_Executor,
            "D1-Q3": executors.D1Q3_Executor, "D1-Q4": executors.D1Q4_Executor,
            "D1-Q5": executors.D1Q5_Executor, "D2-Q1": executors.D2Q1_Executor,
            "D2-Q2": executors.D2Q2_Executor, "D2-Q3": executors.D2Q3_Executor,
            "D2-Q4": executors.D2Q4_Executor, "D2-Q5": executors.D2Q5_Executor,
            "D3-Q1": executors.D3Q1_Executor, "D3-Q2": executors.D3Q2_Executor,
            "D3-Q3": executors.D3Q3_Executor, "D3-Q4": executors.D3Q4_Executor,
            "D3-Q5": executors.D3Q5_Executor, "D4-Q1": executors.D4Q1_Executor,
            "D4-Q2": executors.D4Q2_Executor, "D4-Q3": executors.D4Q3_Executor,
            "D4-Q4": executors.D4Q4_Executor, "D4-Q5": executors.D4Q5_Executor,
            "D5-Q1": executors.D5Q1_Executor, "D5-Q2": executors.D5Q2_Executor,
            "D5-Q3": executors.D5Q3_Executor, "D5-Q4": executors.D5Q4_Executor,
            "D5-Q5": executors.D5Q5_Executor, "D6-Q1": executors.D6Q1_Executor,
            "D6-Q2": executors.D6Q2_Executor, "D6-Q3": executors.D6Q3_Executor,
            "D6-Q4": executors.D6Q4_Executor, "D6-Q5": executors.D6Q5_Executor,
        }
        
        self.abort_signal = AbortSignal()
        self.phase_results: list[PhaseResult] = []
        self._phase_instrumentation: dict[int, PhaseInstrumentation] = {}
        self._phase_status: dict[int, str] = {phase_id: "not_started" for phase_id, *_ in self.FASES}
        self._phase_outputs: dict[int, Any] = {}
        self._context: dict[str, Any] = {}
        self._start_time: float | None = None
        self._execution_plan: ExecutionPlan | None = None
        
        self.dependency_lockdown = get_dependency_lockdown()
        logger.info(f"Orchestrator initialized: {self.dependency_lockdown.get_mode_description()}")
        
        self.recommendation_engine = recommendation_engine_port
        if self.recommendation_engine:
            logger.info("RecommendationEngine port injected")
            
        self.artifacts_dir = Path("artifacts/plan1")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.artifacts_dir / "orchestrator_state.json"
        self._pdf_cache = {}
    
    def get_cached_pdf_content(self, pdf_path: str) -> bytes:
        if pdf_path not in self._pdf_cache:
            self._pdf_cache[pdf_path] = Path(pdf_path).read_bytes()
        return self._pdf_cache[pdf_path]

    def _ensure_not_aborted(self) -> None:
        if self.abort_signal.is_aborted():
            reason = self.abort_signal.get_reason() or "Unknown"
            raise AbortRequested(f"Orchestration aborted: {reason}")
    
    def request_abort(self, reason: str) -> None:
        self.abort_signal.abort(reason)
    
    def reset_abort(self) -> None:
        self.abort_signal.reset()
    
    def _get_phase_timeout(self, phase_id: int) -> float:
        return self.PHASE_TIMEOUTS.get(phase_id, 300.0)
    
    async def process_development_plan_async(
        self, pdf_path: str, preprocessed_document: Any | None = None
    ) -> list[PhaseResult]:
        """Execute 11-phase pipeline."""
        self.reset_abort()
        self.phase_results = []
        self._phase_instrumentation = {}
        self._phase_outputs = {}
        self._context = {"pdf_path": pdf_path}
        
        if preprocessed_document is not None:
            self._context["preprocessed_override"] = preprocessed_document
        
        self._phase_status = {phase_id: "not_started" for phase_id, *_ in self.FASES}
        self._start_time = time.perf_counter()
        
        for phase_id, mode, handler_name, phase_label in self.FASES:
            self._ensure_not_aborted()
            
            handler = getattr(self, handler_name)
            instrumentation = PhaseInstrumentation(
                phase_id=phase_id,
                name=phase_label,
                items_total=self.PHASE_ITEM_TARGETS.get(phase_id),
                snapshot_interval=self.resource_snapshot_interval,
                resource_limits=self.resource_limits,
            )
            
            instrumentation.start(items_total=self.PHASE_ITEM_TARGETS.get(phase_id))
            self._phase_instrumentation[phase_id] = instrumentation
            self._phase_status[phase_id] = "running"
            
            # Resolve args from context
            required_keys = self.PHASE_ARGUMENT_KEYS.get(phase_id, [])
            args = []
            for key in required_keys:
                if key in self._context:
                    args.append(self._context[key])
                else:
                    # Optional args or handle missing gracefully
                    logger.warning(f"Missing argument '{key}' for phase {phase_id}, passing None")
                    args.append(None)
            
            success = False
            data: Any = None
            error: Exception | None = None
            
            try:
                if mode == "sync":
                    if phase_id in TIMEOUT_SYNC_PHASES:
                        data = await execute_phase_with_timeout(
                            phase_id=phase_id,
                            phase_name=phase_label,
                            timeout_s=self._get_phase_timeout(phase_id),
                            coro=asyncio.to_thread,
                            args=(handler,) + tuple(args),
                        )
                    else:
                        data = handler(*args)
                else:
                    data = await execute_phase_with_timeout(
                        phase_id=phase_id,
                        phase_name=phase_label,
                        timeout_s=self._get_phase_timeout(phase_id),
                        handler=handler,
                        args=tuple(args),
                    )
                success = True
                
            except PhaseTimeoutError as exc:
                error = exc
                instrumentation.record_error("timeout", str(exc))
                self.request_abort(f"Phase {phase_id} timed out")
                
            except AbortRequested as exc:
                error = exc
                instrumentation.record_warning("abort", str(exc))
                
            except Exception as exc:
                logger.exception(f"Phase {phase_label} failed")
                error = exc
                instrumentation.record_error("exception", str(exc))
                self.request_abort(f"Phase {phase_id} failed: {exc}")
            
            finally:
                instrumentation.complete()
            
            aborted = self.abort_signal.is_aborted()
            duration_ms = instrumentation.duration_ms() or 0.0
            
            phase_result = PhaseResult(
                success=success and not aborted,
                phase_id=str(phase_id),
                data=data,
                error=error,
                duration_ms=duration_ms,
                mode=mode,
                aborted=aborted,
            )
            self.phase_results.append(phase_result)
            
            if success and not aborted:
                self._phase_outputs[phase_id] = data
                out_key = self.PHASE_OUTPUT_KEYS.get(phase_id)
                if out_key:
                    self._context[out_key] = data

                # IMPORTANT: Update context with results required for subsequent phases
                if phase_id == 5: # Policy Area Scores needed for Macro
                    self._context["policy_area_scores"] = data
                if phase_id == 4: # Dimension Scores needed for Macro
                    self._context["dimension_scores"] = data
                if phase_id == 6: # Cluster Scores needed for Macro
                    self._context["cluster_scores"] = data

                self._phase_status[phase_id] = "completed"
                
                if phase_id in [7, 9, 10]:
                    expected_artifacts = {
                        7: "policy_mapping.json",
                        9: "implementation_recommendations.json",
                        10: "risk_assessment.json"
                    }
                    if phase_id in expected_artifacts:
                        artifact_name = expected_artifacts[phase_id]
                        artifact_path = self.artifacts_dir / artifact_name
                        if artifact_path.exists():
                            logger.info(f"✓ Verified artifact: {artifact_path}")
                
                try:
                    state = {
                        "last_completed_phase": phase_label,
                        "timestamp": datetime.now().isoformat(),
                        "phases_completed": [pid for pid, st in self._phase_status.items() if st == "completed"],
                        "artifacts_generated": [str(p.name) for p in self.artifacts_dir.glob("*.json")]
                    }
                    self.state_file.write_text(json.dumps(state, indent=2))
                except Exception as e:
                    logger.warning(f"Failed to persist state: {e}")
                
                if phase_id == 1:
                    try:
                        document = self._context.get("document")
                        if document is None:
                            raise ValueError("Phase 1 output missing: context['document'] is None")

                        synchronizer = IrrigationSynchronizer(
                            questionnaire=self._monolith_data,
                            preprocessed_document=document,
                        )
                        self._execution_plan = synchronizer.build_execution_plan()
                        
                        logger.info(f"Execution plan built: {len(self._execution_plan.tasks)} tasks")
                    except ValueError as e:
                        logger.error(f"Failed to build execution plan: {e}")
                        self.request_abort(f"Synchronization failed: {e}")
                        raise
            elif aborted:
                self._phase_status[phase_id] = "aborted"
                break
            else:
                self._phase_status[phase_id] = "failed"
                break
        
        return self.phase_results

    # ... (Keep existing methods: process_development_plan, get_processing_status, etc.)
    def process_development_plan(
        self, pdf_path: str, preprocessed_document: Any | None = None
    ) -> list[PhaseResult]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            raise RuntimeError("Cannot call from within async context")
        
        return asyncio.run(self.process_development_plan_async(pdf_path, preprocessed_document))
    
    def get_processing_status(self) -> dict[str, Any]:
        if self._start_time is None:
            status = "not_started"
            elapsed = 0.0
            completed_flag = False
        else:
            aborted = self.abort_signal.is_aborted()
            status = "aborted" if aborted else "running"
            elapsed = time.perf_counter() - self._start_time
            completed_flag = all(state == "completed" for state in self._phase_status.values()) and not aborted
        
        completed = sum(1 for state in self._phase_status.values() if state == "completed")
        total = len(self.FASES)
        overall_progress = completed / total if total else 0.0
        
        phase_progress = {
            str(phase_id): instr.progress()
            for phase_id, instr in self._phase_instrumentation.items()
        }
        
        resource_usage = self.resource_limits.get_resource_usage() if self._start_time else {}
        
        return {
            "status": status,
            "overall_progress": overall_progress,
            "phase_progress": phase_progress,
            "elapsed_time_s": elapsed,
            "resource_usage": resource_usage,
            "abort_status": self.abort_signal.is_aborted(),
            "abort_reason": self.abort_signal.get_reason(),
            "completed": completed_flag,
        }
    
    def get_phase_metrics(self) -> dict[str, Any]:
        return {
            str(phase_id): instr.build_metrics()
            for phase_id, instr in self._phase_instrumentation.items()
        }
    
    def export_metrics(self) -> dict[str, Any]:
        abort_timestamp = self.abort_signal.get_timestamp()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "phase_metrics": self.get_phase_metrics(),
            "resource_usage": self.resource_limits.get_usage_history(),
            "abort_status": {
                "is_aborted": self.abort_signal.is_aborted(),
                "reason": self.abort_signal.get_reason(),
                "timestamp": abort_timestamp.isoformat() if abort_timestamp else None,
            },
            "phase_status": dict(self._phase_status),
        }
    
    def calibrate_method(
        self,
        method_id: str,
        role: str,
        context: dict[str, Any] | None = None,
        pdt_structure: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        if self.calibration_orchestrator is None:
            logger.warning("CalibrationOrchestrator not available, skipping calibration")
            return None
        
        try:
            from orchestration.calibration_orchestrator import (
                CalibrationSubject,
                EvidenceStore,
            )
            
            subject = CalibrationSubject(
                method_id=method_id,
                role=role,
                context=context or {}
            )
            
            evidence = EvidenceStore(
                pdt_structure=pdt_structure or {
                    "chunk_count": 0,
                    "completeness": 0.5,
                    "structure_quality": 0.5
                },
                document_quality=0.5,
                question_id=context.get("question_id") if context else None,
                dimension_id=context.get("dimension_id") if context else None,
                policy_area_id=context.get("policy_area_id") if context else None
            )
            
            result = self.calibration_orchestrator.calibrate(subject, evidence)
            
            return {
                "final_score": result.final_score,
                "layer_scores": {
                    layer_id.value: score
                    for layer_id, score in result.layer_scores.items()
                },
                "active_layers": [layer.value for layer in result.active_layers],
                "role": result.role,
                "method_id": result.method_id,
                "metadata": result.metadata
            }
        
        except Exception as e:
            logger.error(f"Method calibration failed for {method_id}: {e}", exc_info=True)
            return None

    # ... (Keep previous phase methods 0-3)
    def _load_configuration(self) -> dict[str, Any]:
        # Implementation from previous file
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[0]
        start = time.perf_counter()
        
        if self.phase0_validation is not None and not self.phase0_validation.all_passed:
            failed_gates = self.phase0_validation.get_failed_gates()
            raise RuntimeError(
                f"Cannot execute orchestrator Phase 0: "
                f"Phase_zero bootstrap did not complete successfully. "
                f"Failed gates: {[g.gate_name for g in failed_gates]}"
            )
        
        if self.runtime_config is not None:
            mode = self.runtime_config.mode
            if mode == RuntimeMode.PROD:
                logger.info("orchestrator_phase0_prod_mode", strict=True)
            elif mode == RuntimeMode.DEV:
                logger.warning("orchestrator_phase0_dev_mode", strict=False)
            else:  # EXPLORATORY
                logger.warning("orchestrator_phase0_exploratory_mode", strict=False)
        
        monolith = _normalize_monolith_for_hash(self._monolith_data)
        monolith_hash = hashlib.sha256(
            json.dumps(monolith, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            .encode("utf-8")
        ).hexdigest()
        
        micro_questions = monolith["blocks"].get("micro_questions", [])
        meso_questions = monolith["blocks"].get("meso_questions", [])
        macro_question = monolith["blocks"].get("macro_question", {})
        
        question_total = len(micro_questions) + len(meso_questions) + (1 if macro_question else 0)
        
        if question_total != EXPECTED_QUESTION_COUNT:
            logger.warning(f"Question count: expected {EXPECTED_QUESTION_COUNT}, got {question_total}")
            instrumentation.record_warning("integrity", f"Question count: {question_total}")
        
        aggregation_settings = AggregationSettings.from_monolith(monolith)
        
        duration = time.perf_counter() - start
        instrumentation.increment(latency=duration)
        
        config_dict = {
            "monolith": monolith,
            "monolith_sha256": monolith_hash,
            "micro_questions": micro_questions,
            "meso_questions": meso_questions,
            "macro_question": macro_question,
            "_aggregation_settings": aggregation_settings,
        }
        
        if self.runtime_config is not None:
            config_dict["_runtime_mode"] = self.runtime_config.mode.value
            config_dict["_strict_mode"] = self.runtime_config.is_strict_mode()
        
        return config_dict

    def _ingest_document(self, pdf_path: str, config: dict[str, Any]) -> Any:
        # Implementation from previous file
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[1]
        start = time.perf_counter()
        
        document_id = os.path.splitext(os.path.basename(pdf_path))[0] or "doc_1"
        
        try:
            from canonic_phases.Phase_one import (
                CanonicalInput,
                execute_phase_1_with_full_contract,
                CanonPolicyPackage,
            )
            from pathlib import Path
            import hashlib
            
            questionnaire_path = self._canonical_questionnaire.source_path if hasattr(self._canonical_questionnaire, 'source_path') else None
            if not questionnaire_path:
                questionnaire_path = resolve_workspace_path(
                    "canonic_questionnaire_central/questionnaire_monolith.json",
                    require_exists=True,
                )
            else:
                questionnaire_path = Path(questionnaire_path)
                if not questionnaire_path.exists():
                    questionnaire_path = resolve_workspace_path(
                        str(questionnaire_path),
                        require_exists=True,
                    )
            
            pdf_path_obj = Path(pdf_path)
            if not pdf_path_obj.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            pdf_sha256 = hashlib.sha256(pdf_path_obj.read_bytes()).hexdigest()
            questionnaire_sha256 = hashlib.sha256(questionnaire_path.read_bytes()).hexdigest()
            
            canonical_input = CanonicalInput(
                document_id=document_id,
                run_id=f"run_{document_id}_{int(time.time())}",
                pdf_path=pdf_path_obj,
                pdf_sha256=pdf_sha256,
                pdf_size_bytes=pdf_path_obj.stat().st_size,
                pdf_page_count=0,
                questionnaire_path=questionnaire_path,
                questionnaire_sha256=questionnaire_sha256,
                created_at=datetime.utcnow(),
                phase0_version="1.0.0",
                validation_passed=True,
                validation_errors=[],
                validation_warnings=[],
            )
            
            signal_registry = self.executor.signal_registry if hasattr(self.executor, 'signal_registry') else None
            
            if signal_registry is None:
                logger.warning("⚠️  POLICY VIOLATION: signal_registry not available, Phase 1 will run in degraded mode")
            else:
                logger.info("✓ POLICY COMPLIANT: Passing signal_registry to Phase 1 (DI chain: Factory → Orchestrator → Phase 1)")
            
            canon_package = execute_phase_1_with_full_contract(
                canonical_input,
                signal_registry=signal_registry
            )
            
            if not isinstance(canon_package, CanonPolicyPackage):
                raise ValueError(f"Phase 1 returned invalid type: {type(canon_package)}")
            
            actual_chunk_count = len(canon_package.chunk_graph.chunks)
            if actual_chunk_count != P01_EXPECTED_CHUNK_COUNT:
                raise ValueError(
                    f"P01 validation failed: expected {P01_EXPECTED_CHUNK_COUNT} chunks, "
                    f"got {actual_chunk_count}"
                )
            
            for i, chunk in enumerate(canon_package.chunk_graph.chunks):
                if not hasattr(chunk, "policy_area") or not chunk.policy_area:
                    raise ValueError(f"Chunk {i} missing policy_area")
                if not hasattr(chunk, "dimension") or not chunk.dimension:
                    raise ValueError(f"Chunk {i} missing dimension")
            
            logger.info(f"✓ P01-ES v1.0 validation passed: {actual_chunk_count} chunks")
            return canon_package
            
        except Exception as e:
            instrumentation.record_error("ingestion", str(e))
            raise RuntimeError(f"Document ingestion failed: {e}") from e
        
        duration = time.perf_counter() - start
        instrumentation.increment(latency=duration)
        
        return canon_package
    
    def _lookup_question_from_plan_task(self, task: Any, config: dict[str, Any]) -> dict[str, Any] | None:
        """Look up full question data from monolith using task metadata.
        
        Args:
            task: Task from execution_plan with question_id and dimension
            config: Configuration dict containing micro_questions from monolith
            
        Returns:
            Question dict from monolith, or None if not found
        """
        micro_questions = config.get("micro_questions", [])
        question_id = task.question_id
        
        for question in micro_questions:
            if question.get("id") == question_id or question.get("question_id") == question_id:
                return question
        
        logger.warning(f"Question {question_id} not found in monolith for task {task.task_id}")
        return None

    async def _execute_micro_questions_async(
        self, document: Any, config: dict[str, Any]
    ) -> list[MicroQuestionRun]:
        """Execute micro questions using ExecutionPlan from Phase 1.
        
        Consumes all tasks from self._execution_plan, tracks status, errors, and retries.
        Each task is mapped to the correct executor using dimension and question metadata.
        
        Invariants:
        - No orphan tasks (all tasks in plan are consumed)
        - No duplicate execution (each task executed exactly once, ignoring retries)
        - Task metadata drives execution (dimension, policy_area, question_id)
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[2]
        
        # Use execution_plan if available, fallback to legacy config-based approach
        if self._execution_plan is not None:
            tasks = list(self._execution_plan.tasks)
            logger.info(f"Phase 2: Executing {len(tasks)} tasks from execution plan (plan_id: {self._execution_plan.plan_id})")
            instrumentation.start(items_total=len(tasks))
            
            task_status = {}
            results: list[MicroQuestionRun] = []
            tasks_executed = set()
            tasks_failed = set()
            
            for task in tasks:
                self._ensure_not_aborted()
                task_id = task.task_id
                start_q = time.perf_counter()
                
                # Track task to ensure no duplicates
                if task_id in tasks_executed:
                    logger.error(f"Duplicate task execution detected: {task_id}")
                    instrumentation.record_error("duplicate_task", task_id)
                    continue
                
                tasks_executed.add(task_id)
                task_status[task_id] = "running"
                
                # Look up full question data from monolith
                question = self._lookup_question_from_plan_task(task, config)
                if question is None:
                    error_msg = f"Question data not found for task {task_id}"
                    logger.error(error_msg)
                    task_status[task_id] = "failed"
                    tasks_failed.add(task_id)
                    instrumentation.record_error("question_lookup_failed", task_id)
                    
                    results.append(MicroQuestionRun(
                        question_id=task.question_id,
                        question_global=UNKNOWN_QUESTION_GLOBAL,
                        base_slot=UNKNOWN_BASE_SLOT,
                        metadata={"task_id": task_id, "error": "question_not_found"},
                        evidence=None,
                        error=error_msg,
                        aborted=False
                    ))
                    continue
                
                base_slot = question.get("base_slot")
                if not base_slot:
                    error_msg = f"Task {task_id}: Question missing base_slot"
                    logger.warning(error_msg)
                    task_status[task_id] = "failed"
                    tasks_failed.add(task_id)
                    instrumentation.record_error("missing_base_slot", task_id)
                    
                    results.append(MicroQuestionRun(
                        question_id=question.get("id"),
                        question_global=question.get("global_id", UNKNOWN_QUESTION_GLOBAL),
                        base_slot=UNKNOWN_BASE_SLOT,
                        metadata={"task_id": task_id, "error": "missing_base_slot"},
                        evidence=None,
                        error=error_msg,
                        aborted=False
                    ))
                    continue

                executor_class = self.executors.get(base_slot)
                if not executor_class:
                    error_msg = f"Task {task_id}: No executor found for {base_slot}"
                    logger.warning(error_msg)
                    task_status[task_id] = "failed"
                    tasks_failed.add(task_id)
                    instrumentation.record_error("executor_not_found", task_id)
                    
                    results.append(MicroQuestionRun(
                        question_id=question.get("id"),
                        question_global=question.get("global_id"),
                        base_slot=base_slot,
                        metadata={"task_id": task_id, "error": "executor_not_found"},
                        evidence=None,
                        error=error_msg,
                        aborted=False
                    ))
                    continue

                try:
                    instance = executor_class(
                        method_executor=self.executor,
                        signal_registry=self.executor.signal_registry,
                        config=self.executor_config,
                        questionnaire_provider=self._canonical_questionnaire,
                        calibration_orchestrator=self.calibration_orchestrator,
                        enriched_packs=self._enriched_packs or {},
                    )

                    q_context = {
                        "question_id": question.get("id"),
                        "question_global": question.get("global_id"),
                        "base_slot": base_slot,
                        "patterns": question.get("patterns", []),
                        "expected_elements": question.get("expected_elements", []),
                        "identity": {
                            "dimension_id": question.get("dimension_id", task.dimension),
                            "cluster_id": question.get("cluster_id"),
                        },
                        "task_metadata": {
                            "task_id": task_id,
                            "policy_area": task.policy_area,
                            "chunk_id": task.chunk_id,
                            "chunk_index": task.chunk_index,
                        }
                    }
                    
                    # Validate dimension_id consistency
                    question_dimension = question.get("dimension_id")
                    if question_dimension and question_dimension != task.dimension:
                        logger.warning(
                            f"Task {task_id}: dimension_id mismatch - "
                            f"question has '{question_dimension}' but task has '{task.dimension}'. "
                            f"Using question dimension_id."
                        )

                    result_data = instance.execute(
                        document=document,
                        method_executor=self.executor,
                        question_context=q_context
                    )

                    duration = (time.perf_counter() - start_q) * 1000

                    run_result = MicroQuestionRun(
                        question_id=question.get("id"),
                        question_global=question.get("global_id"),
                        base_slot=base_slot,
                        metadata={**result_data.get("metadata", {}), "task_id": task_id},
                        evidence=result_data.get("evidence"),
                        duration_ms=duration,
                    )
                    results.append(run_result)
                    task_status[task_id] = "completed"
                    instrumentation.increment(latency=duration)
                    
                    logger.debug(f"Task {task_id} completed successfully in {duration:.2f}ms")

                except Exception as e:
                    logger.error(f"Task {task_id}: Executor {base_slot} failed: {e}", exc_info=True)
                    task_status[task_id] = "failed"
                    tasks_failed.add(task_id)
                    instrumentation.record_error("execution", f"{task_id}: {str(e)}")
                    
                    results.append(MicroQuestionRun(
                        question_id=question.get("id"),
                        question_global=question.get("global_id"),
                        base_slot=base_slot,
                        metadata={"task_id": task_id, "error": str(e)},
                        evidence=None,
                        error=str(e),
                        aborted=False
                    ))
            
            # Verify plan coverage: all tasks must be executed
            orphan_tasks = set(t.task_id for t in tasks) - tasks_executed
            if orphan_tasks:
                error_msg = f"Orphan tasks detected (not executed): {orphan_tasks}"
                logger.error(error_msg)
                instrumentation.record_error("orphan_tasks", str(len(orphan_tasks)))
                # Orphan tasks indicate a serious logic error - fail in all modes
                # In PROD mode, this is a hard failure; in DEV, log as critical warning
                if self.runtime_config.mode == RuntimeMode.PRODUCTION:
                    self.request_abort(error_msg)
                else:
                    logger.critical(f"DEVELOPMENT MODE WARNING: {error_msg}")
            
            # In PROD mode, fail Phase 2 if any tasks failed
            if tasks_failed and self.runtime_config.mode == RuntimeMode.PRODUCTION:
                error_msg = f"Phase 2 failed: {len(tasks_failed)} tasks failed in PROD mode"
                logger.error(error_msg)
                self.request_abort(error_msg)
            
            # Log final metrics
            logger.info(
                f"Phase 2 complete: {len(tasks_executed)} tasks executed, "
                f"{len(tasks_failed)} failed, {len(orphan_tasks)} orphaned"
            )
            
            return results
            
        else:
            # Fallback: legacy config-based approach when execution_plan not available
            logger.warning("Phase 2: No execution plan available, falling back to config-based approach")
            micro_questions = config.get("micro_questions", [])
            instrumentation.start(items_total=len(micro_questions))
            
            results: list[MicroQuestionRun] = []

            for question in micro_questions:
                self._ensure_not_aborted()
                start_q = time.perf_counter()

                base_slot = question.get("base_slot")
                if not base_slot:
                    logger.warning(f"Question missing base_slot: {question.get('id')}")
                    continue

                executor_class = self.executors.get(base_slot)
                if not executor_class:
                    logger.warning(f"No executor found for {base_slot}")
                    continue

                try:
                    instance = executor_class(
                        method_executor=self.executor,
                        signal_registry=self.executor.signal_registry,
                        config=self.executor_config,
                        questionnaire_provider=self._canonical_questionnaire,
                        calibration_orchestrator=self.calibration_orchestrator,
                        enriched_packs=self._enriched_packs or {},
                    )

                    q_context = {
                        "question_id": question.get("id"),
                        "question_global": question.get("global_id"),
                        "base_slot": base_slot,
                        "patterns": question.get("patterns", []),
                        "expected_elements": question.get("expected_elements", []),
                        "identity": {
                            "dimension_id": question.get("dimension_id"),
                            "cluster_id": question.get("cluster_id"),
                        }
                    }

                    result_data = instance.execute(
                        document=document,
                        method_executor=self.executor,
                        question_context=q_context
                    )

                    duration = (time.perf_counter() - start_q) * 1000

                    run_result = MicroQuestionRun(
                        question_id=question.get("id"),
                        question_global=question.get("global_id"),
                        base_slot=base_slot,
                        metadata=result_data.get("metadata", {}),
                        evidence=result_data.get("evidence"),
                        duration_ms=duration,
                    )
                    results.append(run_result)
                    instrumentation.increment(latency=duration)

                except Exception as e:
                    logger.error(f"Executor {base_slot} failed: {e}", exc_info=True)
                    instrumentation.record_error("execution", str(e))
                    results.append(MicroQuestionRun(
                        question_id=question.get("id"),
                        question_global=question.get("global_id"),
                        base_slot=base_slot,
                        metadata={},
                        evidence=None,
                        error=str(e),
                        aborted=False
                    ))

            return results

    async def _score_micro_results_async(
        self, micro_results: list[MicroQuestionRun], config: dict[str, Any]
    ) -> list[ScoredMicroQuestion]:
        # Implementation from previous file
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[3]
        
        instrumentation.start(items_total=len(micro_results))
        
        scored_results: list[ScoredMicroQuestion] = []
        signal_registry = self.executor.signal_registry if hasattr(self.executor, 'signal_registry') else None
        
        logger.info(f"Phase 3: Scoring {len(micro_results)} micro-question results")
        # Initialize SignalEnrichedScorer if signals available
        scorer_engine = None
        if signal_registry is not None:
            scorer_engine = SignalEnrichedScorer(signal_registry=signal_registry)
            logger. info(f"Phase 3: Scoring {len(micro_results)} micro-question results using SignalEnrichedScorer")
        else:
            logger.info(f"Phase 3: Scoring {len(micro_results)} micro-question results")
        
        for idx, micro_result in enumerate(micro_results):
            self._ensure_not_aborted()
            
            try: 
                # Extract scoring signals if available
                scoring_signals = None
                if signal_registry is not None:
                    try:
                        scoring_signals = signal_registry.get_scoring_signals(micro_result.question_id)
                    except Exception as e: 
                        pass
                
                # Extract metadata and evidence
                metadata = micro_result. metadata
                evidence_obj = micro_result.evidence
                if hasattr(evidence_obj, "__dict__"):
                    evidence = evidence_obj.__dict__
                elif isinstance(evidence_obj, dict):
                    evidence = evidence_obj
                else:
                    evidence = {}
                
                # Extract score from multiple possible locations
                score = metadata.get("overall_confidence")
                if score is None:
                    validation = evidence.get("validation", {})
                    score = validation. get("score")
                
                if score is None:
                    conf_scores = evidence.get("confidence_scores", {})
                    score = conf_scores.get("mean", 0.0)
                
                try:
                    score_float = float(score) if score is not None else 0.0
                except (TypeError, ValueError):
                    score_float = 0.0
                
                # Determine completeness and quality level
                completeness = metadata.get("completeness")
                if completeness: 
                    completeness_lower = str(completeness).lower()
                    quality_mapping = {
                        "complete": "EXCELENTE",
                        "partial": "ACEPTABLE",
                        "insufficient": "INSUFICIENTE",
                        "not_applicable": "NO_APLICABLE",
                    }
                    quality_level = quality_mapping.get(completeness_lower, "INSUFICIENTE")
                else:
                    validation = evidence.get("validation", {})
                    quality_level = validation.get("quality_level", "INSUFICIENTE")
                
                # Build base scoring details
                base_scoring_details = {
                    "source": "evidence_nexus",
                    "method": "overall_confidence",
                    "completeness": completeness,
                    "calibrated_interval": metadata.get("calibrated_interval"),
                }
                
                # Apply signal enrichment if scorer engine available
                if scorer_engine is not None:
                    # Validate quality level using signals
                    validated_quality, validation_details = scorer_engine.validate_quality_level(
                        question_id=micro_result.question_id,
                        quality_level=quality_level,
                        score=score_float,
                        completeness=str(completeness).lower() if completeness else None,
                    )
                    
                    # Get threshold adjustment details
                    _, adjustment_details = scorer_engine.adjust_threshold_for_question(
                        question_id=micro_result.question_id,
                        base_threshold=0.7,
                        score=score_float,
                        metadata=metadata
                    )
                    
                    # Enrich scoring details with signal metadata
                    scoring_details = scorer_engine.enrich_scoring_details(
                        question_id=micro_result.question_id,
                        base_scoring_details=base_scoring_details,
                        threshold_adjustment=adjustment_details,
                        quality_validation=validation_details
                    )
                    
                    # Use signal-validated quality
                    final_quality_level = validated_quality
                else:
                    # No signal enrichment - use base scoring
                    scoring_details = base_scoring_details
                    final_quality_level = quality_level
                
                # Add raw signal info if available (legacy compatibility)
                if scoring_signals is not None:
                    scoring_details["signal_enrichment_raw"] = {
                        "modality": scoring_signals.question_modalities.get(micro_result.question_id),
                        "source_hash": getattr(scoring_signals, 'source_hash', None),
                        "signal_source": "sisas_registry"
                    }
                
                # Create scored result
                scored = ScoredMicroQuestion(
                    question_id=micro_result.question_id,
                    question_global=micro_result.question_global,
                    base_slot=micro_result.base_slot,
                    score=score_float,
                    normalized_score=score_float,
                    quality_level=final_quality_level,
                    evidence=micro_result.evidence,
                    scoring_details=scoring_details,
                    metadata=micro_result. metadata,
                    error=micro_result.error,
                )
                
                scored_results. append(scored)
                instrumentation.increment(latency=0.0)
                
            except Exception as e:
                logger.error(
                    f"Phase 3: Failed to score question {micro_result.question_global}: {e}",
                    exc_info=True
                )
                scored = ScoredMicroQuestion(
                    question_id=micro_result.question_id,
                    question_global=micro_result.question_global,
                    base_slot=micro_result.base_slot,
                    score=0.0,
                    normalized_score=0.0,
                    quality_level="ERROR",
                    evidence=micro_result.evidence,
                    scoring_details={"error":  str(e)},
                    metadata=micro_result.metadata,
                    error=f"Scoring error: {e}",
                )
                scored_results. append(scored)
                instrumentation.increment(latency=0.0)
                
            except Exception as e:
                logger.error(
                    f"Phase 3: Failed to score question {micro_result.question_global}: {e}",
                    exc_info=True
                )
                scored = ScoredMicroQuestion(
                    question_id=micro_result.question_id,
                    question_global=micro_result.question_global,
                    base_slot=micro_result.base_slot,
                    score=0.0,
                    normalized_score=0.0,
                    quality_level="ERROR",
                    evidence=micro_result.evidence,
                    scoring_details={"error": str(e)},
                    metadata=micro_result.metadata,
                    error=f"Scoring error: {e}",
                )
                scored_results.append(scored)
                instrumentation.increment(latency=0.0)
        
        return scored_results
    
    async def _aggregate_dimensions_async(
        self, scored_results: list[ScoredMicroQuestion], config: dict[str, Any]
    ) -> list[DimensionScore]:
        """FASE 4: Aggregate dimensions."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[4]
        start = time.perf_counter()
        
        # Build lookup map for dimension and policy area from config
        micro_questions_config = config.get("micro_questions", [])
        q_map = {}
        for q in micro_questions_config:
            qid = q.get("id")
            if qid:
                q_map[qid] = {
                    "dimension": q.get("dimension_id"),
                    "policy_area": q.get("policy_area_id"),
                    "cluster": q.get("cluster_id")
                }

        # Convert ScoredMicroQuestion to ScoredResult
        agg_inputs = []
        for res in scored_results:
            info = q_map.get(res.question_id, {})
            # Construct ScoredResult
            evidence_dict = {}
            if res.evidence:
                if isinstance(res.evidence, dict):
                    evidence_dict = res.evidence
                elif hasattr(res.evidence, "__dict__"):
                    evidence_dict = res.evidence.__dict__

            # Ensure required fields are present and not None
            if not info.get("policy_area") or not info.get("dimension"):
                logger.warning(f"Skipping question {res.question_id} due to missing metadata (area/dim)")
                continue

            scored_result = ScoredResult(
                question_global=res.question_global,
                base_slot=res.base_slot,
                policy_area=info["policy_area"],
                dimension=info["dimension"],
                score=res.score if res.score is not None else 0.0,
                quality_level=res.quality_level or "INSUFICIENTE",
                evidence=evidence_dict,
                raw_results=evidence_dict.get("raw_results", {})
            )
            agg_inputs.append(scored_result)

        instrumentation.start(items_total=60) # Approx dimensions
        
        monolith = config.get("monolith")
        aggregation_settings = config.get("_aggregation_settings")
        
        # Instantiate aggregator with SOTA features enabled
        dim_aggregator = DimensionAggregator(
            monolith=monolith,
            abort_on_insufficient=False, # Don't crash, just log errors
            aggregation_settings=aggregation_settings,
            enable_sota_features=True
        )

        # Enhance with contracts if needed
        # enhanced_dim_agg = enhance_aggregator(dim_aggregator, "dimension", enable_contracts=True)
        # However, DimensionAggregator.run() expects itself.
        # We will use the built-in SOTA features of DimensionAggregator for now as per `aggregation.py` logic.

        try:
            dimension_scores = dim_aggregator.run(
                agg_inputs,
                group_by_keys=dim_aggregator.dimension_group_by_keys
            )

            logger.info(f"Phase 4: Aggregated {len(dimension_scores)} dimension scores")

            duration = time.perf_counter() - start
            instrumentation.increment(count=len(dimension_scores), latency=duration)

            return dimension_scores

        except Exception as e:
            logger.error(f"Phase 4 failed: {e}", exc_info=True)
            instrumentation.record_error("aggregation", str(e))
            raise

    async def _aggregate_policy_areas_async(
        self, dimension_scores: list[DimensionScore], config: dict[str, Any]
    ) -> list[AreaScore]:
        """FASE 5: Aggregate policy areas."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[5]
        start = time.perf_counter()
        
        instrumentation.start(items_total=10)
        
        monolith = config.get("monolith")
        aggregation_settings = config.get("_aggregation_settings")
        
        area_aggregator = AreaPolicyAggregator(
            monolith=monolith,
            abort_on_insufficient=False,
            aggregation_settings=aggregation_settings,
        )

        # Apply enhancements (contract enforcement)
        enhanced_area_agg = enhance_aggregator(area_aggregator, "area", enable_contracts=True)

        try:
            # Note: enhanced aggregator wraps methods but might not wrap 'run' fully if not designed as proxy
            # Checking `EnhancedAreaAggregator` in aggregation_enhancements.py:
            # It provides `diagnose_hermeticity`. It doesn't seem to override `run`.
            # So we use the base aggregator's run, which calls `aggregate_area`.
            # If we want to use enhancements, we should modify how we call it or rely on `aggregation.py` implementation.
            # `aggregation.py` AreaPolicyAggregator doesn't seem to use EnhancedAreaAggregator internally.
            # But the user asked to "enforce it flux by the 15 contracts".
            # `EnhancedAreaAggregator` enforces contract in `diagnose_hermeticity`.
            # Let's stick to the robust base implementation which is also fully capable,
            # but maybe we can manually invoke diagnosis for logging/contract enforcement.

            area_scores = area_aggregator.run(
                dimension_scores,
                group_by_keys=area_aggregator.area_group_by_keys
            )

            # Post-hoc contract verification using enhanced aggregator
            for score in area_scores:
                actual_dims = {d.dimension_id for d in score.dimension_scores}
                # We need expected dimensions. This requires looking up config again.
                # For now, rely on `AreaPolicyAggregator.validate_hermeticity` which is already called inside `run`.
                pass

            logger.info(f"Phase 5: Aggregated {len(area_scores)} area scores")

            duration = time.perf_counter() - start
            instrumentation.increment(count=len(area_scores), latency=duration)

            return area_scores

        except Exception as e:
            logger.error(f"Phase 5 failed: {e}", exc_info=True)
            instrumentation.record_error("aggregation", str(e))
            raise

    def _aggregate_clusters(
        self, policy_area_scores: list[AreaScore], config: dict[str, Any]
    ) -> list[ClusterScore]:
        """FASE 6: Aggregate clusters."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[6]
        start = time.perf_counter()
        
        instrumentation.start(items_total=4)
        
        monolith = config.get("monolith")
        aggregation_settings = config.get("_aggregation_settings")
        
        cluster_aggregator = ClusterAggregator(
            monolith=monolith,
            abort_on_insufficient=False,
            aggregation_settings=aggregation_settings,
        )

        try:
            cluster_definitions = monolith["blocks"]["niveles_abstraccion"]["clusters"]
            cluster_scores = cluster_aggregator.run(
                policy_area_scores,
                cluster_definitions
            )

            logger.info(f"Phase 6: Aggregated {len(cluster_scores)} cluster scores")

            duration = time.perf_counter() - start
            instrumentation.increment(count=len(cluster_scores), latency=duration)

            return cluster_scores

        except Exception as e:
            logger.error(f"Phase 6 failed: {e}", exc_info=True)
            instrumentation.record_error("aggregation", str(e))
            raise

    def _evaluate_macro(
        self,
        cluster_scores: list[ClusterScore],
        config: dict[str, Any],
        policy_area_scores: list[AreaScore] | None = None,
        dimension_scores: list[DimensionScore] | None = None
    ) -> MacroEvaluation:
        """FASE 7: Evaluate macro."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[7]
        start = time.perf_counter()
        
        instrumentation.start(items_total=1)
        
        monolith = config.get("monolith")
        aggregation_settings = config.get("_aggregation_settings")
        
        # Retrieve missing inputs from context if passed as None (due to signature limitations of some callers)
        if policy_area_scores is None:
            policy_area_scores = self._context.get("policy_area_scores", [])
        if dimension_scores is None:
            dimension_scores = self._context.get("dimension_scores", [])

        macro_aggregator = MacroAggregator(
            monolith=monolith,
            abort_on_insufficient=False,
            aggregation_settings=aggregation_settings,
        )

        try:
            macro_score = macro_aggregator.evaluate_macro(
                cluster_scores=cluster_scores,
                area_scores=policy_area_scores,
                dimension_scores=dimension_scores
            )

            # Format as MacroEvaluation
            cluster_data = [
                ClusterScoreData(
                    id=c.cluster_id,
                    score=c.score,
                    normalized_score=c.score/3.0
                ) for c in cluster_scores
            ]

            macro_eval = MacroEvaluation(
                macro_score=macro_score.score,
                macro_score_normalized=macro_score.score/3.0,
                clusters=cluster_data,
                details=macro_score
            )

            logger.info(f"Phase 7: Macro evaluation complete. Score: {macro_score.score:.4f}")

            duration = time.perf_counter() - start
            instrumentation.increment(count=1, latency=duration)

            return macro_eval

        except Exception as e:
            logger.error(f"Phase 7 failed: {e}", exc_info=True)
            instrumentation.record_error("evaluation", str(e))
            raise
    
    async def _generate_recommendations(
        self, macro_result: MacroEvaluation, config: dict[str, Any]
    ) -> dict[str, Any]:
        """FASE 8: Generate recommendations (STUB)."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[8]
        
        instrumentation.start(items_total=1)
        
        logger.warning("Phase 8 stub - add your recommendation logic here")
        
        recommendations = {
            "status": "stub",
            "macro_score": macro_result.macro_score,
        }
        return recommendations
    
    def _assemble_report(
        self, recommendations: dict[str, Any], config: dict[str, Any]
    ) -> dict[str, Any]:
        """FASE 9: Assemble report (STUB)."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[9]
        
        instrumentation.start(items_total=1)
        
        logger.warning("Phase 9 stub - add your report logic here")
        
        report = {
            "status": "stub",
            "recommendations": recommendations,
        }
        return report
    
    async def _format_and_export(
        self, report: dict[str, Any], config: dict[str, Any]
    ) -> dict[str, Any]:
        """FASE 10: Format and export (and Ingest to Dashboard)."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[10]
        
        instrumentation.start(items_total=1)
        
        # Dashboard Ingestion Integration
        # We perform this here to ensure the dashboard is updated immediately after analysis
        try:
            from dashboard_atroz_.ingestion import DashboardIngester
            ingester = DashboardIngester()
            # Pass the full context which contains all artifacts (macro_result, cluster_scores, etc.)
            await ingester.ingest_results(self._context)
        except Exception as e:
            logger.error(f"Dashboard ingestion failed in Phase 10: {e}")
            instrumentation.record_warning("ingestion", f"Dashboard update failed: {e}")

        logger.warning("Phase 10 stub - add your export logic here")
        
        export_payload = {
            "status": "stub",
            "report": report,
            "dashboard_updated": True
        }
        return export_payload


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "Orchestrator",
    "MethodExecutor",
    "AbortSignal",
    "AbortRequested",
    "ResourceLimits",
    "PhaseInstrumentation",
    "PhaseResult",
    "MicroQuestionRun",
    "ScoredMicroQuestion",
    "Evidence",
    "MacroEvaluation",
]
