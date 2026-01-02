"""
ADVERSARIAL TESTS FOR TYPE DEFAULTS
====================================
These tests verify type-specific calibration defaults and prohibited operations.
"""
import pytest
from src.farfan_pipeline.infrastructure.calibration import (
    get_type_defaults,
    is_operation_prohibited,
    PROHIBITED_OPERATIONS,
)


class TestTypeDefaultsLoading:
    """Test loading of type-specific defaults from epistemic_minima_by_type.json."""

    def test_type_a_defaults_loaded(self) -> None:
        """TYPE_A defaults must be loadable."""
        defaults = get_type_defaults("TYPE_A")
        assert "n1_ratio" in defaults
        assert "n2_ratio" in defaults
        assert "n3_ratio" in defaults
        assert "veto_threshold" in defaults
        assert "prior_strength" in defaults

    def test_type_b_defaults_loaded(self) -> None:
        """TYPE_B defaults must be loadable."""
        defaults = get_type_defaults("TYPE_B")
        assert "prior_strength" in defaults
        # TYPE_B should have stronger priors
        assert defaults["prior_strength"].default_value == 2.0

    def test_type_e_strictest_veto_threshold(self) -> None:
        """TYPE_E must have strictest veto threshold."""
        defaults_e = get_type_defaults("TYPE_E")
        assert defaults_e["veto_threshold"].min_value == 0.01

    def test_type_d_most_lenient_veto_threshold(self) -> None:
        """TYPE_D must have most lenient veto threshold."""
        defaults_d = get_type_defaults("TYPE_D")
        assert defaults_d["veto_threshold"].max_value == 0.10

    def test_unknown_type_raises(self) -> None:
        """Unknown contract type must raise KeyError."""
        with pytest.raises(KeyError, match="Unknown contract type"):
            get_type_defaults("TYPE_INVALID")

    def test_flyweight_pattern_caching(self) -> None:
        """Same type should return cached instance (flyweight pattern)."""
        defaults1 = get_type_defaults("TYPE_A")
        defaults2 = get_type_defaults("TYPE_A")
        # Should be the exact same dict instance due to caching
        assert defaults1 is defaults2


class TestProhibitedOperations:
    """Test prohibited operations enforcement."""

    def test_type_a_prohibitions(self) -> None:
        """TYPE_A must prohibit weighted_mean and concat_only."""
        assert is_operation_prohibited("TYPE_A", "weighted_mean")
        assert is_operation_prohibited("TYPE_A", "concat_only")
        assert not is_operation_prohibited("TYPE_A", "semantic_triangulation")

    def test_type_b_prohibitions(self) -> None:
        """TYPE_B must prohibit weighted_mean and simple_concat."""
        assert is_operation_prohibited("TYPE_B", "weighted_mean")
        assert is_operation_prohibited("TYPE_B", "simple_concat")
        assert not is_operation_prohibited("TYPE_B", "bayesian_update")

    def test_type_c_prohibitions(self) -> None:
        """TYPE_C must prohibit concat_only and weighted_mean."""
        assert is_operation_prohibited("TYPE_C", "concat_only")
        assert is_operation_prohibited("TYPE_C", "weighted_mean")
        assert not is_operation_prohibited("TYPE_C", "topological_overlay")

    def test_type_d_prohibitions(self) -> None:
        """TYPE_D must prohibit concat_only and simple_concat."""
        assert is_operation_prohibited("TYPE_D", "concat_only")
        assert is_operation_prohibited("TYPE_D", "simple_concat")
        assert not is_operation_prohibited("TYPE_D", "weighted_mean")

    def test_type_e_no_averaging(self) -> None:
        """TYPE_E CRITICAL: must prohibit ALL forms of averaging."""
        assert is_operation_prohibited("TYPE_E", "weighted_mean")
        assert is_operation_prohibited("TYPE_E", "average")
        assert is_operation_prohibited("TYPE_E", "mean")
        assert is_operation_prohibited("TYPE_E", "avg")
        assert not is_operation_prohibited("TYPE_E", "min_consistency")

    def test_case_insensitive_checking(self) -> None:
        """Prohibition checking must be case-insensitive."""
        assert is_operation_prohibited("TYPE_E", "WEIGHTED_MEAN")
        assert is_operation_prohibited("TYPE_E", "Average")
        assert is_operation_prohibited("TYPE_E", "MEAN")

    def test_substring_matching(self) -> None:
        """Operations containing prohibited terms must be caught."""
        assert is_operation_prohibited("TYPE_E", "compute_weighted_mean_value")
        assert is_operation_prohibited("TYPE_E", "calculate_average_score")

    def test_prohibited_operations_immutable(self) -> None:
        """PROHIBITED_OPERATIONS must be immutable."""
        prohibited = PROHIBITED_OPERATIONS["TYPE_E"]
        assert isinstance(prohibited, frozenset)
        with pytest.raises(AttributeError):
            prohibited.add("new_operation")  # type: ignore[union-attr]
