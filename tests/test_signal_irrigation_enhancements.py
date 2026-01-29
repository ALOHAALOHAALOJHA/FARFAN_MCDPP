# Phase 3 Tests
class TestPhase3SignalEnrichment:
    """Test Phase 3 signal-enriched scoring."""

    def test_threshold_adjustment_no_registry(self):
        """Test threshold adjustment without signal registry (graceful degradation)."""
        from farfan_pipeline.phases.Phase_03.phase3_10_00_phase3_signal_enriched_scoring import (
            SignalEnrichedScorer,
        )

        scorer = SignalEnrichedScorer(signal_registry=None)

        adjusted, details = scorer.adjust_threshold_for_question(
            question_id="Q001",
            base_threshold=0.65,
            score=0.5,
            metadata={},
        )

        # Should return base threshold unchanged
        assert adjusted == 0.65
        assert details["adjustment"] == "none"

    def test_quality_validation_score_consistency(self):
        """Test quality validation with score-quality consistency check."""
        from farfan_pipeline.phases.Phase_03.phase3_10_00_phase3_signal_enriched_scoring import (
            SignalEnrichedScorer,
        )

        scorer = SignalEnrichedScorer()

        # High score with low quality should be promoted
        validated, details = scorer.validate_quality_level(
            question_id="Q001",
            quality_level="INSUFICIENTE",
            score=0.85,
            completeness="complete",
        )

        assert validated == "ACEPTABLE"  # Promoted
        assert details["adjusted"] is True
        assert len(details["checks"]) > 0

    def test_quality_validation_completeness_alignment(self):
        """Test quality validation with completeness alignment."""
        from farfan_pipeline.phases.Phase_03.phase3_10_00_phase3_signal_enriched_scoring import (
            SignalEnrichedScorer,
        )

        scorer = SignalEnrichedScorer()

        # Complete evidence with low quality should be promoted
        validated, details = scorer.validate_quality_level(
            question_id="Q002",
            quality_level="INSUFICIENTE",
            score=0.5,
            completeness="complete",
        )

        assert validated == "ACEPTABLE"
        assert details["adjusted"] is True

    def test_scoring_details_enrichment(self):
        """Test enrichment of scoring details with signal provenance."""
        from farfan_pipeline.phases.Phase_03.phase3_10_00_phase3_signal_enriched_scoring import (
            SignalEnrichedScorer,
        )

        scorer = SignalEnrichedScorer()

        base_details = {
            "source": "evidence_nexus",
            "method": "overall_confidence",
        }

        threshold_adj = {"adjustment": "test"}
        quality_val = {"validation": "test"}

        enriched = scorer.enrich_scoring_details(
            question_id="Q003",
            base_scoring_details=base_details,
            threshold_adjustment=threshold_adj,
            quality_validation=quality_val,
        )

        assert "signal_enrichment" in enriched
        assert enriched["signal_enrichment"]["enabled"] is True
        assert "threshold_adjustment" in enriched["signal_enrichment"]
        assert "quality_validation" in enriched["signal_enrichment"]


