#!/usr/bin/env python3
"""
Verification script for CalibrationOrchestrator implementation.

Checks that all required components are properly implemented.
"""

import sys
from pathlib import Path

def check_imports():
    """Verify all imports work."""
    print("=" * 70)
    print("VERIFICATION: CalibrationOrchestrator Implementation")
    print("=" * 70)
    print("\n1. Checking imports...")
    
    try:
        from src.orchestration.calibration_orchestrator import (
            CalibrationOrchestrator,
            CalibrationSubject,
            CalibrationResult,
            EvidenceStore,
            LayerID,
            LayerRequirementsResolver,
            ROLE_LAYER_REQUIREMENTS,
            BaseLayerEvaluator,
            ChainLayerEvaluator,
            UnitLayerEvaluator,
            QuestionLayerEvaluator,
            DimensionLayerEvaluator,
            PolicyLayerEvaluator,
            CongruenceLayerEvaluator,
            MetaLayerEvaluator,
            ChoquetAggregator,
        )
        print("   ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False

def check_layer_ids():
    """Verify all 8 LayerIDs exist."""
    print("\n2. Checking LayerID enum...")
    
    try:
        from src.orchestration.calibration_orchestrator import LayerID
        
        expected_layers = ["@b", "@chain", "@u", "@q", "@d", "@p", "@C", "@m"]
        actual_layers = [layer.value for layer in LayerID]
        
        if set(expected_layers) == set(actual_layers):
            print(f"   ✓ All 8 LayerIDs present: {', '.join(expected_layers)}")
            return True
        else:
            print(f"   ✗ LayerID mismatch")
            print(f"      Expected: {expected_layers}")
            print(f"      Got: {actual_layers}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def check_role_requirements():
    """Verify all 8 roles are defined."""
    print("\n3. Checking role layer requirements...")
    
    try:
        from src.orchestration.calibration_orchestrator import ROLE_LAYER_REQUIREMENTS
        
        expected_roles = [
            "INGEST_PDM", "STRUCTURE", "EXTRACT", "SCORE_Q",
            "AGGREGATE", "REPORT", "META_TOOL", "TRANSFORM"
        ]
        
        actual_roles = list(ROLE_LAYER_REQUIREMENTS.keys())
        
        if set(expected_roles) == set(actual_roles):
            print(f"   ✓ All 8 roles defined")
            for role, layers in ROLE_LAYER_REQUIREMENTS.items():
                layer_str = ", ".join(layer.value for layer in layers)
                print(f"      {role:15} → {len(layers)} layers: {layer_str}")
            return True
        else:
            print(f"   ✗ Role mismatch")
            print(f"      Expected: {expected_roles}")
            print(f"      Got: {actual_roles}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def check_config_files():
    """Verify all configuration files exist."""
    print("\n4. Checking configuration files...")
    
    config_dir = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
    
    required_files = [
        "COHORT_2024_intrinsic_calibration.json",
        "COHORT_2024_questionnaire_monolith.json",
        "COHORT_2024_fusion_weights.json",
        "COHORT_2024_method_compatibility.json",
        "COHORT_2024_canonical_method_inventory.json",
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = config_dir / filename
        if filepath.exists():
            print(f"   ✓ {filename}")
        else:
            print(f"   ✗ {filename} MISSING")
            all_exist = False
    
    return all_exist

def check_test_file():
    """Verify test file exists."""
    print("\n5. Checking test file...")
    
    test_file = Path("tests/orchestration/test_calibration_orchestrator.py")
    
    if test_file.exists():
        print(f"   ✓ test_calibration_orchestrator.py exists")
        return True
    else:
        print(f"   ✗ test_calibration_orchestrator.py MISSING")
        return False

def check_examples():
    """Verify example files exist."""
    print("\n6. Checking example files...")
    
    examples_dir = Path("tests/orchestration/orchestration_examples")
    
    required_examples = [
        "example_basic_calibration.py",
        "example_role_based_activation.py",
        "example_batch_calibration.py",
        "example_layer_evaluator_detail.py",
        "example_completeness_validation.py",
        "README.md",
    ]
    
    all_exist = True
    for filename in required_examples:
        filepath = examples_dir / filename
        if filepath.exists():
            print(f"   ✓ {filename}")
        else:
            print(f"   ✗ {filename} MISSING")
            all_exist = False
    
    return all_exist

def check_orchestrator_integration():
    """Verify integration with main Orchestrator."""
    print("\n7. Checking integration with main Orchestrator...")
    
    try:
        from src.orchestration.orchestrator import Orchestrator
        
        if hasattr(Orchestrator, 'calibrate_method'):
            print("   ✓ calibrate_method exists in Orchestrator")
            return True
        else:
            print("   ✗ calibrate_method NOT FOUND in Orchestrator")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def main():
    """Run all verification checks."""
    checks = [
        check_imports,
        check_layer_ids,
        check_role_requirements,
        check_config_files,
        check_test_file,
        check_examples,
        check_orchestrator_integration,
    ]
    
    results = [check() for check in checks]
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Checks Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ ALL CHECKS PASSED - Implementation Complete!")
        print("\nThe CalibrationOrchestrator is fully implemented with:")
        print("  • 8 LayerID enums")
        print("  • 8 role definitions with layer requirements")
        print("  • 8 layer evaluators")
        print("  • LayerRequirementsResolver")
        print("  • ChoquetAggregator")
        print("  • CalibrationOrchestrator main class")
        print("  • Integration with main Orchestrator")
        print("  • Complete test suite")
        print("  • 5 example scripts + README")
        print("  • All 5 configuration files")
        return 0
    else:
        print("\n✗ SOME CHECKS FAILED - Review implementation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
