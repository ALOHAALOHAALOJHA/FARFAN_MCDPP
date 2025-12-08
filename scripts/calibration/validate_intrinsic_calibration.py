#!/usr/bin/env python3
"""
validate_intrinsic_calibration.py - Comprehensive validation of intrinsic calibration

Jobfront 1.3: Validate Intrinsic Calibration
- Schema validation
- Purity checks
- Coverage analysis
- Weight verification
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    """Save JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def validate_schema(data: dict) -> tuple[bool, list[str]]:
    """
    Validate schema of intrinsic_calibration.json.
    
    Checks:
    - Every entry has required keys
    - All scores in [0.0, 1.0]
    - Status in: {computed, pending, excluded, none}
    - No forbidden keys
    """
    errors = []
    required_keys = {'calibration_status', 'layer', 'last_updated'}
    valid_statuses = {'computed', 'pending', 'excluded', 'none'}
    forbidden_keys = ['@chain', '@q', '@d', '@p', '@C', '@u', '@m',
                     'final_score', 'layer_scores', 'chain_', 'queue_']

    methods = {k: v for k, v in data.items() if k != '_metadata'}

    for method_id, entry in methods.items():
        # Check required keys
        missing = required_keys - set(entry.keys())
        if missing:
            errors.append(f"{method_id}: Missing required keys: {missing}")

        # Check calibration status
        status = entry.get('calibration_status')
        if status not in valid_statuses:
            errors.append(f"{method_id}: Invalid status '{status}', must be in {valid_statuses}")

        # For computed methods, check score keys and ranges
        if status == 'computed':
            score_keys = {'b_theory', 'b_impl', 'b_deploy'}
            missing_scores = score_keys - set(entry.keys())
            if missing_scores:
                errors.append(f"{method_id}: Missing score keys: {missing_scores}")

            # Check score ranges
            for score_key in score_keys:
                if score_key in entry:
                    score = entry[score_key]
                    if not isinstance(score, (int, float)):
                        errors.append(f"{method_id}: {score_key} is not numeric: {score}")
                    elif not (0.0 <= score <= 1.0):
                        errors.append(f"{method_id}: {score_key}={score} out of range [0.0, 1.0]")

        # Check for forbidden keys
        for key in entry.keys():
            for forbidden in forbidden_keys:
                if forbidden.lower() in key.lower():
                    errors.append(f"{method_id}: Forbidden key '{key}' contains '{forbidden}'")

    return len(errors) == 0, errors


def verify_purity(data: dict) -> tuple[bool, list[str]]:
    """
    Verify purity - no contamination from other calibration layers.
    
    Checks for:
    - Forbidden patterns (@chain, @q, @d, @p, etc.) in calibration data
    - Note: "final_score" is ALLOWED in evidence traces (it's part of computation)
    - Note: method_id can contain any characters (it's just the method name)
    """
    violations = []
    forbidden_patterns = ["@chain", "@q", "@d", "@p", "@C", "@u", "@m",
                         "layer_scores", "queue_",
                         "context_q", "context_d"]

    methods = {k: v for k, v in data.items() if k != '_metadata'}

    for method_id, entry in methods.items():
        # Check TOP-LEVEL keys only (not evidence, not method_id)
        for key in entry.keys():
            if key in ['evidence', 'triage_evidence', 'method_id']:
                continue  # Skip evidence and method_id

            for pattern in forbidden_patterns:
                if pattern.lower() in key.lower():
                    violations.append(
                        f"{method_id}: Contamination detected - key '{key}' contains forbidden pattern '{pattern}'"
                    )

            # Check for forbidden pattern in THIS key's value
            value_str = json.dumps(entry[key])
            for pattern in forbidden_patterns:
                if pattern in value_str:
                    violations.append(
                        f"{method_id}: Contamination detected - {key} value contains forbidden pattern '{pattern}'"
                    )

    return len(violations) == 0, violations


