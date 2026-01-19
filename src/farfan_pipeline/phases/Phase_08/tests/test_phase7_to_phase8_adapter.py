"""
Tests for Phase 7 to Phase 8 Interface Adapter

Verifies formal compatibility and contract satisfaction.

Test Coverage:
- Property-based tests
- Edge cases
- Contract validation
- Regression tests
"""

import pytest
from dataclasses import dataclass, field
from typing import Any, Dict


# ============================================================================
# MOCK DATA STRUCTURES (for testing without full Phase dependencies)
# ============================================================================

@dataclass
class MockDimensionScore:
    """Mock DimensionScore for testing."""
    dimension_id: str
    area_id: str
    score: float
    quality_level: str


@dataclass
class MockAreaScore:
    """Mock AreaScore for testing."""
    area_id: str
    area_name: str
    score: float
    quality_level: str
    dimension_scores: list[MockDimensionScore] = field(default_factory=list)


@dataclass
class MockClusterScore:
    """Mock ClusterScore for testing."""
    cluster_id: str
    score: float
    coherence: float
    dispersion_scenario: str
    penalty_applied: float
    area_ids: list[str] = field(default_factory=list)
    area_scores: list[float] = field(default_factory=list)


@dataclass
class MockMacroScore:
    """Mock MacroScore for testing."""
    evaluation_id: str
    score: float
    score_normalized: float
    quality_level: str
    cross_cutting_coherence: float
    coherence_breakdown: Dict[str, Any] = field(default_factory=dict)
    systemic_gaps: list[str] = field(default_factory=list)
    gap_severity: Dict[str, str] = field(default_factory=dict)
    strategic_alignment: float = 0.0
    alignment_breakdown: Dict[str, Any] = field(default_factory=dict)
    cluster_scores: list[MockClusterScore] = field(default_factory=list)
    validation_passed: bool = True
    validation_details: Dict[str, Any] = field(default_factory=dict)
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"
    evaluation_timestamp: str = "2026-01-14T00:00:00Z"
    pipeline_version: str = "1.0.0"


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def valid_macro_score():
    """Create a valid MacroScore for testing."""
    return MockMacroScore(
        evaluation_id="EVAL-TEST-001",
        score=2.5,
        score_normalized=0.833,
        quality_level="BUENO",
        cross_cutting_coherence=0.85,
        strategic_alignment=0.75,
        systemic_gaps=["PA01", "PA05"],
        gap_severity={"PA01": "MODERATE", "PA05": "SEVERE"},
        cluster_scores=[
            MockClusterScore(
                cluster_id="CLUSTER_MESO_1",
                score=2.3,
                coherence=0.82,
                dispersion_scenario="CONVERGENTE",
                penalty_applied=0.0,
                area_ids=["PA01", "PA02", "PA03"],
                area_scores=[2.1, 2.4, 2.5],
            ),
            MockClusterScore(
                cluster_id="CLUSTER_MESO_2",
                score=2.6,
                coherence=0.88,
                dispersion_scenario="CONVERGENTE",
                penalty_applied=0.0,
                area_ids=["PA04", "PA05", "PA06"],
                area_scores=[2.5, 2.6, 2.7],
            ),
            MockClusterScore(
                cluster_id="CLUSTER_MESO_3",
                score=2.4,
                coherence=0.80,
                dispersion_scenario="BALANCEADO",
                penalty_applied=0.05,
                area_ids=["PA07", "PA08"],
                area_scores=[2.3, 2.5],
            ),
            MockClusterScore(
                cluster_id="CLUSTER_MESO_4",
                score=2.7,
                coherence=0.90,
                dispersion_scenario="CONVERGENTE",
                penalty_applied=0.0,
                area_ids=["PA09", "PA10"],
                area_scores=[2.6, 2.8],
            ),
        ],
        provenance_node_id="P7-MACRO-001",
    )


