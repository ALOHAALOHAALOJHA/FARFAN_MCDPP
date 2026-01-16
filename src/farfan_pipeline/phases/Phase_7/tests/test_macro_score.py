"""
Unit tests for MacroScore data model.

Tests MacroScore initialization, validation, and serialization.
"""

import pytest
from dataclasses import FrozenInstanceError


def test_macro_score_imports():
    """Test that MacroScore can be imported."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    assert MacroScore is not None


def test_macro_score_creation():
    """Test MacroScore creation with valid data."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    macro_score = MacroScore(
        evaluation_id="TEST_001",
        score=2.5,
        score_normalized=0.833,
        quality_level="BUENO",
        cross_cutting_coherence=0.90,
        strategic_alignment=0.85,
    )
    
    assert macro_score.evaluation_id == "TEST_001"
    assert macro_score.score == 2.5
    assert macro_score.score_normalized == 0.833
    assert macro_score.quality_level == "BUENO"
    assert macro_score.cross_cutting_coherence == 0.90
    assert macro_score.strategic_alignment == 0.85


def test_macro_score_validation_score_bounds():
    """Test MacroScore score bounds validation."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    # Test score below minimum
    with pytest.raises(ValueError, match="score must be in"):
        MacroScore(
            evaluation_id="TEST_002",
            score=-0.5,  # Invalid: below 0.0
            score_normalized=0.5,
            quality_level="BUENO",
            cross_cutting_coherence=0.9,
        )
    
    # Test score above maximum
    with pytest.raises(ValueError, match="score must be in"):
        MacroScore(
            evaluation_id="TEST_003",
            score=3.5,  # Invalid: above 3.0
            score_normalized=0.5,
            quality_level="BUENO",
            cross_cutting_coherence=0.9,
        )


def test_macro_score_validation_normalized_bounds():
    """Test MacroScore normalized score bounds validation."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    with pytest.raises(ValueError, match="score_normalized must be in"):
        MacroScore(
            evaluation_id="TEST_004",
            score=2.5,
            score_normalized=1.5,  # Invalid: above 1.0
            quality_level="BUENO",
            cross_cutting_coherence=0.9,
        )


def test_macro_score_validation_coherence_bounds():
    """Test MacroScore coherence bounds validation."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    with pytest.raises(ValueError, match="cross_cutting_coherence must be in"):
        MacroScore(
            evaluation_id="TEST_005",
            score=2.5,
            score_normalized=0.833,
            quality_level="BUENO",
            cross_cutting_coherence=1.5,  # Invalid: above 1.0
        )


def test_macro_score_validation_alignment_bounds():
    """Test MacroScore alignment bounds validation."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    with pytest.raises(ValueError, match="strategic_alignment must be in"):
        MacroScore(
            evaluation_id="TEST_006",
            score=2.5,
            score_normalized=0.833,
            quality_level="BUENO",
            cross_cutting_coherence=0.9,
            strategic_alignment=-0.1,  # Invalid: below 0.0
        )


def test_macro_score_validation_quality_level():
    """Test MacroScore quality level validation."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    with pytest.raises(ValueError, match="quality_level must be one of"):
        MacroScore(
            evaluation_id="TEST_007",
            score=2.5,
            score_normalized=0.833,
            quality_level="INVALID",  # Invalid quality level
            cross_cutting_coherence=0.9,
        )


def test_macro_score_to_dict():
    """Test MacroScore serialization to dictionary."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    macro_score = MacroScore(
        evaluation_id="TEST_008",
        score=2.5,
        score_normalized=0.833,
        quality_level="BUENO",
        cross_cutting_coherence=0.90,
        strategic_alignment=0.85,
    )
    
    result = macro_score.to_dict()
    
    assert isinstance(result, dict)
    assert result["evaluation_id"] == "TEST_008"
    assert result["score"] == 2.5
    assert result["quality_level"] == "BUENO"
    assert result["cross_cutting_coherence"] == 0.90


def test_macro_score_timestamp_auto_generation():
    """Test that evaluation_timestamp is auto-generated if not provided."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    macro_score = MacroScore(
        evaluation_id="TEST_009",
        score=2.5,
        score_normalized=0.833,
        quality_level="BUENO",
        cross_cutting_coherence=0.90,
    )
    
    assert macro_score.evaluation_timestamp != ""
    # Check for ISO 8601 timestamp (either Z suffix or timezone offset)
    assert ("Z" in macro_score.evaluation_timestamp or 
            "+00:00" in macro_score.evaluation_timestamp or
            "T" in macro_score.evaluation_timestamp)


def test_macro_score_with_all_fields():
    """Test MacroScore with all fields populated."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    macro_score = MacroScore(
        evaluation_id="TEST_010",
        score=2.5,
        score_normalized=0.833,
        quality_level="BUENO",
        cross_cutting_coherence=0.90,
        coherence_breakdown={"strategic": 0.95, "operational": 0.88},
        systemic_gaps=["PA01", "PA05"],
        gap_severity={"PA01": "MODERATE", "PA05": "SEVERE"},
        strategic_alignment=0.85,
        alignment_breakdown={"vertical": 0.90, "horizontal": 0.85},
        cluster_scores=[],
        cluster_details={"CLUSTER_MESO_1": {"score": 2.6}},
        validation_passed=True,
        validation_details={"all_checks": "passed"},
        score_std=0.15,
        confidence_interval_95=(2.2, 2.8),
        provenance_node_id="PROV_123",
        aggregation_method="weighted_average",
        evaluation_timestamp="2026-01-13T00:00:00Z",
        pipeline_version="1.0.0",
    )
    
    assert macro_score.evaluation_id == "TEST_010"
    assert len(macro_score.systemic_gaps) == 2
    assert macro_score.provenance_node_id == "PROV_123"
