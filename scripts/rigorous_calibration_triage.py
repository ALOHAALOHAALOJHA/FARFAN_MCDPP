#!/usr/bin/env python3
"""
Rigorous Intrinsic Calibration Triage Script

Execute rigorous calibration triage for all 1995 methods:
- Apply decision automaton to canonical_method_inventory.json
- For each method:
  * If excluded → set {calibration_status:'excluded', reason:<pattern>}
  * If pending → {b_theory:0.5, b_impl:0.5, b_deploy:0.5, status:'pending'}
  * If computable → calculate b_theory, b_impl, b_deploy with full evidence
- Generate intrinsic_calibration.json with ≥80% coverage
- Include _metadata section and _base_weights
- Produce intrinsic_calibration_report.md with statistics
- Create evidence_traces/ directory with detailed traces
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict:
    """Load JSON file"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    """Save JSON file with formatting"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_method_source(repo_root: Path, file_path: str, line_number: int) -> str:
    """
    Extract method source code from file.
    Returns empty string if unable to read.
    """
    try:
        full_path = (
            repo_root / file_path.replace("src/", "", 1)
            if file_path.startswith("src/")
            else repo_root / file_path
        )
        if not full_path.exists():
            full_path = repo_root / "src" / file_path
        if not full_path.exists():
            return ""

        with open(full_path, encoding="utf-8") as f:
            lines = f.readlines()

        if line_number < 1 or line_number > len(lines):
            return ""

        start_idx = line_number - 1
        method_def = lines[start_idx]

        indentation = len(method_def) - len(method_def.lstrip())

        source_lines = [method_def]

        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                source_lines.append(line)
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indentation:
                break
            source_lines.append(line)

        return "".join(source_lines)
    except Exception:
        return ""


def apply_exclusion_rules(
    method_info: dict[str, Any], rubric: dict[str, Any]
) -> tuple[bool, str | None]:
    """
    Apply exclusion criteria from rubric.
    Returns (is_excluded, reason)
    """
    method_name = method_info.get("method", "") or method_info.get("method_name", "")
    layer = method_info.get("layer", "unknown")
    method_info.get("docstring", "") or ""
    return_type = method_info.get("return_type", "")

    exclusion_rules = rubric.get("exclusion_criteria", {})
    patterns = exclusion_rules.get("patterns", [])

    for pattern_rule in patterns:
        pattern = pattern_rule.get("pattern", "")
        if pattern in method_name:
            return True, pattern_rule.get("reason", "Excluded by pattern")

    additional_rules = exclusion_rules.get("additional_rules", {})

    is_private_utility = (
        method_name.startswith("_")
        and layer == "utility"
        and not any(
            verb in method_name.lower()
            for verb in ["compute", "calculate", "analyze", "process"]
        )
    )
    if is_private_utility:
        return True, additional_rules.get("private_utility_in_utility_layer", {}).get(
            "reason", "Private utility function"
        )

    is_pure_getter = (
        method_name.startswith("get_")
        and return_type in ["str", "Path", "bool"]
        and not any(
            verb in method_name.lower() for verb in ["validate", "compute", "analyze"]
        )
    )
    if is_pure_getter:
        return True, additional_rules.get("pure_getter", {}).get(
            "reason", "Simple getter"
        )

    return False, None


