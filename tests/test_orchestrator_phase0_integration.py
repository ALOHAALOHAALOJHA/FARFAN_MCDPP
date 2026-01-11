"""
Unit Tests for Phase 0 and Orchestrator Integration
====================================================

Tests the wiring between Phase 0 components (RuntimeConfig, exit gates)
and the Orchestrator to ensure proper integration and contract enforcement.

Test Coverage:
1. Orchestrator accepts RuntimeConfig parameter
2. Orchestrator validates RuntimeConfig in __init__
3. Orchestrator fails if Phase 0 gates failed
4. Orchestrator logs runtime mode
5. _load_configuration includes runtime mode in config
6. Phase0ValidationResult dataclass functionality
"""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path
# Phase 0 imports
# Orchestrator imports
from farfan_pipeline.orchestration.orchestrator import Orchestrator, Phase0ValidationResult

from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode
from farfan_pipeline.phases.Phase_zero.phase0_50_01_exit_gates import GateResult

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_runtime_config_prod():
    """RuntimeConfig in PROD mode."""
    config = RuntimeConfig.from_dict(
        {
            "mode": "prod",
            "allow_contradiction_fallback": False,
            "allow_validator_disable": False,
            "allow_execution_estimates": False,
            "allow_networkx_fallback": False,
            "allow_spacy_fallback": False,
            "allow_dev_ingestion_fallbacks": False,
            "allow_aggregation_defaults": False,
        }
    )
    return config


@pytest.fixture
def mock_runtime_config_dev():
    """RuntimeConfig in DEV mode."""
    config = RuntimeConfig.from_dict(
        {
            "mode": "dev",
            "allow_contradiction_fallback": True,
            "allow_validator_disable": True,
            "allow_execution_estimates": True,
            "allow_networkx_fallback": True,
            "allow_spacy_fallback": True,
            "allow_dev_ingestion_fallbacks": True,
            "allow_aggregation_defaults": True,
        }
    )
    return config


@pytest.fixture
def mock_phase0_validation_success():
    """Phase0ValidationResult with all 7 gates passed (P1 Hardening compliant)."""
    gate_results = [
        GateResult(passed=True, gate_name="bootstrap", gate_id=1),
        GateResult(passed=True, gate_name="input_verification", gate_id=2),
        GateResult(passed=True, gate_name="boot_checks", gate_id=3),
        GateResult(passed=True, gate_name="determinism", gate_id=4),
        GateResult(passed=True, gate_name="questionnaire_integrity", gate_id=5),
        GateResult(passed=True, gate_name="method_registry", gate_id=6),
        GateResult(passed=True, gate_name="smoke_tests", gate_id=7),
    ]
    return Phase0ValidationResult(
        all_passed=True,
        gate_results=gate_results,
        validation_time=datetime.now(UTC).isoformat(),
        seed_snapshot={"python": 42, "numpy": 42},
        questionnaire_sha256="a" * 64,
        input_pdf_sha256="b" * 64,
    )


@pytest.fixture
def mock_phase0_validation_failure():
    """Phase0ValidationResult with bootstrap gate failed."""
    gate_results = [
        GateResult(
            passed=False, gate_name="bootstrap", gate_id=1, reason="Runtime config not loaded"
        ),
    ]
    return Phase0ValidationResult(
        all_passed=False,
        gate_results=gate_results,
        validation_time=datetime.now(UTC).isoformat(),
        seed_snapshot={},
        questionnaire_sha256="",
        input_pdf_sha256="",
    )


@pytest.fixture
def mock_phase0_validation_p1_hardening_failure():
    """Phase0ValidationResult with P1 Hardening gates (5-7) failed but mandatory (1-4) passed."""
    gate_results = [
        GateResult(passed=True, gate_name="bootstrap", gate_id=1),
        GateResult(passed=True, gate_name="input_verification", gate_id=2),
        GateResult(passed=True, gate_name="boot_checks", gate_id=3),
        GateResult(passed=True, gate_name="determinism", gate_id=4),
        GateResult(
            passed=False, gate_name="questionnaire_integrity", gate_id=5, reason="Hash mismatch"
        ),
        GateResult(
            passed=False, gate_name="method_registry", gate_id=6, reason="Only 400 of 416 methods"
        ),
        GateResult(passed=True, gate_name="smoke_tests", gate_id=7),
    ]
    return Phase0ValidationResult(
        all_passed=False,
        gate_results=gate_results,
        validation_time=datetime.now(UTC).isoformat(),
        seed_snapshot={"python": 42, "numpy": 42},
        questionnaire_sha256="c" * 64,
        input_pdf_sha256="d" * 64,
    )


