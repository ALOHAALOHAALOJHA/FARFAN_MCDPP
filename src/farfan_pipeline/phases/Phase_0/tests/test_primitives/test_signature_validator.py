import pytest
from farfan_pipeline.phases.Phase_0.primitives.signature_validator import (
    validate_signature,
    validate_call_signature
)

def test_validate_signature_decorator():
    @validate_signature(enforce=True)
    def add(a: int, b: int) -> int:
        return a + b
        
    assert add(1, 2) == 3
    
    # Validation usually checks arguments against signature
    # If we pass wrong types but python accepts them, signature binding works
    # This validator checks if *arguments match the signature structure*, not type checking
    # e.g. missing argument
    with pytest.raises(TypeError):
        add(1) # Missing 'b'

def test_validate_call_signature():
    def func(x, y): pass
    
    assert validate_call_signature(func, 1, 2) is True
    assert validate_call_signature(func, 1) is False # Missing arg
