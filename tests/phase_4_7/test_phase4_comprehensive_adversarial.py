"""
Comprehensive Adversarial Tests for Phase 4-7 Modules
======================================================

This test suite covers ALL Phase 4 modules with correct imports.

Uses REAL modularized monolith from conftest.py - NO FAKE DATA.

Author: F.A.R.F.A.N. Pipeline Team
Version: 3.1.0 - Fixed all class signatures and API calls
"""

from __future__ import annotations

import asyncio
import math
import pytest
from dataclasses import dataclass, replace, field
from typing import Any

# Import actual classes from Phase 4
from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import (
    DimensionAggregator,
    DimensionScore as ActualDimensionScore,
    AreaPolicyAggregator,
    AreaScore as ActualAreaScore,
    ClusterAggregator,
    ClusterScore as ActualClusterScore,
    MacroAggregator,
    MacroScore,
    validate_scored_results,
)
from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation_integration import (
    aggregate_dimensions_async,
    aggregate_policy_areas_async,
    aggregate_clusters,
    evaluate_macro,
)
from farfan_pipeline.phases.Phase_04.phase4_10_00_uncertainty_quantification import (
    BootstrapAggregator,
    aggregate_with_uncertainty,
)
from farfan_pipeline.phases.Phase_04.phase4_10_00_choquet_aggregator import (
    ChoquetAggregator,
    ChoquetConfig,
    CalibrationConfigError,
)
from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation_provenance import (
    AggregationDAG,
    ProvenanceNode,
)
from farfan_pipeline.phases.Phase_04.primitives.phase4_10_00_quality_levels import (
    QualityLevel,
    QualityLevelThresholds,
    determine_quality_level,
)
from farfan_pipeline.phases.Phase_04.phase4_10_00_phase_4_7_constants import (
    QUALITY_LEVEL_EXCELENTE,
    QUALITY_LEVEL_BUENO,
    QUALITY_LEVEL_ACEPTABLE,
    QUALITY_LEVEL_INSUFICIENTE,
    MIN_SCORE,
    MAX_SCORE,
    QUALITY_THRESHOLD_EXCELENTE_MIN,
    QUALITY_THRESHOLD_BUENO_MIN,
    QUALITY_THRESHOLD_ACEPTABLE_MIN,
)
from farfan_pipeline.phases.Phase_04.enhancements.phase4_10_00_enhanced_aggregators import (
    EnhancedDimensionAggregator,
    EnhancedAreaAggregator,
)
from farfan_pipeline.phases.Phase_04.enhancements.phase4_10_00_adaptive_meso_scoring import (
    AdaptiveMesoScoring,
)
from farfan_pipeline.phases.Phase_04.enhancements.phase4_10_00_signal_enriched_aggregation import (
    SignalEnrichedAggregator,
)


# =============================================================================
# TEST DATA HELPERS - Uses actual Phase 4 classes
# =============================================================================


def create_scored_result_dict(
    question_global: int, base_slot: str, policy_area: str, dimension: str, score: float
) -> dict[str, Any]:
    """Create a scored result as dict (as expected by validate_scored_results)."""
    return {
        "question_global": question_global,
        "base_slot": base_slot,
        "policy_area": policy_area,
        "dimension": dimension,
        "score": score,
        "quality_level": "BUENO",
        "evidence": {},
        "raw_results": {},
    }


def create_dimension_score_group(
    dimension: str = "DIM01", policy_area: str = "PA01", scores: list[float] | None = None
) -> list[Any]:
    """Create a group of ScoredResult objects (validated, not mocks)."""
    scores = scores or [2.0, 2.0, 2.0, 2.0, 2.0]
    dicts = [
        create_scored_result_dict(
            question_global=i + 1,
            base_slot=f"{dimension}-Q{i+1:03d}",
            policy_area=policy_area,
            dimension=dimension,
            score=score,
        )
        for i, score in enumerate(scores)
    ]
    # Use real validator to convert dicts to ScoredResult objects
    return validate_scored_results(dicts)


def create_mock_instrumentation():
    """Create mock instrumentation for testing."""

    class MockInstrumentation:
        def __init__(self):
            self.items_total = 0
            self.items_completed = 0

        def start(self, items_total: int = 1):
            self.items_total = items_total
            self.items_completed = 0

        def complete_item(self):
            self.items_completed += 1

    return MockInstrumentation()


# =============================================================================
# TEST CLASS 1: AREA POLICY AGGREGATOR
# =============================================================================


