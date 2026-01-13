import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock blake3 before importing bootstrap
sys.modules["blake3"] = MagicMock()

from farfan_pipeline.phases.Phase_0.phase0_90_02_bootstrap import (
    WiringBootstrap,
    WiringComponents,
    WiringFeatureFlags
)

def test_bootstrap_initialization(temp_dir):
    bootstrap = WiringBootstrap(
        questionnaire_path=temp_dir / "q.json",
        questionnaire_hash="hash",
        executor_config_path=temp_dir / "exec.json",
        calibration_profile="default",
        abort_on_insufficient=True,
        resource_limits={},
        flags=WiringFeatureFlags(enable_http_signals=False)
    )
    assert bootstrap.questionnaire_hash == "hash"

@patch("farfan_pipeline.phases.Phase_0.phase0_90_02_bootstrap.Phase0Validator")
def test_bootstrap_execution(mock_validator, temp_dir):
    # Mock resources
    (temp_dir / "q.json").write_text("{}")
    
    bootstrap = WiringBootstrap(
        questionnaire_path=temp_dir / "q.json",
        questionnaire_hash="hash",
        executor_config_path=temp_dir / "exec.json",
        calibration_profile="default",
        abort_on_insufficient=True,
        resource_limits={},
        flags=WiringFeatureFlags(enable_http_signals=False)
    )
    
    # Mock internal methods to avoid deep dependencies
    with patch.object(bootstrap, '_load_resources') as mock_load, \
         patch.object(bootstrap, '_build_signal_system') as mock_sigs, \
         patch.object(bootstrap, '_create_executor_config') as mock_exec, \
         patch.object(bootstrap, '_create_factory') as mock_fac, \
         patch.object(bootstrap, '_build_class_registry') as mock_reg, \
         patch.object(bootstrap, '_create_arg_router') as mock_router, \
         patch.object(bootstrap, '_compute_init_hashes') as mock_hashes:
         
         # Setup return values for mocks
         mock_load.return_value = MagicMock()
         mock_sigs.return_value = (MagicMock(), MagicMock())
         mock_exec.return_value = MagicMock()
         mock_fac.return_value = MagicMock()
         mock_reg.return_value = {}
         mock_router.return_value = MagicMock()
         mock_router.return_value.get_special_route_coverage.return_value = 30
         mock_hashes.return_value = {"hash": "test"}
         
         components = bootstrap.bootstrap()
         assert isinstance(components, WiringComponents)