def compute_b_theory(
    method_info: dict[str, Any], repo_root: Path, rubric: dict[str, Any]
) -> tuple[float, dict]:
    """
    Compute b_theory: theoretical foundation quality

    Components:
    - Statistical grounding (count keywords in docstring)
    - Logical consistency (docstring length, params/returns docs)
    - Appropriate assumptions (detect assumption keywords)
    """
    docstring = method_info.get("docstring", "") or ""

    b_theory_config = rubric["b_theory"]
    weights = b_theory_config["weights"]
    rules = b_theory_config["rules"]

    stat_rules = rules["grounded_in_valid_statistics"]["scoring"]
    stat_keywords = stat_rules["has_bayesian_or_statistical_model"]["keywords"]
    stat_matches = [kw for kw in stat_keywords if kw in docstring.lower()]

    if (
        len(stat_matches)
        >= stat_rules["has_bayesian_or_statistical_model"]["threshold"]
    ):
        stat_score = stat_rules["has_bayesian_or_statistical_model"]["score"]
        stat_rule = "has_bayesian_or_statistical_model"
    elif len(stat_matches) >= stat_rules["has_some_statistical_grounding"]["threshold"]:
        stat_score = stat_rules["has_some_statistical_grounding"]["score"]
        stat_rule = "has_some_statistical_grounding"
    else:
        stat_score = stat_rules["no_statistical_grounding"]["score"]
        stat_rule = "no_statistical_grounding"

    logic_rules = rules["logical_consistency"]["scoring"]
    doc_length = len(docstring)
    has_returns_doc = "return" in docstring.lower()
    has_params_doc = "param" in docstring.lower() or "arg" in docstring.lower()

    if doc_length > 50 and has_returns_doc and has_params_doc:
        logical_score = logic_rules["complete_documentation"]["score"]
        logic_rule = "complete_documentation"
    elif doc_length > 20:
        logical_score = logic_rules["partial_documentation"]["score"]
        logic_rule = "partial_documentation"
    else:
        logical_score = logic_rules["minimal_documentation"]["score"]
        logic_rule = "minimal_documentation"

    assumption_rules = rules["appropriate_assumptions"]["scoring"]
    assumption_keywords = assumption_rules["assumptions_documented"]["keywords"]
    assumption_matches = [kw for kw in assumption_keywords if kw in docstring.lower()]

    if len(assumption_matches) > 0:
        assumptions_score = assumption_rules["assumptions_documented"]["score"]
        assumptions_rule = "assumptions_documented"
    else:
        assumptions_score = assumption_rules["implicit_assumptions"]["score"]
        assumptions_rule = "implicit_assumptions"

    b_theory = (
        weights["grounded_in_valid_statistics"] * stat_score
        + weights["logical_consistency"] * logical_score
        + weights["appropriate_assumptions"] * assumptions_score
    )

    evidence = {
        "formula": "b_theory = 0.4*stat + 0.3*logic + 0.3*assumptions",
        "components": {
            "grounded_in_valid_statistics": {
                "weight": weights["grounded_in_valid_statistics"],
                "score": stat_score,
                "matched_keywords": stat_matches,
                "keyword_count": len(stat_matches),
                "rule_applied": stat_rule,
            },
            "logical_consistency": {
                "weight": weights["logical_consistency"],
                "score": logical_score,
                "docstring_length": doc_length,
                "has_returns_doc": has_returns_doc,
                "has_params_doc": has_params_doc,
                "rule_applied": logic_rule,
            },
            "appropriate_assumptions": {
                "weight": weights["appropriate_assumptions"],
                "score": assumptions_score,
                "matched_keywords": assumption_matches,
                "rule_applied": assumptions_rule,
            },
        },
        "final_score": round(b_theory, 3),
    }

    return round(b_theory, 3), evidence


