"""
Unit tests for DoWhy causal inference integration.

Tests the DoWhyCausalAnalyzer class and its integration with the Derek Beach
process tracing pipeline.

Phase 1 SOTA Enhancement - 2026-01-07
"""

from __future__ import annotations

import networkx as nx
import pandas as pd
import pytest

from farfan_pipeline.methods.causal_inference_dowhy import (
    DOWHY_AVAILABLE,
    CausalAnalysisResult,
    CausalEffectEstimate,
    DoWhyCausalAnalyzer,
    RefutationResult,
    create_dowhy_analyzer,
)


class TestDoWhyCausalAnalyzer:
    """Test suite for DoWhyCausalAnalyzer"""

    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        analyzer = DoWhyCausalAnalyzer()
        assert analyzer is not None
        assert isinstance(analyzer.graph, nx.DiGraph)
        assert analyzer.logger is not None

    def test_factory_function(self):
        """Test create_dowhy_analyzer factory"""
        graph = nx.DiGraph([("A", "B"), ("B", "C")])
        analyzer = create_dowhy_analyzer(graph)

        assert analyzer is not None
        assert analyzer.graph == graph
        assert analyzer.graph.number_of_edges() == 2

    def test_dowhy_availability(self):
        """Test DoWhy availability detection"""
        analyzer = DoWhyCausalAnalyzer()
        assert analyzer.is_available() == DOWHY_AVAILABLE

    def test_graph_conversion(self):
        """Test NetworkX to DoWhy graph conversion"""
        graph = nx.DiGraph()
        graph.add_edge("treatment", "outcome")
        graph.add_edge("confounder", "treatment")
        graph.add_edge("confounder", "outcome")

        analyzer = DoWhyCausalAnalyzer(graph)
        gml_string = analyzer._convert_to_dowhy_graph(graph)

        assert "digraph" in gml_string
        assert "treatment" in gml_string
        assert "outcome" in gml_string
        assert "->" in gml_string

    def test_empty_graph_conversion(self):
        """Test conversion of empty graph"""
        analyzer = DoWhyCausalAnalyzer()
        gml_string = analyzer._convert_to_dowhy_graph(nx.DiGraph())
        assert gml_string == "digraph {}"

    def test_find_confounders(self):
        """Test confounder identification from graph structure"""
        # Create graph: Z -> X, Z -> Y, X -> Y
        graph = nx.DiGraph()
        graph.add_edge("Z", "X")  # Z is common cause
        graph.add_edge("Z", "Y")
        graph.add_edge("X", "Y")  # X -> Y is the causal effect of interest

        analyzer = DoWhyCausalAnalyzer(graph)
        confounders = analyzer.find_confounders("X", "Y")

        assert "Z" in confounders

    def test_find_mediators(self):
        """Test mediator identification on causal path"""
        # Create graph: X -> M -> Y
        graph = nx.DiGraph()
        graph.add_edge("X", "M")
        graph.add_edge("M", "Y")

        analyzer = DoWhyCausalAnalyzer(graph)
        mediators = analyzer.find_mediators("X", "Y")

        assert "M" in mediators
        assert "X" not in mediators  # Source not a mediator
        assert "Y" not in mediators  # Target not a mediator

    def test_get_all_paths(self):
        """Test finding all causal paths"""
        # Create graph with multiple paths: X->Y directly and X->M->Y
        graph = nx.DiGraph()
        graph.add_edge("X", "Y")
        graph.add_edge("X", "M")
        graph.add_edge("M", "Y")

        analyzer = DoWhyCausalAnalyzer(graph)
        paths = analyzer.get_all_paths("X", "Y")

        assert len(paths) == 2
        assert ["X", "Y"] in paths  # Direct path
        assert ["X", "M", "Y"] in paths  # Mediated path

    def test_no_path_between_nodes(self):
        """Test behavior when no path exists"""
        graph = nx.DiGraph()
        graph.add_edge("X", "Y")
        graph.add_edge("A", "B")  # Disconnected

        analyzer = DoWhyCausalAnalyzer(graph)
        paths = analyzer.get_all_paths("X", "B")

        assert len(paths) == 0

    @pytest.mark.skipif(not DOWHY_AVAILABLE, reason="DoWhy not installed")
    def test_identify_effect_with_data(self):
        """Test causal effect identification with sample data"""
        # Create simple causal graph: Z -> T, Z -> Y, T -> Y
        graph = nx.DiGraph()
        graph.add_edge("Z", "T")
        graph.add_edge("Z", "Y")
        graph.add_edge("T", "Y")

        # Generate synthetic data
        import numpy as np

        np.random.seed(42)
        n = 100
        Z = np.random.normal(0, 1, n)
        T = 2 * Z + np.random.normal(0, 0.5, n)
        Y = 3 * T + 4 * Z + np.random.normal(0, 0.5, n)

        data = pd.DataFrame({"Z": Z, "T": T, "Y": Y})

        analyzer = DoWhyCausalAnalyzer(graph)
        result = analyzer.identify_effect(data, treatment="T", outcome="Y", common_causes=["Z"])

        assert isinstance(result, CausalAnalysisResult)
        # Should identify Z as backdoor variable
        if result.identified:
            assert "Z" in result.backdoor_variables or len(result.backdoor_variables) > 0

    @pytest.mark.skipif(not DOWHY_AVAILABLE, reason="DoWhy not installed")
    def test_estimate_effect_with_data(self):
        """Test causal effect estimation"""
        # Create simple graph
        graph = nx.DiGraph()
        graph.add_edge("Z", "T")
        graph.add_edge("Z", "Y")
        graph.add_edge("T", "Y")

        # Generate synthetic data with known effect
        import numpy as np

        np.random.seed(42)
        n = 200
        Z = np.random.normal(0, 1, n)
        T = 2 * Z + np.random.normal(0, 0.5, n)
        Y = 3.0 * T + 4 * Z + np.random.normal(0, 0.5, n)  # True effect = 3.0

        data = pd.DataFrame({"Z": Z, "T": T, "Y": Y})

        analyzer = DoWhyCausalAnalyzer(graph)
        estimate = analyzer.estimate_effect(
            data, treatment="T", outcome="Y", method="backdoor.linear_regression", common_causes=["Z"]
        )

        assert isinstance(estimate, CausalEffectEstimate)
        if estimate.identified:
            # Should estimate effect around 3.0
            assert 2.0 < estimate.value < 4.0
            assert estimate.confidence_interval[0] < estimate.value < estimate.confidence_interval[1]

    @pytest.mark.skipif(not DOWHY_AVAILABLE, reason="DoWhy not installed")
    def test_refute_estimate(self):
        """Test refutation tests on estimated effect"""
        # Create graph
        graph = nx.DiGraph()
        graph.add_edge("T", "Y")

        # Generate data with clear causal effect
        import numpy as np

        np.random.seed(42)
        n = 300
        T = np.random.normal(0, 1, n)
        Y = 2.0 * T + np.random.normal(0, 0.5, n)

        data = pd.DataFrame({"T": T, "Y": Y})

        analyzer = DoWhyCausalAnalyzer(graph)
        estimate = analyzer.estimate_effect(data, treatment="T", outcome="Y")

        if estimate.identified:
            refutations = analyzer.refute_estimate(
                data, treatment="T", outcome="Y", estimate=estimate, methods=["placebo_treatment_refuter"]
            )

            assert isinstance(refutations, dict)
            if "placebo_treatment_refuter" in refutations:
                result = refutations["placebo_treatment_refuter"]
                assert isinstance(result, RefutationResult)
                assert result.method == "placebo_treatment_refuter"

    def test_invalid_treatment_variable(self):
        """Test error handling for invalid treatment variable"""
        graph = nx.DiGraph([("T", "Y")])
        data = pd.DataFrame({"T": [1, 2, 3], "Y": [4, 5, 6]})

        analyzer = DoWhyCausalAnalyzer(graph)

        with pytest.raises(ValueError, match=r"Treatment variable .* not found"):
            analyzer.identify_effect(data, treatment="INVALID", outcome="Y")

    def test_invalid_outcome_variable(self):
        """Test error handling for invalid outcome variable"""
        graph = nx.DiGraph([("T", "Y")])
        data = pd.DataFrame({"T": [1, 2, 3], "Y": [4, 5, 6]})

        analyzer = DoWhyCausalAnalyzer(graph)

        with pytest.raises(ValueError, match=r"Outcome variable .* not found"):
            analyzer.identify_effect(data, treatment="T", outcome="INVALID")

    def test_policy_graph_structure(self):
        """Test with policy-relevant causal graph structure"""
        # Simulate Derek Beach policy analysis graph
        graph = nx.DiGraph()

        # Inputs -> Activities -> Outputs -> Results -> Impacts
        graph.add_edge("INSUMOS", "ACTIVIDADES")
        graph.add_edge("ACTIVIDADES", "PRODUCTOS")
        graph.add_edge("PRODUCTOS", "RESULTADOS")
        graph.add_edge("RESULTADOS", "IMPACTOS")

        # Cross-cutting factors
        graph.add_edge("VIABILIDAD_POLITICA", "ACTIVIDADES")
        graph.add_edge("VIABILIDAD_POLITICA", "RESULTADOS")

        analyzer = DoWhyCausalAnalyzer(graph)

        # Test path analysis
        paths = analyzer.get_all_paths("INSUMOS", "IMPACTOS")
        assert len(paths) > 0
        assert all("INSUMOS" == path[0] for path in paths)
        assert all("IMPACTOS" == path[-1] for path in paths)

        # Test confounder detection
        confounders = analyzer.find_confounders("ACTIVIDADES", "RESULTADOS")
        assert "VIABILIDAD_POLITICA" in confounders

    def test_multiple_confounders(self):
        """Test identification of multiple confounders"""
        graph = nx.DiGraph()
        graph.add_edge("Z1", "T")
        graph.add_edge("Z1", "Y")
        graph.add_edge("Z2", "T")
        graph.add_edge("Z2", "Y")
        graph.add_edge("T", "Y")

        analyzer = DoWhyCausalAnalyzer(graph)
        confounders = analyzer.find_confounders("T", "Y")

        assert "Z1" in confounders
        assert "Z2" in confounders
        assert len(confounders) == 2


