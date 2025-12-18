"""Tests for Phase 0 fallback policy enforcement."""

import os
import pytest


def test_prod_policy_forbids_category_a_c(monkeypatch):
    """Test that PROD mode forbids Category A and C fallbacks."""
    from canonic_phases.phase_0_input_validation.phase0_runtime_config import (
        RuntimeConfig,
        get_runtime_config,
    )
    from canonic_phases.phase_0_input_validation.contracts.phase0_fallback_policy_contract import (
        FallbackPolicyContract,
    )
    
    # Set PROD mode
    monkeypatch.setenv("SAAAAAA_RUNTIME_MODE", "prod")
    
    # Ensure Category A/C fallbacks are disabled
    monkeypatch.setenv("ALLOW_CONTRADICTION_FALLBACK", "false")
    monkeypatch.setenv("ALLOW_VALIDATOR_DISABLE", "false")
    monkeypatch.setenv("ALLOW_EXECUTION_ESTIMATES", "false")
    monkeypatch.setenv("ALLOW_DEV_INGESTION_FALLBACKS", "false")
    monkeypatch.setenv("ALLOW_AGGREGATION_DEFAULTS", "false")
    
    rc = get_runtime_config()
    contract = FallbackPolicyContract()
    
    # Should not raise - all forbidden fallbacks are disabled
    contract.enforce_prod_policy(rc)


def test_prod_policy_rejects_category_a_enabled(monkeypatch):
    """Test that PROD mode rejects enabled Category A fallbacks."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_fallback_policy_contract import (
        FallbackPolicyContract,
    )
    
    # Mock config with Category A enabled
    class MockConfig:
        allow_contradiction_fallback = True
        allow_validator_disable = False
        allow_execution_estimates = False
        allow_dev_ingestion_fallbacks = False
        allow_aggregation_defaults = False
    
    contract = FallbackPolicyContract()
    
    with pytest.raises(AssertionError, match="Category A.*contradiction.*forbidden"):
        contract.enforce_prod_policy(MockConfig())


def test_prod_policy_rejects_category_c_enabled(monkeypatch):
    """Test that PROD mode rejects enabled Category C fallbacks."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_fallback_policy_contract import (
        FallbackPolicyContract,
    )
    
    # Mock config with Category C enabled
    class MockConfig:
        allow_contradiction_fallback = False
        allow_validator_disable = False
        allow_execution_estimates = False
        allow_dev_ingestion_fallbacks = True
        allow_aggregation_defaults = False
    
    contract = FallbackPolicyContract()
    
    with pytest.raises(AssertionError, match="Category C.*dev ingestion.*forbidden"):
        contract.enforce_prod_policy(MockConfig())
