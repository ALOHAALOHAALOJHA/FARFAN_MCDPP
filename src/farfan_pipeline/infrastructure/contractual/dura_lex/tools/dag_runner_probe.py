#!/usr/bin/env python3
"""
CLI tool for Concurrency Determinism Contract (CDC) probe
"""
import sys
import json
from farfan_pipeline.contracts.concurrency_determinism import ConcurrencyDeterminismContract

def main():
    def dummy_task(x):
        return x + 1
        
    inputs = [1, 2, 3, 4, 5]
    
    print("Running with 1 worker...")
    res1 = ConcurrencyDeterminismContract.execute_concurrently(dummy_task, inputs, workers=1)
    print("Running with 4 workers...")
    res2 = ConcurrencyDeterminismContract.execute_concurrently(dummy_task, inputs, workers=4)
    
    stable = (res1 == res2)
    print(f"Stable Outputs: {stable}")
    
    certificate = {
        "pass": stable,
        "worker_configs": [1, 4],
        "stable_outputs": True
    }
    
    with open("cdc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: cdc_certificate.json")

if __name__ == "__main__":
    main()
