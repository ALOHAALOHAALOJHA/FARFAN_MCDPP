"""
CANONICAL INTRINSIC CALIBRATION LOADER

Reads method metadata from config/intrinsic_calibration.json.
Provides get_required_layers_for_method() - the ONLY function that decides layers.

JOBFRONT 4 will implement:
- IntrinsicCalibrationLoader class
- get_intrinsic_loader() singleton
- get_required_layers_for_method(method_id) -> list[str]
"""
# STUB - Implementation in JOBFRONT 4

from typing import TypedDict


class MethodMetadata(TypedDict, total=False):
    """Method metadata from intrinsic_calibration.json."""
    layer: str
    b_theory: float
    b_impl: float
    b_deploy: float
    calibration_status: str


class IntrinsicCalibrationLoader:
    """
    STUB - Will be implemented in JOBFRONT 4.
    
    Loads and caches intrinsic calibration data.
    """
    
    def get_metadata(self, method_id: str) -> MethodMetadata | None:
        """Get metadata for a method."""
        raise NotImplementedError("JOBFRONT 4 pending")
    
    def get_required_layers_for_method(self, method_id: str) -> list[str]:
        """
        OBLIGATORIO: Única función que decide capas de un método.
        
        Flow:
        1. Load intrinsic_calibration.json
        2. Get "layer" field for method_id
        3. Map to LAYER_REQUIREMENTS
        4. Return required layers
        """
        raise NotImplementedError("JOBFRONT 4 pending")
    
    def get_base_score(self, method_id: str) -> float:
        """Get base calibration score for method."""
        raise NotImplementedError("JOBFRONT 4 pending")


def get_intrinsic_loader() -> IntrinsicCalibrationLoader:
    """SINGLETON: Get the canonical intrinsic calibration loader."""
    raise NotImplementedError("JOBFRONT 4 pending")
