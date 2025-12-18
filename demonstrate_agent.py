#!/usr/bin/env python3.12
"""
Demonstration of F.A.R.F.A.N Agent Prime Directives

Shows epistemic constraints and discovery protocol in action.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from farfan_pipeline.agents import (
    EpistemicConstraints,
    StatementType,
    DiscoveryProtocol,
)


def demonstrate_epistemic_constraints() -> None:
    """Demonstrate epistemic constraint enforcement."""
    print("=" * 80)
    print("DEMONSTRATION: EPISTEMIC CONSTRAINTS")
    print("=" * 80)
    print()

    print("1. Creating falsifiable statement...")
    stmt = EpistemicConstraints.create_falsifiable_statement(
        claim="[OBSERVATION] Repository contains 240 analytical methods",
        statement_type=StatementType.OBSERVATION,
        evidence=[
            "METHODS_TO_QUESTIONS_AND_FILES.json contains 240 entries",
            "METHODS_OPERACIONALIZACION.json contains 240 entries",
            "Cross-reference between files shows exact match",
        ],
        disproof_conditions=[
            "Count of methods in either file differs from 240",
            "Methods list between files shows mismatch",
        ],
    )
    print(f"   Claim: {stmt.claim}")
    print(f"   Type: {stmt.statement_type.value}")
    print(f"   Evidence items: {len(stmt.evidence)}")
    print(f"   Disproof conditions: {len(stmt.disproof_conditions)}")
    print()

    print("2. Testing hedging detection...")
    try:
        EpistemicConstraints.validate_no_hedging("This probably works")
        print("   ✗ FAILED: Should have detected hedging")
    except Exception as e:
        print(f"   ✓ SUCCESS: Detected hedging - {type(e).__name__}")
    print()

    print("3. Testing statement labeling...")
    text = "[DECISION] Implement discovery protocol using Path-based scanning"
    stmt_type = EpistemicConstraints.validate_statement_labeled(text)
    print(f"   Detected type: {stmt_type.value}")
    print()

    print("4. Testing insufficient evidence halt...")
    try:
        EpistemicConstraints.halt_insufficient_evidence(
            context="calibration",
            required_inputs=["validation_set", "num_runs"],
        )
        print("   ✗ FAILED: Should have halted")
    except Exception as e:
        print(f"   ✓ SUCCESS: Halted execution - {type(e).__name__}")
    print()


def demonstrate_discovery_protocol() -> None:
    """Demonstrate discovery protocol execution."""
    print("=" * 80)
    print("DEMONSTRATION: DISCOVERY PROTOCOL")
    print("=" * 80)
    print()

    repo_root = Path(__file__).parent.resolve()
    protocol = DiscoveryProtocol(repo_root)

    print("[OBSERVATION] Executing Step 1.1.1: Repository Scan Commands")
    print()
    print("Scanning repository structure...")

    inventory = protocol.execute_repository_scan()

    print()
    print("INVENTORY RESULTS:")
    print(f"  Total Files: {inventory.total_files}")
    print(f"  Total Lines of Code: {inventory.total_lines_of_code:,}")
    print(f"  Python Files: {len(inventory.python_files)}")
    print(f"  Test Files: {len(inventory.test_files)}")
    print(f"  Config Files: {len(inventory.config_files)}")
    print(f"  Documentation: {len(inventory.documentation_files)}")
    print(f"  Dependencies: {len(inventory.dependencies)}")
    print()

    print("KEY DEPENDENCIES (first 10):")
    for dep_name, dep_version in sorted(inventory.dependencies.items())[:10]:
        print(f"  - {dep_name}: {dep_version}")
    print()

    print("ARCHITECTURE SUMMARY:")
    for key, value in inventory.architecture_summary.items():
        if isinstance(value, list):
            print(f"  - {key}: {len(value)} items")
        else:
            print(f"  - {key}: {value}")
    print()

    print("[DECISION] Generate comprehensive inventory report...")
    report = protocol.generate_inventory_report(inventory)
    print()
    print(report)


def main() -> None:
    """Run agent demonstrations."""
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "F.A.R.F.A.N AGENT PRIME DIRECTIVES" + " " * 29 + "║")
    print("║" + " " * 20 + "Demonstration Script" + " " * 38 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    demonstrate_epistemic_constraints()
    print()
    demonstrate_discovery_protocol()

    print()
    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
