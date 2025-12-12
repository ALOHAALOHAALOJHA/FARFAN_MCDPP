"""
Import Adapters for COHORT 2024 Migration

Provides backward-compatible import paths for code that references old configuration
file locations. Automatically redirects to COHORT_2024 files with metadata validation.

This module allows existing code to continue working without modification while
enforcing the new cohort structure.

Usage in existing code (no changes needed):
    from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration import intrinsic_calibration_loader
    # Automatically loads from calibration_parametrization_system/calibration/
    
    from orchestration.orchestrator import executor_config
    # Automatically loads from calibration_parametrization_system/parametrization/
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .cohort_loader import CohortLoader

_cohort_loader = CohortLoader()


class ConfigPathAdapter:
    """
    Adapter that intercepts config file loads and redirects to COHORT_2024 files.
    """

    PATH_MAPPINGS = {
        "system/config/calibration/intrinsic_calibration.json": "intrinsic_calibration",
        "system/config/calibration/intrinsic_calibration_rubric.json": "intrinsic_calibration_rubric",
        "system/config/questionnaire/questionnaire_monolith.json": "questionnaire_monolith",
        "system/config/calibration/runtime_layers.json": "runtime_layers",
        "config/json_files_ no_schemas/method_compatibility.json": "method_compatibility",
        "config/json_files_ no_schemas/fusion_specification.json": "fusion_weights",
        "config/json_files_ no_schemas/executor_config.json": "executor_config",
        "scripts/inventory/canonical_method_inventory.json": "canonical_method_inventory",
    }

    CATEGORY_MAP = {
        "intrinsic_calibration": "calibration",
        "intrinsic_calibration_rubric": "calibration",
        "questionnaire_monolith": "calibration",
        "method_compatibility": "calibration",
        "fusion_weights": "calibration",
        "canonical_method_inventory": "calibration",
        "runtime_layers": "parametrization",
        "executor_config": "parametrization",
    }

    @classmethod
    def load_config(cls, original_path: str) -> dict[str, Any]:
        """
        Load config from original path, automatically redirecting to COHORT_2024.

        Args:
            original_path: Original config file path (e.g., "system/config/calibration/intrinsic_calibration.json")

        Returns:
            Config dict with _cohort_metadata

        Raises:
            FileNotFoundError: If mapping not found for original path
        """
        # Normalize path
        original_path = original_path.replace("\\", "/")

        if original_path not in cls.PATH_MAPPINGS:
            raise FileNotFoundError(
                f"No COHORT_2024 mapping found for: {original_path}\n"
                f"Available mappings: {list(cls.PATH_MAPPINGS.keys())}"
            )

        config_name = cls.PATH_MAPPINGS[original_path]
        category = cls.CATEGORY_MAP[config_name]

        if category == "calibration":
            return _cohort_loader.load_calibration(config_name)
        else:
            return _cohort_loader.load_parametrization(config_name)

    @classmethod
    def get_cohort_path(cls, original_path: str) -> Path:
        """
        Get the COHORT_2024 file path for an original path.

        Args:
            original_path: Original config file path

        Returns:
            Path to COHORT_2024 file
        """
        original_path = original_path.replace("\\", "/")

        if original_path not in cls.PATH_MAPPINGS:
            raise FileNotFoundError(f"No COHORT_2024 mapping for: {original_path}")

        config_name = cls.PATH_MAPPINGS[original_path]
        category = cls.CATEGORY_MAP[config_name]

        cohort_dir = Path(__file__).parent
        if category == "calibration":
            return cohort_dir / "calibration" / f"COHORT_2024_{config_name}.json"
        else:
            return cohort_dir / "parametrization" / f"COHORT_2024_{config_name}.json"


def patch_json_loads():
    """
    Monkey-patch json.load/json.loads to intercept config loads.

    WARNING: This is a nuclear option. Only use if automated path updates fail.
    Prefer explicit import updates via ConfigPathAdapter.load_config().
    """
    import json

    _original_load = json.load

    def patched_load(fp, *args, **kwargs):
        result = _original_load(fp, *args, **kwargs)
        # Check if this looks like a config file missing cohort metadata
        if (
            isinstance(result, dict)
            and "_metadata" in result
            and "_cohort_metadata" not in result
        ):
            import warnings

            warnings.warn(
                f"Loaded config file without cohort metadata: {getattr(fp, 'name', 'unknown')}. "
                f"Consider using ConfigPathAdapter.load_config() for automatic COHORT_2024 routing.",
                UserWarning,
                stacklevel=2,
            )
        return result

    json.load = patched_load


__all__ = ["ConfigPathAdapter", "patch_json_loads"]