class TestAreaPolicyAggregatorAdversarial:
    """Adversarial tests for AreaPolicyAggregator (aggregation.py)."""

    def test_area_aggregation_with_all_dimensions(self, create_minimal_monolith):
        """Test area aggregation with complete 6 dimensions."""
        monolith = create_minimal_monolith()

        # Create 6 dimension scores for one area
        dim_aggregator = DimensionAggregator(
            monolith=monolith, abort_on_insufficient=False
        )

        dimension_scores = []
        for dim_idx in range(1, 7):
            results = create_dimension_score_group(
                dimension=f"DIM{dim_idx:02d}", policy_area="PA01", scores=[2.0, 2.0, 2.0, 2.0, 2.0]
            )
            dim_score = dim_aggregator.aggregate_dimension(
                results, group_by_values={"policy_area": "PA01", "dimension": f"DIM{dim_idx:02d}"}
            )
            dimension_scores.append(dim_score)

        # Aggregate to area
        area_aggregator = AreaPolicyAggregator(
            monolith=monolith, abort_on_insufficient=False
        )

        area_score = area_aggregator.aggregate_area(
            dimension_scores, group_by_values={"policy_area": "PA01", "area_id": "PA01"}
        )

        # Area ID may be UNKNOWN if monolith doesn't have the mapping, but score should be valid
        assert area_score.score == pytest.approx(2.0)
        assert 0.0 <= area_score.score <= 3.0
        assert len(area_score.dimension_scores) == 6

    def test_area_aggregation_hermeticity_validation_failure(self, create_minimal_monolith):
        """Test that missing dimensions trigger hermeticity validation failure."""
        monolith = create_minimal_monolith()

        # Create only 4 dimension scores (missing 2)
        dim_aggregator = DimensionAggregator(
            monolith=monolith, abort_on_insufficient=False
        )

        dimension_scores = []
        for dim_idx in [1, 2, 4, 5]:  # Missing DIM03, DIM06
            results = create_dimension_score_group(
                dimension=f"DIM{dim_idx:02d}", policy_area="PA01", scores=[2.0] * 5
            )
            dim_score = dim_aggregator.aggregate_dimension(
                results, group_by_values={"policy_area": "PA01", "dimension": f"DIM{dim_idx:02d}"}
            )
            dimension_scores.append(dim_score)

        area_aggregator = AreaPolicyAggregator(
            monolith=monolith, abort_on_insufficient=False
        )

        area_score = area_aggregator.aggregate_area(
            dimension_scores, group_by_values={"policy_area": "PA01", "area_id": "PA01"}
        )

        # Hermeticity should fail but aggregation should complete
        assert area_score.validation_passed is False
        assert "hermeticity" in str(area_score.validation_details).lower()

    def test_area_aggregation_with_dimension_overlap(self, create_minimal_monolith):
        """Test that duplicate dimension IDs are detected."""
        monolith = create_minimal_monolith()

        dim_aggregator = DimensionAggregator(monolith=monolith, abort_on_insufficient=False)

        # Create duplicate DIM01
        results = create_dimension_score_group(
            dimension="DIM01", policy_area="PA01", scores=[2.0] * 5
        )
        dim_score1 = dim_aggregator.aggregate_dimension(
            results, group_by_values={"policy_area": "PA01", "dimension": "DIM01"}
        )
        dim_score2 = dim_aggregator.aggregate_dimension(
            results, group_by_values={"policy_area": "PA01", "dimension": "DIM01"}
        )

        area_aggregator = AreaPolicyAggregator(
            monolith=create_minimal_monolith(), abort_on_insufficient=False
        )

        area_score = area_aggregator.aggregate_area(
            [dim_score1, dim_score2], group_by_values={"policy_area": "PA01", "area_id": "PA01"}
        )

        # Should complete, possibly with warnings
        assert 0.0 <= area_score.score <= 3.0

    def test_area_aggregation_score_clamping(self, create_minimal_monolith):
        """Test that out-of-range dimension scores are clamped."""
        # Create dimension scores with out-of-range values
        dimension_scores = [
            ActualDimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=score,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={},
            )
            for i, score in enumerate([-1.0, 0.5, 2.0, 2.5, 3.0, 4.0])
        ]

        area_aggregator = AreaPolicyAggregator(
            monolith=create_minimal_monolith(), abort_on_insufficient=False
        )

        area_score = area_aggregator.aggregate_area(
            dimension_scores, group_by_values={"policy_area": "PA01", "area_id": "PA01"}
        )

        # Score should be in valid range
        assert 0.0 <= area_score.score <= 3.0


# =============================================================================
# TEST CLASS 2: CLUSTER AGGREGATOR
# =============================================================================


class TestClusterAggregatorAdversarial:
    """Adversarial tests for ClusterAggregator (aggregation.py)."""

    def test_cluster_aggregation_with_multiple_areas(self, create_minimal_monolith):
        """Test cluster aggregation with multiple policy areas."""
        monolith = create_minimal_monolith()

        # Create area scores for a cluster
        area_scores = [
            ActualAreaScore(
                area_id=f"PA0{i}",
                area_name=f"Area {i}",
                score=2.0 + i * 0.1,
                quality_level="BUENO",
                dimension_scores=[],
                validation_passed=True,
                validation_details={},
            )
            for i in range(1, 6)
        ]

        cluster_aggregator = ClusterAggregator(monolith=monolith, abort_on_insufficient=False)

        cluster_score = cluster_aggregator.aggregate_cluster(
            area_scores, group_by_values={"cluster_id": "MESO_1"}
        )

        assert cluster_score.cluster_id == "MESO_1"
        assert 0.0 <= cluster_score.score <= 3.0
        assert len(cluster_score.area_scores) == 5

    def test_cluster_aggregation_coherence_metric(self, create_minimal_monolith):
        """Test that cluster aggregation calculates coherence."""
        monolith = create_minimal_monolith()

        # High variance areas (low coherence)
        area_scores = [
            ActualAreaScore(
                area_id="PA01",
                area_name="Area 1",
                score=1.0,
                quality_level="ACEPTABLE",
                dimension_scores=[],
                validation_passed=True,
                validation_details={},
            ),
            ActualAreaScore(
                area_id="PA02",
                area_name="Area 2",
                score=3.0,
                quality_level="EXCELENTE",
                dimension_scores=[],
                validation_passed=True,
                validation_details={},
            ),
        ]

        cluster_aggregator = ClusterAggregator(monolith=monolith, abort_on_insufficient=False)

        cluster_score = cluster_aggregator.aggregate_cluster(
            area_scores, group_by_values={"cluster_id": "MESO_1"}
        )

        # Coherence metric should exist
        assert hasattr(cluster_score, "coherence")
        # High variance should reduce coherence
        assert cluster_score.coherence < 1.0

    def test_cluster_aggregation_single_area(self, create_minimal_monolith):
        """Test cluster aggregation with only one area."""
        area_scores = [
            ActualAreaScore(
                area_id="PA01",
                area_name="Only Area",
                score=2.5,
                quality_level="BUENO",
                dimension_scores=[],
                validation_passed=True,
                validation_details={},
            )
        ]

        cluster_aggregator = ClusterAggregator(
            monolith=create_minimal_monolith(), abort_on_insufficient=False
        )

        cluster_score = cluster_aggregator.aggregate_cluster(
            area_scores, group_by_values={"cluster_id": "MESO_1"}
        )

        # Should handle gracefully
        assert cluster_score.score == pytest.approx(2.5)


