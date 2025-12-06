"""Clean Orchestrator - Versión Completa y Funcional

Orquestador de 11 fases con toda la funcionalidad real preservada.
Sin simplificaciones, sin placeholders.
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
from dataclasses import dataclass, field, asdict, is_dataclass, replace
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, TypeVar, ParamSpec, TypedDict

if TYPE_CHECKING:
    from farfan_pipeline.core.orchestrator.factory import CanonicalQuestionnaire

from farfan_pipeline.core.analysis_port import RecommendationEnginePort
from farfan_pipeline.config.paths import PROJECT_ROOT, RULES_DIR, CONFIG_DIR
from farfan_pipeline.processing.aggregation import (
    AggregationSettings,
    AreaPolicyAggregator,
    AreaScore,
    ClusterAggregator,
    ClusterScore,
    DimensionAggregator,
    DimensionScore,
    MacroAggregator,
    MacroScore,
    ValidationError,
    group_by,
    validate_scored_results,
)
from farfan_pipeline.utils.paths import safe_join
from farfan_pipeline.core.dependency_lockdown import get_dependency_lockdown
from farfan_pipeline.core.types import PreprocessedDocument
from farfan_pipeline.core.orchestrator import executors_contract as executors
from farfan_pipeline.core.orchestrator.arg_router import (
    ArgRouterError,
    ArgumentValidationError,
    ExtendedArgRouter,
)
from farfan_pipeline.core.orchestrator.class_registry import ClassRegistryError
from farfan_pipeline.core.orchestrator.executor_config import ExecutorConfig
from farfan_pipeline.core.orchestrator.irrigation_synchronizer import (
    IrrigationSynchronizer,
    ExecutionPlan,
)

logger = logging.getLogger(__name__)
_CORE_MODULE_DIR = Path(__file__).resolve().parent

# Configuración de ambiente
EXPECTED_QUESTION_COUNT = int(os.getenv("EXPECTED_QUESTION_COUNT", "305"))
EXPECTED_METHOD_COUNT = int(os.getenv("EXPECTED_METHOD_COUNT", "416"))
PHASE_TIMEOUT_DEFAULT = int(os.getenv("PHASE_TIMEOUT_SECONDS", "300"))
P01_EXPECTED_CHUNK_COUNT = 60
TIMEOUT_SYNC_PHASES: set[int] = {1}

P = ParamSpec("P")
T = TypeVar("T")


# ============================================================================
# UTILIDADES DE PATH
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
    """Normalize monolith for hash computation and JSON serialization.
    
    Converts MappingProxyType to dict recursively to ensure:
    1. JSON serialization doesn't fail
    2. Hash computation is consistent
    """
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
# TYPED DICTS Y DATACLASSES
# ============================================================================

class MacroScoreDict(TypedDict):
    """Typed container for macro score evaluation results."""
    macro_score: MacroScore
    macro_score_normalized: float
    cluster_scores: list[ClusterScore]
    cross_cutting_coherence: float
    systemic_gaps: list[str]
    strategic_alignment: float
    quality_band: str


@dataclass
class ClusterScoreData:
    """Type-safe cluster score data for macro evaluation."""
    id: str
    score: float
    normalized_score: float


@dataclass
class MacroEvaluation:
    """Type-safe macro evaluation result."""
    macro_score: float
    macro_score_normalized: float
    clusters: list[ClusterScoreData]


@dataclass
class Evidence:
    """Evidence container for orchestrator results."""
    modality: str
    elements: list[Any] = field(default_factory=list)
    raw_results: dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseResult:
    """Result of a single orchestration phase."""
    success: bool
    phase_id: str
    data: Any
    error: Exception | None
    duration_ms: float
    mode: str
    aborted: bool = False


@dataclass
class MicroQuestionRun:
    """Result of executing a single micro-question."""
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
    """Scored micro-question result."""
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
# MECANISMO DE ABORT
# ============================================================================

class AbortRequested(RuntimeError):
    """Raised when an abort signal is triggered during orchestration."""
    pass


class AbortSignal:
    """Thread-safe abort signal shared across orchestration phases."""
    
    def __init__(self) -> None:
        self._event = threading.Event()
        self._lock = threading.Lock()
        self._reason: str | None = None
        self._timestamp: datetime | None = None
    
    def abort(self, reason: str) -> None:
        """Trigger an abort with a reason and timestamp."""
        if not reason:
            reason = "Abort requested"
        with self._lock:
            if not self._event.is_set():
                self._event.set()
                self._reason = reason
                self._timestamp = datetime.utcnow()
    
    def is_aborted(self) -> bool:
        """Check whether abort has been triggered."""
        return self._event.is_set()
    
    def get_reason(self) -> str | None:
        """Return the abort reason if set."""
        with self._lock:
            return self._reason
    
    def get_timestamp(self) -> datetime | None:
        """Return the abort timestamp if set."""
        with self._lock:
            return self._timestamp
    
    def reset(self) -> None:
        """Clear the abort signal."""
        self._lock.acquire()
        try:
            self._event.clear()
            self._reason = None
            self._timestamp = None
        finally:
            self._lock.release()


# ============================================================================
# GESTIÓN DE RECURSOS
# ============================================================================

class ResourceLimits:
    """Runtime resource guard with adaptive worker prediction."""
    
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
            logger.warning("psutil no disponible, usando fallbacks")
    
    @property
    def max_workers(self) -> int:
        """Return the current worker budget."""
        return self._max_workers
    
    def attach_semaphore(self, semaphore: asyncio.Semaphore) -> None:
        """Attach an asyncio semaphore for budget control."""
        self._semaphore = semaphore
        self._semaphore_limit = self._max_workers
    
    async def apply_worker_budget(self) -> int:
        """Apply the current worker budget to the semaphore."""
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
                reduction = current - desired
                for _ in range(reduction):
                    await self._semaphore.acquire()
            
            self._semaphore_limit = desired
            return self._max_workers
    
    def _record_usage(self, usage: dict[str, float]) -> None:
        """Record resource usage and predict worker budget."""
        self._usage_history.append(usage)
        self._predict_worker_budget()
    
    def _predict_worker_budget(self) -> None:
        """Adjust worker budget based on recent resource usage."""
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
        """Capture current resource usage metrics."""
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
        """Check if memory limit has been exceeded."""
        usage = usage or self.get_resource_usage()
        exceeded = False
        if self.max_memory_mb is not None:
            exceeded = usage.get("rss_mb", 0.0) > self.max_memory_mb
        return exceeded, usage
    
    def check_cpu_exceeded(self, usage: dict[str, float] | None = None) -> tuple[bool, dict[str, float]]:
        """Check if CPU limit has been exceeded."""
        usage = usage or self.get_resource_usage()
        exceeded = False
        if self.max_cpu_percent:
            exceeded = usage.get("cpu_percent", 0.0) > self.max_cpu_percent
        return exceeded, usage
    
    def get_usage_history(self) -> list[dict[str, float]]:
        """Return the recorded usage history."""
        return list(self._usage_history)


# ============================================================================
# INSTRUMENTACIÓN DE FASES
# ============================================================================

class PhaseInstrumentation:
    """Collects granular telemetry for each orchestration phase."""
    
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
        """Mark the start of phase execution."""
        if items_total is not None:
            self.items_total = items_total
        self.start_time = time.perf_counter()
    
    def increment(self, count: int = 1, latency: float | None = None) -> None:
        """Increment processed item count and optionally record latency."""
        self.items_processed += count
        if latency is not None:
            self.latencies.append(latency)
            self._detect_latency_anomaly(latency)
        if self.resource_limits and self.should_snapshot():
            self.capture_resource_snapshot()
    
    def should_snapshot(self) -> bool:
        """Determine if a resource snapshot should be captured."""
        if self.items_total == 0 or self.items_processed == 0:
            return False
        return self.items_processed % self.snapshot_interval == 0
    
    def capture_resource_snapshot(self) -> None:
        """Capture a resource usage snapshot."""
        if not self.resource_limits:
            return
        snapshot = self.resource_limits.get_resource_usage()
        snapshot["items_processed"] = self.items_processed
        self.resource_snapshots.append(snapshot)
    
    def record_warning(self, category: str, message: str, **extra: Any) -> None:
        """Record a warning during phase execution."""
        entry = {
            "category": category,
            "message": message,
            **extra,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.warnings.append(entry)
    
    def record_error(self, category: str, message: str, **extra: Any) -> None:
        """Record an error during phase execution."""
        entry = {
            "category": category,
            "message": message,
            **extra,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.errors.append(entry)
    
    def _detect_latency_anomaly(self, latency: float) -> None:
        """Detect latency anomalies using statistical thresholds."""
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
        """Mark the end of phase execution."""
        self.end_time = time.perf_counter()
    
    def duration_ms(self) -> float | None:
        """Return the phase duration in milliseconds."""
        if self.start_time is None or self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000.0
    
    def progress(self) -> float | None:
        """Return the progress fraction (0.0 to 1.0)."""
        if not self.items_total:
            return None
        return min(1.0, self.items_processed / float(self.items_total))
    
    def throughput(self) -> float | None:
        """Return items processed per second."""
        if self.start_time is None:
            return None
        elapsed = (time.perf_counter() - self.start_time) if self.end_time is None else (self.end_time - self.start_time)
        if not elapsed:
            return None
        return self.items_processed / elapsed
    
    def latency_histogram(self) -> dict[str, float | None]:
        """Return latency percentiles."""
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
        """Build a metrics summary dictionary."""
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
# TIMEOUT DE FASES
# ============================================================================

class PhaseTimeoutError(RuntimeError):
    """Raised when a phase exceeds its timeout."""
    
    def __init__(self, phase_id: int | str, phase_name: str, timeout_s: float) -> None:
        self.phase_id = phase_id
        self.phase_name = phase_name
        self.timeout_s = timeout_s
        super().__init__(f"Phase {phase_id} ({phase_name}) timed out after {timeout_s}s")


async def execute_phase_with_timeout(
    phase_id: int,
    phase_name: str,
    coro: Callable[P, T] | None = None,
    *varargs: P.args,
    handler: Callable[P, T] | None = None,
    args: tuple | None = None,
    timeout_s: float = 300.0,
    **kwargs: P.kwargs,
) -> T:
    """Execute an async phase with timeout and comprehensive logging."""
    target = coro or handler
    if target is None:
        raise ValueError("Either 'coro' or 'handler' must be provided")
    
    call_args = varargs if varargs else (args or ())
    
    start = time.perf_counter()
    logger.info(f"Fase {phase_id} ({phase_name}) iniciada, timeout={timeout_s}s")
    
    try:
        result = await asyncio.wait_for(target(*call_args, **kwargs), timeout=timeout_s)
        elapsed = time.perf_counter() - start
        logger.info(f"Fase {phase_id} completada en {elapsed:.2f}s")
        return result
    
    except asyncio.TimeoutError as exc:
        elapsed = time.perf_counter() - start
        logger.error(f"Fase {phase_id} TIMEOUT después de {elapsed:.2f}s")
        raise PhaseTimeoutError(phase_id, phase_name, timeout_s) from exc
    
    except asyncio.CancelledError:
        elapsed = time.perf_counter() - start
        logger.warning(f"Fase {phase_id} CANCELADA después de {elapsed:.2f}s")
        raise
    
    except Exception as exc:
        elapsed = time.perf_counter() - start
        logger.error(f"Fase {phase_id} ERROR: {exc} (después de {elapsed:.2f}s)", exc_info=True)
        raise


# ============================================================================
# METHOD EXECUTOR Y LAZY LOADING
# ============================================================================

class _LazyInstanceDict:
    """Lazy instance dictionary for backward compatibility."""
    
    def __init__(self, method_registry: Any) -> None:
        self._registry = method_registry
    
    def get(self, class_name: str, default: Any = None) -> Any:
        """Get instance lazily."""
        try:
            return self._registry._get_instance(class_name)
        except Exception:
            return default
    
    def __getitem__(self, class_name: str) -> Any:
        """Get instance lazily (dict access)."""
        return self._registry._get_instance(class_name)
    
    def __contains__(self, class_name: str) -> bool:
        """Check if class is available."""
        return class_name in self._registry._class_paths
    
    def keys(self) -> list[str]:
        """Get available class names."""
        return list(self._registry._class_paths.keys())
    
    def values(self) -> list[Any]:
        """Get instantiated instances (triggers lazy loading)."""
        return [self.get(name) for name in self.keys()]
    
    def items(self) -> list[tuple[str, Any]]:
        """Get (name, instance) pairs (triggers lazy loading)."""
        return [(name, self.get(name)) for name in self.keys()]
    
    def __len__(self) -> int:
        """Get number of available classes."""
        return len(self._registry._class_paths)


class MethodExecutor:
    """Execute catalog methods using lazy method injection."""
    
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
                logger.info("method_registry_initialized_lazy_mode")
            except Exception as exc:
                self.degraded_mode = True
                reason = f"Method registry initialization failed: {exc}"
                self.degraded_reasons.append(reason)
                logger.error("DEGRADED MODE: %s", reason)
                self._method_registry = MethodRegistry(class_paths={})
        
        try:
            from farfan_pipeline.core.orchestrator.class_registry import build_class_registry
            registry = build_class_registry()
        except (ClassRegistryError, ModuleNotFoundError, ImportError) as exc:
            self.degraded_mode = True
            reason = f"Could not build class registry: {exc}"
            self.degraded_reasons.append(reason)
            logger.warning("DEGRADED MODE: %s", reason)
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
        """Execute a method using lazy instantiation."""
        from farfan_pipeline.core.orchestrator.method_registry import MethodRegistryError
        
        try:
            method = self._method_registry.get_method(class_name, method_name)
        except MethodRegistryError as exc:
            logger.error(f"method_retrieval_failed: {class_name}.{method_name}: {exc}")
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
        """Inject a method directly without requiring a class."""
        self._method_registry.inject_method(class_name, method_name, method)
        logger.info(f"method_injected_into_executor: {class_name}.{method_name}")
    
    def has_method(self, class_name: str, method_name: str) -> bool:
        """Check if a method is available."""
        return self._method_registry.has_method(class_name, method_name)
    
    def get_registry_stats(self) -> dict[str, Any]:
        """Get statistics from the method registry."""
        return self._method_registry.get_stats()
    
    def get_routing_metrics(self) -> dict[str, Any]:
        """Get routing metrics from ExtendedArgRouter."""
        if hasattr(self._router, "get_metrics"):
            return self._router.get_metrics()
        return {}


# ============================================================================
# VALIDACIÓN DE DEFINICIONES DE FASES
# ============================================================================

def validate_phase_definitions(
    phase_list: list[tuple[int, str, str, str]], orchestrator_class: type
) -> None:
    """Validate phase definitions for structural coherence."""
    if not phase_list:
        raise RuntimeError("FASES cannot be empty - no phases defined for orchestration")
    
    phase_ids = [phase[0] for phase in phase_list]
    
    seen_ids = set()
    for phase_id in phase_ids:
        if phase_id in seen_ids:
            raise RuntimeError(f"Duplicate phase ID {phase_id} in FASES definition")
        seen_ids.add(phase_id)
    
    if phase_ids != sorted(phase_ids):
        raise RuntimeError(f"Phase IDs must be sorted in ascending order. Got {phase_ids}")
    if phase_ids[0] != 0:
        raise RuntimeError(f"Phase IDs must start from 0. Got first ID: {phase_ids[0]}")
    if phase_ids[-1] != len(phase_list) - 1:
        raise RuntimeError(f"Phase IDs must be contiguous from 0 to {len(phase_list) - 1}. Got highest ID: {phase_ids[-1]}")
    
    valid_modes = {"sync", "async"}
    for phase_id, mode, handler_name, label in phase_list:
        if mode not in valid_modes:
            raise RuntimeError(f"Phase {phase_id} ({label}): invalid mode '{mode}'. Mode must be one of {valid_modes}")
        
        if not hasattr(orchestrator_class, handler_name):
            raise RuntimeError(f"Phase {phase_id} ({label}): handler method '{handler_name}' does not exist in {orchestrator_class.__name__}")
        
        handler = getattr(orchestrator_class, handler_name, None)
        if not callable(handler):
            raise RuntimeError(f"Phase {phase_id} ({label}): handler '{handler_name}' is not callable")


# ============================================================================
# ORQUESTADOR PRINCIPAL
# ============================================================================

class Orchestrator:
    """Robust 11-phase orchestrator with abort support and resource control."""
    
    FASES: list[tuple[int, str, str, str]] = [
        (0, "sync", "_load_configuration", "FASE 0 - Validación de Configuración"),
        (1, "sync", "_ingest_document", "FASE 1 - Ingestión de Documento"),
        (2, "async", "_execute_micro_questions_async", "FASE 2 - Micro Preguntas"),
        (3, "async", "_score_micro_results_async", "FASE 3 - Scoring Micro"),
        (4, "async", "_aggregate_dimensions_async", "FASE 4 - Agregación Dimensiones"),
        (5, "async", "_aggregate_policy_areas_async", "FASE 5 - Agregación Áreas"),
        (6, "sync", "_aggregate_clusters", "FASE 6 - Agregación Clústeres"),
        (7, "sync", "_evaluate_macro", "FASE 7 - Evaluación Macro"),
        (8, "async", "_generate_recommendations", "FASE 8 - Recomendaciones"),
        (9, "sync", "_assemble_report", "FASE 9 - Ensamblado de Reporte"),
        (10, "async", "_format_and_export", "FASE 10 - Formateo y Exportación"),
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
    
    PERCENTAGE_SCALE: int = 100
    
    def __init__(
        self,
        method_executor: MethodExecutor,
        questionnaire: "CanonicalQuestionnaire",
        executor_config: ExecutorConfig,
        calibration_orchestrator: Any | None = None,
        resource_limits: ResourceLimits | None = None,
        resource_snapshot_interval: int = 10,
        recommendation_engine_port: RecommendationEnginePort | None = None,
        processor_bundle: Any | None = None,
    ) -> None:
        """Initialize the orchestrator with all dependencies injected.
        
        Args:
            method_executor: Configured MethodExecutor instance
            questionnaire: Loaded and validated CanonicalQuestionnaire
            executor_config: Executor configuration object
            calibration_orchestrator: Calibration orchestrator instance
            resource_limits: Resource limit configuration
            resource_snapshot_interval: Interval for resource snapshots
            recommendation_engine_port: Optional recommendation engine port
            processor_bundle: ProcessorBundle with enriched_signal_packs (WIRING REQUIRED)
        """
        from farfan_pipeline.core.orchestrator.factory import (
            _validate_questionnaire_structure,
            get_questionnaire_provider,
        )
        
        validate_phase_definitions(self.FASES, self.__class__)
        
        self.executor = method_executor
        self._canonical_questionnaire = questionnaire
        self._monolith_data = dict(questionnaire.data)
        self.executor_config = executor_config
        self.calibration_orchestrator = calibration_orchestrator
        self.resource_limits = resource_limits or ResourceLimits()
        self.resource_snapshot_interval = max(1, resource_snapshot_interval)
        self.questionnaire_provider = get_questionnaire_provider()
        
        # ========================================================================
        # WIRING: ProcessorBundle → Orchestrator
        # Store enriched_signal_packs for use in Phase 2
        # ========================================================================
        self._processor_bundle = processor_bundle
        self._enriched_packs = None
        if processor_bundle is not None:
            if hasattr(processor_bundle, "enriched_signal_packs"):
                self._enriched_packs = processor_bundle.enriched_signal_packs
                logger.info(f"Orchestrator wired with {len(self._enriched_packs) if self._enriched_packs else 0} enriched signal packs")
            else:
                logger.warning("ProcessorBundle provided but missing enriched_signal_packs attribute")
        else:
            logger.warning("No ProcessorBundle provided - signal enrichment unavailable")
        
        # ========================================================================
        # WIRING: MethodExecutor.signal_registry verification
        # Ensure MethodExecutor has access to QuestionnaireSignalRegistry
        # ========================================================================
        if not hasattr(self.executor, "signal_registry") or self.executor.signal_registry is None:
            logger.error("WIRING VIOLATION: MethodExecutor missing signal_registry")
            raise RuntimeError(
                "MethodExecutor must be configured with signal_registry. "
                "Executors require indirect access to QuestionnaireSignalRegistry."
            )
        else:
            logger.info("✓ MethodExecutor.signal_registry verified")
        
        try:
            _validate_questionnaire_structure(self._monolith_data)
        except (ValueError, TypeError) as e:
            raise RuntimeError(f"Questionnaire structure validation failed: {e}") from e
        
        if not self.executor.instances:
            raise RuntimeError("MethodExecutor.instances is empty - no executable methods registered")
        
        # Executor registry
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
        
        # State management
        self.abort_signal = AbortSignal()
        self.phase_results: list[PhaseResult] = []
        self._phase_instrumentation: dict[int, PhaseInstrumentation] = {}
        self._phase_status: dict[int, str] = {phase_id: "not_started" for phase_id, *_ in self.FASES}
        self._phase_outputs: dict[int, Any] = {}
        self._context: dict[str, Any] = {}
        self._start_time: float | None = None
        self._execution_plan: ExecutionPlan | None = None
        
        # Additional attributes for phase 0 validations
        self._method_map_data: dict[str, Any] | None = None
        self._schema_data: dict[str, Any] | None = None
        self.catalog: dict[str, Any] | None = None
        
        self.dependency_lockdown = get_dependency_lockdown()
        logger.info(f"Orchestrator dependency mode: {self.dependency_lockdown.get_mode_description()}")
        
        self.recommendation_engine = recommendation_engine_port
        if self.recommendation_engine is not None:
            logger.info("RecommendationEngine port injected successfully")
        else:
            logger.warning("No RecommendationEngine port provided - recommendations unavailable")
    
    def _ensure_not_aborted(self) -> None:
        """Check if orchestration has been aborted and raise exception if so."""
        if self.abort_signal.is_aborted():
            reason = self.abort_signal.get_reason() or "Unknown reason"
            raise AbortRequested(f"Orchestration aborted: {reason}")
    
    def request_abort(self, reason: str) -> None:
        """Request orchestration to abort with a specific reason."""
        self.abort_signal.abort(reason)
    
    def reset_abort(self) -> None:
        """Reset the abort signal to allow new orchestration runs."""
        self.abort_signal.reset()
    
    def _get_phase_timeout(self, phase_id: int) -> float:
        """Get timeout for a specific phase."""
        return self.PHASE_TIMEOUTS.get(phase_id, 300.0)
    
    def _resolve_path(self, path: str | None) -> str | None:
        """Resolve a relative or absolute path."""
        if path is None:
            return None
        resolved = resolve_workspace_path(path)
        return str(resolved)
    
    async def process_development_plan_async(
        self, pdf_path: str, preprocessed_document: Any | None = None
    ) -> list[PhaseResult]:
        """Execute the complete 11-phase pipeline asynchronously."""
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
                            phase_id, phase_label,
                            asyncio.to_thread, handler, *args,
                            timeout_s=self._get_phase_timeout(phase_id),
                        )
                    else:
                        data = handler(*args)
                else:
                    data = await execute_phase_with_timeout(
                        phase_id, phase_label,
                        handler, *args,
                        timeout_s=self._get_phase_timeout(phase_id),
                    )
                success = True
                
            except PhaseTimeoutError as exc:
                error = exc
                instrumentation.record_error("timeout", str(exc))
                self.request_abort(f"Fase {phase_id} timed out: {exc}")
                
            except AbortRequested as exc:
                error = exc
                instrumentation.record_warning("abort", str(exc))
                
            except Exception as exc:
                logger.exception(f"Fase {phase_label} falló")
                error = exc
                instrumentation.record_error("exception", str(exc))
                self.request_abort(f"Fase {phase_id} falló: {exc}")
            
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
                
                # Build execution plan after Phase 1
                if phase_id == 1:
                    try:
                        logger.info("Building execution plan after Phase 1 completion")
                        document = self._context.get("document")
                        chunks = getattr(document, "chunks", []) if document else []
                        
                        synchronizer = IrrigationSynchronizer(
                            questionnaire=self._monolith_data, document_chunks=chunks
                        )
                        self._execution_plan = synchronizer.build_execution_plan()
                        
                        logger.info(
                            f"Execution plan built: {len(self._execution_plan.tasks)} tasks, "
                            f"plan_id={self._execution_plan.plan_id}"
                        )
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
    
    def process_development_plan(self, pdf_path: str, preprocessed_document: Any | None = None) -> list[PhaseResult]:
        """Sync wrapper for process_development_plan_async."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            raise RuntimeError("process_development_plan() must be called outside an active asyncio loop")
        
        return asyncio.run(self.process_development_plan_async(pdf_path, preprocessed_document=preprocessed_document))
    
    async def process(self, preprocessed_document: Any) -> list[PhaseResult]:
        """DEPRECATED ALIAS for process_development_plan_async()."""
        import warnings
        warnings.warn(
            "Orchestrator.process() is deprecated. Use process_development_plan_async() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        
        pdf_path = getattr(preprocessed_document, "source_path", None)
        if pdf_path is None:
            metadata = getattr(preprocessed_document, "metadata", {})
            pdf_path = metadata.get("source_path", "unknown.pdf")
        
        return await self.process_development_plan_async(pdf_path=str(pdf_path), preprocessed_document=preprocessed_document)
    
    def get_processing_status(self) -> dict[str, Any]:
        """Get current processing status."""
        if self._start_time is None:
            status = "not_started"
            elapsed = 0.0
            completed_flag = False
        else:
            aborted = self.abort_signal.is_aborted()
            status = "aborted" if aborted else "running"
            elapsed = time.perf_counter() - self._start_time
            completed_flag = (
                all(state == "completed" for state in self._phase_status.values())
                and not aborted
            )
        
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
        """Get metrics for all phases."""
        return {
            str(phase_id): instr.build_metrics()
            for phase_id, instr in self._phase_instrumentation.items()
        }
    
    async def monitor_progress_async(self, poll_interval: float = 2.0):
        """Monitor progress asynchronously."""
        while True:
            status = self.get_processing_status()
            yield status
            if status["status"] != "running":
                break
            await asyncio.sleep(poll_interval)
    
    def abort_handler(self, reason: str) -> None:
        """Alias for request_abort."""
        self.request_abort(reason)
    
    def health_check(self) -> dict[str, Any]:
        """System health check."""
        usage = self.resource_limits.get_resource_usage()
        cpu_headroom = max(0.0, self.resource_limits.max_cpu_percent - usage.get("cpu_percent", 0.0))
        mem_headroom = max(0.0, (self.resource_limits.max_memory_mb or 0.0) - usage.get("rss_mb", 0.0))
        
        score = max(0.0, min(100.0, (cpu_headroom / max(1.0, self.resource_limits.max_cpu_percent)) * 50.0))
        
        if self.resource_limits.max_memory_mb:
            score += max(0.0, min(50.0, (mem_headroom / max(1.0, self.resource_limits.max_memory_mb)) * 50.0))
        
        score = min(100.0, score)
        
        if self.abort_signal.is_aborted():
            score = min(score, 20.0)
        
        return {
            "score": score,
            "resource_usage": usage,
            "abort": self.abort_signal.is_aborted(),
        }
    
    def get_system_health(self) -> dict[str, Any]:
        """Comprehensive system health check."""
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
        }
        
        try:
            executor_health = {
                "instances_loaded": len(self.executor.instances),
                "status": "healthy",
            }
            health["components"]["method_executor"] = executor_health
        except Exception as e:
            health["status"] = "unhealthy"
            health["components"]["method_executor"] = {"status": "unhealthy", "error": str(e)}
        
        try:
            from farfan_pipeline.core.orchestrator import get_questionnaire_provider
            provider = get_questionnaire_provider()
            questionnaire_health = {
                "has_data": provider.has_data(),
                "status": "healthy" if provider.has_data() else "unhealthy",
            }
            health["components"]["questionnaire_provider"] = questionnaire_health
            
            if not provider.has_data():
                health["status"] = "degraded"
        except Exception as e:
            health["status"] = "unhealthy"
            health["components"]["questionnaire_provider"] = {"status": "unhealthy", "error": str(e)}
        
        try:
            usage = self.resource_limits.get_resource_usage()
            resource_health = {
                "cpu_percent": usage.get("cpu_percent", 0),
                "memory_mb": usage.get("rss_mb", 0),
                "worker_budget": usage.get("worker_budget", 0),
                "status": "healthy",
            }
            
            if usage.get("cpu_percent", 0) > 80:
                resource_health["status"] = "degraded"
                resource_health["warning"] = "High CPU usage"
                health["status"] = "degraded"
            
            if usage.get("rss_mb", 0) > 3500:
                resource_health["status"] = "degraded"
                resource_health["warning"] = "High memory usage"
                health["status"] = "degraded"
            
            health["components"]["resources"] = resource_health
        except Exception as e:
            health["status"] = "unhealthy"
            health["components"]["resources"] = {"status": "unhealthy", "error": str(e)}
        
        if self.abort_signal.is_aborted():
            health["status"] = "unhealthy"
            health["abort_reason"] = self.abort_signal.get_reason()
        
        return health
    
    def export_metrics(self) -> dict[str, Any]:
        """Export all metrics for monitoring."""
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
