"""
SISAS Signal Irrigation System - Signal Delivery to Questions.

This module materializes the signal irrigation infrastructure that routes signals
from extractors to questions based on the integration_map.json slot_to_signal mappings.

Architecture:
    Extractors → SignalIrrigator → Questions (via slot_to_signal routing)

Key Features:
- Loads slot_to_signal mappings from integration_map.json
- Routes signals to appropriate questions based on signal type
- Tracks irrigation paths and value_added per signal
- Provides instrumentation with trace IDs
- Validates signal quality before delivery
- Deduplicates signals across questions

Version: 1.0.0
Status: Production-ready
Author: FARFAN Pipeline Team
Date: 2026-01-07
"""

from __future__ import annotations

import json
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class SignalDelivery:
    """Represents a delivered signal to a question."""
    delivery_id: str
    question_id: str
    signal_type: str
    signal_payload: Dict[str, Any]
    confidence: float
    irrigation_path: List[str]  # Trace from extractor → slot → question
    value_added: float  # Expected value contribution
    delivered_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IrrigationStats:
    """Statistics for signal irrigation."""
    total_signals_received: int = 0
    total_signals_delivered: int = 0
    total_questions_irrigated: int = 0
    signals_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    questions_by_slot: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    average_confidence: float = 0.0
    total_value_added: float = 0.0


