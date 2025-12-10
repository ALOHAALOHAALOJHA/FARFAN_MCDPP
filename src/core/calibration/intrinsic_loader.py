"""
CANONICAL INTRINSIC CALIBRATION LOADER
Single source of truth for method metadata and layer requirements.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict


class MethodMetadata(TypedDict, total=False):
    """Method metadata from intrinsic calibration."""
    layer: str
    role: str
    base_score: float
    description: str


class IntrinsicCalibrationLoader:
    """
    CANONICAL loader for intrinsic calibration data.
    Reads method metadata including layer requirements from JSON.
    """
    
    def __init__(self, calibration_path: str | Path | None = None):
        if calibration_path is None:
            calibration_path = self._get_default_path()
        self.calibration_path = Path(calibration_path)
        self._data: dict[str, Any] | None = None
        self._method_cache: dict[str, MethodMetadata] = {}
    
    def _get_default_path(self) -> Path:
        """Get default path to intrinsic calibration JSON."""
        return (
            Path(__file__).parent.parent.parent
            / "cross_cutting_infrastrucuture"
            / "capaz_calibration_parmetrization"
            / "calibration"
            / "COHORT_2024_intrinsic_calibration.json"
        )
    
    def _load_data(self) -> dict[str, Any]:
        """Load calibration data from JSON."""
        if self._data is None:
            with open(self.calibration_path) as f:
                self._data = json.load(f)
        return self._data
    
    def get_metadata(self, method_id: str) -> MethodMetadata | None:
        """
        Get metadata for a method.
        Returns None if method not found.
        """
        if method_id in self._method_cache:
            return self._method_cache[method_id]
        
        data = self._load_data()
        methods = data.get("methods", {})
        
        if method_id not in methods:
            return None
        
        method_data = methods[method_id]
        metadata: MethodMetadata = {
            "layer": method_data.get("layer"),
            "role": method_data.get("role"),
            "base_score": method_data.get("base_score", 0.5),
            "description": method_data.get("description", ""),
        }
        
        self._method_cache[method_id] = metadata
        return metadata
    
    def is_executor(self, method_id: str) -> bool:
        """
        Check if method is an executor (D1Q1-D6Q5).
        
        Public API for executor detection.
        
        Args:
            method_id: Method identifier to check
            
        Returns:
            True if method is an executor, False otherwise
        """
        method_lower = method_id.lower()
        if "executor" in method_lower:
            return True
        if method_lower.startswith("d") and "q" in method_lower:
            parts = method_lower.split("_")
            if parts and parts[0].startswith("d") and "q" in parts[0]:
                return True
        return False
    
    def get_required_layers_for_method(self, method_id: str) -> list[str]:
        """
        OBLIGATORIO: Única función que decide capas de un método.
        Lee campo "layer" de intrinsic_calibration.json.
        
        Priority:
        1. Executors ALWAYS get 8 layers (full context)
        2. Method-specific "layer" field from JSON
        3. Fallback to "core" (conservative 8 layers)
        """
        from .layer_requirements import LAYER_REQUIREMENTS
        
        if self.is_executor(method_id):
            return ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]
        
        metadata = self.get_metadata(method_id)
        if metadata is None:
            return LAYER_REQUIREMENTS["core"]["layers"]
        
        method_type = metadata.get("layer")
        if method_type is None or method_type not in LAYER_REQUIREMENTS:
            return LAYER_REQUIREMENTS["core"]["layers"]
        
        return LAYER_REQUIREMENTS[method_type]["layers"]
    
    def get_base_score(self, method_id: str) -> float:
        """Get base calibration score for method."""
        metadata = self.get_metadata(method_id)
        if metadata is None:
            return 0.5
        return metadata.get("base_score", 0.5)
    
    def get_all_method_ids(self) -> list[str]:
        """Get all method IDs in the calibration data."""
        data = self._load_data()
        methods = data.get("methods", {})
        return [k for k in methods.keys() if not k.startswith("_")]


_intrinsic_loader: IntrinsicCalibrationLoader | None = None


def get_intrinsic_loader() -> IntrinsicCalibrationLoader:
    """
    SINGLETON: Get the canonical intrinsic calibration loader.
    """
    global _intrinsic_loader
    if _intrinsic_loader is None:
        _intrinsic_loader = IntrinsicCalibrationLoader()
    return _intrinsic_loader


def get_required_layers_for_method(method_id: str) -> list[str]:
    """
    OBLIGATORIO: Get required layers for a method.
    
    This is the canonical function to determine which layers a method needs.
    Delegates to the singleton IntrinsicCalibrationLoader.
    
    Args:
        method_id: Method identifier
        
    Returns:
        List of required layer identifiers (e.g., ["@b", "@chain", "@q", ...])
    """
    loader = get_intrinsic_loader()
    return loader.get_required_layers_for_method(method_id)


def is_executor(method_id: str) -> bool:
    """
    Check if method is an executor (D1Q1-D6Q5).
    
    Args:
        method_id: Method identifier to check
        
    Returns:
        True if method is an executor, False otherwise
    """
    loader = get_intrinsic_loader()
    return loader.is_executor(method_id)


__all__ = [
    "IntrinsicCalibrationLoader",
    "get_intrinsic_loader",
    "MethodMetadata",
    "get_required_layers_for_method",
    "is_executor",
]
