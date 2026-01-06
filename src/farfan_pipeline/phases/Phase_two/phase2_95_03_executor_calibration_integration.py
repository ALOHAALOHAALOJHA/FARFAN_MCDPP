"""Real-Time Calibration Engine - GAP 3 Implementation.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Executor Calibration Integration
PHASE_ROLE: Provides real-time calibration based on actual execution metrics

GAP 3 Implementation: Real-Time Calibration Engine

This module replaces the stub implementation with a full calibration engine that:
- Computes quality scores based on actual execution metrics
- Detects performance regressions (time, memory)
- Dynamically adjusts method weights based on historical performance
- Provides confidence scores based on sample size and variance

Requirements Implemented:
    CA-01: Quality score computed from success rate, time ratio, memory ratio
    CA-02: Regression detection when time > 120% or memory > 130% of baseline
    CA-03: Method weights updated based on per-method success rates
    CA-04: Confidence score reflects sample size and variance
    CA-05: Calibration results persisted for historical analysis

Design by Contract:
- Preconditions: executor_id is non-empty string, metrics are non-negative
- Postconditions: CalibrationResult always returned with valid score [0,1]
- Invariants: No side effects on external state without explicit persistence
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# === DATA MODELS ===

@dataclass
class CalibrationMetrics:
    """Runtime metrics captured during executor execution.

    Attributes:
        runtime_ms: Execution time in milliseconds
        memory_mb: Memory usage in megabytes
        methods_executed: Total number of methods called
        methods_succeeded: Number of methods that completed successfully
    """
    runtime_ms: float
    memory_mb: float
    methods_executed: int
    methods_succeeded: int


@dataclass
class ExecutionMetrics:
    """Extended execution metrics for calibration.

    Attributes:
        executor_id: Unique identifier for the executor
        execution_time_ms: Total execution time in milliseconds
        peak_memory_mb: Peak memory usage in megabytes
        methods_executed: Total number of methods called
        methods_succeeded: Number of methods that completed successfully
        per_method_times: Dictionary mapping method_name to execution time in ms
    """
    executor_id: str
    execution_time_ms: float
    peak_memory_mb: float
    methods_executed: int
    methods_succeeded: int
    per_method_times: Dict[str, float] = field(default_factory=dict)


@dataclass
class ProfileBaseline:
    """Historical baseline metrics for an executor.

    Attributes:
        executor_id: Unique identifier for the executor
        avg_time_ms: Average execution time in milliseconds
        avg_memory_mb: Average memory usage in megabytes
        stddev_time_ms: Standard deviation of execution time
        stddev_memory_mb: Standard deviation of memory usage
        sample_count: Number of samples used to compute baseline
        last_updated: ISO timestamp of last update
    """
    executor_id: str
    avg_time_ms: float
    avg_memory_mb: float
    stddev_time_ms: float
    stddev_memory_mb: float
    sample_count: int
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CalibrationResult:
    """Result of calibration instrumentation with quality scores.

    Attributes:
        quality_score: Aggregated quality score [0,1]
        confidence: Confidence in the quality score [0,1]
        method_weights: Per-method weight assignments
        regression_detected: Whether a performance regression was detected
        regression_details: Description of detected regression
        layer_scores: Per-layer quality scores
        layers_used: List of calibration layers applied
        aggregation_method: Method used to aggregate layer scores
        metrics: Runtime metrics captured during execution
    """
    quality_score: float
    confidence: float = 0.5
    method_weights: Dict[str, float] = field(default_factory=dict)
    regression_detected: bool = False
    regression_details: Optional[str] = None
    layer_scores: Dict[str, float] = field(default_factory=dict)
    layers_used: list[str] = field(default_factory=list)
    aggregation_method: str = "real_time"
    metrics: CalibrationMetrics = field(default_factory=lambda: CalibrationMetrics(0.0, 0.0, 0, 0))


# === STORAGE INTERFACES ===

class BaselineStore:
    """Stores and retrieves executor baselines.

    Thread-safe storage for performance baselines with file persistence.
    """

    def __init__(self, storage_dir: Path | str = Path("artifacts/calibration/baselines")):
        """Initialize baseline store.

        Args:
            storage_dir: Directory for storing baseline files.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, ProfileBaseline] = {}
        self._lock = threading.Lock()

    def get_baseline(self, executor_id: str) -> Optional[ProfileBaseline]:
        """Retrieve baseline for an executor.

        Args:
            executor_id: Unique executor identifier.

        Returns:
            ProfileBaseline if exists, else None.
        """
        with self._lock:
            # Check cache first
            if executor_id in self._cache:
                return self._cache[executor_id]

            # Load from disk
            baseline_path = self._get_path(executor_id)
            if not baseline_path.exists():
                return None

            try:
                with open(baseline_path, "r") as f:
                    data = json.load(f)
                baseline = ProfileBaseline(**data)
                self._cache[executor_id] = baseline
                return baseline
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                logger.warning(f"Failed to load baseline for {executor_id}: {e}")
                return None

    def update_baseline(self, executor_id: str, metrics: ExecutionMetrics) -> ProfileBaseline:
        """Update baseline with new execution metrics.

        Uses exponential moving average for smooth updates.

        Args:
            executor_id: Unique executor identifier.
            metrics: New execution metrics to incorporate.

        Returns:
            Updated ProfileBaseline.
        """
        with self._lock:
            existing = self._cache.get(executor_id)
            if existing is None:
                existing = self.get_baseline(executor_id)

            if existing is None:
                # Create new baseline
                baseline = ProfileBaseline(
                    executor_id=executor_id,
                    avg_time_ms=metrics.execution_time_ms,
                    avg_memory_mb=metrics.peak_memory_mb,
                    stddev_time_ms=0.0,
                    stddev_memory_mb=0.0,
                    sample_count=1,
                )
            else:
                # Update with exponential moving average (alpha=0.1)
                alpha = 0.1
                n = existing.sample_count

                new_avg_time = alpha * metrics.execution_time_ms + (1 - alpha) * existing.avg_time_ms
                new_avg_memory = alpha * metrics.peak_memory_mb + (1 - alpha) * existing.avg_memory_mb

                # Update stddev using Welford's online algorithm approximation
                time_diff = metrics.execution_time_ms - existing.avg_time_ms
                new_stddev_time = math.sqrt(
                    (1 - alpha) * (existing.stddev_time_ms ** 2) + alpha * (time_diff ** 2)
                )

                memory_diff = metrics.peak_memory_mb - existing.avg_memory_mb
                new_stddev_memory = math.sqrt(
                    (1 - alpha) * (existing.stddev_memory_mb ** 2) + alpha * (memory_diff ** 2)
                )

                baseline = ProfileBaseline(
                    executor_id=executor_id,
                    avg_time_ms=new_avg_time,
                    avg_memory_mb=new_avg_memory,
                    stddev_time_ms=new_stddev_time,
                    stddev_memory_mb=new_stddev_memory,
                    sample_count=n + 1,
                )

            # Persist and cache
            self._save_baseline(baseline)
            self._cache[executor_id] = baseline
            return baseline

    def _get_path(self, executor_id: str) -> Path:
        """Get file path for executor baseline."""
        safe_id = hashlib.md5(executor_id.encode()).hexdigest()[:16]
        return self.storage_dir / f"{safe_id}_baseline.json"

    def _save_baseline(self, baseline: ProfileBaseline) -> None:
        """Persist baseline to disk."""
        baseline_path = self._get_path(baseline.executor_id)
        data = {
            "executor_id": baseline.executor_id,
            "avg_time_ms": baseline.avg_time_ms,
            "avg_memory_mb": baseline.avg_memory_mb,
            "stddev_time_ms": baseline.stddev_time_ms,
            "stddev_memory_mb": baseline.stddev_memory_mb,
            "sample_count": baseline.sample_count,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        with open(baseline_path, "w") as f:
            json.dump(data, f, indent=2)


class WeightStore:
    """Stores and retrieves method weights per executor.

    Thread-safe storage for method weights with file persistence.
    """

    def __init__(self, storage_dir: Path | str = Path("artifacts/calibration/weights")):
        """Initialize weight store.

        Args:
            storage_dir: Directory for storing weight files.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Dict[str, float]] = {}
        self._lock = threading.Lock()

    def get_weights(self, executor_id: str) -> Dict[str, float]:
        """Retrieve method weights for an executor.

        Args:
            executor_id: Unique executor identifier.

        Returns:
            Dictionary of method_name -> weight.
        """
        with self._lock:
            # Check cache first
            if executor_id in self._cache:
                return self._cache[executor_id].copy()

            # Load from disk
            weights_path = self._get_path(executor_id)
            if not weights_path.exists():
                return {}

            try:
                with open(weights_path, "r") as f:
                    data = json.load(f)
                weights = data.get("weights", {})
                self._cache[executor_id] = weights
                return weights.copy()
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to load weights for {executor_id}: {e}")
                return {}

    def save_weights(self, executor_id: str, weights: Dict[str, float]) -> None:
        """Persist method weights for an executor.

        Args:
            executor_id: Unique executor identifier.
            weights: Dictionary of method_name -> weight.
        """
        with self._lock:
            self._cache[executor_id] = weights.copy()

            weights_path = self._get_path(executor_id)
            data = {
                "executor_id": executor_id,
                "weights": weights,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            with open(weights_path, "w") as f:
                json.dump(data, f, indent=2)

    def _get_path(self, executor_id: str) -> Path:
        """Get file path for executor weights."""
        safe_id = hashlib.md5(executor_id.encode()).hexdigest()[:16]
        return self.storage_dir / f"{safe_id}_weights.json"


class CalibrationResultStore:
    """Stores calibration results for historical analysis.

    Appends results to JSONL files for audit trail.
    """

    def __init__(self, storage_dir: Path | str = Path("artifacts/calibration/results")):
        """Initialize result store.

        Args:
            storage_dir: Directory for storing result files.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def save_result(
        self,
        executor_id: str,
        result: CalibrationResult,
        metrics: ExecutionMetrics
    ) -> None:
        """Persist calibration result for audit.

        Args:
            executor_id: Unique executor identifier.
            result: CalibrationResult to persist.
            metrics: ExecutionMetrics that produced the result.
        """
        with self._lock:
            result_path = self.storage_dir / "calibration_history.jsonl"

            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "executor_id": executor_id,
                "quality_score": result.quality_score,
                "confidence": result.confidence,
                "regression_detected": result.regression_detected,
                "regression_details": result.regression_details,
                "execution_time_ms": metrics.execution_time_ms,
                "peak_memory_mb": metrics.peak_memory_mb,
                "methods_executed": metrics.methods_executed,
                "methods_succeeded": metrics.methods_succeeded,
                "method_weights": result.method_weights,
            }

            with open(result_path, "a") as f:
                f.write(json.dumps(record) + "\n")


