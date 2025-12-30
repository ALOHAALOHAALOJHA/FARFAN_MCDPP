#!/usr/bin/env python3
"""
Comprehensive Audit for Executor Contracts V3 (Q001-Q020)
Validates structure, completeness, method bindings, and CQVR compliance.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

# Critical contract fields per architecture
REQUIRED_FIELDS = [
    "contract_id", "contract_version", "question_id", "policy_area",
    "expected_evidence_type", "method_binding", "cqvr_framework",
    "validation_rules", "output_format"
]

REQUIRED_METHOD_BINDING_FIELDS = ["strategy", "methods", "fallback_chain"]
REQUIRED_CQVR_FIELDS = ["credibilidad", "qualidad", "vigencia", "relevancia"]
REQUIRED_OUTPUT_FORMAT_FIELDS = ["primary_metric", "secondary_metrics", "aggregation_strategy"]

def load_contract(contract_path: Path) -> Dict[str, Any]:
    """Load and parse contract JSON."""
    with open(contract_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def audit_contract_structure(contract: Dict[str, Any], contract_id: str) -> Dict[str, Any]:
    """Audit basic structure and required fields."""
    issues = []
    warnings = []
    
    # Check required top-level fields
    missing_fields = [f for f in REQUIRED_FIELDS if f not in contract]
    if missing_fields:
        issues.append(f"Missing required fields: {missing_fields}")
    
    # Validate contract_id matches filename
    if contract.get("contract_id") != contract_id:
        issues.append(f"contract_id mismatch: {contract.get('contract_id')} != {contract_id}")
    
    # Validate version is v3
    if contract.get("contract_version") != "v3":
        issues.append(f"Wrong version: {contract.get('contract_version')} (expected v3)")
    
    # Check question_id format
    question_id = contract.get("question_id", "")
    if not question_id.startswith("Q") or len(question_id) < 4:
        issues.append(f"Invalid question_id format: {question_id}")
    
    return {"issues": issues, "warnings": warnings}

def audit_method_binding(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit method_binding section."""
    issues = []
    warnings = []
    
    method_binding = contract.get("method_binding", {})
    
    # Check required fields
    missing_fields = [f for f in REQUIRED_METHOD_BINDING_FIELDS if f not in method_binding]
    if missing_fields:
        issues.append(f"method_binding missing: {missing_fields}")
    
    # Validate strategy
    strategy = method_binding.get("strategy")
    valid_strategies = ["single", "parallel", "sequential", "adaptive"]
    if strategy not in valid_strategies:
        issues.append(f"Invalid strategy: {strategy} (valid: {valid_strategies})")
    
    # Validate methods list
    methods = method_binding.get("methods", [])
    if not methods:
        issues.append("No methods defined in method_binding.methods")
    elif not isinstance(methods, list):
        issues.append(f"methods must be a list, got {type(methods)}")
    else:
        # Check each method has required fields
        for idx, method in enumerate(methods):
            if not isinstance(method, dict):
                issues.append(f"Method {idx} is not a dict")
                continue
            
            if "method_id" not in method:
                issues.append(f"Method {idx} missing method_id")
            if "weight" not in method:
                warnings.append(f"Method {idx} missing weight")
            
            # Validate weight is numeric
            if "weight" in method:
                try:
                    weight = float(method["weight"])
                    if not (0 <= weight <= 1):
                        warnings.append(f"Method {method.get('method_id')} weight {weight} outside [0,1]")
                except (ValueError, TypeError):
                    issues.append(f"Method {method.get('method_id')} has non-numeric weight")
    
    # Validate fallback_chain
    fallback = method_binding.get("fallback_chain", [])
    if not isinstance(fallback, list):
        issues.append(f"fallback_chain must be a list, got {type(fallback)}")
    
    return {"issues": issues, "warnings": warnings}

