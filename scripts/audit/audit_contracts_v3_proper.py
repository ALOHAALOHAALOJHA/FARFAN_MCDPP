#!/usr/bin/env python3
"""
Comprehensive Audit for Executor Contracts V3 (Q001-Q020)
Adapted for actual V3 contract structure with identity/executor_binding/method_binding format.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

# V3 Contract Structure - top-level sections
REQUIRED_V3_SECTIONS = [
    "identity", "executor_binding", "method_binding", "question_context",
    "signal_requirements", "evidence_assembly", "output_contract",
    "validation_rules", "human_answer_structure", "traceability"
]

# identity section required fields
REQUIRED_IDENTITY_FIELDS = [
    "base_slot", "question_id", "dimension_id", "policy_area_id",
    "contract_version", "contract_hash", "question_global"
]

# method_binding required fields
REQUIRED_METHOD_BINDING_FIELDS = ["orchestration_mode", "method_count", "methods"]

def load_contract(contract_path: Path) -> Dict[str, Any]:
    """Load and parse contract JSON."""
    with open(contract_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def audit_json_validity(contract_path: Path) -> Dict[str, Any]:
    """Check if JSON is valid."""
    try:
        with open(contract_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return {"valid": True, "error": None}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Line {e.lineno}, Col {e.colno}: {e.msg}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def audit_contract_structure(contract: Dict[str, Any], contract_id: str) -> Dict[str, Any]:
    """Audit V3 contract structure."""
    issues = []
    warnings = []
    
    # Check top-level sections
    missing_sections = [s for s in REQUIRED_V3_SECTIONS if s not in contract]
    if missing_sections:
        issues.append(f"Missing top-level sections: {missing_sections}")
    
    # Audit identity section
    identity = contract.get("identity", {})
    if identity:
        missing_identity = [f for f in REQUIRED_IDENTITY_FIELDS if f not in identity]
        if missing_identity:
            issues.append(f"identity missing fields: {missing_identity}")
        
        # Validate question_id
        q_id = identity.get("question_id", "")
        expected_q_id = contract_id.split(".")[0]  # Q001 from Q001.v3
        if q_id != expected_q_id:
            issues.append(f"question_id mismatch: {q_id} != {expected_q_id}")
        
        # Validate version format
        version = identity.get("contract_version", "")
        if not version.startswith("3."):
            warnings.append(f"Unexpected version format: {version} (expected 3.x.x)")
    else:
        issues.append("identity section is empty or missing")
    
    # Audit executor_binding
    executor_binding = contract.get("executor_binding", {})
    if executor_binding:
        if "executor_class" not in executor_binding:
            warnings.append("executor_binding missing executor_class")
        if "executor_module" not in executor_binding:
            warnings.append("executor_binding missing executor_module")
    else:
        warnings.append("executor_binding section is empty")
    
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
    
    # Validate orchestration_mode
    orchestration = method_binding.get("orchestration_mode")
    valid_modes = ["multi_method_pipeline", "single_method", "parallel", "sequential"]
    if orchestration and orchestration not in valid_modes:
        warnings.append(f"Unusual orchestration_mode: {orchestration}")
    
    # Validate methods
    methods = method_binding.get("methods", [])
    method_count = method_binding.get("method_count", 0)
    
    if not methods:
        issues.append("No methods defined")
    elif not isinstance(methods, list):
        issues.append(f"methods must be a list, got {type(methods)}")
    else:
        # Check count consistency
        if len(methods) != method_count:
            issues.append(f"method_count mismatch: declared {method_count}, actual {len(methods)}")
        
        # Check method structure
        for idx, method in enumerate(methods):
            if not isinstance(method, dict):
                issues.append(f"Method {idx} is not a dict")
                continue
            
            # Required method fields
            required_method_fields = ["class_name", "method_name", "priority", "provides", "role"]
            missing_method_fields = [f for f in required_method_fields if f not in method]
            if missing_method_fields:
                issues.append(f"Method {idx} ({method.get('method_name', 'unknown')}) missing: {missing_method_fields}")
            
            # Check priority is numeric and unique
            if "priority" in method:
                try:
                    priority = int(method["priority"])
                    if priority < 1:
                        warnings.append(f"Method {idx} has priority {priority} < 1")
                except (ValueError, TypeError):
                    issues.append(f"Method {idx} priority is not an integer")
        
        # Check for duplicate priorities
        priorities = [m.get("priority") for m in methods if "priority" in m]
        if len(priorities) != len(set(priorities)):
            warnings.append(f"Duplicate priorities found: {sorted(priorities)}")
    
    return {"issues": issues, "warnings": warnings}

def audit_question_context(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit question_context section."""
    issues = []
    warnings = []
    
    context = contract.get("question_context", {})
    
    if not context:
        warnings.append("question_context is empty")
        return {"issues": issues, "warnings": warnings}
    
    # Expected fields
    expected_fields = ["base_question", "policy_area", "dimension", "cluster"]
    missing = [f for f in expected_fields if f not in context]
    if missing:
        warnings.append(f"question_context missing optional fields: {missing}")
    
    # Check base_question content
    base_q = context.get("base_question", {})
    if base_q and not base_q.get("text"):
        warnings.append("base_question missing text content")
    
    return {"issues": issues, "warnings": warnings}

