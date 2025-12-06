"""
Tests for Signal Intelligence Layer - Comprehensive Expansion Verification
==========================================================================

Verifies that EnrichedSignalPack initialization properly invokes expand_all_patterns
with comprehensive logging and metrics tracking for the 5x pattern multiplication.
"""

import pytest
from unittest.mock import Mock, patch

from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    EnrichedSignalPack,
    create_enriched_signal_pack,
    expand_all_patterns,
    validate_expansion_result,
)


@pytest.fixture
def mock_base_signal_pack():
    """Create a mock base signal pack with patterns that have semantic_expansion."""
    mock_pack = Mock()
    mock_pack.patterns = [
        {
            "id": "PAT-Q001-001",
            "pattern": r"presupuesto\s+asignado",
            "semantic_expansion": "presupuesto|recursos|fondos|financiamiento",
            "confidence_weight": 0.85,
            "match_type": "REGEX",
            "category": "GENERAL",
        },
        {
            "id": "PAT-Q001-002",
            "pattern": r"meta\s+2027",
            "semantic_expansion": "meta|objetivo|indicador",
            "confidence_weight": 0.90,
            "match_type": "REGEX",
            "category": "INDICADOR",
        },
    ]
    mock_pack.micro_questions = []
    return mock_pack


class TestEnrichedSignalPackInitialization:
    """Test suite for EnrichedSignalPack initialization and expand_all_patterns invocation."""

    def test_initialization_with_valid_base_pack(self, mock_base_signal_pack):
        """Test that initialization succeeds with valid base pack."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        assert enriched_pack is not None
        assert enriched_pack.base_pack == mock_base_signal_pack
        assert isinstance(enriched_pack.patterns, list)
        assert len(enriched_pack.patterns) > 0

    def test_expand_all_patterns_is_invoked(self, mock_base_signal_pack):
        """Test that expand_all_patterns is invoked during initialization."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        # Verify expansion metrics indicate invocation
        metrics = enriched_pack.get_expansion_metrics()
        assert metrics["expand_all_patterns_invoked"] is True
        assert metrics["enabled"] is True

    def test_patterns_are_expanded(self, mock_base_signal_pack):
        """Test that patterns are actually expanded (multiplier > 1)."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        metrics = enriched_pack.get_expansion_metrics()
        assert metrics["multiplier"] > 1.0
        assert metrics["variant_count"] > 0
        assert metrics["expanded_count"] > metrics["original_count"]

    def test_5x_multiplier_target(self, mock_base_signal_pack):
        """Test that expansion approaches or achieves 5x multiplier target."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        metrics = enriched_pack.get_expansion_metrics()
        multiplier = metrics["multiplier"]

        # Should at least meet minimum 2x
        assert multiplier >= 2.0, f"Multiplier {multiplier} below minimum 2x"

        # Log if target not achieved for debugging
        if multiplier < 5.0:
            print(
                f"INFO: Multiplier {multiplier} below 5x target (acceptable if >= 2x)"
            )

    def test_metrics_are_comprehensive(self, mock_base_signal_pack):
        """Test that expansion metrics contain all expected fields."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        metrics = enriched_pack.get_expansion_metrics()

        # Verify all critical metric fields are present
        required_fields = [
            "enabled",
            "original_count",
            "expanded_count",
            "variant_count",
            "multiplier",
            "patterns_with_expansion",
            "expansion_timestamp",
            "validation_result",
            "meets_target",
            "meets_minimum",
            "expand_all_patterns_invoked",
            "expansion_successful",
            "initialization_duration_seconds",
        ]

        for field in required_fields:
            assert field in metrics, f"Missing metric field: {field}"

    def test_validation_result_is_stored(self, mock_base_signal_pack):
        """Test that validation result is stored in metrics."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        metrics = enriched_pack.get_expansion_metrics()
        validation_result = metrics.get("validation_result")

        assert validation_result is not None
        assert "valid" in validation_result
        assert "multiplier" in validation_result
        assert "meets_minimum" in validation_result
        assert "meets_target" in validation_result

    def test_verify_expansion_invoked_method(self, mock_base_signal_pack):
        """Test the verify_expansion_invoked helper method."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        # Should return True for successful expansion
        assert enriched_pack.verify_expansion_invoked() is True

    def test_expansion_disabled_flag(self, mock_base_signal_pack):
        """Test that expansion can be disabled with flag."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        metrics = enriched_pack.get_expansion_metrics()

        assert metrics["enabled"] is False
        assert metrics["multiplier"] == 1.0
        assert metrics["variant_count"] == 0
        assert len(enriched_pack.patterns) == len(mock_base_signal_pack.patterns)

    def test_original_patterns_not_mutated(self, mock_base_signal_pack):
        """Test that original base pack patterns are not mutated."""
        original_pattern_count = len(mock_base_signal_pack.patterns)
        original_first_pattern = mock_base_signal_pack.patterns[0].copy()

        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        # Original should be unchanged
        assert len(mock_base_signal_pack.patterns) == original_pattern_count
        assert mock_base_signal_pack.patterns[0]["id"] == original_first_pattern["id"]


