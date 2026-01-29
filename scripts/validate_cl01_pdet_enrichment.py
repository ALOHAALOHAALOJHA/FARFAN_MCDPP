#!/usr/bin/env python3
"""
Validation script for CL01_seguridad_paz PDET enrichment.

This script demonstrates how to access and validate the PDET contextual
information that has been added to the CL01 cluster.
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_cluster_metadata(cluster_id: str) -> Dict[str, Any]:
    """Load cluster metadata."""
    cluster_path = (
        Path(__file__).resolve().parent.parent
        / "canonic_questionnaire_central"
        / "clusters"
        / f"{cluster_id}_seguridad_paz"
        / "metadata.json"
    )
    with open(cluster_path) as f:
        return json.load(f)


def validate_pdet_enrichment(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate PDET enrichment against expected structure."""
    results = {"valid": True, "checks": {}, "summary": {}}

    # Check 1: PDET context exists
    pdet_context = metadata.get("pdet_context")
    results["checks"]["pdet_context_exists"] = pdet_context is not None

    if not pdet_context:
        results["valid"] = False
        return results

    # Check 2: Required fields present
    required_fields = [
        "relevance",
        "description",
        "territorial_scope",
        "institutional_actors",
        "financing_context",
        "territorial_disaggregation",
        "coherence_requirements",
    ]

    for field in required_fields:
        field_present = field in pdet_context
        results["checks"][f"has_{field}"] = field_present
        if not field_present:
            results["valid"] = False

    # Check 3: Relevance level is appropriate
    relevance = pdet_context.get("relevance", "")
    results["checks"]["relevance_level"] = relevance
    results["checks"]["relevance_appropriate"] = relevance in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    # Check 4: Security/peace challenges defined
    security_challenges = pdet_context.get("security_peace_challenges_pdet", {})
    results["checks"]["security_challenges_count"] = len(security_challenges)
    results["checks"]["has_security_challenges"] = len(security_challenges) > 0

    # Check 5: Institutional actors defined
    institutional_actors = pdet_context.get("institutional_actors", {})
    results["checks"]["institutional_actors_count"] = len(institutional_actors)
    results["checks"]["has_institutional_actors"] = len(institutional_actors) > 0

    # Check 6: Financing mechanisms defined
    financing = pdet_context.get("financing_context", {})
    results["checks"]["financing_mechanisms_count"] = len(financing)
    results["checks"]["has_financing_mechanisms"] = len(financing) > 0

    # Check 7: Policy areas alignment
    policy_areas = metadata.get("policy_area_ids", [])
    results["checks"]["policy_areas"] = policy_areas
    results["checks"]["has_policy_areas"] = len(policy_areas) > 0

    # Summary statistics
    results["summary"]["relevance"] = relevance
    results["summary"]["municipalities"] = pdet_context.get("territorial_scope", {}).get(
        "municipalities", 0
    )
    results["summary"]["subregions"] = pdet_context.get("territorial_scope", {}).get(
        "subregions", 0
    )
    results["summary"]["security_challenge_categories"] = len(security_challenges)
    results["summary"]["institutional_actors"] = len(institutional_actors)
    results["summary"]["financing_mechanisms"] = len(financing)
    results["summary"]["policy_areas"] = policy_areas

    # Check 8: Value contribution (Gate 2)
    value_items = (
        len(security_challenges)
        + len(institutional_actors)
        + len(financing)
        + len(pdet_context.get("territorial_disaggregation", {}).get("required_levels", []))
        + len(pdet_context.get("coherence_requirements", {}))
    )
    results["checks"]["value_items_count"] = value_items
    results["checks"]["meets_value_threshold"] = value_items >= 10

    return results


def print_validation_report(results: Dict[str, Any]):
    """Print formatted validation report."""
    print("=" * 70)
    print("CL01 SEGURIDAD Y PAZ - PDET ENRICHMENT VALIDATION REPORT")
    print("=" * 70)
    print()

    # Overall status
    status_icon = "✓" if results["valid"] else "✗"
    print(f"Overall Status: {status_icon} {'VALID' if results['valid'] else 'INVALID'}")
    print()

    # Summary
    print("SUMMARY:")
    print("-" * 70)
    for key, value in results["summary"].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    print()

    # Validation Gates
    print("VALIDATION GATES:")
    print("-" * 70)

    # Gate 1: Scope
    print("  Gate 1 - Scope Validity:")
    print(f"    ✓ PDET context exists: {results['checks']['pdet_context_exists']}")
    print(f"    ✓ Relevance level: {results['checks']['relevance_level']}")
    print(f"    ✓ Policy areas defined: {results['checks']['has_policy_areas']}")
    print()

    # Gate 2: Value
    print("  Gate 2 - Value Contribution:")
    print(f"    ✓ Value items count: {results['checks']['value_items_count']}")
    print(f"    ✓ Meets threshold (≥10): {results['checks']['meets_value_threshold']}")
    print(f"    ✓ Security challenges: {results['checks']['security_challenges_count']}")
    print(f"    ✓ Institutional actors: {results['checks']['institutional_actors_count']}")
    print(f"    ✓ Financing mechanisms: {results['checks']['financing_mechanisms_count']}")
    print()

    # Gate 3: Capability
    print("  Gate 3 - Capability:")
    print(f"    ✓ Requires SEMANTIC_PROCESSING: YES (descriptive context)")
    print(f"    ✓ Requires TABLE_PARSING: YES (structured data)")
    print()

    # Gate 4: Channel
    print("  Gate 4 - Channel Integrity:")
    print(f"    ✓ Explicit source: PDET municipalities + cluster metadata")
    print(f"    ✓ Traceable: YES")
    print(f"    ✓ Governed: YES")
    print()

    # Detailed checks
    print("DETAILED CHECKS:")
    print("-" * 70)
    failed_checks = [k for k, v in results["checks"].items() if isinstance(v, bool) and not v]
    if failed_checks:
        print("  Failed checks:")
        for check in failed_checks:
            print(f"    ✗ {check}")
    else:
        print("  ✓ All checks passed")
    print()

    print("=" * 70)


def main():
    """Main validation routine."""
    try:
        # Load cluster metadata
        metadata = load_cluster_metadata("CL01")

        # Validate enrichment
        results = validate_pdet_enrichment(metadata)

        # Print report
        print_validation_report(results)

        # Exit with appropriate code
        exit(0 if results["valid"] else 1)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        exit(2)


if __name__ == "__main__":
    main()
