#!/usr/bin/env python3
"""
Fix output_contract.schema.properties const values in all 300 executor contracts.

Problem: All contracts have hardcoded const values from Q271/PA09.
Solution: Update const values to match identity section.

Also validates irrigation of empirical data from contract to Phase 2 nodes.
"""

import json
from pathlib import Path
from typing import Any
import hashlib


CONTRACTS_DIR = Path("src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized")


def fix_output_contract_const(contract: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """
    Fix output_contract.schema.properties const values to match identity.
    
    Returns:
        Tuple of (fixed_contract, list_of_changes)
    """
    changes = []
    identity = contract.get("identity", {})
    output_schema = contract.get("output_contract", {}).get("schema", {}).get("properties", {})
    
    # Fields to sync from identity to output_contract.schema.properties.*.const
    sync_map = {
        "question_id": "question_id",
        "base_slot": "base_slot",
        "question_global": "question_global",
        "policy_area_id": "policy_area_id",
        "dimension_id": "dimension_id",
        "cluster_id": "cluster_id",
    }
    
    for identity_field, schema_field in sync_map.items():
        identity_value = identity.get(identity_field)
        if schema_field in output_schema:
            current_const = output_schema[schema_field].get("const")
            if current_const != identity_value:
                changes.append(f"{schema_field}.const: {current_const} → {identity_value}")
                output_schema[schema_field]["const"] = identity_value
    
    return contract, changes


def validate_irrigation(contract: dict[str, Any]) -> dict[str, Any]:
    """
    Validate that all empirical data from contract flows to Phase 2 nodes.
    
    Returns dict with validation results.
    """
    results = {
        "contract_id": contract.get("identity", {}).get("question_id", "UNKNOWN"),
        "issues": [],
        "irrigation_score": 0,
        "max_score": 0,
    }
    
    # 1. Check patterns irrigation
    results["max_score"] += 1
    patterns = contract.get("question_context", {}).get("patterns", [])
    if patterns:
        results["irrigation_score"] += 1
        results["patterns_count"] = len(patterns)
    else:
        results["issues"].append("NO_PATTERNS: question_context.patterns is empty")
    
    # 2. Check expected_elements irrigation
    results["max_score"] += 1
    expected_elements = contract.get("question_context", {}).get("expected_elements", [])
    if expected_elements:
        results["irrigation_score"] += 1
        results["expected_elements_count"] = len(expected_elements)
    else:
        results["issues"].append("NO_EXPECTED_ELEMENTS: question_context.expected_elements is empty")
    
    # 3. Check validations irrigation
    results["max_score"] += 1
    validations = contract.get("question_context", {}).get("validations", {})
    if validations:
        results["irrigation_score"] += 1
        results["validations_count"] = len(validations)
    else:
        results["issues"].append("NO_VALIDATIONS: question_context.validations is empty")
    
    # 4. Check failure_contract irrigation
    results["max_score"] += 1
    failure_contract = contract.get("error_handling", {}).get("failure_contract", {})
    if failure_contract and failure_contract.get("abort_if"):
        results["irrigation_score"] += 1
        results["failure_contract_abort_conditions"] = len(failure_contract.get("abort_if", []))
    else:
        results["issues"].append("NO_FAILURE_CONTRACT: error_handling.failure_contract.abort_if is empty")
    
    # 5. Check assembly_rules irrigation
    results["max_score"] += 1
    assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
    if assembly_rules:
        results["irrigation_score"] += 1
        results["assembly_rules_count"] = len(assembly_rules)
    else:
        results["issues"].append("NO_ASSEMBLY_RULES: evidence_assembly.assembly_rules is empty")
    
    # 6. Check validation_rules irrigation
    results["max_score"] += 1
    validation_rules = contract.get("validation_rules", {}).get("rules", [])
    if validation_rules:
        results["irrigation_score"] += 1
        results["validation_rules_count"] = len(validation_rules)
    else:
        results["issues"].append("NO_VALIDATION_RULES: validation_rules.rules is empty")
    
    # 7. Check human_answer_structure has concrete_example
    results["max_score"] += 1
    concrete_example = contract.get("human_answer_structure", {}).get("concrete_example", {})
    if concrete_example:
        results["irrigation_score"] += 1
    else:
        results["issues"].append("NO_CONCRETE_EXAMPLE: human_answer_structure.concrete_example is empty")
    
    # 8. Check template_variable_bindings
    results["max_score"] += 1
    template_vars = contract.get("human_answer_structure", {}).get("template_variable_bindings", {}).get("variables", {})
    if template_vars:
        results["irrigation_score"] += 1
        results["template_variables_count"] = len(template_vars)
    else:
        results["issues"].append("NO_TEMPLATE_VARS: human_answer_structure.template_variable_bindings.variables is empty")
    
    # 9. Check method_binding has methods
    results["max_score"] += 1
    methods = contract.get("method_binding", {}).get("methods", [])
    if methods:
        results["irrigation_score"] += 1
        results["methods_count"] = len(methods)
    else:
        results["issues"].append("NO_METHODS: method_binding.methods is empty")
    
    # 10. Check human_readable_output template
    results["max_score"] += 1
    template = contract.get("output_contract", {}).get("human_readable_output", {}).get("template", {})
    if template:
        results["irrigation_score"] += 1
        results["template_sections"] = list(template.keys())
    else:
        results["issues"].append("NO_HR_TEMPLATE: output_contract.human_readable_output.template is empty")
    
    results["irrigation_percentage"] = round(results["irrigation_score"] / results["max_score"] * 100, 1)
    
    return results


def process_all_contracts(dry_run: bool = True) -> dict[str, Any]:
    """
    Process all 300 contracts: fix const values and validate irrigation.
    """
    contract_files = sorted(CONTRACTS_DIR.glob("Q*.v3.json"))
    
    report = {
        "total_contracts": len(contract_files),
        "contracts_fixed": 0,
        "contracts_with_issues": 0,
        "all_changes": [],
        "irrigation_summary": {
            "perfect": 0,
            "good": 0,
            "needs_work": 0,
            "broken": 0,
        },
        "common_issues": {},
        "dry_run": dry_run,
    }
    
    for contract_path in contract_files:
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        
        question_id = contract.get("identity", {}).get("question_id", contract_path.stem)
        
        # Fix const values
        fixed_contract, changes = fix_output_contract_const(contract)
        
        if changes:
            report["contracts_fixed"] += 1
            report["all_changes"].append({
                "file": contract_path.name,
                "question_id": question_id,
                "changes": changes,
            })
            
            if not dry_run:
                with open(contract_path, "w", encoding="utf-8") as f:
                    json.dump(fixed_contract, f, indent=2, ensure_ascii=False)
        
        # Validate irrigation
        irrigation = validate_irrigation(contract)
        
        if irrigation["issues"]:
            report["contracts_with_issues"] += 1
            for issue in irrigation["issues"]:
                issue_type = issue.split(":")[0]
                report["common_issues"][issue_type] = report["common_issues"].get(issue_type, 0) + 1
        
        # Categorize irrigation quality
        pct = irrigation["irrigation_percentage"]
        if pct == 100:
            report["irrigation_summary"]["perfect"] += 1
        elif pct >= 80:
            report["irrigation_summary"]["good"] += 1
        elif pct >= 50:
            report["irrigation_summary"]["needs_work"] += 1
        else:
            report["irrigation_summary"]["broken"] += 1
    
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix and validate executor contracts")
    parser.add_argument("--fix", action="store_true", help="Actually fix files (default: dry run)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all changes")
    args = parser.parse_args()
    
    print("=" * 70)
    print("EXECUTOR CONTRACT AUDIT & FIX")
    print("=" * 70)
    
    report = process_all_contracts(dry_run=not args.fix)
    
    print(f"\n📊 SUMMARY")
    print(f"   Total contracts: {report['total_contracts']}")
    print(f"   Contracts needing fix: {report['contracts_fixed']}")
    print(f"   Contracts with irrigation issues: {report['contracts_with_issues']}")
    print(f"   Mode: {'DRY RUN' if report['dry_run'] else 'APPLIED FIXES'}")
    
    print(f"\n📈 IRRIGATION QUALITY")
    print(f"   Perfect (100%): {report['irrigation_summary']['perfect']}")
    print(f"   Good (80-99%): {report['irrigation_summary']['good']}")
    print(f"   Needs work (50-79%): {report['irrigation_summary']['needs_work']}")
    print(f"   Broken (<50%): {report['irrigation_summary']['broken']}")
    
    if report["common_issues"]:
        print(f"\n⚠️  COMMON ISSUES")
        for issue, count in sorted(report["common_issues"].items(), key=lambda x: -x[1]):
            print(f"   {issue}: {count} contracts")
    
    if args.verbose and report["all_changes"]:
        print(f"\n📝 CHANGES {'TO APPLY' if report['dry_run'] else 'APPLIED'}")
        for change in report["all_changes"][:10]:  # Show first 10
            print(f"   {change['file']}: {', '.join(change['changes'])}")
        if len(report["all_changes"]) > 10:
            print(f"   ... and {len(report['all_changes']) - 10} more")
    
    if report["dry_run"] and report["contracts_fixed"] > 0:
        print(f"\n💡 Run with --fix to apply changes")
    
    return report


if __name__ == "__main__":
    main()
