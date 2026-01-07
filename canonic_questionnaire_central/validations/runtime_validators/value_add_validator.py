"""
Value-Add Validator - REGLA 2 Enforcement

"Information is provided only if it demonstrably adds value 
to the process the consumer is executing."
"""
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import json


@dataclass
class ValueAddMetrics:
    signal_id: str
    baseline_score: float
    enriched_score: float
    value_add_delta: float
    value_add_pct: float
    is_duplicate: bool
    recommendation: str


class SignalDeduplicator:
    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.duplicates_removed: int = 0
    
    def _compute_hash(self, signal: Dict) -> str:
        payload = signal.get("payload", {})
        content = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def is_duplicate(self, signal: Dict) -> bool:
        h = self._compute_hash(signal)
        if h in self.seen_hashes:
            return True
        self.seen_hashes.add(h)
        return False
    
    def deduplicate(self, signals: List[Dict]) -> List[Dict]:
        result = []
        for signal in signals:
            if not self.is_duplicate(signal):
                result.append(signal)
            else:
                self.duplicates_removed += 1
        return result
    
    def get_stats(self) -> Dict[str, int]:
        return {
            "unique_signals": len(self.seen_hashes),
            "duplicates_removed": self.duplicates_removed
        }


class ValueAddScorer:
    def __init__(self, min_value_add_threshold: float = 0.05):
        self.threshold = min_value_add_threshold
        self.baseline_scores: Dict[str, float] = {}
        self.enriched_scores: Dict[str, float] = {}
        self.signal_contributions: Dict[str, List[str]] = defaultdict(list)
    
    def record_baseline(self, question_id: str, score: float):
        self.baseline_scores[question_id] = score
    
    def record_enriched(self, question_id: str, score: float, signal_ids: List[str]):
        self.enriched_scores[question_id] = score
        self.signal_contributions[question_id] = signal_ids
    
    def compute_value_add(self, question_id: str, signal_id: str) -> ValueAddMetrics:
        baseline = self.baseline_scores.get(question_id, 0)
        enriched = self.enriched_scores.get(question_id, 0)
        delta = enriched - baseline
        
        signals = self.signal_contributions.get(question_id, [])
        contribution = delta / len(signals) if signals else 0
        pct = (contribution / baseline * 100) if baseline > 0 else 0
        
        return ValueAddMetrics(
            signal_id=signal_id,
            baseline_score=baseline,
            enriched_score=enriched,
            value_add_delta=contribution,
            value_add_pct=pct,
            is_duplicate=False,
            recommendation="KEEP" if abs(contribution) >= self.threshold else "CONSIDER_REMOVAL"
        )
    
    def should_emit(self, signal_type: str, payload: Dict) -> bool:
        # Heuristic estimation
        if signal_type == "QUANTITATIVE_TRIPLET":
            completeness = payload.get("completeness", 0)
            return completeness >= 0.5
        if signal_type == "STRUCTURAL_MARKER":
            section = payload.get("section_context", "")
            return section in ["PPI", "DIAGNOSTICO", "ESTRATEGICA"]
        return True  # Default: emit
    
    def get_low_value_signals(self) -> List[str]:
        low_value = []
        for qid, signals in self.signal_contributions.items():
            for sig in signals:
                metrics = self.compute_value_add(qid, sig)
                if metrics.recommendation == "CONSIDER_REMOVAL":
                    low_value.append(sig)
        return low_value
