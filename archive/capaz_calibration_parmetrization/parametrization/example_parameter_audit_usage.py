"""
Example Usage of Parameter Audit System

Demonstrates various ways to use the hardcoded parameter audit system
programmatically for integration into custom workflows, CI/CD pipelines,
or development tools.
"""

from pathlib import Path
import json
import logging

from hardcoded_parameter_scanner import (
    run_audit,
    HardcodedParameterScanner,
    ConfigurationRegistry,
    AuditStatistics,
)
from executor_parameter_validator import (
    ExecutorParameterValidator,
    validate_executors,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def example_1_simple_audit():
    """Example 1: Simple full audit with defaults."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Simple Full Audit")
    print("=" * 80)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    config_base_path = Path(__file__).resolve().parent
    output_dir = project_root / "artifacts" / "audit_reports"
    
    stats = run_audit(src_path, config_base_path, output_dir)
    
    print(f"\nResults:")
    print(f"  Files Scanned: {stats.total_files_scanned}")
    print(f"  Violations: {stats.violations_found}")
    print(f"  Critical: {stats.critical_violations}")
    print(f"  Status: {stats.certification_status}")
    
    return stats.certification_status == "PASS"


def example_2_check_specific_files():
    """Example 2: Scan specific files only."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Scan Specific Files")
    print("=" * 80)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    config_base_path = Path(__file__).resolve().parent
    
    scanner = HardcodedParameterScanner(src_path, config_base_path)
    
    target_files = [
        src_path / "canonic_phases" / "Phase_four_five_six_seven" / "aggregation.py",
        src_path / "orchestration" / "orchestrator.py",
    ]
    
    all_violations = []
    for file_path in target_files:
        if file_path.exists():
            print(f"\nScanning: {file_path.relative_to(project_root)}")
            violations = scanner.scan_file(file_path)
            all_violations.extend(violations)
            print(f"  Violations: {len(violations)}")
    
    print(f"\nTotal violations in selected files: {len(all_violations)}")
    
    return all_violations


def example_3_filter_by_severity():
    """Example 3: Filter violations by severity."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Filter by Severity")
    print("=" * 80)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    config_base_path = Path(__file__).resolve().parent
    
    scanner = HardcodedParameterScanner(src_path, config_base_path)
    scanner.scan_directory()
    
    critical_violations = [v for v in scanner.violations if v.severity == "CRITICAL"]
    high_violations = [v for v in scanner.violations if v.severity == "HIGH"]
    
    print(f"\nCRITICAL Violations: {len(critical_violations)}")
    for v in critical_violations[:5]:
        print(f"  - {v.file_path}:{v.line_number} - {v.variable_name} = {v.hardcoded_value}")
    
    if len(critical_violations) > 5:
        print(f"  ... and {len(critical_violations) - 5} more")
    
    print(f"\nHIGH Violations: {len(high_violations)}")
    for v in high_violations[:5]:
        print(f"  - {v.file_path}:{v.line_number} - {v.variable_name} = {v.hardcoded_value}")
    
    if len(high_violations) > 5:
        print(f"  ... and {len(high_violations) - 5} more")
    
    return critical_violations, high_violations


def example_4_executor_validation():
    """Example 4: Executor-specific validation."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Executor Validation")
    print("=" * 80)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    
    validator = ExecutorParameterValidator(src_path)
    violations = validator.validate_all()
    
    print(f"\nExecutor violations: {len(violations)}")
    
    if violations:
        print("\nTop violations:")
        for v in violations[:5]:
            print(f"  - {v.executor_class}: {v.parameter_name} = {v.hardcoded_value}")
            print(f"    Recommendation: {v.recommendation}")
    else:
        print("\n✅ All executors properly configured!")
    
    return violations


def example_5_custom_report():
    """Example 5: Generate custom report format."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Custom Report Format")
    print("=" * 80)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    config_base_path = Path(__file__).resolve().parent
    
    scanner = HardcodedParameterScanner(src_path, config_base_path)
    scanner.scan_directory()
    
    violations_by_file = {}
    for v in scanner.violations:
        if v.file_path not in violations_by_file:
            violations_by_file[v.file_path] = []
        violations_by_file[v.file_path].append(v)
    
    print(f"\nFiles with violations: {len(violations_by_file)}")
    print("\nTop 10 files by violation count:")
    
    sorted_files = sorted(
        violations_by_file.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    for i, (file_path, violations) in enumerate(sorted_files[:10], 1):
        print(f"  {i}. {file_path}")
        print(f"     Violations: {len(violations)}")
        
        critical = sum(1 for v in violations if v.severity == "CRITICAL")
        high = sum(1 for v in violations if v.severity == "HIGH")
        medium = sum(1 for v in violations if v.severity == "MEDIUM")
        
        print(f"     Breakdown: {critical} CRITICAL, {high} HIGH, {medium} MEDIUM")
    
    return violations_by_file


def example_6_check_config_coverage():
    """Example 6: Check configuration coverage."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Configuration Coverage")
    print("=" * 80)
    
    config_base_path = Path(__file__).resolve().parent
    registry = ConfigurationRegistry(config_base_path)
    
    print("\nConfiguration Registry Stats:")
    print(f"  Known Weights: {len(registry.known_weights)}")
    print(f"  Known Thresholds: {len(registry.known_thresholds)}")
    print(f"  Known Scores: {len(registry.known_scores)}")
    print(f"  Known Timeouts: {len(registry.known_timeouts)}")
    
    if registry.known_weights:
        print(f"\n  Sample Weights: {sorted(list(registry.known_weights))[:10]}")
    
    if registry.known_thresholds:
        print(f"  Sample Thresholds: {sorted(list(registry.known_thresholds))[:10]}")
    
    if registry.known_scores:
        print(f"  Sample Scores: {sorted(list(registry.known_scores))[:10]}")
    
    return registry


