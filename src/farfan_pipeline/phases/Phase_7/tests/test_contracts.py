"""
Unit tests for Phase 7 Contracts.

Tests input, mission, and output contracts.
"""

import pytest
from dataclasses import dataclass


@dataclass
class MockClusterScore:
    """Mock ClusterScore for testing."""
    cluster_id: str
    score: float
    coherence: float
    variance: float
    weakest_area: str = "PA01"
    dispersion_scenario: str = "LOW"
    penalty_applied: float = 0.0
    areas: list = None
    score_std: float = 0.1
    
    def __post_init__(self):
        if self.areas is None:
            self.areas = []


def test_input_contract_imports():
    """Test that input contract can be imported."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_input_contract import (
        Phase7InputContract,
        validate_phase7_input,
    )
    assert Phase7InputContract is not None
    assert validate_phase7_input is not None


def test_input_contract_valid_input():
    """Test input contract with valid cluster scores."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_input_contract import Phase7InputContract
    
    cluster_scores = [
        MockClusterScore("CLUSTER_MESO_1", 2.5, 0.9, 0.1),
        MockClusterScore("CLUSTER_MESO_2", 2.3, 0.85, 0.15),
        MockClusterScore("CLUSTER_MESO_3", 2.1, 0.88, 0.12),
        MockClusterScore("CLUSTER_MESO_4", 2.4, 0.92, 0.08),
    ]
    
    is_valid, msg = Phase7InputContract.validate(cluster_scores)
    assert is_valid is True
    assert "satisfied" in msg.lower()


def test_input_contract_wrong_count():
    """Test input contract with wrong number of clusters."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_input_contract import Phase7InputContract
    
    # Too few clusters
    cluster_scores = [
        MockClusterScore("CLUSTER_MESO_1", 2.5, 0.9, 0.1),
        MockClusterScore("CLUSTER_MESO_2", 2.3, 0.85, 0.15),
    ]
    
    is_valid, msg = Phase7InputContract.validate(cluster_scores)
    assert is_valid is False
    assert "Expected 4 ClusterScores" in msg


def test_input_contract_missing_cluster():
    """Test input contract with missing required cluster."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_input_contract import Phase7InputContract
    
    cluster_scores = [
        MockClusterScore("CLUSTER_MESO_1", 2.5, 0.9, 0.1),
        MockClusterScore("CLUSTER_MESO_2", 2.3, 0.85, 0.15),
        MockClusterScore("CLUSTER_MESO_3", 2.1, 0.88, 0.12),
        MockClusterScore("INVALID_ID", 2.4, 0.92, 0.08),  # Wrong ID
    ]
    
    is_valid, msg = Phase7InputContract.validate(cluster_scores)
    assert is_valid is False
    assert "Cluster mismatch" in msg


def test_input_contract_score_out_of_bounds():
    """Test input contract with score out of bounds."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_input_contract import Phase7InputContract
    
    cluster_scores = [
        MockClusterScore("CLUSTER_MESO_1", 5.0, 0.9, 0.1),  # Out of bounds
        MockClusterScore("CLUSTER_MESO_2", 2.3, 0.85, 0.15),
        MockClusterScore("CLUSTER_MESO_3", 2.1, 0.88, 0.12),
        MockClusterScore("CLUSTER_MESO_4", 2.4, 0.92, 0.08),
    ]
    
    is_valid, msg = Phase7InputContract.validate(cluster_scores)
    assert is_valid is False
    assert "out of bounds" in msg


def test_input_contract_validation_function():
    """Test validate_phase7_input function raises exception."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_input_contract import validate_phase7_input
    
    # Invalid input
    cluster_scores = [MockClusterScore("CLUSTER_MESO_1", 2.5, 0.9, 0.1)]
    
    with pytest.raises(ValueError, match="input contract violation"):
        validate_phase7_input(cluster_scores)


def test_mission_contract_imports():
    """Test that mission contract can be imported."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_mission_contract import Phase7MissionContract
    assert Phase7MissionContract is not None


def test_mission_contract_invariants():
    """Test mission contract invariants validation."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_mission_contract import Phase7MissionContract
    
    is_valid, msg = Phase7MissionContract.validate_invariants()
    assert is_valid is True
    assert "satisfied" in msg.lower()


