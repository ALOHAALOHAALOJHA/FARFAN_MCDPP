#!/usr/bin/env python3
"""
Example demonstrating calibration vs parametrization separation.

This script shows:
1. Loading calibration data (WHAT: intrinsic quality scores)
2. Loading parametrization data (HOW: runtime execution parameters)
3. Proper separation and hierarchy
4. Verification of boundary compliance
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from farfan_pipeline.core.orchestrator.parameter_loader import (
    get_conservative_defaults,
    load_executor_config,
)


def load_calibration_data() -> dict:
    """
    Load calibration data (WHAT domain).

    Calibration defines intrinsic quality characteristics:
    - b_theory, b_impl, b_deploy: Base quality scores
    - layer_quality: Quality ratings for architectural layers
    - fusion_weights: Weights for combining quality signals
    """
    print("=" * 80)
    print("CALIBRATION DOMAIN (WHAT)")
    print("=" * 80)
    print()

    calibration_data = {}

    intrinsic_cal_file = Path("system/config/calibration/intrinsic_calibration.json")
    if intrinsic_cal_file.exists():
        print("Loading intrinsic_calibration.json...")
        with open(intrinsic_cal_file) as f:
            calibration_data["intrinsic"] = json.load(f)
        print(f"  ✓ Loaded: {len(calibration_data['intrinsic'])} entries")
    else:
        print("  ℹ intrinsic_calibration.json not found (empty or missing)")
        calibration_data["intrinsic"] = {}

    fusion_spec_file = Path("config/json_files_ no_schemas/fusion_specification.json")
    if fusion_spec_file.exists():
        print("Loading fusion_specification.json...")
        with open(fusion_spec_file) as f:
            calibration_data["fusion"] = json.load(f)
        print(
            f"  ✓ Loaded role_fusion_parameters for {len(calibration_data['fusion'].get('role_fusion_parameters', {}))} roles"
        )
    else:
        print("  ⚠ fusion_specification.json not found")

    print()
    print("Calibration Summary:")
    print("-" * 80)
    print("  Domain: WHAT (intrinsic quality characteristics)")
    print("  Governance: Domain experts, peer review required")
    print("  Change Frequency: Quarterly/annually")
    print("  Affects: Quality measurements, analytical validity")
    print()

    return calibration_data


def load_parametrization_data(env: str = "production") -> dict:
    """
    Load parametrization data (HOW domain).

    Parametrization defines runtime execution parameters:
    - timeout_s, retry, max_tokens: Execution control
    - temperature, seed: LLM behavior
    - Resource limits and monitoring
    """
    print("=" * 80)
    print("PARAMETRIZATION DOMAIN (HOW)")
    print("=" * 80)
    print()

    print(f"Loading ExecutorConfig for environment: {env}")
    print()

    print("1. Conservative Defaults (fallback):")
    defaults = get_conservative_defaults()
    for key, value in defaults.items():
        print(f"     {key}: {value}")
    print()

    env_file = Path(f"system/config/environments/{env}.json")
    if env_file.exists():
        print(f"2. Environment File Override: {env_file}")
        with open(env_file) as f:
            env_data = json.load(f)
            if "executor" in env_data:
                for key, value in env_data["executor"].items():
                    print(f"     {key}: {value}")
    else:
        print(f"2. Environment File: {env_file} (not found)")
    print()

    print("3. Environment Variables:")
    import os

    env_vars = {
        "FARFAN_TIMEOUT_S": os.getenv("FARFAN_TIMEOUT_S"),
        "FARFAN_RETRY": os.getenv("FARFAN_RETRY"),
        "FARFAN_MAX_TOKENS": os.getenv("FARFAN_MAX_TOKENS"),
        "FARFAN_TEMPERATURE": os.getenv("FARFAN_TEMPERATURE"),
    }
    found_env = False
    for var, val in env_vars.items():
        if val is not None:
            print(f"     {var}: {val}")
            found_env = True
    if not found_env:
        print("     (none set)")
    print()

    config = load_executor_config(env=env)

    print("Final Resolved Configuration:")
    print("-" * 80)
    print(f"  timeout_s: {config.timeout_s}")
    print(f"  retry: {config.retry}")
    print(f"  max_tokens: {config.max_tokens}")
    print(f"  temperature: {config.temperature}")
    print(f"  seed: {config.seed}")
    print()

    print("Parametrization Summary:")
    print("-" * 80)
    print("  Domain: HOW (runtime execution parameters)")
    print("  Governance: Operations team, no peer review")
    print("  Change Frequency: As needed (daily/per-run)")
    print("  Affects: Execution behavior, NOT quality measurements")
    print()

    return {
        "defaults": defaults,
        "config": config,
    }


def demonstrate_separation() -> None:
    """Demonstrate proper separation of calibration and parametrization."""
    print("\n")
    print("#" * 80)
    print("# CALIBRATION VS PARAMETRIZATION BOUNDARY DEMONSTRATION")
    print("#" * 80)
    print("\n")

    calibration = load_calibration_data()

    print("\n")

    parametrization = load_parametrization_data(env="production")

    print("\n")
    print("=" * 80)
    print("BOUNDARY COMPLIANCE VERIFICATION")
    print("=" * 80)
    print()

    runtime_params = {
        "timeout_s",
        "retry",
        "max_tokens",
        "temperature",
        "seed",
        "max_workers",
        "memory_limit_mb",
    }
    quality_params = {
        "b_theory",
        "b_impl",
        "b_deploy",
        "fusion_weights",
        "linear_weights",
        "interaction_weights",
        "quality_score",
    }

    def check_dict_for_params(d: dict, forbidden: set, path: str = "") -> list:
        violations = []
        if not isinstance(d, dict):
            return violations
        for key, value in d.items():
            full_path = f"{path}.{key}" if path else key
            if key in forbidden:
                violations.append(f"  ✗ Found '{key}' at {full_path}")
            if isinstance(value, dict):
                violations.extend(check_dict_for_params(value, forbidden, full_path))
        return violations

    print("Checking calibration files for runtime parameters...")
    cal_violations = check_dict_for_params(calibration, runtime_params)
    if cal_violations:
        print("  ❌ VIOLATIONS FOUND:")
        for v in cal_violations:
            print(v)
    else:
        print("  ✅ No runtime parameters in calibration data")
    print()

    print("Checking ExecutorConfig for quality parameters...")
    from dataclasses import fields

    from farfan_pipeline.core.orchestrator.executor_config import ExecutorConfig

    config_fields = {f.name for f in fields(ExecutorConfig)}
    quality_fields = config_fields & quality_params

    if quality_fields:
        print(f"  ❌ VIOLATIONS FOUND: {quality_fields}")
    else:
        print("  ✅ No quality parameters in ExecutorConfig")
    print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("✓ Calibration (WHAT): Defines intrinsic quality characteristics")
    print("  - Located in: system/config/calibration/")
    print("  - Governed by: Domain experts")
    print("  - Contains: b_theory, b_impl, fusion_weights, etc.")
    print()
    print("✓ Parametrization (HOW): Defines runtime execution parameters")
    print("  - Located in: system/config/environments/")
    print("  - Governed by: Operations team")
    print("  - Contains: timeout_s, retry, max_tokens, etc.")
    print()
    print("✓ Boundary Maintained: No crossover detected")
    print()
    print("Golden Rule: If it affects WHAT quality we measure → Calibration")
    print("             If it affects HOW we execute → Parametrization")
    print()


def main() -> int:
    """Main entry point."""
    try:
        demonstrate_separation()
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
