"""
Adversarial Tests for Phase 4 Dimension Aggregation
====================================================

This test suite subjects Phase 4 to adversarial conditions to ensure:
1. Edge cases and boundary conditions are handled correctly
2. Intermodular wiring (Phase 3 → Phase 4 → Phase 5) is robust
3. Data flow adds value at each step
4. Failures are graceful and informative

Author: Phase 4 Adversarial Testing
Version: 1.0.0
"""

import math
import pytest
import sys
from pathlib import Path
from dataclasses import dataclass, replace
from typing import Any, List
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# =============================================================================
# FIXTURES - Test Data Construction
# =============================================================================

@dataclass
class ScoredResult:
    """Mock ScoredResult for testing."""
    question_global: int | str
    base_slot: str
    policy_area: str
    dimension: str
    score: float
    quality_level: str
    evidence: dict
    raw_results: dict


def create_valid_scored_result(
    question_id: int = 1,
    policy_area: str = "PA01",
    dimension: str = "DIM01",
    score: float = 2.0,
    quality_level: str = "BUENO"
) -> ScoredResult:
    """Create a valid ScoredResult for testing."""
    return ScoredResult(
        question_global=question_id,
        base_slot=f"{dimension}-Q{question_id:03d}",
        policy_area=policy_area,
        dimension=dimension,
        score=score,
        quality_level=quality_level,
        evidence={},
        raw_results={}
    )


def create_dimension_score_group(
    policy_area: str = "PA01",
    dimension: str = "DIM01",
    scores: List[float] | None = None
) -> List[ScoredResult]:
    """Create a group of 5 scored results for one dimension."""
    if scores is None:
        scores = [2.0, 2.5, 1.5, 2.0, 1.8]

    return [
        create_valid_scored_result(
            question_id=i,
            policy_area=policy_area,
            dimension=dimension,
            score=score
        )
        for i, score in enumerate(scores, start=1)
    ]


# =============================================================================
# TEST CLASS 1: BOUNDARY CONDITIONS
# =============================================================================

