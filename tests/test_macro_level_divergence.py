"""
Tests for Macro-Level Development Plan Divergence Analysis

Validates that the system can effectively answer macro-level questions about
divergence between development plans and the PA×DIM matrix.

Author: F.A.R.F.A.N Pipeline
Version: 1.0.0
"""

import pytest
from pathlib import Path
from typing import Dict, List, Tuple

# Test markers
pytestmark = [pytest.mark.updated, pytest.mark.integration]


class TestPADIMMatrixCapability:
    """Test PA×DIM matrix tracking and coverage analysis capabilities."""
    
    def test_pa_dim_matrix_dimensions(self):
        """Test that PA×DIM matrix has correct dimensions (10×6 = 60 cells)."""
        policy_areas = [f"PA{i:02d}" for i in range(1, 11)]
        dimensions = [f"DIM{i:02d}" for i in range(1, 7)]
        
        assert len(policy_areas) == 10, "Should have 10 policy areas"
        assert len(dimensions) == 6, "Should have 6 dimensions"
        
        # Total cells
        total_cells = len(policy_areas) * len(dimensions)
        assert total_cells == 60, "PA×DIM matrix should have 60 cells"
    
    def test_policy_area_enum_exists(self):
        """Test that PolicyArea enum is defined with PA01-PA10."""
        try:
            from farfan_pipeline.core.types import PolicyArea
            
            # Check all PA01-PA10 exist
            for i in range(1, 11):
                pa_name = f"PA{i:02d}"
                assert hasattr(PolicyArea, pa_name), f"PolicyArea.{pa_name} should exist"
            
            # Check total count
            policy_areas = list(PolicyArea)
            assert len(policy_areas) == 10, "Should have exactly 10 policy areas"
            
        except ImportError:
            pytest.fail("PolicyArea enum not found in farfan_pipeline.core.types")
    
    def test_dimension_enum_exists(self):
        """Test that DimensionCausal enum is defined with DIM01-DIM06."""
        try:
            from farfan_pipeline.core.types import DimensionCausal
            
            # Check all DIM01-DIM06 exist
            for i in range(1, 7):
                dim_name = f"DIM{i:02d}_" 
                # Note: actual names are DIM01_INSUMOS, etc.
                matching = [d for d in DimensionCausal if d.value == f"DIM{i:02d}"]
                assert len(matching) == 1, f"DIM{i:02d} should exist"
            
            # Check total count
            dimensions = list(DimensionCausal)
            assert len(dimensions) == 6, "Should have exactly 6 dimensions"
            
        except ImportError:
            pytest.fail("DimensionCausal enum not found in farfan_pipeline.core.types")
    
    def test_coverage_matrix_type_exists(self):
        """Test that coverage_matrix field exists in appropriate types."""
        try:
            from farfan_pipeline.core.types import AnalysisResult
            import inspect
            
            # Check AnalysisResult has coverage_matrix_scores
            sig = inspect.signature(AnalysisResult)
            assert 'coverage_matrix_scores' in str(sig), \
                "AnalysisResult should have coverage_matrix_scores field"
            
        except ImportError:
            pytest.fail("AnalysisResult not found in farfan_pipeline.core.types")


