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

import pytest
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from dataclasses import asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Phase 0 imports
from canonic_phases.Phase_zero.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode
from canonic_phases.Phase_zero.phase0_50_01_exit_gates import GateResult

# Orchestrator imports
from farfan_pipeline.orchestration.orchestrator import Orchestrator, Phase0ValidationResult


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_runtime_config_prod():
    """RuntimeConfig in PROD mode."""
    config = RuntimeConfig.from_dict({
        "mode": "prod",
        "allow_contradiction_fallback": False,
        "allow_validator_disable": False,
        "allow_execution_estimates": False,
        "allow_networkx_fallback": False,
        "allow_spacy_fallback": False,
        "allow_dev_ingestion_fallbacks": False,
        "allow_aggregation_defaults": False,
    })
    return config


@pytest.fixture
def mock_runtime_config_dev():
    """RuntimeConfig in DEV mode."""
    config = RuntimeConfig.from_dict({
        "mode": "dev",
        "allow_contradiction_fallback": True,
        "allow_validator_disable": True,
        "allow_execution_estimates": True,
        "allow_networkx_fallback": True,
        "allow_spacy_fallback": True,
        "allow_dev_ingestion_fallbacks": True,
        "allow_aggregation_defaults": True,
    })
    return config


@pytest.fixture
def mock_phase0_validation_success():
    """Phase0ValidationResult with all gates passed."""
    gate_results = [
        GateResult(passed=True, gate_name="bootstrap", gate_id=1),
        GateResult(passed=True, gate_name="input_verification", gate_id=2),
        GateResult(passed=True, gate_name="boot_checks", gate_id=3),
        GateResult(passed=True, gate_name="determinism", gate_id=4),
    ]
    return Phase0ValidationResult(
        all_passed=True,
        gate_results=gate_results,
        validation_time=datetime.utcnow().isoformat()
    )


@pytest.fixture
def mock_phase0_validation_failure():
    """Phase0ValidationResult with bootstrap gate failed."""
    gate_results = [
        GateResult(
            passed=False,
            gate_name="bootstrap",
            gate_id=1,
            reason="Runtime config not loaded"
        ),
    ]
    return Phase0ValidationResult(
        all_passed=False,
        gate_results=gate_results,
        validation_time=datetime.utcnow().isoformat()
    )