# Phase 4-7 Tests
class TestPhase47SignalEnrichment:
    """Test Phase 4-7 signal-enriched aggregation."""

    def test_weight_adjustment_critical_scores(self):
        """Test weight adjustment for critical scores."""
        from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
            SignalEnrichedAggregator,
        )

        aggregator = SignalEnrichedAggregator(signal_registry=None)

        base_weights = {
            "Q1": 0.2,
            "Q2": 0.2,
            "Q3": 0.2,
            "Q4": 0.2,
            "Q5": 0.2,
        }

        score_data = {
            "Q1": 0.3,  # Low but not critical
            "Q2": 0.25,  # Critical - should get boost
            "Q3": 0.8,
            "Q4": 0.7,
            "Q5": 0.6,
        }

        adjusted, details = aggregator.adjust_aggregation_weights(
            base_weights=base_weights,
            score_data=score_data,
        )

        # Q2 should have higher weight than base
        assert adjusted["Q2"] > base_weights["Q2"]
        assert len(details["adjustments"]) > 0

        # Weights should still sum to 1.0 (normalized)
        assert abs(sum(adjusted.values()) - 1.0) < 0.01

    def test_dispersion_analysis_convergence(self):
        """Test dispersion analysis with convergent scores."""
        from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
            SignalEnrichedAggregator,
        )

        aggregator = SignalEnrichedAggregator()

        # Low dispersion scores
        scores = [0.75, 0.78, 0.76, 0.77, 0.79]

        metrics, interpretation = aggregator.analyze_score_dispersion(
            scores=scores,
            context="dimension_DIM01",
        )

        assert metrics["cv"] < 0.15  # Low coefficient of variation
        assert interpretation["summary"]["dispersion_level"] == "convergence"
        assert len(interpretation["insights"]) > 0

    def test_dispersion_analysis_high_dispersion(self):
        """Test dispersion analysis with high dispersion."""
        from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
            SignalEnrichedAggregator,
        )

        aggregator = SignalEnrichedAggregator()

        # High dispersion scores
        scores = [0.2, 0.5, 0.8, 0.3, 0.9]

        metrics, interpretation = aggregator.analyze_score_dispersion(
            scores=scores,
            context="dimension_DIM02",
        )

        assert metrics["cv"] > 0.40  # High coefficient of variation
        assert interpretation["summary"]["dispersion_level"] in ["high", "extreme"]

    def test_aggregation_method_selection(self):
        """Test aggregation method selection based on dispersion."""
        from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
            SignalEnrichedAggregator,
        )

        aggregator = SignalEnrichedAggregator()

        # Extreme dispersion
        scores = [0.1, 0.9, 0.2, 0.8, 0.3]
        metrics, _ = aggregator.analyze_score_dispersion(
            scores=scores,
            context="test",
        )

        method, details = aggregator.select_aggregation_method(
            scores=scores,
            dispersion_metrics=metrics,
            context="test",
        )

        # Should recommend robust method for extreme dispersion
        assert method in ["median", "choquet"]
        assert "selected_method" in details


# Phase 8 Tests
class TestPhase8SignalEnrichment:
    """Test Phase 8 signal-enriched recommendations."""

    def test_rule_condition_enhancement_basic(self):
        """Test basic rule condition enhancement."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_signal_enriched_recommendations import (
            SignalEnrichedRecommender,
        )

        recommender = SignalEnrichedRecommender(signal_registry=None)

        condition = {
            "field": "score",
            "operator": "lt",
            "value": 0.5,
        }

        score_data = {
            "score": 0.3,
            "question_global": 1,
        }

        met, details = recommender.enhance_rule_condition(
            rule_id="RULE001",
            condition=condition,
            score_data=score_data,
        )

        assert met is True  # 0.3 < 0.5
        assert "base_evaluation" in details
        assert details["base_evaluation"]["met"] is True

    def test_intervention_priority_critical_score(self):
        """Test intervention priority for critical score."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_signal_enriched_recommendations import (
            SignalEnrichedRecommender,
        )

        recommender = SignalEnrichedRecommender()

        recommendation = {
            "rule_id": "RULE001",
            "intervention": "Improve baseline",
        }

        score_data = {
            "score": 0.25,  # Critical
            "quality_level": "INSUFICIENTE",
            "question_global": 1,
        }

        priority, details = recommender.compute_intervention_priority(
            recommendation=recommendation,
            score_data=score_data,
        )

        # Should have high priority due to critical score + insufficient quality
        assert priority > 0.7
        assert len(details["factors"]) > 0

    def test_intervention_priority_good_score(self):
        """Test intervention priority for good score (lower priority)."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_signal_enriched_recommendations import (
            SignalEnrichedRecommender,
        )

        recommender = SignalEnrichedRecommender()

        recommendation = {
            "rule_id": "RULE002",
            "intervention": "Minor improvement",
        }

        score_data = {
            "score": 0.85,
            "quality_level": "EXCELENTE",
            "question_global": 2,
        }

        priority, details = recommender.compute_intervention_priority(
            recommendation=recommendation,
            score_data=score_data,
        )

        # Should have lower priority
        assert priority < 0.7

    def test_template_selection(self):
        """Test intervention template selection."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_signal_enriched_recommendations import (
            SignalEnrichedRecommender,
        )

        recommender = SignalEnrichedRecommender()

        score_data = {
            "question_global": 1,
        }

        template_id, details = recommender.select_intervention_template(
            problem_type="insufficient_baseline",
            score_data=score_data,
        )

        assert template_id is not None
        assert "selected_template" in details


