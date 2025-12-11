"""Tests for Phase 3 scoring transformation logic.

Validates that Phase 3 correctly extracts validation scores from Phase 2
evidence and transforms MicroQuestionRun to ScoredMicroQuestion.
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from canonic_phases.Phase_three.scoring import (
    extract_score_from_evidence,
    extract_quality_level,
    transform_micro_result_to_scored,
)


@dataclass
class MockEvidence:
    """Mock Evidence object for testing."""
    modality: str
    elements: list[Any] = field(default_factory=list)
    raw_results: dict[str, Any] = field(default_factory=dict)
    validation: dict[str, Any] = field(default_factory=dict)


@dataclass
class MockMicroQuestionRun:
    """Mock MicroQuestionRun for testing."""
    question_id: str
    question_global: int
    base_slot: str
    metadata: dict[str, Any]
    evidence: Any
    error: str | None = None


def test_extract_score_from_evidence_valid():
    """Test extracting valid score from evidence."""
    evidence = {
        "validation": {
            "score": 0.85,
            "quality_level": "EXCELENTE"
        }
    }
    
    score = extract_score_from_evidence(evidence)
    assert score == 0.85, f"Expected 0.85, got {score}"
    print("✓ extract_score_from_evidence with valid score")


def test_extract_score_from_evidence_none():
    """Test extracting score when evidence is None."""
    score = extract_score_from_evidence(None)
    assert score == 0.0, f"Expected 0.0 for None evidence, got {score}"
    print("✓ extract_score_from_evidence with None evidence")


def test_extract_score_from_evidence_missing():
    """Test extracting score when validation is missing."""
    evidence = {"other_data": "value"}
    
    score = extract_score_from_evidence(evidence)
    assert score == 0.0, f"Expected 0.0 for missing validation, got {score}"
    print("✓ extract_score_from_evidence with missing validation")


def test_extract_quality_level_valid():
    """Test extracting valid quality level."""
    evidence = {
        "validation": {
            "score": 0.85,
            "quality_level": "EXCELENTE"
        }
    }
    
    quality = extract_quality_level(evidence)
    assert quality == "EXCELENTE", f"Expected EXCELENTE, got {quality}"
    print("✓ extract_quality_level with valid quality")


def test_extract_quality_level_none():
    """Test extracting quality level when evidence is None."""
    quality = extract_quality_level(None)
    assert quality == "INSUFICIENTE", f"Expected INSUFICIENTE for None, got {quality}"
    print("✓ extract_quality_level with None evidence")


def test_transform_micro_result_to_scored():
    """Test full transformation from MicroQuestionRun to scored dict."""
    evidence = MockEvidence(
        modality="TYPE_A",
        elements=[{"text": "test"}],
        validation={
            "score": 0.75,
            "quality_level": "BUENO",
            "passed": True
        }
    )
    
    micro_result = MockMicroQuestionRun(
        question_id="D1-Q1",
        question_global=1,
        base_slot="D1-Q1",
        metadata={"policy_area": "PA1", "dimension": "D1"},
        evidence=evidence,
        error=None
    )
    
    scored_dict = transform_micro_result_to_scored(micro_result)
    
    assert scored_dict["question_id"] == "D1-Q1"
    assert scored_dict["question_global"] == 1
    assert scored_dict["base_slot"] == "D1-Q1"
    assert scored_dict["score"] == 0.75
    assert scored_dict["quality_level"] == "BUENO"
    assert scored_dict["error"] is None
    
    print("✓ transform_micro_result_to_scored with valid data")


def test_transform_micro_result_with_error():
    """Test transformation when micro result has error."""
    evidence = MockEvidence(
        modality="TYPE_A",
        validation={
            "score": 0.0,
            "quality_level": "ERROR"
        }
    )
    
    micro_result = MockMicroQuestionRun(
        question_id="D1-Q2",
        question_global=2,
        base_slot="D1-Q2",
        metadata={},
        evidence=evidence,
        error="Execution failed"
    )
    
    scored_dict = transform_micro_result_to_scored(micro_result)
    
    assert scored_dict["error"] == "Execution failed"
    assert scored_dict["score"] == 0.0
    
    print("✓ transform_micro_result_to_scored with error")


def run_all_tests():
    """Run all Phase 3 tests."""
    print("\n=== Phase 3 Scoring Tests ===\n")
    
    try:
        test_extract_score_from_evidence_valid()
        test_extract_score_from_evidence_none()
        test_extract_score_from_evidence_missing()
        test_extract_quality_level_valid()
        test_extract_quality_level_none()
        test_transform_micro_result_to_scored()
        test_transform_micro_result_with_error()
        
        print("\n✅ All Phase 3 tests passed!\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