@pytest.fixture
def mock_orchestrator_dependencies():
    """Mock dependencies for Orchestrator initialization."""
    method_executor = Mock()
    questionnaire = Mock()
    questionnaire.data = {
        "blocks": {
            "micro_questions": [],
            "meso_questions": [],
            "macro_question": {}
        }
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
        """Test Phase0ValidationResult when all gates pass."""
        result = mock_phase0_validation_success
        
        assert result.all_passed is True
        assert len(result.gate_results) == 4
        assert all(g.passed for g in result.gate_results)
        assert len(result.get_failed_gates()) == 0
    
    def test_phase0_validation_result_failure(self, mock_phase0_validation_failure):
        """Test Phase0ValidationResult when gates fail."""
        result = mock_phase0_validation_failure
        
        assert result.all_passed is False
        assert len(result.gate_results) == 1
        assert result.gate_results[0].passed is False
        assert len(result.get_failed_gates()) == 1
        assert result.get_failed_gates()[0].gate_name == "bootstrap"
    
    def test_phase0_validation_get_summary_success(self, mock_phase0_validation_success):
        """Test get_summary() method for successful validation."""
        result = mock_phase0_validation_success
        summary = result.get_summary()
        
        assert "4/4 gates passed" in summary
        assert "failed" not in summary
    
    def test_phase0_validation_get_summary_failure(self, mock_phase0_validation_failure):
        """Test get_summary() method for failed validation."""
        result = mock_phase0_validation_failure
        summary = result.get_summary()
        
        assert "0/1 gates passed" in summary or "1 gates passed" in summary
        assert "bootstrap failed" in summary


# ============================================================================
# TEST SUITE 2: Orchestrator RuntimeConfig Integration
# ============================================================================

class TestOrchestratorRuntimeConfig:
    """Test Orchestrator integration with RuntimeConfig."""
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_orchestrator_accepts_runtime_config(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_prod
    ):
        """Test that Orchestrator accepts runtime_config parameter."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=mock_runtime_config_prod
        )
        
        assert orchestrator.runtime_config is not None
        assert orchestrator.runtime_config.mode == RuntimeMode.PROD
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_orchestrator_runtime_config_none(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies
    ):
        """Test that Orchestrator works with runtime_config=None (legacy mode)."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=None
        )
        
        assert orchestrator.runtime_config is None
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    @patch('farfan_pipeline.orchestration.orchestrator.logger')
    def test_orchestrator_logs_runtime_mode_prod(
        self,
        mock_logger,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_prod
    ):
        """Test that Orchestrator logs runtime mode (PROD)."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=mock_runtime_config_prod
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
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    @patch('farfan_pipeline.orchestration.orchestrator.logger')
    def test_orchestrator_logs_runtime_mode_dev(
        self,
        mock_logger,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_dev
    ):
        """Test that Orchestrator logs runtime mode (DEV)."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=mock_runtime_config_dev
        )
        
        assert mock_logger.info.called
        assert orchestrator.runtime_config.mode == RuntimeMode.DEV
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    @patch('farfan_pipeline.orchestration.orchestrator.logger')
    def test_orchestrator_warns_if_no_runtime_config(
        self,
        mock_logger,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies
    ):
        """Test that Orchestrator warns if runtime_config not provided."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=None
        )
        
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
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_orchestrator_accepts_phase0_validation(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_success
    ):
        """Test that Orchestrator accepts phase0_validation parameter."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            phase0_validation=mock_phase0_validation_success
        )
        
        assert orchestrator.phase0_validation is not None
        assert orchestrator.phase0_validation.all_passed is True
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_orchestrator_fails_if_phase0_gates_failed(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_failure
    ):
        """Test that Orchestrator initialization fails if Phase 0 gates failed."""
        with pytest.raises(RuntimeError) as exc_info:
            Orchestrator(
                **mock_orchestrator_dependencies,
                phase0_validation=mock_phase0_validation_failure
            )
        
        assert "Phase 0 exit gates failed" in str(exc_info.value)
        assert "bootstrap" in str(exc_info.value)
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    @patch('farfan_pipeline.orchestration.orchestrator.logger')
    def test_orchestrator_logs_phase0_validation_success(
        self,
        mock_logger,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_success
    ):
        """Test that Orchestrator logs Phase 0 validation success."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            phase0_validation=mock_phase0_validation_success
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
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_load_configuration_includes_runtime_mode(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_prod
    ):
        """Test that _load_configuration includes runtime mode in config dict."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=mock_runtime_config_prod
        )
        orchestrator._phase_instrumentation[0] = Mock()
        
        config = orchestrator._load_configuration()
        
        assert "_runtime_mode" in config
        assert config["_runtime_mode"] == "prod"
        assert "_strict_mode" in config
        assert config["_strict_mode"] is True
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_load_configuration_without_runtime_config(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies
    ):
        """Test that _load_configuration works without runtime_config."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=None
        )
        orchestrator._phase_instrumentation[0] = Mock()
        
        config = orchestrator._load_configuration()
        
        # Should not have runtime mode keys
        assert "_runtime_mode" not in config
        assert "_strict_mode" not in config
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_load_configuration_validates_phase0_success(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_success
    ):
        """Test that _load_configuration validates Phase 0 completion (success case)."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            phase0_validation=mock_phase0_validation_success
        )
        orchestrator._phase_instrumentation[0] = Mock()
        
        # Should not raise
        config = orchestrator._load_configuration()
        assert config is not None
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_load_configuration_fails_if_phase0_failed(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_phase0_validation_failure
    ):
        """Test that _load_configuration would fail if Phase 0 failed.
        
        Note: This test shows that __init__ catches Phase 0 failures,
        preventing _load_configuration from ever being called.
        """
        # __init__ should raise RuntimeError before we even get to _load_configuration
        with pytest.raises(RuntimeError) as exc_info:
            Orchestrator(
                **mock_orchestrator_dependencies,
                phase0_validation=mock_phase0_validation_failure
            )
        
        assert "Phase 0 exit gates failed" in str(exc_info.value)


# ============================================================================
# TEST SUITE 5: Combined Integration Tests
# ============================================================================

class TestOrchestratorFullIntegration:
    """Test full integration of RuntimeConfig + Phase 0 validation."""
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_orchestrator_with_full_phase0_context(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies,
        mock_runtime_config_prod,
        mock_phase0_validation_success
    ):
        """Test Orchestrator with both RuntimeConfig and Phase 0 validation."""
        orchestrator = Orchestrator(
            **mock_orchestrator_dependencies,
            runtime_config=mock_runtime_config_prod,
            phase0_validation=mock_phase0_validation_success
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
    
    @patch('orchestration.orchestrator.validate_phase_definitions')
    @patch('orchestration.questionnaire_validation._validate_questionnaire_structure')
    def test_orchestrator_backward_compatible_no_phase0(
        self,
        mock_validate_structure,
        mock_validate_phases,
        mock_orchestrator_dependencies
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
