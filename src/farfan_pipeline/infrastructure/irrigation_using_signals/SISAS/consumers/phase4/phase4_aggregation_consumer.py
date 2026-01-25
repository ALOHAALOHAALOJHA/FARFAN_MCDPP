# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase4/phase4_aggregation_consumer.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import logging
import time

from ..base_consumer import BaseConsumer
from ...core.signal import Signal, SignalConfidence
from ...core.contracts import ConsumptionContract


# =============================================================================
# PHASE 4 SOPHISTICATED ENHANCEMENTS - SIGNAL CORRELATION & ADAPTIVE PROCESSING
# =============================================================================

class SignalPriority(Enum):
    """Signal priority levels for adaptive processing"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class CircuitBreakerState(Enum):
    """Circuit breaker states for fault tolerance"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures detected, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class SignalCorrelation:
    """Tracks correlation between related signals"""
    correlation_id: str
    signal_ids: List[str] = field(default_factory=list)
    causation_chain: List[str] = field(default_factory=list)
    correlation_strength: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SignalQualityMetrics:
    """Comprehensive quality metrics for signals"""
    signal_id: str
    confidence_score: float = 0.0
    completeness_score: float = 0.0
    freshness_score: float = 0.0
    consistency_score: float = 0.0
    overall_quality: float = 0.0
    computed_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_overall_quality(self) -> float:
        """Calculate weighted overall quality"""
        self.overall_quality = (
            self.confidence_score * 0.3 +
            self.completeness_score * 0.25 +
            self.freshness_score * 0.25 +
            self.consistency_score * 0.2
        )
        return self.overall_quality


