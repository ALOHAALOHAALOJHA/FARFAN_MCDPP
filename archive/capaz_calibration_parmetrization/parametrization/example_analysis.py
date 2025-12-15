#!/usr/bin/env python3
"""
Example usage of the signature-based parametrization analysis system

Demonstrates:
- Loading and querying method signatures
- Finding methods with specific patterns
- Analyzing parameter usage
- Generating custom reports
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_signatures(signatures_path: Path) -> dict[str, Any]:
    with open(signatures_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_methods_with_pattern(signatures: dict[str, Any], pattern: str) -> list[str]:
    results = []
    for sig_name, sig_data in signatures.get("signatures", {}).items():
        if pattern.lower() in sig_name.lower():
            results.append(sig_name)
        elif pattern.lower() in sig_data.get("method_name", "").lower():
            results.append(sig_name)
    return results


def find_methods_with_critical_params(signatures: dict[str, Any]) -> list[tuple[str, list[str]]]:
    results = []
    for sig_name, sig_data in signatures.get("signatures", {}).items():
        critical = sig_data.get("critical_optional", [])
        if critical:
            results.append((sig_name, critical))
    return results


def find_methods_with_hardcoded(signatures: dict[str, Any]) -> list[tuple[str, int]]:
    results = []
    for sig_name, sig_data in signatures.get("signatures", {}).items():
        hardcoded = sig_data.get("hardcoded_parameters", [])
        if hardcoded:
            results.append((sig_name, len(hardcoded)))
    return results


def analyze_parameter_usage(signatures: dict[str, Any]) -> dict[str, int]:
    param_counts: dict[str, int] = {}

    for sig_data in signatures.get("signatures", {}).values():
        for param in sig_data.get("required_inputs", []):
            param_counts[param] = param_counts.get(param, 0) + 1
        for param in sig_data.get("optional_inputs", []):
            param_counts[param] = param_counts.get(param, 0) + 1

    return dict(sorted(param_counts.items(), key=lambda x: x[1], reverse=True))


def generate_custom_report(signatures_path: Path) -> None:
    print("=" * 70)
    print("CUSTOM SIGNATURE ANALYSIS REPORT")
    print("=" * 70)
    print()

    signatures = load_signatures(signatures_path)

    print("[1] Bayesian Methods")
    print("-" * 70)
    bayesian_methods = find_methods_with_pattern(signatures, "bayesian")
    for method in bayesian_methods[:10]:
        print(f"  - {method}")
    print(f"  Total: {len(bayesian_methods)}")
    print()

    print("[2] Methods with Critical Parameters")
    print("-" * 70)
    critical_methods = find_methods_with_critical_params(signatures)
    for method, params in critical_methods[:10]:
        print(f"  - {method}")
        print(f"    Critical params: {', '.join(params)}")
    print(f"  Total: {len(critical_methods)}")
    print()

    print("[3] Methods with Hardcoded Parameters")
    print("-" * 70)
    hardcoded_methods = find_methods_with_hardcoded(signatures)
    hardcoded_methods.sort(key=lambda x: x[1], reverse=True)
    for method, count in hardcoded_methods[:10]:
        print(f"  - {method} ({count} hardcoded params)")
    print(f"  Total methods: {len(hardcoded_methods)}")
    total_hardcoded = sum(count for _, count in hardcoded_methods)
    print(f"  Total hardcoded params: {total_hardcoded}")
    print()

    print("[4] Most Common Parameter Names")
    print("-" * 70)
    param_usage = analyze_parameter_usage(signatures)
    for param, count in list(param_usage.items())[:15]:
        print(f"  {param:<30} {count:>5} uses")
    print()

    print("[5] Executor Methods")
    print("-" * 70)
    executor_methods = find_methods_with_pattern(signatures, "executor")
    for method in executor_methods[:10]:
        print(f"  - {method}")
    print(f"  Total: {len(executor_methods)}")
    print()

    print("=" * 70)
    print("END OF REPORT")
    print("=" * 70)


def query_specific_method(signatures_path: Path, method_pattern: str) -> None:
    signatures = load_signatures(signatures_path)

    print(f"\nSearching for methods matching: '{method_pattern}'")
    print("=" * 70)

    matches = find_methods_with_pattern(signatures, method_pattern)

    if not matches:
        print(f"No methods found matching '{method_pattern}'")
        return

    for match in matches:
        sig_data = signatures["signatures"][match]
        print(f"\n{match}")
        print("-" * 70)
        print(f"Module:       {sig_data['module']}")
        print(f"Class:        {sig_data['class_name']}")
        print(f"Method:       {sig_data['method_name']}")
        print(f"Line:         {sig_data['line_number']}")
        print(f"Output type:  {sig_data['output_type']}")

        if sig_data['required_inputs']:
            print(f"Required:     {', '.join(sig_data['required_inputs'])}")
        if sig_data['optional_inputs']:
            print(f"Optional:     {', '.join(sig_data['optional_inputs'])}")
        if sig_data['critical_optional']:
            print(f"Critical:     {', '.join(sig_data['critical_optional'])}")
        if sig_data['hardcoded_parameters']:
            print(f"Hardcoded:    {len(sig_data['hardcoded_parameters'])} parameters")
            for param in sig_data['hardcoded_parameters'][:3]:
                print(f"              {param['variable']} = {param['value']}")

        if sig_data['docstring']:
            docstring = sig_data['docstring'][:200]
            print(f"Description:  {docstring}...")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    parametrization_dir = repo_root / "src" / "cross_cutting_infrastrucuture" / "capaz_calibration_parmetrization" / "parametrization"

    signatures_path = parametrization_dir / "method_signatures.json"

    if not signatures_path.exists():
        print(f"Error: {signatures_path} not found")
        print("Run 'python run_signature_analysis.py' first to generate signatures")
        return

    import sys
    if len(sys.argv) > 1:
        query_specific_method(signatures_path, sys.argv[1])
    else:
        generate_custom_report(signatures_path)


if __name__ == "__main__":
    main()
