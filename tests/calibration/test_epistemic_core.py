"""
ADVERSARIAL TESTS FOR EPISTEMIC CALIBRATION CORE
=================================================

Tests the N0-N4 epistemic calibration system:
- N0InfrastructureCalibration
- N1EmpiricalCalibration  
- N2InferentialCalibration
- N3AuditCalibration (VETO GATE - Popperian asymmetry)
- N4MetaCalibration

CONSTITUTIONAL INVARIANTS TESTED:
    CI-03: INMUTABILIDAD EPISTÉMICA - Level nunca cambia post-init
    CI-04: ASIMETRÍA POPPERIANA - N3 puede vetar N1/N2, nunca al revés
    CI-05: SEPARACIÓN CALIBRACIÓN-NIVEL - PDM ajusta parámetros, no nivel

Version: 4.0.0
"""

from __future__ import annotations

import pytest

from farfan_pipeline.infrastructure.calibration import (
    ValidationError,
    CalibrationBoundsError,
    ClosedInterval,
    EpistemicLevel,
    N0InfrastructureCalibration,
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    N3AuditCalibration,
    N4MetaCalibration,
    create_calibration,
    get_default_calibration_for_level,
    validate_epistemic_level,
)


# =============================================================================
# CLOSED INTERVAL TESTS
# =============================================================================


class TestClosedInterval:
    """Tests for ClosedInterval bounds validation."""

    def test_valid_interval_construction(self) -> None:
        """Valid intervals should construct without error."""
        interval = ClosedInterval(lower=0.0, upper=1.0)
        assert interval.lower == 0.0
        assert interval.upper == 1.0

    def test_lower_equals_upper_is_valid(self) -> None:
        """Point intervals (lower == upper) should be valid."""
        interval = ClosedInterval(lower=0.5, upper=0.5)
        assert interval.contains(0.5)

    def test_lower_greater_than_upper_MUST_RAISE(self) -> None:
        """ADVERSARIAL: lower > upper must fail construction."""
        with pytest.raises(ValidationError, match="[Mm]alformed"):
            ClosedInterval(lower=1.0, upper=0.5)

    def test_nan_lower_MUST_RAISE(self) -> None:
        """ADVERSARIAL: NaN bounds are invalid."""
        with pytest.raises(ValidationError, match="[Nn]a[Nn]"):
            ClosedInterval(lower=float("nan"), upper=1.0)

    def test_nan_upper_MUST_RAISE(self) -> None:
        """ADVERSARIAL: NaN bounds are invalid."""
        with pytest.raises(ValidationError, match="[Nn]a[Nn]"):
            ClosedInterval(lower=0.0, upper=float("nan"))

    def test_inf_lower_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Infinite bounds are invalid."""
        with pytest.raises(ValidationError, match="[Ff]inite"):
            ClosedInterval(lower=float("-inf"), upper=1.0)

    def test_inf_upper_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Infinite bounds are invalid."""
        with pytest.raises(ValidationError, match="[Ff]inite"):
            ClosedInterval(lower=0.0, upper=float("inf"))

    def test_contains_boundary_values(self) -> None:
        """Boundary values should be contained (closed interval)."""
        interval = ClosedInterval(lower=0.0, upper=1.0)
        assert interval.contains(0.0)  # Lower boundary
        assert interval.contains(1.0)  # Upper boundary
        assert interval.contains(0.5)  # Interior
        assert not interval.contains(-0.1)  # Below
        assert not interval.contains(1.1)  # Above

    def test_midpoint_calculation(self) -> None:
        """Midpoint should be arithmetic mean of bounds."""
        interval = ClosedInterval(lower=0.0, upper=1.0)
        assert interval.midpoint() == 0.5


# =============================================================================
# N0 INFRASTRUCTURE CALIBRATION TESTS
# =============================================================================


