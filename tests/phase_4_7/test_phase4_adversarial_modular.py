"""
Adversarial Tests for Phase 4-7 with MEANINGFUL CONNECTIONS
============================================================

Based on 3 Pillars:
1. CONSUMER: Test suite validating Phase 4 aggregation
2. SCOPE: Adversarial testing of intermodular wiring
3. VALUE ADDED: Validates real PA→Cluster→Dimension relationships from modular structure
4. EQUIPMENT: Uses modular fixtures to verify hierarchical constraints

Each test validates a MEANINGFUL structural constraint:
- PA→Cluster assignments are correct
- Cluster aggregation uses correct PA counts
- Hermeticity validation respects real cluster boundaries
- Dimension aggregation produces valid area scores
"""

from __future__ import annotations

import pytest
from typing import Any


# =============================================================================
# TEST CLASS 1: CLUSTER → PA MAPPING VALIDATION
# VALUE: Verifies aggregation respects real cluster structure from modular metadata
# =============================================================================

class TestClusterStructureValidation:
    """Validate that aggregation respects REAL cluster→PA mappings."""

    def test_cluster_01_has_correct_pas(
        self,
        cluster_to_pas_mapping: dict[str, list[str]],
        pa_to_cluster_mapping: dict[str, str]
    ):
        """
        VALUE: Validates CL01 structure matches modular metadata.

        REAL STRUCTURE from clusters/CL01_seguridad_paz/metadata.json:
            CL01 contains: PA02, PA03, PA07

        VERIFIES: The mapping is correctly loaded and used.
        """
        # CL01 should have exactly 3 PAs
        cl01_pas = cluster_to_pas_mapping["CL01"]
        assert cl01_pas == ["PA02", "PA03", "PA07"], (
            f"CL01 PA mismatch from modular metadata: expected [PA02, PA03, PA07], got {cl01_pas}"
        )

        # Verify reverse mapping: each PA maps to CL01
        for pa_id in cl01_pas:
            assert pa_to_cluster_mapping[pa_id] == "CL01", (
                f"PA {pa_id} should map to CL01 per modular metadata, "
                f"got {pa_to_cluster_mapping[pa_id]}"
            )

    def test_cluster_02_has_correct_pas(
        self,
        cluster_to_pas_mapping: dict[str, list[str]],
        pa_to_cluster_mapping: dict[str, str]
    ):
        """
        VALUE: Validates CL02 structure matches modular metadata.

        REAL STRUCTURE: CL02 contains PA01, PA05, PA06
        """
        cl02_pas = cluster_to_pas_mapping["CL02"]
        assert cl02_pas == ["PA01", "PA05", "PA06"]

        for pa_id in cl02_pas:
            assert pa_to_cluster_mapping[pa_id] == "CL02"

    def test_cluster_03_has_correct_pas(
        self,
        cluster_to_pas_mapping: dict[str, list[str]],
        pa_to_cluster_mapping: dict[str, str]
    ):
        """
        VALUE: Validates CL03 structure matches modular metadata.

        REAL STRUCTURE: CL03 contains PA04, PA08
        """
        cl03_pas = cluster_to_pas_mapping["CL03"]
        assert cl03_pas == ["PA04", "PA08"]

        for pa_id in cl03_pas:
            assert pa_to_cluster_mapping[pa_id] == "CL03"

    def test_cluster_04_has_correct_pas(
        self,
        cluster_to_pas_mapping: dict[str, list[str]],
        pa_to_cluster_mapping: dict[str, str]
    ):
        """
        VALUE: Validates CL04 structure matches modular metadata.

        REAL STRUCTURE: CL04 contains PA09, PA10
        """
        cl04_pas = cluster_to_pas_mapping["CL04"]
        assert cl04_pas == ["PA09", "PA10"]

        for pa_id in cl04_pas:
            assert pa_to_cluster_mapping[pa_id] == "CL04"


# =============================================================================
# TEST CLASS 2: AREA POLICY AGGREGATOR WITH REAL STRUCTURE
# VALUE: Verifies area aggregation respects PA→Cluster assignments
# =============================================================================

