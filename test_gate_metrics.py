from src.farfan_pipeline.orchestration.gates.gate_orchestrator import GateOrchestrator, GateMetrics
import dataclasses

def test_metrics_init():
    orchestrator = GateOrchestrator()
    metrics = orchestrator.get_metrics()
    print("Initial Metrics:", metrics)
    assert metrics.total_executions == 0
    assert metrics.gate_1_pass_rate == 0.0
    
    # We can't easily test validate_pre_dispatch without mocking signals and gates, 
    # but successful import and init confirms syntax and structure.

if __name__ == "__main__":
    test_metrics_init()
