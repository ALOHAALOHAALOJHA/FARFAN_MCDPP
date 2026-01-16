"""
Unit tests for MacroAggregator.

Tests aggregation logic, coherence analysis, gap detection, and alignment scoring.
"""

import pytest
from dataclasses import dataclass, field


@dataclass
class MockDimensionScore:
    """Mock DimensionScore for testing."""
    dimension_id: str
    score: float


@dataclass
class MockAreaScore:
    """Mock AreaScore for testing (Phase 5 output)."""
    area_id: str
    area_name: str
    score: float
    quality_level: str
    dimension_scores: list = field(default_factory=list)
    validation_passed: bool = True
    validation_details: dict = field(default_factory=dict)
    cluster_id: str = ""
    score_std: float = 0.1
    confidence_interval_95: tuple = field(default_factory=lambda: (0.0, 3.0))
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"


@dataclass
class MockClusterScore:
    """Mock ClusterScore for testing."""
    cluster_id: str
    score: float
    coherence: float
    variance: float
    weakest_area: str
    dispersion_scenario: str
    penalty_applied: float
    areas: list
    score_std: float = 0.1
    area_scores: list = field(default_factory=list)  # Added for gap detection


def create_mock_cluster_scores():
    """Create 4 mock cluster scores for testing."""
    return [
        MockClusterScore("CLUSTER_MESO_1", 2.5, 0.9, 0.1, "PA01", "LOW", 0.0, ["PA01", "PA02", "PA03"], 0.1, []),
        MockClusterScore("CLUSTER_MESO_2", 2.3, 0.85, 0.15, "PA04", "LOW", 0.0, ["PA04", "PA05", "PA06"], 0.1, []),
        MockClusterScore("CLUSTER_MESO_3", 2.1, 0.88, 0.12, "PA07", "LOW", 0.0, ["PA07", "PA08"], 0.1, []),
        MockClusterScore("CLUSTER_MESO_4", 2.4, 0.92, 0.08, "PA09", "LOW", 0.0, ["PA09", "PA10"], 0.1, []),
    ]


def test_macro_aggregator_imports():
    """Test that MacroAggregator can be imported."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    assert MacroAggregator is not None


def test_macro_aggregator_initialization():
    """Test MacroAggregator initialization."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    
    assert aggregator.enable_gap_detection is True
    assert aggregator.enable_coherence_analysis is True
    assert aggregator.enable_alignment_scoring is True
    assert aggregator.cluster_weights is not None


def test_macro_aggregator_custom_weights():
    """Test MacroAggregator with custom weights."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    custom_weights = {
        "CLUSTER_MESO_1": 0.3,
        "CLUSTER_MESO_2": 0.3,
        "CLUSTER_MESO_3": 0.2,
        "CLUSTER_MESO_4": 0.2,
    }
    
    aggregator = MacroAggregator(cluster_weights=custom_weights)
    
    # Weights should be normalized to sum to 1.0
    weight_sum = sum(aggregator.cluster_weights.values())
    assert abs(weight_sum - 1.0) < 1e-6


def test_macro_aggregator_aggregation():
    """Test basic aggregation functionality."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_mock_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert macro_score is not None
    assert 0.0 <= macro_score.score <= 3.0
    assert 0.0 <= macro_score.score_normalized <= 1.0
    assert macro_score.quality_level in {"EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"}


def test_macro_aggregator_weighted_score():
    """Test weighted score calculation."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_mock_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    # With equal weights (0.25 each), expected score:
    # (2.5 + 2.3 + 2.1 + 2.4) / 4 = 9.3 / 4 = 2.325
    expected_score = 2.325
    assert abs(macro_score.score - expected_score) < 0.01


def test_macro_aggregator_validation_count():
    """Test that aggregator validates input count."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    
    # Test with wrong number of clusters
    with pytest.raises(ValueError, match="Expected 4 ClusterScores"):
        aggregator.aggregate([])
    
    with pytest.raises(ValueError, match="Expected 4 ClusterScores"):
        aggregator.aggregate(create_mock_cluster_scores()[:3])


def test_macro_aggregator_validation_cluster_ids():
    """Test that aggregator validates cluster IDs."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    
    # Create invalid cluster scores with wrong IDs
    invalid_scores = [
        MockClusterScore("CLUSTER_MESO_1", 2.5, 0.9, 0.1, "PA01", "LOW", 0.0, []),
        MockClusterScore("CLUSTER_MESO_2", 2.3, 0.85, 0.15, "PA04", "LOW", 0.0, []),
        MockClusterScore("CLUSTER_MESO_3", 2.1, 0.88, 0.12, "PA07", "LOW", 0.0, []),
        MockClusterScore("INVALID_ID", 2.4, 0.92, 0.08, "PA09", "LOW", 0.0, []),
    ]
    
    with pytest.raises(ValueError, match="Cluster mismatch"):
        aggregator.aggregate(invalid_scores)


def test_macro_aggregator_validation_score_bounds():
    """Test that aggregator validates score bounds."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    
    # Create cluster scores with out-of-bounds score
    invalid_scores = create_mock_cluster_scores()
    invalid_scores[0].score = 5.0  # Invalid: above 3.0
    
    with pytest.raises(ValueError, match="score out of bounds"):
        aggregator.aggregate(invalid_scores)


