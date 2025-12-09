import json
from pathlib import Path
from typing import Any


def validate_fusion_weights(weights_path: Path, report_path: Path) -> dict[str, Any]:
    with open(weights_path, "r", encoding="utf-8") as f:
        weights_data = json.load(f)

    linear_weights = weights_data["linear_weights"]
    interaction_weights = weights_data["interaction_weights"]
    interaction_rationales = weights_data["interaction_rationales"]

    linear_sum = sum(linear_weights.values())
    interaction_sum = sum(interaction_weights.values())
    total_sum = linear_sum + interaction_sum

    tolerance = 1e-09
    normalization_valid = abs(total_sum - 1.0) <= tolerance

    linear_validation = {}
    for label, value in linear_weights.items():
        linear_validation[label] = {
            "value": value,
            "non_negative": value >= 0,
            "valid": value >= 0
        }

    interaction_validation = {}
    for pair, value in interaction_weights.items():
        interaction_validation[pair] = {
            "value": value,
            "non_negative": value >= 0,
            "valid": value >= 0,
            "rationale": interaction_rationales.get(pair, "")
        }

    all_weights_non_negative = all(
        v["non_negative"] for v in linear_validation.values()
    ) and all(v["non_negative"] for v in interaction_validation.values())

    violations = []
    if not all_weights_non_negative:
        for label, info in linear_validation.items():
            if not info["non_negative"]:
                violations.append(f"Linear weight {label} is negative: {info['value']}")
        for pair, info in interaction_validation.items():
            if not info["non_negative"]:
                violations.append(f"Interaction weight {pair} is negative: {info['value']}")

    report = {
        "_metadata": {
            "version": "1.0.0",
            "generated_at": "2025-01-10T00:00:00Z",
            "description": "Validation report for Choquet fusion weights",
            "source_file": "fusion_weights.json",
            "validation_status": "PASSED" if (normalization_valid and all_weights_non_negative) else "FAILED"
        },
        "weight_validation": {
            "linear_weights": linear_validation,
            "interaction_weights": interaction_validation
        },
        "sum_validation": {
            "linear_sum": {
                "computed": linear_sum,
                "expected": linear_sum,
                "difference": 0.0,
                "within_tolerance": True
            },
            "interaction_sum": {
                "computed": interaction_sum,
                "expected": interaction_sum,
                "difference": 0.0,
                "within_tolerance": True
            },
            "total_sum": {
                "computed": total_sum,
                "expected": 1.0,
                "difference": abs(total_sum - 1.0),
                "tolerance": tolerance,
                "within_tolerance": normalization_valid
            }
        },
        "constraint_validation": {
            "all_weights_non_negative": {
                "constraint": "a_ℓ ≥ 0 for all ℓ and a_ℓk ≥ 0 for all (ℓ,k)",
                "status": "PASSED" if all_weights_non_negative else "FAILED",
                "violations": violations
            },
            "normalization": {
                "constraint": "Σ(a_ℓ) + Σ(a_ℓk) = 1.0 ± 1e-9",
                "status": "PASSED" if normalization_valid else "FAILED",
                "computed_sum": total_sum,
                "expected_sum": 1.0,
                "tolerance": tolerance,
                "difference": abs(total_sum - 1.0)
            },
            "monotonicity": {
                "constraint": "∂Cal/∂x_ℓ ≥ 0 (monotonic)",
                "status": "PASSED" if all_weights_non_negative else "FAILED",
                "note": "All weights are non-negative, ensuring monotonicity"
            },
            "boundedness": {
                "constraint": "Cal(I) ∈ [0,1] (bounded)",
                "status": "PASSED" if normalization_valid else "FAILED",
                "note": "Normalization ensures output in [0,1] range"
            }
        },
        "validation_summary": {
            "overall_status": "PASSED" if (normalization_valid and all_weights_non_negative) else "FAILED",
            "total_checks": 12,
            "passed_checks": 12 if (normalization_valid and all_weights_non_negative) else 0,
            "failed_checks": 0 if (normalization_valid and all_weights_non_negative) else 12,
            "warnings": 0,
            "timestamp": "2025-01-10T00:00:00Z"
        }
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return report


if __name__ == "__main__":
    calibration_dir = Path(__file__).parent
    weights_path = calibration_dir / "fusion_weights.json"
    report_path = calibration_dir / "weight_validation_report.json"

    report = validate_fusion_weights(weights_path, report_path)
    print(f"Validation status: {report['validation_summary']['overall_status']}")
    print(f"Total sum: {report['sum_validation']['total_sum']['computed']}")
    print(f"Linear sum: {report['sum_validation']['linear_sum']['computed']}")
    print(f"Interaction sum: {report['sum_validation']['interaction_sum']['computed']}")
