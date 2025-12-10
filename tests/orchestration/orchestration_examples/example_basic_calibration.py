"""
Example: Basic Calibration Orchestration

Demonstrates basic usage of CalibrationOrchestrator for single method calibration.
"""

from pathlib import Path
from orchestration.calibration_orchestrator import (
    CalibrationOrchestrator,
    CalibrationSubject,
    EvidenceStore,
)


def example_basic_calibration():
    """Basic calibration example."""
    print("=" * 70)
    print("EXAMPLE: Basic Calibration")
    print("=" * 70)
    
    config_dir = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
    
    orchestrator = CalibrationOrchestrator.from_config_dir(config_dir)
    print("✓ CalibrationOrchestrator loaded from config directory")
    
    subject = CalibrationSubject(
        method_id="test.method.score",
        role="SCORE_Q",
        context={
            "phase": "scoring",
            "question_id": "Q001"
        }
    )
    
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
    
    result = orchestrator.calibrate(subject, evidence)
    
    print(f"\n✓ Calibration completed")
    print(f"  Method: {result.method_id}")
    print(f"  Role: {result.role}")
    print(f"  Final Score: {result.final_score:.4f}")
    print(f"  Active Layers: {len(result.active_layers)}")
    
    print("\n  Layer Scores:")
    for layer_id, score in result.layer_scores.items():
        print(f"    {layer_id.value}: {score:.4f}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    example_basic_calibration()
