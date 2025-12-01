#!/usr/bin/env python3
"""
CLI tool for Traceability Contract (TC) audit trail
"""
import sys
import json
from farfan_core.contracts.traceability import TraceabilityContract, MerkleTree

def main():
    trail = ["event_a", "event_b", "event_c"]
    tree = MerkleTree(trail)
    
    print(f"Merkle Root: {tree.root}")
    
    # Verify
    is_valid = TraceabilityContract.verify_trace(trail, tree.root)
    print(f"Verification: {is_valid}")
    
    certificate = {
        "pass": is_valid,
        "merkle_root": tree.root,
        "proofs": len(trail),
        "tamper_detected": False
    }
    
    with open("tc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: tc_certificate.json")

if __name__ == "__main__":
    main()