def analyze_coverage(data: dict) -> tuple[bool, dict[str, Any]]:
    """
    Analyze coverage statistics.
    
    Returns:
    - pass/fail based on threshold
    - detailed statistics
    """
    metadata = data.get('_metadata', {})
    total = metadata.get('total_methods', 0)
    computed = metadata.get('computed_methods', 0)
    excluded = metadata.get('excluded_methods', 0)

    methods = {k: v for k, v in data.items() if k != '_metadata'}

    # Count by status
    status_counts = {
        'computed': 0,
        'pending': 0,
        'excluded': 0,
        'none': 0
    }

    for entry in methods.values():
        status = entry.get('calibration_status', 'none')
        if status in status_counts:
            status_counts[status] += 1

    # Calculate coverage
    coverage = (computed / total * 100) if total > 0 else 0

    # Check threshold
    threshold = 25.0  # Realistic threshold (most methods are correctly excluded)
    passed = coverage >= threshold

    stats = {
        'total_methods': total,
        'computed_methods': computed,
        'excluded_methods': excluded,
        'coverage_percent': round(coverage, 2),
        'threshold_percent': threshold,
        'passed': passed,
        'status_breakdown': status_counts
    }

    return passed, stats


def verify_weights(rubric_path: Path) -> tuple[bool, list[str]]:
    """
    Verify weight configuration in rubric.
    
    Checks:
    - b_theory weights sum to 1.0
    - b_impl weights sum to 1.0
    - b_deploy weights sum to 1.0
    """
    rubric = load_json(rubric_path)
    errors = []

    # Check b_theory weights
    theory_weights = rubric.get('b_theory', {}).get('weights', {})
    theory_sum = sum(theory_weights.values())
    if abs(theory_sum - 1.0) > 0.0001:
        errors.append(f"b_theory weights sum to {theory_sum:.4f}, expected 1.0 (weights: {theory_weights})")

    # Check b_impl weights
    impl_weights = rubric.get('b_impl', {}).get('weights', {})
    impl_sum = sum(impl_weights.values())
    if abs(impl_sum - 1.0) > 0.0001:
        errors.append(f"b_impl weights sum to {impl_sum:.4f}, expected 1.0 (weights: {impl_weights})")

    # Check b_deploy weights
    deploy_weights = rubric.get('b_deploy', {}).get('weights', {})
    deploy_sum = sum(deploy_weights.values())
    if abs(deploy_sum - 1.0) > 0.0001:
        errors.append(f"b_deploy weights sum to {deploy_sum:.4f}, expected 1.0 (weights: {deploy_weights})")

    return len(errors) == 0, errors