@pytest.fixture
def mock_orchestrator_dependencies():
    """Mock dependencies for Orchestrator initialization."""
    method_executor = Mock()
    questionnaire = Mock()
    questionnaire.data = {
        "blocks": {"micro_questions": [], "meso_questions": [], "macro_question": {}}
    }
    executor_config = Mock()

    return {
        "method_executor": method_executor,
        "questionnaire": questionnaire,
        "executor_config": executor_config,
    }


# ============================================================================
# TEST SUITE 1: Phase0ValidationResult Dataclass
# ============================================================================


class TestPhase0ValidationResult:
    """Test Phase0ValidationResult dataclass functionality."""

    def test_phase0_validation_result_all_passed(self, mock_phase0_validation_success):
        """Test Phase0ValidationResult when all 7 gates pass."""
        result = mock_phase0_validation_success

        assert result.all_passed is True
        assert len(result.gate_results) == 7
        assert all(g.passed for g in result.gate_results)
        assert len(result.get_failed_gates()) == 0
        assert result.has_mandatory_gates_passed() is True
        assert result.has_p1_hardening_gates_passed() is True

    def test_phase0_validation_result_failure(self, mock_phase0_validation_failure):
        """Test Phase0ValidationResult when gates fail."""
        result = mock_phase0_validation_failure

        assert result.all_passed is False
        assert len(result.gate_results) == 1
        assert result.gate_results[0].passed is False
        assert len(result.get_failed_gates()) == 1
        assert result.get_failed_gates()[0].gate_name == "bootstrap"
        # Mandatory gates NOT passed because bootstrap failed
        assert result.has_mandatory_gates_passed() is False

    def test_phase0_validation_p1_hardening_gates(
        self, mock_phase0_validation_p1_hardening_failure
    ):
        """Test Phase0ValidationResult with P1 hardening gates failed."""
        result = mock_phase0_validation_p1_hardening_failure

        assert result.all_passed is False
        assert result.has_mandatory_gates_passed() is True  # Gates 1-4 passed
        assert result.has_p1_hardening_gates_passed() is False  # Gates 5-7 have failures

        failed = result.get_failed_gates()
        failed_names = [g.gate_name for g in failed]
        assert "questionnaire_integrity" in failed_names
        assert "method_registry" in failed_names

    def test_phase0_validation_get_summary_success(self, mock_phase0_validation_success):
        """Test get_summary() method for successful validation."""
        result = mock_phase0_validation_success
        summary = result.get_summary()

        assert "7/7 gates passed" in summary
        assert "failed" not in summary

    def test_phase0_validation_get_summary_failure(self, mock_phase0_validation_failure):
        """Test get_summary() method for failed validation."""
        result = mock_phase0_validation_failure
        summary = result.get_summary()

        assert "0/7 gates passed" in summary
        assert "bootstrap failed" in summary

    def test_phase0_validation_seed_snapshot(self, mock_phase0_validation_success):
        """Test seed_snapshot attribute for determinism."""
        result = mock_phase0_validation_success

        assert result.seed_snapshot == {"python": 42, "numpy": 42}
        seeds_valid, missing = result.validate_determinism_seeds()
        assert seeds_valid is True
        assert missing == []

    def test_phase0_validation_missing_seeds(self, mock_phase0_validation_failure):
        """Test seed validation when seeds are missing."""
        result = mock_phase0_validation_failure

        seeds_valid, missing = result.validate_determinism_seeds()
        assert seeds_valid is False
        assert "python" in missing
        assert "numpy" in missing

    def test_phase0_validation_get_gate_by_name(self, mock_phase0_validation_success):
        """Test get_gate_by_name() method."""
        result = mock_phase0_validation_success

        bootstrap_gate = result.get_gate_by_name("bootstrap")
        assert bootstrap_gate is not None
        assert bootstrap_gate.gate_id == 1
        assert bootstrap_gate.passed is True

        nonexistent = result.get_gate_by_name("nonexistent")
        assert nonexistent is None


