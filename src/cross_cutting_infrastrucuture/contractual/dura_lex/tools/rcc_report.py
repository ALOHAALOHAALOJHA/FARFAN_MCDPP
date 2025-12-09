#!/usr/bin/env python3
"""
CLI tool for Risk Certificate Contract (RCC) report
"""
import sys
import json
import numpy as np
from farfan_pipeline.contracts.risk_certificate import RiskCertificateContract

def main():
    # Synthetic data
    np.random.seed(123)
    cal_data = list(np.random.beta(2, 5, 500))
    holdout_data = list(np.random.beta(2, 5, 200))
    alpha = 0.05
    seed = 123
    
    result = RiskCertificateContract.verify_risk(cal_data, holdout_data, alpha, seed)
    
    print(f"Alpha: {result['alpha']}")
    print(f"Threshold: {result['threshold']:.4f}")
    print(f"Coverage: {result['coverage']:.4f}")
    print(f"Risk: {result['risk']:.4f}")
    
    certificate = {
        "pass": True,
        "alpha": result['alpha'],
        "coverage": result['coverage'],
        "risk": result['risk'],
        "seed": seed
    }
    
    with open("rcc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: rcc_certificate.json")

if __name__ == "__main__":
    main()
