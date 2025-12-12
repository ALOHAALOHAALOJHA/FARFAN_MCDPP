"""
Tests for Nexus-Scoring Alignment and Interface Stability
=========================================================

This test suite verifies the harmonization between Phase 2 (EvidenceNexus)
and Phase 3 (Scoring), ensuring stable entry point for scoring operations.

Test Categories:
1. Interface Contract Tests
2. Evidence Structure Tests
3. Scoring Modality Tests
4. Adaptive Threshold Tests
5. End-to-End Integration Tests

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
Date: 2025-12-11
"""

import pytest
from typing import Any

from farfan_pipeline.analysis.scoring.scoring import (
    EvidenceStructureError,
    ModalityConfig,
    ModalityValidationError,
    QualityLevel,
    ScoredResult,
    ScoringValidator,
    apply_scoring,
    determine_quality_level,
)
from farfan_pipeline.analysis.scoring.nexus_scoring_validator import (
    NexusScoringValidator,
    BatchValidator,
    ValidationResult,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def valid_nexus_evidence() -> dict[str, Any]:
    """Valid evidence structure from Phase 2."""
    return {
        "elements": [
            {"text": "Element 1", "source": "doc1", "confidence": 0.9},
            {"text": "Element 2", "source": "doc2", "confidence": 0.8},
            {"text": "Element 3", "source": "doc3", "confidence": 0.85},
        ],
        "by_type": {
            "indicator_numeric": [{"value": 100, "unit": "personas"}],
            "territorial_coverage": [{"region": "nacional"}],
        },
        "confidence": 0.85,
        "completeness": 0.90,
        "graph_hash": "a" * 64,  # Valid SHA-256 hex length
        "patterns": {
            "pattern1": ["match1", "match2"],
            "pattern2": ["match3"],
        }
    }


@pytest.fixture
def valid_micro_question_run(valid_nexus_evidence: dict[str, Any]) -> dict[str, Any]:
    """Valid MicroQuestionRun from Phase 2."""
    return {
        "question_id": "Q001",
        "question_global": 1,
        "base_slot": "D1-Q1",
        "metadata": {
            "policy_area_id": "PA01",
            "dimension_id": "DIM01",
        },
        "evidence": valid_nexus_evidence,
        "error": None,
        "duration_ms": 123.45,
        "aborted": False,
    }


@pytest.fixture
def valid_scoring_context() -> dict[str, Any]:
    """Valid scoring context from SISAS."""
    return {
        "modality": "TYPE_A",
        "threshold": 0.75,
        "weight_elements": 0.5,
        "weight_similarity": 0.3,
        "weight_patterns": 0.2,
        "aggregation_method": "weighted_mean",
    }


# =============================================================================
# INTERFACE CONTRACT TESTS
# =============================================================================

class TestInterfaceContract:
    """Test interface contract between Nexus and Scoring."""
    
    def test_valid_nexus_output_structure(
        self,
        valid_micro_question_run: dict[str, Any]
    ) -> None:
        """Test valid nexus output passes validation."""
        result = NexusScoringValidator.validate_nexus_output(valid_micro_question_run)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.metadata["has_evidence"]
        assert result.metadata["confidence"] == 0.85
    
    def test_missing_evidence_key(self) -> None:
        """Test missing evidence key fails validation."""
        invalid_run = {
            "question_id": "Q001",
            "metadata": {},
        }
        
        result = NexusScoringValidator.validate_nexus_output(invalid_run)
        
        assert not result.is_valid
        assert any("evidence" in err for err in result.errors)
    
    def test_none_evidence_handled_gracefully(self) -> None:
        """Test None evidence (failed question) handled gracefully."""
        run_with_none_evidence = {
            "question_id": "Q001",
            "evidence": None,
            "error": "Extraction failed",
        }
        
        result = NexusScoringValidator.validate_nexus_output(run_with_none_evidence)
        
        assert result.is_valid  # None is valid for failed questions
        assert len(result.warnings) > 0
        assert not result.metadata["has_evidence"]
    
    def test_missing_required_evidence_keys(self) -> None:
        """Test missing required evidence keys."""
        incomplete_evidence = {
            "elements": [],
            # Missing "confidence"
        }
        run = {"evidence": incomplete_evidence}
        
        result = NexusScoringValidator.validate_nexus_output(run)
        
        assert not result.is_valid
        assert any("confidence" in err for err in result.errors)


# =============================================================================
# EVIDENCE STRUCTURE TESTS
# =============================================================================

class TestEvidenceStructure:
    """Test evidence structure validation."""
    
    def test_scoring_validator_accepts_valid_evidence(
        self,
        valid_nexus_evidence: dict[str, Any]
    ) -> None:
        """Test ScoringValidator accepts valid nexus evidence."""
        # Should not raise exception
        ScoringValidator.validate_evidence(valid_nexus_evidence)
    
    def test_scoring_validator_rejects_invalid_type(self) -> None:
        """Test ScoringValidator rejects non-dict evidence."""
        with pytest.raises(EvidenceStructureError, match="must be dict"):
            ScoringValidator.validate_evidence("invalid")
    
    def test_scoring_validator_rejects_missing_elements(self) -> None:
        """Test ScoringValidator rejects evidence without elements."""
        invalid = {"confidence": 0.5}  # Missing "elements"
        
        with pytest.raises(EvidenceStructureError, match="elements"):
            ScoringValidator.validate_evidence(invalid)
    
    def test_scoring_validator_rejects_invalid_confidence(self) -> None:
        """Test ScoringValidator rejects out-of-range confidence."""
        invalid = {
            "elements": [],
            "confidence": 1.5  # Out of range
        }
        
        with pytest.raises(EvidenceStructureError, match="confidence"):
            ScoringValidator.validate_evidence(invalid)
    
    def test_extract_scores_from_evidence(
        self,
        valid_nexus_evidence: dict[str, Any]
    ) -> None:
        """Test score extraction from evidence."""
        scores = ScoringValidator.extract_scores(valid_nexus_evidence)
        
        assert "elements_score" in scores
        assert "similarity_score" in scores
        assert "patterns_score" in scores
        
        # All scores in [0, 1]
        for score in scores.values():
            assert 0.0 <= score <= 1.0


# =============================================================================
# SCORING MODALITY TESTS
# =============================================================================

class TestScoringModalities:
    """Test scoring modality functions."""
    
    @pytest.mark.parametrize("modality", ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E", "TYPE_F"])
    def test_all_modalities_produce_valid_scores(
        self,
        valid_nexus_evidence: dict[str, Any],
        modality: str
    ) -> None:
        """Test all modalities produce valid scores."""
        result = apply_scoring(valid_nexus_evidence, modality)  # type: ignore
        
        assert isinstance(result, ScoredResult)
        assert 0.0 <= result.score <= 1.0
        assert 0.0 <= result.normalized_score <= 100.0
        assert isinstance(result.quality_level, QualityLevel)
        assert isinstance(result.passes_threshold, bool)
        assert len(result.confidence_interval) == 2
    
    def test_type_a_high_threshold(
        self,
        valid_nexus_evidence: dict[str, Any]
    ) -> None:
        """Test TYPE_A uses high threshold (0.75)."""
        result = apply_scoring(valid_nexus_evidence, "TYPE_A")
        
        assert result.scoring_metadata["threshold"] == 0.75
        assert result.scoring_metadata["modality"] == "TYPE_A"
    
    def test_type_b_pattern_emphasis(
        self,
        valid_nexus_evidence: dict[str, Any]
    ) -> None:
        """Test TYPE_B emphasizes patterns."""
        result = apply_scoring(valid_nexus_evidence, "TYPE_B")
        
        # TYPE_B should have higher pattern weight
        assert result.scoring_metadata["threshold"] == 0.65
    
    def test_modality_config_validation(self) -> None:
        """Test ModalityConfig validation."""
        # Valid config
        config = ModalityConfig(
            modality="TYPE_A",
            threshold=0.75,
            weight_elements=0.5,
            weight_similarity=0.3,
            weight_patterns=0.2
        )
        assert config.threshold == 0.75
        
        # Invalid threshold
        with pytest.raises(ModalityValidationError):
            ModalityConfig(
                modality="TYPE_A",
                threshold=1.5,  # Out of range
                weight_elements=0.5,
                weight_similarity=0.3,
                weight_patterns=0.2
            )
        
        # Invalid weights (don't sum to 1)
        with pytest.raises(ModalityValidationError):
            ModalityConfig(
                modality="TYPE_A",
                threshold=0.75,
                weight_elements=0.5,
                weight_similarity=0.5,
                weight_patterns=0.5  # Sum > 1
            )


# =============================================================================
# ADAPTIVE THRESHOLD TESTS
# =============================================================================

class TestAdaptiveThresholds:
    """Test adaptive threshold computation and application."""
    
    def test_scoring_context_validation(
        self,
        valid_scoring_context: dict[str, Any]
    ) -> None:
        """Test scoring context validation."""
        result = NexusScoringValidator.validate_scoring_context(valid_scoring_context)
        
        assert result.is_valid
        assert result.metadata["has_context"]
        assert result.metadata["modality"] == "TYPE_A"
        assert result.metadata["threshold"] == 0.75
    
    def test_missing_scoring_context_handled(self) -> None:
        """Test missing scoring context uses defaults."""
        result = NexusScoringValidator.validate_scoring_context(None)
        
        assert result.is_valid
        assert not result.metadata["has_context"]
        assert len(result.warnings) > 0
    
    def test_invalid_threshold_rejected(self) -> None:
        """Test invalid threshold rejected."""
        invalid_context = {
            "modality": "TYPE_A",
            "threshold": 1.5  # Out of range
        }
        
        result = NexusScoringValidator.validate_scoring_context(invalid_context)
        
        assert not result.is_valid
        assert any("threshold" in err.lower() for err in result.errors)


# =============================================================================
# QUALITY LEVEL TESTS
# =============================================================================

class TestQualityLevels:
    """Test quality level determination."""
    
    @pytest.mark.parametrize("score,expected_level", [
        (0.90, QualityLevel.EXCELLENT),
        (0.85, QualityLevel.EXCELLENT),
        (0.75, QualityLevel.GOOD),
        (0.70, QualityLevel.GOOD),
        (0.60, QualityLevel.ADEQUATE),
        (0.50, QualityLevel.ADEQUATE),
        (0.40, QualityLevel.POOR),
        (0.20, QualityLevel.POOR),
    ])
    def test_quality_level_thresholds(
        self,
        score: float,
        expected_level: QualityLevel
    ) -> None:
        """Test quality level determination matches thresholds."""
        level = determine_quality_level(score)
        assert level == expected_level


# =============================================================================
# PHASE TRANSITION TESTS
# =============================================================================

class TestPhaseTransition:
    """Test complete Phase 2 → Phase 3 transition."""
    
    def test_valid_phase_transition(
        self,
        valid_micro_question_run: dict[str, Any],
        valid_scoring_context: dict[str, Any]
    ) -> None:
        """Test valid phase transition."""
        result = NexusScoringValidator.validate_phase_transition(
            valid_micro_question_run,
            valid_scoring_context
        )
        
        assert result.is_valid
        assert result.metadata["overall_valid"]
        assert result.metadata["nexus_validation"]["has_evidence"]
        assert result.metadata["context_validation"]["has_context"]
    
    def test_confidence_threshold_alignment(
        self,
        valid_micro_question_run: dict[str, Any]
    ) -> None:
        """Test confidence vs threshold alignment warning."""
        # Set low threshold
        low_threshold_context = {
            "modality": "TYPE_A",
            "threshold": 0.90,  # Higher than evidence confidence (0.85)
        }
        
        result = NexusScoringValidator.validate_phase_transition(
            valid_micro_question_run,
            low_threshold_context
        )
        
        # Should be valid but with warning
        assert result.is_valid
        assert len(result.warnings) > 0
        assert "confidence_threshold_delta" in result.metadata


# =============================================================================
# BATCH VALIDATION TESTS
# =============================================================================

class TestBatchValidation:
    """Test batch validation for multiple questions."""
    
    def test_batch_validation_all_valid(
        self,
        valid_micro_question_run: dict[str, Any],
        valid_scoring_context: dict[str, Any]
    ) -> None:
        """Test batch validation with all valid runs."""
        runs = [valid_micro_question_run.copy() for _ in range(10)]
        contexts = [valid_scoring_context.copy() for _ in range(10)]
        
        batch_result = BatchValidator.validate_batch(runs, contexts)
        
        assert batch_result["total_validations"] == 10
        assert batch_result["valid_count"] == 10
        assert batch_result["success_rate"] == 1.0
        assert batch_result["total_errors"] == 0
    
    def test_batch_validation_mixed_results(
        self,
        valid_micro_question_run: dict[str, Any]
    ) -> None:
        """Test batch validation with mixed results."""
        # Create mix of valid and invalid runs
        runs = []
        for i in range(5):
            runs.append(valid_micro_question_run.copy())
        for i in range(5):
            invalid_run = {"question_id": f"Q{i:03d}"}  # Missing evidence
            runs.append(invalid_run)
        
        batch_result = BatchValidator.validate_batch(runs)
        
        assert batch_result["total_validations"] == 10
        assert batch_result["valid_count"] == 5
        assert batch_result["invalid_count"] == 5
        assert batch_result["success_rate"] == 0.5


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_complete_nexus_to_scoring_flow(
        self,
        valid_nexus_evidence: dict[str, Any]
    ) -> None:
        """Test complete flow from nexus evidence to scored result."""
        # 1. Validate evidence structure
        ScoringValidator.validate_evidence(valid_nexus_evidence)
        
        # 2. Apply scoring
        scored_result = apply_scoring(valid_nexus_evidence, "TYPE_A")
        
        # 3. Verify result structure
        assert isinstance(scored_result, ScoredResult)
        assert scored_result.score > 0
        assert scored_result.quality_level in QualityLevel
        
        # 4. Convert to dict (for serialization)
        result_dict = scored_result.to_dict()
        assert "score" in result_dict
        assert "quality_level" in result_dict
    
    def test_300_questions_interface_stability(
        self,
        valid_micro_question_run: dict[str, Any],
        valid_scoring_context: dict[str, Any]
    ) -> None:
        """Test interface stability for all 300 questions."""
        # Simulate 300 questions
        runs = []
        contexts = []
        
        for i in range(1, 301):
            run = valid_micro_question_run.copy()
            run["question_id"] = f"Q{i:03d}"
            run["question_global"] = i
            runs.append(run)
            
            context = valid_scoring_context.copy()
            # Vary modalities
            modalities = ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E", "TYPE_F"]
            context["modality"] = modalities[i % len(modalities)]
            contexts.append(context)
        
        # Batch validate
        batch_result = BatchValidator.validate_batch(runs, contexts)
        
        # All should be valid
        assert batch_result["total_validations"] == 300
        assert batch_result["success_rate"] == 1.0
        
        print(f"\n✅ Interface stability confirmed for 300 questions")
        print(f"   Valid: {batch_result['valid_count']}/300")
        print(f"   Success rate: {batch_result['success_rate']:.2%}")


# =============================================================================
# PYTEST MARKERS
# =============================================================================

pytestmark = pytest.mark.updated