def compute_b_impl(
    method_info: dict[str, Any], repo_root: Path, rubric: dict[str, Any]
) -> tuple[float, dict]:
    """
    Compute b_impl: implementation quality

    Components:
    - Test coverage (default 0.35 conservative)
    - Type annotations (via AST analysis)
    - Error handling (detect try/except in source)
    - Documentation completeness
    """
    input_params = method_info.get("input_parameters", [])
    return_type = method_info.get("return_type")
    docstring = method_info.get("docstring", "") or ""
    file_path = method_info.get("module", "") or method_info.get("file_path", "")
    line_number = method_info.get("line_number", 0)

    b_impl_config = rubric["b_impl"]
    weights = b_impl_config["weights"]
    rules = b_impl_config["rules"]

    test_rules = rules["test_coverage"]["scoring"]
    test_score = test_rules["no_test_evidence"]["score"]
    test_rule = "no_test_evidence"

    params_with_types = sum(
        1 for p in input_params if p.get("type_hint") or p.get("type")
    )
    total_params = max(len(input_params), 1)
    has_return_type = return_type is not None and return_type not in ("", "None")
    type_score = (params_with_types / total_params * 0.7) + (
        0.3 if has_return_type else 0
    )

    source_code = get_method_source(repo_root, file_path, line_number)
    has_try_except = "try:" in source_code and "except" in source_code

    error_rules = rules["error_handling"]["scoring"]
    if has_try_except:
        error_score = error_rules["comprehensive_handling"]["score"]
        error_rule = "comprehensive_handling"
    else:
        error_score = error_rules["minimal_handling"]["score"]
        error_rule = "minimal_handling"

    doc_length = len(docstring)
    has_description = doc_length > 50
    has_params_doc = "param" in docstring.lower() or "arg" in docstring.lower()
    has_returns_doc = "return" in docstring.lower()
    has_examples = "example" in docstring.lower()
    doc_score = (
        (0.4 if has_description else 0.1)
        + (0.3 if has_params_doc else 0)
        + (0.2 if has_returns_doc else 0)
        + (0.1 if has_examples else 0)
    )

    b_impl = (
        weights["test_coverage"] * test_score
        + weights["type_annotations"] * type_score
        + weights["error_handling"] * error_score
        + weights["documentation"] * doc_score
    )

    evidence = {
        "formula": "b_impl = 0.35*test + 0.25*type + 0.25*error + 0.15*doc",
        "components": {
            "test_coverage": {
                "weight": weights["test_coverage"],
                "score": test_score,
                "rule_applied": test_rule,
                "note": "Conservative default until measured",
            },
            "type_annotations": {
                "weight": weights["type_annotations"],
                "score": round(type_score, 3),
                "formula": "(typed_params / total_params) * 0.7 + (0.3 if has_return_type else 0)",
                "details": {
                    "typed_params": params_with_types,
                    "total_params": total_params,
                    "has_return_type": has_return_type,
                },
            },
            "error_handling": {
                "weight": weights["error_handling"],
                "score": error_score,
                "rule_applied": error_rule,
                "has_try_except": has_try_except,
            },
            "documentation": {
                "weight": weights["documentation"],
                "score": round(doc_score, 3),
                "formula": "weighted_sum(desc, params, returns, examples)",
                "details": {
                    "doc_length": doc_length,
                    "has_params": has_params_doc,
                    "has_returns": has_returns_doc,
                    "has_examples": has_examples,
                },
            },
        },
        "final_score": round(b_impl, 3),
    }

    return round(b_impl, 3), evidence


def compute_b_deploy(
    method_info: dict[str, Any], rubric: dict[str, Any]
) -> tuple[float, dict]:
    """
    Compute b_deploy: deployment maturity

    Get layer maturity baseline from rubric, then apply formulas:
    - validation = baseline * 0.8
    - stability = baseline * 0.9
    - failure = baseline * 0.85
    """
    layer = method_info.get("layer", "unknown")

    b_deploy_config = rubric["b_deploy"]
    weights = b_deploy_config["weights"]
    rules = b_deploy_config["rules"]

    layer_maturity_map = rules["layer_maturity_baseline"]["scoring"]
    base_maturity = layer_maturity_map.get(
        layer, layer_maturity_map.get("unknown", 0.3)
    )

    validation_score = base_maturity * 0.8
    stability_score = base_maturity * 0.9
    failure_score = base_maturity * 0.85

    b_deploy = (
        weights["validation_runs"] * validation_score
        + weights["stability_coefficient"] * stability_score
        + weights["failure_rate"] * failure_score
    )

    evidence = {
        "formula": "b_deploy = 0.4*validation + 0.35*stability + 0.25*failure",
        "components": {
            "layer_maturity_baseline": {
                "layer": layer,
                "baseline_score": base_maturity,
                "source": "rubric layer_maturity_baseline mapping",
            },
            "validation_runs": {
                "weight": weights["validation_runs"],
                "score": round(validation_score, 3),
                "formula": "layer_maturity_baseline * 0.8",
                "computation": f"{base_maturity} * 0.8 = {round(validation_score, 3)}",
            },
            "stability_coefficient": {
                "weight": weights["stability_coefficient"],
                "score": round(stability_score, 3),
                "formula": "layer_maturity_baseline * 0.9",
                "computation": f"{base_maturity} * 0.9 = {round(stability_score, 3)}",
            },
            "failure_rate": {
                "weight": weights["failure_rate"],
                "score": round(failure_score, 3),
                "formula": "layer_maturity_baseline * 0.85",
                "computation": f"{base_maturity} * 0.85 = {round(failure_score, 3)}",
            },
        },
        "final_score": round(b_deploy, 3),
    }

    return round(b_deploy, 3), evidence