def audit_cqvr_framework(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit CQVR framework compliance."""
    issues = []
    warnings = []
    
    cqvr = contract.get("cqvr_framework", {})
    
    # Check required CQVR dimensions
    missing_dims = [d for d in REQUIRED_CQVR_FIELDS if d not in cqvr]
    if missing_dims:
        issues.append(f"Missing CQVR dimensions: {missing_dims}")
    
    # Validate each dimension has threshold and weight
    for dim in REQUIRED_CQVR_FIELDS:
        if dim in cqvr:
            dim_config = cqvr[dim]
            if not isinstance(dim_config, dict):
                issues.append(f"CQVR.{dim} must be dict, got {type(dim_config)}")
                continue
            
            if "threshold" not in dim_config:
                warnings.append(f"CQVR.{dim} missing threshold")
            if "weight" not in dim_config:
                warnings.append(f"CQVR.{dim} missing weight")
            
            # Validate threshold range
            if "threshold" in dim_config:
                try:
                    thresh = float(dim_config["threshold"])
                    if not (0 <= thresh <= 1):
                        warnings.append(f"CQVR.{dim} threshold {thresh} outside [0,1]")
                except (ValueError, TypeError):
                    issues.append(f"CQVR.{dim} threshold is not numeric")
    
    # Check if weights sum to ~1.0
    if all(d in cqvr for d in REQUIRED_CQVR_FIELDS):
        try:
            weights = [float(cqvr[d].get("weight", 0)) for d in REQUIRED_CQVR_FIELDS]
            total_weight = sum(weights)
            if abs(total_weight - 1.0) > 0.01:
                warnings.append(f"CQVR weights sum to {total_weight:.3f} (expected ~1.0)")
        except (ValueError, TypeError):
            pass
    
    return {"issues": issues, "warnings": warnings}

def audit_validation_rules(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit validation_rules section."""
    issues = []
    warnings = []
    
    validation = contract.get("validation_rules", {})
    
    if not validation:
        warnings.append("No validation_rules defined")
        return {"issues": issues, "warnings": warnings}
    
    # Check for common validation fields
    expected_fields = ["min_evidence_count", "required_fields", "data_quality_checks"]
    present_fields = [f for f in expected_fields if f in validation]
    
    if not present_fields:
        warnings.append(f"No standard validation fields found ({expected_fields})")
    
    # Validate min_evidence_count if present
    if "min_evidence_count" in validation:
        try:
            min_count = int(validation["min_evidence_count"])
            if min_count < 0:
                issues.append(f"min_evidence_count {min_count} is negative")
        except (ValueError, TypeError):
            issues.append("min_evidence_count is not an integer")
    
    return {"issues": issues, "warnings": warnings}

def audit_output_format(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit output_format section."""
    issues = []
    warnings = []
    
    output_fmt = contract.get("output_format", {})
    
    # Check required fields
    missing_fields = [f for f in REQUIRED_OUTPUT_FORMAT_FIELDS if f not in output_fmt]
    if missing_fields:
        issues.append(f"output_format missing: {missing_fields}")
    
    # Validate aggregation_strategy
    aggregation = output_fmt.get("aggregation_strategy")
    valid_strategies = ["weighted_average", "max", "min", "bayesian_fusion", "ensemble"]
    if aggregation and aggregation not in valid_strategies:
        warnings.append(f"Unusual aggregation_strategy: {aggregation}")
    
    return {"issues": issues, "warnings": warnings}

def audit_single_contract(contract_path: Path) -> Dict[str, Any]:
    """Perform comprehensive audit of a single contract."""
    contract_id = contract_path.stem  # e.g., "Q001.v3"
    
    try:
        contract = load_contract(contract_path)
    except json.JSONDecodeError as e:
        return {
            "contract_id": contract_id,
            "status": "CRITICAL",
            "error": f"JSON parse error: {e}",
            "issues": [],
            "warnings": []
        }
    except Exception as e:
        return {
            "contract_id": contract_id,
            "status": "CRITICAL",
            "error": f"Failed to load: {e}",
            "issues": [],
            "warnings": []
        }
    
    # Run all audit checks
    all_issues = []
    all_warnings = []
    
    # Structure audit
    struct_result = audit_contract_structure(contract, contract_id)
    all_issues.extend(struct_result["issues"])
    all_warnings.extend(struct_result["warnings"])
    
    # Method binding audit
    method_result = audit_method_binding(contract)
    all_issues.extend([f"method_binding: {i}" for i in method_result["issues"]])
    all_warnings.extend([f"method_binding: {w}" for w in method_result["warnings"]])
    
    # CQVR audit
    cqvr_result = audit_cqvr_framework(contract)
    all_issues.extend([f"CQVR: {i}" for i in cqvr_result["issues"]])
    all_warnings.extend([f"CQVR: {w}" for w in cqvr_result["warnings"]])
    
    # Validation rules audit
    valid_result = audit_validation_rules(contract)
    all_issues.extend([f"validation: {i}" for i in valid_result["issues"]])
    all_warnings.extend([f"validation: {w}" for w in valid_result["warnings"]])
    
    # Output format audit
    output_result = audit_output_format(contract)
    all_issues.extend([f"output_format: {i}" for i in output_result["issues"]])
    all_warnings.extend([f"output_format: {w}" for w in output_result["warnings"]])
    
    # Determine status
    if all_issues:
        status = "FAIL"
    elif all_warnings:
        status = "WARN"
    else:
        status = "PASS"
    
    return {
        "contract_id": contract_id,
        "status": status,
        "issues": all_issues,
        "warnings": all_warnings,
        "method_count": len(contract.get("method_binding", {}).get("methods", [])),
        "policy_area": contract.get("policy_area", "UNKNOWN"),
        "question_id": contract.get("question_id", "UNKNOWN")
    }

def generate_summary_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics from audit results."""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    critical = sum(1 for r in results if r["status"] == "CRITICAL")
    
    # Collect all unique issues
    all_issues = defaultdict(int)
    for result in results:
        for issue in result.get("issues", []):
            all_issues[issue] += 1
    
    all_warnings = defaultdict(int)
    for result in results:
        for warning in result.get("warnings", []):
            all_warnings[warning] += 1
    
    return {
        "total_contracts": total,
        "passed": passed,
        "warned": warned,
        "failed": failed,
        "critical": critical,
        "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
        "common_issues": dict(sorted(all_issues.items(), key=lambda x: x[1], reverse=True)[:10]),
        "common_warnings": dict(sorted(all_warnings.items(), key=lambda x: x[1], reverse=True)[:10])
    }

def main():
    """Main audit execution."""
    contracts_dir = Path("src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized")
    
    if not contracts_dir.exists():
        print(f"ERROR: Contracts directory not found: {contracts_dir}")
        return
    
    # Audit Q001-Q020
    results = []
    for i in range(1, 21):
        contract_file = contracts_dir / f"Q{i:03d}.v3.json"
        if contract_file.exists():
            print(f"Auditing {contract_file.name}...", end=" ")
            result = audit_single_contract(contract_file)
            results.append(result)
            print(result["status"])
        else:
            print(f"MISSING: {contract_file.name}")
            results.append({
                "contract_id": f"Q{i:03d}.v3",
                "status": "CRITICAL",
                "error": "File not found",
                "issues": [],
                "warnings": []
            })
    
    # Generate summary
    summary = generate_summary_report(results)
    
    # Generate detailed report
    report = {
        "audit_metadata": {
            "audit_type": "Executor Contracts V3 Audit",
            "scope": "Q001-Q020",
            "total_contracts": len(results)
        },
        "summary": summary,
        "detailed_results": results
    }
    
    # Save report
    output_path = Path("audit_contracts_v3_q001_q020_report.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    print(f"Total Contracts: {summary['total_contracts']}")
    print(f"PASSED: {summary['passed']} ({summary['pass_rate']})")
    print(f"WARNED: {summary['warned']}")
    print(f"FAILED: {summary['failed']}")
    print(f"CRITICAL: {summary['critical']}")
    
    if summary['common_issues']:
        print("\nMost Common Issues:")
        for issue, count in list(summary['common_issues'].items())[:5]:
            print(f"  [{count}x] {issue}")
    
    if summary['common_warnings']:
        print("\nMost Common Warnings:")
        for warning, count in list(summary['common_warnings'].items())[:5]:
            print(f"  [{count}x] {warning}")
    
    print(f"\nDetailed report saved to: {output_path}")
    
    # Print detailed results for failed contracts
    failed_contracts = [r for r in results if r["status"] in ["FAIL", "CRITICAL"]]
    if failed_contracts:
        print("\n" + "="*80)
        print("FAILED CONTRACTS DETAILS")
        print("="*80)
        for result in failed_contracts:
            print(f"\n{result['contract_id']} - {result['status']}")
            if "error" in result:
                print(f"  ERROR: {result['error']}")
            if result.get("issues"):
                print("  Issues:")
                for issue in result["issues"]:
                    print(f"    - {issue}")

if __name__ == "__main__":
    main()
