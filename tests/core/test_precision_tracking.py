"""
Comprehensive Tests for Precision Tracking Module
==================================================

Tests for enhanced get_patterns_for_context() validation and comprehensive
stats tracking to ensure 60% precision improvement is measurable.

Coverage:
- get_patterns_with_validation() wrapper function
- validate_filter_integration() validation function
- Enhanced stats tracking with all new fields
- Validation status and target achievement
- Error handling and edge cases

Test Standards:
- pytest for test framework
- Clear test names describing behavior
- Comprehensive edge case coverage
- Property-based testing where applicable
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from farfan_pipeline.core.orchestrator.precision_tracking import (
    get_patterns_with_validation,
    validate_filter_integration,
    create_precision_tracking_session,
    add_measurement_to_session,
    finalize_precision_tracking_session,
    compare_precision_across_policy_areas,
    export_precision_metrics_for_monitoring,
    PRECISION_TARGET_THRESHOLD,
)


class TestGetPatternsWithValidation:
    """Test get_patterns_with_validation() function."""

    def test_basic_usage_with_valid_context(self):
        """Test basic usage with valid document context."""
        mock_pack = MagicMock()
        mock_pack.patterns = [
            {"id": "p1", "pattern": "test1"},
            {"id": "p2", "pattern": "test2"},
            {"id": "p3", "pattern": "test3"},
        ]

        filtered_patterns = [{"id": "p1", "pattern": "test1"}]
        base_stats = {
            "total_patterns": 3,
            "passed": 1,
            "context_filtered": 2,
            "scope_filtered": 0,
            "filter_rate": 0.67,
            "integration_validated": True,
            "false_positive_reduction": 0.60,
        }

        mock_pack.get_patterns_for_context.return_value = (
            filtered_patterns,
            base_stats,
        )

        context = {"section": "budget", "chapter": 3}
        patterns, stats = get_patterns_with_validation(mock_pack, context)

        assert patterns == filtered_patterns
        assert stats["pre_filter_count"] == 3
        assert stats["post_filter_count"] == 1
        assert stats["filtering_successful"] is True
        assert stats["validation_status"] == "VALIDATED"
        assert stats["target_achieved"] is True
        assert stats["target_status"] == "ACHIEVED"
        assert "validation_timestamp" in stats
        assert "validation_details" in stats

        mock_pack.get_patterns_for_context.assert_called_once_with(
            context, track_precision_improvement=True
        )

    def test_validation_details_comprehensive(self):
        """Test validation_details contains all required fields."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": f"p{i}"} for i in range(10)]

        filtered = [{"id": f"p{i}"} for i in range(4)]
        base_stats = {
            "total_patterns": 10,
            "passed": 4,
            "context_filtered": 6,
            "scope_filtered": 0,
            "filter_rate": 0.60,
            "integration_validated": True,
            "false_positive_reduction": 0.60,
        }

        mock_pack.get_patterns_for_context.return_value = (filtered, base_stats)

        context = {"section": "budget"}
        _, stats = get_patterns_with_validation(mock_pack, context)

        validation_details = stats["validation_details"]
        assert validation_details["filter_function_called"] is True
        assert validation_details["pre_filter_count"] == 10
        assert validation_details["post_filter_count"] == 4
        assert validation_details["context_fields"] == ["section"]
        assert validation_details["context_field_count"] == 1
        assert validation_details["filtering_successful"] is True
        assert validation_details["patterns_reduced"] == 6
        assert validation_details["reduction_percentage"] == 60.0

    def test_target_not_met_scenario(self):
        """Test scenario where 60% target is not met."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": f"p{i}"} for i in range(10)]

        filtered = [{"id": f"p{i}"} for i in range(8)]
        base_stats = {
            "total_patterns": 10,
            "passed": 8,
            "context_filtered": 2,
            "scope_filtered": 0,
            "filter_rate": 0.20,
            "integration_validated": True,
            "false_positive_reduction": 0.30,
        }

        mock_pack.get_patterns_for_context.return_value = (filtered, base_stats)

        context = {"section": "budget"}
        _, stats = get_patterns_with_validation(mock_pack, context)

        assert stats["target_achieved"] is False
        assert stats["target_status"] == "NOT_MET"
        assert stats["validation_status"] == "VALIDATED"
        assert stats["false_positive_reduction"] == 0.30

    def test_integration_not_validated_scenario(self):
        """Test scenario where integration is not validated."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": "p1"}]

        base_stats = {
            "total_patterns": 1,
            "passed": 1,
            "context_filtered": 0,
            "scope_filtered": 0,
            "filter_rate": 0.0,
            "integration_validated": False,
            "false_positive_reduction": 0.0,
        }

        mock_pack.get_patterns_for_context.return_value = ([{"id": "p1"}], base_stats)

        context = {}
        _, stats = get_patterns_with_validation(mock_pack, context)

        assert stats["validation_status"] == "NOT_VALIDATED"
        assert stats["integration_validated"] is False

    def test_invalid_context_type_handling(self):
        """Test handling of invalid context type."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
            },
        )

        patterns, stats = get_patterns_with_validation(
            mock_pack, "not_a_dict"  # Invalid type
        )

        mock_pack.get_patterns_for_context.assert_called_once()
        call_args = mock_pack.get_patterns_for_context.call_args
        assert call_args[0][0] == {}

    def test_filtering_failure_detection(self):
        """Test detection of filtering failure (more patterns after than before)."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": "p1"}]

        filtered = [{"id": "p1"}, {"id": "p2"}]
        base_stats = {
            "total_patterns": 1,
            "passed": 2,
            "context_filtered": 0,
            "scope_filtered": 0,
            "filter_rate": 0.0,
            "integration_validated": True,
            "false_positive_reduction": 0.0,
        }

        mock_pack.get_patterns_for_context.return_value = (filtered, base_stats)

        _, stats = get_patterns_with_validation(mock_pack, {})

        assert stats["filtering_successful"] is False
        assert stats["integration_validated"] is False
        assert stats["validation_status"] == "FAILED"

    def test_tracking_disabled_scenario(self):
        """Test scenario with precision tracking disabled."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": "p1"}]

        base_stats = {
            "total_patterns": 1,
            "passed": 1,
            "context_filtered": 0,
            "scope_filtered": 0,
        }

        mock_pack.get_patterns_for_context.return_value = ([{"id": "p1"}], base_stats)

        _, stats = get_patterns_with_validation(
            mock_pack, {}, track_precision_improvement=False
        )

        assert stats["target_achieved"] is False
        assert stats["validation_status"] == "TRACKING_DISABLED"
        assert stats["target_status"] == "UNKNOWN"

    def test_empty_patterns_scenario(self):
        """Test scenario with no patterns."""
        mock_pack = MagicMock()
        mock_pack.patterns = []

        base_stats = {
            "total_patterns": 0,
            "passed": 0,
            "context_filtered": 0,
            "scope_filtered": 0,
            "filter_rate": 0.0,
            "integration_validated": True,
            "false_positive_reduction": 0.0,
        }

        mock_pack.get_patterns_for_context.return_value = ([], base_stats)

        patterns, stats = get_patterns_with_validation(mock_pack, {})

        assert patterns == []
        assert stats["pre_filter_count"] == 0
        assert stats["post_filter_count"] == 0
        assert stats["filtering_successful"] is True

    def test_timestamp_format(self):
        """Test validation timestamp is in ISO format."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
            },
        )

        _, stats = get_patterns_with_validation(mock_pack, {})

        timestamp = stats["validation_timestamp"]
        assert isinstance(timestamp, str)
        assert "T" in timestamp
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def test_context_fields_tracking(self):
        """Test context fields are tracked in validation details."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
            },
        )

        context = {"section": "budget", "chapter": 3, "page": 47, "policy_area": "PA05"}

        _, stats = get_patterns_with_validation(mock_pack, context)

        validation_details = stats["validation_details"]
        assert set(validation_details["context_fields"]) == {
            "section",
            "chapter",
            "page",
            "policy_area",
        }
        assert validation_details["context_field_count"] == 4

    def test_reduction_percentage_calculation(self):
        """Test reduction percentage is calculated correctly."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": f"p{i}"} for i in range(100)]

        filtered = [{"id": f"p{i}"} for i in range(40)]
        base_stats = {
            "total_patterns": 100,
            "passed": 40,
            "context_filtered": 60,
            "scope_filtered": 0,
            "filter_rate": 0.60,
            "integration_validated": True,
            "false_positive_reduction": 0.60,
        }

        mock_pack.get_patterns_for_context.return_value = (filtered, base_stats)

        _, stats = get_patterns_with_validation(mock_pack, {})

        validation_details = stats["validation_details"]
        assert validation_details["patterns_reduced"] == 60
        assert validation_details["reduction_percentage"] == 60.0


