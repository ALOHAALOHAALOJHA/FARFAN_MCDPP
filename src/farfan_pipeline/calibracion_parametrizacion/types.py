"""
Type definitions for calibration and parametrization module.
Stub module for test execution.
"""
from dataclasses import dataclass, field
from typing import Any

@dataclass
class CalibrationThreshold:
    """Threshold configuration."""
    value: float = 0.7
    min_value: float = 0.0
    max_value: float = 1.0

@dataclass
class ParameterSet:
    """Set of parameters for calibration."""
    name: str = "default"
    values: dict[str, Any] = field(default_factory=dict)

__all__ = ["CalibrationThreshold", "ParameterSet"]
