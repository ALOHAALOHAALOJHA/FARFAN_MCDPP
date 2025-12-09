"""
Integration test for configuration loading.

Tests that all calibration configs load correctly and validate:
- intrinsic_calibration.json
- method_compatibility.json
- fusion_weights.json
- Schema validation
- Weight normalization
"""

from __future__ import annotations

from typing import Any

import pytest


@pytest.mark.integration
class TestConfigurationLoading:
    """Test configuration file loading."""

    def test_load_intrinsic_calibration_config(self, intrinsic_calibration_config: dict[str, Any]):
        """Test loading intrinsic calibration configuration."""
        assert intrinsic_calibration_config is not None
        assert "base_layer" in intrinsic_calibration_config
        assert "components" in intrinsic_calibration_config
        assert "role_requirements" in intrinsic_calibration_config

    def test_load_method_compatibility_config(self, method_compatibility_config: dict[str, Any]):
        """Test loading method compatibility configuration."""
        assert method_compatibility_config is not None
        assert "method_compatibility" in method_compatibility_config

    def test_load_fusion_weights_config(self, fusion_weights_config: dict[str, Any]):
        """Test loading fusion weights configuration."""
        assert fusion_weights_config is not None
        assert "_fusion_formula" in fusion_weights_config or "role_fusion_parameters" in fusion_weights_config


@pytest.mark.integration
class TestConfigurationValidation:
    """Test configuration schema validation."""

    def test_intrinsic_calibration_has_required_fields(self, intrinsic_calibration_config: dict[str, Any]):
        """Intrinsic calibration config must have required fields."""
        assert "base_layer" in intrinsic_calibration_config

        base_layer = intrinsic_calibration_config["base_layer"]
        assert "symbol" in base_layer
        assert base_layer["symbol"] == "@b"
        assert "aggregation" in base_layer
        assert "weights" in base_layer["aggregation"]

    def test_base_layer_components_exist(self, intrinsic_calibration_config: dict[str, Any]):
        """Base layer must have all three components."""
        components = intrinsic_calibration_config["components"]

        assert "b_theory" in components
        assert "b_impl" in components
        assert "b_deploy" in components

    def test_component_subcomponents_valid(self, intrinsic_calibration_config: dict[str, Any]):
        """Each component must have valid subcomponents."""
        components = intrinsic_calibration_config["components"]

        for component_name, component_data in components.items():
            assert "subcomponents" in component_data
            assert "weight" in component_data
            assert len(component_data["subcomponents"]) > 0

    def test_role_requirements_complete(self, intrinsic_calibration_config: dict[str, Any]):
        """All roles must have complete requirements."""
        role_reqs = intrinsic_calibration_config["role_requirements"]

        expected_roles = ["SCORE_Q", "INGEST_PDM", "STRUCTURE", "EXTRACT", "AGGREGATE", "REPORT", "META_TOOL", "TRANSFORM"]

        for role in expected_roles:
            assert role in role_reqs, f"Missing role {role}"
            role_data = role_reqs[role]
            assert "required_layers" in role_data
            assert "min_base_score" in role_data
            assert "critical_components" in role_data

    def test_method_compatibility_entries(self, method_compatibility_config: dict[str, Any]):
        """Method compatibility must have valid entries."""
        method_compat = method_compatibility_config.get("method_compatibility", {})

        for method_id, compat_data in method_compat.items():
            assert "questions" in compat_data or "dimensions" in compat_data or "policies" in compat_data


@pytest.mark.integration
class TestWeightNormalization:
    """Test weight normalization in configurations."""

    def test_base_layer_weights_normalized(self, intrinsic_calibration_config: dict[str, Any]):
        """Base layer weights must sum to 1.0."""
        weights = intrinsic_calibration_config["base_layer"]["aggregation"]["weights"]

        total = weights["b_theory"] + weights["b_impl"] + weights["b_deploy"]

        assert abs(total - 1.0) < 1e-6, f"Base layer weights sum to {total}, not 1.0"

    def test_component_weights_normalized(self, intrinsic_calibration_config: dict[str, Any]):
        """Component weights must match aggregation weights."""
        components = intrinsic_calibration_config["components"]
        base_agg_weights = intrinsic_calibration_config["base_layer"]["aggregation"]["weights"]

        assert abs(components["b_theory"]["weight"] - base_agg_weights["b_theory"]) < 1e-6
        assert abs(components["b_impl"]["weight"] - base_agg_weights["b_impl"]) < 1e-6
        assert abs(components["b_deploy"]["weight"] - base_agg_weights["b_deploy"]) < 1e-6

    def test_subcomponent_weights_normalized(self, intrinsic_calibration_config: dict[str, Any]):
        """Subcomponent weights must sum to 1.0 within each component."""
        components = intrinsic_calibration_config["components"]

        for component_name, component_data in components.items():
            subcomponents = component_data["subcomponents"]
            total = sum(sub["weight"] for sub in subcomponents.values())

            assert abs(total - 1.0) < 1e-6, f"{component_name} subcomponent weights sum to {total}"


@pytest.mark.integration
class TestConfigurationConsistency:
    """Test consistency across configurations."""

    def test_role_layers_match_available_layers(self, intrinsic_calibration_config: dict[str, Any]):
        """Required layers for roles must be valid layer names."""
        valid_layers = {"@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"}

        role_reqs = intrinsic_calibration_config["role_requirements"]

        for role_name, role_data in role_reqs.items():
            for layer in role_data["required_layers"]:
                assert layer in valid_layers, f"Role {role_name} requires invalid layer {layer}"

    def test_critical_components_match_component_names(self, intrinsic_calibration_config: dict[str, Any]):
        """Critical components for roles must be valid component names."""
        valid_components = {"b_theory", "b_impl", "b_deploy"}

        role_reqs = intrinsic_calibration_config["role_requirements"]

        for role_name, role_data in role_reqs.items():
            for component in role_data["critical_components"]:
                assert component in valid_components, f"Role {role_name} requires invalid component {component}"

    def test_compatibility_scores_valid(self, method_compatibility_config: dict[str, Any]):
        """Compatibility scores must be in valid discrete levels."""
        valid_scores = {0.0, 0.1, 0.3, 0.7, 1.0}

        method_compat = method_compatibility_config.get("method_compatibility", {})

        for method_id, compat_data in method_compat.items():
            for score in compat_data.get("questions", {}).values():
                assert score in valid_scores, f"Method {method_id} has invalid question score {score}"

            for score in compat_data.get("dimensions", {}).values():
                assert score in valid_scores, f"Method {method_id} has invalid dimension score {score}"

            for score in compat_data.get("policies", {}).values():
                assert score in valid_scores, f"Method {method_id} has invalid policy score {score}"


@pytest.mark.integration
class TestConfigurationMetadata:
    """Test configuration metadata."""

    def test_cohort_metadata_present(self, intrinsic_calibration_config: dict[str, Any]):
        """Configuration must have cohort metadata."""
        assert "_cohort_metadata" in intrinsic_calibration_config or "_metadata" in intrinsic_calibration_config

    def test_config_version_present(self, intrinsic_calibration_config: dict[str, Any]):
        """Configuration must have version information."""
        if "_metadata" in intrinsic_calibration_config:
            assert "version" in intrinsic_calibration_config["_metadata"]

    def test_authority_documented(self, intrinsic_calibration_config: dict[str, Any]):
        """Configuration must document authority."""
        if "_metadata" in intrinsic_calibration_config:
            metadata = intrinsic_calibration_config["_metadata"]
            assert "authority" in metadata or "description" in metadata