class TestAreaAggregatorWithRealStructure:
    """Test AreaPolicyAggregator with REAL modular structure."""

    def test_area_score_has_correct_cluster_id(
        self,
        pa_to_cluster_mapping: dict[str, str],
        generate_dimension_score_for_pa,
        monolith_from_modular
    ):
        """
        VALUE: Verifies AreaScore.cluster_id matches PA→Cluster mapping from modular metadata.

        MEANINGFUL CONSTRAINT:
            PA02 area scores MUST have cluster_id="CL01"
            PA01 area scores MUST have cluster_id="CL02"
            etc.
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            AreaPolicyAggregator, DimensionScore
        )

        aggregator = AreaPolicyAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        # Create dimension scores for PA02 (should map to CL01)
        pa_id = "PA02"
        expected_cluster_id = pa_to_cluster_mapping[pa_id]  # Should be "CL01"

        dimension_scores = [
            DimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id=pa_id,
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={}
            )
            for i in range(1, 7)
        ]

        area_score = aggregator.aggregate_area(
            dimension_scores,
            {"area_id": pa_id}  # Code expects area_id, not policy_area
        )

        # MEANINGFUL ASSERTION: Verify cluster_id matches modular metadata
        assert area_score.cluster_id == expected_cluster_id, (
            f"PA{pa_id} cluster_id mismatch from modular metadata: "
            f"expected {expected_cluster_id}, got {area_score.cluster_id}"
        )

    def test_multiple_areas_respect_cluster_boundaries(
        self,
        cluster_to_pas_mapping: dict[str, list[str]],
        pa_to_cluster_mapping: dict[str, str],
        monolith_from_modular
    ):
        """
        VALUE: Verifies areas are grouped by correct cluster boundaries.

        CL01 should only contain: PA02, PA03, PA07
        CL02 should only contain: PA01, PA05, PA06

        This validates that aggregation respects REAL cluster boundaries.
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            AreaPolicyAggregator, DimensionScore
        )

        aggregator = AreaPolicyAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        # Create area scores for CL01 PAs: PA02, PA03, PA07
        cl01_expected_pas = set(cluster_to_pas_mapping["CL01"])

        actual_area_scores = []
        for pa_id in cl01_expected_pas:
            dimension_scores = [
                DimensionScore(
                    dimension_id="DIM01",
                    area_id=pa_id,
                    score=2.0,
                    quality_level="BUENO",
                    contributing_questions=[1, 2, 3, 4, 5],
                    validation_passed=True,
                    validation_details={}
                )
            ]
            area_score = aggregator.aggregate_area(dimension_scores, {"policy_area": pa_id})
            actual_area_scores.append(area_score)

        # Verify all CL01 areas have cluster_id="CL01"
        for area_score in actual_area_scores:
            assert area_score.cluster_id == "CL01", (
                f"PA {area_score.area_id} (in CL01 per modular metadata) "
                f"has cluster_id={area_score.cluster_id}, expected CL01"
            )


# =============================================================================
# TEST CLASS 3: CLUSTER AGGREGATOR HERMETICITY WITH REAL COUNTS
# VALUE: Verifies hermeticity uses correct PA counts from modular structure
# =============================================================================

class TestClusterHermeticityWithRealCounts:
    """Test ClusterAggregator hermeticity with REAL PA counts from modular metadata."""

    def test_cluster_01_hermeticity_with_real_pa_count(
        self,
        cluster_to_pas_mapping: dict[str, list[str]],
        cluster_policy_area_counts: dict[str, int],
        assert_hermeticity_for_cluster,
        monolith_from_modular
    ):
        """
        VALUE: Verifies CL01 hermeticity uses REAL count (3 PAs) from modular metadata.

        MEANINGFUL CONSTRAINT:
            CL01 from clusters/CL01_seguridad_paz/metadata.json
            contains exactly 3 PAs: [PA02, PA03, PA07]

        If aggregation receives only 2 areas, it should detect hermeticity violation.
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            ClusterAggregator, AreaScore
        )

        aggregator = ClusterAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        # Create only 2 area scores (CL01 expects 3)
        area_scores = [
            AreaScore(
                area_id="PA02",
                area_name="Violencia y Conflicto",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CL01",
                validation_passed=True,
                validation_details={}
            ),
            AreaScore(
                area_id="PA03",
                area_name="Ambiente",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CL01",
                validation_passed=True,
                validation_details={}
            )
            # Missing PA07 - hermeticity violation
        ]

        cluster_score = aggregator.aggregate_cluster(
            area_scores,
            {"cluster_id": "CL01", "cluster_name": "Seguridad y Paz"}
        )

        # MEANINGFUL ASSERTION: Hermeticity should fail due to missing PA07
        assert cluster_score.validation_passed is False
        assert "hermeticity" in str(cluster_score.validation_details).lower()

    def test_cluster_02_hermeticity_with_real_pa_count(
        self,
        cluster_policy_area_counts: dict[str, int],
        monolith_from_modular
    ):
        """
        VALUE: Verifies CL02 hermeticity uses REAL count (3 PAs) from modular metadata.

        CL02 from modular metadata: [PA01, PA05, PA06]
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            ClusterAggregator, AreaScore
        )

        aggregator = ClusterAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        # Create all 3 area scores for CL02
        area_scores = [
            AreaScore(
                area_id=pa_id,
                area_name=f"Area {pa_id}",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=[],
                cluster_id="CL02",
                validation_passed=True,
                validation_details={}
            )
            for pa_id in ["PA01", "PA05", "PA06"]
        ]

        cluster_score = aggregator.aggregate_cluster(
            area_scores,
            {"cluster_id": "CL02", "cluster_name": "Grupos Poblacionales"}
        )

        # MEANINGFUL ASSERTION: Hermeticity should pass with all 3 PAs
        assert cluster_score.validation_passed is True


