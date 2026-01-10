"""Regression tests for Phase 3 scoring pipeline.

Ensures Phase 3 catches score corruption and prevents silent failures.
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
import pytest

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))


@dataclass
class MockEvidence:
    """Mock Evidence object."""
    modality: str = "text"
    elements: list[Any] = field(default_factory=list)
    raw_results: dict[str, Any] = field(default_factory=dict)
    validation: dict[str, Any] = field(default_factory=dict)
    confidence_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class MockMicroQuestionRun:
    """Mock MicroQuestionRun."""
    question_id: str
    question_global: int
    base_slot: str
    metadata: dict[str, Any]
    evidence: Any
    error: str | None = None


class TestPhase3RegressionScoreCorruption:
    """Regression tests for score corruption detection."""
    
    def test_detects_score_corruption_infinity(self):
        """Test Phase 3 detects infinity scores."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        # Infinity should be clamped to 1.0
        score = validate_and_clamp_score(float('inf'), "Q001", 1, counters)
        assert score == 1.0
        assert counters.out_of_bounds_scores == 1
        assert counters.score_clamping_applied == 1
    
    def test_detects_score_corruption_negative_infinity(self):
        """Test Phase 3 detects negative infinity scores."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        # Negative infinity should be clamped to 0.0
        score = validate_and_clamp_score(float('-inf'), "Q001", 1, counters)
        assert score == 0.0
        assert counters.out_of_bounds_scores == 1
        assert counters.score_clamping_applied == 1
    
    def test_detects_score_corruption_large_values(self):
        """Test Phase 3 detects very large scores."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        large_values = [10.0, 100.0, 1000.0, 1e6, 1e9]
        
        for val in large_values:
            score = validate_and_clamp_score(val, "Q001", 1, counters)
            assert score == 1.0
        
        assert counters.out_of_bounds_scores == len(large_values)
        assert counters.score_clamping_applied == len(large_values)
    
    def test_detects_score_corruption_large_negative(self):
        """Test Phase 3 detects very large negative scores."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        large_negative = [-10.0, -100.0, -1000.0, -1e6, -1e9]
        
        for val in large_negative:
            score = validate_and_clamp_score(val, "Q001", 1, counters)
            assert score == 0.0
        
        assert counters.out_of_bounds_scores == len(large_negative)
        assert counters.score_clamping_applied == len(large_negative)


class TestPhase3RegressionQualityCorruption:
    """Regression tests for quality level corruption detection."""
    
    def test_detects_quality_corruption_mixed_case(self):
        """Test Phase 3 handles mixed-case quality levels."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_quality_level,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        # Mixed case should fail and correct to INSUFICIENTE
        mixed_cases = ["excelente", "Excelente", "aceptable", "Aceptable"]
        
        for level in mixed_cases:
            result = validate_quality_level(level, "Q001", 1, counters)
            assert result == "INSUFICIENTE"
        
        assert counters.invalid_quality_levels == len(mixed_cases)
    
    def test_detects_quality_corruption_typos(self):
        """Test Phase 3 detects quality level typos."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_quality_level,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        typos = ["EXELENTE", "ACEPTBLE", "INSUFFICIENTE", "NO_APLICBLE"]
        
        for level in typos:
            result = validate_quality_level(level, "Q001", 1, counters)
            assert result == "INSUFICIENTE"
        
        assert counters.invalid_quality_levels == len(typos)
    
    def test_detects_quality_corruption_empty_string(self):
        """Test Phase 3 handles empty string quality level."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_quality_level,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        result = validate_quality_level("", "Q001", 1, counters)
        
        assert result == "INSUFICIENTE"
        assert counters.invalid_quality_levels == 1


