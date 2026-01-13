"""
Phase 4 Primitives Layer Tests - Adversarial & Comprehensive

Tests the primitives layer (Layer 0) with adversarial conditions.
Covers: phase4_00_00_aggregation_settings.py, phase4_00_00_types.py

Module: src/farfan_pipeline/phases/Phase_4/tests/test_phase4_00_00_primitives.py
Version: 1.0.0
Status: ADVERSARIAL
"""
from __future__ import annotations

import pytest
from dataclasses import FrozenInstanceError

# Import primitives under test
from farfan_pipeline.phases.Phase_4.primitives.phase4_00_00_aggregation_settings import (
    AggregationSettings,
    validate_aggregation_settings,
)
from farfan_pipeline.phases.Phase_4.primitives.phase4_00_00_types import (
    PolicyAreaID,
    DimensionID,
    Score,
    Weight,
    IAggregator,
    IConfigBuilder,
    MIN_SCORE,
    MAX_SCORE,
    MIN_WEIGHT,
    MAX_WEIGHT,
    WEIGHT_SUM_TOLERANCE,
    is_valid_score,
    is_valid_weight,
    are_weights_normalized,
)


class TestAggregationSettingsDataclass:
    """Test AggregationSettings pure dataclass."""
    
    def test_creation_with_valid_data(self):
        """Test creating AggregationSettings with valid minimal data."""
        settings = AggregationSettings(
            dimension_group_by_keys=["policy_area", "dimension"],
            area_group_by_keys=["area_id"],
            cluster_group_by_keys=["cluster_id"],
            dimension_question_weights={},
            policy_area_dimension_weights={},
            cluster_policy_area_weights={},
            macro_cluster_weights={},
            dimension_expected_counts={},
            area_expected_dimension_counts={},
        )
        assert settings.dimension_group_by_keys == ["policy_area", "dimension"]
        assert settings.sisas_source == "legacy"
        assert settings.source_hash is None
    
    def test_immutability_frozen_dataclass(self):
        """ADVERSARIAL: Test that dataclass is frozen and cannot be modified."""
        settings = AggregationSettings(
            dimension_group_by_keys=["test"],
            area_group_by_keys=["test"],
            cluster_group_by_keys=["test"],
            dimension_question_weights={},
            policy_area_dimension_weights={},
            cluster_policy_area_weights={},
            macro_cluster_weights={},
            dimension_expected_counts={},
            area_expected_dimension_counts={},
        )
        
        with pytest.raises(FrozenInstanceError):
            settings.dimension_group_by_keys = ["modified"]
    
    def test_validation_valid_settings(self):
        """Test validate_aggregation_settings with valid data."""
        settings = AggregationSettings(
            dimension_group_by_keys=["policy_area", "dimension"],
            area_group_by_keys=["area_id"],
            cluster_group_by_keys=["cluster_id"],
            dimension_question_weights={},
            policy_area_dimension_weights={},
            cluster_policy_area_weights={},
            macro_cluster_weights={},
            dimension_expected_counts={},
            area_expected_dimension_counts={},
        )
        
        is_valid, errors = validate_aggregation_settings(settings)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validation_empty_group_by_keys(self):
        """ADVERSARIAL: Test validation with empty group_by_keys."""
        settings = AggregationSettings(
            dimension_group_by_keys=[],
            area_group_by_keys=[],
            cluster_group_by_keys=[],
            dimension_question_weights={},
            policy_area_dimension_weights={},
            cluster_policy_area_weights={},
            macro_cluster_weights={},
            dimension_expected_counts={},
            area_expected_dimension_counts={},
        )
        
        is_valid, errors = validate_aggregation_settings(settings)
        assert is_valid is False
        assert len(errors) == 3


class TestTypeValidation:
    """Test type validation functions."""
    
    def test_valid_score_boundaries(self):
        """Test is_valid_score with boundary values."""
        assert is_valid_score(0.0) is True
        assert is_valid_score(3.0) is True
        assert is_valid_score(1.5) is True
    
    def test_invalid_scores(self):
        """ADVERSARIAL: Test is_valid_score with invalid values."""
        assert is_valid_score(-0.1) is False
        assert is_valid_score(3.1) is False
    
    def test_valid_weight_boundaries(self):
        """Test is_valid_weight with boundary values."""
        assert is_valid_weight(0.0) is True
        assert is_valid_weight(1.0) is True
        assert is_valid_weight(0.5) is True
    
    def test_invalid_weights(self):
        """ADVERSARIAL: Test is_valid_weight with invalid values."""
        assert is_valid_weight(-0.1) is False
        assert is_valid_weight(1.1) is False
    
    def test_weights_normalized_valid(self):
        """Test are_weights_normalized with valid normalized weights."""
        assert are_weights_normalized([1.0]) is True
        assert are_weights_normalized([0.5, 0.5]) is True
        assert are_weights_normalized([0.25, 0.25, 0.25, 0.25]) is True
    
    def test_weights_not_normalized(self):
        """ADVERSARIAL: Test are_weights_normalized with invalid weights."""
        assert are_weights_normalized([0.5, 0.6]) is False
        assert are_weights_normalized([]) is False


class TestProtocols:
    """Test Protocol definitions."""
    
    def test_iaggregator_protocol_exists(self):
        """Test that IAggregator protocol is defined."""
        assert IAggregator is not None
    
    def test_iconfig_builder_protocol_exists(self):
        """Test that IConfigBuilder protocol is defined."""
        assert IConfigBuilder is not None
    
    def test_iaggregator_implementation(self):
        """Test that a class implementing IAggregator works."""
        class MockAggregator:
            def aggregate(self, scores, weights=None):
                return sum(scores) / len(scores) if scores else 0.0
            
            def validate_inputs(self, scores, weights=None):
                if not scores:
                    return False, "Empty scores"
                return True, ""
        
        aggregator = MockAggregator()
        assert isinstance(aggregator, IAggregator)
        result = aggregator.aggregate([1.0, 2.0, 3.0])
        assert result == 2.0
