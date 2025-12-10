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
    role: str
    base_score: float
    description: str
    b_theory: float
    b_impl: float
    b_deploy: float


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
            "role": method_data.get("role", ""),
            "base_score": method_data.get("base_score", 0.5),
            "description": method_data.get("description", ""),
            "b_theory": method_data.get("b_theory", 0.5),
            "b_impl": method_data.get("b_impl", 0.5),
            "b_deploy": method_data.get("b_deploy", 0.5),
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
        
        Sigue la ruta canónica F.A.R.F.A.N.:
        1. Executors ALWAYS get 8 layers (SCORE_Q role)
        2. Other methods: derive layers from ROLE using LAYER_REQUIREMENTS mapping
        3. Unknown methods: fallback to "core" (8 layers, conservative)
        
        Args:
            method_id: Method identifier
            
        Returns:
            List of required layer identifiers
        """
        from .layer_requirements import LAYER_REQUIREMENTS
        
        # Special case: Executors always get SCORE_Q role (8 layers)
        if self.is_executor(method_id):
            return LAYER_REQUIREMENTS["score"]["layers"]
        
        # Get method metadata to determine role
        metadata = self.get_metadata(method_id)
        
        if metadata is None:
            # Method not in intrinsic calibration - use conservative default
            return LAYER_REQUIREMENTS["core"]["layers"]
        
        # Get role from metadata
        role = metadata.get("role", "").upper()
        
        # Map role to layer requirement type
        role_to_layer_type = {
            "SCORE_Q": "score",
            "INGEST_PDM": "ingest",
            "STRUCTURE": "processor",
            "EXTRACT": "extractor",
            "AGGREGATE": "core",
            "REPORT": "orchestrator",
            "META_TOOL": "utility",
            "TRANSFORM": "utility",
        }
        
        layer_type = role_to_layer_type.get(role)
        
        if layer_type is None or layer_type not in LAYER_REQUIREMENTS:
            # Unknown role - use conservative default (8 layers)
            return LAYER_REQUIREMENTS["core"]["layers"]
        
        return LAYER_REQUIREMENTS[layer_type]["layers"]
    
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
