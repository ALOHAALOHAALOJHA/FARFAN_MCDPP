#!/usr/bin/env python3
"""
Validation script for PDET policy area enrichment.

This script validates that all policy areas have been properly enriched
with PDET municipality context and that all four validation gates are compliant.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def validate_policy_area_enrichment(pa_dir: Path) -> Dict[str, Any]:
    """Validate PDET enrichment for a single policy area."""
    metadata_path = pa_dir / "metadata.json"
    keywords_path = pa_dir / "keywords.json"

    results = {"policy_area": pa_dir.name, "valid": False, "checks": {}, "warnings": []}

    # Check 1: metadata.json exists
    if not metadata_path.exists():
        results["checks"]["metadata_exists"] = False
        return results
    results["checks"]["metadata_exists"] = True

    # Load metadata
    with open(metadata_path) as f:
        metadata = json.load(f)

    # Check 2: pdet_enrichment field exists
    if "pdet_enrichment" not in metadata:
        results["checks"]["pdet_enrichment_exists"] = False
        return results
    results["checks"]["pdet_enrichment_exists"] = True

    pdet = metadata["pdet_enrichment"]

    # Check 3: All four validation gates present
    gates = pdet.get("_validation_gates", {})
    required_gates = ["gate_1_scope", "gate_2_value_add", "gate_3_capability", "gate_4_channel"]
    gates_present = {gate: gate in gates for gate in required_gates}
    results["checks"]["gates_present"] = all(gates_present.values())

    if not results["checks"]["gates_present"]:
        missing_gates = [g for g, present in gates_present.items() if not present]
        results["warnings"].append(f"Missing gates: {missing_gates}")

    # Check 4: PDET context has required fields
    context = pdet.get("pdet_context", {})
    context_checks = {
        "has_subregions": len(context.get("relevant_subregions", [])) > 0,
        "has_pillars": len(context.get("pdet_pillars", [])) > 0,
        "has_indicators": len(context.get("key_indicators", [])) > 0,
        "has_territorial_coverage": "territorial_coverage" in context,
        "has_legal_basis": "legal_basis" in context,
    }
    results["checks"]["pdet_context"] = all(context_checks.values())

    if not results["checks"]["pdet_context"]:
        missing_fields = [f for f, present in context_checks.items() if not present]
        results["warnings"].append(f"Incomplete PDET context: {missing_fields}")

    # Check 5: Quality assurance verification
    qa = pdet.get("quality_assurance", {})
    qa_checks = {
        "gate_compliance_verified": qa.get("gate_compliance_verified", False),
        "all_gates_passed": qa.get("all_gates_passed", False),
        "compliance_score": qa.get("compliance_score", 0) == 1.0,
    }
    results["checks"]["quality_assurance"] = all(qa_checks.values())

    if not results["checks"]["quality_assurance"]:
        failing_qa = [q for q, status in qa_checks.items() if not status]
        results["warnings"].append(f"QA issues: {failing_qa}")

    # Check 6: Gate 1 - Scope validity
    gate1 = gates.get("gate_1_scope", {})
    gate1_valid = (
        gate1.get("required_scope") == "pdet_context"
        and "ENRICHMENT_DATA" in gate1.get("allowed_signal_types", [])
        and gate1.get("min_confidence", 0) >= 0.75
    )
    results["checks"]["gate_1_valid"] = gate1_valid

    # Check 7: Gate 2 - Value contribution
    gate2 = gates.get("gate_2_value_add", {})
    gate2_valid = (
        gate2.get("estimated_value_add", 0) >= 0.10
        and len(gate2.get("enables", [])) > 0
        and len(gate2.get("optimizes", [])) > 0
    )
    results["checks"]["gate_2_valid"] = gate2_valid

    # Check 8: Gate 3 - Capability requirements
    gate3 = gates.get("gate_3_capability", {})
    required_capabilities = gate3.get("required_capabilities", [])
    gate3_valid = (
        "SEMANTIC_PROCESSING" in required_capabilities and "TABLE_PARSING" in required_capabilities
    )
    results["checks"]["gate_3_valid"] = gate3_valid

    # Check 9: Gate 4 - Channel integrity
    gate4 = gates.get("gate_4_channel", {})
    gate4_valid = (
        gate4.get("is_explicit", False)
        and gate4.get("is_documented", False)
        and gate4.get("is_traceable", False)
        and gate4.get("is_governed", False)
        and gate4.get("source") == "colombia_context.pdet_municipalities"
    )
    results["checks"]["gate_4_valid"] = gate4_valid

    # Check 10: Keywords enrichment
    if keywords_path.exists():
        with open(keywords_path) as f:
            keywords_data = json.load(f)
        results["checks"]["keywords_enriched"] = "_pdet_enrichment" in keywords_data
    else:
        results["checks"]["keywords_enriched"] = False
        results["warnings"].append("keywords.json not found")

    # Overall validation
    all_checks_passed = all(results["checks"].values())
    results["valid"] = all_checks_passed

    # Add summary data
    results["summary"] = {
        "subregion_count": len(context.get("relevant_subregions", [])),
        "pillar_count": len(context.get("pdet_pillars", [])),
        "indicator_count": len(context.get("key_indicators", [])),
        "policy_relevance": gate1.get("policy_area_relevance", "UNKNOWN"),
        "value_add": gate2.get("estimated_value_add", 0),
        "compliance_score": qa.get("compliance_score", 0),
    }

    return results


def main():
    """Run validation for all policy areas."""
    # Use relative path from script location
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    policy_areas_dir = repo_root / "canonic_questionnaire_central" / "policy_areas"

    if not policy_areas_dir.exists():
        print(f"Error: Policy areas directory not found at {policy_areas_dir}")
        print("Please run this script from the repository root or scripts directory.")
        return 1

    print("=" * 80)
    print("PDET Policy Area Enrichment Validation")
    print("=" * 80)
    print()

    # Find all policy area directories
    pa_dirs = sorted(
        [d for d in policy_areas_dir.iterdir() if d.is_dir() and d.name.startswith("PA")]
    )

    all_results = []
    passed_count = 0
    failed_count = 0

    for pa_dir in pa_dirs:
        results = validate_policy_area_enrichment(pa_dir)
        all_results.append(results)

        if results["valid"]:
            passed_count += 1
            status = "✅ PASS"
        else:
            failed_count += 1
            status = "❌ FAIL"

        print(f"{status} - {results['policy_area']}")

        summary = results["summary"]
        print(f"  Subregions: {summary['subregion_count']}")
        print(f"  Pillars: {summary['pillar_count']}")
        print(f"  Indicators: {summary['indicator_count']}")
        print(f"  Relevance: {summary['policy_relevance']}")
        print(f"  Value Add: {summary['value_add']:.0%}")
        print(f"  Compliance: {summary['compliance_score']:.0%}")

        # Show check results
        checks = results["checks"]
        failed_checks = [check for check, passed in checks.items() if not passed]
        if failed_checks:
            print(f"  Failed checks: {', '.join(failed_checks)}")

        # Show warnings
        if results["warnings"]:
            for warning in results["warnings"]:
                print(f"  ⚠️  {warning}")

        print()

    print("=" * 80)
    print("Validation Summary")
    print("=" * 80)
    print(f"Total Policy Areas: {len(all_results)}")
    print(f"Passed: {passed_count} ({passed_count/len(all_results)*100:.1f}%)")
    print(f"Failed: {failed_count} ({failed_count/len(all_results)*100:.1f}%)")
    print()

    if failed_count == 0:
        print("✅ ALL POLICY AREAS SUCCESSFULLY ENRICHED")
        print()
        print("Four Validation Gates:")
        print("  ✅ Gate 1: Consumer Scope Validity")
        print("  ✅ Gate 2: Value Contribution")
        print("  ✅ Gate 3: Consumer Capability & Readiness")
        print("  ✅ Gate 4: Channel Authenticity & Integrity")
        print()
        print("All policy areas comply with the four-gate validation framework.")
        return 0
    else:
        print("❌ VALIDATION FAILED")
        print(f"{failed_count} policy area(s) require attention.")
        return 1


if __name__ == "__main__":
    exit(main())
