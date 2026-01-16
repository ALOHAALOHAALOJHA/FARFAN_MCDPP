#!/usr/bin/env python3
"""
Example: Using the F.A.R.F.A.N Core Orchestrator

This example demonstrates how to use the PipelineOrchestrator to execute
the complete F.A.R.F.A.N pipeline with proper configuration and error handling.

Author: F.A.R.F.A.N Core Team
"""

from pathlib import Path

from farfan_pipeline.orchestration import (
    PipelineOrchestrator,
    OrchestratorConfig,
    PhaseID,
    PhaseStatus,
    get_development_config,
)


def example_1_basic_execution():
    """Example 1: Basic pipeline execution with default configuration."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Pipeline Execution")
    print("=" * 70)

    # Create configuration
    config = get_development_config()

    # Create orchestrator
    orchestrator = PipelineOrchestrator(
        config=config.to_dict(),
        strict_mode=False,  # Non-strict for development
        deterministic=True,
    )

    # Execute full pipeline
    context = orchestrator.execute_pipeline(
        start_phase=PhaseID.PHASE_0,
        end_phase=PhaseID.PHASE_9,
    )

    # Print summary
    summary = context.get_execution_summary()
    print(f"\n✓ Execution ID: {summary['execution_id']}")
    print(f"✓ Total Time: {summary['elapsed_time_s']:.2f}s")
    print(f"✓ Phases Completed: {summary['phases_completed']}/{summary['total_phases']}")
    print(f"✓ Total Violations: {summary['total_violations']}")
    print()


def example_2_partial_execution():
    """Example 2: Execute only specific phases."""
    print("=" * 70)
    print("EXAMPLE 2: Partial Pipeline Execution (Phases 4-7)")
    print("=" * 70)

    config = get_development_config()
    orchestrator = PipelineOrchestrator(
        config=config.to_dict(),
        strict_mode=False,
        deterministic=True,
    )

    # Execute only aggregation phases (4-7)
    context = orchestrator.execute_pipeline(
        start_phase=PhaseID.PHASE_4,
        end_phase=PhaseID.PHASE_7,
    )

    # Print phase-by-phase results
    print("\nPhase Results:")
    for phase_id, result in context.phase_results.items():
        status_symbol = "✓" if result.status == PhaseStatus.COMPLETED else "✗"
        print(f"{status_symbol} {phase_id.value}: {result.execution_time_s:.3f}s")
    print()


def example_3_custom_configuration():
    """Example 3: Custom configuration with specific paths and settings."""
    print("=" * 70)
    print("EXAMPLE 3: Custom Configuration")
    print("=" * 70)

    # Create custom configuration
    config = OrchestratorConfig(
        # Custom paths (these would be real paths in production)
        # questionnaire_path=Path("/path/to/custom_questionnaire.json"),
        # executor_config_path=Path("/path/to/custom_executors.json"),
        output_dir=Path("./output/custom_run"),

        # Execution settings
        strict_mode=False,
        deterministic=True,

        # Resource limits
        resource_limits={
            "memory_mb": 4096,
            "cpu_seconds": 600,
        },

        # Logging
        log_level="DEBUG",

        # Phase range
        start_phase="P00",
        end_phase="P05",
    )

    print(f"Configuration:")
    print(f"  Output Dir: {config.output_dir}")
    print(f"  Strict Mode: {config.strict_mode}")
    print(f"  Deterministic: {config.deterministic}")
    print(f"  Memory Limit: {config.resource_limits['memory_mb']} MB")
    print(f"  Phase Range: {config.start_phase} → {config.end_phase}")
    print()


def example_4_error_handling():
    """Example 4: Error handling and violation reporting."""
    print("=" * 70)
    print("EXAMPLE 4: Error Handling and Violation Reporting")
    print("=" * 70)

    config = get_development_config()
    orchestrator = PipelineOrchestrator(
        config=config.to_dict(),
        strict_mode=False,  # Don't raise exceptions
        deterministic=True,
    )

    try:
        context = orchestrator.execute_pipeline()

        # Check for violations
        if context.total_violations:
            print(f"\n⚠️  Found {len(context.total_violations)} violations:")

            # Group by severity
            from farfan_pipeline.phases.Phase_00.interphase.wiring_types import Severity

            critical = [v for v in context.total_violations if v.severity == Severity.CRITICAL]
            high = [v for v in context.total_violations if v.severity == Severity.HIGH]
            medium = [v for v in context.total_violations if v.severity == Severity.MEDIUM]

            print(f"  🔴 Critical: {len(critical)}")
            print(f"  🟠 High: {len(high)}")
            print(f"  🟡 Medium: {len(medium)}")

            # Show critical violations
            if critical:
                print("\nCritical Violations:")
                for v in critical[:3]:  # Show first 3
                    print(f"  • {v.component_path}")
                    print(f"    {v.message}")
                    if v.remediation:
                        print(f"    Fix: {v.remediation}")
        else:
            print("\n✅ No violations detected!")

    except Exception as e:
        print(f"\n❌ Pipeline execution failed: {e}")

    print()


def example_5_accessing_phase_outputs():
    """Example 5: Accessing outputs from specific phases."""
    print("=" * 70)
    print("EXAMPLE 5: Accessing Phase Outputs")
    print("=" * 70)

    config = get_development_config()
    orchestrator = PipelineOrchestrator(
        config=config.to_dict(),
        strict_mode=False,
        deterministic=True,
    )

    context = orchestrator.execute_pipeline()

    # Access Phase 0 output (WiringComponents)
    wiring = context.get_phase_output(PhaseID.PHASE_0)
    if wiring:
        print(f"✓ Phase 0 (Bootstrap): WiringComponents initialized")
        print(f"  - Components: {len(wiring.init_hashes)}")

    # Access Phase 1 output (CPP)
    cpp = context.get_phase_output(PhaseID.PHASE_1)
    if cpp:
        print(f"✓ Phase 1 (CPP Ingestion): {len(cpp.chunks)} chunks")

    # Access Phase 4 output (Dimension scores)
    dim_scores = context.get_phase_output(PhaseID.PHASE_4)
    if dim_scores:
        print(f"✓ Phase 4 (Dimension Aggregation): {len(dim_scores)} dimensions")

    # Access Phase 5 output (Policy area scores)
    pa_scores = context.get_phase_output(PhaseID.PHASE_5)
    if pa_scores:
        print(f"✓ Phase 5 (Policy Area Aggregation): {len(pa_scores)} policy areas")

    # Access Phase 7 output (Macro score)
    macro = context.get_phase_output(PhaseID.PHASE_7)
    if macro:
        print(f"✓ Phase 7 (Macro Aggregation): score = {macro.macro_score}")

    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "F.A.R.F.A.N ORCHESTRATOR EXAMPLES" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    examples = [
        example_1_basic_execution,
        example_2_partial_execution,
        example_3_custom_configuration,
        example_4_error_handling,
        example_5_accessing_phase_outputs,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example {i} failed: {e}\n")

        if i < len(examples):
            input("Press Enter to continue to next example...")
            print("\n")

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
