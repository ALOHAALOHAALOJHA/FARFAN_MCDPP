
import pytest
from pathlib import Path
from canonic_phases.phase_0_input_validation.phase0_signature_validator import (
    SignatureRegistry,
    FunctionSignature,
    validate_signature,
    validate_call_signature,
    _signature_registry
)

def test_signature_registry():
    registry = SignatureRegistry(registry_path=Path("tmp_registry.json"))

    def my_func(a: int, b: str) -> bool:
        return True

    sig = registry.register_function(my_func)

    assert sig.function_name == "my_func"
    assert "a" in sig.parameters
    assert sig.parameter_types["a"] == str(int)

    retrieved = registry.get_signature("tests.canonic_phases.test_signature_validator", None, "my_func")
    # Note: module name depends on how test is run

    # Clean up
    if registry.registry_path.exists():
        registry.registry_path.unlink()

def test_validate_signature_decorator():
    @validate_signature(enforce=True)
    def my_func(a: int) -> int:
        return a + 1

    assert my_func(1) == 2

    with pytest.raises(TypeError):
        my_func("string") # type: ignore

def test_validate_call_signature():
    def my_func(a: int, b: int):
        pass

    assert validate_call_signature(my_func, 1, 2)
    assert not validate_call_signature(my_func, 1) # Missing arg
