"""
Layer Assignment System for Calibration

This module defines the canonical layer requirements for all method roles
and provides layer assignment with Choquet integral weights for executors.

Layers:
- @b: Code quality (base theory)
- @chain: Method wiring/orchestration
- @q: Question appropriateness
- @d: Dimension alignment
- @p: Policy area fit
- @C: Contract compliance
- @u: Document quality
- @m: Governance maturity
"""

import re
from typing import Any

LAYER_REQUIREMENTS: dict[str, list[str]] = {
    "ingest": ["@b", "@chain", "@u", "@m"],
    "processor": ["@b", "@chain", "@u", "@m"],
    "analyzer": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
    "score": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
    "executor": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
    "utility": ["@b", "@chain", "@m"],
    "orchestrator": ["@b", "@chain", "@m"],
    "core": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
    "extractor": ["@b", "@chain", "@u", "@m"],
}

CHOQUET_WEIGHTS: dict[str, float] = {
    "@b": 0.17,
    "@chain": 0.13,
    "@q": 0.08,
    "@d": 0.07,
    "@p": 0.06,
    "@C": 0.08,
    "@u": 0.04,
    "@m": 0.04,
}

CHOQUET_INTERACTION_WEIGHTS: dict[tuple[str, str], float] = {
    ("@u", "@chain"): 0.13,
    ("@chain", "@C"): 0.10,
    ("@q", "@d"): 0.10,
}


def identify_executors(executors_file_path: str) -> list[dict[str, Any]]:
    """
    Identify all D[1-6]Q[1-5] executors from the executors.py file.

    Args:
        executors_file_path: Path to executors.py

    Returns:
        List of executor metadata dicts with method_id, role, dimension, question

    Raises:
        RuntimeError: If <30 executors found
    """
    with open(executors_file_path) as f:
        content = f.read()

    pattern = re.compile(r"class (D([1-6])_Q([1-5])_\w+)\(")
    matches = pattern.findall(content)

    executors = []
    for class_name, dim, question in matches:
        method_id = f"farfan_pipeline.core.orchestrator.executors.{class_name}"
        executors.append(
            {
                "method_id": method_id,
                "class_name": class_name,
                "dimension": f"D{dim}",
                "question": f"Q{question}",
                "role": "executor",
                "type": "analyzer",
            }
        )

    if len(executors) < 30:
        raise RuntimeError(
            f"layer assignment corrupted: Found {len(executors)} executors, expected 30"
        )

    return executors


def assign_layers_and_weights(
    method_id: str, role: str, dimension: str = None, question: str = None
) -> dict[str, Any]:
    """
    Assign layers and Choquet weights to a method based on its role.

    Args:
        method_id: Fully qualified method identifier
        role: Method role (ingest, processor, analyzer, etc.)
        dimension: Dimension ID (D1-D6) for executors
        question: Question ID (Q1-Q5) for executors

    Returns:
        Dict with layers, weights, and aggregator_type

    Raises:
        ValueError: If role not found in LAYER_REQUIREMENTS
    """
    if role not in LAYER_REQUIREMENTS:
        raise ValueError(f"Unknown role: {role}")

    layers = LAYER_REQUIREMENTS[role]

    weights = {layer: CHOQUET_WEIGHTS[layer] for layer in layers}

    interaction_weights = {}
    for (l1, l2), weight in CHOQUET_INTERACTION_WEIGHTS.items():
        if l1 in layers and l2 in layers:
            interaction_weights[f"{l1},{l2}"] = weight

    sum_linear = sum(weights.values())
    sum_interaction = sum(interaction_weights.values())
    total = sum_linear + sum_interaction

    if abs(total - 1.0) > 0.01:
        scale = 1.0 / total
        weights = {k: v * scale for k, v in weights.items()}
        interaction_weights = {k: v * scale for k, v in interaction_weights.items()}

    return {
        "method_id": method_id,
        "role": role,
        "dimension": dimension,
        "question": question,
        "layers": layers,
        "weights": weights,
        "interaction_weights": interaction_weights,
        "aggregator_type": "choquet",
    }


def generate_canonical_inventory(executors_file_path: str) -> dict[str, Any]:
    """
    Generate the canonical inventory of methods with layer assignments.

    Args:
        executors_file_path: Path to executors.py

    Returns:
        Dict with metadata for all methods (NO SCORES)

    Raises:
        RuntimeError: If any validation fails
    """
    executors = identify_executors(executors_file_path)

    inventory = {
        "_metadata": {
            "version": "1.0.0",
            "description": "Canonical layer assignments for F.A.R.F.A.N. calibration system",
            "total_executors": len(executors),
            "layer_system": {
                "@b": "Code quality (base theory)",
                "@chain": "Method wiring/orchestration",
                "@q": "Question appropriateness",
                "@d": "Dimension alignment",
                "@p": "Policy area fit",
                "@C": "Contract compliance",
                "@u": "Document quality",
                "@m": "Governance maturity",
            },
        },
        "methods": {},
    }

    for executor in executors:
        assignment = assign_layers_and_weights(
            method_id=executor["method_id"],
            role=executor["role"],
            dimension=executor["dimension"],
            question=executor["question"],
        )

        if len(assignment["layers"]) < 8:
            raise RuntimeError(
                f"layer assignment corrupted: Executor {executor['method_id']} "
                f"has {len(assignment['layers'])} layers, expected 8"
            )

        weights_sum = sum(assignment["weights"].values()) + sum(
            assignment["interaction_weights"].values()
        )
        if abs(weights_sum - 1.0) > 0.01:
            raise RuntimeError(
                f"layer assignment corrupted: Weights for {executor['method_id']} "
                f"sum to {weights_sum}, expected 1.0"
            )

        inventory["methods"][executor["method_id"]] = {
            "method_id": assignment["method_id"],
            "role": assignment["role"],
            "dimension": assignment["dimension"],
            "question": assignment["question"],
            "layers": assignment["layers"],
            "weights": assignment["weights"],
            "interaction_weights": assignment["interaction_weights"],
            "aggregator_type": assignment["aggregator_type"],
        }

    return inventory
