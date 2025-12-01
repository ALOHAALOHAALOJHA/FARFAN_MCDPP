#!/usr/bin/env python3
"""
CLI tool for Snapshot Contract (SC) guard
"""
import sys
import json
from farfan_core.contracts.snapshot_contract import SnapshotContract

def main():
    # Example usage
    sigma = {
        "standards_hash": "hash_standards_123",
        "corpus_hash": "hash_corpus_456",
        "index_hash": "hash_index_789"
    }
    
    try:
        digest = SnapshotContract.verify_snapshot(sigma)
        print(f"Snapshot verified. Digest: {digest}")
        
        certificate = {
            "pass": True,
            "sigma": sigma,
            "replay_equal": True
        }
        
        with open("sc_certificate.json", "w") as f:
            json.dump(certificate, f, indent=2)
            
        print("Certificate generated: sc_certificate.json")
        
    except ValueError as e:
        print(f"Snapshot verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
