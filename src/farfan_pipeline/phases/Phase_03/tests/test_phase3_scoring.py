"""Tests for Phase 3 scoring transformation logic.

Validates that Phase 3 correctly extracts EvidenceNexus outputs
(overall_confidence, completeness) from Phase 2 results and transforms
MicroQuestionRun to ScoredMicroQuestion.
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

# Add src to path for imports
repo_root = Path(__file__).resolve().parent.parent

from farfan_pipeline.phases.Phase_03.phase3_20_00_score_extraction import (
    extract_score_from_nexus,
    map_completeness_to_quality,
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
    confidence_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class MockMicroQuestionRun:
    """Mock MicroQuestionRun for testing."""
    question_id: str
    question_global: int
    base_slot: str
    metadata: dict[str, Any]
    evidence: Any
    error: str | None = None


def test_extract_score_from_nexus_with_overall_confidence():
    """Test extracting score from overall_confidence (primary path)."""
    result_data = {
        "overall_confidence": 0.85,
        "completeness": "complete"
    }
    
    score = extract_score_from_nexus(result_data)
    assert score == 0.85, f"Expected 0.85, got {score}"
    print("✓ extract_score_from_nexus with overall_confidence")


def test_extract_score_from_nexus_fallback_validation():
    """Test extracting score from validation.score (fallback)."""
    result_data = {
        "validation": {
            "score": 0.0,
            "quality_level": "FAILED_VALIDATION"
        }
    }
    
    score = extract_score_from_nexus(result_data)
    assert score == 0.0, f"Expected 0.0, got {score}"
    print("✓ extract_score_from_nexus with validation fallback")


def test_extract_score_from_nexus_fallback_confidence_mean():
    """Test extracting score from evidence confidence_scores.mean."""
    result_data = {
        "evidence": {
            "confidence_scores": {
                "mean": 0.72,
                "min": 0.5,
                "max": 0.9
            }
        }
    }
    
    score = extract_score_from_nexus(result_data)
    assert score == 0.72, f"Expected 0.72, got {score}"
    print("✓ extract_score_from_nexus with confidence_scores fallback")


def test_map_completeness_to_quality_complete():
    """Test mapping complete → EXCELENTE."""
    quality = map_completeness_to_quality("complete")
    assert quality == "EXCELENTE", f"Expected EXCELENTE, got {quality}"
    print("✓ map_completeness_to_quality: complete → EXCELENTE")


def test_map_completeness_to_quality_partial():
    """Test mapping partial → ACEPTABLE."""
    quality = map_completeness_to_quality("partial")
    assert quality == "ACEPTABLE", f"Expected ACEPTABLE, got {quality}"
    print("✓ map_completeness_to_quality: partial → ACEPTABLE")


def test_map_completeness_to_quality_insufficient():
    """Test mapping insufficient → INSUFICIENTE."""
    quality = map_completeness_to_quality("insufficient")
    assert quality == "INSUFICIENTE", f"Expected INSUFICIENTE, got {quality}"
    print("✓ map_completeness_to_quality: insufficient → INSUFICIENTE")


def test_map_completeness_to_quality_not_applicable():
    """Test mapping not_applicable → NO_APLICABLE."""
    quality = map_completeness_to_quality("not_applicable")
    assert quality == "NO_APLICABLE", f"Expected NO_APLICABLE, got {quality}"
    print("✓ map_completeness_to_quality: not_applicable → NO_APLICABLE")


def test_extract_quality_level_with_completeness():
    """Test extracting quality level from completeness (primary)."""
    quality = extract_quality_level(None, completeness="complete")
    assert quality == "EXCELENTE", f"Expected EXCELENTE, got {quality}"
    print("✓ extract_quality_level with completeness")


def test_extract_quality_level_fallback_validation():
    """Test extracting quality level from validation (fallback)."""
    evidence = {
        "validation": {
            "quality_level": "FAILED_VALIDATION"
        }
    }
    
    quality = extract_quality_level(evidence, completeness=None)
    assert quality == "FAILED_VALIDATION", f"Expected FAILED_VALIDATION, got {quality}"
    print("✓ extract_quality_level with validation fallback")


def test_extract_quality_level_none():
    """Test extracting quality level when nothing available."""
    quality = extract_quality_level(None, completeness=None)
    assert quality == "INSUFICIENTE", f"Expected INSUFICIENTE for None, got {quality}"
    print("✓ extract_quality_level with None inputs")


def run_all_tests():
    """Run all Phase 3 tests."""
    print("\n=== Phase 3 Scoring Tests (EvidenceNexus) ===\n")
    
    try:
        test_extract_score_from_nexus_with_overall_confidence()
        test_extract_score_from_nexus_fallback_validation()
        test_extract_score_from_nexus_fallback_confidence_mean()
        test_map_completeness_to_quality_complete()
        test_map_completeness_to_quality_partial()
        test_map_completeness_to_quality_insufficient()
        test_map_completeness_to_quality_not_applicable()
        test_extract_quality_level_with_completeness()
        test_extract_quality_level_fallback_validation()
        test_extract_quality_level_none()
        
        print("\n✅ All Phase 3 tests passed! (EvidenceNexus architecture validated)\n")
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
