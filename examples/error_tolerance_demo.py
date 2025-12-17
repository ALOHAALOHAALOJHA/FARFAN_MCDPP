"""Demonstration of error tolerance and partial result handling.

This script shows how the error tolerance feature works in different scenarios.
Run this to validate the error tolerance implementation.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from canonic_phases.Phase_zero.runtime_config import RuntimeMode
from orchestration.orchestrator import ErrorTolerance


def demo_threshold_computation() -> None:
    """Demonstrate threshold computation."""
    print("=" * 60)
    print("DEMO 1: Threshold Computation")
    print("=" * 60)
    
    tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
    
    # Simulate 92 successes, 8 failures (8% failure rate)
    for _ in range(92):
        tracker.record_success()
    for _ in range(8):
        tracker.record_failure()
    
    print(f"\nTotal questions: {tracker.total_questions}")
    print(f"Successful: {tracker.successful_questions}")
    print(f"Failed: {tracker.failed_questions}")
    print(f"Failure rate: {tracker.current_failure_rate():.2%}")
    print(f"Threshold (10%): {tracker.max_failure_rate:.2%}")
    print(f"Threshold exceeded: {tracker.threshold_exceeded()}")
    print(f"Can mark success: {tracker.can_mark_success(RuntimeMode.PRODUCTION)}")
    
    print("\n✓ Within threshold - pipeline succeeds\n")


def demo_threshold_exceeded() -> None:
    """Demonstrate threshold exceeded scenario."""
    print("=" * 60)
    print("DEMO 2: Threshold Exceeded (PRODUCTION Mode)")
    print("=" * 60)
    
    tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
    
    # Simulate 80 successes, 20 failures (20% failure rate)
    for _ in range(80):
        tracker.record_success()
    for _ in range(20):
        tracker.record_failure()
    
    print(f"\nTotal questions: {tracker.total_questions}")
    print(f"Successful: {tracker.successful_questions}")
    print(f"Failed: {tracker.failed_questions}")
    print(f"Failure rate: {tracker.current_failure_rate():.2%}")
    print(f"Threshold (10%): {tracker.max_failure_rate:.2%}")
    print(f"Threshold exceeded: {tracker.threshold_exceeded()}")
    print(f"Can mark success (PRODUCTION): {tracker.can_mark_success(RuntimeMode.PRODUCTION)}")
    
    print("\n✗ Threshold exceeded - pipeline aborts in PRODUCTION mode\n")


def demo_partial_success_dev_mode() -> None:
    """Demonstrate partial success in DEV mode."""
    print("=" * 60)
    print("DEMO 3: Partial Success (DEV Mode)")
    print("=" * 60)
    
    tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
    
    # Simulate 60 successes, 40 failures (40% failure rate)
    for _ in range(60):
        tracker.record_success()
    for _ in range(40):
        tracker.record_failure()
    
    print(f"\nTotal questions: {tracker.total_questions}")
    print(f"Successful: {tracker.successful_questions}")
    print(f"Failed: {tracker.failed_questions}")
    print(f"Failure rate: {tracker.current_failure_rate():.2%}")
    print(f"Threshold (10%): {tracker.max_failure_rate:.2%}")
    print(f"Threshold exceeded: {tracker.threshold_exceeded()}")
    print(f"Can mark success (PRODUCTION): {tracker.can_mark_success(RuntimeMode.PRODUCTION)}")
    print(f"Can mark success (DEV): {tracker.can_mark_success(RuntimeMode.DEV)}")
    
    print("\n⚠ Partial success - DEV mode allows continuation for debugging\n")


def demo_edge_case_below_50_percent() -> None:
    """Demonstrate edge case below 50% success rate."""
    print("=" * 60)
    print("DEMO 4: Below 50% Success (DEV Mode)")
    print("=" * 60)
    
    tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
    
    # Simulate 40 successes, 60 failures (60% failure rate)
    for _ in range(40):
        tracker.record_success()
    for _ in range(60):
        tracker.record_failure()
    
    print(f"\nTotal questions: {tracker.total_questions}")
    print(f"Successful: {tracker.successful_questions}")
    print(f"Failed: {tracker.failed_questions}")
    print(f"Failure rate: {tracker.current_failure_rate():.2%}")
    print(f"Can mark success (PRODUCTION): {tracker.can_mark_success(RuntimeMode.PRODUCTION)}")
    print(f"Can mark success (DEV): {tracker.can_mark_success(RuntimeMode.DEV)}")
    
    print("\n✗ Even DEV mode rejects below 50% success rate\n")


def demo_export_state() -> None:
    """Demonstrate state export."""
    print("=" * 60)
    print("DEMO 5: Error Tolerance State Export")
    print("=" * 60)
    
    tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
    
    for _ in range(92):
        tracker.record_success()
    for _ in range(8):
        tracker.record_failure()
    
    state = tracker.to_dict()
    
    print("\nExported state:")
    for key, value in state.items():
        if isinstance(value, float):
            if key == "current_failure_rate":
                print(f"  {key}: {value:.2%}")
            else:
                print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n✓ State can be exported for reporting and monitoring\n")


def demo_runtime_modes_comparison() -> None:
    """Compare behavior across runtime modes."""
    print("=" * 60)
    print("DEMO 6: Runtime Mode Comparison")
    print("=" * 60)
    
    scenarios = [
        (95, 5, "5% failure"),
        (90, 10, "10% failure (threshold)"),
        (85, 15, "15% failure"),
        (60, 40, "40% failure"),
    ]
    
    modes = [
        (RuntimeMode.PRODUCTION, "PRODUCTION"),
        (RuntimeMode.CI, "CI"),
        (RuntimeMode.DEV, "DEV"),
        (RuntimeMode.EXPLORATORY, "EXPLORATORY"),
    ]
    
    print("\n" + "-" * 60)
    print(f"{'Scenario':<25} | {'PROD':<6} | {'CI':<6} | {'DEV':<6} | {'EXPL':<6}")
    print("-" * 60)
    
    for success, fail, label in scenarios:
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(success):
            tracker.record_success()
        for _ in range(fail):
            tracker.record_failure()
        
        results = []
        for mode, _ in modes:
            can_succeed = tracker.can_mark_success(mode)
            results.append("✓" if can_succeed else "✗")
        
        print(f"{label:<25} | {results[0]:<6} | {results[1]:<6} | {results[2]:<6} | {results[3]:<6}")
    
    print("-" * 60)
    print("\n✓ Runtime modes provide flexible error handling policies\n")


def main() -> None:
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("ERROR TOLERANCE DEMONSTRATION")
    print("=" * 60)
    print("\nThis script demonstrates the error tolerance feature")
    print("implemented in the F.A.R.F.A.N pipeline.\n")
    
    try:
        demo_threshold_computation()
        demo_threshold_exceeded()
        demo_partial_success_dev_mode()
        demo_edge_case_below_50_percent()
        demo_export_state()
        demo_runtime_modes_comparison()
        
        print("=" * 60)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nKey Takeaways:")
        print("  1. 10% failure threshold per phase")
        print("  2. PRODUCTION mode enforces strict compliance")
        print("  3. DEV mode allows partial success (50%+ success rate)")
        print("  4. Precise accounting of failures vs successes")
        print("  5. Transparent error reporting in manifests")
        print()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