@dataclass
class CircuitBreaker:
    """Circuit breaker for fault tolerance"""
    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_max_calls: int = 3
    
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    half_open_attempts: int = 0

    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        self.success_count += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_attempts += 1
            if self.half_open_attempts >= self.half_open_max_calls:
                self.state = CircuitBreakerState.CLOSED
                self.half_open_attempts = 0

    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def can_attempt(self) -> bool:
        """Check if call can be attempted"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_attempts = 0
                    return True
            return False
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            return self.half_open_attempts < self.half_open_max_calls
        
        return False


@dataclass
class DeadLetterQueueEntry:
    """Entry in dead letter queue for failed signals"""
    signal: Signal
    failure_reason: str
    retry_count: int = 0
    max_retries: int = 3
    first_failed_at: datetime = field(default_factory=datetime.utcnow)
    last_retry_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    
    def can_retry(self) -> bool:
        """Check if signal can be retried"""
        if self.retry_count >= self.max_retries:
            return False
        if self.next_retry_at and datetime.utcnow() < self.next_retry_at:
            return False
        return True
    
    def schedule_retry(self, backoff_seconds: int = 60):
        """Schedule next retry with exponential backoff"""
        self.retry_count += 1
        self.last_retry_at = datetime.utcnow()
        backoff = backoff_seconds * (2 ** (self.retry_count - 1))
        self.next_retry_at = datetime.utcnow() + timedelta(seconds=backoff)


@dataclass
class Phase4AggregationConsumer(BaseConsumer):
    """
    SOPHISTICATED Phase 4 Signal-Enriched Aggregation Consumer.

    Implements advanced signal processing capabilities:
    - Multi-signal correlation and causality tracking
    - Adaptive signal prioritization based on quality metrics
    - Event chain reconstruction for full provenance
    - Sophisticated error recovery with signal replay
    - Circuit breaker pattern for fault tolerance
    - Dead letter queue with exponential backoff retry
    - Signal batching and throttling for performance
    - Real-time quality metrics computation

    Responsabilidad: Procesa señales para agregación enriquecida,
    integrando outputs de Phase 3 (scoring) para generar agregados
    dimensionales y territoriales con adaptive intelligence.

    Señales que consume:
    - AnswerDeterminacySignal: Para ponderación por determinación
    - AnswerSpecificitySignal: Para agregación por especificidad
    - DataIntegritySignal: Para validación de referencias
    - EventCompletenessSignal: Para verificación de completitud

    Señales que produce (indirectamente via vehicles):
    - AggregationCompleteSignal: Cuando la agregación termina
    - UncertaintyQuantifiedSignal: Cuantificación de incertidumbre
    """

    consumer_id: str = "phase4_aggregation_consumer"
    consumer_phase: str = "phase_04"
    
    # Sophisticated enhancement components
    _logger: logging.Logger = field(default=None)
    _correlation_index: Dict[str, SignalCorrelation] = field(default_factory=dict)
    _quality_metrics_cache: Dict[str, SignalQualityMetrics] = field(default_factory=dict)
    _signal_priority_queue: Dict[SignalPriority, deque] = field(default_factory=lambda: {
        SignalPriority.CRITICAL: deque(maxlen=1000),
        SignalPriority.HIGH: deque(maxlen=1000),
        SignalPriority.MEDIUM: deque(maxlen=1000),
        SignalPriority.LOW: deque(maxlen=1000)
    })
    _dead_letter_queue: List[DeadLetterQueueEntry] = field(default_factory=list)
    _circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    _signal_batch: List[Signal] = field(default_factory=list)
    _batch_size: int = 10
    _batch_timeout_seconds: float = 5.0
    _last_batch_process_time: datetime = field(default_factory=datetime.utcnow)
    _processing_history: deque = field(default_factory=lambda: deque(maxlen=10000))
    _causation_graph: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    
    # Performance metrics
    _metrics: Dict[str, Any] = field(default_factory=lambda: {
        "total_signals_processed": 0,
        "total_signals_failed": 0,
        "total_retries": 0,
        "total_batch_operations": 0,
        "avg_processing_time_ms": 0.0,
        "correlations_detected": 0,
        "circuit_breaker_trips": 0,
        "quality_adjustments_made": 0
    })

    def __post_init__(self):
        super().__post_init__()
        
        if self._logger is None:
            self._logger = logging.getLogger(f"SISAS.{self.consumer_id}")

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE4_AGGREGATION_ENHANCED",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "AnswerDeterminacySignal",
                "AnswerSpecificitySignal",
                "DataIntegritySignal",
                "EventCompletenessSignal",
                "StructuralAlignmentSignal",
                "CanonicalMappingSignal"
            ],
            subscribed_buses=["epistemic_bus", "structural_bus", "integrity_bus"],
            context_filters={
                "phase": ["phase_03", "phase_04"],
                "consumer_scope": ["Phase_04", "Cross-Phase"]
            },
            required_capabilities=["can_enrich", "can_transform", "can_validate"]
        )
        
        self._logger.info(f"Initialized sophisticated Phase 4 aggregation consumer with "
                         f"batch_size={self._batch_size}, circuit_breaker enabled")

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        SOPHISTICATED signal processing with multi-stage intelligence.

        Processing pipeline:
        1. Circuit breaker check
        2. Quality assessment and prioritization
        3. Correlation detection
        4. Adaptive batch processing
        5. Error recovery with DLQ
        6. Provenance tracking
        """
        start_time = time.time()
        
        try:
            # Stage 1: Circuit breaker check
            if not self._circuit_breaker.can_attempt():
                self._logger.warning(f"Circuit breaker OPEN - rejecting signal {signal.signal_id}")
                self._enqueue_to_dlq(signal, "Circuit breaker open")
                return {
                    "signal_id": signal.signal_id,
                    "processed": False,
                    "reason": "circuit_breaker_open",
                    "phase": "phase_04"
                }
            
            # Stage 2: Quality assessment
            quality_metrics = self._assess_signal_quality(signal)
            priority = self._determine_priority(signal, quality_metrics)
            
            # Stage 3: Correlation detection
            correlation = self._detect_correlations(signal)
            
            # Stage 4: Add to batch or process immediately based on priority
            if priority == SignalPriority.CRITICAL:
                result = self._process_signal_immediate(signal, quality_metrics, correlation)
            else:
                self._add_to_batch(signal, priority)
                result = {
                    "signal_id": signal.signal_id,
                    "processed": False,
                    "batched": True,
                    "priority": priority.name,
                    "phase": "phase_04"
                }
            
            # Check if batch should be processed
            self._check_and_process_batch()
            
            # Stage 5: Record success
            self._circuit_breaker.record_success()
            processing_time_ms = (time.time() - start_time) * 1000
            self._update_metrics(success=True, processing_time_ms=processing_time_ms)
            
            # Stage 6: Store provenance
            self._record_provenance(signal, result, quality_metrics, correlation)
            
            return result
            
        except Exception as e:
            self._logger.error(f"Signal processing error: {e}", exc_info=True)
            self._circuit_breaker.record_failure()
            self._enqueue_to_dlq(signal, str(e))
            self._update_metrics(success=False)
            
            return {
                "signal_id": signal.signal_id,
                "processed": False,
                "error": str(e),
                "phase": "phase_04"
            }

    def _process_signal_immediate(
        self,
        signal: Signal,
        quality_metrics: SignalQualityMetrics,
        correlation: Optional[SignalCorrelation]
    ) -> Dict[str, Any]:
        """
        Immediate processing for high-priority signals.
        
        Core aggregation logic with quality-aware weighting.
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "aggregation_components": {},
            "aggregated_value": 0.0,
            "uncertainty_bounds": {},
            "quality_metrics": {
                "overall_quality": quality_metrics.overall_quality,
                "confidence": quality_metrics.confidence_score,
                "completeness": quality_metrics.completeness_score,
                "freshness": quality_metrics.freshness_score
            },
            "correlation": {
                "correlation_id": correlation.correlation_id if correlation else None,
                "related_signals": len(correlation.signal_ids) if correlation else 0
            },
            "phase": "phase_04"
        }

        # Extract weights based on signal type with quality adjustment
        quality_factor = quality_metrics.overall_quality

        if signal.signal_type == "AnswerDeterminacySignal":
            base_weight = self._get_determinacy_weight(signal)
            result["aggregation_components"]["determinacy_weight"] = base_weight * quality_factor

        elif signal.signal_type == "AnswerSpecificitySignal":
            base_weight = self._get_specificity_weight(signal)
            result["aggregation_components"]["specificity_weight"] = base_weight * quality_factor

        elif signal.signal_type == "DataIntegritySignal":
            base_weight = self._get_integrity_weight(signal)
            result["aggregation_components"]["integrity_weight"] = base_weight * quality_factor

        elif signal.signal_type == "EventCompletenessSignal":
            base_weight = self._get_completeness_weight(signal)
            result["aggregation_components"]["completeness_weight"] = base_weight * quality_factor

        elif signal.signal_type == "StructuralAlignmentSignal":
            base_weight = self._get_alignment_weight(signal)
            result["aggregation_components"]["alignment_weight"] = base_weight * quality_factor

        elif signal.signal_type == "CanonicalMappingSignal":
            base_weight = self._get_mapping_weight(signal)
            result["aggregation_components"]["mapping_weight"] = base_weight * quality_factor

        # Calculate aggregated value with adaptive weighting
        result["aggregated_value"] = self._calculate_aggregated_value(
            result["aggregation_components"],
            quality_metrics
        )

        # Quantify uncertainty with correlation-aware bounds
        result["uncertainty_bounds"] = self._quantify_uncertainty(
            result["aggregation_components"],
            correlation
        )

        return result

    def _get_determinacy_weight(self, signal: Signal) -> float:
        """Obtiene peso de determinación para agregación"""
        level = str(getattr(signal, 'determinacy_level', 'INDETERMINATE'))
        weight_map = {
            "DeterminacyLevel.HIGH": 1.0,
            "DeterminacyLevel.MEDIUM": 0.7,
            "DeterminacyLevel.LOW": 0.4,
            "DeterminacyLevel.INDETERMINATE": 0.1
        }
        return weight_map.get(level, 0.5)

    def _get_specificity_weight(self, signal: Signal) -> float:
        """Obtiene peso de especificidad para agregación"""
        return getattr(signal, 'specificity_score', 0.5)

    def _get_integrity_weight(self, signal: Signal) -> float:
        """Obtiene peso de integridad para agregación"""
        return getattr(signal, 'integrity_score', 1.0)

    def _get_completeness_weight(self, signal: Signal) -> float:
        """Obtiene peso de completitud para agregación"""
        return getattr(signal, 'completeness_score', 1.0)

    def _get_alignment_weight(self, signal: Signal) -> float:
        """Obtiene peso de alineación estructural"""
        status = str(getattr(signal, 'alignment_status', 'MISALIGNED'))
        weight_map = {
            "AlignmentStatus.ALIGNED": 1.0,
            "AlignmentStatus.PARTIAL": 0.6,
            "AlignmentStatus.MISALIGNED": 0.2
        }
        return weight_map.get(status, 0.5)

    def _get_mapping_weight(self, signal: Signal) -> float:
        """Obtiene peso de mapeo canónico"""
        return getattr(signal, 'mapping_completeness', 0.5)

    def _calculate_aggregated_value(
        self,
        components: Dict[str, float],
        quality_metrics: Optional[SignalQualityMetrics] = None
    ) -> float:
        """
        Calcula valor agregado usando ponderación adaptativa.
        
        Aplica ajustes basados en calidad de señales para mejorar precisión.
        """
        if not components:
            return 0.0

        # Pesos para el método Choquet simplificado con ajuste adaptativo
        base_weights = {
            "determinacy_weight": 0.25,
            "specificity_weight": 0.25,
            "integrity_weight": 0.20,
            "completeness_weight": 0.15,
            "alignment_weight": 0.10,
            "mapping_weight": 0.05
        }
        
        # Adaptive weight adjustment based on signal quality
        if quality_metrics and quality_metrics.overall_quality > 0:
            quality_factor = quality_metrics.overall_quality
            # Boost weights for high-quality signals
            if quality_factor > 0.8:
                base_weights = {k: v * 1.1 for k, v in base_weights.items()}
                self._metrics["quality_adjustments_made"] += 1

        # Normalize weights to sum to 1.0
        total_weight = sum(base_weights.values())
        normalized_weights = {k: v / total_weight for k, v in base_weights.items()}

        weighted_sum = sum(
            components.get(key, 0.0) * weight
            for key, weight in normalized_weights.items()
        )

        return min(1.0, weighted_sum)

    def _quantify_uncertainty(
        self,
        components: Dict[str, float],
        correlation: Optional[SignalCorrelation] = None
    ) -> Dict[str, Any]:
        """
        Cuantifica incertidumbre con awareness de correlaciones.
        
        Considera strength de correlaciones para ajustar intervalos de confianza.
        """
        if not components:
            return {
                "lower_bound": 0.0,
                "upper_bound": 0.0,
                "confidence_interval": "UNKNOWN",
                "correlation_adjusted": False
            }

        # Varianza basada en dispersión de componentes
        values = list(components.values())
        if not values:
            return {
                "lower_bound": 0.0,
                "upper_bound": 0.0,
                "confidence_interval": "UNKNOWN",
                "correlation_adjusted": False
            }

        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        
        # Adjust uncertainty based on correlation strength
        correlation_adjusted = False
        if correlation and correlation.correlation_strength > 0.7:
            # Strong correlations reduce uncertainty
            std_dev *= (1.0 - (correlation.correlation_strength - 0.7) * 0.5)
            correlation_adjusted = True

        # Intervalos de confianza (95%)
        margin = 1.96 * std_dev
        lower = max(0.0, mean_val - margin)
        upper = min(1.0, mean_val + margin)

        # Determinar nivel de confianza
        if std_dev < 0.1:
            confidence = "HIGH"
        elif std_dev < 0.2:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return {
            "lower_bound": lower,
            "upper_bound": upper,
            "std_dev": std_dev,
            "confidence_interval": confidence,
            "margin_of_error": margin,
            "correlation_adjusted": correlation_adjusted,
            "correlation_strength": correlation.correlation_strength if correlation else 0.0
        }
    
    # =============================================================================
    # SOPHISTICATED HELPER METHODS - MULTI-SIGNAL INTELLIGENCE
    # =============================================================================
    
    def _assess_signal_quality(self, signal: Signal) -> SignalQualityMetrics:
        """
        Assess comprehensive quality metrics for a signal.
        
        Evaluates confidence, completeness, freshness, and consistency.
        """
        metrics = SignalQualityMetrics(signal_id=signal.signal_id)
        
        # Confidence score from signal
        if hasattr(signal, 'confidence'):
            confidence_map = {
                SignalConfidence.HIGH: 1.0,
                SignalConfidence.MEDIUM: 0.7,
                SignalConfidence.LOW: 0.4,
                SignalConfidence.INDETERMINATE: 0.1
            }
            metrics.confidence_score = confidence_map.get(signal.confidence, 0.5)
        else:
            metrics.confidence_score = 0.5
        
        # Completeness score based on payload
        if hasattr(signal, 'value') and signal.value is not None:
            metrics.completeness_score = 1.0
        else:
            metrics.completeness_score = 0.3
        
        # Freshness score based on signal age
        if hasattr(signal, 'created_at'):
            age_seconds = (datetime.utcnow() - signal.created_at).total_seconds()
            # Signals older than 1 hour get reduced freshness
            if age_seconds < 3600:
                metrics.freshness_score = 1.0
            elif age_seconds < 7200:
                metrics.freshness_score = 0.8
            elif age_seconds < 14400:
                metrics.freshness_score = 0.6
            else:
                metrics.freshness_score = 0.4
        else:
            metrics.freshness_score = 0.5
        
        # Consistency score - check against recent signals
        metrics.consistency_score = self._check_consistency(signal)
        
        # Calculate overall quality
        metrics.calculate_overall_quality()
        
        # Cache for future reference
        self._quality_metrics_cache[signal.signal_id] = metrics
        
        return metrics
    
    def _check_consistency(self, signal: Signal) -> float:
        """Check signal consistency against recent processing history"""
        # Simple heuristic: check if similar signals had similar values
        consistent_count = 0
        total_count = 0
        
        for hist_entry in list(self._processing_history)[-100:]:
            if hist_entry.get("signal_type") == signal.signal_type:
                total_count += 1
                # Simple consistency check
                if hasattr(signal, 'value') and 'aggregated_value' in hist_entry:
                    hist_val = hist_entry['aggregated_value']
                    curr_val = getattr(signal, 'value', 0)
                    if isinstance(curr_val, (int, float)) and isinstance(hist_val, (int, float)):
                        if abs(curr_val - hist_val) < 0.3:
                            consistent_count += 1
        
        if total_count > 0:
            return consistent_count / total_count
        return 0.7  # Default to reasonable consistency
    
    def _determine_priority(
        self,
        signal: Signal,
        quality_metrics: SignalQualityMetrics
    ) -> SignalPriority:
        """
        Adaptively determine signal priority based on quality and type.
        
        Higher quality signals and critical types get higher priority.
        """
        # Base priority on signal type
        critical_types = ["DataIntegritySignal", "EventCompletenessSignal"]
        high_types = ["AnswerDeterminacySignal", "StructuralAlignmentSignal"]
        
        if signal.signal_type in critical_types:
            base_priority = SignalPriority.CRITICAL
        elif signal.signal_type in high_types:
            base_priority = SignalPriority.HIGH
        else:
            base_priority = SignalPriority.MEDIUM
        
        # Adjust based on quality
        if quality_metrics.overall_quality < 0.4 and base_priority == SignalPriority.CRITICAL:
            return SignalPriority.HIGH  # Downgrade low-quality critical signals
        elif quality_metrics.overall_quality > 0.9 and base_priority == SignalPriority.MEDIUM:
            return SignalPriority.HIGH  # Upgrade very high-quality signals
        
        return base_priority
    
    def _detect_correlations(self, signal: Signal) -> Optional[SignalCorrelation]:
        """
        Detect correlations with other signals using correlation_id and causation.
        
        Builds correlation chains for provenance tracking by:
        1. Grouping signals by correlation_id (typically node_id from context)
        2. Building causation graph from event_id relationships
        3. Computing correlation strength based on shared contexts
        """
        correlation_id = getattr(signal.context, 'node_id', None) or signal.signal_id
        
        # Check if correlation already exists
        if correlation_id in self._correlation_index:
            correlation = self._correlation_index[correlation_id]
            correlation.signal_ids.append(signal.signal_id)
            
            # Update causation graph: link this signal to previous signals with same correlation
            # This builds the causal chain where signals with same correlation_id are related
            if hasattr(signal.source, 'event_id'):
                parent_event = signal.source.event_id
                for existing_signal_id in correlation.signal_ids[:-1]:
                    self._causation_graph[existing_signal_id].add(signal.signal_id)
            
            # Add to causation chain (most recent signals first)
            if signal.signal_id not in correlation.causation_chain:
                correlation.causation_chain.append(signal.signal_id)
            
            self._metrics["correlations_detected"] += 1
            return correlation
        else:
            # Create new correlation starting with this signal
            correlation = SignalCorrelation(
                correlation_id=correlation_id,
                signal_ids=[signal.signal_id],
                causation_chain=[signal.signal_id],  # Initialize with current signal
                correlation_strength=1.0,
                metadata={
                    "phase": signal.context.phase,
                    "node_type": signal.context.node_type
                }
            )
            self._correlation_index[correlation_id] = correlation
            return correlation
    
    def _add_to_batch(self, signal: Signal, priority: SignalPriority):
        """Add signal to priority-based batch queue"""
        self._signal_priority_queue[priority].append(signal)
        self._logger.debug(f"Signal {signal.signal_id} added to {priority.name} queue")
    
    def _check_and_process_batch(self):
        """Check if batch should be processed based on size or time"""
        total_queued = sum(len(q) for q in self._signal_priority_queue.values())
        time_since_last = (datetime.utcnow() - self._last_batch_process_time).total_seconds()
        
        should_process = (
            total_queued >= self._batch_size or
            time_since_last >= self._batch_timeout_seconds
        )
        
        if should_process and total_queued > 0:
            self._process_batch()
    
    def _process_batch(self):
        """Process batched signals in priority order"""
        self._logger.info("Processing signal batch")
        batch_results = []
        
        # Process in priority order: CRITICAL -> HIGH -> MEDIUM -> LOW
        for priority in sorted(self._signal_priority_queue.keys(), key=lambda p: p.value, reverse=True):
            queue = self._signal_priority_queue[priority]
            
            while queue:
                signal = queue.popleft()
                try:
                    quality_metrics = self._quality_metrics_cache.get(
                        signal.signal_id,
                        self._assess_signal_quality(signal)
                    )
                    correlation = self._detect_correlations(signal)
                    result = self._process_signal_immediate(signal, quality_metrics, correlation)
                    batch_results.append(result)
                except Exception as e:
                    self._logger.error(f"Batch processing error for {signal.signal_id}: {e}")
                    self._enqueue_to_dlq(signal, str(e))
        
        self._last_batch_process_time = datetime.utcnow()
        self._metrics["total_batch_operations"] += 1
        self._logger.info(f"Batch processed: {len(batch_results)} signals")
    
    def _enqueue_to_dlq(self, signal: Signal, reason: str):
        """Add failed signal to dead letter queue for retry"""
        entry = DeadLetterQueueEntry(
            signal=signal,
            failure_reason=reason
        )
        entry.schedule_retry()
        self._dead_letter_queue.append(entry)
        self._logger.warning(f"Signal {signal.signal_id} added to DLQ: {reason}")
    
    def process_dlq_retries(self) -> Dict[str, Any]:
        """
        Process retry-able signals from dead letter queue.
        
        Implements exponential backoff retry strategy.
        """
        retry_results = {
            "attempted": 0,
            "succeeded": 0,
            "failed": 0,
            "exhausted": 0
        }
        
        for entry in list(self._dead_letter_queue):
            if not entry.can_retry():
                if entry.retry_count >= entry.max_retries:
                    retry_results["exhausted"] += 1
                continue
            
            retry_results["attempted"] += 1
            self._metrics["total_retries"] += 1
            
            try:
                result = self.process_signal(entry.signal)
                if result.get("processed", False):
                    retry_results["succeeded"] += 1
                    self._dead_letter_queue.remove(entry)
                    self._logger.info(f"DLQ retry succeeded for {entry.signal.signal_id}")
                else:
                    retry_results["failed"] += 1
                    entry.schedule_retry()
            except Exception as e:
                retry_results["failed"] += 1
                entry.schedule_retry()
                self._logger.error(f"DLQ retry failed for {entry.signal.signal_id}: {e}")
        
        return retry_results
    
    def _record_provenance(
        self,
        signal: Signal,
        result: Dict[str, Any],
        quality_metrics: SignalQualityMetrics,
        correlation: Optional[SignalCorrelation]
    ):
        """Record complete provenance for audit trail"""
        provenance_entry = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
            "quality_metrics": {
                "overall_quality": quality_metrics.overall_quality,
                "confidence": quality_metrics.confidence_score,
                "completeness": quality_metrics.completeness_score,
                "freshness": quality_metrics.freshness_score,
                "consistency": quality_metrics.consistency_score
            },
            "correlation_id": correlation.correlation_id if correlation else None,
            "event_chain": self._reconstruct_event_chain(signal)
        }
        self._processing_history.append(provenance_entry)
    
    def _reconstruct_event_chain(self, signal: Signal) -> List[str]:
        """Reconstruct full event causation chain for a signal"""
        chain = [signal.signal_id]
        visited = {signal.signal_id}
        
        # Traverse causation graph backwards
        to_visit = [signal.signal_id]
        while to_visit:
            current = to_visit.pop(0)
            # Find parents in causation graph
            for parent_id, children in self._causation_graph.items():
                if current in children and parent_id not in visited:
                    chain.insert(0, parent_id)
                    visited.add(parent_id)
                    to_visit.append(parent_id)
        
        return chain
    
    def _update_metrics(self, success: bool, processing_time_ms: float = 0.0):
        """Update performance metrics"""
        if success:
            self._metrics["total_signals_processed"] += 1
            # Update rolling average
            current_avg = self._metrics["avg_processing_time_ms"]
            total_processed = self._metrics["total_signals_processed"]
            self._metrics["avg_processing_time_ms"] = (
                (current_avg * (total_processed - 1) + processing_time_ms) / total_processed
            )
        else:
            self._metrics["total_signals_failed"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive consumer metrics"""
        return {
            **self._metrics,
            "dlq_size": len(self._dead_letter_queue),
            "correlation_count": len(self._correlation_index),
            "circuit_breaker_state": self._circuit_breaker.state.value,
            "queued_signals": {
                priority.name: len(queue)
                for priority, queue in self._signal_priority_queue.items()
            },
            "quality_metrics_cached": len(self._quality_metrics_cache),
            "provenance_entries": len(self._processing_history)
        }
    
    def get_correlation_insights(self) -> Dict[str, Any]:
        """Get insights about signal correlations"""
        return {
            "total_correlations": len(self._correlation_index),
            "correlation_details": [
                {
                    "correlation_id": corr.correlation_id,
                    "signal_count": len(corr.signal_ids),
                    "strength": corr.correlation_strength,
                    "age_seconds": (datetime.utcnow() - corr.created_at).total_seconds()
                }
                for corr in self._correlation_index.values()
            ],
            "causation_graph_size": len(self._causation_graph)
        }
