"""
Unit Layer Configuration Loader Tests.

Tests loading and saving of UnitLayerConfig from/to JSON.
"""
import json
import tempfile
from pathlib import Path

import pytest

from src.farfan_pipeline.core.calibration.unit_layer import UnitLayerConfig
from src.farfan_pipeline.core.calibration.unit_layer_loader import (
    load_unit_layer_config,
    save_unit_layer_config
)


class TestConfigLoader:
    """Test configuration loading."""
    
    def test_load_default_config(self):
        """Test loading from default location."""
        config_path = Path("system/config/calibration/unit_layer_config.json")
        
        if not config_path.exists():
            pytest.skip("Default config file not found")
        
        config = load_unit_layer_config()
        
        assert config.w_S == 0.25
        assert config.w_M == 0.25
        assert config.w_I == 0.25
        assert config.w_P == 0.25
        assert config.aggregation_type == "geometric_mean"
    
    def test_load_from_custom_path(self):
        """Test loading from custom path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "component_weights": {
                    "w_S": 0.3,
                    "w_M": 0.3,
                    "w_I": 0.2,
                    "w_P": 0.2
                },
                "aggregation": {
                    "aggregation_type": "harmonic_mean"
                },
                "hard_gates": {
                    "require_ppi_presence": False,
                    "require_indicator_matrix": True,
                    "min_structural_compliance": 0.6,
                    "i_struct_hard_gate": 0.75,
                    "p_struct_hard_gate": 0.75
                },
                "anti_gaming_thresholds": {
                    "max_placeholder_ratio": 0.15,
                    "min_unique_values_ratio": 0.6,
                    "min_number_density": 0.03,
                    "gaming_penalty_cap": 0.4
                },
                "S_structural_compliance": {
                    "w_block_coverage": 0.5,
                    "w_hierarchy": 0.25,
                    "w_order": 0.25,
                    "min_block_tokens": 150,
                    "min_block_numbers": 5
                },
                "M_mandatory_sections": {
                    "critical_sections_weight": 2.5,
                    "sections": {
                        "Diagnóstico": {
                            "min_tokens": 1000,
                            "min_keywords": 4,
                            "min_numbers": 15,
                            "min_sources": 3
                        }
                    }
                },
                "I_indicator_quality": {
                    "w_i_struct": 0.5,
                    "w_i_link": 0.3,
                    "w_i_logic": 0.2,
                    "i_struct": {
                        "critical_fields_weight": 2.5,
                        "placeholder_penalty_multiplier": 4.0
                    },
                    "i_link": {
                        "fuzzy_match_threshold": 0.9
                    },
                    "i_logic": {
                        "valid_lb_year_min": 2018,
                        "valid_lb_year_max": 2024
                    }
                },
                "P_ppi_completeness": {
                    "w_p_presence": 0.25,
                    "w_p_structure": 0.35,
                    "w_p_consistency": 0.4,
                    "p_struct": {
                        "nonzero_row_threshold": 0.85
                    },
                    "p_consistency": {
                        "accounting_tolerance": 0.02,
                        "trazabilidad_threshold": 0.85
                    }
                }
            }
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = load_unit_layer_config(temp_path)
            
            assert config.w_S == 0.3
            assert config.w_M == 0.3
            assert config.w_I == 0.2
            assert config.w_P == 0.2
            assert config.aggregation_type == "harmonic_mean"
            assert config.require_ppi_presence is False
            assert config.min_structural_compliance == 0.6
            assert config.diagnostico_min_tokens == 1000
            assert config.i_critical_fields_weight == 2.5
            assert config.i_valid_lb_year_min == 2018
            assert config.p_accounting_tolerance == 0.02
        finally:
            Path(temp_path).unlink()
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_unit_layer_config("/nonexistent/path/config.json")
    
    def test_config_validation_on_load(self):
        """Test that invalid config triggers validation error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "component_weights": {
                    "w_S": 0.5,
                    "w_M": 0.5,
                    "w_I": 0.5,
                    "w_P": 0.5
                },
                "aggregation": {"aggregation_type": "geometric_mean"},
                "hard_gates": {},
                "anti_gaming_thresholds": {},
                "S_structural_compliance": {},
                "M_mandatory_sections": {"sections": {}},
                "I_indicator_quality": {},
                "P_ppi_completeness": {}
            }
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must sum to 1.0"):
                load_unit_layer_config(temp_path)
        finally:
            Path(temp_path).unlink()