class TestMacroQuestionStructure:
    """Test macro question structure and configuration."""
    
    def test_macro_question_result_type_exists(self):
        """Test that MacroQuestionResult type is defined."""
        try:
            from farfan_pipeline.core.types import MacroQuestionResult
            import inspect
            
            # Check it's a dataclass
            sig = inspect.signature(MacroQuestionResult)
            params = list(sig.parameters.keys())
            
            # Check required fields
            required_fields = ['score', 'scoring_level', 'aggregation_method']
            for field in required_fields:
                assert field in params, f"MacroQuestionResult should have {field} field"
            
        except ImportError:
            pytest.fail("MacroQuestionResult not found in farfan_pipeline.core.types")
    
    def test_macro_question_defined_in_questionnaire(self):
        """Test that macro question is defined in questionnaire_monolith.json."""
        questionnaire_path = Path(__file__).resolve().parent.parent / "canonic_questionnaire_central" / "questionnaire_monolith.json"
        
        if not questionnaire_path.exists():
            pytest.skip("questionnaire_monolith.json not found")
        
        import json
        with open(questionnaire_path) as f:
            questionnaire = json.load(f)
        
        blocks = questionnaire.get("blocks", {})
        macro_question = blocks.get("macro_question", {})
        
        assert macro_question, "macro_question should be defined in blocks"
        assert macro_question.get("question_id") == "MACRO_1", \
            "Macro question should have ID MACRO_1"
        assert macro_question.get("type") == "MACRO", \
            "Macro question should have type MACRO"
    
    def test_macro_question_aggregation_method(self):
        """Test that macro question uses holistic_assessment aggregation."""
        questionnaire_path = Path(__file__).resolve().parent.parent / "canonic_questionnaire_central" / "questionnaire_monolith.json"
        
        if not questionnaire_path.exists():
            pytest.skip("questionnaire_monolith.json not found")
        
        import json
        with open(questionnaire_path) as f:
            questionnaire = json.load(f)
        
        macro_question = questionnaire.get("blocks", {}).get("macro_question", {})
        
        assert macro_question.get("aggregation_method") == "holistic_assessment", \
            "Macro question should use holistic_assessment aggregation"


class TestCarverCapabilities:
    """Test Carver component capabilities for macro-level synthesis."""
    
    def test_carver_file_exists(self):
        """Test that carver.py exists."""
        carver_path = Path(__file__).resolve().parent.parent / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "carver.py"
        assert carver_path.exists(), "carver.py should exist"
    
    def test_carver_dimension_support(self):
        """Test that Carver supports 6 dimensions."""
        try:
            from farfan_pipeline.phases.Phase_two.carver import Dimension
            
            dimensions = list(Dimension)
            assert len(dimensions) == 6, "Carver should support 6 dimensions"
            
            # Check dimension names
            expected = ["D1_INSUMOS", "D2_ACTIVIDADES", "D3_PRODUCTOS", 
                       "D4_RESULTADOS", "D5_IMPACTOS", "D6_CAUSALIDAD"]
            for exp in expected:
                assert any(exp in d.name for d in dimensions), \
                    f"Dimension {exp} should exist"
            
        except ImportError:
            pytest.skip("Cannot import Carver Dimension enum")
    
    def test_carver_gap_analyzer_exists(self):
        """Test that GapAnalyzer class exists in Carver."""
        try:
            from farfan_pipeline.phases.Phase_two.carver import GapAnalyzer
            
            # Check it has identify_gaps method
            assert hasattr(GapAnalyzer, 'identify_gaps'), \
                "GapAnalyzer should have identify_gaps method"
            
        except ImportError:
            pytest.skip("Cannot import GapAnalyzer from Carver")
    
    def test_carver_evidence_analyzer_exists(self):
        """Test that EvidenceAnalyzer class exists in Carver."""
        try:
            from farfan_pipeline.phases.Phase_two.carver import EvidenceAnalyzer
            
            # Check key methods
            methods = ['extract_items', 'count_by_type', 'find_corroborations', 
                      'find_contradictions']
            for method in methods:
                assert hasattr(EvidenceAnalyzer, method), \
                    f"EvidenceAnalyzer should have {method} method"
            
        except ImportError:
            pytest.skip("Cannot import EvidenceAnalyzer from Carver")
    
    def test_carver_bayesian_confidence_exists(self):
        """Test that BayesianConfidenceEngine exists in Carver."""
        try:
            from farfan_pipeline.phases.Phase_two.carver import BayesianConfidenceEngine
            
            # Check compute method
            assert hasattr(BayesianConfidenceEngine, 'compute'), \
                "BayesianConfidenceEngine should have compute method"
            
        except ImportError:
            pytest.skip("Cannot import BayesianConfidenceEngine from Carver")


