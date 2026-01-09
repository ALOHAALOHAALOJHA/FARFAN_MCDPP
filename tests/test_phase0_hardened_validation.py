"""
Unit Tests for Hardened Phase 0 Validation
==========================================

Tests the new Phase 0 validation gates introduced in P1 Hardening:
- Gate 5: Questionnaire Integrity (SHA256 validation)
- Gate 6: Method Registry (method count validation)
- Gate 7: Smoke Tests (sample method validation)

Test Coverage:
1. Questionnaire integrity gate with valid/invalid hashes
2. Method registry gate with expected/unexpected counts
3. Smoke tests gate with available/unavailable methods
4. Integration with orchestrator _load_configuration
5. PROD vs DEV mode behavior differences
6. Machine-readable error reporting
"""

import pytest
import os
import sys
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Phase 0 imports
from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode
from farfan_pipeline.phases.Phase_zero.phase0_50_01_exit_gates import (
    GateResult,
    check_questionnaire_integrity_gate,
    check_method_registry_gate,
    check_smoke_tests_gate,
    check_all_gates,
    get_gate_summary,
)


# ============================================================================
# MOCK RUNNERS
# ============================================================================

@dataclass
class MockPhase0Runner:
    """Mock Phase 0 runner for testing."""
    errors: list[str]
    _bootstrap_failed: bool
    runtime_config: RuntimeConfig | None
    seed_snapshot: dict[str, int]
    input_pdf_sha256: str
    questionnaire_sha256: str
    method_executor: any = None
    questionnaire: any = None


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_questionnaire_data():
    """Sample questionnaire data for hashing."""
    return {
        "blocks": {
            "micro_questions": [{"id": f"Q{i:03d}"} for i in range(1, 301)],
            "meso_questions": [{"id": f"M{i:03d}"} for i in range(1, 5)],
            "macro_question": {"id": "MACRO"}
        }
    }


