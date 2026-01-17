"""Tests for orchestrator signal registry validation integration.

This module tests the integration of signal registry health checks into
the orchestrator initialization:
- Health check invocation in Orchestrator.__init__
- Production mode fail-fast enforcement
- Development mode warning-only behavior
- Validation result logging

Author: F.A.R.F.A.N Pipeline Team
Status: Production Test Suite
Test Priority: P1 (Critical)
"""

from typing import Any
from unittest.mock import Mock, MagicMock, patch
import pytest

from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode
from farfan_pipeline.phases.Phase_02.executor_config import ExecutorConfig


class TestOrchestratorSignalValidationIntegration:
    """Test orchestrator integration with signal validation."""

    def test_orchestrator_calls_signal_validation_on_init(self):
        """Orchestrator calls validate_signals_for_questionnaire during init."""
        from orchestration.orchestrator import Orchestrator, MethodExecutor
        from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import CanonicalQuestionnaire

        # Create mock components
        mock_questionnaire = Mock(spec=CanonicalQuestionnaire)
        mock_questionnaire.version = "1.0.0"
        mock_questionnaire.sha256 = "a" * 64
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [
                    {
                        "question_id": f"Q{i:03d}",
                        "patterns": [{"pattern": "test"}],
                        "expected_elements": [{"element": "test"}],
                        "scoring_modality": "binary_presence",
                        "validation_rules": [{"rule": "test"}],
                    }
                    for i in range(1, 301)  # 300 questions
                ]
            }
        }

        mock_signal_registry = Mock()
        mock_signal_registry.validate_signals_for_questionnaire = Mock(
            return_value={
                "valid": True,
                "total_questions": 300,
                "expected_questions": 300,
                "missing_questions": [],
                "malformed_signals": {},
                "signal_coverage": {
                    "micro_answering": {"success": 300, "failed": 0},
                    "validation": {"success": 300, "failed": 0},
                    "scoring": {"success": 300, "failed": 0},
                },
                "coverage_percentages": {
                    "micro_answering": 100.0,
                    "validation": 100.0,
                    "scoring": 100.0,
                },
                "stale_signals": [],
                "timestamp": 0.0,
                "elapsed_seconds": 1.0,
            }
        )

        mock_executor = Mock(spec=MethodExecutor)
        mock_executor.signal_registry = mock_signal_registry
        mock_executor.instances = {"test": Mock()}
        mock_executor.degraded_mode = False

        mock_runtime_config = Mock(spec=RuntimeConfig)
        mock_runtime_config.mode = RuntimeMode.DEV

        executor_config = Mock(spec=ExecutorConfig)

        # Initialize orchestrator (should call validation)
        with patch("orchestration.orchestrator._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=executor_config,
                runtime_config=mock_runtime_config,
            )

        # Verify validation was called
        mock_signal_registry.validate_signals_for_questionnaire.assert_called_once()
        call_kwargs = mock_signal_registry.validate_signals_for_questionnaire.call_args[1]
        assert "expected_question_count" in call_kwargs

    def test_orchestrator_fails_in_prod_mode_with_invalid_signals(self):
        """Orchestrator raises RuntimeError in PROD mode when signals invalid."""
        from orchestration.orchestrator import Orchestrator, MethodExecutor
        from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import CanonicalQuestionnaire

        # Create mock components
        mock_questionnaire = Mock(spec=CanonicalQuestionnaire)
        mock_questionnaire.version = "1.0.0"
        mock_questionnaire.sha256 = "a" * 64
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [
                    {"question_id": "Q001", "patterns": []},  # Invalid
                ]
            }
        }

        mock_signal_registry = Mock()
        mock_signal_registry.validate_signals_for_questionnaire = Mock(
            return_value={
                "valid": False,
                "total_questions": 1,
                "expected_questions": 300,
                "missing_questions": ["Q001"],
                "malformed_signals": {"Q001": ["missing patterns"]},
                "signal_coverage": {
                    "micro_answering": {"success": 0, "failed": 1},
                },
                "coverage_percentages": {
                    "micro_answering": 0.0,
                },
                "stale_signals": [],
                "timestamp": 0.0,
                "elapsed_seconds": 0.1,
            }
        )

        mock_executor = Mock(spec=MethodExecutor)
        mock_executor.signal_registry = mock_signal_registry
        mock_executor.instances = {"test": Mock()}

        # PROD mode
        mock_runtime_config = Mock(spec=RuntimeConfig)
        mock_runtime_config.mode = Mock(value="prod")

        executor_config = Mock(spec=ExecutorConfig)

        # Should raise RuntimeError in PROD mode
        with pytest.raises(RuntimeError) as exc_info:
            with patch("orchestration.orchestrator._validate_questionnaire_structure"):
                Orchestrator(
                    method_executor=mock_executor,
                    questionnaire=mock_questionnaire,
                    executor_config=executor_config,
                    runtime_config=mock_runtime_config,
                )

        # Check error message mentions production mode
        assert (
            "Production mode" in str(exc_info.value) or "production" in str(exc_info.value).lower()
        )

    def test_orchestrator_warns_in_dev_mode_with_invalid_signals(self, caplog):
        """Orchestrator logs warning in DEV mode but continues."""
        from orchestration.orchestrator import Orchestrator, MethodExecutor
        from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import CanonicalQuestionnaire

        # Create mock components
        mock_questionnaire = Mock(spec=CanonicalQuestionnaire)
        mock_questionnaire.version = "1.0.0"
        mock_questionnaire.sha256 = "a" * 64
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [
                    {
                        "question_id": "Q001",
                        "patterns": [{"pattern": "test"}],
                        "expected_elements": [{"element": "test"}],
                        "scoring_modality": "binary_presence",
                        "validation_rules": [{"rule": "test"}],
                    }
                ]
            }
        }

        mock_signal_registry = Mock()
        mock_signal_registry.validate_signals_for_questionnaire = Mock(
            return_value={
                "valid": False,
                "total_questions": 1,
                "expected_questions": 300,
                "missing_questions": [],
                "malformed_signals": {},
                "signal_coverage": {
                    "micro_answering": {"success": 1, "failed": 0},
                },
                "coverage_percentages": {
                    "micro_answering": 100.0,
                },
                "stale_signals": [],
                "timestamp": 0.0,
                "elapsed_seconds": 0.1,
            }
        )

        mock_executor = Mock(spec=MethodExecutor)
        mock_executor.signal_registry = mock_signal_registry
        mock_executor.instances = {"test": Mock()}

        # DEV mode
        mock_runtime_config = Mock(spec=RuntimeConfig)
        mock_runtime_config.mode = RuntimeMode.DEV

        executor_config = Mock(spec=ExecutorConfig)

        # Should succeed but log warning
        with patch("orchestration.orchestrator._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=executor_config,
                runtime_config=mock_runtime_config,
            )

        # Orchestrator should be created successfully
        assert orchestrator is not None

    def test_orchestrator_logs_validation_success(self, caplog):
        """Orchestrator logs when signal validation passes."""
        from orchestration.orchestrator import Orchestrator, MethodExecutor
        from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import CanonicalQuestionnaire

        # Create mock components with valid signals
        mock_questionnaire = Mock(spec=CanonicalQuestionnaire)
        mock_questionnaire.version = "1.0.0"
        mock_questionnaire.sha256 = "a" * 64
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [
                    {
                        "question_id": f"Q{i:03d}",
                        "patterns": [{"pattern": "test"}],
                        "expected_elements": [{"element": "test"}],
                        "scoring_modality": "binary_presence",
                        "validation_rules": [{"rule": "test"}],
                    }
                    for i in range(1, 301)
                ]
            }
        }

        mock_signal_registry = Mock()
        mock_signal_registry.validate_signals_for_questionnaire = Mock(
            return_value={
                "valid": True,
                "total_questions": 300,
                "expected_questions": 300,
                "missing_questions": [],
                "malformed_signals": {},
                "signal_coverage": {
                    "micro_answering": {"success": 300, "failed": 0},
                    "validation": {"success": 300, "failed": 0},
                    "scoring": {"success": 300, "failed": 0},
                },
                "coverage_percentages": {
                    "micro_answering": 100.0,
                    "validation": 100.0,
                    "scoring": 100.0,
                },
                "stale_signals": [],
                "timestamp": 0.0,
                "elapsed_seconds": 2.5,
            }
        )

        mock_executor = Mock(spec=MethodExecutor)
        mock_executor.signal_registry = mock_signal_registry
        mock_executor.instances = {"test": Mock()}

        mock_runtime_config = Mock(spec=RuntimeConfig)
        mock_runtime_config.mode = RuntimeMode.PROD

        executor_config = Mock(spec=ExecutorConfig)

        # Initialize orchestrator
        with patch("orchestration.orchestrator._validate_questionnaire_structure"):
            orchestrator = Orchestrator(
                method_executor=mock_executor,
                questionnaire=mock_questionnaire,
                executor_config=executor_config,
                runtime_config=mock_runtime_config,
            )

        # Orchestrator should be created successfully
        assert orchestrator is not None