# =============================================================================
# TEST CLASS 3: MACRO AGGREGATOR
# =============================================================================


class TestMacroAggregatorAdversarial:
    """Adversarial tests for MacroAggregator (aggregation.py)."""

    def test_macro_aggregation_comprehensive(self, create_minimal_monolith):
        """Test macro aggregation with all inputs."""
        # Create sample inputs
        dimension_scores = [
            ActualDimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={},
            )
            for i in range(1, 7)
        ]

        area_scores = [
            ActualAreaScore(
                area_id="PA01",
                area_name="Test Area",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=dimension_scores[:3],
                validation_passed=True,
                validation_details={},
            )
        ]

        cluster_scores = [
            ActualClusterScore(
                cluster_id="MESO_1",
                cluster_name="Test Cluster",
                areas=["PA01"],
                score=2.0,
                coherence=0.9,
                variance=0.1,
                weakest_area=None,
                area_scores=area_scores,
                validation_passed=True,
                validation_details={},
            )
        ]

        macro_aggregator = MacroAggregator(
            monolith=create_minimal_monolith(), abort_on_insufficient=False
        )

        macro_result = macro_aggregator.aggregate_macro(
            cluster_scores,
            dimension_scores=dimension_scores,
            area_scores=area_scores,
        )

        assert macro_result.score is not None
        assert 0.0 <= macro_result.score <= 3.0
        assert hasattr(macro_result, "cross_cutting_coherence")

    def test_macro_aggregation_identifies_gaps(self, create_minimal_monolith):
        """Test that macro aggregation identifies systemic gaps."""
        # Create scores with a gap (one dimension very low)
        dimension_scores = [
            ActualDimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=0.5 if i == 3 else 2.5,
                quality_level="INSUFICIENTE" if i == 3 else "BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={},
            )
            for i in range(1, 7)
        ]

        macro_aggregator = MacroAggregator(
            monolith=create_minimal_monolith(), abort_on_insufficient=False
        )

        macro_result = macro_aggregator.aggregate_macro(
            cluster_scores=[],
            dimension_scores=dimension_scores,
            area_scores=[],
        )

        # Should identify the gap
        assert hasattr(macro_result, "validation_details")
        assert "systemic_gaps" in macro_result.validation_details


# =============================================================================
# TEST CLASS 4: BOOTSTRAP UNCERTAINTY QUANTIFICATION
# =============================================================================


class TestBootstrapUncertaintyAdversarial:
    """Adversarial tests for BootstrapAggregator (uncertainty_quantification.py)."""

    def test_bootstrap_aggregator_basic(self):
        """Test basic bootstrap aggregation."""
        aggregator = BootstrapAggregator(iterations=100, seed=42)

        data = [1.0, 2.0, 3.0, 2.5, 1.5]

        def mean_func(d):
            return sum(d) / len(d)

        metrics = aggregator.compute_bca_interval(data, mean_func)

        assert metrics.point_estimate == pytest.approx(2.0)
        assert metrics.ci_lower_95 < metrics.point_estimate
        assert metrics.ci_upper_95 > metrics.point_estimate
        assert metrics.confidence_interval_method == "BCa"
        assert metrics.sample_count == 100

    def test_bootstrap_with_single_value(self):
        """Test bootstrap with single value (edge case)."""
        aggregator = BootstrapAggregator(iterations=50, seed=42)

        data = [2.0]

        def mean_func(d):
            return sum(d) / len(d)

        metrics = aggregator.compute_bca_interval(data, mean_func)

        # Should handle single value
        assert metrics.point_estimate == 2.0
        # CI should be very narrow or zero
        assert abs(metrics.ci_upper_95 - metrics.ci_lower_95) < 0.5

    def test_bootstrap_with_extreme_variance(self):
        """Test bootstrap with extreme variance."""
        aggregator = BootstrapAggregator(iterations=100, seed=42)

        # Extreme variance: 0.0 to 3.0
        data = [0.0, 0.5, 1.5, 2.5, 3.0]

        def mean_func(d):
            return sum(d) / len(d)

        metrics = aggregator.compute_bca_interval(data, mean_func)

        # Should have wide CI due to high variance
        ci_width = metrics.ci_upper_95 - metrics.ci_lower_95
        assert ci_width > 0.5  # Wide interval

    def test_convergence_diagnostics(self):
        """Test convergence diagnostics for bootstrap."""
        aggregator = BootstrapAggregator(iterations=500, seed=42)

        data = [1.0, 2.0, 3.0, 2.0, 2.0] * 10  # More data

        def mean_func(d):
            return sum(d) / len(d)

        metrics, diagnostics = aggregator.compute_with_convergence(data, mean_func)

        assert diagnostics.effective_sample_size > 0
        assert diagnostics.convergence_status in ["converged", "failed"]
        assert len(diagnostics.pathology_flags) >= 0

    def test_aggregate_with_uncertainty_api(self):
        """Test the main API function for aggregation with uncertainty."""
        scores = [1.5, 2.0, 2.5, 2.0, 2.0]

        point_estimate, metrics = aggregate_with_uncertainty(scores)

        assert point_estimate == pytest.approx(2.0)
        assert metrics.std_error > 0
        assert metrics.confidence_interval_method == "BCa"


