"""
Contract Governance Utilities
"""
from typing import Type, Any, Callable
import functools

def uses_contract(contract_class: Type[Any]) -> Callable:
    """
    Decorator to explicitly declare that a function or class relies on a specific contract.
    This serves as documentation and allows for static analysis of contract dependencies.
    
    Usage:
        @uses_contract(RoutingContract)
        def my_function():
            ...
    """
    def decorator(obj: Any) -> Any:
        if not hasattr(obj, "_contract_dependencies"):
            obj._contract_dependencies = []
        obj._contract_dependencies.append(contract_class)
        
        # If it's a function, wrap it to preserve metadata
        if callable(obj) and not isinstance(obj, type):
            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                return obj(*args, **kwargs)
            wrapper._contract_dependencies = obj._contract_dependencies
            return wrapper
            
        return obj
    return decorator
