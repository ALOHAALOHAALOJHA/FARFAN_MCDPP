"""
Scope Validator - REGLA 1 Enforcement

"Information is provided to a consumer strictly according to 
that consumer's defined scope."
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field


class ScopeLevel(Enum):
    EVIDENCE_COLLECTION = "evidence_collection"
    STRUCTURAL_ANALYSIS = "structural_analysis"
    SCORING_BASELINE = "scoring_baseline"
    SCORING_ENRICHED = "scoring_enriched"
    CAUSAL_VALIDATION = "causal_validation"
    AGGREGATION = "aggregation"
    REPORTING = "reporting"


@dataclass
class SignalScope:
    scope_id: str
    level: ScopeLevel
    allowed_signal_types: List[str]
    min_confidence: float = 0.5
    max_signals_per_query: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def allows_signal_type(self, signal_type: str) -> bool:
        return signal_type in self.allowed_signal_types
    
    def allows_confidence(self, confidence: float) -> bool:
        return confidence >= self.min_confidence


PREDEFINED_SCOPES = {
    "EVIDENCE_NEXUS": SignalScope(
        scope_id="EVIDENCE_NEXUS",
        level=ScopeLevel.EVIDENCE_COLLECTION,
        allowed_signal_types=[
            "STRUCTURAL_MARKER", "QUANTITATIVE_TRIPLET", "NORMATIVE_REFERENCE",
            "FINANCIAL_CHAIN", "CAUSAL_LINK", "SEMANTIC_RELATIONSHIP"
        ],
        min_confidence=0.6,
        max_signals_per_query=200
    ),
    "BASELINE_SCORER": SignalScope(
        scope_id="BASELINE_SCORER",
        level=ScopeLevel.SCORING_BASELINE,
        allowed_signal_types=["QUANTITATIVE_TRIPLET"],
        min_confidence=0.7,
        max_signals_per_query=50
    ),
    "POLICY_AREA_SCORER": SignalScope(
        scope_id="POLICY_AREA_SCORER",
        level=ScopeLevel.SCORING_ENRICHED,
        allowed_signal_types=[
            "NORMATIVE_REFERENCE", "FINANCIAL_CHAIN", "POPULATION_DISAGGREGATION"
        ],
        min_confidence=0.7,
        max_signals_per_query=100
    ),
    "DIMENSION_AGGREGATOR": SignalScope(
        scope_id="DIMENSION_AGGREGATOR",
        level=ScopeLevel.AGGREGATION,
        allowed_signal_types=["PROGRAMMATIC_HIERARCHY", "FINANCIAL_CHAIN"],
        min_confidence=0.8,
        max_signals_per_query=100
    ),
    "CLUSTER_AGGREGATOR": SignalScope(
        scope_id="CLUSTER_AGGREGATOR",
        level=ScopeLevel.AGGREGATION,
        allowed_signal_types=["PROGRAMMATIC_HIERARCHY"],
        min_confidence=0.8,
        max_signals_per_query=50
    )
}


@dataclass
class ScopeValidationResult:
    is_valid: bool
    consumer_id: str
    signal_type: str
    confidence: float
    scope: SignalScope
    violations: List[str]


class ScopeValidator:
    def __init__(self, scopes: Optional[Dict[str, SignalScope]] = None):
        self.scopes = scopes or PREDEFINED_SCOPES
    
    def validate(self, consumer_id: str, signal_type: str, confidence: float) -> ScopeValidationResult:
        scope = self.scopes.get(consumer_id)
        if not scope:
            return ScopeValidationResult(
                is_valid=False, consumer_id=consumer_id, signal_type=signal_type,
                confidence=confidence, scope=None, violations=[f"No scope defined for {consumer_id}"]
            )
        
        violations = []
        if not scope.allows_signal_type(signal_type):
            violations.append(f"Signal type {signal_type} not in allowed: {scope.allowed_signal_types}")
        if not scope.allows_confidence(confidence):
            violations.append(f"Confidence {confidence} < min {scope.min_confidence}")
        
        return ScopeValidationResult(
            is_valid=len(violations) == 0,
            consumer_id=consumer_id, signal_type=signal_type,
            confidence=confidence, scope=scope, violations=violations
        )
    
    def filter_signals(self, consumer_id: str, signals: List[Dict]) -> List[Dict]:
        scope = self.scopes.get(consumer_id)
        if not scope:
            return []
        
        filtered = [
            s for s in signals
            if scope.allows_signal_type(s.get("signal_type", ""))
            and scope.allows_confidence(s.get("confidence", 0))
        ]
        return filtered[:scope.max_signals_per_query]
