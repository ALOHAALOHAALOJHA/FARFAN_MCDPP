"""
Tests for Aggregation Validation Module (Phases 4-7)

Tests validation logic that ensures:
- No empty results at any phase
- Traceability from macro down to micro questions
- Valid score ranges
- Non-zero macro score for valid inputs
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from canonic_phases.phase_4_7_aggregation_pipeline.aggregation import (
    DimensionScore,
    AreaScore,
    ClusterScore,
    MacroScore,
    ScoredResult,
)
from canonic_phases.phase_4_7_aggregation_pipeline.aggregation_validation import (
    validate_phase4_output,
    validate_phase5_output,
    validate_phase6_output,
    validate_phase7_output,
    validate_full_aggregation_pipeline,
    AggregationValidationError,
    enforce_validation_or_fail,
)


class TestPhase4Validation:
    """Test Phase 4 (Dimension Aggregation) validation."""
    
    def test_empty_dimension_scores_fails(self):
        """Empty dimension scores should fail validation."""
        scored_results = [
            ScoredResult(
                question_global="Q001",
                base_slot="DIM01-Q001",
                policy_area="PA01",
                dimension="DIM01",
                score=2.0,
                quality_level="ACEPTABLE",
                evidence={},
                raw_results={}
            )
        ]
        
        result = validate_phase4_output([], scored_results)
        
        assert not result.passed
        assert "EMPTY" in result.error_message
        assert result.phase == "Phase 4 (Dimension Aggregation)"
    
    def test_non_traceable_dimension_scores_fails(self):
        """Dimension scores without contributing questions should fail."""
        dimension_scores = [
            DimensionScore(
                dimension_id="DIM01",
                area_id="PA01",
                score=2.0,
                quality_level="ACEPTABLE",
                contributing_questions=[],  # Empty - not traceable!
                validation_passed=True,
                validation_details={}
            )
        ]
        
        result = validate_phase4_output(dimension_scores, [])
        
        assert not result.passed
        assert "not traceable" in result.error_message.lower()
    
    def test_invalid_score_range_fails(self):
        """Dimension scores outside [0, 3] should fail."""
        dimension_scores = [
            DimensionScore(
                dimension_id="DIM01",
                area_id="PA01",
                score=5.0,  # Invalid - too high!
                quality_level="ACEPTABLE",
                contributing_questions=["Q001", "Q002"],
                validation_passed=True,
                validation_details={}
            )
        ]
        
        result = validate_phase4_output(dimension_scores, [])
        
        assert not result.passed
        assert "outside [0, 3]" in result.error_message
    
    def test_valid_dimension_scores_passes(self):
        """Valid dimension scores should pass validation."""
        dimension_scores = [
            DimensionScore(
                dimension_id="DIM01",
                area_id="PA01",
                score=2.0,
                quality_level="ACEPTABLE",
                contributing_questions=["Q001", "Q002", "Q003"],
                validation_passed=True,
                validation_details={}
            )
        ]
        
        scored_results = [
            ScoredResult(
                question_global=f"Q{i:03d}",
                base_slot=f"DIM01-Q{i:03d}",
                policy_area="PA01",
                dimension="DIM01",
                score=2.0,
                quality_level="ACEPTABLE",
                evidence={},
                raw_results={}
            )
            for i in range(1, 4)
        ]
        
        result = validate_phase4_output(dimension_scores, scored_results)
        
        assert result.passed
        assert result.details["traceable"]


class TestPhase5Validation:
    """Test Phase 5 (Area Policy Aggregation) validation."""
    
    def test_empty_area_scores_fails(self):
        """Empty area scores should fail validation."""
        dimension_scores = [
            DimensionScore(
                dimension_id="DIM01",
                area_id="PA01",
                score=2.0,
                quality_level="ACEPTABLE",
                contributing_questions=["Q001"],
                validation_passed=True,
                validation_details={}
            )
        ]
        
        result = validate_phase5_output([], dimension_scores)
        
        assert not result.passed
        assert "EMPTY" in result.error_message
    
    def test_non_traceable_area_scores_fails(self):
        """Area scores without dimension scores should fail."""
        area_scores = [
            AreaScore(
                area_id="PA01",
                area_name="Area 1",
                score=2.0,
                quality_level="ACEPTABLE",
                dimension_scores=[],  # Empty - not traceable!
                validation_passed=True,
                validation_details={}
            )
        ]
        
        result = validate_phase5_output(area_scores, [])
        
        assert not result.passed
        assert "not traceable" in result.error_message.lower()
    
    def test_valid_area_scores_passes(self):
        """Valid area scores should pass validation."""
        dimension_score = DimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="ACEPTABLE",
            contributing_questions=["Q001"],
            validation_passed=True,
            validation_details={}
        )
        
        area_scores = [
            AreaScore(
                area_id="PA01",
                area_name="Area 1",
                score=2.0,
                quality_level="ACEPTABLE",
                dimension_scores=[dimension_score],
                validation_passed=True,
                validation_details={}
            )
        ]
        
        result = validate_phase5_output(area_scores, [dimension_score])
        
        assert result.passed
        assert result.details["traceable"]


class TestPhase6Validation:
    """Test Phase 6 (Cluster Aggregation) validation."""
    
    def test_empty_cluster_scores_fails(self):
        """Empty cluster scores should fail validation."""
        area_score = AreaScore(
            area_id="PA01",
            area_name="Area 1",
            score=2.0,
            quality_level="ACEPTABLE",
            dimension_scores=[],
            validation_passed=True,
            validation_details={}
        )
        
        result = validate_phase6_output([], [area_score])
        
        assert not result.passed
        assert "EMPTY" in result.error_message
    
    def test_valid_cluster_scores_passes(self):
        """Valid cluster scores should pass validation."""
        area_score = AreaScore(
            area_id="PA01",
            area_name="Area 1",
            score=2.0,
            quality_level="ACEPTABLE",
            dimension_scores=[],
            validation_passed=True,
            validation_details={}
        )
        
        cluster_scores = [
            ClusterScore(
                cluster_id="CL01",
                cluster_name="Cluster 1",
                areas=["PA01"],
                score=2.0,
                coherence=0.9,
                variance=0.1,
                weakest_area="PA01",
                area_scores=[area_score],
                validation_passed=True,
                validation_details={}
            )
        ]
        
        result = validate_phase6_output(cluster_scores, [area_score])
        
        assert result.passed
        assert result.details["traceable"]


class TestPhase7Validation:
    """Test Phase 7 (Macro Evaluation) validation."""
    
    def test_zero_macro_score_with_valid_inputs_fails(self):
        """Zero macro score with valid non-zero inputs should fail."""
        area_score = AreaScore(
            area_id="PA01",
            area_name="Area 1",
            score=2.0,
            quality_level="ACEPTABLE",
            dimension_scores=[],
            validation_passed=True,
            validation_details={}
        )
        
        dimension_score = DimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="ACEPTABLE",
            contributing_questions=["Q001"],
            validation_passed=True,
            validation_details={}
        )
        
        cluster_score = ClusterScore(
            cluster_id="CL01",
            cluster_name="Cluster 1",
            areas=["PA01"],
            score=2.0,  # Non-zero input
            coherence=0.9,
            variance=0.1,
            weakest_area="PA01",
            area_scores=[area_score],
            validation_passed=True,
            validation_details={}
        )
        
        macro_score = MacroScore(
            score=0.0,  # Zero - problematic!
            quality_level="INSUFICIENTE",
            cross_cutting_coherence=0.5,
            systemic_gaps=[],
            strategic_alignment=0.5,
            cluster_scores=[cluster_score],
            validation_passed=True,
            validation_details={}
        )
        
        result = validate_phase7_output(
            macro_score, [cluster_score], [area_score], [dimension_score]
        )
        
        assert not result.passed
        assert "ZERO" in result.error_message
        assert "valid non-zero inputs" in result.error_message
    
    def test_non_traceable_macro_score_fails(self):
        """Macro score without cluster scores should fail."""
        macro_score = MacroScore(
            score=2.0,
            quality_level="ACEPTABLE",
            cross_cutting_coherence=0.5,
            systemic_gaps=[],
            strategic_alignment=0.5,
            cluster_scores=[],  # Empty - not traceable!
            validation_passed=True,
            validation_details={}
        )
        
        result = validate_phase7_output(macro_score, [], [], [])
        
        assert not result.passed
        assert "not traceable" in result.error_message.lower()
    
    def test_invalid_coherence_range_fails(self):
        """Coherence outside [0, 1] should fail."""
        cluster_score = ClusterScore(
            cluster_id="CL01",
            cluster_name="Cluster 1",
            areas=["PA01"],
            score=2.0,
            coherence=0.9,
            variance=0.1,
            weakest_area="PA01",
            area_scores=[],
            validation_passed=True,
            validation_details={}
        )
        
        macro_score = MacroScore(
            score=2.0,
            quality_level="ACEPTABLE",
            cross_cutting_coherence=1.5,  # Invalid - too high!
            systemic_gaps=[],
            strategic_alignment=0.5,
            cluster_scores=[cluster_score],
            validation_passed=True,
            validation_details={}
        )
        
        result = validate_phase7_output(macro_score, [cluster_score], [], [])
        
        assert not result.passed
        assert "outside [0, 1]" in result.error_message
    
    def test_valid_macro_score_passes(self):
        """Valid macro score should pass validation."""
        cluster_score = ClusterScore(
            cluster_id="CL01",
            cluster_name="Cluster 1",
            areas=["PA01"],
            score=2.0,
            coherence=0.9,
            variance=0.1,
            weakest_area="PA01",
            area_scores=[],
            validation_passed=True,
            validation_details={}
        )
        
        macro_score = MacroScore(
            score=2.0,
            quality_level="ACEPTABLE",
            cross_cutting_coherence=0.8,
            systemic_gaps=[],
            strategic_alignment=0.7,
            cluster_scores=[cluster_score],
            validation_passed=True,
            validation_details={}
        )
        
        result = validate_phase7_output(
            macro_score, [cluster_score], [], []
        )
        
        assert result.passed
        assert result.details["traceable"]


class TestFullPipelineValidation:
    """Test full pipeline validation."""
    
    def test_enforce_validation_raises_on_failure(self):
        """enforce_validation_or_fail should raise on failures."""
        from canonic_phases.phase_4_7_aggregation_pipeline.aggregation_validation import ValidationResult
        
        failed_result = ValidationResult(
            passed=False,
            phase="Phase 4",
            error_message="Test failure",
            details={}
        )
        
        with pytest.raises(AggregationValidationError):
            enforce_validation_or_fail([failed_result], allow_failure=False)
    
    def test_enforce_validation_allows_failure_when_requested(self):
        """enforce_validation_or_fail should not raise when allow_failure=True."""
        from canonic_phases.phase_4_7_aggregation_pipeline.aggregation_validation import ValidationResult
        
        failed_result = ValidationResult(
            passed=False,
            phase="Phase 4",
            error_message="Test failure",
            details={}
        )
        
        # Should not raise
        enforce_validation_or_fail([failed_result], allow_failure=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
