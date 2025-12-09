"""Core validation functions for calibration system integrity."""

import json
from pathlib import Path
from typing import Any, TypedDict


class ValidationResult(TypedDict):
    validator_name: str
    passed: bool
    errors: list[str]
    warnings: list[str]
    details: dict[str, Any]


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


def validate_layer_completeness(
    inventory_path: str | Path = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_canonical_method_inventory.json",
    layer_assignment_path: str | Path = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_layer_assignment.py",
) -> ValidationResult:
    """
    Validate that all methods have required layers per role.
    
    Checks:
    - All methods have 'layers' field
    - Layers match role requirements from LAYER_REQUIREMENTS
    - No missing required layers for role
    """
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {
        "total_methods_checked": 0,
        "methods_with_incomplete_layers": [],
        "methods_missing_layer_field": [],
    }

    try:
        inventory_path = Path(inventory_path)
        if not inventory_path.exists():
            errors.append(f"Inventory file not found: {inventory_path}")
            return ValidationResult(
                validator_name="validate_layer_completeness",
                passed=False,
                errors=errors,
                warnings=warnings,
                details=details,
            )

        with open(inventory_path) as f:
            data = json.load(f)

        methods = data.get("methods", {})
        if isinstance(methods, dict) and "_note" in methods:
            warnings.append(
                "Inventory contains reference stub. Check if full inventory needs loading."
            )
            return ValidationResult(
                validator_name="validate_layer_completeness",
                passed=True,
                errors=errors,
                warnings=warnings,
                details={"note": "Stub file detected, skipping detailed validation"},
            )

        details["total_methods_checked"] = len(methods)

        for method_id, method_data in methods.items():
            if "layers" not in method_data:
                errors.append(f"Method {method_id} missing 'layers' field")
                details["methods_missing_layer_field"].append(method_id)
                continue

            role = method_data.get("role", "unknown")
            if role not in LAYER_REQUIREMENTS:
                warnings.append(f"Unknown role '{role}' for method {method_id}")
                continue

            required_layers = set(LAYER_REQUIREMENTS[role])
            actual_layers = set(method_data["layers"])
            missing_layers = required_layers - actual_layers

            if missing_layers:
                errors.append(
                    f"Method {method_id} (role={role}) missing layers: {missing_layers}"
                )
                details["methods_with_incomplete_layers"].append(
                    {
                        "method_id": method_id,
                        "role": role,
                        "missing_layers": list(missing_layers),
                    }
                )

        passed = len(errors) == 0

    except Exception as e:
        errors.append(f"Exception during validation: {str(e)}")
        passed = False

    return ValidationResult(
        validator_name="validate_layer_completeness",
        passed=passed,
        errors=errors,
        warnings=warnings,
        details=details,
    )


def validate_fusion_weights(
    fusion_weights_path: str | Path = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_fusion_weights.json",
    tolerance: float = 1e-9,
) -> ValidationResult:
    """
    Validate fusion weights normalization.
    
    Checks:
    - Linear weights sum + interaction weights sum = 1.0 ± tolerance
    - All weights are non-negative
    - Proper structure and keys present
    """
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {
        "linear_sum": 0.0,
        "interaction_sum": 0.0,
        "total_sum": 0.0,
        "tolerance": tolerance,
        "negative_weights": [],
    }

    try:
        fusion_weights_path = Path(fusion_weights_path)
        if not fusion_weights_path.exists():
            errors.append(f"Fusion weights file not found: {fusion_weights_path}")
            return ValidationResult(
                validator_name="validate_fusion_weights",
                passed=False,
                errors=errors,
                warnings=warnings,
                details=details,
            )

        with open(fusion_weights_path) as f:
            data = json.load(f)

        if "_reference_note" in data:
            role_params = data.get("role_fusion_parameters", {})
            if "_note" in role_params:
                warnings.append(
                    "Fusion weights contains reference stub. Full validation may require original file."
                )
                return ValidationResult(
                    validator_name="validate_fusion_weights",
                    passed=True,
                    errors=errors,
                    warnings=warnings,
                    details={"note": "Stub file detected, skipping detailed validation"},
                )

        linear_weights = data.get("linear_weights", {})
        interaction_weights = data.get("interaction_weights", {})

        if not linear_weights:
            errors.append("No linear_weights found in fusion weights file")

        linear_sum = sum(float(v) for v in linear_weights.values())
        interaction_sum = sum(float(v) for v in interaction_weights.values())
        total_sum = linear_sum + interaction_sum

        details["linear_sum"] = linear_sum
        details["interaction_sum"] = interaction_sum
        details["total_sum"] = total_sum

        if abs(total_sum - 1.0) > tolerance:
            errors.append(
                f"Fusion weights sum to {total_sum}, expected 1.0 ± {tolerance}"
            )

        for key, value in linear_weights.items():
            if float(value) < 0:
                errors.append(f"Negative linear weight: {key} = {value}")
                details["negative_weights"].append({"type": "linear", "key": key, "value": value})

        for key, value in interaction_weights.items():
            if float(value) < 0:
                errors.append(f"Negative interaction weight: {key} = {value}")
                details["negative_weights"].append(
                    {"type": "interaction", "key": key, "value": value}
                )

        validation_info = data.get("validation", {})
        if validation_info:
            expected_total = validation_info.get("total_sum", 1.0)
            if abs(expected_total - 1.0) > tolerance:
                warnings.append(
                    f"Validation metadata shows total_sum={expected_total}, expected 1.0"
                )

        passed = len(errors) == 0

    except Exception as e:
        errors.append(f"Exception during validation: {str(e)}")
        passed = False

    return ValidationResult(
        validator_name="validate_fusion_weights",
        passed=passed,
        errors=errors,
        warnings=warnings,
        details=details,
    )


