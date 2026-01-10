"""
Signal Consumption Tracking Integration

Integrates SignalConsumptionProof tracking into executor pattern matching
to enable utility measurement and waste ratio calculation.

This module provides:
- Consumption proof tracking during pattern matching
- Integration with evidence extraction
- Proof chain verification
- Waste ratio calculation

Author: F.A.R.F.A.N Pipeline
Date: 2025-01-15
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption import (
    SignalConsumptionProof,
)

if TYPE_CHECKING:
    import farfan_pipeline.phases.Phase_2.executors.base_executor_with_contract import BaseExecutorWithContract


@dataclass
class ConsumptionTracker:
    """Tracks signal consumption during executor execution."""
    
    executor_id: str
    question_id: str
    policy_area: str
    proof: SignalConsumptionProof = field(init=False)
    injection_time: float = field(default_factory=time.time)
    match_count: int = 0
    evidence_count: int = 0
    
    def __post_init__(self) -> None:
        """Initialize consumption proof."""
        self.proof = SignalConsumptionProof(
            executor_id=self.executor_id,
            question_id=self.question_id,
            policy_area=self.policy_area,
            timestamp=self.injection_time,
        )
    
    def record_pattern_match(
        self,
        pattern: str | dict[str, Any],
        text_segment: str,
        produced_evidence: bool = False,
    ) -> None:
        """Record a pattern match and update consumption proof.
        
        Args:
            pattern: Pattern string or pattern dict with 'pattern' key
            text_segment: Text segment that matched
            produced_evidence: Whether this match produced evidence
        """
        # Extract pattern string
        if isinstance(pattern, dict):
            pattern_str = pattern.get("pattern", str(pattern))
            pattern_id = pattern.get("id", "")
        else:
            pattern_str = str(pattern)
            pattern_id = ""
        
        # Record in proof
        self.proof.record_pattern_match(pattern_str, text_segment)
        self.match_count += 1
        
        if produced_evidence:
            self.evidence_count += 1
        
        logger.debug(
            "pattern_match_tracked",
            executor_id=self.executor_id,
            question_id=self.question_id,
            pattern_id=pattern_id[:50],
            match_count=self.match_count,
            evidence_count=self.evidence_count,
        )
    
    def get_consumption_summary(self) -> dict[str, Any]:
        """Get summary of consumption tracking.
        
        Returns:
            Dict with consumption metrics
        """
        return {
            "executor_id": self.executor_id,
            "question_id": self.question_id,
            "policy_area": self.policy_area,
            "match_count": self.match_count,
            "evidence_count": self.evidence_count,
            "proof_chain_length": len(self.proof.proof_chain),
            "proof_chain_head": self.proof.proof_chain[-1] if self.proof.proof_chain else None,
            "injection_time": self.injection_time,
            "consumption_time": time.time(),
        }
    
    def get_proof(self) -> SignalConsumptionProof:
        """Get the consumption proof object."""
        return self.proof


def create_consumption_tracker(
    executor_id: str,
    question_id: str,
    policy_area: str,
    injection_time: float | None = None,
) -> ConsumptionTracker:
    """Create a consumption tracker for an executor execution.
    
    Args:
        executor_id: Executor identifier (e.g., "D1-Q1")
        question_id: Question ID (e.g., "Q001")
        policy_area: Policy area code (e.g., "PA01")
    
    Returns:
        ConsumptionTracker instance
    """
    return ConsumptionTracker(
        executor_id=executor_id,
        question_id=question_id,
        policy_area=policy_area,
        injection_time=time.time() if injection_time is None else float(injection_time),
    )


def track_pattern_match_from_evidence(
    tracker: ConsumptionTracker,
    evidence_item: dict[str, Any],
    text: str,
) -> None:
    """Track pattern match from an evidence item.
    
    Args:
        tracker: Consumption tracker instance
        evidence_item: Evidence item dict with lineage information
        text: Source text for extracting match segment
    """
    lineage = evidence_item.get("lineage", {})
    pattern_id = lineage.get("pattern_id", "")
    pattern_text = lineage.get("pattern_text", "")
    span = evidence_item.get("span", (0, 0))
    
    # Extract text segment
    if span and len(span) == 2:
        start, end = span
        text_segment = text[start:end]
    else:
        text_segment = evidence_item.get("raw_text", "")[:100]
    
    # Record match
    tracker.record_pattern_match(
        pattern={"id": pattern_id, "pattern": pattern_text},
        text_segment=text_segment,
        produced_evidence=True,  # Evidence items always produce evidence
    )


# ============================================================================
# INTEGRATION WITH BASE EXECUTOR
# ============================================================================

def inject_consumption_tracking(
    executor: BaseExecutorWithContract,
    question_id: str,
    policy_area_id: str,
    injection_time: float | None = None,
) -> ConsumptionTracker:
    """Inject consumption tracking into executor execution.
    
    This function should be called at the start of executor execution
    to enable consumption tracking throughout the execution.
    
    Args:
        executor: Base executor instance
        question_id: Question ID being processed
        policy_area_id: Policy area ID
    
    Returns:
        ConsumptionTracker instance
    
    Example:
        >>> tracker = inject_consumption_tracking(executor, "Q001", "PA01")
        >>> # During execution, pattern matches are tracked
        >>> summary = tracker.get_consumption_summary()
    """
    executor_id = executor.get_base_slot()
    tracker = create_consumption_tracker(
        executor_id, question_id, policy_area_id, injection_time=injection_time
    )
    
    # Store tracker in executor for access during execution
    # Use a private attribute to avoid conflicts
    setattr(executor, "_consumption_tracker", tracker)
    
    logger.info(
        "consumption_tracking_injected",
        executor_id=executor_id,
        question_id=question_id,
        policy_area=policy_area_id,
    )
    
    return tracker


def get_consumption_tracker(executor: BaseExecutorWithContract) -> ConsumptionTracker | None:
    """Get consumption tracker from executor if it exists.
    
    Args:
        executor: Base executor instance
    
    Returns:
        ConsumptionTracker instance or None if not injected
    """
    return getattr(executor, "_consumption_tracker", None)


def record_evidence_matches(
    executor: BaseExecutorWithContract,
    evidence: dict[str, Any],
    source_text: str,
) -> None:
    """Record pattern matches from evidence dict.
    
    This function extracts pattern matches from evidence and records them
    in the consumption tracker.
    
    Args:
        executor: Base executor instance with injected tracker
        evidence: Evidence dict with element_type -> matches structure
        source_text: Source text used for matching
    """
    tracker = get_consumption_tracker(executor)
    if tracker is None:
        logger.warning(
            "consumption_tracker_not_found",
            executor_id=executor.get_base_slot(),
        )
        return
    
    # Iterate through evidence items
    for element_type, matches in evidence.items():
        if not isinstance(matches, list):
            continue
        
        for match_item in matches:
            if isinstance(match_item, dict):
                track_pattern_match_from_evidence(tracker, match_item, source_text)


# ============================================================================
# CONTEXT SCOPING INTEGRATION
# ============================================================================

def verify_pattern_scope(
    pattern: dict[str, Any],
    document_context: dict[str, Any],
    policy_area: str,
    question_id: str,
) -> tuple[bool, str | None]:
    """Verify that pattern scope matches document context.
    
    Args:
        pattern: Pattern dict with context_requirement and context_scope
        document_context: Document context dict
        policy_area: Policy area for the question
        question_id: Question ID
    
    Returns:
        Tuple of (is_valid, violation_message)
    """
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_context_scoper import (
        context_matches,
        in_scope,
    )
    
    # Check context requirement
    context_req = pattern.get("context_requirement")
    if context_req:
        if not context_matches(document_context, context_req):
            return False, f"Pattern context requirement not met: {context_req}"
    
    # Check scope
    scope = pattern.get("context_scope", "global")
    if not in_scope(document_context, scope):
        return False, f"Pattern scope '{scope}' not applicable to context"
    
    # Check policy area boundary (if pattern has policy_area specified)
    pattern_pa = pattern.get("policy_area")
    if pattern_pa and pattern_pa != policy_area:
        return False, f"Pattern belongs to {pattern_pa} but question is in {policy_area}"
    
    return True, None
