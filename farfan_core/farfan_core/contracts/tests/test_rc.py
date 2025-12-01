"""
Tests for Routing Contract (RC)
"""
import pytest
from hypothesis import given, strategies as st
import hashlib
import json
from farfan_core.contracts.routing_contract import RoutingContract, RoutingInput

def calculate_route_hash(route):
    return hashlib.blake2b(json.dumps(route, sort_keys=True).encode()).hexdigest()

class TestRoutingContract:
    
    @given(st.text(), st.dictionaries(st.text(), st.integers()), st.dictionaries(st.text(), st.integers()), st.dictionaries(st.text(), st.floats()), st.integers())
    def test_determinism(self, context_hash, theta, sigma, budgets, seed):
        """Igual (QuestionContext.hash, Θ, σ, budgets, seed) ⇒ A* idéntico (byte a byte)."""
        inputs = RoutingInput(context_hash, theta, sigma, budgets, seed)
        
        route1 = RoutingContract.compute_route(inputs)
        route2 = RoutingContract.compute_route(inputs)
        
        assert route1 == route2
        assert calculate_route_hash(route1) == calculate_route_hash(route2)

    def test_metamorphosis_sigma_change(self):
        """Cambia exactamente un hash en σ ⇒ A* cambia y se registra diff."""
        inputs1 = RoutingInput("ctx", {}, {"h": 1}, {}, 42)
        inputs2 = RoutingInput("ctx", {}, {"h": 2}, {}, 42) # Changed sigma
        
        route1 = RoutingContract.compute_route(inputs1)
        route2 = RoutingContract.compute_route(inputs2)
        
        assert route1 != route2

    def test_tie_breaking(self):
        """Ties: misma ordenación por κ=(content_hash→lexicográfico)."""
        # The implementation of compute_route already sorts, ensuring this property.
        # We verify it explicitly here.
        inputs = RoutingInput("ctx", {}, {}, {}, 42)
        route = RoutingContract.compute_route(inputs)
        assert route == sorted(route)

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
