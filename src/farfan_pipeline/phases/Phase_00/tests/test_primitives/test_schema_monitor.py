import pytest
import sys
from unittest.mock import MagicMock

# Mock external dependency BEFORE importing schema_monitor
mock_params = MagicMock()
mock_params.ParameterLoaderV2.get.return_value = 0.05
sys.modules["farfan_pipeline.core.parameters"] = mock_params
sys.modules["farfan_pipeline.core"] = MagicMock() # Ensure parent exists

from farfan_pipeline.phases.Phase_00.primitives.schema_monitor import (
    SchemaDriftDetector,
    PayloadValidator
)

def test_drift_detection():
    detector = SchemaDriftDetector(sample_rate=1.0) # Always sample
    
    # Baseline
    detector.record_payload({"a": 1, "b": "s"}, source="test")
    detector.baseline_schema["test"] = {
        "keys": {"a", "b"},
        "types": {"a": "int", "b": "str"},
        "sample_values": {},
        "timestamp": ""
    }
    
    # New key
    detector.record_payload({"a": 1, "b": "s", "c": 2}, source="test")
    alerts = detector.get_alerts(source="test")
    
    assert any(a["type"] == "NEW_KEYS" for a in alerts)
    assert "c" in alerts[0]["keys"]

def test_payload_validator():
    validator = PayloadValidator()
    validator.schemas["test"] = {"required_keys": ["id"], "types": {"id": "int"}}
    
    # Valid
    validator.validate({"id": 1}, source="test")
    
    # Missing key
    with pytest.raises(ValueError):
        validator.validate({"name": "foo"}, source="test")
        
    # Wrong type
    with pytest.raises(TypeError):
        validator.validate({"id": "string"}, source="test")