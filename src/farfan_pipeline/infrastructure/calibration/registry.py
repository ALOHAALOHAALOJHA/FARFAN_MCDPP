"""
Epistemic Calibration Registry - 8-Layer Resolution System
===========================================================

Module: registry.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Orchestrate hierarchical calibration resolution with PDM sensitivity
Lifecycle State: DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 4.0.0-epistemological

CONSTITUTIONAL PRINCIPLES ENFORCED:
    CI-03: INMUTABILIDAD EPISTÉMICA - Level never changes post-resolution
    CI-04: ASIMETRÍA POPPERIANA - N3 has veto authority over N1/N2
    CI-05: SEPARACIÓN CALIBRACIÓN-NIVEL - PDM adjusts parameters, not level

8-LAYER RESOLUTION ARCHITECTURE:
    Layer 0: Global defaults (seed, timeouts)
    Layer 1: Level defaults (N0-N4 from level_configs/*.json)
    Layer 2: Contract type overrides (TYPE_A-E from type_configs/*.json)
    Layer 3: Method-specific overrides (from method_registry)
    Layer 4: PDM-driven adjustments (Python logic based on document structure)
    Layer 5-7: Reserved for future extensions

CRITICAL: The level determined in Layer 1 is IMMUTABLE through all
subsequent layers. PDM adjustments (Layer 4) can ONLY modify parameter
values, NEVER the epistemic level itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Final

from .calibration_core import (
    ClosedInterval,
    EpistemicLevel,
    ValidationError,
    validate_epistemic_level,
)
from .epistemic_core import (
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    N3AuditCalibration,
    N4MetaCalibration,
    N0InfrastructureCalibration,
    PDMSensitivity,
    create_calibration,
)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class CalibrationResolutionError(ValidationError):
    """
    Raised when calibration cannot be resolved.

    This indicates a configuration error that must be fixed before
    the pipeline can execute.
    """

    pass


# =============================================================================
# REGISTRY IMPLEMENTATION
# =============================================================================


class EpistemicCalibrationRegistry:
    """
    Orchestrate hierarchical calibration resolution with PDM sensitivity.

    This registry implements an 8-layer resolution pipeline:
    1. Determine immutable epistemic level (Layer 1)
    2. Load level defaults from JSON (Layer 1)
    3. Apply contract type overrides (Layer 2)
    4. Apply method-specific overrides (Layer 3)
    5. Apply PDM-driven adjustments (Layer 4)
    6-8. Reserved for future extensions

    CONSTITUTIONAL RULE: The epistemic level determined in step 1 is
    IMMUTABLE through all subsequent steps. PDM adjustments (step 5)
    can ONLY modify parameter values, NEVER the level itself.

    Attributes:
        root: Root path to calibration configuration directory
        method_level_map: Immutable mapping of method_id -> level
        level_defaults: Cached level configurations from JSON
        type_overrides: Cached contract type overrides from JSON
    """

    def __init__(self, root_path: Path):
        """
        Initialize the calibration registry.

        Args:
            root_path: Root path to calibration configuration directory

        Raises:
            CalibrationResolutionError: If required configurations are missing
        """
        self.root = root_path
        self.method_level_map = self._load_method_registry()
        self.level_defaults = self._load_level_defaults()
        self.type_overrides = self._load_type_overrides()

        # DEFENSIVE: Validate all required levels have configs
        required_levels = EpistemicLevel
        loaded_levels = set(self.level_defaults.keys())
        missing_levels = required_levels - loaded_levels

        if missing_levels:
            raise CalibrationResolutionError(
                f"Missing level configurations for: {missing_levels}. "
                f"Expected levels: {sorted(EpistemicLevel)}"
            )

    def _load_method_registry(self) -> dict[str, str]:
        """
        Load the immutable method-to-level mapping.

        This mapping is the single source of truth for epistemic level
        assignment. It CANNOT be modified at runtime.

        RETURNS:
            Dict mapping method_id (ClassName.method_name) to level

        RAISES:
            CalibrationResolutionError: If registry file is missing
        """
        registry_path = self.root / "config" / "method_registry_epistemic.json"

        if not registry_path.exists():
            raise CalibrationResolutionError(
                f"Method registry not found: {registry_path}\n"
                "This file is REQUIRED for level assignment."
            )

        with open(registry_path) as f:
            data = json.load(f)

        # Extract flat mapping for efficient lookup
        flat_mapping = data.get("flat_mapping", {})

        # Validate all levels are recognized
        valid_levels = EpistemicLevel
        for method_id, level in flat_mapping.items():
            if level not in valid_levels:
                raise CalibrationResolutionError(
                    f"Invalid level '{level}' for method '{method_id}'. "
                    f"Valid levels: {sorted(valid_levels)}"
                )

        return flat_mapping

    def _load_level_defaults(self) -> dict[str, dict[str, Any]]:
        """
        Load default configurations for each epistemic level.

        RETURNS:
            Dict mapping level_id to configuration dict

        RAISES:
            CalibrationResolutionError: If level config is invalid
        """
        level_configs = {}
        level_dir = self.root / "level_configs"

        if not level_dir.exists():
            raise CalibrationResolutionError(
                f"Level configs directory not found: {level_dir}"
            )

        for json_file in level_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    config = json.load(f)
                    level_id = config["level"]
                    level_configs[level_id] = config
            except (json.JSONDecodeError, KeyError) as e:
                raise CalibrationResolutionError(
                    f"Invalid level config file {json_file}: {e}"
                ) from e

        return level_configs

    def _load_type_overrides(self) -> dict[str, dict[str, Any]]:
        """
        Load contract type override configurations.

        RETURNS:
            Dict mapping contract_type to override dict
        """
        type_configs = {}
        type_dir = self.root / "type_configs"

        # Type overrides are optional
        if not type_dir.exists():
            return type_configs

        for json_file in type_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    config = json.load(f)
                    contract_type = config["contract_type"]
                    type_configs[contract_type] = config
            except (json.JSONDecodeError, KeyError):
                # Continue on error (type overrides are optional)
                continue

        return type_configs

    def resolve_calibration(
        self,
        method_id: str,
        contract_type: str,
        pdm_profile: Any | None = None,
    ) -> dict[str, Any]:
        """
        Resolve calibration through 8-layer pipeline.

        ARCHITECTURE:
            Layer 1: Determine level (INMUTABLE) [CI-03]
            Layer 2: Load level defaults
            Layer 3: Apply type overrides
            Layer 4: Apply PDM logic (parameters only, never level) [CI-05]

        Args:
            method_id: Fully-qualified method (ClassName.method_name)
            contract_type: Contract type (TYPE_A, TYPE_B, etc.)
            pdm_profile: Optional PDM structural profile

        Returns:
            Dict with resolved calibration parameters

        Raises:
            CalibrationResolutionError: If resolution fails
        """
        # LAYER 1: Determine level (INMUTABLE)
        level = self.method_level_map.get(method_id)

        if level is None:
            raise CalibrationResolutionError(
                f"Method '{method_id}' not found in registry. "
                "All methods MUST be pre-registered in method_registry_epistemic.json"
            )

        # LAYER 2: Load config base del nivel
        base_config = self.level_defaults.get(level, {}).copy()

        if not base_config:
            raise CalibrationResolutionError(
                f"No base configuration for level '{level}'"
            )

        # Store original level for validation
        original_level = base_config.get("level")

        # LAYER 3: Aplicar overrides por tipo de contrato
        if contract_type in self.type_overrides:
            type_config = self.type_overrides[contract_type]
            base_config = self._deep_merge(base_config, type_config)

        # LAYER 4: Aplicar lógica PDM (Python dinámico)
        if pdm_profile is not None:
            pdm_adjustments = self._apply_pdm_logic(level, pdm_profile)
            base_config["calibration_parameters"].update(pdm_adjustments)

        # CRITICAL VALIDATION: Nunca cambiar el nivel [CI-03, CI-05]
        resolved_level = base_config.get("level")
        if resolved_level != original_level:
            raise CalibrationResolutionError(
                f"CONSTITUTIONAL VIOLATION [CI-03/CI-05]: "
                f"Level changed from '{original_level}' to '{resolved_level}'. "
                f"Epistemic level is IMMUTABLE and cannot be changed by "
                f"type overrides or PDM adjustments."
            )

        # Validate final level matches method registry
        if resolved_level != level:
            raise CalibrationResolutionError(
                f"CONSTITUTIONAL VIOLATION [CI-03]: "
                f"Resolved level '{resolved_level}' does not match "
                f"registry level '{level}' for method '{method_id}'"
            )

        return base_config

    def _apply_pdm_logic(self, level: str, pdm_profile: Any) -> dict[str, Any]:
        """
        Apply PDM-driven parameter adjustments.

        CONSTITUTIONAL RULE [CI-05]:
            This function adjusts PARAMETERS (thresholds, weights),
            NEVER the epistemic level itself.

        Args:
            level: Epistemic level (N0-N4)
            pdm_profile: PDM structural profile

        Returns:
            Dict of parameter adjustments
        """
        adjustments = {}

        if level == "N1-EMP":
            adjustments.update(self._pdm_n1_rules(pdm_profile))
        elif level == "N2-INF":
            adjustments.update(self._pdm_n2_rules(pdm_profile))
        elif level == "N3-AUD":
            adjustments.update(self._pdm_n3_rules(pdm_profile))
        elif level in ("N0-INFRA", "N4-META"):
            # N0 and N4 are level-agnostic, no PDM adjustments
            pass

        # DEFENSIVE: Ensure level is not in adjustments [CI-05]
        if "level" in adjustments:
            del adjustments["level"]

        return adjustments

    def _pdm_n1_rules(self, pdm: Any) -> dict[str, float]:
        """
        PDM rules for N1: Adjust extraction parameters.

        LOGIC:
        - Si contiene tablas PPI/PAI: Boost extracción tabular
        - Si jerarquía > 3 niveles: Aumentar sensibilidad jerárquica
        """
        adjustments = {}

        # Detección de tablas críticas
        if hasattr(pdm, "table_schemas"):
            critical_tables = {"PPI", "PAI", "POI", "financial_table"}
            if any(t in pdm.table_schemas for t in critical_tables):
                adjustments["table_extraction_boost"] = 1.2

        # Ajuste por profundidad jerárquica
        if hasattr(pdm, "hierarchy_depth") and pdm.hierarchy_depth > 3:
            adjustments["hierarchy_sensitivity"] = 1.1

        return adjustments

    def _pdm_n2_rules(self, pdm: Any) -> dict[str, Any]:
        """
        PDM rules for N2: Adjust Bayesian inference parameters.

        LOGIC:
        - Si detecta baselines históricos: Usar data-driven priors
        - Si estructura jerárquica: Habilitar modelos jerárquicos
        """
        adjustments = {}

        # Detección de baselines temporales
        if hasattr(pdm, "temporal_structure") and pdm.temporal_structure.get(
            "has_baselines"
        ):
            adjustments["use_data_driven_priors"] = True
            adjustments["prior_strength"] = 0.7  # Aumentar peso de priors

        # Modelos jerárquicos para estructuras anidadas
        if hasattr(pdm, "hierarchy_depth") and pdm.hierarchy_depth > 2:
            adjustments["enable_hierarchical_models"] = True

        return adjustments

    def _pdm_n3_rules(self, pdm: Any) -> dict[str, Any]:
        """
        PDM rules for N3: Adjust audit strictness.

        LOGIC:
        - Si contiene datos financieros: Aumentar strictness
        - Si requiere lógica temporal: Habilitar validación temporal
        """
        adjustments = {}

        # Strictness financiera
        if hasattr(pdm, "contains_financial_data") and pdm.contains_financial_data:
            adjustments["financial_strictness"] = 1.5
            adjustments["veto_threshold_partial"] = 0.6  # Más estricto

        # Validación de consistencia temporal
        if hasattr(pdm, "temporal_structure") and pdm.temporal_structure.get(
            "requires_ordering"
        ):
            adjustments["temporal_logic_required"] = True

        return adjustments

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """
        Recursive merge of dictionaries.

        BEHAVIOR:
            - override has priority over base in conflicts
            - Nested dicts are merged recursively
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_method_level(self, method_id: str) -> str:
        """
        Get the epistemic level for a method.

        Args:
            method_id: Fully-qualified method name

        Returns:
            Epistemic level (N0-N4)

        Raises:
            CalibrationResolutionError: If method not found
        """
        level = self.method_level_map.get(method_id)

        if level is None:
            raise CalibrationResolutionError(
                f"Method '{method_id}' not found in registry. "
                "Valid methods are registered in method_registry_epistemic.json"
            )

        return level

    def create_calibration_object(
        self, level: str, **kwargs
    ) -> (
        N0InfrastructureCalibration
        | N1EmpiricalCalibration
        | N2InferentialCalibration
        | N3AuditCalibration
        | N4MetaCalibration
    ):
        """
        Create a calibration object for a given level.

        Args:
            level: Epistemic level
            **kwargs: Parameter overrides

        Returns:
            Corresponding calibration object
        """
        return create_calibration(level, **kwargs)


# =============================================================================
# MOCK PDM PROFILE FOR TESTING
# =============================================================================


class MockPDMProfile(SimpleNamespace):
    """
    Mock PDM structural profile for testing.

    In production, this would be replaced by the actual
    PDMStructuralProfile from the parametrization module.
    """

    # Default mock attributes
    table_schemas: list[str] = []
    hierarchy_depth: int = 2
    contains_financial_data: bool = False
    temporal_structure: dict[str, Any] = {
        "has_baselines": False,
        "requires_ordering": False,
    }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def create_registry(
    root_path: Path | str | None = None,
) -> EpistemicCalibrationRegistry:
    """
    Factory function to create a calibration registry.

    Args:
        root_path: Root path to calibration config directory.
                  If None, uses default path.

    Returns:
        Initialized EpistemicCalibrationRegistry
    """
    if root_path is None:
        # Default to this module's calibration directory
        root_path = Path(__file__).parent

    return EpistemicCalibrationRegistry(Path(root_path))


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Exceptions
    "CalibrationResolutionError",
    # Main class
    "EpistemicCalibrationRegistry",
    # Factory
    "create_registry",
    # Mock for testing
    "MockPDMProfile",
]
