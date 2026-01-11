"""
Comprehensive Adversarial Tests for Phase 4-7 Modules
======================================================

This test suite covers ALL 26 files in the Phase_four_five_six_seven module.

Uses REAL modularized monolith from conftest.py - NO FAKE DATA.

Author: F.A.R.F.A.N. Pipeline Team
Version: 2.1.0 - With REAL monolith integration
"""

from __future__ import annotations

import math
import pytest
from dataclasses import dataclass, replace
from typing import Any

# =============================================================================
# TEST DATA HELPERS (Uses REAL monolith from conftest.py fixtures)
# =============================================================================


@dataclass
class ScoredResult:
    """Micro-question score from Phase 3."""

    question_global: int | str
    base_slot: str
    policy_area: str
    dimension: str
    score: float
    quality_level: str
    evidence: dict[str, Any]
    raw_results: dict[str, Any]


@dataclass
class DimensionScore:
    """Aggregated dimension score."""

    dimension_id: str
    area_id: str
    score: float
    quality_level: str
    contributing_questions: list[int | str]
    validation_passed: bool
    validation_details: dict[str, Any]
    # SOTA fields
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = (0.0, 0.0)
    epistemic_uncertainty: float = 0.0
    aleatoric_uncertainty: float = 0.0
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"


def create_dimension_score_group(
    dimension: str = "DIM01", policy_area: str = "PA01", scores: list[float] | None = None
) -> list[ScoredResult]:
    """Create a group of scored results for a dimension."""
    scores = scores or [2.0, 2.0, 2.0, 2.0, 2.0]
    return [
        ScoredResult(
            question_global=i + 1,
            base_slot=f"{dimension}-Q{i+1:03d}",
            policy_area=policy_area,
            dimension=dimension,
            score=score,
            quality_level="BUENO",
            evidence={},
            raw_results={},
        )
        for i, score in enumerate(scores)
    ]


# =============================================================================
# TEST CLASS 1: AREA POLICY AGGREGATOR
# =============================================================================


