"""
Questionnaire Signal Registry - Phase 2 Critical Component.

Provides O(1) mapping between FARFAN questions (Q001-Q305) and signal types (MC01-MC10).
Enables robust signal routing with empirical availability tracking.

This registry implements the integration mapping defined in integration_map.json
and fulfills the strategic irrigation requirement from the harmonized corpus plan.

Key Features:
- O(1) question → signals lookup via inverted index
- O(1) signal → questions reverse lookup
- Expected signal counts per question
- Empirical availability tracking for expectation adjustment
- Support for MICRO (Q001-Q300), MESO (Q301-Q304), and MACRO (Q305) questions
- Slot-based generic question mapping (D1-Q1, D1-Q2, etc.)

Author: F.A.R.F.A.N Pipeline Team - Phase 2 Enhancement
Version: 1.0.0
Date: 2026-01-12
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class QuestionSignalMapping:
    """Represents the signal mapping for a specific question."""

    question_id: str
    policy_area: str | None
    slot: str | None
    primary_signals: list[str]
    secondary_signals: list[str]
    expected_patterns: list[str]
    scoring_modality: str
    empirical_availability: float
    weight: float = 1.0
    farfan_dimensions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def all_signals(self) -> list[str]:
        """Get all signals (primary + secondary)."""
        return self.primary_signals + self.secondary_signals

    @property
    def expected_signal_count(self) -> int:
        """Calculate expected number of signals for this question."""
        # Primary signals are expected, secondary are optional
        return len(self.primary_signals)


@dataclass
class SignalTypeMapping:
    """Represents the reverse mapping: signal → questions."""

    signal_type: str
    questions_mapped: list[str]
    coverage: float
    primary_for: list[str]
    secondary_for: list[str]

    @property
    def total_questions(self) -> int:
        """Total questions using this signal."""
        return len(self.questions_mapped)


class QuestionnaireSignalRegistry:
    """
    Registry for question-signal mappings based on empirical integration.

    Loads integration_map.json and provides O(1) lookups for signal routing.
    Tracks empirical availability to adjust extraction expectations.

    Usage:
        registry = QuestionnaireSignalRegistry()

        # Get signals for a question
        mapping = registry.get_question_mapping("Q001")
        print(mapping.primary_signals)  # ["QUANTITATIVE_TRIPLET", "NORMATIVE_REFERENCE"]

        # Get questions for a signal
        questions = registry.get_questions_for_signal("FINANCIAL_CHAIN")

        # Get expected signal counts
        expected = registry.get_expected_signal_counts("Q003")
    """

    def __init__(self, integration_map_file: Path | None = None):
        """
        Initialize registry with integration map data.

        Args:
            integration_map_file: Path to integration_map.json (optional)
        """
        if integration_map_file is None:
            # Navigate from src/farfan_pipeline/phases/Phase_2/registries/ to repo root
            integration_map_file = (
                Path(__file__).resolve().parent.parent.parent.parent.parent.parent
                / "canonic_questionnaire_central"
                / "_registry"
                / "questions"
                / "integration_map.json"
            )

        self.integration_map_file = integration_map_file
        self.integration_data = self._load_integration_map()

        # Build inverted indexes
        self.question_to_signals: dict[str, QuestionSignalMapping] = {}
        self.signal_to_questions: dict[str, SignalTypeMapping] = {}
        self.slot_to_questions: dict[str, list[str]] = {}

        self._build_indexes()

        logger.info(
            f"QuestionnaireSignalRegistry initialized: "
            f"{len(self.question_to_signals)} questions mapped to "
            f"{len(self.signal_to_questions)} signal types"
        )

    def _load_integration_map(self) -> dict[str, Any]:
        """Load integration map JSON."""
        try:
            with open(self.integration_map_file, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Integration map file not found: {self.integration_map_file}")
            raise RuntimeError(
                f"Cannot initialize QuestionnaireSignalRegistry without integration map at: {self.integration_map_file}"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in integration map file: {e}")
            raise

    def _build_indexes(self):
        """Build O(1) inverted indexes for fast lookups."""
        # Process slot-to-signal mappings (MICRO questions Q001-Q300)
        slot_mappings = self.integration_data.get("farfan_question_mapping", {}).get(
            "slot_to_signal_mapping", {}
        )

        for slot_id, slot_data in slot_mappings.items():
            slot = slot_data.get("slot")
            children_questions = slot_data.get("children_questions", [])
            primary_signals = slot_data.get("primary_signals", [])
            secondary_signals = slot_data.get("secondary_signals", [])
            expected_patterns = slot_data.get("expected_patterns", [])
            scoring_modality = slot_data.get("scoring_modality", "TYPE_A")
            empirical_availability = slot_data.get("empirical_availability", 1.0)
            weight = slot_data.get("weight", 1.0)
            farfan_dimensions = slot_data.get("farfan_dimensions", [])

            # Store slot mapping
            self.slot_to_questions[slot] = children_questions

            # Create mapping for each child question
            for question_id in children_questions:
                # Determine policy area from question ID
                # Q001-Q030 → PA01, Q031-Q060 → PA02, etc.
                q_num = int(question_id[1:])  # Extract number from Q001
                policy_area = None
                if 1 <= q_num <= 300:
                    # Each PA has 30 questions
                    pa_num = ((q_num - 1) // 30) + 1
                    policy_area = f"PA{pa_num:02d}"

                mapping = QuestionSignalMapping(
                    question_id=question_id,
                    policy_area=policy_area,
                    slot=slot,
                    primary_signals=primary_signals.copy(),
                    secondary_signals=secondary_signals.copy(),
                    expected_patterns=expected_patterns.copy(),
                    scoring_modality=scoring_modality,
                    empirical_availability=empirical_availability,
                    weight=weight,
                    farfan_dimensions=farfan_dimensions.copy(),
                    metadata={
                        "generic_abbrev": slot_data.get("generic_abbrev"),
                        "generic_question": slot_data.get("generic_question"),
                    },
                )

                self.question_to_signals[question_id] = mapping

                # Update reverse index
                for signal in primary_signals + secondary_signals:
                    if signal not in self.signal_to_questions:
                        self.signal_to_questions[signal] = SignalTypeMapping(
                            signal_type=signal,
                            questions_mapped=[],
                            coverage=0.0,
                            primary_for=[],
                            secondary_for=[],
                        )

                    self.signal_to_questions[signal].questions_mapped.append(question_id)
                    if signal in primary_signals:
                        self.signal_to_questions[signal].primary_for.append(question_id)
                    else:
                        self.signal_to_questions[signal].secondary_for.append(question_id)

        # Process MESO questions (Q301-Q304)
        meso_questions = (
            self.integration_data.get("farfan_meso_macro_integration", {})
            .get("meso_questions", {})
        )

        for meso_id, meso_data in meso_questions.items():
            question_id = meso_data.get("question_id")
            required_signals = meso_data.get("required_signals", [])
            policy_areas = meso_data.get("policy_areas", [])
            cluster = meso_data.get("cluster")

            mapping = QuestionSignalMapping(
                question_id=question_id,
                policy_area=None,  # MESO spans multiple PAs
                slot=None,
                primary_signals=required_signals.copy(),
                secondary_signals=[],
                expected_patterns=meso_data.get("integration_patterns", []),
                scoring_modality=meso_data.get("scoring_modality", "MESO_INTEGRATION"),
                empirical_availability=1.0,
                weight=1.0,
                farfan_dimensions=[cluster],
                metadata={
                    "cluster": cluster,
                    "policy_areas": policy_areas,
                    "micro_dependencies": meso_data.get("micro_dependencies", []),
                },
            )

            self.question_to_signals[question_id] = mapping

            # Update reverse index
            for signal in required_signals:
                if signal not in self.signal_to_questions:
                    self.signal_to_questions[signal] = SignalTypeMapping(
                        signal_type=signal,
                        questions_mapped=[],
                        coverage=0.0,
                        primary_for=[],
                        secondary_for=[],
                    )

                self.signal_to_questions[signal].questions_mapped.append(question_id)
                self.signal_to_questions[signal].primary_for.append(question_id)

        # Process MACRO question (Q305)
        macro_data = (
            self.integration_data.get("farfan_meso_macro_integration", {})
            .get("macro_question", {})
        )

        if macro_data:
            question_id = macro_data.get("question_id")
            required_signals = macro_data.get("required_signals", [])

            # If required_signals is ["ALL"], expand to all known signal types
            if required_signals == ["ALL"]:
                required_signals = list(self.signal_to_questions.keys())

            mapping = QuestionSignalMapping(
                question_id=question_id,
                policy_area=None,
                slot=None,
                primary_signals=required_signals.copy(),
                secondary_signals=[],
                expected_patterns=[],
                scoring_modality=macro_data.get("scoring_modality", "MACRO_HOLISTIC"),
                empirical_availability=1.0,
                weight=1.0,
                farfan_dimensions=["MACRO"],
                metadata={
                    "abbrev": macro_data.get("abbrev"),
                    "question": macro_data.get("question"),
                    "meso_dependencies": macro_data.get("meso_dependencies", []),
                    "evaluation_components": macro_data.get("evaluation_components", {}),
                },
            )

            self.question_to_signals[question_id] = mapping

            # Update reverse index
            for signal in required_signals:
                if signal not in self.signal_to_questions:
                    self.signal_to_questions[signal] = SignalTypeMapping(
                        signal_type=signal,
                        questions_mapped=[],
                        coverage=0.0,
                        primary_for=[],
                        secondary_for=[],
                    )

                self.signal_to_questions[signal].questions_mapped.append(question_id)
                self.signal_to_questions[signal].primary_for.append(question_id)

        # Calculate coverage for each signal type
        total_questions = 305  # Q001-Q305
        for signal_type, mapping in self.signal_to_questions.items():
            mapping.coverage = len(mapping.questions_mapped) / total_questions

    def get_question_mapping(self, question_id: str) -> QuestionSignalMapping | None:
        """
        Get signal mapping for a specific question.

        Args:
            question_id: Question identifier (Q001-Q305)

        Returns:
            QuestionSignalMapping or None if not found
        """
        return self.question_to_signals.get(question_id)

    def get_questions_for_signal(
        self, signal_type: str, primary_only: bool = False
    ) -> list[str]:
        """
        Get all questions that use a specific signal type.

        Args:
            signal_type: Signal type (e.g., "FINANCIAL_CHAIN")
            primary_only: If True, only return questions where this is a primary signal

        Returns:
            List of question IDs
        """
        mapping = self.signal_to_questions.get(signal_type)
        if not mapping:
            return []

        if primary_only:
            return mapping.primary_for.copy()
        else:
            return mapping.questions_mapped.copy()

    def get_signal_type_mapping(self, signal_type: str) -> SignalTypeMapping | None:
        """
        Get complete mapping information for a signal type.

        Args:
            signal_type: Signal type identifier

        Returns:
            SignalTypeMapping or None if not found
        """
        return self.signal_to_questions.get(signal_type)

    def get_expected_signal_counts(self, question_id: str) -> dict[str, int]:
        """
        Get expected signal counts for a question.

        Args:
            question_id: Question identifier

        Returns:
            Dictionary with expected counts per signal type
        """
        mapping = self.get_question_mapping(question_id)
        if not mapping:
            return {}

        counts = {}
        # Primary signals are expected (count = 1 each)
        for signal in mapping.primary_signals:
            counts[signal] = 1

        # Secondary signals are optional (count = 0)
        for signal in mapping.secondary_signals:
            counts[signal] = 0

        return counts

    def get_empirical_availability(self, question_id: str) -> float:
        """
        Get empirical availability score for a question.

        This score indicates how frequently this question's signals
        appear in the empirical corpus (0.0-1.0).

        Args:
            question_id: Question identifier

        Returns:
            Empirical availability score (0.0-1.0)
        """
        mapping = self.get_question_mapping(question_id)
        if not mapping:
            return 0.0

        return mapping.empirical_availability

    def get_questions_by_policy_area(self, policy_area: str) -> list[str]:
        """
        Get all MICRO questions for a specific policy area.

        Args:
            policy_area: Policy area code (PA01-PA10)

        Returns:
            List of question IDs for that policy area
        """
        questions = []
        for question_id, mapping in self.question_to_signals.items():
            if mapping.policy_area == policy_area:
                questions.append(question_id)

        return sorted(questions)

    def get_questions_by_slot(self, slot: str) -> list[str]:
        """
        Get all questions for a generic slot.

        Args:
            slot: Slot identifier (D1-Q1, D1-Q2, etc.)

        Returns:
            List of question IDs for that slot
        """
        return self.slot_to_questions.get(slot, []).copy()

    def get_questions_by_signal_combination(
        self, required_signals: list[str], match_all: bool = True
    ) -> list[str]:
        """
        Get questions that use a specific combination of signals.

        Args:
            required_signals: List of signal types
            match_all: If True, question must use ALL signals; if False, ANY signal

        Returns:
            List of matching question IDs
        """
        matching_questions = []

        for question_id, mapping in self.question_to_signals.items():
            question_signals = set(mapping.all_signals)
            required_set = set(required_signals)

            if match_all:
                # Question must have all required signals
                if required_set.issubset(question_signals):
                    matching_questions.append(question_id)
            else:
                # Question must have at least one required signal
                if question_signals.intersection(required_set):
                    matching_questions.append(question_id)

        return sorted(matching_questions)

    def get_signal_coverage_stats(self) -> dict[str, Any]:
        """
        Get comprehensive statistics about signal coverage.

        Returns:
            Dictionary with coverage statistics
        """
        stats = {
            "total_questions_mapped": len(self.question_to_signals),
            "total_signal_types": len(self.signal_to_questions),
            "signal_coverage": {},
            "average_signals_per_question": 0.0,
            "questions_with_multiple_signals": 0,
        }

        total_signals = 0
        multi_signal_count = 0

        for question_id, mapping in self.question_to_signals.items():
            signal_count = len(mapping.all_signals)
            total_signals += signal_count
            if signal_count > 1:
                multi_signal_count += 1

        if self.question_to_signals:
            stats["average_signals_per_question"] = (
                total_signals / len(self.question_to_signals)
            )
        stats["questions_with_multiple_signals"] = multi_signal_count

        # Per-signal coverage
        for signal_type, mapping in self.signal_to_questions.items():
            stats["signal_coverage"][signal_type] = {
                "total_questions": mapping.total_questions,
                "coverage_percentage": mapping.coverage * 100,
                "primary_for": len(mapping.primary_for),
                "secondary_for": len(mapping.secondary_for),
            }

        return stats

    def validate_question_id(self, question_id: str) -> bool:
        """
        Validate that a question ID exists in the registry.

        Args:
            question_id: Question identifier to validate

        Returns:
            True if question exists, False otherwise
        """
        return question_id in self.question_to_signals

    def get_all_signal_types(self) -> list[str]:
        """Get list of all known signal types."""
        return sorted(self.signal_to_questions.keys())

    def get_all_question_ids(self) -> list[str]:
        """Get list of all known question IDs."""
        return sorted(self.question_to_signals.keys())


# Convenience functions


def load_questionnaire_signal_registry() -> QuestionnaireSignalRegistry:
    """
    Convenience function to load the questionnaire signal registry.

    Returns:
        Initialized QuestionnaireSignalRegistry
    """
    return QuestionnaireSignalRegistry()


def get_signals_for_question(question_id: str) -> list[str]:
    """
    Convenience function to get signals for a question.

    Args:
        question_id: Question identifier

    Returns:
        List of signal types (primary + secondary)
    """
    registry = load_questionnaire_signal_registry()
    mapping = registry.get_question_mapping(question_id)
    return mapping.all_signals if mapping else []


__all__ = [
    "QuestionnaireSignalRegistry",
    "QuestionSignalMapping",
    "SignalTypeMapping",
    "load_questionnaire_signal_registry",
    "get_signals_for_question",
]
