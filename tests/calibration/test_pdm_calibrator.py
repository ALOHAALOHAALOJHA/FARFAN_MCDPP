"""
TESTS FOR PHASE 1 PDM CALIBRATOR
================================

Tests for Phase1PDMCalibrator - the calibration system for Phase 1
that makes methods sensitive to Colombian municipal development plans (PDM).

CALIBRATION CONSTRAINTS:
- Does NOT alter constitutional structure (60 chunks)
- Does NOT redefine hierarchy (PDMStructuralProfile responsibility)
- ONLY adjusts heuristic parameters in calibrable subphases
- MUST improve metrics (precision, recall, F1) vs baseline

Version: PDM-2025.1
"""

from __future__ import annotations

import pytest
from pathlib import Path

from farfan_pipeline.calibration import Phase1PDMCalibrator
from farfan_pipeline.pdm.profile import (
    PDMStructuralProfile,
    get_default_profile,
)
# DELETED_MODULE: from farfan_pipeline.calibration.pdm_calibrator import (
    CALIBRABLE_SUBPHASES,
    NON_CALIBRABLE_SUBPHASES,
    GoldAnnotation,
    CalibrationCorpus,
    CalibrationMetrics,
    CalibrationResult,
    CalibrationError,
)


# =============================================================================
# SUBPHASE CLASSIFICATION TESTS
# =============================================================================


class TestSubphaseClassification:
    """Tests for calibrable vs non-calibrable subphase classification."""

    def test_calibrable_subphases_defined(self) -> None:
        """Calibrable subphases should be defined."""
        assert "SP5" in CALIBRABLE_SUBPHASES  # Causal Extraction
        assert "SP7" in CALIBRABLE_SUBPHASES  # Discourse Analysis
        assert "SP9" in CALIBRABLE_SUBPHASES  # Causal Integration
        assert "SP10" in CALIBRABLE_SUBPHASES  # Strategic Integration
        assert "SP12" in CALIBRABLE_SUBPHASES  # SISAS Irrigation
        assert "SP14" in CALIBRABLE_SUBPHASES  # Quality Metrics

    def test_non_calibrable_subphases_defined(self) -> None:
        """Non-calibrable (constitutional) subphases should be defined."""
        assert "SP0" in NON_CALIBRABLE_SUBPHASES  # Language Detection
        assert "SP2" in NON_CALIBRABLE_SUBPHASES  # Structural Analysis
        assert "SP4" in NON_CALIBRABLE_SUBPHASES  # PA×Dim Grid (60-chunk invariant)
        assert "SP13" in NON_CALIBRABLE_SUBPHASES  # Validation (integrity gate)

    def test_subphases_are_disjoint(self) -> None:
        """Calibrable and non-calibrable sets must be disjoint."""
        calibrable_keys = set(CALIBRABLE_SUBPHASES.keys())
        non_calibrable_keys = set(NON_CALIBRABLE_SUBPHASES.keys())
        overlap = calibrable_keys & non_calibrable_keys
        assert len(overlap) == 0, f"Subphases in both sets: {overlap}"


# =============================================================================
# GOLD ANNOTATION TESTS
# =============================================================================


class TestGoldAnnotation:
    """Tests for GoldAnnotation data structure."""

    def test_gold_annotation_creation(self) -> None:
        """GoldAnnotation should construct with required fields."""
        annotation = GoldAnnotation(
            document_id="PDM-001",
            hierarchy_labels={1: "H1", 10: "H2", 50: "H3"},
            section_boundaries={"Diagnóstico": (1, 100)},
            causal_dimension_spans=[(10, 50, "D4_OUTPUT")],
            semantic_units=[(60, 80, "META")],
        )
        assert annotation.document_id == "PDM-001"
        assert len(annotation.hierarchy_labels) == 3

    def test_gold_annotation_validation_passes(self) -> None:
        """Complete annotation should pass validation."""
        annotation = GoldAnnotation(
            document_id="PDM-001",
            hierarchy_labels={1: "H1"},
            section_boundaries={"Diagnóstico": (1, 100)},
            causal_dimension_spans=[(10, 50, "D4_OUTPUT")],
        )
        assert annotation.validate()

    def test_gold_annotation_validation_fails_empty(self) -> None:
        """Empty annotation should fail validation."""
        annotation = GoldAnnotation(document_id="PDM-001")
        assert not annotation.validate()


# =============================================================================
# CALIBRATION CORPUS TESTS
# =============================================================================


class TestCalibrationCorpus:
    """Tests for CalibrationCorpus data structure."""

    def test_corpus_requires_minimum_documents(self) -> None:
        """Corpus must have ≥10 PDM documents."""
        # Less than 10 documents should fail validation
        corpus = CalibrationCorpus(
            pdm_documents=[Path(f"doc{i}.pdf") for i in range(5)],
            profile=get_default_profile(),
        )
        assert not corpus.validate()

    def test_corpus_requires_profile(self) -> None:
        """Corpus without profile should fail validation."""
        corpus = CalibrationCorpus(
            pdm_documents=[Path(f"doc{i}.pdf") for i in range(15)],
            profile=None,
        )
        assert not corpus.validate()


# =============================================================================
# CALIBRATION METRICS TESTS
# =============================================================================


class TestCalibrationMetrics:
    """Tests for CalibrationMetrics data structure."""

    def test_metrics_comparison(self) -> None:
        """is_better_than should compare F1 scores."""
        metrics1 = CalibrationMetrics(precision=0.8, recall=0.7, f1_score=0.75)
        metrics2 = CalibrationMetrics(precision=0.85, recall=0.75, f1_score=0.80)
        
        assert metrics2.is_better_than(metrics1)
        assert not metrics1.is_better_than(metrics2)

    def test_equal_f1_not_better(self) -> None:
        """Equal F1 scores: neither is better."""
        metrics1 = CalibrationMetrics(f1_score=0.75)
        metrics2 = CalibrationMetrics(f1_score=0.75)
        
        assert not metrics1.is_better_than(metrics2)
        assert not metrics2.is_better_than(metrics1)


