"""
Intrinsic Calibration Scoring Implementation

Implements exact formulas from intrinsic_calibration_rubric.json v2.0.0:
- b_theory = 0.4*statistical_validity + 0.3*logical_consistency + 0.3*appropriate_assumptions
- b_impl = 0.35*test_coverage + 0.25*type_annotations + 0.25*error_handling + 0.15*documentation
- b_deploy = 0.4*validation_runs + 0.35*stability_coefficient + 0.25*failure_rate

All formulas are traceable and reproducible.
"""

import re
from pathlib import Path
from typing import Any


def compute_statistical_validity(
    method_info: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """
    Compute statistical validity score.

    Keywords: bayesian, probability, regression, likelihood
    Scoring: >=2 keywords → 1.0, ==1 keyword → 0.6, ==0 keywords → 0.2
    """
    docstring = method_info.get("docstring", "") or ""
    method_name = method_info.get("method_name", "")

    keywords = ["bayesian", "probability", "regression", "likelihood"]

    # Search in both docstring and method name
    text_to_search = (docstring + " " + method_name).lower()
    matched = [kw for kw in keywords if kw in text_to_search]

    if len(matched) >= 2:
        score = 1.0
        rule = "strong_statistical"
    elif len(matched) == 1:
        score = 0.6
        rule = "moderate_statistical"
    else:
        score = 0.2
        rule = "weak_statistical"

    evidence = {
        "score": score,
        "rule_applied": rule,
        "keywords_searched": keywords,
        "keywords_matched": matched,
        "keyword_count": len(matched),
    }

    return score, evidence


def compute_logical_consistency(
    method_info: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """
    Compute logical consistency score based on documentation quality.

    Complete: docstring>100 + params + returns → 1.0
    Good: docstring>50 + (params OR returns) → 0.7
    Basic: docstring>20 → 0.4
    Minimal: otherwise → 0.1
    """
    docstring = method_info.get("docstring", "") or ""
    doc_length = len(docstring)

    has_params_doc = "param" in docstring.lower() or "arg" in docstring.lower()
    has_returns_doc = "return" in docstring.lower()

    if doc_length > 100 and has_params_doc and has_returns_doc:
        score = 1.0
        rule = "complete"
    elif doc_length > 50 and (has_params_doc or has_returns_doc):
        score = 0.7
        rule = "good"
    elif doc_length > 20:
        score = 0.4
        rule = "basic"
    else:
        score = 0.1
        rule = "minimal"

    evidence = {
        "score": score,
        "rule_applied": rule,
        "docstring_length": doc_length,
        "has_params_doc": has_params_doc,
        "has_returns_doc": has_returns_doc,
    }

    return score, evidence


def compute_appropriate_assumptions(
    method_info: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """
    Compute appropriate assumptions score.

    Keywords: assum, constraint, precondition
    Scoring: >=1 keyword → 0.8, ==0 keywords → 0.3
    """
    docstring = method_info.get("docstring", "") or ""

    keywords = ["assum", "constraint", "precondition"]
    matched = [kw for kw in keywords if kw in docstring.lower()]

    if len(matched) >= 1:
        score = 0.8
        rule = "explicit_assumptions"
    else:
        score = 0.3
        rule = "implicit_assumptions"

    evidence = {
        "score": score,
        "rule_applied": rule,
        "keywords_searched": keywords,
        "keywords_matched": matched,
        "keyword_count": len(matched),
    }

    return score, evidence


def compute_b_theory(
    method_info: dict[str, Any], rubric: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """
    Compute b_theory using exact formula:
    b_theory = 0.4 * statistical_validity + 0.3 * logical_consistency + 0.3 * appropriate_assumptions

    Returns: (score, evidence)
    """
    # Get component scores
    stat_score, stat_evidence = compute_statistical_validity(method_info)
    logic_score, logic_evidence = compute_logical_consistency(method_info)
    assumptions_score, assumptions_evidence = compute_appropriate_assumptions(
        method_info
    )

    # Apply exact formula
    b_theory = 0.4 * stat_score + 0.3 * logic_score + 0.3 * assumptions_score

    evidence = {
        "formula": "b_theory = 0.4*statistical_validity + 0.3*logical_consistency + 0.3*appropriate_assumptions",
        "weights": {
            "statistical_validity": 0.4,
            "logical_consistency": 0.3,
            "appropriate_assumptions": 0.3,
        },
        "components": {
            "statistical_validity": stat_evidence,
            "logical_consistency": logic_evidence,
            "appropriate_assumptions": assumptions_evidence,
        },
        "computation": f"{0.4}*{stat_score} + {0.3}*{logic_score} + {0.3}*{assumptions_score} = {b_theory:.3f}",
        "final_score": round(b_theory, 3),
    }

    return round(b_theory, 3), evidence


def compute_test_coverage_score(
    method_info: dict[str, Any], repo_root: Path
) -> tuple[float, dict[str, Any]]:
    """
    Compute test coverage score.

    ≥80% → 1.0 (linear scaling below)
    Fallback: has_test_file → 0.5, no_test → 0.2
    """
    # Try to find test file
    file_path = method_info.get("file_path", "")

    # Check for test file existence (heuristic)
    has_test_file = False
    if file_path:
        # Convert src path to test path
        test_path_patterns = [
            file_path.replace("src/", "tests/").replace(".py", "_test.py"),
            file_path.replace("src/", "tests/test_"),
            file_path.replace("farfan_core/", "tests/"),
        ]

        for pattern in test_path_patterns:
            full_path = repo_root / pattern
            if full_path.exists():
                has_test_file = True
                break

    # Use fallback scoring (actual coverage data not available)
    if has_test_file:
        score = 0.5
        rule = "has_test_file"
    else:
        score = 0.2
        rule = "no_test_evidence"

    evidence = {
        "score": score,
        "rule_applied": rule,
        "formula": "min(1.0, coverage_percent / 80.0)",
        "note": "Using fallback - actual coverage data unavailable",
        "has_test_file": has_test_file,
    }

    return score, evidence


def compute_type_annotations_score(
    method_info: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """
    Compute type annotations score.

    Formula: (typed_params / total_params) * 0.7 + (0.3 if return_type else 0)
    """
    input_params = method_info.get("input_parameters", [])
    return_type = method_info.get("return_type")

    # Count typed parameters
    typed_params = sum(1 for p in input_params if p.get("type_hint"))
    total_params = max(len(input_params), 1)  # Avoid division by zero

    has_return_type = return_type is not None and return_type != ""

    # Apply exact formula
    score = (typed_params / total_params) * 0.7 + (0.3 if has_return_type else 0)

    evidence = {
        "score": round(score, 3),
        "formula": "(typed_params / total_params) * 0.7 + (0.3 if return_type else 0)",
        "computation": f"({typed_params} / {total_params}) * 0.7 + {0.3 if has_return_type else 0} = {score:.3f}",
        "typed_params": typed_params,
        "total_params": total_params,
        "has_return_type": has_return_type,
    }

    return round(score, 3), evidence


def get_method_source(repo_root: Path, file_path: str, line_number: int) -> str:
    """
    Attempt to read the source code of a method.
    Uses indentation-based heuristic.
    """
    try:
        # Try multiple path patterns
        possible_paths = [
            repo_root / "src" / file_path,
            repo_root / file_path,
            repo_root / "farfan_core" / file_path,
        ]

        source_path = None
        for path in possible_paths:
            if path.exists():
                source_path = path
                break

        if not source_path:
            return ""

        with open(source_path, encoding="utf-8") as f:
            lines = f.readlines()

        if line_number < 1 or line_number > len(lines):
            return ""

        # Adjust for 0-indexing
        start_idx = line_number - 1
        method_def = lines[start_idx]

        # Determine indentation of the def line
        indentation = len(method_def) - len(method_def.lstrip())

        source_lines = [method_def]

        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip():  # Keep empty lines
                source_lines.append(line)
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indentation:
                break  # End of method
            source_lines.append(line)

        return "".join(source_lines)
    except Exception:
        return ""


def compute_error_handling_score(
    method_info: dict[str, Any], repo_root: Path
) -> tuple[float, dict[str, Any]]:
    """
    Compute error handling score.

    Comprehensive: try/except + validation → 1.0
    Good: try/except OR validation → 0.7
    Basic: otherwise → 0.3
    """
    file_path = method_info.get("file_path", "")
    line_number = method_info.get("line_number", 0)

    # Try to read source code
    source_code = get_method_source(repo_root, file_path, line_number)

    has_try_except = "try:" in source_code and "except" in source_code

    # Check for input validation patterns
    validation_patterns = [
        r"if\s+not\s+\w+:",
        r"if\s+\w+\s+is\s+None:",
        r"assert\s+",
        r"raise\s+\w+Error",
        r"ValueError",
        r"TypeError",
    ]
    has_input_validation = any(
        re.search(pattern, source_code) for pattern in validation_patterns
    )

    if has_try_except and has_input_validation:
        score = 1.0
        rule = "comprehensive"
    elif has_try_except or has_input_validation:
        score = 0.7
        rule = "good"
    else:
        score = 0.3
        rule = "basic"

    evidence = {
        "score": score,
        "rule_applied": rule,
        "has_try_except": has_try_except,
        "has_input_validation": has_input_validation,
        "source_analyzed": len(source_code) > 0,
    }

    return score, evidence


def compute_documentation_score(
    method_info: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """
    Compute documentation score.

    Formula: (0.4 if length>50 else 0.1) + (0.3 if params else 0) + (0.2 if returns else 0) + (0.1 if examples else 0)
    """
    docstring = method_info.get("docstring", "") or ""
    doc_length = len(docstring)

    has_description = doc_length > 50
    has_params_doc = "param" in docstring.lower() or "arg" in docstring.lower()
    has_returns_doc = "return" in docstring.lower()
    has_examples = "example" in docstring.lower()

    # Apply exact formula
    score = (
        (0.4 if has_description else 0.1)
        + (0.3 if has_params_doc else 0)
        + (0.2 if has_returns_doc else 0)
        + (0.1 if has_examples else 0)
    )

    evidence = {
        "score": round(score, 3),
        "formula": "(0.4 if length>50 else 0.1) + (0.3 if params else 0) + (0.2 if returns else 0) + (0.1 if examples else 0)",
        "computation": f"{0.4 if has_description else 0.1} + {0.3 if has_params_doc else 0} + {0.2 if has_returns_doc else 0} + {0.1 if has_examples else 0} = {score:.3f}",
        "doc_length": doc_length,
        "has_description": has_description,
        "has_params_doc": has_params_doc,
        "has_returns_doc": has_returns_doc,
        "has_examples": has_examples,
    }

    return round(score, 3), evidence


def compute_b_impl(
    method_info: dict[str, Any], repo_root: Path, rubric: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """
    Compute b_impl using exact formula:
    b_impl = 0.35 * test_coverage + 0.25 * type_annotations + 0.25 * error_handling + 0.15 * documentation

    Returns: (score, evidence)
    """
    # Get component scores
    test_score, test_evidence = compute_test_coverage_score(method_info, repo_root)
    type_score, type_evidence = compute_type_annotations_score(method_info)
    error_score, error_evidence = compute_error_handling_score(method_info, repo_root)
    doc_score, doc_evidence = compute_documentation_score(method_info)

    # Apply exact formula
    b_impl = (
        0.35 * test_score + 0.25 * type_score + 0.25 * error_score + 0.15 * doc_score
    )

    evidence = {
        "formula": "b_impl = 0.35*test_coverage + 0.25*type_annotations + 0.25*error_handling + 0.15*documentation",
        "weights": {
            "test_coverage": 0.35,
            "type_annotations": 0.25,
            "error_handling": 0.25,
            "documentation": 0.15,
        },
        "components": {
            "test_coverage": test_evidence,
            "type_annotations": type_evidence,
            "error_handling": error_evidence,
            "documentation": doc_evidence,
        },
        "computation": f"{0.35}*{test_score} + {0.25}*{type_score} + {0.25}*{error_score} + {0.15}*{doc_score} = {b_impl:.3f}",
        "final_score": round(b_impl, 3),
    }

    return round(b_impl, 3), evidence


def compute_validation_runs_score(layer: str) -> tuple[float, dict[str, Any]]:
    """
    Compute validation runs score.

    ≥20 projects → 1.0 (linear below)
    Fallback: layer_maturity_baseline
    """
    # Layer maturity baselines
    layer_maturity = {
        "orchestrator": 0.7,
        "processor": 0.6,
        "analyzer": 0.5,
        "ingestion": 0.6,
        "executor": 0.5,
        "utility": 0.6,
        "unknown": 0.3,
    }

    base_maturity = layer_maturity.get(layer, layer_maturity["unknown"])

    # Use fallback: no actual run data available
    score = base_maturity

    evidence = {
        "score": round(score, 3),
        "formula": "min(1.0, run_count / 20.0)",
        "fallback_formula": "layer_maturity_baseline",
        "layer": layer,
        "layer_maturity_baseline": base_maturity,
        "note": "Using layer maturity fallback - actual validation run data unavailable",
    }

    return round(score, 3), evidence


def compute_stability_coefficient_score(layer: str) -> tuple[float, dict[str, Any]]:
    """
    Compute stability coefficient score.

    CV < 0.1 → 1.0 (scaled: max(0, 1.0 - cv/0.5))
    Fallback: layer_maturity_baseline * 0.9
    """
    # Layer maturity baselines
    layer_maturity = {
        "orchestrator": 0.7,
        "processor": 0.6,
        "analyzer": 0.5,
        "ingestion": 0.6,
        "executor": 0.5,
        "utility": 0.6,
        "unknown": 0.3,
    }

    base_maturity = layer_maturity.get(layer, layer_maturity["unknown"])

    # Use fallback: layer_maturity * 0.9
    score = base_maturity * 0.9

    evidence = {
        "score": round(score, 3),
        "formula": "max(0.0, 1.0 - (cv / 0.5))",
        "fallback_formula": "layer_maturity_baseline * 0.9",
        "layer": layer,
        "layer_maturity_baseline": base_maturity,
        "computation": f"{base_maturity} * 0.9 = {score:.3f}",
        "note": "Using layer maturity fallback - actual CV data unavailable",
    }

    return round(score, 3), evidence


def compute_failure_rate_score(layer: str) -> tuple[float, dict[str, Any]]:
    """
    Compute failure rate score.

    < 1% → 1.0 (exponential decay: exp(-rate/5.0))
    Fallback: layer_maturity_baseline * 0.85
    """
    # Layer maturity baselines
    layer_maturity = {
        "orchestrator": 0.7,
        "processor": 0.6,
        "analyzer": 0.5,
        "ingestion": 0.6,
        "executor": 0.5,
        "utility": 0.6,
        "unknown": 0.3,
    }

    base_maturity = layer_maturity.get(layer, layer_maturity["unknown"])

    # Use fallback: layer_maturity * 0.85
    score = base_maturity * 0.85

    evidence = {
        "score": round(score, 3),
        "formula": "exp(-failure_rate / 5.0)",
        "fallback_formula": "layer_maturity_baseline * 0.85",
        "layer": layer,
        "layer_maturity_baseline": base_maturity,
        "computation": f"{base_maturity} * 0.85 = {score:.3f}",
        "note": "Using layer maturity fallback - actual failure rate data unavailable",
    }

    return round(score, 3), evidence


def compute_b_deploy(
    method_info: dict[str, Any], rubric: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """
    Compute b_deploy using exact formula:
    b_deploy = 0.4 * validation_runs + 0.35 * stability_coefficient + 0.25 * failure_rate

    Returns: (score, evidence)
    """
    layer = method_info.get("layer", "unknown")

    # Get component scores
    validation_score, validation_evidence = compute_validation_runs_score(layer)
    stability_score, stability_evidence = compute_stability_coefficient_score(layer)
    failure_score, failure_evidence = compute_failure_rate_score(layer)

    # Apply exact formula
    b_deploy = 0.4 * validation_score + 0.35 * stability_score + 0.25 * failure_score

    evidence = {
        "formula": "b_deploy = 0.4*validation_runs + 0.35*stability_coefficient + 0.25*failure_rate",
        "weights": {
            "validation_runs": 0.4,
            "stability_coefficient": 0.35,
            "failure_rate": 0.25,
        },
        "components": {
            "validation_runs": validation_evidence,
            "stability_coefficient": stability_evidence,
            "failure_rate": failure_evidence,
        },
        "computation": f"{0.4}*{validation_score} + {0.35}*{stability_score} + {0.25}*{failure_score} = {b_deploy:.3f}",
        "final_score": round(b_deploy, 3),
    }

    return round(b_deploy, 3), evidence
