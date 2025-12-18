"""
Tests for Agent Prime Directives: Epistemic Constraints
"""

import pytest
from farfan_pipeline.agents.prime_directives import (
    EpistemicConstraints,
    StatementType,
    FalsifiableStatement,
    EpistemicViolationError,
)


class TestEpistemicConstraints:
    """Test epistemic constraint enforcement."""

    def test_no_hedging_valid_text(self) -> None:
        """Test validation passes for text without hedging terms."""
        valid_text = "The repository contains 240 methods."
        EpistemicConstraints.validate_no_hedging(valid_text)

    def test_no_hedging_detects_violations(self) -> None:
        """Test detection of hedging terms."""
        hedging_texts = [
            "This probably works",
            "It seems to be correct",
            "The result is likely accurate",
            "Maybe this is the right approach",
            "It should work fine",
        ]

        for text in hedging_texts:
            with pytest.raises(EpistemicViolationError) as exc_info:
                EpistemicConstraints.validate_no_hedging(text)
            assert "NO_HEDGING constraint violated" in str(exc_info.value)

    def test_statement_labeled_observation(self) -> None:
        """Test detection of OBSERVATION label."""
        text = "[OBSERVATION] The file exists at path /src/main.py"
        stmt_type = EpistemicConstraints.validate_statement_labeled(text)
        assert stmt_type == StatementType.OBSERVATION

    def test_statement_labeled_assumption(self) -> None:
        """Test detection of ASSUMPTION label."""
        text = "[ASSUMPTION] The user wants feature X based on context"
        stmt_type = EpistemicConstraints.validate_statement_labeled(text)
        assert stmt_type == StatementType.ASSUMPTION

    def test_statement_labeled_decision(self) -> None:
        """Test detection of DECISION label."""
        text = "[DECISION] Implement solution using approach Y"
        stmt_type = EpistemicConstraints.validate_statement_labeled(text)
        assert stmt_type == StatementType.DECISION

    def test_statement_labeled_missing_label(self) -> None:
        """Test error when statement lacks label."""
        text = "This statement has no label"
        with pytest.raises(EpistemicViolationError) as exc_info:
            EpistemicConstraints.validate_statement_labeled(text)
        assert "SEPARATION_MANDATORY constraint violated" in str(exc_info.value)

    def test_halt_insufficient_evidence(self) -> None:
        """Test halt mechanism for insufficient evidence."""
        context = "method calibration"
        required = ["test_pdts", "validation_set", "num_runs"]

        with pytest.raises(EpistemicViolationError) as exc_info:
            EpistemicConstraints.halt_insufficient_evidence(context, required)

        error_msg = str(exc_info.value)
        assert "INSUFFICIENT_EVIDENCE" in error_msg
        assert context in error_msg
        assert all(req in error_msg for req in required)

    def test_create_falsifiable_statement_valid(self) -> None:
        """Test creation of valid falsifiable statement."""
        claim = "Method X produces deterministic output"
        evidence = ["Test run 1: hash ABC", "Test run 2: hash ABC"]
        disproof = ["Test run produces different hash with same inputs"]

        stmt = EpistemicConstraints.create_falsifiable_statement(
            claim=claim,
            statement_type=StatementType.OBSERVATION,
            evidence=evidence,
            disproof_conditions=disproof,
        )

        assert stmt.claim == claim
        assert stmt.statement_type == StatementType.OBSERVATION
        assert stmt.evidence == evidence
        assert stmt.disproof_conditions == disproof

    def test_create_falsifiable_statement_with_hedging(self) -> None:
        """Test rejection of statement with hedging terms."""
        claim = "Method X probably produces deterministic output"

        with pytest.raises(EpistemicViolationError):
            EpistemicConstraints.create_falsifiable_statement(
                claim=claim,
                statement_type=StatementType.OBSERVATION,
                evidence=["test"],
                disproof_conditions=["different output"],
            )

    def test_create_falsifiable_statement_without_disproof(self) -> None:
        """Test rejection of statement without disproof conditions."""
        claim = "Method X is deterministic"

        with pytest.raises(EpistemicViolationError) as exc_info:
            EpistemicConstraints.create_falsifiable_statement(
                claim=claim,
                statement_type=StatementType.OBSERVATION,
                evidence=["test"],
                disproof_conditions=[],
            )

        assert "disproof conditions" in str(exc_info.value).lower()

    def test_validate_falsifiability_valid(self) -> None:
        """Test validation of falsifiable claim."""
        claim = "All methods are deterministic"
        disproof = ["Find a method that produces different output with same input"]

        EpistemicConstraints.validate_falsifiability(claim, disproof)

    def test_validate_falsifiability_invalid(self) -> None:
        """Test rejection of non-falsifiable claim."""
        claim = "The system is elegant"
        disproof: list[str] = []

        with pytest.raises(EpistemicViolationError) as exc_info:
            EpistemicConstraints.validate_falsifiability(claim, disproof)

        assert "FALSIFIABILITY constraint violated" in str(exc_info.value)

    def test_forbidden_hedging_terms_immutable(self) -> None:
        """Test that forbidden terms set is immutable."""
        terms = EpistemicConstraints.FORBIDDEN_HEDGING_TERMS
        assert isinstance(terms, frozenset)
        assert len(terms) > 0
        assert "probably" in terms
        assert "likely" in terms

    def test_falsifiable_statement_frozen(self) -> None:
        """Test that FalsifiableStatement is immutable."""
        stmt = FalsifiableStatement(
            claim="Test claim",
            statement_type=StatementType.OBSERVATION,
            evidence=["evidence1"],
            disproof_conditions=["disproof1"],
        )

        with pytest.raises(AttributeError):
            stmt.claim = "Modified claim"  # type: ignore

    def test_case_insensitive_hedging_detection(self) -> None:
        """Test hedging detection is case-insensitive."""
        texts = [
            "This PROBABLY works",
            "It SEEMS correct",
            "LIKELY accurate",
        ]

        for text in texts:
            with pytest.raises(EpistemicViolationError):
                EpistemicConstraints.validate_no_hedging(text)

    def test_all_statement_types_detected(self) -> None:
        """Test all statement types can be detected."""
        for stmt_type in StatementType:
            text = f"[{stmt_type.value}] Test statement"
            detected = EpistemicConstraints.validate_statement_labeled(text)
            assert detected == stmt_type