def test_mission_contract_cluster_weights():
    """Test mission contract cluster weights sum to 1.0."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_mission_contract import Phase7MissionContract
    
    weight_sum = sum(Phase7MissionContract.CLUSTER_WEIGHTS.values())
    assert abs(weight_sum - 1.0) < 1e-6


def test_mission_contract_coherence_weights():
    """Test mission contract coherence weights sum to 1.0."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_mission_contract import Phase7MissionContract
    
    coherence_sum = sum(Phase7MissionContract.COHERENCE_WEIGHTS.values())
    assert abs(coherence_sum - 1.0) < 1e-6


def test_mission_contract_quality_thresholds():
    """Test mission contract quality thresholds are properly ordered."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_mission_contract import Phase7MissionContract
    
    thresholds = Phase7MissionContract.QUALITY_THRESHOLDS
    assert thresholds["EXCELENTE"] > thresholds["BUENO"]
    assert thresholds["BUENO"] > thresholds["ACEPTABLE"]
    assert thresholds["ACEPTABLE"] > thresholds["INSUFICIENTE"]


def test_output_contract_imports():
    """Test that output contract can be imported."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_output_contract import (
        Phase7OutputContract,
        validate_phase7_output,
    )
    assert Phase7OutputContract is not None
    assert validate_phase7_output is not None


def test_output_contract_valid_output():
    """Test output contract with valid MacroScore."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_output_contract import Phase7OutputContract
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    macro_score = MacroScore(
        evaluation_id="TEST_001",
        score=2.5,
        score_normalized=0.833,
        quality_level="BUENO",
        cross_cutting_coherence=0.90,
        strategic_alignment=0.85,
        cluster_scores=[
            MockClusterScore("CLUSTER_MESO_1", 2.5, 0.9, 0.1),
            MockClusterScore("CLUSTER_MESO_2", 2.3, 0.85, 0.15),
            MockClusterScore("CLUSTER_MESO_3", 2.1, 0.88, 0.12),
            MockClusterScore("CLUSTER_MESO_4", 2.4, 0.92, 0.08),
        ],
    )
    
    input_cluster_ids = {"CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"}
    is_valid, msg = Phase7OutputContract.validate(macro_score, input_cluster_ids)
    assert is_valid is True


def test_output_contract_score_out_of_bounds():
    """Test output contract with score out of bounds."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_output_contract import Phase7OutputContract
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    # This will fail in MacroScore.__post_init__
    with pytest.raises(ValueError):
        MacroScore(
            evaluation_id="TEST_002",
            score=5.0,  # Out of bounds
            score_normalized=0.833,
            quality_level="BUENO",
            cross_cutting_coherence=0.90,
        )


def test_output_contract_invalid_quality_level():
    """Test output contract with invalid quality level."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    with pytest.raises(ValueError):
        MacroScore(
            evaluation_id="TEST_003",
            score=2.5,
            score_normalized=0.833,
            quality_level="INVALID",  # Invalid
            cross_cutting_coherence=0.90,
        )


def test_output_contract_provenance_mismatch():
    """Test output contract with provenance mismatch."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_output_contract import Phase7OutputContract
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    macro_score = MacroScore(
        evaluation_id="TEST_004",
        score=2.5,
        score_normalized=0.833,
        quality_level="BUENO",
        cross_cutting_coherence=0.90,
        cluster_scores=[
            MockClusterScore("CLUSTER_MESO_1", 2.5, 0.9, 0.1),
            MockClusterScore("CLUSTER_MESO_2", 2.3, 0.85, 0.15),
        ],  # Only 2 clusters
    )
    
    # Input claims 4 clusters but output only has 2
    input_cluster_ids = {"CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"}
    is_valid, msg = Phase7OutputContract.validate(macro_score, input_cluster_ids)
    assert is_valid is False
    assert "Provenance mismatch" in msg


def test_output_contract_validation_function():
    """Test validate_phase7_output function raises exception."""
    from farfan_pipeline.phases.Phase_7.contracts.phase7_output_contract import validate_phase7_output
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore
    
    macro_score = MacroScore(
        evaluation_id="TEST_005",
        score=2.5,
        score_normalized=0.833,
        quality_level="BUENO",
        cross_cutting_coherence=0.90,
        cluster_scores=[],  # Empty
    )
    
    input_cluster_ids = {"CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"}
    
    with pytest.raises(ValueError, match="output contract violation"):
        validate_phase7_output(macro_score, input_cluster_ids)
