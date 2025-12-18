"""
Agent Prime Directives: Epistemic Constraints

Enforces strict epistemic discipline:
- NO_GUESSING: Halt on insufficient evidence
- NO_HEDGING: Forbidden terms enforcement
- SEPARATION_MANDATORY: Label statements as [OBSERVATION], [ASSUMPTION], [DECISION]
- FALSIFIABILITY: Every claim specifies disproof conditions
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final


class StatementType(Enum):
    """Statement classification types."""

    OBSERVATION = "OBSERVATION"
    ASSUMPTION = "ASSUMPTION"
    DECISION = "DECISION"


class EpistemicViolationError(Exception):
    """Raised when epistemic constraints are violated."""

    pass


@dataclass(frozen=True)
class FalsifiableStatement:
    """A statement with explicit falsifiability conditions."""

    claim: str
    statement_type: StatementType
    evidence: list[str]
    disproof_conditions: list[str]

    def __post_init__(self) -> None:
        """Validate statement has disproof conditions."""
        if not self.disproof_conditions:
            raise EpistemicViolationError(
                f"Statement lacks disproof conditions: {self.claim}"
            )


class EpistemicConstraints:
    """Enforces epistemic constraints on agent reasoning."""

    FORBIDDEN_HEDGING_TERMS: Final[frozenset[str]] = frozenset(
        {
            "probably",
            "likely",
            "maybe",
            "it seems",
            "should work",
            "might",
            "could be",
            "perhaps",
            "possibly",
            "presumably",
        }
    )

    @staticmethod
    def validate_no_hedging(text: str) -> None:
        """
        Validate text contains no hedging terms.

        Args:
            text: Text to validate

        Raises:
            EpistemicViolationError: If hedging terms found
        """
        text_lower = text.lower()
        violations = [
            term
            for term in EpistemicConstraints.FORBIDDEN_HEDGING_TERMS
            if term in text_lower
        ]

        if violations:
            raise EpistemicViolationError(
                f"NO_HEDGING constraint violated. Forbidden terms found: {violations}"
            )

    @staticmethod
    def validate_statement_labeled(text: str) -> StatementType:
        """
        Validate statement is properly labeled with type.

        Args:
            text: Statement text

        Returns:
            Detected statement type

        Raises:
            EpistemicViolationError: If no valid label found
        """
        text_upper = text.upper()

        for stmt_type in StatementType:
            if f"[{stmt_type.value}]" in text_upper:
                return stmt_type

        raise EpistemicViolationError(
            "SEPARATION_MANDATORY constraint violated. "
            "Statement must be labeled [OBSERVATION], [ASSUMPTION], or [DECISION]"
        )

    @staticmethod
    def halt_insufficient_evidence(
        context: str, required_inputs: list[str]
    ) -> None:
        """
        Halt execution and declare insufficient evidence.

        Args:
            context: Context where evidence is insufficient
            required_inputs: List of required inputs to proceed

        Raises:
            EpistemicViolationError: Always raises to halt execution
        """
        raise EpistemicViolationError(
            f"INSUFFICIENT_EVIDENCE in context: {context}\n"
            f"Required inputs: {', '.join(required_inputs)}"
        )

    @staticmethod
    def create_falsifiable_statement(
        claim: str,
        statement_type: StatementType,
        evidence: list[str],
        disproof_conditions: list[str],
    ) -> FalsifiableStatement:
        """
        Create a falsifiable statement with validation.

        Args:
            claim: The claim being made
            statement_type: Type of statement
            evidence: Supporting evidence
            disproof_conditions: Conditions that would disprove the claim

        Returns:
            Validated falsifiable statement

        Raises:
            EpistemicViolationError: If constraints violated
        """
        EpistemicConstraints.validate_no_hedging(claim)

        return FalsifiableStatement(
            claim=claim,
            statement_type=statement_type,
            evidence=evidence,
            disproof_conditions=disproof_conditions,
        )

    @staticmethod
    def validate_falsifiability(
        claim: str, disproof_conditions: list[str]
    ) -> None:
        """
        Validate a claim has explicit disproof conditions.

        Args:
            claim: The claim to validate
            disproof_conditions: Conditions that would disprove the claim

        Raises:
            EpistemicViolationError: If no disproof conditions provided
        """
        if not disproof_conditions:
            raise EpistemicViolationError(
                f"FALSIFIABILITY constraint violated. "
                f"Claim lacks disproof conditions: {claim}"
            )
