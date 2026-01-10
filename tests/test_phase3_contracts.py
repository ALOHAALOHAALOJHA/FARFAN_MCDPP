"""Tests for Phase 3 15-Contract Compliance and Intramodular Wiring.

Verifies that Phase 3 adheres to key system contracts (Determinism, Traceability)
and correctly integrates SignalEnrichedScorer (Wiring).
"""

import sys
import pytest
import asyncio
import unittest.mock
from pathlib import Path
from dataclasses import dataclass, field
from unittest.mock import MagicMock

# Add src to path

from orchestration.orchestrator import Orchestrator, MicroQuestionRun, ScoredMicroQuestion, Evidence


# Mock dependencies
class MockSignalRegistry:
    def get_scoring_signals(self, question_id):
        m = MagicMock(question_modalities={question_id: "test_modality"}, source_hash="hash_123")
        m.scoring_modality = "binary_presence"  # Fix the attribute access in logs
        # Ensure stable string representation
        m.__repr__ = lambda x: "<MockSignalObject>"
        return m

    def get_micro_answering_signals(self, question_id):
        signals = MagicMock()
        signals.patterns = ["p1", "p2"]
        signals.indicators = ["i1"]
        return signals


class MockExecutor:
    def __init__(self):
        self.signal_registry = MockSignalRegistry()


class MockInstrumentation:
    def start(self, items_total=None):
        pass

    def increment(self, latency=None):
        pass

    def record_error(self, category, message):
        pass

    def complete(self):
        pass


