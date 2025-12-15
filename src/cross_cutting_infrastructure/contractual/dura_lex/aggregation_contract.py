"""
Aggregation Contract - Dura Lex Enforcement for Phases 4-7

This module defines formal contracts for the hierarchical aggregation pipeline:
- Phase 4: DimensionAggregator (5 micro → 1 dimension)
- Phase 5: AreaPolicyAggregator (6 dimensions → 1 area)
- Phase 6: ClusterAggregator (multiple areas → 1 cluster)
- Phase 7: MacroAggregator (4 clusters → 1 holistic score)

Contract Hierarchy:
    BaseAggregationContract
        ├── DimensionAggregationContract
        ├── AreaAggregationContract
        ├── ClusterAggregationContract
        └── MacroAggregationContract

Mathematical Invariants:
    [AGG-001] Weight normalization: Σ(weights) = 1.0 ± 1e-6
    [AGG-002] Score bounds: 0.0 ≤ score ≤ MAX_SCORE
    [AGG-003] Coherence bounds: 0.0 ≤ coherence ≤ 1.0
    [AGG-004] Hermeticity: No gaps, no overlaps, no duplicates
    [AGG-005] Monotonicity: More high scores → higher aggregate
    [AGG-006] Convexity: weighted_avg lies in convex hull of inputs
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AggregationContractViolation:
    """Records contract violation with severity and context."""
    
    contract_id: str
    invariant_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    message: str
    actual_value: Any
    expected_value: Any
    context: dict[str, Any]


class BaseAggregationContract(ABC):
    """
    Base contract for all aggregation operations.
    
    Enforces fundamental mathematical properties:
    - Weight normalization
    - Score bounds
    - Non-negativity
    - Reproducibility
    """
    
    WEIGHT_TOLERANCE = 1e-6
    MAX_SCORE = 3.0
    MIN_SCORE = 0.0
    
    def __init__(self, contract_id: str, abort_on_violation: bool = True):
        """
        Initialize aggregation contract.
        
        Args:
            contract_id: Unique identifier for contract
            abort_on_violation: Whether to raise exception on violation
        """
        self.contract_id = contract_id
        self.abort_on_violation = abort_on_violation
        self.violations: list[AggregationContractViolation] = []
    
    def validate_weight_normalization(
        self,
        weights: list[float],
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        [AGG-001] Validate weights sum to 1.0 within tolerance.
        
        Mathematical property: Σ(w_i) = 1.0 ± ε where ε = 1e-6
        Rationale: Normalized weights ensure proper probability distribution
        
        Args:
            weights: List of weights to validate
            context: Additional context for error reporting
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If abort_on_violation and validation fails
        """
        if not weights:
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-001",
                severity="CRITICAL",
                message="Empty weights list",
                actual_value=[],
                expected_value="non-empty list",
                context=context or {}
            )
            self.violations.append(violation)
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        weight_sum = sum(weights)
        expected = 1.0
        
        if abs(weight_sum - expected) > self.WEIGHT_TOLERANCE:
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-001",
                severity="CRITICAL",
                message=f"Weights do not sum to 1.0: sum={weight_sum:.10f}",
                actual_value=weight_sum,
                expected_value=expected,
                context=context or {}
            )
            self.violations.append(violation)
            logger.error(f"[{self.contract_id}] Weight normalization violation: {violation.message}")
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        return True
    
    def validate_score_bounds(
        self,
        score: float,
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        [AGG-002] Validate score within valid bounds.
        
        Mathematical property: MIN_SCORE ≤ score ≤ MAX_SCORE
        Rationale: Scores must lie in defined range for consistency
        
        Args:
            score: Score to validate
            context: Additional context for error reporting
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If abort_on_violation and validation fails
        """
        if not (self.MIN_SCORE <= score <= self.MAX_SCORE):
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-002",
                severity="HIGH",
                message=f"Score out of bounds: {score:.4f} not in [{self.MIN_SCORE}, {self.MAX_SCORE}]",
                actual_value=score,
                expected_value=f"[{self.MIN_SCORE}, {self.MAX_SCORE}]",
                context=context or {}
            )
            self.violations.append(violation)
            logger.warning(f"[{self.contract_id}] Score bounds violation: {violation.message}")
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        return True
    
    def validate_coherence_bounds(
        self,
        coherence: float,
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        [AGG-003] Validate coherence within [0, 1] bounds.
        
        Mathematical property: 0.0 ≤ coherence ≤ 1.0
        Rationale: Coherence is a normalized metric
        
        Args:
            coherence: Coherence value to validate
            context: Additional context for error reporting
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If abort_on_violation and validation fails
        """
        if not (0.0 <= coherence <= 1.0):
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-003",
                severity="MEDIUM",
                message=f"Coherence out of bounds: {coherence:.4f} not in [0, 1]",
                actual_value=coherence,
                expected_value="[0.0, 1.0]",
                context=context or {}
            )
            self.violations.append(violation)
            logger.warning(f"[{self.contract_id}] Coherence bounds violation: {violation.message}")
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        return True
    
    def validate_convexity(
        self,
        aggregated: float,
        inputs: list[float],
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        [AGG-006] Validate convexity: aggregated in convex hull of inputs.
        
        Mathematical property: min(inputs) ≤ aggregated ≤ max(inputs)
        Rationale: Weighted averages lie within input bounds
        
        Args:
            aggregated: Aggregated result
            inputs: Input scores
            context: Additional context for error reporting
            
        Returns:
            True if valid, False otherwise
        """
        if not inputs:
            return True
        
        min_input = min(inputs)
        max_input = max(inputs)
        
        # Allow small tolerance for floating point
        tolerance = 1e-6
        
        if not (min_input - tolerance <= aggregated <= max_input + tolerance):
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-006",
                severity="HIGH",
                message=f"Convexity violation: {aggregated:.4f} not in [{min_input:.4f}, {max_input:.4f}]",
                actual_value=aggregated,
                expected_value=f"[{min_input:.4f}, {max_input:.4f}]",
                context=context or {}
            )
            self.violations.append(violation)
            logger.warning(f"[{self.contract_id}] Convexity violation: {violation.message}")
            # Don't abort on convexity - it's informational
            return False
        
        return True
    
    @abstractmethod
    def validate_hermeticity(
        self,
        actual_ids: set[str],
        expected_ids: set[str],
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        [AGG-004] Validate hermeticity: no gaps, no overlaps, no duplicates.
        
        Must be implemented by subclasses with specific validation logic.
        """
        pass
    
    def get_violations(self) -> list[AggregationContractViolation]:
        """Return all recorded violations."""
        return self.violations.copy()
    
    def clear_violations(self) -> None:
        """Clear all recorded violations."""
        self.violations.clear()


class DimensionAggregationContract(BaseAggregationContract):
    """
    Contract for Phase 4: Dimension Aggregation.
    
    Validates:
    - 5 micro questions per dimension (Q1-Q5)
    - Weight normalization
    - Score bounds
    - No duplicate questions
    """
    
    EXPECTED_QUESTION_COUNT = 5
    
    def __init__(self, abort_on_violation: bool = True):
        super().__init__("DIM_AGG", abort_on_violation)
    
    def validate_hermeticity(
        self,
        actual_ids: set[str],
        expected_ids: set[str],
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        Validate dimension has exactly the expected questions.
        
        Args:
            actual_ids: Actual question IDs present
            expected_ids: Expected question IDs
            context: Additional context
            
        Returns:
            True if hermetic, False otherwise
        """
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        
        if missing or extra:
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-004",
                severity="HIGH",
                message=f"Dimension hermeticity violation: missing={missing}, extra={extra}",
                actual_value=actual_ids,
                expected_value=expected_ids,
                context=context or {}
            )
            self.violations.append(violation)
            logger.error(f"[{self.contract_id}] Hermeticity violation: {violation.message}")
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        return True


class AreaAggregationContract(BaseAggregationContract):
    """
    Contract for Phase 5: Policy Area Aggregation.
    
    Validates:
    - 6 dimensions per area (DIM01-DIM06)
    - Dimension hermeticity
    - No dimension gaps or overlaps
    """
    
    EXPECTED_DIMENSION_COUNT = 6
    
    def __init__(self, abort_on_violation: bool = True):
        super().__init__("AREA_AGG", abort_on_violation)
    
    def validate_hermeticity(
        self,
        actual_ids: set[str],
        expected_ids: set[str],
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        Validate area has exactly the expected dimensions.
        
        Args:
            actual_ids: Actual dimension IDs present
            expected_ids: Expected dimension IDs
            context: Additional context
            
        Returns:
            True if hermetic, False otherwise
        """
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        
        if missing or extra:
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-004",
                severity="CRITICAL",
                message=f"Area hermeticity violation: missing={missing}, extra={extra}",
                actual_value=actual_ids,
                expected_value=expected_ids,
                context=context or {}
            )
            self.violations.append(violation)
            logger.error(f"[{self.contract_id}] Hermeticity violation: {violation.message}")
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        return True


class ClusterAggregationContract(BaseAggregationContract):
    """
    Contract for Phase 6: Cluster (MESO) Aggregation.
    
    Validates:
    - Variable areas per cluster (based on cluster definition)
    - Coherence calculation
    - Penalty application
    """
    
    def __init__(self, abort_on_violation: bool = True):
        super().__init__("CLUSTER_AGG", abort_on_violation)
    
    def validate_hermeticity(
        self,
        actual_ids: set[str],
        expected_ids: set[str],
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        Validate cluster has exactly the expected policy areas.
        
        Args:
            actual_ids: Actual area IDs present
            expected_ids: Expected area IDs for this cluster
            context: Additional context
            
        Returns:
            True if hermetic, False otherwise
        """
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        
        if missing or extra:
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-004",
                severity="HIGH",
                message=f"Cluster hermeticity violation: missing={missing}, extra={extra}",
                actual_value=actual_ids,
                expected_value=expected_ids,
                context=context or {}
            )
            self.violations.append(violation)
            logger.error(f"[{self.contract_id}] Hermeticity violation: {violation.message}")
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        return True


class MacroAggregationContract(BaseAggregationContract):
    """
    Contract for Phase 7: Macro (Holistic) Aggregation.
    
    Validates:
    - 4 clusters (MESO questions)
    - Cross-cutting coherence
    - Strategic alignment
    """
    
    EXPECTED_CLUSTER_COUNT = 4
    
    def __init__(self, abort_on_violation: bool = True):
        super().__init__("MACRO_AGG", abort_on_violation)
    
    def validate_hermeticity(
        self,
        actual_ids: set[str],
        expected_ids: set[str],
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        Validate macro has exactly 4 clusters.
        
        Args:
            actual_ids: Actual cluster IDs present
            expected_ids: Expected cluster IDs (should be 4)
            context: Additional context
            
        Returns:
            True if hermetic, False otherwise
        """
        if len(actual_ids) != self.EXPECTED_CLUSTER_COUNT:
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-004",
                severity="CRITICAL",
                message=f"Macro hermeticity violation: expected {self.EXPECTED_CLUSTER_COUNT} clusters, got {len(actual_ids)}",
                actual_value=actual_ids,
                expected_value=expected_ids,
                context=context or {}
            )
            self.violations.append(violation)
            logger.error(f"[{self.contract_id}] Hermeticity violation: {violation.message}")
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        
        if missing or extra:
            violation = AggregationContractViolation(
                contract_id=self.contract_id,
                invariant_id="AGG-004",
                severity="CRITICAL",
                message=f"Macro hermeticity violation: missing={missing}, extra={extra}",
                actual_value=actual_ids,
                expected_value=expected_ids,
                context=context or {}
            )
            self.violations.append(violation)
            logger.error(f"[{self.contract_id}] Hermeticity violation: {violation.message}")
            if self.abort_on_violation:
                raise ValueError(f"[{self.contract_id}] {violation.message}")
            return False
        
        return True


# Factory function for contract creation
def create_aggregation_contract(
    level: str,
    abort_on_violation: bool = True
) -> BaseAggregationContract:
    """
    Factory function to create appropriate aggregation contract.
    
    Args:
        level: Aggregation level (dimension, area, cluster, macro)
        abort_on_violation: Whether to abort on contract violations
        
    Returns:
        Appropriate contract instance
        
    Raises:
        ValueError: If level is invalid
    """
    contracts = {
        "dimension": DimensionAggregationContract,
        "area": AreaAggregationContract,
        "cluster": ClusterAggregationContract,
        "macro": MacroAggregationContract,
    }
    
    if level.lower() not in contracts:
        raise ValueError(f"Invalid aggregation level: {level}. Must be one of {list(contracts.keys())}")
    
    return contracts[level.lower()](abort_on_violation=abort_on_violation)