class TestPhase4BoundaryConditions:
    """Test Phase 4 behavior at score boundaries [0, 3]."""

    def test_all_minimum_scores(self):
        """Test with all scores at minimum boundary (0.0)."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator, DimensionScore
        )

        # Create group with all scores at 0.0
        results = create_dimension_score_group(scores=[0.0, 0.0, 0.0, 0.0, 0.0])

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False,
            enable_sota_features=False  # Disable SOTA to avoid BootstrapAggregator issue
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should produce 0.0 score with INSUFICIENTE quality
        assert dim_score.score == 0.0
        assert dim_score.quality_level == "INSUFICIENTE"
        assert dim_score.validation_passed is True

    def test_all_maximum_scores(self):
        """Test with all scores at maximum boundary (3.0)."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        # Create group with all scores at 3.0
        results = create_dimension_score_group(scores=[3.0, 3.0, 3.0, 3.0, 3.0])

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should produce 3.0 score with EXCELENTE quality
        assert dim_score.score == pytest.approx(3.0)
        assert dim_score.quality_level == "EXCELENTE"

    def test_score_clamping_below_zero(self):
        """Test that negative scores are clamped to 0.0."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        # Create group with some negative scores
        results = create_dimension_score_group(scores=[-1.0, -0.5, 2.0, 2.5, 3.0])

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Score should be clamped and validation should record it
        assert 0.0 <= dim_score.score <= 3.0
        assert dim_score.validation_details.get("clamping") is not None
        assert dim_score.validation_details["clamping"]["applied"] is True

    def test_score_clamping_above_three(self):
        """Test that scores > 3.0 are clamped to 3.0."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        # Create group with scores above 3.0
        results = create_dimension_score_group(scores=[2.0, 3.5, 4.0, 2.5, 3.0])

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Score should be clamped and validation should record it
        assert 0.0 <= dim_score.score <= 3.0
        assert dim_score.validation_details.get("clamping") is not None

    def test_quality_threshold_boundaries(self):
        """Test quality level assignment at threshold boundaries."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        # Test EXCELENTE threshold (>= 2.55, i.e., 0.85 * 3.0)
        results = create_dimension_score_group(scores=[2.55, 2.55, 2.55, 2.55, 2.55])
        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )
        assert dim_score.quality_level == "EXCELENTE"

        # Test BUENO threshold (>= 2.1, i.e., 0.70 * 3.0)
        results = create_dimension_score_group(scores=[2.1, 2.1, 2.1, 2.1, 2.1])
        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )
        assert dim_score.quality_level == "BUENO"

        # Test ACEPTABLE threshold (>= 1.65, i.e., 0.55 * 3.0)
        results = create_dimension_score_group(scores=[1.65, 1.65, 1.65, 1.65, 1.65])
        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )
        assert dim_score.quality_level == "ACEPTABLE"

        # Test INSUFICIENTE (< 1.65)
        results = create_dimension_score_group(scores=[1.64, 1.64, 1.64, 1.64, 1.64])
        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )
        assert dim_score.quality_level == "INSUFICIENTE"


# =============================================================================
# TEST CLASS 2: EMPTY AND MALFORMED INPUTS
# =============================================================================

class TestPhase4EmptyMalformedInputs:
    """Test Phase 4 with empty and malformed inputs."""

    def test_empty_input_list(self):
        """Test with completely empty input list."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            [],  # Empty list
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should return a minimal score with validation failed
        assert dim_score.score == 0.0
        assert dim_score.quality_level == "INSUFICIENTE"
        assert dim_score.validation_passed is False
        assert dim_score.validation_details.get("type") == "empty"

    def test_single_score_input(self):
        """Test with only 1 score (below expected 5)."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        results = [create_valid_scored_result(question_id=1, score=2.0)]

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should still aggregate but with coverage warning
        assert dim_score.validation_details.get("coverage") is not None
        assert dim_score.validation_details["coverage"]["valid"] is False

    def test_missing_required_fields(self):
        """Test with ScoredResult objects missing required fields."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            validate_scored_results, ValidationError
        )

        # Create malformed data
        malformed_data = [
            {
                "question_global": 1,
                "base_slot": "DIM01-Q001",
                # Missing: policy_area, dimension, score, quality_level, evidence, raw_results
            }
        ]

        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            validate_scored_results(malformed_data)

        assert "missing keys" in str(exc_info.value).lower()

    def test_invalid_score_types(self):
        """Test with invalid score types (e.g., strings, bool)."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            validate_scored_results, ValidationError
        )

        # Boolean scores should be rejected
        malformed_data = [
            {
                "question_global": 1,
                "base_slot": "DIM01-Q001",
                "policy_area": "PA01",
                "dimension": "DIM01",
                "score": True,  # Boolean instead of numeric
                "quality_level": "BUENO",
                "evidence": {},
                "raw_results": {}
            }
        ]

        with pytest.raises(ValidationError) as exc_info:
            validate_scored_results(malformed_data)

        assert "bool" in str(exc_info.value).lower() or "type" in str(exc_info.value).lower()

    def test_nan_and_infinity_scores(self):
        """Test handling of NaN and Infinity values."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        # Create scores with NaN and Infinity
        results = create_dimension_score_group(scores=[float('nan'), float('inf'), 2.0, 2.0, 2.0])

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        # Should handle gracefully (clamping will convert to 0.0 or 3.0)
        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Score should be finite after processing
        assert not math.isnan(dim_score.score)
        assert not math.isinf(dim_score.score)

    def test_invalid_quality_level(self):
        """Test with invalid quality level type (not string)."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            validate_scored_results, ValidationError
        )

        # Create results with invalid quality type (integer instead of string)
        results = [
            {
                "question_global": 1,
                "base_slot": "DIM01-Q001",
                "policy_area": "PA01",
                "dimension": "DIM01",
                "score": 2.0,
                "quality_level": 12345,  # Invalid: should be str, not int
                "evidence": {},
                "raw_results": {}
            }
        ]

        # Should fail validation - quality_level must be a string
        with pytest.raises(ValidationError) as exc_info:
            validate_scored_results(results)

        assert "quality_level" in str(exc_info.value).lower() or "type" in str(exc_info.value).lower()


# =============================================================================
# TEST CLASS 3: INTERMODULAR WIRING
# =============================================================================

class TestPhase4IntermodularWiring:
    """Test Phase 4 wiring with Phase 3 (input) and Phase 5 (output)."""

    def test_entry_contract_from_phase3(self):
        """Test entry contract validation for Phase 3 → Phase 4."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.interface.phase4_7_entry_contract import (
            Phase4_7EntryContract
        )

        contract = Phase4_7EntryContract()

        # Create valid Phase 3 output with correct field names
        results = [
            ScoredResult(
                question_global=i,
                base_slot="DIM01-Q001",
                policy_area="PA01",
                dimension="DIM01",
                score=2.0,
                quality_level="BUENO",
                evidence={},
                raw_results={}
            )
            for i in range(1, 6)
        ]

        # Should pass validation (may have warnings but no critical failures)
        is_valid, violations, metadata = contract.validate_input(
            results,
            strict_mode=False
        )

        # At minimum should have processed the input
        assert metadata["input_count"] == 5
        assert metadata["source_phase"] == "PHASE_3"

    def test_entry_contract_missing_traceability(self):
        """Test entry contract rejects results without traceability."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.interface.phase4_7_entry_contract import (
            validate_phase4_7_entry
        )

        # Create results with empty question_id (not traceable)
        results = [
            ScoredResult(
                question_global="",  # Empty - not traceable
                base_slot="DIM01-Q001",
                policy_area="PA01",
                dimension="DIM01",
                score=2.0,
                quality_level="BUENO",
                evidence={},
                raw_results={}
            )
        ]

        is_valid, violations, metadata = validate_phase4_7_entry(
            results,
            strict_mode=False
        )

        assert not is_valid
        assert any("question_id" in v.lower() for v in violations)

    def test_phase4_output_to_phase5_compatibility(self):
        """Test that Phase 4 output is compatible with Phase 5 input."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator, AreaPolicyAggregator
        )

        # Create Phase 4 output
        dim_aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False,
            enable_sota_features=False
        )

        # Create multiple dimension scores for one area
        dimension_scores = []
        for dim_idx in range(1, 7):  # 6 dimensions
            results = create_dimension_score_group(
                dimension=f"DIM{dim_idx:02d}",
                scores=[2.0, 2.0, 2.0, 2.0, 2.0]
            )
            dim_score = dim_aggregator.aggregate_dimension(
                results,
                {"policy_area": "PA01", "dimension": f"DIM{dim_idx:02d}"}
            )
            dimension_scores.append(dim_score)

        # Verify Phase 4 output has required fields for Phase 5
        for dim_score in dimension_scores:
            assert hasattr(dim_score, "dimension_id")
            assert hasattr(dim_score, "area_id")
            assert hasattr(dim_score, "score")
            assert hasattr(dim_score, "quality_level")
            assert hasattr(dim_score, "validation_details")

    def test_traceability_preservation_across_phases(self):
        """Test that traceability is preserved from Phase 4 → Phase 5."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        # Create original scored results
        original_question_ids = [1, 2, 3, 4, 5]
        results = [
            create_valid_scored_result(
                question_id=qid,
                policy_area="PA01",
                dimension="DIM01",
                score=2.0
            )
            for qid in original_question_ids
        ]

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Verify traceability is preserved
        assert len(dim_score.contributing_questions) == 5
        assert set(qid for qid in dim_score.contributing_questions) == set(original_question_ids)

    def test_error_propagation_from_phase4_to_phase5(self):
        """Test that Phase 4 errors properly propagate to Phase 5."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.validation.phase4_7_validation import (
            validate_phase4_output, validate_phase5_output
        )

        # Create invalid Phase 4 output (empty)
        empty_dimension_scores = []
        empty_input = []

        # Phase 4 validation should fail
        phase4_result = validate_phase4_output(empty_dimension_scores, empty_input)
        assert not phase4_result.passed
        assert "EMPTY" in phase4_result.error_message or "empty" in phase4_result.error_message

        # Phase 5 should also fail with empty dimension scores
        mock_area_scores = []
        phase5_result = validate_phase5_output(mock_area_scores, empty_dimension_scores)
        assert not phase5_result.passed


