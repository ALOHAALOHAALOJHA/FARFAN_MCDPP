"""
Example: Role-Based Layer Activation

Demonstrates how different roles activate different layers in calibration.
"""

from pathlib import Path
from src.orchestration.calibration_orchestrator import (
    CalibrationOrchestrator,
    CalibrationSubject,
    EvidenceStore,
    ROLE_LAYER_REQUIREMENTS,
)


def example_role_based_activation():
    """Demonstrate role-based layer activation."""
    print("=" * 70)
    print("EXAMPLE: Role-Based Layer Activation")
    print("=" * 70)
    
    config_dir = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
    orchestrator = CalibrationOrchestrator.from_config_dir(config_dir)
    
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
    
    test_cases = [
        ("test.ingest.method", "INGEST_PDM", "ingestion"),
        ("test.processor.method", "STRUCTURE", "structuring"),
        ("test.score.method", "SCORE_Q", "scoring"),
        ("test.aggregate.method", "AGGREGATE", "aggregation"),
        ("test.report.method", "REPORT", "reporting"),
        ("test.meta.method", "META_TOOL", "meta"),
    ]
    
    print("\nRole Layer Requirements:")
    print("-" * 70)
    for role, layers in ROLE_LAYER_REQUIREMENTS.items():
        layer_names = [layer.value for layer in layers]
        print(f"  {role:15} → {len(layers)} layers: {', '.join(layer_names)}")
    
    print("\n" + "=" * 70)
    print("Calibrating Methods with Different Roles:")
    print("=" * 70)
    
    for method_id, role, phase in test_cases:
        subject = CalibrationSubject(
            method_id=method_id,
            role=role,
            context={"phase": phase}
        )
        
        result = orchestrator.calibrate(subject, evidence)
        
        print(f"\n{role} ({phase}):")
        print(f"  Method: {method_id}")
        print(f"  Active Layers: {len(result.active_layers)}")
        print(f"  Layers: {', '.join(layer.value for layer in result.active_layers)}")
        print(f"  Final Score: {result.final_score:.4f}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    example_role_based_activation()
