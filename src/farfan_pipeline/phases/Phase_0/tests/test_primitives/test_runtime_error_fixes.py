import pytest
from farfan_pipeline.phases.Phase_0.primitives.runtime_error_fixes import (
    ensure_list_return,
    safe_text_extract,
    safe_weighted_multiply,
    safe_list_iteration
)

def test_ensure_list_return():
    assert ensure_list_return([1, 2]) == [1, 2]
    assert ensure_list_return(None) == []
    assert ensure_list_return(True) == []
    assert ensure_list_return("string") == ["s", "t", "r", "i", "n", "g"] # list(str) behavior

def test_safe_text_extract():
    class TextObj:
        text = "content"
    
    assert safe_text_extract("simple") == "simple"
    assert safe_text_extract(TextObj()) == "content"
    assert safe_text_extract(123) == "123"

def test_safe_weighted_multiply():
    assert safe_weighted_multiply([1, 2], 2) == [2, 4]
    assert safe_weighted_multiply([], 2) == []
    # Test numpy if available, handled internally
    
def test_safe_list_iteration():
    assert safe_list_iteration([1, 2]) == [1, 2]
    assert safe_list_iteration("test") == ["test"] # String treated as single item
    assert safe_list_iteration(None) == []
    assert safe_list_iteration(True) == []
