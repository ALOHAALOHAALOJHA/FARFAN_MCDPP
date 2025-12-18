"""Tests for Phase0Result validation."""

import pytest
from pathlib import Path
import tempfile


def test_phase0_result_construction():
    """Test that Phase0Result can be constructed with valid data."""
    from canonic_phases.phase_0_input_validation.phase0_results import Phase0Result
    
    with tempfile.TemporaryDirectory() as tmpdir:
        result = Phase0Result(
            runtime_config=object(),
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            seed_snapshot={"random": 42, "numpy": 42},
            boot_check_results={"spacy": True, "calibration": True},
            gate_results=[
                {"passed": True, "gate_id": i, "gate_name": f"gate_{i}"}
                for i in range(1, 8)
            ],
            artifacts_dir=Path(tmpdir),
            execution_id="test-execution-123",
            claims=[{"claim": "test", "evidence": "validation"}],
        )
        
        assert result.input_pdf_sha256 == "a" * 64
        assert result.questionnaire_sha256 == "b" * 64
        assert len(result.gate_results) == 7


def test_phase0_result_rejects_invalid_pdf_hash():
    """Test that Phase0Result rejects invalid PDF hash."""
    from canonic_phases.phase_0_input_validation.phase0_results import Phase0Result
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="Invalid PDF SHA-256 length"):
            Phase0Result(
                runtime_config=object(),
                input_pdf_sha256="a" * 32,  # Too short
                questionnaire_sha256="b" * 64,
                seed_snapshot={"random": 42},
                boot_check_results={},
                gate_results=[
                    {"passed": True, "gate_id": i}
                    for i in range(1, 8)
                ],
                artifacts_dir=Path(tmpdir),
                execution_id="test",
                claims=[],
            )


def test_phase0_result_rejects_failed_gates():
    """Test that Phase0Result rejects failed gates."""
    from canonic_phases.phase_0_input_validation.phase0_results import Phase0Result
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="Phase 0 exit gates failed"):
            Phase0Result(
                runtime_config=object(),
                input_pdf_sha256="a" * 64,
                questionnaire_sha256="b" * 64,
                seed_snapshot={"random": 42},
                boot_check_results={},
                gate_results=[
                    {"passed": False, "gate_id": 1, "gate_name": "bootstrap"}
                ] + [
                    {"passed": True, "gate_id": i}
                    for i in range(2, 8)
                ],
                artifacts_dir=Path(tmpdir),
                execution_id="test",
                claims=[],
            )


def test_phase0_result_rejects_missing_artifacts_dir():
    """Test that Phase0Result rejects non-existent artifacts directory."""
    from canonic_phases.phase_0_input_validation.phase0_results import Phase0Result
    
    with pytest.raises(ValueError, match="Artifacts directory does not exist"):
        Phase0Result(
            runtime_config=object(),
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            seed_snapshot={"random": 42},
            boot_check_results={},
            gate_results=[
                {"passed": True, "gate_id": i}
                for i in range(1, 8)
            ],
            artifacts_dir=Path("/nonexistent/path"),
            execution_id="test",
            claims=[],
        )


def test_phase0_result_is_immutable():
    """Test that Phase0Result is immutable (frozen dataclass)."""
    from canonic_phases.phase_0_input_validation.phase0_results import Phase0Result
    
    with tempfile.TemporaryDirectory() as tmpdir:
        result = Phase0Result(
            runtime_config=object(),
            input_pdf_sha256="a" * 64,
            questionnaire_sha256="b" * 64,
            seed_snapshot={"random": 42},
            boot_check_results={},
            gate_results=[
                {"passed": True, "gate_id": i}
                for i in range(1, 8)
            ],
            artifacts_dir=Path(tmpdir),
            execution_id="test",
            claims=[],
        )
        
        # Attempt to modify should fail
        with pytest.raises(Exception):  # FrozenInstanceError
            result.execution_id = "modified"