# Test class
class TestPhase3Contracts:

    @pytest.fixture
    def orchestrator(self):
        # Partial mock of Orchestrator to test _score_micro_results_async
        orch = MagicMock(spec=Orchestrator)
        orch.executor = MockExecutor()
        orch._phase_instrumentation = {3: MockInstrumentation()}
        orch._ensure_not_aborted = MagicMock()
        return orch

    @pytest.mark.asyncio
    async def test_contract_traceability_and_wiring(self, orchestrator):
        """
        Contract: Traceability
        Verify that scoring outputs contain full provenance including signal enrichment details.
        Also verifies Intramodular Wiring (SignalEnrichedScorer usage).
        """
        # Input with partial completeness
        micro_result = MicroQuestionRun(
            question_id="Q001",
            question_global=1,
            base_slot="D1-Q1",
            metadata={
                "overall_confidence": 0.7,
                "completeness": "partial",
                "calibrated_interval": [0.6, 0.8],
            },
            evidence=Evidence(modality="text", raw_results={}),
            duration_ms=100,
        )

        with unittest.mock.patch("orchestration.orchestrator.EXPECTED_QUESTION_COUNT", 1):
            with unittest.mock.patch(
                "orchestration.orchestrator.validate_micro_results_input", MagicMock()
            ):
                # Execute actual method from Orchestrator class
                results = await Orchestrator._score_micro_results_async(
                    orchestrator, [micro_result], {}
                )

        assert len(results) == 1
        scored = results[0]

        # Verify Traceability
        assert "scoring_details" in scored.__dict__
        details = scored.scoring_details

        # Check signal enrichment details (from SignalEnrichedScorer)
        assert "signal_enrichment" in details
        assert details["signal_enrichment"]["enabled"] is True
        assert "quality_validation" in details["signal_enrichment"]
        assert "threshold_adjustment" in details["signal_enrichment"]

        # Check base details
        assert details["source"] == "evidence_nexus"
        assert details["completeness"] == "partial"

        print("\n✓ Traceability Contract: Output contains signal enrichment provenance")

    @pytest.mark.asyncio
    async def test_contract_determinism(self, orchestrator):
        """
        Contract: Determinism
        Verify that Phase 3 produces byte-identical output for identical input.
        """
        micro_result = MicroQuestionRun(
            question_id="Q001",
            question_global=1,
            base_slot="D1-Q1",
            metadata={"overall_confidence": 0.85, "completeness": "complete"},
            evidence=Evidence(modality="text", raw_results={}),
            duration_ms=100,
        )

        # Mock EXPECTED_QUESTION_COUNT to 1 for test
        with unittest.mock.patch("orchestration.orchestrator.EXPECTED_QUESTION_COUNT", 1):
            with unittest.mock.patch(
                "orchestration.orchestrator.validate_micro_results_input", MagicMock()
            ):
                with unittest.mock.patch("time.time", return_value=1234567890.0):
                    # Run 1
                    results1 = await Orchestrator._score_micro_results_async(
                        orchestrator, [micro_result], {}
                    )

                    # Run 2
                    results2 = await Orchestrator._score_micro_results_async(
                        orchestrator, [micro_result], {}
                    )

        # Assert equality
        assert results1[0].score == results2[0].score
        assert results1[0].quality_level == results2[0].quality_level

        # Deep compare scoring details
        import json

        d1 = json.dumps(results1[0].scoring_details, sort_keys=True, default=str)
        d2 = json.dumps(results2[0].scoring_details, sort_keys=True, default=str)
        assert d1 == d2

        print("\n✓ Determinism Contract: Identical inputs produce identical outputs")

    @pytest.mark.asyncio
    async def test_contract_wiring_logic_promotion(self, orchestrator):
        """
        Contract: Wiring / Logic
        Verify that SignalEnrichedScorer logic (promotion) is actually applied.
        """
        # Case: High score (0.9) but Insufficient evidence -> Should be promoted to ACEPTABLE
        # SignalEnrichedScorer rule: if score >= 0.8 and quality INSUFICIENTE -> promote to ACEPTABLE
        micro_result = MicroQuestionRun(
            question_id="Q001",
            question_global=1,
            base_slot="D1-Q1",
            metadata={"overall_confidence": 0.9, "completeness": "insufficient"},
            evidence=Evidence(modality="text", raw_results={}),
            duration_ms=100,
        )

        with unittest.mock.patch("orchestration.orchestrator.EXPECTED_QUESTION_COUNT", 1):
            with unittest.mock.patch(
                "orchestration.orchestrator.validate_micro_results_input", MagicMock()
            ):
                results = await Orchestrator._score_micro_results_async(
                    orchestrator, [micro_result], {}
                )
        scored = results[0]

        # Without SignalEnrichedScorer, insufficient -> INSUFICIENTE
        # With SignalEnrichedScorer, 0.9 >= 0.8 (HIGH) -> promote to ACEPTABLE
        assert scored.quality_level == "ACEPTABLE"

        validation = scored.scoring_details["signal_enrichment"]["quality_validation"]
        assert validation["validated_quality"] == "ACEPTABLE"
        assert validation["original_quality"] == "INSUFICIENTE"
        assert any(check["check"] == "score_quality_consistency" for check in validation["checks"])

        print("\n✓ Wiring Contract: SignalEnrichedScorer logic (promotion) correctly applied")

    @pytest.mark.asyncio
    async def test_contract_wiring_logic_demotion(self, orchestrator):
        """
        Contract: Wiring / Logic
        Verify that SignalEnrichedScorer logic (demotion) is actually applied.
        """
        # Case: Low score (0.2) but Complete evidence (mapped to EXCELENTE) -> Should be demoted to ACEPTABLE
        # SignalEnrichedScorer rule: if score < 0.3 and quality EXCELENTE -> demote to ACEPTABLE
        micro_result = MicroQuestionRun(
            question_id="Q001",
            question_global=1,
            base_slot="D1-Q1",
            metadata={"overall_confidence": 0.2, "completeness": "complete"},
            evidence=Evidence(modality="text", raw_results={}),
            duration_ms=100,
        )

        with unittest.mock.patch("orchestration.orchestrator.EXPECTED_QUESTION_COUNT", 1):
            with unittest.mock.patch(
                "orchestration.orchestrator.validate_micro_results_input", MagicMock()
            ):
                results = await Orchestrator._score_micro_results_async(
                    orchestrator, [micro_result], {}
                )
        scored = results[0]

        # Without SignalEnrichedScorer, complete -> EXCELENTE
        # With SignalEnrichedScorer, 0.2 < 0.3 (LOW) -> demote to ACEPTABLE
        assert scored.quality_level == "ACEPTABLE"

        validation = scored.scoring_details["signal_enrichment"]["quality_validation"]
        assert validation["validated_quality"] == "ACEPTABLE"
        assert validation["original_quality"] == "EXCELENTE"
        assert any(check["check"] == "low_score_validation" for check in validation["checks"])

        print("\n✓ Wiring Contract: SignalEnrichedScorer logic (demotion) correctly applied")
