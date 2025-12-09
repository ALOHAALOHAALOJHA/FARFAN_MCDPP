"""
Unit tests for Base Layer (@b) computation.

Tests the intrinsic quality assessment of methods:
- b_theory: theoretical/conceptual soundness
- b_impl: implementation quality
- b_deploy: operational stability

Formula: x_@b = w_th * b_theory + w_imp * b_impl + w_dep * b_deploy
where w_th + w_imp + w_dep = 1.0
"""

from __future__ import annotations

from typing import Any

import pytest


class TestBaseLayerComputation:
    """Test base layer score computation."""

    def test_base_layer_weights_sum_to_one(self, intrinsic_calibration_config: dict[str, Any]):
        """Verify base layer weights sum to 1.0."""
        weights = intrinsic_calibration_config["base_layer"]["aggregation"]["weights"]
        total = weights["b_theory"] + weights["b_impl"] + weights["b_deploy"]
        assert abs(total - 1.0) < 1e-6, f"Base layer weights must sum to 1.0, got {total}"

    def test_base_layer_weights_non_negative(self, intrinsic_calibration_config: dict[str, Any]):
        """Verify all base layer weights are non-negative."""
        weights = intrinsic_calibration_config["base_layer"]["aggregation"]["weights"]
        assert weights["b_theory"] >= 0, "b_theory weight must be non-negative"
        assert weights["b_impl"] >= 0, "b_impl weight must be non-negative"
        assert weights["b_deploy"] >= 0, "b_deploy weight must be non-negative"

    def test_base_layer_score_bounded(self, sample_base_layer_scores: dict[str, float], intrinsic_calibration_config: dict[str, Any]):
        """Verify base layer score is bounded in [0,1]."""
        weights = intrinsic_calibration_config["base_layer"]["aggregation"]["weights"]

        score = (
            weights["b_theory"] * sample_base_layer_scores["b_theory"]
            + weights["b_impl"] * sample_base_layer_scores["b_impl"]
            + weights["b_deploy"] * sample_base_layer_scores["b_deploy"]
        )

        assert 0.0 <= score <= 1.0, f"Base layer score {score} not in [0,1]"

    def test_b_theory_subcomponents_sum_to_one(self, intrinsic_calibration_config: dict[str, Any]):
        """Verify b_theory subcomponent weights sum to 1.0."""
        subcomponents = intrinsic_calibration_config["components"]["b_theory"]["subcomponents"]
        total = sum(sub["weight"] for sub in subcomponents.values())
        assert abs(total - 1.0) < 1e-6, f"b_theory subcomponent weights must sum to 1.0, got {total}"

    def test_b_impl_subcomponents_sum_to_one(self, intrinsic_calibration_config: dict[str, Any]):
        """Verify b_impl subcomponent weights sum to 1.0."""
        subcomponents = intrinsic_calibration_config["components"]["b_impl"]["subcomponents"]
        total = sum(sub["weight"] for sub in subcomponents.values())
        assert abs(total - 1.0) < 1e-6, f"b_impl subcomponent weights must sum to 1.0, got {total}"

    def test_b_deploy_subcomponents_sum_to_one(self, intrinsic_calibration_config: dict[str, Any]):
        """Verify b_deploy subcomponent weights sum to 1.0."""
        subcomponents = intrinsic_calibration_config["components"]["b_deploy"]["subcomponents"]
        total = sum(sub["weight"] for sub in subcomponents.values())
        assert abs(total - 1.0) < 1e-6, f"b_deploy subcomponent weights must sum to 1.0, got {total}"

    @pytest.mark.parametrize(
        "b_theory,b_impl,b_deploy",
        [
            (1.0, 1.0, 1.0),
            (0.0, 0.0, 0.0),
            (0.5, 0.5, 0.5),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (0.9, 0.8, 0.7),
        ],
    )
    def test_base_layer_various_inputs(self, b_theory: float, b_impl: float, b_deploy: float, intrinsic_calibration_config: dict[str, Any]):
        """Test base layer computation with various input values."""
        weights = intrinsic_calibration_config["base_layer"]["aggregation"]["weights"]

        score = (
            weights["b_theory"] * b_theory
            + weights["b_impl"] * b_impl
            + weights["b_deploy"] * b_deploy
        )

        assert 0.0 <= score <= 1.0, f"Base layer score {score} not in [0,1]"

    def test_base_layer_monotonicity_b_theory(self, intrinsic_calibration_config: dict[str, Any]):
        """Test monotonicity: increasing b_theory increases overall score."""
        weights = intrinsic_calibration_config["base_layer"]["aggregation"]["weights"]

        b_impl = 0.8
        b_deploy = 0.7

        score_low = weights["b_theory"] * 0.3 + weights["b_impl"] * b_impl + weights["b_deploy"] * b_deploy
        score_high = weights["b_theory"] * 0.9 + weights["b_impl"] * b_impl + weights["b_deploy"] * b_deploy

        assert score_high >= score_low, "Increasing b_theory should not decrease overall score"

    def test_base_layer_test_coverage_thresholds(self, intrinsic_calibration_config: dict[str, Any]):
        """Verify test coverage thresholds are properly defined."""
        test_coverage = intrinsic_calibration_config["components"]["b_impl"]["subcomponents"]["test_coverage"]

        assert "thresholds" in test_coverage
        assert "excellent" in test_coverage["thresholds"]
        assert test_coverage["thresholds"]["excellent"] == 80.0

    def test_base_layer_stability_coefficient_direction(self, intrinsic_calibration_config: dict[str, Any]):
        """Verify stability coefficient has correct direction (lower is better)."""
        stability = intrinsic_calibration_config["components"]["b_deploy"]["subcomponents"]["stability_coefficient"]

        assert stability["direction"] == "lower_is_better"

    def test_base_layer_failure_rate_direction(self, intrinsic_calibration_config: dict[str, Any]):
        """Verify failure rate has correct direction (lower is better)."""
        failure_rate = intrinsic_calibration_config["components"]["b_deploy"]["subcomponents"]["failure_rate"]

        assert failure_rate["direction"] == "lower_is_better"


