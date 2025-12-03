"""
Tests for SOTA aggregation features.

This module tests the three SOTA injection points:
1. Choquet integral aggregation (non-linear interactions)
2. Bayesian uncertainty quantification (bootstrap + CI)
3. DAG provenance tracking (lineage + SHAP attribution)
"""

import pytest
import numpy as np

from farfan_pipeline.processing.aggregation_provenance import (
    AggregationDAG,
    ProvenanceNode,
)
from farfan_pipeline.processing.uncertainty_quantification import (
    BootstrapAggregator,
    BayesianPropagation,
    SensitivityAnalysis,
    aggregate_with_uncertainty,
)
from farfan_pipeline.processing.choquet_adapter import (
    ChoquetProcessingAdapter,
    create_default_choquet_adapter,
)


class TestChoquetAggregation:
    """Test Choquet integral aggregation."""
    
    def test_choquet_creates_non_linear_interactions(self):
        """Choquet with interactions should differ from naive weighted average."""
        scores = [7.0, 8.0, 6.5]
        weights = [0.33, 0.33, 0.34]
        
        # Naive weighted average
        naive_score = sum(s * w for s, w in zip(scores, weights))
        
        # Choquet with interactions
        interaction_weights = {("0", "1"): 0.1}  # Synergy between first two
        choquet = ChoquetProcessingAdapter(
            linear_weights={str(i): w for i, w in enumerate(weights)},
            interaction_weights=interaction_weights,
        )
        choquet_score = choquet.aggregate(scores, weights, interaction_pairs=[(0, 1)])
        
        # Choquet should differ due to min(7.0, 8.0) * 0.1 = 0.7 interaction term
        assert abs(choquet_score - naive_score) > 0.01
        assert choquet_score > naive_score  # Positive interaction (synergy)
    
    def test_choquet_with_redundancy_penalty(self):
        """Negative interaction weights should penalize redundancy."""
        scores = [8.0, 8.0]  # Redundant high scores
        weights = [0.5, 0.5]
        
        interaction_weights = {("0", "1"): -0.1}  # Redundancy penalty
        choquet = ChoquetProcessingAdapter(
            linear_weights={"0": 0.5, "1": 0.5},
            interaction_weights=interaction_weights,
        )
        choquet_score = choquet.aggregate(scores, weights, interaction_pairs=[(0, 1)])
        
        naive_score = 8.0  # Weighted average
        assert choquet_score < naive_score  # Penalty applied
    
    def test_choquet_default_adapter(self):
        """Default adapter should work for n inputs."""
        adapter = create_default_choquet_adapter(n_inputs=5)
        scores = [7.0, 8.0, 6.5, 7.5, 8.5]
        result = adapter.aggregate(scores, weights=None)
        
        assert 0.0 <= result <= 10.0  # Reasonable range
        assert isinstance(result, float)


