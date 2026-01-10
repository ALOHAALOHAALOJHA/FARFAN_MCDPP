"""Standalone contract verification utility for pre-execution validation.

This module provides command-line and programmatic interfaces for verifying
all 30 base executor contracts (D1-Q1 through D6-Q5) before pipeline execution.

Usage:
    # Verify all contracts with default class registry
    python -m farfan_pipeline.core.orchestrator.verify_contracts

    # Verify with custom class registry
    python -m farfan_pipeline.core.orchestrator.verify_contracts --strict

    # Programmatic usage
    from orchestration.verify_contracts import verify_all_contracts
    result = verify_all_contracts()
    if not result["passed"]:
        print(f"Validation failed: {result['errors']}")
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

from farfan_pipeline.phases.Phase_2.executors.base_executor_with_contract import (
    BaseExecutorWithContract,
)

logger = logging.getLogger(__name__)


def verify_all_contracts(
    class_registry: dict[str, type[object]] | None = None,
    strict: bool = True,
    verbose: bool = False,
) -> dict[str, Any]:
    """Verify all 30 base executor contracts.

    Args:
        class_registry: Optional class registry. If None, will build one.
        strict: If True, raise exception on any errors.
        verbose: If True, log detailed information.

    Returns:
        Verification result dictionary with:
            - passed: bool
            - total_contracts: int
            - errors: list[str]
            - warnings: list[str]
            - verified_contracts: list[str]

    Raises:
        RuntimeError: If strict=True and verification fails.
    """
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    logger.info("Starting contract verification for 30 base executors")

    if class_registry is None:
        logger.info("Building class registry...")
        try:
            from orchestration.class_registry import (
                build_class_registry,
            )

            class_registry = build_class_registry()
            logger.info(f"Class registry built with {len(class_registry)} classes")
        except Exception as exc:
            logger.error(f"Failed to build class registry: {exc}")
            if strict:
                raise RuntimeError(f"Class registry construction failed: {exc}") from exc
            class_registry = None

    result = BaseExecutorWithContract.verify_all_base_contracts(class_registry=class_registry)

    logger.info(
        f"Verification complete: passed={result['passed']}, "
        f"verified={len(result['verified_contracts'])}/{result['total_contracts']}, "
        f"errors={len(result['errors'])}, warnings={len(result.get('warnings', []))}"
    )

    if not result["passed"]:
        logger.error(f"Contract verification FAILED with {len(result['errors'])} errors")
        for error in result["errors"][:20]:
            logger.error(f"  - {error}")

        if strict:
            raise RuntimeError(
                f"Contract verification failed with {len(result['errors'])} errors. "
                "See logs for details."
            )

    if result.get("warnings"):
        logger.warning(f"Contract verification had {len(result['warnings'])} warnings")
        for warning in result["warnings"][:10]:
            logger.warning(f"  - {warning}")

    return result


def main() -> int:
    """Command-line entry point for contract verification.

    Returns:
        Exit code: 0 if all contracts valid, 1 if any errors.
    """
    parser = argparse.ArgumentParser(
        description="Verify all 30 base executor contracts (D1-Q1 through D6-Q5)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any validation errors (default: False)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--no-class-registry",
        action="store_true",
        help="Skip class registry validation (faster but incomplete)",
    )

    args = parser.parse_args()

    try:
        class_registry = None
        if not args.no_class_registry:
            from orchestration.class_registry import (
                build_class_registry,
            )

            class_registry = build_class_registry()

        result = verify_all_contracts(
            class_registry=class_registry,
            strict=args.strict,
            verbose=args.verbose,
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*60}")
            print("CONTRACT VERIFICATION RESULTS")
            print(f"{'='*60}")
            print(f"Status: {'PASSED' if result['passed'] else 'FAILED'}")
            print(
                f"Verified: {len(result['verified_contracts'])}/{result['total_contracts']} contracts"
            )
            print(f"Errors: {len(result['errors'])}")
            print(f"Warnings: {len(result.get('warnings', []))}")

            if result["errors"]:
                print(f"\n{'='*60}")
                print("ERRORS")
                print(f"{'='*60}")
                for error in result["errors"][:20]:
                    print(f"  - {error}")
                if len(result["errors"]) > 20:
                    print(f"  ... and {len(result['errors']) - 20} more errors")

            if result.get("warnings"):
                print(f"\n{'='*60}")
                print("WARNINGS")
                print(f"{'='*60}")
                for warning in result["warnings"][:10]:
                    print(f"  - {warning}")
                if len(result["warnings"]) > 10:
                    print(f"  ... and {len(result['warnings']) - 10} more warnings")

            if result["verified_contracts"]:
                print(f"\n{'='*60}")
                print("VERIFIED CONTRACTS")
                print(f"{'='*60}")
                for i, contract in enumerate(result["verified_contracts"], 1):
                    print(f"  {i:2d}. {contract}")

        return 0 if result["passed"] else 1

    except Exception as exc:
        logger.error(f"Contract verification failed with exception: {exc}", exc_info=True)
        if args.json:
            print(json.dumps({"error": str(exc), "passed": False}))
        else:
            print(f"\nERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
