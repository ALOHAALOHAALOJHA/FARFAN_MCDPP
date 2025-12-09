"""
COHORT 2024 Configuration Loader

Central loader for all calibration and parametrization files with automatic
path resolution based on COHORT_MANIFEST.json.

Usage:
    from calibration_parametrization_system.cohort_loader import CohortLoader
    
    loader = CohortLoader()
    
    # Load calibration files
    intrinsic_cal = loader.load_calibration("intrinsic_calibration")
    rubric = loader.load_calibration("intrinsic_calibration_rubric")
    questionnaire = loader.load_calibration("questionnaire_monolith")
    method_compat = loader.load_calibration("method_compatibility")
    fusion_weights = loader.load_calibration("fusion_weights")
    method_inventory = loader.load_calibration("canonical_method_inventory")
    
    # Load parametrization files
    runtime_layers = loader.load_parametrization("runtime_layers")
    executor_config = loader.load_parametrization("executor_config")
    
    # Verify cohort metadata
    metadata = loader.get_cohort_metadata()
    assert metadata["cohort_id"] == "COHORT_2024"
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CohortLoader:
    """Loader for COHORT 2024 configuration files."""

    def __init__(self, cohort_dir: Path | None = None):
        if cohort_dir is None:
            cohort_dir = Path(__file__).parent
        self.cohort_dir = cohort_dir
        self.calibration_dir = cohort_dir / "calibration"
        self.parametrization_dir = cohort_dir / "parametrization"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        """Load COHORT_MANIFEST.json."""
        manifest_path = self.cohort_dir / "COHORT_MANIFEST.json"
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)

    def get_cohort_metadata(self) -> dict[str, Any]:
        """Get cohort metadata from manifest."""
        return {
            "cohort_id": self.manifest["cohort_id"],
            "wave_version": self.manifest["wave_version"],
            "migration_date": self.manifest["migration_date"],
        }

    def load_calibration(self, name: str) -> dict[str, Any]:
        """
        Load calibration file by name.

        Args:
            name: Short name (e.g., "intrinsic_calibration", "method_compatibility")

        Returns:
            Loaded JSON data with cohort metadata

        Raises:
            FileNotFoundError: If file not found
            ValueError: If cohort metadata missing or invalid
        """
        filename = f"COHORT_2024_{name}.json"
        file_path = self.calibration_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Calibration file not found: {file_path}\n"
                f"Available names: intrinsic_calibration, intrinsic_calibration_rubric, "
                f"questionnaire_monolith, method_compatibility, fusion_weights, "
                f"canonical_method_inventory"
            )

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        self._validate_cohort_metadata(data, filename)
        return data

    def load_parametrization(self, name: str) -> dict[str, Any]:
        """
        Load parametrization file by name.

        Args:
            name: Short name (e.g., "runtime_layers", "executor_config")

        Returns:
            Loaded JSON data with cohort metadata

        Raises:
            FileNotFoundError: If file not found
            ValueError: If cohort metadata missing or invalid
        """
        filename = f"COHORT_2024_{name}.json"
        file_path = self.parametrization_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Parametrization file not found: {file_path}\n"
                f"Available names: runtime_layers, executor_config"
            )

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        self._validate_cohort_metadata(data, filename)
        return data

    def _validate_cohort_metadata(self, data: dict[str, Any], filename: str) -> None:
        """Validate cohort metadata in loaded file."""
        if "_cohort_metadata" not in data:
            raise ValueError(
                f"Missing _cohort_metadata in {filename}. "
                f"All COHORT_2024 files must have embedded metadata."
            )

        metadata = data["_cohort_metadata"]
        required_fields = ["cohort_id", "creation_date", "wave_version"]
        missing = [f for f in required_fields if f not in metadata]
        if missing:
            raise ValueError(
                f"Missing required metadata fields in {filename}: {missing}"
            )

        if metadata["cohort_id"] != "COHORT_2024":
            raise ValueError(
                f"Invalid cohort_id in {filename}: {metadata['cohort_id']} "
                f"(expected COHORT_2024)"
            )

    def list_calibration_files(self) -> list[str]:
        """List all available calibration file names (without COHORT_2024_ prefix)."""
        files = []
        for file_path in self.calibration_dir.glob("COHORT_2024_*.json"):
            name = file_path.stem.replace("COHORT_2024_", "")
            files.append(name)
        return sorted(files)

    def list_parametrization_files(self) -> list[str]:
        """List all available parametrization file names (without COHORT_2024_ prefix)."""
        files = []
        for file_path in self.parametrization_dir.glob("COHORT_2024_*.json"):
            name = file_path.stem.replace("COHORT_2024_", "")
            files.append(name)
        return sorted(files)

    def get_original_path(self, category: str, filename: str) -> str | None:
        """
        Get original path for a migrated file.

        Args:
            category: "calibration" or "parametrization"
            filename: COHORT_2024_* filename

        Returns:
            Original path or None if not found
        """
        files_key = f"{category}_files"
        if files_key not in self.manifest:
            return None

        for file_info in self.manifest[files_key]:
            if file_info["new_filename"] == filename:
                return file_info["original_path"]
        return None


__all__ = ["CohortLoader"]
