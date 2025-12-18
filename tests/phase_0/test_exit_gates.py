"""Tests for Phase 0 exit gates."""

import pytest


def test_all_exit_gates_pass():
    """Test that ExitGatesContract validates all 7 gates passing."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_exit_gates_contract import (
        ExitGatesContract,
    )
    
    gates = [
        {"passed": True, "gate_name": "bootstrap", "gate_id": 1},
        {"passed": True, "gate_name": "input_verification", "gate_id": 2},
        {"passed": True, "gate_name": "boot_checks", "gate_id": 3},
        {"passed": True, "gate_name": "determinism", "gate_id": 4},
        {"passed": True, "gate_name": "questionnaire_integrity", "gate_id": 5},
        {"passed": True, "gate_name": "method_registry", "gate_id": 6},
        {"passed": True, "gate_name": "smoke_tests", "gate_id": 7},
    ]
    
    # Should not raise
    ExitGatesContract().validate(gates)


def test_exit_gates_rejects_failure():
    """Test that ExitGatesContract rejects failed gates."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_exit_gates_contract import (
        ExitGatesContract,
    )
    
    gates = [
        {"passed": True, "gate_name": "bootstrap", "gate_id": 1},
        {"passed": False, "gate_name": "input_verification", "gate_id": 2},
        {"passed": True, "gate_name": "boot_checks", "gate_id": 3},
        {"passed": True, "gate_name": "determinism", "gate_id": 4},
        {"passed": True, "gate_name": "questionnaire_integrity", "gate_id": 5},
        {"passed": True, "gate_name": "method_registry", "gate_id": 6},
        {"passed": True, "gate_name": "smoke_tests", "gate_id": 7},
    ]
    
    with pytest.raises(AssertionError, match="Exit gates failed"):
        ExitGatesContract().validate(gates)


def test_exit_gates_requires_all_seven():
    """Test that ExitGatesContract requires exactly 7 gates."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_exit_gates_contract import (
        ExitGatesContract,
    )
    
    gates = [
        {"passed": True, "gate_name": "bootstrap", "gate_id": 1},
        {"passed": True, "gate_name": "input_verification", "gate_id": 2},
    ]
    
    with pytest.raises(AssertionError, match="Expected 7 gates"):
        ExitGatesContract().validate(gates)


def test_bootstrap_contract():
    """Test BootstrapContract validation."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_bootstrap_contract import (
        BootstrapContract,
    )
    
    # Mock successful runner
    class MockRunner:
        _bootstrap_failed = False
        runtime_config = object()
        errors = []
    
    # Should not raise
    BootstrapContract().validate(MockRunner())


def test_bootstrap_contract_rejects_failure():
    """Test BootstrapContract rejects failed bootstrap."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_bootstrap_contract import (
        BootstrapContract,
    )
    
    # Mock failed runner
    class MockRunner:
        _bootstrap_failed = True
        runtime_config = None
        errors = ["Bootstrap error"]
    
    with pytest.raises(AssertionError, match="Bootstrap failed"):
        BootstrapContract().validate(MockRunner())


def test_input_contract_validates_hashes():
    """Test InputContract validates SHA-256 hashes."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_input_contract import (
        InputContract,
    )
    
    pdf_hash = "a" * 64
    questionnaire_hash = "b" * 64
    
    # Should not raise
    InputContract().validate_hashes(pdf_hash, questionnaire_hash)


def test_input_contract_rejects_invalid_length():
    """Test InputContract rejects invalid hash length."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_input_contract import (
        InputContract,
    )
    
    pdf_hash = "a" * 32  # Too short
    questionnaire_hash = "b" * 64
    
    with pytest.raises(AssertionError, match="Invalid PDF SHA-256 length"):
        InputContract().validate_hashes(pdf_hash, questionnaire_hash)


def test_input_contract_rejects_invalid_format():
    """Test InputContract rejects invalid hash format."""
    from canonic_phases.phase_0_input_validation.contracts.phase0_input_contract import (
        InputContract,
    )
    
    pdf_hash = "z" * 64  # Invalid hex
    questionnaire_hash = "b" * 64
    
    with pytest.raises(AssertionError, match="Invalid PDF SHA-256 format"):
        InputContract().validate_hashes(pdf_hash, questionnaire_hash)
