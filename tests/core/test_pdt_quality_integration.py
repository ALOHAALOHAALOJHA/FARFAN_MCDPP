"""
Tests for PDT Quality Integration with Signal Intelligence Layer
"""

from farfan_pipeline.core.orchestrator import (
    BOOST_FACTORS,
    PDT_QUALITY_THRESHOLDS,
    PDTQualityMetrics,
    apply_pdt_quality_boost,
    compute_pdt_section_quality,
    create_enriched_signal_pack,
    track_pdt_precision_correlation,
)


class TestPDTQualityMetrics:
    """Tests for PDTQualityMetrics dataclass."""

    def test_metrics_creation(self):
        """Test creating PDTQualityMetrics."""
        metrics = PDTQualityMetrics(
            S_structural=0.90,
            M_mandatory=0.85,
            I_struct=0.88,
            I_link=0.82,
            I_logic=0.85,
            I_total=0.85,
            P_total=0.80,
            U_total=0.85,
            quality_level="excellent",
            section_name="Diagnóstico",
            boost_factor=1.5,
        )

        assert metrics.S_structural == 0.90
        assert metrics.I_struct == 0.88
        assert metrics.quality_level == "excellent"
        assert metrics.boost_factor == 1.5

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = PDTQualityMetrics(
            I_struct=0.85, quality_level="excellent", section_name="Test"
        )

        metrics_dict = metrics.to_dict()

        assert isinstance(metrics_dict, dict)
        assert "I_struct" in metrics_dict
        assert "quality_level" in metrics_dict
        assert "section_name" in metrics_dict
        assert metrics_dict["I_struct"] == 0.85


class TestComputePDTSectionQuality:
    """Tests for compute_pdt_section_quality function."""

    def test_compute_from_unit_layer_scores(self):
        """Test computing quality from pre-computed Unit Layer scores."""
        unit_scores = {
            "score": 0.88,
            "components": {
                "S": 0.92,
                "M": 0.85,
                "I": 0.88,
                "I_struct": 0.90,
                "I_link": 0.85,
                "I_logic": 0.89,
                "P": 0.85,
                "P_presence": 1.0,
                "P_struct": 0.80,
                "P_consistency": 0.75,
            },
        }

        metrics = compute_pdt_section_quality(
            "Diagnóstico", unit_layer_scores=unit_scores
        )

        assert metrics.section_name == "Diagnóstico"
        assert metrics.S_structural == 0.92
        assert metrics.M_mandatory == 0.85
        assert metrics.I_struct == 0.90
        assert metrics.I_total == 0.88
        assert metrics.U_total == 0.88
        assert metrics.quality_level == "excellent"
        assert metrics.boost_factor == BOOST_FACTORS["excellent"]

    def test_quality_level_excellent(self):
        """Test excellent quality level (I_struct>0.8)."""
        metrics = compute_pdt_section_quality(
            "Test", unit_layer_scores={"score": 0.85, "components": {"I_struct": 0.85}}
        )

        assert metrics.quality_level == "excellent"
        assert metrics.boost_factor == 1.5

    def test_quality_level_good(self):
        """Test good quality level (I_struct>0.6)."""
        metrics = compute_pdt_section_quality(
            "Test", unit_layer_scores={"score": 0.70, "components": {"I_struct": 0.65}}
        )

        assert metrics.quality_level == "good"
        assert metrics.boost_factor == 1.2

    def test_quality_level_acceptable(self):
        """Test acceptable quality level (I_struct>0.4)."""
        metrics = compute_pdt_section_quality(
            "Test", unit_layer_scores={"score": 0.50, "components": {"I_struct": 0.45}}
        )

        assert metrics.quality_level == "acceptable"
        assert metrics.boost_factor == 1.0

    def test_quality_level_poor(self):
        """Test poor quality level (I_struct<0.4)."""
        metrics = compute_pdt_section_quality(
            "Test", unit_layer_scores={"score": 0.35, "components": {"I_struct": 0.30}}
        )

        assert metrics.quality_level == "poor"
        assert metrics.boost_factor == 0.8

    def test_no_data_returns_defaults(self):
        """Test with no PDT data returns default values."""
        metrics = compute_pdt_section_quality("Empty")

        assert metrics.section_name == "Empty"
        assert metrics.I_struct == 0.0
        assert metrics.quality_level == "poor"


