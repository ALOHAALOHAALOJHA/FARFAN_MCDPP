"""Automated test runner for executing all validators with pass/fail reporting."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TypedDict

from .validators import (
    ValidationResult,
    validate_anti_universality,
    validate_boundedness,
    validate_config_files,
    validate_fusion_weights,
    validate_intrinsic_calibration,
    validate_layer_completeness,
)


class ValidationSuiteReport(TypedDict):
    execution_timestamp: str
    total_validators: int
    passed_validators: int
    failed_validators: int
    validation_results: dict[str, ValidationResult]
    summary: dict[str, Any]
    overall_passed: bool


def run_all_validations(
    config_dir: str | Path = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization",
    scores_data: dict[str, Any] | None = None,
    scores_path: str | Path | None = None,
    verbose: bool = True,
) -> ValidationSuiteReport:
    """
    Run all validation functions and generate comprehensive report.
    
    Args:
        config_dir: Directory containing COHORT_2024 configuration files
        scores_data: Optional pre-loaded scores data for anti-universality/boundedness checks
        scores_path: Optional path to scores file
        verbose: If True, print progress messages
        
    Returns:
        Comprehensive validation suite report with all results
    """
    if verbose:
        print("=" * 80)
        print("F.A.R.F.A.N CALIBRATION VALIDATION SUITE")
        print("=" * 80)
        print(f"Starting validation suite at {datetime.utcnow().isoformat()}Z")
        print()

    config_dir = Path(config_dir)
    validation_results: dict[str, ValidationResult] = {}

    validators: list[tuple[str, Callable[[], ValidationResult]]] = [
        (
            "layer_completeness",
            lambda: validate_layer_completeness(
                inventory_path=config_dir / "calibration/COHORT_2024_canonical_method_inventory.json",
                layer_assignment_path=config_dir / "calibration/COHORT_2024_layer_assignment.py",
            ),
        ),
        (
            "fusion_weights",
            lambda: validate_fusion_weights(
                fusion_weights_path=config_dir / "calibration/COHORT_2024_fusion_weights.json"
            ),
        ),
        (
            "anti_universality",
            lambda: validate_anti_universality(
                scores_data=scores_data, scores_path=scores_path
            ),
        ),
        (
            "intrinsic_calibration",
            lambda: validate_intrinsic_calibration(
                calibration_path=config_dir / "calibration/COHORT_2024_intrinsic_calibration.json"
            ),
        ),
        ("config_files", lambda: validate_config_files(config_dir=config_dir)),
        (
            "boundedness",
            lambda: validate_boundedness(
                scores_data=scores_data, scores_path=scores_path
            ),
        ),
    ]

    for validator_name, validator_func in validators:
        if verbose:
            print(f"Running validator: {validator_name}...")

        try:
            result = validator_func()
            validation_results[validator_name] = result

            if verbose:
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                print(f"  {status}")
                if result["errors"]:
                    print(f"    Errors: {len(result['errors'])}")
                if result["warnings"]:
                    print(f"    Warnings: {len(result['warnings'])}")
                print()

        except Exception as e:
            if verbose:
                print(f"  ✗ EXCEPTION: {str(e)}")
                print()

            validation_results[validator_name] = ValidationResult(
                validator_name=validator_name,
                passed=False,
                errors=[f"Validator raised exception: {str(e)}"],
                warnings=[],
                details={"exception": str(e)},
            )

    passed_count = sum(1 for r in validation_results.values() if r["passed"])
    failed_count = len(validation_results) - passed_count
    overall_passed = failed_count == 0

    total_errors = sum(len(r["errors"]) for r in validation_results.values())
    total_warnings = sum(len(r["warnings"]) for r in validation_results.values())

    summary = {
        "overall_status": "PASS" if overall_passed else "FAIL",
        "pass_rate": f"{passed_count}/{len(validation_results)}",
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "failed_validators": [
            name for name, result in validation_results.items() if not result["passed"]
        ],
    }

    report = ValidationSuiteReport(
        execution_timestamp=datetime.now().astimezone().isoformat(),
        total_validators=len(validation_results),
        passed_validators=passed_count,
        failed_validators=failed_count,
        validation_results=validation_results,
        summary=summary,
        overall_passed=overall_passed,
    )

    if verbose:
        print("=" * 80)
        print("VALIDATION SUITE SUMMARY")
        print("=" * 80)
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Pass Rate: {summary['pass_rate']}")
        print(f"Total Errors: {total_errors}")
        print(f"Total Warnings: {total_warnings}")
        failed_vals = summary["failed_validators"]
        if failed_vals and isinstance(failed_vals, list):
            print(f"Failed Validators: {', '.join(failed_vals)}")
        print("=" * 80)

    return report


def save_report(
    report: ValidationSuiteReport,
    output_path: str | Path = "validation_suite_report.json",
) -> None:
    """Save validation suite report to JSON file."""
    output_path = Path(output_path)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Validation report saved to: {output_path}")


def print_detailed_report(report: ValidationSuiteReport) -> None:
    """Print detailed validation report to console."""
    print("\n" + "=" * 80)
    print("DETAILED VALIDATION REPORT")
    print("=" * 80)
    print(f"Execution Time: {report['execution_timestamp']}")
    print(f"Total Validators: {report['total_validators']}")
    print(f"Passed: {report['passed_validators']}")
    print(f"Failed: {report['failed_validators']}")
    print()

    for validator_name, result in report["validation_results"].items():
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"{status} {validator_name}")

        if result["errors"]:
            print(f"  Errors ({len(result['errors'])}):")
            for error in result["errors"][:5]:
                print(f"    - {error}")
            if len(result["errors"]) > 5:
                print(f"    ... and {len(result['errors']) - 5} more")

        if result["warnings"]:
            print(f"  Warnings ({len(result['warnings'])}):")
            for warning in result["warnings"][:3]:
                print(f"    - {warning}")
            if len(result["warnings"]) > 3:
                print(f"    ... and {len(result['warnings']) - 3} more")

        if result["details"]:
            print(f"  Details: {', '.join(f'{k}={v}' for k, v in list(result['details'].items())[:3])}")

        print()

    print("=" * 80)


def run_cli() -> None:
    """CLI entry point for running validation suite."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run F.A.R.F.A.N calibration validation suite"
    )
    parser.add_argument(
        "--config-dir",
        default="src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization",
        help="Configuration directory",
    )
    parser.add_argument(
        "--scores-path", default=None, help="Optional path to scores file"
    )
    parser.add_argument(
        "--output",
        default="validation_suite_report.json",
        help="Output report path",
    )
    parser.add_argument(
        "--detailed", action="store_true", help="Print detailed report"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress progress messages"
    )

    args = parser.parse_args()

    report = run_all_validations(
        config_dir=args.config_dir,
        scores_path=args.scores_path,
        verbose=not args.quiet,
    )

    save_report(report, output_path=args.output)

    if args.detailed:
        print_detailed_report(report)

    exit_code = 0 if report["overall_passed"] else 1
    exit(exit_code)


if __name__ == "__main__":
    run_cli()
