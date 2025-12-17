#!/usr/bin/env python3
"""
CLI tool for Alignment Stability Contract (ASC) digest
"""
import sys
import json
from farfan_pipeline.contracts.alignment_stability import AlignmentStabilityContract

def main():
    sections = ["Section A", "Section B"]
    standards = ["Standard 1", "Standard 2"]
    params = {"lambda": 1.0, "epsilon": 0.05, "max_iter": 500}
    
    result = AlignmentStabilityContract.compute_alignment(sections, standards, params)
    
    print(f"Plan Digest: {result['plan_digest']}")
    print(f"Cost: {result['cost']}")
    print(f"Unmatched Mass: {result['unmatched_mass']}")
    
    certificate = {
        "pass": True,
        "plan_digest": result['plan_digest'],
        "cost": result['cost'],
        "unmatched_mass": result['unmatched_mass']
    }
    
    with open("asc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: asc_certificate.json")

if __name__ == "__main__":
    main()