class TestApplyPDTQualityBoost:
    """Tests for apply_pdt_quality_boost function."""

    def test_boost_with_quality_map(self):
        """Test applying boost with quality map."""
        pdt_quality_map = {
            "Diagnóstico": PDTQualityMetrics(
                I_struct=0.90,
                quality_level="excellent",
                boost_factor=1.5,
                section_name="Diagnóstico",
            ),
            "PPI": PDTQualityMetrics(
                I_struct=0.35,
                quality_level="poor",
                boost_factor=0.8,
                section_name="PPI",
            ),
        }

        patterns = [
            {
                "id": "p1",
                "pattern": "test1",
                "pdt_section": "Diagnóstico",
                "priority": 1.0,
            },
            {"id": "p2", "pattern": "test2", "pdt_section": "PPI", "priority": 1.0},
        ]

        boosted, stats = apply_pdt_quality_boost(patterns, pdt_quality_map)

        assert len(boosted) == 2
        assert stats["total_patterns"] == 2
        assert stats["boosted_count"] == 2
        assert stats["excellent_quality"] == 1
        assert stats["poor_quality"] == 1

        p1_boosted = next(p for p in boosted if p["id"] == "p1")
        assert p1_boosted["pdt_quality_boost"] == 1.5
        assert p1_boosted["boosted_priority"] == 1.5

        p2_boosted = next(p for p in boosted if p["id"] == "p2")
        assert p2_boosted["pdt_quality_boost"] == 0.8
        assert p2_boosted["boosted_priority"] == 0.8

    def test_boost_reorders_by_priority(self):
        """Test that patterns are reordered by boosted priority."""
        pdt_quality_map = {
            "High": PDTQualityMetrics(
                I_struct=0.90,
                quality_level="excellent",
                boost_factor=1.5,
                section_name="High",
            ),
            "Low": PDTQualityMetrics(
                I_struct=0.30,
                quality_level="poor",
                boost_factor=0.8,
                section_name="Low",
            ),
        }

        patterns = [
            {"id": "p1", "pdt_section": "Low", "priority": 2.0},
            {"id": "p2", "pdt_section": "High", "priority": 1.0},
        ]

        boosted, _ = apply_pdt_quality_boost(patterns, pdt_quality_map)

        assert boosted[0]["id"] == "p1"
        assert boosted[0]["boosted_priority"] == 1.6
        assert boosted[1]["id"] == "p2"
        assert boosted[1]["boosted_priority"] == 1.5

    def test_boost_without_quality_map(self):
        """Test boost with empty quality map."""
        patterns = [{"id": "p1", "priority": 1.0}]

        boosted, stats = apply_pdt_quality_boost(patterns, {})

        assert len(boosted) == 1
        assert stats["unknown_quality"] == 1
        assert boosted[0].get("pdt_quality_boost", 1.0) == 1.0

    def test_boost_stats_aggregation(self):
        """Test boost statistics aggregation."""
        pdt_quality_map = {
            "E1": PDTQualityMetrics(
                quality_level="excellent", boost_factor=1.5, section_name="E1"
            ),
            "E2": PDTQualityMetrics(
                quality_level="excellent", boost_factor=1.5, section_name="E2"
            ),
            "G1": PDTQualityMetrics(
                quality_level="good", boost_factor=1.2, section_name="G1"
            ),
            "A1": PDTQualityMetrics(
                quality_level="acceptable", boost_factor=1.0, section_name="A1"
            ),
            "P1": PDTQualityMetrics(
                quality_level="poor", boost_factor=0.8, section_name="P1"
            ),
        }

        patterns = [
            {"id": f"p{i}", "pdt_section": section, "priority": 1.0}
            for i, section in enumerate(["E1", "E2", "G1", "A1", "P1"])
        ]

        _, stats = apply_pdt_quality_boost(patterns, pdt_quality_map)

        assert stats["excellent_quality"] == 2
        assert stats["good_quality"] == 1
        assert stats["acceptable_quality"] == 1
        assert stats["poor_quality"] == 1
        assert stats["max_boost_factor"] == 1.5
        assert 1.0 <= stats["avg_boost_factor"] <= 1.5