class TestValidateFilterIntegration:
    """Test validate_filter_integration() function."""

    def test_default_test_contexts(self):
        """Test validation with default test contexts."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": "p1"}, {"id": "p2"}]

        def mock_get_patterns(context, track_precision_improvement=True):
            if context.get("section") == "budget":
                return (
                    [{"id": "p1"}],
                    {
                        "total_patterns": 2,
                        "passed": 1,
                        "context_filtered": 1,
                        "scope_filtered": 0,
                        "filter_rate": 0.50,
                        "integration_validated": True,
                        "false_positive_reduction": 0.60,
                        "target_achieved": True,
                    },
                )
            return (
                [{"id": "p1"}, {"id": "p2"}],
                {
                    "total_patterns": 2,
                    "passed": 2,
                    "context_filtered": 0,
                    "scope_filtered": 0,
                    "filter_rate": 0.0,
                    "integration_validated": True,
                    "false_positive_reduction": 0.0,
                    "target_achieved": False,
                },
            )

        mock_pack.get_patterns_for_context.side_effect = mock_get_patterns

        report = validate_filter_integration(mock_pack)

        assert report["total_tests"] == 5
        assert report["successful_tests"] == 5
        assert report["failed_tests"] == 0
        assert "validation_summary" in report
        assert isinstance(report["all_results"], list)

    def test_custom_test_contexts(self):
        """Test validation with custom test contexts."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
                "filter_rate": 0.0,
                "integration_validated": True,
                "false_positive_reduction": 0.0,
                "target_achieved": False,
            },
        )

        test_contexts = [
            {"section": "test1"},
            {"section": "test2"},
        ]

        report = validate_filter_integration(mock_pack, test_contexts)

        assert report["total_tests"] == 2
        assert report["successful_tests"] == 2

    def test_all_tests_successful(self):
        """Test scenario where all tests pass successfully."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": f"p{i}"} for i in range(10)]
        mock_pack.get_patterns_for_context.return_value = (
            [{"id": "p1"}],
            {
                "total_patterns": 10,
                "passed": 1,
                "context_filtered": 9,
                "scope_filtered": 0,
                "filter_rate": 0.90,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
                "target_achieved": True,
            },
        )

        test_contexts = [{"section": "test"}]
        report = validate_filter_integration(mock_pack, test_contexts)

        assert report["integration_validated"] is True
        assert report["target_achievement_rate"] == 1.0
        assert report["integration_rate"] == 1.0

    def test_some_tests_fail(self):
        """Test scenario where some tests fail with exceptions."""
        mock_pack = MagicMock()
        mock_pack.patterns = []

        call_count = [0]

        def mock_get_patterns(context, track_precision_improvement=True):
            call_count[0] += 1
            if call_count[0] == 2:
                raise ValueError("Test error")
            return (
                [],
                {
                    "total_patterns": 0,
                    "passed": 0,
                    "context_filtered": 0,
                    "scope_filtered": 0,
                    "filter_rate": 0.0,
                    "integration_validated": True,
                    "false_positive_reduction": 0.0,
                    "target_achieved": False,
                },
            )

        mock_pack.get_patterns_for_context.side_effect = mock_get_patterns

        test_contexts = [{"test": 1}, {"test": 2}, {"test": 3}]
        report = validate_filter_integration(mock_pack, test_contexts)

        assert report["total_tests"] == 3
        assert report["successful_tests"] == 2
        assert report["failed_tests"] == 1
        assert len(report["errors"]) == 1
        assert report["errors"][0]["test_index"] == 1

    def test_all_tests_fail(self):
        """Test scenario where all tests fail."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.side_effect = Exception("Fatal error")

        test_contexts = [{"test": 1}, {"test": 2}]
        report = validate_filter_integration(mock_pack, test_contexts)

        assert report["total_tests"] == 2
        assert report["successful_tests"] == 0
        assert report["failed_tests"] == 2
        assert report["integration_validated"] is False
        assert "ALL TESTS FAILED" in report["validation_summary"]

    def test_integration_rate_calculation(self):
        """Test integration rate is calculated correctly."""
        mock_pack = MagicMock()
        mock_pack.patterns = []

        call_count = [0]

        def mock_get_patterns(context, track_precision_improvement=True):
            call_count[0] += 1
            integration_validated = call_count[0] <= 3
            return (
                [],
                {
                    "total_patterns": 0,
                    "passed": 0,
                    "context_filtered": 0,
                    "scope_filtered": 0,
                    "filter_rate": 0.0,
                    "integration_validated": integration_validated,
                    "false_positive_reduction": 0.0,
                    "target_achieved": False,
                },
            )

        mock_pack.get_patterns_for_context.side_effect = mock_get_patterns

        test_contexts = [{"test": i} for i in range(5)]
        report = validate_filter_integration(mock_pack, test_contexts)

        assert report["integration_validated_count"] == 3
        assert report["integration_rate"] == 0.6
        assert report["integration_validated"] is False

    def test_target_achievement_rate_calculation(self):
        """Test target achievement rate is calculated correctly."""
        mock_pack = MagicMock()
        mock_pack.patterns = []

        call_count = [0]

        def mock_get_patterns(context, track_precision_improvement=True):
            call_count[0] += 1
            target_achieved = call_count[0] % 2 == 1
            return (
                [],
                {
                    "total_patterns": 0,
                    "passed": 0,
                    "context_filtered": 0,
                    "scope_filtered": 0,
                    "filter_rate": 0.0,
                    "integration_validated": True,
                    "false_positive_reduction": 0.60 if target_achieved else 0.30,
                    "target_achieved": target_achieved,
                },
            )

        mock_pack.get_patterns_for_context.side_effect = mock_get_patterns

        test_contexts = [{"test": i} for i in range(6)]
        report = validate_filter_integration(mock_pack, test_contexts)

        assert report["target_achieved_count"] == 3
        assert report["target_achievement_rate"] == 0.5

    def test_average_metrics_calculation(self):
        """Test average metrics are calculated correctly."""
        mock_pack = MagicMock()
        mock_pack.patterns = []

        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 100,
                "passed": 40,
                "context_filtered": 60,
                "scope_filtered": 0,
                "filter_rate": 0.60,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
                "target_achieved": True,
            },
        )

        test_contexts = [{"test": i} for i in range(3)]
        report = validate_filter_integration(mock_pack, test_contexts)

        assert report["average_filter_rate"] == 0.60
        assert report["average_fp_reduction"] == 0.60

    def test_min_max_fp_reduction_tracking(self):
        """Test min and max false positive reduction are tracked."""
        mock_pack = MagicMock()
        mock_pack.patterns = []

        call_count = [0]
        fp_reductions = [0.30, 0.60, 0.45]

        def mock_get_patterns(context, track_precision_improvement=True):
            result_idx = call_count[0]
            call_count[0] += 1
            return (
                [],
                {
                    "total_patterns": 100,
                    "passed": 50,
                    "context_filtered": 50,
                    "scope_filtered": 0,
                    "filter_rate": 0.50,
                    "integration_validated": True,
                    "false_positive_reduction": fp_reductions[result_idx],
                    "target_achieved": fp_reductions[result_idx]
                    >= PRECISION_TARGET_THRESHOLD,
                },
            )

        mock_pack.get_patterns_for_context.side_effect = mock_get_patterns

        test_contexts = [{"test": i} for i in range(3)]
        report = validate_filter_integration(mock_pack, test_contexts)

        assert report["max_fp_reduction"] == 0.60
        assert report["min_fp_reduction"] == 0.30

    def test_validation_summary_format(self):
        """Test validation summary is well-formatted."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
                "filter_rate": 0.0,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
                "target_achieved": True,
            },
        )

        test_contexts = [{}]
        report = validate_filter_integration(mock_pack, test_contexts)

        summary = report["validation_summary"]
        assert "Filter Integration Validation Report" in summary
        assert "Tests:" in summary
        assert "Integration validated:" in summary
        assert "60% target achieved:" in summary
        assert "Average filter rate:" in summary
        assert "Average FP reduction:" in summary
        assert "Overall status:" in summary
        assert "Target status:" in summary


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_pack_without_patterns_attribute(self):
        """Test handling of pack without patterns attribute."""
        mock_pack = MagicMock(spec=[])
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
            },
        )

        patterns, stats = get_patterns_with_validation(mock_pack, {})

        assert stats["pre_filter_count"] == 0

    def test_none_document_context(self):
        """Test handling of None document context."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
            },
        )

        patterns, stats = get_patterns_with_validation(mock_pack, None)

        call_args = mock_pack.get_patterns_for_context.call_args
        assert call_args[0][0] == {}

    def test_very_large_pattern_count(self):
        """Test handling of very large pattern counts."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": f"p{i}"} for i in range(10000)]

        filtered = [{"id": f"p{i}"} for i in range(1000)]
        base_stats = {
            "total_patterns": 10000,
            "passed": 1000,
            "context_filtered": 9000,
            "scope_filtered": 0,
            "filter_rate": 0.90,
            "integration_validated": True,
            "false_positive_reduction": 0.60,
        }

        mock_pack.get_patterns_for_context.return_value = (filtered, base_stats)

        _, stats = get_patterns_with_validation(mock_pack, {})

        assert stats["pre_filter_count"] == 10000
        assert stats["post_filter_count"] == 1000
        assert stats["validation_details"]["patterns_reduced"] == 9000

    def test_zero_context_fields(self):
        """Test handling of empty context dict."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
            },
        )

        _, stats = get_patterns_with_validation(mock_pack, {})

        validation_details = stats["validation_details"]
        assert validation_details["context_fields"] == []
        assert validation_details["context_field_count"] == 0

    def test_precision_target_boundary(self):
        """Test behavior at precision target boundary."""
        mock_pack = MagicMock()
        mock_pack.patterns = []

        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
                "filter_rate": 0.0,
                "integration_validated": True,
                "false_positive_reduction": PRECISION_TARGET_THRESHOLD,
                "target_achieved": True,
            },
        )

        _, stats = get_patterns_with_validation(mock_pack, {})

        assert stats["target_achieved"] is True
        assert stats["target_status"] == "ACHIEVED"
        assert stats["false_positive_reduction"] == PRECISION_TARGET_THRESHOLD


