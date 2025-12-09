"""
Example: Completeness Validation

Demonstrates completeness validation ensuring all required layers are computed.
"""

from pathlib import Path
from src.orchestration.calibration_orchestrator import (
    CalibrationOrchestrator,
    CalibrationSubject,
    EvidenceStore,
    LayerID,
    ROLE_LAYER_REQUIREMENTS,
)


def example_completeness_validation():
    """Demonstrate completeness validation."""
    print("=" * 70)
    print("EXAMPLE: Completeness Validation")
    print("=" * 70)
    
    config_dir = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
    orchestrator = CalibrationOrchestrator.from_config_dir(config_dir)
    print("✓ CalibrationOrchestrator initialized")
    
    evidence = EvidenceStore(
        pdt_structure={
            "chunk_count": 60,
            "completeness": 0.85,
            "structure_quality": 0.9
        },
        document_quality=0.85,
        question_id="Q001",
        dimension_id="D1",
        policy_area_id="PA1"
    )
    
    print("\n" + "=" * 70)
    print("Testing Completeness Validation for Each Role")
    print("=" * 70)
    
    for role, required_layers in ROLE_LAYER_REQUIREMENTS.items():
        print(f"\n{role}:")
        print(f"  Required Layers: {len(required_layers)}")
        print(f"  Layers: {', '.join(layer.value for layer in required_layers)}")
        
        subject = CalibrationSubject(
            method_id=f"test.{role.lower()}.method",
            role=role,
            context={"test": "completeness"}
        )
        
        try:
            result = orchestrator.calibrate(subject, evidence)
            
            computed_count = len(result.layer_scores)
            required_count = len(required_layers)
            
            if computed_count == required_count:
                print(f"  ✓ PASS: All {required_count} layers computed")
                print(f"  Final Score: {result.final_score:.4f}")
            else:
                print(f"  ✗ FAIL: {computed_count}/{required_count} layers computed")
        
        except ValueError as e:
            print(f"  ✗ ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("Testing Missing Layer Detection")
    print("=" * 70)
    
    print("\nSimulating missing layer scenario:")
    required = {LayerID.BASE, LayerID.CHAIN, LayerID.UNIT, LayerID.META}
    computed = {
        LayerID.BASE: 0.8,
        LayerID.CHAIN: 0.7,
    }
    
    print(f"  Required: {', '.join(layer.value for layer in required)}")
    print(f"  Computed: {', '.join(layer.value for layer in computed.keys())}")
    
    try:
        orchestrator._validate_completeness(
            required, computed, "test.method", "TEST_ROLE"
        )
        print("  ✗ FAIL: Validation should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ PASS: Correctly detected missing layers")
        print(f"  Error: {e}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    example_completeness_validation()
