"""
Chain Layer (@chain) Configuration and Evaluator

Implements the Chain Layer evaluation for method chaining and orchestration,
ensuring proper signature validation and upstream output compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict


class ChainValidationConfig(TypedDict):
    strict_mode: bool
    allow_missing_optional: bool
    penalize_warnings: bool


@dataclass(frozen=True)
class ChainLayerConfig:
    validation_config: ChainValidationConfig
    score_missing_required: float
    score_missing_critical: float
    score_missing_optional: float
    score_warnings: float
    score_perfect: float

    def __post_init__(self) -> None:
        scores = [
            self.score_missing_required,
            self.score_missing_critical,
            self.score_missing_optional,
            self.score_warnings,
            self.score_perfect
        ]
        if not all(0.0 <= s <= 1.0 for s in scores):
            raise ValueError("All chain layer scores must be in range [0.0, 1.0]")
        
        if not (
            self.score_missing_required < self.score_missing_critical < 
            self.score_missing_optional < self.score_warnings < self.score_perfect
        ):
            raise ValueError(
                "Chain layer scores must be strictly increasing: "
                "missing_required < missing_critical < missing_optional < warnings < perfect"
            )


class MethodSignature(TypedDict):
    required_inputs: list[str]
    optional_inputs: list[str]
    critical_optional: list[str]
    output_type: str
    output_range: list[float] | None


class UpstreamOutputs(TypedDict):
    available_outputs: set[str]
    output_types: dict[str, str]


class ChainValidationResult(TypedDict):
    score: float
    validation_status: str
    missing_required: list[str]
    missing_critical: list[str]
    missing_optional: list[str]
    warnings: list[str]
    available_ratio: float


class ChainLayerEvaluator:
    def __init__(self, config: ChainLayerConfig):
        self.config = config

    def validate_signature_against_upstream(
        self,
        method_signature: MethodSignature,
        upstream_outputs: UpstreamOutputs
    ) -> ChainValidationResult:
        required = set(method_signature.get("required_inputs", []))
        optional = set(method_signature.get("optional_inputs", []))
        critical_optional = set(method_signature.get("critical_optional", []))
        available = upstream_outputs["available_outputs"]

        missing_required = list(required - available)
        missing_critical = list(critical_optional - available)
        missing_optional = list((optional - critical_optional) - available)
        warnings = []

        if missing_required:
            score = self.config.score_missing_required
            status = "failed_missing_required"
        elif missing_critical:
            score = self.config.score_missing_critical
            status = "failed_missing_critical"
        elif missing_optional and not self.config.validation_config["allow_missing_optional"]:
            score = self.config.score_missing_optional
            status = "passed_missing_optional"
            warnings.append(f"Missing {len(missing_optional)} optional inputs")
        else:
            score = self.config.score_perfect
            status = "perfect"

        output_types = upstream_outputs.get("output_types", {})
        for inp in required | critical_optional:
            if inp in available:
                expected_type = None
                if inp in output_types:
                    actual_type = output_types[inp]
                    if expected_type and actual_type != expected_type:
                        warnings.append(
                            f"Type mismatch for '{inp}': expected {expected_type}, got {actual_type}"
                        )
                        if status == "perfect":
                            status = "passed_with_warnings"
                            score = self.config.score_warnings

        if status == "perfect" and warnings:
            status = "passed_with_warnings"
            score = self.config.score_warnings

        total_inputs = len(required) + len(optional)
        if total_inputs > 0:
            available_count = len((required | optional) & available)
            available_ratio = available_count / total_inputs
        else:
            available_ratio = 1.0

        return ChainValidationResult(
            score=score,
            validation_status=status,
            missing_required=missing_required,
            missing_critical=missing_critical,
            missing_optional=missing_optional,
            warnings=warnings,
            available_ratio=available_ratio
        )

    def evaluate(
        self,
        method_signature: MethodSignature,
        upstream_outputs: UpstreamOutputs
    ) -> dict[str, Any]:
        result = self.validate_signature_against_upstream(
            method_signature, upstream_outputs
        )

        return {
            "chain_score": result["score"],
            "validation_status": result["validation_status"],
            "missing_required": result["missing_required"],
            "missing_critical": result["missing_critical"],
            "missing_optional": result["missing_optional"],
            "warnings": result["warnings"],
            "available_ratio": result["available_ratio"],
            "config": {
                "strict_mode": self.config.validation_config["strict_mode"],
                "allow_missing_optional": self.config.validation_config["allow_missing_optional"],
                "penalize_warnings": self.config.validation_config["penalize_warnings"]
            },
            "score_thresholds": {
                "missing_required": self.config.score_missing_required,
                "missing_critical": self.config.score_missing_critical,
                "missing_optional": self.config.score_missing_optional,
                "warnings": self.config.score_warnings,
                "perfect": self.config.score_perfect
            }
        }

    def evaluate_chain_sequence(
        self,
        method_signatures: list[tuple[str, MethodSignature]],
        initial_inputs: set[str]
    ) -> dict[str, Any]:
        available_outputs = initial_inputs.copy()
        output_types: dict[str, str] = {}
        sequence_results: list[dict[str, Any]] = []

        for method_id, signature in method_signatures:
            upstream = UpstreamOutputs(
                available_outputs=available_outputs,
                output_types=output_types
            )
            
            result = self.validate_signature_against_upstream(signature, upstream)
            
            sequence_results.append({
                "method_id": method_id,
                "score": result["score"],
                "status": result["validation_status"],
                "missing_required": result["missing_required"],
                "missing_critical": result["missing_critical"],
                "warnings": result["warnings"]
            })

            if result["validation_status"] != "failed_missing_required":
                output_name = method_id.split(".")[-1]
                available_outputs.add(output_name)
                output_types[output_name] = signature.get("output_type", "Any")

        if sequence_results:
            total_score = sum(r["score"] for r in sequence_results) / len(sequence_results)
        else:
            total_score = 0.0
        failed_count = sum(1 for r in sequence_results if "failed" in r["status"])
        
        return {
            "sequence_score": total_score,
            "method_results": sequence_results,
            "failed_methods": failed_count,
            "total_methods": len(method_signatures),
            "final_available_outputs": list(available_outputs)
        }


def create_default_chain_config() -> ChainLayerConfig:
    return ChainLayerConfig(
        validation_config={
            "strict_mode": False,
            "allow_missing_optional": True,
            "penalize_warnings": True
        },
        score_missing_required=0.0,
        score_missing_critical=0.3,
        score_missing_optional=0.6,
        score_warnings=0.8,
        score_perfect=1.0
    )


__all__ = [
    "ChainLayerConfig",
    "ChainValidationConfig",
    "MethodSignature",
    "UpstreamOutputs",
    "ChainValidationResult",
    "ChainLayerEvaluator",
    "create_default_chain_config"
]