class TestLogging:
    """Test logging behavior."""

    @patch("farfan_pipeline.core.orchestrator.precision_tracking.logger")
    def test_success_logging(self, mock_logger):
        """Test logging on successful validation."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": "p1"}]
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 1,
                "passed": 0,
                "context_filtered": 1,
                "scope_filtered": 0,
                "filter_rate": 1.0,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
            },
        )

        get_patterns_with_validation(mock_pack, {})

        mock_logger.info.assert_called()

    @patch("farfan_pipeline.core.orchestrator.precision_tracking.logger")
    def test_target_achieved_logging(self, mock_logger):
        """Test logging when target is achieved."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
                "filter_rate": 0.0,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
            },
        )

        get_patterns_with_validation(mock_pack, {})

        info_calls = [call for call in mock_logger.info.call_args_list]
        assert any("precision_target_achieved" in str(call) for call in info_calls)

    @patch("farfan_pipeline.core.orchestrator.precision_tracking.logger")
    def test_target_not_met_logging(self, mock_logger):
        """Test logging when target is not met."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
                "filter_rate": 0.0,
                "integration_validated": True,
                "false_positive_reduction": 0.30,
            },
        )

        get_patterns_with_validation(mock_pack, {})

        mock_logger.warning.assert_called()

    @patch("farfan_pipeline.core.orchestrator.precision_tracking.logger")
    def test_filtering_failure_logging(self, mock_logger):
        """Test logging when filtering fails validation."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": "p1"}]
        mock_pack.get_patterns_for_context.return_value = (
            [{"id": "p1"}, {"id": "p2"}],
            {
                "total_patterns": 1,
                "passed": 2,
                "context_filtered": 0,
                "scope_filtered": 0,
                "filter_rate": 0.0,
                "integration_validated": True,
                "false_positive_reduction": 0.0,
            },
        )

        get_patterns_with_validation(mock_pack, {})

        mock_logger.error.assert_called()


