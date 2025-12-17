"""
Congruence Layer (@C) Configuration and Evaluator

Implements the Congruence Layer evaluation for method calibration,
measuring output range compatibility, semantic tag alignment, and fusion rule validity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict


class CongruenceRequirements(TypedDict):
    require_output_range_compatibility: bool
    require_semantic_alignment: bool
    require_fusion_validity: bool


class CongruenceThresholds(TypedDict):
    min_jaccard_similarity: float
    max_range_mismatch_ratio: float
    min_fusion_validity_score: float


@dataclass(frozen=True)
class CongruenceLayerConfig:
    w_scale: float
    w_semantic: float
    w_fusion: float
    requirements: CongruenceRequirements
    thresholds: CongruenceThresholds

    def __post_init__(self) -> None:
        total = self.w_scale + self.w_semantic + self.w_fusion
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Congruence layer weights must sum to 1.0, got {total}"
            )
        if self.w_scale < 0 or self.w_semantic < 0 or self.w_fusion < 0:
            raise ValueError("Congruence layer weights must be non-negative")


class OutputRangeSpec(TypedDict):
    min: float
    max: float
    output_type: str


class SemanticTagSet(TypedDict):
    tags: set[str]
    description: str | None


class FusionRule(TypedDict):
    rule_type: str
    operator: str
    is_valid: bool
    description: str | None


class CongruenceLayerEvaluator:
    def __init__(self, config: CongruenceLayerConfig):
        self.config = config

    def evaluate_output_scale_compatibility(
        self, current_range: OutputRangeSpec, upstream_range: OutputRangeSpec
    ) -> float:
        if current_range["output_type"] != upstream_range["output_type"]:
            return 0.0

        curr_min, curr_max = current_range["min"], current_range["max"]
        up_min, up_max = upstream_range["min"], upstream_range["max"]

        curr_span = curr_max - curr_min
        up_span = up_max - up_min

        if curr_span == 0 or up_span == 0:
            return 0.0

        overlap_min = max(curr_min, up_min)
        overlap_max = min(curr_max, up_max)

        if overlap_min >= overlap_max:
            return 0.0

        overlap_span = overlap_max - overlap_min
        max_span = max(curr_span, up_span)
        compatibility = overlap_span / max_span

        mismatch_ratio = abs(curr_span - up_span) / max_span
        threshold = self.config.thresholds["max_range_mismatch_ratio"]
        
        if mismatch_ratio > threshold:
            compatibility *= (1.0 - (mismatch_ratio - threshold))

        return max(0.0, min(1.0, compatibility))

    def evaluate_semantic_alignment(
        self, current_tags: SemanticTagSet, upstream_tags: SemanticTagSet
    ) -> float:
        curr_set = current_tags["tags"]
        up_set = upstream_tags["tags"]

        if not curr_set or not up_set:
            return 0.0

        intersection = len(curr_set & up_set)
        union = len(curr_set | up_set)

        if union == 0:
            return 0.0

        jaccard_similarity = intersection / union

        threshold = self.config.thresholds["min_jaccard_similarity"]
        
        if jaccard_similarity < threshold:
            return 0.0
        
        return jaccard_similarity

    def evaluate_fusion_rule_validity(
        self, fusion_rule: FusionRule, context: dict[str, Any] | None = None
    ) -> float:
        if not fusion_rule["is_valid"]:
            return 0.0

        rule_type = fusion_rule["rule_type"].lower()
        operator = fusion_rule["operator"].lower()

        valid_operators = {
            "aggregation": {"sum", "avg", "weighted_avg", "max", "min", "choquet"},
            "combination": {"and", "or", "product", "weighted_sum"},
            "transformation": {"normalize", "scale", "clamp", "sigmoid"},
        }

        if rule_type not in valid_operators:
            return 0.5

        if operator not in valid_operators[rule_type]:
            return 0.5

        base_score = 1.0

        if context:
            input_count = context.get("input_count", 0)
            if input_count == 0:
                return 0.0
            
            if operator == "weighted_avg" or operator == "weighted_sum":
                weights = context.get("weights", [])
                if len(weights) != input_count:
                    base_score *= 0.7
                elif abs(sum(weights) - 1.0) > 0.01:
                    base_score *= 0.8

        threshold = self.config.thresholds["min_fusion_validity_score"]
        if base_score < threshold:
            return 0.0

        return base_score

    def evaluate(
        self,
        current_range: OutputRangeSpec,
        upstream_range: OutputRangeSpec,
        current_tags: SemanticTagSet,
        upstream_tags: SemanticTagSet,
        fusion_rule: FusionRule,
        fusion_context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        c_scale = self.evaluate_output_scale_compatibility(current_range, upstream_range)
        c_sem = self.evaluate_semantic_alignment(current_tags, upstream_tags)
        c_fusion = self.evaluate_fusion_rule_validity(fusion_rule, fusion_context)

        c_play = c_scale * c_sem * c_fusion

        return {
            "C_play": c_play,
            "c_scale": c_scale,
            "c_sem": c_sem,
            "c_fusion": c_fusion,
            "weights": {
                "w_scale": self.config.w_scale,
                "w_semantic": self.config.w_semantic,
                "w_fusion": self.config.w_fusion
            },
            "thresholds": self.config.thresholds
        }


def create_default_congruence_config() -> CongruenceLayerConfig:
    return CongruenceLayerConfig(
        w_scale=0.4,
        w_semantic=0.35,
        w_fusion=0.25,
        requirements={
            "require_output_range_compatibility": True,
            "require_semantic_alignment": True,
            "require_fusion_validity": True
        },
        thresholds={
            "min_jaccard_similarity": 0.3,
            "max_range_mismatch_ratio": 0.5,
            "min_fusion_validity_score": 0.6
        }
    )


__all__ = [
    "CongruenceLayerConfig",
    "CongruenceRequirements",
    "CongruenceThresholds",
    "OutputRangeSpec",
    "SemanticTagSet",
    "FusionRule",
    "CongruenceLayerEvaluator",
    "create_default_congruence_config"
]