# =============================================================================
# CALIBRATION RESULT TESTS
# =============================================================================


class TestCalibrationResult:
    """Tests for CalibrationResult data structure."""

    def test_result_is_improvement(self) -> None:
        """Result with improved F1 should be flagged as improvement."""
        result = CalibrationResult(
            subphase="SP5",
            optimized_parameters={"threshold": 0.65},
            metrics_before=CalibrationMetrics(f1_score=0.70),
            metrics_after=CalibrationMetrics(f1_score=0.80),
            error_reduction={"ERR-01": 50.0},
        )
        assert result.is_improvement()

    def test_result_is_not_improvement_degraded(self) -> None:
        """Result with degraded F1 should NOT be flagged as improvement."""
        result = CalibrationResult(
            subphase="SP5",
            optimized_parameters={"threshold": 0.65},
            metrics_before=CalibrationMetrics(f1_score=0.80),
            metrics_after=CalibrationMetrics(f1_score=0.70),  # WORSE
            error_reduction={"ERR-01": 50.0},
        )
        assert not result.is_improvement()

    def test_result_is_not_improvement_negative_error_reduction(self) -> None:
        """Negative error reduction (errors increased) should NOT be improvement."""
        result = CalibrationResult(
            subphase="SP5",
            optimized_parameters={"threshold": 0.65},
            metrics_before=CalibrationMetrics(f1_score=0.70),
            metrics_after=CalibrationMetrics(f1_score=0.75),
            error_reduction={"ERR-01": -10.0},  # Errors increased!
        )
        assert not result.is_improvement()

    def test_result_summary(self) -> None:
        """get_summary should return structured summary."""
        result = CalibrationResult(
            subphase="SP5",
            optimized_parameters={"threshold": 0.65},
            metrics_before=CalibrationMetrics(precision=0.75, recall=0.70, f1_score=0.725),
            metrics_after=CalibrationMetrics(precision=0.85, recall=0.80, f1_score=0.825),
            error_reduction={"ERR-01": 50.0},
        )
        summary = result.get_summary()
        
        assert summary["subphase"] == "SP5"
        assert summary["f1_improvement"] == pytest.approx(0.1)
        assert "precision_before" in summary
        assert "precision_after" in summary


# =============================================================================
# PHASE 1 PDM CALIBRATOR TESTS
# =============================================================================


class TestPhase1PDMCalibrator:
    """Tests for Phase1PDMCalibrator."""

    @pytest.fixture
    def profile(self) -> PDMStructuralProfile:
        """Get default PDM profile."""
        return get_default_profile()

    @pytest.fixture
    def calibrator(self, profile: PDMStructuralProfile) -> Phase1PDMCalibrator:
        """Create calibrator with default profile."""
        return Phase1PDMCalibrator(profile)

    def test_calibrator_construction(self, calibrator: Phase1PDMCalibrator) -> None:
        """Calibrator should construct with profile."""
        assert calibrator.profile is not None
        assert len(calibrator.calibration_history) == 0

    def test_fit_rejects_invalid_corpus(self, calibrator: Phase1PDMCalibrator) -> None:
        """fit() should reject invalid corpus."""
        invalid_corpus = CalibrationCorpus(
            pdm_documents=[Path("doc1.pdf")],  # Only 1 document (need ≥10)
            profile=calibrator.profile,
        )
        with pytest.raises(ValueError, match="≥10"):
            calibrator.fit(invalid_corpus)

    def test_fit_rejects_non_calibrable_subphases(
        self, calibrator: Phase1PDMCalibrator, profile: PDMStructuralProfile
    ) -> None:
        """fit() should reject non-calibrable subphases."""
        # Create minimally valid corpus structure
        corpus = CalibrationCorpus(
            pdm_documents=[Path(f"doc{i}.pdf") for i in range(15)],
            gold_annotations={
                f"doc{i}.pdf": GoldAnnotation(
                    document_id=f"doc{i}.pdf",
                    hierarchy_labels={1: "H1"},
                    section_boundaries={"Diagnóstico": (1, 100)},
                    causal_dimension_spans=[(10, 50, "D4_OUTPUT")],
                )
                for i in range(15)
            },
            profile=profile,
        )
        
        # Try to calibrate non-calibrable subphase
        with pytest.raises(ValueError, match="[Cc]annot calibrate"):
            calibrator.fit(corpus, target_subphases={"SP4"})  # SP4 is constitutional


# =============================================================================
# CALIBRATION INVARIANT TESTS
# =============================================================================


class TestCalibrationInvariants:
    """Tests for calibration invariants."""

    def test_60_chunk_invariant_not_altered(self) -> None:
        """Calibration must NOT alter the 60-chunk constitutional invariant."""
        # This is a design constraint test - verify documentation
        # SP4 (PA×Dim Grid) is NON-CALIBRABLE
        assert "SP4" in NON_CALIBRABLE_SUBPHASES
        assert "PA×Dim Grid" in NON_CALIBRABLE_SUBPHASES["SP4"] or \
               "Grid" in NON_CALIBRABLE_SUBPHASES["SP4"]

    def test_hierarchy_not_redefined(self) -> None:
        """Calibration must NOT redefine hierarchy (PDMStructuralProfile responsibility)."""
        # SP2 (Structural Analysis) is NON-CALIBRABLE
        assert "SP2" in NON_CALIBRABLE_SUBPHASES
