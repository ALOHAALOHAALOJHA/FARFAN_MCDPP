# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/consumption.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


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
    
    access_pattern: str = ""  # "bursty", "steady", "declining", "growing"
    peak_hour: int = 0  # 0-23
    
    consumers_accessing: List[str] = field(default_factory=list)
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. CONSUMPTION


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
    coupling_strength: str = ""  # "strong", "moderate", "weak", "none"
    
    co_occurrence_count: int = 0
    observation_period_days: int = 0
    
    typical_lag_ms: float = 0.0  # Tiempo entre activación de A y B
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONSUMPTION


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
    
    health_status: str = ""  # "healthy", "degraded", "unhealthy", "unknown"
    last_activity:  str = ""
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONSUMPTION
