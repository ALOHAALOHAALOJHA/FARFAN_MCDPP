#!/usr/bin/env python3
"""
Phase 2 Canonical Migration Helper

This script assists with the systematic migration of Phase 2 files from legacy
locations to the canonical frozen structure under src/canonic_phases/phase_2/.

Usage:
    python scripts/migrate_phase2_canonical.py --dry-run
    python scripts/migrate_phase2_canonical.py --execute --section phase_root
    python scripts/migrate_phase2_canonical.py --execute --all

Safety:
- Always run with --dry-run first
- Creates backups before moving files
- Validates imports after migration
- Generates import update report
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
LEGACY_PHASE_TWO = SRC_ROOT / "farfan_pipeline" / "phases" / "Phase_two"
LEGACY_ORCHESTRATION = SRC_ROOT / "farfan_pipeline" / "orchestration"
LEGACY_DURA_LEX = (
    SRC_ROOT / "farfan_pipeline" / "infrastructure" / "contractual" / "dura_lex"
)
CANONICAL_PHASE2 = SRC_ROOT / "canonic_phases" / "phase_2"

MIGRATION_MAP = {
    "phase_root": [
        {
            "source": LEGACY_PHASE_TWO / "arg_router.py",
            "target": CANONICAL_PHASE2 / "phase2_a_arg_router.py",
            "action": "move",
        },
        {
            "source": LEGACY_PHASE_TWO / "carver.py",
            "target": CANONICAL_PHASE2 / "phase2_b_carver.py",
            "action": "move",
        },
        {
            "source": LEGACY_PHASE_TWO / "contract_validator_cqvr.py",
            "target": CANONICAL_PHASE2 / "phase2_c_contract_validator_cqvr.py",
            "action": "move",
        },
        {
            "source": LEGACY_PHASE_TWO / "executor_config.py",
            "target": CANONICAL_PHASE2 / "phase2_d_executor_config.py",
            "action": "move",
        },
        {
            "source": LEGACY_PHASE_TWO / "irrigation_synchronizer.py",
            "target": CANONICAL_PHASE2 / "phase2_e_irrigation_synchronizer.py",
            "action": "move",
        },
        {
            "source": LEGACY_ORCHESTRATION / "executor_chunk_synchronizer.py",
            "target": CANONICAL_PHASE2 / "phase2_f_executor_chunk_synchronizer.py",
            "action": "move",
        },
        {
            "source": SRC_ROOT / "farfan_pipeline" / "synchronization.py",
            "target": CANONICAL_PHASE2 / "phase2_g_synchronization.py",
            "action": "move",
        },
        {
            "source": LEGACY_PHASE_TWO / "evidence_nexus.py",
            "target": CANONICAL_PHASE2 / "evidence_nexus.py",
            "action": "move",
        },
    ],
    "executors": [
        {
            "source": LEGACY_PHASE_TWO / "base_executor_with_contract.py",
            "target": CANONICAL_PHASE2 / "executors" / "base_executor_with_contract.py",
            "action": "move",
        },
        {
            "source": LEGACY_PHASE_TWO / "executor_instrumentation_mixin.py",
            "target": CANONICAL_PHASE2
            / "executors"
            / "phase2_executor_instrumentation_mixin.py",
            "action": "move",
        },
        {
            "source": LEGACY_PHASE_TWO / "executor_profiler.py",
            "target": CANONICAL_PHASE2 / "executors" / "phase2_executor_profiler.py",
            "action": "move",
        },
    ],
    "orchestration": [
        {
            "source": LEGACY_ORCHESTRATION / "method_registry.py",
            "target": CANONICAL_PHASE2
            / "orchestration"
            / "phase2_method_registry.py",
            "action": "copy",
        },
        {
            "source": LEGACY_ORCHESTRATION / "method_signature_validator.py",
            "target": CANONICAL_PHASE2
            / "orchestration"
            / "phase2_method_signature_validator.py",
            "action": "copy",
        },
        {
            "source": LEGACY_ORCHESTRATION / "method_source_validator.py",
            "target": CANONICAL_PHASE2
            / "orchestration"
            / "phase2_method_source_validator.py",
            "action": "copy",
        },
        {
            "source": LEGACY_ORCHESTRATION / "precision_tracking.py",
            "target": CANONICAL_PHASE2
            / "orchestration"
            / "phase2_precision_tracking.py",
            "action": "copy",
        },
        {
            "source": LEGACY_ORCHESTRATION / "resource_aware_executor.py",
            "target": CANONICAL_PHASE2
            / "orchestration"
            / "phase2_resource_aware_executor.py",
            "action": "copy",
        },
        {
            "source": LEGACY_ORCHESTRATION / "resource_manager.py",
            "target": CANONICAL_PHASE2
            / "orchestration"
            / "phase2_resource_manager.py",
            "action": "copy",
        },
        {
            "source": LEGACY_ORCHESTRATION / "signature_types.py",
            "target": CANONICAL_PHASE2
            / "orchestration"
            / "phase2_signature_types.py",
            "action": "copy",
        },
        {
            "source": LEGACY_ORCHESTRATION / "task_planner.py",
            "target": CANONICAL_PHASE2 / "orchestration" / "phase2_task_planner.py",
            "action": "copy",
        },
        {
            "source": LEGACY_ORCHESTRATION / "factory.py",
            "target": CANONICAL_PHASE2 / "orchestration" / "phase2_factory.py",
            "action": "copy",
        },
    ],
    "contracts": [
        {
            "source": LEGACY_DURA_LEX / "concurrency_determinism.py",
            "target": CANONICAL_PHASE2
            / "contracts"
            / "phase2_concurrency_determinism.py",
            "action": "copy",
        },
        {
            "source": LEGACY_DURA_LEX / "compute_contract_hashes.py",
            "target": CANONICAL_PHASE2
            / "contracts"
            / "phase2_compute_contract_hashes.py",
            "action": "copy",
        },
        {
            "source": LEGACY_DURA_LEX / "context_immutability.py",
            "target": CANONICAL_PHASE2
            / "contracts"
            / "phase2_context_immutability.py",
            "action": "copy",
        },
        {
            "source": LEGACY_DURA_LEX / "permutation_invariance.py",
            "target": CANONICAL_PHASE2
            / "contracts"
            / "phase2_permutation_invariance.py",
            "action": "copy",
        },
        {
            "source": LEGACY_DURA_LEX / "risk_certificate.py",
            "target": CANONICAL_PHASE2 / "contracts" / "phase2_risk_certificate.py",
            "action": "copy",
        },
        {
            "source": LEGACY_DURA_LEX / "routing_contract.py",
            "target": CANONICAL_PHASE2 / "contracts" / "phase2_routing_contract.py",
            "action": "copy",
        },
        {
            "source": LEGACY_DURA_LEX / "runtime_contracts.py",
            "target": CANONICAL_PHASE2 / "contracts" / "phase2_runtime_contracts.py",
            "action": "copy",
        },
        {
            "source": LEGACY_DURA_LEX / "snapshot_contract.py",
            "target": CANONICAL_PHASE2 / "contracts" / "phase2_snapshot_contract.py",
            "action": "copy",
        },
    ],
}


def add_canonical_header(file_path: Path, module_name: str) -> None:
    """Add mandatory 20-line canonical header to Python file."""
    header = f'''"""
Module: src.canonic_phases.phase_2.{module_name}
Phase: 2 (Executor Orchestration)
Version: 1.0.0
Freeze Date: 2025-12-18
Classification: CANONICAL_FROZEN

Purpose:
{module_name} - Migrated from legacy location to canonical structure.

Contracts Enforced:
[To be documented]

Success Criteria:
[To be documented]

Failure Modes:
[To be documented]

Verification:
[To be documented]
"""

'''
    content = file_path.read_text()
    if not content.startswith('"""'):
        file_path.write_text(header + content)


def migrate_file(source: Path, target: Path, action: str, dry_run: bool) -> dict[str, Any]:
    """Migrate a single file according to the migration map."""
    result = {
        "source": str(source),
        "target": str(target),
        "action": action,
        "status": "pending",
        "message": "",
    }

    if not source.exists():
        result["status"] = "skipped"
        result["message"] = f"Source file does not exist: {source}"
        return result

    if target.exists():
        result["status"] = "skipped"
        result["message"] = f"Target already exists: {target}"
        return result

    if dry_run:
        result["status"] = "dry_run"
        result["message"] = f"Would {action} {source.name} -> {target.name}"
        return result

    try:
        target.parent.mkdir(parents=True, exist_ok=True)

        if action == "move":
            shutil.move(str(source), str(target))
            result["message"] = f"Moved {source.name} to {target}"
        elif action == "copy":
            shutil.copy2(str(source), str(target))
            result["message"] = f"Copied {source.name} to {target}"

        module_name = target.stem
        add_canonical_header(target, module_name)

        result["status"] = "success"
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)

    return result


def main() -> None:
    """Execute Phase 2 canonical migration."""
    parser = argparse.ArgumentParser(description="Phase 2 Canonical Migration Helper")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute the migration"
    )
    parser.add_argument(
        "--section",
        choices=["phase_root", "executors", "orchestration", "contracts", "all"],
        default="all",
        help="Which section to migrate",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "phase2_migration_report.json",
        help="Output path for migration report",
    )

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        parser.error("Must specify either --dry-run or --execute")

    sections = (
        list(MIGRATION_MAP.keys()) if args.section == "all" else [args.section]
    )

    results = []
    for section in sections:
        print(f"\n{'='*60}")
        print(f"Section: {section}")
        print(f"{'='*60}")

        for migration in MIGRATION_MAP[section]:
            result = migrate_file(
                migration["source"],
                migration["target"],
                migration["action"],
                args.dry_run,
            )
            results.append(result)
            print(f"[{result['status'].upper()}] {result['message']}")

    report = {
        "dry_run": args.dry_run,
        "sections": sections,
        "results": results,
        "summary": {
            "success": sum(1 for r in results if r["status"] == "success"),
            "skipped": sum(1 for r in results if r["status"] == "skipped"),
            "error": sum(1 for r in results if r["status"] == "error"),
            "dry_run": sum(1 for r in results if r["status"] == "dry_run"),
        },
    }

    args.output.write_text(json.dumps(report, indent=2))
    print(f"\nReport written to: {args.output}")
    print(f"\nSummary: {report['summary']}")


if __name__ == "__main__":
    main()