@pytest.fixture
def valid_phase5_output():
    """Create valid Phase 5 output (10 AreaScores with 60 DimensionScores)."""
    phase5_output = []
    
    for area_num in range(1, 11):  # 10 areas
        area_id = f"PA{area_num:02d}"
        area_name = f"Policy Area {area_num}"
        
        # Create 6 DimensionScores for this area
        dimension_scores = []
        for dim_num in range(1, 7):  # 6 dimensions
            dim_id = f"DIM{dim_num:02d}"
            dim_score = MockDimensionScore(
                dimension_id=dim_id,
                area_id=area_id,
                score=2.0 + (area_num + dim_num) * 0.1,  # Vary scores
                quality_level="BUENO",
            )
            dimension_scores.append(dim_score)
        
        # Create AreaScore
        area_score = MockAreaScore(
            area_id=area_id,
            area_name=area_name,
            score=2.3 + area_num * 0.05,
            quality_level="BUENO",
            dimension_scores=dimension_scores,
        )
        phase5_output.append(area_score)
    
    return phase5_output


# ============================================================================
# ADAPTER TESTS
# ============================================================================

def test_adapter_basic_functionality(valid_macro_score, valid_phase5_output):
    """Test basic adapter functionality with valid inputs."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    # Verify structure
    assert isinstance(result, dict)
    assert "micro_scores" in result
    assert "cluster_data" in result
    assert "macro_data" in result
    assert "metadata" in result


def test_adapter_micro_scores_cardinality(valid_macro_score, valid_phase5_output):
    """Test that adapter produces exactly 60 micro scores."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    micro_scores = result["micro_scores"]
    assert len(micro_scores) == 60, f"Expected 60 micro scores, got {len(micro_scores)}"


def test_adapter_micro_scores_format(valid_macro_score, valid_phase5_output):
    """Test that micro score keys follow PA{01-10}-DIM{01-06} format."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    micro_scores = result["micro_scores"]
    
    # Check all 60 expected keys
    expected_keys = set()
    for pa_num in range(1, 11):
        for dim_num in range(1, 7):
            key = f"PA{pa_num:02d}-DIM{dim_num:02d}"
            expected_keys.add(key)
    
    actual_keys = set(micro_scores.keys())
    assert actual_keys == expected_keys, f"Key mismatch: {actual_keys.symmetric_difference(expected_keys)}"


def test_adapter_cluster_data_transformation(valid_macro_score, valid_phase5_output):
    """Test that cluster_scores List is transformed to cluster_data Dict."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    cluster_data = result["cluster_data"]
    
    # Verify structure
    assert isinstance(cluster_data, dict)
    assert len(cluster_data) == 4  # 4 clusters from MacroScore
    
    # Verify each cluster has required fields
    for cluster_id, cluster_info in cluster_data.items():
        assert "cluster_id" in cluster_info
        assert "score" in cluster_info
        assert "variance" in cluster_info  # Mapped from coherence
        assert "coherence" in cluster_info


def test_adapter_macro_band_mapping(valid_macro_score, valid_phase5_output):
    """Test that quality_level is correctly mapped to macro_band."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    macro_data = result["macro_data"]
    
    assert "macro_band" in macro_data
    assert macro_data["macro_band"] == valid_macro_score.quality_level
    assert macro_data["macro_band"] == "BUENO"


def test_adapter_macro_data_completeness(valid_macro_score, valid_phase5_output):
    """Test that macro_data contains all expected fields."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    macro_data = result["macro_data"]
    
    required_fields = [
        "macro_band", "macro_score", "macro_score_normalized",
        "cross_cutting_coherence", "strategic_alignment",
        "systemic_gaps", "gap_severity",
        "evaluation_id", "pipeline_version"
    ]
    
    for field in required_fields:
        assert field in macro_data, f"Required field '{field}' missing from macro_data"


def test_adapter_metadata_provenance(valid_macro_score, valid_phase5_output):
    """Test that metadata preserves provenance information."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    metadata = result["metadata"]
    
    assert metadata["source_phase"] == "Phase_07"
    assert metadata["evaluation_id"] == valid_macro_score.evaluation_id
    assert "provenance_chain" in metadata


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_adapter_without_phase5_output(valid_macro_score):
    """Test adapter when Phase 5 output is not provided."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, phase5_output=None)
    
    # Should still work, but micro_scores will be empty
    assert "micro_scores" in result
    assert len(result["micro_scores"]) == 0