# === REAL-TIME CALIBRATION ENGINE ===

class RealTimeCalibrationEngine:
    """
    Computes calibration results based on actual execution metrics.

    GAP 3 Implementation: Real-Time Calibration Engine

    Features:
        - Quality score from success rate, time ratio, memory ratio
        - Regression detection at configurable thresholds
        - Dynamic method weight updates
        - Confidence scoring based on sample size and variance
        - Result persistence for historical analysis
    """

    # Thresholds for regression detection (CA-02)
    TIME_REGRESSION_THRESHOLD = 1.2   # 20% slower triggers regression
    MEMORY_REGRESSION_THRESHOLD = 1.3  # 30% more memory triggers regression

    def __init__(
        self,
        baseline_store: BaselineStore | None = None,
        weight_store: WeightStore | None = None,
        result_store: CalibrationResultStore | None = None,
        persist_results: bool = True,
    ):
        """Initialize calibration engine.

        Args:
            baseline_store: Store for performance baselines.
            weight_store: Store for method weights.
            result_store: Store for calibration results.
            persist_results: Whether to persist results for audit.
        """
        self.baseline_store = baseline_store or BaselineStore()
        self.weight_store = weight_store or WeightStore()
        self.result_store = result_store or CalibrationResultStore()
        self.persist_results = persist_results

    def compute_calibration_result(
        self,
        executor_id: str,
        metrics: ExecutionMetrics,
        baseline: Optional[ProfileBaseline] = None
    ) -> CalibrationResult:
        """
        Compute calibration result from execution metrics.

        Implements CA-01 through CA-05.

        Args:
            executor_id: Identifier for the executor.
            metrics: Metrics from the current execution.
            baseline: Optional baseline for comparison (fetched if not provided).

        Returns:
            CalibrationResult with quality score, confidence, and updated weights.
        """
        if baseline is None:
            baseline = self.baseline_store.get_baseline(executor_id)

        # CA-01: Base quality from success rate
        if metrics.methods_executed == 0:
            base_quality = 0.0
        else:
            base_quality = metrics.methods_succeeded / metrics.methods_executed

        # CA-02: Regression detection and penalty
        regression_detected = False
        regression_details = None
        quality_penalty = 0.0

        if baseline and baseline.sample_count >= 5:
            time_ratio = metrics.execution_time_ms / max(baseline.avg_time_ms, 0.001)
            memory_ratio = metrics.peak_memory_mb / max(baseline.avg_memory_mb, 0.001)

            regression_messages = []

            if time_ratio > self.TIME_REGRESSION_THRESHOLD:
                quality_penalty += 0.1
                regression_detected = True
                regression_messages.append(
                    f"Time regression: {time_ratio:.2f}x baseline "
                    f"({metrics.execution_time_ms:.1f}ms vs {baseline.avg_time_ms:.1f}ms avg)"
                )

            if memory_ratio > self.MEMORY_REGRESSION_THRESHOLD:
                quality_penalty += 0.15
                regression_detected = True
                regression_messages.append(
                    f"Memory regression: {memory_ratio:.2f}x baseline "
                    f"({metrics.peak_memory_mb:.1f}MB vs {baseline.avg_memory_mb:.1f}MB avg)"
                )

            if regression_messages:
                regression_details = "; ".join(regression_messages)
                logger.warning(
                    f"Regression detected for {executor_id}: {regression_details}"
                )

        quality_score = max(0.0, min(1.0, base_quality - quality_penalty))

        # CA-04: Confidence based on sample size and variance
        confidence = self._compute_confidence(metrics, baseline)

        # CA-03: Update method weights
        method_weights = self._update_weights(executor_id, metrics)

        # Build layer scores for detailed breakdown
        layer_scores = {
            "success_rate": base_quality,
            "time_penalty": -quality_penalty if regression_detected else 0.0,
            "final_score": quality_score,
        }

        # Create result
        result = CalibrationResult(
            quality_score=quality_score,
            confidence=confidence,
            method_weights=method_weights,
            regression_detected=regression_detected,
            regression_details=regression_details,
            layer_scores=layer_scores,
            layers_used=["success_rate", "regression_detection", "method_weights"],
            aggregation_method="real_time_weighted",
            metrics=CalibrationMetrics(
                runtime_ms=metrics.execution_time_ms,
                memory_mb=metrics.peak_memory_mb,
                methods_executed=metrics.methods_executed,
                methods_succeeded=metrics.methods_succeeded,
            ),
        )

        # Update baseline with new data
        self.baseline_store.update_baseline(executor_id, metrics)

        # CA-05: Persist result for historical analysis
        if self.persist_results:
            self.result_store.save_result(executor_id, result, metrics)

        logger.debug(
            f"Calibration computed for {executor_id}: "
            f"quality={quality_score:.3f}, confidence={confidence:.3f}, "
            f"regression={regression_detected}"
        )

        return result

    def _compute_confidence(
        self,
        metrics: ExecutionMetrics,
        baseline: Optional[ProfileBaseline]
    ) -> float:
        """
        Compute confidence score based on sample size and variance.

        Higher sample count → higher confidence (asymptotic to 1.0)
        Lower variance → higher confidence

        Args:
            metrics: Current execution metrics.
            baseline: Historical baseline if available.

        Returns:
            Confidence score in [0.0, 1.0].
        """
        if not baseline or baseline.sample_count == 0:
            return 0.5  # Low confidence with no data
        
        if baseline.sample_count < 5:
            return 0.5  # Low confidence with insufficient data

        # Higher sample count -> higher confidence (asymptotic to 1.0)
        # Uses 1 - e^(-n/50) so ~63% confidence at 50 samples, ~86% at 100
        sample_factor = 1 - math.exp(-baseline.sample_count / 50)

        # Lower coefficient of variation -> higher confidence
        if baseline.avg_time_ms > 0 and baseline.stddev_time_ms >= 0:
            cv = baseline.stddev_time_ms / baseline.avg_time_ms
            variance_factor = max(0.0, 1 - cv)
        else:
            variance_factor = 1.0

        # Weighted combination: 60% sample size, 40% variance
        confidence = min(1.0, sample_factor * 0.6 + variance_factor * 0.4)

        return confidence

    def _update_weights(
        self,
        executor_id: str,
        metrics: ExecutionMetrics
    ) -> Dict[str, float]:
        """
        Update method weights based on per-method performance.

        Uses inverse-time weighting with exponential moving average.

        Args:
            executor_id: Executor identifier.
            metrics: Execution metrics with per-method times.

        Returns:
            Normalized method weights.
        """
        current_weights = self.weight_store.get_weights(executor_id)

        for method_name, time_ms in metrics.per_method_times.items():
            # Inverse-time weighting (faster = higher weight)
            raw_weight = 1.0 / max(time_ms, 1.0)

            # Exponential moving average with alpha=0.3
            old_weight = current_weights.get(method_name, raw_weight)
            new_weight = 0.3 * raw_weight + 0.7 * old_weight
            current_weights[method_name] = new_weight

        # Normalize weights to sum to 1.0
        if current_weights:
            total = sum(current_weights.values())
            if total > 0:
                normalized = {k: v / total for k, v in current_weights.items()}
            else:
                normalized = current_weights
        else:
            normalized = {}

        self.weight_store.save_weights(executor_id, normalized)
        return normalized