class TestTrackPDTPrecisionCorrelation:
    """Tests for track_pdt_precision_correlation function."""

    def test_correlation_tracking(self):
        """Test correlation tracking between quality and retention."""
        pdt_quality_map = {
            "High": PDTQualityMetrics(
                I_struct=0.90, quality_level="excellent", section_name="High"
            ),
            "Low": PDTQualityMetrics(
                I_struct=0.30, quality_level="poor", section_name="Low"
            ),
        }

        patterns_before = [
            {"id": "p1", "pdt_section": "High"},
            {"id": "p2", "pdt_section": "High"},
            {"id": "p3", "pdt_section": "Low"},
            {"id": "p4", "pdt_section": "Low"},
        ]

        patterns_after = [{"id": "p1"}, {"id": "p2"}, {"id": "p3"}]

        corr = track_pdt_precision_correlation(
            patterns_before, patterns_after, pdt_quality_map
        )

        assert corr["total_patterns_before"] == 4
        assert corr["total_patterns_after"] == 3
        assert corr["patterns_from_high_quality"] == 2
        assert corr["patterns_from_low_quality"] == 2
        assert corr["high_quality_retention_rate"] == 1.0
        assert corr["low_quality_retention_rate"] == 0.5
        assert corr["quality_correlation"] > 0

    def test_threshold_effectiveness(self):
        """Test threshold effectiveness calculation."""
        pdt_quality_map = {
            "Excellent": PDTQualityMetrics(I_struct=0.85, section_name="Excellent"),
            "Good": PDTQualityMetrics(I_struct=0.65, section_name="Good"),
            "Poor": PDTQualityMetrics(I_struct=0.35, section_name="Poor"),
        }

        patterns_before = [
            {"id": "p1", "pdt_section": "Excellent"},
            {"id": "p2", "pdt_section": "Good"},
            {"id": "p3", "pdt_section": "Poor"},
        ]

        patterns_after = [{"id": "p1"}, {"id": "p2"}]

        corr = track_pdt_precision_correlation(
            patterns_before, patterns_after, pdt_quality_map
        )

        assert "I_struct_threshold_effectiveness" in corr

        threshold_metrics = corr["I_struct_threshold_effectiveness"]
        assert "I_struct>0.8" in threshold_metrics
        assert "I_struct>0.6" in threshold_metrics
        assert "I_struct>0.4" in threshold_metrics

    def test_empty_quality_map(self):
        """Test with empty quality map."""
        corr = track_pdt_precision_correlation([{"id": "p1"}], [{"id": "p1"}], {})

        assert corr["total_patterns_before"] == 1
        assert corr["total_patterns_after"] == 1
        assert corr["patterns_from_high_quality"] == 0