def example_7_ci_cd_integration():
    """Example 7: CI/CD integration pattern."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: CI/CD Integration")
    print("=" * 80)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    config_base_path = Path(__file__).resolve().parent
    output_dir = project_root / "artifacts" / "audit_reports"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n1. Running audit...")
    stats = run_audit(src_path, config_base_path, output_dir)
    
    print("\n2. Running executor validation...")
    executor_report_path = output_dir / "executor_validation.md"
    executor_violations = validate_executors(src_path, executor_report_path)
    
    print("\n3. Checking certification status...")
    passed = stats.critical_violations == 0 and executor_violations == 0
    
    if passed:
        print("\n✅ CERTIFICATION PASSED")
        print("   - Zero critical violations")
        print("   - All executors properly configured")
        exit_code = 0
    else:
        print("\n❌ CERTIFICATION FAILED")
        if stats.critical_violations > 0:
            print(f"   - {stats.critical_violations} critical violations")
        if executor_violations > 0:
            print(f"   - {executor_violations} executor violations")
        exit_code = 1
    
    print(f"\n4. Exit code: {exit_code}")
    
    return exit_code


def example_8_programmatic_fix_suggestions():
    """Example 8: Generate programmatic fix suggestions."""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Fix Suggestions")
    print("=" * 80)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    config_base_path = Path(__file__).resolve().parent
    
    scanner = HardcodedParameterScanner(src_path, config_base_path)
    scanner.scan_directory()
    
    critical_violations = [v for v in scanner.violations if v.severity == "CRITICAL"]
    
    if not critical_violations:
        print("\n✅ No critical violations to fix!")
        return
    
    print(f"\nFound {len(critical_violations)} critical violations.")
    print("\nSuggested fixes:\n")
    
    for i, v in enumerate(critical_violations[:5], 1):
        print(f"{i}. File: {v.file_path}:{v.line_number}")
        print(f"   Variable: {v.variable_name}")
        print(f"   Hardcoded: {v.hardcoded_value}")
        print(f"   Category: {v.category}")
        print()
        
        if v.category == "weight":
            print("   Fix:")
            print("   1. Add to COHORT_2024_fusion_weights.json or appropriate JSON config")
            print("   2. Replace with:")
            print(f"      {v.variable_name} = config.get('component.{v.variable_name}', {v.hardcoded_value})")
        
        elif v.category == "score":
            print("   Fix:")
            print("   1. Add to COHORT_2024_runtime_layers.json or appropriate JSON config")
            print("   2. Replace with:")
            print(f"      {v.variable_name} = config.get('{v.variable_name}', {v.hardcoded_value})")
        
        elif v.category == "threshold":
            print("   Fix:")
            print("   1. Add to appropriate JSON config under appropriate component")
            print("   2. Replace with:")
            print(f"      {v.variable_name} = config.get('thresholds.{v.variable_name}', {v.hardcoded_value})")
        
        print()


def example_9_json_export():
    """Example 9: Export violations as JSON for external tools."""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: JSON Export")
    print("=" * 80)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    config_base_path = Path(__file__).resolve().parent
    
    scanner = HardcodedParameterScanner(src_path, config_base_path)
    scanner.scan_directory()
    
    export_data = {
        "summary": {
            "total_violations": len(scanner.violations),
            "critical": sum(1 for v in scanner.violations if v.severity == "CRITICAL"),
            "high": sum(1 for v in scanner.violations if v.severity == "HIGH"),
            "medium": sum(1 for v in scanner.violations if v.severity == "MEDIUM"),
        },
        "violations": [v.to_dict() for v in scanner.violations[:10]],
    }
    
    output_file = project_root / "artifacts" / "violations_export.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nExported violations to: {output_file}")
    print(f"Summary: {export_data['summary']}")
    
    return export_data


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("PARAMETER AUDIT SYSTEM - USAGE EXAMPLES")
    print("=" * 80)
    
    examples = [
        ("Simple Full Audit", example_1_simple_audit),
        ("Scan Specific Files", example_2_check_specific_files),
        ("Filter by Severity", example_3_filter_by_severity),
        ("Executor Validation", example_4_executor_validation),
        ("Custom Report", example_5_custom_report),
        ("Configuration Coverage", example_6_check_config_coverage),
        ("CI/CD Integration", example_7_ci_cd_integration),
        ("Fix Suggestions", example_8_programmatic_fix_suggestions),
        ("JSON Export", example_9_json_export),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRun specific example (1-9) or 'all' to run all:")
    print("(Note: Running programmatically, will run Example 7 for demonstration)")
    
    result = example_7_ci_cd_integration()
    
    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
