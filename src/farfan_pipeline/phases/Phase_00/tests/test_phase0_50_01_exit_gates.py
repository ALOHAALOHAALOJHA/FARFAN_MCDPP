import pytest
from unittest.mock import MagicMock
from farfan_pipeline.phases.Phase_00.phase0_50_01_exit_gates import (
    check_all_gates,
    GateResult
)

def test_check_all_gates():
    runner = MagicMock()
    # Gate 1: Bootstrap
    runner.errors = []
    runner._bootstrap_failed = False
    runner.runtime_config = MagicMock()
    runner.runtime_config.expected_method_count = 100 
    
    # Gate 2: Input Verification
    runner.input_pdf_sha256 = "a" * 64
    runner.questionnaire_sha256 = "b" * 64
    
    # Gate 3: Boot Checks (uses runner.errors which is empty)
    
    # Gate 4: Determinism
    runner.seed_snapshot = {"python": 1, "numpy": 2}
    
    # Gate 5: Questionnaire Integrity
    runner.runtime_config.expected_questionnaire_sha256 = "" # Legacy mode
    
    # Gate 6: Method Registry
    # IMPORTANT: Ensure get_stats returns a real dict, not a Mock
    stats_dict = {"total_classes_registered": 1000, "failed_classes": 0}
    runner.method_executor.method_registry.get_stats.return_value = stats_dict
    # Also handle the property access chain
    runner.method_executor._method_registry.get_stats.return_value = stats_dict
    
    # Gate 7: Smoke Tests
    runner.method_executor.instances.get.return_value = MagicMock()
    
    # Mock passed gates
    passed, results = check_all_gates(runner)
    
    if not passed:
        for r in results:
            if not r.passed:
                print(f"FAILED GATE: {r.gate_name} - {r.reason}")
                
    assert passed is True
    assert all(r.passed for r in results)

def test_gate_failure():
    runner = MagicMock()
    runner._bootstrap_failed = True
    
    passed, results = check_all_gates(runner)
    assert passed is False
    assert results[0].passed is False # Gate 1 checks errors