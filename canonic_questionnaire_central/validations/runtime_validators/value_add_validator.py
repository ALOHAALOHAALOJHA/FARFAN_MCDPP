"""
Value-Add Validator for SISAS Signal Processing.

Implements Rule 2: Value-Add Validation
"Information is provided only if it demonstrably adds value
to the process the consumer is executing."
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from collections import defaultdict
import hashlib
import statistics
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValueAddMetrics:
    """Métricas de value-add por señal."""
    signal_id: str
    signal_type: str
    baseline_score: float
    enriched_score: float
    delta: float
    delta_percentage: float
    contributing_to_questions: List[str]
    
    @property
    def is_valuable(self) -> bool:
        return self.delta_percentage > 0.10


class ValueAddScorer:
    """Medidor de value-add por señal (Regla 2)."""
    
    def __init__(self, min_value_add_threshold: float = 0.10):
        self._baseline_scores: Dict[str, float] = {}
        self._enriched_scores: Dict[str, float] = {}
        self._signal_contributions: Dict[str, List[str]] = defaultdict(list)
        self._value_add_log: List[ValueAddMetrics] = []
        self._min_threshold = min_value_add_threshold
    
    def record_baseline(self, question_id: str, score: float) -> None:
        self._baseline_scores[question_id] = score
    
    def record_enriched(self, question_id: str, score: float, contributing_signals: List[str]) -> None:
        self._enriched_scores[question_id] = score
        for signal_id in contributing_signals:
            self._signal_contributions[signal_id].append(question_id)
    
    def compute_value_add(self, signal_id: str, signal_type: str) -> ValueAddMetrics:
        """Calcula el value-add de una señal específica."""
        questions = self._signal_contributions.get(signal_id, [])
        
        if not questions:
            return ValueAddMetrics(
                signal_id=signal_id, signal_type=signal_type,
                baseline_score=0.0, enriched_score=0.0,
                delta=0.0, delta_percentage=0.0,
                contributing_to_questions=[]
            )
        
        deltas = []
        for q_id in questions:
            baseline = self._baseline_scores.get(q_id, 0.0)
            enriched = self._enriched_scores.get(q_id, 0.0)
            deltas.append(enriched - baseline)
        
        avg_delta = statistics.mean(deltas) if deltas else 0.0
        avg_baseline = statistics.mean([self._baseline_scores.get(q, 0) for q in questions])
        avg_enriched = statistics.mean([self._enriched_scores.get(q, 0) for q in questions])
        delta_pct = avg_delta / avg_baseline if avg_baseline > 0 else 0.0
        
        metrics = ValueAddMetrics(
            signal_id=signal_id, signal_type=signal_type,
            baseline_score=avg_baseline, enriched_score=avg_enriched,
            delta=avg_delta, delta_percentage=delta_pct,
            contributing_to_questions=questions
        )
        self._value_add_log.append(metrics)
        return metrics
    
    def estimate_value_add(self, signal_type: str, payload: Dict[str, Any]) -> float:
        """Estima value-add a priori. Source: corpus_thresholds_weights.json"""
        estimates = {
            "QUANTITATIVE_TRIPLET": lambda p: self._estimate_triplet_value(p),
            "FINANCIAL_CHAIN": lambda p: 0.20 if p.get("programa_vinculado") else 0.10,
            "STRUCTURAL_MARKER": lambda p: 0.15 if p.get("section_context") == "PPI" else 0.08,
            "NORMATIVE_REFERENCE": lambda p: 0.18 if p.get("norm_type") == "ley" else 0.10,
            "CAUSAL_LINK": lambda p: min(0.25, 0.10 + p.get("chain_length", 0) * 0.05),
            "TEMPORAL_MARKER": lambda p: 0.02,
            "INSTITUTIONAL_ENTITY": lambda p: 0.10 if p.get("level") == "NATIONAL" else 0.05,
            "POPULATION_DISAGGREGATION": lambda p: 0.12,
            "PROGRAMMATIC_HIERARCHY": lambda p: 0.10,
            "SEMANTIC_RELATIONSHIP": lambda p: 0.03,
        }
        estimator = estimates.get(signal_type, lambda p: 0.05)
        return estimator(payload)
    
    def _estimate_triplet_value(self, payload: Dict[str, Any]) -> float:
        completeness = payload.get("completeness", "BAJO")
        values = {"COMPLETO": 0.25, "ALTO": 0.20, "MEDIO": 0.15, "BAJO": 0.08}
        return values.get(completeness, 0.10)
    
    def should_emit(self, signal_type: str, payload: Dict[str, Any], threshold: Optional[float] = None) -> bool:
        threshold = threshold or self._min_threshold
        return self.estimate_value_add(signal_type, payload) >= threshold
    
    def get_report(self) -> Dict[str, Any]:
        if not self._value_add_log:
            return {"rule": "REGLA_2_VALUE_ADD_VALIDATION", "status": "no_data", "signals_analyzed": 0}
        
        valuable = [m for m in self._value_add_log if m.is_valuable]
        low_value = [m for m in self._value_add_log if not m.is_valuable]
        
        by_type = defaultdict(list)
        for m in self._value_add_log:
            by_type[m.signal_type].append(m.delta_percentage)
        
        type_averages = {t: statistics.mean(deltas) for t, deltas in by_type.items()}
        
        return {
            "rule": "REGLA_2_VALUE_ADD_VALIDATION",
            "status": "complete",
            "signals_analyzed": len(self._value_add_log),
            "valuable_signals": len(valuable),
            "low_value_signals": len(low_value),
            "value_rate": len(valuable) / len(self._value_add_log) if self._value_add_log else 0,
            "average_delta_by_type": type_averages
        }
    
    def reset(self) -> None:
        self._baseline_scores.clear()
        self._enriched_scores.clear()
        self._signal_contributions.clear()
        self._value_add_log.clear()


class SignalDeduplicator:
    """Eliminador de señales redundantes."""
    
    def __init__(self):
        self._seen_hashes: set = set()
        self._duplicates_removed: int = 0
        self._originals_kept: int = 0
    
    def _compute_content_hash(self, signal: Dict[str, Any]) -> str:
        signal_type = signal.get("signal_type", "")
        source_chunk = signal.get("source_chunk_id", "")
        payload = signal.get("payload", {})
        content = f"{signal_type}:{source_chunk}:{sorted(payload.items())}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def is_duplicate(self, signal: Dict[str, Any]) -> bool:
        content_hash = self._compute_content_hash(signal)
        if content_hash in self._seen_hashes:
            self._duplicates_removed += 1
            return True
        self._seen_hashes.add(content_hash)
        self._originals_kept += 1
        return False
    
    def deduplicate(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sorted_signals = sorted(signals, key=lambda s: -s.get("confidence", 0))
        unique = []
        for signal in sorted_signals:
            if not self.is_duplicate(signal):
                unique.append(signal)
        return unique
    
    def get_stats(self) -> Dict[str, Any]:
        total = self._originals_kept + self._duplicates_removed
        return {
            "total_processed": total,
            "originals_kept": self._originals_kept,
            "duplicates_removed": self._duplicates_removed,
            "deduplication_rate": self._duplicates_removed / total if total > 0 else 0.0
        }
    
    def reset(self) -> None:
        self._seen_hashes.clear()
        self._duplicates_removed = 0
        self._originals_kept = 0
