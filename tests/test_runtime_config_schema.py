"""Tests for RuntimeConfig Pydantic schema with PROD mode enforcement."""

import pytest
from pydantic import ValidationError

from farfan_pipeline.phases.Phase_zero.runtime_config_schema import RuntimeConfigSchema, RuntimeMode


class TestRuntimeConfigSchema:
    """Validate RuntimeConfig Pydantic schema with PROD mode enforcement."""

    def test_valid_config_accepted(self):
        config = RuntimeConfigSchema(
            mode=RuntimeMode.DEV,
            allow_contradiction_fallback=False,
            allow_validator_disable=False,
            expected_question_count=300,
            expected_method_count=400,
            phase_timeout_seconds=600,
            max_workers=8,
            batch_size=200,
        )
        assert config.mode == RuntimeMode.DEV
        assert config.expected_question_count == 300

    def test_prod_mode_enforcement(self):
        # Valid PROD config
        prod_config = RuntimeConfigSchema(
            mode=RuntimeMode.PROD,
            allow_dev_ingestion_fallbacks=False,
            allow_execution_estimates=False,
            allow_aggregation_defaults=False,
            allow_missing_base_weights=False,
        )
        # This should not raise an exception
        assert prod_config.mode == RuntimeMode.PROD

        # Invalid PROD config - should raise error
        with pytest.raises(ValueError, match="PROD mode forbids"):
            RuntimeConfigSchema(
                mode=RuntimeMode.PROD,
                allow_dev_ingestion_fallbacks=True,  # Forbidden in PROD
            )

        with pytest.raises(ValueError, match="PROD mode forbids"):
            RuntimeConfigSchema(
                mode=RuntimeMode.PROD,
                allow_execution_estimates=True,  # Forbidden in PROD
            )

        with pytest.raises(ValueError, match="PROD mode forbids"):
            RuntimeConfigSchema(
                mode=RuntimeMode.PROD,
                allow_aggregation_defaults=True,  # Forbidden in PROD
            )

        with pytest.raises(ValueError, match="PROD mode forbids"):
            RuntimeConfigSchema(
                mode=RuntimeMode.PROD,
                allow_missing_base_weights=True,  # Forbidden in PROD
            )

    def test_processing_config_validation(self):
        # Test valid values
        config = RuntimeConfigSchema(
            expected_question_count=500,
            expected_method_count=600,
            phase_timeout_seconds=1800,
            max_workers=16,
            batch_size=5000,
        )
        assert config.expected_question_count == 500

        # Test invalid values
        with pytest.raises(ValueError, match="expected_question_count must be positive"):
            RuntimeConfigSchema(expected_question_count=0)

        with pytest.raises(ValueError, match="expected_method_count must be positive"):
            RuntimeConfigSchema(expected_method_count=0)

        with pytest.raises(ValueError, match="phase_timeout_seconds must be at least 10"):
            RuntimeConfigSchema(phase_timeout_seconds=5)

        with pytest.raises(ValueError, match="max_workers must be between 1 and 64"):
            RuntimeConfigSchema(max_workers=0)

        with pytest.raises(ValueError, match="max_workers must be between 1 and 64"):
            RuntimeConfigSchema(max_workers=65)

        with pytest.raises(ValueError, match="batch_size must be positive"):
            RuntimeConfigSchema(batch_size=0)