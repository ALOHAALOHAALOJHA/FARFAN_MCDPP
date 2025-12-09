"""Example usage patterns for the validation suite."""

from pathlib import Path

from .runner import print_detailed_report, run_all_validations, save_report
from .validators import (
    validate_anti_universality,
    validate_boundedness,
    validate_config_files,
    validate_fusion_weights,
    validate_intrinsic_calibration,
    validate_layer_completeness,
)


def example_run_single_validator() -> None:
    """Example: Run a single validator."""
    print("=" * 80)
    print("EXAMPLE: Running single validator (layer_completeness)")
    print("=" * 80)

    result = validate_layer_completeness()

    print(f"Validator: {result['validator_name']}")
    print(f"Passed: {result['passed']}")
    print(f"Errors: {len(result['errors'])}")
    print(f"Warnings: {len(result['warnings'])}")
    print()

    if result["errors"]:
        print("Errors:")
        for error in result["errors"][:5]:
            print(f"  - {error}")
        print()

    if result["warnings"]:
        print("Warnings:")
        for warning in result["warnings"][:3]:
            print(f"  - {warning}")
        print()


def example_run_full_suite() -> None:
    """Example: Run complete validation suite."""
    print("=" * 80)
    print("EXAMPLE: Running full validation suite")
    print("=" * 80)

    report = run_all_validations(verbose=True)

    print()
    print("Report Summary:")
    print(f"  Overall Status: {report['summary']['overall_status']}")
    print(f"  Pass Rate: {report['summary']['pass_rate']}")
    print(f"  Total Errors: {report['summary']['total_errors']}")
    print(f"  Total Warnings: {report['summary']['total_warnings']}")


def example_validate_with_scores() -> None:
    """Example: Validate with custom scores data."""
    print("=" * 80)
    print("EXAMPLE: Validating with scores data")
    print("=" * 80)

    sample_scores = {
        "dimension_1": {
            "question_1": {
                "method_a": 0.85,
                "method_b": 0.72,
                "method_c": 0.91
            },
            "question_2": {
                "method_a": 0.78,
                "method_b": 0.89,
                "method_c": 0.65
            }
        },
        "dimension_2": {
            "question_1": {
                "method_a": 0.92,
                "method_b": 0.81,
                "method_c": 0.73
            }
        }
    }

    print("\nChecking anti-universality...")
    anti_univ_result = validate_anti_universality(scores_data=sample_scores)
    print(f"  Passed: {anti_univ_result['passed']}")
    print(f"  Methods checked: {anti_univ_result['details']['methods_checked']}")

    print("\nChecking boundedness...")
    boundedness_result = validate_boundedness(scores_data=sample_scores)
    print(f"  Passed: {boundedness_result['passed']}")
    print(f"  Scores checked: {boundedness_result['details']['total_scores_checked']}")


def example_validate_fusion_weights() -> None:
    """Example: Validate fusion weights with custom tolerance."""
    print("=" * 80)
    print("EXAMPLE: Validating fusion weights")
    print("=" * 80)

    result = validate_fusion_weights(tolerance=1e-9)

    print(f"Passed: {result['passed']}")
    print(f"Linear sum: {result['details'].get('linear_sum', 'N/A')}")
    print(f"Interaction sum: {result['details'].get('interaction_sum', 'N/A')}")
    print(f"Total sum: {result['details'].get('total_sum', 'N/A')}")

    if result["details"].get("negative_weights"):
        print(f"Negative weights found: {len(result['details']['negative_weights'])}")


def example_save_and_load_report() -> None:
    """Example: Save report to file and work with it."""
    print("=" * 80)
    print("EXAMPLE: Saving and working with validation report")
    print("=" * 80)

    report = run_all_validations(verbose=False)

    output_path = Path("example_validation_report.json")
    save_report(report, output_path=output_path)
    print(f"\nReport saved to: {output_path}")

    print("\nDetailed report:")
    print_detailed_report(report)

    if not report["overall_passed"]:
        print("\nFailed validators:")
        for validator_name in report["summary"]["failed_validators"]:
            result = report["validation_results"][validator_name]
            print(f"\n{validator_name}:")
            for error in result["errors"]:
                print(f"  - {error}")


def example_custom_config_directory() -> None:
    """Example: Run validations with custom configuration directory."""
    print("=" * 80)
    print("EXAMPLE: Custom configuration directory")
    print("=" * 80)

    custom_config_dir = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization"

    report = run_all_validations(
        config_dir=custom_config_dir,
        verbose=False
    )

    print(f"Validated configuration in: {custom_config_dir}")
    print(f"Overall Status: {report['summary']['overall_status']}")
    print(f"Validators Run: {report['total_validators']}")
    print(f"Passed: {report['passed_validators']}")
    print(f"Failed: {report['failed_validators']}")


def example_check_specific_file() -> None:
    """Example: Validate a specific configuration file."""
    print("=" * 80)
    print("EXAMPLE: Validate specific configuration file")
    print("=" * 80)

    print("\nValidating intrinsic calibration...")
    result = validate_intrinsic_calibration()
    print(f"  Passed: {result['passed']}")
    print(f"  Components checked: {result['details'].get('components_checked', 'N/A')}")

    print("\nValidating config files in directory...")
    result = validate_config_files()
    print(f"  Passed: {result['passed']}")
    print(f"  Files checked: {result['details'].get('files_checked', 'N/A')}")
    print(f"  Files passed: {result['details'].get('files_passed', 'N/A')}")


def main() -> None:
    """Run all examples."""
    examples = [
        ("Single Validator", example_run_single_validator),
        ("Full Suite", example_run_full_suite),
        ("With Scores", example_validate_with_scores),
        ("Fusion Weights", example_validate_fusion_weights),
        ("Save Report", example_save_and_load_report),
        ("Custom Config Dir", example_custom_config_directory),
        ("Specific File", example_check_specific_file),
    ]

    print("\n" + "=" * 80)
    print("F.A.R.F.A.N VALIDATION SUITE - EXAMPLES")
    print("=" * 80)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print()

    try:
        choice = input("Select example (1-7, or 'all'): ").strip().lower()

        if choice == "all":
            for name, func in examples:
                print(f"\n\nRunning: {name}")
                try:
                    func()
                except Exception as e:
                    print(f"Error: {e}")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            name, func = examples[int(choice) - 1]
            print(f"\n\nRunning: {name}")
            func()
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")


if __name__ == "__main__":
    main()
