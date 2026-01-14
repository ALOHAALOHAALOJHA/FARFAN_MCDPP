import pytest
import logging
import json
from farfan_pipeline.phases.Phase_0.primitives.json_logger import (
    JsonFormatter,
    get_json_logger
)

def test_json_formatter():
    """Test JSON log formatting."""
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    record.correlation_id = "123"
    
    formatter = JsonFormatter()
    output = formatter.format(record)
    data = json.loads(output)
    
    assert data["message"] == "Test message"
    assert data["correlation_id"] == "123"
    assert data["level"] == "INFO"

def test_get_json_logger():
    """Test logger factory."""
    logger = get_json_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert any(isinstance(h.formatter, JsonFormatter) for h in logger.handlers)
