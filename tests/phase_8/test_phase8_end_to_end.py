"""
Phase 8 End-to-End Test Suite
=============================

Validates Phase 8 recommendation flow end-to-end using canonical rules.
"""

from pathlib import Path
import json
from typing import Any, cast

import pytest


@pytest.fixture(scope="module")
def phase8_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "src" / "farfan_pipeline" / "phases" / "Phase_08"


def _load_rules(phase8_path: Path) -> dict[str, Any]:
    rules_path = phase8_path / "json_phase_eight" / "recommendation_rules_enhanced.json"
    return json.loads(rules_path.read_text())


def test_end_to_end_recommendations_generated(phase8_path: Path) -> None:
    from farfan_pipeline.phases.Phase_08.phase8_20_00_recommendation_engine import (
        RecommendationEngine,
    )

    rules_path = phase8_path / "json_phase_eight" / "recommendation_rules_enhanced.json"
    schema_path = phase8_path / "rules" / "recommendation_rules.schema.json"

    engine = RecommendationEngine(rules_path=rules_path, schema_path=schema_path)

    micro_scores = {"PA01-DIM01": 0.5, "PA02-DIM02": 1.2}
    cluster_data = {
        "CL01": {"score": 52.0, "variance": 0.2, "weak_pa": "PA02"},
        "CL02": {"score": 70.0, "variance": 0.1, "weak_pa": "PA05"},
    }
    macro_data = {
        "macro_band": "DEFICIENTE",
        "variance_alert": "ALTA",
        "clusters_below_target": ["CL01"],
        "priority_micro_gaps": ["PA01-DIM01"],
        "macro_score": 55.0,
    }

    results = engine.generate_all_recommendations(
        micro_scores=micro_scores,
        cluster_data=cluster_data,
        macro_data=macro_data,
    )

    assert "MICRO" in results
    assert "MESO" in results
    assert "MACRO" in results

    micro = results["MICRO"].to_dict()
    meso = results["MESO"].to_dict()
    macro = results["MACRO"].to_dict()

    assert isinstance(micro.get("recommendations"), list)
    assert isinstance(meso.get("recommendations"), list)
    assert isinstance(macro.get("recommendations"), list)


def test_recommendations_payload_contains_actions(phase8_path: Path) -> None:
    rules = _load_rules(phase8_path)
    samples = list(rules.get("rules", []))[:5]
    assert samples, "Expected rules present"

    for rule in samples:
        recs = rule.get("recommendations")
        assert isinstance(recs, list) and recs, "recommendations must exist"
        typed_recs = cast(list[dict[str, Any]], recs)
        for rec in typed_recs:
            assert rec.get("action"), "recommendation.action required"
            assert rec.get("expected_output"), "recommendation.expected_output required"
            assert rec.get("cost", {}).get("basis") == "score_band_scaled"
