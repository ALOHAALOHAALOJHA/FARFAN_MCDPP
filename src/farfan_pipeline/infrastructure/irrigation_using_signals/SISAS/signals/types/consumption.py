# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/consumption.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class AccessPattern(Enum):
    """Patrones de acceso"""
    BURSTY = "bursty"
    STEADY = "steady"
    DECLINING = "declining"
    GROWING = "growing"
    SPORADIC = "sporadic"


class CouplingStrength(Enum):
    """Fuerza de acoplamiento"""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NONE = "none"


class HealthStatus(Enum):
    """Estado de salud"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class FrequencySignal(Signal):
    """
    Señal que indica frecuencia de uso/acceso.

    Uso: Tracking de qué datos se usan más.
    """

    signal_type: str = field(default="FrequencySignal", init=False)

    # Payload específico
    resource_id: str = ""  # Archivo, endpoint, señal
    resource_type: str = ""  # "canonical_file", "signal", "endpoint"

    access_count: int = 0
    period_start: str = ""
    period_end:  str = ""

    access_pattern: AccessPattern = AccessPattern.STEADY
    peak_hour: int = 0  # 0-23

    consumers_accessing: List[str] = field(default_factory=list)
    
    # Análisis adicional
    avg_access_per_day: float = 0.0
    trend_score: float = 0.0  # -1.0 (declining) to 1.0 (growing)

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONSUMPTION

    def __post_init__(self):
        super().__post_init__()
        # Calcular promedio por día
        if self.period_start and self.period_end:
            try:
                start_dt = datetime.fromisoformat(self.period_start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(self.period_end.replace('Z', '+00:00'))
                days = max(1, (end_dt - start_dt).days)
                self.avg_access_per_day = self.access_count / days
            except:
                self.avg_access_per_day = 0.0

    def get_usage_analysis(self) -> Dict[str, Any]:
        """Análisis de uso"""
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "access_count": self.access_count,
            "avg_per_day": self.avg_access_per_day,
            "pattern": self.access_pattern.value,
            "peak_hour": self.peak_hour,
            "unique_consumers": len(self.consumers_accessing),
            "popularity_level": self.get_popularity_level(),
            "trend_direction": self.get_trend_direction()
        }

    def get_popularity_level(self) -> str:
        """Nivel de popularidad"""
        if self.avg_access_per_day > 100:
            return "very_high"
        elif self.avg_access_per_day > 50:
            return "high"
        elif self.avg_access_per_day > 10:
            return "medium"
        elif self.avg_access_per_day > 1:
            return "low"
        return "very_low"

    def get_trend_direction(self) -> str:
        """Dirección de tendencia"""
        if self.trend_score > 0.3:
            return "growing"
        elif self.trend_score < -0.3:
            return "declining"
        return "stable"

    def is_underutilized(self) -> bool:
        """Verifica si está subutilizado"""
        return self.avg_access_per_day < 1.0


@dataclass
class TemporalCouplingSignal(Signal):
    """
    Señal que indica acoplamiento temporal entre componentes.

    Uso: Detectar si dos componentes siempre se activan juntos.
    """

    signal_type: str = field(default="TemporalCouplingSignal", init=False)

    # Payload específico
    component_a: str = ""
    component_b: str = ""

    correlation_coefficient: float = 0.0  # -1 a 1
    coupling_strength: CouplingStrength = CouplingStrength.NONE

    co_occurrence_count: int = 0
    observation_period_days: int = 0

    typical_lag_ms: float = 0.0  # Tiempo entre activación de A y B
    
    # Análisis adicional
    independent_occurrences_a: int = 0
    independent_occurrences_b: int = 0

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONSUMPTION

    def get_coupling_analysis(self) -> Dict[str, Any]:
        """Análisis de acoplamiento"""
        return {
            "component_a": self.component_a,
            "component_b": self.component_b,
            "correlation": self.correlation_coefficient,
            "coupling_strength": self.coupling_strength.value,
            "co_occurrences": self.co_occurrence_count,
            "typical_lag_ms": self.typical_lag_ms,
            "is_strongly_coupled": self.is_strongly_coupled(),
            "coupling_type": self.get_coupling_type()
        }

    def is_strongly_coupled(self) -> bool:
        """Verifica si hay acoplamiento fuerte"""
        return (
            abs(self.correlation_coefficient) > 0.7 or
            self.coupling_strength == CouplingStrength.STRONG
        )

    def get_coupling_type(self) -> str:
        """Tipo de acoplamiento"""
        if abs(self.correlation_coefficient) < 0.3:
            return "independent"
        elif self.correlation_coefficient > 0.7:
            return "positive_strong"
        elif self.correlation_coefficient > 0.3:
            return "positive_moderate"
        elif self.correlation_coefficient < -0.7:
            return "negative_strong"
        elif self.correlation_coefficient < -0.3:
            return "negative_moderate"
        return "neutral"

    def get_decoupling_priority(self) -> str:
        """Prioridad de desacoplamiento"""
        if self.is_strongly_coupled():
            return "high"
        elif self.coupling_strength == CouplingStrength.MODERATE:
            return "medium"
        return "low"


@dataclass
class ConsumerHealthSignal(Signal):
    """
    Señal que indica salud de un consumidor.

    Uso: Monitoreo de consumidores para detectar degradación.
    """

    signal_type: str = field(default="ConsumerHealthSignal", init=False)

    # Payload específico
    consumer_id: str = ""
    consumer_phase: str = ""

    signals_received: int = 0
    signals_processed: int = 0
    signals_failed: int = 0

    avg_processing_time_ms: float = 0.0
    error_rate: float = 0.0

    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_activity:  str = ""
    
    # Métricas adicionales
    throughput: float = 0.0  # Señales por segundo
    latency_p95: float = 0.0  # Percentil 95 de latencia
    memory_usage_mb: float = 0.0

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONSUMPTION

    def get_health_report(self) -> Dict[str, Any]:
        """Reporte de salud completo"""
        return {
            "consumer_id": self.consumer_id,
            "consumer_phase": self.consumer_phase,
            "health_status": self.health_status.value,
            "signals_received": self.signals_received,
            "signals_processed": self.signals_processed,
            "signals_failed": self.signals_failed,
            "processing_rate": self.get_processing_rate(),
            "error_rate": self.error_rate,
            "avg_processing_time_ms": self.avg_processing_time_ms,
            "throughput": self.throughput,
            "latency_p95": self.latency_p95,
            "is_healthy": self.is_healthy(),
            "requires_attention": self.requires_attention()
        }

    def get_processing_rate(self) -> float:
        """Tasa de procesamiento exitoso"""
        if self.signals_received == 0:
            return 0.0
        return self.signals_processed / self.signals_received

    def is_healthy(self) -> bool:
        """Verifica si está saludable"""
        return (
            self.health_status == HealthStatus.HEALTHY and
            self.error_rate < 0.05 and  # Menos de 5% errores
            self.get_processing_rate() > 0.95  # Más de 95% procesados
        )

    def requires_attention(self) -> bool:
        """Determina si requiere atención"""
        return (
            self.health_status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY] or
            self.error_rate > 0.1 or
            self.avg_processing_time_ms > 5000 or
            self.get_processing_rate() < 0.8
        )

    def get_performance_category(self) -> str:
        """Categoría de performance"""
        if self.avg_processing_time_ms < 100:
            return "excellent"
        elif self.avg_processing_time_ms < 500:
            return "good"
        elif self.avg_processing_time_ms < 2000:
            return "acceptable"
        return "poor"

    def get_improvement_suggestions(self) -> List[str]:
        """Sugerencias de mejora"""
        suggestions = []
        
        if self.error_rate > 0.1:
            suggestions.append("High error rate - investigate failure causes")
        
        if self.avg_processing_time_ms > 2000:
            suggestions.append("Slow processing - consider optimization")
        
        if self.throughput < 10:
            suggestions.append("Low throughput - check for bottlenecks")
        
        if self.memory_usage_mb > 1000:
            suggestions.append("High memory usage - check for leaks")
        
        return suggestions
