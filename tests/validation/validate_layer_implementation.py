"""
Validation Script for Congruence and Chain Layer Implementation

Verifies that all components are properly implemented and accessible.
"""

import sys
from pathlib import Path


def validate_imports():
    """Validate all imports work correctly."""
    print("=" * 60)
    print("VALIDATION: Testing Imports")
    print("=" * 60)
    
    try:
        from orchestration.congruence_layer import (
            CongruenceLayerEvaluator,
            CongruenceLayerConfig,
            OutputRangeSpec,
            SemanticTagSet,
            FusionRule,
            create_default_congruence_config
        )
        print("✅ Congruence Layer imports successful")
    except Exception as e:
        print(f"❌ Congruence Layer import failed: {e}")
        return False

    try:
        from orchestration.chain_layer import (
            ChainLayerEvaluator,
            ChainLayerConfig,
            MethodSignature,
            UpstreamOutputs,
            create_default_chain_config
        )
        print("✅ Chain Layer imports successful")
    except Exception as e:
        print(f"❌ Chain Layer import failed: {e}")
        return False

    try:
        from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_congruence_layer import (
            CongruenceLayerEvaluator as C2024_CongruenceEvaluator
        )
        print("✅ COHORT_2024 Congruence Layer imports successful")
    except Exception as e:
        print(f"❌ COHORT_2024 Congruence import failed: {e}")
        return False

    try:
        from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_chain_layer import (
            ChainLayerEvaluator as C2024_ChainEvaluator
        )
        print("✅ COHORT_2024 Chain Layer imports successful")
    except Exception as e:
        print(f"❌ COHORT_2024 Chain import failed: {e}")
        return False

    return True


def validate_functionality():
    """Validate basic functionality of both evaluators."""
    print("\n" + "=" * 60)
    print("VALIDATION: Testing Basic Functionality")
    print("=" * 60)
    
    try:
        from orchestration.congruence_layer import (
            CongruenceLayerEvaluator,
            OutputRangeSpec,
            SemanticTagSet,
            FusionRule,
            create_default_congruence_config
        )
        
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)
        
        current_range = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        upstream_range = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        current_tags = SemanticTagSet(tags={"test"}, description=None)
        upstream_tags = SemanticTagSet(tags={"test"}, description=None)
        fusion = FusionRule(
            rule_type="aggregation",
            operator="sum",
            is_valid=True,
            description=None
        )
        
        result = evaluator.evaluate(
            current_range, upstream_range,
            current_tags, upstream_tags,
            fusion
        )
        
        assert "C_play" in result
        assert "c_scale" in result
        assert "c_sem" in result
        assert "c_fusion" in result
        assert result["C_play"] == 1.0
        
        print("✅ Congruence Layer functionality validated")
    except Exception as e:
        print(f"❌ Congruence Layer functionality failed: {e}")
        return False

    try:
        from orchestration.chain_layer import (
            ChainLayerEvaluator,
            MethodSignature,
            UpstreamOutputs,
            create_default_chain_config
        )
        
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)
        
        signature = MethodSignature(
            required_inputs=["input"],
            optional_inputs=["metadata"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        
        upstream = UpstreamOutputs(
            available_outputs={"input", "metadata"},
            output_types={}
        )
        
        result = evaluator.evaluate(signature, upstream)
        
        assert "chain_score" in result
        assert "validation_status" in result
        assert "missing_required" in result
        assert result["chain_score"] == 1.0
        
        print("✅ Chain Layer functionality validated")
    except Exception as e:
        print(f"❌ Chain Layer functionality failed: {e}")
        return False

    return True


def validate_files():
    """Validate all required files exist."""
    print("\n" + "=" * 60)
    print("VALIDATION: Checking File Existence")
    print("=" * 60)
    
    required_files = [
        "src/orchestration/congruence_layer.py",
        "src/orchestration/chain_layer.py",
        "src/orchestration/congruence_layer_example.py",
        "src/orchestration/chain_layer_example.py",
        "src/orchestration/CONGRUENCE_CHAIN_LAYER_README.md",
        "src/orchestration/__init__.py",
        "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_congruence_layer.py",
        "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_chain_layer.py",
        "tests/test_congruence_layer.py",
        "tests/test_chain_layer.py",
        "tests/test_congruence_chain_integration.py",
        "documentation/CONGRUENCE_CHAIN_IMPLEMENTATION.md",
        "IMPLEMENTATION_SUMMARY.md"
    ]
    
    all_exist = True
    for filepath in required_files:
        path = Path(filepath)
        if path.exists():
            print(f"✅ {filepath}")
        else:
            print(f"❌ {filepath} NOT FOUND")
            all_exist = False
    
    return all_exist


def main():
    """Run all validations."""
    print("\n" + "=" * 60)
    print("CONGRUENCE AND CHAIN LAYER IMPLEMENTATION VALIDATION")
    print("=" * 60)
    
    results = []
    
    results.append(("File Existence", validate_files()))
    results.append(("Import Validation", validate_imports()))
    results.append(("Functionality Validation", validate_functionality()))
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 ALL VALIDATIONS PASSED - Implementation is complete!")
        return 0
    else:
        print("\n⚠️  SOME VALIDATIONS FAILED - Please review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
