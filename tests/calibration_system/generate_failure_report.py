#!/usr/bin/env python3
"""
Generate Calibration System Failure Report

Aggregates test results and generates a comprehensive failure report
when any validation test fails.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate calibration system failure report"
    )
    parser.add_argument("--test1", required=True, help="Test 1 outcome")
    parser.add_argument("--test2", required=True, help="Test 2 outcome")
    parser.add_argument("--test3", required=True, help="Test 3 outcome")
    parser.add_argument("--test4", required=True, help="Test 4 outcome")
    parser.add_argument("--test5", required=True, help="Test 5 outcome")
    parser.add_argument("--test6", required=True, help="Test 6 outcome")
    parser.add_argument("--test7", required=True, help="Test 7 outcome")
    parser.add_argument("--output", default="calibration_system_failure_report.md",
                       help="Output file path")
    return parser.parse_args()


def load_test_results() -> Dict[str, List[str]]:
    """Load detailed test results from XML files"""
    results_dir = Path("test-results")
    failures = {}
    
    if not results_dir.exists():
        return failures
    
    for xml_file in results_dir.glob("*.xml"):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            test_name = xml_file.stem
            test_failures = []
            
            for testcase in root.findall(".//testcase"):
                failure = testcase.find("failure")
                if failure is not None:
                    test_failures.append({
                        "name": testcase.get("name"),
                        "message": failure.get("message", ""),
                        "details": failure.text or ""
                    })
            
            if test_failures:
                failures[test_name] = test_failures
                
        except Exception as e:
            print(f"Warning: Could not parse {xml_file}: {e}")
    
    return failures


def generate_report(args: argparse.Namespace) -> str:
    """Generate the failure report"""
    tests = {
        "Test 1: Inventory Consistency": args.test1,
        "Test 2: Layer Correctness": args.test2,
        "Test 3: Intrinsic Coverage (≥80%)": args.test3,
        "Test 4: AST Extraction Accuracy": args.test4,
        "Test 5: Orchestrator Runtime": args.test5,
        "Test 6: No Hardcoded Calibrations": args.test6,
        "Test 7: Performance Benchmarks": args.test7,
    }
    
    failures = load_test_results()
    failed_tests = [name for name, outcome in tests.items() if outcome != "success"]
    
    report = []
    report.append("# CALIBRATION SYSTEM FAILURE REPORT")
    report.append("")
    report.append(f"**Generated:** {datetime.now().isoformat()}")
    report.append("")
    
    if not failed_tests:
        report.append("## ✅ STATUS: PRODUCTION READY")
        report.append("")
        report.append("All calibration validation tests passed successfully.")
        report.append("")
        report.append("### Test Results")
        report.append("")
        for test_name, outcome in tests.items():
            report.append(f"- ✅ {test_name}: **{outcome}**")
        
    else:
        report.append("## ❌ STATUS: NOT READY FOR PRODUCTION")
        report.append("")
        report.append(f"**{len(failed_tests)} of {len(tests)} validation tests FAILED**")
        report.append("")
        report.append("### Critical Failures")
        report.append("")
        
        for test_name, outcome in tests.items():
            icon = "✅" if outcome == "success" else "❌"
            report.append(f"{icon} **{test_name}**: {outcome}")
        
        report.append("")
        report.append("---")
        report.append("")
        report.append("## Failure Analysis")
        report.append("")
        
        test_descriptions = {
            "Test 1": {
                "name": "Inventory Consistency",
                "purpose": "Verifies all methods are consistently defined across JSON files",
                "impact": "Inconsistent inventories can cause runtime errors and calibration mismatches",
                "remediation": [
                    "Ensure all methods in executors_methods.json exist in intrinsic_calibration.json",
                    "Remove orphaned calibration entries",
                    "Verify all 30 executors are properly defined"
                ]
            },
            "Test 2": {
                "name": "Layer Correctness",
                "purpose": "Validates architectural integrity with 8 required layers",
                "impact": "Missing layers break the execution pipeline",
                "remediation": [
                    "Each executor must have methods in all 8 layers: ingestion, extraction, transformation, validation, aggregation, scoring, reporting, meta",
                    "Verify LAYER_REQUIREMENTS mapping is complete",
                    "Check layer dependencies are acyclic"
                ]
            },
            "Test 3": {
                "name": "Intrinsic Coverage",
                "purpose": "Ensures ≥80% methods have computed calibrations",
                "impact": "Low coverage means system relies on defaults or fails",
                "remediation": [
                    "Run intrinsic calibration triage on uncalibrated methods",
                    "Ensure all 30 executors have at least one method with status='computed'",
                    "Document reasons for any 'excluded' or 'manual' methods"
                ]
            },
            "Test 4": {
                "name": "AST Extraction Accuracy",
                "purpose": "Validates extracted signatures match actual source code",
                "impact": "Signature mismatches cause method execution failures",
                "remediation": [
                    "Re-extract method signatures from source code",
                    "Update method inventory with correct signatures",
                    "Keep mismatch rate below 5%"
                ]
            },
            "Test 5": {
                "name": "Orchestrator Runtime",
                "purpose": "Tests correct layer evaluation and aggregation",
                "impact": "Runtime errors prevent policy analysis",
                "remediation": [
                    "Fix layer ordering issues",
                    "Ensure context propagation works correctly",
                    "Test calibration resolution without errors"
                ]
            },
            "Test 6": {
                "name": "No Hardcoded Calibrations",
                "purpose": "Scans for magic numbers in calibration-sensitive code",
                "impact": "Hardcoded values prevent systematic calibration",
                "remediation": [
                    "Move all thresholds, weights, scores to configuration",
                    "Use calibration_registry.get_calibration() instead of literals",
                    "Update intrinsic_calibration.json with externalized values"
                ]
            },
            "Test 7": {
                "name": "Performance Benchmarks",
                "purpose": "Validates load times and calibration speed",
                "impact": "Slow performance degrades user experience",
                "remediation": [
                    "Optimize JSON file size and structure",
                    "Ensure load intrinsic.json < 1s",
                    "Ensure calibrate 30 executors < 5s",
                    "Ensure calibrate 200 methods < 30s"
                ]
            }
        }
        
        for test_name in failed_tests:
            test_num = test_name.split(":")[0].replace("Test ", "Test")
            test_info = test_descriptions.get(test_num, {})
            
            report.append(f"### {test_name}")
            report.append("")
            
            if test_info:
                report.append(f"**Purpose:** {test_info.get('purpose', 'N/A')}")
                report.append("")
                report.append(f"**Impact:** {test_info.get('impact', 'N/A')}")
                report.append("")
                report.append("**Remediation Steps:**")
                report.append("")
                for step in test_info.get('remediation', []):
                    report.append(f"1. {step}")
                report.append("")
            
            test_key = f"test{test_num.replace('Test', '')}-" + test_info.get('name', '').lower().replace(' ', '-')
            if test_key in failures:
                report.append("**Specific Failures:**")
                report.append("")
                for failure in failures[test_key][:5]:
                    report.append(f"- `{failure['name']}`")
                    if failure['message']:
                        report.append(f"  - {failure['message'][:200]}")
                report.append("")
        
        report.append("---")
        report.append("")
        report.append("## Required Actions")
        report.append("")
        report.append("1. **DO NOT MERGE** this PR until all tests pass")
        report.append("2. Review failure details above")
        report.append("3. Apply remediation steps for each failed test")
        report.append("4. Re-run validation suite: `pytest tests/calibration_system/ -v`")
        report.append("5. Verify all tests pass locally before pushing")
        report.append("")
        report.append("## Support")
        report.append("")
        report.append("For assistance:")
        report.append("- Review test source code in `tests/calibration_system/`")
        report.append("- Check calibration documentation in `AGENTS.md`")
        report.append("- Examine test output artifacts for detailed error messages")
    
    return "\n".join(report)


def main():
    """Main entry point"""
    args = parse_args()
    report = generate_report(args)
    
    output_path = Path(args.output)
    output_path.write_text(report)
    
    print(f"✓ Generated failure report: {output_path}")


if __name__ == "__main__":
    main()