# Phase 9 Tests
class TestPhase9SignalEnrichment:
    """Test Phase 9 signal-enriched reporting."""

    def test_narrative_enrichment_low_score(self):
        """Test narrative enrichment for low score."""
        from farfan_pipeline.phases.Phase_09.phase9_10_00_signal_enriched_reporting import (
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
        from farfan_pipeline.phases.Phase_09.phase9_10_00_signal_enriched_reporting import (
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
        from farfan_pipeline.phases.Phase_09.phase9_10_00_signal_enriched_reporting import (
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
        from farfan_pipeline.phases.Phase_09.phase9_10_00_signal_enriched_reporting import (
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


# Integration Tests
class TestSignalIrrigationIntegration:
    """Test integration across multiple phases."""

    def test_phase3_to_phase47_flow(self):
        """Test signal enrichment flow from Phase 3 to Phase 4-7."""
        from farfan_pipeline.phases.Phase_03.phase3_10_00_phase3_signal_enriched_scoring import (
            SignalEnrichedScorer,
        )
        from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
            SignalEnrichedAggregator,
        )

        # Phase 3: Score with enrichment
        scorer = SignalEnrichedScorer()
        validated_quality, quality_details = scorer.validate_quality_level(
            question_id="Q001",
            quality_level="INSUFICIENTE",
            score=0.85,
            completeness="complete",
        )

        # Phase 4-7: Use score for aggregation
        aggregator = SignalEnrichedAggregator()
        scores = [0.85, 0.75, 0.80, 0.78]

        metrics, interpretation = aggregator.analyze_score_dispersion(
            scores=scores,
            context="dimension_DIM01",
        )

        # Both phases should work together
        assert validated_quality == "ACEPTABLE"
        assert metrics["cv"] < 0.15  # Convergent

    def test_phase47_to_phase8_flow(self):
        """Test signal enrichment flow from Phase 4-7 to Phase 8."""
        from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
            SignalEnrichedAggregator,
        )
        from farfan_pipeline.phases.Phase_08.phase8_30_00_signal_enriched_recommendations import (
            SignalEnrichedRecommender,
        )

        # Phase 4-7: Aggregate and analyze
        aggregator = SignalEnrichedAggregator()
        scores = [0.2, 0.3, 0.25]

        metrics, interpretation = aggregator.analyze_score_dispersion(
            scores=scores,
            context="dimension_DIM02",
        )

        mean_score = metrics["mean"]

        # Phase 8: Generate recommendations based on aggregated score
        recommender = SignalEnrichedRecommender()
        recommendation = {"rule_id": "RULE001"}
        score_data = {
            "score": mean_score,
            "quality_level": "INSUFICIENTE",
            "question_global": 1,
        }

        priority, priority_details = recommender.compute_intervention_priority(
            recommendation=recommendation,
            score_data=score_data,
        )

        # Low mean score should result in high priority
        assert mean_score < 0.4
        assert priority > 0.7

    def test_end_to_end_signal_provenance(self):
        """Test signal provenance tracking end-to-end."""
        from farfan_pipeline.phases.Phase_03.phase3_10_00_phase3_signal_enriched_scoring import (
            SignalEnrichedScorer,
        )
        from farfan_pipeline.phases.Phase_04.phase4_30_00_signal_enriched_aggregation import (
            SignalEnrichedAggregator,
        )
        from farfan_pipeline.phases.Phase_08.phase8_30_00_signal_enriched_recommendations import (
            SignalEnrichedRecommender,
        )
        from farfan_pipeline.phases.Phase_09.phase9_10_00_signal_enriched_reporting import (
            SignalEnrichedReporter,
        )

        # Create all enrichers
        scorer = SignalEnrichedScorer()
        aggregator = SignalEnrichedAggregator()
        recommender = SignalEnrichedRecommender()
        reporter = SignalEnrichedReporter()

        # Verify all have consistent initialization
        assert scorer.enable_threshold_adjustment is True
        assert aggregator.enable_weight_adjustment is True
        assert recommender.enable_pattern_matching is True
        assert reporter.enable_narrative_enrichment is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