def test_macro_aggregator_quality_classification():
    """Test quality level classification."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    
    # Test EXCELENTE (>= 2.55)
    excellent_scores = [
        MockClusterScore("CLUSTER_MESO_1", 2.7, 0.9, 0.1, "PA01", "LOW", 0.0, []),
        MockClusterScore("CLUSTER_MESO_2", 2.6, 0.85, 0.15, "PA04", "LOW", 0.0, []),
        MockClusterScore("CLUSTER_MESO_3", 2.8, 0.88, 0.12, "PA07", "LOW", 0.0, []),
        MockClusterScore("CLUSTER_MESO_4", 2.5, 0.92, 0.08, "PA09", "LOW", 0.0, []),
    ]
    macro_score = aggregator.aggregate(excellent_scores)
    assert macro_score.quality_level == "EXCELENTE"
    
    # Test BUENO (>= 2.10, < 2.55)
    good_scores = create_mock_cluster_scores()  # Average 2.325
    macro_score = aggregator.aggregate(good_scores)
    assert macro_score.quality_level == "BUENO"


def test_macro_aggregator_coherence_analysis():
    """Test cross-cutting coherence analysis."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator(enable_coherence_analysis=True)
    cluster_scores = create_mock_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert 0.0 <= macro_score.cross_cutting_coherence <= 1.0
    assert "strategic_coherence" in macro_score.coherence_breakdown
    assert "operational_coherence" in macro_score.coherence_breakdown
    assert "institutional_coherence" in macro_score.coherence_breakdown


def test_macro_aggregator_alignment_scoring():
    """Test strategic alignment scoring."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator(enable_alignment_scoring=True)
    cluster_scores = create_mock_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert 0.0 <= macro_score.strategic_alignment <= 1.0
    assert "vertical_alignment" in macro_score.alignment_breakdown
    assert "horizontal_alignment" in macro_score.alignment_breakdown
    assert "temporal_alignment" in macro_score.alignment_breakdown


def test_macro_aggregator_gap_detection():
    """Test systemic gap detection using SystemicGapDetector."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator(enable_gap_detection=True)
    
    # Create area scores with some below threshold (0.55 on normalized scale = 1.65 on raw scale)
    area_with_gap = MockAreaScore(
        area_id="PA01",
        area_name="Mujeres y Género",
        score=1.2,  # Below 1.65 threshold
        quality_level="INSUFICIENTE"
    )
    area_without_gap = MockAreaScore(
        area_id="PA04",
        area_name="Educación",
        score=2.3,  # Above threshold
        quality_level="BUENO"
    )
    
    # Create cluster scores with area_scores included
    gap_scores = [
        MockClusterScore(
            "CLUSTER_MESO_1", 1.5, 0.9, 0.1, "PA01", "LOW", 0.0, 
            ["PA01", "PA02", "PA03"], 0.1,
            [area_with_gap]  # Include area scores for gap detection
        ),
        MockClusterScore(
            "CLUSTER_MESO_2", 2.3, 0.85, 0.15, "PA04", "LOW", 0.0,
            ["PA04", "PA05", "PA06"], 0.1,
            [area_without_gap]
        ),
        MockClusterScore(
            "CLUSTER_MESO_3", 2.1, 0.88, 0.12, "PA07", "LOW", 0.0,
            ["PA07", "PA08"], 0.1, []
        ),
        MockClusterScore(
            "CLUSTER_MESO_4", 2.4, 0.92, 0.08, "PA09", "LOW", 0.0,
            ["PA09", "PA10"], 0.1, []
        ),
    ]
    
    macro_score = aggregator.aggregate(gap_scores)
    
    # Should detect PA01 as a gap (score 1.2 / 3.0 = 0.4 < 0.55 threshold)
    assert "PA01" in macro_score.systemic_gaps
    # Gap severity should use priority from SystemicGapDetector (CRITICAL/HIGH/MEDIUM/LOW)
    assert macro_score.gap_severity["PA01"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def test_macro_aggregator_uncertainty_propagation():
    """Test uncertainty propagation from cluster scores."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_mock_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert macro_score.score_std >= 0.0
    assert len(macro_score.confidence_interval_95) == 2
    assert macro_score.confidence_interval_95[0] <= macro_score.score <= macro_score.confidence_interval_95[1]


def test_macro_aggregator_provenance():
    """Test provenance tracking."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_mock_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert macro_score.evaluation_id != ""
    assert macro_score.provenance_node_id != ""
    assert macro_score.aggregation_method == "weighted_average"
    assert macro_score.evaluation_timestamp != ""
    assert len(macro_score.cluster_scores) == 4


def test_macro_aggregator_disabled_features():
    """Test aggregator with disabled features."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator(
        enable_gap_detection=False,
        enable_coherence_analysis=False,
        enable_alignment_scoring=False,
    )
    
    cluster_scores = create_mock_cluster_scores()
    macro_score = aggregator.aggregate(cluster_scores)
    
    # Should still produce valid macro score
    assert macro_score.score > 0
    assert macro_score.cross_cutting_coherence == 0.0
    assert macro_score.strategic_alignment == 0.0
    assert len(macro_score.systemic_gaps) == 0