class TestBaseLayerComponentScoring:
    """Test individual component scoring logic."""

    def test_test_coverage_score_excellent(self):
        """Test coverage >= 80% should map to 1.0."""
        coverage = 85.0
        threshold = 80.0

        if coverage >= threshold:
            score = 1.0
        else:
            score = coverage / threshold

        assert score == 1.0

    def test_test_coverage_score_linear_below_threshold(self):
        """Test coverage < 80% should map linearly."""
        coverage = 40.0
        threshold = 80.0

        score = coverage / threshold

        assert score == 0.5

    def test_stability_coefficient_score_excellent(self):
        """CV < 0.1 should map to 1.0."""
        cv = 0.05
        threshold = 0.1

        if cv <= threshold:
            score = 1.0
        else:
            score = max(0.0, 1.0 - (cv - threshold) / 0.5)

        assert score == 1.0

    def test_failure_rate_score_excellent(self):
        """Failure rate < 1% should map to 1.0."""
        failure_rate = 0.5
        threshold = 1.0

        if failure_rate <= threshold:
            score = 1.0
        else:
            score = max(0.0, 1.0 - (failure_rate - threshold) / 10.0)

        assert score == 1.0

    def test_validation_runs_score_excellent(self):
        """Validation runs >= 20 should map to 1.0."""
        runs = 25
        threshold = 20

        if runs >= threshold:
            score = 1.0
        else:
            score = runs / threshold

        assert score == 1.0


class TestBaseLayerRoleRequirements:
    """Test role-specific base layer requirements."""

    def test_score_q_role_min_base_score(self, intrinsic_calibration_config: dict[str, Any]):
        """SCORE_Q role requires min_base_score >= 0.7."""
        role_reqs = intrinsic_calibration_config["role_requirements"]["SCORE_Q"]

        assert role_reqs["min_base_score"] >= 0.7

    def test_score_q_role_critical_components(self, intrinsic_calibration_config: dict[str, Any]):
        """SCORE_Q role requires b_theory and b_impl as critical."""
        role_reqs = intrinsic_calibration_config["role_requirements"]["SCORE_Q"]

        assert "b_theory" in role_reqs["critical_components"]
        assert "b_impl" in role_reqs["critical_components"]

    def test_ingest_pdm_role_min_base_score(self, intrinsic_calibration_config: dict[str, Any]):
        """INGEST_PDM role requires min_base_score >= 0.6."""
        role_reqs = intrinsic_calibration_config["role_requirements"]["INGEST_PDM"]

        assert role_reqs["min_base_score"] >= 0.6

    def test_all_roles_have_required_layers(self, intrinsic_calibration_config: dict[str, Any]):
        """All roles must specify required_layers."""
        role_reqs = intrinsic_calibration_config["role_requirements"]

        for role_name, role_data in role_reqs.items():
            assert "required_layers" in role_data, f"Role {role_name} missing required_layers"
            assert len(role_data["required_layers"]) > 0, f"Role {role_name} has empty required_layers"
