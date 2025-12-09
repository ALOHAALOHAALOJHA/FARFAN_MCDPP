"""
Example: Batch Calibration

Demonstrates calibrating multiple methods in batch with result aggregation.
"""

from pathlib import Path
from typing import List
from src.orchestration.calibration_orchestrator import (
    CalibrationOrchestrator,
    CalibrationSubject,
    CalibrationResult,
    EvidenceStore,
)


def example_batch_calibration():
    """Batch calibration example."""
    print("=" * 70)
    print("EXAMPLE: Batch Calibration")
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
    
    methods = [
        ("farfan.executor.D1Q1", "SCORE_Q"),
        ("farfan.executor.D1Q2", "SCORE_Q"),
        ("farfan.executor.D2Q1", "SCORE_Q"),
        ("farfan.aggregator.dimension", "AGGREGATE"),
        ("farfan.aggregator.policy_area", "AGGREGATE"),
        ("farfan.processor.ingestion", "INGEST_PDM"),
        ("farfan.processor.structure", "STRUCTURE"),
        ("farfan.reporting.generator", "REPORT"),
    ]
    
    results: List[CalibrationResult] = []
    
    print(f"\nCalibrating {len(methods)} methods...")
    print("-" * 70)
    
    for method_id, role in methods:
        subject = CalibrationSubject(
            method_id=method_id,
            role=role,
            context={"batch_id": "batch_001"}
        )
        
        result = orchestrator.calibrate(subject, evidence)
        results.append(result)
        
        print(f"  {method_id:30} → {result.final_score:.4f} ({len(result.active_layers)} layers)")
    
    print("\n" + "=" * 70)
    print("Batch Statistics")
    print("=" * 70)
    
    scores = [r.final_score for r in results]
    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)
    
    print(f"  Total Methods: {len(results)}")
    print(f"  Average Score: {avg_score:.4f}")
    print(f"  Min Score: {min_score:.4f}")
    print(f"  Max Score: {max_score:.4f}")
    
    role_groups = {}
    for result in results:
        if result.role not in role_groups:
            role_groups[result.role] = []
        role_groups[result.role].append(result.final_score)
    
    print("\nBy Role:")
    for role, role_scores in role_groups.items():
        avg = sum(role_scores) / len(role_scores)
        print(f"  {role:15} → avg: {avg:.4f} (n={len(role_scores)})")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    example_batch_calibration()