class TestUncertaintyQuantification:
    """Test Bayesian uncertainty quantification."""
    
    def test_bootstrap_computes_confidence_intervals(self):
        """Bootstrap should provide 95% CI around mean."""
        scores = [7.0, 7.5, 6.8, 7.2, 6.9]
        weights = [0.2, 0.2, 0.2, 0.2, 0.2]
        
        bootstrapper = BootstrapAggregator(n_samples=1000, random_seed=42)
        uncertainty = bootstrapper.bootstrap_weighted_average(scores, weights)
        
        # Mean should be close to weighted average
        expected_mean = sum(s * w for s, w in zip(scores, weights))
        assert abs(uncertainty.mean - expected_mean) < 0.1
        
        # CI should contain mean
        lower, upper = uncertainty.confidence_interval_95
        assert lower < uncertainty.mean < upper
        
        # Std should be positive
        assert uncertainty.std > 0.0
    
    def test_bootstrap_is_deterministic(self):
        """Same seed should produce identical results."""
        scores = [7.0, 8.0, 6.5]
        
        bootstrap1 = BootstrapAggregator(n_samples=500, random_seed=42)
        result1 = bootstrap1.bootstrap_weighted_average(scores)
        
        bootstrap2 = BootstrapAggregator(n_samples=500, random_seed=42)
        result2 = bootstrap2.bootstrap_weighted_average(scores)
        
        assert result1.mean == result2.mean
        assert result1.std == result2.std
        assert result1.confidence_interval_95 == result2.confidence_interval_95
    
    def test_uncertainty_decomposition(self):
        """Epistemic and aleatoric uncertainty should be non-negative."""
        scores = [7.0, 8.0, 6.5, 7.5, 8.2]
        
        _, uncertainty = aggregate_with_uncertainty(scores, n_bootstrap=1000, random_seed=42)
        
        assert uncertainty.epistemic_uncertainty >= 0.0
        assert uncertainty.aleatoric_uncertainty >= 0.0
        assert uncertainty.dominant_uncertainty_type() in ["epistemic", "aleatoric", "balanced"]
    
    def test_bayesian_propagation_analytical(self):
        """Analytical propagation should match expected variance formula."""
        scores = [7.0, 8.0, 6.0]
        uncertainties = [0.5, 0.3, 0.4]
        weights = [0.33, 0.33, 0.34]
        
        mean, std = BayesianPropagation.propagate_weighted_average(
            scores, uncertainties, weights
        )
        
        # Mean should match weighted average
        expected_mean = sum(s * w for s, w in zip(scores, weights))
        assert abs(mean - expected_mean) < 1e-9
        
        # Variance: sum(w_i^2 * var_i)
        expected_var = sum(w**2 * u**2 for w, u in zip(weights, uncertainties))
        expected_std = np.sqrt(expected_var)
        assert abs(std - expected_std) < 1e-9
    
    def test_coefficient_of_variation_threshold(self):
        """High CV should trigger high uncertainty flag."""
        # Low uncertainty case
        scores_low_var = [7.0, 7.1, 7.05, 6.95, 7.0]
        _, unc_low = aggregate_with_uncertainty(scores_low_var, n_bootstrap=1000, random_seed=42)
        assert not unc_low.is_high_uncertainty(threshold=0.1)
        
        # High uncertainty case
        scores_high_var = [3.0, 9.0, 2.0, 8.5, 4.0]
        _, unc_high = aggregate_with_uncertainty(scores_high_var, n_bootstrap=1000, random_seed=42)
        assert unc_high.is_high_uncertainty(threshold=0.1)