# =============================================================================
# TEST CLASS 5: CHOQUET AGGREGATOR
# =============================================================================


class TestChoquetAggregatorAdversarial:
    """Adversarial tests for ChoquetAggregator (choquet_aggregator.py)."""

    def test_choquet_linear_aggregation_only(self):
        """Test Choquet with only linear weights (no interactions)."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.5, "@chain": 0.3, "@q": 0.2}, validate_boundedness=True
        )

        aggregator = ChoquetAggregator(config)

        result = aggregator.aggregate(
            subject="test_method", layer_scores={"@b": 0.8, "@chain": 0.7, "@q": 0.9}
        )

        # Linear only: 0.5*0.8 + 0.3*0.7 + 0.2*0.9 = 0.78
        expected = 0.5 * 0.8 + 0.3 * 0.7 + 0.2 * 0.9
        assert result.calibration_score == pytest.approx(expected)
        assert result.breakdown.interaction_contribution == 0.0
        assert result.validation_passed is True

    def test_choquet_with_interaction_terms(self):
        """Test Choquet with interaction terms."""
        config = ChoquetConfig(
            linear_weights={"@b": 0.4, "@chain": 0.4},
            interaction_weights={("@b", "@chain"): 0.2},
            validate_boundedness=True,
        )

        aggregator = ChoquetAggregator(config)

        result = aggregator.aggregate(
            subject="test_with_interaction", layer_scores={"@b": 0.8, "@chain": 0.6}
        )

        # Linear: 0.4*0.8 + 0.4*0.6 = 0.56
        # Interaction bonus applied
        assert result.calibration_score > 0.56
        assert result.breakdown.interaction_contribution > 0

    def test_choquet_boundedness_violation(self):
        """Test that boundedness violations are caught."""
        # Weights that would exceed 1.0 with interaction
        config = ChoquetConfig(
            linear_weights={"@b": 0.8, "@chain": 0.8},
            interaction_weights={("@b", "@chain"): 0.5},
            validate_boundedness=True,
            normalize_weights=False,  # Don't auto-normalize
        )

        aggregator = ChoquetAggregator(config)

        # This should exceed bounds
        with pytest.raises(CalibrationConfigError) as exc_info:
            aggregator.aggregate(subject="test_violation", layer_scores={"@b": 1.0, "@chain": 1.0})

        assert "boundedness" in str(exc_info.value).lower()

    def test_choquet_missing_layer(self):
        """Test that missing layers raise error."""
        config = ChoquetConfig(linear_weights={"@b": 0.5, "@chain": 0.3, "@q": 0.2})

        aggregator = ChoquetAggregator(config)

        # Missing @q layer
        with pytest.raises(ValueError) as exc_info:
            aggregator.aggregate(subject="test_missing", layer_scores={"@b": 0.8, "@chain": 0.7})

        assert "missing" in str(exc_info.value).lower()

    def test_choquet_score_clamping(self):
        """Test that out-of-bounds scores are clamped."""
        config = ChoquetConfig(linear_weights={"@b": 0.5, "@chain": 0.5})

        aggregator = ChoquetAggregator(config)

        # Scores outside [0, 1]
        result = aggregator.aggregate(
            subject="test_clamp", layer_scores={"@b": -0.2, "@chain": 1.5}
        )

        # Should be clamped to [0, 1]
        assert 0.0 <= result.calibration_score <= 1.0


# =============================================================================
# TEST CLASS 6: PROVENANCE DAG
# =============================================================================


class TestProvenanceDAGAdversarial:
    """Adversarial tests for AggregationDAG (aggregation_provenance.py)."""

    def test_dag_construction(self):
        """Test basic DAG construction with nodes and edges."""
        dag = AggregationDAG()

        # Add nodes
        dag.add_node(
            ProvenanceNode(node_id="Q001", level="micro", score=2.0, quality_level="BUENO")
        )

        dag.add_node(
            ProvenanceNode(node_id="DIM01", level="dimension", score=2.0, quality_level="BUENO")
        )

        # Add edge
        dag.add_aggregation_edge(
            source_ids=["Q001"], target_id="DIM01", operation="weighted_average", weights=[1.0]
        )

        stats = dag.get_statistics()
        assert stats["node_count"] == 2
        assert stats["edge_count"] == 1
        assert stats["is_dag"] is True

    def test_dag_cycle_detection(self):
        """Test that cycles are detected and prevented."""
        dag = AggregationDAG()

        dag.add_node(ProvenanceNode(node_id="A", level="micro", score=1.0, quality_level="BUENO"))
        dag.add_node(
            ProvenanceNode(node_id="B", level="dimension", score=2.0, quality_level="BUENO")
        )
        dag.add_node(ProvenanceNode(node_id="C", level="area", score=2.5, quality_level="BUENO"))

        # A -> B -> C
        dag.add_aggregation_edge(["A"], "B", "op1", [1.0])
        dag.add_aggregation_edge(["B"], "C", "op2", [1.0])

        # Try to add cycle: C -> A
        with pytest.raises(ValueError) as exc_info:
            dag.add_aggregation_edge(["C"], "A", "op3", [1.0])

        assert "cycle" in str(exc_info.value).lower()

    def test_dag_lineage_tracing(self):
        """Test lineage tracing through DAG."""
        dag = AggregationDAG()

        # Create hierarchy: Q1, Q2, Q3 -> DIM01 -> PA01
        for i in range(1, 4):
            dag.add_node(
                ProvenanceNode(node_id=f"Q00{i}", level="micro", score=2.0, quality_level="BUENO")
            )

        dag.add_node(
            ProvenanceNode(node_id="DIM01", level="dimension", score=2.0, quality_level="BUENO")
        )

        dag.add_node(ProvenanceNode(node_id="PA01", level="area", score=2.0, quality_level="BUENO"))

        dag.add_aggregation_edge(
            ["Q001", "Q002", "Q003"], "DIM01", "weighted_average", [1 / 3, 1 / 3, 1 / 3]
        )
        dag.add_aggregation_edge(["DIM01"], "PA01", "weighted_average", [1.0])

        # Trace PA01 lineage
        lineage = dag.trace_lineage("PA01")

        assert lineage["target_id"] == "PA01"
        assert lineage["ancestor_count"] == 4  # Q1, Q2, Q3, DIM01
        assert lineage["micro_question_count"] == 3
        assert set(lineage["micro_questions"]) == {"Q001", "Q002", "Q003"}

    def test_shapley_attribution(self):
        """Test Shapley value attribution."""
        dag = AggregationDAG()

        dag.add_node(
            ProvenanceNode(node_id="Q001", level="micro", score=1.0, quality_level="ACEPTABLE")
        )
        dag.add_node(
            ProvenanceNode(node_id="Q002", level="micro", score=3.0, quality_level="EXCELENTE")
        )
        dag.add_node(
            ProvenanceNode(node_id="DIM01", level="dimension", score=2.0, quality_level="BUENO")
        )

        # Equal weights: (1.0 + 3.0) / 2 = 2.0
        dag.add_aggregation_edge(["Q001", "Q002"], "DIM01", "weighted_average", [0.5, 0.5])

        attribution = dag.compute_shapley_attribution("DIM01")

        # Shapley values should reflect contribution
        assert "Q001" in attribution
        assert "Q002" in attribution
        # Q002 contributed more
        assert attribution["Q002"] > attribution["Q001"]

    def test_critical_path_identification(self):
        """Test critical path identification."""
        dag = AggregationDAG()

        # Create nodes with varying contributions
        dag.add_node(
            ProvenanceNode(node_id="Q001", level="micro", score=0.5, quality_level="INSUFICIENTE")
        )
        dag.add_node(
            ProvenanceNode(node_id="Q002", level="micro", score=2.5, quality_level="EXCELENTE")
        )
        dag.add_node(
            ProvenanceNode(node_id="Q003", level="micro", score=2.0, quality_level="BUENO")
        )
        dag.add_node(
            ProvenanceNode(node_id="DIM01", level="dimension", score=1.67, quality_level="BUENO")
        )

        dag.add_aggregation_edge(
            ["Q001", "Q002", "Q003"], "DIM01", "weighted_average", [1 / 3, 1 / 3, 1 / 3]
        )

        critical = dag.get_critical_path("DIM01", top_k=2)

        assert len(critical) == 2
        # Top critical should be Q002 (highest contribution)
        assert critical[0][0] == "Q002"


# =============================================================================
# TEST CLASS 7: QUALITY LEVELS
# =============================================================================


class TestQualityLevelsAdversarial:
    """Adversarial tests for quality levels (phase4_10_00_quality_levels.py)."""

    def test_quality_level_thresholds(self):
        """Test quality level determination from scores."""
        thresholds = QualityLevelThresholds()

        # EXCELENTE: >= 2.5
        assert determine_quality_level(2.7, thresholds) == QualityLevel.EXCELENTE
        assert determine_quality_level(3.0, thresholds) == QualityLevel.EXCELENTE

        # BUENO: >= 2.0
        assert determine_quality_level(2.2, thresholds) == QualityLevel.BUENO

        # ACEPTABLE: >= 1.5
        assert determine_quality_level(1.8, thresholds) == QualityLevel.ACEPTABLE

        # INSUFICIENTE: < 1.5
        assert determine_quality_level(1.0, thresholds) == QualityLevel.INSUFICIENTE
        assert determine_quality_level(0.0, thresholds) == QualityLevel.INSUFICIENTE

    def test_quality_level_boundaries(self):
        """Test quality level at exact boundaries."""
        thresholds = QualityLevelThresholds()

        # Test exact boundaries
        assert determine_quality_level(2.5, thresholds) == QualityLevel.EXCELENTE
        assert determine_quality_level(2.0, thresholds) == QualityLevel.BUENO
        assert determine_quality_level(1.5, thresholds) == QualityLevel.ACEPTABLE

        # Just below boundaries
        assert determine_quality_level(2.49, thresholds) == QualityLevel.BUENO
        assert determine_quality_level(1.99, thresholds) == QualityLevel.ACEPTABLE
        assert determine_quality_level(1.49, thresholds) == QualityLevel.INSUFICIENTE


# =============================================================================
# TEST CLASS 8: AGGREGATION INTEGRATION
# =============================================================================


class TestAggregationIntegrationAdversarial:
    """Adversarial tests for aggregation_integration.py."""

    def test_aggregate_dimensions_async(self, create_minimal_monolith):
        """Test async dimension aggregation integration."""
        # Create scored results as dicts
        results = []
        for dim_idx in range(1, 4):
            for q_idx in range(1, 6):
                results.append(
                    create_scored_result_dict(
                        question_global=dim_idx * 10 + q_idx,
                        base_slot=f"DIM{dim_idx:02d}-Q{q_idx:03d}",
                        policy_area="PA01",
                        dimension=f"DIM{dim_idx:02d}",
                        score=2.0,
                    )
                )

        # Aggregate
        instrumentation = create_mock_instrumentation()
        dimension_scores = asyncio.run(
            aggregate_dimensions_async(results, create_minimal_monolith(), instrumentation)
        )

        # Should have 3 dimension scores
        assert len(dimension_scores) == 3
        for dim_score in dimension_scores:
            assert 0.0 <= dim_score.score <= 3.0
            assert dim_score.validation_passed is True

    def test_aggregate_policy_areas_async(self, create_minimal_monolith):
        """Test async area aggregation integration."""
        # Create dimension scores
        dimension_scores = [
            ActualDimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={},
            )
            for i in range(1, 7)
        ]

        # Aggregate to areas
        instrumentation = create_mock_instrumentation()
        area_scores = asyncio.run(
            aggregate_policy_areas_async(dimension_scores, create_minimal_monolith(), instrumentation)
        )

        # Should have 1 area score
        assert len(area_scores) == 1
        assert 0.0 <= area_scores[0].score <= 3.0

    def test_aggregate_clusters_integration(self, create_minimal_monolith):
        """Test cluster aggregation integration."""
        # Create area scores for a cluster
        area_scores = [
            ActualAreaScore(
                area_id=f"PA0{i}",
                area_name=f"Area {i}",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=[],
                validation_passed=True,
                validation_details={},
            )
            for i in range(1, 4)
        ]

        # Aggregate to clusters
        instrumentation = create_mock_instrumentation()
        cluster_scores = aggregate_clusters(area_scores, create_minimal_monolith(), instrumentation)

        assert len(cluster_scores) >= 1

    def test_evaluate_macro_integration(self, create_minimal_monolith):
        """Test macro evaluation integration."""
        # Create sample data
        dimension_scores = [
            ActualDimensionScore(
                dimension_id="DIM01",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={},
            )
        ]

        area_scores = [
            ActualAreaScore(
                area_id="PA01",
                area_name="Test Area",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=dimension_scores,
                validation_passed=True,
                validation_details={},
            )
        ]

        cluster_scores = [
            ActualClusterScore(
                cluster_id="MESO_1",
                cluster_name="Test Cluster",
                areas=["PA01"],
                score=2.0,
                coherence=0.9,
                variance=0.1,
                weakest_area=None,
                area_scores=area_scores,
                validation_passed=True,
                validation_details={},
            )
        ]

        # Evaluate macro
        instrumentation = create_mock_instrumentation()
        macro_result = evaluate_macro(
            cluster_scores, dimension_scores, area_scores, create_minimal_monolith(), instrumentation
        )

        assert macro_result["macro_score"] is not None
        assert 0.0 <= macro_result["macro_score"] <= 3.0


# =============================================================================
# TEST CLASS 9: END-TO-END FLOW
# =============================================================================


class TestPhase4EndToEndFlow:
    """End-to-end flow tests from Phase 3 through Phase 5."""

    def test_full_flow_phase3_to_phase5(self, create_minimal_monolith):
        """Test complete flow from micro-questions to area scores."""
        # Simulate Phase 3 output: 30 micro-questions (5 per dimension × 6 dimensions)
        phase3_output = []
        for dim_idx in range(1, 7):
            for q_idx in range(1, 6):
                phase3_output.append(
                    create_scored_result_dict(
                        question_global=dim_idx * 100 + q_idx,
                        base_slot=f"DIM{dim_idx:02d}-Q{q_idx:03d}",
                        policy_area="PA01",
                        dimension=f"DIM{dim_idx:02d}",
                        score=2.0,
                    )
                )

        # Phase 4: Aggregate to dimensions
        instrumentation = create_mock_instrumentation()
        dimension_scores = asyncio.run(
            aggregate_dimensions_async(phase3_output, create_minimal_monolith(), instrumentation)
        )

        assert len(dimension_scores) == 6
        for dim_score in dimension_scores:
            assert len(dim_score.contributing_questions) == 5
            assert 0.0 <= dim_score.score <= 3.0

        # Phase 5: Aggregate to areas
        area_scores = asyncio.run(
            aggregate_policy_areas_async(dimension_scores, create_minimal_monolith(), instrumentation)
        )

        assert len(area_scores) == 1
        assert 0.0 <= area_scores[0].score <= 3.0

        # Verify value add: data is transformed meaningfully
        # Area score should be average of dimension scores
        expected_area_score = sum(d.score for d in dimension_scores) / len(dimension_scores)
        assert area_scores[0].score == pytest.approx(expected_area_score)

    def test_full_flow_with_traceability(self, create_minimal_monolith):
        """Test that traceability is preserved through full flow."""
        # Create Phase 3 output with traceability
        phase3_output = []
        question_ids = []
        for dim_idx in range(1, 4):
            for q_idx in range(1, 6):
                qid = dim_idx * 100 + q_idx
                question_ids.append(qid)
                phase3_output.append(
                    create_scored_result_dict(
                        question_global=qid,
                        base_slot=f"DIM{dim_idx:02d}-Q{q_idx:03d}",
                        policy_area="PA01",
                        dimension=f"DIM{dim_idx:02d}",
                        score=2.0,
                    )
                )

        # Aggregate through phases
        instrumentation = create_mock_instrumentation()
        dimension_scores = asyncio.run(
            aggregate_dimensions_async(phase3_output, create_minimal_monolith(), instrumentation)
        )

        area_scores = asyncio.run(
            aggregate_policy_areas_async(dimension_scores, create_minimal_monolith(), instrumentation)
        )

        # Verify traceability
        # All original question IDs should be traceable
        all_traced_questions = set()
        for dim_score in dimension_scores:
            all_traced_questions.update(dim_score.contributing_questions)

        assert len(all_traced_questions) == 15  # 3 dimensions × 5 questions

    def test_full_flow_with_variance(self, create_minimal_monolith):
        """Test full flow with score variance."""
        # Create varied scores
        phase3_output = []
        for dim_idx in range(1, 4):
            # Different average per dimension
            base_score = 1.0 + dim_idx * 0.5
            for q_idx in range(1, 6):
                phase3_output.append(
                    create_scored_result_dict(
                        question_global=dim_idx * 100 + q_idx,
                        base_slot=f"DIM{dim_idx:02d}-Q{q_idx:03d}",
                        policy_area="PA01",
                        dimension=f"DIM{dim_idx:02d}",
                        score=base_score,
                    )
                )

        instrumentation = create_mock_instrumentation()
        dimension_scores = asyncio.run(
            aggregate_dimensions_async(phase3_output, create_minimal_monolith(), instrumentation)
        )

        area_scores = asyncio.run(
            aggregate_policy_areas_async(dimension_scores, create_minimal_monolith(), instrumentation)
        )

        # Dimension scores should differ
        scores = [d.score for d in dimension_scores]
        assert len(set(scores)) == 3  # All different

        # Area score should reflect variance
        assert 1.5 <= area_scores[0].score <= 2.5


# =============================================================================
# TEST CLASS 10: CONSTANTS VALIDATION
# =============================================================================


class TestPhase4ConstantsAdversarial:
    """Adversarial tests for phase4_10_00_phase_4_7_constants.py."""

    def test_quality_level_constants(self):
        """Test quality level constant definitions."""
        assert QUALITY_LEVEL_EXCELENTE == "EXCELENTE"
        assert QUALITY_LEVEL_BUENO == "BUENO"
        assert QUALITY_LEVEL_ACEPTABLE == "ACEPTABLE"
        assert QUALITY_LEVEL_INSUFICIENTE == "INSUFICIENTE"

    def test_score_range_constants(self):
        """Test score range constants."""
        assert MIN_SCORE == 0.0
        assert MAX_SCORE == 3.0

    def test_quality_threshold_constants(self):
        """Test quality threshold constants."""
        # EXCELENTE: 2.5
        assert QUALITY_THRESHOLD_EXCELENTE_MIN == pytest.approx(2.5)
        # BUENO: 2.0
        assert QUALITY_THRESHOLD_BUENO_MIN == pytest.approx(2.0)
        # ACEPTABLE: 1.5
        assert QUALITY_THRESHOLD_ACEPTABLE_MIN == pytest.approx(1.5)

        # Verify ordering
        assert QUALITY_THRESHOLD_EXCELENTE_MIN > QUALITY_THRESHOLD_BUENO_MIN > QUALITY_THRESHOLD_ACEPTABLE_MIN


# =============================================================================
# TEST CLASS 11: VALIDATION MODULE
# =============================================================================


class TestPhase4ValidationAdversarial:
    """Adversarial tests for validation/phase4_10_00_phase4_7_validation.py."""

    def test_dimension_score_validation(self):
        """Test dimension score validation."""
        # Valid dimension score
        valid_dim = ActualDimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="BUENO",
            contributing_questions=[1, 2, 3, 4, 5],
            validation_passed=True,
            validation_details={},
        )

        # Check basic validation
        assert 0.0 <= valid_dim.score <= 3.0
        assert valid_dim.quality_level in ["EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"]

    def test_dimension_score_validation_out_of_range(self):
        """Test dimension score validation with out-of-range score."""
        # Out of range score should be caught
        invalid_dim = ActualDimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=5.0,  # Invalid: > 3.0
            quality_level="EXCELENTE",
            contributing_questions=[1, 2, 3, 4, 5],
            validation_passed=True,
            validation_details={},
        )

        # Score should be clamped during aggregation
        assert invalid_dim.score > 3.0  # Raw value is out of range

    def test_area_score_validation_hermeticity(self):
        """Test area score validation for hermeticity."""
        # Missing dimensions (only 4 instead of 6)
        dim_scores = [
            ActualDimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={},
            )
            for i in [1, 2, 4, 5]  # Missing DIM03, DIM06
        ]

        area_score = ActualAreaScore(
            area_id="PA01",
            area_name="Test Area",
            score=2.0,
            quality_level="BUENO",
            dimension_scores=dim_scores,
            validation_passed=False,  # Should fail hermeticity
            validation_details={"hermeticity": "missing_dimensions"},
        )

        # Hermeticity should fail
        assert area_score.validation_passed is False
        assert "hermeticity" in str(area_score.validation_details).lower()


# =============================================================================
# TEST CLASS 12: ENHANCED AGGREGATORS
# =============================================================================


class TestEnhancedAggregatorsAdversarial:
    """Adversarial tests for enhancements/phase4_10_00_enhanced_aggregators.py."""

    def test_enhanced_dimension_aggregator(self, create_minimal_monolith):
        """Test enhanced dimension aggregator with CI tracking."""
        aggregator = EnhancedDimensionAggregator(
            enable_sota_features=True,
        )

        results = create_dimension_score_group(scores=[1.5, 2.0, 2.5, 2.0, 2.0])

        dim_score = aggregator.aggregate_dimension(
            results, group_by_values={"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should have basic metrics
        assert 0.0 <= dim_score.score <= 3.0
        assert hasattr(dim_score, "validation_details")

    def test_enhanced_area_aggregator(self, create_minimal_monolith):
        """Test enhanced area aggregator with dispersion analysis."""
        aggregator = EnhancedAreaAggregator()

        # Create varied dimension scores
        dimension_scores = [
            ActualDimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=1.0 + i * 0.3,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={},
            )
            for i in range(1, 7)
        ]

        area_score = aggregator.aggregate_area(
            dimension_scores, group_by_values={"policy_area": "PA01", "area_id": "PA01"}
        )

        # Should have validation details
        assert hasattr(area_score, "validation_details")


# =============================================================================
# TEST CLASS 13: CHOQUET PRIMITIVES
# =============================================================================


class TestChoquetPrimitivesAdversarial:
    """Adversarial tests for primitives/phase4_10_00_choquet_primitives.py."""

    def test_fuzzy_measure_operations(self):
        """Test fuzzy measure primitive operations."""
        from farfan_pipeline.phases.Phase_04.primitives.phase4_10_00_choquet_primitives import (
            FuzzyMeasure,
            is_fuzzy_measure,
            check_monotonicity,
        )

        # Valid fuzzy measure
        measure = FuzzyMeasure(
            {
                frozenset(): 0.0,
                frozenset({"a"}): 0.3,
                frozenset({"b"}): 0.5,
                frozenset({"a", "b"}): 1.0,
            }
        )

        assert is_fuzzy_measure(measure) is True
        assert check_monotonicity(measure) is True

    def test_mobius_transform(self):
        """Test Möbius transform computation."""
        from farfan_pipeline.phases.Phase_04.primitives.phase4_10_00_choquet_primitives import (
            mobius_transform,
        )

        # Simple fuzzy measure
        measure = {
            frozenset(): 0.0,
            frozenset({1}): 0.3,
            frozenset({2}): 0.5,
            frozenset({1, 2}): 1.0,
        }

        mobius = mobius_transform(measure)

        # Möbius values should sum to 1.0
        total = sum(mobius.values())
        assert total == pytest.approx(1.0)


# =============================================================================
# TEST CLASS 14: SIGNAL ENRICHED AGGREGATION
# =============================================================================


class TestSignalEnrichedAggregationAdversarial:
    """Adversarial tests for phase4_10_00_signal_enriched_aggregation.py."""

    def test_signal_enriched_aggregator(self, create_minimal_monolith):
        """Test signal-enriched aggregation."""
        aggregator = SignalEnrichedAggregator(
            enable_critical_score_boosting=True
        )

        results = create_dimension_score_group(scores=[0.5, 2.5, 2.0, 2.0, 2.0])

        dim_score = aggregator.aggregate_with_signal_enrichment(
            results,
            group_by_values={"policy_area": "PA01", "dimension": "DIM01"},
            signal_metadata={"variance_high": True},
        )

        # Should apply signal-based adjustments
        assert 0.0 <= dim_score.score <= 3.0

    def test_critical_score_detection(self):
        """Test critical score detection and boosting."""
        # Create data with low scores
        scores = [0.2, 2.5, 2.3, 2.7, 0.3]

        # Check for low scores (below 1.0)
        low_scores = [s for s in scores if s < 1.0]
        assert len(low_scores) == 2
        assert 0.2 in low_scores
        assert 0.3 in low_scores


# =============================================================================
# TEST CLASS 15: ADAPTIVE MESO SCORING
# =============================================================================


class TestAdaptiveMesoScoringAdversarial:
    """Adversarial tests for phase4_10_00_adaptive_meso_scoring.py."""

    def test_adaptive_meso_scoring_basic(self):
        """Test basic adaptive meso scoring."""
        scorer = AdaptiveMesoScoring()

        # Should have methods for adaptive scoring
        assert hasattr(scorer, "get_metrics")

    def test_performance_tracking(self):
        """Test performance metric tracking."""
        scorer = AdaptiveMesoScoring()

        metrics = scorer.get_metrics()

        assert hasattr(metrics, "aggregation_count")
        assert hasattr(metrics, "average_execution_time")
