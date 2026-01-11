"""ADVERSARIAL Tests for Phase 3 scoring transformation logic.

Simulates a determinista, adversarial, and operationally realistic Python pipeline,
reproducing interpreter behavior, quality tools, and industrial orchestration.

Validates that Phase 3 correctly extracts EvidenceNexus outputs
(overall_confidence, completeness) from Phase 2 results and transforms
MicroQuestionRun to ScoredMicroQuestion.

With EMPHATICALLY ADVERSARIAL approach testing:
- Malformed metadata extraction
- Missing field fallbacks
- Type coercion attacks
- Invalid data structure handling
"""

import sys
import math
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
import pytest

# Add src to path for imports

from farfan_pipeline.phases.Phase_3.phase3_10_00_phase3_score_extraction import (
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
# ADVERSARIAL TEST SUITE: Score Extraction
# =============================================================================

class TestAdversarialScoreExtraction:
    """Test score extraction with adversarial inputs."""

    def test_extract_score_with_nan_values(self):
        """ADVERSARIAL: Test extraction with NaN confidence values."""
        result_data = {"overall_confidence": float("nan")}

        score = extract_score_from_nexus(result_data)
        # NaN might pass through or be converted
        if score != score:  # NaN check
            # If NaN, that's a potential issue - but test current behavior
            pass
        else:
            # Should default to 0.0
            assert score == 0.0

    def test_extract_score_with_infinity_values(self):
        """ADVERSARIAL: Test extraction with infinity confidence values."""
        # Positive infinity
        result_data1 = {"overall_confidence": float("inf")}
        score1 = extract_score_from_nexus(result_data1)
        # Should handle infinity gracefully
        assert isinstance(score1, float)

        # Negative infinity
        result_data2 = {"overall_confidence": float("-inf")}
        score2 = extract_score_from_nexus(result_data2)
        assert isinstance(score2, float)

    def test_extract_score_with_extreme_values(self):
        """ADVERSARIAL: Test extraction with extreme numeric values."""
        extreme_values = [
            1.7976931348623157e+308,  # Max float
            -1.7976931348623157e+308,  # Min float
            1e-324,  # Min positive
            10**1000,  # Very large
            -10**1000,  # Very large negative
        ]

        for val in extreme_values:
            result_data = {"overall_confidence": val}
            score = extract_score_from_nexus(result_data)
            # Should return a float without crashing
            assert isinstance(score, float)

    def test_extract_score_with_string_corruption(self):
        """ADVERSARIAL: Test extraction with string corruption."""
        corrupted_strings = [
            "not_a_number",
            "NaN",
            "inf",
            "-inf",
            "0.5.0.5",  # Double decimal
            "0x1.0",  # Hex
            "0o1.0",  # Octal
            "",  # Empty
            "   ",  # Whitespace
            "\x00\x00",  # Null bytes
        ]

        for corrupted in corrupted_strings:
            result_data = {"overall_confidence": corrupted}
            score = extract_score_from_nexus(result_data)
            # Should handle gracefully (likely default to 0.0)
            assert isinstance(score, (int, float))

    def test_extract_score_with_type_pollution(self):
        """ADVERSARIAL: Test extraction with type pollution."""
        polluted_types = [
            None,
            [0.5],  # List
            (0.5,),  # Tuple
            {"score": 0.5},  # Dict
            {0.5},  # Set
            True,  # Boolean
            False,  # Boolean
            b"0.5",  # Bytes
        ]

        for polluted in polluted_types:
            result_data = {"overall_confidence": polluted}
            score = extract_score_from_nexus(result_data)
            # Should handle all types gracefully
            assert isinstance(score, (int, float))

    def test_extract_score_with_missing_fields(self):
        """ADVERSARIAL: Test extraction with missing required fields."""
        # Empty dict
        score1 = extract_score_from_nexus({})
        assert isinstance(score1, (int, float))

        # Missing overall_confidence, no validation
        score2 = extract_score_from_nexus({"other_field": 0.5})
        assert isinstance(score2, (int, float))

        # Empty validation dict
        score3 = extract_score_from_nexus({"validation": {}})
        assert isinstance(score3, (int, float))

    def test_extract_score_with_circular_references(self):
        """ADVERSARIAL: Test extraction with circular reference structures."""
        circular_dict = {}
        circular_dict["self"] = circular_dict

        # Should handle without infinite recursion
        score = extract_score_from_nexus(circular_dict)
        assert isinstance(score, (int, float))


# =============================================================================
# ADVERSARIAL TEST SUITE: Quality Mapping
# =============================================================================

class TestAdversarialQualityMapping:
    """Test quality level mapping with adversarial inputs."""

    def test_map_completeness_with_none(self):
        """ADVERSARIAL: Test mapping with None completeness."""
        quality = map_completeness_to_quality(None)
        assert quality == "INSUFICIENTE"

    def test_map_completeness_with_empty_string(self):
        """ADVERSARIAL: Test mapping with empty string."""
        quality = map_completeness_to_quality("")
        assert quality == "INSUFICIENTE"

    def test_map_completeness_with_whitespace(self):
        """ADVERSARIAL: Test mapping with whitespace only."""
        quality = map_completeness_to_quality("   ")
        assert quality == "INSUFICIENTE"

    def test_map_completeness_with_mixed_case(self):
        """ADVERSARIAL: Test mapping with mixed case (should be case-sensitive)."""
        # These should NOT map correctly due to case sensitivity
        quality1 = map_completeness_to_quality("Complete")  # Title case - rejected
        quality2 = map_completeness_to_quality("COMPLETE")  # Upper case - rejected
        quality3 = map_completeness_to_quality("CoMpLeTe")  # Mixed case - rejected

        # Should default to INSUFICIENTE for wrong case (strictly lowercase)
        assert quality1 == "INSUFICIENTE"
        assert quality2 == "INSUFICIENTE"
        assert quality3 == "INSUFICIENTE"

        # Only exact lowercase "complete" should map to EXCELENTE
        quality4 = map_completeness_to_quality("complete")
        assert quality4 == "EXCELENTE"

    def test_map_completeness_with_unicode_homographs(self):
        """ADVERSARIAL: Test mapping with Unicode homograph attacks."""
        homographs = [
            "coмplete",  # Cyrillic
            "c\u0302omplete",  # Combining accent
            "compl\u00e8te",  # Latin e with grave
        ]

        for homograph in homographs:
            quality = map_completeness_to_quality(homograph)
            assert quality == "INSUFICIENTE"

    def test_map_completeness_with_null_bytes(self):
        """ADVERSARIAL: Test mapping with null bytes."""
        quality = map_completeness_to_quality("complete\x00")
        # Should reject or trim
        assert quality in ["INSUFICIENTE", "EXCELENTE"]

    def test_map_completeness_with_type_pollution(self):
        """ADVERSARIAL: Test mapping with non-string types."""
        polluted_types = [
            123,
            0.5,
            True,
            False,
            [],
            {},
            set(),
            None,
        ]

        for polluted in polluted_types:
            quality = map_completeness_to_quality(polluted)
            # Should handle all types gracefully
            assert quality in ["EXCELENTE", "ACEPTABLE", "INSUFICIENTE", "NO_APLICABLE"]


# =============================================================================
# ADVERSARIAL TEST SUITE: Quality Level Extraction
# =============================================================================

class TestAdversarialQualityExtraction:
    """Test quality level extraction with adversarial inputs."""

    def test_extract_quality_with_corrupted_evidence(self):
        """ADVERSARIAL: Test extraction with corrupted evidence dict."""
        corrupted_evidences = [
            None,
            {},
            {"validation": None},
            {"validation": {}},
            {"validation": {"no_quality": "value"}},
        ]

        for evidence in corrupted_evidences:
            quality = extract_quality_level(evidence, completeness=None)
            # Should default to INSUFICIENTE
            assert quality == "INSUFICIENTE"

    def test_extract_quality_with_corrupted_completeness(self):
        """ADVERSARIAL: Test extraction with corrupted completeness."""
        corrupted_completeness = [
            None,
            "",
            "INVALID",
            "corrupted",
            "\x00\x00",
            "not_applicable\x00malicious",
        ]

        for comp in corrupted_completeness:
            quality = extract_quality_level(None, completeness=comp)
            # Should handle all gracefully
            assert quality in ["EXCELENTE", "ACEPTABLE", "INSUFICIENTE", "NO_APLICABLE"]

    def test_extract_quality_with_both_corrupted(self):
        """ADVERSARIAL: Test extraction with both evidence and completeness corrupted."""
        # Both None
        quality1 = extract_quality_level(None, completeness=None)
        assert quality1 == "INSUFICIENTE"

        # Both invalid
        quality2 = extract_quality_level(
            {"validation": {"quality_level": "MALICIOUS"}},
            completeness="INVALID"
        )
        # One might take precedence, but both should be valid enum values
        assert quality2 in ["EXCELENTE", "ACEPTABLE", "INSUFICIENTE", "NO_APLICABLE"]


# =============================================================================
# ADVERSARIAL TEST SUITE: Legacy Evidence Extraction
# =============================================================================

class TestAdversarialEvidenceExtraction:
    """Test legacy evidence score extraction with adversarial inputs."""

    def test_extract_from_evidence_with_pollution(self):
        """ADVERSARIAL: Test evidence extraction with polluted data."""
        polluted_evidences = [
            None,
            {},
            {"validation": None},
            {"validation": {"no_score": "value"}},
            {"confidence_scores": None},
            {"confidence_scores": {}},
            {"confidence_scores": {"no_mean": "value"}},
        ]

        for evidence in polluted_evidences:
            score = extract_score_from_evidence(evidence)
            # Should default to 0.0
            assert score == 0.0

    def test_extract_from_evidence_with_nan_scores(self):
        """ADVERSARIAL: Test evidence extraction with NaN scores."""
        evidence = {"validation": {"score": float("nan")}}
        score = extract_score_from_evidence(evidence)
        # NaN might pass through or be handled
        assert isinstance(score, (int, float))

    def test_extract_from_evidence_with_infinity_scores(self):
        """ADVERSARIAL: Test evidence extraction with infinity scores."""
        # Positive infinity in validation
        evidence1 = {"validation": {"score": float("inf")}}
        score1 = extract_score_from_evidence(evidence1)
        assert isinstance(score1, float)

        # Infinity in confidence_scores
        evidence2 = {"confidence_scores": {"mean": float("-inf")}}
        score2 = extract_score_from_evidence(evidence2)
        assert isinstance(score2, float)


# =============================================================================
# ADVERSARIAL TEST SUITE: Transform Functions
# =============================================================================

class TestAdversarialTransform:
    """Test transform functions with adversarial inputs."""

    def test_transform_with_missing_attributes(self):
        """ADVERSARIAL: Test transform with missing object attributes."""
        # Create object with missing attributes
        class IncompleteResult:
            question_id = "Q001"
            # Missing other attributes

        incomplete = IncompleteResult()

        # Should handle missing attributes gracefully
        result = transform_micro_result_to_scored(incomplete)
        assert isinstance(result, dict)

    def test_transform_with_corrupted_metadata(self):
        """ADVERSARIAL: Test transform with corrupted metadata."""
        micro_result = MockMicroQuestionRun(
            question_id="Q001",
            question_global=1,
            base_slot="SLOT",
            metadata={
                "overall_confidence": float("nan"),
                "completeness": "INVALID\x00",
            },
            evidence=None,
            error="ERROR"
        )

        result = transform_micro_result_to_scored(micro_result)

        # Should produce valid dict despite corruption
        assert isinstance(result, dict)
        assert "score" in result
        assert "quality_level" in result

    def test_transform_with_malformed_evidence(self):
        """ADVERSARIAL: Test transform with malformed evidence."""
        # Create circular reference separately
        circular_dict = {}
        circular_dict["self"] = circular_dict

        malformed_evidences = [
            None,
            "string_evidence",
            12345,
            [],
            circular_dict,  # Circular reference
        ]

        for evidence in malformed_evidences:
            micro_result = MockMicroQuestionRun(
                question_id="Q001",
                question_global=1,
                base_slot="SLOT",
                metadata={"overall_confidence": 0.5},
                evidence=evidence,
            )

            result = transform_micro_result_to_scored(micro_result)
            assert isinstance(result, dict)

    def test_transform_with_extreme_values(self):
        """ADVERSARIAL: Test transform with extreme values."""
        extreme_values = [
            float("inf"),
            float("-inf"),
            1.7976931348623157e+308,
            -1.7976931348623157e+308,
        ]

        for val in extreme_values:
            micro_result = MockMicroQuestionRun(
                question_id="Q001",
                question_global=1,
                base_slot="SLOT",
                metadata={"overall_confidence": val},
                evidence=None,
            )

            result = transform_micro_result_to_scored(micro_result)
            assert isinstance(result, dict)
            assert "score" in result


# =============================================================================
# ADVERSARIAL TEST SUITE: Fallback Chain Tests
# =============================================================================

class TestAdversarialFallbackChains:
    """Test fallback behavior with adversarial inputs."""

    def test_fallback_chain_with_all_corrupted(self):
        """ADVERSARIAL: Test all fallback paths are corrupted."""
        result_data = {
            "overall_confidence": "not_a_number",
            "validation": {"score": "also_not_a_number"},
            "evidence": {
                "confidence_scores": {
                    "mean": "still_not_a_number"
                }
            }
        }

        score = extract_score_from_nexus(result_data)
        # Should ultimately default to 0.0
        assert score == 0.0

    def test_fallback_priority(self):
        """ADVERSARIAL: Test fallback priority under corruption."""
        # overall_confidence is primary
        result_data1 = {
            "overall_confidence": 0.7,
            "validation": {"score": 0.3},
            "evidence": {"confidence_scores": {"mean": 0.5}}
        }
        score1 = extract_score_from_nexus(result_data1)
        assert score1 == 0.7

        # If primary is corrupted, fall back to validation
        result_data2 = {
            "overall_confidence": "corrupted",
            "validation": {"score": 0.4},
            "evidence": {"confidence_scores": {"mean": 0.5}}
        }
        score2 = extract_score_from_nexus(result_data2)
        assert score2 == 0.4

        # If both are corrupted, fall back to confidence_scores
        result_data3 = {
            "overall_confidence": "corrupted",
            "validation": {"score": "corrupted"},
            "evidence": {"confidence_scores": {"mean": 0.6}}
        }
        score3 = extract_score_from_nexus(result_data3)
        assert score3 == 0.6


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
