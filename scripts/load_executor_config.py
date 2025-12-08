#!/usr/bin/env python3
"""
CLI utility for loading ExecutorConfig with proper hierarchy.

Usage examples:
    # Load production config
    python scripts/load_executor_config.py --env production

    # Load with CLI overrides
    python scripts/load_executor_config.py --env staging --timeout-s 120 --retry 5

    # Load with environment variable
    FARFAN_TIMEOUT_S=90 python scripts/load_executor_config.py --env production

    # Show defaults only
    python scripts/load_executor_config.py --show-defaults
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from farfan_pipeline.core.orchestrator.parameter_loader import (
    get_conservative_defaults,
    load_executor_config,
)


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Load ExecutorConfig with hierarchy: CLI > ENV > file > defaults"
    )

    parser.add_argument(
        "--env",
        type=str,
        default="production",
        choices=["development", "staging", "production"],
        help="Environment to load (default: production)",
    )

    parser.add_argument(
        "--timeout-s",
        type=float,
        dest="timeout_s",
        help="Override timeout in seconds",
    )

    parser.add_argument(
        "--retry",
        type=int,
        help="Override retry attempts",
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        dest="max_tokens",
        help="Override max tokens",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        help="Override temperature",
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Override random seed",
    )

    parser.add_argument(
        "--show-defaults",
        action="store_true",
        help="Show conservative defaults only",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    parser.add_argument(
        "--show-hierarchy",
        action="store_true",
        help="Show loading hierarchy with sources",
    )

    args = parser.parse_args()

    if args.show_defaults:
        defaults = get_conservative_defaults()
        if args.json:
            print(json.dumps(defaults, indent=2))
        else:
            print("Conservative Defaults:")
            print("-" * 40)
            for key, value in defaults.items():
                print(f"  {key}: {value}")
        return 0

    cli_overrides = {}
    if args.timeout_s is not None:
        cli_overrides["timeout_s"] = args.timeout_s
    if args.retry is not None:
        cli_overrides["retry"] = args.retry
    if args.max_tokens is not None:
        cli_overrides["max_tokens"] = args.max_tokens
    if args.temperature is not None:
        cli_overrides["temperature"] = args.temperature
    if args.seed is not None:
        cli_overrides["seed"] = args.seed

    try:
        config = load_executor_config(env=args.env, cli_overrides=cli_overrides or None)

        if args.json:
            config_dict = {
                "timeout_s": config.timeout_s,
                "retry": config.retry,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "seed": config.seed,
            }
            print(json.dumps(config_dict, indent=2))
        elif args.show_hierarchy:
            print("Loading Hierarchy (highest to lowest priority):")
            print("=" * 60)
            print()

            print("1. CLI Arguments (highest priority):")
            if cli_overrides:
                for key, value in cli_overrides.items():
                    print(f"   ✓ {key}: {value}")
            else:
                print("   (none)")
            print()

            print("2. Environment Variables:")
            import os

            env_vars = [
                "FARFAN_TIMEOUT_S",
                "FARFAN_RETRY",
                "FARFAN_MAX_TOKENS",
                "FARFAN_TEMPERATURE",
                "FARFAN_SEED",
            ]
            found_env = False
            for var in env_vars:
                if var in os.environ:
                    print(f"   ✓ {var}: {os.environ[var]}")
                    found_env = True
            if not found_env:
                print("   (none)")
            print()

            print("3. Environment File:")
            env_file = Path(f"system/config/environments/{args.env}.json")
            if env_file.exists():
                print(f"   ✓ {env_file}")
                with open(env_file) as f:
                    env_data = json.load(f)
                    if "executor" in env_data:
                        for key, value in env_data["executor"].items():
                            print(f"      {key}: {value}")
            else:
                print(f"   ✗ {env_file} (not found)")
            print()

            print("4. Conservative Defaults (fallback):")
            defaults = get_conservative_defaults()
            for key, value in defaults.items():
                print(f"   • {key}: {value}")
            print()

            print("=" * 60)
            print("Final Resolved Configuration:")
            print("-" * 60)
            print(f"  timeout_s: {config.timeout_s}")
            print(f"  retry: {config.retry}")
            print(f"  max_tokens: {config.max_tokens}")
            print(f"  temperature: {config.temperature}")
            print(f"  seed: {config.seed}")
        else:
            print(f"ExecutorConfig (env={args.env}):")
            print("-" * 40)
            print(f"  timeout_s: {config.timeout_s}")
            print(f"  retry: {config.retry}")
            print(f"  max_tokens: {config.max_tokens}")
            print(f"  temperature: {config.temperature}")
            print(f"  seed: {config.seed}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
