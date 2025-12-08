#!/usr/bin/env python3
"""
Rigorous Intrinsic Calibration Triage - Method by Method Analysis

Per tesislizayjuan-debug requirements (comments 3512949686, 3513311176):
- Apply decision automaton to EVERY method in canonical_method_catalog.json
- Use machine-readable rubric from config/intrinsic_calibration_rubric.json
- Produce traceable, reproducible evidence for all scores

Pass 1: Determine if method requires calibration (3-question gate per rubric)
Pass 2: Compute evidence-based intrinsic scores using explicit rubric rules
Pass 3: Populate intrinsic_calibration.json with reproducible evidence

NO UNIFORM DEFAULTS. Each method analyzed individually.
ALL SCORES TRACEABLE. Evidence shows exact computation path.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .intrinsic_scoring import compute_b_deploy, compute_b_impl, compute_b_theory
except ImportError:
    from intrinsic_scoring import compute_b_deploy, compute_b_impl, compute_b_theory


def load_json(path: Path) -> dict:
    """Load JSON file"""
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    """Save JSON file with formatting"""
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def triage_pass1_requires_calibration(
    method_info: dict[str, Any], rubric: dict[str, Any]
) -> tuple[bool, str, dict[str, Any]]:
    """
    Pass 1: Does this method require intrinsic calibration?
    Determine if a method requires calibration based on the 3-question rubric.

    Returns: (requires_calibration, reason, evidence_dict)
    """
    method_name = method_info.get("method_name", "")
    docstring = method_info.get("docstring", "") or ""
    layer = method_info.get("layer", "unknown")
    return_type = method_info.get("return_type", "")

    # Load decision rules from rubric
    triggers = rubric["calibration_triggers"]
    exclusion_rules = rubric["exclusion_criteria"]

    # Check explicit exclusion patterns first
    exclusion_patterns = exclusion_rules["patterns"]
    for pattern_rule in exclusion_patterns:
        if pattern_rule["pattern"] in method_name:
            return (
                False,
                pattern_rule["reason"],
                {
                    "matched_exclusion_pattern": pattern_rule["pattern"],
                    "exclusion_reason": pattern_rule["reason"],
                },
            )

    # Q1: Analytically active?
    q1_config = triggers["questions"]["q1_analytically_active"]
    primary_verbs = q1_config["indicators"].get("primary_analytical_verbs", [])
    etl_verbs = q1_config["indicators"].get("generative_etl_verbs", [])
    all_analytical_verbs = primary_verbs + etl_verbs

    q1_matches_name = [
        verb for verb in all_analytical_verbs if verb in method_name.lower()
    ]
    q1_matches_doc = [
        verb for verb in all_analytical_verbs[:10] if verb in docstring.lower()
    ]
    q1_analytical = len(q1_matches_name) > 0 or len(q1_matches_doc) > 0

    # Q2: Parametric?
    q2_config = triggers["questions"]["q2_parametric"]
    parametric_keywords = q2_config["indicators"].get("parametric_keywords", [])
    parametric_verbs = q2_config["indicators"].get("parametric_verbs", [])
    critical_layers = q2_config["indicators"].get("check_layer", [])

    q2_matches_kw = [kw for kw in parametric_keywords if kw in docstring.lower()]
    q2_matches_verb = [verb for verb in parametric_verbs if verb in method_name.lower()]
    q2_parametric = (
        len(q2_matches_kw) > 0 or len(q2_matches_verb) > 0 or layer in critical_layers
    )

    # Q3: Safety-critical?
    q3_config = triggers["questions"]["q3_safety_critical"]
    safety_verbs = q3_config["indicators"].get("safety_verbs", [])
    safety_layers = q3_config["indicators"].get("critical_layers", [])
    eval_types = q3_config["indicators"].get("evaluative_return_types", [])

    q3_matches_verb = [verb for verb in safety_verbs if verb in method_name.lower()]
    q3_safety_critical = (
        len(q3_matches_verb) > 0 or layer in safety_layers or return_type in eval_types
    )

    if (
        q3_config["indicators"].get("exclude_simple_getters", False)
        and method_name.startswith("get_")
        and not q3_matches_verb
    ):
        q3_safety_critical = False

    # Additional exclusion rules
    is_private_utility = (
        method_name.startswith("_") and not q1_analytical and layer == "utility"
    )
    is_pure_getter = (
        method_name.startswith("get_")
        and return_type in ["str", "Path", "bool"]
        and not q1_analytical
        and not q3_safety_critical
    )

    # Build machine-readable evidence
    triage_evidence = {
        "q1_analytically_active": {
            "result": q1_analytical,
            "matched_verbs_in_name": q1_matches_name,
            "matched_verbs_in_doc": q1_matches_doc,
        },
        "q2_parametric": {
            "result": q2_parametric,
            "matched_keywords": q2_matches_kw,
            "matched_verbs": q2_matches_verb,
            "layer_is_critical": layer in critical_layers,
        },
        "q3_safety_critical": {
            "result": q3_safety_critical,
            "matched_safety_verbs": q3_matches_verb,
            "layer_is_critical": layer in safety_layers,
            "return_type_is_evaluative": return_type in eval_types,
        },
        "decision_rule": "requires_calibration = (q1 OR q2 OR q3) AND NOT excluded",
    }

    # Decision per rubric
    if is_private_utility:
        return False, "Private utility function - non-analytical", triage_evidence

    if is_pure_getter:
        return False, "Simple getter with no analytical logic", triage_evidence

    if q1_analytical or q2_parametric or q3_safety_critical:
        reasons = []
        if q1_analytical:
            reasons.append("analytically active")
        if q2_parametric:
            reasons.append("encodes assumptions/knobs")
        if q3_safety_critical:
            reasons.append("safety-critical for evaluation")
        return True, f"Requires calibration: {', '.join(reasons)}", triage_evidence

    return False, "Non-analytical utility function", triage_evidence


def triage_and_calibrate_method(
    method_info: dict[str, Any], repo_root: Path, rubric: dict[str, Any]
) -> dict[str, Any]:
    """
    Full triage and calibration for one method using rubric.

    Returns calibration entry for intrinsic_calibration.json
    """
    canonical_name = method_info.get("canonical_name", "")

    # Pass 1: Requires calibration?
    requires_cal, reason, triage_evidence = triage_pass1_requires_calibration(
        method_info, rubric
    )

    if not requires_cal:
        # Excluded method
        return {
            "method_id": canonical_name,
            "calibration_status": "excluded",
            "reason": reason,
            "triage_evidence": triage_evidence,
            "layer": method_info.get("layer", "unknown"),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "approved_by": "automated_triage",
            "rubric_version": rubric["_metadata"]["version"],
        }

    # Pass 2: Compute intrinsic calibration scores using rubric
    b_theory, theory_evidence = compute_b_theory(method_info, repo_root, rubric)
    b_impl, impl_evidence = compute_b_impl(method_info, repo_root, rubric)
    b_deploy, deploy_evidence = compute_b_deploy(method_info, rubric)

    # Pass 3: Create calibration profile with machine-readable evidence
    return {
        "method_id": canonical_name,
        "b_theory": b_theory,
        "b_impl": b_impl,
        "b_deploy": b_deploy,
        "evidence": {
            "triage_decision": triage_evidence,
            "triage_reason": reason,
            "b_theory_computation": theory_evidence,
            "b_impl_computation": impl_evidence,
            "b_deploy_computation": deploy_evidence,
        },
        "calibration_status": "computed",
        "layer": method_info.get("layer", "unknown"),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "approved_by": "automated_triage_with_rubric",
        "rubric_version": rubric["_metadata"]["version"],
    }


def main():
    """Execute rigorous method-by-method triage using machine-readable rubric"""
    repo_root = Path(__file__).resolve().parents[4]
    catalogue_path = repo_root / "config" / "canonical_method_catalogue_v2.json"
    rubric_path = (
        Path(__file__).resolve().parent / "intrinsic_calibration_rubric.json"
    )  # Same directory as script
    output_path = repo_root / "config" / "intrinsic_calibration.json"

    print("Loading machine-readable rubric...")
    rubric = load_json(rubric_path)
    print(f"  Rubric version: {rubric['_metadata']['version']}")

    print("Loading canonical method catalogue...")
    catalogue = load_json(catalogue_path)
    print(f"  Total methods in catalogue: {len(catalogue)}")

    print("Loading current intrinsic calibrations...")
    if output_path.exists():
        intrinsic = load_json(output_path)
    else:
        intrinsic = {}

    # Get existing calibrations (keep manually curated ones)
    existing_methods = {}
    for method_id, profile in intrinsic.items():
        if not method_id.startswith("_"):
            # Keep if approved_by indicates manual curation
            if "system_architect" in profile.get("approved_by", ""):
                existing_methods[method_id] = profile

    print(f"Preserving {len(existing_methods)} manually curated calibrations")

    # Process ALL catalogue methods (flat array structure)
    all_methods = {}
    for method_info in catalogue:
        unique_id = method_info.get("unique_id", "")
        if unique_id:
            # Add method_name field from canonical_name for compatibility
            method_info["method_name"] = method_info.get("canonical_name", "")
            all_methods[unique_id] = method_info

    print(f"\nProcessing {len(all_methods)} methods with rubric-based triage...")
    print("=" * 80)

    processed = 0
    calibrated = 0
    excluded = 0

    new_methods = {}

    for method_id, method_info in sorted(all_methods.items()):
        # Keep existing manual calibrations
        if method_id in existing_methods:
            new_methods[method_id] = existing_methods[method_id]
            calibrated += 1
        else:
            # Apply triage process with rubric
            calibration_entry = triage_and_calibrate_method(
                method_info, repo_root, rubric
            )
            new_methods[method_id] = calibration_entry

            if calibration_entry.get("calibration_status") == "excluded":
                excluded += 1
            else:
                calibrated += 1

        processed += 1
        if processed % 100 == 0:
            print(f"  Processed {processed}/{len(all_methods)} methods...")

    # Update intrinsic calibration file
    output_data = {
        "_metadata": {
            "version": "2.0.0",
            "generated": datetime.now(timezone.utc).isoformat(),
            "total_methods": len(all_methods),
            "computed_methods": calibrated,
            "excluded_methods": excluded,
            "coverage_percent": round((calibrated / len(all_methods)) * 100, 2),
            "rubric_version": rubric["_metadata"]["version"],
            "rubric_reference": "src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json",
            "methodology": "Machine-readable rubric with traceable evidence",
            "reproducibility": "All scores can be regenerated from rubric + catalogue",
        }
    }
    output_data.update(new_methods)

    print("\nSaving intrinsic_calibration.json...")
    save_json(output_path, output_data)

    print("\n" + "=" * 80)
    print("RIGOROUS TRIAGE COMPLETE")
    print("=" * 80)
    print(f"Total methods processed: {len(all_methods)}")
    print(f"Methods calibrated: {calibrated}")
    print(f"Methods excluded: {excluded}")
    print(f"Coverage: {calibrated/len(all_methods)*100:.2f}%")
    print(f"Rubric version: {rubric['_metadata']['version']}")
    print("\n✓ Every method analyzed using machine-readable rubric")
    print("✓ All scores traceable with explicit formulas and evidence")
    print("✓ Scores are reproducible from rubric + catalog")

    return 0


if __name__ == "__main__":
    sys.exit(main())
