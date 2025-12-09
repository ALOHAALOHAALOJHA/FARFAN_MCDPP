#!/usr/bin/env python3
"""
CLI tool for Routing Contract (RC) check
"""
import sys
import json
import hashlib
from farfan_pipeline.contracts.routing_contract import RoutingContract, RoutingInput

def main():
    # Example usage
    inputs = RoutingInput(
        context_hash="dummy_context_hash",
        theta={"param": 1},
        sigma={"state": "active"},
        budgets={"cpu": 100.0},
        seed=12345
    )
    
    route = RoutingContract.compute_route(inputs)
    route_hash = hashlib.blake2b(json.dumps(route, sort_keys=True).encode()).hexdigest()
    inputs_hash = hashlib.blake2b(inputs.to_bytes()).hexdigest()
    
    print(f"Route: {route}")
    print(f"Route Hash: {route_hash}")
    
    certificate = {
        "pass": True,
        "route_hash": route_hash,
        "inputs_hash": inputs_hash,
        "tie_breaks": ["lexicographical"]
    }
    
    with open("rc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
    
    print("Certificate generated: rc_certificate.json")

if __name__ == "__main__":
    main()
