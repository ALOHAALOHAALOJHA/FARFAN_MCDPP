"""
ADVERSARIAL TESTS FOR TYPE DEFAULTS
====================================

Tests for contract type-specific calibration defaults:
- TYPE_A (Semantic)
- TYPE_B (Bayesian)
- TYPE_C (Causal)
- TYPE_D (Financial)
- TYPE_E (Logical)
- SUBTIPO_F (Hybrid)

Tests prohibited operations, fusion strategies, and question mappings.

Version: 4.0.0
"""

from __future__ import annotations

import pytest

from farfan_pipeline.calibration import (
    get_type_defaults,
    get_all_type_defaults,
    is_operation_prohibited,
    is_operation_permitted,
    get_fusion_strategy,
    validate_fusion_strategy_for_type,
    get_contract_type_for_question,
)
# DELETED_MODULE: from farfan_pipeline.calibration.type_defaults import (
    UnknownContractTypeError,
    VALID_CONTRACT_TYPES,
    PROHIBITED_OPERATIONS,
    CONTRACT_TYPE_A,
    CONTRACT_TYPE_B,
    CONTRACT_TYPE_C,
    CONTRACT_TYPE_D,
    CONTRACT_TYPE_E,
    CONTRACT_SUBTIPO_F,
)


# =============================================================================
# TYPE DEFAULTS LOADING TESTS
# =============================================================================


class TestTypeDefaultsLoading:
    """Test loading of type-specific defaults from canonical source."""

    def test_type_a_defaults_loaded(self) -> None:
        """TYPE_A defaults must be loadable."""
        defaults = get_type_defaults(CONTRACT_TYPE_A)
        assert defaults.contract_type_code == CONTRACT_TYPE_A
        assert defaults.epistemic_ratios is not None
        assert defaults.veto_threshold is not None
        assert defaults.prior_strength is not None

    def test_type_b_defaults_loaded(self) -> None:
        """TYPE_B defaults must be loadable."""
        defaults = get_type_defaults(CONTRACT_TYPE_B)
        assert defaults.contract_type_code == CONTRACT_TYPE_B
        assert defaults.prior_strength.lower == 0.1
        assert defaults.prior_strength.upper == 10.0

    def test_type_e_strictest_veto_threshold(self) -> None:
        """TYPE_E must have strictest veto threshold."""
        defaults_e = get_type_defaults(CONTRACT_TYPE_E)
        assert defaults_e.veto_threshold.lower == 0.01

    def test_type_d_most_lenient_veto_threshold(self) -> None:
        """TYPE_D must have most lenient veto threshold."""
        defaults_d = get_type_defaults(CONTRACT_TYPE_D)
        assert defaults_d.veto_threshold.upper == 0.10

    def test_unknown_type_raises(self) -> None:
        """Unknown contract type must raise UnknownContractTypeError."""
        with pytest.raises(UnknownContractTypeError, match="Unknown contract type"):
            get_type_defaults("TYPE_INVALID")

    def test_flyweight_pattern_caching(self) -> None:
        """Same type should return cached instance (flyweight pattern)."""
        defaults1 = get_type_defaults(CONTRACT_TYPE_A)
        defaults2 = get_type_defaults(CONTRACT_TYPE_A)
        # Should be the exact same object instance due to caching
        assert defaults1 is defaults2

    def test_all_valid_types_loadable(self) -> None:
        """All valid contract types should be loadable."""
        for contract_type in VALID_CONTRACT_TYPES:
            defaults = get_type_defaults(contract_type)
            assert defaults.contract_type_code == contract_type

    def test_get_all_type_defaults(self) -> None:
        """get_all_type_defaults should return all types."""
        all_defaults = get_all_type_defaults()
        assert len(all_defaults) == len(VALID_CONTRACT_TYPES)
        for contract_type in VALID_CONTRACT_TYPES:
            assert contract_type in all_defaults


# =============================================================================
# PROHIBITED OPERATIONS TESTS
# =============================================================================