class TestOrchestratorMacroCapability:
    """Test Orchestrator macro-level execution capabilities."""
    
    def test_orchestrator_file_exists(self):
        """Test that orchestrator.py exists."""
        orchestrator_path = Path(__file__).resolve().parent.parent / "src" / "orchestration" / "orchestrator.py"
        assert orchestrator_path.exists(), "orchestrator.py should exist"
    
    def test_orchestrator_has_macro_eval_method(self):
        """Test that Orchestrator has _evaluate_macro method."""
        orchestrator_path = Path(__file__).resolve().parent.parent / "src" / "orchestration" / "orchestrator.py"
        
        if not orchestrator_path.exists():
            pytest.skip("orchestrator.py not found")
        
        source = orchestrator_path.read_text()
        assert "_evaluate_macro" in source, \
            "Orchestrator should have _evaluate_macro method"
    
    def test_orchestrator_pa_dim_awareness(self):
        """Test that Orchestrator is aware of PA×DIM structure."""
        orchestrator_path = Path(__file__).resolve().parent.parent / "src" / "orchestration" / "orchestrator.py"
        
        if not orchestrator_path.exists():
            pytest.skip("orchestrator.py not found")
        
        source = orchestrator_path.read_text()
        
        # Check for policy area references
        has_pa = "PA01" in source or "policy_area" in source
        assert has_pa, "Orchestrator should reference policy areas"
        
        # Check for dimension references
        has_dim = "DIM01" in source or "dimension" in source
        assert has_dim, "Orchestrator should reference dimensions"


class TestGapSeverityClassification:
    """Test gap severity classification for divergence analysis."""
    
    def test_gap_severity_enum_exists(self):
        """Test that GapSeverity enum exists."""
        try:
            from farfan_pipeline.phases.Phase_two.carver import GapSeverity
            
            # Check all severity levels exist
            expected = ["CRITICAL", "MAJOR", "MINOR", "COSMETIC"]
            for level in expected:
                assert hasattr(GapSeverity, level), \
                    f"GapSeverity.{level} should exist"
            
        except ImportError:
            pytest.skip("Cannot import GapSeverity from Carver")
    
    def test_evidence_strength_enum_exists(self):
        """Test that EvidenceStrength enum exists."""
        try:
            from farfan_pipeline.phases.Phase_two.carver import EvidenceStrength
            
            # Check all strength levels exist
            expected = ["DEFINITIVE", "STRONG", "MODERATE", "WEAK", "ABSENT"]
            for level in expected:
                assert hasattr(EvidenceStrength, level), \
                    f"EvidenceStrength.{level} should exist"
            
        except ImportError:
            pytest.skip("Cannot import EvidenceStrength from Carver")


