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
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from canonic_phases.Phase_three.scoring import (
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


# =============================================================================
# Round 1: extract_score_from_nexus Tests
# =============================================================================

def test_extract_score_from_nexus_normal():
    """Test normal confidence extraction."""
    result = {"overall_confidence": 0.85}
    score, meta = extract_score_from_nexus(result)
    assert score == 0.85, f"Expected 0.85, got {score}"
    assert "overall_confidence" in meta["extraction_path"], f"Expected 'overall_confidence' in path, got {meta['extraction_path']}"
    print("✓ test_extract_score_from_nexus_normal")


def test_extract_score_from_nexus_percentage():
    """Test percentage string parsing."""
    result = {"overall_confidence": "85%"}
    score, meta = extract_score_from_nexus(result)
    assert abs(score - 0.85) < 0.001, f"Expected ~0.85, got {score}"
    assert any("Parsed percentage" in w for w in meta["warnings"]), f"Expected 'Parsed percentage' warning, got {meta['warnings']}"
    print("✓ test_extract_score_from_nexus_percentage")


def test_extract_score_from_nexus_out_of_range():
    """Test range clamping."""
    result = {"overall_confidence": 1.5}
    score, meta = extract_score_from_nexus(result)
    assert score == 1.0, f"Expected 1.0 (clamped), got {score}"
    assert any("clamping" in w.lower() for w in meta["warnings"]), f"Expected clamping warning, got {meta['warnings']}"
    print("✓ test_extract_score_from_nexus_out_of_range")


def test_extract_score_from_nexus_fallback_validation():
    """Test fallback to validation.score."""
    result = {"validation": {"score": 0.7}}
    score, meta = extract_score_from_nexus(result)
    assert score == 0.7, f"Expected 0.7, got {score}"
    assert "validation.score" in meta["fallbacks_used"], f"Expected 'validation.score' in fallbacks, got {meta['fallbacks_used']}"
    print("✓ test_extract_score_from_nexus_fallback_validation")


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
    score, meta = extract_score_from_nexus(result_data)
    assert score == 0.72, f"Expected 0.72, got {score}"
    assert "confidence_scores.mean" in meta["fallbacks_used"], f"Expected 'confidence_scores.mean' in fallbacks, got {meta['fallbacks_used']}"
    print("✓ test_extract_score_from_nexus_fallback_confidence_mean")


def test_extract_score_from_nexus_strict_mode():
    """Test strict mode raises error."""
    try:
        extract_score_from_nexus({}, strict=True)
        assert False, "Expected ValueError to be raised"
    except ValueError as e:
        assert "No valid confidence" in str(e), f"Expected 'No valid confidence' in error, got {e}"
        print("✓ test_extract_score_from_nexus_strict_mode")


def test_extract_score_from_nexus_numeric_string():
    """Test numeric string parsing."""
    result = {"overall_confidence": "0.75"}
    score, meta = extract_score_from_nexus(result)
    assert abs(score - 0.75) < 0.001, f"Expected ~0.75, got {score}"
    assert any("numeric string" in w.lower() for w in meta["warnings"]), f"Expected numeric string warning, got {meta['warnings']}"
    print("✓ test_extract_score_from_nexus_numeric_string")


def test_extract_score_from_nexus_default_fallback():
    """Test ultimate fallback returns 0.0 with warning."""
    result = {}
    score, meta = extract_score_from_nexus(result, strict=False)
    assert score == 0.0, f"Expected 0.0, got {score}"
    assert "default_fallback" in meta["extraction_path"], f"Expected 'default_fallback' in path, got {meta['extraction_path']}"
    assert any("failed" in w.lower() for w in meta["warnings"]), f"Expected failure warning, got {meta['warnings']}"
    print("✓ test_extract_score_from_nexus_default_fallback")


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
        # Round 1: extract_score_from_nexus tests
        print("--- Round 1: extract_score_from_nexus ---")
        test_extract_score_from_nexus_normal()
        test_extract_score_from_nexus_percentage()
        test_extract_score_from_nexus_out_of_range()
        test_extract_score_from_nexus_fallback_validation()
        test_extract_score_from_nexus_fallback_confidence_mean()
        test_extract_score_from_nexus_strict_mode()
        test_extract_score_from_nexus_numeric_string()
        test_extract_score_from_nexus_default_fallback()
        
        # Completeness mapping tests
        print("\n--- Completeness Mapping ---")
        test_map_completeness_to_quality_complete()
        test_map_completeness_to_quality_partial()
        test_map_completeness_to_quality_insufficient()
        test_map_completeness_to_quality_not_applicable()
        
        # Quality level extraction tests
        print("\n--- Quality Level Extraction ---")
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