class TestEnrichedSignalPackValidation:
    """Test suite for input validation in EnrichedSignalPack initialization."""

    def test_none_base_pack_raises_error(self):
        """Test that None base_pack raises ValueError."""
        with pytest.raises(ValueError, match="base_signal_pack cannot be None"):
            EnrichedSignalPack(None, enable_semantic_expansion=True)

    def test_missing_patterns_attribute_raises_error(self):
        """Test that missing patterns attribute raises ValueError."""
        mock_pack = Mock(spec=[])  # No attributes

        with pytest.raises(ValueError, match="must have 'patterns' attribute"):
            EnrichedSignalPack(mock_pack, enable_semantic_expansion=True)

    def test_none_patterns_raises_error(self):
        """Test that None patterns raises ValueError."""
        mock_pack = Mock()
        mock_pack.patterns = None

        with pytest.raises(ValueError, match="patterns cannot be None"):
            EnrichedSignalPack(mock_pack, enable_semantic_expansion=True)

    def test_non_list_patterns_raises_error(self):
        """Test that non-list patterns raises TypeError."""
        mock_pack = Mock()
        mock_pack.patterns = "not a list"

        with pytest.raises(TypeError, match="must be a list"):
            EnrichedSignalPack(mock_pack, enable_semantic_expansion=True)

    def test_empty_patterns_list_handled(self):
        """Test that empty patterns list is handled gracefully."""
        mock_pack = Mock()
        mock_pack.patterns = []
        mock_pack.micro_questions = []

        # Should not raise error, just skip expansion
        enriched_pack = EnrichedSignalPack(mock_pack, enable_semantic_expansion=True)

        assert len(enriched_pack.patterns) == 0
        metrics = enriched_pack.get_expansion_metrics()
        assert metrics["original_count"] == 0


class TestExpansionMetricsRetrieval:
    """Test suite for expansion metrics retrieval methods."""

    def test_get_expansion_metrics_returns_copy(self, mock_base_signal_pack):
        """Test that get_expansion_metrics returns a copy (not reference)."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        metrics1 = enriched_pack.get_expansion_metrics()
        metrics2 = enriched_pack.get_expansion_metrics()

        # Should be equal but different objects
        assert metrics1 == metrics2
        assert metrics1 is not metrics2

    def test_get_expansion_summary_format(self, mock_base_signal_pack):
        """Test that get_expansion_summary returns formatted string."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        summary = enriched_pack.get_expansion_summary()

        assert isinstance(summary, str)
        assert "Semantic Expansion" in summary
        assert "multiplier" in summary.lower()
        assert "variants" in summary.lower()

    def test_log_expansion_report_executes(self, mock_base_signal_pack):
        """Test that log_expansion_report executes without error."""
        enriched_pack = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        # Should not raise any exceptions
        enriched_pack.log_expansion_report()


class TestCreateEnrichedSignalPackFactory:
    """Test suite for create_enriched_signal_pack factory function."""

    def test_factory_creates_enriched_pack(self, mock_base_signal_pack):
        """Test that factory function creates EnrichedSignalPack instance."""
        enriched_pack = create_enriched_signal_pack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )

        assert isinstance(enriched_pack, EnrichedSignalPack)

    def test_factory_respects_expansion_flag(self, mock_base_signal_pack):
        """Test that factory respects enable_semantic_expansion flag."""
        # With expansion
        pack_with_expansion = create_enriched_signal_pack(
            mock_base_signal_pack, enable_semantic_expansion=True
        )
        metrics_with = pack_with_expansion.get_expansion_metrics()

        # Without expansion
        pack_without_expansion = create_enriched_signal_pack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )
        metrics_without = pack_without_expansion.get_expansion_metrics()

        assert metrics_with["enabled"] is True
        assert metrics_without["enabled"] is False
        assert metrics_with["multiplier"] > metrics_without["multiplier"]


class TestExpansionLoggingAndMetrics:
    """Test suite for expansion logging and metrics tracking."""

    @patch("farfan_pipeline.core.orchestrator.signal_intelligence_layer.logger")
    def test_init_begin_logged(self, mock_logger, mock_base_signal_pack):
        """Test that enriched_signal_pack_init_begin is logged."""
        EnrichedSignalPack(mock_base_signal_pack, enable_semantic_expansion=True)

        # Check that init_begin was called
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("enriched_signal_pack_init_begin" in str(call) for call in log_calls)

    @patch("farfan_pipeline.core.orchestrator.signal_intelligence_layer.logger")
    def test_expand_all_patterns_invoking_logged(
        self, mock_logger, mock_base_signal_pack
    ):
        """Test that expand_all_patterns_invoking_now is logged."""
        EnrichedSignalPack(mock_base_signal_pack, enable_semantic_expansion=True)

        # Check that expansion invocation was logged
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any(
            "expand_all_patterns_invoking_now" in str(call) for call in log_calls
        )

    @patch("farfan_pipeline.core.orchestrator.signal_intelligence_layer.logger")
    def test_init_complete_logged(self, mock_logger, mock_base_signal_pack):
        """Test that enriched_signal_pack_init_complete is logged."""
        EnrichedSignalPack(mock_base_signal_pack, enable_semantic_expansion=True)

        # Check that init_complete was called
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any(
            "enriched_signal_pack_init_complete" in str(call) for call in log_calls
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
