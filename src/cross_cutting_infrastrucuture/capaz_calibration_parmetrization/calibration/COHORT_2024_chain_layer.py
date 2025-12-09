"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

Chain Layer (@chain) Evaluator Implementation

Implements discrete scoring logic for method chain validation:
- 0.0: missing_required (hard mismatch: schema incompatible OR required input unavailable)
- 0.3: missing_critical (critical optional missing)
- 0.6: missing_optional AND many_missing (ratio>0.5) OR soft_schema_violation
- 0.8: all contracts pass AND warnings exist
- 1.0: all inputs present AND no warnings

This evaluator ensures proper method wiring and orchestration in analysis chains.
"""
from __future__ import annotations

from typing import Any, TypedDict


class ChainEvaluationResult(TypedDict):
    score: float
    reason: str
    missing_required: list[str]
    missing_critical: list[str]
    missing_optional: list[str]
    warnings: list[str]
    schema_violations: list[str]


class ChainSequenceResult(TypedDict):
    method_scores: dict[str, float]
    individual_results: dict[str, ChainEvaluationResult]
    chain_quality: float
    weakest_link: str | None


class ChainLayerEvaluator:
    """
    Evaluates method chain compatibility with discrete scoring logic.

    Scoring Logic:
        - 0.0: Hard failure (missing required input OR schema incompatible)
        - 0.3: Critical optional missing
        - 0.6: Many optional missing (>50%) OR soft schema violation
        - 0.8: All contracts pass but warnings exist
        - 1.0: Perfect (all inputs present, no warnings)

    Weakest Link Principle:
        Chain quality = min(method_scores)
    """

    def __init__(self, method_signatures: dict[str, dict[str, Any]] | None = None) -> None:
        """
        Initialize chain layer evaluator.

        Args:
            method_signatures: Optional dict mapping method_id to signature metadata
                              with required_inputs, optional_inputs, critical_optional
        """
        self.method_signatures = method_signatures or {}

    def _get_method_signature(self, method_id: str) -> dict[str, Any] | None:
        """Get method signature metadata."""
        return self.method_signatures.get(method_id)

    def _check_schema_compatibility(
        self,
        required_type: str,
        provided_type: str | None,
    ) -> tuple[bool, bool]:
        """
        Check schema compatibility between required and provided types.

        Returns:
            (is_compatible, is_soft_violation)
            - (False, False): Hard incompatibility
            - (True, True): Soft incompatibility (e.g., int vs float)
            - (True, False): Full compatibility
        """
        if provided_type is None:
            return (True, False)

        required_type = required_type.lower()
        provided_type = provided_type.lower()

        if required_type == provided_type:
            return (True, False)

        if required_type == "any" or provided_type == "any":
            return (True, False)

        soft_compatible = [
            ("int", "float"),
            ("float", "int"),
            ("list", "tuple"),
            ("tuple", "list"),
        ]

        for t1, t2 in soft_compatible:
            if (required_type == t1 and provided_type == t2) or (
                required_type == t2 and provided_type == t1
            ):
                return (True, True)

        return (False, False)

    def evaluate(
        self,
        method_id: str,
        provided_inputs: set[str],
        upstream_outputs: dict[str, str] | None = None,
    ) -> ChainEvaluationResult:
        """
        Evaluate chain compatibility for a single method.

        Args:
            method_id: Method identifier
            provided_inputs: Set of available input names
            upstream_outputs: Optional dict mapping input_name -> output_type
                            for type checking

        Returns:
            ChainEvaluationResult with score, reason, and detailed analysis
        """
        signature = self._get_method_signature(method_id)

        if signature is None:
            return ChainEvaluationResult(
                score=0.0,
                reason="missing_required: no signature found",
                missing_required=["<signature>"],
                missing_critical=[],
                missing_optional=[],
                warnings=["Method signature not found in registry"],
                schema_violations=[],
            )

        required_inputs = set(signature.get("required_inputs", []))
        optional_inputs = set(signature.get("optional_inputs", []))
        critical_optional = set(signature.get("critical_optional", []))

        missing_required = required_inputs - provided_inputs
        missing_critical = critical_optional - provided_inputs
        missing_optional = optional_inputs - provided_inputs - critical_optional

        warnings: list[str] = []
        schema_violations: list[str] = []

        if upstream_outputs:
            for inp in provided_inputs:
                if inp in upstream_outputs:
                    provided_type = upstream_outputs[inp]
                    required_type = signature.get("input_types", {}).get(inp, "Any")

                    is_compatible, is_soft = self._check_schema_compatibility(
                        required_type, provided_type
                    )

                    if not is_compatible:
                        schema_violations.append(
                            f"Hard type mismatch: {inp} requires {required_type}, got {provided_type}"
                        )
                    elif is_soft:
                        warnings.append(
                            f"Soft type mismatch: {inp} prefers {required_type}, got {provided_type}"
                        )

        if missing_required or schema_violations:
            return ChainEvaluationResult(
                score=0.0,
                reason="missing_required: hard mismatch (schema incompatible OR required input unavailable)",
                missing_required=list(missing_required),
                missing_critical=list(missing_critical),
                missing_optional=list(missing_optional),
                warnings=warnings,
                schema_violations=schema_violations,
            )

        if missing_critical:
            return ChainEvaluationResult(
                score=0.3,
                reason="missing_critical: critical optional inputs missing",
                missing_required=[],
                missing_critical=list(missing_critical),
                missing_optional=list(missing_optional),
                warnings=warnings,
                schema_violations=[],
            )

        total_optional = len(optional_inputs) - len(critical_optional)
        many_missing = (
            len(missing_optional) / total_optional > 0.5 if total_optional > 0 else False
        )

        if many_missing or warnings:
            if many_missing and warnings:
                reason = "missing_optional AND many_missing (ratio>0.5) with soft_schema_violation"
                score = 0.6
            elif many_missing:
                reason = "missing_optional AND many_missing (ratio>0.5)"
                score = 0.6
            elif warnings:
                reason = "all contracts pass AND warnings exist"
                score = 0.8
            else:
                reason = "all inputs present AND no warnings"
                score = 1.0

            return ChainEvaluationResult(
                score=score,
                reason=reason,
                missing_required=[],
                missing_critical=[],
                missing_optional=list(missing_optional),
                warnings=warnings,
                schema_violations=[],
            )

        return ChainEvaluationResult(
            score=1.0,
            reason="all inputs present AND no warnings",
            missing_required=[],
            missing_critical=[],
            missing_optional=[],
            warnings=[],
            schema_violations=[],
        )

    def validate_chain_sequence(
        self,
        method_sequence: list[str],
        initial_inputs: set[str],
        method_outputs: dict[str, set[str]] | None = None,
    ) -> ChainSequenceResult:
        """
        Validate a sequence of methods as a chain.

        Args:
            method_sequence: Ordered list of method_ids
            initial_inputs: Initial set of available inputs
            method_outputs: Optional dict mapping method_id -> set of output names

        Returns:
            ChainSequenceResult with individual scores and chain quality
        """
        method_scores: dict[str, float] = {}
        individual_results: dict[str, ChainEvaluationResult] = {}

        available_inputs = initial_inputs.copy()

        for method_id in method_sequence:
            result = self.evaluate(method_id, available_inputs)
            method_scores[method_id] = result["score"]
            individual_results[method_id] = result

            if method_outputs and method_id in method_outputs:
                available_inputs.update(method_outputs[method_id])

        chain_quality = self.compute_chain_quality(method_scores)

        weakest_link = None
        if method_scores:
            weakest_link = min(method_scores.items(), key=lambda x: x[1])[0]

        return ChainSequenceResult(
            method_scores=method_scores,
            individual_results=individual_results,
            chain_quality=chain_quality,
            weakest_link=weakest_link,
        )

    def compute_chain_quality(self, method_scores: dict[str, float]) -> float:
        """
        Compute overall chain quality using weakest link principle.

        Args:
            method_scores: Dict mapping method_id -> score

        Returns:
            Minimum score (weakest link determines chain quality)
        """
        if not method_scores:
            return 0.0
        return min(method_scores.values())


def create_evaluator_from_validator(
    validator_or_path: Any,
) -> ChainLayerEvaluator:
    """
    Create ChainLayerEvaluator from MethodSignatureValidator.

    Args:
        validator_or_path: Either MethodSignatureValidator instance or path to signatures

    Returns:
        Configured ChainLayerEvaluator
    """
    try:
        from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.method_signature_validator import (
            MethodSignatureValidator,
        )

        if isinstance(validator_or_path, str):
            validator = MethodSignatureValidator(validator_or_path)
            validator.load_signatures()
        else:
            validator = validator_or_path

        methods = validator.signatures_data.get("methods", {})
        signatures = {}

        for method_id, method_data in methods.items():
            if "signature" in method_data:
                signatures[method_id] = method_data["signature"]
            else:
                signatures[method_id] = method_data

        return ChainLayerEvaluator(signatures)

    except ImportError:
        return ChainLayerEvaluator({})


__all__ = [
    "ChainLayerEvaluator",
    "ChainEvaluationResult",
    "ChainSequenceResult",
    "create_evaluator_from_validator",
]