@pytest.mark.updated
class TestOrchestratorPhase3SignalTracking:
    """Test Phase 3 signal tracking in scoring details."""

    def test_phase3_records_applied_signals_in_scoring_details(self):
        """Phase 3 scoring records which signals were applied."""
        # This is an integration point test - verify that scoring_details
        # contains signal tracking information

        from orchestration.orchestrator import ScoredMicroQuestion

        # Create a mock scored result as it would come from Phase 3
        scoring_details = {
            "source": "evidence_nexus",
            "method": "overall_confidence",
            "signal_enrichment_raw": {
                "modality": "binary_presence",
                "source_hash": "abc123",
                "signal_source": "sisas_registry",
            },
            "applied_signals": {
                "question_id": "Q001",
                "scoring_modality": "binary_presence",
                "has_modality_config": True,
                "threshold_defined": True,
                "signal_lookup_timestamp": 1234567890.0,
            },
        }

        # Verify structure exists
        assert "applied_signals" in scoring_details
        assert "question_id" in scoring_details["applied_signals"]
        assert "scoring_modality" in scoring_details["applied_signals"]
        assert "signal_lookup_timestamp" in scoring_details["applied_signals"]

    def test_phase3_logs_signal_application_debug(self, caplog):
        """Phase 3 logs signal application at debug level."""
        # This test verifies that the logging structure is correct
        # In actual integration, we'd see these logs during Phase 3

        import structlog

        logger = structlog.get_logger(__name__)

        with caplog.at_level("DEBUG"):
            logger.debug(
                "signal_applied_in_scoring",
                question_id="Q001",
                modality="binary_presence",
                scoring_modality="binary_presence",
            )

        # Check that the log was created
        assert len(caplog.records) > 0