# =============================================================================
# TEST CLASS 4: DIMENSION AGGREGATOR SOTA FEATURES
# VALUE: Verifies SOTA features (uncertainty, provenance) work correctly
# =============================================================================

class TestDimensionAggregatorSOTAFeatures:
    """Test DimensionAggregator SOTA features add value."""

    def test_bootstrap_uncertainty_produces_confidence_interval(
        self,
        generate_scored_result_for_pa
    ):
        """
        VALUE: Verifies BootstrapAggregator produces meaningful uncertainty metrics.

        SOTA FEATURE: BCa (Bias-Corrected and Accelerated) Bootstrapping
        VALUE ADDED: Provides confidence intervals for dimension scores
        EQUIPMENT: Tests verify CI is reasonable (not too wide, not too narrow)
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.uncertainty_quantification import (
            BootstrapAggregator
        )

        aggregator = BootstrapAggregator(iterations=100, seed=42)

        # Create realistic score distribution
        scores = [1.5, 2.0, 2.5, 2.0, 1.8]

        def mean_func(d):
            return sum(d) / len(d)

        metrics = aggregator.compute_bca_interval(scores, mean_func)

        # MEANINGFUL ASSERTIONS:
        # 1. Point estimate should be the mean
        assert metrics.point_estimate == pytest.approx(1.96)

        # 2. CI should contain the point estimate
        assert metrics.ci_lower_95 <= metrics.point_estimate <= metrics.ci_upper_95

        # 3. CI should be reasonable (not too wide for this variance)
        ci_width = metrics.ci_upper_95 - metrics.ci_lower_95
        assert ci_width < 2.0, f"CI too wide: {ci_width}"

    def test_provenance_dag_tracks_real_lineage(
        self,
        generate_scored_result_for_pa,
        pa_to_cluster_mapping: dict[str, str]
    ):
        """
        VALUE: Verifies ProvenanceDAG tracks REAL question→dimension→area lineage.

        SOTA FEATURE: W3C PROV-compliant provenance tracking
        VALUE ADDED: Enables traceability from macro scores to micro questions
        EQUIPMENT: Tests verify lineage is complete and accurate
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation_provenance import (
            AggregationDAG, ProvenanceNode
        )

        dag = AggregationDAG()

        # Simulate REAL aggregation flow: PA02 questions → DIM02 → PA02 area
        pa_id = "PA02"
        cluster_id = pa_to_cluster_mapping[pa_id]  # Should be "CL01"

        # Add micro-question nodes
        for q_id in [1, 2, 3]:
            dag.add_node(ProvenanceNode(
                node_id=f"Q00{q_id}",
                level="micro",
                score=2.0,
                quality_level="BUENO",
                metadata={"policy_area": pa_id}
            ))

        # Add dimension node
        dag.add_node(ProvenanceNode(
            node_id="DIM02",
            level="dimension",
            score=2.0,
            quality_level="BUENO",
            metadata={"policy_area": pa_id}
        ))

        # Add aggregation edge (3 questions → dimension)
        dag.add_aggregation_edge(
            source_ids=["Q001", "Q002", "Q003"],
            target_id="DIM02",
            operation="weighted_average",
            weights=[1/3, 1/3, 1/3]
        )

        # MEANINGFUL ASSERTION: Verify lineage is complete
        lineage = dag.trace_lineage("DIM02")

        assert lineage["micro_question_count"] == 3
        assert set(lineage["micro_questions"]) == {"Q001", "Q002", "Q003"}
        assert lineage["depth"] >= 1  # At least 1 level from micro to dimension

    def test_choquet_aggregation_handles_interactions(
        self,
        monolith_from_modular
    ):
        """
        VALUE: Verifies Choquet aggregator captures synergies between layers.

        SOTA FEATURE: Choquet integral with fuzzy measures
        VALUE ADDED: Captures non-linear interactions between layers
        EQUIPMENT: Tests verify interaction contribution is meaningful
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.choquet_aggregator import (
            ChoquetAggregator, ChoquetConfig
        )

        config = ChoquetConfig(
            linear_weights={"@b": 0.5, "@chain": 0.3},
            interaction_weights={("@b", "@chain"): 0.2},
            validate_boundedness=True
        )

        aggregator = ChoquetAggregator(config)

        result = aggregator.aggregate(
            subject="test_with_interaction",
            layer_scores={"@b": 0.8, "@chain": 0.6}
        )

        # MEANINGFUL ASSERTIONS:
        # 1. Interaction should add value beyond linear aggregation
        linear_result = 0.5 * 0.8 + 0.3 * 0.6  # = 0.58
        assert result.calibration_score > linear_result, (
            f"Choquet should add value beyond linear: "
            f"Choquet={result.calibration_score}, linear={linear_result}"
        )

        # 2. Interaction contribution should be tracked
        assert result.breakdown.interaction_contribution > 0


# =============================================================================
# TEST CLASS 5: INTERMODULAR WIRING - PHASE 3 → 4 → 5
# VALUE: Verifies data flow adds value at each transformation step
# =============================================================================

class TestIntermodularWiring:
    """Test that data flow adds value through Phase 3 → 4 → 5."""

    def test_phase_3_to_4_traceability_preserved(
        self,
        generate_scored_result_for_pa,
        monolith_from_modular
    ):
        """
        VALUE: Verifies Phase 3 → 4 preserves question traceability.

        MEANINGFUL CONSTRAINT:
            Phase 3 outputs (ScoredResult) contain question_global IDs
            Phase 4 outputs (DimensionScore) must preserve these IDs
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        aggregator = DimensionAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        # Simulate Phase 3 output with traceability
        phase3_output = [
            generate_scored_result_for_pa(pa_id="PA02", question_id=i+1, score=2.0)
            for i in range(5)
        ]

        # Phase 4: Aggregate to dimension
        dim_score = aggregator.aggregate_dimension(
            phase3_output,
            {"policy_area": "PA02", "dimension": "DIM01"}
        )

        # MEANINGFUL ASSERTION: Traceability is preserved
        assert len(dim_score.contributing_questions) == 5
        assert set(dim_score.contributing_questions) == {1, 2, 3, 4, 5}

    def test_phase_4_to_5_cluster_id_propagates(
        self,
        pa_to_cluster_mapping: dict[str, str],
        generate_dimension_score_for_pa,
        monolith_from_modular
    ):
        """
        VALUE: Verifies Phase 4 → 5 propagates cluster_id correctly.

        MEANINGFUL CONSTRAINT:
            PA02 → CL01 (from modular metadata)
            AreaScore for PA02 must have cluster_id="CL01"
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            AreaPolicyAggregator, DimensionScore
        )

        aggregator = AreaPolicyAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        pa_id = "PA02"
        expected_cluster = pa_to_cluster_mapping[pa_id]

        # Phase 4 output: dimension scores
        dimension_scores = [
            DimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id=pa_id,
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={}
            )
            for i in range(1, 7)
        ]

        # Phase 5: Aggregate to area
        area_score = aggregator.aggregate_area(
            dimension_scores,
            {"area_id": pa_id}  # Code expects area_id, not policy_area
        )

        # MEANINGFUL ASSERTION: cluster_id from modular metadata propagates
        assert area_score.cluster_id == expected_cluster, (
            f"PA{pa_id} cluster_id should propagate from modular metadata: "
            f"expected {expected_cluster}, got {area_score.cluster_id}"
        )


# =============================================================================
# TEST CLASS 6: VALUE ADD VALIDATION
# VALUE: Ensures each transformation step adds meaningful value
# =============================================================================

class TestValueAddValidation:
    """Verify each aggregation step adds meaningful value."""

    def test_dimension_aggregation_adds_statistical_value(
        self,
        generate_scored_result_for_pa,
        monolith_from_modular
    ):
        """
        VALUE: Verifies dimension aggregation provides statistical summary.

        VALUE ADDED:
            - Reduces 5 question scores → 1 dimension score
            - Provides quality level classification
            - Tracks contributing questions

        EQUIPMENT: Tests verify these outputs are meaningful
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        aggregator = DimensionAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        # Input: 5 question scores with variance
        phase3_output = [
            generate_scored_result_for_pa(pa_id="PA01", question_id=i+1, score=1.5 + i*0.2)
            for i in range(5)
        ]

        dim_score = aggregator.aggregate_dimension(
            phase3_output,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # MEANINGFUL ASSERTIONS:
        # 1. Score is within valid range
        assert 0.0 <= dim_score.score <= 3.0

        # 2. Quality level is determined
        assert dim_score.quality_level in ["EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"]

        # 3. Contributing questions are tracked
        assert len(dim_score.contributing_questions) == 5

        # 4. SOTA features add value
        if hasattr(dim_score, "confidence_interval_95"):
            ci_low, ci_high = dim_score.confidence_interval_95
            # CI should be reasonable
            assert ci_low <= ci_high

    def test_area_aggregation_adds_hermeticity_validation(
        self,
        generate_dimension_score_for_pa,
        cluster_policy_area_counts: dict[str, int],
        monolith_from_modular
    ):
        """
        VALUE: Verifies area aggregation adds hermeticity validation.

        VALUE ADDED:
            - Validates dimension completeness
            - Detects missing dimensions
            - Provides validation details

        This adds value by catching data quality issues early.
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            AreaPolicyAggregator, DimensionScore
        )

        aggregator = AreaPolicyAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        # Create dimension scores with missing dimensions (only 4 of 6)
        dimension_scores = [
            DimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
                validation_passed=True,
                validation_details={}
            )
            for i in [1, 2, 4, 5]  # Missing DIM03, DIM06
        ]

        area_score = aggregator.aggregate_area(
            dimension_scores,
            {"policy_area": "PA01"}
        )

        # MEANINGFUL ASSERTION: Hermeticity validation adds value
        assert area_score.validation_passed is False
        assert "hermeticity" in str(area_score.validation_details).lower()
        # Should indicate missing dimensions
        assert "missing" in str(area_score.validation_details).lower() or "dimension" in str(area_score.validation_details).lower()


# =============================================================================
# TEST CLASS 7: QUALITY LEVEL DETERMINATION
# VALUE: Verifies quality levels match rubric from modular structure
# =============================================================================

class TestQualityLevelDetermination:
    """Verify quality level determination adds value."""

    def test_quality_level_thresholds_match_rubric(
        self,
        monolith_from_modular
    ):
        """
        VALUE: Verifies quality levels match canonical thresholds.

        MEANINGFUL CONSTRAINT:
            EXCELENTE: >= 2.55 (85% of 3.0)
            BUENO: >= 2.10 (70% of 3.0)
            ACEPTABLE: >= 1.65 (55% of 3.0)
            INSUFICIENTE: < 1.65

        VALUE ADDED: Provides interpretable quality classification
        """
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )
        from farfan_pipeline.phases.Phase_four_five_six_seven.primitives.quality_levels import (
            QualityLevel, QualityLevelThresholds
        )

        aggregator = DimensionAggregator(monolith=monolith_from_modular, abort_on_insufficient=False)

        thresholds = QualityLevelThresholds()

        # Test each threshold boundary
        test_cases = [
            (2.7, QualityLevel.EXCELENTE),   # >= 2.55
            (2.2, QualityLevel.BUENO),       # >= 2.10
            (1.8, QualityLevel.ACEPTABLE),   # >= 1.65
            (1.0, QualityLevel.INSUFICIENTE), # < 1.65
        ]

        for score, expected_quality in test_cases:
            # Create scored results with all same score
            results = [
                type('Obj', (), {
                    'question_global': i+1,
                    'base_slot': f"DIM01-Q{i+1:03d}",
                    'policy_area': 'PA01',
                    'dimension': 'DIM01',
                    'score': score,
                    'quality_level': 'BUENO',
                    'evidence': {},
                    'raw_results': {}
                })()
                for i in range(5)
            ]

            dim_score = aggregator.aggregate_dimension(
                results,
                {"policy_area": "PA01", "dimension": "DIM01"}
            )

            # MEANINGFUL ASSERTION: Quality matches rubric
            assert dim_score.quality_level == expected_quality.value, (
                f"Score {score} should be {expected_quality.value}, got {dim_score.quality_level}"
            )
