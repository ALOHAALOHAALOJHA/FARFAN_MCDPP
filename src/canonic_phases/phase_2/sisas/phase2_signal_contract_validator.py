"""
Module: src.canonic_phases.phase_2.sisas.phase2_signal_contract_validator
Purpose: Validate signal definitions against contracts
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - SignalSchemaContract: Signals must conform to expected schema
    - SignalQualityContract: Signals must meet minimum quality standards

Determinism:
    Seed-Strategy: NOT_APPLICABLE
    State-Management: Stateless validation

Inputs:
    - signal: Dict[str, Any] — Signal definition to validate

Outputs:
    - is_valid: bool — Whether signal passes validation
    - violations: List[str] — List of validation violations

Failure-Modes:
    - SchemaViolation: ValueError — Signal doesn't match schema
    - QualityViolation: ValueError — Signal quality below threshold
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


class SignalContractValidator:
    """
    Validates signal definitions against Phase 2 contracts.
    
    SUCCESS_CRITERIA: All signal validations completed
    FAILURE_MODES: [SchemaViolation, QualityViolation]
    TERMINATION_CONDITION: All checks completed
    CONVERGENCE_RULE: N/A (single-pass validation)
    VERIFICATION_STRATEGY: Schema and quality threshold checks
    """
    
    def __init__(self) -> None:
        """Initialize signal contract validator."""
        self.required_fields = {"signal_id", "signal_type", "schema", "quality_score"}
        self.min_quality_score = 0.70
    
    def validate_signal(
        self,
        signal: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate a signal definition.
        
        Args:
            signal: Signal definition dictionary
        
        Returns:
            Tuple of (is_valid, violations)
        """
        violations: List[str] = []
        
        # Check required fields
        missing_fields = self.required_fields - set(signal.keys())
        if missing_fields:
            violations.append(f"Missing required fields: {missing_fields}")
        
        # Check quality score
        quality_score = signal.get("quality_score", 0.0)
        if quality_score < self.min_quality_score:
            violations.append(
                f"Quality score {quality_score} below minimum {self.min_quality_score}"
            )
        
        # Check signal_id format
        signal_id = signal.get("signal_id", "")
        if not signal_id or not isinstance(signal_id, str):
            violations.append("Invalid signal_id format")
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def validate_signals_batch(
        self,
        signals: List[Dict[str, Any]]
    ) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate a batch of signal definitions.
        
        Args:
            signals: List of signal definitions
        
        Returns:
            Dictionary mapping signal_id to (is_valid, violations)
        """
        results = {}
        for signal in signals:
            signal_id = signal.get("signal_id", "unknown")
            results[signal_id] = self.validate_signal(signal)
        return results
