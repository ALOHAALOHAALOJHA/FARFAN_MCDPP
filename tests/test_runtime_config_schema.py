# tests/test_runtime_config_schema.py
import pytest
from pydantic import ValidationError
from farfan_pipeline.phases.Phase_zero.runtime_config_schema import RuntimeConfigSchema, RuntimeMode


class TestRuntimeConfigSchema:
    """Validate RuntimeConfig Pydantic schema."""
    
    def test_valid_config_accepted(self):
        config = RuntimeConfigSchema(
            mode=RuntimeMode.DEV,
            allow_contradiction_fallback=False,
            expected_question_count=305,
            expected_method_count=416,
            phase_timeout_seconds=300,
        )
        assert config.mode == RuntimeMode.DEV
        assert config.expected_question_count == 305
        assert config.allow_contradiction_fallback is False
        assert config.expected_method_count == 416
        assert config.phase_timeout_seconds == 300

    def test_prod_mode_constraints(self):
        # Valid PROD config
        config = RuntimeConfigSchema(
            mode=RuntimeMode.PROD,
            allow_dev_ingestion_fallbacks=False,
            allow_execution_estimates=False,
            allow_aggregation_defaults=False,
            allow_missing_base_weights=False,
        )
        assert config.mode == RuntimeMode.PROD
        
        # Invalid PROD config - should raise error
        with pytest.raises(ValueError, match="PROD mode forbids"):
            RuntimeConfigSchema(
                mode=RuntimeMode.PROD,
                allow_dev_ingestion_fallbacks=True,  # Forbidden in PROD
            )
    
    def test_question_count_must_be_positive(self):
        with pytest.raises(ValueError, match="expected_question_count must be positive"):
            RuntimeConfigSchema(expected_question_count=0)

    def test_phase_timeout_minimum(self):
        with pytest.raises(ValueError, match="phase_timeout_seconds must be at least 10"):
            RuntimeConfigSchema(phase_timeout_seconds=5)

    def test_max_workers_range(self):
        with pytest.raises(ValueError, match="max_workers must be between 1 and 64"):
            RuntimeConfigSchema(max_workers=100)

    def test_batch_size_must_be_positive(self):
        with pytest.raises(ValueError, match="batch_size must be positive"):
            RuntimeConfigSchema(batch_size=0)