def test_adapter_empty_cluster_scores(valid_phase5_output):
    """Test adapter with MacroScore having empty cluster_scores."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    macro_score = MockMacroScore(
        evaluation_id="EVAL-EMPTY",
        score=2.0,
        score_normalized=0.67,
        quality_level="ACEPTABLE",
        cross_cutting_coherence=0.7,
        cluster_scores=[],  # Empty!
    )
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(macro_score, valid_phase5_output)
    
    # Should work, cluster_data will be empty
    assert len(result["cluster_data"]) == 0


def test_adapter_all_quality_levels(valid_phase5_output):
    """Test adapter with all valid quality levels."""
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    quality_levels = ["EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"]
    adapter = Phase7To8Adapter()
    
    for quality_level in quality_levels:
        macro_score = MockMacroScore(
            evaluation_id=f"EVAL-{quality_level}",
            score=2.5,
            score_normalized=0.833,
            quality_level=quality_level,
            cross_cutting_coherence=0.8,
        )
        
        result = adapter.adapt(macro_score, valid_phase5_output)
        assert result["macro_data"]["macro_band"] == quality_level


# ============================================================================
# CONTRACT VALIDATION TESTS
# ============================================================================

def test_adapter_satisfies_phase8_precondition_002(valid_macro_score, valid_phase5_output):
    """
    Test that adapter output satisfies Phase 8 PRE-P8-002:
    Micro Scores Available (60 PA×DIM keys).
    """
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    # PRE-P8-002: micro_scores dict contains all 60 PA×DIM keys
    micro_scores = result["micro_scores"]
    assert isinstance(micro_scores, dict)
    assert len(micro_scores) == 60


def test_adapter_satisfies_phase8_precondition_003(valid_macro_score, valid_phase5_output):
    """
    Test that adapter output satisfies Phase 8 PRE-P8-003:
    Cluster Data Available.
    """
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    # PRE-P8-003: cluster_data contains cluster_id, score, variance for all clusters
    cluster_data = result["cluster_data"]
    assert isinstance(cluster_data, dict)
    assert len(cluster_data) > 0
    
    for cluster_id, cluster_info in cluster_data.items():
        assert "cluster_id" in cluster_info
        assert "score" in cluster_info
        assert "variance" in cluster_info


def test_adapter_satisfies_phase8_precondition_004(valid_macro_score, valid_phase5_output):
    """
    Test that adapter output satisfies Phase 8 PRE-P8-004:
    Macro Band Available.
    """
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    # PRE-P8-004: macro_data contains macro_band field with valid band name
    macro_data = result["macro_data"]
    assert "macro_band" in macro_data
    assert isinstance(macro_data["macro_band"], str)
    assert macro_data["macro_band"] in ["EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"]


# ============================================================================
# PROPERTY-BASED TESTS (using pytest-hypothesis if available)
# ============================================================================

try:
    from hypothesis import given, strategies as st
    
    @given(
        score=st.floats(min_value=0.0, max_value=3.0),
        quality_level=st.sampled_from(["EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"]),
    )
    def test_adapter_property_macro_band_preserved(score, quality_level, valid_phase5_output):
        """Property: macro_band is identity mapping of quality_level."""
        from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
        
        macro_score = MockMacroScore(
            evaluation_id="PROP-TEST",
            score=score,
            score_normalized=score / 3.0,
            quality_level=quality_level,
            cross_cutting_coherence=0.8,
        )
        
        adapter = Phase7To8Adapter()
        result = adapter.adapt(macro_score, valid_phase5_output)
        
        assert result["macro_data"]["macro_band"] == quality_level

except ImportError:
    # hypothesis not available, skip property-based tests
    pass


# ============================================================================
# INTEGRATION TEST WITH ACTUAL CONTRACTS
# ============================================================================

def test_adapter_integration_with_phase8_input_contract(valid_macro_score, valid_phase5_output):
    """
    Integration test: Verify adapter output passes Phase 8 input contract validation.
    """
    from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import Phase7To8Adapter
    from farfan_pipeline.phases.Phase_08.contracts.phase8_input_contract import validate_phase8_input_contract
    
    adapter = Phase7To8Adapter()
    result = adapter.adapt(valid_macro_score, valid_phase5_output)
    
    # Validate with Phase 8 input contract
    validation_result = validate_phase8_input_contract(result)
    
    assert validation_result["status"] == "PASS", f"Validation failed: {validation_result['failures']}"
    assert validation_result["preconditions_passed"] >= 4  # At least 4 of 5 should pass


if __name__ == "__main__":
    print("Running Phase 7→8 Adapter Tests...")
    print("=" * 70)
    pytest.main([__file__, "-v"])
