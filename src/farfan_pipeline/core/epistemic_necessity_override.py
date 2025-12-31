"""
Epistemic Necessity Override for Method Selection

Specification Source: episte_refact.md Section 2.2 (Epistemic Minima)
Purpose: Override score threshold for epistemically necessary methods

This module implements the epistemic necessity override logic, ensuring that
methods which are epistemically required for a given TYPE are included
regardless of their score threshold.

Author: F.A.R.F.A.N Epistemic Remediation Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# Default thresholds
SCORE_THRESHOLD = 0.4
EPISTEMIC_THRESHOLD = 0.3


class EpistemicNecessitySelector:
    """
    Selects methods with epistemic necessity override.

    Per episte_refact.md Section 2.2:
    "Certain methods are epistemically necessary for specific TYPEs.
     These MUST be included regardless of score threshold."
    """

    def __init__(
        self,
        config_path: str | None = None,
        score_threshold: float = SCORE_THRESHOLD,
        epistemic_threshold: float = EPISTEMIC_THRESHOLD
    ):
        """
        Initialize selector with configuration.

        Args:
            config_path: Path to epistemic_minima_by_type.json
            score_threshold: Default score threshold for non-mandatory methods
            epistemic_threshold: Threshold for mandatory pattern matching
        """
        if config_path is None:
            config_path = str(
                Path(__file__).parent.parent.parent / "artifacts" / "data" / "methods" / "epistemic_minima_by_type.json"
            )

        self.score_threshold = score_threshold
        self.epistemic_threshold = epistemic_threshold

        # Load epistemic minima configuration
        try:
            with open(config_path, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            self.config = {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config: {e}")
            self.config = {}

        self.logger = logging.getLogger(self.__class__.__name__)

    def select_with_epistemic_override(
        self,
        candidates: list[dict],
        question_type: str,
        layer: str
    ) -> list[dict]:
        """
        Select methods with epistemic necessity override.

        Args:
            candidates: List of candidate methods with scores
            question_type: TYPE_A, TYPE_B, TYPE_C, TYPE_D, or TYPE_E
            layer: N1, N2, or N3

        Returns:
            List of selected methods with epistemic necessity applied
        """
        if not candidates:
            return []

        # Get type requirements
        type_spec = self.config.get("type_specifications", {}).get(question_type, {})
        mandatory_patterns = type_spec.get("mandatory_patterns", {}).get(layer, [])
        forced_inclusions = type_spec.get("epistemic_necessity_override", {}).get("forced_inclusions", [])

        selected = []
        selection_log = []

        for candidate in candidates:
            method_id = candidate.get("method_id", "")
            score = candidate.get("score", 0.0)

            # Priority 1: Check if method matches forced inclusion pattern
            if any(re.search(pattern, method_id, re.IGNORECASE) for pattern in forced_inclusions):
                selected.append({
                    **candidate,
                    "selection_reason": "epistemic_necessity_override",
                    "effective_score": 1.0,
                    "layer": layer,
                    "necessity_type": "forced_inclusion"
                })
                selection_log.append({
                    "method": method_id,
                    "reason": "forced_inclusion",
                    "original_score": score,
                    "effective_score": 1.0
                })
                continue

            # Priority 2: Check if method matches mandatory pattern
            if any(re.search(pattern, method_id, re.IGNORECASE) for pattern in mandatory_patterns):
                if score >= self.epistemic_threshold:
                    selected.append({
                        **candidate,
                        "selection_reason": "mandatory_pattern_match",
                        "effective_score": max(score, 0.8),  # Boost to ensure selection
                        "layer": layer,
                        "necessity_type": "mandatory_pattern"
                    })
                    selection_log.append({
                        "method": method_id,
                        "reason": "mandatory_pattern",
                        "original_score": score,
                        "effective_score": max(score, 0.8)
                    })
                else:
                    self.logger.warning(
                        f"Method {method_id} matches mandatory pattern but score {score:.3f} "
                        f"below epistemic threshold {self.epistemic_threshold}"
                    )
                continue

            # Priority 3: Check if method meets standard score threshold
            if score >= self.score_threshold:
                selected.append({
                    **candidate,
                    "selection_reason": "score_threshold",
                    "effective_score": score,
                    "layer": layer,
                    "necessity_type": "standard"
                })
                selection_log.append({
                    "method": method_id,
                    "reason": "score_threshold",
                    "original_score": score,
                    "effective_score": score
                })

        # Sort by effective score (descending)
        selected.sort(key=lambda m: m.get("effective_score", 0), reverse=True)

        self.logger.info(
            f"Selected {len(selected)} methods for TYPE_{question_type} {layer} "
            f"(epistemic override active: {sum(1 for s in selected if s.get('necessity_type') in ['forced_inclusion', 'mandatory_pattern'])} forced)"
        )

        return selected

    def enforce_layer_ratio(
        self,
        selected_by_layer: dict[str, list],
        question_type: str
    ) -> dict[str, list]:
        """
        Enforce TYPE-specific layer ratios.

        Per episte_refact.md Section 1.1, each TYPE has expected layer ratios.
        If actual ratios deviate significantly, log warnings and potentially regenerate.

        Args:
            selected_by_layer: Dict mapping layer to list of selected methods
            question_type: TYPE_A, TYPE_B, TYPE_C, TYPE_D, or TYPE_E

        Returns:
            Adjusted selected methods by layer
        """
        type_spec = self.config.get("type_specifications", {}).get(question_type, {})
        expected_ratios = type_spec.get("expected_layer_ratio", {})

        total_methods = sum(len(methods) for methods in selected_by_layer.values())

        if total_methods == 0:
            return selected_by_layer

        actual_ratios = {}
        for layer in ["N1_EMP", "N2_INF", "N3_AUD"]:
            count = len(selected_by_layer.get(layer, []))
            actual_ratios[layer] = count / total_methods if total_methods > 0 else 0.0

        # Check each layer against expected range
        warnings = []
        for layer, expected in expected_ratios.items():
            actual = actual_ratios.get(layer, 0.0)
            min_ratio = expected.get("min", 0.0)
            max_ratio = expected.get("max", 1.0)

            if actual < min_ratio:
                warnings.append(
                    f"TYPE_{question_type}: {layer} ratio {actual:.2%} below minimum {min_ratio:.2%}"
                )
            elif actual > max_ratio:
                warnings.append(
                    f"TYPE_{question_type}: {layer} ratio {actual:.2%} above maximum {max_ratio:.2%}"
                )

        if warnings:
            self.logger.warning("Layer ratio violations detected:")
            for warning in warnings:
                self.logger.warning(f"  - {warning}")

        return selected_by_layer

    def apply_diversity_adjustment(
        self,
        candidates: list[dict],
        question_type: str
    ) -> list[dict]:
        """
        Apply score adjustments based on TYPE-specific preferences.

        Per diversity_constraints.json:
        Methods matching TYPE-preferred patterns get score boost.
        Methods matching TYPE-excluded patterns get score penalty.

        Args:
            candidates: List of candidate methods
            question_type: TYPE_A, TYPE_B, TYPE_C, TYPE_D, or TYPE_E

        Returns:
            Candidates with adjusted scores
        """
        # Load diversity constraints
        diversity_path = Path(
            Path(__file__).parent.parent.parent / "artifacts" / "data" / "methods" / "diversity_constraints.json"
        )

        try:
            with open(diversity_path, "r") as f:
                diversity_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.logger.warning("Could not load diversity constraints - skipping diversity adjustment")
            return candidates

        type_profile = diversity_config.get("type_method_profiles", {}).get(question_type, {})

        adjusted = []
        for candidate in candidates:
            method_id = candidate.get("method_id", "")
            base_score = candidate.get("score", 0.0)

            # Check each layer's preferences
            adjusted_score = base_score
            for layer in ["n1", "n2", "n3"]:
                layer_key = f"preferred_{layer}_methods"
                if layer_key not in type_profile:
                    continue

                preferred = type_profile[layer_key].get("patterns", [])
                excluded = type_profile[layer_key].get("excluded_patterns", [])

                # Check excluded patterns (score = 0)
                if any(re.search(pattern, method_id, re.IGNORECASE) for pattern in excluded):
                    adjusted_score = 0.0
                    break

                # Check preferred patterns (score boost)
                if any(re.search(pattern, method_id, re.IGNORECASE) for pattern in preferred):
                    adjusted_score = base_score * 1.2  # 20% boost
                    break

            adjusted.append({
                **candidate,
                "score": adjusted_score,
                "original_score": base_score
            })

        return adjusted

    def validate_fusion_strategy(
        self,
        methods: list[dict],
        question_type: str
    ) -> dict:
        """
        Validate fusion strategy matches TYPE specification.

        Args:
            methods: List of selected methods
            question_type: TYPE_A, TYPE_B, TYPE_C, TYPE_D, or TYPE_E

        Returns:
            Validation result with any violations
        """
        # Load fusion strategy validation config
        fusion_path = Path(
            Path(__file__).parent.parent.parent / "artifacts" / "data" / "methods" / "fusion_strategy_validation.json"
        )

        try:
            with open(fusion_path, "r") as f:
                fusion_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"valid": True, "violations": []}

        type_strategy = fusion_config.get("type_fusion_strategies", {}).get(question_type, {})
        prohibited = type_strategy.get("prohibited_combinations", [])

        violations = []
        for method in methods:
            layer = method.get("layer", "")
            merge_behavior = method.get("merge_behavior", "concat")

            for prohibited_item in prohibited:
                if prohibited_item["layer"] == layer and prohibited_item["merge"] == merge_behavior:
                    violations.append({
                        "method": method.get("method_id", ""),
                        "layer": layer,
                        "merge_behavior": merge_behavior,
                        "rationale": prohibited_item.get("rationale", ""),
                        "correction": f"Use {type_strategy.get(f'{layer}_strategy', 'unknown')} instead"
                    })

        return {
            "valid": len(violations) == 0,
            "violations": violations
        }


def select_methods_with_necessity(
    candidates: list[dict],
    question_type: str,
    config_path: str | None = None
) -> dict[str, list]:
    """
    High-level function to select methods with epistemic necessity override.

    Args:
        candidates: All candidate methods with scores
        question_type: TYPE_A, TYPE_B, TYPE_C, TYPE_D, or TYPE_E
        config_path: Optional path to config files

    Returns:
        Dict mapping layer to list of selected methods
    """
    selector = EpistemicNecessitySelector(config_path)

    # Apply diversity adjustment first
    candidates = selector.apply_diversity_adjustment(candidates, question_type)

    # Group by layer
    candidates_by_layer = {}
    for candidate in candidates:
        layer = candidate.get("layer", "")
        if layer not in candidates_by_layer:
            candidates_by_layer[layer] = []
        candidates_by_layer[layer].append(candidate)

    # Select with epistemic override for each layer
    selected_by_layer = {}
    for layer, layer_candidates in candidates_by_layer.items():
        # Extract layer name (N1-EMP -> N1, etc.)
        layer_short = layer.split("-")[0]
        selected = selector.select_with_epistemic_override(
            layer_candidates, question_type, layer_short
        )
        selected_by_layer[layer] = selected

    # Enforce layer ratios
    selected_by_layer = selector.enforce_layer_ratio(selected_by_layer, question_type)

    # Validate fusion strategies
    all_methods = []
    for methods in selected_by_layer.values():
        all_methods.extend(methods)

    fusion_validation = selector.validate_fusion_strategy(all_methods, question_type)

    if not fusion_validation["valid"]:
        logger.warning("Fusion strategy validation failed:")
        for violation in fusion_validation["violations"]:
            logger.warning(f"  - {violation}")

    return selected_by_layer


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Select methods with epistemic necessity override"
    )
    parser.add_argument("candidates_file", type=str, help="Path to candidates JSON")
    parser.add_argument("question_type", type=str, help="TYPE_A, TYPE_B, TYPE_C, TYPE_D, or TYPE_E")
    parser.add_argument("--output", type=str, help="Output file for selected methods")

    args = parser.parse_args()

    with open(args.candidates_file, "r") as f:
        candidates = json.load(f)

    result = select_methods_with_necessity(candidates, args.question_type)

    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)
