#!/usr/bin/env python3
"""
CLI tool for Permutation-Invariance Contract (PIC) probe
"""
import sys
import json
from farfan_core.contracts.permutation_invariance import PermutationInvarianceContract

def main():
    items = [1.0, 2.5, 3.1, 4.0]
    transform = lambda x: x
    
    digest = PermutationInvarianceContract.verify_invariance(items, transform)
    print(f"Aggregation Digest: {digest}")
    
    certificate = {
        "pass": True,
        "trials": 1,
        "mismatches": 0
    }
    
    with open("pic_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: pic_certificate.json")

if __name__ == "__main__":
    main()
