"""
Unit Tests for Calibration Types
================================

Tests for CalibrationSubject, CalibrationEvidenceContext, CalibrationResult,
LayerId, and ROLE_LAYER_REQUIREMENTS.

Verification Strategy:
    - Property-based tests via Hypothesis for invariant coverage
    - Edge case tests for boundary conditions
    - Serialization round-trip tests
"""

from __future__ import annotations

import pytest

from farfan_pipeline.orchestration.calibration_types import (
    CalibrationSubject,
    CalibrationEvidenceContext,
    CalibrationResult,
    LayerId,
    ROLE_LAYER_REQUIREMENTS,
    VALID_ROLES,
)


# =============================================================================
# CALIBRATION SUBJECT TESTS
# =============================================================================


class TestCalibrationSubject:
    """Tests for CalibrationSubject invariants."""

    def test_valid_construction(self) -> None:
        """SC-001: Valid CalibrationSubject can be constructed."""
        subject = CalibrationSubject(
            method_id="farfan_pipeline.executors.D1Q1",
            role="SCORE_Q",
            context={"question_id": "Q001"},
        )
        assert subject.method_id == "farfan_pipeline.executors.D1Q1"
        assert subject.role == "SCORE_Q"
        assert subject.context.get("question_id") == "Q001"

    def test_empty_method_id_rejected(self) -> None:
        """INV-CS-001: method_id cannot be empty."""
        with pytest.raises(ValueError, match="method_id cannot be empty"):
            CalibrationSubject(method_id="", role="SCORE_Q")

    def test_whitespace_method_id_rejected(self) -> None:
        """INV-CS-001: method_id cannot be whitespace-only."""
        with pytest.raises(ValueError, match="method_id cannot be empty"):
            CalibrationSubject(method_id="   ", role="SCORE_Q")

    def test_invalid_role_rejected(self) -> None:
        """INV-CS-002: Invalid role is rejected."""
        with pytest.raises(ValueError, match="role must be one of"):
            CalibrationSubject(method_id="test", role="INVALID_ROLE")

    def test_all_valid_roles_accepted(self) -> None:
        """All roles in VALID_ROLES are accepted."""
        for role in VALID_ROLES:
            subject = CalibrationSubject(method_id="test.method", role=role)
            assert subject.role == role

    def test_context_is_immutable(self) -> None:
        """INV-CS-003: context is converted to MappingProxyType."""
        subject = CalibrationSubject(
            method_id="test.method",
            role="SCORE_Q",
            context={"key": "value"},
        )
        # MappingProxyType doesn't allow item assignment
        with pytest.raises(TypeError):
            subject.context["new_key"] = "new_value"  # type: ignore

    def test_get_active_layers_for_score_q(self) -> None:
        """SCORE_Q role activates all 8 layers."""
        subject = CalibrationSubject(
            method_id="test.method",
            role="SCORE_Q",
        )
        active = subject.get_active_layers()
        assert len(active) == 8
        assert LayerId.QUESTION in active
        assert LayerId.DIMENSION in active
        assert LayerId.POLICY in active

    def test_get_active_layers_for_ingest_pdm(self) -> None:
        """INGEST_PDM role activates 4 layers."""
        subject = CalibrationSubject(
            method_id="test.method",
            role="INGEST_PDM",
        )
        active = subject.get_active_layers()
        assert len(active) == 4
        assert LayerId.BASE in active
        assert LayerId.CHAIN in active
        assert LayerId.UNIT in active
        assert LayerId.META in active


# =============================================================================
# CALIBRATION EVIDENCE CONTEXT TESTS
# =============================================================================