class TestEnrichedSignalPackPDTIntegration:
    """Tests for PDT quality integration in EnrichedSignalPack."""

    def test_create_with_pdt_quality_map(self):
        """Test creating enriched pack with PDT quality map."""
        mock_pack = {"patterns": [{"id": "p1"}]}

        pdt_quality_map = {
            "Test": PDTQualityMetrics(I_struct=0.85, section_name="Test")
        }

        enriched = create_enriched_signal_pack(
            mock_pack, enable_semantic_expansion=False, pdt_quality_map=pdt_quality_map
        )

        assert enriched is not None
        assert enriched._pdt_quality_map == pdt_quality_map

    def test_add_pdt_section_quality(self):
        """Test adding section quality dynamically."""
        mock_pack = {"patterns": []}

        enriched = create_enriched_signal_pack(
            mock_pack, enable_semantic_expansion=False
        )

        unit_scores = {"score": 0.85, "components": {"I_struct": 0.90}}
        metrics = enriched.add_pdt_section_quality(
            "NewSection", unit_layer_scores=unit_scores
        )

        assert metrics.section_name == "NewSection"
        assert "NewSection" in enriched._pdt_quality_map

    def test_get_pdt_quality_summary(self):
        """Test getting PDT quality summary."""
        mock_pack = {"patterns": []}

        pdt_quality_map = {
            "S1": PDTQualityMetrics(
                I_struct=0.90,
                quality_level="excellent",
                U_total=0.88,
                section_name="S1",
            ),
            "S2": PDTQualityMetrics(
                I_struct=0.65, quality_level="good", U_total=0.68, section_name="S2"
            ),
        }

        enriched = create_enriched_signal_pack(
            mock_pack, enable_semantic_expansion=False, pdt_quality_map=pdt_quality_map
        )

        summary = enriched.get_pdt_quality_summary()

        assert summary["total_sections"] == 2
        assert summary["avg_I_struct"] == (0.90 + 0.65) / 2
        assert summary["quality_distribution"]["excellent"] == 1
        assert summary["quality_distribution"]["good"] == 1
        assert len(summary["sections"]) == 2

    def test_get_patterns_with_pdt_boost(self):
        """Test get_patterns_for_context with PDT boost enabled."""
        mock_pack = {
            "patterns": [
                {"id": "p1", "pdt_section": "High", "context_scope": "global"},
                {"id": "p2", "pdt_section": "Low", "context_scope": "global"},
            ]
        }

        pdt_quality_map = {
            "High": PDTQualityMetrics(
                I_struct=0.90,
                quality_level="excellent",
                boost_factor=1.5,
                section_name="High",
            ),
            "Low": PDTQualityMetrics(
                I_struct=0.30,
                quality_level="poor",
                boost_factor=0.8,
                section_name="Low",
            ),
        }

        enriched = create_enriched_signal_pack(
            mock_pack, enable_semantic_expansion=False, pdt_quality_map=pdt_quality_map
        )

        patterns, stats = enriched.get_patterns_for_context(
            {}, track_precision_improvement=True, enable_pdt_boost=True
        )

        assert "pdt_quality_boost" in stats
        assert stats["pdt_quality_boost"]["boosted_count"] == 2
        assert "pdt_precision_correlation" in stats


class TestPDTQualityConstants:
    """Tests for PDT quality thresholds and boost factors."""

    def test_quality_thresholds(self):
        """Test quality threshold constants."""
        assert PDT_QUALITY_THRESHOLDS["I_struct_excellent"] == 0.8
        assert PDT_QUALITY_THRESHOLDS["I_struct_good"] == 0.6
        assert PDT_QUALITY_THRESHOLDS["I_struct_acceptable"] == 0.4

    def test_boost_factors(self):
        """Test boost factor constants."""
        assert BOOST_FACTORS["excellent"] == 1.5
        assert BOOST_FACTORS["good"] == 1.2
        assert BOOST_FACTORS["acceptable"] == 1.0
        assert BOOST_FACTORS["poor"] == 0.8

    def test_threshold_hierarchy(self):
        """Test that thresholds form proper hierarchy."""
        thresholds = [
            PDT_QUALITY_THRESHOLDS["I_struct_excellent"],
            PDT_QUALITY_THRESHOLDS["I_struct_good"],
            PDT_QUALITY_THRESHOLDS["I_struct_acceptable"],
        ]

        assert thresholds == sorted(thresholds, reverse=True)

    def test_boost_factor_hierarchy(self):
        """Test that boost factors form proper hierarchy."""
        factors = [
            BOOST_FACTORS["excellent"],
            BOOST_FACTORS["good"],
            BOOST_FACTORS["acceptable"],
            BOOST_FACTORS["poor"],
        ]

        assert factors == sorted(factors, reverse=True)
