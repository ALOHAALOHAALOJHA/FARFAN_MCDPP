"""Integration tests for Phase 3 scoring pipeline.

Tests the complete Phase 3 flow with validation, including:
- Input validation failures
- Evidence presence checks
- Score bounds enforcement
- Quality level validation
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
import pytest

# Add src to path for imports


@dataclass
class MockEvidence:
    """Mock Evidence object for testing."""
    modality: str = "text"
    elements: list[Any] = field(default_factory=list)
    raw_results: dict[str, Any] = field(default_factory=dict)
    validation: dict[str, Any] = field(default_factory=dict)
    confidence_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class MockMicroQuestionRun:
    """Mock MicroQuestionRun for integration testing."""
    question_id: str
    question_global: int
    base_slot: str
    metadata: dict[str, Any]
    evidence: Any
    error: str | None = None


class TestPhase3InputValidation:
    """Test Phase 3 input validation requirements."""
    
    def test_rejects_wrong_question_count(self):
        """Test Phase 3 rejects input with wrong question count."""
        from farfan_pipeline.phases.Phase_three.validation import validate_micro_results_input
        
        # Create 100 questions instead of 305
        micro_results = [
            MockMicroQuestionRun(
                question_id=f"Q{i:03d}",
                question_global=i,
                base_slot="SLOT",
                metadata={"overall_confidence": 0.8},
                evidence=MockEvidence(),
            )
            for i in range(1, 101)
        ]
        
        with pytest.raises(ValueError, match="Expected 305 micro-question results but got 100"):
            validate_micro_results_input(micro_results, 305)
    
    def test_rejects_empty_input(self):
        """Test Phase 3 rejects empty micro_results list."""
        from farfan_pipeline.phases.Phase_three.validation import validate_micro_results_input
        
        with pytest.raises(ValueError, match="micro_results list is empty"):
            validate_micro_results_input([], 305)
    
    def test_accepts_correct_count(self):
        """Test Phase 3 accepts correct question count."""
        from farfan_pipeline.phases.Phase_three.validation import validate_micro_results_input
        
        micro_results = [
            MockMicroQuestionRun(
                question_id=f"Q{i:03d}",
                question_global=i,
                base_slot="SLOT",
                metadata={"overall_confidence": 0.8},
                evidence=MockEvidence(),
            )
            for i in range(1, 306)
        ]
        
        # Should not raise
        validate_micro_results_input(micro_results, 305)


class TestPhase3ScoreBoundsValidation:
    """Test Phase 3 score bounds validation and clamping."""
    
    def test_clamps_negative_scores(self):
        """Test Phase 3 clamps negative scores to 0.0."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        score = validate_and_clamp_score(-0.5, "Q001", 1, counters)
        
        assert score == 0.0
        assert counters.out_of_bounds_scores == 1
        assert counters.score_clamping_applied == 1
    
    def test_clamps_scores_above_one(self):
        """Test Phase 3 clamps scores above 1.0."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        score = validate_and_clamp_score(2.5, "Q001", 1, counters)
        
        assert score == 1.0
        assert counters.out_of_bounds_scores == 1
        assert counters.score_clamping_applied == 1
    
    def test_accepts_valid_scores(self):
        """Test Phase 3 accepts scores in [0.0, 1.0] range."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        for test_score in [0.0, 0.25, 0.5, 0.75, 1.0]:
            score = validate_and_clamp_score(test_score, "Q001", 1, counters)
            assert score == test_score
        
        assert counters.out_of_bounds_scores == 0
        assert counters.score_clamping_applied == 0
    
    def test_handles_unconvertible_scores(self):
        """Test Phase 3 handles unconvertible score types."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_and_clamp_score,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        # Test unconvertible types
        score = validate_and_clamp_score("not_a_number", "Q001", 1, counters)
        assert score == 0.0
        assert counters.out_of_bounds_scores == 1
        
        score = validate_and_clamp_score({"invalid": "dict"}, "Q002", 2, counters)
        assert score == 0.0
        assert counters.out_of_bounds_scores == 2


class TestPhase3QualityLevelValidation:
    """Test Phase 3 quality level enum validation."""
    
    def test_accepts_valid_quality_levels(self):
        """Test Phase 3 accepts all valid quality levels."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_quality_level,
            ValidationCounters,
        )
        
        valid_levels = ["EXCELENTE", "ACEPTABLE", "INSUFICIENTE", "NO_APLICABLE"]
        counters = ValidationCounters()
        
        for level in valid_levels:
            result = validate_quality_level(level, "Q001", 1, counters)
            assert result == level
        
        assert counters.invalid_quality_levels == 0
    
    def test_corrects_invalid_quality_levels(self):
        """Test Phase 3 corrects invalid quality levels to INSUFICIENTE."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_quality_level,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        invalid_levels = ["INVALID", "ERROR", "UNKNOWN", ""]
        
        for level in invalid_levels:
            result = validate_quality_level(level, "Q001", 1, counters)
            assert result == "INSUFICIENTE"
        
        assert counters.invalid_quality_levels == len(invalid_levels)
        assert counters.quality_level_corrections == len(invalid_levels)
    
    def test_handles_none_quality_level(self):
        """Test Phase 3 handles None quality level."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_quality_level,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        result = validate_quality_level(None, "Q001", 1, counters)
        
        assert result == "INSUFICIENTE"
        assert counters.invalid_quality_levels == 1


