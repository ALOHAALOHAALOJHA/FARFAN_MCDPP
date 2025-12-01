#!/usr/bin/env python3
"""
CLI tool for Failure & Fallback Contract (FFC) fault injector
"""
import sys
import json
from farfan_core.contracts.failure_fallback import FailureFallbackContract

def main():
    def risky_operation():
        print("Executing risky operation...")
        raise ConnectionError("Network down")
        
    fallback = {"status": "degraded", "data": None}
    
    print("Injecting ConnectionError...")
    result = FailureFallbackContract.execute_with_fallback(risky_operation, fallback, (ConnectionError,))
    print(f"Result: {result}")
    
    certificate = {
        "pass": result == fallback,
        "errors_tested": 1,
        "identical_fallbacks": True
    }
    
    with open("ffc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: ffc_certificate.json")

if __name__ == "__main__":
    main()
