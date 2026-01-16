"""
Tests for Phase 2 → Phase 3 Interface Adapter
==============================================

Property-based, edge case, and contraejemplo tests for the
Phase2ToPhase3Adapter as specified in the formal audit.

Version: 1.0.0
Date: 2026-01-13
"""
from __future__ import annotations

import pytest
from dataclasses import dataclass
from typing import Any

from farfan_pipeline.phases.Phase_02.interphase.phase2_phase3_adapter import (
    MicroQuestionRun,
    AdaptationResult,
    parse_phase2_question_id,
    derive_dimension,
    derive_question_in_dimension,
    derive_base_slot,
    derive_question_global,
    transform_question_id,
    reverse_transform_question_id,
    adapt_single_result,
    adapt_phase2_to_phase3,
    validate_adaptation,
    PHASE2_QID_PATTERN,
    PHASE3_QID_PATTERN,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@dataclass
class MockPhase2Result:
    """Mock Phase 2 result."""
    question_id: str
    policy_area: str
    narrative: str
    evidence: dict[str, Any]
    confidence_score: float
    provenance: dict[str, Any]
    metadata: dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def create_mock_result(
    question_id: str = "Q001_PA01",
    confidence_score: float = 0.75,
    evidence: dict[str, Any] | None = None,
) -> MockPhase2Result:
    """Create a mock Phase 2 result."""
    if evidence is None:
        evidence = {"elements": [{"type": "test"}], "confidence": 0.8}
    
    return MockPhase2Result(
        question_id=question_id,
        policy_area=question_id.split("_")[1] if "_" in question_id else "PA01",
        narrative="x" * 100,
        evidence=evidence,
        confidence_score=confidence_score,
        provenance={"sha256": "a" * 64},
    )


def create_mock_phase2_output(count: int = 300) -> dict[str, Any]:
    """Create mock Phase 2 output with specified number of results."""
    results = []
    for i in range(count):
        q_base = (i % 30) + 1
        pa_num = (i // 30) + 1
        question_id = f"Q{q_base:03d}_PA{pa_num:02d}"
        results.append(create_mock_result(question_id=question_id))
    return {"results": results}


# =============================================================================
# DERIVATION FUNCTION TESTS
# =============================================================================

class TestParsePhase2QuestionId:
    """Tests for parse_phase2_question_id function."""
    
    def test_valid_format_q001_pa01(self):
        """Parse Q001_PA01."""
        q_base, pa_num = parse_phase2_question_id("Q001_PA01")
        assert q_base == 1
        assert pa_num == 1
    
    def test_valid_format_q015_pa05(self):
        """Parse Q015_PA05."""
        q_base, pa_num = parse_phase2_question_id("Q015_PA05")
        assert q_base == 15
        assert pa_num == 5
    
    def test_valid_format_q030_pa10(self):
        """Parse Q030_PA10."""
        q_base, pa_num = parse_phase2_question_id("Q030_PA10")
        assert q_base == 30
        assert pa_num == 10
    
    def test_invalid_format_raises(self):
        """Invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Phase 2 question_id format"):
            parse_phase2_question_id("PA01-DIM01-Q001")  # Phase 3 format
    
    def test_out_of_range_q_raises(self):
        """Out of range question raises ValueError."""
        with pytest.raises(ValueError, match="out of range"):
            parse_phase2_question_id("Q031_PA01")
    
    def test_out_of_range_pa_raises(self):
        """Out of range PA raises ValueError."""
        with pytest.raises(ValueError, match="out of range"):
            parse_phase2_question_id("Q001_PA11")


class TestDeriveDimension:
    """Tests for derive_dimension function."""
    
    @pytest.mark.parametrize("q_base,expected", [
        (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),      # DIM01
        (6, 2), (7, 2), (8, 2), (9, 2), (10, 2),     # DIM02
        (11, 3), (12, 3), (13, 3), (14, 3), (15, 3), # DIM03
        (16, 4), (17, 4), (18, 4), (19, 4), (20, 4), # DIM04
        (21, 5), (22, 5), (23, 5), (24, 5), (25, 5), # DIM05
        (26, 6), (27, 6), (28, 6), (29, 6), (30, 6), # DIM06
    ])
    def test_dimension_derivation(self, q_base: int, expected: int):
        """Test dimension derivation for all questions."""
        assert derive_dimension(q_base) == expected


class TestDeriveQuestionInDimension:
    """Tests for derive_question_in_dimension function."""
    
    @pytest.mark.parametrize("q_base,expected", [
        (1, 1), (6, 1), (11, 1), (16, 1), (21, 1), (26, 1),  # Q1 in dim
        (2, 2), (7, 2), (12, 2), (17, 2), (22, 2), (27, 2),  # Q2 in dim
        (5, 5), (10, 5), (15, 5), (20, 5), (25, 5), (30, 5), # Q5 in dim
    ])
    def test_question_in_dimension_derivation(self, q_base: int, expected: int):
        """Test question position within dimension."""
        assert derive_question_in_dimension(q_base) == expected


class TestDeriveBaseSlot:
    """Tests for derive_base_slot function."""
    
    @pytest.mark.parametrize("q_base,expected", [
        (1, "D1-Q1"),
        (5, "D1-Q5"),
        (6, "D2-Q1"),
        (10, "D2-Q5"),
        (15, "D3-Q5"),
        (20, "D4-Q5"),
        (25, "D5-Q5"),
        (30, "D6-Q5"),
    ])
    def test_base_slot_derivation(self, q_base: int, expected: str):
        """Test base_slot derivation."""
        assert derive_base_slot(q_base) == expected


class TestDeriveQuestionGlobal:
    """Tests for derive_question_global function."""
    
    @pytest.mark.parametrize("q_base,pa_num,expected", [
        (1, 1, 1),      # First question
        (30, 1, 30),    # Last Q in PA01
        (1, 2, 31),     # First Q in PA02
        (15, 5, 135),   # (5-1)*30 + 15 = 135
        (30, 10, 300),  # Last question
    ])
    def test_question_global_derivation(self, q_base: int, pa_num: int, expected: int):
        """Test question_global derivation."""
        assert derive_question_global(q_base, pa_num) == expected


# =============================================================================
# QUESTION ID TRANSFORMATION TESTS
# =============================================================================

class TestTransformQuestionId:
    """Tests for transform_question_id function."""
    
    @pytest.mark.parametrize("phase2_id,phase3_id", [
        ("Q001_PA01", "PA01-DIM01-Q001"),
        ("Q005_PA01", "PA01-DIM01-Q005"),
        ("Q006_PA02", "PA02-DIM02-Q006"),
        ("Q015_PA05", "PA05-DIM03-Q015"),
        ("Q020_PA07", "PA07-DIM04-Q020"),
        ("Q025_PA08", "PA08-DIM05-Q025"),
        ("Q030_PA10", "PA10-DIM06-Q030"),
    ])
    def test_transform_question_id(self, phase2_id: str, phase3_id: str):
        """Test question_id transformation."""
        assert transform_question_id(phase2_id) == phase3_id


class TestReverseTransformQuestionId:
    """Tests for reverse_transform_question_id function."""
    
    @pytest.mark.parametrize("phase3_id,phase2_id", [
        ("PA01-DIM01-Q001", "Q001_PA01"),
        ("PA05-DIM03-Q015", "Q015_PA05"),
        ("PA10-DIM06-Q030", "Q030_PA10"),
    ])
    def test_reverse_transform(self, phase3_id: str, phase2_id: str):
        """Test reverse transformation."""
        assert reverse_transform_question_id(phase3_id) == phase2_id
    
    def test_invalid_format_raises(self):
        """Invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Phase 3 question_id format"):
            reverse_transform_question_id("Q001_PA01")  # Phase 2 format


class TestTransformRoundTrip:
    """Tests for round-trip transformation."""
    
    @pytest.mark.parametrize("q_base,pa_num", [
        (1, 1), (15, 5), (30, 10), (7, 3), (22, 8),
    ])
    def test_round_trip(self, q_base: int, pa_num: int):
        """Round-trip transformation preserves identity."""
        original = f"Q{q_base:03d}_PA{pa_num:02d}"
        transformed = transform_question_id(original)
        restored = reverse_transform_question_id(transformed)
        assert restored == original


# =============================================================================
# ADAPTER FUNCTION TESTS
# =============================================================================

class TestAdaptSingleResult:
    """Tests for adapt_single_result function."""
    
    def test_basic_adaptation(self):
        """Basic adaptation works."""
        result = create_mock_result("Q015_PA05", confidence_score=0.75)
        mqr = adapt_single_result(result)
        
        assert mqr.question_id == "PA05-DIM03-Q015"
        assert mqr.question_global == 135
        assert mqr.base_slot == "D3-Q5"
        assert mqr.error is None
    
    def test_confidence_injection(self):
        """Confidence is injected into evidence."""
        result = create_mock_result("Q001_PA01", confidence_score=0.85)
        result.evidence = {"elements": []}  # No confidence key
        
        mqr = adapt_single_result(result, inject_confidence=True)
        
        assert mqr.evidence['confidence'] == 0.85
    
    def test_confidence_not_overwritten(self):
        """Existing evidence confidence is not overwritten."""
        result = create_mock_result("Q001_PA01", confidence_score=0.85)
        result.evidence = {"elements": [], "confidence": 0.5}  # Has confidence
        
        mqr = adapt_single_result(result, inject_confidence=True)
        
        # Original confidence preserved
        assert mqr.evidence['confidence'] == 0.5
    
    def test_invalid_question_id_returns_error(self):
        """Invalid question_id returns error MicroQuestionRun."""
        result = create_mock_result("INVALID_ID")
        mqr = adapt_single_result(result)
        
        assert mqr.error is not None
        assert "Invalid Phase 2 question_id format" in mqr.error
    
    def test_dict_input(self):
        """Dict input is accepted."""
        result_dict = {
            "question_id": "Q001_PA01",
            "confidence_score": 0.75,
            "evidence": {"elements": []},
            "metadata": {},
        }
        
        mqr = adapt_single_result(result_dict)
        
        assert mqr.question_id == "PA01-DIM01-Q001"
        assert mqr.question_global == 1


class TestAdaptPhase2ToPhase3:
    """Tests for adapt_phase2_to_phase3 function."""
    
    def test_full_adaptation_300(self):
        """Adapt all 300 results."""
        output = create_mock_phase2_output(300)
        result = adapt_phase2_to_phase3(output)
        
        assert len(result.micro_runs) == 300
        assert result.success_count == 300
        assert result.error_count == 0
    
    def test_question_global_uniqueness(self):
        """All question_global values are unique."""
        output = create_mock_phase2_output(300)
        result = adapt_phase2_to_phase3(output)
        
        globals = [mqr.question_global for mqr in result.micro_runs]
        assert len(globals) == len(set(globals))
    
    def test_all_phase3_format(self):
        """All question_ids are in Phase 3 format."""
        output = create_mock_phase2_output(10)
        result = adapt_phase2_to_phase3(output)
        
        for mqr in result.micro_runs:
            if not mqr.error:
                assert PHASE3_QID_PATTERN.match(mqr.question_id)
    
    def test_list_input(self):
        """List input is accepted."""
        results = [create_mock_result(f"Q{i:03d}_PA01") for i in range(1, 6)]
        result = adapt_phase2_to_phase3(results)
        
        assert len(result.micro_runs) == 5
        assert result.success_count == 5


class TestValidateAdaptation:
    """Tests for validate_adaptation function."""
    
    def test_valid_adaptation(self):
        """Valid adaptation passes validation."""
        output = create_mock_phase2_output(300)
        result = adapt_phase2_to_phase3(output)
        
        is_valid, errors = validate_adaptation(300, result)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_count_mismatch_detected(self):
        """Count mismatch is detected."""
        output = create_mock_phase2_output(290)
        result = adapt_phase2_to_phase3(output)
        
        is_valid, errors = validate_adaptation(300, result)
        
        assert not is_valid
        assert any("Count mismatch" in e for e in errors)


# =============================================================================
# CONTRAEJEMPLO TESTS (INC-P23-XXX)
# =============================================================================

class TestIncP23001QuestionIdFormat:
    """Tests for INC-P23-001: question_id format mismatch."""
    
    def test_format_mismatch_without_adapter(self):
        """Without adapter: formats don't match."""
        result = create_mock_result("Q015_PA05")
        
        # Phase 2 format
        assert result.question_id == "Q015_PA05"
        # Phase 3 expects
        assert result.question_id != "PA05-DIM03-Q015"
    
    def test_format_match_with_adapter(self):
        """With adapter: formats match."""
        result = create_mock_result("Q015_PA05")
        mqr = adapt_single_result(result)
        
        assert mqr.question_id == "PA05-DIM03-Q015"


class TestIncP23003ConfidenceLocation:
    """Tests for INC-P23-003: confidence location mismatch."""
    
    def test_confidence_missing_without_injection(self):
        """Without injection: confidence missing from evidence."""
        result = create_mock_result("Q001_PA01", confidence_score=0.75)
        result.evidence = {"elements": []}  # No confidence
        
        mqr = adapt_single_result(result, inject_confidence=False)
        
        # Confidence not in evidence
        assert 'confidence' not in mqr.evidence
    
    def test_confidence_present_with_injection(self):
        """With injection: confidence in evidence."""
        result = create_mock_result("Q001_PA01", confidence_score=0.75)
        result.evidence = {"elements": []}  # No confidence
        
        mqr = adapt_single_result(result, inject_confidence=True)
        
        assert mqr.evidence['confidence'] == 0.75


class TestIncP23004QuestionGlobal:
    """Tests for INC-P23-004: question_global derivation."""
    
    def test_question_global_derived(self):
        """question_global is correctly derived."""
        result = create_mock_result("Q015_PA05")
        mqr = adapt_single_result(result)
        
        # (5-1)*30 + 15 = 135
        assert mqr.question_global == 135


class TestIncP23005BaseSlot:
    """Tests for INC-P23-005: base_slot derivation."""
    
    def test_base_slot_derived(self):
        """base_slot is correctly derived."""
        result = create_mock_result("Q015_PA05")
        mqr = adapt_single_result(result)
        
        # Q015 → DIM03, Q5 in dim → D3-Q5
        assert mqr.base_slot == "D3-Q5"


# =============================================================================
# INTEGRATION TEST
# =============================================================================

class TestFullAdaptationPipeline:
    """Integration test for complete adaptation pipeline."""
    
    def test_full_pipeline(self):
        """Complete adaptation pipeline works correctly."""
        # Create realistic Phase 2 output
        output = create_mock_phase2_output(300)
        
        # Adapt
        result = adapt_phase2_to_phase3(output)
        
        # Validate
        is_valid, errors = validate_adaptation(300, result)
        
        # Assertions
        assert is_valid, f"Validation errors: {errors}"
        assert len(result.micro_runs) == 300
        assert result.success_count == 300
        assert result.error_count == 0
        
        # Verify first and last
        first = result.micro_runs[0]
        assert first.question_id == "PA01-DIM01-Q001"
        assert first.question_global == 1
        assert first.base_slot == "D1-Q1"
        
        # Find Q030_PA10 (should be at index 299)
        last_expected_global = 300
        last = [m for m in result.micro_runs if m.question_global == last_expected_global][0]
        assert last.question_id == "PA10-DIM06-Q030"
        assert last.base_slot == "D6-Q5"
