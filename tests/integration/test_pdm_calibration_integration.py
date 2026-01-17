"""
Tests de integración completa entre PDM y calibración epistémica.

Valida que:
- PDM profile alimenta calibration registry correctamente
- Ajustes PDM-driven se aplican en todas las capas
- Invariantes constitucionales se preservan
"""

from __future__ import annotations

import pytest

# DELETED_MODULE: from farfan_pipeline.calibration.registry import EpistemicRegistry
from farfan_pipeline.pdm.profiles import ProfileManager


class TestPDMCalibrationIntegration:
    """Test PDM and calibration integration."""

    def test_pdm_profile_feeds_calibration_registry(self) -> None:
        """PDM profile alimenta calibration registry correctamente."""
        # Create PDM profile
        profile_manager = ProfileManager()
        profile = profile_manager.create_default_profile()

        # Create calibration registry
        registry = EpistemicRegistry()

        # Feed profile to registry
        registry.apply_pdm_profile(profile)

        # Verify profile is applied
        assert registry.get_active_profile() == profile

    def test_pdm_adjustments_applied_all_layers(self) -> None:
        """Ajustes PDM-driven se aplican en todas las capas."""
        profile_manager = ProfileManager()
        profile = profile_manager.create_high_precision_profile()

        registry = EpistemicRegistry()
        registry.apply_pdm_profile(profile)

        # Verify adjustments in all layers
        assert registry.get_layer_config("base")["precision"] >= 0.90
        assert registry.get_layer_config("semantic")["precision"] >= 0.90

    def test_constitutional_invariants_preserved(self) -> None:
        """Invariantes constitucionales se preservan."""
        registry = EpistemicRegistry()

        # Get constitutional invariants
        invariants = registry.get_constitutional_invariants()

        # Verify core invariants
        assert "min_confidence" in invariants
        assert invariants["min_confidence"] >= 0.0
        assert invariants["min_confidence"] <= 1.0
