"""Tests for Phase 9 Signal Enriched Reporting."""

import pytest

class TestPhase9SignalEnrichment:
    """Test Phase 9 signal-enriched reporting."""

    def test_narrative_enrichment_low_score(self):
        """Test narrative enrichment for low score."""
        from farfan_pipeline.phases.Phase_9.phase9_10_00_signal_enriched_reporting import (
            SignalEnrichedReporter,
        )

        reporter = SignalEnrichedReporter(signal_registry=None)

        base_narrative = "The baseline analysis is incomplete."
        score_data = {
            "score": 0.3,
            "quality_level": "INSUFICIENTE",
        }

        enriched, details = reporter.enrich_narrative_context(
            question_id="Q001",
            base_narrative=base_narrative,
            score_data=score_data,
        )

        # Narrative should be enriched (or unchanged if no registry)
        assert len(enriched) >= len(base_narrative)
        # With no registry, we expect basic details
        assert "base_length" in details

    def test_section_emphasis_critical_scores(self):
        """Test section emphasis with critical scores."""
        from farfan_pipeline.phases.Phase_9.phase9_10_00_signal_enriched_reporting import (
            SignalEnrichedReporter,
        )

        reporter = SignalEnrichedReporter()

        section_data = {
            "scores": [0.2, 0.3, 0.25, 0.28],  # All critical
            "representative_question": "Q001",
        }

        emphasis, details = reporter.determine_section_emphasis(
            section_id="SEC01",
            section_data=section_data,
            policy_area="PA01",
        )

        # Should have high emphasis due to critical scores
        assert emphasis >= 0.7
        assert len(details["factors"]) > 0

    def test_section_emphasis_convergent_scores(self):
        """Test section emphasis with convergent scores."""
        from farfan_pipeline.phases.Phase_9.phase9_10_00_signal_enriched_reporting import (
            SignalEnrichedReporter,
        )

        reporter = SignalEnrichedReporter()

        section_data = {
            "scores": [0.75, 0.76, 0.75, 0.76],  # Low variance
            "representative_question": "Q002",
        }

        emphasis, details = reporter.determine_section_emphasis(
            section_id="SEC02",
            section_data=section_data,
            policy_area="PA02",
        )

        # Should have lower emphasis due to convergence (not interesting)
        assert emphasis < 0.6

    def test_evidence_highlighting_no_registry(self):
        """Test evidence highlighting without registry (graceful degradation)."""
        from farfan_pipeline.phases.Phase_9.phase9_10_00_signal_enriched_reporting import (
            SignalEnrichedReporter,
        )

        reporter = SignalEnrichedReporter(signal_registry=None)

        evidence_list = [
            {"text": "Evidence item 1", "id": "E1"},
            {"text": "Evidence item 2", "id": "E2"},
        ]

        highlighted, details = reporter.highlight_evidence_patterns(
            question_id="Q003",
            evidence_list=evidence_list,
        )

        # Should return original evidence unchanged
        assert len(highlighted) == len(evidence_list)
        assert highlighted[0]["text"] == evidence_list[0]["text"]
