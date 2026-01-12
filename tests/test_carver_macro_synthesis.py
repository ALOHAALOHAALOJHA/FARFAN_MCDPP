"""
Tests for Carver Macro Synthesis with PA×DIM Divergence Analysis

Validates the new synthesize_macro() method and PA×DIM divergence calculation.

Author: F.A.R.F.A.N Pipeline
Version: 1.0.0
"""

import pytest
from typing import Dict, List, Tuple

# Test markers
pytestmark = [pytest.mark.updated, pytest.mark.integration]


class TestCarverMacroSynthesis:
    """Test Carver's synthesize_macro() method."""

    def test_carver_has_synthesize_macro_method(self):
        """Test that Carver has synthesize_macro method."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            synthesizer = DoctoralCarverSynthesizer()
            assert hasattr(
                synthesizer, "synthesize_macro"
            ), "DoctoralCarverSynthesizer should have synthesize_macro method"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_synthesize_macro_with_empty_meso_results(self):
        """Test macro synthesis with no meso results."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            synthesizer = DoctoralCarverSynthesizer()
            result = synthesizer.synthesize_macro(meso_results=[], coverage_matrix=None)

            assert isinstance(result, dict), "Result should be a dictionary"
            assert "score" in result, "Result should have score"
            assert "scoring_level" in result, "Result should have scoring_level"
            assert "hallazgos" in result, "Result should have hallazgos"
            assert "recomendaciones" in result, "Result should have recomendaciones"
            assert "fortalezas" in result, "Result should have fortalezas"
            assert "debilidades" in result, "Result should have debilidades"

            # With no meso results, score should be 0
            assert result["score"] == 0.0, "Score should be 0 with no meso results"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_synthesize_macro_with_meso_results(self):
        """Test macro synthesis with meso results."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            # Create mock meso results
            meso_results = [
                {"score": 0.85, "question_id": "MESO_1"},
                {"score": 0.75, "question_id": "MESO_2"},
                {"score": 0.90, "question_id": "MESO_3"},
            ]

            synthesizer = DoctoralCarverSynthesizer()
            result = synthesizer.synthesize_macro(meso_results=meso_results, coverage_matrix=None)

            assert result["score"] > 0.7, "Score should be > 0.7 with good meso results"
            assert result["n_meso_evaluated"] == 3, "Should have 3 meso results"
            assert len(result["hallazgos"]) > 0, "Should have hallazgos"
            assert len(result["fortalezas"]) > 0, "Should have fortalezas"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_synthesize_macro_with_coverage_matrix(self):
        """Test macro synthesis with PA×DIM coverage matrix."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            # Create mock coverage matrix (60 cells)
            coverage_matrix: Dict[Tuple[str, str], float] = {}
            policy_areas = [f"PA{i:02d}" for i in range(1, 11)]
            dimensions = [f"DIM{i:02d}" for i in range(1, 7)]

            for pa in policy_areas:
                for dim in dimensions:
                    # Simulate varying coverage
                    if pa in ["PA05", "PA07"]:
                        coverage_matrix[(pa, dim)] = 0.45  # Low coverage
                    else:
                        coverage_matrix[(pa, dim)] = 0.80  # Good coverage

            meso_results = [{"score": 0.80}]

            synthesizer = DoctoralCarverSynthesizer()
            result = synthesizer.synthesize_macro(
                meso_results=meso_results, coverage_matrix=coverage_matrix
            )

            assert "divergence_analysis" in result, "Should have divergence_analysis"
            div_analysis = result["divergence_analysis"]

            assert "overall_coverage" in div_analysis, "Should have overall_coverage"
            assert "critical_gaps_count" in div_analysis, "Should have critical_gaps_count"
            assert "low_coverage_pas" in div_analysis, "Should have low_coverage_pas"

            # Should detect PA05 and PA07 as low coverage
            low_pas = div_analysis["low_coverage_pas"]
            assert (
                "PA05" in low_pas or "PA07" in low_pas
            ), "Should identify PA05 or PA07 as low coverage"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_pa_dim_divergence_analysis(self):
        """Test _analyze_pa_dim_divergence method."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            # Create coverage matrix with known patterns
            coverage_matrix: Dict[Tuple[str, str], float] = {}

            # High coverage for most cells
            for i in range(1, 11):
                for j in range(1, 7):
                    pa = f"PA{i:02d}"
                    dim = f"DIM{j:02d}"
                    coverage_matrix[(pa, dim)] = 0.85

            # Create critical gaps in PA05
            for j in range(1, 7):
                coverage_matrix[("PA05", f"DIM{j:02d}")] = 0.35

            synthesizer = DoctoralCarverSynthesizer()
            analysis = synthesizer._analyze_pa_dim_divergence(coverage_matrix)

            assert analysis["total_cells"] == 60, "Should have 60 cells"
            assert analysis["critical_gaps_count"] == 6, "Should have 6 critical gaps in PA05"
            assert "PA05" in analysis["low_coverage_pas"], "Should identify PA05 as low coverage"

            # Check overall coverage is affected
            assert (
                analysis["overall_coverage"] <= 0.80
            ), "Overall coverage should be <= 0.80 with PA05 gaps"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_macro_scoring_levels(self):
        """Test that macro scoring produces correct levels."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            synthesizer = DoctoralCarverSynthesizer()

            # Test excelente level
            result_high = synthesizer.synthesize_macro(
                meso_results=[{"score": 0.90}, {"score": 0.88}], coverage_matrix=None
            )
            assert (
                result_high["scoring_level"] == "excelente"
            ), "High scores should produce 'excelente' level"

            # Test insuficiente level
            result_low = synthesizer.synthesize_macro(
                meso_results=[{"score": 0.40}, {"score": 0.45}], coverage_matrix=None
            )
            assert (
                result_low["scoring_level"] == "insuficiente"
            ), "Low scores should produce 'insuficiente' level"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_macro_recommendations_generation(self):
        """Test that recommendations are generated based on gaps."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            # Create coverage matrix with critical gaps
            coverage_matrix: Dict[Tuple[str, str], float] = {}
            for i in range(1, 11):
                for j in range(1, 7):
                    pa = f"PA{i:02d}"
                    dim = f"DIM{j:02d}"
                    # Create many critical gaps
                    coverage_matrix[(pa, dim)] = 0.30

            meso_results = [{"score": 0.50}]

            synthesizer = DoctoralCarverSynthesizer()
            result = synthesizer.synthesize_macro(
                meso_results=meso_results, coverage_matrix=coverage_matrix
            )

            recomendaciones = result["recomendaciones"]
            assert len(recomendaciones) > 0, "Should generate recommendations"

            # Should mention critical gaps
            has_priority_rec = any(
                "PRIORIDAD ALTA" in r or "gaps críticos" in r for r in recomendaciones
            )
            assert has_priority_rec, "Should have high priority recommendation for critical gaps"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_macro_identifies_strengths_and_weaknesses(self):
        """Test that strengths and weaknesses are properly identified."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            synthesizer = DoctoralCarverSynthesizer()

            # Test with high performing meso results
            result_strong = synthesizer.synthesize_macro(
                meso_results=[{"score": 0.85}, {"score": 0.87}, {"score": 0.83}],
                coverage_matrix=None,
            )

            fortalezas = result_strong["fortalezas"]
            assert len(fortalezas) > 0, "Should identify fortalezas"

            # Should mention consistency
            has_consistency = any("consistencia" in f.lower() for f in fortalezas)
            assert has_consistency, "Should mention consistency as strength"

            # Test with inconsistent results
            result_weak = synthesizer.synthesize_macro(
                meso_results=[{"score": 0.90}, {"score": 0.40}, {"score": 0.85}],
                coverage_matrix=None,
            )

            debilidades = result_weak["debilidades"]
            assert len(debilidades) > 0, "Should identify debilidades"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")


