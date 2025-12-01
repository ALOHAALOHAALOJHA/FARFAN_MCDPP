"""
Tests for Risk Certificate Contract (RCC)
"""
import pytest
import numpy as np
from farfan_core.contracts.risk_certificate import RiskCertificateContract

class TestRiskCertificateContract:
    
    def test_reproducibility(self):
        """Split fijo+seed ⇒ mismos intervalos/sets."""
        cal_data = [0.1, 0.2, 0.5, 0.8]
        holdout = [0.15, 0.6]
        alpha = 0.1
        seed = 42
        
        res1 = RiskCertificateContract.verify_risk(cal_data, holdout, alpha, seed)
        res2 = RiskCertificateContract.verify_risk(cal_data, holdout, alpha, seed)
        
        assert res1 == res2

    def test_coverage_guarantee(self):
        """Cobertura empírica ≈ (1−α) en holdout (statistically)."""
        # Generate synthetic data
        np.random.seed(42)
        data = np.random.random(1000)
        cal_data = list(data[:800])
        holdout = list(data[800:])
        alpha = 0.1
        
        res = RiskCertificateContract.verify_risk(cal_data, holdout, alpha, 42)
        
        # Coverage should be close to 1-alpha (0.9)
        # Allow some statistical fluctuation
        assert res["coverage"] >= 0.85 

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
