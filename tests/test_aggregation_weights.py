from canonic_phases.Phase_four_five_six_seven.aggregation import AggregationSettings


def test_normalize_weights_returns_empty_on_all_invalid() -> None:
    weight_map = {"a": -1, "b": "x", "c": None}  # type: ignore[arg-type]
    normalized = AggregationSettings._normalize_weights(weight_map)  # type: ignore[arg-type]
    assert normalized == {}

