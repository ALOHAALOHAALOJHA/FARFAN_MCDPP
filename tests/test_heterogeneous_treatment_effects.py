"""
Unit Tests for EconML Heterogeneous Treatment Effects (Phase 3 SOTA)
=====================================================================

Tests for CATE estimation and policy recommendation.

Phase 3 Testing - 2026-01-07
"""

import logging
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from farfan_pipeline.methods.heterogeneous_treatment_effects import (
    HeterogeneousTreatmentAnalyzer,
    CATEEstimate,
    HeterogeneityAnalysis,
    PolicyRecommendation,
    create_treatment_analyzer,
)


@pytest.fixture
def mock_config() -> Mock:
    """Fixture for mock configuration"""
    return Mock()


@pytest.fixture
def analyzer(mock_config: Mock) -> HeterogeneousTreatmentAnalyzer:
    """Fixture for HeterogeneousTreatmentAnalyzer"""
    return HeterogeneousTreatmentAnalyzer(config=mock_config)


@pytest.fixture
def treatment_data() -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    Fixture for treatment effect data.

    Simulates heterogeneous treatment effects:
    - Treatment effect larger for high_income group
    """
    np.random.seed(42)
    n = 300

    # Covariates
    income = np.random.choice(["low", "high"], size=n, p=[0.6, 0.4])
    education = np.random.choice(["basic", "advanced"], size=n, p=[0.7, 0.3])
    region = np.random.choice(["rural", "urban"], size=n, p=[0.5, 0.5])

    income_numeric = np.where(income == "high", 1.0, 0.0)
    education_numeric = np.where(education == "advanced", 1.0, 0.0)
    region_numeric = np.where(region == "urban", 1.0, 0.0)

    X = pd.DataFrame(
        {
            "income": income,
            "education": education,
            "region": region,
            "income_num": income_numeric,
            "education_num": education_numeric,
            "region_num": region_numeric,
        }
    )

    # Treatment assignment (slightly confounded by income)
    treatment_prob = 0.5 + 0.2 * income_numeric
    T = pd.Series((np.random.rand(n) < treatment_prob).astype(float))

    # Outcome: heterogeneous treatment effect
    # Base outcome
    Y_base = 10 + 2 * income_numeric + 1.5 * education_numeric + np.random.randn(n)

    # Treatment effect (larger for high income)
    treatment_effect = 3 + 2 * income_numeric
    Y = pd.Series(Y_base + T * treatment_effect)

    return X, T, Y


# ==================== HeterogeneousTreatmentAnalyzer Tests ====================


class TestHeterogeneousTreatmentAnalyzer:
    """Tests for HeterogeneousTreatmentAnalyzer"""

    def test_initialization(self, analyzer: HeterogeneousTreatmentAnalyzer) -> None:
        """Test analyzer initialization"""
        assert isinstance(analyzer.logger, logging.Logger)
        assert analyzer.model is None
        assert analyzer.feature_names == []

    def test_availability_check(self, analyzer: HeterogeneousTreatmentAnalyzer) -> None:
        """Test EconML availability check"""
        available = analyzer.is_available()
        assert isinstance(available, bool)

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_estimate_cate_dml_linear(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test CATE estimation with Linear DML"""
        X, T, Y = treatment_data

        # Use numeric columns only
        X_numeric = X[["income_num", "education_num", "region_num"]]

        estimate = analyzer.estimate_cate_dml(
            X=X_numeric, T=T, Y=Y, method="linear", n_estimators=50
        )

        assert estimate.method == "DML-linear"
        assert estimate.n_observations == len(X)
        assert estimate.point_estimate > 0  # Should detect positive treatment effect
        assert estimate.std_error > 0
        assert len(estimate.confidence_interval) == 2

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_estimate_cate_dml_forest(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test CATE estimation with Causal Forest DML"""
        X, T, Y = treatment_data
        X_numeric = X[["income_num", "education_num", "region_num"]]

        estimate = analyzer.estimate_cate_dml(
            X=X_numeric, T=T, Y=Y, method="forest", n_estimators=50
        )

        assert estimate.method == "DML-forest"
        assert estimate.n_observations == len(X)
        # Forest should provide feature importance
        assert len(estimate.feature_importance) > 0

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_estimate_cate_t_learner(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test CATE estimation with T-Learner"""
        X, T, Y = treatment_data
        X_numeric = X[["income_num", "education_num", "region_num"]]

        estimate = analyzer.estimate_cate_metalearner(
            X=X_numeric, T=T, Y=Y, learner_type="T", n_estimators=50
        )

        assert estimate.method == "T-Learner"
        assert estimate.n_observations == len(X)
        assert estimate.point_estimate > 0

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_estimate_cate_s_learner(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test CATE estimation with S-Learner"""
        X, T, Y = treatment_data
        X_numeric = X[["income_num", "education_num", "region_num"]]

        estimate = analyzer.estimate_cate_metalearner(
            X=X_numeric, T=T, Y=Y, learner_type="S", n_estimators=50
        )

        assert estimate.method == "S-Learner"
        assert estimate.n_observations == len(X)

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_estimate_cate_x_learner(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test CATE estimation with X-Learner"""
        X, T, Y = treatment_data
        X_numeric = X[["income_num", "education_num", "region_num"]]

        estimate = analyzer.estimate_cate_metalearner(
            X=X_numeric, T=T, Y=Y, learner_type="X", n_estimators=50
        )

        assert estimate.method == "X-Learner"
        assert estimate.n_observations == len(X)

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_analyze_heterogeneity(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test heterogeneity analysis across subgroups"""
        X, T, Y = treatment_data

        analysis = analyzer.analyze_heterogeneity(
            X=X, T=T, Y=Y, subgroup_columns=["income", "education"]
        )

        assert analysis.average_treatment_effect > 0
        assert analysis.heterogeneity_score >= 0
        assert len(analysis.subgroup_effects) > 0
        assert len(analysis.recommendations) > 0

        # Should detect that high-income group has larger effect
        high_income_effect = analysis.subgroup_effects.get("income=high")
        low_income_effect = analysis.subgroup_effects.get("income=low")

        if high_income_effect and low_income_effect:
            # High income should have larger effect (by design)
            assert high_income_effect.point_estimate > low_income_effect.point_estimate

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_recommend_optimal_policy(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test optimal policy recommendation"""
        X, T, Y = treatment_data
        X_numeric = X[["income_num", "education_num", "region_num"]]

        recommendation = analyzer.recommend_optimal_policy(
            X=X_numeric,
            T=T,
            Y=Y,
            policy_name="Targeted Intervention",
            benefit_threshold=2.0,
        )

        assert recommendation.policy_name == "Targeted Intervention"
        assert len(recommendation.treatment_assignment) >= 0
        assert recommendation.expected_value >= 0
        assert 0 <= recommendation.confidence <= 1.0

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_sensitivity_analysis(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test sensitivity analysis for unmeasured confounding"""
        X, T, Y = treatment_data
        X_numeric = X[["income_num", "education_num", "region_num"]]

        sensitivity = analyzer.sensitivity_analysis(
            X=X_numeric, T=T, Y=Y, confounder_strength=0.2
        )

        assert "baseline_cate" in sensitivity
        assert "confounded_cate" in sensitivity
        assert "bias" in sensitivity
        assert "robustness_value" in sensitivity
        assert "interpretation" in sensitivity


# ==================== Integration Tests ====================


class TestHeterogeneousTreatmentIntegration:
    """Integration tests for complete CATE workflow"""

    @pytest.mark.skipif(
        not HeterogeneousTreatmentAnalyzer().is_available(),
        reason="EconML not available",
    )
    def test_complete_workflow(
        self,
        analyzer: HeterogeneousTreatmentAnalyzer,
        treatment_data: tuple[pd.DataFrame, pd.Series, pd.Series],
    ) -> None:
        """Test complete heterogeneous treatment effect workflow"""
        X, T, Y = treatment_data

        # Step 1: Estimate CATE
        X_numeric = X[["income_num", "education_num", "region_num"]]
        cate_estimate = analyzer.estimate_cate_dml(X_numeric, T, Y, method="forest")

        # Check for errors in metadata
        assert cate_estimate.metadata.get("error") is None
        assert cate_estimate.point_estimate > 0

        # Step 2: Analyze heterogeneity
        heterogeneity = analyzer.analyze_heterogeneity(
            X=X, T=T, Y=Y, subgroup_columns=["income"]
        )

        assert heterogeneity.heterogeneity_score >= 0
        assert len(heterogeneity.subgroup_effects) > 0

        # Step 3: Recommend policy
        policy = analyzer.recommend_optimal_policy(
            X=X_numeric, T=T, Y=Y, benefit_threshold=1.0
        )

        assert policy.expected_value >= 0
        assert len(policy.treatment_assignment) >= 0

        # Step 4: Sensitivity analysis
        sensitivity = analyzer.sensitivity_analysis(X_numeric, T, Y)

        assert "robustness_value" in sensitivity


# ==================== Factory Function Tests ====================


def test_create_treatment_analyzer() -> None:
    """Test factory function"""
    analyzer = create_treatment_analyzer()
    assert isinstance(analyzer, HeterogeneousTreatmentAnalyzer)


def test_create_treatment_analyzer_with_config() -> None:
    """Test factory function with config"""
    config = Mock()
    analyzer = create_treatment_analyzer(config=config)
    assert isinstance(analyzer, HeterogeneousTreatmentAnalyzer)
    assert analyzer.config == config
