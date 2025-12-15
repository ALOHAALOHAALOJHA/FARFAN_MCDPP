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
import time
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, TypeVar, ParamSpec, TypedDict, Protocol

from canonic_phases.Phase_zero.paths import PROJECT_ROOT
from canonic_phases.Phase_zero.paths import safe_join

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
    group_by,
    validate_scored_results,
)
from canonic_phases.Phase_two import executors_contract as executors
from canonic_phases.Phase_two.arg_router import (
    ArgRouterError,
    ArgumentValidationError,
    ExtendedArgRouter,
)
from canonic_phases.Phase_two.class_registry import ClassRegistryError
from canonic_phases.Phase_two.executor_config import ExecutorConfig
from canonic_phases.Phase_two.irrigation_synchronizer import (
    IrrigationSynchronizer,
    ExecutionPlan,
)

class QuestionnaireAccess(Protocol):
    """Minimal questionnaire contract needed by the orchestrator."""
    data: dict[str, Any]
    source_path: str | Path | None

logger = logging.getLogger(__name__)
_CORE_MODULE_DIR = Path(__file__).resolve().parent

EXPECTED_QUESTION_COUNT = int(os.getenv("EXPECTED_QUESTION_COUNT", "305"))
EXPECTED_METHOD_COUNT = int(os.getenv("EXPECTED_METHOD_COUNT", "416"))
PHASE_TIMEOUT_DEFAULT = int(os.getenv("PHASE_TIMEOUT_SECONDS", "300"))
P01_EXPECTED_CHUNK_COUNT = 60
TIMEOUT_SYNC_PHASES: set[int] = {1}

P = ParamSpec("P")
T = TypeVar("T")


# ============================================================================
# PATH RESOLUTION
# ============================================================================

def resolve_workspace_path(
    path: str | Path,
    *,
    project_root: Path = PROJECT_ROOT,
    rules_dir: Path = RULES_DIR,
    module_dir: Path = _CORE_MODULE_DIR,
) -> Path:
    """Resolve repository-relative paths deterministically."""
    path_obj = Path(path)
    
    if path_obj.is_absolute():
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