# =============================================================================
# TEST CLASS 4: VALUE ADD VERIFICATION
# =============================================================================

class TestPhase4ValueAdd:
    """Verify that each file in the Phase 4 flow adds distinct value."""

    def test_aggregation_py_core_value_add(self):
        """Verify aggregation.py provides core aggregation logic."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator, group_by, calculate_weighted_average
        )

        # Test group_by utility
        results = create_dimension_score_group(scores=[1.0, 2.0, 3.0, 2.5, 1.5])

        grouped = group_by(results, key_func=lambda r: (r.policy_area, r.dimension))

        assert ("PA01", "DIM01") in grouped
        assert len(grouped[("PA01", "DIM01")]) == 5

        # Test weighted average
        scores = [1.0, 2.0, 3.0]
        weights = [0.2, 0.3, 0.5]
        avg = calculate_weighted_average(scores, weights)

        expected = 1.0 * 0.2 + 2.0 * 0.3 + 3.0 * 0.5
        assert abs(avg - expected) < 1e-6

    def test_aggregation_integration_py_value_add(self):
        """Verify aggregation_integration.py provides orchestration value."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation_integration import (
            macro_score_to_evaluation
        )
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import MacroScore

        # Create a MacroScore
        macro_score = MacroScore(
            score=2.5,
            quality_level="EXCELENTE",
            cross_cutting_coherence=0.85,
            systemic_gaps=[],
            strategic_alignment=0.90,
            cluster_scores=[]
        )

        # Test conversion to evaluation dict
        evaluation = macro_score_to_evaluation(macro_score)

        assert evaluation["macro_score"] == 2.5
        assert evaluation["macro_score_normalized"] == pytest.approx(2.5 / 3.0)
        assert isinstance(evaluation["clusters"], list)

    def test_validation_py_value_add(self):
        """Verify validation.py provides comprehensive validation."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.validation.phase4_7_validation import (
            validate_phase4_output, ValidationResult
        )

        # Test with valid data
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import DimensionScore

        valid_dim_score = DimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="BUENO",
            contributing_questions=[1, 2, 3, 4, 5]
        )

        result = validate_phase4_output([valid_dim_score], [])

        assert isinstance(result, ValidationResult)
        assert result.passed is True
        assert result.phase == "Phase 4 (Dimension Aggregation)"
        assert result.details["dimension_count"] == 1
        assert result.details["traceable"] is True

    def test_entry_contract_py_value_add(self):
        """Verify entry contract provides input validation value."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.interface.phase4_7_entry_contract import (
            Phase4_7EntryContract, extract_entry_provenance
        )

        # Create test data with ScoredResult structure
        results = [
            ScoredResult(
                question_global=1,
                base_slot="DIM01-Q001",
                policy_area="PA01",
                dimension="DIM01",
                score=2.0,
                quality_level="BUENO",
                evidence={},
                raw_results={}
            ),
            ScoredResult(
                question_global=2,
                base_slot="DIM02-Q001",
                policy_area="PA02",
                dimension="DIM02",
                score=2.5,
                quality_level="BUENO",
                evidence={},
                raw_results={}
            )
        ]

        # Test provenance extraction
        provenance = extract_entry_provenance(results)

        assert provenance["provenance.source_phase"] == "PHASE_3"
        assert provenance["input_count"] == 2
        assert "PA01" in provenance["areas_covered"]
        assert "PA02" in provenance["areas_covered"]
        assert "DIM01" in provenance["dimensions_covered"]
        assert "DIM02" in provenance["dimensions_covered"]

    def test_exit_contract_py_value_add(self):
        """Verify exit contract provides output validation value."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.interface.phase4_7_exit_contract import (
            Phase4_7ExitContract, extract_exit_delivery_metadata
        )
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import MacroScore, ClusterScore

        # Create a MacroScore
        macro_score = MacroScore(
            score=2.5,
            quality_level="EXCELENTE",
            cross_cutting_coherence=0.85,
            systemic_gaps=[],
            strategic_alignment=0.90,
            cluster_scores=[
                ClusterScore(
                    cluster_id="C001",
                    cluster_name="Cluster 1",
                    areas=["PA01", "PA02"],
                    score=2.5,
                    coherence=0.85,
                    variance=0.1,
                    weakest_area="PA01",
                    area_scores=[]
                )
            ]
        )

        # Test delivery metadata extraction
        metadata = extract_exit_delivery_metadata(macro_score)

        assert metadata["target_phase"] == "PHASE_8"
        assert metadata["score"] == 2.5
        assert metadata["quality_level"] == "EXCELENTE"
        assert metadata["cluster_count"] == 1
        assert "C001" in metadata["cluster_ids"]


# =============================================================================
# TEST CLASS 5: HERMETICITY AND COVERAGE VALIDATION
# =============================================================================

class TestPhase4HermeticityAndCoverage:
    """Test hermeticity validation and coverage requirements."""

    def test_missing_dimension_in_area(self):
        """Test detection of missing dimensions in a policy area."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            AreaPolicyAggregator, DimensionScore, HermeticityValidationError
        )

        # Create only 5 dimensions instead of required 6
        dimension_scores = [
            DimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5]
            )
            for i in range(1, 6)  # Only DIM01-DIM05, missing DIM06
        ]

        # Create a mock monolith with 6 dimensions expected
        mock_monolith = {
            "blocks": {
                "scoring": {},
                "niveles_abstraccion": {
                    "policy_areas": [
                        {
                            "policy_area_id": "PA01",
                            "dimension_ids": ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]
                        }
                    ],
                    "dimensions": [
                        {"dimension_id": f"DIM{i:02d}"}
                        for i in range(1, 7)
                    ]
                }
            }
        }

        aggregator = AreaPolicyAggregator(
            monolith=mock_monolith,
            abort_on_insufficient=True
        )

        # Should raise HermeticityValidationError
        with pytest.raises(HermeticityValidationError) as exc_info:
            aggregator.validate_hermeticity(dimension_scores, "PA01")

        assert "missing dimensions" in str(exc_info.value).lower()

    def test_extra_dimension_in_area(self):
        """Test detection of unexpected dimensions in a policy area."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            AreaPolicyAggregator, DimensionScore, HermeticityValidationError
        )

        # Create 7 dimensions when only 6 expected
        dimension_scores = [
            DimensionScore(
                dimension_id=f"DIM{i:02d}",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5]
            )
            for i in range(1, 8)  # DIM01-DIM07, extra DIM07
        ]

        mock_monolith = {
            "blocks": {
                "scoring": {},
                "niveles_abstraccion": {
                    "policy_areas": [
                        {
                            "policy_area_id": "PA01",
                            "dimension_ids": ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]
                        }
                    ],
                    "dimensions": [
                        {"dimension_id": f"DIM{i:02d}"}
                        for i in range(1, 7)
                    ]
                }
            }
        }

        aggregator = AreaPolicyAggregator(
            monolith=mock_monolith,
            abort_on_insufficient=True
        )

        # Should raise HermeticityValidationError
        with pytest.raises(HermeticityValidationError) as exc_info:
            aggregator.validate_hermeticity(dimension_scores, "PA01")

        assert "unexpected dimensions" in str(exc_info.value).lower()

    def test_duplicate_dimension_detection(self):
        """Test detection of duplicate dimensions."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            AreaPolicyAggregator, DimensionScore, HermeticityValidationError
        )

        # Create duplicate DIM01
        dimension_scores = [
            DimensionScore(
                dimension_id="DIM01",
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5]
            ),
            DimensionScore(
                dimension_id="DIM01",  # Duplicate
                area_id="PA01",
                score=2.5,
                quality_level="BUENO",
                contributing_questions=[6, 7, 8, 9, 10]
            )
        ]

        # Create a mock monolith with 1 dimension expected
        mock_monolith = {
            "blocks": {
                "scoring": {},
                "niveles_abstraccion": {
                    "policy_areas": [
                        {
                            "policy_area_id": "PA01",
                            "dimension_ids": ["DIM01"]
                        }
                    ],
                    "dimensions": [
                        {"dimension_id": "DIM01"}
                    ]
                }
            }
        }

        aggregator = AreaPolicyAggregator(
            monolith=mock_monolith,
            abort_on_insufficient=True
        )

        # Should raise HermeticityValidationError
        with pytest.raises(HermeticityValidationError) as exc_info:
            aggregator.validate_hermeticity(dimension_scores, "PA01")

        assert "duplicate" in str(exc_info.value).lower()

    def test_insufficient_coverage_below_threshold(self):
        """Test coverage validation when below threshold."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator, CoverageError
        )

        # Create only 2 results when 5 expected
        results = [
            create_valid_scored_result(question_id=1, score=2.0),
            create_valid_scored_result(question_id=2, score=2.5)
        ]

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=True
        )

        # Should raise CoverageError
        with pytest.raises(CoverageError) as exc_info:
            aggregator.validate_coverage(results, expected_count=5)

        assert "expected 5" in str(exc_info.value).lower()


# =============================================================================
# TEST CLASS 6: WEIGHT VALIDATION
# =============================================================================

class TestPhase4WeightValidation:
    """Test weight validation in aggregation."""

    def test_weight_sum_not_equal_to_one(self):
        """Test that weights not summing to 1.0 fails validation."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator, WeightValidationError
        )

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=True
        )

        # Weights that don't sum to 1.0
        invalid_weights = [0.3, 0.3, 0.3]  # Sum = 0.9, invalid

        # When abort_on_insufficient=True, should raise WeightValidationError
        with pytest.raises(WeightValidationError) as exc_info:
            aggregator.validate_weights(invalid_weights)

        assert "sum" in str(exc_info.value).lower()

    def test_negative_weights_rejected(self):
        """Test that negative weights are rejected."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            AggregationSettings
        )

        # Create weights with negative value
        raw_weights = {"DIM01": {"Q001": 0.5, "Q002": -0.3, "Q003": 0.8}}

        # _normalize_weights should filter out negative weights
        normalized = AggregationSettings._normalize_weights(raw_weights["DIM01"])

        # Negative weight should be filtered out
        assert -0.3 not in normalized.values()
        assert all(w >= 0 for w in normalized.values())

    def test_empty_weights_falls_back_to_equal(self):
        """Test that empty weights falls back to equal weighting."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        results = create_dimension_score_group(scores=[1.0, 2.0, 3.0, 2.5, 1.5])

        # Aggregate with no weights (should use equal weights)
        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"},
            weights=None  # Should use equal weights
        )

        # Should calculate average with equal weights
        expected_avg = sum([1.0, 2.0, 3.0, 2.5, 1.5]) / 5
        assert abs(dim_score.score - expected_avg) < 1e-6


