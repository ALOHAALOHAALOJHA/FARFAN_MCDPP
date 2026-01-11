"""
Adversarial tests for Phase 2 (Executor & Synchronizer).

These tests simulate:
1. Resource exhaustion (Memory/CPU)
2. Executor hangs/deadlocks
3. Malformed input data
4. Concurrency race conditions
5. Interrupt recovery

"""
import asyncio
import time
import pytest
from unittest.mock import Mock, MagicMock, patch
import threading
from concurrent.futures import ThreadPoolExecutor

from farfan_pipeline.phases.Phase_2.phase2_30_03_resource_aware_executor import (
    ResourceAwareExecutor,
    InterruptController,
    InterruptibleExecutor,
    ResourceEmergencyInterrupt,
    PartialExecutionResult,
)
from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import (
    IrrigationSynchronizer,
    Task,
    ExecutionPlan,
)
from farfan_pipeline.phases.Phase_2.phase2_50_01_task_planner import ExecutableTask


class TestPhase2Adversarial:
    
    @pytest.fixture
    def interrupt_controller(self):
        return InterruptController()

    @pytest.fixture
    def interruptible_executor(self, interrupt_controller):
        return InterruptibleExecutor(interrupt_controller, check_interval_ms=10)

    def test_executor_interruption_recovery(self, interrupt_controller, interruptible_executor):
        """
        Adversarial Test: Simulate a task that gets interrupted mid-execution.
        Verifies partial results are saved and can be resumed.
        """
        
        # Define a multi-step task
        execution_log = []
        
        def step_1():
            execution_log.append("step_1")
            time.sleep(0.05)
            return "result_1"
            
        def step_2():
            execution_log.append("step_2")
            # Simulate external interrupt here
            interrupt_controller.signal_interrupt("Simulated Emergency")
            time.sleep(0.05)
            return "result_2"
            
        def step_3():
            execution_log.append("step_3")
            return "result_3"
            
        task_id = "adversarial_task_001"
        methods = [step_1, step_2, step_3]
        
        # Execute - should fail AFTER step 2 completes, before step 3
        result = interruptible_executor.execute_with_interrupts(task_id, methods)
        
        # Verify interruption
        assert result.interrupt_reason == "Simulated Emergency"
        assert result.completed_steps == 2 # Step 1 & 2 completed, Step 3 blocked
        assert len(result.partial_results) == 2
        assert result.partial_results == ["result_1", "result_2"]
        assert result.resumable is True
        
        # Verify saved state
        saved = interruptible_executor.get_partial_progress(task_id)
        assert saved is not None
        assert saved.completed_steps == 2
        
        # Clear interrupt and resume
        interrupt_controller.clear_interrupt()
        
        # Resume execution
        final_result = interruptible_executor.resume_execution(task_id, methods)
        
        # Verify completion
        assert final_result.completed_steps == 3
        assert final_result.partial_results == ["result_1", "result_2", "result_3"]
        assert final_result.interrupt_reason is None
        assert final_result.resumable is False # Fully done

    def test_executor_deadlock_simulation(self, interrupt_controller, interruptible_executor):
        """
        Adversarial Test: Simulate a task that hangs (deadlock-like).
        Verify we can forcefully interrupt it from another thread.
        """
        
        def hanging_step():
            # Busy wait mimicking a hang
            start = time.time()
            while time.time() - start < 2.0:
                interruptible_executor.check_interrupt()
                time.sleep(0.01)
            return "finished"
            
        task_id = "hanging_task_001"
        
        # Thread to run the hanging task
        result_container = {}
        
        def run_task():
            try:
                result_container['result'] = interruptible_executor.execute_with_interrupts(task_id, [hanging_step])
            except ResourceEmergencyInterrupt:
                result_container['error'] = "Interrupted"

        t = threading.Thread(target=run_task)
        t.start()
        
        # Let it run for a bit
        time.sleep(0.1)
        
        # Signal interrupt
        interrupt_controller.signal_interrupt("Force Kill")
        
        t.join(timeout=1.0)
        
        assert not t.is_alive(), "Thread should have finished after interrupt"
        # Since execute_with_interrupts catches the exception and returns partial result:
        assert 'result' in result_container
        assert result_container['result'].interrupt_reason == "Force Kill"
        
    def test_synchronizer_malformed_input(self):
        """
        Adversarial Test: Feed garbage data to IrrigationSynchronizer.
        """
        # Malformed questionnaire: missing required fields
        garbage_questionnaire = {
            "blocks": {
                "micro_questions": [
                    {"id": "broken", "text": "missing fields"} # Missing policy_area_id, dimension_id
                ]
            }
        }
        
        # Should raise ValueError during init or execution
        # Depending on implementation, it might validate on init or execution
        # Based on code, init is safe, but build_execution_plan triggers extract_questions
        
        sync = IrrigationSynchronizer(
            questionnaire=garbage_questionnaire,
            document_chunks=[{"chunk_id": "c1", "text": "foo"}] # Legacy mode for simplicity
        )
        
        with pytest.raises(ValueError) as excinfo:
             sync.build_execution_plan()
             
        assert "missing policy_area_id" in str(excinfo.value) or "missing dimension_id" in str(excinfo.value)

    def test_synchronizer_duplicate_task_ids(self):
        """
        Adversarial Test: Ensure duplicate task IDs are detected and rejected.
        This simulates a hash collision or bad generator logic.
        """
        # Create a questionnaire that would generate duplicate task IDs
        # Same global question ID twice
        duplicate_questions = {
            "blocks": {
                "micro_questions": [
                    {
                        "question_id": "Q001",
                        "question_global": 1, 
                        "policy_area_id": "PA01",
                        "dimension_id": "D1",
                        "text": "First Q1"
                    },
                    {
                        "question_id": "Q001", # Same ID
                        "question_global": 1,  # Same global -> Same task_id MQC-001_PA01
                        "policy_area_id": "PA01",
                        "dimension_id": "D1",
                        "text": "Duplicate Q1"
                    }
                ]
            }
        }
        
        # Mock ChunkMatrix to bypass invariant validation
        with patch("farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer.ChunkMatrix") as MockChunkMatrix:
            MockChunkMatrix.EXPECTED_CHUNK_COUNT = 60 # Set to int to avoid JSON serialization error
            
            # Mock validation_orchestrator and signal_registry stuff
            with patch("farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer.validate_phase6_schema_compatibility"):
                 # We need to mock chunk routing to return success
                 with patch.object(IrrigationSynchronizer, 'validate_chunk_routing') as mock_routing:
                    mock_routing.return_value = Mock(
                        chunk_id="chunk_1",
                        policy_area_id="PA01", 
                        dimension_id="D1",
                        expected_elements=[],
                        document_position=(0, 100)
                    )
                    
                    # Mock signal resolution
                    with patch.object(IrrigationSynchronizer, '_resolve_signals_for_question', return_value=tuple()):
                        
                        # Set up mock chunk matrix instance
                        mock_chunk_matrix_instance = MockChunkMatrix.return_value
                        # Mock get_chunk if needed, though we mocked validate_chunk_routing so maybe not
                        
                        sync = IrrigationSynchronizer(
                            questionnaire=duplicate_questions,
                            preprocessed_document=Mock() # Will trigger ChunkMatrix init which is now mocked
                        )
                        # Ensure sync uses the mocked matrix
                        sync.chunk_matrix = mock_chunk_matrix_instance
                        sync.chunk_matrix._preprocessed_document.chunks = []
                        
                        # Also need to ensure chunk_count is set safely (mocked init should handle, but verify)
                        sync.chunk_count = 60

                        with pytest.raises(ValueError) as excinfo:
                            sync.build_execution_plan()
                            
                        assert "Duplicate task_id detected" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_resource_aware_executor_circuit_breaker(self):
        """
        Adversarial Test: Verify ResourceAwareExecutor respects circuit breaker.
        """
        mock_rm = Mock()
        mock_rm.can_execute.return_value = (False, "Circuit Open")
        
        executor = ResourceAwareExecutor(
            method_executor=Mock(),
            resource_manager=mock_rm,
            signal_registry=Mock(),
            config=Mock(),
            questionnaire_provider=Mock()
        )
        
        with pytest.raises(RuntimeError) as excinfo:
            await executor.execute_with_resource_management(
                executor_id="D1-Q1",
                context={}
            )
            
        assert "Circuit Open" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_resource_aware_executor_timeout(self):
        """
        Adversarial Test: Verify timeout enforcement.
        """
        mock_rm = Mock()
        mock_rm.can_execute.return_value = (True, "OK")
        
        # Use AsyncMock for async method
        from unittest.mock import AsyncMock
        mock_rm.start_executor_execution = AsyncMock(return_value={
            "max_memory_mb": 1024,
            "max_workers": 1,
            "priority": 0, # Low priority -> base timeout
            "degradation": {
                "entity_limit_factor": 1.0,
                "disable_expensive_computations": False,
                "use_simplified_methods": False,
                "skip_optional_analysis": False,
                "reduce_embedding_dims": False,
                "applied_strategies": [] # Added missing key
            }
        })
        # end_executor_execution is also async
        mock_rm.end_executor_execution = AsyncMock()
        
        # Create an executor that sleeps longer than timeout
        async def slow_execution(*args, **kwargs):
            await asyncio.sleep(0.2)
            return {}
            
        executor = ResourceAwareExecutor(
            method_executor=Mock(),
            resource_manager=mock_rm,
            signal_registry=Mock(),
            config=Mock(),
            questionnaire_provider=Mock()
        )
        
        # Use patch on the Class method because of __slots__ restriction on instance
        with patch.object(ResourceAwareExecutor, '_calculate_timeout', return_value=0.05):
            with patch.object(ResourceAwareExecutor, '_execute_async', side_effect=slow_execution):
                with pytest.raises(RuntimeError) as excinfo:
                    await executor.execute_with_resource_management(
                        executor_id="D1-Q1",
                        context={}
                    )
                    
                assert "timed out" in str(excinfo.value)