@pytest.fixture
def sample_questionnaire_hash(sample_questionnaire_data):
    """Compute SHA256 of sample questionnaire."""
    json_str = json.dumps(sample_questionnaire_data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


@pytest.fixture
def mock_runtime_config_prod():
    """RuntimeConfig in PROD mode."""
    return RuntimeConfig.from_dict({
        "mode": "prod",
        "allow_contradiction_fallback": False,
        "allow_validator_disable": False,
        "allow_execution_estimates": False,
        "allow_networkx_fallback": False,
        "allow_spacy_fallback": False,
        "allow_dev_ingestion_fallbacks": False,
        "allow_aggregation_defaults": False,
    })


@pytest.fixture
def mock_runtime_config_dev():
    """RuntimeConfig in DEV mode."""
    return RuntimeConfig.from_dict({
        "mode": "dev",
        "allow_contradiction_fallback": True,
        "allow_validator_disable": True,
        "allow_execution_estimates": True,
        "allow_networkx_fallback": True,
        "allow_spacy_fallback": True,
        "allow_dev_ingestion_fallbacks": True,
        "allow_aggregation_defaults": True,
    })


@pytest.fixture
def mock_method_executor_healthy():
    """Mock MethodExecutor with healthy registry."""
    executor = Mock()
    registry = Mock()
    registry.get_stats.return_value = {
        "total_classes_registered": 416,
        "instantiated_classes": 50,
        "failed_classes": 0,
        "direct_methods_injected": 0,
        "instantiated_class_names": ["PDFChunkExtractor", "SemanticAnalyzer"],
        "failed_class_names": [],
    }
    executor._method_registry = registry
    
    # Mock instances for smoke tests
    instances = Mock()
    instances.get = Mock(side_effect=lambda name: Mock() if name in ["PDFChunkExtractor", "SemanticAnalyzer", "DimensionAggregator"] else None)
    executor.instances = instances
    
    return executor


@pytest.fixture
def mock_method_executor_degraded():
    """Mock MethodExecutor with degraded registry (some failures)."""
    executor = Mock()
    registry = Mock()
    registry.get_stats.return_value = {
        "total_classes_registered": 416,
        "instantiated_classes": 400,
        "failed_classes": 16,
        "direct_methods_injected": 0,
        "instantiated_class_names": ["PDFChunkExtractor"],
        "failed_class_names": ["BrokenClass1", "BrokenClass2", "BrokenClass3"],
    }
    executor._method_registry = registry
    
    # Mock instances with some failures
    instances = Mock()
    instances.get = Mock(side_effect=lambda name: Mock() if name == "PDFChunkExtractor" else None)
    executor.instances = instances
    
    return executor


@pytest.fixture
def mock_method_executor_insufficient():
    """Mock MethodExecutor with insufficient method count."""
    executor = Mock()
    registry = Mock()
    registry.get_stats.return_value = {
        "total_classes_registered": 200,  # Less than expected 416
        "instantiated_classes": 200,
        "failed_classes": 0,
        "direct_methods_injected": 0,
        "instantiated_class_names": ["PDFChunkExtractor"],
        "failed_class_names": [],
    }
    executor._method_registry = registry
    
    instances = Mock()
    instances.get = Mock(return_value=Mock())
    executor.instances = instances
    
    return executor


# ============================================================================
# TEST SUITE 1: Questionnaire Integrity Gate
# ============================================================================

class TestQuestionnaireIntegrityGate:
    """Test Gate 5: Questionnaire Integrity validation."""
    
    def test_questionnaire_integrity_pass_with_matching_hash(self, sample_questionnaire_hash, mock_runtime_config_prod):
        """Test gate passes when questionnaire hash matches expected."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256=sample_questionnaire_hash,
        )
        
        with patch.dict(os.environ, {"EXPECTED_QUESTIONNAIRE_SHA256": sample_questionnaire_hash}):
            result = check_questionnaire_integrity_gate(runner)
        
        assert result.passed is True
        assert result.gate_name == "questionnaire_integrity"
        assert result.gate_id == 5
        assert result.reason is None
    
    def test_questionnaire_integrity_fail_with_mismatch(self, sample_questionnaire_hash, mock_runtime_config_prod):
        """Test gate fails when questionnaire hash doesn't match."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,  # Different hash
        )
        
        with patch.dict(os.environ, {"EXPECTED_QUESTIONNAIRE_SHA256": sample_questionnaire_hash}):
            result = check_questionnaire_integrity_gate(runner)
        
        assert result.passed is False
        assert result.gate_name == "questionnaire_integrity"
        assert "hash mismatch" in result.reason.lower()
    
    def test_questionnaire_integrity_pass_without_expected_hash(self, sample_questionnaire_hash):
        """Test gate passes with warning when no expected hash configured (legacy mode)."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=None,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256=sample_questionnaire_hash,
        )
        
        with patch.dict(os.environ, {}, clear=True):
            result = check_questionnaire_integrity_gate(runner)
        
        assert result.passed is True
        assert result.reason is not None
        assert "legacy mode" in result.reason.lower()
    
    def test_questionnaire_integrity_fail_with_invalid_hash_format(self, mock_runtime_config_prod):
        """Test gate fails when expected hash has invalid format."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
        )
        
        with patch.dict(os.environ, {"EXPECTED_QUESTIONNAIRE_SHA256": "invalid_hash"}):
            result = check_questionnaire_integrity_gate(runner)
        
        assert result.passed is False
        assert "invalid expected hash format" in result.reason.lower()
    
    def test_questionnaire_integrity_fail_without_computed_hash(self, sample_questionnaire_hash, mock_runtime_config_prod):
        """Test gate fails when questionnaire hash not computed."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="",  # Empty hash
        )
        
        with patch.dict(os.environ, {"EXPECTED_QUESTIONNAIRE_SHA256": sample_questionnaire_hash}):
            result = check_questionnaire_integrity_gate(runner)
        
        assert result.passed is False
        assert "not computed" in result.reason.lower()


# ============================================================================
# TEST SUITE 2: Method Registry Gate
# ============================================================================

class TestMethodRegistryGate:
    """Test Gate 6: Method Registry validation."""
    
    def test_method_registry_pass_with_expected_count(self, mock_runtime_config_prod, mock_method_executor_healthy):
        """Test gate passes when method count matches expected."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=mock_method_executor_healthy,
        )
        
        with patch.dict(os.environ, {"EXPECTED_METHOD_COUNT": "416"}):
            result = check_method_registry_gate(runner)
        
        assert result.passed is True
        assert result.gate_name == "method_registry"
        assert result.gate_id == 6
    
    def test_method_registry_fail_with_insufficient_count(self, mock_runtime_config_prod, mock_method_executor_insufficient):
        """Test gate fails when method count less than expected."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=mock_method_executor_insufficient,
        )
        
        with patch.dict(os.environ, {"EXPECTED_METHOD_COUNT": "416"}):
            result = check_method_registry_gate(runner)
        
        assert result.passed is False
        assert "method count mismatch" in result.reason.lower()
        assert "expected 416" in result.reason.lower()
        assert "registered 200" in result.reason.lower()
    
    def test_method_registry_fail_in_prod_with_failures(self, mock_runtime_config_prod, mock_method_executor_degraded):
        """Test gate fails in PROD mode when methods failed to load."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=mock_method_executor_degraded,
        )
        
        with patch.dict(os.environ, {"EXPECTED_METHOD_COUNT": "416"}):
            result = check_method_registry_gate(runner)
        
        assert result.passed is False
        assert "prod mode" in result.reason.lower()
        assert "failed classes" in result.reason.lower()
    
    def test_method_registry_pass_in_dev_with_failures(self, mock_runtime_config_dev, mock_method_executor_degraded):
        """Test gate passes in DEV mode with warning when methods failed."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_dev,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=mock_method_executor_degraded,
        )
        
        with patch.dict(os.environ, {"EXPECTED_METHOD_COUNT": "416"}):
            result = check_method_registry_gate(runner)
        
        assert result.passed is True
        assert result.reason is not None
        assert "dev mode" in result.reason.lower()
    
    def test_method_registry_fail_without_executor(self, mock_runtime_config_prod):
        """Test gate fails when MethodExecutor not available."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=None,
        )
        
        result = check_method_registry_gate(runner)
        
        assert result.passed is False
        assert "not initialized" in result.reason.lower()
    
    def test_method_registry_fail_without_registry(self, mock_runtime_config_prod):
        """Test gate fails when MethodRegistry not accessible."""
        executor = Mock()
        executor._method_registry = None
        executor.method_registry = None
        
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=executor,
        )
        
        result = check_method_registry_gate(runner)
        
        assert result.passed is False
        assert "not accessible" in result.reason.lower()


