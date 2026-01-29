import pytest
from unittest.mock import patch, MagicMock
from farfan_pipeline.phases.Phase_00.phase0_50_00_boot_checks import (
    run_boot_checks,
    BootCheckError,
    RuntimeMode
)

def test_boot_checks_dev_mode(mock_config):
    """Test boot checks pass/warn in DEV mode."""
    # Mock all checks to fail or pass
    with patch("farfan_pipeline.phases.Phase_00.phase0_50_00_boot_checks.check_contradiction_module_available", return_value=False), \
         patch("farfan_pipeline.phases.Phase_00.phase0_50_00_boot_checks.check_wiring_validator_available", return_value=True):
         
         results = run_boot_checks(mock_config)
         assert results["wiring_validator"] is True
         assert results["contradiction_module"] is False
         # Does not raise because DEV mode allow_contradiction_fallback=True in mock_config

def test_boot_checks_prod_fatal(mock_config):
    """Test boot checks fail in PROD mode."""
    # Force PROD mode
    object.__setattr__(mock_config, 'mode', RuntimeMode.PROD)
    object.__setattr__(mock_config, 'allow_contradiction_fallback', False)
    
    with patch("farfan_pipeline.phases.Phase_00.phase0_50_00_boot_checks.check_contradiction_module_available", side_effect=BootCheckError("mod", "reason", "code")):
        with pytest.raises(BootCheckError):
            run_boot_checks(mock_config)
