#!/usr/bin/env python3
"""
Phase 0 CLI Entry Point
========================

Thin CLI wrapper for Phase 0: Validation, Hardening & Bootstrap.

This module:
1. Parses CLI arguments (plan path, artifacts dir)
2. Invokes VerifiedPipelineRunner (P0.0-P0.3)
3. Calls WiringBootstrap to produce WiringComponents
4. Returns WiringComponents for handoff to Phase 1

Phase 0 does NOT:
- Ingest documents (Phase 1)
- Orchestrate executors (Phase 2+)
- Perform semantic analysis
- Generate reports

Output: WiringComponents dataclass ready for Phase 1 handoff.

Author: Phase 0 Compliance Team
Version: 3.0.0
Specification: P00-EN v2.0
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 0
__stage__ = 90
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "LOW"
__execution_pattern__ = "Singleton"

import argparse
import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from farfan_pipeline.phases.Phase_00.phase0_10_00_paths import (
    PROJECT_ROOT,
)
from farfan_pipeline.phases.Phase_00.phase0_90_01_verified_pipeline_runner import (
    VerifiedPipelineRunner,
)
from farfan_pipeline.phases.Phase_00.phase0_90_02_bootstrap import (
    WiringBootstrap,
)

if TYPE_CHECKING:
    pass


async def run_phase_zero(
    plan_path: Path,
    artifacts_dir: Path,
    questionnaire_path: Path | None = None,
) -> WiringComponents | None:
    """
    Execute complete Phase 0 sequence.

    Args:
        plan_path: Path to input policy plan PDF
        artifacts_dir: Directory for output artifacts
        questionnaire_path: Path to questionnaire (defaults to canonical)

    Returns:
        WiringComponents if Phase 0 succeeds, None on failure
    """
    if questionnaire_path is None:
        questionnaire_path = QUESTIONNAIRE_FILE

    # P0.0-P0.3: Run verified pipeline runner
    runner = VerifiedPipelineRunner(
        plan_pdf_path=plan_path,
        artifacts_dir=artifacts_dir,
        questionnaire_path=questionnaire_path,
    )

    phase0_success = await runner.run_phase_zero()

    if not phase0_success:
        runner.generate_failure_manifest()
        return None

    # Bootstrap: Assemble WiringComponents
    try:
        bootstrap = WiringBootstrap()
        wiring = bootstrap.bootstrap()

        print("\n" + "=" * 80, flush=True)
        print("PHASE 0 COMPLETE - WiringComponents ready for Phase 1 handoff", flush=True)
        print("=" * 80 + "\n", flush=True)

        return wiring

    except Exception as e:
        print(f"\n❌ Bootstrap failed: {e}", flush=True)
        runner.errors.append(f"Bootstrap failed: {e}")
        runner.generate_failure_manifest()
        return None


def main() -> int:
    """CLI entry point for Phase 0."""
    parser = argparse.ArgumentParser(description="Phase 0: Validation, Hardening & Bootstrap")
    parser.add_argument(
        "--plan",
        type=str,
        default="data/plans/Plan_1.pdf",
        help="Path to plan PDF (default: data/plans/Plan_1.pdf)",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=str,
        default="artifacts/plan1",
        help="Directory for artifacts (default: artifacts/plan1)",
    )
    parser.add_argument(
        "--questionnaire",
        type=str,
        default=None,
        help="Path to questionnaire (default: canonical questionnaire)",
    )

    args = parser.parse_args()

    # Resolve paths
    plan_path = PROJECT_ROOT / args.plan
    artifacts_dir = PROJECT_ROOT / args.artifacts_dir
    questionnaire_path = Path(args.questionnaire) if args.questionnaire else None

    print("=" * 80, flush=True)
    print("F.A.R.F.A.N PHASE 0: VALIDATION, HARDENING & BOOTSTRAP", flush=True)
    print("=" * 80, flush=True)
    print(f"Plan: {plan_path}", flush=True)
    print(f"Artifacts: {artifacts_dir}", flush=True)
    print("=" * 80 + "\n", flush=True)

    # Run Phase 0
    wiring = asyncio.run(run_phase_zero(plan_path, artifacts_dir, questionnaire_path))

    if wiring is None:
        print("\nPHASE_0_VERIFIED=0", flush=True)
        return 1

    print("\nPHASE_0_VERIFIED=1", flush=True)
    print(f"WiringComponents ready: {type(wiring).__name__}", flush=True)
    return 0


def cli() -> None:
    """Console script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