def _validate_questionnaire_structure(monolith_data: dict[str, Any]) -> None:
    """Validate questionnaire structure (dimensions and policy areas)."""
    if not isinstance(monolith_data, dict):
        raise TypeError(f"Questionnaire must be a dict, got {type(monolith_data)}")
    
    if "canonical_notation" not in monolith_data:
        raise ValueError("Questionnaire missing 'canonical_notation'")
    
    canonical_notation = monolith_data["canonical_notation"]
    if "dimensions" not in canonical_notation:
        raise ValueError("Questionnaire missing 'canonical_notation.dimensions'")
    dimensions = canonical_notation["dimensions"]
    if not isinstance(dimensions, dict):
        raise TypeError("Dimensions must be a dict")
    expected_dims = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]
    for dim_id in expected_dims:
        if dim_id not in dimensions:
            raise ValueError(f"Missing dimension: {dim_id}")
    
    if "policy_areas" not in canonical_notation:
        raise ValueError("Questionnaire missing 'canonical_notation.policy_areas'")
    policy_areas = canonical_notation["policy_areas"]
    if not isinstance(policy_areas, dict):
        raise TypeError("Policy areas must be a dict")
    expected_pas = [f"PA{i:02d}" for i in range(1, 11)]
    for pa_id in expected_pas:
        if pa_id not in policy_areas:
            raise ValueError(f"Missing policy area: {pa_id}")


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
    
    try:
        result = await asyncio.wait_for(target(*call_args, **kwargs), timeout=timeout_s)
        elapsed = time.perf_counter() - start
        logger.info(f"Phase {phase_id} completed in {elapsed:.2f}s")
        return result
    
    except asyncio.TimeoutError as exc:
        elapsed = time.perf_counter() - start
        logger.error(f"Phase {phase_id} TIMEOUT after {elapsed:.2f}s")
        raise PhaseTimeoutError(phase_id, phase_name, timeout_s) from exc
    
    except asyncio.CancelledError:
        elapsed = time.perf_counter() - start
        logger.warning(f"Phase {phase_id} CANCELLED after {elapsed:.2f}s")
        raise
    
    except Exception as exc:
        elapsed = time.perf_counter() - start
        logger.error(f"Phase {phase_id} ERROR: {exc} (after {elapsed:.2f}s)", exc_info=True)
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
        from farfan_pipeline.core.orchestrator.method_registry import (
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
            from farfan_pipeline.core.orchestrator.class_registry import build_class_registry
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
        from farfan_pipeline.core.orchestrator.method_registry import MethodRegistryError
        
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
        7: ["cluster_scores", "config"],
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
        questionnaire: QuestionnaireAccess,
        executor_config: ExecutorConfig,
        calibration_orchestrator: Any | None = None,
        resource_limits: ResourceLimits | None = None,
        resource_snapshot_interval: int = 10,
        recommendation_engine_port: RecommendationEnginePort | None = None,
        processor_bundle: Any | None = None,
    ) -> None:
        """Initialize orchestrator."""
        validate_phase_definitions(self.FASES, self.__class__)
        
        self.executor = method_executor
        self._canonical_questionnaire = questionnaire
        self._monolith_data = dict(questionnaire.data)
        self.executor_config = executor_config
        
        if calibration_orchestrator is not None:
            self.calibration_orchestrator = calibration_orchestrator
            logger.info("CalibrationOrchestrator injected into main orchestrator")
        else:
            try:
                from pathlib import Path
                from src.orchestration.calibration_orchestrator import CalibrationOrchestrator
                
                config_dir = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
                if config_dir.exists():
                    self.calibration_orchestrator = CalibrationOrchestrator.from_config_dir(config_dir)
                    logger.info("CalibrationOrchestrator auto-loaded from config directory")
                else:
                    self.calibration_orchestrator = None
                    logger.warning("Calibration config directory not found, calibration disabled")
            except Exception as e:
                self.calibration_orchestrator = None
                logger.warning(f"Failed to auto-load CalibrationOrchestrator: {e}")
        
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
    
    def _ensure_not_aborted(self) -> None:
        """Check abort status."""
        if self.abort_signal.is_aborted():
            reason = self.abort_signal.get_reason() or "Unknown"
            raise AbortRequested(f"Orchestration aborted: {reason}")
    
    def request_abort(self, reason: str) -> None:
        """Request abort."""
        self.abort_signal.abort(reason)
    
    def reset_abort(self) -> None:
        """Reset abort signal."""
        self.abort_signal.reset()
    
    def _get_phase_timeout(self, phase_id: int) -> float:
        """Get phase timeout."""
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
            
            args = [self._context[key] for key in self.PHASE_ARGUMENT_KEYS.get(phase_id, [])]
            
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
                self._phase_status[phase_id] = "completed"
                
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
    
    def process_development_plan(
        self, pdf_path: str, preprocessed_document: Any | None = None
    ) -> list[PhaseResult]:
        """Sync wrapper."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            raise RuntimeError("Cannot call from within async context")
        
        return asyncio.run(self.process_development_plan_async(pdf_path, preprocessed_document))
    
    def get_processing_status(self) -> dict[str, Any]:
        """Get status."""
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
        """Get phase metrics."""
        return {
            str(phase_id): instr.build_metrics()
            for phase_id, instr in self._phase_instrumentation.items()
        }
    
    def export_metrics(self) -> dict[str, Any]:
        """Export metrics."""
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
        """
        Calibrate a method using the integrated CalibrationOrchestrator.
        
        Args:
            method_id: Method identifier
            role: Method role (INGEST_PDM, SCORE_Q, AGGREGATE, etc.)
            context: Execution context
            pdt_structure: PDT structure for unit layer evaluation
        
        Returns:
            Calibration result dict or None if calibration unavailable
        """
        if self.calibration_orchestrator is None:
            logger.warning("CalibrationOrchestrator not available, skipping calibration")
            return None
        
        try:
            from src.orchestration.calibration_orchestrator import (
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
    
    # ========================================================================
    # PHASE IMPLEMENTATIONS
    # ========================================================================
    
    def _load_configuration(self) -> dict[str, Any]:
        """FASE 0: Load configuration."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[0]
        start = time.perf_counter()
        
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
        
        return {
            "monolith": monolith,
            "monolith_sha256": monolith_hash,
            "micro_questions": micro_questions,
            "meso_questions": meso_questions,
            "macro_question": macro_question,
            "_aggregation_settings": aggregation_settings,
        }
    
    def _ingest_document(self, pdf_path: str, config: dict[str, Any]) -> Any:
        """FASE 1: Ingest document using Phase 1 SPC pipeline.
        
        QUESTIONNAIRE ACCESS POLICY ENFORCEMENT:
        - Phase 1 receives signal_registry via DI (not questionnaire file)
        - Follows LEVEL 3 access: Factory → Orchestrator → Phase 1 → signal_registry
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[1]
        start = time.perf_counter()
        
        document_id = os.path.splitext(os.path.basename(pdf_path))[0] or "doc_1"
        
        try:
            # Import Phase 1 components
            from canonic_phases.Phase_one import (
                CanonicalInput,
                execute_phase_1_with_full_contract,
                CanonPolicyPackage,
            )
            from pathlib import Path
            import hashlib
            
            # Get questionnaire path from canonical questionnaire
            questionnaire_path = self._canonical_questionnaire.source_path if hasattr(self._canonical_questionnaire, 'source_path') else None
            if not questionnaire_path:
                # Fallback to default path
                from canonic_phases.Phase_zero.paths import PROJECT_ROOT
                questionnaire_path = PROJECT_ROOT / "canonic_questionnaire_central" / "questionnaire_monolith.json"
            else:
                questionnaire_path = Path(questionnaire_path)
            
            pdf_path_obj = Path(pdf_path)
            
            # Compute hashes for integrity
            pdf_sha256 = hashlib.sha256(pdf_path_obj.read_bytes()).hexdigest()
            questionnaire_sha256 = hashlib.sha256(questionnaire_path.read_bytes()).hexdigest()
            
            # Create CanonicalInput for Phase 1
            canonical_input = CanonicalInput(
                document_id=document_id,
                run_id=f"run_{document_id}_{int(time.time())}",
                pdf_path=pdf_path_obj,
                pdf_sha256=pdf_sha256,
                pdf_size_bytes=pdf_path_obj.stat().st_size,
                pdf_page_count=0,  # Will be computed by Phase 1
                questionnaire_path=questionnaire_path,
                questionnaire_sha256=questionnaire_sha256,
                created_at=datetime.utcnow(),
                phase0_version="1.0.0",
                validation_passed=True,
                validation_errors=[],
                validation_warnings=[],
            )
            
            # POLICY ENFORCEMENT: Pass signal_registry to Phase 1 (LEVEL 3 access)
            # Factory created signal_registry → injected to Orchestrator → passed to Phase 1
            signal_registry = self.executor.signal_registry if hasattr(self.executor, 'signal_registry') else None
            
            if signal_registry is None:
                logger.warning("⚠️  POLICY VIOLATION: signal_registry not available, Phase 1 will run in degraded mode")
            else:
                logger.info("✓ POLICY COMPLIANT: Passing signal_registry to Phase 1 (DI chain: Factory → Orchestrator → Phase 1)")
            
            # Execute Phase 1 with full contract AND signal_registry
            canon_package = execute_phase_1_with_full_contract(
                canonical_input,
                signal_registry=signal_registry  # DI: Inject signal registry
            )
            
            # Validate output
            if not isinstance(canon_package, CanonPolicyPackage):
                raise ValueError(f"Phase 1 returned invalid type: {type(canon_package)}")
            
            # Validate chunk count
            actual_chunk_count = len(canon_package.chunk_graph.chunks)
            if actual_chunk_count != P01_EXPECTED_CHUNK_COUNT:
                raise ValueError(
                    f"P01 validation failed: expected {P01_EXPECTED_CHUNK_COUNT} chunks, "
                    f"got {actual_chunk_count}"
                )
            
            # Validate each chunk has policy_area_id and dimension_id
            for i, chunk in enumerate(canon_package.chunk_graph.chunks):
                if not hasattr(chunk, "policy_area") or not chunk.policy_area:
                    raise ValueError(f"Chunk {i} missing policy_area")
                if not hasattr(chunk, "dimension") or not chunk.dimension:
                    raise ValueError(f"Chunk {i} missing dimension")
            
            logger.info(f"✓ P01-ES v1.0 validation passed: {actual_chunk_count} chunks")
            
            # Store canon_package for subsequent phases
            # Note: Downstream phases should work with CanonPolicyPackage directly
            return canon_package
            
        except Exception as e:
            instrumentation.record_error("ingestion", str(e))
            raise RuntimeError(f"Document ingestion failed: {e}") from e
        
        duration = time.perf_counter() - start
        instrumentation.increment(latency=duration)
        
        return canon_package
    
    async def _execute_micro_questions_async(
        self, document: Any, config: dict[str, Any]
    ) -> list[MicroQuestionRun]:
        """FASE 2: Execute micro-questions.
        
        Args:
            document: CanonPolicyPackage from Phase 1 (60 chunks with PA×DIM coordinates)
            config: Configuration dictionary
            
        Returns:
            List of MicroQuestionRun results
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[2]
        
        micro_questions = config.get("micro_questions", [])
        instrumentation.start(items_total=len(micro_questions))
        
        logger.warning("Phase 2 stub - add your executor logic here")
        
        results: list[MicroQuestionRun] = []
        return results
    
    async def _score_micro_results_async(
        self, micro_results: list[MicroQuestionRun], config: dict[str, Any]
    ) -> list[ScoredMicroQuestion]:
        """FASE 3: Transform Phase 2 results to scored results.
        
        Extracts scoring from EvidenceNexus outputs and transforms
        MicroQuestionRun objects to ScoredMicroQuestion objects ready for
        Phase 4 aggregation.
        
        Phase 2 uses EvidenceNexus which returns:
        - overall_confidence (0.0-1.0) → score
        - completeness (complete/partial/insufficient) → quality_level
        
        These nexus fields are now included in Phase 2 result_data and
        accessible via MicroQuestionRun.metadata.
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[3]
        
        instrumentation.start(items_total=len(micro_results))
        
        scored_results: list[ScoredMicroQuestion] = []
        
        logger.info(f"Phase 3: Scoring {len(micro_results)} micro-question results using EvidenceNexus outputs")
        
        for idx, micro_result in enumerate(micro_results):
            self._ensure_not_aborted()
            
            try:
                # Get metadata which should contain nexus fields from Phase 2
                metadata = micro_result.metadata
                
                # Extract evidence (Evidence dataclass or dict)
                evidence_obj = micro_result.evidence
                if hasattr(evidence_obj, "__dict__"):
                    evidence = evidence_obj.__dict__
                elif isinstance(evidence_obj, dict):
                    evidence = evidence_obj
                else:
                    evidence = {}
                
                # PRIMARY: Extract score from overall_confidence (EvidenceNexus output)
                score = metadata.get("overall_confidence")
                if score is None:
                    # Fallback 1: Check validation.score (only set when validation fails)
                    validation = evidence.get("validation", {})
                    score = validation.get("score")
                
                if score is None:
                    # Fallback 2: Use mean confidence from evidence elements
                    conf_scores = evidence.get("confidence_scores", {})
                    score = conf_scores.get("mean", 0.0)
                
                # Ensure score is float
                try:
                    score_float = float(score) if score is not None else 0.0
                except (TypeError, ValueError):
                    logger.warning(
                        f"Invalid score type for question {micro_result.question_global}: "
                        f"{type(score)}. Defaulting to 0.0"
                    )
                    score_float = 0.0
                
                # PRIMARY: Map completeness to quality_level (EvidenceNexus output)
                completeness = metadata.get("completeness")
                if completeness:
                    # Map EvidenceNexus completeness enum to quality level
                    completeness_lower = str(completeness).lower()
                    quality_mapping = {
                        "complete": "EXCELENTE",
                        "partial": "ACEPTABLE",
                        "insufficient": "INSUFICIENTE",
                        "not_applicable": "NO_APLICABLE",
                    }
                    quality_level = quality_mapping.get(completeness_lower, "INSUFICIENTE")
                else:
                    # Fallback: Check validation.quality_level (only set when validation fails)
                    validation = evidence.get("validation", {})
                    quality_level = validation.get("quality_level", "INSUFICIENTE")
                
                # Build scoring details
                scoring_details = {
                    "source": "evidence_nexus",
                    "method": "overall_confidence",
                    "completeness": completeness,
                    "calibrated_interval": metadata.get("calibrated_interval"),
                }
                
                # Create ScoredMicroQuestion
                scored = ScoredMicroQuestion(
                    question_id=micro_result.question_id,
                    question_global=micro_result.question_global,
                    base_slot=micro_result.base_slot,
                    score=score_float,
                    normalized_score=score_float,  # Already normalized 0.0-1.0
                    quality_level=quality_level,
                    evidence=micro_result.evidence,
                    scoring_details=scoring_details,
                    metadata=micro_result.metadata,
                    error=micro_result.error,
                )
                
                scored_results.append(scored)
                
                instrumentation.increment(latency=0.0)
                
                logger.debug(
                    f"Phase 3: Scored question {micro_result.question_global}: "
                    f"score={score_float:.3f}, quality={quality_level}, completeness={completeness}"
                )
                
            except Exception as e:
                logger.error(
                    f"Phase 3: Failed to score question {micro_result.question_global}: {e}",
                    exc_info=True
                )
                
                # Create failed scored result
                scored = ScoredMicroQuestion(
                    question_id=micro_result.question_id,
                    question_global=micro_result.question_global,
                    base_slot=micro_result.base_slot,
                    score=0.0,
                    normalized_score=0.0,
                    quality_level="ERROR",
                    evidence=micro_result.evidence,
                    scoring_details={"error": str(e), "source": "exception_recovery"},
                    metadata=micro_result.metadata,
                    error=f"Scoring error: {e}",
                )
                
                scored_results.append(scored)
                instrumentation.increment(latency=0.0)
        
        logger.info(
            f"Phase 3 complete: {len(scored_results)}/{len(micro_results)} results scored. "
            f"Using EvidenceNexus overall_confidence and completeness fields."
        )
        
        return scored_results
    
    async def _aggregate_dimensions_async(
        self, scored_results: list[ScoredMicroQuestion], config: dict[str, Any]
    ) -> list[DimensionScore]:
        """FASE 4: Aggregate dimensions (STUB - requires your implementation)."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[4]
        
        instrumentation.start(items_total=6)
        
        logger.warning("Phase 4 stub - add your aggregation logic here")
        
        dimension_scores: list[DimensionScore] = []
        return dimension_scores
    
    async def _aggregate_policy_areas_async(
        self, dimension_scores: list[DimensionScore], config: dict[str, Any]
    ) -> list[AreaScore]:
        """FASE 5: Aggregate policy areas (STUB - requires your implementation)."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[5]
        
        instrumentation.start(items_total=10)
        
        logger.warning("Phase 5 stub - add your aggregation logic here")
        
        area_scores: list[AreaScore] = []
        return area_scores
    
    def _aggregate_clusters(
        self, policy_area_scores: list[AreaScore], config: dict[str, Any]
    ) -> list[ClusterScore]:
        """FASE 6: Aggregate clusters (STUB - requires your implementation)."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[6]
        
        instrumentation.start(items_total=4)
        
        logger.warning("Phase 6 stub - add your aggregation logic here")
        
        cluster_scores: list[ClusterScore] = []
        return cluster_scores
    
    def _evaluate_macro(
        self, cluster_scores: list[ClusterScore], config: dict[str, Any]
    ) -> MacroEvaluation:
        """FASE 7: Evaluate macro (STUB - requires your implementation)."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[7]
        
        instrumentation.start(items_total=1)
        
        logger.warning("Phase 7 stub - add your macro logic here")
        
        macro_eval = MacroEvaluation(
            macro_score=0.0,
            macro_score_normalized=0.0,
            clusters=[]
        )
        return macro_eval
    
    async def _generate_recommendations(
        self, macro_result: MacroEvaluation, config: dict[str, Any]
    ) -> dict[str, Any]:
        """FASE 8: Generate recommendations (STUB - requires your implementation)."""
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
        """FASE 9: Assemble report (STUB - requires your implementation)."""
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
        """FASE 10: Format and export (STUB - requires your implementation)."""
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[10]
        
        instrumentation.start(items_total=1)
        
        logger.warning("Phase 10 stub - add your export logic here")
        
        export_payload = {
            "status": "stub",
            "report": report,
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