class TestProhibitedOperations:
    """Test prohibited operations enforcement."""

    def test_type_a_prohibitions(self) -> None:
        """TYPE_A must prohibit non-semantic operations."""
        assert is_operation_prohibited(CONTRACT_TYPE_A, "weighted_mean")
        assert is_operation_prohibited(CONTRACT_TYPE_A, "bayesian_update")
        assert not is_operation_prohibited(CONTRACT_TYPE_A, "semantic_corroboration")
        assert not is_operation_prohibited(CONTRACT_TYPE_A, "dempster_shafer")

    def test_type_b_prohibitions(self) -> None:
        """TYPE_B must prohibit non-Bayesian operations."""
        assert is_operation_prohibited(CONTRACT_TYPE_B, "weighted_mean")
        assert is_operation_prohibited(CONTRACT_TYPE_B, "semantic_corroboration")
        assert not is_operation_prohibited(CONTRACT_TYPE_B, "bayesian_update")
        assert not is_operation_prohibited(CONTRACT_TYPE_B, "concat")

    def test_type_c_prohibitions(self) -> None:
        """TYPE_C must prohibit operations that don't preserve graph structure."""
        assert is_operation_prohibited(CONTRACT_TYPE_C, "weighted_mean")
        assert is_operation_prohibited(CONTRACT_TYPE_C, "concat")
        assert not is_operation_prohibited(CONTRACT_TYPE_C, "topological_overlay")
        assert not is_operation_prohibited(CONTRACT_TYPE_C, "graph_construction")

    def test_type_d_prohibitions(self) -> None:
        """TYPE_D must prohibit non-financial operations."""
        assert is_operation_prohibited(CONTRACT_TYPE_D, "semantic_corroboration")
        assert is_operation_prohibited(CONTRACT_TYPE_D, "topological_overlay")
        # Financial contracts CAN use weighted_mean for budget aggregation
        assert not is_operation_prohibited(CONTRACT_TYPE_D, "weighted_mean")
        assert not is_operation_prohibited(CONTRACT_TYPE_D, "concat")

    def test_type_e_prohibitions(self) -> None:
        """TYPE_E logical consistency contracts."""
        # TYPE_E CAN use weighted_mean per canonical source
        assert not is_operation_prohibited(CONTRACT_TYPE_E, "weighted_mean")
        assert not is_operation_prohibited(CONTRACT_TYPE_E, "concat")
        # TYPE_E prohibits operations that don't preserve logical consistency
        assert is_operation_prohibited(CONTRACT_TYPE_E, "bayesian_update")
        assert is_operation_prohibited(CONTRACT_TYPE_E, "semantic_corroboration")
        assert is_operation_prohibited(CONTRACT_TYPE_E, "graph_construction")

    def test_case_insensitive_checking(self) -> None:
        """Prohibition checking must be case-insensitive."""
        assert is_operation_prohibited(CONTRACT_TYPE_A, "WEIGHTED_MEAN")
        assert is_operation_prohibited(CONTRACT_TYPE_A, "Bayesian_Update")
        assert is_operation_prohibited(CONTRACT_TYPE_B, "SEMANTIC_CORROBORATION")

    def test_substring_matching(self) -> None:
        """Operations containing prohibited terms must be caught."""
        assert is_operation_prohibited(CONTRACT_TYPE_A, "compute_weighted_mean_value")
        assert is_operation_prohibited(CONTRACT_TYPE_B, "calculate_semantic_corroboration_score")

    def test_prohibited_operations_immutable(self) -> None:
        """PROHIBITED_OPERATIONS must be immutable."""
        prohibited = PROHIBITED_OPERATIONS[CONTRACT_TYPE_E]
        assert isinstance(prohibited, frozenset)
        with pytest.raises(AttributeError):
            prohibited.add("new_operation")  # type: ignore[union-attr]


# =============================================================================
# PERMITTED OPERATIONS TESTS
# =============================================================================


class TestPermittedOperations:
    """Test permitted operations checking."""

    def test_type_a_permitted_operations(self) -> None:
        """TYPE_A should permit semantic operations."""
        assert is_operation_permitted(CONTRACT_TYPE_A, "semantic_corroboration")
        assert is_operation_permitted(CONTRACT_TYPE_A, "dempster_shafer")
        assert is_operation_permitted(CONTRACT_TYPE_A, "veto_gate")

    def test_type_b_permitted_operations(self) -> None:
        """TYPE_B should permit Bayesian operations."""
        assert is_operation_permitted(CONTRACT_TYPE_B, "bayesian_update")
        assert is_operation_permitted(CONTRACT_TYPE_B, "concat")
        assert is_operation_permitted(CONTRACT_TYPE_B, "veto_gate")

    def test_subtipo_f_no_prohibitions(self) -> None:
        """SUBTIPO_F (fallback) should have minimal prohibitions."""
        # SUBTIPO_F is the most permissive type
        defaults = get_type_defaults(CONTRACT_SUBTIPO_F)
        assert len(defaults.prohibited_operations) == 0


# =============================================================================
# FUSION STRATEGY TESTS
# =============================================================================


