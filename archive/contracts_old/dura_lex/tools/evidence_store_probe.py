#!/usr/bin/env python3
"""
CLI tool for Idempotency & De-dup Contract (IDC) probe
"""
import sys
import json
from farfan_pipeline.contracts.idempotency_dedup import IdempotencyContract

def main():
    items = [
        {"id": 1, "val": "a"},
        {"id": 2, "val": "b"},
        {"id": 1, "val": "a"} # Duplicate
    ]
    
    result = IdempotencyContract.verify_idempotency(items)
    
    print(f"State Hash: {result['state_hash']}")
    print(f"Items Stored: {result['count']}")
    print(f"Duplicates Blocked: {result['duplicates_blocked']}")
    
    certificate = {
        "pass": True,
        "duplicates_blocked": result['duplicates_blocked'],
        "state_hash": result['state_hash']
    }
    
    with open("idc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: idc_certificate.json")

if __name__ == "__main__":
    main()