class TestConfigSaver:
    """Test configuration saving."""
    
    def test_save_and_reload(self):
        """Test saving config and reloading produces same values."""
        original_config = UnitLayerConfig(
            w_S=0.3,
            w_M=0.3,
            w_I=0.2,
            w_P=0.2,
            aggregation_type="harmonic_mean",
            min_structural_compliance=0.6
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            save_unit_layer_config(original_config, temp_path)
            reloaded_config = load_unit_layer_config(temp_path)
            
            assert reloaded_config.w_S == original_config.w_S
            assert reloaded_config.w_M == original_config.w_M
            assert reloaded_config.w_I == original_config.w_I
            assert reloaded_config.w_P == original_config.w_P
            assert reloaded_config.aggregation_type == original_config.aggregation_type
            assert reloaded_config.min_structural_compliance == original_config.min_structural_compliance
        finally:
            Path(temp_path).unlink()
    
    def test_saved_json_structure(self):
        """Test that saved JSON has correct structure."""
        config = UnitLayerConfig()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            save_unit_layer_config(config, temp_path)
            
            with open(temp_path, encoding='utf-8') as f:
                data = json.load(f)
            
            assert "_metadata" in data
            assert "component_weights" in data
            assert "aggregation" in data
            assert "hard_gates" in data
            assert "anti_gaming_thresholds" in data
            assert "S_structural_compliance" in data
            assert "M_mandatory_sections" in data
            assert "I_indicator_quality" in data
            assert "P_ppi_completeness" in data
            
            assert data["component_weights"]["w_S"] == 0.25
            assert data["aggregation"]["aggregation_type"] == "geometric_mean"
        finally:
            Path(temp_path).unlink()
    
    def test_roundtrip_preserves_all_fields(self):
        """Test that all fields survive a save/load roundtrip."""
        original_config = UnitLayerConfig(
            w_S=0.3,
            w_M=0.25,
            w_I=0.25,
            w_P=0.2,
            aggregation_type="harmonic_mean",
            require_ppi_presence=False,
            require_indicator_matrix=True,
            min_structural_compliance=0.6,
            i_struct_hard_gate=0.75,
            p_struct_hard_gate=0.75,
            max_placeholder_ratio=0.15,
            min_unique_values_ratio=0.6,
            min_number_density=0.03,
            gaming_penalty_cap=0.4,
            diagnostico_min_tokens=1000,
            diagnostico_min_keywords=4,
            i_critical_fields_weight=2.5,
            p_accounting_tolerance=0.02
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            save_unit_layer_config(original_config, temp_path)
            reloaded_config = load_unit_layer_config(temp_path)
            
            # Check all critical fields
            assert reloaded_config.require_ppi_presence == original_config.require_ppi_presence
            assert reloaded_config.max_placeholder_ratio == original_config.max_placeholder_ratio
            assert reloaded_config.diagnostico_min_tokens == original_config.diagnostico_min_tokens
            assert reloaded_config.i_critical_fields_weight == original_config.i_critical_fields_weight
            assert reloaded_config.p_accounting_tolerance == original_config.p_accounting_tolerance
        finally:
            Path(temp_path).unlink()


class TestDefaultValues:
    """Test default value handling."""
    
    def test_missing_sections_use_defaults(self):
        """Test that missing config sections use default values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "component_weights": {
                    "w_S": 0.25,
                    "w_M": 0.25,
                    "w_I": 0.25,
                    "w_P": 0.25
                },
                "aggregation": {"aggregation_type": "geometric_mean"},
                "hard_gates": {},
                "anti_gaming_thresholds": {},
                "S_structural_compliance": {},
                "M_mandatory_sections": {"sections": {}},
                "I_indicator_quality": {},
                "P_ppi_completeness": {}
            }
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = load_unit_layer_config(temp_path)
            
            # Should use default values
            assert config.require_ppi_presence is True
            assert config.min_structural_compliance == 0.5
            assert config.max_placeholder_ratio == 0.10
        finally:
            Path(temp_path).unlink()