# ============================================================================
# TEST SUITE 2: Orchestrator RuntimeConfig Integration
# ============================================================================


class TestOrchestratorRuntimeConfig:
    """Test Orchestrator integration with RuntimeConfig."""

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_orchestrator_accepts_runtime_config(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_prod,
    ):
        """Test that Orchestrator accepts runtime_config parameter."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies, runtime_config=mock_runtime_config_prod
        )

        assert orchestrator.runtime_config is not None
        assert orchestrator.runtime_config.mode == RuntimeMode.PROD

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_orchestrator_runtime_config_none(
        self, mock_validate_structure, mock_validate_phases, mock_orchestrator_dependencies
    ):
        """Test that Orchestrator works with runtime_config=None (legacy mode)."""
        orchestrator = Orchestrator(**mock_orchestrator_dependencies, runtime_config=None)

        assert orchestrator.runtime_config is None

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    @patch("orchestration.orchestrator.logger")
    def test_orchestrator_logs_runtime_mode_prod(
        self,
        mock_logger,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_prod,
    ):
        """Test that Orchestrator logs runtime mode (PROD)."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies, runtime_config=mock_runtime_config_prod
        )

        # Check that info was logged
        assert mock_logger.info.called
        found = False
        for call in mock_logger.info.call_args_list:
            if call.args and "orchestrator_runtime_mode" in str(call.args[0]):
                found = True
                break
            # Structlog style
            if call.args and call.args[0] == "orchestrator_runtime_mode":
                found = True
                break
        assert found, "orchestrator_runtime_mode not logged"

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    @patch("orchestration.orchestrator.logger")
    def test_orchestrator_logs_runtime_mode_dev(
        self,
        mock_logger,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_dev,
    ):
        """Test that Orchestrator logs runtime mode (DEV)."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies, runtime_config=mock_runtime_config_dev
        )

        assert mock_logger.info.called
        assert orchestrator.runtime_config.mode == RuntimeMode.DEV

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    @patch("orchestration.orchestrator.logger")
    def test_orchestrator_warns_if_no_runtime_config(
        self,
        mock_logger,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
    ):
        """Test that Orchestrator warns if runtime_config not provided."""
        orchestrator = Orchestrator(**mock_orchestrator_dependencies, runtime_config=None)

        # Check that warning was logged
        assert mock_logger.warning.called
        found = False
        for call in mock_logger.warning.call_args_list:
            if call.args and "orchestrator_no_runtime_config" in str(call.args[0]):
                found = True
                break
            if call.args and call.args[0] == "orchestrator_no_runtime_config":
                found = True
                break
        assert found, "orchestrator_no_runtime_config warning not logged"


# ============================================================================
# TEST SUITE 3: Orchestrator Phase 0 Validation Integration
# ============================================================================


class TestOrchestratorPhase0Validation:
    """Test Orchestrator integration with Phase 0 exit gate validation."""

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_orchestrator_accepts_phase0_validation(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_success,
    ):
        """Test that Orchestrator accepts phase0_validation parameter."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies, phase0_validation=mock_phase0_validation_success
        )

        assert orchestrator.phase0_validation is not None
        assert orchestrator.phase0_validation.all_passed is True

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_orchestrator_fails_if_phase0_gates_failed(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_failure,
    ):
        """Test that Orchestrator initialization fails if Phase 0 gates failed."""
        with pytest.raises(RuntimeError) as exc_info:
            Orchestrator(
                **mock_orchestrator_dependencies, phase0_validation=mock_phase0_validation_failure
            )

        assert "Phase 0 exit gates failed" in str(exc_info.value)
        assert "bootstrap" in str(exc_info.value)

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    @patch("orchestration.orchestrator.logger")
    def test_orchestrator_logs_phase0_validation_success(
        self,
        mock_logger,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_success,
    ):
        """Test that Orchestrator logs Phase 0 validation success."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies, phase0_validation=mock_phase0_validation_success
        )

        # Check that info was logged
        assert mock_logger.info.called
        found = False
        for call in mock_logger.info.call_args_list:
            if call.args and "orchestrator_phase0_validation_passed" in str(call.args[0]):
                found = True
                break
            if call.args and call.args[0] == "orchestrator_phase0_validation_passed":
                found = True
                break
        assert found, "orchestrator_phase0_validation_passed not logged"


# ============================================================================
# TEST SUITE 4: Orchestrator _load_configuration Integration
# ============================================================================


class TestOrchestratorLoadConfiguration:
    """Test _load_configuration method with Phase 0 integration."""

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_load_configuration_includes_runtime_mode(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_prod,
    ):
        """Test that _load_configuration includes runtime mode in config dict."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies, runtime_config=mock_runtime_config_prod
        )
        orchestrator._phase_instrumentation[0] = Mock()

        config = orchestrator._load_configuration()

        assert "_runtime_mode" in config
        assert config["_runtime_mode"] == "prod"
        assert "_strict_mode" in config
        assert config["_strict_mode"] is True

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_load_configuration_without_runtime_config(
        self, mock_validate_structure, mock_validate_phases, mock_orchestrator_dependencies
    ):
        """Test that _load_configuration works without runtime_config."""
        orchestrator = Orchestrator(**mock_orchestrator_dependencies, runtime_config=None)
        orchestrator._phase_instrumentation[0] = Mock()

        config = orchestrator._load_configuration()

        # Should not have runtime mode keys
        assert "_runtime_mode" not in config
        assert "_strict_mode" not in config

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_load_configuration_validates_phase0_success(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_success,
    ):
        """Test that _load_configuration validates Phase 0 completion (success case)."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies, phase0_validation=mock_phase0_validation_success
        )
        orchestrator._phase_instrumentation[0] = Mock()

        # Should not raise
        config = orchestrator._load_configuration()
        assert config is not None

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_load_configuration_fails_if_phase0_failed(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_failure,
    ):
        """Test that _load_configuration would fail if Phase 0 failed.

        Note: This test shows that __init__ catches Phase 0 failures,
        preventing _load_configuration from ever being called.
        """
        # __init__ should raise RuntimeError before we even get to _load_configuration
        with pytest.raises(RuntimeError) as exc_info:
            Orchestrator(
                **mock_orchestrator_dependencies, phase0_validation=mock_phase0_validation_failure
            )

        assert "Phase 0 exit gates failed" in str(exc_info.value)


# ============================================================================
# TEST SUITE 5: Combined Integration Tests
# ============================================================================


class TestOrchestratorFullIntegration:
    """Test full integration of RuntimeConfig + Phase 0 validation."""

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_orchestrator_with_full_phase0_context(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_prod,
        mock_phase0_validation_success,
    ):
        """Test Orchestrator with both RuntimeConfig and Phase 0 validation."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=mock_runtime_config_prod,
            phase0_validation=mock_phase0_validation_success,
        )
        orchestrator._phase_instrumentation[0] = Mock()

        # Verify both are stored
        assert orchestrator.runtime_config is not None
        assert orchestrator.runtime_config.mode == RuntimeMode.PROD
        assert orchestrator.phase0_validation is not None
        assert orchestrator.phase0_validation.all_passed is True

        # Verify _load_configuration includes runtime mode
        config = orchestrator._load_configuration()
        assert config["_runtime_mode"] == "prod"

    @patch("farfan_pipeline.orchestration.orchestrator.validate_phase_definitions")
    def test_orchestrator_backward_compatible_no_phase0(
        self, mock_validate_structure, mock_validate_phases, mock_orchestrator_dependencies
    ):
        """Test that Orchestrator works without any Phase 0 parameters (legacy mode)."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies
            # No runtime_config, no phase0_validation
        )
        orchestrator._phase_instrumentation[0] = Mock()

        assert orchestrator.runtime_config is None
        assert orchestrator.phase0_validation is None

        # Should still work
        config = orchestrator._load_configuration()
        assert config is not None
        assert "_runtime_mode" not in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
