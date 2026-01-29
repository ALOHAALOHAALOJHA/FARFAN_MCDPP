"""Tests for ProcessorConfig Pydantic schema."""

import pytest
from pydantic import ValidationError

from farfan_pipeline.methods.processor_config_schema import ProcessorConfigSchema


class TestProcessorConfigSchema:
    """Validate ProcessorConfig Pydantic schema."""

    def test_valid_config_accepted(self):
        config = ProcessorConfigSchema(
            enable_semantic_tagging=True,
            confidence_threshold=0.7,
            context_window_chars=500,
            max_evidence_per_pattern=10,
        )
        assert config.enable_semantic_tagging is True
        assert config.confidence_threshold == 0.7

    def test_invalid_utf8_normalization_form_rejected(self):
        with pytest.raises(ValidationError, match="utf8_normalization_form"):
            ProcessorConfigSchema(utf8_normalization_form="INVALID_FORM")

    def test_invalid_spacy_model_rejected(self):
        with pytest.raises(ValidationError, match="preferred_spacy_model"):
            ProcessorConfigSchema(preferred_spacy_model="invalid_model")

    def test_threshold_bounds_enforced(self):
        with pytest.raises(ValidationError):
            ProcessorConfigSchema(confidence_threshold=1.5)  # > 1.0

        with pytest.raises(ValidationError):
            ProcessorConfigSchema(confidence_threshold=-0.5)  # < 0.0

    def test_sentence_length_validation(self):
        # Valid configuration
        config = ProcessorConfigSchema(min_sentence_length=50, max_sentence_length=300)
        assert config.min_sentence_length == 50
        assert config.max_sentence_length == 300

        # Invalid: min >= max
        with pytest.raises(
            ValidationError, match="min_sentence_length must be less than max_sentence_length"
        ):
            ProcessorConfigSchema(min_sentence_length=600, max_sentence_length=500)

    def test_context_window_validation(self):
        with pytest.raises(ValidationError, match="context_window_chars must be at least 100"):
            ProcessorConfigSchema(context_window_chars=50)  # < 100

    def test_probability_ranges(self):
        with pytest.raises(ValidationError, match="entropy_weight must be in"):
            ProcessorConfigSchema(entropy_weight=1.5)

        with pytest.raises(ValidationError, match="proximity_decay_rate must be in"):
            ProcessorConfigSchema(proximity_decay_rate=-0.1)

        with pytest.raises(ValidationError, match="bayesian_prior_confidence must be in"):
            ProcessorConfigSchema(bayesian_prior_confidence=1.2)

        with pytest.raises(ValidationError, match="bayesian_entropy_weight must be in"):
            ProcessorConfigSchema(bayesian_entropy_weight=-0.2)
