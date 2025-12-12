"""Core validation functions for system integrity."""

import json
from pathlib import Path
from typing import Any, TypedDict


class ValidationResult(TypedDict):
    validator_name: str
    passed: bool
    errors: list[str]
    warnings: list[str]
    details: dict[str, Any]


def validate_boundedness(
    scores_data: dict[str, Any] | None = None,
    scores_path: str | Path | None = None,
    min_bound: float = 0.0,
    max_bound: float = 1.0,
) -> ValidationResult:
    """
    Validate that all scores are bounded in [0, 1].
    
    Checks:
    - All scores >= 0.0
    - All scores <= 1.0
    - No NaN or infinite values
    
    Args:
        scores_data: Pre-loaded scores dict (optional)
        scores_path: Path to scores file (optional)
        min_bound: Minimum allowed score (default: 0.0)
        max_bound: Maximum allowed score (default: 1.0)
    """
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {
        "total_scores_checked": 0,
        "out_of_bounds_scores": [],
        "invalid_values": [],
        "min_bound": min_bound,
        "max_bound": max_bound,
    }

    try:
        if scores_data is None and scores_path is None:
            warnings.append(
                "No scores data or path provided. Skipping boundedness check."
            )
            return ValidationResult(
                validator_name="validate_boundedness",
                passed=True,
                errors=errors,
                warnings=warnings,
                details=details,
            )

        if scores_data is None and scores_path is not None:
            scores_path = Path(scores_path)
            if not scores_path.exists():
                errors.append(f"Scores file not found: {scores_path}")
                return ValidationResult(
                    validator_name="validate_boundedness",
                    passed=False,
                    errors=errors,
                    warnings=warnings,
                    details=details,
                )
            with open(scores_path) as f:
                scores_data = json.load(f)

        if not scores_data or not isinstance(scores_data, dict):
            warnings.append("Empty or invalid scores data structure")
            return ValidationResult(
                validator_name="validate_boundedness",
                passed=True,
                errors=errors,
                warnings=warnings,
                details=details,
            )

        def check_value(value: Any, path: str) -> None:
            if isinstance(value, (int, float)):
                details["total_scores_checked"] += 1

                if value != value:
                    errors.append(f"NaN value at {path}")
                    details["invalid_values"].append({"path": path, "value": "NaN"})
                    return

                if value == float("inf") or value == float("-inf"):
                    errors.append(f"Infinite value at {path}")
                    details["invalid_values"].append(
                        {"path": path, "value": str(value)}
                    )
                    return

                if value < min_bound:
                    errors.append(
                        f"Score below minimum at {path}: {value} < {min_bound}"
                    )
                    details["out_of_bounds_scores"].append(
                        {"path": path, "value": value, "violation": "below_minimum"}
                    )

                if value > max_bound:
                    errors.append(
                        f"Score above maximum at {path}: {value} > {max_bound}"
                    )
                    details["out_of_bounds_scores"].append(
                        {"path": path, "value": value, "violation": "above_maximum"}
                    )

        def traverse(obj: Any, path: str = "root") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.startswith("_"):
                        continue
                    traverse(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    traverse(item, f"{path}[{i}]")
            else:
                check_value(obj, path)

        traverse(scores_data)

        passed = len(errors) == 0

    except Exception as e:
        errors.append(f"Exception during validation: {str(e)}")
        passed = False

    return ValidationResult(
        validator_name="validate_boundedness",
        passed=passed,
        errors=errors,
        warnings=warnings,
        details=details,
    )
