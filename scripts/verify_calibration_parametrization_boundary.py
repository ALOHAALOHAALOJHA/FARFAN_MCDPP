#!/usr/bin/env python3
"""
Verification script for calibration vs parametrization boundary.

This script verifies that:
1. Calibration files contain NO runtime parameters
2. ExecutorConfig contains NO quality scores
3. Environment files contain ONLY runtime parameters
4. No crossover between domains

Exit codes:
    0: All checks passed
    1: Violations found
    2: Script error
"""

import json
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any

RUNTIME_PARAMS = {
    "timeout_s",
    "retry",
    "max_tokens",
    "temperature",
    "seed",
    "extra",
    "max_workers",
    "memory_limit_mb",
    "enable_profiling",
    "log_level",
    "logging",
    "resources",
    "monitoring",
    "security",
}

QUALITY_PARAMS = {
    "b_theory",
    "b_impl",
    "b_deploy",
    "fusion_weights",
    "linear_weights",
    "interaction_weights",
    "quality_score",
    "a_l",
    "a_lk",
    "base_quality",
    "layer_quality",
    "role_fusion_parameters",
}


def scan_dict_for_keys(
    data: dict[str, Any], forbidden_keys: set[str], path: str = ""
) -> list[str]:
    """Recursively scan dictionary for forbidden keys."""
    violations = []
    for key, value in data.items():
        full_path = f"{path}.{key}" if path else key

        if key in forbidden_keys:
            violations.append(f"Found forbidden key '{key}' at path: {full_path}")

        if isinstance(value, dict):
            violations.extend(scan_dict_for_keys(value, forbidden_keys, full_path))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    violations.extend(
                        scan_dict_for_keys(item, forbidden_keys, f"{full_path}[{i}]")
                    )

    return violations


def verify_calibration_file(file_path: Path) -> tuple[bool, list[str]]:
    """
    Verify calibration file contains no runtime parameters.

    Args:
        file_path: Path to calibration file

    Returns:
        Tuple of (is_valid, violations)
    """
    try:
        with open(file_path) as f:
            data = json.load(f)
    except Exception as e:
        return False, [f"Failed to load {file_path}: {e}"]

    violations = scan_dict_for_keys(data, RUNTIME_PARAMS)

    if violations:
        return False, [f"❌ {file_path.name}:"] + [f"   {v}" for v in violations]

    return True, [f"✓ {file_path.name}: No runtime parameters found"]


def verify_executor_config() -> tuple[bool, list[str]]:
    """
    Verify ExecutorConfig dataclass contains no quality scores.

    Returns:
        Tuple of (is_valid, violations)
    """
    try:
        from farfan_pipeline.core.orchestrator.executor_config import ExecutorConfig

        config_fields = {f.name for f in fields(ExecutorConfig)}
        quality_fields = config_fields & QUALITY_PARAMS

        if quality_fields:
            return False, [
                "❌ ExecutorConfig contains quality score fields:",
                f"   {quality_fields}",
            ]

        return True, ["✓ ExecutorConfig: No quality score fields found"]

    except Exception as e:
        return False, [f"❌ Failed to check ExecutorConfig: {e}"]


def verify_environment_file(file_path: Path) -> tuple[bool, list[str]]:
    """
    Verify environment file contains only runtime parameters.

    Args:
        file_path: Path to environment file

    Returns:
        Tuple of (is_valid, violations)
    """
    try:
        with open(file_path) as f:
            data = json.load(f)
    except Exception as e:
        return False, [f"Failed to load {file_path}: {e}"]

    violations = scan_dict_for_keys(data, QUALITY_PARAMS)

    allowed_top_keys = {
        "_metadata",
        "_notes",
        "executor",
        "logging",
        "resources",
        "monitoring",
        "security",
    }
    invalid_top_keys = set(data.keys()) - allowed_top_keys

    if invalid_top_keys:
        violations.append(
            f"Invalid top-level keys in {file_path.name}: {invalid_top_keys}"
        )

    if violations:
        return False, [f"❌ {file_path.name}:"] + [f"   {v}" for v in violations]

    return True, [f"✓ {file_path.name}: Only runtime parameters found"]


def main() -> int:
    """Main verification routine."""
    print("=" * 80)
    print("Calibration vs Parametrization Boundary Verification")
    print("=" * 80)
    print()

    all_valid = True
    results: list[str] = []

    print("Checking calibration files...")
    print("-" * 80)

    calibration_files = [
        Path("system/config/calibration/intrinsic_calibration.json"),
        Path("system/config/questionnaire/questionnaire_monolith.json"),
        Path("config/json_files_ no_schemas/fusion_specification.json"),
    ]

    for cal_file in calibration_files:
        if not cal_file.exists():
            results.append(f"⚠ {cal_file.name}: File not found (skipped)")
            continue

        is_valid, messages = verify_calibration_file(cal_file)
        all_valid = all_valid and is_valid
        results.extend(messages)

    print("\n".join(results))
    print()

    print("Checking ExecutorConfig...")
    print("-" * 80)

    is_valid, messages = verify_executor_config()
    all_valid = all_valid and is_valid
    print("\n".join(messages))
    print()

    print("Checking environment files...")
    print("-" * 80)

    env_results: list[str] = []
    env_files = [
        Path("system/config/environments/development.json"),
        Path("system/config/environments/staging.json"),
        Path("system/config/environments/production.json"),
    ]

    for env_file in env_files:
        if not env_file.exists():
            env_results.append(f"⚠ {env_file.name}: File not found (skipped)")
            continue

        is_valid, messages = verify_environment_file(env_file)
        all_valid = all_valid and is_valid
        env_results.extend(messages)

    print("\n".join(env_results))
    print()

    print("=" * 80)
    if all_valid:
        print("✅ ALL CHECKS PASSED")
        print("=" * 80)
        return 0
    else:
        print("❌ VIOLATIONS FOUND")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Script error: {e}", file=sys.stderr)
        sys.exit(2)