def validate_anti_universality(
    scores_data: dict[str, Any] | None = None,
    scores_path: str | Path | None = None,
) -> ValidationResult:
    """
    Validate anti-universality: no method should be maximal everywhere.
    
    Checks:
    - No single method has maximum score across all dimensions/questions
    - Methods show variation across contexts
    - No method dominates all others universally
    
    Args:
        scores_data: Pre-loaded scores dict (optional)
        scores_path: Path to scores file (optional, used if scores_data not provided)
    """
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {
        "methods_checked": 0,
        "universal_methods": [],
        "max_score_contexts": {},
    }

    try:
        if scores_data is None and scores_path is None:
            warnings.append(
                "No scores data or path provided. Skipping anti-universality check."
            )
            return ValidationResult(
                validator_name="validate_anti_universality",
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
                    validator_name="validate_anti_universality",
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
                validator_name="validate_anti_universality",
                passed=True,
                errors=errors,
                warnings=warnings,
                details=details,
            )

        method_scores: dict[str, list[float]] = {}
        contexts: list[str] = []

        for context_id, context_data in scores_data.items():
            if context_id.startswith("_"):
                continue
            contexts.append(context_id)

            if isinstance(context_data, dict):
                for method_id, score in context_data.items():
                    if isinstance(score, (int, float)):
                        if method_id not in method_scores:
                            method_scores[method_id] = []
                        method_scores[method_id].append(float(score))

        details["methods_checked"] = len(method_scores)
        details["contexts_checked"] = len(contexts)

        if not method_scores:
            warnings.append("No method scores found in data structure")
            return ValidationResult(
                validator_name="validate_anti_universality",
                passed=True,
                errors=errors,
                warnings=warnings,
                details=details,
            )

        for method_id, scores in method_scores.items():
            if not scores:
                continue

            max_score = max(scores)
            min_score = min(scores)

            if max_score == 1.0 and min_score == 1.0 and len(scores) > 1:
                errors.append(
                    f"Method {method_id} is maximal (1.0) across all {len(scores)} contexts"
                )
                details["universal_methods"].append(method_id)
            elif max_score == 1.0 and len(scores) > 5:
                max_count = sum(1 for s in scores if s == 1.0)
                if max_count == len(scores):
                    errors.append(
                        f"Method {method_id} has perfect score in all {len(scores)} contexts"
                    )
                    details["universal_methods"].append(method_id)
                elif max_count / len(scores) > 0.95:
                    warnings.append(
                        f"Method {method_id} is near-universal: {max_count}/{len(scores)} contexts at maximum"
                    )

        passed = len(errors) == 0

    except Exception as e:
        errors.append(f"Exception during validation: {str(e)}")
        passed = False

    return ValidationResult(
        validator_name="validate_anti_universality",
        passed=passed,
        errors=errors,
        warnings=warnings,
        details=details,
    )


