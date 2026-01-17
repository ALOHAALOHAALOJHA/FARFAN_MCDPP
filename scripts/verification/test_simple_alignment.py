#!/usr/bin/env python3
"""Simple test to verify orchestrator accepts factory's dependencies."""

import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / "src"))

def main():
    """Test basic alignment."""
    print("=" * 70)
    print("SIMPLE FACTORY-ORCHESTRATOR ALIGNMENT TEST")
    print("=" * 70)

    # Test 1: Import orchestrator classes directly
    print("\n1. Testing direct orchestrator imports...")
    try:
        from farfan_pipeline.orchestration.orchestrator import (
            Orchestrator,
            MethodExecutor,
            Phase0ValidationResult,
            GateResult,
        )
        print("   ✓ Successfully imported Orchestrator, MethodExecutor,Phase0ValidationResult, GateResult")
    except Exception as e:
        print(f"   ✗ Failed to import orchestrator classes: {e}")
        return 1

    # Test 2: Check Orchestrator signature
    print("\n2. Testing Orchestrator.__init__ signature...")
    import inspect
    sig = inspect.signature(Orchestrator.__init__)
    params = list(sig.parameters.keys())
    expected = ['self', 'method_executor', 'questionnaire', 'executor_config', 'runtime_config', 'phase0_validation']

    if params == expected:
        print(f"   ✓ Orchestrator.__init__ has correct signature")
        print(f"     Parameters: {', '.join(params[1:])}")  # Skip 'self'
    else:
        print(f"   ✗ Signature mismatch!")
        print(f"     Expected: {expected}")
        print(f"     Got:      {params}")
        return 1

    # Test 3: Check MethodExecutor signature
    print("\n3. Testing MethodExecutor.__init__ signature...")
    sig = inspect.signature(MethodExecutor.__init__)
    params = list(sig.parameters.keys())
    expected = ['self', 'method_registry', 'arg_router', 'signal_registry']

    if params == expected:
        print(f"   ✓ MethodExecutor.__init__ has correct signature")
        print(f"     Parameters: {', '.join(params[1:])}")  # Skip 'self'
    else:
        print(f"   ✗ Signature mismatch!")
        print(f"     Expected: {expected}")
        print(f"     Got:      {params}")
        return 1

    # Test 4: Check Phase0ValidationResult dataclass
    print("\n4. Testing Phase0ValidationResult structure...")
    from dataclasses import fields

    field_names = [f.name for f in fields(Phase0ValidationResult)]
    expected = ['all_passed', 'gate_results', 'validation_time']

    if field_names == expected:
        print(f"   ✓ Phase0ValidationResult has correct fields")
        print(f"     Fields: {', '.join(field_names)}")
    else:
        print(f"   ✗ Fields mismatch!")
        print(f"     Expected: {expected}")
        print(f"     Got:      {field_names}")
        return 1

    # Test 5: Test that we can create mock instances
    print("\n5. Testing mock instance creation...")
    try:
        # Create mock dependencies
        class MockMethodRegistry:
            def get_method(self, class_name, method_name):
                return lambda: None

        class MockArgRouter:
            def route(self, class_name, method_name, **kwargs):
                return kwargs

        class MockQuestionnaire:
            def __init__(self):
                self.version = "1.0.0"
                self.data = {}

        class MockConfig:
            pass

        # Create MethodExecutor
        method_executor = MethodExecutor(
            method_registry=MockMethodRegistry(),
            arg_router=MockArgRouter(),
            signal_registry=None
        )
        print("   ✓ Created MethodExecutor instance")

        # Create Phase0ValidationResult
        gate_result = GateResult(
            gate_name="test_gate",
            passed=True,
            message="Test passed",
            details={}
        )
        phase0_validation = Phase0ValidationResult(
            all_passed=True,
            gate_results=[gate_result],
            validation_time="2025-01-01T00:00:00Z"
        )
        print("   ✓ Created Phase0ValidationResult instance")

        # Create Orchestrator
        orchestrator = Orchestrator(
            method_executor=method_executor,
            questionnaire=MockQuestionnaire(),
            executor_config=MockConfig(),
            runtime_config=None,
            phase0_validation=phase0_validation
        )
        print("   ✓ Created Orchestrator instance with all dependencies")

    except Exception as e:
        print(f"   ✗ Failed to create instances: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED - Factory and Orchestrator are aligned!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
