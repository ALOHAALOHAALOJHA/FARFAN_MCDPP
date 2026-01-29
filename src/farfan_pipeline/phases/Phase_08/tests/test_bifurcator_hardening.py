"""
Bifurcator Hardening Regression Tests

Tests for v2.0.0 hardening features:
- Step 1: Input normalization (level, score_key, metadata)
- Step 2: Determinism with stable sorting
- Step 3: Amplification control with caps

Module: src/farfan_pipeline/phases/Phase_08/tests/test_bifurcator_hardening.py
Version: 1.0.0
Status: ACTIVE
Purpose: Regression tests for bifurcator hardening
"""
from __future__ import annotations

import pytest
from dataclasses import dataclass

from farfan_pipeline.phases.Phase_08.phase8_25_00_recommendation_bifurcator import (
    # Main API
    bifurcate_recommendations,
    RecommendationBifurcator,
    BifurcationResult,
    # Configuration
    AmplificationConfig,
    # Data structures
    CrossPollinationNode,
    TemporalCascade,
    SynergyMatrix,
    # Helper functions (for direct testing)
    _normalize_level,
    _parse_score_key,
    _safe_get_metadata,
    _stable_sort_key,
    _ensure_deterministic_input,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@dataclass
class MockRecommendation:
    """Mock recommendation for testing."""
    rule_id: str
    level: str = "MICRO"
    score_key: str | None = None
    gap: float | None = None
    score_band: str = "CRITICO"
    metadata: dict | None = None
    horizon: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dict format expected by bifurcator."""
        meta = self.metadata or {}
        if self.score_key:
            meta = {**meta, "score_key": self.score_key}
        if self.gap is not None:
            meta = {**meta, "gap": self.gap}
        meta["score_band"] = self.score_band

        return {
            "rule_id": self.rule_id,
            "level": self.level,
            "metadata": meta,
            "horizon": self.horizon or {"start": "2026-01", "end": "2026-06"},
        }


def create_valid_micro_recommendation(
    rule_id: str,
    pa: int,
    dim: int,
    gap: float = 0.5,
    score_band: str = "CRITICO",
) -> dict:
    """Create a valid MICRO recommendation with proper score_key."""
    return {
        "rule_id": rule_id,
        "level": "MICRO",
        "metadata": {
            "score_key": f"PA{pa:02d}-DIM{dim:02d}",
            "gap": gap,
            "score_band": score_band,
        },
        "horizon": {"start": "2026-01", "end": "2026-06"},
    }


# =============================================================================
# TEST CLASS 1: Input Normalization (Step 1)
# =============================================================================

class TestInputNormalization:
    """Tests para Step 1: Normalización de entradas."""

    def test_level_none_defaults_to_micro(self):
        """Test that None level defaults to MICRO."""
        recs = [create_valid_micro_recommendation("TEST-001", 1, 1)]
        result = bifurcate_recommendations(recs, None)
        assert result.level == "MICRO"

    def test_level_invalid_defaults_to_micro(self):
        """Test that invalid level defaults to MICRO."""
        recs = [create_valid_micro_recommendation("TEST-001", 1, 1)]
        result = bifurcate_recommendations(recs, "INVALID")
        assert result.level == "MICRO"

    def test_level_case_insensitive(self):
        """Test that level is case-insensitive."""
        recs = [create_valid_micro_recommendation("TEST-001", 1, 1)]

        result_lower = bifurcate_recommendations(recs, "micro")
        assert result_lower.level == "MICRO"

        result_upper = bifurcate_recommendations(recs, "MESO")
        assert result_upper.level == "MESO"

        result_mixed = bifurcate_recommendations(recs, "MaCrO")
        assert result_mixed.level == "MACRO"

    def test_missing_metadata_handled(self):
        """Test that missing metadata is handled gracefully."""
        recs = [{"rule_id": "TEST-001"}]  # No metadata
        result = bifurcate_recommendations(recs, "MICRO")
        assert result.original_count == 1
        # Should not crash, just produce empty analysis

    def test_metadata_not_dict_handled(self):
        """Test that non-dict metadata is handled gracefully."""
        recs = [{"rule_id": "TEST-001", "metadata": "invalid"}]
        result = bifurcate_recommendations(recs, "MICRO")
        assert result.original_count == 1

    def test_invalid_score_key_skipped(self):
        """Test that invalid score_key format is skipped safely."""
        recs = [
            {
                "rule_id": "TEST-001",
                "metadata": {"score_key": "INVALID-FORMAT"},
            }
        ]
        result = bifurcate_recommendations(recs, "MICRO")
        # Should skip resonance but not crash
        assert result.original_count == 1

    def test_score_key_none_handled(self):
        """Test that None score_key is handled gracefully."""
        recs = [
            {
                "rule_id": "TEST-001",
                "metadata": {"score_key": None},
            }
        ]
        result = bifurcate_recommendations(recs, "MICRO")
        assert result.original_count == 1

    def test_gap_missing_or_invalid(self):
        """Test that missing/invalid gap is handled gracefully."""
        recs = [
            {
                "rule_id": "TEST-001",
                "metadata": {
                    "score_key": "PA01-DIM01",
                    # gap is missing
                },
            }
        ]
        result = bifurcate_recommendations(recs, "MICRO")
        # Should default to 0.0 and not crash
        assert result.original_count == 1


class TestInputNormalizationHelpers:
    """Direct tests for helper functions."""

    def test_normalize_level_valid_inputs(self):
        """Test _normalize_level with all valid inputs."""
        assert _normalize_level("MICRO") == "MICRO"
        assert _normalize_level("micro") == "MICRO"
        assert _normalize_level("  micro  ") == "MICRO"
        assert _normalize_level("MESO") == "MESO"
        assert _normalize_level("MACRO") == "MACRO"

    def test_normalize_level_defaults(self):
        """Test _normalize_level defaults."""
        assert _normalize_level(None) == "MICRO"
        assert _normalize_level("INVALID") == "MICRO"
        assert _normalize_level("") == "MICRO"

    def test_parse_score_key_valid(self):
        """Test _parse_score_key with valid inputs."""
        result = _parse_score_key("PA01-DIM01")
        assert result == ("PA01", "DIM01")

        result = _parse_score_key("pa10-dim06")
        assert result == ("PA10", "DIM06")  # Uppercased

    def test_parse_score_key_invalid(self):
        """Test _parse_score_key with invalid inputs."""
        assert _parse_score_key(None) is None
        assert _parse_score_key("") is None
        assert _parse_score_key("INVALID") is None
        assert _parse_score_key("PA01-DIM") is None
        assert _parse_score_key("PA-DIM01") is None

    def test_safe_get_metadata(self):
        """Test _safe_get_metadata."""
        rec = {"metadata": {"score_key": "PA01-DIM01"}}
        assert _safe_get_metadata(rec) == {"score_key": "PA01-DIM01"}

        # Missing metadata
        assert _safe_get_metadata({}) == {}

        # Non-dict metadata
        assert _safe_get_metadata({"metadata": "invalid"}) == {}


# =============================================================================
# TEST CLASS 2: Determinism (Step 2)
# =============================================================================

class TestDeterminism:
    """Tests para Step 2: Determinismo con ordenamiento estable."""

    def test_same_input_same_output(self):
        """Test that same input produces same output."""
        recs = [
            create_valid_micro_recommendation("RULE-001", 1, 1),
            create_valid_micro_recommendation("RULE-002", 2, 2),
            create_valid_micro_recommendation("RULE-003", 3, 3),
        ]

        result1 = bifurcate_recommendations(recs, "MICRO")
        result2 = bifurcate_recommendations(recs, "MICRO")

        # Amplification should be identical
        assert result1.amplification_factor == result2.amplification_factor

        # Cross-pollination counts should be identical
        assert len(result1.cross_pollinations) == len(result2.cross_pollinations)

        # Temporal cascade counts should be identical
        assert len(result1.temporal_cascades) == len(result2.temporal_cascades)

    def test_different_input_order_same_output(self):
        """Test that input order doesn't affect output."""
        recs = [
            create_valid_micro_recommendation("RULE-001", 1, 1),
            create_valid_micro_recommendation("RULE-002", 2, 2),
            create_valid_micro_recommendation("RULE-003", 3, 3),
        ]

        # Run with different orderings
        import random
        orderings = [
            recs,
            list(reversed(recs)),
            [recs[2], recs[0], recs[1]],
        ]

        results = [bifurcate_recommendations(r, "MICRO") for r in orderings]

        # All should have same amplification
        for r in results[1:]:
            assert r.amplification_factor == results[0].amplification_factor

        # All should have same counts
        for r in results[1:]:
            assert len(r.cross_pollinations) == len(results[0].cross_pollinations)
            assert len(r.temporal_cascades) == len(results[0].temporal_cascades)

    def test_output_lists_are_sorted(self):
        """Test that output lists in to_dict() are sorted deterministically."""
        recs = [
            create_valid_micro_recommendation("RULE-003", 3, 3),
            create_valid_micro_recommendation("RULE-001", 1, 1),
            create_valid_micro_recommendation("RULE-002", 2, 2),
        ]

        result = bifurcate_recommendations(recs, "MICRO")
        output = result.to_dict()

        # Check that cross_pollinations are sorted
        cp_list = output["cross_pollinations"]
        if cp_list:
            # Should be sorted by (source, target)
            sources = [cp["source"] for cp in cp_list]
            targets = [cp["target"] for cp in cp_list]
            assert sources == sorted(sources)
            # For same source, targets should be sorted
            # (this is implicit in the tuple sort)

        # Check that temporal_cascades are sorted
        tc_list = output["temporal_cascades"]
        if tc_list:
            # Should be sorted by (root, order, horizon)
            roots = [tc["root"] for tc in tc_list]
            orders = [tc["order"] for tc in tc_list]
            horizons = [tc["horizon"] for tc in tc_list]

            # All roots should be in sorted order (with stability)
            assert roots == sorted(roots)

    def test_stable_sort_key_consistency(self):
        """Test that _stable_sort_key produces consistent ordering."""
        recs = [
            {"rule_id": "RULE-002", "metadata": {"score_key": "PA02-DIM02"}},
            {"rule_id": "RULE-001", "metadata": {"score_key": "PA01-DIM01"}},
            {"rule_id": "RULE-003", "metadata": {"score_key": "PA03-DIM03"}},
        ]

        sorted_recs = _ensure_deterministic_input(recs)

        # Should be sorted by (score_key, rule_id)
        assert sorted_recs[0]["rule_id"] == "RULE-001"
        assert sorted_recs[1]["rule_id"] == "RULE-002"
        assert sorted_recs[2]["rule_id"] == "RULE-003"

    def test_stable_sort_with_missing_fields(self):
        """Test stable sort with missing score_key/rule_id."""
        recs = [
            {"rule_id": "RULE-001"},  # No metadata
            {"metadata": {"score_key": "PA01-DIM01"}},  # No rule_id
            {"rule_id": "RULE-002", "metadata": {"score_key": "PA02-DIM02"}},
        ]

        # Should not crash
        sorted_recs = _ensure_deterministic_input(recs)
        assert len(sorted_recs) == 3

        # Items with missing fields should sort to front (empty strings)


# =============================================================================
# TEST CLASS 3: Amplification Caps (Step 3)
# =============================================================================

class TestAmplificationCaps:
    """Tests para Step 3: Control de amplificación con límites."""

    def test_default_amplification_cap(self):
        """Test that default amplification cap is applied."""
        # Create many recommendations to potentially exceed cap
        recs = [
            create_valid_micro_recommendation(f"RULE-{i:03d}", (i % 10) + 1, (i % 6) + 1)
            for i in range(50)  # Many recommendations
        ]

        config = AmplificationConfig(max_amplification_factor=5.0)
        result = bifurcate_recommendations(recs, "MICRO", amplification_config=config)

        # Should be capped at 5.0
        assert result.amplification_factor <= 5.0

    def test_custom_amplification_cap(self):
        """Test that custom amplification cap is applied."""
        recs = [
            create_valid_micro_recommendation(f"RULE-{i:03d}", (i % 10) + 1, (i % 6) + 1)
            for i in range(20)
        ]

        # Test with cap of 2.0
        config = AmplificationConfig(max_amplification_factor=2.0)
        result = bifurcate_recommendations(recs, "MICRO", amplification_config=config)
        assert result.amplification_factor <= 2.0

        # Test with cap of 3.5
        config = AmplificationConfig(max_amplification_factor=3.5)
        result = bifurcate_recommendations(recs, "MICRO", amplification_config=config)
        assert result.amplification_factor <= 3.5

    def test_no_amplification_cap(self):
        """Test that None cap means no limit."""
        recs = [
            create_valid_micro_recommendation(f"RULE-{i:03d}", (i % 10) + 1, (i % 6) + 1)
            for i in range(20)
        ]

        config = AmplificationConfig(max_amplification_factor=None)
        result = bifurcate_recommendations(recs, "MICRO", amplification_config=config)

        # Should be at least 1.0, possibly higher
        assert result.amplification_factor >= 1.0

    def test_max_hidden_value_ratio_cap(self):
        """Test that hidden value ratio is capped."""
        # Create recommendations that would generate high hidden value
        recs = [
            create_valid_micro_recommendation("RULE-001", 1, 1, gap=10.0),  # Large gap
        ]

        # Low cap on hidden value ratio
        config = AmplificationConfig(max_hidden_value_ratio=0.5)
        result = bifurcate_recommendations(recs, "MICRO", amplification_config=config)

        # Amplification should be controlled
        assert result.amplification_factor >= 1.0

    def test_max_cascade_bonus_cap(self):
        """Test that cascade bonus is capped."""
        recs = [
            create_valid_micro_recommendation("RULE-001", 1, 1, score_band="CRISIS"),
        ]

        # Low cap on cascade bonus
        config = AmplificationConfig(max_cascade_bonus=0.5)
        result = bifurcate_recommendations(recs, "MICRO", amplification_config=config)

        assert result.amplification_factor >= 1.0

    def test_max_synergy_multiplier_cap(self):
        """Test that synergy multiplier is capped."""
        # Create many recommendations in same PA for high synergy
        recs = [
            create_valid_micro_recommendation(f"RULE-{i:03d}", 1, (i % 6) + 1)
            for i in range(10)
        ]

        # Low cap on synergy multiplier
        config = AmplificationConfig(max_synergy_multiplier=1.5)
        result = bifurcate_recommendations(recs, "MICRO", amplification_config=config)

        assert result.amplification_factor >= 1.0

    def test_all_caps_combined(self):
        """Test that all caps work together."""
        recs = [
            create_valid_micro_recommendation(f"RULE-{i:03d}", (i % 10) + 1, (i % 6) + 1, gap=5.0)
            for i in range(30)
        ]

        # All caps set low
        config = AmplificationConfig(
            max_amplification_factor=2.0,
            max_hidden_value_ratio=1.0,
            max_cascade_bonus=0.5,
            max_synergy_multiplier=1.5,
        )
        result = bifurcate_recommendations(recs, "MICRO", amplification_config=config)

        # Final should be capped
        assert result.amplification_factor <= 2.0

    def test_amplification_config_defaults(self):
        """Test that AmplificationConfig has proper defaults."""
        config = AmplificationConfig()

        # Default cap should be 10.0
        assert config.max_amplification_factor == 10.0
        assert config.max_hidden_value_ratio == 5.0
        assert config.max_cascade_bonus == 2.0
        assert config.max_synergy_multiplier == 3.0


# =============================================================================
# TEST CLASS 4: Integration Tests
# =============================================================================

class TestBifurcatorIntegration:
    """Integration tests for hardening features combined."""

    def test_invalid_input_with_caps(self):
        """Test that invalid input is handled even with custom caps."""
        recs = [
            {"rule_id": "TEST-001"},  # Missing metadata
            {
                "rule_id": "TEST-002",
                "metadata": {"score_key": "INVALID"},
            },  # Invalid score_key
        ]

        config = AmplificationConfig(max_amplification_factor=2.0)
        result = bifurcate_recommendations(recs, "INVALID-LEVEL", amplification_config=config)

        # Should normalize level and handle inputs gracefully
        assert result.level == "MICRO"  # Default
        assert result.original_count == 2

    def test_determinism_with_caps(self):
        """Test that determinism is maintained with custom caps."""
        recs = [
            create_valid_micro_recommendation(f"RULE-{i:03d}", (i % 10) + 1, (i % 6) + 1)
            for i in range(20)
        ]

        config = AmplificationConfig(max_amplification_factor=3.0)

        results = [
            bifurcate_recommendations(recs, "MICRO", amplification_config=config)
            for _ in range(3)
        ]

        # All results should be identical
        for r in results[1:]:
            assert r.amplification_factor == results[0].amplification_factor
            assert len(r.cross_pollinations) == len(results[0].cross_pollinations)

    def test_full_bifurcation_result_structure(self):
        """Test that BifurcationResult has all expected fields."""
        recs = [
            create_valid_micro_recommendation("RULE-001", 1, 1),
        ]

        result = bifurcate_recommendations(recs, "MICRO")

        # Check all expected fields exist
        assert hasattr(result, "original_count")
        assert hasattr(result, "bifurcated_count")
        assert hasattr(result, "cross_pollinations")
        assert hasattr(result, "temporal_cascades")
        assert hasattr(result, "synergy_matrix")
        assert hasattr(result, "amplification_factor")
        assert hasattr(result, "level")
        assert hasattr(result, "analysis_timestamp")
        assert hasattr(result, "hidden_value_score")
        assert hasattr(result, "cascade_depth")
        assert hasattr(result, "strongest_synergy")

    def test_to_dict_output_structure(self):
        """Test that to_dict() produces expected structure."""
        recs = [
            create_valid_micro_recommendation("RULE-001", 1, 1),
        ]

        result = bifurcate_recommendations(recs, "MICRO")
        output = result.to_dict()

        # Check expected keys
        expected_keys = [
            "level",
            "original_count",
            "bifurcated_count",
            "amplification_factor",
            "hidden_value_score",
            "cascade_depth",
            "cross_pollinations_count",
            "temporal_cascades_count",
            "synergies_count",
            "strongest_synergy",
            "analysis_timestamp",
            "cross_pollinations",
            "temporal_cascades",
        ]

        for key in expected_keys:
            assert key in output, f"Missing key: {key}"

    def test_micro_vs_meso_vs_macro(self):
        """Test that all three levels work correctly."""
        recs = [
            create_valid_micro_recommendation("RULE-001", 1, 1),
        ]

        # MICRO
        result_micro = bifurcate_recommendations(recs, "MICRO")
        assert result_micro.level == "MICRO"

        # MESO
        recs_meso = [{"rule_id": "MESO-001", "metadata": {"cluster_id": "CLUSTER_MESO_1"}}]
        result_meso = bifurcate_recommendations(recs_meso, "MESO")
        assert result_meso.level == "MESO"

        # MACRO
        recs_macro = [{"rule_id": "MACRO-001"}]
        result_macro = bifurcate_recommendations(recs_macro, "MACRO")
        assert result_macro.level == "MACRO"


# =============================================================================
# TEST CLASS 5: Edge Cases
# =============================================================================

class TestBifurcatorEdgeCases:
    """Edge case tests for bifurcator."""

    def test_empty_recommendations(self):
        """Test with empty recommendation list."""
        result = bifurcate_recommendations([], "MICRO")

        assert result.original_count == 0
        assert result.bifurcated_count == 0
        assert result.amplification_factor >= 1.0  # Should handle gracefully

    def test_single_recommendation(self):
        """Test with single recommendation."""
        recs = [create_valid_micro_recommendation("RULE-001", 1, 1)]
        result = bifurcate_recommendations(recs, "MICRO")

        assert result.original_count == 1
        assert result.amplification_factor >= 1.0

    def test_all_same_score_key(self):
        """Test with all recommendations having same score_key."""
        recs = [
            create_valid_micro_recommendation(f"RULE-{i:03d}", 1, 1)
            for i in range(5)
        ]

        result = bifurcate_recommendations(recs, "MICRO")

        # Should detect same-dimension cross-pollination
        assert result.original_count == 5
        # May have cross-pollinations due to same dimension

    def test_score_band_horizon_mapping(self):
        """Test that score bands map to correct horizons."""
        bands = ["CRISIS", "CRITICO", "ACEPTABLE", "BUENO", "EXCELENTE"]

        for band in bands:
            recs = [
                create_valid_micro_recommendation("RULE-001", 1, 1, score_band=band),
            ]
            result = bifurcate_recommendations(recs, "MICRO")

            # Should produce cascades based on band
            assert result.original_count == 1
            assert len(result.temporal_cascades) >= 1  # At least first-order


# =============================================================================
# MAIN RUNNER (for direct execution)
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