def decide_calibration_requirement(
    method_info: dict[str, Any], rubric: dict[str, Any]
) -> tuple[str, str, dict]:
    """
    Apply decision automaton to determine calibration requirement.

    Returns: (status, reason, evidence)
    - status: 'excluded', 'pending', or 'computable'
    - reason: explanation
    - evidence: decision trace
    """
    method_name = method_info.get("method", "") or method_info.get("method_name", "")
    docstring = method_info.get("docstring", "") or ""
    layer = method_info.get("layer", "unknown")
    return_type = method_info.get("return_type", "")

    triggers = rubric["calibration_triggers"]

    q1_config = triggers["questions"]["q1_analytically_active"]
    primary_verbs = q1_config["indicators"].get("primary_analytical_verbs", [])
    generative_verbs = q1_config["indicators"].get("generative_etl_verbs", [])
    all_analytical_verbs = primary_verbs + generative_verbs

    q1_matches_name = [
        verb for verb in all_analytical_verbs if verb in method_name.lower()
    ]
    q1_matches_doc = [verb for verb in primary_verbs[:10] if verb in docstring.lower()]
    q1_analytical = len(q1_matches_name) > 0 or len(q1_matches_doc) > 0

    q2_config = triggers["questions"]["q2_parametric"]
    parametric_keywords = q2_config["indicators"].get("parametric_keywords", [])
    parametric_verbs = q2_config["indicators"].get("parametric_verbs", [])
    critical_layers = q2_config["indicators"].get("check_layer", [])

    q2_matches_kw = [kw for kw in parametric_keywords if kw in docstring.lower()]
    q2_matches_verb = [verb for verb in parametric_verbs if verb in method_name.lower()]
    q2_parametric = (
        len(q2_matches_kw) > 0 or len(q2_matches_verb) > 0 or layer in critical_layers
    )

    q3_config = triggers["questions"]["q3_safety_critical"]
    safety_verbs = q3_config["indicators"].get("safety_verbs", [])
    safety_layers = q3_config["indicators"].get("critical_layers", [])
    eval_types = q3_config["indicators"].get("evaluative_return_types", [])

    q3_matches_verb = [verb for verb in safety_verbs if verb in method_name.lower()]
    q3_safety_critical = (
        len(q3_matches_verb) > 0 or layer in safety_layers or return_type in eval_types
    )

    evidence = {
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

    if q1_analytical or q2_parametric or q3_safety_critical:
        reasons = []
        if q1_analytical:
            reasons.append("analytically active")
        if q2_parametric:
            reasons.append("encodes assumptions/knobs")
        if q3_safety_critical:
            reasons.append("safety-critical")
        return "computable", f"Requires calibration: {', '.join(reasons)}", evidence

    return "excluded", "Non-analytical utility function", evidence


def calibrate_method(
    method_id: str, method_info: dict[str, Any], repo_root: Path, rubric: dict[str, Any]
) -> dict[str, Any]:
    """
    Full calibration for one method.

    Returns calibration entry for intrinsic_calibration.json
    """
    is_excluded, exclusion_reason = apply_exclusion_rules(method_info, rubric)

    if is_excluded:
        return {
            "calibration_status": "excluded",
            "reason": exclusion_reason,
            "layer": method_info.get("layer", "unknown"),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    status, reason, triage_evidence = decide_calibration_requirement(
        method_info, rubric
    )

    if status == "excluded":
        return {
            "calibration_status": "excluded",
            "reason": reason,
            "evidence": triage_evidence,
            "layer": method_info.get("layer", "unknown"),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
    elif status == "pending":
        return {
            "b_theory": 0.5,
            "b_impl": 0.5,
            "b_deploy": 0.5,
            "calibration_status": "pending",
            "reason": reason,
            "layer": method_info.get("layer", "unknown"),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
    else:
        b_theory, theory_evidence = compute_b_theory(method_info, repo_root, rubric)
        b_impl, impl_evidence = compute_b_impl(method_info, repo_root, rubric)
        b_deploy, deploy_evidence = compute_b_deploy(method_info, rubric)

        return {
            "b_theory": b_theory,
            "b_impl": b_impl,
            "b_deploy": b_deploy,
            "calibration_status": "computed",
            "evidence": {
                "triage_decision": triage_evidence,
                "triage_reason": reason,
                "b_theory_computation": theory_evidence,
                "b_impl_computation": impl_evidence,
                "b_deploy_computation": deploy_evidence,
            },
            "layer": method_info.get("layer", "unknown"),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }


def generate_report(output_path: Path, calibration_data: dict, stats: dict) -> None:
    """Generate intrinsic_calibration_report.md"""
    report_lines = [
        "# Intrinsic Calibration Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Summary Statistics",
        "",
        f"- **Total Methods:** {stats['total_methods']}",
        f"- **Computed:** {stats['computed_methods']} ({stats['computed_percent']:.2f}%)",
        f"- **Excluded:** {stats['excluded_methods']} ({stats['excluded_percent']:.2f}%)",
        f"- **Pending:** {stats['pending_methods']} ({stats['pending_percent']:.2f}%)",
        f"- **Coverage:** {stats['coverage_percent']:.2f}%",
        "",
        "## Calibration Status Distribution",
        "",
        "| Status | Count | Percentage |",
        "|--------|-------|------------|",
        f"| Computed | {stats['computed_methods']} | {stats['computed_percent']:.2f}% |",
        f"| Excluded | {stats['excluded_methods']} | {stats['excluded_percent']:.2f}% |",
        f"| Pending | {stats['pending_methods']} | {stats['pending_percent']:.2f}% |",
        "",
        "## Layer Distribution",
        "",
        "| Layer | Total | Computed | Excluded | Pending |",
        "|-------|-------|----------|----------|---------|",
    ]

    for layer, counts in sorted(stats["by_layer"].items()):
        report_lines.append(
            f"| {layer} | {counts['total']} | {counts['computed']} | {counts['excluded']} | {counts['pending']} |"
        )

    report_lines.extend(
        [
            "",
            "## Score Statistics (Computed Methods Only)",
            "",
            "### b_theory",
            f"- **Mean:** {stats['score_stats']['b_theory']['mean']:.3f}",
            f"- **Min:** {stats['score_stats']['b_theory']['min']:.3f}",
            f"- **Max:** {stats['score_stats']['b_theory']['max']:.3f}",
            f"- **Median:** {stats['score_stats']['b_theory']['median']:.3f}",
            "",
            "### b_impl",
            f"- **Mean:** {stats['score_stats']['b_impl']['mean']:.3f}",
            f"- **Min:** {stats['score_stats']['b_impl']['min']:.3f}",
            f"- **Max:** {stats['score_stats']['b_impl']['max']:.3f}",
            f"- **Median:** {stats['score_stats']['b_impl']['median']:.3f}",
            "",
            "### b_deploy",
            f"- **Mean:** {stats['score_stats']['b_deploy']['mean']:.3f}",
            f"- **Min:** {stats['score_stats']['b_deploy']['min']:.3f}",
            f"- **Max:** {stats['score_stats']['b_deploy']['max']:.3f}",
            f"- **Median:** {stats['score_stats']['b_deploy']['median']:.3f}",
            "",
            "## Top Exclusion Reasons",
            "",
            "| Reason | Count |",
            "|--------|-------|",
        ]
    )

    for reason, count in sorted(
        stats["exclusion_reasons"].items(), key=lambda x: x[1], reverse=True
    )[:10]:
        report_lines.append(f"| {reason} | {count} |")

    report_lines.extend(
        [
            "",
            "## Methodology",
            "",
            "This calibration was generated using the rigorous triage process:",
            "",
            "1. **Exclusion Rules:** Methods matching exclusion patterns (e.g., `__init__`, formatters) are excluded",
            "2. **Decision Automaton:** Three-question gate determines calibration requirement:",
            "   - Q1: Analytically active?",
            "   - Q2: Parametric (encodes assumptions)?",
            "   - Q3: Safety-critical?",
            "3. **Score Computation:** For computable methods, calculate:",
            "   - **b_theory:** Statistical grounding, logical consistency, assumptions",
            "   - **b_impl:** Test coverage, type annotations, error handling, documentation",
            "   - **b_deploy:** Layer maturity baseline with validation/stability/failure factors",
            "",
            "All scores are traceable and reproducible from the rubric and method metadata.",
            "",
            f"**Rubric Version:** {stats['rubric_version']}",
            "",
            "---",
            "",
            "*See evidence_traces/ directory for detailed computation traces.*",
        ]
    )

    report_path = output_path.parent / "intrinsic_calibration_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"✓ Report generated: {report_path}")


def save_evidence_traces(
    evidence_dir: Path, calibration_data: dict, sample_size: int = 50
) -> None:
    """Save detailed evidence traces for sample of methods"""
    evidence_dir.mkdir(exist_ok=True)

    methods_with_evidence = [
        (method_id, data)
        for method_id, data in calibration_data.items()
        if not method_id.startswith("_")
        and data.get("calibration_status") == "computed"
        and "evidence" in data
    ]

    import random

    random.seed(42)
    sample = random.sample(
        methods_with_evidence, min(sample_size, len(methods_with_evidence))
    )

    for method_id, data in sample:
        safe_filename = (
            method_id.replace("::", "_").replace(":", "_").replace("/", "_")[:100]
            + ".json"
        )
        trace_path = evidence_dir / safe_filename

        trace_data = {
            "method_id": method_id,
            "calibration": {
                "b_theory": data.get("b_theory"),
                "b_impl": data.get("b_impl"),
                "b_deploy": data.get("b_deploy"),
                "status": data.get("calibration_status"),
            },
            "evidence": data.get("evidence", {}),
            "layer": data.get("layer"),
            "last_updated": data.get("last_updated"),
        }

        save_json(trace_path, trace_data)

    print(f"✓ Saved {len(sample)} evidence traces to {evidence_dir}")


def main():
    """Execute rigorous calibration triage for all methods"""
    repo_root = Path(__file__).resolve().parent.parent
    inventory_path = repo_root / "canonical_method_inventory.json"
    rubric_path = (
        repo_root
        / "src"
        / "farfan_pipeline"
        / "core"
        / "calibration"
        / "intrinsic_calibration_rubric.json"
    )
    output_path = repo_root / "intrinsic_calibration.json"
    evidence_dir = repo_root / "evidence_traces"

    print("=" * 80)
    print("RIGOROUS CALIBRATION TRIAGE")
    print("=" * 80)
    print()

    print(f"Loading rubric from: {rubric_path}")
    if not rubric_path.exists():
        print(f"ERROR: Rubric not found at {rubric_path}")
        return 1
    rubric = load_json(rubric_path)
    print(f"  ✓ Rubric version: {rubric['_metadata']['version']}")
    print()

    print(f"Loading method inventory from: {inventory_path}")
    if not inventory_path.exists():
        print(f"ERROR: Inventory not found at {inventory_path}")
        return 1
    inventory = load_json(inventory_path)
    print(f"  ✓ Total methods in inventory: {len(inventory)}")
    print()

    print("Processing methods...")
    print("-" * 80)

    calibration_results = {}
    stats = {
        "total_methods": 0,
        "computed_methods": 0,
        "excluded_methods": 0,
        "pending_methods": 0,
        "by_layer": defaultdict(
            lambda: {"total": 0, "computed": 0, "excluded": 0, "pending": 0}
        ),
        "exclusion_reasons": defaultdict(int),
        "score_stats": {
            "b_theory": {"values": []},
            "b_impl": {"values": []},
            "b_deploy": {"values": []},
        },
        "rubric_version": rubric["_metadata"]["version"],
    }

    processed = 0
    for method_id, method_info in inventory.items():
        stats["total_methods"] += 1
        layer = method_info.get("layer", "unknown")
        stats["by_layer"][layer]["total"] += 1

        calibration_entry = calibrate_method(method_id, method_info, repo_root, rubric)
        calibration_results[method_id] = calibration_entry

        status = calibration_entry.get("calibration_status")
        if status == "computed":
            stats["computed_methods"] += 1
            stats["by_layer"][layer]["computed"] += 1
            stats["score_stats"]["b_theory"]["values"].append(
                calibration_entry.get("b_theory", 0)
            )
            stats["score_stats"]["b_impl"]["values"].append(
                calibration_entry.get("b_impl", 0)
            )
            stats["score_stats"]["b_deploy"]["values"].append(
                calibration_entry.get("b_deploy", 0)
            )
        elif status == "excluded":
            stats["excluded_methods"] += 1
            stats["by_layer"][layer]["excluded"] += 1
            reason = calibration_entry.get("reason", "Unknown")
            stats["exclusion_reasons"][reason] += 1
        elif status == "pending":
            stats["pending_methods"] += 1
            stats["by_layer"][layer]["pending"] += 1

        processed += 1
        if processed % 100 == 0:
            print(f"  Processed {processed}/{stats['total_methods']} methods...")

    stats["computed_percent"] = (
        (stats["computed_methods"] / stats["total_methods"] * 100)
        if stats["total_methods"] > 0
        else 0
    )
    stats["excluded_percent"] = (
        (stats["excluded_methods"] / stats["total_methods"] * 100)
        if stats["total_methods"] > 0
        else 0
    )
    stats["pending_percent"] = (
        (stats["pending_methods"] / stats["total_methods"] * 100)
        if stats["total_methods"] > 0
        else 0
    )
    stats["coverage_percent"] = stats["computed_percent"]

    for score_type in ["b_theory", "b_impl", "b_deploy"]:
        values = stats["score_stats"][score_type]["values"]
        if values:
            stats["score_stats"][score_type]["mean"] = sum(values) / len(values)
            stats["score_stats"][score_type]["min"] = min(values)
            stats["score_stats"][score_type]["max"] = max(values)
            sorted_values = sorted(values)
            mid = len(sorted_values) // 2
            stats["score_stats"][score_type]["median"] = (
                sorted_values[mid]
                if len(sorted_values) % 2 == 1
                else (sorted_values[mid - 1] + sorted_values[mid]) / 2
            )
        else:
            stats["score_stats"][score_type].update(
                {"mean": 0, "min": 0, "max": 0, "median": 0}
            )

    print()
    print("-" * 80)
    print(f"✓ Processed all {stats['total_methods']} methods")
    print()

    output_data = {
        "_metadata": {
            "version": "2.0.0",
            "generated": datetime.now(timezone.utc).isoformat(),
            "total_methods": stats["total_methods"],
            "computed_methods": stats["computed_methods"],
            "excluded_methods": stats["excluded_methods"],
            "pending_methods": stats["pending_methods"],
            "coverage_percent": round(stats["coverage_percent"], 2),
            "rubric_version": stats["rubric_version"],
            "rubric_reference": "src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json",
            "methodology": "Rigorous triage with decision automaton",
            "reproducibility": "All scores traceable from rubric + inventory",
        },
        "_base_weights": {"w_th": 0.4, "w_imp": 0.35, "w_dep": 0.25},
    }
    output_data.update(calibration_results)

    print(f"Saving calibration data to: {output_path}")
    save_json(output_path, output_data)
    print(f"  ✓ Saved {len(calibration_results)} calibrations")
    print()

    print("Generating report...")
    generate_report(output_path, calibration_results, stats)
    print()

    print("Saving evidence traces...")
    save_evidence_traces(evidence_dir, calibration_results, sample_size=50)
    print()

    print("=" * 80)
    print("CALIBRATION COMPLETE")
    print("=" * 80)
    print()
    print(f"📊 Total methods:     {stats['total_methods']}")
    print(
        f"✅ Computed:          {stats['computed_methods']} ({stats['computed_percent']:.2f}%)"
    )
    print(
        f"🚫 Excluded:          {stats['excluded_methods']} ({stats['excluded_percent']:.2f}%)"
    )
    print(
        f"⏸️  Pending:           {stats['pending_methods']} ({stats['pending_percent']:.2f}%)"
    )
    print(f"📈 Coverage:          {stats['coverage_percent']:.2f}%")
    print()
    print("Score Averages (Computed Methods):")
    print(f"  b_theory:  {stats['score_stats']['b_theory']['mean']:.3f}")
    print(f"  b_impl:    {stats['score_stats']['b_impl']['mean']:.3f}")
    print(f"  b_deploy:  {stats['score_stats']['b_deploy']['mean']:.3f}")
    print()

    if stats["coverage_percent"] >= 80:
        print("✅ Coverage target met: ≥80%")
    else:
        print(f"⚠️  Coverage below target: {stats['coverage_percent']:.2f}% < 80%")
    print()

    print("Output files:")
    print(f"  - {output_path}")
    print(f"  - {output_path.parent / 'intrinsic_calibration_report.md'}")
    print(f"  - {evidence_dir}/ (sample evidence traces)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