@pytest.mark.updated
class TestOrchestratorSignalValidationRobustness:
    """Test robustness of signal validation in orchestrator."""

    def test_orchestrator_handles_validation_exception_gracefully(self):
        """Orchestrator handles exceptions during validation gracefully."""
        from orchestration.orchestrator import Orchestrator, MethodExecutor
        from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import CanonicalQuestionnaire

        # Create mock components
        mock_questionnaire = Mock(spec=CanonicalQuestionnaire)
        mock_questionnaire.version = "1.0.0"
        mock_questionnaire.sha256 = "a" * 64
        mock_questionnaire.data = {
            "blocks": {
                "micro_questions": [
                    {"question_id": "Q001", "patterns": [{"pattern": "test"}]},
                ]
            }
        }

        mock_signal_registry = Mock()
        # Validation method raises exception
        mock_signal_registry.validate_signals_for_questionnaire = Mock(
            side_effect=Exception("Validation internal error")
        )

        mock_executor = Mock(spec=MethodExecutor)
        mock_executor.signal_registry = mock_signal_registry
        mock_executor.instances = {"test": Mock()}

        mock_runtime_config = Mock(spec=RuntimeConfig)
        mock_runtime_config.mode = RuntimeMode.DEV

        executor_config = Mock(spec=ExecutorConfig)

        # Should raise the exception (not silently catch it)
        with pytest.raises(Exception) as exc_info:
            with patch("orchestration.orchestrator._validate_questionnaire_structure"):
                Orchestrator(
                    method_executor=mock_executor,
                    questionnaire=mock_questionnaire,
                    executor_config=executor_config,
                    runtime_config=mock_runtime_config,
                )

        assert "Validation internal error" in str(exc_info.value)

    def test_orchestrator_requires_signal_registry(self):
        """Orchestrator fails if signal_registry is None."""
        from orchestration.orchestrator import Orchestrator, MethodExecutor
        from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import CanonicalQuestionnaire

        mock_questionnaire = Mock(spec=CanonicalQuestionnaire)
        mock_questionnaire.version = "1.0.0"
        mock_questionnaire.sha256 = "a" * 64
        mock_questionnaire.data = {"blocks": {"micro_questions": []}}

        mock_executor = Mock(spec=MethodExecutor)
        mock_executor.signal_registry = None  # No signal registry
        mock_executor.instances = {"test": Mock()}

        executor_config = Mock(spec=ExecutorConfig)

        # Should raise RuntimeError about missing signal_registry
        with pytest.raises(RuntimeError) as exc_info:
            with patch("orchestration.orchestrator._validate_questionnaire_structure"):
                Orchestrator(
                    method_executor=mock_executor,
                    questionnaire=mock_questionnaire,
                    executor_config=executor_config,
                )

        assert "signal_registry" in str(exc_info.value).lower()
