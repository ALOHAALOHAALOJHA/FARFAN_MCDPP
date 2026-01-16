"""
Unit tests for MacroAggregator.

Tests aggregation logic, coherence analysis, gap detection, and alignment scoring.
Uses real ClusterScore and AreaScore dataclasses from Phase 5 and 6.
"""

from farfan_pipeline.phases.Phase_6.phase6_10_00_cluster_score import ClusterScore
from farfan_pipeline.phases.Phase_5.phase5_10_00_area_score import AreaScore


def create_real_area_scores():
    """Create realistic AreaScore objects for testing."""
    area_scores = []
    
    # PA01 - Mujeres y Género
    area_scores.append(AreaScore(
        area_id="PA01",
        area_name="Mujeres y Género",
        score=2.5,
        quality_level="BUENO",
        dimension_scores=[],  # Simplified for macro testing
        cluster_id="CLUSTER_MESO_1",
        score_std=0.1,
        confidence_interval_95=(2.3, 2.7),
        provenance_node_id="PROV_PA01",
    ))
    
    # PA02 - Víctimas
    area_scores.append(AreaScore(
        area_id="PA02",
        area_name="Víctimas",
        score=2.6,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_1",
        score_std=0.08,
        confidence_interval_95=(2.4, 2.8),
        provenance_node_id="PROV_PA02",
    ))
    
    # PA03 - Étnico
    area_scores.append(AreaScore(
        area_id="PA03",
        area_name="Étnico",
        score=2.4,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_1",
        score_std=0.12,
        confidence_interval_95=(2.2, 2.6),
        provenance_node_id="PROV_PA03",
    ))
    
    # PA04 - Salud
    area_scores.append(AreaScore(
        area_id="PA04",
        area_name="Salud",
        score=2.3,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_2",
        score_std=0.09,
        confidence_interval_95=(2.1, 2.5),
        provenance_node_id="PROV_PA04",
    ))
    
    # PA05 - Educación
    area_scores.append(AreaScore(
        area_id="PA05",
        area_name="Educación",
        score=2.2,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_2",
        score_std=0.11,
        confidence_interval_95=(2.0, 2.4),
        provenance_node_id="PROV_PA05",
    ))
    
    # PA06 - Vivienda
    area_scores.append(AreaScore(
        area_id="PA06",
        area_name="Vivienda",
        score=2.4,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_2",
        score_std=0.10,
        confidence_interval_95=(2.2, 2.6),
        provenance_node_id="PROV_PA06",
    ))
    
    # PA07 - Tierras
    area_scores.append(AreaScore(
        area_id="PA07",
        area_name="Tierras",
        score=2.1,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_3",
        score_std=0.13,
        confidence_interval_95=(1.9, 2.3),
        provenance_node_id="PROV_PA07",
    ))
    
    # PA08 - Infraestructura
    area_scores.append(AreaScore(
        area_id="PA08",
        area_name="Infraestructura",
        score=2.0,
        quality_level="ACEPTABLE",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_3",
        score_std=0.14,
        confidence_interval_95=(1.8, 2.2),
        provenance_node_id="PROV_PA08",
    ))
    
    # PA09 - Seguridad
    area_scores.append(AreaScore(
        area_id="PA09",
        area_name="Seguridad",
        score=2.4,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_4",
        score_std=0.09,
        confidence_interval_95=(2.2, 2.6),
        provenance_node_id="PROV_PA09",
    ))
    
    # PA10 - Reincorporación
    area_scores.append(AreaScore(
        area_id="PA10",
        area_name="Reincorporación",
        score=2.3,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_4",
        score_std=0.10,
        confidence_interval_95=(2.1, 2.5),
        provenance_node_id="PROV_PA10",
    ))
    
    return area_scores