# === SINGLETON ENGINE INSTANCE ===

_calibration_engine: Optional[RealTimeCalibrationEngine] = None
_engine_lock = threading.Lock()


def get_calibration_engine() -> RealTimeCalibrationEngine:
    """Get or create the global calibration engine instance."""
    global _calibration_engine
    with _engine_lock:
        if _calibration_engine is None:
            _calibration_engine = RealTimeCalibrationEngine()
        return _calibration_engine


# === PUBLIC API (BACKWARD COMPATIBLE) ===

def instrument_executor(
    executor_id: str,
    context: dict[str, Any],
    runtime_ms: float,
    memory_mb: float,
    methods_executed: int,
    methods_succeeded: int,
) -> CalibrationResult:
    """Instrument executor execution with real-time calibration.

    GAP 3: Replaces stub implementation with real-time calibration.

    Args:
        executor_id: Unique executor identifier
        context: Execution context (may contain per_method_times)
        runtime_ms: Execution time in milliseconds
        memory_mb: Memory usage in megabytes
        methods_executed: Total number of methods called
        methods_succeeded: Number of methods that completed successfully

    Returns:
        CalibrationResult with real quality scores and metrics

    Preconditions:
        - executor_id is non-empty string
        - runtime_ms >= 0
        - memory_mb >= 0
        - methods_executed >= 0
        - methods_succeeded >= 0
        - methods_succeeded <= methods_executed

    Postconditions:
        - quality_score in [0, 1]
        - confidence in [0, 1]
        - metrics match input values
    """
    # Validate preconditions
    if not executor_id:
        raise ValueError("executor_id cannot be empty")
    if runtime_ms < 0:
        raise ValueError(f"runtime_ms must be non-negative, got {runtime_ms}")
    if memory_mb < 0:
        raise ValueError(f"memory_mb must be non-negative, got {memory_mb}")
    if methods_executed < 0:
        raise ValueError(f"methods_executed must be non-negative, got {methods_executed}")
    if methods_succeeded < 0:
        raise ValueError(f"methods_succeeded must be non-negative, got {methods_succeeded}")
    if methods_succeeded > methods_executed:
        raise ValueError(
            f"methods_succeeded ({methods_succeeded}) cannot exceed "
            f"methods_executed ({methods_executed})"
        )

    # Extract per-method times from context if available
    per_method_times = context.get("per_method_times", {})

    # Build execution metrics
    metrics = ExecutionMetrics(
        executor_id=executor_id,
        execution_time_ms=runtime_ms,
        peak_memory_mb=memory_mb,
        methods_executed=methods_executed,
        methods_succeeded=methods_succeeded,
        per_method_times=per_method_times,
    )

    # Compute calibration using real-time engine
    engine = get_calibration_engine()
    result = engine.compute_calibration_result(executor_id, metrics)

    logger.debug(
        f"Real-time calibration for {executor_id}: "
        f"runtime={runtime_ms:.1f}ms, memory={memory_mb:.1f}MB, "
        f"quality={result.quality_score:.3f}, confidence={result.confidence:.3f}"
    )

    return result