class TestPhase3EvidenceValidation:
    """Test Phase 3 evidence presence validation."""
    
    def test_detects_missing_evidence(self):
        """Test Phase 3 detects and counts missing evidence."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_evidence_presence,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        result = validate_evidence_presence(None, "Q001", 1, counters)
        
        assert result is False
        assert counters.missing_evidence == 1
    
    def test_accepts_present_evidence(self):
        """Test Phase 3 accepts present evidence."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_evidence_presence,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        evidence = MockEvidence()
        
        result = validate_evidence_presence(evidence, "Q001", 1, counters)
        
        assert result is True
        assert counters.missing_evidence == 0
    
    def test_counts_multiple_missing_evidence(self):
        """Test Phase 3 counts multiple missing evidence."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_evidence_presence,
            ValidationCounters,
        )
        
        counters = ValidationCounters()
        
        # Simulate multiple missing evidence
        for i in range(1, 6):
            validate_evidence_presence(None, f"Q{i:03d}", i, counters)
        
        assert counters.missing_evidence == 5


class TestPhase3ValidationCounters:
    """Test Phase 3 validation counters and reporting."""
    
    def test_counters_track_all_failures(self):
        """Test counters track all validation failure types."""
        from farfan_pipeline.phases.Phase_three.validation import (
            ValidationCounters,
            validate_evidence_presence,
            validate_and_clamp_score,
            validate_quality_level,
        )
        
        counters = ValidationCounters(total_questions=305)
        
        # Simulate various validation failures
        validate_evidence_presence(None, "Q001", 1, counters)  # Missing evidence
        validate_evidence_presence(None, "Q002", 2, counters)  # Missing evidence
        
        validate_and_clamp_score(-0.5, "Q003", 3, counters)  # Out of bounds
        validate_and_clamp_score(1.5, "Q004", 4, counters)   # Out of bounds
        validate_and_clamp_score("bad", "Q005", 5, counters)  # Unconvertible
        
        validate_quality_level("INVALID", "Q006", 6, counters)  # Invalid
        validate_quality_level(None, "Q007", 7, counters)       # None
        
        assert counters.total_questions == 305
        assert counters.missing_evidence == 2
        assert counters.out_of_bounds_scores == 3
        assert counters.score_clamping_applied == 2
        assert counters.invalid_quality_levels == 2
        assert counters.quality_level_corrections == 2


class TestPhase3EndToEnd:
    """End-to-end integration tests for Phase 3."""
    
    def test_full_validation_pipeline(self):
        """Test complete Phase 3 validation pipeline."""
        from farfan_pipeline.phases.Phase_three.validation import (
            validate_micro_results_input,
            validate_evidence_presence,
            validate_and_clamp_score,
            validate_quality_level,
            ValidationCounters,
        )
        
        # Create test data with various validation issues
        micro_results = []
        for i in range(1, 306):
            if i <= 300:
                evidence = MockEvidence()
            else:
                evidence = None  # Missing evidence for last 5
            
            if i <= 250:
                score = 0.8
            elif i <= 275:
                score = -0.5  # Out of bounds
            elif i <= 300:
                score = 1.5   # Out of bounds
            else:
                score = 0.0
            
            micro_results.append(
                MockMicroQuestionRun(
                    question_id=f"Q{i:03d}",
                    question_global=i,
                    base_slot="SLOT",
                    metadata={"overall_confidence": score},
                    evidence=evidence,
                )
            )
        
        # Input validation
        validate_micro_results_input(micro_results, 305)
        
        # Validation pipeline
        counters = ValidationCounters(total_questions=len(micro_results))
        
        for micro_result in micro_results:
            validate_evidence_presence(
                micro_result.evidence,
                micro_result.question_id,
                micro_result.question_global,
                counters,
            )
            
            score = micro_result.metadata.get("overall_confidence", 0.0)
            validate_and_clamp_score(
                score,
                micro_result.question_id,
                micro_result.question_global,
                counters,
            )
            
            # Assume all get "EXCELENTE" quality level
            validate_quality_level(
                "EXCELENTE",
                micro_result.question_id,
                micro_result.question_global,
                counters,
            )
        
        # Verify counters
        assert counters.total_questions == 305
        assert counters.missing_evidence == 5
        assert counters.out_of_bounds_scores == 50  # 25 + 25
        assert counters.score_clamping_applied == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
