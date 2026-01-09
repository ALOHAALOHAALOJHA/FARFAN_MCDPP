"""
Unit Tests for Bayesian Inference Engine (Phase 2 SOTA)
========================================================

Comprehensive tests for:
- BayesianPriorBuilder (AGUJA I)
- BayesianSamplingEngine (AGUJA II)
- BayesianDiagnostics
- BayesianEngineAdapter

Phase 2 Testing - 2026-01-07
"""

import logging
from typing import Any
from unittest.mock import Mock

import numpy as np
import pytest

from farfan_pipeline.inference.bayesian_prior_builder import (
    BayesianPriorBuilder,
    PriorParameters,
    HierarchicalPrior,
)
from farfan_pipeline.inference.bayesian_sampling_engine import (
    BayesianSamplingEngine,
    SamplingResult,
)
from farfan_pipeline.inference.bayesian_diagnostics import (
    BayesianDiagnostics,
    ModelComparison,
    PosteriorPredictiveCheck,
)
from farfan_pipeline.inference.bayesian_adapter import BayesianEngineAdapter


# Test Configuration
class MockConfig:
    """Mock configuration for testing"""

    def __init__(self) -> None:
        self.bayesian_thresholds = Mock()
        self.bayesian_thresholds.prior_alpha = 1.0
        self.bayesian_thresholds.prior_beta = 1.0

    def get(self, key: str, default: Any = None) -> Any:
        if key == "bayesian_thresholds.prior_alpha":
            return 1.0
        elif key == "bayesian_thresholds.prior_beta":
            return 1.0
        return default


@pytest.fixture
def mock_config() -> MockConfig:
    """Fixture for mock configuration"""
    return MockConfig()


@pytest.fixture
def prior_builder(mock_config: MockConfig) -> BayesianPriorBuilder:
    """Fixture for BayesianPriorBuilder"""
    return BayesianPriorBuilder(config=mock_config)


@pytest.fixture
def sampling_engine(mock_config: MockConfig) -> BayesianSamplingEngine:
    """Fixture for BayesianSamplingEngine"""
    return BayesianSamplingEngine(config=mock_config)


@pytest.fixture
def diagnostics() -> BayesianDiagnostics:
    """Fixture for BayesianDiagnostics"""
    return BayesianDiagnostics()


@pytest.fixture
def adapter(mock_config: MockConfig) -> BayesianEngineAdapter:
    """Fixture for BayesianEngineAdapter"""
    return BayesianEngineAdapter(config=mock_config)


# ==================== BayesianPriorBuilder Tests ====================