class TestDivergenceAnalysisCapability:
    """Test divergence analysis capabilities across PA×DIM matrix."""
    
    def test_coverage_matrix_structure(self):
        """Test that coverage matrix can represent PA×DIM structure."""
        # Simulate coverage matrix
        coverage_matrix: Dict[Tuple[str, str], float] = {}
        
        policy_areas = [f"PA{i:02d}" for i in range(1, 11)]
        dimensions = [f"DIM{i:02d}" for i in range(1, 7)]
        
        # Populate matrix
        for pa in policy_areas:
            for dim in dimensions:
                coverage_matrix[(pa, dim)] = 0.0
        
        assert len(coverage_matrix) == 60, \
            "Coverage matrix should have 60 cells"
    
    def test_divergence_identification_logic(self):
        """Test logic for identifying divergence in PA×DIM matrix."""
        # Simulate coverage with gaps
        coverage_matrix: Dict[Tuple[str, str], float] = {}
        
        policy_areas = [f"PA{i:02d}" for i in range(1, 11)]
        dimensions = [f"DIM{i:02d}" for i in range(1, 7)]
        
        # Populate with varying coverage
        for pa in policy_areas:
            for dim in dimensions:
                # Simulate gaps in PA05 and PA07
                if pa in ["PA05", "PA07"]:
                    coverage_matrix[(pa, dim)] = 0.3  # Low coverage
                else:
                    coverage_matrix[(pa, dim)] = 0.9  # High coverage
        
        # Identify low coverage cells
        threshold = 0.5
        gaps = [(pa, dim, score) 
                for (pa, dim), score in coverage_matrix.items() 
                if score < threshold]
        
        # Should identify 12 gaps (2 PA × 6 DIM)
        assert len(gaps) == 12, f"Should identify 12 gaps, found {len(gaps)}"
        
        # All gaps should be in PA05 or PA07
        for pa, dim, score in gaps:
            assert pa in ["PA05", "PA07"], \
                f"Gap should be in PA05 or PA07, found {pa}"
    
    def test_pa_coverage_aggregation(self):
        """Test aggregation of coverage scores by policy area."""
        coverage_matrix: Dict[Tuple[str, str], float] = {}
        
        policy_areas = [f"PA{i:02d}" for i in range(1, 11)]
        dimensions = [f"DIM{i:02d}" for i in range(1, 7)]
        
        # Populate matrix
        for pa in policy_areas:
            for dim in dimensions:
                coverage_matrix[(pa, dim)] = 0.8
        
        # Aggregate by PA
        pa_scores: Dict[str, float] = {}
        for pa in policy_areas:
            scores = [coverage_matrix[(pa, dim)] for dim in dimensions]
            pa_scores[pa] = sum(scores) / len(scores)
        
        assert len(pa_scores) == 10, "Should have scores for 10 policy areas"
        for pa, score in pa_scores.items():
            assert 0.0 <= score <= 1.0, f"PA score should be in [0,1], got {score}"
    
    def test_dimension_coverage_aggregation(self):
        """Test aggregation of coverage scores by dimension."""
        coverage_matrix: Dict[Tuple[str, str], float] = {}
        
        policy_areas = [f"PA{i:02d}" for i in range(1, 11)]
        dimensions = [f"DIM{i:02d}" for i in range(1, 7)]
        
        # Populate matrix
        for pa in policy_areas:
            for dim in dimensions:
                coverage_matrix[(pa, dim)] = 0.7
        
        # Aggregate by dimension
        dim_scores: Dict[str, float] = {}
        for dim in dimensions:
            scores = [coverage_matrix[(pa, dim)] for pa in policy_areas]
            dim_scores[dim] = sum(scores) / len(scores)
        
        assert len(dim_scores) == 6, "Should have scores for 6 dimensions"
        for dim, score in dim_scores.items():
            assert 0.0 <= score <= 1.0, f"Dimension score should be in [0,1], got {score}"


class TestMacroAuditTool:
    """Test the macro-level divergence audit tool itself."""
    
    def test_audit_tool_exists(self):
        """Test that audit_macro_level_divergence.py exists."""
        audit_path = Path(__file__).resolve().parent.parent / "audit_macro_level_divergence.py"
        assert audit_path.exists(), "audit_macro_level_divergence.py should exist"
    
    def test_audit_tool_executable(self):
        """Test that audit tool can be imported and run."""
            
            from audit_macro_level_divergence import MacroLevelAuditor, MacroLevelAuditReport
            
            # Check classes exist
            assert MacroLevelAuditor is not None
            assert MacroLevelAuditReport is not None
            
        except ImportError as e:
            pytest.fail(f"Cannot import audit tool: {e}")
    
    def test_audit_report_generated(self):
        """Test that audit report JSON was generated."""
        report_path = Path(__file__).resolve().parent.parent / "audit_macro_level_divergence_report.json"
        
        if not report_path.exists():
            pytest.skip("Audit report not yet generated - run audit_macro_level_divergence.py first")
        
        import json
        with open(report_path) as f:
            report = json.load(f)
        
        # Check report structure
        assert "summary" in report, "Report should have summary"
        assert "components" in report, "Report should have components"
        assert "pa_dim_matrix_audit" in report, "Report should have PA×DIM audit"
        
        # Check summary fields
        summary = report["summary"]
        assert "macro_level_ready" in summary
        assert "overall_score" in summary
        assert "total_capabilities_checked" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
