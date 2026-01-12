import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.aggregation import AggregationSettings


def test_normalize_weights_returns_empty_on_all_invalid() -> None:
    weight_map = {"a": -1, "b": "x", "c": None}  # type: ignore[arg-type]
    normalized = AggregationSettings._normalize_weights(weight_map)  # type: ignore[arg-type]
    assert normalized == {}