def create_real_cluster_scores():
    """Create realistic ClusterScore objects using real AreaScore data."""
    all_area_scores = create_real_area_scores()
    
    # Group area scores by cluster
    cluster_1_areas = [a for a in all_area_scores if a.cluster_id == "CLUSTER_MESO_1"]
    cluster_2_areas = [a for a in all_area_scores if a.cluster_id == "CLUSTER_MESO_2"]
    cluster_3_areas = [a for a in all_area_scores if a.cluster_id == "CLUSTER_MESO_3"]
    cluster_4_areas = [a for a in all_area_scores if a.cluster_id == "CLUSTER_MESO_4"]
    
    return [
        ClusterScore(
            cluster_id="CLUSTER_MESO_1",
            cluster_name="Enfoque Diferencial y Víctimas",
            areas=["PA01", "PA02", "PA03"],
            score=2.5,
            coherence=0.90,
            variance=0.01,
            weakest_area="PA03",
            area_scores=cluster_1_areas,
            validation_passed=True,
            score_std=0.10,
            confidence_interval_95=(2.3, 2.7),
            provenance_node_id="PROV_CLUSTER_1",
            dispersion_scenario="LOW",
            penalty_applied=0.0,
        ),
        ClusterScore(
            cluster_id="CLUSTER_MESO_2",
            cluster_name="Derechos Sociales",
            areas=["PA04", "PA05", "PA06"],
            score=2.3,
            coherence=0.85,
            variance=0.015,
            weakest_area="PA05",
            area_scores=cluster_2_areas,
            validation_passed=True,
            score_std=0.10,
            confidence_interval_95=(2.1, 2.5),
            provenance_node_id="PROV_CLUSTER_2",
            dispersion_scenario="LOW",
            penalty_applied=0.0,
        ),
        ClusterScore(
            cluster_id="CLUSTER_MESO_3",
            cluster_name="Desarrollo Rural",
            areas=["PA07", "PA08"],
            score=2.1,
            coherence=0.88,
            variance=0.012,
            weakest_area="PA08",
            area_scores=cluster_3_areas,
            validation_passed=True,
            score_std=0.13,
            confidence_interval_95=(1.9, 2.3),
            provenance_node_id="PROV_CLUSTER_3",
            dispersion_scenario="LOW",
            penalty_applied=0.0,
        ),
        ClusterScore(
            cluster_id="CLUSTER_MESO_4",
            cluster_name="Seguridad y Reintegración",
            areas=["PA09", "PA10"],
            score=2.4,
            coherence=0.92,
            variance=0.008,
            weakest_area="PA10",
            area_scores=cluster_4_areas,
            validation_passed=True,
            score_std=0.09,
            confidence_interval_95=(2.2, 2.6),
            provenance_node_id="PROV_CLUSTER_4",
            dispersion_scenario="LOW",
            penalty_applied=0.0,
        ),
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
    
    assert aggregator.cluster_weights == custom_weights


def test_macro_aggregator_aggregation():
    """Test basic aggregation with real cluster scores."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_real_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert macro_score is not None
    assert 0.0 <= macro_score.score <= 3.0
    assert 0.0 <= macro_score.score_normalized <= 1.0
    assert macro_score.quality_level in {"EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"}


def test_macro_aggregator_weighted_score():
    """Test weighted score calculation with real data."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_real_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    # With equal weights (0.25 each), score should be close to average
    expected_avg = (2.5 + 2.3 + 2.1 + 2.4) / 4  # 2.325
    assert abs(macro_score.score - expected_avg) < 0.1


def test_macro_aggregator_validation_count():
    """Test validation of cluster count."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_real_cluster_scores()[:3]  # Only 3 clusters
    
    try:
        aggregator.aggregate(cluster_scores)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "4 ClusterScores" in str(e)  # Updated to match actual error message


def test_macro_aggregator_validation_cluster_ids():
    """Test validation of cluster IDs."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_real_cluster_scores()
    # Duplicate cluster ID
    cluster_scores[3] = ClusterScore(
        cluster_id="CLUSTER_MESO_1",  # Duplicate
        cluster_name="Duplicate",
        areas=["PA09", "PA10"],
        score=2.4,
        coherence=0.92,
        variance=0.008,
        weakest_area="PA10",
        area_scores=[],
    )
    
    try:
        aggregator.aggregate(cluster_scores)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        # Updated to match actual error message format
        assert "mismatch" in str(e).lower() or "duplicate" in str(e).lower()


def test_macro_aggregator_validation_score_bounds():
    """Test validation of score bounds."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_real_cluster_scores()
    
    # Test with invalid score - this will be caught by ClusterScore validation
    try:
        invalid_cluster = ClusterScore(
            cluster_id="CLUSTER_MESO_5",
            cluster_name="Invalid",
            areas=["PA11"],
            score=5.0,  # Invalid score
            coherence=0.9,
            variance=0.1,
            weakest_area="PA11",
            area_scores=[],
        )
        assert False, "ClusterScore should have raised ValueError"
    except ValueError as e:
        assert "score must be in [0.0, 3.0]" in str(e)


def test_macro_aggregator_quality_classification():
    """Test quality level classification."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_real_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    # Based on average ~2.3, should be "BUENO"
    assert macro_score.quality_level == "BUENO"


def test_macro_aggregator_coherence_analysis():
    """Test cross-cutting coherence analysis."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator(enable_coherence_analysis=True)
    cluster_scores = create_real_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert 0.0 <= macro_score.cross_cutting_coherence <= 1.0
    assert "strategic_coherence" in macro_score.coherence_breakdown
    assert "operational_coherence" in macro_score.coherence_breakdown
    assert "institutional_coherence" in macro_score.coherence_breakdown


def test_macro_aggregator_alignment_scoring():
    """Test strategic alignment scoring."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator(enable_alignment_scoring=True)
    cluster_scores = create_real_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert 0.0 <= macro_score.strategic_alignment <= 1.0
    assert "vertical_alignment" in macro_score.alignment_breakdown
    assert "horizontal_alignment" in macro_score.alignment_breakdown
    assert "temporal_alignment" in macro_score.alignment_breakdown


def test_macro_aggregator_gap_detection():
    """Test systemic gap detection using SystemicGapDetector with real data."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator(enable_gap_detection=True)
    
    # Create area scores with one below threshold for gap detection
    area_with_gap = AreaScore(
        area_id="PA01",
        area_name="Mujeres y Género",
        score=1.2,  # Below threshold (1.65 on raw scale = 0.55 normalized)
        quality_level="INSUFICIENTE",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_1",
    )
    area_without_gap = AreaScore(
        area_id="PA04",
        area_name="Salud",
        score=2.3,
        quality_level="BUENO",
        dimension_scores=[],
        cluster_id="CLUSTER_MESO_2",
    )
    
    # Create cluster scores with area_scores included
    gap_scores = [
        ClusterScore(
            cluster_id="CLUSTER_MESO_1",
            cluster_name="Test Cluster 1",
            areas=["PA01", "PA02", "PA03"],
            score=1.5,
            coherence=0.9,
            variance=0.1,
            weakest_area="PA01",
            area_scores=[area_with_gap],
        ),
        ClusterScore(
            cluster_id="CLUSTER_MESO_2",
            cluster_name="Test Cluster 2",
            areas=["PA04", "PA05", "PA06"],
            score=2.3,
            coherence=0.85,
            variance=0.15,
            weakest_area="PA04",
            area_scores=[area_without_gap],
        ),
        ClusterScore(
            cluster_id="CLUSTER_MESO_3",
            cluster_name="Test Cluster 3",
            areas=["PA07", "PA08"],
            score=2.1,
            coherence=0.88,
            variance=0.12,
            weakest_area="PA07",
            area_scores=[],
        ),
        ClusterScore(
            cluster_id="CLUSTER_MESO_4",
            cluster_name="Test Cluster 4",
            areas=["PA09", "PA10"],
            score=2.4,
            coherence=0.92,
            variance=0.08,
            weakest_area="PA09",
            area_scores=[],
        ),
    ]
    
    macro_score = aggregator.aggregate(gap_scores)
    
    # Should detect PA01 as a gap (score 1.2 / 3.0 = 0.4 < 0.55 threshold)
    assert "PA01" in macro_score.systemic_gaps
    assert macro_score.gap_severity["PA01"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def test_macro_aggregator_uncertainty_propagation():
    """Test uncertainty propagation from cluster scores."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_real_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert macro_score.score_std >= 0.0
    assert len(macro_score.confidence_interval_95) == 2
    assert macro_score.confidence_interval_95[0] <= macro_score.confidence_interval_95[1]


def test_macro_aggregator_provenance():
    """Test provenance tracking."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator()
    cluster_scores = create_real_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert macro_score.provenance_node_id != ""
    assert macro_score.provenance_node_id.startswith("PROV_MACRO_")


def test_macro_aggregator_disabled_features():
    """Test with disabled features."""
    from farfan_pipeline.phases.Phase_7.phase7_20_00_macro_aggregator import MacroAggregator
    
    aggregator = MacroAggregator(
        enable_gap_detection=False,
        enable_coherence_analysis=False,
        enable_alignment_scoring=False,
    )
    cluster_scores = create_real_cluster_scores()
    
    macro_score = aggregator.aggregate(cluster_scores)
    
    assert len(macro_score.systemic_gaps) == 0
    assert macro_score.cross_cutting_coherence == 0.0
    assert macro_score.strategic_alignment == 0.0

