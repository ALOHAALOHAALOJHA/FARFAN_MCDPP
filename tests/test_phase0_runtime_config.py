"""
Phase 0 Test Suite - Runtime Configuration & Boot Checks
=========================================================

Focused tests for Phase 0 components that can be imported cleanly.

Author: F.A.R.F.A.N Test Suite
Date: 2025-12-10
"""

import os
from pathlib import Path

# Add src to path
import pytest

# Import Phase 0 components from Phase_zero folder
from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import (
    ConfigurationError,
    FallbackCategory,
    RuntimeConfig,
    RuntimeMode,
    reset_runtime_config,
)

from farfan_pipeline.phases.Phase_zero.phase0_50_00_boot_checks import (
    BootCheckError,
    check_networkx_available,
    get_boot_check_summary,
)


class TestRuntimeConfiguration:
    """Test suite for RuntimeConfig validation and parsing."""
    
    def setup_method(self):
        """Reset config before each test."""
        reset_runtime_config()
        # Clear environment
        for key in list(os.environ.keys()):
            if key.startswith("SAAAAAA_") or key.startswith("ALLOW_") or key.startswith("STRICT_") or key.startswith("PHASE_") or key.startswith("EXPECTED_") or key.startswith("PREFERRED_"):
                del os.environ[key]
    
    def teardown_method(self):
        """Cleanup after each test."""
        reset_runtime_config()
    
    def test_default_prod_mode(self):
        """Test default runtime mode is PROD."""
        config = RuntimeConfig.from_env()
        assert config.mode == RuntimeMode.PROD
        print("  ✓ Default runtime mode is PROD")
    
    def test_dev_mode_parsing(self):
        """Test DEV mode parsing from environment."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        config = RuntimeConfig.from_env()
        assert config.mode == RuntimeMode.DEV
        print("  ✓ DEV mode parsed correctly")
    
    def test_exploratory_mode_parsing(self):
        """Test EXPLORATORY mode parsing."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "exploratory"
        config = RuntimeConfig.from_env()
        assert config.mode == RuntimeMode.EXPLORATORY
        print("  ✓ EXPLORATORY mode parsed correctly")
    
    def test_invalid_mode_raises_error(self):
        """Test invalid runtime mode raises ConfigurationError."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "invalid_mode"
        with pytest.raises(ConfigurationError, match="Invalid SAAAAAA_RUNTIME_MODE"):
            RuntimeConfig.from_env()
        print("  ✓ Invalid mode raises ConfigurationError")
    
    def test_prod_illegal_combination_dev_ingestion(self):
        """Test PROD + ALLOW_DEV_INGESTION_FALLBACKS raises error."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["ALLOW_DEV_INGESTION_FALLBACKS"] = "true"
        with pytest.raises(ConfigurationError, match="Illegal configuration"):
            RuntimeConfig.from_env()
        print("  ✓ PROD + DEV_INGESTION_FALLBACKS rejected")
    
    def test_prod_illegal_combination_execution_estimates(self):
        """Test PROD + ALLOW_EXECUTION_ESTIMATES raises error."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["ALLOW_EXECUTION_ESTIMATES"] = "true"
        with pytest.raises(ConfigurationError, match="Illegal configuration"):
            RuntimeConfig.from_env()
        print("  ✓ PROD + EXECUTION_ESTIMATES rejected")
    
    def test_prod_illegal_combination_aggregation_defaults(self):
        """Test PROD + ALLOW_AGGREGATION_DEFAULTS raises error."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["ALLOW_AGGREGATION_DEFAULTS"] = "true"
        with pytest.raises(ConfigurationError, match="Illegal configuration"):
            RuntimeConfig.from_env()
        print("  ✓ PROD + AGGREGATION_DEFAULTS rejected")
    
    def test_prod_illegal_combination_missing_base_weights(self):
        """Test PROD + ALLOW_MISSING_BASE_WEIGHTS raises error."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["ALLOW_MISSING_BASE_WEIGHTS"] = "true"
        with pytest.raises(ConfigurationError, match="Illegal configuration"):
            RuntimeConfig.from_env()
        print("  ✓ PROD + MISSING_BASE_WEIGHTS rejected")
    
    def test_dev_allows_all_fallbacks(self):
        """Test DEV mode allows all fallback flags."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
        os.environ["ALLOW_DEV_INGESTION_FALLBACKS"] = "true"
        os.environ["ALLOW_EXECUTION_ESTIMATES"] = "true"
        os.environ["ALLOW_AGGREGATION_DEFAULTS"] = "true"
        os.environ["ALLOW_MISSING_BASE_WEIGHTS"] = "true"
        
        config = RuntimeConfig.from_env()
        assert config.allow_dev_ingestion_fallbacks
        assert config.allow_execution_estimates
        assert config.allow_aggregation_defaults
        assert config.allow_missing_base_weights
        print("  ✓ DEV mode allows all fallbacks")
    
    def test_strict_mode_detection(self):
        """Test is_strict_mode() correctly identifies strict PROD."""
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        config = RuntimeConfig.from_env()
        assert config.is_strict_mode()
        print("  ✓ Strict mode detected correctly")
    
    def test_fallback_summary_generation(self):
        """Test get_fallback_summary() returns correct structure."""
        config = RuntimeConfig.from_env()
        summary = config.get_fallback_summary()
        
        assert "critical" in summary
        assert "quality" in summary
        assert "development" in summary
        assert "operational" in summary
        
        # Check critical category has expected flags
        assert "contradiction_fallback" in summary["critical"]
        assert "validator_disable" in summary["critical"]
        assert "execution_estimates" in summary["critical"]
        
        print("  ✓ Fallback summary generated correctly")
    
    def test_timeout_parsing(self):
        """Test phase timeout parsing from environment."""
        os.environ["PHASE_TIMEOUT_SECONDS"] = "600"
        config = RuntimeConfig.from_env()
        assert config.phase_timeout_seconds == 600
        print("  ✓ Phase timeout parsed correctly")
    
    def test_expected_counts_parsing(self):
        """Test expected question/method counts."""
        os.environ["EXPECTED_QUESTION_COUNT"] = "305"
        os.environ["EXPECTED_METHOD_COUNT"] = "416"
        config = RuntimeConfig.from_env()
        assert config.expected_question_count == 305
        assert config.expected_method_count == 416
        print("  ✓ Expected counts parsed correctly")
    
    def test_preferred_spacy_model_default(self):
        """Test PREFERRED_SPACY_MODEL has default value."""
        config = RuntimeConfig.from_env()
        assert config.preferred_spacy_model == "es_core_news_lg"
        print("  ✓ PREFERRED_SPACY_MODEL default is es_core_news_lg")
    
    def test_preferred_embedding_model_default(self):
        """Test PREFERRED_EMBEDDING_MODEL has default value."""
        config = RuntimeConfig.from_env()
        assert "paraphrase-multilingual-MiniLM" in config.preferred_embedding_model
        print("  ✓ PREFERRED_EMBEDDING_MODEL default set correctly")