class TestCalibrationEvidenceContext:
    """Tests for CalibrationEvidenceContext invariants."""

    def test_valid_construction(self) -> None:
        """Valid CalibrationEvidenceContext can be constructed."""
        ctx = CalibrationEvidenceContext(
            chunk_count=60,
            completeness=0.85,
            structure_quality=0.90,
            document_quality=0.88,
            question_id="Q001",
            dimension_id="D1",
            policy_area_id="PA01",
        )
        assert ctx.chunk_count == 60
        assert ctx.completeness == 0.85
        assert ctx.question_id == "Q001"

    def test_completeness_bounds_lower(self) -> None:
        """INV-CEC-001: completeness must be >= 0.0."""
        with pytest.raises(ValueError, match="completeness must be in"):
            CalibrationEvidenceContext(
                chunk_count=60,
                completeness=-0.1,
                structure_quality=0.5,
                document_quality=0.5,
            )

    def test_completeness_bounds_upper(self) -> None:
        """INV-CEC-001: completeness must be <= 1.0."""
        with pytest.raises(ValueError, match="completeness must be in"):
            CalibrationEvidenceContext(
                chunk_count=60,
                completeness=1.5,
                structure_quality=0.5,
                document_quality=0.5,
            )

    def test_structure_quality_bounds(self) -> None:
        """INV-CEC-002: structure_quality must be in [0.0, 1.0]."""
        with pytest.raises(ValueError, match="structure_quality must be in"):
            CalibrationEvidenceContext(
                chunk_count=60,
                completeness=0.5,
                structure_quality=1.1,
                document_quality=0.5,
            )

    def test_document_quality_bounds(self) -> None:
        """INV-CEC-003: document_quality must be in [0.0, 1.0]."""
        with pytest.raises(ValueError, match="document_quality must be in"):
            CalibrationEvidenceContext(
                chunk_count=60,
                completeness=0.5,
                structure_quality=0.5,
                document_quality=-0.01,
            )

    def test_chunk_count_negative_rejected(self) -> None:
        """chunk_count must be non-negative."""
        with pytest.raises(ValueError, match="chunk_count must be non-negative"):
            CalibrationEvidenceContext(
                chunk_count=-1,
                completeness=0.5,
                structure_quality=0.5,
                document_quality=0.5,
            )

    def test_boundary_values_accepted(self) -> None:
        """Boundary values 0.0 and 1.0 are accepted."""
        ctx = CalibrationEvidenceContext(
            chunk_count=0,
            completeness=0.0,
            structure_quality=1.0,
            document_quality=0.0,
        )
        assert ctx.completeness == 0.0
        assert ctx.structure_quality == 1.0

    def test_to_dict_serialization(self) -> None:
        """to_dict produces correct dictionary."""
        ctx = CalibrationEvidenceContext(
            chunk_count=60,
            completeness=0.85,
            structure_quality=0.90,
            document_quality=0.88,
            question_id="Q001",
        )
        d = ctx.to_dict()
        assert d["chunk_count"] == 60
        assert d["completeness"] == 0.85
        assert d["question_id"] == "Q001"
        assert d["dimension_id"] is None


# =============================================================================
# CALIBRATION RESULT TESTS
# =============================================================================


class TestCalibrationResult:
    """Tests for CalibrationResult invariants."""

    def test_valid_construction(self) -> None:
        """Valid CalibrationResult can be constructed."""
        result = CalibrationResult(
            method_id="test.method",
            role="SCORE_Q",
            final_score=0.85,
            layer_scores={LayerId.BASE: 0.9, LayerId.QUESTION: 0.8},
            active_layers=(LayerId.BASE, LayerId.QUESTION),
        )
        assert result.method_id == "test.method"
        assert result.final_score == 0.85
        assert len(result.active_layers) == 2

    def test_final_score_bounds_lower(self) -> None:
        """INV-CR-001: final_score must be >= 0.0."""
        with pytest.raises(ValueError, match="final_score must be in"):
            CalibrationResult(
                method_id="test",
                role="SCORE_Q",
                final_score=-0.1,
                layer_scores={LayerId.BASE: 0.5},
                active_layers=(LayerId.BASE,),
            )

    def test_final_score_bounds_upper(self) -> None:
        """INV-CR-001: final_score must be <= 1.0."""
        with pytest.raises(ValueError, match="final_score must be in"):
            CalibrationResult(
                method_id="test",
                role="SCORE_Q",
                final_score=1.5,
                layer_scores={LayerId.BASE: 0.5},
                active_layers=(LayerId.BASE,),
            )

    def test_layer_score_bounds(self) -> None:
        """INV-CR-002: All layer_scores must be in [0.0, 1.0]."""
        with pytest.raises(ValueError, match="layer_scores"):
            CalibrationResult(
                method_id="test",
                role="SCORE_Q",
                final_score=0.8,
                layer_scores={LayerId.BASE: 1.5},
                active_layers=(LayerId.BASE,),
            )

    def test_empty_active_layers_rejected(self) -> None:
        """INV-CR-003: active_layers cannot be empty."""
        with pytest.raises(ValueError, match="active_layers cannot be empty"):
            CalibrationResult(
                method_id="test",
                role="SCORE_Q",
                final_score=0.8,
                layer_scores={},
                active_layers=(),
            )

    def test_to_dict_serialization(self) -> None:
        """to_dict produces correct dictionary."""
        result = CalibrationResult(
            method_id="test.method",
            role="SCORE_Q",
            final_score=0.85,
            layer_scores={LayerId.BASE: 0.9, LayerId.QUESTION: 0.8},
            active_layers=(LayerId.BASE, LayerId.QUESTION),
            metadata={"key": "value"},
        )
        d = result.to_dict()
        assert d["method_id"] == "test.method"
        assert d["final_score"] == 0.85
        assert d["layer_scores"]["@b"] == 0.9
        assert d["layer_scores"]["@q"] == 0.8
        assert "@b" in d["active_layers"]
        assert d["metadata"]["key"] == "value"

    def test_get_layer_score(self) -> None:
        """get_layer_score returns correct score or None."""
        result = CalibrationResult(
            method_id="test",
            role="SCORE_Q",
            final_score=0.8,
            layer_scores={LayerId.BASE: 0.9},
            active_layers=(LayerId.BASE,),
        )
        assert result.get_layer_score(LayerId.BASE) == 0.9
        assert result.get_layer_score(LayerId.QUESTION) is None

    def test_is_layer_active(self) -> None:
        """is_layer_active returns correct boolean."""
        result = CalibrationResult(
            method_id="test",
            role="SCORE_Q",
            final_score=0.8,
            layer_scores={LayerId.BASE: 0.9},
            active_layers=(LayerId.BASE,),
        )
        assert result.is_layer_active(LayerId.BASE) is True
        assert result.is_layer_active(LayerId.QUESTION) is False


