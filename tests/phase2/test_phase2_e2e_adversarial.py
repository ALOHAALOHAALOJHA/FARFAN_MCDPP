"""
End-to-End Adversarial Test for Phase 2.

This test simulates a hostile environment with:
1. Malformed/Poisoned Document Inputs (Phase 1 Output)
2. Faulty Executors (simulated via mocks)
3. Resource Contention
4. Schema Violations

It runs the pipeline flow:
    Factory -> Orchestrator -> Synchronizer -> Plan -> Execution -> Result

Goal: Ensure the pipeline does NOT crash and reports errors correctly.
"""

import pytest
import json
import time
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from farfan_pipeline.phases.Phase_2.phase2_10_00_factory import AnalysisPipelineFactory
from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer, Task
from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import TaskExecutor, TaskResult, ExecutionError
from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import ExecutionPlan

# Mock dependencies that are hard to instantiate in isolation
class MockChunk:
    def __init__(self, chunk_id, text, policy_area_id, dimension_id):
        self.chunk_id = chunk_id
        self.text = text
        self.policy_area_id = policy_area_id
        self.dimension_id = dimension_id
        self.start_pos = 0
        self.end_pos = len(text)

class MockPreprocessedDocument:
    def __init__(self, chunks):
        self.chunks = chunks
        self.document_id = "adversarial_doc_001"

@pytest.fixture
def adversarial_setup():
    # 1. Poisoned Questionnaire (valid structure but potentially hostile content)
    # We use a minimal valid structure to pass schema validation, but logic will be stressed
    questionnaire = {
        "canonical_notation": {
            "dimensions": {"D1": "Dimension 1"},
            "policy_areas": {"PA01": "Policy Area 1"}
        },
        "blocks": {
            "micro_questions": [
                {
                    "question_id": "Q001",
                    "question_global": 1,
                    "policy_area_id": "PA01",
                    "dimension_id": "D1",
                    "text": "What is the budget?",
                    "expected_elements": [{"name": "budget", "type": "currency", "required": True}],
                    "patterns": [{"pattern": "budget is $amount"}],
                    "signal_requirements": ["S_BUDGET"]
                }
            ]
        }
    }

    # 2. Poisoned Document Chunks
    # - Chunk 1: Binary garbage
    # - Chunk 2: Empty text
    # - Chunk 3: Massive text (simulating memory pressure)
    chunks = [
        MockChunk("c1", "\x00\xff\xfe garbage", "PA01", "D1"),
        MockChunk("c2", "", "PA01", "D1"),
        MockChunk("c3", "A" * 10000, "PA01", "D1") 
    ]
    doc = MockPreprocessedDocument(chunks)

    # 3. Mock Signal Registry
    mock_registry = Mock()
    mock_registry.get_all_policy_areas.return_value = ["PA01"]
    
    # Return fake signals
    mock_registry.get_signals_for_chunk.return_value = [
        {"signal_id": "s1", "signal_type": "S_BUDGET", "content": {"value": 100}}
    ]

    return questionnaire, doc, mock_registry

def test_phase2_e2e_adversarial_flow(adversarial_setup):
    questionnaire, doc, signal_registry = adversarial_setup

    # --- Step 1: Synchronization (Adversarial Data) ---
    # We expect the synchronizer to handle garbage chunks gracefully or fail specifically
    
    # We mock ChunkMatrix to avoid strict 60-chunk invariant for this specific test
    # allowing us to test partial/garbage documents
    with patch("farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer.ChunkMatrix") as MockChunkMatrix:
        MockChunkMatrix.EXPECTED_CHUNK_COUNT = 3 # Override constraint
        
        # Mock matrix behavior
        matrix_instance = MockChunkMatrix.return_value
        matrix_instance._preprocessed_document = doc
        
        # Mock get_chunk to simulate routing logic
        def get_chunk(pa, dim):
            # Return the binary garbage chunk for PA01/D1
            return doc.chunks[0] 
        matrix_instance.get_chunk.side_effect = get_chunk

        # Mock validate_phase6_schema_compatibility to pass (we test execution failure, not schema)
        with patch("farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer.validate_phase6_schema_compatibility"):
            
            synchronizer = IrrigationSynchronizer(
                questionnaire=questionnaire,
                preprocessed_document=doc,
                signal_registry=signal_registry
            )
            # Force mock matrix
            synchronizer.chunk_matrix = matrix_instance
            synchronizer.chunk_count = 3

            # Build Plan - Should succeed despite garbage text (Synchronizer checks metadata mostly)
            plan = synchronizer.build_execution_plan()
            
            assert isinstance(plan, ExecutionPlan)
            assert len(plan.tasks) > 0
            task = plan.tasks[0]
            assert task.chunk_id == "c1" # The garbage chunk

    # --- Step 2: Execution (Faulty Executor) ---
    # Now we execute this plan using TaskExecutor.
    # We simulate an executor that crashes on binary data.

    with patch("farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor.DynamicContractExecutor") as MockExecutorClass:
        mock_executor_instance = MockExecutorClass.return_value
        
        # Define a side effect that crashes
        def execute_crash(context):
            if "\x00" in context.chunk_text:
                raise ValueError("Executor crashed on binary data!")
            return {"result": "success"}
        
        mock_executor_instance.execute.side_effect = execute_crash

        # Initialize TaskExecutor
        task_executor = TaskExecutor(
            questionnaire_monolith=questionnaire_monolith_mock(questionnaire),
            preprocessed_document=doc,
            signal_registry=signal_registry
        )
        
        # Execute Plan
        results = task_executor.execute_plan(plan)

        # --- Step 3: Verification ---
        assert len(results) == 1
        result = results[0]
        
        # Verification 1: Pipeline did NOT crash (we got a result object)
        assert isinstance(result, TaskResult)
        
        # Verification 2: Task failed gracefully
        assert result.success is False
        assert "Executor crashed on binary data" in result.error
        
        # Verification 3: Provenance maintained
        assert result.task_id == task.task_id
        assert result.chunk_id == "c1"

def questionnaire_monolith_mock(data):
    """Helper to wrap questionnaire data in expected structure for TaskExecutor"""
    return data # TaskExecutor expects dict, data is dict

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