class TestBootChecks:
    """Test suite for boot-time dependency checks."""
    
    def setup_method(self):
        """Setup test environment."""
        reset_runtime_config()
    
    def test_networkx_available(self):
        """Test NetworkX availability check."""
        result = check_networkx_available()
        # Should return bool (True if networkx is installed)
        assert isinstance(result, bool)
        print(f"  ✓ NetworkX availability check works: {result}")
    
    def test_boot_check_summary_format(self):
        """Test boot check summary formatting."""
        results = {
            "check1": True,
            "check2": False,
            "check3": True,
        }
        
        summary = get_boot_check_summary(results)
        
        assert "Boot Checks: 2/3 passed" in summary
        assert "✓ check1" in summary
        assert "✗ check2" in summary
        assert "✓ check3" in summary
        print("  ✓ Boot check summary formatted correctly")
    
    def test_boot_check_summary_all_pass(self):
        """Test boot check summary with all passing."""
        results = {
            "check1": True,
            "check2": True,
            "check3": True,
        }
        
        summary = get_boot_check_summary(results)
        
        assert "Boot Checks: 3/3 passed" in summary
        assert "✓ check1" in summary
        assert "✓ check2" in summary
        assert "✓ check3" in summary
        print("  ✓ All-pass summary formatted correctly")
    
    def test_boot_check_error_structure(self):
        """Test BootCheckError has correct structure."""
        error = BootCheckError(
            component="test_component",
            reason="Test failure reason",
            code="TEST_ERROR_CODE",
        )
        
        assert error.component == "test_component"
        assert error.reason == "Test failure reason"
        assert error.code == "TEST_ERROR_CODE"
        assert "TEST_ERROR_CODE" in str(error)
        assert "test_component" in str(error)
        print("  ✓ BootCheckError structure correct")


class TestFallbackCategories:
    """Test suite for fallback category definitions."""
    
    def test_fallback_categories_defined(self):
        """Test all fallback categories are defined."""
        categories = list(FallbackCategory)
        
        assert FallbackCategory.CRITICAL in categories
        assert FallbackCategory.QUALITY in categories
        assert FallbackCategory.DEVELOPMENT in categories
        assert FallbackCategory.OPERATIONAL in categories
        print(f"  ✓ {len(categories)} fallback categories defined")
    
    def test_fallback_category_values(self):
        """Test fallback category values are correct."""
        assert FallbackCategory.CRITICAL.value == "critical"
        assert FallbackCategory.QUALITY.value == "quality"
        assert FallbackCategory.DEVELOPMENT.value == "development"
        assert FallbackCategory.OPERATIONAL.value == "operational"
        print("  ✓ Fallback category values correct")


class TestRuntimeModes:
    """Test suite for runtime mode definitions."""
    
    def test_runtime_modes_defined(self):
        """Test all runtime modes are defined."""
        modes = list(RuntimeMode)
        
        assert RuntimeMode.PROD in modes
        assert RuntimeMode.DEV in modes
        assert RuntimeMode.EXPLORATORY in modes
        print(f"  ✓ {len(modes)} runtime modes defined")
    
    def test_runtime_mode_values(self):
        """Test runtime mode values are correct."""
        assert RuntimeMode.PROD.value == "prod"
        assert RuntimeMode.DEV.value == "dev"
        assert RuntimeMode.EXPLORATORY.value == "exploratory"
        print("  ✓ Runtime mode values correct")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
