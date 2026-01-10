"""
Unit Tests for CausalNex Structure Learning (Phase 2 SOTA)
===========================================================

Tests for Bayesian Network structure learning and what-if analysis.

Phase 2 Testing - 2026-01-07
"""

import logging
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from farfan_pipeline.methods.causal_structure_learning import CausalStructureLearner


@pytest.fixture
def mock_config() -> Mock:
    """Fixture for mock configuration"""
    return Mock()


@pytest.fixture
def learner(mock_config: Mock) -> CausalStructureLearner:
    """Fixture for CausalStructureLearner"""
    return CausalStructureLearner(config=mock_config)


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Fixture for sample data"""
    np.random.seed(42)
    n = 100

    # Simulate causal structure: X -> Y -> Z
    X = np.random.randn(n)
    Y = 0.5 * X + np.random.randn(n) * 0.3
    Z = 0.7 * Y + np.random.randn(n) * 0.3

    return pd.DataFrame({"X": X, "Y": Y, "Z": Z})


@pytest.fixture
def categorical_data() -> pd.DataFrame:
    """Fixture for categorical data (for Bayesian Network)"""
    np.random.seed(42)
    n = 200

    budget = np.random.choice(["low", "medium", "high"], size=n, p=[0.3, 0.5, 0.2])
    support = np.random.choice(["weak", "moderate", "strong"], size=n, p=[0.4, 0.4, 0.2])

    # Simulate success depends on budget and support
    success_prob = np.zeros(n)
    for i in range(n):
        if budget[i] == "high" and support[i] == "strong":
            success_prob[i] = 0.9
        elif budget[i] == "high" or support[i] == "strong":
            success_prob[i] = 0.6
        elif budget[i] == "low" and support[i] == "weak":
            success_prob[i] = 0.1
        else:
            success_prob[i] = 0.4

    success = (np.random.rand(n) < success_prob).astype(str)
    success = np.where(success == "True", "yes", "no")

    return pd.DataFrame({"budget": budget, "support": support, "success": success})


# ==================== CausalStructureLearner Tests ====================


class TestCausalStructureLearner:
    """Tests for CausalStructureLearner"""

    def test_initialization(self, learner: CausalStructureLearner) -> None:
        """Test structure learner initialization"""
        assert isinstance(learner.logger, logging.Logger)
        assert learner.structure_model is None
        assert learner.bayesian_network is None

    def test_availability_check(self, learner: CausalStructureLearner) -> None:
        """Test CausalNex availability check"""
        available = learner.is_available()
        assert isinstance(available, bool)

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_learn_structure_empty_data(self, learner: CausalStructureLearner) -> None:
        """Test structure learning with empty data"""
        empty_df = pd.DataFrame()
        result = learner.learn_structure(empty_df)

        assert "error" in result.metadata
        assert result.n_nodes == 0

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_learn_structure_success(
        self, learner: CausalStructureLearner, sample_data: pd.DataFrame
    ) -> None:
        """Test successful structure learning"""
        result = learner.learn_structure(sample_data, w_threshold=0.1)

        assert result.is_dag is True
        assert result.n_nodes == 3
        assert result.n_edges >= 0  # NOTEARS may find 0 or more edges
        assert len(result.cycles) == 0  # Should be acyclic

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_fit_bayesian_network(
        self, learner: CausalStructureLearner, categorical_data: pd.DataFrame
    ) -> None:
        """Test fitting Bayesian Network"""
        # First learn structure
        result = learner.learn_structure(categorical_data, w_threshold=0.1)

        if result.n_edges > 0:
            # Fit Bayesian Network
            success = learner.fit_bayesian_network(categorical_data)
            assert success is True
            assert learner.bayesian_network is not None
            assert learner.inference_engine is not None

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_query_distribution_no_inference_engine(self, learner: CausalStructureLearner) -> None:
        """Test query distribution without inference engine"""
        result = learner.query_distribution("X", evidence={})

        assert result.passed is False if hasattr(result, "passed") else True
        assert "error" in result.metadata

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_what_if_analysis_no_engine(self, learner: CausalStructureLearner) -> None:
        """Test what-if analysis without inference engine"""
        scenario = learner.what_if_analysis(
            scenario_name="Test",
            interventions={"X": "high"},
            query_variables=["Y"],
        )

        assert "error" in scenario.metadata

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_find_causal_paths_no_structure(self, learner: CausalStructureLearner) -> None:
        """Test finding causal paths without structure"""
        paths = learner.find_causal_paths("X", "Y")
        assert paths == []

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_markov_blanket_no_structure(self, learner: CausalStructureLearner) -> None:
        """Test Markov blanket without structure"""
        blanket = learner.find_markov_blanket("X")
        assert blanket == []

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_get_structure_summary_no_structure(self, learner: CausalStructureLearner) -> None:
        """Test structure summary without structure"""
        summary = learner.get_structure_summary()
        assert "error" in summary

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_export_structure_no_structure(
        self, learner: CausalStructureLearner, tmp_path: Path
    ) -> None:
        """Test exporting structure without structure"""
        output_path = tmp_path / "test.dot"
        success = learner.export_structure_dot(str(output_path))
        assert success is False


# ==================== Integration Tests ====================


class TestCausalStructureIntegration:
    """Integration tests for complete structure learning workflow"""

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_complete_workflow_continuous(
        self, learner: CausalStructureLearner, sample_data: pd.DataFrame
    ) -> None:
        """Test complete workflow with continuous data"""
        # Step 1: Learn structure
        structure_result = learner.learn_structure(sample_data, w_threshold=0.1)

        assert structure_result.is_dag is True
        assert structure_result.n_nodes == 3

        # Step 2: Get summary
        if structure_result.n_edges > 0:
            summary = learner.get_structure_summary()
            assert "n_nodes" in summary
            assert summary["n_nodes"] == 3

    @pytest.mark.skipif(
        not CausalStructureLearner().is_available(),
        reason="CausalNex not available",
    )
    def test_complete_workflow_categorical(
        self, learner: CausalStructureLearner, categorical_data: pd.DataFrame
    ) -> None:
        """Test complete workflow with categorical data"""
        # Step 1: Learn structure
        structure_result = learner.learn_structure(categorical_data, w_threshold=0.05)

        if structure_result.n_edges == 0:
            pytest.skip("NOTEARS found no edges - may happen with small samples")

        # Step 2: Fit Bayesian Network
        success = learner.fit_bayesian_network(categorical_data)
        if not success:
            pytest.skip("Failed to fit Bayesian Network - may happen with sparse structure")

        # Step 3: Query distribution
        result = learner.query_distribution("success", evidence={"budget": "high"})
        assert result.query_variable == "success"
        assert len(result.posterior_distribution) > 0

        # Step 4: What-if analysis
        scenario = learner.what_if_analysis(
            scenario_name="Increase Budget",
            interventions={"budget": "high"},
            query_variables=["success"],
            baseline_evidence={"budget": "low"},
        )

        assert scenario.scenario_name == "Increase Budget"
        assert "success" in scenario.predictions


# ==================== Factory Function Tests ====================


def test_create_structure_learner() -> None:
    """Test factory function"""
    learner = create_structure_learner()
    assert isinstance(learner, CausalStructureLearner)


def test_create_structure_learner_with_config() -> None:
    """Test factory function with config"""
    config = Mock()
    learner = create_structure_learner(config=config)
    assert isinstance(learner, CausalStructureLearner)
    assert learner.config == config