class TestBayesianPriorBuilder:
    """Tests for BayesianPriorBuilder (AGUJA I)"""

    def test_initialization(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test prior builder initialization"""
        assert prior_builder.default_alpha == 1.0
        assert prior_builder.default_beta == 1.0
        assert isinstance(prior_builder.logger, logging.Logger)

    def test_straw_in_wind_prior(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test straw-in-wind prior (weak confirmation)"""
        prior = prior_builder.build_prior_for_evidence_type("straw_in_wind", rarity=0.0)

        assert prior.distribution == "beta"
        assert prior.alpha == 1.5
        assert prior.beta == 1.5
        assert prior.metadata["test_type"] == "weak_confirmation"

    def test_hoop_test_prior(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test hoop test prior (necessary condition)"""
        prior = prior_builder.build_prior_for_evidence_type("hoop", rarity=0.0)

        assert prior.distribution == "beta"
        assert prior.alpha == 2.0
        assert prior.beta == 1.0
        assert prior.metadata["test_type"] == "necessity"

    def test_smoking_gun_prior(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test smoking gun prior (sufficient condition)"""
        prior = prior_builder.build_prior_for_evidence_type("smoking_gun", rarity=0.0)

        assert prior.distribution == "beta"
        assert prior.alpha == 1.0
        assert prior.beta == 2.0
        assert prior.metadata["test_type"] == "sufficiency"

    def test_doubly_decisive_prior(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test doubly decisive prior (necessary AND sufficient)"""
        prior = prior_builder.build_prior_for_evidence_type("doubly_decisive", rarity=0.0)

        assert prior.distribution == "beta"
        assert prior.alpha == 3.0
        assert prior.beta == 3.0
        assert prior.metadata["test_type"] == "necessity_and_sufficiency"

    def test_rarity_adjustment(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test that rarity increases prior concentration"""
        prior_common = prior_builder.build_prior_for_evidence_type("hoop", rarity=0.0)
        prior_rare = prior_builder.build_prior_for_evidence_type("hoop", rarity=0.5)

        # Rare evidence should have higher concentration
        assert prior_rare.alpha > prior_common.alpha
        assert prior_rare.beta > prior_common.beta

    def test_hierarchical_prior(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test hierarchical prior for multi-level analysis"""
        group_sizes = [10, 20, 30]
        hierarchical = prior_builder.build_hierarchical_prior(group_sizes)

        assert hierarchical.n_groups == 3
        assert len(hierarchical.group_priors) == 3
        assert hierarchical.population_alpha == 2.0
        assert hierarchical.population_beta == 2.0

        # Check group weights sum to 1
        total_weight = sum(gp.metadata["weight"] for gp in hierarchical.group_priors)
        assert abs(total_weight - 1.0) < 1e-6

    def test_adaptive_prior_no_data(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test adaptive prior with no historical data"""
        prior = prior_builder.build_adaptive_prior(historical_data=None)

        # Should fall back to default
        assert prior.alpha == 1.0
        assert prior.beta == 1.0
        assert prior.metadata["adaptive"] is False

    def test_adaptive_prior_with_data(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test adaptive prior with historical data"""
        historical_data = [0.6, 0.7, 0.65, 0.68]
        prior = prior_builder.build_adaptive_prior(historical_data, confidence=1.0)

        assert prior.metadata["adaptive"] is True
        assert prior.metadata["n_observations"] == 4
        # Prior should be centered around historical mean
        assert 0.5 < prior.alpha / (prior.alpha + prior.beta) < 0.8

    def test_weakly_informative_prior(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test weakly informative prior"""
        prior = prior_builder.build_weakly_informative_prior(center=0.5, concentration=2.0)

        assert prior.alpha == 1.0
        assert prior.beta == 1.0
        assert prior.metadata["weakly_informative"] is True

    def test_skeptical_prior(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test skeptical prior (favors null hypothesis)"""
        prior = prior_builder.build_skeptical_prior(strength=0.8)

        # Beta should be larger than alpha (favors low probabilities)
        assert prior.beta > prior.alpha
        assert prior.metadata["skeptical"] is True

    def test_optimistic_prior(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test optimistic prior (favors alternative hypothesis)"""
        prior = prior_builder.build_optimistic_prior(strength=0.8)

        # Alpha should be larger than beta (favors high probabilities)
        assert prior.alpha > prior.beta
        assert prior.metadata["optimistic"] is True

    def test_prior_summary(self, prior_builder: BayesianPriorBuilder) -> None:
        """Test prior summary statistics"""
        prior = PriorParameters(distribution="beta", alpha=2.0, beta=2.0)
        summary = prior_builder.get_prior_summary(prior)

        assert summary["distribution"] == "beta"
        assert summary["alpha"] == 2.0
        assert summary["beta"] == 2.0
        assert abs(summary["mean"] - 0.5) < 1e-6  # Beta(2,2) has mean 0.5
        assert "variance" in summary


# ==================== BayesianSamplingEngine Tests ====================


class TestBayesianSamplingEngine:
    """Tests for BayesianSamplingEngine (AGUJA II)"""

    def test_initialization(self, sampling_engine: BayesianSamplingEngine) -> None:
        """Test sampling engine initialization"""
        assert isinstance(sampling_engine.logger, logging.Logger)

    @pytest.mark.skipif(
        not BayesianSamplingEngine(Mock()).is_available(),
        reason="PyMC not available",
    )
    def test_beta_binomial_sampling(self, sampling_engine: BayesianSamplingEngine) -> None:
        """Test Beta-Binomial conjugate sampling"""
        result = sampling_engine.sample_beta_binomial(
            n_successes=7,
            n_trials=10,
            prior_alpha=1.0,
            prior_beta=1.0,
            n_samples=500,
            n_chains=2,
        )

        assert result.converged is True
        assert 0.0 < result.posterior_mean < 1.0
        assert result.n_samples == 500
        assert result.n_chains == 2
        # Posterior mean should be near 7/10 = 0.7
        assert 0.5 < result.posterior_mean < 0.9

    @pytest.mark.skipif(
        not BayesianSamplingEngine(Mock()).is_available(),
        reason="PyMC not available",
    )
    def test_convergence_diagnostics(self, sampling_engine: BayesianSamplingEngine) -> None:
        """Test that convergence diagnostics are computed"""
        result = sampling_engine.sample_beta_binomial(
            n_successes=8,
            n_trials=10,
            prior_alpha=2.0,
            prior_beta=2.0,
            n_samples=1000,
            n_chains=2,
        )

        assert result.rhat is not None
        # R-hat should be close to 1.0 for convergence
        if result.rhat is not None:
            assert result.rhat < 1.1

    @pytest.mark.skipif(
        not BayesianSamplingEngine(Mock()).is_available(),
        reason="PyMC not available",
    )
    def test_hierarchical_sampling(self, sampling_engine: BayesianSamplingEngine) -> None:
        """Test hierarchical Beta-Binomial sampling"""
        group_data = [
            (7, 10),   # (n_successes, n_trials) for level 1
            (12, 20),  # (n_successes, n_trials) for level 2
            (18, 30),  # (n_successes, n_trials) for level 3
        ]

        results = sampling_engine.sample_hierarchical_beta(
            group_data=group_data,
            population_alpha=2.0,
            population_beta=2.0,
        )

        assert len(results) == 3
        assert all(r.converged for r in results)


# ==================== BayesianDiagnostics Tests ====================


class TestBayesianDiagnostics:
    """Tests for BayesianDiagnostics"""

    def test_initialization(self, diagnostics: BayesianDiagnostics) -> None:
        """Test diagnostics initialization"""
        assert isinstance(diagnostics.logger, logging.Logger)

    def test_availability_check(self, diagnostics: BayesianDiagnostics) -> None:
        """Test arviz availability check"""
        # Should return True or False, not error
        available = diagnostics.is_available()
        assert isinstance(available, bool)

    @pytest.mark.skipif(
        not BayesianDiagnostics().is_available(),
        reason="arviz not available",
    )
    def test_posterior_predictive_check(self, diagnostics: BayesianDiagnostics) -> None:
        """Test posterior predictive check (requires arviz)"""
        # This test requires a real trace object from PyMC
        # For now, test the structure
        observed_data = np.array([0.5, 0.6, 0.7])
        # Without real trace, expect error handling
        result = diagnostics.posterior_predictive_check(
            trace=None, observed_data=observed_data, test_statistic="mean"
        )
        assert result.passed is False  # Should fail without trace


# ==================== BayesianEngineAdapter Tests ====================


class TestBayesianEngineAdapter:
    """Tests for BayesianEngineAdapter (Unified Interface)"""

    def test_initialization(self, adapter: BayesianEngineAdapter) -> None:
        """Test adapter initialization"""
        assert adapter.prior_builder is not None
        assert adapter.sampling_engine is not None
        assert adapter.diagnostics is not None

    def test_update_prior_with_evidence(self, adapter: BayesianEngineAdapter) -> None:
        """Test Bayesian updating"""
        result = adapter.update_prior_with_evidence(
            prior_alpha=1.0,
            prior_beta=1.0,
            evidence_count=10,
            success_count=7,
        )

        assert "posterior_mean" in result
        assert "posterior_alpha" in result
        assert "posterior_beta" in result

        # Posterior alpha = prior alpha + successes
        assert result["posterior_alpha"] == 1.0 + 7.0
        # Posterior beta = prior beta + failures
        assert result["posterior_beta"] == 1.0 + 3.0

    @pytest.mark.skipif(
        not BayesianEngineAdapter(Mock()).is_available(),
        reason="PyMC not available",
    )
    def test_necessity_test(self, adapter: BayesianEngineAdapter) -> None:
        """Test hoop test (necessity)"""
        observations = [1, 1, 1, 0, 1, 1, 1, 1]  # 7/8 success
        result = adapter.test_necessity_from_observations(observations)

        assert "posterior_mean" in result
        assert "test_type" in result
        assert result["test_type"] == "necessity_hoop"
        # High success rate should yield high posterior
        assert result["posterior_mean"] > 0.5

    @pytest.mark.skipif(
        not BayesianEngineAdapter(Mock()).is_available(),
        reason="PyMC not available",
    )
    def test_sufficiency_test(self, adapter: BayesianEngineAdapter) -> None:
        """Test smoking gun (sufficiency)"""
        observations = [1, 1, 1, 0, 1, 1, 1, 1]
        result = adapter.test_sufficiency_from_observations(observations)

        assert "posterior_mean" in result
        assert "test_type" in result
        assert result["test_type"] == "sufficiency_smoking_gun"

    @pytest.mark.skipif(
        not BayesianEngineAdapter(Mock()).is_available(),
        reason="PyMC not available",
    )
    def test_doubly_decisive_test(self, adapter: BayesianEngineAdapter) -> None:
        """Test doubly decisive (necessity AND sufficiency)"""
        observations = [1, 1, 1, 1, 1, 1, 1, 1, 1, 0]  # 9/10 success
        result = adapter.test_doubly_decisive(observations)

        assert "posterior_mean" in result
        assert "test_type" in result
        assert result["test_type"] == "doubly_decisive"
        # Very high success rate should yield very high posterior
        assert result["posterior_mean"] > 0.7


# ==================== Integration Tests ====================


class TestBayesianEngineIntegration:
    """Integration tests for complete Bayesian workflow"""

    @pytest.mark.skipif(
        not BayesianEngineAdapter(Mock()).is_available(),
        reason="PyMC not available",
    )
    def test_complete_workflow(self, adapter: BayesianEngineAdapter) -> None:
        """Test complete Bayesian process tracing workflow"""
        # Step 1: Build prior
        prior = adapter.prior_builder.build_prior_for_evidence_type("hoop", rarity=0.3)
        assert prior.metadata["test_type"] == "necessity"

        # Step 2: Collect evidence (simulated)
        observations = [1] * 8 + [0] * 2  # 80% success

        # Step 3: Perform test
        result = adapter.test_necessity_from_observations(observations, prior=prior)

        # Step 4: Validate results
        assert result["converged"] is True
        assert 0.6 < result["posterior_mean"] < 0.95

        # Step 5: Check diagnostics
        if "rhat" in result:
            assert result["rhat"] < 1.1

    def test_hierarchical_analysis_workflow(self, adapter: BayesianEngineAdapter) -> None:
        """Test hierarchical analysis for micro-meso-macro levels"""
        # Convert observations to (successes, trials) tuples
        level_data = [
            (7, 10),   # micro: 7 successes out of 10
            (12, 20),  # meso: 12 successes out of 20
            (18, 30),  # macro: 18 successes out of 30
        ]

        result = adapter.analyze_hierarchical_mechanisms(
            level_data, level_names=["micro", "meso", "macro"]
        )

        assert "levels" in result
        assert len(result["levels"]) == 3
