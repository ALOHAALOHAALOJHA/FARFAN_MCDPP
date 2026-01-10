"""
Scope Validator for SISAS Signal Processing.

Implements Rule 1: Scope-Based Irrigation
"Information is provided to a consumer strictly according to
that consumer's defined scope."
"""

from dataclasses import dataclass, field
from typing import List, Any, Optional, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ScopeLevel(Enum):
    """Niveles de scope predefinidos."""

    EVIDENCE_COLLECTION = "evidence_collection"
    STRUCTURAL_ANALYSIS = "structural_analysis"
    SCORING_BASELINE = "scoring_baseline"
    SCORING_QUALITY = "scoring_quality"
    SCORING_CHAIN = "scoring_chain"
    CROSS_CUTTING = "cross_cutting"
    AGGREGATION = "aggregation"


@dataclass
class SignalScope:
    """Definición de scope para un consumidor."""

    allowed_signal_types: List[str]
    min_confidence: float = 0.50
    max_signals_per_query: int = 100
    allowed_membership_criteria: Optional[List[str]] = None
    allowed_dimensions: Optional[List[str]] = None
    allowed_policy_areas: Optional[List[str]] = None
    scope_name: Optional[str] = None
    scope_level: Optional[ScopeLevel] = None

    def allows_signal_type(self, signal_type: str) -> bool:
        return signal_type in self.allowed_signal_types

    def allows_confidence(self, confidence: float) -> bool:
        return confidence >= self.min_confidence


@dataclass
class ScopeValidationResult:
    """Resultado de validación de scope."""

    valid: bool
    consumer_id: str
    signal_type: str
    signal_confidence: float
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ScopeValidator:
    """Validador de scope para irrigación (Regla 1)."""

    def __init__(self, strict_mode: bool = True):
        self._strict_mode = strict_mode
        self._validation_log: List[ScopeValidationResult] = []
        self._violations_count = 0
        self._signals_filtered = 0

    def validate(
        self,
        consumer_id: str,
        scope: SignalScope,
        signal_type: str,
        signal_confidence: float,
        signal_metadata: Optional[dict] = None,
    ) -> ScopeValidationResult:
        """Valida si una señal puede ser irrigada a un consumidor."""

        violations = []
        warnings = []
        signal_metadata = signal_metadata or {}

        if not scope.allows_signal_type(signal_type):
            violations.append(
                f"Signal type {signal_type} not in allowed types: {scope.allowed_signal_types}"
            )

        if not scope.allows_confidence(signal_confidence):
            violations.append(
                f"Signal confidence {signal_confidence:.2f} below threshold {scope.min_confidence:.2f}"
            )

        if scope.allowed_membership_criteria is not None:
            signal_mc = signal_metadata.get("membership_criteria_id")
            if signal_mc and signal_mc not in scope.allowed_membership_criteria:
                violations.append(
                    f"Membership criteria {signal_mc} not in allowed: {scope.allowed_membership_criteria}"
                )

        is_valid = len(violations) == 0

        result = ScopeValidationResult(
            valid=is_valid,
            consumer_id=consumer_id,
            signal_type=signal_type,
            signal_confidence=signal_confidence,
            violations=violations,
            warnings=warnings,
        )

        self._validation_log.append(result)

        if not is_valid:
            self._violations_count += 1
            self._signals_filtered += 1

        return result

    def filter_signals(
        self, consumer_id: str, scope: SignalScope, signals: List[dict]
    ) -> List[dict]:
        """Filtra señales según el scope del consumidor."""

        allowed = []
        for signal in signals:
            signal_type = signal.get("signal_type", "")
            confidence = signal.get("confidence", 0.0)
            metadata = signal.get("metadata", {})

            result = self.validate(consumer_id, scope, signal_type, confidence, metadata)
            if result.valid:
                allowed.append(signal)

        if len(allowed) > scope.max_signals_per_query:
            allowed = sorted(allowed, key=lambda s: -s.get("confidence", 0))
            allowed = allowed[: scope.max_signals_per_query]

        return allowed

    def get_compliance_report(self) -> dict:
        """Genera reporte de compliance con Regla 1."""
        total = len(self._validation_log)
        valid = sum(1 for r in self._validation_log if r.valid)

        violations_by_type = {}
        for r in self._validation_log:
            if not r.valid:
                violations_by_type[r.signal_type] = violations_by_type.get(r.signal_type, 0) + 1

        return {
            "rule": "REGLA_1_SCOPE_BASED_IRRIGATION",
            "total_validations": total,
            "valid": valid,
            "violations": self._violations_count,
            "compliance_rate": valid / total if total > 0 else 1.0,
            "signals_filtered": self._signals_filtered,
            "violations_by_signal_type": violations_by_type,
            "status": "COMPLIANT" if self._violations_count == 0 else "VIOLATIONS_DETECTED",
        }

    def reset_log(self) -> None:
        self._validation_log.clear()
        self._violations_count = 0
        self._signals_filtered = 0


PREDEFINED_SCOPES = {
    ScopeLevel.EVIDENCE_COLLECTION: SignalScope(
        scope_name="Evidence Collection",
        scope_level=ScopeLevel.EVIDENCE_COLLECTION,
        allowed_signal_types=[
            "STRUCTURAL_MARKER",
            "QUANTITATIVE_TRIPLET",
            "NORMATIVE_REFERENCE",
            "PROGRAMMATIC_HIERARCHY",
            "FINANCIAL_CHAIN",
            "TEMPORAL_MARKER",
            "CAUSAL_LINK",
            "INSTITUTIONAL_ENTITY",
            "SEMANTIC_RELATIONSHIP",
        ],
        min_confidence=0.50,
        max_signals_per_query=200,
    ),
    ScopeLevel.SCORING_BASELINE: SignalScope(
        scope_name="Baseline Scoring",
        scope_level=ScopeLevel.SCORING_BASELINE,
        allowed_signal_types=["QUANTITATIVE_TRIPLET"],
        min_confidence=0.70,
        max_signals_per_query=50,
    ),
    ScopeLevel.SCORING_QUALITY: SignalScope(
        scope_name="Quality Scoring",
        scope_level=ScopeLevel.SCORING_QUALITY,
        allowed_signal_types=["QUANTITATIVE_TRIPLET", "FINANCIAL_CHAIN", "NORMATIVE_REFERENCE"],
        min_confidence=0.65,
        max_signals_per_query=75,
    ),
    ScopeLevel.SCORING_CHAIN: SignalScope(
        scope_name="Causal Chain Scoring",
        scope_level=ScopeLevel.SCORING_CHAIN,
        allowed_signal_types=["CAUSAL_LINK", "FINANCIAL_CHAIN", "PROGRAMMATIC_HIERARCHY"],
        min_confidence=0.60,
        max_signals_per_query=100,
    ),
    ScopeLevel.CROSS_CUTTING: SignalScope(
        scope_name="Cross-Cutting Themes",
        scope_level=ScopeLevel.CROSS_CUTTING,
        allowed_signal_types=[
            "CROSS_CUTTING_THEME",
            "POPULATION_DISAGGREGATION",
            "INSTITUTIONAL_ENTITY",
        ],
        min_confidence=0.55,
        max_signals_per_query=50,
    ),
}