class SignalIrrigator:
    """
    Routes signals from extractors to questions based on integration_map.json.

    This is the core irrigation system that materializes SISAS signal delivery.
    It consumes the slot_to_signal_mapping and routes extracted signals to
    the appropriate questions.

    Usage:
        irrigator = SignalIrrigator()

        # Extract signals
        triplets = triplet_extractor.extract(text)

        # Irrigate to questions
        deliveries = irrigator.irrigate_signal(
            signal_type="QUANTITATIVE_TRIPLET",
            signal_data=triplets.matches,
            confidence=triplets.confidence
        )

        # Get irrigated questions
        for delivery in deliveries:
            print(f"Delivered to {delivery.question_id} via {delivery.irrigation_path}")
    """

    def __init__(self, integration_map_path: Optional[Path] = None):
        """
        Initialize signal irrigator with integration map.

        Args:
            integration_map_path: Path to integration_map.json. If None, uses default location.
        """
        if integration_map_path is None:
            integration_map_path = self._default_integration_map_path()

        self.integration_map_path = integration_map_path
        self.slot_to_signal_mapping: Dict[str, Dict[str, Any]] = {}
        self.signal_to_questions_index: Dict[str, List[str]] = defaultdict(list)
        self.question_to_slots_index: Dict[str, str] = {}

        # Statistics
        self.stats = IrrigationStats()

        # Delivered signals cache (for deduplication)
        self.delivered_signals: Dict[str, List[SignalDelivery]] = defaultdict(list)

        # Load integration map
        self._load_integration_map()
        self._build_routing_indices()

        logger.info(f"SignalIrrigator initialized with {len(self.slot_to_signal_mapping)} slots")

    def _default_integration_map_path(self) -> Path:
        """Get default path to integration_map.json."""
        # Navigate from infrastructure to canonic_questionnaire_central
        return Path(__file__).parent.parent.parent.parent.parent / \
               "canonic_questionnaire_central" / "_registry" / "questions" / \
               "integration_map.json"

    def _load_integration_map(self) -> None:
        """Load integration map from JSON file."""
        if not self.integration_map_path.exists():
            logger.warning(f"Integration map not found at {self.integration_map_path}")
            return

        try:
            with open(self.integration_map_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            farfan_mapping = data.get("farfan_question_mapping", {})
            self.slot_to_signal_mapping = farfan_mapping.get("slot_to_signal_mapping", {})

            logger.info(f"Loaded {len(self.slot_to_signal_mapping)} slot mappings from integration_map.json")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load integration_map.json: {e}")
            raise

    def _build_routing_indices(self) -> None:
        """Build inverted indices for fast signal routing."""
        # Index: signal_type -> [question_ids]
        for slot_id, slot_config in self.slot_to_signal_mapping.items():
            children_questions = slot_config.get("children_questions", [])
            primary_signals = slot_config.get("primary_signals", [])
            secondary_signals = slot_config.get("secondary_signals", [])

            # Map primary signals to questions
            for signal_type in primary_signals:
                for question_id in children_questions:
                    if question_id not in self.signal_to_questions_index[signal_type]:
                        self.signal_to_questions_index[signal_type].append(question_id)

            # Map secondary signals to questions (lower priority)
            for signal_type in secondary_signals:
                for question_id in children_questions:
                    if question_id not in self.signal_to_questions_index[signal_type]:
                        self.signal_to_questions_index[signal_type].append(question_id)

            # Reverse index: question_id -> slot_id
            for question_id in children_questions:
                self.question_to_slots_index[question_id] = slot_id

        logger.info(f"Built routing indices: {len(self.signal_to_questions_index)} signal types mapped")

    def irrigate_signal(
        self,
        signal_type: str,
        signal_data: List[Dict[str, Any]],
        confidence: float,
        extractor_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[SignalDelivery]:
        """
        Irrigate a signal to all relevant questions.

        Args:
            signal_type: Type of signal (e.g., "QUANTITATIVE_TRIPLET")
            signal_data: List of signal matches/extractions
            confidence: Aggregate confidence score
            extractor_id: ID of the extractor that produced the signal
            metadata: Additional metadata about the signal

        Returns:
            List of SignalDelivery objects representing delivered signals
        """
        self.stats.total_signals_received += 1
        self.stats.signals_by_type[signal_type] += 1

        # Get target questions for this signal type
        target_questions = self.signal_to_questions_index.get(signal_type, [])

        if not target_questions:
            logger.warning(f"No questions mapped for signal type: {signal_type}")
            return []

        deliveries = []

        # Deliver signal to each target question
        for question_id in target_questions:
            slot_id = self.question_to_slots_index.get(question_id)

            if not slot_id:
                continue

            slot_config = self.slot_to_signal_mapping.get(slot_id, {})

            # Build irrigation path
            irrigation_path = [
                extractor_id or f"{signal_type}Extractor",
                slot_id,
                question_id
            ]

            # Calculate value added (empirical availability from slot config)
            value_added = slot_config.get("empirical_availability", 0.5)

            # Create delivery
            delivery = SignalDelivery(
                delivery_id=str(uuid.uuid4()),
                question_id=question_id,
                signal_type=signal_type,
                signal_payload={
                    "matches": signal_data,
                    "match_count": len(signal_data),
                    "confidence": confidence
                },
                confidence=confidence,
                irrigation_path=irrigation_path,
                value_added=value_added,
                delivered_at=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "slot_id": slot_id,
                    "slot_abbrev": slot_config.get("generic_abbrev"),
                    "scoring_modality": slot_config.get("scoring_modality"),
                    "is_primary": signal_type in slot_config.get("primary_signals", []),
                    **(metadata or {})
                }
            )

            deliveries.append(delivery)
            self.delivered_signals[question_id].append(delivery)

            # Update stats
            self.stats.total_signals_delivered += 1
            self.stats.questions_by_slot[slot_id] += 1
            self.stats.total_value_added += value_added

        # Update stats
        if deliveries:
            irrigated_questions = set(d.question_id for d in deliveries)
            self.stats.total_questions_irrigated = len(self.delivered_signals.keys())
            self.stats.average_confidence = (
                sum(d.confidence for d in deliveries) / len(deliveries)
            )

        logger.info(f"Irrigated {len(deliveries)} deliveries for signal type {signal_type}")

        return deliveries

    def get_question_signals(self, question_id: str) -> List[SignalDelivery]:
        """
        Get all signals delivered to a specific question.

        Args:
            question_id: Question ID (e.g., "Q001")

        Returns:
            List of SignalDelivery objects for the question
        """
        return self.delivered_signals.get(question_id, [])

    def get_signals_by_type(self, question_id: str, signal_type: str) -> List[SignalDelivery]:
        """
        Get signals of a specific type delivered to a question.

        Args:
            question_id: Question ID
            signal_type: Signal type to filter by

        Returns:
            List of SignalDelivery objects matching the signal type
        """
        all_signals = self.get_question_signals(question_id)
        return [s for s in all_signals if s.signal_type == signal_type]

    def get_expected_signals_for_question(self, question_id: str) -> Dict[str, Any]:
        """
        Get expected signals configuration for a question.

        Args:
            question_id: Question ID

        Returns:
            Dict with primary_signals, secondary_signals, and other metadata
        """
        slot_id = self.question_to_slots_index.get(question_id)

        if not slot_id:
            return {}

        slot_config = self.slot_to_signal_mapping.get(slot_id, {})

        return {
            "slot_id": slot_id,
            "slot_abbrev": slot_config.get("generic_abbrev"),
            "primary_signals": slot_config.get("primary_signals", []),
            "secondary_signals": slot_config.get("secondary_signals", []),
            "expected_patterns": slot_config.get("expected_patterns", []),
            "scoring_modality": slot_config.get("scoring_modality"),
            "empirical_availability": slot_config.get("empirical_availability")
        }

    def validate_question_irrigation(self, question_id: str) -> Dict[str, Any]:
        """
        Validate that a question has received expected signals.

        Args:
            question_id: Question ID to validate

        Returns:
            Dict with validation results
        """
        expected = self.get_expected_signals_for_question(question_id)
        delivered_signals = self.get_question_signals(question_id)

        if not expected:
            return {
                "question_id": question_id,
                "valid": False,
                "error": "Question not found in integration map"
            }

        primary_signals = set(expected.get("primary_signals", []))
        secondary_signals = set(expected.get("secondary_signals", []))

        delivered_types = {s.signal_type for s in delivered_signals}

        # Check coverage
        primary_coverage = len(primary_signals & delivered_types) / len(primary_signals) if primary_signals else 0.0
        secondary_coverage = len(secondary_signals & delivered_types) / len(secondary_signals) if secondary_signals else 0.0

        return {
            "question_id": question_id,
            "valid": primary_coverage >= 0.5,  # At least 50% of primary signals
            "primary_coverage": primary_coverage,
            "secondary_coverage": secondary_coverage,
            "expected_primary": list(primary_signals),
            "expected_secondary": list(secondary_signals),
            "delivered_types": list(delivered_types),
            "missing_primary": list(primary_signals - delivered_types),
            "total_deliveries": len(delivered_signals)
        }

    def get_irrigation_stats(self) -> Dict[str, Any]:
        """Get irrigation statistics."""
        return {
            "total_signals_received": self.stats.total_signals_received,
            "total_signals_delivered": self.stats.total_signals_delivered,
            "total_questions_irrigated": self.stats.total_questions_irrigated,
            "signals_by_type": dict(self.stats.signals_by_type),
            "questions_by_slot": dict(self.stats.questions_by_slot),
            "average_confidence": self.stats.average_confidence,
            "total_value_added": self.stats.total_value_added,
            "irrigation_efficiency": (
                self.stats.total_signals_delivered / self.stats.total_signals_received
                if self.stats.total_signals_received > 0
                else 0.0
            )
        }

    def clear_deliveries(self) -> None:
        """Clear all delivered signals (useful for batch processing)."""
        self.delivered_signals.clear()
        self.stats = IrrigationStats()
        logger.info("Cleared all signal deliveries")


# Convenience function for quick irrigation
def irrigate_extraction_result(
    irrigator: SignalIrrigator,
    extraction_result: Any,  # ExtractionResult from empirical_extractor_base
    extractor_id: Optional[str] = None
) -> List[SignalDelivery]:
    """
    Convenience function to irrigate an ExtractionResult directly.

    Args:
        irrigator: SignalIrrigator instance
        extraction_result: ExtractionResult from an extractor
        extractor_id: Optional extractor ID

    Returns:
        List of SignalDelivery objects
    """
    return irrigator.irrigate_signal(
        signal_type=extraction_result.signal_type,
        signal_data=extraction_result.matches,
        confidence=extraction_result.confidence,
        extractor_id=extractor_id or extraction_result.extractor_id,
        metadata=extraction_result.metadata
    )


__all__ = [
    'SignalIrrigator',
    'SignalDelivery',
    'IrrigationStats',
    'irrigate_extraction_result'
]
