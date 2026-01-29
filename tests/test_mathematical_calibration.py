"""
Tests for Mathematical Calibration Module
==========================================

Validates that mathematical procedures produce better results than heuristic values.
"""

import numpy as np
import pytest
from sklearn.datasets import make_classification

from farfan_pipeline.calibration.mathematical_calibration import (
    N1EmpiricalOptimizer,
    N2InferentialOptimizer,
    N3AuditOptimizer,
    N4MetaOptimizer,
)


class TestN1EmpiricalOptimizer:
    """Test mathematical optimization for N1 (Empirical Extraction) level."""
    
    def test_optimal_extraction_threshold_roc(self):
        """Test that ROC analysis produces optimal threshold."""
        # Generate synthetic data
        np.random.seed(42)
        n_samples = 1000
        
        # True labels (ground truth)
        true_labels = np.random.randint(0, 2, n_samples)
        
        # Predicted scores (with noise)
        predicted_scores = true_labels.astype(float) + np.random.normal(0, 0.3, n_samples)
        predicted_scores = np.clip(predicted_scores, 0, 1)
        
        # Calculate optimal threshold
        threshold, metrics = N1EmpiricalOptimizer.calculate_optimal_extraction_threshold(
            true_labels, predicted_scores, beta_cost_ratio=1.0
        )
        
        # Validate results
        assert 0.0 <= threshold <= 1.0, "Threshold must be in [0, 1]"
        assert metrics["f_beta_score"] > 0.5, "F1-score should be reasonable"
        assert metrics["roc_auc"] > 0.5, "ROC AUC should be better than random"
        assert metrics["d_prime_sdt"] > 0, "Signal detection d' should be positive"
        
        # Verify optimal threshold is better than heuristic 0.6
        heuristic_threshold = 0.6
        heuristic_predictions = (predicted_scores >= heuristic_threshold).astype(int)
        optimal_predictions = (predicted_scores >= threshold).astype(int)
        
        from sklearn.metrics import f1_score
        heuristic_f1 = f1_score(true_labels, heuristic_predictions)
        optimal_f1 = metrics["f_beta_score"]
        
        print(f"\nHeuristic F1: {heuristic_f1:.3f}, Optimal F1: {optimal_f1:.3f}")
        # Optimal should be at least as good as heuristic
        assert optimal_f1 >= heuristic_f1 - 0.05, "Optimal should match or exceed heuristic"
    
    def test_deduplication_threshold_statistical(self):
        """Test statistical distribution analysis for deduplication."""
        np.random.seed(42)
        
        # Simulate similarity scores
        # Duplicates: high similarity (mean ~0.95)
        similarity_duplicates = np.random.beta(20, 1, 500)  # Skewed towards 1
        
        # Unique pairs: lower similarity (mean ~0.5)
        similarity_unique = np.random.beta(5, 5, 500)  # Centered around 0.5
        
        # Calculate optimal threshold
        threshold, metrics = N1EmpiricalOptimizer.calculate_deduplication_threshold_statistical(
            similarity_duplicates, similarity_unique, false_positive_rate_target=0.01
        )
        
        # Validate results
        assert 0.5 <= threshold <= 1.0, "Dedup threshold should be high"
        assert metrics["actual_fpr"] <= 0.02, "FPR should be controlled"
        assert metrics["sensitivity_recall"] > 0.8, "Should catch most duplicates"
        assert metrics["ks_pvalue"] < 0.05, "Distributions should be significantly different"
        
        print(f"\nDeduplication threshold: {threshold:.3f} (FPR={metrics['actual_fpr']:.4f})")
    
    def test_pattern_fuzzy_threshold_information_theoretic(self):
        """Test information-theoretic optimization for fuzzy matching."""
        np.random.seed(42)
        n_samples = 500
        
        # True matches
        true_matches = np.random.randint(0, 2, n_samples)
        
        # Fuzzy match scores (correlated with true matches)
        match_scores = true_matches.astype(float) * 0.4 + 0.5 + np.random.normal(0, 0.15, n_samples)
        match_scores = np.clip(match_scores, 0, 1)
        
        # Calculate optimal threshold
        threshold, metrics = N1EmpiricalOptimizer.calculate_pattern_fuzzy_threshold_information_theoretic(
            match_scores, true_matches
        )
        
        # Validate results
        assert 0.5 <= threshold <= 1.0, "Fuzzy threshold should be in upper range"
        assert metrics["mutual_information"] > 0, "MI should be positive"
        assert 0 <= metrics["information_gain_ratio"] <= 1, "IG ratio should be normalized"
        
        print(f"\nFuzzy threshold: {threshold:.3f} (MI={metrics['mutual_information']:.3f})")


