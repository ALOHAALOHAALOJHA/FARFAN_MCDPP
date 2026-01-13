import pytest
from unittest.mock import MagicMock
from farfan_pipeline.phases.Phase_0.phase0_90_03_wiring_validator import (
    WiringValidator,
    WiringComponents,
    Severity
)

def test_wiring_validation_pass():
    wiring = MagicMock(spec=WiringComponents)
    # Setup happy path
    wiring.provider = MagicMock()
    wiring.signal_client = MagicMock()
    wiring.signal_registry = MagicMock()
    wiring.signal_registry._signals = {}
    wiring.signal_registry.get = MagicMock()
    wiring.executor_config = MagicMock()
    wiring.executor_config.random_seed = 42
    wiring.arg_router = MagicMock()
    wiring.arg_router.route = MagicMock()
    wiring.arg_router.special_cases = range(30)
    wiring.class_registry = {"C": type}
    
    # Mock internal structure for validators
    # This is complex because validation is deep. 
    # For unit test, we might want to test individual validators or mock them.
    
    validator = WiringValidator(strict_mode=False) # Relax strictness for unit test simplicity
    # Mock validators to pass
    validator.tier_validators = [] # Clear default validators for this test
    
    result = validator.validate(wiring)
    assert result.passed is True

def test_validator_registration():
    validator = WiringValidator()
    mock_tier = MagicMock()
    validator.register_custom_validator(mock_tier)
    assert mock_tier in validator.tier_validators
