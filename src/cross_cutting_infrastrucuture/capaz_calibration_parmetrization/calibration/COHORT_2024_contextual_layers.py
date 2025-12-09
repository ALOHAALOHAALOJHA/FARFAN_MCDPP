"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

Contextual Layer Evaluators (@q, @d, @p)

Implements compatibility-based evaluation for the three contextual layers:
- @q: Question compatibility
- @d: Dimension compatibility
- @p: Policy area compatibility

Priority mapping:
- Priority 3 (CRÍTICO) → 1.0
- Priority 2 (IMPORTANTE) → 0.7
- Priority 1 (COMPLEMENTARIO) → 0.3
- Unmapped methods → 0.1 (penalty)

Anti-Universality Theorem enforcement: No method can score >0.9 across all contexts.
"""

import json
from pathlib import Path
from typing import Any, TypedDict

QUESTION_LAYER_METADATA = {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "layer_symbol": "@q",
    "layer_name": "Question Contextual Layer",
    "implementation_status": "complete",
    "formula": "q_score = registry.evaluate_question(method_id, question_id)",
    "description": "Evaluates method compatibility with specific questionnaire items",
    "registry": {
        "type": "CompatibilityRegistry",
        "config_file": "COHORT_2024_method_compatibility.json",
        "shared_across_layers": True
    },
    "priority_mapping": {
        "CRÍTICO": 1.0,
        "IMPORTANTE": 0.7,
        "COMPLEMENTARIO": 0.3,
        "formula": "priority_3 → 1.0, priority_2 → 0.7, priority_1 → 0.3"
    },
    "unmapped_penalty": 0.1,
    "anti_universality_threshold": 0.9,
    "anti_universality_theorem": (
        "No method can score >0.9 across all questions, dimensions, and policies simultaneously"
    ),
    "context_scope": {
        "id_format": "Q001-Q300",
        "total_questions": 300,
        "examples": ["Q001", "Q031", "Q091"]
    },
    "evaluation_contract": {
        "method": "evaluate_question",
        "args": ["method_id: str", "question_id: str"],
        "returns": "float [0.0-1.0]",
        "unmapped_behavior": "Returns UNMAPPED_PENALTY (0.1) if method or question not declared"
    }
}


DIMENSION_LAYER_METADATA = {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "layer_symbol": "@d",
    "layer_name": "Dimension Contextual Layer",
    "implementation_status": "complete",
    "formula": "d_score = registry.evaluate_dimension(method_id, dimension_id)",
    "description": "Evaluates method compatibility with analytical dimensions",
    "registry": {
        "type": "CompatibilityRegistry",
        "config_file": "COHORT_2024_method_compatibility.json",
        "shared_across_layers": True
    },
    "priority_mapping": {
        "CRÍTICO": 1.0,
        "IMPORTANTE": 0.7,
        "COMPLEMENTARIO": 0.3,
        "formula": "priority_3 → 1.0, priority_2 → 0.7, priority_1 → 0.3"
    },
    "unmapped_penalty": 0.1,
    "anti_universality_threshold": 0.9,
    "anti_universality_theorem": (
        "No method can score >0.9 across all questions, dimensions, and policies simultaneously"
    ),
    "context_scope": {
        "id_format": "DIM01-DIM06",
        "total_dimensions": 6,
        "examples": ["DIM01", "DIM02", "DIM03"]
    },
    "evaluation_contract": {
        "method": "evaluate_dimension",
        "args": ["method_id: str", "dimension_id: str"],
        "returns": "float [0.0-1.0]",
        "unmapped_behavior": "Returns UNMAPPED_PENALTY (0.1) if method or dimension not declared"
    }
}


POLICY_LAYER_METADATA = {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "layer_symbol": "@p",
    "layer_name": "Policy Area Contextual Layer",
    "implementation_status": "complete",
    "formula": "p_score = registry.evaluate_policy(method_id, policy_id)",
    "description": "Evaluates method compatibility with policy areas",
    "registry": {
        "type": "CompatibilityRegistry",
        "config_file": "COHORT_2024_method_compatibility.json",
        "shared_across_layers": True
    },
    "priority_mapping": {
        "CRÍTICO": 1.0,
        "IMPORTANTE": 0.7,
        "COMPLEMENTARIO": 0.3,
        "formula": "priority_3 → 1.0, priority_2 → 0.7, priority_1 → 0.3"
    },
    "unmapped_penalty": 0.1,
    "anti_universality_threshold": 0.9,
    "anti_universality_theorem": (
        "No method can score >0.9 across all questions, dimensions, and policies simultaneously"
    ),
    "context_scope": {
        "id_format": "PA01-PA10",
        "total_policy_areas": 10,
        "examples": ["PA01", "PA02", "PA10"]
    },
    "evaluation_contract": {
        "method": "evaluate_policy",
        "args": ["method_id: str", "policy_id: str"],
        "returns": "float [0.0-1.0]",
        "unmapped_behavior": "Returns UNMAPPED_PENALTY (0.1) if method or policy not declared"
    }
}


class CompatibilityMapping(TypedDict):
    questions: dict[str, float]
    dimensions: dict[str, float]
    policies: dict[str, float]


class CompatibilityRegistry:
    """
    Registry for method compatibility scores across contextual layers.

    Loads from COHORT_2024_method_compatibility.json and provides
    evaluation methods for @q, @d, @p layers with penalty for unmapped methods.
    """

    UNMAPPED_PENALTY: float = 0.1
    ANTI_UNIVERSALITY_THRESHOLD: float = 0.9

    def __init__(self, config_path: Path | str | None = None) -> None:
        """
        Initialize registry from compatibility configuration.

        Args:
            config_path: Path to COHORT_2024_method_compatibility.json
                        If None, uses default location in calibration/
        """
        if config_path is None:
            config_path = (
                Path(__file__).parent / "COHORT_2024_method_compatibility.json"
            )
        else:
            config_path = Path(config_path)

        self._config_path = config_path
        self._compatibility_data: dict[str, CompatibilityMapping] = {}
        self._load_compatibility_data()

    def _load_compatibility_data(self) -> None:
        """Load and validate compatibility configuration from JSON."""
        if not self._config_path.exists():
            raise FileNotFoundError(
                f"Compatibility config not found: {self._config_path}"
            )

        with self._config_path.open() as f:
            data = json.load(f)

        if "_cohort_metadata" not in data:
            raise ValueError(
                f"Missing _cohort_metadata in {self._config_path}"
            )

        metadata = data["_cohort_metadata"]
        if metadata.get("cohort_id") != "COHORT_2024":
            raise ValueError(
                f"Invalid cohort_id: {metadata.get('cohort_id')} "
                f"(expected COHORT_2024)"
            )

        if "method_compatibility" not in data:
            raise ValueError(
                f"Missing method_compatibility in {self._config_path}"
            )

        self._compatibility_data = data["method_compatibility"]
        self._validate_anti_universality()

    def _validate_anti_universality(self) -> None:
        """
        Validate Anti-Universality Theorem: no method can score >0.9
        across all questions, dimensions, and policies simultaneously.
        """
        for method_id, compat in self._compatibility_data.items():
            all_contexts_high = True

            for context_type in ["questions", "dimensions", "policies"]:
                context_scores = compat.get(context_type, {})
                if not context_scores:
                    all_contexts_high = False
                    break

                max_score = max(context_scores.values())
                if max_score <= self.ANTI_UNIVERSALITY_THRESHOLD:
                    all_contexts_high = False
                    break

            if all_contexts_high:
                raise ValueError(
                    f"Anti-Universality violation: Method '{method_id}' "
                    f"has scores >0.9 across all contexts. No method can be "
                    f"universally compatible."
                )

    def evaluate_question(self, method_id: str, question_id: str) -> float:
        """
        Evaluate @q layer score for a method-question pair.

        Args:
            method_id: Method identifier
            question_id: Question ID (e.g., "Q001", "Q031")

        Returns:
            Compatibility score [0.0-1.0]
            Returns UNMAPPED_PENALTY (0.1) if method or question not declared
        """
        if method_id not in self._compatibility_data:
            return self.UNMAPPED_PENALTY

        questions = self._compatibility_data[method_id].get("questions", {})
        return questions.get(question_id, self.UNMAPPED_PENALTY)

    def evaluate_dimension(self, method_id: str, dimension_id: str) -> float:
        """
        Evaluate @d layer score for a method-dimension pair.

        Args:
            method_id: Method identifier
            dimension_id: Dimension ID (e.g., "DIM01", "DIM02")

        Returns:
            Compatibility score [0.0-1.0]
            Returns UNMAPPED_PENALTY (0.1) if method or dimension not declared
        """
        if method_id not in self._compatibility_data:
            return self.UNMAPPED_PENALTY

        dimensions = self._compatibility_data[method_id].get("dimensions", {})
        return dimensions.get(dimension_id, self.UNMAPPED_PENALTY)

    def evaluate_policy(self, method_id: str, policy_id: str) -> float:
        """
        Evaluate @p layer score for a method-policy pair.

        Args:
            method_id: Method identifier
            policy_id: Policy area ID (e.g., "PA01", "PA10")

        Returns:
            Compatibility score [0.0-1.0]
            Returns UNMAPPED_PENALTY (0.1) if method or policy not declared
        """
        if method_id not in self._compatibility_data:
            return self.UNMAPPED_PENALTY

        policies = self._compatibility_data[method_id].get("policies", {})
        return policies.get(policy_id, self.UNMAPPED_PENALTY)

    def get_method_compatibility(self, method_id: str) -> CompatibilityMapping | None:
        """
        Get full compatibility mapping for a method.

        Args:
            method_id: Method identifier

        Returns:
            CompatibilityMapping with questions/dimensions/policies,
            or None if method not in registry
        """
        return self._compatibility_data.get(method_id)

    def validate_method_universality(self, method_id: str) -> tuple[bool, str]:
        """
        Check if a method violates anti-universality constraint.

        Args:
            method_id: Method identifier

        Returns:
            Tuple of (is_valid, message)
            is_valid=False if method has >0.9 in all context types
        """
        if method_id not in self._compatibility_data:
            return True, "Method not in registry"

        compat = self._compatibility_data[method_id]

        max_scores = {}
        for context_type in ["questions", "dimensions", "policies"]:
            scores = compat.get(context_type, {})
            if scores:
                max_scores[context_type] = max(scores.values())
            else:
                max_scores[context_type] = 0.0

        all_high = all(
            score > self.ANTI_UNIVERSALITY_THRESHOLD
            for score in max_scores.values()
        )

        if all_high:
            return False, (
                f"Anti-Universality violation: Method has max scores "
                f"{max_scores} (all >0.9)"
            )

        return True, "Valid"

    def list_methods(self) -> list[str]:
        """List all methods in the compatibility registry."""
        return list(self._compatibility_data.keys())

    def get_metadata(self) -> dict[str, Any]:
        """Get cohort metadata from configuration file."""
        with self._config_path.open() as f:
            data = json.load(f)
        return data.get("_cohort_metadata", {})


class QuestionEvaluator:
    """Evaluator for @q (Question) contextual layer."""

    def __init__(self, registry: CompatibilityRegistry) -> None:
        self.registry = registry

    def evaluate(self, method_id: str, question_id: str) -> float:
        """
        Evaluate @q layer score.

        Args:
            method_id: Method identifier
            question_id: Question ID (Q001-Q300)

        Returns:
            Compatibility score [0.0-1.0]
        """
        return self.registry.evaluate_question(method_id, question_id)


class DimensionEvaluator:
    """Evaluator for @d (Dimension) contextual layer."""

    def __init__(self, registry: CompatibilityRegistry) -> None:
        self.registry = registry

    def evaluate(self, method_id: str, dimension_id: str) -> float:
        """
        Evaluate @d layer score.

        Args:
            method_id: Method identifier
            dimension_id: Dimension ID (DIM01-DIM06)

        Returns:
            Compatibility score [0.0-1.0]
        """
        return self.registry.evaluate_dimension(method_id, dimension_id)


class PolicyEvaluator:
    """Evaluator for @p (Policy) contextual layer."""

    def __init__(self, registry: CompatibilityRegistry) -> None:
        self.registry = registry

    def evaluate(self, method_id: str, policy_id: str) -> float:
        """
        Evaluate @p layer score.

        Args:
            method_id: Method identifier
            policy_id: Policy area ID (PA01-PA10)

        Returns:
            Compatibility score [0.0-1.0]
        """
        return self.registry.evaluate_policy(method_id, policy_id)


def create_contextual_evaluators(
    config_path: Path | str | None = None,
) -> tuple[QuestionEvaluator, DimensionEvaluator, PolicyEvaluator]:
    """
    Create all three contextual layer evaluators with shared registry.

    Args:
        config_path: Path to COHORT_2024_method_compatibility.json

    Returns:
        Tuple of (question_evaluator, dimension_evaluator, policy_evaluator)
    """
    registry = CompatibilityRegistry(config_path)
    return (
        QuestionEvaluator(registry),
        DimensionEvaluator(registry),
        PolicyEvaluator(registry),
    )


def get_question_metadata() -> dict[str, Any]:
    """Return COHORT metadata for Question Layer (@q)."""
    return QUESTION_LAYER_METADATA.copy()


def get_dimension_metadata() -> dict[str, Any]:
    """Return COHORT metadata for Dimension Layer (@d)."""
    return DIMENSION_LAYER_METADATA.copy()


def get_policy_metadata() -> dict[str, Any]:
    """Return COHORT metadata for Policy Layer (@p)."""
    return POLICY_LAYER_METADATA.copy()


__all__ = [
    "DIMENSION_LAYER_METADATA",
    "POLICY_LAYER_METADATA",
    "QUESTION_LAYER_METADATA",
    "CompatibilityMapping",
    "CompatibilityRegistry",
    "DimensionEvaluator",
    "PolicyEvaluator",
    "QuestionEvaluator",
    "create_contextual_evaluators",
    "get_dimension_metadata",
    "get_policy_metadata",
    "get_question_metadata",
]