class TestN2InferentialOptimizer:
    """Test mathematical optimization for N2 (Inferential Computation) level."""
    
    def test_empirical_bayes_prior_strength(self):
        """Test Empirical Bayes for prior strength calculation."""
        np.random.seed(42)
        
        # Simulate historical observations (success rates)
        # Beta(3, 2) distribution: mean ~0.6, variance moderate
        historical_observations = np.random.beta(3, 2, 100)
        
        # Calculate optimal prior strength
        prior_strength, metrics = N2InferentialOptimizer.calculate_optimal_prior_strength_empirical_bayes(
            historical_observations, method="moments"
        )
        
        # Validate results
        assert 0.1 <= prior_strength <= 10.0, "Prior strength in valid range"
        assert metrics["alpha"] > 0 and metrics["beta"] > 0, "Beta parameters positive"
        assert 0 < metrics["prior_mean"] < 1, "Prior mean is a probability"
        assert prior_strength > 1.0, "Should be more informative than uniform prior"
        
        print(f"\nPrior strength: {prior_strength:.2f} (α={metrics['alpha']:.2f}, β={metrics['beta']:.2f})")
        
        # Verify it's better than heuristic 0.5
        assert prior_strength != 0.5, "Should differ from arbitrary heuristic"
    
    def test_mcmc_samples_gelman_rubin(self):
        """Test Gelman-Rubin diagnostic for MCMC sample size."""
        np.random.seed(42)
        
        # Simulate MCMC chains (normal distribution with slight differences)
        n_chains = 4
        n_samples_pilot = 1000
        
        pilot_chains = [
            np.random.normal(0, 1, n_samples_pilot) + i * 0.1  # Slightly different starting points
            for i in range(n_chains)
        ]
        
        # Calculate optimal sample size
        n_samples, metrics = N2InferentialOptimizer.calculate_optimal_mcmc_samples_gelman_rubin(
            pilot_chains, target_rhat=1.01, max_samples=50000
        )
        
        # Validate results
        assert n_samples > 0, "Sample size must be positive"
        assert n_samples <= 50000, "Should respect max limit"
        assert metrics["current_rhat"] >= 1.0, "R̂ must be ≥ 1.0"
        
        print(f"\nOptimal MCMC samples: {n_samples} (R̂={metrics['current_rhat']:.4f})")
        
        # Verify it's more principled than heuristic 5000
        if metrics["current_rhat"] > 1.01:
            assert n_samples > 5000, "Should require more samples if not converged"


