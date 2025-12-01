"""Farfan Core Package Initialization.
"""

from .core.calibration.parameter_loader import ParameterLoader

_parameter_loader = None

def get_parameter_loader() -> "ParameterLoader":
    """
    OBLIGATORY: Single way to get the parameter loader.

    Singleton global - guarantees EVERYONE uses the same one.
    """
    global _parameter_loader

    if _parameter_loader is None:
        _parameter_loader = ParameterLoader()
        _parameter_loader.load()

    return _parameter_loader

__all__ = ["get_parameter_loader"]