class TestPhase3RegressionSilentFailures:
    """Regression tests for silent failure detection."""
    
    def test_prevents_silent_missing_evidence(self):
        """Test Phase 3 doesn't silently accept missing evidence."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_evidence_presence,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        # None evidence should fail validation
        result = validate_evidence_presence(None, "Q001", 1, counters)
        
        assert result is False
        assert counters.missing_evidence == 1
    
    def test_prevents_silent_score_overflow(self):
        """Test Phase 3 doesn't silently accept score overflow."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        # Overflow should be logged and clamped
        score = validate_and_clamp_score(999.9, "Q001", 1, counters)
        
        assert score == 1.0
        assert counters.out_of_bounds_scores == 1
        assert counters.score_clamping_applied == 1
    
    def test_prevents_silent_quality_mutation(self):
        """Test Phase 3 doesn't silently accept quality mutations."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_quality_level,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        # Invalid quality should be logged and corrected
        result = validate_quality_level("CORRUPTED", "Q001", 1, counters)
        
        assert result == "INSUFICIENTE"
        assert counters.invalid_quality_levels == 1
        assert counters.quality_level_corrections == 1


class TestPhase3RegressionInputValidation:
    """Regression tests for input validation."""
    
    def test_rejects_partial_results(self):
        """Test Phase 3 rejects partial results (< 305 questions)."""
        from farfan_pipeline.phases.Phase_three.validation import validate_micro_results_input
        
        # Create only 200 questions
        micro_results = [
            MockMicroQuestionRun(
                question_id=f"Q{i:03d}",
                question_global=i,
                base_slot="SLOT",
                metadata={"overall_confidence": 0.8},
                evidence=MockEvidence(),
            )
            for i in range(1, 201)
        ]
        
        with pytest.raises(ValueError, match="Expected 305 micro-question results but got 200"):
            validate_micro_results_input(micro_results, 305)
    
    def test_rejects_duplicate_results(self):
        """Test Phase 3 rejects too many results (> 305 questions)."""
        from farfan_pipeline.phases.Phase_three.validation import validate_micro_results_input
        
        # Create 400 questions
        micro_results = [
            MockMicroQuestionRun(
                question_id=f"Q{i:03d}",
                question_global=i,
                base_slot="SLOT",
                metadata={"overall_confidence": 0.8},
                evidence=MockEvidence(),
            )
            for i in range(1, 401)
        ]
        
        with pytest.raises(ValueError, match="Expected 305 micro-question results but got 400"):
            validate_micro_results_input(micro_results, 305)


class TestPhase3RegressionDataTypes:
    """Regression tests for data type validation."""
    
    def test_handles_string_scores(self):
        """Test Phase 3 handles string scores gracefully."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        string_scores = ["0.5", "not_a_number", "", "abc"]
        
        for score_str in string_scores:
            score = validate_and_clamp_score(score_str, "Q001", 1, counters)
            # Only "0.5" should convert successfully
            if score_str == "0.5":
                assert score == 0.5
            else:
                assert score == 0.0
        
        # 3 out of 4 should fail conversion
        assert counters.out_of_bounds_scores == 3
    
    def test_handles_dict_scores(self):
        """Test Phase 3 handles dict scores gracefully."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        score = validate_and_clamp_score({"score": 0.8}, "Q001", 1, counters)
        
        assert score == 0.0
        assert counters.out_of_bounds_scores == 1
    
    def test_handles_list_scores(self):
        """Test Phase 3 handles list scores gracefully."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        score = validate_and_clamp_score([0.8], "Q001", 1, counters)
        
        assert score == 0.0
        assert counters.out_of_bounds_scores == 1


class TestPhase3RegressionLogging:
    """Regression tests for validation logging."""
    
    def test_logs_all_validation_counters(self):
        """Test Phase 3 logs all validation counter types."""
        from farfan_pipeline.phases.Phase_three.validation import ValidationCounters
        
        counters = ValidationCounters(
            total_questions=305,
            missing_evidence=5,
            out_of_bounds_scores=10,
            invalid_quality_levels=3,
            score_clamping_applied=8,
            quality_level_corrections=3,
        )
        
        # Should not raise
        counters.log_summary()
        
        # Verify all fields are set
        assert counters.total_questions == 305
        assert counters.missing_evidence == 5
        assert counters.out_of_bounds_scores == 10
        assert counters.invalid_quality_levels == 3
        assert counters.score_clamping_applied == 8
        assert counters.quality_level_corrections == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
