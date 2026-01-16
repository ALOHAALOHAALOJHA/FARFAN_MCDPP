import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
from farfan_pipeline.phases.Phase_00.phase0_90_01_verified_pipeline_runner import (
    VerifiedPipelineRunner
)

@pytest.mark.asyncio
async def test_runner_flow(temp_dir):
    runner = VerifiedPipelineRunner(
        plan_pdf_path=temp_dir / "plan.pdf",
        artifacts_dir=temp_dir / "artifacts",
        questionnaire_path=temp_dir / "q.json"
    )
    
    # Mock stages
    with patch.object(runner, 'verify_input', return_value=True), \
         patch.object(runner, 'run_boot_checks', return_value=True), \
         patch.object(runner, 'initialize_determinism', return_value=True), \
         patch('farfan_pipeline.phases.Phase_0.phase0_90_01_verified_pipeline_runner.check_all_gates') as mock_gates:
         
         # Mock check_all_gates to return Passed
         mock_gate_result = MagicMock()
         mock_gate_result.passed = True
         mock_gates.return_value = (True, [mock_gate_result]*7) # 7 gates now
         
         success = await runner.run_phase_zero()
         assert success is True

def test_failure_manifest(temp_dir):
    runner = VerifiedPipelineRunner(
        plan_pdf_path=temp_dir / "plan.pdf",
        artifacts_dir=temp_dir / "artifacts",
        questionnaire_path=temp_dir / "q.json"
    )
    runner.errors.append("Error 1")
    
    manifest_path = runner.generate_failure_manifest()
    assert manifest_path.exists()
    assert "Error 1" in manifest_path.read_text()