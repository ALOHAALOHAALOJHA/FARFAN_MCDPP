"""
ADVERSARIAL TESTS FOR TYPE DEFAULTS v2.0.0
==========================================
These tests verify type-specific calibration defaults and prohibited operations.

Schema Version: 2.0.0
"""
import pytest
from src.farfan_pipeline.infrastructure.calibration import (
    get_type_defaults,
    is_operation_prohibited,
    PROHIBITED_OPERATIONS,
)


class TestTypeDefaultsLoading:
    """Test loading of type-specific defaults from canonical source."""

    def test_type_a_defaults_loaded(self) -> None:
        """TYPE_A defaults must be loadable."""
        defaults = get_type_defaults("TYPE_A")
        assert defaults.contract_type_code == "TYPE_A"
        assert defaults.epistemic_ratios is not None
        assert defaults.veto_threshold is not None
        assert defaults.prior_strength is not None

    def test_type_b_defaults_loaded(self) -> None:
        """TYPE_B defaults must be loadable with broader prior strength range."""
        defaults = get_type_defaults("TYPE_B")
        assert defaults.contract_type_code == "TYPE_B"
        # TYPE_B should have same prior_strength bounds as others
        # The PRIOR_STRENGTH_BAYESIAN constant (2.0) is a suggested value within the range
        assert defaults.prior_strength.lower == 0.1
        assert defaults.prior_strength.upper == 10.0
        # Verify 2.0 is within the valid range
        assert defaults.prior_strength.contains(2.0)

    def test_type_e_strictest_veto_threshold(self) -> None:
        """TYPE_E must have strictest veto threshold."""
        defaults_e = get_type_defaults("TYPE_E")
        assert defaults_e.veto_threshold.lower == 0.01

    def test_type_d_most_lenient_veto_threshold(self) -> None:
        """TYPE_D must have most lenient veto threshold."""
        defaults_d = get_type_defaults("TYPE_D")
        assert defaults_d.veto_threshold.upper == 0.10

    def test_unknown_type_raises(self) -> None:
        """Unknown contract type must raise UnknownContractTypeError."""
        from src.farfan_pipeline.infrastructure.calibration.type_defaults import UnknownContractTypeError
        with pytest.raises(UnknownContractTypeError, match="Unknown contract type"):
            get_type_defaults("TYPE_INVALID")

    def test_flyweight_pattern_caching(self) -> None:
        """Same type should return cached instance (flyweight pattern)."""
        defaults1 = get_type_defaults("TYPE_A")
        defaults2 = get_type_defaults("TYPE_A")
        # Should be the exact same object instance due to caching
        assert defaults1 is defaults2


class TestProhibitedOperations:
    """Test prohibited operations enforcement."""

    def test_type_a_prohibitions(self) -> None:
        """TYPE_A must prohibit non-semantic operations (based on canonical contratos_clasificados.json)."""
        # TYPE_A uses: semantic_corroboration, dempster_shafer, veto_gate
        assert is_operation_prohibited("TYPE_A", "weighted_mean")
        assert is_operation_prohibited("TYPE_A", "bayesian_update")
        assert not is_operation_prohibited("TYPE_A", "semantic_corroboration")
        assert not is_operation_prohibited("TYPE_A", "dempster_shafer")

    def test_type_b_prohibitions(self) -> None:
        """TYPE_B must prohibit non-Bayesian aggregation (based on canonical source)."""
        # TYPE_B uses: bayesian_update, concat, veto_gate
        assert is_operation_prohibited("TYPE_B", "weighted_mean")
        assert is_operation_prohibited("TYPE_B", "semantic_corroboration")
        assert not is_operation_prohibited("TYPE_B", "bayesian_update")
        assert not is_operation_prohibited("TYPE_B", "concat")

    def test_type_c_prohibitions(self) -> None:
        """TYPE_C must prohibit operations that don't preserve graph structure."""
        # TYPE_C uses: topological_overlay, graph_construction, veto_gate
        assert is_operation_prohibited("TYPE_C", "weighted_mean")
        assert is_operation_prohibited("TYPE_C", "concat")
        assert not is_operation_prohibited("TYPE_C", "topological_overlay")
        assert not is_operation_prohibited("TYPE_C", "graph_construction")

    def test_type_d_prohibitions(self) -> None:
        """TYPE_D must prohibit non-financial operations."""
        # TYPE_D uses: weighted_mean, concat, financial_coherence_audit
        # Financial contracts CAN use weighted_mean for budget aggregation
        assert is_operation_prohibited("TYPE_D", "semantic_corroboration")
        assert is_operation_prohibited("TYPE_D", "topological_overlay")
        assert not is_operation_prohibited("TYPE_D", "weighted_mean")  # ALLOWED for financial
        assert not is_operation_prohibited("TYPE_D", "concat")

    def test_type_e_logical_operations(self) -> None:
        """
        TYPE_E logical consistency contracts per canonical source.
        
        IMPORTANT: Based on contratos_clasificados.json, TYPE_E USES weighted_mean.
        This differs from the original spec but follows the canonical data.
        TYPE_E uses: concat, weighted_mean, logical_consistency_validation
        """
        # TYPE_E CAN use weighted_mean per canonical source
        assert not is_operation_prohibited("TYPE_E", "weighted_mean")
        assert not is_operation_prohibited("TYPE_E", "concat")
        assert not is_operation_prohibited("TYPE_E", "logical_consistency_validation")
        
        # TYPE_E prohibits operations that don't preserve logical consistency
        assert is_operation_prohibited("TYPE_E", "bayesian_update")
        assert is_operation_prohibited("TYPE_E", "semantic_corroboration")
        assert is_operation_prohibited("TYPE_E", "graph_construction")

    def test_case_insensitive_checking(self) -> None:
        """Prohibition checking must be case-insensitive."""
        # Test with operations that ARE prohibited
        assert is_operation_prohibited("TYPE_A", "WEIGHTED_MEAN")
        assert is_operation_prohibited("TYPE_A", "Bayesian_Update")
        assert is_operation_prohibited("TYPE_B", "SEMANTIC_CORROBORATION")

    def test_substring_matching(self) -> None:
        """Operations containing prohibited terms must be caught."""
        # Test substring matching with operations that ARE prohibited
        assert is_operation_prohibited("TYPE_A", "compute_weighted_mean_value")
        assert is_operation_prohibited("TYPE_B", "calculate_semantic_corroboration_score")

    def test_prohibited_operations_immutable(self) -> None:
        """PROHIBITED_OPERATIONS must be immutable."""
        prohibited = PROHIBITED_OPERATIONS["TYPE_E"]
        assert isinstance(prohibited, frozenset)
        with pytest.raises(AttributeError):
            prohibited.add("new_operation")  # type: ignore[union-attr]

    def test_substring_matching_behavior_documented(self) -> None:
        """
        Document substring matching behavior - intentionally conservative.
        
        The current implementation uses substring matching which may produce
        false positives. This is by design to ensure no prohibited operations
        slip through. If this becomes problematic, switch to word-boundary matching.
        """
        # Test with TYPE_A which prohibits "weighted_mean"
        # "compute_weighted_mean" contains "weighted_mean" substring
        assert is_operation_prohibited("TYPE_A", "compute_weighted_mean")
        
        # This is NOT blocked (doesn't contain prohibited substrings for TYPE_A)
        assert not is_operation_prohibited("TYPE_A", "stream_processor")
        
        # These are correctly blocked (actual prohibited operations)
        assert is_operation_prohibited("TYPE_A", "use_bayesian_update")
        assert is_operation_prohibited("TYPE_B", "apply_semantic_corroboration")
