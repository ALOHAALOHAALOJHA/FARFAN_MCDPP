"""
Integration Test for Full Aggregation Pipeline (Phases 4-7) with Orchestrator

This test validates that the aggregation pipeline:
1. Produces non-empty results at each phase
2. Maintains traceability from micro questions to macro score
3. Generates non-zero macro scores for valid inputs
4. Fails hard when results are empty or invalid
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path
from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.aggregation import (
    DimensionAggregator,
    AreaPolicyAggregator,
    ClusterAggregator,
    MacroAggregator,
    ScoredResult,
    AggregationSettings,
)
from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.aggregation_validation import (
    validate_full_aggregation_pipeline,
    AggregationValidationError,
)


@pytest.fixture
def real_monolith():
    """Load real questionnaire monolith."""
    monolith_path = (
        Path(__file__).resolve().parent.parent
        / "canonic_questionnaire_central"
        / "questionnaire_monolith.json"
    )
    with open(monolith_path, "r") as f:
        return json.load(f)


@pytest.fixture
def synthetic_phase3_output(real_monolith):
    """
    Create synthetic Phase 3 output (scored micro questions).

    Generates realistic data for all PA×DIM combinations with varying scores.
    """
    policy_areas = real_monolith["blocks"]["niveles_abstraccion"]["policy_areas"]
    scored_results = []
    question_counter = 1

    for pa in policy_areas:
        pa_id = pa.get("policy_area_id") or pa.get("id")
        dim_ids = pa.get("dimension_ids", [])

        for dim_id in dim_ids:
            # Create 5 questions per dimension (standard)
            for q_idx in range(1, 6):
                # Vary scores to create realistic distribution
                base_score = 2.0 + (question_counter % 5) * 0.2
                scored_results.append(
                    ScoredResult(
                        question_global=f"Q{question_counter:03d}",
                        base_slot=f"{dim_id}-Q{q_idx:03d}",
                        policy_area=pa_id,
                        dimension=dim_id,
                        score=base_score,
                        quality_level="ACEPTABLE" if base_score >= 1.5 else "INSUFICIENTE",
                        evidence={},
                        raw_results={},
                    )
                )
                question_counter += 1

    return scored_results


class TestFullAggregationPipelineIntegration:
    """Integration tests for complete aggregation pipeline."""

    def test_full_pipeline_with_real_monolith(self, real_monolith, synthetic_phase3_output):
        """
        Test full aggregation pipeline with real monolith produces non-trivial results.

        This is the primary integration test verifying:
        - All phases execute without errors
        - Results are non-empty at each phase
        - Macro score is non-zero for valid inputs
        - Traceability is maintained throughout
        """
        settings = AggregationSettings.from_monolith(real_monolith)

        # PHASE 4: Dimension Aggregation
        dim_agg = DimensionAggregator(
            monolith=real_monolith,
            abort_on_insufficient=False,
            aggregation_settings=settings,
            enable_sota_features=False,
        )
        dimension_scores = dim_agg.run(
            synthetic_phase3_output, group_by_keys=settings.dimension_group_by_keys
        )

        # Assertions for Phase 4
        assert len(dimension_scores) > 0, "Phase 4 returned empty dimension scores"
        assert (
            len(dimension_scores) == 60
        ), f"Expected 60 dimensions (6×10), got {len(dimension_scores)}"

        # Verify traceability
        sample_dim = dimension_scores[0]
        assert (
            len(sample_dim.contributing_questions) > 0
        ), "Dimension score not traceable to micro questions"

        # PHASE 5: Area Policy Aggregation
        area_agg = AreaPolicyAggregator(
            monolith=real_monolith, abort_on_insufficient=False, aggregation_settings=settings
        )
        area_scores = area_agg.run(dimension_scores, group_by_keys=settings.area_group_by_keys)

        # Assertions for Phase 5
        assert len(area_scores) > 0, "Phase 5 returned empty area scores"
        assert len(area_scores) == 10, f"Expected 10 policy areas, got {len(area_scores)}"

        # Verify traceability
        sample_area = area_scores[0]
        assert len(sample_area.dimension_scores) > 0, "Area score not traceable to dimension scores"

        # PHASE 6: Cluster Aggregation
        cluster_agg = ClusterAggregator(
            monolith=real_monolith, abort_on_insufficient=False, aggregation_settings=settings
        )
        cluster_definitions = real_monolith["blocks"]["niveles_abstraccion"]["clusters"]
        cluster_scores = cluster_agg.run(area_scores, cluster_definitions)

        # Assertions for Phase 6
        assert len(cluster_scores) > 0, "Phase 6 returned empty cluster scores"
        assert len(cluster_scores) == 4, f"Expected 4 clusters, got {len(cluster_scores)}"

        # Verify traceability
        sample_cluster = cluster_scores[0]
        assert len(sample_cluster.area_scores) > 0, "Cluster score not traceable to area scores"

        # PHASE 7: Macro Evaluation
        macro_agg = MacroAggregator(
            monolith=real_monolith, abort_on_insufficient=False, aggregation_settings=settings
        )
        macro_score = macro_agg.evaluate_macro(
            cluster_scores=cluster_scores,
            area_scores=area_scores,
            dimension_scores=dimension_scores,
        )

        # Assertions for Phase 7
        assert (
            macro_score.score > 0
        ), f"Macro score is ZERO despite valid inputs: {macro_score.score}"
        assert 0 <= macro_score.score <= 3, f"Macro score outside valid range: {macro_score.score}"
        assert len(macro_score.cluster_scores) > 0, "Macro score not traceable to cluster scores"

        # Validate full pipeline
        all_passed, validation_results = validate_full_aggregation_pipeline(
            dimension_scores, area_scores, cluster_scores, macro_score, synthetic_phase3_output
        )

        # Collect all validation errors for detailed reporting
        if not all_passed:
            error_msgs = []
            for result in validation_results:
                if not result.passed:
                    error_msgs.append(f"{result.phase}: {result.error_message}")
            pytest.fail("Pipeline validation failed:\n" + "\n".join(error_msgs))

        assert all_passed, "Full pipeline validation failed"

    def test_empty_phase4_output_fails_validation(self, real_monolith):
        """
        Test that empty Phase 4 output triggers hard failure.

        Verifies that the validation catches empty aggregation results.
        """
        from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.aggregation_validation import (
            validate_phase4_output,
        )

        scored_results = [
            ScoredResult(
                question_global="Q001",
                base_slot="DIM01-Q001",
                policy_area="PA01",
                dimension="DIM01",
                score=2.0,
                quality_level="ACEPTABLE",
                evidence={},
                raw_results={},
            )
        ]

        # Simulate empty dimension scores (broken aggregation)
        validation_result = validate_phase4_output([], scored_results)

        assert not validation_result.passed
        assert "EMPTY" in validation_result.error_message

    def test_score_traceability_chain(self, real_monolith, synthetic_phase3_output):
        """
        Test traceability chain: micro → dimension → area → cluster → macro.

        Verifies that each aggregation level properly traces to its source.
        """
        settings = AggregationSettings.from_monolith(real_monolith)

        # Run full pipeline
        dim_agg = DimensionAggregator(
            monolith=real_monolith,
            abort_on_insufficient=False,
            aggregation_settings=settings,
            enable_sota_features=False,
        )
        dimension_scores = dim_agg.run(
            synthetic_phase3_output, group_by_keys=settings.dimension_group_by_keys
        )

        area_agg = AreaPolicyAggregator(
            monolith=real_monolith, abort_on_insufficient=False, aggregation_settings=settings
        )
        area_scores = area_agg.run(dimension_scores, group_by_keys=settings.area_group_by_keys)

        cluster_agg = ClusterAggregator(
            monolith=real_monolith, abort_on_insufficient=False, aggregation_settings=settings
        )
        cluster_definitions = real_monolith["blocks"]["niveles_abstraccion"]["clusters"]
        cluster_scores = cluster_agg.run(area_scores, cluster_definitions)

        macro_agg = MacroAggregator(
            monolith=real_monolith, abort_on_insufficient=False, aggregation_settings=settings
        )
        macro_score = macro_agg.evaluate_macro(
            cluster_scores=cluster_scores,
            area_scores=area_scores,
            dimension_scores=dimension_scores,
        )

        # Verify traceability chain
        # Dimension → Micro
        dim_sample = dimension_scores[0]
        assert (
            len(dim_sample.contributing_questions) > 0
        ), "Dimension not traceable to micro questions"

        # Area → Dimension
        area_sample = area_scores[0]
        assert len(area_sample.dimension_scores) > 0, "Area not traceable to dimensions"

        # Cluster → Area
        cluster_sample = cluster_scores[0]
        assert len(cluster_sample.area_scores) > 0, "Cluster not traceable to areas"

        # Macro → Cluster
        assert len(macro_score.cluster_scores) > 0, "Macro not traceable to clusters"

        # Full chain: Can we trace from macro back to at least one micro question?
        # Macro → Cluster
        first_cluster = macro_score.cluster_scores[0]
        # Cluster → Area (from cluster_scores list, not macro_score.cluster_scores)
        cluster_with_areas = next(
            cs for cs in cluster_scores if cs.cluster_id == first_cluster.cluster_id
        )
        first_area_from_cluster = cluster_with_areas.area_scores[0]
        # Area → Dimension
        first_dimension = first_area_from_cluster.dimension_scores[0]
        # Dimension → Micro
        first_micro_question = first_dimension.contributing_questions[0]

        assert first_micro_question, "Failed to trace from macro to micro questions"

    def test_aggregation_with_mixed_quality_scores(self, real_monolith):
        """
        Test aggregation with mixed quality scores (some high, some low).

        Verifies that aggregation properly handles diverse score distributions.
        """
        settings = AggregationSettings.from_monolith(real_monolith)

        # Create mixed quality scores: some excellent, some insufficient
        scored_results = []
        for i in range(1, 31):
            # Alternate between high and low scores
            score = 2.8 if i % 2 == 0 else 0.5
            scored_results.append(
                ScoredResult(
                    question_global=f"Q{i:03d}",
                    base_slot=f"DIM0{(i-1)//5 + 1}-Q{i:03d}",
                    policy_area="PA01",
                    dimension=f"DIM0{(i-1)//5 + 1}",
                    score=score,
                    quality_level="EXCELENTE" if score > 2.5 else "INSUFICIENTE",
                    evidence={},
                    raw_results={},
                )
            )

        dim_agg = DimensionAggregator(
            monolith=real_monolith,
            abort_on_insufficient=False,
            aggregation_settings=settings,
            enable_sota_features=False,
        )
        dimension_scores = dim_agg.run(
            scored_results, group_by_keys=settings.dimension_group_by_keys
        )

        assert len(dimension_scores) > 0, "Aggregation failed with mixed quality scores"

        # Verify that scores reflect the mix (should be somewhere in between)
        avg_score = sum(ds.score for ds in dimension_scores) / len(dimension_scores)
        assert 0.5 < avg_score < 2.8, f"Average score doesn't reflect input mix: {avg_score}"


@pytest.mark.updated
class TestAggregationEdgeCases:
    """Test edge cases for aggregation pipeline."""

    def test_aggregation_with_minimum_valid_data(self, real_monolith):
        """Test aggregation with minimum required data (1 dimension, 1 area, 1 cluster)."""
        settings = AggregationSettings.from_monolith(real_monolith)

        # Minimum data: 5 questions for 1 dimension
        scored_results = [
            ScoredResult(
                question_global=f"Q{i:03d}",
                base_slot=f"DIM01-Q{i:03d}",
                policy_area="PA01",
                dimension="DIM01",
                score=2.0,
                quality_level="ACEPTABLE",
                evidence={},
                raw_results={},
            )
            for i in range(1, 6)
        ]

        dim_agg = DimensionAggregator(
            monolith=real_monolith,
            abort_on_insufficient=False,
            aggregation_settings=settings,
            enable_sota_features=False,
        )
        dimension_scores = dim_agg.run(
            scored_results, group_by_keys=settings.dimension_group_by_keys
        )

        assert len(dimension_scores) == 1, "Failed with minimum valid data"
        assert dimension_scores[0].score > 0, "Score is zero with valid inputs"

    def test_aggregation_with_boundary_scores(self, real_monolith):
        """Test aggregation with boundary values (0.0 and 3.0)."""
        settings = AggregationSettings.from_monolith(real_monolith)

        # Test with minimum score (0.0)
        scored_results_min = [
            ScoredResult(
                question_global=f"Q{i:03d}",
                base_slot=f"DIM01-Q{i:03d}",
                policy_area="PA01",
                dimension="DIM01",
                score=0.0,
                quality_level="INSUFICIENTE",
                evidence={},
                raw_results={},
            )
            for i in range(1, 6)
        ]

        dim_agg = DimensionAggregator(
            monolith=real_monolith,
            abort_on_insufficient=False,
            aggregation_settings=settings,
            enable_sota_features=False,
        )
        dimension_scores_min = dim_agg.run(
            scored_results_min, group_by_keys=settings.dimension_group_by_keys
        )

        assert len(dimension_scores_min) == 1
        assert dimension_scores_min[0].score == 0.0, "Aggregation of zeros should yield zero"

        # Test with maximum score (3.0)
        scored_results_max = [
            ScoredResult(
                question_global=f"Q{i:03d}",
                base_slot=f"DIM01-Q{i:03d}",
                policy_area="PA01",
                dimension="DIM01",
                score=3.0,
                quality_level="EXCELENTE",
                evidence={},
                raw_results={},
            )
            for i in range(1, 6)
        ]

        dimension_scores_max = dim_agg.run(
            scored_results_max, group_by_keys=settings.dimension_group_by_keys
        )

        assert len(dimension_scores_max) == 1
        assert (
            abs(dimension_scores_max[0].score - 3.0) < 1e-10
        ), "Aggregation of max scores should yield max"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "updated"])