class TestPADIMDivergenceCalculation:
    """Test PA×DIM divergence calculation logic."""

    def test_divergence_with_uniform_coverage(self):
        """Test divergence analysis with uniform coverage."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            # Create uniform coverage matrix
            coverage_matrix: Dict[Tuple[str, str], float] = {}
            for i in range(1, 11):
                for j in range(1, 7):
                    coverage_matrix[(f"PA{i:02d}", f"DIM{j:02d}")] = 0.80

            synthesizer = DoctoralCarverSynthesizer()
            analysis = synthesizer._analyze_pa_dim_divergence(coverage_matrix)

            assert (
                analysis["critical_gaps_count"] == 0
            ), "Uniform high coverage should have no critical gaps"
            assert (
                analysis["overall_coverage"] == 0.80
            ), "Overall coverage should match uniform value"
            assert len(analysis["low_coverage_pas"]) == 0, "No PAs should have low coverage"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_divergence_by_dimension(self):
        """Test that divergence is calculated by dimension."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            # Create coverage with DIM01 weak across all PAs
            coverage_matrix: Dict[Tuple[str, str], float] = {}
            for i in range(1, 11):
                for j in range(1, 7):
                    pa = f"PA{i:02d}"
                    dim = f"DIM{j:02d}"
                    if dim == "DIM01":
                        coverage_matrix[(pa, dim)] = 0.40  # Weak DIM01
                    else:
                        coverage_matrix[(pa, dim)] = 0.85  # Good others

            synthesizer = DoctoralCarverSynthesizer()
            analysis = synthesizer._analyze_pa_dim_divergence(coverage_matrix)

            assert (
                "DIM01" in analysis["low_coverage_dims"]
            ), "DIM01 should be identified as low coverage"

            dim_scores = analysis["dim_scores"]
            assert dim_scores["DIM01"] < 0.55, "DIM01 score should be low"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")

    def test_divergence_patterns_identification(self):
        """Test that divergence patterns are identified and described."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            # Create specific patterns
            coverage_matrix: Dict[Tuple[str, str], float] = {}

            # PA01-PA08 good, PA09-PA10 bad
            for i in range(1, 9):
                for j in range(1, 7):
                    coverage_matrix[(f"PA{i:02d}", f"DIM{j:02d}")] = 0.80

            for i in range(9, 11):
                for j in range(1, 7):
                    coverage_matrix[(f"PA{i:02d}", f"DIM{j:02d}")] = 0.40

            synthesizer = DoctoralCarverSynthesizer()
            analysis = synthesizer._analyze_pa_dim_divergence(coverage_matrix)

            patterns = analysis["divergence_patterns"]
            assert len(patterns) > 0, "Should identify divergence patterns"

            # Should mention PA09 and PA10
            pattern_text = " ".join(patterns)
            assert (
                "PA09" in pattern_text or "PA10" in pattern_text
            ), "Should mention PAs with low coverage in patterns"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")


class TestMacroSynthesisIntegration:
    """Integration tests for macro synthesis."""

    def test_end_to_end_macro_synthesis(self):
        """Test complete macro synthesis workflow."""
        try:
            from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

            # Create realistic scenario
            meso_results = [
                {"score": 0.85, "question_id": "MESO_1", "question_text": "Cluster 1"},
                {"score": 0.75, "question_id": "MESO_2", "question_text": "Cluster 2"},
                {"score": 0.70, "question_id": "MESO_3", "question_text": "Cluster 3"},
                {"score": 0.80, "question_id": "MESO_4", "question_text": "Cluster 4"},
            ]

            coverage_matrix: Dict[Tuple[str, str], float] = {}
            for i in range(1, 11):
                for j in range(1, 7):
                    pa = f"PA{i:02d}"
                    dim = f"DIM{j:02d}"
                    # Realistic variation
                    if i <= 7:
                        coverage_matrix[(pa, dim)] = 0.75 + (i * 0.02)
                    else:
                        coverage_matrix[(pa, dim)] = 0.55 + (j * 0.03)

            synthesizer = DoctoralCarverSynthesizer()
            result = synthesizer.synthesize_macro(
                meso_results=meso_results,
                coverage_matrix=coverage_matrix,
                macro_question_text="¿El plan es coherente?",
            )

            # Validate complete structure
            assert result["score"] > 0.0, "Score should be calculated"
            assert result["scoring_level"] in ["excelente", "bueno", "aceptable", "insuficiente"]
            assert result["aggregation_method"] == "holistic_assessment"
            assert result["n_meso_evaluated"] == 4

            assert len(result["hallazgos"]) >= 3, "Should have multiple hallazgos"
            assert len(result["recomendaciones"]) >= 3, "Should have multiple recomendaciones"
            assert len(result["fortalezas"]) >= 1, "Should have fortalezas"
            assert len(result["debilidades"]) >= 1, "Should have debilidades"

            assert "divergence_analysis" in result
            assert "metadata" in result
            assert result["metadata"]["synthesis_method"] == "doctoral_carver_macro_v2"

        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