class TestFusionStrategies:
    """Test fusion strategy mappings."""

    def test_get_fusion_strategy_type_a(self) -> None:
        """TYPE_A fusion strategies by level."""
        assert get_fusion_strategy(CONTRACT_TYPE_A, "N1") == "semantic_corroboration"
        assert get_fusion_strategy(CONTRACT_TYPE_A, "N2") == "dempster_shafer"
        assert get_fusion_strategy(CONTRACT_TYPE_A, "N3") == "veto_gate"

    def test_get_fusion_strategy_type_b(self) -> None:
        """TYPE_B fusion strategies by level."""
        assert get_fusion_strategy(CONTRACT_TYPE_B, "N1") == "concat"
        assert get_fusion_strategy(CONTRACT_TYPE_B, "N2") == "bayesian_update"
        assert get_fusion_strategy(CONTRACT_TYPE_B, "N3") == "veto_gate"

    def test_get_fusion_strategy_type_d(self) -> None:
        """TYPE_D fusion strategies by level."""
        assert get_fusion_strategy(CONTRACT_TYPE_D, "N1") == "concat"
        assert get_fusion_strategy(CONTRACT_TYPE_D, "N2") == "weighted_mean"
        assert get_fusion_strategy(CONTRACT_TYPE_D, "N3") == "financial_coherence_audit"

    def test_get_fusion_strategy_invalid_level(self) -> None:
        """Invalid epistemic level should raise ValueError."""
        with pytest.raises(ValueError):
            get_fusion_strategy(CONTRACT_TYPE_A, "N4")
        with pytest.raises(ValueError):
            get_fusion_strategy(CONTRACT_TYPE_A, "N0")

    def test_validate_fusion_strategy_canonical(self) -> None:
        """Canonical strategy should pass validation."""
        is_valid, msg = validate_fusion_strategy_for_type(
            CONTRACT_TYPE_A, "semantic_corroboration", "N1"
        )
        assert is_valid
        assert msg == ""

    def test_validate_fusion_strategy_prohibited(self) -> None:
        """Prohibited strategy should fail validation."""
        is_valid, msg = validate_fusion_strategy_for_type(
            CONTRACT_TYPE_A, "weighted_mean", "N2"
        )
        assert not is_valid
        assert "prohibited" in msg.lower()

    def test_validate_fusion_strategy_non_canonical_but_permitted(self) -> None:
        """Non-canonical but permitted strategy should pass with warning."""
        # concat is permitted for TYPE_A but not canonical for N1
        is_valid, msg = validate_fusion_strategy_for_type(
            CONTRACT_TYPE_A, "concat", "N1"
        )
        assert is_valid
        assert "warning" in msg.lower()


# =============================================================================
# QUESTION TO CONTRACT TYPE MAPPING TESTS
# =============================================================================


class TestQuestionMapping:
    """Test question ID to contract type mapping."""

    def test_base_question_mapping(self) -> None:
        """Base questions (Q001-Q030) should map correctly."""
        # TYPE_A: Q001, Q013
        assert get_contract_type_for_question("Q001") == CONTRACT_TYPE_A
        assert get_contract_type_for_question("Q013") == CONTRACT_TYPE_A

        # TYPE_B: Q002, Q005, etc.
        assert get_contract_type_for_question("Q002") == CONTRACT_TYPE_B
        assert get_contract_type_for_question("Q005") == CONTRACT_TYPE_B

        # TYPE_C: Q008, Q016, etc.
        assert get_contract_type_for_question("Q008") == CONTRACT_TYPE_C
        assert get_contract_type_for_question("Q016") == CONTRACT_TYPE_C

        # TYPE_D: Q003, Q004, etc.
        assert get_contract_type_for_question("Q003") == CONTRACT_TYPE_D
        assert get_contract_type_for_question("Q004") == CONTRACT_TYPE_D

        # TYPE_E: Q010, Q014, etc.
        assert get_contract_type_for_question("Q010") == CONTRACT_TYPE_E
        assert get_contract_type_for_question("Q014") == CONTRACT_TYPE_E

    def test_extended_question_mapping(self) -> None:
        """Extended questions (Q031-Q300) should map to base questions."""
        # Q031 maps to base Q001 (PA02)
        assert get_contract_type_for_question("Q031") == CONTRACT_TYPE_A
        # Q061 maps to base Q001 (PA03)
        assert get_contract_type_for_question("Q061") == CONTRACT_TYPE_A
        # Q045 maps to base Q015 (TYPE_D)
        assert get_contract_type_for_question("Q045") == CONTRACT_TYPE_D

    def test_invalid_question_format(self) -> None:
        """Invalid question format should raise KeyError."""
        with pytest.raises(KeyError):
            get_contract_type_for_question("INVALID")
        with pytest.raises(KeyError):
            get_contract_type_for_question("001")  # Missing Q prefix
