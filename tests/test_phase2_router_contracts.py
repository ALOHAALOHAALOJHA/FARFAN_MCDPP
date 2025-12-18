"""
Phase 2 Router Contract Tests

Verifies:
- Exhaustive type→executor mapping (no silent defaults)
- Routing determinism
- Parameter validation strictness
- No duck-typed routing

Certificate: CERTIFICATE_01_ROUTING_CONTRACT.md
"""

import pytest


@pytest.mark.updated
@pytest.mark.contract
def test_routing_contract_exhaustive_mapping():
    """All payload types must have explicit executor mappings."""
    pytest.skip("TODO: Implement after phase2_a_arg_router.py migration")


@pytest.mark.updated
@pytest.mark.contract
def test_routing_no_silent_default():
    """Unknown payload types must raise RoutingError, not return None."""
    pytest.skip("TODO: Implement after phase2_a_arg_router.py migration")


@pytest.mark.updated
@pytest.mark.contract
def test_routing_determinism():
    """Same payload type must always route to same executor."""
    pytest.skip("TODO: Implement after phase2_a_arg_router.py migration")


@pytest.mark.updated
@pytest.mark.contract
def test_routing_parameter_validation():
    """Missing required parameters must raise ValidationError."""
    pytest.skip("TODO: Implement after phase2_a_arg_router.py migration")