def audit_signal_requirements(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit signal_requirements section."""
    issues = []
    warnings = []
    
    signals = contract.get("signal_requirements", {})
    
    if not signals:
        warnings.append("signal_requirements is empty")
        return {"issues": issues, "warnings": warnings}
    
    # Check required_signals
    required_signals = signals.get("required_signals", [])
    if not required_signals:
        warnings.append("No required_signals defined")
    elif not isinstance(required_signals, list):
        issues.append(f"required_signals must be a list, got {type(required_signals)}")
    
    # Check optional_signals
    optional_signals = signals.get("optional_signals", [])
    if optional_signals and not isinstance(optional_signals, list):
        issues.append(f"optional_signals must be a list, got {type(optional_signals)}")
    
    return {"issues": issues, "warnings": warnings}

def audit_evidence_assembly(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit evidence_assembly section."""
    issues = []
    warnings = []
    
    evidence = contract.get("evidence_assembly", {})
    
    if not evidence:
        warnings.append("evidence_assembly is empty")
        return {"issues": issues, "warnings": warnings}
    
    # Check for key fields
    if "strategy" not in evidence:
        warnings.append("evidence_assembly missing strategy")
    
    if "aggregation_logic" not in evidence:
        warnings.append("evidence_assembly missing aggregation_logic")
    
    return {"issues": issues, "warnings": warnings}

def audit_output_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit output_contract section."""
    issues = []
    warnings = []
    
    output = contract.get("output_contract", {})
    
    if not output:
        warnings.append("output_contract is empty")
        return {"issues": issues, "warnings": warnings}
    
    # Check required output fields
    expected_fields = ["format", "required_keys", "optional_keys"]
    missing = [f for f in expected_fields if f not in output]
    if missing:
        warnings.append(f"output_contract missing: {missing}")
    
    # Validate required_keys
    required_keys = output.get("required_keys", [])
    if not required_keys:
        warnings.append("No required_keys in output_contract")
    elif not isinstance(required_keys, list):
        issues.append(f"required_keys must be a list, got {type(required_keys)}")
    
    return {"issues": issues, "warnings": warnings}

def audit_validation_rules(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit validation_rules section."""
    issues = []
    warnings = []
    
    validation = contract.get("validation_rules", {})
    
    if not validation:
        warnings.append("validation_rules is empty")
        return {"issues": issues, "warnings": warnings}
    
    # Check for common validation fields
    if "min_methods_required" not in validation:
        warnings.append("validation_rules missing min_methods_required")
    
    if "output_validation" not in validation:
        warnings.append("validation_rules missing output_validation")
    
    return {"issues": issues, "warnings": warnings}

def audit_traceability(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Audit traceability section."""
    issues = []
    warnings = []
    
    trace = contract.get("traceability", {})
    
    if not trace:
        warnings.append("traceability section is empty")
        return {"issues": issues, "warnings": warnings}
    
    # Check logging configuration
    if "logging" not in trace:
        warnings.append("traceability missing logging configuration")
    
    return {"issues": issues, "warnings": warnings}

def audit_single_contract(contract_path: Path) -> Dict[str, Any]:
    """Perform comprehensive audit of a single V3 contract."""
    contract_id = contract_path.stem  # e.g., "Q001.v3"
    
    # First check JSON validity
    json_validity = audit_json_validity(contract_path)
    if not json_validity["valid"]:
        return {
            "contract_id": contract_id,
            "status": "CRITICAL",
            "error": f"JSON SYNTAX ERROR: {json_validity['error']}",
            "issues": [],
            "warnings": [],
            "details": {}
        }
    
    # Load contract
    try:
        contract = load_contract(contract_path)
    except Exception as e:
        return {
            "contract_id": contract_id,
            "status": "CRITICAL",
            "error": f"Failed to load: {e}",
            "issues": [],
            "warnings": [],
            "details": {}
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
    
    # Question context audit
    context_result = audit_question_context(contract)
    all_issues.extend([f"question_context: {i}" for i in context_result["issues"]])
    all_warnings.extend([f"question_context: {w}" for w in context_result["warnings"]])
    
    # Signal requirements audit
    signal_result = audit_signal_requirements(contract)
    all_issues.extend([f"signal_requirements: {i}" for i in signal_result["issues"]])
    all_warnings.extend([f"signal_requirements: {w}" for w in signal_result["warnings"]])
    
    # Evidence assembly audit
    evidence_result = audit_evidence_assembly(contract)
    all_issues.extend([f"evidence_assembly: {i}" for i in evidence_result["issues"]])
    all_warnings.extend([f"evidence_assembly: {w}" for w in evidence_result["warnings"]])
    
    # Output contract audit
    output_result = audit_output_contract(contract)
    all_issues.extend([f"output_contract: {i}" for i in output_result["issues"]])
    all_warnings.extend([f"output_contract: {w}" for w in output_result["warnings"]])
    
    # Validation rules audit
    valid_result = audit_validation_rules(contract)
    all_issues.extend([f"validation: {i}" for i in valid_result["issues"]])
    all_warnings.extend([f"validation: {w}" for w in valid_result["warnings"]])
    
    # Traceability audit
    trace_result = audit_traceability(contract)
    all_issues.extend([f"traceability: {i}" for i in trace_result["issues"]])
    all_warnings.extend([f"traceability: {w}" for w in trace_result["warnings"]])
    
    # Determine status
    if all_issues:
        status = "FAIL"
    elif all_warnings:
        status = "WARN"
    else:
        status = "PASS"
    
    # Collect details
    identity = contract.get("identity", {})
    method_binding = contract.get("method_binding", {})
    
    return {
        "contract_id": contract_id,
        "status": status,
        "issues": all_issues,
        "warnings": all_warnings,
        "details": {
            "question_id": identity.get("question_id", "UNKNOWN"),
            "policy_area_id": identity.get("policy_area_id", "UNKNOWN"),
            "dimension_id": identity.get("dimension_id", "UNKNOWN"),
            "contract_version": identity.get("contract_version", "UNKNOWN"),
            "method_count": method_binding.get("method_count", 0),
            "orchestration_mode": method_binding.get("orchestration_mode", "UNKNOWN"),
            "has_all_sections": all(s in contract for s in REQUIRED_V3_SECTIONS)
        }
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
    
    # Collect version info
    versions = defaultdict(int)
    for result in results:
        version = result.get("details", {}).get("contract_version", "UNKNOWN")
        versions[version] += 1
    
    # Collect method counts
    method_counts = [result.get("details", {}).get("method_count", 0) for result in results]
    avg_methods = sum(method_counts) / len(method_counts) if method_counts else 0
    
    return {
        "total_contracts": total,
        "passed": passed,
        "warned": warned,
        "failed": failed,
        "critical": critical,
        "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
        "contract_versions": dict(versions),
        "avg_method_count": f"{avg_methods:.1f}",
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
    print("\n" + "="*80)
    print("AUDITING EXECUTOR CONTRACTS V3: Q001-Q020")
    print("="*80 + "\n")
    
    for i in range(1, 21):
        contract_file = contracts_dir / f"Q{i:03d}.v3.json"
        if contract_file.exists():
            print(f"[{i:02d}/20] Auditing {contract_file.name}...", end=" ")
            result = audit_single_contract(contract_file)
            results.append(result)
            
            # Status indicator
            status_symbol = {
                "PASS": "✓",
                "WARN": "⚠",
                "FAIL": "✗",
                "CRITICAL": "☠"
            }
            print(f"{status_symbol.get(result['status'], '?')} {result['status']}")
        else:
            print(f"[{i:02d}/20] MISSING: {contract_file.name}")
            results.append({
                "contract_id": f"Q{i:03d}.v3",
                "status": "CRITICAL",
                "error": "File not found",
                "issues": [],
                "warnings": [],
                "details": {}
            })
    
    # Generate summary
    summary = generate_summary_report(results)
    
    # Generate detailed report
    report = {
        "audit_metadata": {
            "audit_type": "Executor Contracts V3 Audit (Proper Structure)",
            "scope": "Q001-Q020",
            "total_contracts": len(results),
            "audit_date": "2025-12-14"
        },
        "summary": summary,
        "detailed_results": results
    }
    
    # Save report
    output_path = Path("AUDIT_CONTRACTS_V3_Q001_Q020_DETAILED.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    print(f"Total Contracts:     {summary['total_contracts']}")
    print(f"✓ PASSED:            {summary['passed']} contracts ({summary['pass_rate']})")
    print(f"⚠ WARNINGS:          {summary['warned']} contracts")
    print(f"✗ FAILED:            {summary['failed']} contracts")
    print(f"☠ CRITICAL:          {summary['critical']} contracts")
    print(f"\nAverage Methods:     {summary['avg_method_count']}")
    print(f"Contract Versions:   {', '.join(f'{v}({c})' for v, c in summary['contract_versions'].items())}")
    
    if summary['common_issues']:
        print("\n" + "-"*80)
        print("TOP ISSUES:")
        print("-"*80)
        for issue, count in list(summary['common_issues'].items())[:5]:
            print(f"  [{count:2d}x] {issue}")
    
    if summary['common_warnings']:
        print("\n" + "-"*80)
        print("TOP WARNINGS:")
        print("-"*80)
        for warning, count in list(summary['common_warnings'].items())[:5]:
            print(f"  [{count:2d}x] {warning}")
    
    print(f"\n{'='*80}")
    print(f"Full detailed report saved to: {output_path}")
    print("="*80 + "\n")
    
    # Print critical/failed contracts details
    problematic = [r for r in results if r["status"] in ["FAIL", "CRITICAL"]]
    if problematic:
        print("\n" + "="*80)
        print(f"PROBLEMATIC CONTRACTS DETAILS ({len(problematic)} contracts)")
        print("="*80)
        for result in problematic:
            print(f"\n📄 {result['contract_id']} - {result['status']}")
            if "error" in result:
                print(f"   ⚠️  ERROR: {result['error']}")
            if result.get("issues"):
                print(f"   Issues ({len(result['issues'])}):")
                for issue in result["issues"][:5]:  # Show first 5
                    print(f"      • {issue}")
                if len(result["issues"]) > 5:
                    print(f"      ... and {len(result['issues']) - 5} more")

if __name__ == "__main__":
    main()
