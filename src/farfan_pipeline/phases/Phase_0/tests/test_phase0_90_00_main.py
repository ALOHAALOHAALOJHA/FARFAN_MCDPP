import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from farfan_pipeline.phases.Phase_0.phase0_90_00_main import main

@patch("farfan_pipeline.phases.Phase_0.phase0_90_00_main.run_phase_zero")
def test_main_entry_point(mock_run_phase, temp_dir):
    # Mock successful run
    mock_run_phase.return_value = MagicMock() # Returns wiring components
    
    # Mock sys.argv with named arguments
    args = ["main", "--plan", str(temp_dir/"plan.pdf"), "--artifacts-dir", str(temp_dir/"out")]
    with patch("sys.argv", args):
        ret = main()
        assert ret == 0

@patch("farfan_pipeline.phases.Phase_0.phase0_90_00_main.run_phase_zero")
def test_main_failure(mock_run_phase, temp_dir):
    # Mock failed run
    mock_run_phase.return_value = None
    
    args = ["main", "--plan", str(temp_dir/"plan.pdf")]
    with patch("sys.argv", args):
        ret = main()
        assert ret == 1