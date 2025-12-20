import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from canonic_phases.phase_4_7_aggregation_pipeline.aggregation import (
    AggregationSettings,
    DimensionAggregator,
    ScoredResult,
)
from orchestration.factory import get_canonical_questionnaire


def test_dimension_clamps_scores_to_range() -> None:
    monolith_path = (
        REPO_ROOT / "canonic_questionnaire_central"
        / "questionnaire_monolith.json"
    )
    monolith = get_canonical_questionnaire(
        questionnaire_path=monolith_path,
    ).data
    settings = AggregationSettings.from_monolith(monolith)

    results = [
        ScoredResult(
            question_global=1,
            base_slot="D1-Q1",
            policy_area="PA01",
            dimension="DIM01",
            score=4.5,
            quality_level="EXCELENTE",
            evidence={},
            raw_results={},
        ),
        ScoredResult(
            question_global=2,
            base_slot="D1-Q2",
            policy_area="PA01",
            dimension="DIM01",
            score=-2.0,
            quality_level="INSUFICIENTE",
            evidence={},
            raw_results={},
        ),
        ScoredResult(
            question_global=3,
            base_slot="D1-Q3",
            policy_area="PA01",
            dimension="DIM01",
            score=3.0,
            quality_level="EXCELENTE",
            evidence={},
            raw_results={},
        ),
    ]

    agg = DimensionAggregator(
        monolith=monolith,
        abort_on_insufficient=False,
        aggregation_settings=settings,
        enable_sota_features=False,
    )
    dimension_scores = agg.run(results, group_by_keys=agg.dimension_group_by_keys)
    assert dimension_scores

    ds = dimension_scores[0]
    assert 0.0 <= ds.score <= 3.0
    assert ds.validation_details["clamping"]["applied"] is True
    assert ds.validation_details["clamping"]["n_clamped"] == 2