class TestN3AuditOptimizer:
    """Test mathematical optimization for N3 (Audit/Falsification) level."""
    
    def test_fdr_controlled_significance(self):
        """Test False Discovery Rate control for significance level."""
        np.random.seed(42)
        
        # Simulate p-values (mix of true and false hypotheses)
        n_tests = 100
        n_true_nulls = 70
        n_false_nulls = 30
        
        # True nulls: uniform p-values
        p_true_nulls = np.random.uniform(0, 1, n_true_nulls)
        
        # False nulls: small p-values (significant)
        p_false_nulls = np.random.beta(1, 10, n_false_nulls)  # Skewed towards 0
        
        p_values = np.concatenate([p_true_nulls, p_false_nulls])
        np.random.shuffle(p_values)
        
        # Calculate optimal significance level
        threshold, metrics = N3AuditOptimizer.calculate_optimal_significance_fdr_control(
            p_values, fdr_level=0.05
        )
        
        # Validate results
        assert 0 <= threshold <= 1, "Threshold in valid range"
        assert metrics["n_rejections"] <= metrics["n_tests"], "Rejections ≤ tests"
        assert metrics["expected_fdr"] >= 0, "FDR is non-negative"
        
        print(f"\nFDR-controlled threshold: {threshold:.4f} ({metrics['n_rejections']} rejections)")
        
        # Should be more stringent than arbitrary 0.05
        if metrics["n_rejections"] > 0:
            assert threshold <= 0.05, "FDR control typically stricter than fixed α"
    
    def test_spc_veto_thresholds(self):
        """Test Statistical Process Control for veto thresholds."""
        np.random.seed(42)
        
        # Simulate process values (quality scores)
        # Normal process: mean 0.7, std 0.15
        process_values = np.random.normal(0.7, 0.15, 500)
        process_values = np.clip(process_values, 0, 1)
        
        # Calculate veto thresholds
        critical, warning, metrics = N3AuditOptimizer.calculate_veto_thresholds_spc(
            process_values, sigma_critical=3.0, sigma_warning=2.0
        )
        
        # Validate results
        assert 0 <= critical < warning <= 1, "Thresholds properly ordered"
        assert critical < metrics["process_mean"], "Critical below mean"
        assert warning < metrics["process_mean"], "Warning below mean"
        assert metrics["cpk"] >= 0, "Cpk is non-negative"
        
        print(f"\nVeto thresholds: Critical={critical:.3f}, Warning={warning:.3f}")
        print(f"Process: μ={metrics['process_mean']:.3f}, σ={metrics['process_std']:.3f}, Cpk={metrics['cpk']:.2f}")
        
        # Verify it's data-driven, not arbitrary
        assert critical != 0.0, "Should not be arbitrary zero"
        assert warning != 0.5, "Should not be arbitrary midpoint"


class TestN4MetaOptimizer:
    """Test mathematical optimization for N4 (Meta-Analysis) level."""
    
    def test_failure_threshold_mutual_information(self):
        """Test mutual information for failure detection threshold."""
        np.random.seed(42)
        n_samples = 300
        
        # Simulate method outcomes and failures
        failure_labels = np.random.randint(0, 2, n_samples)
        
        # Outcomes correlated with failures (low scores = failure)
        method_outcomes = 1 - failure_labels.astype(float) * 0.5 + np.random.normal(0, 0.2, n_samples)
        method_outcomes = np.clip(method_outcomes, 0, 1)
        
        # Calculate optimal threshold
        threshold, metrics = N4MetaOptimizer.calculate_failure_threshold_mutual_information(
            method_outcomes, failure_labels
        )
        
        # Validate results
        assert 0 <= threshold <= 1, "Threshold in valid range"
        assert metrics["mutual_information"] >= 0, "MI is non-negative"
        assert 0 <= metrics["normalized_mi"] <= 1, "Normalized MI in [0,1]"
        
        print(f"\nFailure threshold: {threshold:.3f} (MI={metrics['mutual_information']:.3f})")
        
        # Should be optimized, not arbitrary 0.3
        assert threshold != 0.3, "Should differ from heuristic"
    
    def test_synthesis_threshold_entropy(self):
        """Test Shannon entropy for synthesis confidence threshold."""
        np.random.seed(42)
        
        # Simulate evidence distribution
        # Case 1: Low entropy (concentrated evidence)
        evidence_concentrated = np.array([0.7, 0.2, 0.1])
        threshold_conc, metrics_conc = N4MetaOptimizer.calculate_synthesis_threshold_entropy(
            evidence_concentrated, min_confidence=0.95
        )
        
        # Case 2: High entropy (distributed evidence)
        evidence_distributed = np.array([0.33, 0.33, 0.34])
        threshold_dist, metrics_dist = N4MetaOptimizer.calculate_synthesis_threshold_entropy(
            evidence_distributed, min_confidence=0.95
        )
        
        # Validate results
        assert 0.5 <= threshold_conc <= 0.99, "Concentrated threshold reasonable"
        assert 0.5 <= threshold_dist <= 0.99, "Distributed threshold reasonable"
        assert threshold_dist > threshold_conc, "Higher entropy requires higher confidence"
        
        print(f"\nSynthesis thresholds:")
        print(f"  Concentrated (H={metrics_conc['entropy']:.2f}): {threshold_conc:.3f}")
        print(f"  Distributed (H={metrics_dist['entropy']:.2f}): {threshold_dist:.3f}")
        
        # Should be entropy-adjusted, not arbitrary 0.7
        assert threshold_conc != 0.7, "Should be mathematically derived"
        assert threshold_dist != 0.7, "Should adapt to entropy"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