# ============================================================================
# TEST SUITE 3: Smoke Tests Gate
# ============================================================================

class TestSmokeTestsGate:
    """Test Gate 7: Smoke Tests validation."""
    
    def test_smoke_tests_pass_with_all_methods_available(self, mock_runtime_config_prod, mock_method_executor_healthy):
        """Test gate passes when all smoke test methods available."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=mock_method_executor_healthy,
        )
        
        result = check_smoke_tests_gate(runner)
        
        assert result.passed is True
        assert result.gate_name == "smoke_tests"
        assert result.gate_id == 7
    
    def test_smoke_tests_fail_in_prod_with_missing_methods(self, mock_runtime_config_prod, mock_method_executor_degraded):
        """Test gate fails in PROD mode when smoke test methods missing."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=mock_method_executor_degraded,
        )
        
        result = check_smoke_tests_gate(runner)
        
        assert result.passed is False
        assert "smoke tests failed" in result.reason.lower()
    
    def test_smoke_tests_pass_in_dev_with_missing_methods(self, mock_runtime_config_dev, mock_method_executor_degraded):
        """Test gate passes in DEV mode with warning when smoke tests fail."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_dev,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=mock_method_executor_degraded,
        )
        
        result = check_smoke_tests_gate(runner)
        
        assert result.passed is True
        assert result.reason is not None
        assert "dev mode" in result.reason.lower()
    
    def test_smoke_tests_fail_without_executor(self, mock_runtime_config_prod):
        """Test gate fails when MethodExecutor not available."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            method_executor=None,
        )
        
        result = check_smoke_tests_gate(runner)
        
        assert result.passed is False
        assert "not available" in result.reason.lower()


# ============================================================================
# TEST SUITE 4: All Gates Integration
# ============================================================================