class TestCausalAnalysisResult:
    """Test CausalAnalysisResult dataclass"""

    def test_default_initialization(self):
        """Test default values"""
        result = CausalAnalysisResult()
        assert result.identified is False
        assert result.identification_status == "unidentified"
        assert len(result.backdoor_variables) == 0
        assert len(result.warnings) == 0

    def test_custom_initialization(self):
        """Test with custom values"""
        result = CausalAnalysisResult(
            identified=True,
            backdoor_variables=["Z1", "Z2"],
            identification_status="identified",
        )

        assert result.identified is True
        assert result.backdoor_variables == ["Z1", "Z2"]
        assert result.identification_status == "identified"


class TestCausalEffectEstimate:
    """Test CausalEffectEstimate dataclass"""

    def test_default_initialization(self):
        """Test default values"""
        estimate = CausalEffectEstimate()
        assert estimate.value == 0.0
        assert estimate.confidence_interval == (0.0, 0.0)
        assert estimate.identified is False

    def test_custom_initialization(self):
        """Test with custom values"""
        estimate = CausalEffectEstimate(
            value=2.5, confidence_interval=(2.0, 3.0), standard_error=0.25, method="backdoor.linear_regression", identified=True
        )

        assert estimate.value == 2.5
        assert estimate.confidence_interval == (2.0, 3.0)
        assert estimate.standard_error == 0.25
        assert estimate.method == "backdoor.linear_regression"
        assert estimate.identified is True


