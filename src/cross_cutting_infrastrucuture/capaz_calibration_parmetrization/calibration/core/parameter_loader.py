"""
PARAMETER LOADER - Runtime parameters for methods

Reads from config/method_parameters.json.
Separate from calibration (quality scores).

JOBFRONT 4 will implement:
- ParameterLoader class
- get_parameter_loader() singleton
"""
# STUB - Implementation in JOBFRONT 4


class ParameterLoader:
    """
    STUB - Will be implemented in JOBFRONT 4.
    
    Loads runtime parameters for methods.
    """
    
    def get(self, method_id: str) -> dict:
        """Get parameters for a method."""
        raise NotImplementedError("JOBFRONT 4 pending")
    
    def get_threshold(self, method_id: str, default: float = 0.7) -> float:
        """Get validation threshold for a method."""
        raise NotImplementedError("JOBFRONT 4 pending")


def get_parameter_loader() -> ParameterLoader:
    """SINGLETON: Get the canonical parameter loader."""
    raise NotImplementedError("JOBFRONT 4 pending")
