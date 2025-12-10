"""
Unit Tests for Phase 0 Components
==================================

Tests Phase 0 exit gates, determinism, and orchestration according to
P00-EN v2.0 specification.

Test Categories:
    1. Exit Gate Tests - Individual gate validation
    2. Determinism Tests - Seed generation and application
    3. Integration Tests - Full Phase 0 orchestration
    4. Error Path Tests - Failure scenarios

Author: Phase 0 Compliance Team
Version: 1.0.0
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from canonic_phases.Phase_zero.determinism import (
    ALL_SEEDS,
    MANDATORY_SEEDS,
    OPTIONAL_SEEDS,
    apply_seeds_to_rngs,
    derive_seed_from_parts,
    derive_seed_from_string,
    validate_seed_application,
)
from canonic_phases.Phase_zero.exit_gates import (
    check_all_gates,
    check_bootstrap_gate,
    check_determinism_gate,
    check_input_verification_gate,
)
from canonic_phases.Phase_zero.runtime_config import RuntimeConfig


# ============================================================================
# Exit Gate Tests
# ============================================================================

class MockRunner:
    """Mock Phase 0 runner for testing."""
    
    def __init__(self):
        self.errors = []
        self._bootstrap_failed = False
        self.runtime_config = None
        self.seed_snapshot = {}
        self.input_pdf_sha256 = ""
        self.questionnaire_sha256 = ""


def test_bootstrap_gate_passes_with_valid_config():
    """Gate 1 should pass when bootstrap succeeds."""
    runner = MockRunner()
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    
    result = check_bootstrap_gate(runner)
    
    assert result.passed
    assert result.gate_id == 1
    assert result.gate_name == "bootstrap"
    assert result.reason is None


def test_bootstrap_gate_fails_on_bootstrap_failure():
    """Gate 1 should fail if _bootstrap_failed is True."""
    runner = MockRunner()
    runner._bootstrap_failed = True
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    
    result = check_bootstrap_gate(runner)
    
    assert not result.passed
    assert result.gate_id == 1
    assert "Bootstrap failed" in result.reason


def test_bootstrap_gate_fails_on_missing_config():
    """Gate 1 should fail if runtime_config is None."""
    runner = MockRunner()
    runner.runtime_config = None
    
    result = check_bootstrap_gate(runner)
    
    assert not result.passed
    assert "Runtime config not loaded" in result.reason


def test_bootstrap_gate_fails_with_errors():
    """Gate 1 should fail if errors present."""
    runner = MockRunner()
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    runner.errors = ["Some error"]
    
    result = check_bootstrap_gate(runner)
    
    assert not result.passed
    assert "Some error" in result.reason


def test_input_verification_gate_passes_with_hashes():
    """Gate 2 should pass when both files are hashed."""
    runner = MockRunner()
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    runner.input_pdf_sha256 = "abc123" * 10 + "abcd"  # 64 chars
    runner.questionnaire_sha256 = "def456" * 10 + "efgh"
    
    result = check_input_verification_gate(runner)
    
    assert result.passed
    assert result.gate_id == 2
    assert result.gate_name == "input_verification"


def test_input_verification_gate_fails_on_missing_pdf_hash():
    """Gate 2 should fail if PDF not hashed."""
    runner = MockRunner()
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    runner.questionnaire_sha256 = "def456" * 10 + "efgh"
    # input_pdf_sha256 is empty string
    
    result = check_input_verification_gate(runner)
    
    assert not result.passed
    assert "Input PDF not hashed" in result.reason


def test_determinism_gate_passes_with_mandatory_seeds():
    """Gate 4 should pass when python and numpy seeds present."""
    runner = MockRunner()
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    runner.input_pdf_sha256 = "abc123" * 10 + "abcd"
    runner.questionnaire_sha256 = "def456" * 10 + "efgh"
    runner.seed_snapshot = {
        "python": 12345,
        "numpy": 67890,
    }
    
    result = check_determinism_gate(runner)
    
    assert result.passed
    assert result.gate_id == 4


def test_determinism_gate_fails_on_missing_python_seed():
    """Gate 4 should fail if python seed missing."""
    runner = MockRunner()
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    runner.input_pdf_sha256 = "abc123" * 10 + "abcd"
    runner.questionnaire_sha256 = "def456" * 10 + "efgh"
    runner.seed_snapshot = {
        "numpy": 67890,
        # Missing python seed
    }
    
    result = check_determinism_gate(runner)
    
    assert not result.passed
    assert "Missing mandatory seeds" in result.reason
    assert "python" in result.reason


def test_check_all_gates_success():
    """check_all_gates should return True when all gates pass."""
    runner = MockRunner()
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    runner.input_pdf_sha256 = "abc123" * 10 + "abcd"
    runner.questionnaire_sha256 = "def456" * 10 + "efgh"
    runner.seed_snapshot = {"python": 12345, "numpy": 67890}
    
    all_passed, results = check_all_gates(runner)
    
    assert all_passed
    assert len(results) == 4
    assert all(r.passed for r in results)


def test_check_all_gates_fails_fast():
    """check_all_gates should stop at first failure."""
    runner = MockRunner()
    runner.runtime_config = MagicMock(spec=RuntimeConfig)
    runner._bootstrap_failed = True  # Gate 1 will fail
    
    all_passed, results = check_all_gates(runner)
    
    assert not all_passed
    assert len(results) == 1  # Only checked gate 1
    assert not results[0].passed


# ============================================================================
# Determinism Tests
# ============================================================================

def test_derive_seed_from_string_deterministic():
    """Seed derivation should be deterministic for same input."""
    seed1 = derive_seed_from_string("test_input")
    seed2 = derive_seed_from_string("test_input")
    
    assert seed1 == seed2
    assert isinstance(seed1, int)
    assert 0 <= seed1 < 2**32


def test_derive_seed_from_string_unique():
    """Different inputs should produce different seeds."""
    seed1 = derive_seed_from_string("input_a")
    seed2 = derive_seed_from_string("input_b")
    
    assert seed1 != seed2


def test_derive_seed_from_parts_deterministic():
    """Seed derivation from parts should be deterministic."""
    seed1 = derive_seed_from_parts("PU_123", "corr-1", "python")
    seed2 = derive_seed_from_parts("PU_123", "corr-1", "python")
    
    assert seed1 == seed2


def test_apply_seeds_to_rngs_success():
    """Applying seeds should succeed with mandatory seeds."""
    seeds = {
        "python": 12345,
        "numpy": 67890,
        "quantum": 11111,
    }
    
    status = apply_seeds_to_rngs(seeds)
    
    assert status["python"] is True


def test_apply_seeds_to_rngs_fails_without_python():
    """Applying seeds should fail if python seed missing."""
    seeds = {
        "numpy": 67890,
    }
    
    with pytest.raises(ValueError, match="Missing mandatory seeds"):
        apply_seeds_to_rngs(seeds)


def test_validate_seed_application_success():
    """Validation should pass when mandatory seeds applied."""
    seeds = {"python": 12345, "numpy": 67890}
    status = {"python": True, "numpy": True}
    
    success, errors = validate_seed_application(seeds, status)
    
    assert success
    assert len(errors) == 0


def test_mandatory_seeds_constant():
    """MANDATORY_SEEDS should contain python and numpy."""
    assert "python" in MANDATORY_SEEDS
    assert "numpy" in MANDATORY_SEEDS


def test_all_seeds_complete():
    """ALL_SEEDS should be union of mandatory and optional."""
    expected = set(MANDATORY_SEEDS) | set(OPTIONAL_SEEDS)
    assert set(ALL_SEEDS) == expected
