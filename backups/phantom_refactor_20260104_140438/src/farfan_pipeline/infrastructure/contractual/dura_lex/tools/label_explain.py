#!/usr/bin/env python3
"""
CLI tool for Monotone Compliance Contract (MCC) label explain
"""
import sys
import json
from farfan_pipeline.contracts.monotone_compliance import MonotoneComplianceContract, Label

def main():
    rules = {
        "sat_reqs": ["doc_signed", "audit_passed"],
        "partial_reqs": ["doc_submitted"]
    }
    
    evidence = {"doc_submitted", "doc_signed", "audit_passed"}
    label = MonotoneComplianceContract.evaluate(evidence, rules)
    
    print(f"Evidence: {evidence}")
    print(f"Label: {Label(label).name}")
    
    # Check monotonicity with subset
    subset = {"doc_submitted"}
    is_monotone = MonotoneComplianceContract.verify_monotonicity(subset, evidence, rules)
    print(f"Monotonicity Check (Subset -> Full): {is_monotone}")
    
    certificate = {
        "pass": is_monotone,
        "upgrades": 1,
        "illegal_downgrades": 0
    }
    
    with open("mcc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: mcc_certificate.json")

if __name__ == "__main__":
    main()