def validate_intrinsic_calibration(
    calibration_path: str | Path = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json",
) -> ValidationResult:
    """
    Validate intrinsic calibration schema correctness.
    
    Checks:
    - Required fields present (base_layer, components)
    - Weight sums are valid
    - Schema structure matches specification
    - All required subcomponents present
    """
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {
        "components_checked": 0,
        "weight_validations": {},
    }

    try:
        calibration_path = Path(calibration_path)
        if not calibration_path.exists():
            errors.append(f"Intrinsic calibration file not found: {calibration_path}")
            return ValidationResult(
                validator_name="validate_intrinsic_calibration",
                passed=False,
                errors=errors,
                warnings=warnings,
                details=details,
            )

        with open(calibration_path) as f:
            data = json.load(f)

        if "base_layer" not in data:
            errors.append("Missing 'base_layer' field in intrinsic calibration")
        else:
            base_layer = data["base_layer"]
            if "aggregation" not in base_layer:
                errors.append("Missing 'aggregation' in base_layer")
            else:
                agg = base_layer["aggregation"]
                if "weights" in agg:
                    weights = agg["weights"]
                    weight_sum = sum(float(v) for v in weights.values())
                    details["weight_validations"]["base_layer_aggregation"] = weight_sum
                    if abs(weight_sum - 1.0) > 0.01:
                        errors.append(
                            f"Base layer aggregation weights sum to {weight_sum}, expected 1.0"
                        )

        if "components" not in data:
            errors.append("Missing 'components' field in intrinsic calibration")
        else:
            components = data["components"]
            details["components_checked"] = len(components)

            required_components = ["b_theory", "b_impl", "b_deploy"]
            for comp in required_components:
                if comp not in components:
                    errors.append(f"Missing required component: {comp}")
                else:
                    comp_data = components[comp]
                    if "subcomponents" in comp_data:
                        subcomps = comp_data["subcomponents"]
                        subcomp_weights = [
                            float(sc.get("weight", 0)) for sc in subcomps.values()
                        ]
                        if subcomp_weights:
                            subcomp_sum = sum(subcomp_weights)
                            details["weight_validations"][f"{comp}_subcomponents"] = subcomp_sum
                            if abs(subcomp_sum - 1.0) > 0.01:
                                errors.append(
                                    f"Component {comp} subcomponent weights sum to {subcomp_sum}, expected 1.0"
                                )

        passed = len(errors) == 0

    except Exception as e:
        errors.append(f"Exception during validation: {str(e)}")
        passed = False

    return ValidationResult(
        validator_name="validate_intrinsic_calibration",
        passed=passed,
        errors=errors,
        warnings=warnings,
        details=details,
    )


def validate_config_files(
    config_dir: str | Path = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization",
) -> ValidationResult:
    """
    Validate that all COHORT_2024 JSON files load successfully.
    
    Checks:
    - All COHORT_2024_*.json files parse correctly
    - Required metadata fields present
    - No JSON syntax errors
    """
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {
        "files_checked": 0,
        "files_passed": 0,
        "files_failed": [],
    }

    try:
        config_dir = Path(config_dir)
        if not config_dir.exists():
            errors.append(f"Config directory not found: {config_dir}")
            return ValidationResult(
                validator_name="validate_config_files",
                passed=False,
                errors=errors,
                warnings=warnings,
                details=details,
            )

        cohort_files = list(config_dir.rglob("COHORT_2024*.json"))
        details["files_checked"] = len(cohort_files)

        if not cohort_files:
            warnings.append(f"No COHORT_2024 JSON files found in {config_dir}")

        for file_path in cohort_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                if "_cohort_metadata" not in data and "cohort_id" not in str(data):
                    warnings.append(
                        f"File {file_path.name} missing cohort metadata"
                    )

                details["files_passed"] += 1

            except json.JSONDecodeError as e:
                errors.append(f"JSON parse error in {file_path.name}: {str(e)}")
                details["files_failed"].append(
                    {"file": str(file_path), "error": str(e)}
                )
            except Exception as e:
                errors.append(f"Error loading {file_path.name}: {str(e)}")
                details["files_failed"].append(
                    {"file": str(file_path), "error": str(e)}
                )

        passed = len(errors) == 0

    except Exception as e:
        errors.append(f"Exception during validation: {str(e)}")
        passed = False

    return ValidationResult(
        validator_name="validate_config_files",
        passed=passed,
        errors=errors,
        warnings=warnings,
        details=details,
    )


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