class TestN0InfrastructureCalibration:
    """Tests for N0-INFRA level calibration."""

    def test_default_construction(self) -> None:
        """Default N0 calibration should construct with valid defaults."""
        n0 = N0InfrastructureCalibration()
        assert n0.level == "N0-INFRA"
        assert n0.random_seed == 42
        assert n0.default_timeout_seconds > 0

    def test_level_is_immutable(self) -> None:
        """CI-03: Level should be immutable after construction."""
        n0 = N0InfrastructureCalibration()
        # Level is a Final field, cannot be reassigned
        assert n0.level == "N0-INFRA"
        # Frozen dataclass prevents modification
        with pytest.raises(AttributeError):
            n0.level = "N1-EMP"  # type: ignore

    def test_negative_timeout_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Negative timeout should fail validation."""
        with pytest.raises(ValidationError):
            N0InfrastructureCalibration(default_timeout_seconds=-1.0)

    def test_negative_retries_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Negative retry count should fail validation."""
        with pytest.raises(ValidationError):
            N0InfrastructureCalibration(max_retries=-1)

    def test_output_type_is_infrastructure(self) -> None:
        """N0 should produce INFRASTRUCTURE output type."""
        n0 = N0InfrastructureCalibration()
        assert n0.output_type == "INFRASTRUCTURE"

    def test_fusion_behavior_is_none(self) -> None:
        """N0 has no fusion behavior."""
        n0 = N0InfrastructureCalibration()
        assert n0.fusion_behavior == "none"


# =============================================================================
# N1 EMPIRICAL CALIBRATION TESTS
# =============================================================================


class TestN1EmpiricalCalibration:
    """Tests for N1-EMP level calibration."""

    def test_default_construction(self) -> None:
        """Default N1 calibration should construct with valid defaults."""
        n1 = N1EmpiricalCalibration()
        assert n1.level == "N1-EMP"
        assert 0.0 <= n1.extraction_confidence_floor <= 1.0

    def test_level_is_immutable(self) -> None:
        """CI-03: Level should be immutable after construction."""
        n1 = N1EmpiricalCalibration()
        assert n1.level == "N1-EMP"
        with pytest.raises(AttributeError):
            n1.level = "N2-INF"  # type: ignore

    def test_confidence_floor_out_of_bounds_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Confidence floor must be in [0, 1]."""
        with pytest.raises(ValidationError):
            N1EmpiricalCalibration(extraction_confidence_floor=1.5)
        with pytest.raises(ValidationError):
            N1EmpiricalCalibration(extraction_confidence_floor=-0.1)

    def test_table_boost_less_than_one_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Table boost < 1.0 would be a penalty, not boost."""
        with pytest.raises(ValidationError):
            N1EmpiricalCalibration(table_extraction_boost=0.5)

    def test_output_type_is_fact(self) -> None:
        """N1 should produce FACT output type."""
        n1 = N1EmpiricalCalibration()
        assert n1.output_type == "FACT"

    def test_fusion_behavior_is_additive(self) -> None:
        """N1 uses additive fusion (⊕)."""
        n1 = N1EmpiricalCalibration()
        assert n1.fusion_behavior == "additive"


# =============================================================================
# N2 INFERENTIAL CALIBRATION TESTS
# =============================================================================