def main():
    repo_root = Path(__file__).resolve().parents[2]
    calibration_path = repo_root / "config" / "intrinsic_calibration.json"
    rubric_path = repo_root / "src" / "farfan_pipeline" / "core" / "calibration" / "intrinsic_calibration_rubric.json"

    print("=" * 80)
    print("JOBFRONT 1.3: VALIDATE INTRINSIC CALIBRATION")
    print("=" * 80)
    print()

    # Load data
    print("Loading intrinsic_calibration.json...")
    data = load_json(calibration_path)

    # Create validation report
    report = {
        'validated_at': datetime.now(timezone.utc).isoformat(),
        'calibration_file': str(calibration_path),
        'rubric_file': str(rubric_path),
        'checks': {}
    }

    all_passed = True

    # 1. Schema validation
    print("\n1. Schema Validation")
    print("-" * 80)
    schema_passed, schema_errors = validate_schema(data)
    report['checks']['schema_validation'] = {
        'passed': schema_passed,
        'errors': schema_errors
    }

    if schema_passed:
        print("✓ PASSED: All entries have valid schema")
    else:
        print(f"✗ FAILED: {len(schema_errors)} schema errors found")
        for error in schema_errors[:10]:  # Show first 10
            print(f"  - {error}")
        if len(schema_errors) > 10:
            print(f"  ... and {len(schema_errors) - 10} more errors")
        all_passed = False

    # 2. Purity check
    print("\n2. Purity Check")
    print("-" * 80)
    purity_passed, purity_violations = verify_purity(data)
    report['checks']['purity_check'] = {
        'passed': purity_passed,
        'violations': purity_violations
    }

    if purity_passed:
        print("✓ PASSED: No contamination from other layers")
    else:
        print(f"✗ FAILED: {len(purity_violations)} contamination violations found")
        for violation in purity_violations[:10]:
            print(f"  - {violation}")
        if len(purity_violations) > 10:
            print(f"  ... and {len(purity_violations) - 10} more violations")
        all_passed = False

    # 3. Coverage analysis
    print("\n3. Coverage Analysis")
    print("-" * 80)
    coverage_passed, coverage_stats = analyze_coverage(data)
    report['checks']['coverage_analysis'] = coverage_stats

    print(f"Total methods: {coverage_stats['total_methods']}")
    print(f"Computed: {coverage_stats['computed_methods']}")
    print(f"Excluded: {coverage_stats['excluded_methods']}")
    print(f"Coverage: {coverage_stats['coverage_percent']}%")
    print(f"Threshold: {coverage_stats['threshold_percent']}%")
    print(f"Status breakdown: {coverage_stats['status_breakdown']}")

    if coverage_passed:
        print(f"✓ PASSED: Coverage {coverage_stats['coverage_percent']}% >= {coverage_stats['threshold_percent']}%")
    else:
        print(f"✗ FAILED: Coverage {coverage_stats['coverage_percent']}% < {coverage_stats['threshold_percent']}%")
        all_passed = False

    # 4. Weight verification
    print("\n4. Weight Verification")
    print("-" * 80)
    weights_passed, weight_errors = verify_weights(rubric_path)
    report['checks']['weight_verification'] = {
        'passed': weights_passed,
        'errors': weight_errors
    }

    if weights_passed:
        print("✓ PASSED: All weights sum to 1.0")
    else:
        print("✗ FAILED: Weight errors found")
        for error in weight_errors:
            print(f"  - {error}")
        all_passed = False

    # Overall result
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ VALIDATION PASSED: All checks successful")
        report['overall_result'] = 'PASSED'
        exit_code = 0
    else:
        print("✗ VALIDATION FAILED: Some checks failed")
        report['overall_result'] = 'FAILED'
        exit_code = 1
    print("=" * 80)

    # Save reports
    output_dir = repo_root / "docs" / "calibration"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save validation report
    report_path = output_dir / "intrinsic_validation_report.json"
    save_json(report_path, report)
    print(f"\nValidation report saved to: {report_path}")

    # Save purity check log
    purity_log_path = output_dir / "purity_check_log.txt"
    with open(purity_log_path, 'w') as f:
        f.write("Purity Check Log\n")
        f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
        f.write("=" * 80 + "\n\n")
        if purity_passed:
            f.write("✓ PASSED: No contamination detected\n")
        else:
            f.write(f"✗ FAILED: {len(purity_violations)} violations found\n\n")
            for violation in purity_violations:
                f.write(f"- {violation}\n")
    print(f"Purity log saved to: {purity_log_path}")

    # Save coverage analysis
    coverage_md_path = output_dir / "coverage_analysis.md"
    with open(coverage_md_path, 'w') as f:
        f.write("# Coverage Analysis\n\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).isoformat()}\n\n")
        f.write("## Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|:-------|------:|\n")
        f.write(f"| Total Methods | {coverage_stats['total_methods']} |\n")
        f.write(f"| Computed | {coverage_stats['computed_methods']} |\n")
        f.write(f"| Excluded | {coverage_stats['excluded_methods']} |\n")
        f.write(f"| Coverage | {coverage_stats['coverage_percent']}% |\n")
        f.write(f"| Threshold | {coverage_stats['threshold_percent']}% |\n")
        f.write(f"| Status | {'✓ PASSED' if coverage_passed else '✗ FAILED'} |\n\n")

        f.write("## Status Breakdown\n\n")
        f.write("| Status | Count |\n")
        f.write("|:-------|------:|\n")
        for status, count in coverage_stats['status_breakdown'].items():
            f.write(f"| {status} | {count} |\n")
    print(f"Coverage analysis saved to: {coverage_md_path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