class TestRefutationResult:
    """Test RefutationResult dataclass"""

    def test_default_initialization(self):
        """Test default values"""
        result = RefutationResult()
        assert result.method == ""
        assert result.refuted is False
        assert result.p_value is None
        assert result.passed is True

    def test_custom_initialization(self):
        """Test with custom values"""
        result = RefutationResult(method="placebo_treatment_refuter", refuted=False, p_value=0.85, passed=True, summary="Test passed")

        assert result.method == "placebo_treatment_refuter"
        assert result.refuted is False
        assert result.p_value == 0.85
        assert result.passed is True
        assert result.summary == "Test passed"


@pytest.mark.skipif(not DOWHY_AVAILABLE, reason="DoWhy not installed")
class TestDoWhyIntegration:
    """Integration tests for DoWhy with Derek Beach pipeline"""

    def test_end_to_end_causal_analysis(self):
        """Test complete causal analysis workflow"""
        # Create policy intervention graph
        graph = nx.DiGraph()
        graph.add_edge("Intervencion", "Resultado")
        graph.add_edge("ContextoSocioeconomico", "Intervencion")
        graph.add_edge("ContextoSocioeconomico", "Resultado")

        # Generate synthetic policy data
        import numpy as np

        np.random.seed(42)
        n = 500
        Contexto = np.random.normal(50, 10, n)
        Intervencion = 0.5 * Contexto + np.random.normal(0, 5, n)
        Resultado = 1.5 * Intervencion + 0.3 * Contexto + np.random.normal(0, 3, n)

        data = pd.DataFrame(
            {
                "ContextoSocioeconomico": Contexto,
                "Intervencion": Intervencion,
                "Resultado": Resultado,
            }
        )

        analyzer = DoWhyCausalAnalyzer(graph)

        # Step 1: Identify effect
        identification = analyzer.identify_effect(
            data, treatment="Intervencion", outcome="Resultado", common_causes=["ContextoSocioeconomico"]
        )

        assert identification.identified
        assert "ContextoSocioeconomico" in identification.backdoor_variables

        # Step 2: Estimate effect
        estimate = analyzer.estimate_effect(
            data, treatment="Intervencion", outcome="Resultado", method="backdoor.linear_regression", common_causes=["ContextoSocioeconomico"]
        )

        assert estimate.identified
        # Should estimate around 1.5 (true effect)
        assert 1.0 < estimate.value < 2.0

        # Step 3: Refute estimate
        refutations = analyzer.refute_estimate(data, treatment="Intervencion", outcome="Resultado", estimate=estimate)

        assert len(refutations) > 0
        # At least one refutation should pass
        assert any(r.passed for r in refutations.values())