class TestN2InferentialCalibration:
    """Tests for N2-INF level calibration."""

    def test_default_construction(self) -> None:
        """Default N2 calibration should construct with valid defaults."""
        n2 = N2InferentialCalibration()
        assert n2.level == "N2-INF"
        assert 0.0 <= n2.prior_strength <= 1.0
        assert n2.mcmc_samples > 0

    def test_level_is_immutable(self) -> None:
        """CI-03: Level should be immutable after construction."""
        n2 = N2InferentialCalibration()
        assert n2.level == "N2-INF"
        with pytest.raises(AttributeError):
            n2.level = "N3-AUD"  # type: ignore

    def test_prior_strength_out_of_bounds_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Prior strength must be in [0, 1]."""
        with pytest.raises(ValidationError):
            N2InferentialCalibration(prior_strength=1.5)
        with pytest.raises(ValidationError):
            N2InferentialCalibration(prior_strength=-0.1)

    def test_mcmc_samples_must_be_positive(self) -> None:
        """ADVERSARIAL: MCMC samples must be > 0."""
        with pytest.raises(ValidationError):
            N2InferentialCalibration(mcmc_samples=0)
        with pytest.raises(ValidationError):
            N2InferentialCalibration(mcmc_samples=-100)

    def test_likelihood_weight_must_be_positive(self) -> None:
        """ADVERSARIAL: Likelihood weight must be > 0."""
        with pytest.raises(ValidationError):
            N2InferentialCalibration(likelihood_weight=0.0)
        with pytest.raises(ValidationError):
            N2InferentialCalibration(likelihood_weight=-1.0)

    def test_output_type_is_parameter(self) -> None:
        """N2 should produce PARAMETER output type."""
        n2 = N2InferentialCalibration()
        assert n2.output_type == "PARAMETER"

    def test_fusion_behavior_is_multiplicative(self) -> None:
        """N2 uses multiplicative fusion (⊗)."""
        n2 = N2InferentialCalibration()
        assert n2.fusion_behavior == "multiplicative"


# =============================================================================
# N3 AUDIT CALIBRATION TESTS (VETO GATE)
# =============================================================================


class TestN3AuditCalibration:
    """Tests for N3-AUD level calibration (Popperian veto gate)."""

    def test_default_construction(self) -> None:
        """Default N3 calibration should construct with valid defaults."""
        n3 = N3AuditCalibration()
        assert n3.level == "N3-AUD"
        assert n3.veto_threshold_critical < n3.veto_threshold_partial

    def test_level_is_immutable(self) -> None:
        """CI-03: Level should be immutable after construction."""
        n3 = N3AuditCalibration()
        assert n3.level == "N3-AUD"
        with pytest.raises(AttributeError):
            n3.level = "N1-EMP"  # type: ignore

    def test_veto_threshold_ordering_invariant(self) -> None:
        """CONSTITUTIONAL: critical < partial (strictest is lower)."""
        with pytest.raises(ValidationError, match="[Cc]onstitutional|threshold"):
            N3AuditCalibration(
                veto_threshold_critical=0.5,
                veto_threshold_partial=0.3,  # WRONG: partial should be higher
            )

    def test_veto_thresholds_must_be_bounded(self) -> None:
        """ADVERSARIAL: Veto thresholds must be in [0, 1]."""
        with pytest.raises(ValidationError):
            N3AuditCalibration(veto_threshold_critical=-0.1)
        with pytest.raises(ValidationError):
            N3AuditCalibration(veto_threshold_partial=1.5)

    def test_compute_veto_action_critical(self) -> None:
        """Below critical threshold should trigger CRITICAL_VETO."""
        n3 = N3AuditCalibration(
            veto_threshold_critical=0.1,
            veto_threshold_partial=0.5,
        )
        result = n3.compute_veto_action(0.05)  # Below critical
        assert result["veto_action"] == "CRITICAL_VETO"
        assert result["confidence_multiplier"] == 0.0

    def test_compute_veto_action_partial(self) -> None:
        """Between critical and partial should trigger PARTIAL_VETO."""
        n3 = N3AuditCalibration(
            veto_threshold_critical=0.1,
            veto_threshold_partial=0.5,
        )
        result = n3.compute_veto_action(0.3)  # Between thresholds
        assert result["veto_action"] == "PARTIAL_VETO"
        assert result["confidence_multiplier"] == 0.5

    def test_compute_veto_action_approved(self) -> None:
        """Above partial threshold should be APPROVED."""
        n3 = N3AuditCalibration(
            veto_threshold_critical=0.1,
            veto_threshold_partial=0.5,
        )
        result = n3.compute_veto_action(0.8)  # Above all thresholds
        assert result["veto_action"] == "APPROVED"
        assert result["confidence_multiplier"] == 1.0

    def test_output_type_is_constraint(self) -> None:
        """N3 should produce CONSTRAINT output type."""
        n3 = N3AuditCalibration()
        assert n3.output_type == "CONSTRAINT"

    def test_fusion_behavior_is_gate(self) -> None:
        """N3 uses gate fusion (⊘ veto)."""
        n3 = N3AuditCalibration()
        assert n3.fusion_behavior == "gate"


# =============================================================================
# N4 META CALIBRATION TESTS
# =============================================================================


class TestN4MetaCalibration:
    """Tests for N4-META level calibration."""

    def test_default_construction(self) -> None:
        """Default N4 calibration should construct with valid defaults."""
        n4 = N4MetaCalibration()
        assert n4.level == "N4-META"
        assert 0.0 <= n4.failure_detection_threshold <= 1.0

    def test_level_is_immutable(self) -> None:
        """CI-03: Level should be immutable after construction."""
        n4 = N4MetaCalibration()
        assert n4.level == "N4-META"
        with pytest.raises(AttributeError):
            n4.level = "N0-INFRA"  # type: ignore

    def test_thresholds_must_be_bounded(self) -> None:
        """ADVERSARIAL: Thresholds must be in [0, 1]."""
        with pytest.raises(ValidationError):
            N4MetaCalibration(failure_detection_threshold=1.5)
        with pytest.raises(ValidationError):
            N4MetaCalibration(synthesis_confidence_threshold=-0.1)

    def test_output_type_is_meta_analysis(self) -> None:
        """N4 should produce META_ANALYSIS output type."""
        n4 = N4MetaCalibration()
        assert n4.output_type == "META_ANALYSIS"

    def test_fusion_behavior_is_terminal(self) -> None:
        """N4 uses terminal fusion (⊙ synthesis)."""
        n4 = N4MetaCalibration()
        assert n4.fusion_behavior == "terminal"


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================


class TestCalibrationFactory:
    """Tests for calibration factory functions."""

    @pytest.mark.parametrize(
        "level,expected_class",
        [
            ("N0-INFRA", N0InfrastructureCalibration),
            ("N1-EMP", N1EmpiricalCalibration),
            ("N2-INF", N2InferentialCalibration),
            ("N3-AUD", N3AuditCalibration),
            ("N4-META", N4MetaCalibration),
        ],
    )
    def test_create_calibration_returns_correct_type(
        self, level: str, expected_class: type
    ) -> None:
        """Factory should return correct class for each level."""
        calibration = create_calibration(level)
        assert isinstance(calibration, expected_class)
        assert calibration.level == level

    def test_create_calibration_with_custom_params(self) -> None:
        """Factory should accept custom parameters."""
        n1 = create_calibration("N1-EMP", extraction_confidence_floor=0.8)
        assert n1.extraction_confidence_floor == 0.8

    def test_create_calibration_invalid_level_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Invalid level should raise ValidationError."""
        with pytest.raises(ValidationError):
            create_calibration("INVALID_LEVEL")

    def test_get_default_calibration_for_level(self) -> None:
        """get_default_calibration_for_level should return defaults."""
        for level in ["N0-INFRA", "N1-EMP", "N2-INF", "N3-AUD", "N4-META"]:
            calibration = get_default_calibration_for_level(level)
            assert calibration.level == level


# =============================================================================
# EPISTEMIC LEVEL VALIDATION TESTS
# =============================================================================


class TestEpistemicLevelValidation:
    """Tests for epistemic level validation."""

    @pytest.mark.parametrize(
        "valid_level",
        ["N0-INFRA", "N1-EMP", "N2-INF", "N3-AUD", "N4-META"],
    )
    def test_valid_levels_pass_validation(self, valid_level: str) -> None:
        """All canonical levels should pass validation."""
        validate_epistemic_level(valid_level)  # Should not raise

    @pytest.mark.parametrize(
        "invalid_level",
        ["N5-FAKE", "N1", "EMPIRICAL", "n1-emp", "", None],
    )
    def test_invalid_levels_MUST_RAISE(self, invalid_level: str | None) -> None:
        """Invalid levels should raise ValidationError."""
        with pytest.raises((ValidationError, TypeError)):
            validate_epistemic_level(invalid_level)  # type: ignore
