"""Tests for Phase 3 validation module.

Validates strict input checking, score bounds validation, quality level enum,
and evidence presence checks.
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
import pytest

# Add src to path for imports
repo_root = Path(__file__).resolve().parent.parent

from farfan_pipeline.phases.Phase_three.validation import (
    VALID_QUALITY_LEVELS,
    ValidationCounters,
    validate_micro_results_input,
    validate_and_clamp_score,
    validate_quality_level,
    validate_evidence_presence,
)


@dataclass
class MockMicroQuestionRun:
    """Mock MicroQuestionRun for testing."""
    question_id: str
    question_global: int
    base_slot: str
    metadata: dict[str, Any]
    evidence: Any
    error: str | None = None


class TestValidateMicroResultsInput:
    """Test input validation for micro-question results count."""
    
    def test_validate_correct_count(self):
        """Test validation passes with correct count."""
        micro_results = [MockMicroQuestionRun(f"Q{i:03d}", i, "SLOT", {}, {}) for i in range(1, 306)]
        
        # Should not raise
        validate_micro_results_input(micro_results, 305)
    
    def test_validate_empty_list_fails(self):
        """Test validation fails with empty list."""
        with pytest.raises(ValueError, match="micro_results list is empty"):
            validate_micro_results_input([], 305)
    
    def test_validate_wrong_count_fails(self):
        """Test validation fails with incorrect count."""
        micro_results = [MockMicroQuestionRun(f"Q{i:03d}", i, "SLOT", {}, {}) for i in range(1, 101)]
        
        with pytest.raises(ValueError, match="Expected 305 micro-question results but got 100"):
            validate_micro_results_input(micro_results, 305)
    
    def test_validate_too_many_fails(self):
        """Test validation fails with too many results."""
        micro_results = [MockMicroQuestionRun(f"Q{i:03d}", i, "SLOT", {}, {}) for i in range(1, 311)]
        
        with pytest.raises(ValueError, match="Expected 305 micro-question results but got 310"):
            validate_micro_results_input(micro_results, 305)


class TestValidateEvidencePresence:
    """Test evidence presence validation."""
    
    def test_validate_evidence_present(self):
        """Test validation passes with present evidence."""
        counters = ValidationCounters()
        result = validate_evidence_presence({"data": "test"}, "Q001", 1, counters)
        
        assert result is True
        assert counters.missing_evidence == 0
    
    def test_validate_evidence_none_fails(self):
        """Test validation fails with None evidence."""
        counters = ValidationCounters()
        result = validate_evidence_presence(None, "Q001", 1, counters)
        
        assert result is False
        assert counters.missing_evidence == 1


class TestValidateAndClampScore:
    """Test score validation and clamping."""
    
    def test_validate_score_in_range(self):
        """Test score within valid range [0.0, 1.0]."""
        counters = ValidationCounters()
        
        score = validate_and_clamp_score(0.5, "Q001", 1, counters)
        assert score == 0.5
        assert counters.out_of_bounds_scores == 0
        assert counters.score_clamping_applied == 0
    
    def test_validate_score_zero(self):
        """Test score at lower bound."""
        counters = ValidationCounters()
        
        score = validate_and_clamp_score(0.0, "Q001", 1, counters)
        assert score == 0.0
        assert counters.out_of_bounds_scores == 0
    
    def test_validate_score_one(self):
        """Test score at upper bound."""
        counters = ValidationCounters()
        
        score = validate_and_clamp_score(1.0, "Q001", 1, counters)
        assert score == 1.0
        assert counters.out_of_bounds_scores == 0
    
    def test_clamp_score_below_zero(self):
        """Test clamping negative score to 0.0."""
        counters = ValidationCounters()
        
        score = validate_and_clamp_score(-0.5, "Q001", 1, counters)
        assert score == 0.0
        assert counters.out_of_bounds_scores == 1
        assert counters.score_clamping_applied == 1
    
    def test_clamp_score_above_one(self):
        """Test clamping score above 1.0."""
        counters = ValidationCounters()
        
        score = validate_and_clamp_score(1.5, "Q001", 1, counters)
        assert score == 1.0
        assert counters.out_of_bounds_scores == 1
        assert counters.score_clamping_applied == 1
    
    def test_validate_score_none(self):
        """Test None score defaults to 0.0."""
        counters = ValidationCounters()
        
        score = validate_and_clamp_score(None, "Q001", 1, counters)
        assert score == 0.0
        assert counters.out_of_bounds_scores == 0
    
    def test_validate_score_invalid_type(self):
        """Test invalid score type defaults to 0.0."""
        counters = ValidationCounters()
        
        score = validate_and_clamp_score("invalid", "Q001", 1, counters)
        assert score == 0.0
        assert counters.out_of_bounds_scores == 1


class TestValidateQualityLevel:
    """Test quality level enum validation."""
    
    def test_validate_quality_level_excelente(self):
        """Test EXCELENTE is valid."""
        counters = ValidationCounters()
        
        quality = validate_quality_level("EXCELENTE", "Q001", 1, counters)
        assert quality == "EXCELENTE"
        assert counters.invalid_quality_levels == 0
    
    def test_validate_quality_level_aceptable(self):
        """Test ACEPTABLE is valid."""
        counters = ValidationCounters()
        
        quality = validate_quality_level("ACEPTABLE", "Q001", 1, counters)
        assert quality == "ACEPTABLE"
        assert counters.invalid_quality_levels == 0
    
    def test_validate_quality_level_insuficiente(self):
        """Test INSUFICIENTE is valid."""
        counters = ValidationCounters()
        
        quality = validate_quality_level("INSUFICIENTE", "Q001", 1, counters)
        assert quality == "INSUFICIENTE"
        assert counters.invalid_quality_levels == 0
    
    def test_validate_quality_level_no_aplicable(self):
        """Test NO_APLICABLE is valid."""
        counters = ValidationCounters()
        
        quality = validate_quality_level("NO_APLICABLE", "Q001", 1, counters)
        assert quality == "NO_APLICABLE"
        assert counters.invalid_quality_levels == 0
    
    def test_validate_quality_level_invalid(self):
        """Test invalid quality level corrects to INSUFICIENTE."""
        counters = ValidationCounters()
        
        quality = validate_quality_level("INVALID", "Q001", 1, counters)
        assert quality == "INSUFICIENTE"
        assert counters.invalid_quality_levels == 1
        assert counters.quality_level_corrections == 1
    
    def test_validate_quality_level_none(self):
        """Test None quality level corrects to INSUFICIENTE."""
        counters = ValidationCounters()
        
        quality = validate_quality_level(None, "Q001", 1, counters)
        assert quality == "INSUFICIENTE"
        assert counters.invalid_quality_levels == 1
        assert counters.quality_level_corrections == 1
    
    def test_validate_quality_level_whitespace_trimmed(self):
        """Test quality level with whitespace is trimmed."""
        counters = ValidationCounters()
        
        quality = validate_quality_level("  EXCELENTE  ", "Q001", 1, counters)
        assert quality == "EXCELENTE"
        assert counters.invalid_quality_levels == 0


class TestValidationCounters:
    """Test ValidationCounters tracking."""
    
    def test_counters_initialization(self):
        """Test counters initialize to zero."""
        counters = ValidationCounters(total_questions=305)
        
        assert counters.total_questions == 305
        assert counters.missing_evidence == 0
        assert counters.out_of_bounds_scores == 0
        assert counters.invalid_quality_levels == 0
        assert counters.score_clamping_applied == 0
        assert counters.quality_level_corrections == 0
    
    def test_counters_accumulate(self):
        """Test counters accumulate across multiple validations."""
        counters = ValidationCounters()
        
        # Simulate multiple validation failures
        validate_evidence_presence(None, "Q001", 1, counters)
        validate_evidence_presence(None, "Q002", 2, counters)
        validate_and_clamp_score(-0.5, "Q003", 3, counters)
        validate_and_clamp_score(1.5, "Q004", 4, counters)
        validate_quality_level("INVALID", "Q005", 5, counters)
        
        assert counters.missing_evidence == 2
        assert counters.out_of_bounds_scores == 2
        assert counters.score_clamping_applied == 2
        assert counters.invalid_quality_levels == 1
        assert counters.quality_level_corrections == 1


class TestValidQualityLevelsConstant:
    """Test VALID_QUALITY_LEVELS constant."""
    
    def test_valid_quality_levels_set(self):
        """Test VALID_QUALITY_LEVELS contains expected values."""
        expected = {"EXCELENTE", "ACEPTABLE", "INSUFICIENTE", "NO_APLICABLE"}
        assert VALID_QUALITY_LEVELS == expected
    
    def test_valid_quality_levels_frozen(self):
        """Test VALID_QUALITY_LEVELS is immutable."""
        assert isinstance(VALID_QUALITY_LEVELS, frozenset)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
