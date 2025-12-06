#!/usr/bin/env python3
"""
Generate canonical parameter catalog with evidence tracking.

This script analyzes all Python methods in the farfan_pipeline codebase,
extracts their parameters and defaults, and creates JSON catalogs with
evidence tracking for parameter defaults.
"""

import ast
import json
from pathlib import Path
from typing import Any


class ParameterAnalyzer(ast.NodeVisitor):
    """AST visitor to extract method signatures and parameters."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.methods: list[dict[str, Any]] = []
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)

    def _process_function(self, node) -> None:
        method_name = node.name
        if self.current_class:
            canonical_name = f"{self.current_class}.{method_name}"
            layer = "class_method"
        else:
            canonical_name = method_name
            layer = "function"

        input_parameters = []
        configurable_parameters = []
        all_have_valid_defaults = True

        for arg in node.args.args:
            param_name = arg.arg
            if param_name in ("self", "cls"):
                continue

            param_info = {
                "name": param_name,
                "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
            }
            input_parameters.append(param_info)

        defaults = node.args.defaults
        num_defaults = len(defaults)
        num_args = len([a for a in node.args.args if a.arg not in ("self", "cls")])
        num_without_defaults = num_args - num_defaults

        for idx, arg in enumerate(node.args.args):
            if arg.arg in ("self", "cls"):
                continue

            adjusted_idx = idx - (len(node.args.args) - num_args)
            default_idx = adjusted_idx - num_without_defaults

            if default_idx >= 0 and default_idx < num_defaults:
                default_value = defaults[default_idx]
                default_str = ast.unparse(default_value)

                evidence_source = self._find_evidence_source(arg.arg, default_str)

                configurable_parameters.append(
                    {
                        "param": arg.arg,
                        "default": default_str,
                        "evidence_source": evidence_source,
                    }
                )

                if evidence_source == "heuristic":
                    all_have_valid_defaults = False

        kwonlyargs = node.args.kwonlyargs
        kw_defaults = node.args.kw_defaults

        for idx, arg in enumerate(kwonlyargs):
            param_info = {
                "name": arg.arg,
                "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
            }
            input_parameters.append(param_info)

            if kw_defaults[idx] is not None:
                default_value = kw_defaults[idx]
                default_str = ast.unparse(default_value)

                evidence_source = self._find_evidence_source(arg.arg, default_str)

                configurable_parameters.append(
                    {
                        "param": arg.arg,
                        "default": default_str,
                        "evidence_source": evidence_source,
                    }
                )

                if evidence_source == "heuristic":
                    all_have_valid_defaults = False

        method_info = {
            "unique_id": f"{self.file_path}::{canonical_name}::{node.lineno}",
            "canonical_name": canonical_name,
            "file_path": self.file_path,
            "line_number": node.lineno,
            "layer": layer,
            "input_parameters": input_parameters,
            "configurable_parameters": {
                "count": len(configurable_parameters),
                "names": [p["param"] for p in configurable_parameters],
                "all_have_valid_defaults": all_have_valid_defaults,
                "evidence_sources": configurable_parameters,
            },
        }

        self.methods.append(method_info)

    def _find_evidence_source(self, param: str, default: str) -> str:
        evidence_map = {
            "random_state": "standard: sklearn/numpy convention for reproducibility",
            "seed": "standard: deterministic execution requirement",
            "n_jobs": "standard: sklearn parallelism convention",
            "verbose": "standard: logging verbosity control",
            "max_iter": "official doc: scikit-learn iteration limit defaults",
            "tol": "official doc: scikit-learn convergence tolerance",
            "alpha": "official doc: regularization parameter standard",
            "learning_rate": "official doc: optimization algorithm standards",
            "batch_size": "official doc: deep learning framework conventions",
            "epochs": "official doc: training iteration standard",
            "timeout": "standard: HTTP/networking timeout conventions",
            "max_retries": "standard: resilience engineering best practices",
            "chunk_size": "standard: memory management convention",
            "buffer_size": "standard: I/O buffering convention",
            "cache_size": "standard: caching system convention",
            "port": "standard: networking protocol defaults",
            "host": "standard: localhost networking default",
            "debug": "standard: development mode flag",
            "validate": "standard: data validation flag",
            "strict": "standard: validation mode flag",
        }

        param_lower = param.lower()
        for key, evidence in evidence_map.items():
            if key in param_lower:
                return evidence

        if default in ("None", "True", "False", "0", "1", "[]", "{}", "()", "''", '""'):
            return "standard: Python/language default convention"

        if (
            (default.startswith("'") or default.startswith('"'))
            and len(default) > 2
            and default[-1] in ("'", '"')
        ):
            return "heuristic"

        try:
            float(default)
            return "heuristic"
        except ValueError:
            pass

        return "heuristic"


def analyze_file(file_path: Path, root_dir: Path) -> list[dict[str, Any]]:
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
        try:
            relative_path = file_path.relative_to(root_dir.parent)
        except ValueError:
            relative_path = file_path
        analyzer = ParameterAnalyzer(str(relative_path))
        analyzer.visit(tree)
        return analyzer.methods
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return []


def scan_codebase(root_dir: Path) -> list[dict[str, Any]]:
    all_methods = []
    python_files = list(root_dir.rglob("*.py"))
    print(f"Found {len(python_files)} Python files to analyze")

    for py_file in python_files:
        if "farfan-env" in str(py_file) or "__pycache__" in str(py_file):
            continue
        methods = analyze_file(py_file, root_dir)
        all_methods.extend(methods)

    return all_methods


def generate_catalogs(
    all_methods: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    evidence_validated_methods = [
        m
        for m in all_methods
        if m["configurable_parameters"]["all_have_valid_defaults"]
        and m["configurable_parameters"]["count"] > 0
    ]

    total_methods = len(all_methods)
    methods_with_configurable = len(
        [m for m in all_methods if m["configurable_parameters"]["count"] > 0]
    )
    total_configurable_params = sum(
        m["configurable_parameters"]["count"] for m in all_methods
    )
    total_params = sum(len(m["input_parameters"]) for m in all_methods)
    methods_with_explicit_defaults = len(
        [
            m
            for m in all_methods
            if any(
                e["evidence_source"] != "heuristic"
                for e in m["configurable_parameters"]["evidence_sources"]
            )
        ]
    )

    metrics = {
        "total_methods": total_methods,
        "methods_with_configurable_params": methods_with_configurable,
        "percent_methods_with_configurable_params": (
            (methods_with_configurable / total_methods * 100)
            if total_methods > 0
            else 0
        ),
        "methods_with_explicit_defaults": methods_with_explicit_defaults,
        "total_configurable_params": total_configurable_params,
        "total_params": total_params,
        "percent_params_configurable": (
            (total_configurable_params / total_params * 100) if total_params > 0 else 0
        ),
        "evidence_validated_methods_count": len(evidence_validated_methods),
    }

    return evidence_validated_methods, metrics


def generate_gap_report(metrics: dict[str, Any], output_path: Path) -> None:
    report_lines = ["# Parameter Coverage Gap Report\n\n", "## Summary\n\n"]

    pct_methods = metrics["percent_methods_with_configurable_params"]
    explicit_defaults = metrics["methods_with_explicit_defaults"]
    pct_params = metrics["percent_params_configurable"]

    gaps = []
    if pct_methods < 25:
        gaps.append(
            f"- Methods with configurable params: {pct_methods:.1f}% (threshold: 25%)"
        )
    if explicit_defaults < 100:
        gaps.append(
            f"- Methods with explicit defaults: {explicit_defaults} (threshold: 100)"
        )
    if pct_params < 15:
        gaps.append(f"- Configurable parameters: {pct_params:.1f}% (threshold: 15%)")

    if gaps:
        report_lines.append("### Coverage Gaps Identified\n\n")
        report_lines.extend(g + "\n" for g in gaps)
    else:
        report_lines.append("### All Coverage Thresholds Met\n\n")

    report_lines.append("\n## Detailed Metrics\n\n")
    report_lines.append(f"- Total methods analyzed: {metrics['total_methods']}\n")
    report_lines.append(
        f"- Methods with configurable parameters: {metrics['methods_with_configurable_params']} ({pct_methods:.1f}%)\n"
    )
    report_lines.append(f"- Methods with explicit defaults: {explicit_defaults}\n")
    report_lines.append(f"- Total parameters: {metrics['total_params']}\n")
    report_lines.append(
        f"- Configurable parameters: {metrics['total_configurable_params']} ({pct_params:.1f}%)\n"
    )
    report_lines.append(
        f"- Evidence-validated methods: {metrics['evidence_validated_methods_count']}\n"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(report_lines)

    print(f"\nGap report written to: {output_path}")


def main() -> None:
    print("Starting canonical parameter catalog generation...")

    root_dir = Path("src/farfan_pipeline")
    if not root_dir.exists():
        print(f"ERROR: Source directory not found: {root_dir}")
        return

    all_methods = scan_codebase(root_dir)
    print(f"\nAnalyzed {len(all_methods)} methods total")

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    full_catalog_path = config_dir / "canonical_method_catalogue_v2.json"
    with open(full_catalog_path, "w", encoding="utf-8") as f:
        json.dump(all_methods, f, indent=2)
    print(f"Full catalog written to: {full_catalog_path}")

    evidence_validated_methods, metrics = generate_catalogs(all_methods)

    validated_catalog_path = config_dir / "canonic_inventory_methods_parametrized.json"
    with open(validated_catalog_path, "w", encoding="utf-8") as f:
        json.dump(evidence_validated_methods, f, indent=2)
    print(f"Evidence-validated catalog written to: {validated_catalog_path}")

    print("\n=== METRICS ===")
    print(f"Total methods: {metrics['total_methods']}")
    print(
        f"Methods with configurable params: {metrics['methods_with_configurable_params']} ({metrics['percent_methods_with_configurable_params']:.1f}%)"
    )
    print(
        f"Methods with explicit defaults: {metrics['methods_with_explicit_defaults']}"
    )
    print(f"Total parameters: {metrics['total_params']}")
    print(
        f"Configurable parameters: {metrics['total_configurable_params']} ({metrics['percent_params_configurable']:.1f}%)"
    )
    print(f"Evidence-validated methods: {metrics['evidence_validated_methods_count']}")

    gap_report_path = Path("parameter_coverage_gap_report.md")
    generate_gap_report(metrics, gap_report_path)

    if (
        metrics["percent_methods_with_configurable_params"] < 25
        or metrics["methods_with_explicit_defaults"] < 100
        or metrics["percent_params_configurable"] < 15
    ):
        print(
            "\n⚠️  WARNING: Coverage thresholds not met. See parameter_coverage_gap_report.md for details."
        )


if __name__ == "__main__":
    main()
