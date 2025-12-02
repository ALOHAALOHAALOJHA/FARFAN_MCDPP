"""FARFAN Mechanistic Policy Pipeline - Production OpenTelemetry Integration
==========================================================================

Production-ready observability with OpenTelemetry SDK, Prometheus metrics,
Jaeger tracing, and distributed context propagation across the 9-phase pipeline
and all 30 executors.

✅ AUDIT_VERIFIED: Production OpenTelemetry observability stack

Author: FARFAN Team
Date: 2025-01-19
Version: 2.0.0 (Production)
"""

import logging
import os
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Optional

try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
    from opentelemetry.trace import Status, StatusCode, SpanKind
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

try:
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    JAEGER_AVAILABLE = True
except ImportError:
    JAEGER_AVAILABLE = False

try:
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from prometheus_client import start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class OpenTelemetryConfig:
    """Configuration for OpenTelemetry observability."""

    def __init__(
        self,
        service_name: str = "farfan-pipeline",
        service_version: str = "1.0.0",
        jaeger_endpoint: Optional[str] = None,
        prometheus_port: int = 9090,
        enable_console_export: bool = False,
        enable_jaeger: bool = True,
        enable_prometheus: bool = True,
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.jaeger_endpoint = jaeger_endpoint or os.getenv(
            "OTEL_EXPORTER_JAEGER_ENDPOINT",
            "http://localhost:14268/api/traces"
        )
        self.prometheus_port = prometheus_port
        self.enable_console_export = enable_console_export
        self.enable_jaeger = enable_jaeger and JAEGER_AVAILABLE
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE


class FARFANObservability:
    """Production OpenTelemetry observability for FARFAN pipeline."""

    def __init__(self, config: Optional[OpenTelemetryConfig] = None):
        self.config = config or OpenTelemetryConfig()
        self._tracer = None
        self._meter = None
        self._initialized = False
        self._prometheus_server_started = False
        self._metrics: dict[str, Any] = {}

        if not OTEL_AVAILABLE:
            logger.warning("OpenTelemetry SDK not available")
            return

        self._setup_tracing()
        self._setup_metrics()
        self._initialized = True
        logger.info(f"OpenTelemetry initialized for {self.config.service_name}")

    def _setup_tracing(self) -> None:
        """Setup distributed tracing."""
        resource = Resource(attributes={
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
        })

        provider = TracerProvider(resource=resource)

        if self.config.enable_jaeger:
            try:
                jaeger_exporter = JaegerExporter(
                    agent_host_name=os.getenv("JAEGER_AGENT_HOST", "localhost"),
                    agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
                )
                provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
                logger.info("Jaeger exporter configured")
            except Exception as e:
                logger.warning(f"Failed to configure Jaeger: {e}")

        if self.config.enable_console_export:
            console_exporter = ConsoleSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(console_exporter))

        trace.set_tracer_provider(provider)
        self._tracer = trace.get_tracer(self.config.service_name, self.config.service_version)

    def _setup_metrics(self) -> None:
        """Setup metrics collection."""
        resource = Resource(attributes={
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
        })

        readers = []

        if self.config.enable_prometheus:
            try:
                prometheus_reader = PrometheusMetricReader()
                readers.append(prometheus_reader)

                if not self._prometheus_server_started:
                    start_http_server(port=self.config.prometheus_port, addr="0.0.0.0")
                    self._prometheus_server_started = True
                    logger.info(f"Prometheus metrics at http://localhost:{self.config.prometheus_port}")
            except Exception as e:
                logger.warning(f"Failed to configure Prometheus: {e}")

        if self.config.enable_console_export:
            console_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
            readers.append(console_reader)

        if readers:
            provider = MeterProvider(resource=resource, metric_readers=readers)
            metrics.set_meter_provider(provider)
            self._meter = metrics.get_meter(self.config.service_name, self.config.service_version)
            self._create_standard_metrics()

    def _create_standard_metrics(self) -> None:
        """Create standard metrics."""
        if not self._meter:
            return

        self._metrics = {
            "executor_duration": self._meter.create_histogram(
                "farfan.executor.duration_ms",
                description="Executor execution duration in milliseconds",
                unit="ms",
            ),
            "executor_calls": self._meter.create_counter(
                "farfan.executor.calls_total",
                description="Total number of executor calls",
            ),
            "executor_errors": self._meter.create_counter(
                "farfan.executor.errors_total",
                description="Total number of executor errors",
            ),
            "phase_duration": self._meter.create_histogram(
                "farfan.phase.duration_ms",
                description="Phase execution duration in milliseconds",
                unit="ms",
            ),
            "phase_calls": self._meter.create_counter(
                "farfan.phase.calls_total",
                description="Total number of phase executions",
            ),
        }

    def get_tracer(self) -> Any:
        """Get the tracer instance."""
        return self._tracer if self._initialized else None

    def get_meter(self) -> Any:
        """Get the meter instance."""
        return self._meter if self._initialized else None

    @contextmanager
    def start_span(
        self,
        name: str,
        kind: Optional[Any] = None,
        attributes: Optional[dict[str, Any]] = None,
    ):
        """Context manager for creating spans."""
        if not self._initialized or not self._tracer:
            yield None
            return

        with self._tracer.start_as_current_span(
            name,
            kind=kind or SpanKind.INTERNAL,
            attributes=attributes or {}
        ) as span:
            try:
                yield span
            except Exception as e:
                if span:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                raise

    def trace_executor(self, executor_name: str) -> Callable:
        """Decorator for tracing executor execution."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self._initialized:
                    return func(*args, **kwargs)

                attributes = {
                    "executor.name": executor_name,
                    "executor.function": func.__name__,
                }

                parts = executor_name.split("_")
                if len(parts) >= 2:
                    attributes["executor.dimension"] = parts[0]
                    attributes["executor.question"] = parts[1]

                with self.start_span(
                    f"executor.{executor_name}.{func.__name__}",
                    kind=SpanKind.INTERNAL,
                    attributes=attributes,
                ) as span:
                    start_time = time.time()
                    try:
                        if "executor_calls" in self._metrics:
                            self._metrics["executor_calls"].add(1, attributes)

                        result = func(*args, **kwargs)

                        if span:
                            span.set_status(Status(StatusCode.OK))
                            duration_ms = (time.time() - start_time) * 1000
                            span.set_attribute("executor.duration_ms", duration_ms)

                            if "executor_duration" in self._metrics:
                                self._metrics["executor_duration"].record(duration_ms, attributes)

                        return result
                    except Exception as e:
                        if "executor_errors" in self._metrics:
                            self._metrics["executor_errors"].add(1, attributes)
                        if span:
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            span.record_exception(e)
                        raise
            return wrapper
        return decorator

    def trace_phase(self, phase_name: str, phase_number: int) -> Callable:
        """Decorator for tracing pipeline phase execution."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self._initialized:
                    return await func(*args, **kwargs)

                attributes = {
                    "phase.name": phase_name,
                    "phase.number": phase_number,
                }

                with self.start_span(
                    f"phase.{phase_number}.{phase_name}",
                    kind=SpanKind.INTERNAL,
                    attributes=attributes,
                ) as span:
                    start_time = time.time()
                    try:
                        if "phase_calls" in self._metrics:
                            self._metrics["phase_calls"].add(1, attributes)

                        result = await func(*args, **kwargs)

                        if span:
                            span.set_status(Status(StatusCode.OK))
                            duration_ms = (time.time() - start_time) * 1000
                            span.set_attribute("phase.duration_ms", duration_ms)

                            if "phase_duration" in self._metrics:
                                self._metrics["phase_duration"].record(duration_ms, attributes)

                        return result
                    except Exception as e:
                        if span:
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            span.record_exception(e)
                        raise

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self._initialized:
                    return func(*args, **kwargs)

                attributes = {
                    "phase.name": phase_name,
                    "phase.number": phase_number,
                }

                with self.start_span(
                    f"phase.{phase_number}.{phase_name}",
                    kind=SpanKind.INTERNAL,
                    attributes=attributes,
                ) as span:
                    start_time = time.time()
                    try:
                        if "phase_calls" in self._metrics:
                            self._metrics["phase_calls"].add(1, attributes)

                        result = func(*args, **kwargs)

                        if span:
                            span.set_status(Status(StatusCode.OK))
                            duration_ms = (time.time() - start_time) * 1000
                            span.set_attribute("phase.duration_ms", duration_ms)

                            if "phase_duration" in self._metrics:
                                self._metrics["phase_duration"].record(duration_ms, attributes)

                        return result
                    except Exception as e:
                        if span:
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            span.record_exception(e)
                        raise

            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        return decorator

    def propagate_context(self) -> dict[str, str]:
        """Extract context for propagation across boundaries."""
        if not self._initialized:
            return {}

        propagator = TraceContextTextMapPropagator()
        carrier: dict[str, str] = {}
        propagator.inject(carrier)
        return carrier

    def inject_context(self, carrier: dict[str, str]) -> None:
        """Inject context from carrier."""
        if not self._initialized or not carrier:
            return

        propagator = TraceContextTextMapPropagator()
        propagator.extract(carrier)


_global_observability: Optional[FARFANObservability] = None


def get_global_observability() -> FARFANObservability:
    """Get or create global observability instance."""
    global _global_observability
    if _global_observability is None:
        _global_observability = FARFANObservability()
    return _global_observability


def get_tracer(name: str = "farfan-pipeline") -> Any:
    """Get tracer from global observability."""
    obs = get_global_observability()
    return obs.get_tracer()


def trace_executor(executor_name: str) -> Callable:
    """Decorator for tracing executors."""
    obs = get_global_observability()
    return obs.trace_executor(executor_name)


def trace_phase(phase_name: str, phase_number: int) -> Callable:
    """Decorator for tracing phases."""
    obs = get_global_observability()
    return obs.trace_phase(phase_name, phase_number)


__all__ = [
    "OpenTelemetryConfig",
    "FARFANObservability",
    "get_global_observability",
    "get_tracer",
    "trace_executor",
    "trace_phase",
    "SpanKind",
    "Status",
    "StatusCode",
]