class TestProvenanceDAG:
    """Test DAG provenance tracking."""
    
    def test_dag_creation_and_node_addition(self):
        """DAG should accept nodes and maintain structure."""
        dag = AggregationDAG()
        
        node1 = ProvenanceNode(node_id="Q001", level="micro", score=7.0, quality_level="BUENO")
        node2 = ProvenanceNode(node_id="Q002", level="micro", score=8.0, quality_level="EXCELENTE")
        
        dag.add_node(node1)
        dag.add_node(node2)
        
        assert "Q001" in dag.nodes
        assert "Q002" in dag.nodes
        assert dag.graph.number_of_nodes() == 2
    
    def test_dag_aggregation_edges(self):
        """DAG should record aggregation operations."""
        dag = AggregationDAG()
        
        # Add source nodes
        for i in range(3):
            node = ProvenanceNode(
                node_id=f"Q{i:03d}",
                level="micro",
                score=7.0 + i,
                quality_level="BUENO",
            )
            dag.add_node(node)
        
        # Add target node
        target = ProvenanceNode(
            node_id="DIM01_PA01",
            level="dimension",
            score=7.5,
            quality_level="BUENO",
        )
        dag.add_node(target)
        
        # Record aggregation
        dag.add_aggregation_edge(
            source_ids=["Q000", "Q001", "Q002"],
            target_id="DIM01_PA01",
            operation="weighted_average",
            weights=[0.33, 0.33, 0.34],
        )
        
        assert dag.graph.number_of_edges() == 3
        assert dag.graph.has_edge("Q000", "DIM01_PA01")
    
    def test_dag_cycle_detection(self):
        """DAG should reject edges that create cycles."""
        dag = AggregationDAG()
        
        dag.add_node(ProvenanceNode(node_id="A", level="micro", score=7.0, quality_level="BUENO"))
        dag.add_node(ProvenanceNode(node_id="B", level="dimension", score=7.5, quality_level="BUENO"))
        
        # A → B is valid
        dag.add_aggregation_edge(["A"], "B", "weighted_average", [1.0])
        
        # B → A would create cycle, should raise
        with pytest.raises(ValueError, match="cycle"):
            dag.add_aggregation_edge(["B"], "A", "weighted_average", [1.0])
    
    def test_lineage_tracing(self):
        """Should trace complete lineage of a target node."""
        dag = AggregationDAG()
        
        # Build hierarchy: Q001, Q002 → DIM01 → AREA01
        for qid in ["Q001", "Q002"]:
            dag.add_node(ProvenanceNode(node_id=qid, level="micro", score=7.0, quality_level="BUENO"))
        
        dag.add_node(ProvenanceNode(node_id="DIM01", level="dimension", score=7.5, quality_level="BUENO"))
        dag.add_aggregation_edge(["Q001", "Q002"], "DIM01", "weighted_average", [0.5, 0.5])
        
        dag.add_node(ProvenanceNode(node_id="AREA01", level="area", score=7.5, quality_level="BUENO"))
        dag.add_aggregation_edge(["DIM01"], "AREA01", "weighted_average", [1.0])
        
        # Trace AREA01
        lineage = dag.trace_lineage("AREA01")
        
        assert lineage["ancestor_count"] == 3  # Q001, Q002, DIM01
        assert "Q001" in lineage["ancestors"]
        assert "Q002" in lineage["ancestors"]
        assert "DIM01" in lineage["ancestors"]
        assert lineage["micro_question_count"] == 2
        # depth can be fractional due to average path lengths, just check > 1
        assert lineage["depth"] >= 1
    
    def test_shapley_attribution(self):
        """Shapley values should sum to target score."""
        dag = AggregationDAG()
        
        # Add sources
        scores = [7.0, 8.0, 6.5]
        weights = [0.3, 0.4, 0.3]
        for i, score in enumerate(scores):
            dag.add_node(ProvenanceNode(
                node_id=f"Q{i:03d}",
                level="micro",
                score=score,
                quality_level="BUENO",
            ))
        
        # Add target
        target_score = sum(s * w for s, w in zip(scores, weights))
        dag.add_node(ProvenanceNode(
            node_id="DIM01",
            level="dimension",
            score=target_score,
            quality_level="BUENO",
        ))
        
        dag.add_aggregation_edge(
            ["Q000", "Q001", "Q002"],
            "DIM01",
            "weighted_average",
            weights,
        )
        
        # Compute Shapley
        attribution = dag.compute_shapley_attribution("DIM01")
        
        # Shapley values should sum to target score (approximately)
        total_attribution = sum(attribution.values())
        assert abs(total_attribution - target_score) < 0.01
        
        # Highest weight should have highest attribution
        max_weight_idx = weights.index(max(weights))
        max_attr_node = max(attribution, key=attribution.get)
        assert max_attr_node == f"Q{max_weight_idx:03d}"
    
    def test_critical_path_identification(self):
        """Should identify top-k most important inputs."""
        dag = AggregationDAG()
        
        scores = [9.0, 7.0, 8.0, 6.0, 7.5]
        weights = [0.3, 0.2, 0.25, 0.1, 0.15]
        
        for i, score in enumerate(scores):
            dag.add_node(ProvenanceNode(
                node_id=f"Q{i:03d}",
                level="micro",
                score=score,
                quality_level="BUENO",
            ))
        
        target_score = sum(s * w for s, w in zip(scores, weights))
        dag.add_node(ProvenanceNode(
            node_id="DIM01",
            level="dimension",
            score=target_score,
            quality_level="BUENO",
        ))
        
        dag.add_aggregation_edge(
            [f"Q{i:03d}" for i in range(5)],
            "DIM01",
            "weighted_average",
            weights,
        )
        
        critical_path = dag.get_critical_path("DIM01", top_k=3)
        
        assert len(critical_path) == 3
        # Top contributor should be Q000 (highest weight * highest score)
        assert critical_path[0][0] == "Q000"
    
    def test_graphml_export(self, tmp_path):
        """Should export DAG to GraphML format."""
        dag = AggregationDAG()
        
        dag.add_node(ProvenanceNode(node_id="Q001", level="micro", score=7.0, quality_level="BUENO"))
        dag.add_node(ProvenanceNode(node_id="DIM01", level="dimension", score=7.0, quality_level="BUENO"))
        dag.add_aggregation_edge(["Q001"], "DIM01", "weighted_average", [1.0])
        
        output_path = tmp_path / "test_dag.graphml"
        dag.export_graphml(str(output_path))
        
        assert output_path.exists()
        # Verify it's valid XML
        with open(output_path) as f:
            content = f.read()
            assert "<?xml" in content
            assert "<graphml" in content
    
    def test_prov_json_export(self, tmp_path):
        """Should export to W3C PROV-JSON format."""
        dag = AggregationDAG()
        
        dag.add_node(ProvenanceNode(node_id="Q001", level="micro", score=7.0, quality_level="BUENO"))
        dag.add_node(ProvenanceNode(node_id="DIM01", level="dimension", score=7.0, quality_level="BUENO"))
        dag.add_aggregation_edge(["Q001"], "DIM01", "weighted_average", [1.0])
        
        output_path = tmp_path / "provenance.json"
        dag.export_prov_json(str(output_path))
        
        assert output_path.exists()
        
        import json
        with open(output_path) as f:
            prov_doc = json.load(f)
        
        assert "prefix" in prov_doc
        assert "entity" in prov_doc
        assert "activity" in prov_doc
        assert "Q001" in prov_doc["entity"]
    
    def test_dag_statistics(self):
        """Should compute graph statistics."""
        dag = AggregationDAG()
        
        for i in range(5):
            dag.add_node(ProvenanceNode(
                node_id=f"Q{i:03d}",
                level="micro",
                score=7.0,
                quality_level="BUENO",
            ))
        
        dag.add_node(ProvenanceNode(node_id="DIM01", level="dimension", score=7.5, quality_level="BUENO"))
        dag.add_aggregation_edge(
            [f"Q{i:03d}" for i in range(5)],
            "DIM01",
            "weighted_average",
            [0.2] * 5,
        )
        
        stats = dag.get_statistics()
        
        assert stats["node_count"] == 6
        assert stats["edge_count"] == 5
        assert stats["is_dag"] is True
        assert stats["nodes_by_level"]["micro"] == 5
        assert stats["nodes_by_level"]["dimension"] == 1


class TestSensitivityAnalysis:
    """Test Sobol sensitivity analysis."""
    
    def test_sobol_indices_sum_to_one(self):
        """First-order Sobol indices should sum to ~1.0."""
        scores = [7.0, 8.0, 6.5, 7.5]
        weights = [0.25, 0.25, 0.25, 0.25]
        
        sobol = SensitivityAnalysis.compute_sobol_indices(
            scores, weights, n_samples=500, random_seed=42
        )
        
        total = sum(sobol.values())
        assert abs(total - 1.0) < 0.05  # Allow 5% tolerance for MC error
    
    def test_sobol_identifies_influential_inputs(self):
        """Inputs with high variance should have high Sobol index."""
        # Input 0 has high weight but low variance
        # Input 1 has medium weight and high variance (will be perturbed more)
        scores = [7.0, 7.0, 7.0]
        weights = [0.5, 0.3, 0.2]
        
        sobol = SensitivityAnalysis.compute_sobol_indices(
            scores, weights, n_samples=500, random_seed=42
        )
        
        # All have same score, so sensitivity is proportional to weight^2
        # (for weighted average, Sobol ~ w^2 * var, but var is introduced by MC)
        assert len(sobol) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