class TestPrecisionTrackingSession:
    """Test precision tracking session functions."""

    def test_create_session_with_id(self):
        """Test creating a precision tracking session with custom ID."""
        mock_pack = MagicMock()

        session = create_precision_tracking_session(mock_pack, "test_session_001")

        assert session["session_id"] == "test_session_001"
        assert session["enriched_pack"] is mock_pack
        assert session["measurements"] == []
        assert session["measurement_count"] == 0
        assert session["status"] == "ACTIVE"
        assert "start_timestamp" in session
        assert "cumulative_stats" in session

    def test_create_session_auto_id(self):
        """Test creating session with auto-generated ID."""
        mock_pack = MagicMock()

        session = create_precision_tracking_session(mock_pack)

        assert session["session_id"].startswith("precision_session_")
        assert len(session["session_id"]) > len("precision_session_")

    def test_add_measurement_to_session(self):
        """Test adding measurements to active session."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": "p1"}, {"id": "p2"}]
        mock_pack.get_patterns_for_context.return_value = (
            [{"id": "p1"}],
            {
                "total_patterns": 2,
                "passed": 1,
                "context_filtered": 1,
                "scope_filtered": 0,
                "filter_rate": 0.50,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
                "target_achieved": True,
            },
        )

        session = create_precision_tracking_session(mock_pack)
        context = {"section": "budget"}

        patterns, stats = add_measurement_to_session(session, context)

        assert session["measurement_count"] == 1
        assert len(session["measurements"]) == 1
        assert len(session["contexts_tested"]) == 1
        assert session["contexts_tested"][0] == context
        assert session["cumulative_stats"]["total_patterns_processed"] == 2
        assert session["cumulative_stats"]["total_patterns_filtered"] == 1

    def test_multiple_measurements_in_session(self):
        """Test adding multiple measurements to session."""
        mock_pack = MagicMock()
        mock_pack.patterns = [{"id": f"p{i}"} for i in range(10)]
        mock_pack.get_patterns_for_context.return_value = (
            [{"id": "p1"}],
            {
                "total_patterns": 10,
                "passed": 1,
                "context_filtered": 9,
                "scope_filtered": 0,
                "filter_rate": 0.90,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
                "filtering_duration_ms": 5.0,
            },
        )

        session = create_precision_tracking_session(mock_pack)

        contexts = [
            {"section": "budget"},
            {"section": "indicators"},
            {"section": "financial"},
        ]

        for context in contexts:
            add_measurement_to_session(session, context)

        assert session["measurement_count"] == 3
        assert len(session["measurements"]) == 3
        assert session["cumulative_stats"]["total_patterns_processed"] == 30
        assert session["cumulative_stats"]["total_patterns_filtered"] == 27
        assert session["cumulative_stats"]["total_filtering_time_ms"] == 15.0

    def test_finalize_session_with_report(self):
        """Test finalizing session with full report generation."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
                "filter_rate": 0.0,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
                "meets_60_percent_target": True,
            },
        )

        session = create_precision_tracking_session(mock_pack, "test_session")
        add_measurement_to_session(session, {})

        results = finalize_precision_tracking_session(
            session, generate_full_report=True
        )

        assert results["session_id"] == "test_session"
        assert results["status"] == "FINALIZED"
        assert results["measurement_count"] == 1
        assert "aggregate_report" in results
        assert "summary" in results
        assert "start_timestamp" in results
        assert "end_timestamp" in results

    def test_finalize_empty_session(self):
        """Test finalizing session with no measurements."""
        mock_pack = MagicMock()
        session = create_precision_tracking_session(mock_pack)

        results = finalize_precision_tracking_session(session)

        assert results["measurement_count"] == 0
        assert results["summary"] == "No measurements recorded"

    def test_finalize_session_without_report(self):
        """Test finalizing session without full report."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 0,
                "passed": 0,
                "context_filtered": 0,
                "scope_filtered": 0,
            },
        )

        session = create_precision_tracking_session(mock_pack)
        add_measurement_to_session(session, {})

        results = finalize_precision_tracking_session(
            session, generate_full_report=False
        )

        assert "aggregate_report" not in results
        assert results["measurement_count"] == 1


class TestComparePrecisionAcrossPolicyAreas:
    """Test cross-policy-area precision comparison."""

    def test_compare_two_policy_areas(self):
        """Test comparing precision across two policy areas."""
        mock_pack_01 = MagicMock()
        mock_pack_01.patterns = []
        mock_pack_01.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 100,
                "passed": 40,
                "context_filtered": 60,
                "scope_filtered": 0,
                "filter_rate": 0.60,
                "integration_validated": True,
                "false_positive_reduction": 0.60,
                "meets_60_percent_target": True,
            },
        )

        mock_pack_02 = MagicMock()
        mock_pack_02.patterns = []
        mock_pack_02.get_patterns_for_context.return_value = (
            [],
            {
                "total_patterns": 100,
                "passed": 70,
                "context_filtered": 30,
                "scope_filtered": 0,
                "filter_rate": 0.30,
                "integration_validated": True,
                "false_positive_reduction": 0.45,
                "meets_60_percent_target": False,
            },
        )

        packs = {
            "PA01": mock_pack_01,
            "PA02": mock_pack_02,
        }

        comparison = compare_precision_across_policy_areas(packs)

        assert comparison["policy_areas_tested"] == 2
        assert comparison["areas_meeting_target"] == 1
        assert "rankings" in comparison
        assert "best_performer" in comparison
        assert "worst_performer" in comparison
        assert comparison["best_performer"]["policy_area"] == "PA01"
        assert comparison["worst_performer"]["policy_area"] == "PA02"

    def test_compare_no_successful_measurements(self):
        """Test comparison when all measurements fail."""
        mock_pack = MagicMock()
        mock_pack.patterns = []
        mock_pack.get_patterns_for_context.side_effect = Exception("Error")

        packs = {"PA01": mock_pack}

        comparison = compare_precision_across_policy_areas(packs)

        assert comparison["policy_areas_tested"] == 0
        assert comparison["comparison_status"] == "FAILED"

    def test_compare_ranking_by_target_achievement(self):
        """Test ranking by target achievement rate."""
        packs = {}

        for i in range(3):
            mock_pack = MagicMock()
            mock_pack.patterns = []
            target_rate = (i + 1) * 0.25
            mock_pack.get_patterns_for_context.return_value = (
                [],
                {
                    "total_patterns": 100,
                    "passed": 50,
                    "context_filtered": 50,
                    "scope_filtered": 0,
                    "filter_rate": 0.50,
                    "integration_validated": True,
                    "false_positive_reduction": 0.60 * target_rate,
                    "meets_60_percent_target": target_rate >= 0.9,
                },
            )
            packs[f"PA0{i+1}"] = mock_pack

        comparison = compare_precision_across_policy_areas(packs)

        rankings = comparison["rankings"]["by_target_achievement"]
        assert len(rankings) == 3
        assert rankings[0][0] == "PA03"
        assert rankings[-1][0] == "PA01"


class TestExportPrecisionMetrics:
    """Test precision metrics export for monitoring."""

    def test_export_json_format(self):
        """Test exporting metrics in JSON format."""
        measurements = [
            {
                "false_positive_reduction": 0.60,
                "filter_rate": 0.50,
                "integration_validated": True,
                "meets_60_percent_target": True,
            },
            {
                "false_positive_reduction": 0.45,
                "filter_rate": 0.30,
                "integration_validated": True,
                "meets_60_percent_target": False,
            },
        ]

        result = export_precision_metrics_for_monitoring(measurements, "json")

        import json

        parsed = json.loads(result)

        assert "timestamp" in parsed
        assert parsed["measurement_count"] == 2
        assert parsed["target_achievement_count"] == 1
        assert parsed["target_achievement_rate"] == 0.5
        assert parsed["meets_60_percent_target"] is True

    def test_export_prometheus_format(self):
        """Test exporting metrics in Prometheus format."""
        measurements = [
            {
                "false_positive_reduction": 0.60,
                "filter_rate": 0.50,
                "integration_validated": True,
            }
        ]

        result = export_precision_metrics_for_monitoring(measurements, "prometheus")

        assert "precision_target_achievement_rate" in result
        assert "precision_avg_fp_reduction" in result
        assert "precision_measurement_count" in result
        assert "# HELP" in result
        assert "# TYPE" in result

    def test_export_datadog_format(self):
        """Test exporting metrics in Datadog format."""
        measurements = [
            {
                "false_positive_reduction": 0.60,
                "filter_rate": 0.50,
                "integration_validated": True,
            }
        ]

        result = export_precision_metrics_for_monitoring(measurements, "datadog")

        import json

        parsed = json.loads(result)

        assert isinstance(parsed, list)
        assert len(parsed) == 3
        assert all("metric" in m for m in parsed)
        assert all("points" in m for m in parsed)
        assert all("tags" in m for m in parsed)

    def test_export_empty_measurements(self):
        """Test exporting with no measurements."""
        result = export_precision_metrics_for_monitoring([], "json")

        import json

        parsed = json.loads(result)

        assert "error" in parsed
        assert parsed["error"] == "No measurements"

    def test_export_invalid_format(self):
        """Test exporting with invalid format."""
        measurements = [{"false_positive_reduction": 0.60}]

        result = export_precision_metrics_for_monitoring(measurements, "invalid")

        assert result == ""
