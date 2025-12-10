"""
CANONICAL PARAMETER LOADER
Single source of truth for method runtime parameters.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict


class MethodParameters(TypedDict, total=False):
    """Method runtime parameters."""
    parameters: dict[str, Any]
    validation: dict[str, Any]


class ParameterLoader:
    """
    CANONICAL loader for method runtime parameters.
    Reads method-specific parameters from JSON configuration.
    """
    
    def __init__(self, parameters_path: str | Path | None = None):
        if parameters_path is None:
            parameters_path = self._get_default_path()
        self.parameters_path = Path(parameters_path)
        self._data: dict[str, Any] | None = None
        self._method_cache: dict[str, MethodParameters] = {}
    
    def _get_default_path(self) -> Path:
        """Get default path to method parameters JSON."""
        return (
            Path(__file__).parent.parent.parent
            / "cross_cutting_infrastrucuture"
            / "capaz_calibration_parmetrization"
            / "parametrization"
            / "COHORT_2024_method_parameters.json"
        )
    
    def _load_data(self) -> dict[str, Any]:
        """Load parameter data from JSON."""
        if self._data is None:
            with open(self.parameters_path) as f:
                self._data = json.load(f)
        return self._data
    
    def get_parameters(self, method_id: str) -> dict[str, Any]:
        """
        Get runtime parameters for a method.
        
        Args:
            method_id: Method identifier
            
        Returns:
            Dictionary of runtime parameters
        """
        if method_id in self._method_cache:
            cached = self._method_cache[method_id]
            return cached.get("parameters", {})
        
        data = self._load_data()
        methods = data.get("methods", {})
        
        if method_id not in methods:
            # Try to get defaults based on method type
            return self._get_default_parameters(method_id)
        
        method_data = methods[method_id]
        params: MethodParameters = {
            "parameters": method_data.get("parameters", {}),
            "validation": method_data.get("validation", {}),
        }
        
        self._method_cache[method_id] = params
        return params.get("parameters", {})
    
    def _get_default_parameters(self, method_id: str) -> dict[str, Any]:
        """Get default parameters based on method type."""
        data = self._load_data()
        defaults = data.get("defaults", {})
        
        method_lower = method_id.lower()
        
        if "executor" in method_lower or (method_lower.startswith("d") and "q" in method_lower):
            return defaults.get("executor", {})
        elif "ingest" in method_lower:
            return defaults.get("ingest", {})
        elif "processor" in method_lower or "structure" in method_lower:
            return defaults.get("processor", {})
        elif "extract" in method_lower:
            return defaults.get("extractor", {})
        elif "report" in method_lower or "orchestrator" in method_lower:
            return defaults.get("orchestrator", {})
        
        return {}
    
    def get_parameter(
        self,
        method_id: str,
        parameter_name: str,
        default: Any = None
    ) -> Any:
        """
        Get a specific parameter value for a method.
        
        Args:
            method_id: Method identifier
            parameter_name: Name of the parameter
            default: Default value if parameter not found
            
        Returns:
            Parameter value or default
        """
        params = self.get_parameters(method_id)
        return params.get(parameter_name, default)
    
    def get_validation_rules(self, method_id: str) -> dict[str, Any]:
        """
        Get validation rules for method parameters.
        
        Args:
            method_id: Method identifier
            
        Returns:
            Dictionary of validation rules
        """
        if method_id in self._method_cache:
            cached = self._method_cache[method_id]
            return cached.get("validation", {})
        
        data = self._load_data()
        methods = data.get("methods", {})
        
        if method_id not in methods:
            return {}
        
        method_data = methods[method_id]
        return method_data.get("validation", {})
    
    def get_all_method_ids(self) -> list[str]:
        """Get all method IDs with parameter configurations."""
        data = self._load_data()
        methods = data.get("methods", {})
        return [k for k in methods.keys() if not k.startswith("_")]
    
    def validate_parameter(
        self,
        method_id: str,
        parameter_name: str,
        value: Any
    ) -> bool:
        """
        Validate a parameter value against its validation rules.
        
        Args:
            method_id: Method identifier
            parameter_name: Name of the parameter
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        validation_rules = self.get_validation_rules(method_id)
        
        if parameter_name not in validation_rules:
            return True  # No validation rules = always valid
        
        rules = validation_rules[parameter_name]
        param_type = rules.get("type")
        
        # Type validation
        if param_type == "int" and not isinstance(value, int):
            return False
        elif param_type == "float" and not isinstance(value, (int, float)):
            return False
        elif param_type == "string" and not isinstance(value, str):
            return False
        
        # Range validation
        if "range" in rules:
            min_val, max_val = rules["range"]
            if not (min_val <= value <= max_val):
                return False
        
        # Allowed values validation
        if "allowed_values" in rules:
            if value not in rules["allowed_values"]:
                return False
        
        return True


_parameter_loader: ParameterLoader | None = None


def get_parameter_loader() -> ParameterLoader:
    """
    SINGLETON: Get the canonical parameter loader.
    """
    global _parameter_loader
    if _parameter_loader is None:
        _parameter_loader = ParameterLoader()
    return _parameter_loader


def get_method_parameters(method_id: str) -> dict[str, Any]:
    """
    Convenience function to get method parameters.
    
    Args:
        method_id: Method identifier
        
    Returns:
        Dictionary of runtime parameters
    """
    loader = get_parameter_loader()
    return loader.get_parameters(method_id)


def get_method_parameter(
    method_id: str,
    parameter_name: str,
    default: Any = None
) -> Any:
    """
    Convenience function to get a specific method parameter.
    
    Args:
        method_id: Method identifier
        parameter_name: Name of the parameter
        default: Default value if parameter not found
        
    Returns:
        Parameter value or default
    """
    loader = get_parameter_loader()
    return loader.get_parameter(method_id, parameter_name, default)


__all__ = [
    "ParameterLoader",
    "get_parameter_loader",
    "get_method_parameters",
    "get_method_parameter",
    "MethodParameters",
]
