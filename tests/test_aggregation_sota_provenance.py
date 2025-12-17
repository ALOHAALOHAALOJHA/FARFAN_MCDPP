import json
from pathlib import Path

from canonic_phases.Phase_four_five_six_seven.aggregation import (
    AggregationSettings,
    DimensionAggregator,
    validate_scored_results,
)


def test_sota_provenance_handles_string_qids() -> None:
    monolith_path = (
        Path(__file__).resolve().parent.parent
        / "canonic_questionnaire_central"
        / "questionnaire_monolith.json"
    )
    monolith = json.loads(monolith_path.read_text(encoding="utf-8"))
    settings = AggregationSettings.from_monolith(monolith)

    results = validate_scored_results(
        [
            {
                "question_global": "Q001",
                "base_slot": "D1-Q1",
                "policy_area": "PA01",
                "dimension": "DIM01",
                "score": 2.0,
                "quality_level": "ACEPTABLE",
                "evidence": {},
                "raw_results": {},
            },
            {
                "question_global": "Q002",
                "base_slot": "D1-Q2",
                "policy_area": "PA01",
                "dimension": "DIM01",
                "score": 2.5,
                "quality_level": "BUENO",
                "evidence": {},
                "raw_results": {},
            },
            {
                "question_global": "QABC",
                "base_slot": "D1-Q3",
                "policy_area": "PA01",
                "dimension": "DIM01",
                "score": 1.5,
                "quality_level": "ACEPTABLE",
                "evidence": {},
                "raw_results": {},
            },
        ]
    )

    agg = DimensionAggregator(
        monolith=monolith,
        abort_on_insufficient=False,
        aggregation_settings=settings,
        enable_sota_features=True,
    )
    dimension_scores = agg.run(results, group_by_keys=agg.dimension_group_by_keys)
    assert dimension_scores

    ds = dimension_scores[0]
    assert ds.provenance_node_id == "DIM_DIM01_PA01"
    assert "Q001" in agg.provenance_dag.nodes
    assert "Q002" in agg.provenance_dag.nodes
    assert "QABC" in agg.provenance_dag.nodes