class TestAllGatesIntegration:
    """Test check_all_gates with new validation gates."""
    
    def test_all_gates_pass_with_full_validation(
        self,
        sample_questionnaire_hash,
        mock_runtime_config_prod,
        mock_method_executor_healthy
    ):
        """Test all 7 gates pass with complete validation."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256=sample_questionnaire_hash,
            method_executor=mock_method_executor_healthy,
        )
        
        with patch.dict(os.environ, {
            "EXPECTED_QUESTIONNAIRE_SHA256": sample_questionnaire_hash,
            "EXPECTED_METHOD_COUNT": "416"
        }):
            all_passed, results = check_all_gates(runner)
        
        assert all_passed is True
        assert len(results) == 7
        assert all(r.passed for r in results)
    
    def test_all_gates_fail_fast_on_questionnaire_integrity(
        self,
        sample_questionnaire_hash,
        mock_runtime_config_prod,
        mock_method_executor_healthy
    ):
        """Test gates fail fast when questionnaire integrity fails."""
        # Use a valid hash format but wrong value
        wrong_hash = "f" * 64  # Valid format but different hash
        
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256=wrong_hash,  # Valid format but wrong value
            method_executor=mock_method_executor_healthy,
        )
        
        with patch.dict(os.environ, {
            "EXPECTED_QUESTIONNAIRE_SHA256": sample_questionnaire_hash,
            "EXPECTED_METHOD_COUNT": "416"
        }):
            all_passed, results = check_all_gates(runner)
        
        assert all_passed is False
        # Should stop after gate 5 fails (gates 1-4 pass, gate 5 fails)
        assert len(results) == 5
        assert results[4].passed is False
        assert results[4].gate_name == "questionnaire_integrity"
    
    def test_gate_summary_with_all_gates(
        self,
        sample_questionnaire_hash,
        mock_runtime_config_prod,
        mock_method_executor_healthy
    ):
        """Test get_gate_summary includes all 7 gates."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256=sample_questionnaire_hash,
            method_executor=mock_method_executor_healthy,
        )
        
        with patch.dict(os.environ, {
            "EXPECTED_QUESTIONNAIRE_SHA256": sample_questionnaire_hash,
            "EXPECTED_METHOD_COUNT": "416"
        }):
            _, results = check_all_gates(runner)
        
        summary = get_gate_summary(results)
        
        assert "7/7 passed" in summary
        assert "questionnaire_integrity" in summary
        assert "method_registry" in summary
        assert "smoke_tests" in summary


# ============================================================================
# TEST SUITE 5: Machine-Readable Error Reporting
# ============================================================================

class TestMachineReadableErrors:
    """Test machine-readable error reporting for CI."""
    
    def test_gate_result_to_dict(self, sample_questionnaire_hash, mock_runtime_config_prod):
        """Test GateResult.to_dict() produces machine-readable output."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="wrong_hash_" + ("0" * 54),
        )
        
        with patch.dict(os.environ, {"EXPECTED_QUESTIONNAIRE_SHA256": sample_questionnaire_hash}):
            result = check_questionnaire_integrity_gate(runner)
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "passed" in result_dict
        assert "gate_name" in result_dict
        assert "gate_id" in result_dict
        assert "reason" in result_dict
        assert result_dict["passed"] is False
        assert result_dict["gate_name"] == "questionnaire_integrity"
    
    def test_all_gates_results_serializable(
        self,
        sample_questionnaire_hash,
        mock_runtime_config_prod,
        mock_method_executor_insufficient
    ):
        """Test all gate results can be serialized to JSON for CI."""
        runner = MockPhase0Runner(
            errors=[],
            _bootstrap_failed=False,
            runtime_config=mock_runtime_config_prod,
            seed_snapshot={"python": 42, "numpy": 42},
            input_pdf_sha256="a" * 64,
            questionnaire_sha256=sample_questionnaire_hash,
            method_executor=mock_method_executor_insufficient,
        )
        
        with patch.dict(os.environ, {
            "EXPECTED_QUESTIONNAIRE_SHA256": sample_questionnaire_hash,
            "EXPECTED_METHOD_COUNT": "416"
        }):
            _, results = check_all_gates(runner)
        
        # Convert to list of dicts
        results_dicts = [r.to_dict() for r in results]
        
        # Should be JSON-serializable
        import json
        json_output = json.dumps(results_dicts, indent=2)
        
        assert json_output
        assert isinstance(json_output, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