# =============================================================================
# LAYER ID AND ROLE-LAYER REQUIREMENTS TESTS
# =============================================================================


class TestLayerId:
    """Tests for LayerId enumeration."""

    def test_all_layers_have_values(self) -> None:
        """All 8 layers have string values."""
        assert LayerId.BASE.value == "@b"
        assert LayerId.CHAIN.value == "@chain"
        assert LayerId.UNIT.value == "@u"
        assert LayerId.QUESTION.value == "@q"
        assert LayerId.DIMENSION.value == "@d"
        assert LayerId.POLICY.value == "@p"
        assert LayerId.CONGRUENCE.value == "@C"
        assert LayerId.META.value == "@m"

    def test_layer_count(self) -> None:
        """There are exactly 8 layers."""
        assert len(LayerId) == 8


class TestRoleLayerRequirements:
    """Tests for ROLE_LAYER_REQUIREMENTS mapping."""

    def test_all_roles_present(self) -> None:
        """All 8 roles are in the mapping."""
        expected_roles = {
            "INGEST_PDM",
            "STRUCTURE",
            "EXTRACT",
            "SCORE_Q",
            "AGGREGATE",
            "REPORT",
            "META_TOOL",
            "TRANSFORM",
        }
        assert set(ROLE_LAYER_REQUIREMENTS.keys()) == expected_roles

    def test_score_q_has_all_layers(self) -> None:
        """SCORE_Q activates all 8 layers."""
        layers = ROLE_LAYER_REQUIREMENTS["SCORE_Q"]
        assert len(layers) == 8
        assert all(isinstance(layer, LayerId) for layer in layers)

    def test_meta_tool_minimal_layers(self) -> None:
        """META_TOOL has minimal layer set."""
        layers = ROLE_LAYER_REQUIREMENTS["META_TOOL"]
        assert LayerId.BASE in layers
        assert LayerId.CHAIN in layers
        assert LayerId.META in layers
        assert len(layers) == 3

    def test_valid_roles_matches_mapping(self) -> None:
        """VALID_ROLES matches ROLE_LAYER_REQUIREMENTS keys."""
        assert VALID_ROLES == frozenset(ROLE_LAYER_REQUIREMENTS.keys())


# =============================================================================
# PROPERTY-BASED TESTS (if Hypothesis available)
# =============================================================================


try:
    from hypothesis import given, strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Define dummy placeholders to prevent NameError during class definition
    given = lambda *args: lambda fn: fn  # type: ignore

    class st:  # type: ignore
        @staticmethod
        def text(*args, **kwargs):
            return None

        @staticmethod
        def sampled_from(*args, **kwargs):
            return None

        @staticmethod
        def floats(*args, **kwargs):
            return None


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestCalibrationTypesPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(st.text(min_size=1), st.sampled_from(list(VALID_ROLES)))
    def test_valid_roles_always_accepted(self, method_id: str, role: str) -> None:
        """SC-002: All valid roles are accepted."""
        if method_id.strip():  # Non-empty method_id
            subject = CalibrationSubject(method_id=method_id, role=role)
            assert subject.role == role

    @given(
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
    )
    def test_valid_scores_accepted(
        self, completeness: float, structure_quality: float, document_quality: float
    ) -> None:
        """SC-002: Calibration produces valid scores in [0.0, 1.0]."""
        ctx = CalibrationEvidenceContext(
            chunk_count=60,
            completeness=completeness,
            structure_quality=structure_quality,
            document_quality=document_quality,
        )
        assert 0.0 <= ctx.completeness <= 1.0
        assert 0.0 <= ctx.structure_quality <= 1.0
        assert 0.0 <= ctx.document_quality <= 1.0

    @given(
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
    )
    def test_calibration_result_bounds(self, final_score: float, layer_score: float) -> None:
        """All CalibrationResult scores within [0.0, 1.0]."""
        result = CalibrationResult(
            method_id="test.method",
            role="SCORE_Q",
            final_score=final_score,
            layer_scores={LayerId.BASE: layer_score},
            active_layers=(LayerId.BASE,),
        )
        assert 0.0 <= result.final_score <= 1.0
        for score in result.layer_scores.values():
            assert 0.0 <= score <= 1.0