def get_executor_config(
    executor_id: str,
    dimension: str,
    question: str,
    environment: str = "production",
    cli_overrides: Optional[Dict[str, Any]] = None,
) -> dict[str, Any]:
    """Get runtime configuration for executor.

    Loads configuration from the canonical ExecutorConfig system using the
    established loading hierarchy:
    1. CLI arguments (highest priority)
    2. Environment variables (FARFAN_TIMEOUT_S, FARFAN_RETRY, etc.)
    3. Environment file (system/config/environments/{env}.json)
    4. Executor config file (executor_configs/{executor_id}.json)
    5. Conservative defaults (lowest priority)

    Args:
        executor_id: Unique executor identifier
        dimension: Dimension identifier (e.g., "D1")
        question: Question identifier (e.g., "Q1")
        environment: Environment name (development, staging, production)
        cli_overrides: Optional CLI argument overrides

    Returns:
        Runtime configuration dictionary with HOW parameters

    Preconditions:
        - executor_id is non-empty string
        - dimension is non-empty string
        - question is non-empty string

    Postconditions:
        - Returns valid configuration dict
        - All required keys present
        
    Success Criteria:
        - Configuration loaded successfully from appropriate sources
        - All values within valid ranges
        
    Failure Modes:
        - ValueError if preconditions violated
        - ExecutorConfig validation errors if invalid config values
        
    Verification Strategy:
        - Precondition checks enforce non-empty strings
        - ExecutorConfig.__post_init__ validates value ranges
        - Debug logging shows loaded configuration source and values
    """
    if not executor_id:
        raise ValueError("executor_id cannot be empty")
    if not dimension:
        raise ValueError("dimension cannot be empty")
    if not question:
        raise ValueError("question cannot be empty")

    logger.debug(
        f"Config requested for {executor_id} "
        f"(dimension={dimension}, question={question}, environment={environment})"
    )

    # Import ExecutorConfig (local import to avoid circular dependency issues)
    # Module-level caching to avoid repeated imports
    if globals().get("_executor_config_module") is None:
        try:
            from farfan_pipeline.phases.Phase_two.phase2_10_03_executor_config import (
                ExecutorConfig,
            )
            globals()["_executor_config_module"] = {"ExecutorConfig": ExecutorConfig}
        except ModuleNotFoundError:
            # Fallback for when module is imported directly without package context
            import sys
            from pathlib import Path as ImportPath
            
            config_module_path = ImportPath(__file__).parent / "phase2_10_03_executor_config.py"
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "phase2_10_03_executor_config", config_module_path
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load ExecutorConfig from {config_module_path}")
            executor_config_module = importlib.util.module_from_spec(spec)
            # Register in sys.modules to support dataclass introspection
            # Dataclasses use sys.modules.get(cls.__module__) for type checking
            sys.modules["phase2_10_03_executor_config"] = executor_config_module
            spec.loader.exec_module(executor_config_module)
            globals()["_executor_config_module"] = {"ExecutorConfig": executor_config_module.ExecutorConfig}
    
    ExecutorConfig = globals()["_executor_config_module"]["ExecutorConfig"]

    # Load configuration from canonical source
    executor_config = ExecutorConfig.load_from_sources(
        executor_id=executor_id,
        environment=environment,
        cli_overrides=cli_overrides,
    )

    # Helper to get value or default
    def get_or_default(value, default):
        return value if value is not None else default

    # Map ExecutorConfig fields to legacy return schema
    config = {
        "timeout_seconds": get_or_default(executor_config.timeout_s, 300),
        "max_retries": get_or_default(executor_config.retry, 3),
        "retry_delay_seconds": 1.0,  # Not in ExecutorConfig, keep as constant
        "memory_limit_mb": get_or_default(executor_config.memory_limit_mb, 512),
        "enable_caching": True,  # Not in ExecutorConfig, keep as constant
        "enable_profiling": get_or_default(executor_config.enable_profiling, True),
    }

    logger.debug(
        f"Loaded config for {executor_id}: "
        f"timeout={config['timeout_seconds']}s, "
        f"retries={config['max_retries']}, "
        f"memory={config['memory_limit_mb']}MB, "
        f"profiling={config['enable_profiling']}"
    )

    return config


__all__ = [
    # Data models
    "CalibrationMetrics",
    "CalibrationResult",
    "ExecutionMetrics",
    "ProfileBaseline",
    # Stores
    "BaselineStore",
    "WeightStore",
    "CalibrationResultStore",
    # Engine
    "RealTimeCalibrationEngine",
    "get_calibration_engine",
    # Public API
    "instrument_executor",
    "get_executor_config",
]
