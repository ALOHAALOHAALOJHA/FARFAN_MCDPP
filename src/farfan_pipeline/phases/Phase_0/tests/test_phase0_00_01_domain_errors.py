import pytest
from farfan_pipeline.phases.Phase_0.phase0_00_01_domain_errors import (
    ContractViolationError,
    DataContractError,
    SystemContractError
)

def test_domain_error_inheritance():
    """Verify inheritance hierarchy of domain errors."""
    err = DataContractError("Test error")
    assert isinstance(err, ContractViolationError)
    assert isinstance(err, Exception)

def test_system_error_inheritance():
    """Verify system error inheritance."""
    err = SystemContractError("System failure")
    assert isinstance(err, ContractViolationError)

def test_error_message():
    """Verify error string representation."""
    err = DataContractError("Invalid schema")
    assert str(err) == "Invalid schema"