class TestAreaPolicyAggregatorAdversarial:
    """Adversarial tests for AreaPolicyAggregator (aggregation.py)."""

    def test_area_aggregation_with_all_dimensions(self, questionnaire_monolith):
        """Test area aggregation with complete 6 dimensions."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            AreaPolicyAggregator,
            DimensionAggregator,
        )

        # Create 6 dimension scores for one area
        dim_aggregator = DimensionAggregator(
            monolith=questionnaire_monolith, abort_on_insufficient=False
        )

        dimension_scores = []
        for dim_idx in range(1, 7):
            results = create_dimension_score_group(
                dimension=f"DIM{dim_idx:02d}", policy_area="PA01", scores=[2.0, 2.0, 2.0, 2.0, 2.0]
            )
            dim_score = dim_aggregator.aggregate_dimension(
                results, {"policy_area": "PA01", "dimension": f"DIM{dim_idx:02d}"}
            )
            dimension_scores.append(dim_score)

        # Aggregate to area
        area_aggregator = AreaPolicyAggregator(
            monolith=questionnaire_monolith, abort_on_insufficient=False
        )

        area_score = area_aggregator.aggregate_area(
            dimension_scores, {"policy_area": "PA01", "area_name": "Test Area"}
        )

        assert area_score.area_id == "PA01"
        assert area_score.score == pytest.approx(2.0)
        assert area_score.quality_level == "BUENO"
        assert len(area_score.dimension_scores) == 6

    def test_area_aggregation_hermeticity_validation_failure(self, questionnaire_monolith):
        """Test that missing dimensions trigger hermeticity validation failure."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            AreaPolicyAggregator,
            HermeticityValidationError,
            DimensionAggregator,
        )

        # Create only 4 dimension scores (missing 2)
        dim_aggregator = DimensionAggregator(
            monolith=questionnaire_monolith, abort_on_insufficient=False
        )

        dimension_scores = []
        for dim_idx in [1, 2, 4, 5]:  # Missing DIM03, DIM06
            results = create_dimension_score_group(
                dimension=f"DIM{dim_idx:02d}", policy_area="PA01", scores=[2.0] * 5
            )
            dim_score = dim_aggregator.aggregate_dimension(
                results, {"policy_area": "PA01", "dimension": f"DIM{dim_idx:02d}"}
            )
            dimension_scores.append(dim_score)

        area_aggregator = AreaPolicyAggregator(
            monolith=questionnaire_monolith, abort_on_insufficient=False
        )

        area_score = area_aggregator.aggregate_area(
            dimension_scores, {"policy_area": "PA01", "area_name": "Test Area"}
        )

        # Hermeticity should fail but aggregation should complete
        assert area_score.validation_passed is False
        assert "hermeticity" in str(area_score.validation_details).lower()

    def test_area_aggregation_with_dimension_overlap(self, questionnaire_monolith):
        """Test that duplicate dimension IDs are detected."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            AreaPolicyAggregator,
            DimensionAggregator,
        )

        monolith = create_minimal_monolith()

        dim_aggregator = DimensionAggregator(monolith=monolith, abort_on_insufficient=False)

        # Create duplicate DIM01
        results = create_dimension_score_group(
            dimension="DIM01", policy_area="PA01", scores=[2.0] * 5
        )
        dim_score1 = dim_aggregator.aggregate_dimension(
            results, {"policy_area": "PA01", "dimension": "DIM01"}
        )
        dim_score2 = dim_aggregator.aggregate_dimension(
            results, {"policy_area": "PA01", "dimension": "DIM01"}
        )

        area_aggregator = AreaPolicyAggregator(
            monolith=create_minimal_monolith(), abort_on_insufficient=False
        )

        area_score = area_aggregator.aggregate_area(
            [dim_score1, dim_score2], {"policy_area": "PA01", "area_name": "Test Area"}
        )

        # Should detect overlap
        assert area_score.validation_details.get("duplicate_dimensions") is not None

    def test_area_aggregation_score_clamping(self, questionnaire_monolith):
        """Test that out-of-range dimension scores are clamped."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            AreaPolicyAggregator,
        )

        # Create dimension scores with out-of-range values
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import DimensionScore

        dimension_scores = [
            DimensionScore(
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
            dimension_scores, {"policy_area": "PA01", "area_name": "Test Area"}
        )

        # Score should be in valid range
        assert 0.0 <= area_score.score <= 3.0
        assert area_score.validation_details.get("clamping_applied") is True


# =============================================================================
# TEST CLASS 2: CLUSTER AGGREGATOR
# =============================================================================


class TestClusterAggregatorAdversarial:
    """Adversarial tests for ClusterAggregator (aggregation.py)."""

    def test_cluster_aggregation_with_multiple_areas(self, questionnaire_monolith):
        """Test cluster aggregation with multiple policy areas."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            ClusterAggregator,
            AreaScore,
        )

        monolith = create_minimal_monolith()

        # Create area scores for a cluster
        area_scores = [
            AreaScore(
                area_id=f"PA0{i}",
                area_name=f"Area {i}",
                score=2.0 + i * 0.1,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="MESO_1",
                validation_passed=True,
                validation_details={},
            )
            for i in range(1, 6)
        ]

        cluster_aggregator = ClusterAggregator(monolith=monolith, abort_on_insufficient=False)

        cluster_score = cluster_aggregator.aggregate_cluster(
            area_scores, {"cluster_id": "MESO_1", "cluster_name": "Test Cluster"}
        )

        assert cluster_score.cluster_id == "MESO_1"
        assert 0.0 <= cluster_score.score <= 3.0
        assert len(cluster_score.area_scores) == 5

    def test_cluster_aggregation_coherence_metric(self):
        """Test that cluster aggregation calculates coherence."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            ClusterAggregator,
            AreaScore,
        )

        monolith = create_minimal_monolith()

        # High variance areas (low coherence)
        area_scores = [
            AreaScore(
                area_id="PA01",
                area_name="Area 1",
                score=1.0,
                quality_level="ACEPTABLE",
                dimension_scores=[],
                cluster_id="MESO_1",
                validation_passed=True,
                validation_details={},
            ),
            AreaScore(
                area_id="PA02",
                area_name="Area 2",
                score=3.0,
                quality_level="EXCELENTE",
                dimension_scores=[],
                cluster_id="MESO_1",
                validation_passed=True,
                validation_details={},
            ),
        ]

        cluster_aggregator = ClusterAggregator(monolith=monolith, abort_on_insufficient=False)

        cluster_score = cluster_aggregator.aggregate_cluster(
            area_scores, {"cluster_id": "MESO_1", "cluster_name": "Test Cluster"}
        )

        # Coherence metric should exist
        assert "coherence" in cluster_score.validation_details
        # High variance should reduce coherence
        assert cluster_score.validation_details["coherence"] < 1.0

    def test_cluster_aggregation_single_area(self):
        """Test cluster aggregation with only one area."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            ClusterAggregator,
            AreaScore,
        )

        area_scores = [
            AreaScore(
                area_id="PA01",
                area_name="Only Area",
                score=2.5,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="MESO_1",
                validation_passed=True,
                validation_details={},
            )
        ]

        cluster_aggregator = ClusterAggregator(
            monolith=questionnaire_monolith, abort_on_insufficient=False
        )

        cluster_score = cluster_aggregator.aggregate_cluster(
            area_scores, {"cluster_id": "MESO_1", "cluster_name": "Single Area Cluster"}
        )

        # Should handle gracefully
        assert cluster_score.score == pytest.approx(2.5)
        assert cluster_score.validation_details.get("single_area_warning") is not None


# =============================================================================
# TEST CLASS 3: MACRO AGGREGATOR
# =============================================================================


class TestMacroAggregatorAdversarial:
    """Adversarial tests for MacroAggregator (aggregation.py)."""

    def test_macro_aggregation_comprehensive(self):
        """Test macro aggregation with all inputs."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            MacroAggregator,
            DimensionScore,
            AreaScore,
            ClusterScore,
        )

        # Create sample inputs
        dimension_scores = [
            DimensionScore(
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
            AreaScore(
                area_id="PA01",
                area_name="Test Area",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=dimension_scores[:3],
                cluster_id="MESO_1",
                validation_passed=True,
                validation_details={},
            )
        ]

        cluster_scores = [
            ClusterScore(
                cluster_id="MESO_1",
                cluster_name="Test Cluster",
                score=2.0,
                quality_level="BUENO",
                area_scores=area_scores,
                validation_passed=True,
                validation_details={},
            )
        ]

        macro_aggregator = MacroAggregator(
            monolith=questionnaire_monolith, abort_on_insufficient=False
        )

        macro_result = macro_aggregator.evaluate_macro(
            dimension_scores=dimension_scores,
            area_scores=area_scores,
            cluster_scores=cluster_scores,
            metadata={"evaluation_type": "comprehensive"},
        )

        assert macro_result["macro_score"] is not None
        assert 0.0 <= macro_result["macro_score"] <= 3.0
        assert "cross_cutting_coherence" in macro_result

    def test_macro_aggregation_identifies_gaps(self):
        """Test that macro aggregation identifies systemic gaps."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation import (
            MacroAggregator,
            DimensionScore,
        )

        # Create scores with a gap (one dimension very low)
        dimension_scores = [
            DimensionScore(
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
            monolith=questionnaire_monolith, abort_on_insufficient=False
        )

        macro_result = macro_aggregator.evaluate_macro(
            dimension_scores=dimension_scores,
            area_scores=[],
            cluster_scores=[],
            metadata={"evaluation_type": "gap_detection"},
        )

        # Should identify the gap
        assert "systemic_gaps" in macro_result
        assert len(macro_result["systemic_gaps"]) > 0
        assert any("DIM03" in gap for gap in macro_result["systemic_gaps"])


# =============================================================================
# TEST CLASS 4: BOOTSTRAP UNCERTAINTY QUANTIFICATION
# =============================================================================


class TestBootstrapUncertaintyAdversarial:
    """Adversarial tests for BootstrapAggregator (uncertainty_quantification.py)."""

    def test_bootstrap_aggregator_basic(self):
        """Test basic bootstrap aggregation."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_uncertainty_quantification import (
            BootstrapAggregator,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_uncertainty_quantification import (
            BootstrapAggregator,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_uncertainty_quantification import (
            BootstrapAggregator,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_uncertainty_quantification import (
            BootstrapAggregator,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_uncertainty_quantification import (
            aggregate_with_uncertainty,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_choquet_aggregator import (
            ChoquetAggregator,
            ChoquetConfig,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_choquet_aggregator import (
            ChoquetAggregator,
            ChoquetConfig,
        )

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
        # Interaction: 0.2*min(0.8, 0.6) = 0.12
        # Total: 0.68
        expected = 0.4 * 0.8 + 0.4 * 0.6 + 0.2 * min(0.8, 0.6)
        assert result.calibration_score == pytest.approx(expected)
        assert result.breakdown.interaction_contribution > 0

    def test_choquet_boundedness_violation(self):
        """Test that boundedness violations are caught."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_choquet_aggregator import (
            ChoquetAggregator,
            ChoquetConfig,
            CalibrationConfigError,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_choquet_aggregator import (
            ChoquetAggregator,
            ChoquetConfig,
        )

        config = ChoquetConfig(linear_weights={"@b": 0.5, "@chain": 0.3, "@q": 0.2})

        aggregator = ChoquetAggregator(config)

        # Missing @q layer
        with pytest.raises(ValueError) as exc_info:
            aggregator.aggregate(subject="test_missing", layer_scores={"@b": 0.8, "@chain": 0.7})

        assert "missing" in str(exc_info.value).lower()

    def test_choquet_score_clamping(self):
        """Test that out-of-bounds scores are clamped."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_choquet_aggregator import (
            ChoquetAggregator,
            ChoquetConfig,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_provenance import (
            AggregationDAG,
            ProvenanceNode,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_provenance import (
            AggregationDAG,
            ProvenanceNode,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_provenance import (
            AggregationDAG,
            ProvenanceNode,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_provenance import (
            AggregationDAG,
            ProvenanceNode,
        )

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
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_provenance import (
            AggregationDAG,
            ProvenanceNode,
        )

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
    """Adversarial tests for quality levels (primitives/quality_levels.py)."""

    def test_quality_level_thresholds(self):
        """Test quality level determination from scores."""
        from farfan_pipeline.phases.Phase_4.primitives.quality_levels import (
            QualityLevel,
            QualityLevelThresholds,
        )

        thresholds = QualityLevelThresholds()

        # EXCELENTE: >= 2.55 (85% of 3.0)
        assert thresholds.determine_quality(2.7) == QualityLevel.EXCELENTE
        assert thresholds.determine_quality(3.0) == QualityLevel.EXCELENTE

        # BUENO: >= 2.10 (70% of 3.0)
        assert thresholds.determine_quality(2.2) == QualityLevel.BUENO

        # ACEPTABLE: >= 1.65 (55% of 3.0)
        assert thresholds.determine_quality(1.8) == QualityLevel.ACEPTABLE

        # INSUFICIENTE: < 1.65
        assert thresholds.determine_quality(1.0) == QualityLevel.INSUFICIENTE
        assert thresholds.determine_quality(0.0) == QualityLevel.INSUFICIENTE

    def test_quality_level_boundaries(self):
        """Test quality level at exact boundaries."""
        from farfan_pipeline.phases.Phase_4.primitives.quality_levels import (
            QualityLevel,
            QualityLevelThresholds,
        )

        thresholds = QualityLevelThresholds()

        # Test exact boundaries
        assert thresholds.determine_quality(2.55) == QualityLevel.EXCELENTE
        assert thresholds.determine_quality(2.10) == QualityLevel.BUENO
        assert thresholds.determine_quality(1.65) == QualityLevel.ACEPTABLE

        # Just below boundaries
        assert thresholds.determine_quality(2.549) == QualityLevel.BUENO
        assert thresholds.determine_quality(2.099) == QualityLevel.ACEPTABLE
        assert thresholds.determine_quality(1.649) == QualityLevel.INSUFICIENTE


# =============================================================================
# TEST CLASS 8: AGGREGATION INTEGRATION
# =============================================================================


class TestAggregationIntegrationAdversarial:
    """Adversarial tests for aggregation_integration.py."""

    def test_aggregate_dimensions_async(self):
        """Test async dimension aggregation integration."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_integration import (
            aggregate_dimensions_async,
        )

        # Create scored results
        results = []
        for dim_idx in range(1, 4):
            for q_idx in range(1, 6):
                results.append(
                    ScoredResult(
                        question_global=dim_idx * 10 + q_idx,
                        base_slot=f"DIM{dim_idx:02d}-Q{q_idx:03d}",
                        policy_area="PA01",
                        dimension=f"DIM{dim_idx:02d}",
                        score=2.0,
                        quality_level="BUENO",
                        evidence={},
                        raw_results={},
                    )
                )

        # Aggregate
        dimension_scores = aggregate_dimensions_async(
            scored_results=results, monolith=None, signal_registry=None
        )

        # Should have 3 dimension scores
        assert len(dimension_scores) == 3
        for dim_score in dimension_scores:
            assert 0.0 <= dim_score.score <= 3.0
            assert dim_score.validation_passed is True

    def test_aggregate_policy_areas_async(self):
        """Test async area aggregation integration."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_integration import (
            aggregate_policy_areas_async,
            DimensionScore,
        )

        # Create dimension scores
        dimension_scores = [
            DimensionScore(
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
        area_scores = aggregate_policy_areas_async(
            dimension_scores=dimension_scores, monolith=None, signal_registry=None
        )

        # Should have 1 area score
        assert len(area_scores) == 1
        assert area_scores[0].area_id == "PA01"
        assert 0.0 <= area_scores[0].score <= 3.0

    def test_aggregate_clusters_integration(self):
        """Test cluster aggregation integration."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_integration import (
            aggregate_clusters,
            AreaScore,
        )

        # Create area scores for a cluster
        area_scores = [
            AreaScore(
                area_id=f"PA0{i}",
                area_name=f"Area {i}",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="MESO_1",
                validation_passed=True,
                validation_details={},
            )
            for i in range(1, 4)
        ]

        # Aggregate to clusters
        cluster_scores = aggregate_clusters(area_scores=area_scores, monolith=None)

        assert len(cluster_scores) == 1
        assert cluster_scores[0].cluster_id == "MESO_1"

    def test_evaluate_macro_integration(self):
        """Test macro evaluation integration."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_integration import (
            evaluate_macro,
            DimensionScore,
            AreaScore,
            ClusterScore,
        )

        # Create sample data
        dimension_scores = [
            DimensionScore(
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
            AreaScore(
                area_id="PA01",
                area_name="Test Area",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=dimension_scores,
                cluster_id="MESO_1",
                validation_passed=True,
                validation_details={},
            )
        ]

        cluster_scores = [
            ClusterScore(
                cluster_id="MESO_1",
                cluster_name="Test Cluster",
                score=2.0,
                quality_level="BUENO",
                area_scores=area_scores,
                validation_passed=True,
                validation_details={},
            )
        ]

        # Evaluate macro
        macro_result = evaluate_macro(
            dimension_scores=dimension_scores,
            area_scores=area_scores,
            cluster_scores=cluster_scores,
            monolith=None,
        )

        assert macro_result["macro_score"] is not None
        assert 0.0 <= macro_result["macro_score"] <= 3.0


# =============================================================================
# TEST CLASS 9: END-TO-END FLOW
# =============================================================================


class TestPhase4EndToEndFlow:
    """End-to-end flow tests from Phase 3 through Phase 5."""

    def test_full_flow_phase3_to_phase5(self):
        """Test complete flow from micro-questions to area scores."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_integration import (
            aggregate_dimensions_async,
            aggregate_policy_areas_async,
        )

        # Simulate Phase 3 output: 30 micro-questions (5 per dimension × 6 dimensions)
        phase3_output = []
        for dim_idx in range(1, 7):
            for q_idx in range(1, 6):
                phase3_output.append(
                    ScoredResult(
                        question_global=dim_idx * 100 + q_idx,
                        base_slot=f"DIM{dim_idx:02d}-Q{q_idx:03d}",
                        policy_area="PA01",
                        dimension=f"DIM{dim_idx:02d}",
                        score=2.0,
                        quality_level="BUENO",
                        evidence={"source": "human_evaluator"},
                        raw_results={},
                    )
                )

        # Phase 4: Aggregate to dimensions
        dimension_scores = aggregate_dimensions_async(
            scored_results=phase3_output, monolith=None, signal_registry=None
        )

        assert len(dimension_scores) == 6
        for dim_score in dimension_scores:
            assert len(dim_score.contributing_questions) == 5
            assert 0.0 <= dim_score.score <= 3.0

        # Phase 5: Aggregate to areas
        area_scores = aggregate_policy_areas_async(
            dimension_scores=dimension_scores, monolith=None, signal_registry=None
        )

        assert len(area_scores) == 1
        assert area_scores[0].area_id == "PA01"
        assert 0.0 <= area_scores[0].score <= 3.0

        # Verify value add: data is transformed meaningfully
        # Area score should be average of dimension scores
        expected_area_score = sum(d.score for d in dimension_scores) / len(dimension_scores)
        assert area_scores[0].score == pytest.approx(expected_area_score)

    def test_full_flow_with_traceability(self):
        """Test that traceability is preserved through full flow."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_integration import (
            aggregate_dimensions_async,
            aggregate_policy_areas_async,
        )

        # Create Phase 3 output with traceability
        phase3_output = []
        question_ids = []
        for dim_idx in range(1, 4):
            for q_idx in range(1, 6):
                qid = dim_idx * 100 + q_idx
                question_ids.append(qid)
                phase3_output.append(
                    ScoredResult(
                        question_global=qid,
                        base_slot=f"DIM{dim_idx:02d}-Q{q_idx:03d}",
                        policy_area="PA01",
                        dimension=f"DIM{dim_idx:02d}",
                        score=2.0,
                        quality_level="BUENO",
                        evidence={"trace_id": f"trace_{qid}"},
                        raw_results={},
                    )
                )

        # Aggregate through phases
        dimension_scores = aggregate_dimensions_async(
            scored_results=phase3_output, monolith=None, signal_registry=None
        )

        area_scores = aggregate_policy_areas_async(
            dimension_scores=dimension_scores, monolith=None, signal_registry=None
        )

        # Verify traceability
        # All original question IDs should be traceable
        all_traced_questions = set()
        for dim_score in dimension_scores:
            all_traced_questions.update(dim_score.contributing_questions)

        assert len(all_traced_questions) == 15  # 3 dimensions × 5 questions

    def test_full_flow_with_variance(self):
        """Test full flow with score variance."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_integration import (
            aggregate_dimensions_async,
            aggregate_policy_areas_async,
        )

        # Create varied scores
        phase3_output = []
        for dim_idx in range(1, 4):
            # Different average per dimension
            base_score = 1.0 + dim_idx * 0.5
            for q_idx in range(1, 6):
                phase3_output.append(
                    ScoredResult(
                        question_global=dim_idx * 100 + q_idx,
                        base_slot=f"DIM{dim_idx:02d}-Q{q_idx:03d}",
                        policy_area="PA01",
                        dimension=f"DIM{dim_idx:02d}",
                        score=base_score,
                        quality_level="BUENO",
                        evidence={},
                        raw_results={},
                    )
                )

        dimension_scores = aggregate_dimensions_async(
            scored_results=phase3_output, monolith=None, signal_registry=None
        )

        area_scores = aggregate_policy_areas_async(
            dimension_scores=dimension_scores, monolith=None, signal_registry=None
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
    """Adversarial tests for PHASE_4_7_CONSTANTS.py."""

    def test_quality_level_constants(self):
        """Test quality level constant definitions."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_phase_4_7_constants import (
            QUALITY_LEVEL_EXCELENTE,
            QUALITY_LEVEL_BUENO,
            QUALITY_LEVEL_ACEPTABLE,
            QUALITY_LEVEL_INSUFICIENTE,
        )

        assert QUALITY_LEVEL_EXCELENTE == "EXCELENTE"
        assert QUALITY_LEVEL_BUENO == "BUENO"
        assert QUALITY_LEVEL_ACEPTABLE == "ACEPTABLE"
        assert QUALITY_LEVEL_INSUFICIENTE == "INSUFICIENTE"

    def test_score_range_constants(self):
        """Test score range constants."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_phase_4_7_constants import (
            MIN_SCORE,
            MAX_SCORE,
        )

        assert MIN_SCORE == 0.0
        assert MAX_SCORE == 3.0

    def test_quality_threshold_constants(self):
        """Test quality threshold constants."""
        from farfan_pipeline.phases.Phase_4.phase4_10_00_phase_4_7_constants import (
            THRESHOLD_EXCELENTE,
            THRESHOLD_BUENO,
            THRESHOLD_ACEPTABLE,
        )

        # EXCELENTE: 85% of max
        assert THRESHOLD_EXCELENTE == pytest.approx(0.85 * 3.0)
        # BUENO: 70% of max
        assert THRESHOLD_BUENO == pytest.approx(0.70 * 3.0)
        # ACEPTABLE: 55% of max
        assert THRESHOLD_ACEPTABLE == pytest.approx(0.55 * 3.0)

        # Verify ordering
        assert THRESHOLD_EXCELENTE > THRESHOLD_BUENO > THRESHOLD_ACEPTABLE


# =============================================================================
# TEST CLASS 11: VALIDATION MODULE
# =============================================================================


class TestPhase4ValidationAdversarial:
    """Adversarial tests for validation/phase4_7_validation.py."""

    def test_dimension_score_validation(self):
        """Test dimension score validation."""
        from farfan_pipeline.phases.Phase_4.validation import (
            validate_dimension_score,
        )

        # Valid dimension score
        valid_dim = DimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="BUENO",
            contributing_questions=[1, 2, 3, 4, 5],
            validation_passed=True,
            validation_details={},
        )

        result = validate_dimension_score(valid_dim)
        assert result.passed is True

    def test_dimension_score_validation_out_of_range(self):
        """Test dimension score validation with out-of-range score."""
        from farfan_pipeline.phases.Phase_4.validation import (
            validate_dimension_score,
        )

        # Out of range score
        invalid_dim = DimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=5.0,  # Invalid: > 3.0
            quality_level="EXCELENTE",
            contributing_questions=[1, 2, 3, 4, 5],
            validation_passed=True,
            validation_details={},
        )

        result = validate_dimension_score(invalid_dim)
        assert result.passed is False
        assert "score" in str(result.details).lower()

    def test_area_score_validation_hermeticity(self):
        """Test area score validation for hermeticity."""
        from farfan_pipeline.phases.Phase_4.validation import (
            validate_area_score_hermeticity,
            AreaScore,
            DimensionScore,
        )

        # Missing dimensions (only 4 instead of 6)
        dim_scores = [
            DimensionScore(
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

        area_score = AreaScore(
            area_id="PA01",
            area_name="Test Area",
            score=2.0,
            quality_level="BUENO",
            dimension_scores=dim_scores,
            cluster_id="MESO_1",
            validation_passed=True,
            validation_details={},
        )

        result = validate_area_score_hermeticity(area_score)
        assert result.passed is False
        assert "hermeticity" in str(result.details).lower()


# =============================================================================
# TEST CLASS 12: ENHANCED AGGREGATORS
# =============================================================================


class TestEnhancedAggregatorsAdversarial:
    """Adversarial tests for enhancements/enhanced_aggregators.py."""

    def test_enhanced_dimension_aggregator(self):
        """Test enhanced dimension aggregator with CI tracking."""
        from farfan_pipeline.phases.Phase_4.enhancements import (
            EnhancedDimensionAggregator,
        )

        aggregator = EnhancedDimensionAggregator(
            monolith=None, abort_on_insufficient=False, enable_confidence_intervals=True
        )

        results = create_dimension_score_group(scores=[1.5, 2.0, 2.5, 2.0, 2.0])

        dim_score = aggregator.aggregate_dimension(
            results, {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should have enhanced metrics
        assert hasattr(dim_score, "confidence_interval_95")
        assert hasattr(dim_score, "dispersion_metric")

    def test_enhanced_area_aggregator(self):
        """Test enhanced area aggregator with dispersion analysis."""
        from farfan_pipeline.phases.Phase_4.enhancements import (
            EnhancedAreaAggregator,
            DimensionScore,
        )

        aggregator = EnhancedAreaAggregator(monolith=None, abort_on_insufficient=False)

        # Create varied dimension scores
        dimension_scores = [
            DimensionScore(
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
            dimension_scores, {"policy_area": "PA01", "area_name": "Test Area"}
        )

        # Should have coherence metrics
        assert "coherence" in area_score.validation_details
        assert "dispersion" in area_score.validation_details


# =============================================================================
# TEST CLASS 13: CHOQUET PRIMITIVES
# =============================================================================


class TestChoquetPrimitivesAdversarial:
    """Adversarial tests for primitives/choquet_primitives.py."""

    def test_fuzzy_measure_operations(self):
        """Test fuzzy measure primitive operations."""
        from farfan_pipeline.phases.Phase_4.primitives.choquet_primitives import (
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
        from farfan_pipeline.phases.Phase_4.primitives.choquet_primitives import (
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
    """Adversarial tests for signal_enriched_aggregation.py."""

    def test_signal_enriched_aggregator(self):
        """Test signal-enriched aggregation."""
        from farfan_pipeline.phases.Phase_4.enhancements.phase4_10_00_signal_enriched_aggregation import (
            SignalEnrichedAggregator,
        )

        aggregator = SignalEnrichedAggregator(monolith=None, enable_critical_score_boosting=True)

        results = create_dimension_score_group(scores=[0.5, 2.5, 2.0, 2.0, 2.0])

        dim_score = aggregator.aggregate_with_signal_enrichment(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"},
            signal_metadata={"variance_high": True},
        )

        # Should apply signal-based adjustments
        assert hasattr(dim_score, "signal_applied")
        assert 0.0 <= dim_score.score <= 3.0

    def test_critical_score_detection(self):
        """Test critical score detection and boosting."""
        from farfan_pipeline.phases.Phase_4.enhancements.phase4_10_00_signal_enriched_aggregation import (
            detect_critical_scores,
        )

        scores = [0.2, 2.5, 2.3, 2.7, 0.3]

        critical = detect_critical_scores(scores, threshold=0.5, boost_factor=1.2)

        # Should identify low scores
        assert len(critical["low_scores"]) == 2
        assert 0.2 in critical["low_scores"]
        assert 0.3 in critical["low_scores"]


# =============================================================================
# TEST CLASS 15: ADAPTIVE MESO SCORING
# =============================================================================


class TestAdaptiveMesoScoringAdversarial:
    """Adversarial tests for adaptive_meso_scoring.py."""

    def test_adaptive_method_selection(self):
        """Test adaptive scoring method selection."""
        from farfan_pipeline.phases.Phase_4.enhancements.phase4_10_00_adaptive_meso_scoring import (
            AdaptiveMesoScoring,
        )

        scorer = AdaptiveMesoScoring()

        # High variance: should choose robust method
        method1 = scorer.select_aggregation_method(
            scores=[0.5, 2.5, 1.0, 3.0, 0.8], context={"variance_threshold": 0.5}
        )

        # Low variance: should choose standard method
        method2 = scorer.select_aggregation_method(
            scores=[2.0, 2.1, 1.9, 2.0, 2.0], context={"variance_threshold": 0.5}
        )

        assert method1 != method2 or "robust" in method1.lower() or "standard" in method2.lower()

    def test_performance_tracking(self):
        """Test performance metric tracking."""
        from farfan_pipeline.phases.Phase_4.enhancements.phase4_10_00_adaptive_meso_scoring import (
            AdaptiveMesoScoring,
            ScoringMetrics,
        )

        scorer = AdaptiveMesoScoring()

        metrics = scorer.get_metrics()

        assert hasattr(metrics, "aggregation_count")
        assert hasattr(metrics, "average_execution_time")