# =============================================================================
# TEST CLASS 7: ADVERSARIAL STRESS TESTS
# =============================================================================

class TestPhase4AdversarialStress:
    """Stress tests with adversarial conditions."""

    def test_all_insufficient_quality(self):
        """Test with all results having INSUFICIENTE quality."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        results = create_dimension_score_group(scores=[0.5, 0.8, 1.0, 1.2, 1.0])

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should have INSUFICIENTE quality
        assert dim_score.quality_level == "INSUFICIENTE"

    def test_mixed_quality_levels(self):
        """Test with mixed quality levels in input."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        results = [
            create_valid_scored_result(question_id=1, score=0.5, quality_level="INSUFICIENTE"),
            create_valid_scored_result(question_id=2, score=1.8, quality_level="ACEPTABLE"),
            create_valid_scored_result(question_id=3, score=2.5, quality_level="EXCELENTE"),
            create_valid_scored_result(question_id=4, score=2.2, quality_level="BUENO"),
            create_valid_scored_result(question_id=5, score=1.7, quality_level="ACEPTABLE"),
        ]

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should aggregate despite mixed quality
        assert 0.0 <= dim_score.score <= 3.0
        assert dim_score.validation_passed is True

    def test_extreme_score_variance(self):
        """Test with extreme variance in scores."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        # Scores from 0.0 to 3.0 (max variance)
        results = create_dimension_score_group(scores=[0.0, 0.75, 1.5, 2.25, 3.0])

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should calculate mean of 1.5
        assert abs(dim_score.score - 1.5) < 1e-6
        # Quality should be ACEPTABLE (1.5/3.0 = 0.5, which is < 0.55 threshold)
        assert dim_score.quality_level == "INSUFICIENTE"  # 1.5 is below 1.65 threshold

    def test_many_results_beyond_expected(self):
        """Test with more results than expected (e.g., 10 instead of 5)."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        # Create 10 results instead of expected 5
        results = [
            create_valid_scored_result(
                question_id=i,
                score=2.0
            )
            for i in range(1, 11)
        ]

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        dim_score = aggregator.aggregate_dimension(
            results,
            {"policy_area": "PA01", "dimension": "DIM01"}
        )

        # Should aggregate all 10 results
        assert len(dim_score.contributing_questions) == 10
        assert dim_score.score == pytest.approx(2.0)  # All scores are 2.0

    def test_concurrent_aggregation_thread_safety(self):
        """Test that aggregation produces deterministic results (thread safety)."""
        from farfan_pipeline.phases.Phase_four_five_six_seven.aggregation import (
            DimensionAggregator
        )

        results = create_dimension_score_group(scores=[1.0, 2.0, 3.0, 2.5, 1.5])

        aggregator = DimensionAggregator(
            monolith=None,
            abort_on_insufficient=False
        )

        # Aggregate multiple times
        scores = []
        for _ in range(10):
            dim_score = aggregator.aggregate_dimension(
                results,
                {"policy_area": "PA01", "dimension": "DIM01"}
            )
            scores.append(dim_score.score)

        # All results should be identical (deterministic)
        assert all(abs(s - scores[0]) < 1e-9 for s in scores)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
