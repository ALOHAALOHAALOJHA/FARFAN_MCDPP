# tests/test_processor_config_schema.py
import pytest
from pydantic import ValidationError
from farfan_pipeline.methods.processor_config_schema import ProcessorConfigSchema


class TestProcessorConfigSchema:
    """Validate ProcessorConfig Pydantic schema."""
    
    def test_valid_config_accepted(self):
        config = ProcessorConfigSchema(
            preserve_document_structure=True,
            enable_semantic_tagging=True,
            confidence_threshold=0.62,
            context_window_chars=400,
            max_evidence_per_pattern=5,
        )
        assert config.preserve_document_structure is True
        assert config.confidence_threshold == 0.62
    
    def test_invalid_utf8_normalization_form_rejected(self):
        with pytest.raises(ValidationError, match="utf8_normalization_form"):
            ProcessorConfigSchema(utf8_normalization_form="invalid_form")
    
    def test_threshold_bounds_enforced(self):
        with pytest.raises(ValidationError):
            ProcessorConfigSchema(confidence_threshold=1.5)  # > 1.0
        
        with pytest.raises(ValidationError):
            ProcessorConfigSchema(confidence_threshold=-0.1)  # < 0.0
    
    def test_sentence_length_validation(self):
        with pytest.raises(ValidationError):
            ProcessorConfigSchema(
                min_sentence_length=100,
                max_sentence_length=50  # min > max
            )
    
    def test_context_window_bounds(self):
        with pytest.raises(ValidationError):
            ProcessorConfigSchema(context_window_chars=50)  # < 100